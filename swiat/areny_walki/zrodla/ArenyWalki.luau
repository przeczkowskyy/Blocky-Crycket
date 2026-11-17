--[[
	ArenyWalki — arena walki zależna od biomu źródła walki (D-095), po stronie klienta. ModuleScript w
	Workspace/ArenyWalki/Moduly (buduje swiat/areny_walki/zbuduj.py). Woła go odtwarzacz walki prototypu
	(swiat/test_walki2/zrodla/OdtwarzaczWalki2.luau) cienkim wywołaniem w przygotowaniu sceny:

		local uchwyt, powod = ArenyWalki.przygotuj({ zrodlo = <nazwa kontenera źródła>, kontener = <kontener>, folder = <scena lokalna> })

	uchwyt = nil → odtwarzacz zostaje na STAREJ arenie (Workspace/TestWalki2/Arena) i działa jak dotąd; powód trafia do
	atrybutu kontenera („brak_areny_dla_zrodla”, „brak_modelu”, „arena_niewczytana”, „wylaczone” …).
	uchwyt:
		.nazwa          klucz areny ("las" | "bagno" | "proba")
		.scena          CFrame sceny walki = znacznik Scena w modelu areny (CFrame.lookAt(środek płyty, … + (0, 0, 1)))
		.pudloSrodek, .pudloRozmiar   pudło sceny do chowania obcych części (Vector3)
		.model          Model areny (do wykluczenia z chowania obcych)
		:zakoncz()      sprząta wszystko (nastrój, detale, łopot chorągwi); bezpieczne wołać kilka razy

	Nastrój tylko u gracza i tylko na czas walki:
	  • mgła: lokalne właściwości Lighting.Atmosphere (zmiana klienta nie idzie do serwera ani innych graczy) — przy
	    końcu wracają wartości zastane przy starcie walki; gdy w Lighting nie ma Atmosphere, powstaje lokalna i znika.
	    Na kontenerze ArenyWalki stoi wtedy lokalny atrybut CelMglyPasa = 1 — mgły pasów (MglaPasa lasu-pasa i Bagna)
	    ustępują według swojej umowy i niczego nie piszą; po walce przejmują od wartości zastanych (bez mignięcia).
	  • detale z DaneAren (lokalne części w folderze sceny, niszczone przy sprzątaniu): błędne ogniki ze światłem,
	    bąbelki na wodzie, spadające liście, pyłki w smugach światła, kurz, ptaki; chorągwie areny łopoczą (lokalna
	    zmiana CFrame części modelu, przywracana przy końcu).
	Model areny jest Persistent (przychodzi do klienta po dołączeniu, nie jest wypychany) — patrz PROJEKT.md, streaming.
	Wyłączenie bez usuwania: atrybut kontenera ArenyWalki „Wylaczone” = true (walki wracają na starą arenę).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")

local moduly = script.Parent
local kontener = moduly.Parent
local Dane = require(moduly:WaitForChild("DaneAren"))
local L = require(moduly:WaitForChild("LogikaAren"))

local A = {}
A.Dane = Dane
A.Logika = L

local Uchwyt = {}
Uchwyt.__index = Uchwyt

local POLA_MGLY = { "Density", "Offset", "Haze", "Glare" }

local function hex(h: string): Color3
	return Color3.fromHex(h)
end

local function liczCzesci(model: Instance): number
	local n = 0
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			n += 1
		end
	end
	return n
end

function Uchwyt:posprzataj(f: () -> ())
	table.insert(self.sprzatanie, f)
end

function Uchwyt:czesc(w: { [string]: any }): BasePart
	local p = Instance.new(w.Klasa or "Part")
	w.Klasa = nil
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	for k, v in w do
		(p :: any)[k] = v
	end
	p.Parent = self.folder
	self.utworzono += 1
	return p
end

------------------------------------------------------------------ mgła lokalna
function Uchwyt:nastroj(n: any)
	if type(n) ~= "table" then
		return
	end
	local atm = Lighting:FindFirstChildOfClass("Atmosphere")
	local wlasna = false
	if not atm then
		atm = Instance.new("Atmosphere")
		atm.Name = "AtmosferaAreny"
		atm.Parent = Lighting -- lokalny obiekt klienta (nie idzie do serwera), niszczony przy końcu walki
		wlasna = true
		self.utworzono += 1
	end
	local baza = { Color = atm.Color, Decay = atm.Decay }
	for _, pole in POLA_MGLY do
		baza[pole] = (atm :: any)[pole]
	end
	local cel = { Color = hex(n.Color), Decay = hex(n.Decay) }
	for _, pole in POLA_MGLY do
		cel[pole] = n[pole]
	end
	local function zastosuj()
		for _, pole in POLA_MGLY do
			(atm :: any)[pole] = cel[pole]
		end
		atm.Color = cel.Color
		atm.Decay = cel.Decay
	end
	pcall(function()
		kontener:SetAttribute("CelMglyPasa", 1) -- mgły pasów ustępują (umowa MglaPasa: wyższy cel wygrywa)
	end)
	zastosuj()
	self.mgla = { atm = atm, cel = cel, zastosuj = zastosuj }
	self:posprzataj(function()
		self.mgla = nil
		pcall(function()
			kontener:SetAttribute("CelMglyPasa", nil)
		end)
		if wlasna then
			atm:Destroy()
		elseif atm.Parent then
			for _, pole in POLA_MGLY do
				(atm :: any)[pole] = baza[pole]
			end
			atm.Color = baza.Color
			atm.Decay = baza.Decay
		end
	end)
end

------------------------------------------------------------------ detale
function Uchwyt:detale(d: any)
	local ruchome = {} -- { czesci = {…}, krok = function(t) → cframes }
	local scena = self.scena
	for nr, w in d.detale or {} do
		local typ = w.typ
		if typ == "ogniki" then
			local czesci, swiatla = {}, {}
			for i = 1, w.n or 8 do
				local p = self:czesc({ Name = "Ognik", Shape = Enum.PartType.Ball, Size = Vector3.one * 0.7, Color = hex(w.kolor),
					Material = Enum.Material.Neon, Transparency = 0.1 })
				if i <= (w.swiatla or 0) then
					local s = Instance.new("PointLight")
					s.Range, s.Brightness, s.Color, s.Shadows = 9, 1.4, hex(w.kolor), false
					s.Parent = p
					self.utworzono += 1
					table.insert(swiatla, s)
				end
				table.insert(czesci, p)
			end
			table.insert(ruchome, { czesci = czesci, krok = function(t)
				local cf = table.create(#czesci)
				for i = 1, #czesci do
					local x, y, z = L.ognik(i, t, w.r[1], w.r[2], w.y[1], w.y[2])
					cf[i] = CFrame.new(scena:PointToWorldSpace(Vector3.new(x, y, z)))
				end
				return cf
			end })
		elseif typ == "babelki" then
			local czesci = {}
			for _ = 1, w.n or 8 do
				table.insert(czesci, self:czesc({ Name = "Babelek", Shape = Enum.PartType.Ball, Size = Vector3.one * 0.5, Color = hex(w.kolor),
					Material = Enum.Material.Glass, Transparency = 0.35 }))
			end
			local yw = d.yGruntu or -1.8
			table.insert(ruchome, { czesci = czesci, krok = function(t)
				local cf = table.create(#czesci)
				for i, p in czesci do
					local x, y, z, s = L.babelek(i, t, w.r[1], w.r[2], yw)
					local skala = math.max(s, 0.01)
					if math.abs(p.Size.X - 0.7 * skala) > 0.02 then
						p.Size = Vector3.one * (0.7 * skala)
					end
					p.Transparency = if s > 0 then 0.35 else 1
					cf[i] = CFrame.new(scena:PointToWorldSpace(Vector3.new(x, y, z)))
				end
				return cf
			end })
		elseif typ == "liscie" then
			local czesci = {}
			for i = 1, w.n or 10 do
				table.insert(czesci, self:czesc({ Name = "Lisc", Size = Vector3.new(0.7, 0.08, 0.45), Color = hex(w.kolory[(i - 1) % #w.kolory + 1]),
					Material = Enum.Material.SmoothPlastic }))
			end
			table.insert(ruchome, { czesci = czesci, krok = function(t)
				local cf = table.create(#czesci)
				for i = 1, #czesci do
					local x, y, z, obr = L.lisc(i, t, w.r[1], w.r[2], w.y[1], w.y[2], 1.4)
					cf[i] = CFrame.new(scena:PointToWorldSpace(Vector3.new(x, y, z))) * CFrame.Angles(math.sin(obr) * 0.9, obr, math.cos(obr * 0.7) * 0.6)
				end
				return cf
			end })
		elseif typ == "ptaki" then
			local czesci = {}
			for _ = 1, w.n or 3 do
				for _, strona in { -1, 1 } do
					local p = self:czesc({ Name = "Ptak", Size = Vector3.new(1.6, 0.15, 0.6), Color = hex("2B2238"), Material = Enum.Material.SmoothPlastic })
					p:SetAttribute("Strona", strona)
					table.insert(czesci, p)
				end
			end
			table.insert(ruchome, { czesci = czesci, krok = function(t)
				local cf = table.create(#czesci)
				for k = 1, #czesci, 2 do
					local i = math.floor((k + 1) / 2)
					local x, y, z, kier, skrzydla = L.ptak(i, t, w.r[1], w.r[2], w.y[1], w.y[2])
					local baza = CFrame.new(scena:PointToWorldSpace(Vector3.new(x, y, z))) * CFrame.Angles(0, -kier, 0)
					cf[k] = baza * CFrame.new(-0.75, 0, 0) * CFrame.Angles(0, 0, 0.5 * skrzydla + 0.2)
					cf[k + 1] = baza * CFrame.new(0.75, 0, 0) * CFrame.Angles(0, 0, -0.5 * skrzydla - 0.2)
				end
				return cf
			end })
		elseif typ == "pylki" or typ == "kurz" then
			local miejsca = {}
			if typ == "pylki" then
				for _, k in (d.kotwice and d.kotwice[w.punkty]) or {} do
					table.insert(miejsca, { Vector3.new(k[1], math.min(k[3], 30) * 0.45, k[2]), Vector3.new(3, math.min(k[3], 30) * 0.8, 3) })
				end
			else
				for i = 0, 2 do
					local a = math.rad(225 + 45 * i)
					local r = (w.r[1] + w.r[2]) / 2
					table.insert(miejsca, { Vector3.new(r * math.cos(a), 0.6, r * math.sin(a)), Vector3.new(12, 0.6, 12) })
				end
			end
			for _, m in miejsca do
				local p = self:czesc({ Name = if typ == "pylki" then "Pylki" else "Kurz", Size = m[2], Transparency = 1,
					CFrame = scena * CFrame.new(m[1]) })
				local e = Instance.new("ParticleEmitter") -- domyślna (wbudowana) tekstura — żadnych uploadów
				e.Shape = Enum.ParticleEmitterShape.Box
				e.Rate = if typ == "pylki" then (w.tempo or 4) else 3
				e.Lifetime = NumberRange.new(4, 7)
				e.Speed = NumberRange.new(0.2, 0.6)
				e.SpreadAngle = Vector2.new(180, 180)
				e.Size = NumberSequence.new(if typ == "pylki" then 0.25 else 0.5)
				e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.3, 0.45),
					NumberSequenceKeypoint.new(1, 1) })
				e.Color = ColorSequence.new(hex(w.kolor))
				e.LightEmission = if typ == "pylki" then 0.7 else 0
				e.Acceleration = Vector3.new(0, if typ == "pylki" then -0.05 else 0.15, 0)
				e.Parent = p
				self.utworzono += 1
			end
		elseif typ == "choragiewki" then
			-- łopot chorągwi i girlandy areny: lokalna zmiana CFrame części modelu (przywracana przy końcu)
			local grupa = self.model:FindFirstChild(w.grupa or "Plac", true)
			local czesci, baza = {}, {}
			if grupa then
				for _, c in grupa:GetDescendants() do
					if c:IsA("BasePart") and (c.Name == "Chorągiewka" or c.Name == "Chorągiew płat" or c.Name == "Chorągiew ogon") then
						table.insert(czesci, c)
						table.insert(baza, c.CFrame)
					end
				end
			end
			if #czesci > 0 then
				self:posprzataj(function()
					pcall(function()
						workspace:BulkMoveTo(czesci, baza, Enum.BulkMoveMode.FireCFrameChanged)
					end)
				end)
				table.insert(ruchome, { czesci = czesci, krok = function(t)
					local cf = table.create(#czesci)
					for i = 1, #czesci do
						cf[i] = baza[i] * CFrame.Angles(0, L.flaga(i, t), 0)
					end
					return cf
				end })
			end
		else
			warn("[ArenyWalki] nieznany detal nastroju: " .. tostring(typ) .. " (" .. tostring(nr) .. ")")
		end
	end
	self.ruchome = ruchome
end

------------------------------------------------------------------ klatka i koniec
function Uchwyt:krok()
	local t = os.clock() - self.t0
	local m = self.mgla
	if m and m.atm.Parent and (math.abs(m.atm.Density - m.cel.Density) > 1e-3 or math.abs(m.atm.Offset - m.cel.Offset) > 1e-3) then
		m.zastosuj() -- ktoś (np. gasnąca mgła starego lasu) nadpisał Atmosphere w czasie walki
	end
	for _, r in self.ruchome do
		local cf = r.krok(t)
		workspace:BulkMoveTo(r.czesci, cf, Enum.BulkMoveMode.FireCFrameChanged)
	end
end

function Uchwyt:zakoncz()
	if self.zakonczony then
		return
	end
	self.zakonczony = true
	for i = #self.sprzatanie, 1, -1 do
		local ok, blad = pcall(self.sprzatanie[i])
		if not ok then
			warn("[ArenyWalki] sprzątanie: " .. tostring(blad))
		end
	end
	table.clear(self.sprzatanie)
end

------------------------------------------------------------------ API
function A.przygotuj(info: any): (any, string?)
	if type(info) ~= "table" then
		return nil, "zle_wywolanie"
	end
	if kontener:GetAttribute("Wylaczone") == true then
		return nil, "wylaczone"
	end
	local biom = nil
	if typeof(info.kontener) == "Instance" then
		local b = info.kontener:GetAttribute("BiomAreny")
		if type(b) == "string" then
			biom = b
		end
	end
	local klucz = L.wybierz(Dane, info.zrodlo, biom)
	if not klucz then
		return nil, "brak_areny_dla_zrodla"
	end
	local d = Dane.areny[klucz]
	local model = kontener:FindFirstChild(d.model)
	if not model or not model:IsA("Model") then
		return nil, "brak_modelu"
	end
	local znacznik = model:FindFirstChild("Scena")
	if not znacznik or not znacznik:IsA("BasePart") then
		return nil, "brak_znacznika"
	end
	if not L.wczytana(d.czesci, liczCzesci(model) - 1) then
		return nil, "arena_niewczytana"
	end
	local folder = Instance.new("Folder")
	folder.Name = "NastrojAreny"
	folder.Parent = if typeof(info.folder) == "Instance" then info.folder else workspace
	local scena = znacznik.CFrame
	local u = setmetatable({
		nazwa = klucz, scena = scena, model = model, folder = folder, sprzatanie = {}, ruchome = {}, utworzono = 1, t0 = os.clock(),
		pudloSrodek = scena.Position + Vector3.new(0, 60, 0),
		pudloRozmiar = Vector3.new(d.pudloRozmiar[1], d.pudloRozmiar[2], d.pudloRozmiar[3]),
	}, Uchwyt)
	u:posprzataj(function()
		folder:Destroy()
	end)
	local ok, blad = pcall(function()
		u:nastroj(d.nastroj)
		u:detale(d)
		local polaczenie = RunService.RenderStepped:Connect(function()
			if u.zakonczony then
				return
			end
			local ok2, blad2 = pcall(u.krok, u)
			if not ok2 then
				warn("[ArenyWalki] klatka nastroju: " .. tostring(blad2))
				u.ruchome = {}
			end
		end)
		u:posprzataj(function()
			polaczenie:Disconnect()
		end)
		-- scena lokalna zniknęła bez wołania zakoncz (błąd w odtwarzaczu) — sprzątamy sami
		local straz = folder.AncestryChanged:Connect(function()
			if not folder:IsDescendantOf(game) then
				task.defer(function()
					u:zakoncz()
				end)
			end
		end)
		u:posprzataj(function()
			straz:Disconnect()
		end)
	end)
	if not ok then
		warn("[ArenyWalki] nastrój areny " .. klucz .. ": " .. tostring(blad))
	end
	return u, nil
end

return A
