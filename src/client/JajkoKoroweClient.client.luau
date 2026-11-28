--!strict
--[[
	JajkoKoroweClient — leśne jajo w świecie (Paweł 24.11; baza u Pawła do pokazania Karolowi).
	Model: artefakt Pawła „Leśne jajo 3D” przeniesiony 1:1 (zasób 92671202213818, ustawienie:
	tools/studio/jajo_lesne_ustaw.luau) — Workspace/JajkoKorowePodglad/"Jajko korowe": Egg (całe jajo), ShellBottom,
	ShellTopLeft, ShellTopRight (kawałki skorupy, w spoczynku niewidoczne), RockBed, Crystals, Shards, Mushroom*,
	Korzen (niewidzialny PrimaryPart, przód = LookVector). Serwer: src/server/JajkoKorowe.server.luau (zakup przez
	serwer petów Karola; „wyklucie” do wszystkich).

	Karta petów nad jajkiem (układ tablicy Karola): tło z grafiki (KartaPetowJajka), w ramkach modele petów 3D
	z klocków Karola, obok szansa, nazwa i umiejętność; na dole klawisz E, cena i rybka.

	Wyklucie jak w artefakcie: jajo trzęsie się coraz mocniej, żyły świecą jaśniej; potem całe jajo zamienia się
	w kawałki skorupy — odlatuje prawa górna część, po chwili lewa, zostaje dół z rdzeniem w kolorze rzadkości,
	wyrasta słup światła, lecą iskry, nad jajem napis z petem.
	Scenka otwierania (tylko u kupującego): kamera przed jajem (całe jajo w kadrze), gracz, jego bohater i pet
	niewidoczni, HUD i karta schowane, czarne pasy. Jajo nie pęka samo — 5 kliknięć (mysz, dotyk, spacja), każde to
	szarpnięcie i komiksowy dymek (grafika Pawła DymekKomiks + napis); ostatnie = BOOM!. Bez kliknięcia przez
	CZEKAJ_S s scenka idzie dalej sama. Inni gracze widzą wyklucie od razu w całości.

	26.11 (Paweł: „niech zrobi agent Karola, wzorując się na animacji jaja lasu”): ta sama karta i scenka dla jajek
	Bagna i Dżungli (swiat/jajka_biomow) — modele z atrybutem JajkoId w Workspace/JajkaBiomowPodglad, karta nad
	„Punkt <nazwa modelu>”. Kolory żył i blasku z atrybutów modelu KolorZyl / KolorBlasku (bez atrybutu — leśne).
	Umowa z JajkaBiomowSpoczynek (ruch tych jajek w spoczynku): na czas scenki atrybut Wyklucie = true — wtedy jajem
	i blaskiem steruje ten skrypt, poza scenką tamten (jeden „pisarz” CFrame); w chwili BOOM KolorRzadkosci i Final += 1
	(ozdoby grają finał). Leśnym jajem ten skrypt rusza zawsze, jak dotąd. Bez modelu jajko jest pomijane; ze
	StreamingEnabled modele mogą przychodzić później — co sekundę sprawdzamy, co stoi w świecie.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TS = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local UIS = game:GetService("UserInputService")

if not RunService:IsStudio() then
	return
end

local player = Players.LocalPlayer

local KOLOR_ZYL = Color3.fromRGB(83, 232, 154) -- leśne (jajka biomów: atrybut KolorZyl modelu)
local KOLOR_BLASKU = Color3.fromHex("E6FFF0") -- leśne (atrybut KolorBlasku)
local LESNE = { id = "jajko_lesne", kontener = "JajkoKorowePodglad", model = "Jajko korowe", punkt = "PunktJajka" }
local BIOMY = "JajkaBiomowPodglad" -- kontener jajek Bagna i Dżungli (swiat/jajka_biomow)
local TYTULY = { jajko_lesne = "FOREST EGG", jajko_bagienne = "SWAMP EGG", jajko_dzungli = "JUNGLE EGG" }
local RYBKA = "rbxassetid://76704302626777" -- GoldFish
local KARTA = "rbxassetid://84906898270329" -- KartaPetowJajka (1723 × 2274)
local DYMEK = "rbxassetid://105383434661458" -- DymekKomiks (grafika Pawła, 855 × 650)

type Lot = { czesc: BasePart, pos: Vector3, obrot: CFrame, v: Vector3, w: Vector3, t0: number }
type PokazPeta = { model: Model?, kotwica: BasePart, gui: BillboardGui, zywy: boolean }
type Jajko = {
	id: string, -- id jajka w danych petów Karola (jajko_lesne, jajko_bagienne, jajko_dzungli)
	kolorZyl: Color3,
	kolorBlasku: Color3,
	wlasnyRuch: boolean, -- leśne: ruch w spoczynku też tutaj; jajka biomów — JajkaBiomowSpoczynek
	zajete: boolean,
	pokazany: PokazPeta?,
	-- stan ruchu jaja (ustawiany przez scenkę, czytany co klatkę)
	kolysanie: number, -- amplituda spoczynkowa (radiany)
	trzesienie: number, -- dodatkowe drżenie
	szarpniecie: number, -- chwila ostatniego kliknięcia (os.clock)
	blask: number, -- siła świecenia żył (jak BASE_EM w artefakcie)
	model: Model,
	korzen: BasePart,
	jajo: BasePart,
	dom: CFrame,
	kawalki: { [string]: BasePart },
	domy: { [BasePart]: CFrame },
	blaski: { any },
	rdzen: BasePart,
	slup: BasePart,
	poswiata: BasePart,
	swiatlo: PointLight,
	loty: { Lot },
	skala: number,
}

local Z = RS:WaitForChild("JajkoKoroweZdarzenia") :: RemoteEvent
local F = RS:WaitForChild("JajkoKorowe") :: RemoteFunction
local jajka: { [Model]: Jajko } = {} -- jajka w świecie (leśne i biomów), gotowe do scenki

-- wielkie litery z polskimi znakami (string.upper zmienia tylko ASCII)
local PL = { ["ą"] = "Ą", ["ć"] = "Ć", ["ę"] = "Ę", ["ł"] = "Ł", ["ń"] = "Ń", ["ó"] = "Ó", ["ś"] = "Ś", ["ź"] = "Ź", ["ż"] = "Ż" }
local function wielkie(t: string): string
	t = string.upper(t)
	for male, duze in pairs(PL) do
		t = t:gsub(male, duze)
	end
	return t
end

------------------------------------------------------------------ model
local function neon(nazwa: string, ksztalt: Enum.PartType, rodzic: Instance): Part
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Shape = ksztalt
	p.Material = Enum.Material.Neon
	p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery = true, false, false, false
	p.CastShadow = false
	p.Transparency = 1
	p.Parent = rodzic
	return p
end

local function przygotuj(m: Model, id: string, wlasnyRuch: boolean): Jajko?
	local korzen = m.PrimaryPart or m:FindFirstChild("Korzen")
	local jajo = m:FindFirstChild("Egg")
	if not (korzen and korzen:IsA("BasePart") and jajo and jajo:IsA("BasePart")) then
		return nil
	end
	local skala = m:GetScale()
	local kz, kb = m:GetAttribute("KolorZyl"), m:GetAttribute("KolorBlasku")
	local j: Jajko = { id = id, kolorZyl = if typeof(kz) == "Color3" then kz else KOLOR_ZYL,
		kolorBlasku = if typeof(kb) == "Color3" then kb else KOLOR_BLASKU, wlasnyRuch = wlasnyRuch, zajete = false,
		pokazany = nil, kolysanie = 0.012, trzesienie = 0.0, szarpniecie = -10.0, blask = 0.55,
		model = m, korzen = korzen, jajo = jajo, dom = jajo.CFrame, kawalki = {}, domy = {}, blaski = {},
		rdzen = neon("Rdzen", Enum.PartType.Ball, m), slup = neon("Slup swiatla", Enum.PartType.Cylinder, m),
		poswiata = neon("Poswiata slupa", Enum.PartType.Cylinder, m), swiatlo = Instance.new("PointLight"), loty = {},
		skala = skala }
	for _, n in ipairs({ "ShellBottom", "ShellTopLeft", "ShellTopRight" }) do
		local c = m:FindFirstChild(n)
		if c and c:IsA("BasePart") then
			j.kawalki[n] = c
			j.domy[c] = c.CFrame
			c.Transparency = 1
		end
	end
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("SurfaceAppearance") then
			table.insert(j.blaski, d)
		end
	end
	-- rdzeń: spłaszczona świecąca kula w dolnej połowie skorupy (w artefakcie: kula 0,7 m spłaszczona do połowy,
	-- 1,38 m nad ziemią; korzeń modelu leży 0,21 m niżej)
	local s = skala
	j.rdzen.Size = Vector3.new(1.35, 1.35, 1.35) * s
	j.rdzen.CFrame = korzen.CFrame * CFrame.new(0, 1.59 * s, 0)
	local siatka = Instance.new("SpecialMesh")
	siatka.MeshType = Enum.MeshType.Sphere
	siatka.Scale = Vector3.new(1, 0.5, 1)
	siatka.Parent = j.rdzen
	j.rdzen.Color = j.kolorBlasku
	-- słup światła: walec od rdzenia w górę (oś X walca = wysokość)
	local wys = 7 * s
	for _, c in ipairs({ j.slup, j.poswiata }) do
		c.Size = Vector3.new(wys, 1.1 * s, 1.1 * s)
		c.CFrame = korzen.CFrame * CFrame.new(0, 1.66 * s + wys / 2, 0) * CFrame.Angles(0, 0, math.rad(90))
	end
	j.swiatlo.Name = "SwiatloRdzenia"
	j.swiatlo.Color = j.kolorZyl
	j.swiatlo.Range = 14
	j.swiatlo.Brightness = 0
	j.swiatlo.Parent = j.rdzen
	local h = Instance.new("Highlight")
	h.Name = "ObrysKomiksowy"
	h.FillTransparency = 1
	h.OutlineColor = Color3.fromRGB(15, 22, 19)
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Adornee = m
	h.Parent = m
	return j
end

------------------------------------------------------------------ pet wyłaniający się ze słupa światła
-- Paweł 24.11: „po otwarciu jajka i pojawieniu lasera wyłania się z niego trafiony pet, nad nim jego nazwa, pod nim
-- rzadkość”. Model peta z klocków budują moduły Karola (PetyProba/Moduly: RigPetow.zbuduj + Rig_<pet>, bez zmian
-- u niego; poza Studio jego moduł jest pusty — wtedy lecą same napisy). Wszystko tylko u klienta.
-- Pokazany pet jest osobny dla każdego jajka (j.pokazany): wyklucie przy innym jajku go nie chowa.
local function schowajPeta(j: Jajko)
	local p = j.pokazany
	j.pokazany = nil
	if p then
		p.zywy = false
		p.gui:Destroy()
		p.kotwica:Destroy()
		if p.model then
			p.model:Destroy()
		end
	end
end

local function modulyPeta(petId: string): (any, any)
	local k = workspace:FindFirstChild("PetyProba")
	local mod = k and k:FindFirstChild("Moduly")
	local rig = mod and mod:FindFirstChild("RigPetow")
	local dane = mod and mod:FindFirstChild("Rig_" .. petId, true)
	if not (rig and rig:IsA("ModuleScript") and dane and dane:IsA("ModuleScript")) then
		return nil, nil
	end
	local ok, R, D = pcall(function()
		return require(rig), require(dane)
	end)
	if not ok or type(R) ~= "table" or type(R.zbuduj) ~= "function" then
		return nil, nil
	end
	return R, D
end

local WZLOT_S = 0.9 -- tyle pet wznosi się z rdzenia i rośnie

local function wylonPeta(j: Jajko, wynik: any, kolor: Color3)
	schowajPeta(j)
	local s = j.skala
	local lv = j.korzen.CFrame.LookVector
	local przod = Vector3.new(lv.X, 0, lv.Z).Unit
	local start = j.korzen.Position + Vector3.new(0, 1.6 * s, 0)
	local cel = j.korzen.Position + Vector3.new(0, 3.2 * s, 0)
	local kotwica = Instance.new("Part")
	kotwica.Name = "PetZJajkaPunkt"
	kotwica.Size = Vector3.new(0.2, 0.2, 0.2)
	kotwica.Transparency = 1
	kotwica.Anchored, kotwica.CanCollide, kotwica.CanTouch, kotwica.CanQuery = true, false, false, false
	kotwica.Position = start
	kotwica.Parent = workspace

	local R, D = modulyPeta(tostring(wynik.pet))
	local model: Model? = nil
	local skalaPeta, srodek = 1, Vector3.zero
	if R and D then
		local ok, m = pcall(function()
			return (R.zbuduj(D, 1, "PetZJajka"))
		end)
		if ok and typeof(m) == "Instance" and m:IsA("Model") then
			local cf, roz = m:GetBoundingBox()
			skalaPeta = 1.75 * s / math.max(roz.X, roz.Y, roz.Z, 0.1)
			srodek = m:GetPivot():PointToObjectSpace(cf.Position)
			for _, d in ipairs(m:GetDescendants()) do
				if d:IsA("BasePart") then
					d.CanCollide, d.CanTouch, d.CanQuery, d.CastShadow = false, false, false, false
				end
			end
			m:ScaleTo(skalaPeta * 0.12)
			m:PivotTo(CFrame.lookAt(start, start + przod))
			m.Parent = workspace
			model = m
		end
	end

	-- napisy: nazwa nad petem, rzadkość pod nim (jedna tabliczka wyśrodkowana na pecie, środek pusty)
	local b = Instance.new("BillboardGui")
	b.Name = "PetZJajkaNapisy"
	b.Size = UDim2.fromScale(9, 3.1 * s)
	b.AlwaysOnTop = true
	b.LightInfluence = 0
	b.Adornee = kotwica
	local skalaNapisow = Instance.new("UIScale")
	skalaNapisow.Scale = 0
	skalaNapisow.Parent = b
	local function l(t: string, y: number, h: number, c: Color3)
		local x = Instance.new("TextLabel")
		x.BackgroundTransparency = 1
		x.Size = UDim2.fromScale(1, h)
		x.Position = UDim2.fromScale(0, y)
		x.Text = t
		x.TextScaled = true
		x.TextColor3 = c
		x.FontFace = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
		local st = Instance.new("UIStroke")
		st.Thickness = 3
		st.Color = Color3.fromRGB(26, 20, 16)
		st.Parent = x
		x.Parent = b
	end
	l(tostring(wynik.nazwa or ""), 0, 0.18, Color3.new(1, 1, 1))
	l(wielkie(tostring(wynik.rzadkoscNazwa or "")), 0.825, 0.14, kolor)
	b.Parent = player:WaitForChild("PlayerGui")

	local p: PokazPeta = { model = model, kotwica = kotwica, gui = b, zywy = true }
	j.pokazany = p
	task.spawn(function()
		local t0 = os.clock()
		local u: any = nil
		local napisy = false
		while p.zywy do
			local dt = RunService.RenderStepped:Wait()
			if not p.zywy then
				break
			end
			local t = os.clock() - t0
			local a = math.clamp(t / WZLOT_S, 0, 1)
			local e = 1 - (1 - a) ^ 3
			local poz = start:Lerp(cel, e)
			local kat = (1 - e) * math.pi * 2 -- obrót przy wznoszeniu, na końcu przodem do kamery
			if a >= 1 then
				poz += Vector3.new(0, math.sin((t - WZLOT_S) * 2.4) * 0.1 * s, 0)
				kat = math.sin((t - WZLOT_S) * 1.3) * 0.3
			end
			kotwica.Position = poz
			if model then
				if a < 1 then
					model:ScaleTo(skalaPeta * (0.12 + 0.88 * e))
				elseif not u then
					model:ScaleTo(skalaPeta)
					local okU, uchwyt = pcall(function()
						local h = R.uchwyt(model, D, skalaPeta)
						if h and not R.graj(h, "radosc", 1, "spoczynek") then
							R.graj(h, "spoczynek")
						end
						return h
					end)
					u = if okU and uchwyt then uchwyt else false
				end
				local obrot = CFrame.lookAt(Vector3.zero, przod) * CFrame.Angles(0, kat, 0)
				model:PivotTo(CFrame.new(poz) * obrot * CFrame.new(-srodek * model:GetScale()))
				if u then
					pcall(R.krok, u, dt)
				end
			end
			if not napisy and a >= 0.75 then
				napisy = true
				TS:Create(skalaNapisow, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
			end
		end
	end)
end

local function spoczynek(j: Jajko)
	schowajPeta(j)
	table.clear(j.loty)
	j.jajo.Transparency = 0
	j.jajo.CFrame = j.dom
	for c, cf in pairs(j.domy) do
		c.CFrame = cf
		c.Transparency = 1
	end
	j.rdzen.Transparency = 1
	j.slup.Transparency = 1
	j.poswiata.Transparency = 1
	j.swiatlo.Brightness = 0
	j.kolysanie, j.trzesienie, j.blask = 0.012, 0, 0.55
end

-- kawałek skorupy odlatuje: w bok od środka jaja i w górę, z obrotem; grawitacja jak w artefakcie (5,2 m/s²)
local function odlot(j: Jajko, nazwa: string, wGore: number, wBok: number)
	local c = j.kawalki[nazwa]
	if not c then
		return
	end
	local s = j.skala
	local od = c.Position - j.korzen.Position
	local kier = Vector3.new(od.X, 0, od.Z)
	kier = if kier.Magnitude > 0.01 then kier.Unit else j.korzen.CFrame.RightVector
	local strona = if kier:Dot(j.korzen.CFrame.RightVector) >= 0 then 1 else -1
	table.insert(j.loty, { czesc = c, pos = c.Position, obrot = c.CFrame.Rotation, v = kier * wBok * s + Vector3.new(0, wGore * s, 0),
		w = Vector3.new((math.random() - 0.5) * 3, (math.random() - 0.5) * 2, -strona * (2 + math.random() * 1.2)), t0 = os.clock() })
end

local function slup(j: Jajko, kolor: Color3)
	local s = j.skala
	local wys = j.slup.Size.X
	j.slup.Color = j.kolorBlasku
	j.slup.Size = Vector3.new(wys, 0.15, 0.15)
	j.slup.Transparency = 0.05
	TS:Create(j.slup, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Size = Vector3.new(wys, 0.8 * s, 0.8 * s) }):Play()
	j.poswiata.Color = kolor
	j.poswiata.Size = Vector3.new(wys, 0.2, 0.2)
	j.poswiata.Transparency = 0.55
	TS:Create(j.poswiata, TweenInfo.new(0.45, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Size = Vector3.new(wys * 1.03, 1.9 * s, 1.9 * s) }):Play()
end

local function iskry(j: Jajko, kolor: Color3, ile: number)
	local e = Instance.new("ParticleEmitter")
	e.Color = ColorSequence.new(kolor, j.kolorZyl)
	e.LightEmission = 1
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.4), NumberSequenceKeypoint.new(1, 0) })
	e.Speed = NumberRange.new(9, 18)
	e.SpreadAngle = Vector2.new(60, 60)
	e.Lifetime = NumberRange.new(0.7, 1.3)
	e.Acceleration = Vector3.new(0, -14, 0)
	e.Rate = 0
	e.Parent = j.rdzen
	e:Emit(ile)
	task.delay(2.2, function()
		e:Destroy()
	end)
