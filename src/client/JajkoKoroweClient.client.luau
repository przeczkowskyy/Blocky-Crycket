--!strict
--[[
	JajkoKoroweClient — jajko korowe w świecie (Paweł 24.11; baza u Pawła do pokazania Karolowi).
	Bez osobnego okna (Paweł: „z okna rezygnujemy”): po podejściu nad jajkiem pokazuje się podpowiedź z szansami na pety
	— obrazek panelu petów z grafiki okna jajka (kafelki OknoJajka2 i OknoJajka4, już w Roblox), na nim nazwy, szanse,
	rzadkości i cena w Rybkach. E (podpowiedź serwera „Kup jajko”) kupuje; serwer (src/server/JajkoKorowe.server.luau,
	zakup przez serwer petów Karola) wysyła „wyklucie” do wszystkich, więc jajko pęka u każdego w pobliżu.

	Wyklucie według referencji Pawła (model i klipy: swiat/postacie/jajko_korowe.py, Blender):
	  0. spoczynek: kołysanie (klip), szmaragdowe pęknięcia pulsują;
	  1. narastające napięcie (klip „napiecie”): drżenie coraz mocniej, pęknięcia pulsują szybciej i jaśniej;
	  2. rozłupywanie (klip „pekniecie”): odłamki przodu odpadają, z pęknięć bije światło;
	  3. otwarcie rdzenia: pokrywa odlatuje, rdzeń świeci kolorem rzadkości, wyrasta słup światła z poświatą;
	     (Roblox nie przenosi skali z klipu — słup robi klient), iskry; nad jajkiem napis z petem.
	Kreskówkowo: nasycone kolory, Neon bez rozmycia, czarny obrys (Highlight) jak rekwizyty sali wyboru.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TS = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local KSP = game:GetService("KeyframeSequenceProvider")

if not RunService:IsStudio() then
	return
end

local player = Players.LocalPlayer

local KOLOR_SZCZELINY = Color3.fromHex("2BE36B")
local KOLOR_BLASKU = Color3.fromHex("B8FFD2")
-- tablica szans (Paweł 24.11: proste okienko jak podpowiedź Karola, nie wycięte okno) — tools/tablica_jajka.py
local TABLICA = "rbxassetid://108070653620156" -- TablicaSzansJajka (1722 × 2291 px)
local RYBKA = "rbxassetid://76704302626777" -- GoldFish

type Jajko = {
	model: Model,
	tory: { [string]: AnimationTrack },
	szczeliny: { BasePart },
	slup: BasePart?,
	poswiata: BasePart?,
	rdzen: BasePart?,
	rozmiarSlupa: Vector3,
}

local jajko: Jajko? = nil
local tempo, jasnosc = 1.6, 0.0
local zajete = false

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
local function przygotuj(m: Model): Jajko
	local j: Jajko = { model = m, tory = {}, szczeliny = {}, slup = nil, poswiata = nil, rdzen = nil, rozmiarSlupa = Vector3.one }
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") then
			if d.Name:find("^Szczelina") or d.Name:find("^Odlamek szczelina") then
				table.insert(j.szczeliny, d)
			elseif d.Name:find("^Slup swiatla") then
				j.slup = d
			elseif d.Name == "Wnetrze" then
				j.rdzen = d
			end
		end
	end
	if j.slup then
		local s = j.slup :: BasePart
		j.rozmiarSlupa = s.Size
		s.Transparency = 1
		s.CastShadow = false
		local p = s:Clone()
		p.Name = "Poswiata slupa"
		for _, x in ipairs(p:GetChildren()) do
			x:Destroy()
		end
		p.Color = KOLOR_BLASKU
		p.Transparency = 1
		local w = Instance.new("WeldConstraint")
		w.Part0, w.Part1 = s, p
		w.Parent = p
		p.Parent = s.Parent
		j.poswiata = p
	end
	local kontroler = m:FindFirstChildWhichIsA("AnimationController")
	local animator = kontroler and kontroler:FindFirstChildWhichIsA("Animator")
	local saves = m:FindFirstChild("AnimSaves")
	if animator and saves then
		for _, ks in ipairs(saves:GetChildren()) do
			if ks:IsA("KeyframeSequence") then
				local ok, tor = pcall(function()
					local a = Instance.new("Animation")
					a.AnimationId = KSP:RegisterKeyframeSequence(ks)
					return animator:LoadAnimation(a)
				end)
				if ok and tor then
					j.tory[ks.Name] = tor
				end
			end
		end
	end
	local h = Instance.new("Highlight")
	h.Name = "ObrysKomiksowy"
	h.FillTransparency = 1
	h.OutlineColor = Color3.fromRGB(24, 20, 18)
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Adornee = m
	h.Parent = m
	if j.rdzen then
		local l = Instance.new("PointLight")
		l.Name = "SwiatloRdzenia"
		l.Color = KOLOR_SZCZELINY
		l.Range = 10
		l.Brightness = 1.2
		l.Parent = j.rdzen
	end
	return j
end

local function spoczynek(j: Jajko)
	for n, t in pairs(j.tory) do
		if n ~= "spoczynek" then
			t:Stop(0.25)
		end
	end
	local t = j.tory["spoczynek"]
	if t then
		t.Looped = true
		t:Play(0.25)
	end
	if j.slup then
		(j.slup :: BasePart).Transparency = 1
	end
	if j.poswiata then
		(j.poswiata :: BasePart).Transparency = 1
	end
	if j.rdzen then
		(j.rdzen :: BasePart).Color = KOLOR_BLASKU
	end
	tempo, jasnosc = 1.6, 0
end

local function graj(j: Jajko, nazwa: string): number
	local t = j.tory[nazwa]
	if not t then
		return 0
	end
	for n, x in pairs(j.tory) do
		if n ~= nazwa then
			x:Stop(0.05)
		end
	end
	t.Looped = false
	t:Play(0.05)
	return t.Length
end

local function slup(j: Jajko, kolor: Color3)
	local s, p = j.slup, j.poswiata
	if not s or not p then
		return
	end
	local R = j.rozmiarSlupa
	s.Size = Vector3.new(R.X, 0.15, 0.15)
	s.Color = KOLOR_BLASKU
	s.Transparency = 0.05
	TS:Create(s, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Size = R }):Play()
	p.Size = Vector3.new(R.X, 0.2, 0.2)
	p.Color = kolor
	p.Transparency = 0.55
	TS:Create(p, TweenInfo.new(0.45, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
		{ Size = Vector3.new(R.X * 1.05, R.Y * 1.9, R.Z * 1.9) }):Play()
end

local function iskry(j: Jajko, kolor: Color3)
	if not j.rdzen then
		return
	end
	local e = Instance.new("ParticleEmitter")
	e.Color = ColorSequence.new(kolor, KOLOR_SZCZELINY)
	e.LightEmission = 1
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.35), NumberSequenceKeypoint.new(1, 0) })
	e.Speed = NumberRange.new(8, 16)
	e.SpreadAngle = Vector2.new(70, 70)
	e.Lifetime = NumberRange.new(0.6, 1.1)
	e.Acceleration = Vector3.new(0, -14, 0)
	e.Rate = 0
	e.Parent = j.rdzen
	e:Emit(45)
	task.delay(2, function()
		e:Destroy()
	end)
