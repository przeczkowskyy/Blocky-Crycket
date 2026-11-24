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
-- karta petów (Paweł 24.11 w nocy: „niech wygląda tak jak ta Karola — zwierzaki możliwe do zdobycia, szanse,
-- przycisk i cena”): tło z Higgsfield (job 749940e3, assets/processed/SzanseJajka/KartaPetowJajka.png, 1723 × 2274);
-- dopóki nie jest wgrane (pusty napis) — karta rysuje się ramkami w tym samym układzie
local KARTA = ""
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

local Z = RS:WaitForChild("JajkoKoroweZdarzenia") :: RemoteEvent
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

local tablica: BillboardGui? = nil

------------------------------------------------------------------ scenka otwierania (Paweł 24.11)
-- Tylko u kupującego. Kamera staje przed jajem tak, żeby było widać całe jajo; postać gracza, jego bohater i pet są
-- na ten czas niewidoczne (LocalTransparencyModifier — tylko u tego gracza). HUD i karta petów znikają, u góry
-- i dołu czarne pasy. Jajo NIE pęka samo: gracz klika (mysz, dotyk albo spacja) — każde kliknięcie to szarpnięcie
-- jaja, mocniejszy blask pęknięć, drgnięcie kamery i komiksowy dymek z napisem (CLICK!, CRACK!…); ostatnie kliknięcie
-- to BOOM!: odłamki, pokrywa, słup światła i napis z petem. Bez kliknięcia przez CZEKAJ_S scenka idzie dalej sama
-- (żeby nikt nie utknął). Inni gracze widzą wyklucie od razu w całości.
local KLIKI = 5 -- ile kliknięć otwiera jajo
local CZEKAJ_S = 7
local NAPISY = { "CLICK!", "CRACK!", "TAP!", "CRRRK!", "POP!" }
local KOLORY_DYMKOW = { "FFD23D", "FF7A3D", "7DE36B", "5CC8FF" }
local MIEJSCA = { { 0.27, 0.34 }, { 0.73, 0.3 }, { 0.25, 0.62 }, { 0.75, 0.6 }, { 0.5, 0.2 } }

type Kino = { typ: Enum.CameraType, cf: CFrame, fov: number, gui: ScreenGui, hud: boolean, sterowanie: any,
	ukryte: { BasePart }, klik: BindableEvent, zachecacz: Frame? }