end

------------------------------------------------------------------ karta petów (układ tablicy Karola)
-- jedna karta na jajko w świecie (id jajka → karta nad jego punktem E)
type Karta = { id: string, gui: BillboardGui, etykiety: { [string]: TextLabel }, widoki: { ViewportFrame },
	pokazane: { [number]: string } }
local karty: { [string]: Karta } = {}
local RZEDY = { 0.2, 0.32, 0.442, 0.565, 0.685 } -- góra ramki peta w każdym rzędzie (ułamki grafiki)

local function napisKarty(k: Karta, rodzic: Instance, nazwa: string, x: number, y: number, w: number, h: number,
	kolor: string, mx: number, gruby: boolean, wyrownanie: Enum.TextXAlignment?): TextLabel
	local t = Instance.new("TextLabel")
	t.Name = nazwa
	t.BackgroundTransparency = 1
	t.Position = UDim2.fromScale(x, y)
	t.Size = UDim2.fromScale(w, h)
	t.Text = ""
	t.TextScaled = true
	t.TextColor3 = Color3.fromHex(kolor)
	t.TextXAlignment = wyrownanie or Enum.TextXAlignment.Center
	t.FontFace = if gruby
		then Font.new("rbxasset://fonts/families/LuckiestGuy.json")
		else Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Bold)
	t.ZIndex = 4
	local c = Instance.new("UITextSizeConstraint")
	c.MaxTextSize = mx
	c.Parent = t
	t.Parent = rodzic
	k.etykiety[nazwa] = t
	return t