end

------------------------------------------------------------------ napis nad jajkiem po wykluciu
local function napis(j: Jajko, tytul: string, podtytul: string, kolor: Color3)
	local b = Instance.new("BillboardGui")
	b.Name = "WynikJajka"
	b.Size = UDim2.fromScale(7, 2.4)
	b.StudsOffset = Vector3.new(0, 5.5, 0)
	b.AlwaysOnTop = true
	b.Adornee = j.model.PrimaryPart
	local function l(t: string, y: number, h: number, c: Color3)
		local x = Instance.new("TextLabel")
		x.BackgroundTransparency = 1
		x.Size = UDim2.fromScale(1, h)
		x.Position = UDim2.fromScale(0, y)
		x.Text = t
		x.TextScaled = true
		x.TextColor3 = c
		x.FontFace = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
		local s = Instance.new("UIStroke")
		s.Thickness = 3
		s.Color = Color3.fromRGB(26, 20, 16)
		s.Parent = x
		x.Parent = b
	end
	l(tytul, 0, 0.55, Color3.new(1, 1, 1))
	l(podtytul, 0.55, 0.45, kolor)
	b.Parent = player:WaitForChild("PlayerGui")
	local sc = Instance.new("UIScale")
	sc.Scale = 0.4
	sc.Parent = b
	TS:Create(sc, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	task.delay(2.6, function()
		b:Destroy()
	end)
end

local function wyklucie(j: Jajko, wynik: any)
	if zajete then
		return
	end
	zajete = true
	local kolor = Color3.fromHex(wynik.kolor or "FFFFFF")
	-- 1. narastające napięcie
	tempo, jasnosc = 0.45, 0.4
	local d1 = graj(j, "napiecie")
	task.delay(math.max(d1, 1.2) * 0.5, function()
		tempo, jasnosc = 0.18, 0.8
	end)
	task.wait(math.max(d1, 1.2))
	-- 2–3. rozłupywanie i otwarcie rdzenia
	tempo, jasnosc = 0.12, 1
	local d2 = math.max(graj(j, "pekniecie"), 1.6)
	if j.rdzen then
		(j.rdzen :: BasePart).Color = kolor
	end
	task.wait(d2 * 0.42) -- pokrywa odrywa się ok. 22. klatki z 54
	slup(j, kolor)
	iskry(j, kolor)
	napis(j, if wynik.nowy then "NEW PET!" else "PET COPY", string.format("%s · %s", tostring(wynik.nazwa),
		wielkie(tostring(wynik.rzadkoscNazwa or ""))), kolor)
	task.wait(d2 * 0.58 + 1.4)
	spoczynek(j)
	zajete = false
end

------------------------------------------------------------------ podpowiedź z szansami (obrazek panelu petów)
local tablica: BillboardGui? = nil
local etykiety: { [string]: TextLabel } = {}

local function tekst(rodzic: Instance, nazwa: string, x: number, y: number, w: number, h: number, kolor: Color3, mx: number)
	local t = Instance.new("TextLabel")
	t.Name = nazwa
	t.BackgroundTransparency = 1
	t.Position = UDim2.fromScale(x, y)
	t.Size = UDim2.fromScale(w, h)
	t.Text = ""
	t.TextScaled = true
	t.TextColor3 = kolor
	t.FontFace = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
	t.ZIndex = 3
	local c = Instance.new("UITextSizeConstraint")
	c.MaxTextSize = mx
	c.Parent = t
	local s = Instance.new("UIStroke")
	s.Thickness = 2
	s.Color = Color3.fromRGB(26, 20, 16)
	s.Parent = t
	t.Parent = rodzic
	etykiety[nazwa] = t
	return t
end

local function zbudujTablice(punkt: BasePart)
	local b = Instance.new("BillboardGui")
	b.Name = "SzanseJajka"
	b.Size = UDim2.fromScale(3.0, 3.99) -- proporcje grafiki 0,7516
	b.StudsOffset = Vector3.new(3.1, 1.5, 0)
	b.MaxDistance = 24
	b.LightInfluence = 0
	b.Adornee = punkt
	local f = Instance.new("ImageLabel")
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromScale(1, 1)
	f.Image = TABLICA
	f.ImageTransparency = 0.12 -- lekko półprzezroczysta (Paweł)
	f.ScaleType = Enum.ScaleType.Stretch
	f.ZIndex = 1
	f.Parent = b
	-- miejsca z grafiki (ułamki): deska tytułu, 5 rzędów (kółko + pasek), dół: klawisz, cena, kółko na rybkę
	tekst(f, "Tytul", 0.2, 0.035, 0.6, 0.1, Color3.fromHex("FCE3B0"), 30).Text = "FOREST EGG"
	local RZEDY = { 0.25, 0.381, 0.5, 0.619, 0.743 }
	for i, y in ipairs(RZEDY) do
		tekst(f, "Szansa" .. i, 0.115, y - 0.035, 0.12, 0.07, Color3.fromHex("FFD65A"), 16)
		local n = tekst(f, "Pet" .. i, 0.3, y - 0.03, 0.56, 0.06, Color3.new(1, 1, 1), 18)
		n.TextXAlignment = Enum.TextXAlignment.Left
	end
	tekst(f, "PrzyciskE", 0.11, 0.85, 0.11, 0.075, Color3.fromHex("4A2E1A"), 26).Text = "E"
	tekst(f, "Cena", 0.29, 0.852, 0.42, 0.07, Color3.fromHex("FFD65A"), 24)
	local ryb = Instance.new("ImageLabel")
	ryb.BackgroundTransparency = 1
	ryb.Image = RYBKA
	ryb.ScaleType = Enum.ScaleType.Fit
	ryb.Position = UDim2.fromScale(0.785, 0.845)
	ryb.Size = UDim2.fromScale(0.1, 0.08)
	ryb.ZIndex = 3
	ryb.Parent = f
	tekst(f, "Komunikat", 0.05, 0.925, 0.9, 0.05, Color3.new(1, 1, 1), 14)
	b.Parent = player:WaitForChild("PlayerGui")
	tablica = b
end

local F = RS:WaitForChild("JajkoKorowe") :: RemoteFunction
local function odswiezTablice()
	local ok, w = pcall(function()
		return F:InvokeServer("info")
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
		end
	end
	etykiety["Cena"].Text = if type(w.cena) == "number" then tostring(w.cena) else ""
end

local function komunikat(t: string)
	local k = etykiety["Komunikat"]
	if k then
		k.Text = t
		task.delay(2.5, function()
			if k.Text == t then
				k.Text = ""
			end
		end)
	end
end

------------------------------------------------------------------ start
task.spawn(function()
	local k = workspace:WaitForChild("JajkoKorowePodglad", 60)
	local m = k and k:WaitForChild("Jajko korowe", 30)
	local punkt = k and k:WaitForChild("PunktJajka", 60)
	if not (m and m:IsA("Model") and punkt and punkt:IsA("BasePart")) then
		return
	end
	zbudujTablice(punkt)
	odswiezTablice()
	m:WaitForChild("AnimSaves", 10)
	jajko = przygotuj(m)
	spoczynek(jajko :: Jajko)
end)

local Z = RS:WaitForChild("JajkoKoroweZdarzenia") :: RemoteEvent
Z.OnClientEvent:Connect(function(rodzaj, a, b)
	if rodzaj == "wyklucie" and jajko then
		task.spawn(wyklucie, jajko :: Jajko, b)
		if a == player.UserId then
			task.delay(4, odswiezTablice) -- cena następnego jajka
		end
	elseif rodzaj == "odmowa" then
		komunikat(tostring(a))
	end
end)

-- pulsowanie pęknięć
task.spawn(function()
	local t = 0
	while true do
		local dt = task.wait(0.05)
		t += dt
		local j = jajko
		if j then
			local f = (math.sin(t * 2 * math.pi / tempo) + 1) / 2
			local c = KOLOR_SZCZELINY:Lerp(KOLOR_BLASKU, math.clamp(f * 0.55 + jasnosc * 0.45, 0, 1))
			for _, s in ipairs(j.szczeliny) do
				s.Color = c
			end
		end
	end
end)