-- komiksowy dymek: gwiazda z trzech obróconych kwadratów z czarnym obrysem, w środku napis (rysowany natywnie)
local function dymek(rodzic: Instance, napisT: string, x: number, y: number, kolor: string, rozmiar: number, trwaly: boolean?): Frame
	local f = Instance.new("Frame")
	f.Name = "Dymek"
	f.BackgroundTransparency = 1
	f.AnchorPoint = Vector2.new(0.5, 0.5)
	f.Position = UDim2.fromScale(x, y)
	f.Size = UDim2.fromScale(rozmiar, rozmiar)
	f.SizeConstraint = Enum.SizeConstraint.RelativeYY
	f.Rotation = math.random(-14, 14)
	f.ZIndex = 5
	for warstwa, dane in ipairs({ { 0.82, "1A1410" }, { 0.72, kolor } }) do
		for _, kat in ipairs({ 0, 30, 60 }) do
			local k = Instance.new("Frame")
			k.BorderSizePixel = 0
			k.AnchorPoint = Vector2.new(0.5, 0.5)
			k.Position = UDim2.fromScale(0.5, 0.5)
			k.Size = UDim2.fromScale(dane[1], dane[1])
			k.Rotation = kat
			k.BackgroundColor3 = Color3.fromHex(dane[2])
			k.ZIndex = 5 + warstwa
			k.Parent = f
		end
	end
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Position = UDim2.fromScale(0.5, 0.5)
	t.Size = UDim2.fromScale(0.78, 0.4)
	t.Text = napisT
	t.TextScaled = true
	t.TextColor3 = Color3.new(1, 1, 1)
	t.FontFace = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
	t.ZIndex = 9
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
		task.delay(0.55, function()
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
	local srodek = j.model:GetPivot().Position
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

-- ujęcie: kamera przed jajem (przód = LookVector korzenia); odległość liczona z rozmiaru modelu, żeby całe jajo
-- (i początek słupa światła) mieściło się w kadrze także po podmianie modelu na większy
local function ujecie(j: Jajko, mnoznik: number, wyzej: number, bok: number): CFrame
	local p = j.model:GetPivot()
	-- wysokość samego jaja z podstawą: bez słupa światła i poświaty (są w modelu cały czas, tylko niewidoczne)
	local dol, gora = math.huge, -math.huge
	for _, c in ipairs(j.model:GetDescendants()) do
		if c:IsA("BasePart") and c ~= j.slup and c ~= j.poswiata and c.Transparency < 1 then
			dol = math.min(dol, c.Position.Y - c.Size.Y / 2)
			gora = math.max(gora, c.Position.Y + c.Size.Y / 2)
		end
	end
	local wys = if gora > dol then math.clamp(gora - dol, 2, 12) else 3
	local przod = Vector3.new(p.LookVector.X, 0, p.LookVector.Z).Unit
	local wBok = przod:Cross(Vector3.yAxis)
	local odl = wys * 1.9 * mnoznik -- przy polu widzenia 50° jajo zajmuje ok. połowę wysokości ekranu
	return CFrame.lookAt(p.Position + przod * odl + wBok * bok + Vector3.new(0, wys * (0.75 + wyzej), 0),
		p.Position + Vector3.new(0, wys * (0.55 + wyzej * 0.6), 0))
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
	if tablica then
		tablica.Enabled = false
	end
	for _, c in ipairs(k.ukryte) do
		c.LocalTransparencyModifier = 1
	end
	k.gui.Name = "KinoJajka"
	k.gui.IgnoreGuiInset = true
	k.gui.DisplayOrder = 50
	k.gui.ResetOnSpawn = false
	-- pole kliknięć na cały ekran (mysz i dotyk)
	local pole = Instance.new("TextButton")
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
	if tablica then
		tablica.Enabled = true
	end
end

-- czeka na kliknięcie (pole ekranu albo spacja); false, gdy minął czas
local function czekajNaKlik(k: Kino): boolean
	local klikniete = false
	local c1 = k.klik.Event:Connect(function()
		klikniete = true
	end)
	local c2 = game:GetService("UserInputService").InputBegan:Connect(function(input)
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
	local d = dymek(k.gui, "CLICK!", 0.8, 0.76, "FFD23D", 0.2, true) -- z boku, nie zasłania jaja
	d.Rotation = -6
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

local function finalWyklucia(j: Jajko, wynik: any, kolor: Color3, kino: Kino?)
	tempo, jasnosc = 0.12, 1
	local d2 = math.max(graj(j, "pekniecie"), 1.6)
	if j.rdzen then
		(j.rdzen :: BasePart).Color = kolor
	end
	if kino then
		local cam = workspace.CurrentCamera
		local baza = ujecie(j, 0.85, 0, 0.6)
		task.spawn(function()
			local t0 = os.clock()
			while os.clock() - t0 < d2 * 0.42 do
				local sila = 0.1 * (os.clock() - t0) / (d2 * 0.42)
				if cam then
					cam.CFrame = baza * CFrame.new((math.random() - 0.5) * sila, (math.random() - 0.5) * sila, 0)
				end
				task.wait()
			end
		end)
	end
	task.wait(d2 * 0.42) -- pokrywa odrywa się ok. 22. klatki z 54
	slup(j, kolor)
	iskry(j, kolor)
	if kino then
		kamera(ujecie(j, 1.35, 0.35, 0), 0.7, Enum.EasingStyle.Back)
	end
	napis(j, if wynik.nowy then "NEW PET!" else "PET COPY", string.format("%s · %s", tostring(wynik.nazwa),
		wielkie(tostring(wynik.rzadkoscNazwa or ""))), kolor)
	task.wait(d2 * 0.58 + 1.6)
end

local function wyklucie(j: Jajko, wynik: any, zKinem: boolean?)
	if zajete then
		return
	end
	zajete = true
	local kolor = Color3.fromHex(wynik.kolor or "FFFFFF")
	local kino: Kino? = nil
	if zKinem then
		local okK, wynikK = pcall(kinoStart, j)
		kino = if okK then wynikK else nil
	end
	if not kino then
		-- inni gracze: całość od razu
		tempo, jasnosc = 0.45, 0.4
		local d1 = math.max(graj(j, "napiecie"), 1.2)
		task.delay(d1 * 0.5, function()
			tempo, jasnosc = 0.18, 0.8
		end)
		task.wait(d1)
		finalWyklucia(j, wynik, kolor, nil)
		spoczynek(j)
		zajete = false
		return
	end
	local k = kino :: Kino
	local okS, blad = pcall(function()
		kamera(ujecie(j, 1.05, 0, 0.9), 0.5)
		task.wait(0.5)
		local napiecie = j.tory["napiecie"]
		local dl = if napiecie then math.max(napiecie.Length, 0.6) else 1.2
		local kawalek = dl / (KLIKI - 1)
		for i = 1, KLIKI - 1 do
			zachecaj(k)
			czekajNaKlik(k)
			-- szarpnięcie: kolejny kawałek klipu napięcia, potem jajo zastyga w tej pozie do następnego kliknięcia
			if napiecie then
				for n, x in pairs(j.tory) do
					if n ~= "napiecie" then
						x:Stop(0.05)
					end
				end
				napiecie.Looped = false
				napiecie:Play(0.03)
				napiecie.TimePosition = (i - 1) * kawalek
				napiecie:AdjustSpeed(1)
				task.delay(kawalek * 0.95, function()
					if napiecie.IsPlaying then
						napiecie:AdjustSpeed(0)
					end
				end)
			end
			tempo = 0.9 - 0.18 * i
			jasnosc = 0.2 * i
			local m = MIEJSCA[(i - 1) % #MIEJSCA + 1]
			dymek(k.gui, NAPISY[(i - 1) % #NAPISY + 1], m[1], m[2], KOLORY_DYMKOW[(i - 1) % #KOLORY_DYMKOW + 1], 0.24 + 0.02 * i)
			-- kamera: krótkie „uderzenie” (bliżej i z powrotem), z każdym kliknięciem ciut bliżej
			local cam = workspace.CurrentCamera
			if cam then
				cam.CFrame = ujecie(j, 1.0 - 0.035 * i, 0, 0.9 - 0.08 * i)
				kamera(ujecie(j, 1.05 - 0.035 * i, 0, 0.9 - 0.08 * i), 0.18, Enum.EasingStyle.Back)
			end
			task.wait(math.max(0.22, kawalek))
		end
		zachecaj(k)
		czekajNaKlik(k)
		if k.zachecacz then
			k.zachecacz:Destroy()
			k.zachecacz = nil
		end
		dymek(k.gui, "BOOM!", 0.5, 0.28, "FF4D3D", 0.36)
		finalWyklucia(j, wynik, kolor, k)
	end)
	if not okS then
		warn("[JajkoKorowe] scenka: " .. tostring(blad))
	end
	spoczynek(j)
	pcall(kinoKoniec, k)
	pcall(function()
		Z:FireServer("koniec")
	end)
	zajete = false
end

------------------------------------------------------------------ podpowiedź z szansami (karta petów)
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

local KOLORY_RZADKOSCI = { "B8C2CC", "6BD66B", "4FB3FF", "C27BFF", "FFC23D" }
local RZEDY = { 0.2, 0.32, 0.442, 0.565, 0.685 } -- góra ramki peta w każdym rzędzie (ułamki karty)
local widoki: { ViewportFrame } = {}

local function napisKarty(rodzic: Instance, nazwa: string, x: number, y: number, w: number, h: number, kolor: string,
	mx: number, gruby: boolean, wyrownanie: Enum.TextXAlignment?): TextLabel
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
	etykiety[nazwa] = t
	return t
end

local function ramka(rodzic: Instance, x: number, y: number, w: number, h: number, kolor: string, rog: number,
	obrys: string?, grubosc: number?): Frame
	local f = Instance.new("Frame")
	f.BorderSizePixel = 0
	f.Position = UDim2.fromScale(x, y)
	f.Size = UDim2.fromScale(w, h)
	f.BackgroundColor3 = Color3.fromHex(kolor)
	f.ZIndex = 2
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(rog, 0)
	c.Parent = f
	if obrys then
		local s = Instance.new("UIStroke")
		s.Color = Color3.fromHex(obrys)
		s.Thickness = grubosc or 2
		s.Parent = f
	end
	f.Parent = rodzic
	return f
end

local function zbudujTablice(punkt: BasePart)
	local b = Instance.new("BillboardGui")
	b.Name = "SzanseJajka"
	b.Size = UDim2.fromScale(3.9, 5.15) -- proporcje tła 0,7577
	b.StudsOffset = Vector3.new(3.7, 1.9, 0)
	b.MaxDistance = 26
	b.LightInfluence = 0
	b.Adornee = punkt
	local f = Instance.new("ImageLabel")
	f.BackgroundTransparency = 1
	f.Size = UDim2.fromScale(1, 1)
	f.Image = KARTA
	f.ScaleType = Enum.ScaleType.Stretch
	f.ZIndex = 1
	f.Parent = b
	if KARTA == "" then
		-- zastępcza karta z ramek (ten sam układ co tło z grafiki)
		ramka(f, 0.01, 0.05, 0.98, 0.94, "7A4B2A", 0.05, "1A1410", 3).ZIndex = 1
		ramka(f, 0.26, 0.01, 0.48, 0.1, "9A6238", 0.2, "1A1410", 3)
		ramka(f, 0.075, 0.135, 0.85, 0.685, "F5E6C8", 0.03, "1A1410", 2)
		for i, y in ipairs(RZEDY) do
			ramka(f, 0.115, y, 0.14, 0.1, "3A2A22", 0.12, KOLORY_RZADKOSCI[i], 3)
		end
		ramka(f, 0.105, 0.845, 0.125, 0.09, "F1E3C4", 0.15, "1A1410", 2)
		ramka(f, 0.265, 0.845, 0.47, 0.09, "9A6238", 0.2, "1A1410", 2)
		ramka(f, 0.775, 0.845, 0.12, 0.09, "9A6238", 0.5, "1A1410", 2)
	end
	local tytul = napisKarty(f, "Tytul", 0.28, 0.022, 0.44, 0.075, "FCE3B0", 80, true)
	tytul.Text = "FOREST EGG"
	local st = Instance.new("UIStroke")
	st.Thickness = 2.5
	st.Color = Color3.fromRGB(26, 20, 16)
	st.Parent = tytul
	for i, y in ipairs(RZEDY) do
		-- zwierzak w ramce (model 3D z klocków Karola), obok: szansa, nazwa i umiejętność — jak na tablicy Karola
		local v = Instance.new("ViewportFrame")
		v.Name = "Pet" .. i .. "Widok"
		v.BackgroundTransparency = 1
		v.Position = UDim2.fromScale(0.123, y + 0.006)
		v.Size = UDim2.fromScale(0.124, 0.088)
		v.Ambient = Color3.fromRGB(200, 200, 200)
		v.LightColor = Color3.new(1, 1, 1)
		v.ZIndex = 3
		v.Parent = f
		widoki[i] = v
		napisKarty(f, "Szansa" .. i, 0.275, y + 0.006, 0.16, 0.055, "2B2118", 60, true, Enum.TextXAlignment.Left)
		napisKarty(f, "Pet" .. i, 0.44, y + 0.004, 0.45, 0.058, "2B2118", 60, false, Enum.TextXAlignment.Left)
		napisKarty(f, "Skill" .. i, 0.275, y + 0.062, 0.61, 0.034, "6B4A2E", 40, false, Enum.TextXAlignment.Left)
	end
	napisKarty(f, "PrzyciskE", 0.115, 0.855, 0.105, 0.07, "4A2E1A", 80, true).Text = "E"
	local cena = napisKarty(f, "Cena", 0.28, 0.858, 0.44, 0.065, "FFD65A", 80, true)
	local sc = Instance.new("UIStroke")
	sc.Thickness = 2.5
	sc.Color = Color3.fromRGB(26, 20, 16)
	sc.Parent = cena
	local ryb = Instance.new("ImageLabel")
	ryb.BackgroundTransparency = 1
	ryb.Image = RYBKA
	ryb.ScaleType = Enum.ScaleType.Fit
	ryb.Position = UDim2.fromScale(0.782, 0.85)
	ryb.Size = UDim2.fromScale(0.106, 0.08)
	ryb.ZIndex = 4
	ryb.Parent = f
	local kom = napisKarty(f, "Komunikat", 0.08, 0.79, 0.84, 0.035, "8A1F1F", 26, false)
	kom.ZIndex = 5
	b.Parent = player:WaitForChild("PlayerGui")
	tablica = b
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

local F = RS:WaitForChild("JajkoKorowe") :: RemoteFunction
local pokazane: { [number]: string } = {}
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
			etykiety["Skill" .. i].Text = sz.skill or ""
			if pokazane[i] ~= sz.pet and widoki[i] then
				pokazane[i] = sz.pet
				pokazPeta(widoki[i], sz.pet)
			end
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

Z.OnClientEvent:Connect(function(rodzaj, a, b)
	if rodzaj == "wyklucie" and jajko then
		task.spawn(wyklucie, jajko :: Jajko, b, a == player.UserId)
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