end

local function obrys(t: TextLabel, grubosc: number)
	local s = Instance.new("UIStroke")
	s.Thickness = grubosc
	s.Color = Color3.fromRGB(26, 20, 16)
	s.Parent = t
end

local function zbudujTablice(punkt: BasePart, id: string, tytul: string): Karta
	local b = Instance.new("BillboardGui")
	local k: Karta = { id = id, gui = b, etykiety = {}, widoki = {}, pokazane = {} }
	b.Name = "SzanseJajka"
	b.Size = UDim2.fromScale(4.4, 5.8) -- proporcje grafiki 0,7577
	b.StudsOffset = Vector3.new(4.6, 1.2, 0)
	b.MaxDistance = 28
	b.LightInfluence = 0
	b.Adornee = punkt
	local f = Instance.new("ImageLabel")
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromScale(1, 1)
	f.Image = KARTA
	f.ScaleType = Enum.ScaleType.Stretch
	f.ZIndex = 1
	f.Parent = b
	obrys(napisKarty(k, f, "Tytul", 0.285, 0.024, 0.43, 0.072, "FCE3B0", 80, true), 2.5)
	k.etykiety["Tytul"].Text = tytul
	for i, y in ipairs(RZEDY) do
		-- zwierzak w ramce (model 3D z klocków Karola), obok: szansa, nazwa i umiejętność — jak na tablicy Karola
		local v = Instance.new("ViewportFrame")
		v.Name = "Pet" .. i .. "Widok"
		v.BackgroundTransparency = 1
		v.Position = UDim2.fromScale(0.127, y + 0.008)
		v.Size = UDim2.fromScale(0.116, 0.084)
		v.Ambient = Color3.fromRGB(200, 200, 200)
		v.LightColor = Color3.new(1, 1, 1)
		v.ZIndex = 3
		v.Parent = f
		k.widoki[i] = v
		napisKarty(k, f, "Szansa" .. i, 0.28, y + 0.01, 0.15, 0.05, "2B2118", 60, true, Enum.TextXAlignment.Left)
		napisKarty(k, f, "Pet" .. i, 0.43, y + 0.009, 0.45, 0.052, "2B2118", 60, false, Enum.TextXAlignment.Left)
		-- umiejętność: do dwóch linijek (długie opisy epickich i legendarnych nie kurczą się do nieczytelnych)
		local sk = napisKarty(k, f, "Skill" .. i, 0.28, y + 0.056, 0.6, 0.042, "6B4A2E", 40, false, Enum.TextXAlignment.Left)
		sk.TextWrapped = true
		sk.TextYAlignment = Enum.TextYAlignment.Top
	end
	napisKarty(k, f, "PrzyciskE", 0.115, 0.856, 0.105, 0.068, "4A2E1A", 80, true).Text = "E"
	obrys(napisKarty(k, f, "Cena", 0.29, 0.86, 0.42, 0.06, "FFD65A", 80, true), 2.5)
	local ryb = Instance.new("ImageLabel")
	ryb.BackgroundTransparency = 1
	ryb.Image = RYBKA
	ryb.ScaleType = Enum.ScaleType.Fit
	ryb.Position = UDim2.fromScale(0.785, 0.852)
	ryb.Size = UDim2.fromScale(0.1, 0.074)
	ryb.ZIndex = 4
	ryb.Parent = f
	local kom = napisKarty(k, f, "Komunikat", 0.08, 0.787, 0.84, 0.032, "8A1F1F", 40, false)
	kom.ZIndex = 5
	b.Parent = player:WaitForChild("PlayerGui")
	karty[id] = k
	return k
