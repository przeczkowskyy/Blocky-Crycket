--[[
	RigPetow — budowa petów i jajka z klocków (dane Moduly/Rigi/*, wygenerowane z modeli swiat/postacie) i odtwarzanie
	ich klipów przez Motor6D.Transform (ModuleScript w Workspace/PetyProba/Moduly; używa go KlientPetow i budowa
	w Studio — zbuduj.py). Bez wgrywania czegokolwiek: części Roblox, stawy, spawy, próbki klipów z danych.

		zbuduj(dane, skala?, nazwa?)  → model, uchwyt   — Model (PrimaryPart = niewidzialny, zakotwiczony korzeń),
		                                                 kości (niewidzialne części) na Motor6D, bryły na Weld
		uchwyt(model, dane, skala?)   → uchwyt albo nil  — dla modelu zbudowanego wcześniej (np. w Edit)
		graj(u, klip, predkosc?, potem?) → true/false     — klip od początku; po klipie bez pętli: klip `potem`
		krok(u, dt)                                      — przesuwa czas i ustawia stawy (woła klient co klatkę)
		ustaw(u, cf)                                     — korzeń w miejscu cf (punkt na ziemi pod postacią)
		zeruj(u)                                         — wszystkie stawy w spoczynku
		czesci(u) → lista widocznych części; dlugosc(dane, klip) → sekundy
	Układ danych: swiat/pety_proba/dane_petow.py (rig_modelu). Klatki co 1/fps s, liniowo między nimi.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local R = {}

local KLASY = { [3] = "WedgePart", [4] = "CornerWedgePart" }
local KSZTALTY = { [0] = "Block", [1] = "Ball", [2] = "Cylinder" }

local function bezFizyki(p: BasePart)
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.CastShadow = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
end

local function v3(t, a: number, s: number): Vector3
	return Vector3.new(t[a] * s, t[a + 1] * s, t[a + 2] * s)
end

function R.zbuduj(dane, skala: number?, nazwa: string?)
	local s = skala or 1
	local model = Instance.new("Model")
	model.Name = nazwa or dane.nazwa
	local hrpPos = v3(dane.hrp, 1, s)
	local korzen = Instance.new("Part")
	korzen.Name = "Korzen"
	korzen.Size = Vector3.new(0.4, 0.4, 0.4) * s
	korzen.Transparency = 1
	korzen.Anchored = true
	bezFizyki(korzen)
	korzen.CFrame = CFrame.new(hrpPos)
	korzen.Parent = model
	local kosci = {}
	for i, k in dane.kosci do
		local p = Instance.new("Part")
		p.Name = k[1]
		p.Size = v3(k, 9, s)
		p.Transparency = 1
		p.Anchored = false
		bezFizyki(p)
		p.CFrame = CFrame.new(v3(k, 6, s))
		p.Parent = model
		kosci[i] = p
	end
	local motory = {}
	for i, k in dane.kosci do
		local rodzic, srodekRodzica
		if k[2] == 0 then
			rodzic, srodekRodzica = korzen, hrpPos
		else
			rodzic, srodekRodzica = kosci[k[2]], v3(dane.kosci[k[2]], 6, s)
		end
		local staw = v3(k, 3, s)
		local m = Instance.new("Motor6D")
		m.Name = k[1]
		m.C0 = CFrame.new(staw - srodekRodzica)
		m.C1 = CFrame.new(staw - v3(k, 6, s))
		m.Part0 = rodzic
		m.Part1 = kosci[i]
		m.Parent = kosci[i]
		motory[i] = m
	end
	for _, c in dane.czesci do
		local p
		if KLASY[c[2]] then
			p = Instance.new(KLASY[c[2]])
		else
			p = Instance.new("Part")
			p.Shape = Enum.PartType[KSZTALTY[c[2]] or "Block"]
		end
		p.Name = c[3]
		p.Size = v3(c, 10, s)
		local cf = CFrame.new(v3(c, 4, s)) * CFrame.fromOrientation(c[7], c[8], c[9])
		p.CFrame = cf
		p.Color = Color3.fromHex(c[13])
		local mat = dane.materialy[c[14] + 1]
		p.Material = Enum.Material[mat[1]]
		p.Reflectance = mat[2]
		p.Anchored = false
		bezFizyki(p)
		if c[15] ~= "" then
			local sm = Instance.new("SpecialMesh")
			sm.MeshType = Enum.MeshType[c[15]]
			sm.Parent = p
		end
		local kosc = kosci[c[1]]
		local w = Instance.new("Weld")
		w.Part0 = kosc
		w.Part1 = p
		w.C0 = kosc.CFrame:Inverse() * cf
		w.Parent = p
		p.Parent = kosc
	end
	model.PrimaryPart = korzen
	return model, R.nowyUchwyt(model, dane, s, korzen, motory)
end

function R.nowyUchwyt(model: Model, dane, s: number, korzen: BasePart, motory)
	return { model = model, dane = dane, skala = s, korzen = korzen, motory = motory, klip = nil, t = 0,
		predkosc = 1, potem = nil, koniec = false }
end

-- uchwyt dla modelu zbudowanego wcześniej (kości po nazwach z danych)
function R.uchwyt(model: Model, dane, skala: number?)
	local korzen = model:FindFirstChild("Korzen")
	if not korzen then
		return nil
	end
	local motory = {}
	for i, k in dane.kosci do
		local kosc = model:FindFirstChild(k[1])
		local m = kosc and kosc:FindFirstChild(k[1])
		if not m or not m:IsA("Motor6D") then
			return nil
		end
		motory[i] = m
	end
	return R.nowyUchwyt(model, dane, skala or 1, korzen, motory)
end

function R.dlugosc(dane, klip: string): number
	local kl = dane.klipy[klip]
	if not kl then
		return 0
	end
	return (#kl.klatki - 1) / kl.fps
end

-- CFrame-y klatek liczone raz na dane, klip i skalę
local pamiec = {}
local function klatkiCF(dane, klip: string, s: number)
	local klucz = dane.id .. "|" .. klip .. "|" .. tostring(s)
	local w = pamiec[klucz]
	if w then
		return w
	end
	local kl = dane.klipy[klip]
	w = {}
	for f, wiersz in kl.klatki do
		local rzad = {}
		for j = 1, #kl.kosci do
			local o = (j - 1) * 6
			rzad[j] = CFrame.new(wiersz[o + 1] * s, wiersz[o + 2] * s, wiersz[o + 3] * s)
				* CFrame.fromOrientation(wiersz[o + 4], wiersz[o + 5], wiersz[o + 6])
		end
		w[f] = rzad
	end
	pamiec[klucz] = w
	return w
end

function R.zeruj(u)
	for _, m in u.motory do
		m.Transform = CFrame.identity
	end
end

function R.graj(u, klip: string, predkosc: number?, potem: string?): boolean
	if not u.dane.klipy[klip] then
		return false
	end
	R.zeruj(u)
	u.klip = klip
	u.t = 0
	u.predkosc = predkosc or 1
	u.potem = potem
	u.koniec = false
	return true
end

function R.krok(u, dt: number)
	local klip = u.klip
	if not klip then
		return
	end
	local kl = u.dane.klipy[klip]
	local n = #kl.klatki
	u.t += dt * u.predkosc
	local f = u.t * kl.fps
	local ost = n - 1
	if kl.petla then
		f = f % ost
	elseif f >= ost then
		f = ost
		if not u.koniec then
			u.koniec = true
			if u.potem then
				local dalej = u.potem
				R.graj(u, dalej, 1, nil)
				return R.krok(u, 0)
			end
		end
	end
	local i0 = math.floor(f)
	local a = f - i0
	local i1 = math.min(i0 + 1, ost)
	local cf = klatkiCF(u.dane, klip, u.skala)
	local r0, r1 = cf[i0 + 1], cf[i1 + 1]
	for j, ki in kl.kosci do
		local m = u.motory[ki]
		if m then
			m.Transform = if a < 1e-4 then r0[j] else r0[j]:Lerp(r1[j], a)
		end
	end
end

-- cf = początek układu modelu: punkt na ziemi pod postacią (z obrotem; przód modelu = −Z cf)
function R.ustaw(u, cf: CFrame)
	local h = u.dane.hrp
	u.korzen.CFrame = cf * CFrame.new(h[1] * u.skala, h[2] * u.skala, h[3] * u.skala)
end

function R.czesci(u)
	local w = {}
	for _, d in u.model:GetDescendants() do
		if d:IsA("BasePart") and d.Transparency < 1 then
			table.insert(w, d)
		end
	end
	return w
end

return R
