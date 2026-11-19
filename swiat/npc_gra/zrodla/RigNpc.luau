--[[
	RigNpc — budowa postaci niezależnej z klocków (dane Moduly/Rigi/Rig_<id>, wygenerowane z modułów swiat/postacie
	przez swiat/npc_gra/dane.py) i odtwarzanie jej klipów przez Motor6D.Transform u klienta. Układ danych jak
	RigKowala / RigPetow; tu dochodzą płynne przejścia między klipami i obrót głowy oraz tułowia ku graczowi
	(dokładany do pozy z klipu). Nic nie jest wgrywane: zwykłe części Roblox, bez kolizji, dotyku, promieni i cieni.

		zbuduj(dane, skala?, nazwa?) → model, uchwyt     Model (PrimaryPart = niewidzialny, zakotwiczony korzeń),
		                                                kości (niewidzialne części) na Motor6D, bryły na Weld
		ustaw(u, cf)                                     korzeń tak, żeby cf było punktem na ziemi pod postacią
		                                                (przód postaci = −Z cf)
		graj(u, klip, przejscie?) → true/false           klip od początku; przejscie = sekundy mieszania z bieżącą pozą
		krok(u, dt, tulow?, glowa?, pochyl?)             przesuwa czas i ustawia stawy; kąty wzroku w radianach
		dlugosc(dane, klip) → sekundy; bryly(u) → liczba widocznych części
	Klatki co 1/fps s, liniowo między nimi (numer klatki liczy LogikaNpc.klatka).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = require(script.Parent:WaitForChild("LogikaNpc"))

local R = {}

local KLASY = { [3] = "WedgePart", [4] = "CornerWedgePart" }
local KSZTALTY = { [0] = "Block", [1] = "Ball", [2] = "Cylinder" }
local ZERO = CFrame.identity

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
	local bryl = 0
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
		bryl += 1
	end
	model.PrimaryPart = korzen
	local poza, poprz = {}, {}
	for i = 1, #motory do
		poza[i] = ZERO
		poprz[i] = ZERO
	end
	return model, {
		model = model, dane = dane, skala = s, korzen = korzen, motory = motory, kosci = kosci, bryl = bryl,
		poza = poza, poprz = poprz, klip = nil, t = 0, przejscie = 0, t_przejscia = 0,
	}
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

function R.graj(u, klip: string, przejscie: number?): boolean
	if not u.dane.klipy[klip] then
		return false
	end
	for i = 1, #u.motory do
		u.poprz[i] = u.poza[i]
	end
	u.klip = klip
	u.t = 0
	u.przejscie = przejscie or 0
	u.t_przejscia = 0
	return true
end

function R.krok(u, dt: number, tulow: number?, glowa: number?, pochyl: number?)
	local klip = u.klip
	if not klip then
		return
	end
	local kl = u.dane.klipy[klip]
	u.t += dt
	local i0, i1, a = L.klatka(u.t, kl.fps, #kl.klatki, kl.petla)
	local cf = klatkiCF(u.dane, klip, u.skala)
	local r0, r1 = cf[i0 + 1], cf[i1 + 1]
	local poza = u.poza
	local n = #poza
	for i = 1, n do
		poza[i] = ZERO
	end
	for j, ki in kl.kosci do
		poza[ki] = if a < 1e-4 then r0[j] else r0[j]:Lerp(r1[j], a)
	end
	if u.przejscie > 0 then
		u.t_przejscia += dt
		local w = u.t_przejscia / u.przejscie
		if w >= 1 then
			u.przejscie = 0
		else
			w = w * w * (3 - 2 * w)
			local poprz = u.poprz
			for i = 1, n do
				poza[i] = poprz[i]:Lerp(poza[i], w)
			end
		end
	end
	local motory = u.motory
	local ig, it = u.dane.glowa, u.dane.tulow
	for i = 1, n do
		local p = poza[i]
		if i == ig then
			p = CFrame.fromOrientation(pochyl or 0, glowa or 0, 0) * p
		elseif i == it then
			p = CFrame.fromOrientation(0, tulow or 0, 0) * p
		end
		motory[i].Transform = p
	end
end

-- cf = początek układu modelu: punkt na ziemi pod postacią (z obrotem; przód modelu = −Z cf)
function R.ustaw(u, cf: CFrame)
	local h = u.dane.hrp
	u.korzen.CFrame = cf * CFrame.new(h[1] * u.skala, h[2] * u.skala, h[3] * u.skala)
end

function R.bryly(u): number
	return u.bryl
end

return R