end

-- zwierzak w ramce: model z klocków z danych Karola (PetyProba/Moduly: RigPetow.zbuduj + Rig_<pet>), bez zmian u niego
local function pokazPeta(v: ViewportFrame, petId: string)
	for _, x in ipairs(v:GetChildren()) do
		x:Destroy()
	end
	local k = workspace:FindFirstChild("PetyProba")
	local mod = k and k:FindFirstChild("Moduly")
	local rig = mod and mod:FindFirstChild("RigPetow")
	local dane = mod and mod:FindFirstChild("Rig_" .. petId, true)
	if not (rig and rig:IsA("ModuleScript") and dane and dane:IsA("ModuleScript")) then
		return
	end
	local ok, model = pcall(function()
		local R = require(rig) :: any
		local m = R.zbuduj(require(dane), 1, "Podglad " .. petId)
		return m
	end)
	if not ok or typeof(model) ~= "Instance" then
		return
	end
	local m = model :: Model
	m.Parent = v
	local cf, rozmiar = m:GetBoundingBox()
	local przod = m:GetPivot().LookVector
	local bok = m:GetPivot().RightVector
	local cam = Instance.new("Camera")
	cam.FieldOfView = 30
	local odl = math.max(rozmiar.X, rozmiar.Y, rozmiar.Z) * 2.3
	cam.CFrame = CFrame.lookAt(cf.Position + (przod * 0.9 + bok * 0.45).Unit * odl + Vector3.new(0, rozmiar.Y * 0.2, 0), cf.Position)
	cam.Parent = v
	v.CurrentCamera = cam
end

local function odswiezTablice(k: Karta)
	local etykiety, widoki, pokazane = k.etykiety, k.widoki, k.pokazane
	local ok, w = pcall(function()
		return F:InvokeServer("info", k.id)
	end)
	if not (ok and type(w) == "table" and w.ok) then
		return
	end
	local kolejnosc = { pospolity = 1, zwykly = 2, rzadki = 3, epicki = 4, legendarny = 5 }
	for _, sz in ipairs(w.szanse) do
		local i = kolejnosc[sz.rzadkosc]
		if i then
			etykiety["Szansa" .. i].Text = string.format("%g%%", math.floor(sz.szansa * 1000 + 0.5) / 10)
			etykiety["Pet" .. i].Text = sz.nazwa
			etykiety["Skill" .. i].Text = (string.gsub(string.gsub(sz.skill or "", "Złota", "Rybek"), "Złoto", "Rybki"))
			if pokazane[i] ~= sz.pet and widoki[i] then
				pokazane[i] = sz.pet
				pokazPeta(widoki[i], sz.pet)
			end
		end
	end
	etykiety["Cena"].Text = if type(w.cena) == "number" then tostring(w.cena) else ""
end

local function komunikat(t: string, id: string?)
	local karta = karty[id or LESNE.id]
	local k = karta and karta.etykiety["Komunikat"]
	if k then
		k.Text = t
		task.delay(2.5, function()
			if k.Text == t then
				k.Text = ""
			end
		end)
	end
end

------------------------------------------------------------------ scenka otwierania
local KLIKI = 5 -- ile kliknięć otwiera jajo
local CZEKAJ_S = 7
local NAPISY = { "CLICK!", "CRACK!", "TAP!", "CRRRK!", "POP!" }
local KOLORY_NAPISOW = { "E8452C", "F08A1D", "2F9BE8", "3FAE4F" }
local MIEJSCA = { { 0.24, 0.34 }, { 0.76, 0.3 }, { 0.22, 0.62 }, { 0.78, 0.6 }, { 0.5, 0.2 } }

type Kino = { typ: Enum.CameraType, cf: CFrame, fov: number, gui: ScreenGui, hud: boolean, sterowanie: any,
	ukryte: { BasePart }, klik: BindableEvent, zachecacz: Frame? }

-- komiksowy dymek: grafika Pawła (wybuch z ogonkiem) + napis w środku
local function dymek(rodzic: Instance, napisT: string, x: number, y: number, kolor: string, rozmiar: number, trwaly: boolean?): Frame
	local f = Instance.new("Frame")
	f.Name = "Dymek"
	f.BackgroundTransparency = 1
	f.AnchorPoint = Vector2.new(0.5, 0.5)
	f.Position = UDim2.fromScale(x, y)
	f.Size = UDim2.fromScale(rozmiar * 1.3154, rozmiar) -- proporcje grafiki 855 × 650
	f.SizeConstraint = Enum.SizeConstraint.RelativeYY
	f.Rotation = math.random(-10, 10)
	f.ZIndex = 5
	local im = Instance.new("ImageLabel")
	im.BackgroundTransparency = 1
	im.Size = UDim2.fromScale(1, 1)
	im.Image = DYMEK
	im.ScaleType = Enum.ScaleType.Stretch
	im.ZIndex = 5
	im.Parent = f
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Position = UDim2.fromScale(0.52, 0.43) -- środek „brzucha” dymka (ogonek jest w lewym dolnym rogu)
	t.Size = UDim2.fromScale(0.5, 0.3)
	t.Text = napisT
	t.TextScaled = true
	t.TextColor3 = Color3.fromHex(kolor)
	t.FontFace = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
	t.ZIndex = 6
	local s = Instance.new("UIStroke")
	s.Thickness = 3
	s.Color = Color3.fromRGB(26, 20, 16)
	s.Parent = t
	t.Parent = f
	local sc = Instance.new("UIScale")
	sc.Scale = 0.2
	sc.Parent = f
	f.Parent = rodzic
	TS:Create(sc, TweenInfo.new(0.22, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	if not trwaly then
		task.delay(0.6, function()
			local zn = TS:Create(sc, TweenInfo.new(0.18, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0 })
			zn:Play()
			zn.Completed:Wait()
			f:Destroy()
		end)
	end
	return f
end

-- części, których nie ma być widać w scence: postać gracza, jego bohater z klocków (pakiet Karola) i pety w pobliżu
local function doUkrycia(j: Jajko): { BasePart }
	local lista: { BasePart } = {}
	local srodek = j.korzen.Position
	local function zbierz(korzen: Instance?)
		if not korzen then
			return
		end
		for _, d in ipairs(korzen:GetDescendants()) do
			if d:IsA("BasePart") and not d:IsDescendantOf(j.model) and (d.Position - srodek).Magnitude < 40 then
				table.insert(lista, d)
			end
		end
	end
	zbierz(player.Character)
	local bs = workspace:FindFirstChild("BohaterSwiat")
	zbierz(bs and bs:FindFirstChild("BohaterowieLokalni"))
	local pety = workspace:FindFirstChild("PetyProba")
	if pety then
		for _, d in ipairs(pety:GetDescendants()) do
			if d:IsA("Model") and d.Name:sub(1, 4) == "Pet " then
				zbierz(d)
			end
		end
	end
	return lista
end

-- ujęcie: kamera przed jajem (przód = LookVector korzenia); odległość z wysokości jaja z podstawą
local function ujecie(j: Jajko, mnoznik: number, wyzej: number, bok: number): CFrame
	local p = j.korzen.CFrame
	local wys = 3.03 * j.skala -- jajo ze skałami: 3,03 m w pliku
	local przod = Vector3.new(p.LookVector.X, 0, p.LookVector.Z).Unit
	local wBok = przod:Cross(Vector3.yAxis)
	local odl = wys * 1.9 * mnoznik -- przy polu widzenia 50° jajo zajmuje ok. połowę wysokości ekranu
	return CFrame.lookAt(p.Position + przod * odl + wBok * bok + Vector3.new(0, wys * (0.7 + wyzej), 0),
		p.Position + Vector3.new(0, wys * (0.5 + wyzej * 0.6), 0))
end

local function kamera(cf: CFrame, czas: number, styl: Enum.EasingStyle?)
	local cam = workspace.CurrentCamera
	if cam then
		TS:Create(cam, TweenInfo.new(czas, styl or Enum.EasingStyle.Quad, Enum.EasingDirection.InOut), { CFrame = cf }):Play()
	end
end

local function kinoStart(j: Jajko): Kino?
	local cam = workspace.CurrentCamera
	if not cam then
		return nil
	end
	local pg = player:WaitForChild("PlayerGui")
	local hudGui = pg:FindFirstChild("HUD")
	local k: Kino = { typ = cam.CameraType, cf = cam.CFrame, fov = cam.FieldOfView, gui = Instance.new("ScreenGui"),
		hud = if hudGui and hudGui:IsA("ScreenGui") then hudGui.Enabled else false, sterowanie = nil,
		ukryte = doUkrycia(j), klik = Instance.new("BindableEvent"), zachecacz = nil }
	if hudGui and hudGui:IsA("ScreenGui") then
		hudGui.Enabled = false
	end
	for _, karta in pairs(karty) do
		karta.gui.Enabled = false
	end
	for _, c in ipairs(k.ukryte) do
		c.LocalTransparencyModifier = 1
	end
	k.gui.Name = "KinoJajka"
	k.gui.IgnoreGuiInset = true
	k.gui.DisplayOrder = 50
	k.gui.ResetOnSpawn = false
	local pole = Instance.new("TextButton") -- kliknięcia na całym ekranie (mysz i dotyk)
	pole.Name = "Klik"
	pole.BackgroundTransparency = 1
	pole.Text = ""
	pole.AutoButtonColor = false
	pole.Size = UDim2.fromScale(1, 1)
	pole.ZIndex = 2
	pole.Parent = k.gui
	pole.Activated:Connect(function()
		k.klik:Fire()
	end)
	for _, gora in ipairs({ true, false }) do
		local f = Instance.new("Frame")
		f.BackgroundColor3 = Color3.new(0, 0, 0)
		f.BorderSizePixel = 0
		f.AnchorPoint = Vector2.new(0, if gora then 0 else 1)
		f.Position = UDim2.fromScale(0, if gora then 0 else 1)
		f.Size = UDim2.fromScale(1, 0)
		f.ZIndex = 3
		f.Parent = k.gui
		TS:Create(f, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Size = UDim2.fromScale(1, 0.09) }):Play()
	end
	k.gui.Parent = pg
	-- (w tej grze nie ma standardowego PlayerModule — ruch zatrzymujemy prędkością postaci)
	local hum = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	if hum then
		k.sterowanie = { hum = hum, predkosc = hum.WalkSpeed, skok = hum.JumpPower }
		hum.WalkSpeed = 0
		hum.JumpPower = 0
	end
	cam.CameraType = Enum.CameraType.Scriptable
	cam.FieldOfView = 50
	return k
end

local function kinoKoniec(k: Kino)
	local cam = workspace.CurrentCamera
	if cam then
		local t = TS:Create(cam, TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut), { CFrame = k.cf, FieldOfView = k.fov })
		t:Play()
		t.Completed:Wait()
		cam.CameraType = k.typ
	end
	for _, c in ipairs(k.ukryte) do
		if c.Parent then
			c.LocalTransparencyModifier = 0
		end
	end
	k.gui:Destroy()
	k.klik:Destroy()
	if k.sterowanie and k.sterowanie.hum.Parent then
		k.sterowanie.hum.WalkSpeed = k.sterowanie.predkosc
		k.sterowanie.hum.JumpPower = k.sterowanie.skok
	end
	local hudGui = player:WaitForChild("PlayerGui"):FindFirstChild("HUD")
	if hudGui and hudGui:IsA("ScreenGui") and k.hud then
		hudGui.Enabled = true
	end
	for _, karta in pairs(karty) do
		karta.gui.Enabled = true
	end
end

-- czeka na kliknięcie (pole ekranu albo spacja); false, gdy minął czas
local function czekajNaKlik(k: Kino): boolean
	local klikniete = false
	local c1 = k.klik.Event:Connect(function()
		klikniete = true
	end)
	local c2 = UIS.InputBegan:Connect(function(input)
		if input.KeyCode == Enum.KeyCode.Space or input.KeyCode == Enum.KeyCode.ButtonA then
			klikniete = true
		end
	end)
	local t0 = os.clock()
	while not klikniete and os.clock() - t0 < CZEKAJ_S do
		task.wait()
	end
	c1:Disconnect()
	c2:Disconnect()
	return klikniete
end

local function zachecaj(k: Kino)
	if k.zachecacz then
		return
	end
	local d = dymek(k.gui, "CLICK!", 0.82, 0.74, "E8452C", 0.2, true) -- z boku, nie zasłania jaja
	d.Rotation = -5
	k.zachecacz = d
	local sc = d:FindFirstChildWhichIsA("UIScale")
	task.spawn(function()
		task.wait(0.25)
		while d.Parent and sc do
			sc.Scale = 1 + 0.08 * math.sin(os.clock() * 7)
			task.wait()
		end
	end)
end

-- zakup idzie „bez pokazu” (src/server/JajkoKorowe.server.luau): pakiet petów Karola nie gra animacji inkubatora,
-- a napis „Wykluł się…” i swojego peta za graczem trzyma do sygnału ze scenki (lokalny PetyProba/Sygnaly/PokazWyklucia:
-- "odsloniety" — pet wyłonił się ze słupa; "koniec", Vector3 jaja — pet rusza za graczem od jaja)
local function sygnalPetow(co: string, skad: Vector3?)
	local k = workspace:FindFirstChild("PetyProba")
	local s = k and k:FindFirstChild("Sygnaly")
	local e = s and s:FindFirstChild("PokazWyklucia")
	if e and e:IsA("BindableEvent") then
		e:Fire(co, skad)
	end
end

-- finał jak w artefakcie: całe jajo -> kawałki; prawa górna część odlatuje, po chwili lewa; rdzeń, słup, iskry
local function finalWyklucia(j: Jajko, wynik: any, kolor: Color3, kino: Kino?)
	j.trzesienie, j.blask = 0.05, 1.65
	j.jajo.Transparency = 1
	for c in pairs(j.domy) do
		c.Transparency = 0
	end
	-- ozdoby jajek biomów grają finał (JajkaBiomowSpoczynek: błysk w kolorze rzadkości)
	j.model:SetAttribute("KolorRzadkosci", kolor)
	j.model:SetAttribute("Final", (tonumber(j.model:GetAttribute("Final")) or 0) + 1)
	j.rdzen.Color = kolor:Lerp(j.kolorBlasku, 0.35)
	j.rdzen.Transparency = 0
	j.swiatlo.Color = kolor
	j.swiatlo.Brightness = 3
	odlot(j, "ShellTopRight", 3.4, 2.3)
	iskry(j, kolor, 18)
	task.wait(0.95)
	odlot(j, "ShellTopLeft", 3.2, 2.7)
	slup(j, kolor)
	iskry(j, kolor, 45)
	j.swiatlo.Brightness = 6
	if kino then
		-- odjazd i wyżej: nad jajem musi się zmieścić pet z nazwą
		kamera(ujecie(j, 1.5, 0.45, 0), 0.7, Enum.EasingStyle.Back)
	end
	task.delay(0.4, function()
		j.trzesienie = 0
	end)
	-- ze słupa światła wyłania się trafiony pet (nazwa nad nim, rzadkość pod nim); słup przygasa, żeby go nie zasłaniał
	task.wait(0.45)
	wylonPeta(j, wynik, kolor)
	-- Paweł 28.11: smuga światła zasłaniała peta przez całą scenkę (słup przygasał tylko do 0,6) — pet ma być widoczny
	-- w 100%. Słup i jego poświata gasną całkiem, zanim pet skończy się wznosić, a światło rdzenia słabnie, żeby
	-- nie prześwietlało modelu.
	TS:Create(j.slup, TweenInfo.new(WZLOT_S * 0.7), { Transparency = 1 }):Play()
	TS:Create(j.poswiata, TweenInfo.new(WZLOT_S * 0.7), { Transparency = 1 }):Play()
	TS:Create(j.swiatlo, TweenInfo.new(WZLOT_S), { Brightness = 1.5 }):Play()
	task.wait(WZLOT_S * 0.75)
	if kino then
		dymek(kino.gui, if wynik.nowy then "NEW PET!" else "AGAIN!", 0.79, 0.3, if wynik.nowy then "F08A1D" else "2F9BE8", 0.3, true)
		sygnalPetow("odsloniety") -- napis pakietu petów „Wykluł się: … — premia” dopiero teraz, razem z „NEW PET!”
	end
	task.wait(3.1)
	-- wygaszenie słupa
	TS:Create(j.slup, TweenInfo.new(0.5), { Transparency = 1 }):Play()
	TS:Create(j.poswiata, TweenInfo.new(0.5), { Transparency = 1 }):Play()
	task.wait(0.55)
end

local function wyklucie(j: Jajko, wynik: any, zKinem: boolean?)
	if j.zajete then
		return
	end
	j.zajete = true
	j.model:SetAttribute("Wyklucie", true) -- na czas scenki jajem steruje ten skrypt (nie JajkaBiomowSpoczynek)
	local kolor = Color3.fromHex(wynik.kolor or "FFFFFF")
	local kino: Kino? = nil
	if zKinem then
		local okK, wynikK = pcall(kinoStart, j)
		kino = if okK then wynikK else nil
	end
	if not kino then
		-- inni gracze: całość od razu (trzęsienie narasta przez 1,5 s jak w artefakcie)
		local t0 = os.clock()
		while os.clock() - t0 < 1.5 do
			local u = (os.clock() - t0) / 1.5
			j.trzesienie = 0.012 + 0.06 * u * u
			j.blask = 0.55 + 1.1 * u
			task.wait()
		end
		finalWyklucia(j, wynik, kolor, nil)
		spoczynek(j)
		j.model:SetAttribute("Wyklucie", nil)
		if zKinem then
			sygnalPetow("koniec", j.korzen.Position) -- kupujący bez kina (nie udało się go włączyć)
		end
		j.zajete = false
		return
	end
	local k = kino :: Kino
	local okS, blad = pcall(function()
		kamera(ujecie(j, 1.05, 0, 0.9), 0.5)
		task.wait(0.5)
		for i = 1, KLIKI - 1 do
			zachecaj(k)
			czekajNaKlik(k)
			-- szarpnięcie jaja, jaśniejsze żyły, stałe drżenie rośnie z każdym kliknięciem
			j.szarpniecie = os.clock()
			j.trzesienie = 0.008 * i
			j.blask = 0.55 + 0.28 * i
			iskry(j, j.kolorZyl, 4 + 2 * i)
			local m = MIEJSCA[(i - 1) % #MIEJSCA + 1]
			dymek(k.gui, NAPISY[(i - 1) % #NAPISY + 1], m[1], m[2], KOLORY_NAPISOW[(i - 1) % #KOLORY_NAPISOW + 1], 0.26 + 0.02 * i)
			-- kamera: krótkie „uderzenie” (bliżej i z powrotem), z każdym kliknięciem ciut bliżej
			local cam = workspace.CurrentCamera
			if cam then
				cam.CFrame = ujecie(j, 1.0 - 0.03 * i, 0, 0.9 - 0.1 * i)
				kamera(ujecie(j, 1.05 - 0.03 * i, 0, 0.9 - 0.1 * i), 0.18, Enum.EasingStyle.Back)
			end
			task.wait(0.28)
		end
		zachecaj(k)
		czekajNaKlik(k)
		if k.zachecacz then
			k.zachecacz:Destroy()
			k.zachecacz = nil
		end
		j.szarpniecie = os.clock()
		dymek(k.gui, "BOOM!", 0.5, 0.26, "E8452C", 0.4)
		finalWyklucia(j, wynik, kolor, k)
	end)
	if not okS then
		warn("[JajkoKorowe] scenka: " .. tostring(blad))
	end
	spoczynek(j)
	j.model:SetAttribute("Wyklucie", nil)
	pcall(kinoKoniec, k)
	sygnalPetow("koniec", j.korzen.Position)
	pcall(function()
		Z:FireServer("koniec")
	end)
	j.zajete = false
end

------------------------------------------------------------------ start
-- co sekundę: co stoi w świecie (leśne jajo i jajka biomów; ze StreamingEnabled modele i punkty E przychodzą
-- i znikają) — nowy egzemplarz modelu dostaje przygotowanie, karta wisi nad aktualnym punktem E
local wToku: { [Model]: boolean } = {}

local function podepnij(id: string, m: Model, punkt: BasePart?, wlasnyRuch: boolean, tytul: string)
	if punkt then
		local k = karty[id]
		if not k or not k.gui.Parent then
			if k then
				k.gui:Destroy()
			end
			task.spawn(odswiezTablice, zbudujTablice(punkt, id, tytul))
		elseif k.gui.Adornee ~= punkt then
			k.gui.Adornee = punkt
		end
	end
	if jajka[m] or wToku[m] then
		return
	end
	wToku[m] = true
	task.spawn(function()
		m:WaitForChild("Egg", 30)
		m:WaitForChild("ShellTopRight", 10)
		local j = if m.Parent then przygotuj(m, id, wlasnyRuch) else nil
		if j then
			jajka[m] = j
			spoczynek(j)
		end
		wToku[m] = nil
	end)
end

local function jajkoPoId(id: string): Jajko?
	for m, j in pairs(jajka) do
		if j.id == id and m.Parent then
			return j
		end
	end
	return nil
end

task.spawn(function()
	while true do
		local k = workspace:FindFirstChild(LESNE.kontener)
		local m = k and k:FindFirstChild(LESNE.model)
		if k and m and m:IsA("Model") then
			local p = k:FindFirstChild(LESNE.punkt)
			podepnij(LESNE.id, m, if p and p:IsA("BasePart") then p else nil, true, TYTULY[LESNE.id])
		end
		local b = workspace:FindFirstChild(BIOMY)
		if b then
			for _, x in ipairs(b:GetChildren()) do
				local id = x:GetAttribute("JajkoId")
				if x:IsA("Model") and type(id) == "string" and id ~= LESNE.id then
					local p = b:FindFirstChild("Punkt " .. x.Name)
					podepnij(id, x, if p and p:IsA("BasePart") then p else nil, false, TYTULY[id] or wielkie(x.Name))
				end
			end
		end
		for mm in pairs(jajka) do
			if not mm.Parent then
				jajka[mm] = nil -- model zniknął (streaming) — nowy egzemplarz podepnie się sam
			end
		end
		task.wait(1)
	end
end)

Z.OnClientEvent:Connect(function(rodzaj, a, b)
	if rodzaj == "wyklucie" and type(b) == "table" then
		local id = if type(b.jajko) == "string" then b.jajko else LESNE.id
		local j = jajkoPoId(id)
		if j then
			task.spawn(wyklucie, j, b, a == player.UserId)
		elseif a == player.UserId then
			pcall(function()
				Z:FireServer("koniec") -- bez modelu tego jajka u nas nie ma scenki: od razu zdejmij blokadę
			end)
			sygnalPetow("koniec") -- i napis „Wykluł się…” od razu
		end
		if a == player.UserId then
			task.delay(4, function() -- cena następnego jajka
				local k = karty[id]
				if k then
					odswiezTablice(k)
				end
			end)
		end
	elseif rodzaj == "odmowa" then
		komunikat(tostring(a), if type(b) == "string" then b else nil)
	end
end)

-- ruch co klatkę: kołysanie i drżenie całego jaja wokół podstawy, szarpnięcie po kliknięciu, lot kawałków skorupy,
-- pulsowanie żył (EmissiveStrength) i rdzenia. Jajka biomów tylko w scence (Wyklucie = true) — w spoczynku rusza nimi
-- JajkaBiomowSpoczynek (jeden „pisarz” CFrame i blasku).
RunService.RenderStepped:Connect(function(dt)
	local t = os.clock()
	for m, j in pairs(jajka) do
		if not m.Parent or (not j.wlasnyRuch and m:GetAttribute("Wyklucie") ~= true) then
			continue
		end
		-- żyły
		local puls = j.blask * (0.85 + 0.15 * math.sin(t * (2 + j.blask * 6)))
		for _, sa in ipairs(j.blaski) do
			sa.EmissiveStrength = puls
		end
		-- jajo
		if j.jajo.Transparency < 1 then
			local sz = math.clamp(1 - (t - j.szarpniecie) / 0.35, 0, 1) -- szarpnięcie gaśnie w 0,35 s
			local a = j.kolysanie + j.trzesienie + 0.07 * sz
			local szybko = j.trzesienie > 0.001 or sz > 0
			local rz = if szybko then math.sin(t * 46) * a else math.sin(t * 1.6) * a
			local rx = if szybko then math.sin(t * 37 + 1) * a * 0.5 else math.sin(t * 1.1 + 1) * a * 0.6
			local podstawa = j.korzen.CFrame
			j.jajo.CFrame = podstawa * CFrame.Angles(rx, 0, rz) * podstawa:ToObjectSpace(j.dom)
		end
		-- kawałki w locie
		local g = 5.2 * j.skala
		for i = #j.loty, 1, -1 do
			local l = j.loty[i]
			local wiek = t - l.t0
			l.v -= Vector3.new(0, g * dt, 0)
			l.pos += l.v * dt
			l.obrot = l.obrot * CFrame.Angles(l.w.X * dt, l.w.Y * dt, l.w.Z * dt)
			l.czesc.CFrame = CFrame.new(l.pos) * l.obrot
			if wiek > 1.5 then
				l.czesc.Transparency = math.clamp((wiek - 1.5) / 0.35, 0, 1)
				if wiek > 1.9 then
					table.remove(j.loty, i)
				end
			end
		end
		-- rdzeń lekko pulsuje, gdy jest odsłonięty
		if j.rdzen.Transparency < 1 then
			local s = j.skala
			local p = 1 + 0.04 * math.sin(t * 14)
			j.rdzen.Size = Vector3.new(1.35 * p, 1.35, 1.35 * p) * s
		end
	end
end)
