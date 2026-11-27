--[[
	TreningAFKClient — okno i animacje treningu AFK (D-141; na main od 24.11). Serwer: src/server/TreningAFK.server.luau.

	Trzecia wersja (Paweł 23.11): pasek w procentach, płynny; okno z grafik Glossy Ink (D.obrazy, wgrane 23.11 po „tak”); postać naprawdę ćwiczy:
		Siła — hantle w obu dłoniach, uginanie ramion na zmianę;
		HP (Kondycja) — leży na ławce i wyciska sztangę;
		Zręczność — bieg na bieżni (taśma się przesuwa);
		Inteligencja — stoi z otwartą książką i przewraca kartki;
		Pancerz — NPC rzuca pomidorami, postać zasłania się tarczą;
		Szczęście — potrząsa kubkiem i rzuca kości na stolik.
	Klikać nie trzeba; skill check (okrągły przycisk) daje chwilowe ×2.

	Animacje są PROCEDURALNE (bez wgrywania): co klatkę ustawiamy Transform stawów R15 (nazwy Root, Waist, Neck,
	*Shoulder, *Elbow, *Wrist, *Hip, *Knee, *Ankle) — działa na każdym szkielecie R15: na bohaterze klasy z pakietu
	Karola (Workspace/BohaterSwiat/BohaterowieLokalni, stawy Motor6D, jego pętla ma priorytet Last — nasza Last+1,
	więc nadpisujemy pozę tylko w czasie treningu, bez zmian w jego plikach), na awatarze (AnimationConstraint) i na
	modelach ras (ten sam szkielet). Bieg na bohaterze gra jego własny klip "bieg" przez umowę RuchBohatera.
	Agent Karola, sesja 25.11: stanowiska w sali Training Center (TreningAFKDane.miejsca); na czas treningu broń bohatera
	schowana, a narzędzie awatara w plecaku; sztanga i książka liczone z wymiarów postaci (kot ma krótkie łapy i szatę).
	Ograniczenie: pozę i ruch rekwizytów widzi tylko trenujący gracz — dla innych graczy trzeba będzie te same ruchy
	wgrać jako animacje Roblox (osobna zgoda na wgranie).
	Agent Karola, 27.11 (polecenie Pawła: sklep u trenera): długość paska przychodzi z serwera ("start", …, pasek,
	wzmocnienie_s — ulepszenie stanowiska skraca pasek), nad panelem licznik wzmacniacza; okno trenera ma dwie zakładki:
	TRAIN (sześć ćwiczeń) i SHOP (ulepszenia stanowisk i wzmacniacze ×2 za Rybki — cenę i saldo liczy serwer).
	Agent Karola, 27.11 wieczorem (Karol: „animacje na bieżni nie działają: bieżnia się rusza, ale ludek stoi w miejscu.
	Tak samo ze sztangą — słabo się podnosi”): awatar Robloxa ma dziś stawy AnimationConstraint, a jego Animator co klatkę
	nadpisuje ich Transform — pozy z pętli renderowania nie docierały do ciała (ani do kota Pawła, który je kopiuje).
	Na czas treningu Animator awatara jest odpięty (wraca po treningu), pozy idą też w PreSimulation, a celowanie dłoni
	liczy stawy AnimationConstraint z ich zaczepów. Kot rasy z podglądu Pawła (Workspace/KotyRasSwiatLokalne/<gracz>) jest
	osobnym rodzajem szkieletu: pozy liczone z jego wymiarów, rekwizyty w jego łapach, te same Transform także na
	stawach awatara (kot Pawła je kopiuje). Bieg ma własną pozę na każdym szkielecie (krok w rytmie taśmy), sztanga pełny
	ruch z przytrzymaniem na górze. Szczęście (Karol: „niech też rzuca się prawdziwymi kośćmi”): przez cały pasek
	potrząsanie kubkiem, na końcu paska rzut — kości lądują oczkami z serwera do góry, potem „+N LUCK”.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TS = game:GetService("TweenService")
local RunService = game:GetService("RunService")

local D = require(RS:WaitForChild("Shared"):WaitForChild("TreningAFKDane"))
local Z = RS:WaitForChild("TreningAFK") :: RemoteEvent
local player = Players.LocalPlayer

local FONT = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
local CIEMNY = Color3.fromRGB(26, 20, 16)

local function obrys(rodzic: Instance, grubosc: number)
	local s = Instance.new("UIStroke")
	s.Color = CIEMNY
	s.Thickness = grubosc
	s.Parent = rodzic
	return s
end
local function rog(rodzic: Instance, r: number)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r, 0)
	c.Parent = rodzic
end
local function napis(rodzic: Instance, nazwa: string, pos: UDim2, size: UDim2, kolor: Color3): TextLabel
	local t = Instance.new("TextLabel")
	t.Name = nazwa
	t.BackgroundTransparency = 1
	t.Position, t.Size = pos, size
	t.FontFace = FONT
	t.TextScaled = true
	t.TextColor3 = kolor
	t.Text = ""
	obrys(t, 2)
	t.Parent = rodzic
	return t
end

------------------------------------------------------------ okno (grafiki Glossy Ink z D.obrazy; układ zmierzony na panelu 1024 × 404)
local gui = Instance.new("ScreenGui")
gui.Name = "TreningAFK"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = true
gui.DisplayOrder = 15
gui.Enabled = false

local panel = Instance.new("ImageLabel")
panel.Name = "Panel"
panel.Image = D.obrazy.panel
panel.BackgroundTransparency = 1
panel.ScaleType = Enum.ScaleType.Fit
panel.AnchorPoint = Vector2.new(0.5, 1)
panel.Position = UDim2.new(0.5, 0, 1, -10)
panel.Size = UDim2.fromScale(0.4, 0.4)
panel.Parent = gui
local ar = Instance.new("UIAspectRatioConstraint")
ar.AspectRatio = 1024 / 404
ar.Parent = panel
local mx = Instance.new("UISizeConstraint")
mx.MinSize = Vector2.new(320, 0)
mx.MaxSize = Vector2.new(580, 230)
mx.Parent = panel

local function ulamek(x, y, w, h)
	return UDim2.fromScale(x, y), UDim2.fromScale(w, h)
end

-- tabliczka u góry: nazwa statystyki
local tp, ts = ulamek(0.112, 0.03, 0.293, 0.15)
local tytul = napis(panel, "Tytul", tp, ts, Color3.fromRGB(252, 227, 176))
-- ikona stanowiska, czynność, przyrost
local ikona = Instance.new("ImageLabel")
ikona.Name = "Ikona"
ikona.BackgroundTransparency = 1
ikona.ScaleType = Enum.ScaleType.Fit
ikona.Position, ikona.Size = ulamek(0.05, 0.22, 0.1, 0.3)
ikona.Parent = panel
local cp, cs = ulamek(0.17, 0.25, 0.4, 0.2)
local czynnoscL = napis(panel, "Czynnosc", cp, cs, Color3.new(1, 1, 1))
czynnoscL.TextXAlignment = Enum.TextXAlignment.Left
local pp, psz = ulamek(0.56, 0.27, 0.36, 0.16)
local przyrostL = napis(panel, "Przyrost", pp, psz, Color3.fromRGB(140, 232, 101))
przyrostL.TextXAlignment = Enum.TextXAlignment.Right

-- tor paska (ciemny tor jest w grafice panelu); wypełnienie NATYWNE (Paweł 23.11: obrazek paska się pikselował):
-- zaokrąglona ramka z gradientem zieleni (jasna góra → ciemny dół), czarnym obrysem i połyskiem — jak w makiecie Figmy
local tor = Instance.new("Frame")
tor.Name = "Tor"
tor.BackgroundTransparency = 1
tor.Position, tor.Size = ulamek(0.0684, 0.5941, 0.7471, 0.2277)
tor.Parent = panel
local wyp = Instance.new("Frame")
wyp.Name = "Wypelnienie"
wyp.BackgroundColor3 = Color3.new(1, 1, 1)
wyp.BorderSizePixel = 0
wyp.AnchorPoint = Vector2.new(0, 0.5)
wyp.Position = UDim2.new(0, 5, 0.5, 0)
wyp.Size = UDim2.new(0, 0, 0.78, 0)
wyp.Parent = tor
rog(wyp, 0.5)
local grad = Instance.new("UIGradient")
grad.Rotation = 90
grad.Color = ColorSequence.new({
	ColorSequenceKeypoint.new(0, Color3.fromRGB(158, 242, 89)),
	ColorSequenceKeypoint.new(0.55, Color3.fromRGB(92, 212, 56)),
	ColorSequenceKeypoint.new(1, Color3.fromRGB(46, 158, 41)),
})
grad.Parent = wyp
local wypObrys = Instance.new("UIStroke")
wypObrys.Color = CIEMNY
wypObrys.Thickness = 2.5
wypObrys.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
wypObrys.Parent = wyp
local polysk = Instance.new("Frame")
polysk.Name = "Polysk"
polysk.BackgroundColor3 = Color3.new(1, 1, 1)
polysk.BackgroundTransparency = 0.45
polysk.BorderSizePixel = 0
polysk.Position = UDim2.new(0.5, 0, 0.14, 0)
polysk.AnchorPoint = Vector2.new(0.5, 0)
polysk.Size = UDim2.new(1, -14, 0.22, 0)
polysk.Parent = wyp
rog(polysk, 0.5)
local liczba = napis(tor, "Liczba", UDim2.fromScale(0, 0.05), UDim2.fromScale(1, 0.9), Color3.new(1, 1, 1))
liczba.ZIndex = 3

-- STOP we wnęce po prawej (czerwony przycisk z grafiki, napis natywnie)
local stop = Instance.new("ImageButton")
stop.Name = "Stop"
stop.BackgroundTransparency = 1
stop.Image = D.obrazy.stop
stop.ScaleType = Enum.ScaleType.Fit
stop.Position, stop.Size = ulamek(0.835, 0.565, 0.112, 0.285)
stop.Parent = panel
local stopL = napis(stop, "Napis", UDim2.fromScale(0.08, 0.2), UDim2.fromScale(0.84, 0.6), Color3.new(1, 1, 1))
stopL.Text = "STOP"
stopL.ZIndex = 3

-- podpowiedź na desce, nad paskiem
local hp, hs = ulamek(0.17, 0.46, 0.66, 0.11)
local podp = napis(panel, "Podpowiedz", hp, hs, Color3.fromRGB(255, 236, 180))
podp.Text = "HIT THE SKILL CHECKS FOR 2X SPEED!"
-- agent Karola, 27.11 (limit treningu, TreningAFKDane.limitNaPoziom): ponad limitem podpowiedź mówi, że trzeba awansować
local PODPOWIEDZ, KOLOR_PODPOWIEDZI = podp.Text, podp.TextColor3
local function pokazLimit(ponad: boolean)
	podp.Text = if ponad then D.tekstLimitu else PODPOWIEDZ
	podp.TextColor3 = if ponad then Color3.fromRGB(255, 120, 100) else KOLOR_PODPOWIEDZI
end

-- skill check: złota moneta z pięścią + „2X”, wokół kurczący się pierścień
local check = Instance.new("ImageButton")
check.Name = "SkillCheck"
check.AnchorPoint = Vector2.new(0.5, 0.5)
check.Size = UDim2.fromScale(0.11, 0.11)
check.BackgroundTransparency = 1
check.Image = D.obrazy.skillCheck
check.ScaleType = Enum.ScaleType.Fit
check.Visible = false
check.ZIndex = 20
check.Parent = gui
local ca = Instance.new("UIAspectRatioConstraint")
ca.Parent = check
local mc = Instance.new("UISizeConstraint")
mc.MinSize = Vector2.new(72, 72) -- duży cel także na telefonie
mc.Parent = check
local dwaX = napis(check, "Napis2x", UDim2.fromScale(0.2, 0.58), UDim2.fromScale(0.6, 0.26), Color3.new(1, 1, 1))
dwaX.Text = "2X"
dwaX.ZIndex = 22
local pierscien = Instance.new("Frame")
pierscien.Name = "Pierscien"
pierscien.AnchorPoint = Vector2.new(0.5, 0.5)
pierscien.Position = UDim2.fromScale(0.5, 0.5)
pierscien.BackgroundTransparency = 1
pierscien.ZIndex = 19
pierscien.Parent = check
rog(pierscien, 0.5)
local ps = Instance.new("UIStroke")
ps.Color = Color3.new(1, 1, 1)
ps.Thickness = 3
ps.Parent = pierscien

gui.Parent = player:WaitForChild("PlayerGui")

------------------------------------------------------------ stan
local aktywne: string? = nil
local postep = 0 -- w powtórzeniach, płynnie liczony u gracza między wiadomościami serwera
local tempo = 1
local pokazanyProcent = 0
-- agent Karola, 27.11: sklep trenera — pasek z serwera (ulepszenie stanowiska), wzmacniacz ×2 z licznikiem nad panelem
local pasekReps = D.powtorzenNaPasek
local wzmDo = 0 -- os.clock() końca wzmacniacza statystyki trenowanej teraz
local wzmL = napis(panel, "Wzmocnienie", UDim2.fromScale(0.2, -0.17), UDim2.fromScale(0.6, 0.15), Color3.fromRGB(255, 214, 90))
wzmL.Visible = false

local function rysuj(dt: number)
	local cel = math.clamp(postep / pasekReps, 0, 1)
	-- żwawe, płynne dociąganie do celu (nie skacze przy poprawkach z serwera)
	if cel < pokazanyProcent - 0.5 then
		pokazanyProcent = cel -- nowy pasek po pełnym
	else
		pokazanyProcent += (cel - pokazanyProcent) * math.min(1, dt * 14)
	end
	-- szerokość w pikselach: pasek nie jest węższy niż wysoki (zaokrąglone końce z grafiki), przy 0% znika
	local szer = tor.AbsoluteSize.X - 10
	local wys = wyp.AbsoluteSize.Y
	wyp.Visible = pokazanyProcent > 0.01
	wyp.Size = UDim2.new(0, math.max(wys, pokazanyProcent * szer), 0.78, 0)
	liczba.Text = string.format("%d%%", math.floor(pokazanyProcent * 100 + 0.5)) .. (if tempo > 1 then "  x" .. tostring(tempo) else "")
	local zostalo = wzmDo - os.clock()
	local s = aktywne and D.stanowisko(aktywne)
	wzmL.Visible = zostalo > 0 and s ~= nil
	if wzmL.Visible and s then
		wzmL.Text = string.format("%s X%d  %d:%02d", s.skrot, D.sklep.wzmacniacze.mnoznik, math.floor(zostalo / 60),
			math.floor(zostalo % 60))
	end
end

-- agent Karola, 27.11: duzy = większy i dłużej na ekranie (wynik rzutu kośćmi)
local function wyskok(tekst: string, kolor: Color3, duzy: boolean?)
	local t = napis(gui, "Wyskok", UDim2.new(0.5, 0, 0.72, 0), if duzy then UDim2.fromScale(0.42, 0.12) else UDim2.fromScale(0.3, 0.08),
		kolor)
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Text = tekst
	t.Rotation = math.random(-6, 6)
	local czas = if duzy then 1.9 else 1.1
	TS:Create(t, TweenInfo.new(czas, if duzy then Enum.EasingStyle.Quint else Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Position = UDim2.new(0.5, 0, 0.58, 0), TextTransparency = 1 }):Play()
	task.delay(czas + 0.1, function()
		t:Destroy()
	end)
end

------------------------------------------------------------ szkielet: bohater Karola albo awatar
local STAWY = { "Root", "Waist", "Neck", "LeftShoulder", "LeftElbow", "LeftWrist", "RightShoulder", "RightElbow", "RightWrist",
	"LeftHip", "LeftKnee", "LeftAnkle", "RightHip", "RightKnee", "RightAnkle" }
local CZY_STAW = {}
for _, n in ipairs(STAWY) do
	CZY_STAW[n] = true
end

-- agent Karola, 27.11: lustro = stawy awatara, na które idą te same Transform, gdy widać kota Pawła (on je kopiuje)
type Rig = { model: Model, rodzaj: string, stawy: { [string]: any }, lustro: { [string]: any }?, korzen: BasePart?,
	dlonL: BasePart?, dlonP: BasePart? }
local rig: Rig? = nil

local function zbierzStawy(model: Model): { [string]: any }
	local stawy = {}
	for _, d in ipairs(model:GetDescendants()) do
		if (d:IsA("Motor6D") or d:IsA("AnimationConstraint")) and CZY_STAW[d.Name] and stawy[d.Name] == nil then
			stawy[d.Name] = d
		end
	end
	return stawy
end

-- agent Karola, 27.11: kot rasy z podglądu Pawła (KotRasySwiatClient, tylko odczyt): model lokalny o nazwie gracza
local function kotPawla(hrp: BasePart): Model?
	local f = workspace:FindFirstChild("KotyRasSwiatLokalne")
	local m = f and f:FindFirstChild(player.Name)
	local r = m and m:IsA("Model") and m:FindFirstChild("HumanoidRootPart") :: BasePart?
	if m and r and (r.Position - hrp.Position).Magnitude < 10 then
		return m :: Model
	end
	return nil
end

local function ruchBohatera(): BindableFunction?
	local k = workspace:FindFirstChild("BohaterSwiat")
	local s = k and k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild("RuchBohatera")
	return if f and f:IsA("BindableFunction") then f else nil
end

local function znajdzRig(): Rig?
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not (char and hrp) then
		return nil
	end
	local model: Model = char
	local rodzaj = "awatar"
	local k = workspace:FindFirstChild("BohaterSwiat")
	local lok = k and k:FindFirstChild("BohaterowieLokalni")
	local ruch = ruchBohatera()
	local stanB = ruch and ruch:Invoke("stan")
	if lok and stanB then
		local naj, odl = nil, 10
		for _, m in ipairs(lok:GetChildren()) do
			local r = m:IsA("Model") and m:FindFirstChild("HumanoidRootPart") :: BasePart?
			if r and (r.Position - hrp.Position).Magnitude < odl then
				naj, odl = m, (r.Position - hrp.Position).Magnitude
			end
		end
		if naj then
			model, rodzaj = naj, "bohater"
		end
	end
	local lustro: { [string]: any }? = nil
	local kot = if rodzaj == "awatar" then kotPawla(hrp) else nil
	if kot then
		model, rodzaj, lustro = kot, "kot", zbierzStawy(char)
	end
	return {
		model = model,
		rodzaj = rodzaj,
		stawy = zbierzStawy(model),
		lustro = lustro,
		korzen = model:FindFirstChild("HumanoidRootPart") :: BasePart?,
		dlonL = model:FindFirstChild("LeftHand") :: BasePart?,
		dlonP = model:FindFirstChild("RightHand") :: BasePart?,
	}
end

local animateWylaczony: LocalScript? = nil
-- agent Karola, 27.11: Animator awatara odpięty na czas treningu — przy stawach AnimationConstraint nadpisywał co klatkę
-- Transform (próba w Play 27.11: wpis w pętli renderowania nie ruszał dłoni, po odpięciu Animatora — ruszał)
local animatorOdpiety: Animator? = nil
local animatorHum: Humanoid? = nil
local function przejmijAwatara(r: Rig)
	if r.rodzaj == "bohater" then
		return
	end
	local char = player.Character
	if not char then
		return
	end
	local a = char:FindFirstChild("Animate")
	if a and a:IsA("LocalScript") and not a.Disabled then
		a.Disabled = true
		animateWylaczony = a
	end
	local hum = char:FindFirstChildOfClass("Humanoid")
	local an = hum and hum:FindFirstChildOfClass("Animator")
	if hum and an then
		for _, tr in ipairs(an:GetPlayingAnimationTracks()) do
			tr:Stop(0)
		end
		animatorOdpiety, animatorHum = an, hum
		an.Parent = nil
	end
end

local function zerujStawy(stawy: { [string]: any }?)
	for _, j in pairs(stawy or {}) do
		pcall(function()
			j.Transform = CFrame.identity
		end)
	end
end

local function oddajSzkielet(r: Rig?)
	if animatorOdpiety then
		if animatorHum and animatorHum.Parent then
			animatorOdpiety.Parent = animatorHum
		end
		animatorOdpiety, animatorHum = nil, nil
	end
	if animateWylaczony then
		animateWylaczony.Disabled = false
		animateWylaczony = nil
	end
	if r then
		zerujStawy(r.stawy)
		zerujStawy(r.lustro)
	end
	local ruch = ruchBohatera()
	if ruch then
		pcall(function()
			ruch:Invoke("klip", nil)
			ruch:Invoke("przesun", nil)
		end)
	end
end

------------------------------------------------------------ agent Karola, sesja 25.11: nic w łapach, dłonie na rekwizycie
-- (1) Na czas treningu broń znika: u bohatera lokalnie (LocalTransparencyModifier) modele przedmiotów z kategorii
-- „Weapons” (moduł przymierzalni Workspace/StrojeProba/Moduly/DaneStrojow; bez niego — modele przyspawane do dłoni albo
-- do StaffPivot), narzędzie awatara idzie do plecaka. Po treningu wszystko wraca.
-- (2) Kot ma krótkie łapy (zasięg ok. 0,75 st od barku) i grubą szatę, więc kąty „na oko” wkładały sztangę w ubranie,
-- a książkę w głowę. Dłonie celują teraz w punkt w układzie UpperTorso: dwa odcinki ramienia z długości ze stawów Motor6D
-- (bark może wysunąć się do przodu o ≤ 0,5 st, gdy łapa nie sięga), a punkt liczy się z grubości klatki z ubraniem
-- i dołu głowy tej postaci (rasa, klasa i strój mają różne wymiary).
local bronCzesci: { BasePart } = {}
local bronModel: Model? = nil
local odlozoneNarzedzie: Tool? = nil
local przedmiotyStrojow: any = nil

local function czyBron(m: Model): boolean
	if przedmiotyStrojow == nil then
		przedmiotyStrojow = false
		local sp = workspace:FindFirstChild("StrojeProba")
		local md = sp and sp:FindFirstChild("Moduly")
		local dane = md and md:FindFirstChild("DaneStrojow")
		if dane and dane:IsA("ModuleScript") then
			local ok, d = pcall(require, dane)
			if ok and type(d) == "table" and type(d.przedmioty) == "table" then
				przedmiotyStrojow = d.przedmioty
			end
		end
	end
	local p = przedmiotyStrojow and przedmiotyStrojow[m.Name]
	if p then
		return p.kategoria == "Weapons"
	end
	for _, d in ipairs(m:GetDescendants()) do
		local p0 = d:IsA("JointInstance") and d.Part0
		if p0 and (p0.Name == "StaffPivot" or p0.Name == "RightHand" or p0.Name == "LeftHand") then
			return true
		end
	end
	return false
end

local function schowajBron(r: Rig)
	if r.rodzaj ~= "awatar" and (bronModel ~= r.model or (bronCzesci[1] and bronCzesci[1].Parent == nil)) then
		bronModel = r.model
		bronCzesci = {}
		for _, m in ipairs(r.model:GetChildren()) do
			-- agent Karola, 27.11: broń kota Pawła to model „Bron” w kocie
			if m:IsA("Model") and (if r.rodzaj == "kot" then m.Name == "Bron" else czyBron(m)) then
				for _, p in ipairs(m:GetDescendants()) do
					if p:IsA("BasePart") then
						table.insert(bronCzesci, p)
					end
				end
			end
		end
	end
	for _, p in ipairs(bronCzesci) do
		p.LocalTransparencyModifier = 1
	end
	local char = player.Character
	local narz = char and char:FindFirstChildOfClass("Tool")
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if narz and hum then
		odlozoneNarzedzie = narz
		hum:UnequipTools()
	end
end

local function oddajBron(r: Rig?)
	-- części bohatera mają wspólną przezroczystość lokalną (pętla bohatera): bierzemy ją z widocznej części ciała
	local ltm = 0
	if r and #bronCzesci > 0 then
		for _, d in ipairs(r.model:GetDescendants()) do
			if d:IsA("BasePart") and d.Transparency < 1 and not table.find(bronCzesci, d) then
				ltm = d.LocalTransparencyModifier
				break
			end
		end
	end
	for _, p in ipairs(bronCzesci) do
		p.LocalTransparencyModifier = ltm
	end
	bronCzesci, bronModel = {}, nil
	local narz = odlozoneNarzedzie
	odlozoneNarzedzie = nil
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if narz and hum and narz.Parent == player:FindFirstChildOfClass("Backpack") then
		hum:EquipTool(narz)
	end
end

type Miary = { klatka: number, glowaDol: number, wysTulowia: number, bark: Vector3, zasieg: number }
local miary: Miary? = nil

-- agent Karola, 27.11: staw jako para C0 / C1 — Motor6D wprost, AnimationConstraint z zaczepów (awatar Robloxa ma dziś
-- takie stawy; Attachment1 = Attachment0 * Transform, czyli to samo co C0 * Transform * C1⁻¹ w Motor6D)
type Staw = { C0: CFrame, C1: CFrame }
local function staw(r: Rig, n: string): Staw?
	local j = r.stawy[n]
	if j and j:IsA("Motor6D") then
		return { C0 = j.C0, C1 = j.C1 }
	elseif j and j:IsA("AnimationConstraint") and j.Attachment0 and j.Attachment1 then
		return { C0 = j.Attachment0.CFrame, C1 = j.Attachment1.CFrame }
	end
	return nil
end

local function dlugosciRamienia(r: Rig, strona: string): (number, number)
	local sh, el, wr = staw(r, strona .. "Shoulder"), staw(r, strona .. "Elbow"), staw(r, strona .. "Wrist")
	if not (sh and el and wr) then
		return 1, 1.1
	end
	return (el.C0.Position - sh.C1.Position).Magnitude, (wr.C0.Position - el.C1.Position).Magnitude + wr.C1.Position.Magnitude
end

-- wymiary w układzie UpperTorso (−Z = przód): przód klatki z ubraniem, dół głowy, wysokość tułowia, bark, zasięg łapy
local function zmierz(r: Rig): Miary
	local M: Miary = { klatka = 0.6, glowaDol = 0.75, wysTulowia = 1.6, bark = Vector3.new(1.5, 0.5, 0), zasieg = 2 }
	local ut = r.model:FindFirstChild("UpperTorso") :: BasePart?
	local sh, szyja, pas = staw(r, "RightShoulder"), staw(r, "Neck"), staw(r, "Waist")
	if not ut then
		return M
	end
	if sh then
		M.bark = sh.C0.Position
		local a, b = dlugosciRamienia(r, "Right")
		M.zasieg = a + b
	end
	M.wysTulowia = if szyja and pas then szyja.C0.Y - pas.C1.Y else ut.Size.Y
	local function rogi(korzen: BasePart, f: (Vector3) -> ())
		local lista = korzen:GetDescendants()
		table.insert(lista, korzen)
		for _, p in ipairs(lista) do
			if p:IsA("BasePart") and p.Transparency < 1 then
				local cf = ut.CFrame:ToObjectSpace(p.CFrame)
				local h = p.Size / 2
				for _, s in ipairs({ Vector3.new(1, 1, 1), Vector3.new(1, 1, -1), Vector3.new(1, -1, 1), Vector3.new(1, -1, -1),
					Vector3.new(-1, 1, 1), Vector3.new(-1, 1, -1), Vector3.new(-1, -1, 1), Vector3.new(-1, -1, -1) }) do
					f(cf * (h * s))
				end
			end
		end
	end
	local przod = 0
	rogi(ut, function(q)
		przod = math.max(przod, -q.Z)
	end)
	if przod > 0 then
		M.klatka = przod
	end
	local glowa = r.model:FindFirstChild("Head") :: BasePart?
	if glowa then
		local dol = math.huge
		rogi(glowa, function(q)
			dol = math.min(dol, q.Y)
		end)
		if dol < math.huge then
			M.glowaDol = dol
		end
	end
	return M
end

-- dłoń w punkcie cel (układ UpperTorso): Transform barku (wysunięcie + pochylenie + odwiedzenie) i łokcia
local function celuj(r: Rig, strona: string, cel: Vector3, maxWysun: number): (CFrame?, CFrame?)
	local sh = staw(r, strona .. "Shoulder")
	if not sh then
		return nil, nil
	end
	local L1, L2 = dlugosciRamienia(r, strona)
	local v = cel - sh.C0.Position
	local zasieg = (L1 + L2) * 0.98
	local wysun = Vector3.zero
	if v.Magnitude > zasieg then
		wysun = v.Unit * math.min(v.Magnitude - zasieg, maxWysun)
		v -= wysun
	end
	local d = math.max(v.Magnitude, math.abs(L1 - L2) + 0.01)
	local u = v.Unit
	local odw = math.asin(math.clamp(u.X, -1, 1))
	local poch = math.atan2(-u.Z, -u.Y)
	local zgiecie = math.pi - math.acos(math.clamp((L1 * L1 + L2 * L2 - d * d) / (2 * L1 * L2), -1, 1))
	local alfa = math.atan2(L2 * math.sin(zgiecie), L1 + L2 * math.cos(zgiecie))
	return CFrame.new(wysun) * CFrame.Angles(poch - alfa, 0, odw), CFrame.Angles(zgiecie, 0, 0)
end

-- agent Karola, 26.11: książka większa i dalej od ciała. Pomiar u Kota-Maga (próba w Play): książka 0,98 × 0,67 st
-- (skala 0,45) siedziała 0,9 st przed klatką, w środku wielkich mankietów rękawów (nachodziła na nie do 0,18 st), a u
-- wojownika obracająca się kartka wchodziła w tułów i głowę (do 0,48 st). Teraz: dolna krawędź przed ubraniem klatki,
-- nisko pod brodą, książka pochylona 50° (strony ku twarzy), łapy trzymają dolne rogi od strony stron (pierścień
-- mankietu leży wtedy nad stroną, nie przecina jej), skala z wysokości tułowia (kot 0,85 st → 0,85; człowiek 1,5 → 1,08).
-- Kartka (3/4 szerokości strony) przewraca się, „zwijając się” w połowie obrotu (krótsza w poprzek), żeby nie zahaczać
-- o twarz ani o mankiety rękawów przy łapach (sprawdzone w Play na Kocie-Magu, wojowniku, zwiadowcy i awatarze).
local KSIAZKA_TH = math.rad(50) -- nachylenie od poziomu (strony ku twarzy)
local KARTKA_SZER = 0.75 -- szerokość przewracanej kartki względem strony
local KARTKA_ZWIJA = 0.7 -- o ile krótsza w poprzek jest kartka w połowie obrotu
local function ukladKsiazki(M: Miary): (CFrame, number)
	local k = M.wysTulowia
	local s = math.clamp(0.55 + 0.35 * k, 0.6, 1.3) -- skala książki (1 = 2,1 × 1,5 st)
	local pol = 0.75 * s -- połowa długości (grzbiet wzdłuż Z książki; +Z = dolna krawędź, bliżej ciała)
	local yD = M.bark.Y - 0.55 * k -- dolna krawędź: nisko pod brodą
	local zD = -(M.klatka + 0.35 * k) -- … i przed ubraniem klatki
	local c = Vector3.new(0, yD + pol * math.sin(KSIAZKA_TH), zD - pol * math.cos(KSIAZKA_TH))
	return CFrame.new(c) * CFrame.Angles(KSIAZKA_TH, 0, 0), s
end

-- agent Karola, 27.11 (Karol: „ze sztangą — słabo się podnosi”): jedno powtórzenie = wyciśnięcie (0–0,3, szybko,
-- z wyhamowaniem), przytrzymanie na wyprostowanych ramionach (do 0,45), wolniejsze opuszczanie (do 0,9) i chwila na
-- klatce → wysokość 0 (klatka) … 1 (wyprost)
local function wyciskanie(f: number): number
	if f < 0.3 then
		return 1 - (1 - f / 0.3) ^ 2
	elseif f < 0.45 then
		return 1
	elseif f < 0.9 then
		return 0.5 + 0.5 * math.cos(math.pi * (f - 0.45) / 0.45)
	end
	return 0
end

-- sztanga: odległość dłoni od środka tułowia ku niebu (dół: gryf dotyka ubrania klatki, góra = ramiona prawie proste;
-- krótkie łapy kota — co najmniej 0,6 st ruchu, bark wysuwa się wtedy do 0,5 st)
local function torSztangi(M: Miary, f: number): number
	local dol = M.klatka + 0.18
	local gora = math.max(dol + 0.6, M.zasieg * 0.97)
	return dol + (gora - dol) * wyciskanie(f)
end

------------------------------------------------------------ rekwizyty stanowiska
local stanowiskoM: Model? = nil
local bazowe: { [Instance]: CFrame } = {} -- Model (PivotTo) albo BasePart → pozycja z serwera
local lokalne: { Instance } = {} -- części tworzone u gracza (pomidor w locie, plamy)

local function grupa(nazwa: string): Model?
	local m = stanowiskoM and stanowiskoM:FindFirstChild(nazwa, true)
	return if m and m:IsA("Model") then m else nil
end
local function zapamietajGrupe(m: Model?)
	if m and bazowe[m] == nil then
		bazowe[m] = m:GetPivot()
	end
end
local rozmiary: { [BasePart]: Vector3 } = {} -- agent Karola, 26.11: części, którym zmieniamy rozmiar (kartka książki)
local function przywrocRekwizyty()
	for i, cf in pairs(bazowe) do
		if i.Parent and i:IsA("Model") then
			if i:GetScale() ~= 1 then
				i:ScaleTo(1) -- agent Karola, sesja 25.11: książka zmniejszona do wzrostu postaci wraca do rozmiaru
			end
			i:PivotTo(cf)
			for _, p in ipairs(i:GetDescendants()) do -- agent Karola, 27.11: kości schowane w kubku znów widać
				if p:IsA("BasePart") then
					p.LocalTransparencyModifier = 0
				end
			end
		end
	end
	-- agent Karola, 26.11: części po modelach (kartka leży w grupie Kartka — PivotTo grupy przesunąłby ją jeszcze raz)
	for i, cf in pairs(bazowe) do
		if i.Parent and i:IsA("BasePart") then
			if rozmiary[i] then
				i.Size = rozmiary[i]
			end
			i.CFrame = cf
			i.LocalTransparencyModifier = 0
		end
	end
	bazowe = {}
	rozmiary = {}
	for _, p in ipairs(lokalne) do
		p:Destroy()
	end
	lokalne = {}
	stanowiskoM = nil
end

-- środek maty stanowiska (układ o z serwera: Mata leży w o * (0, 0.15, 0))
local function ukladO(): CFrame
	local mata = stanowiskoM and stanowiskoM.PrimaryPart
	return if mata then mata.CFrame * CFrame.new(0, -0.15, 0) else CFrame.identity
end

------------------------------------------------------------ pozy (kąty w stopniach, oś X: + = do przodu dla rąk i nóg)
local function R(x: number, y: number?, z: number?): CFrame
	return CFrame.Angles(math.rad(x), math.rad(y or 0), math.rad(z or 0))
end
local function dzwon(f: number): number -- 0 → 1 → 0 w jednym powtórzeniu
	return math.sin(math.pi * math.clamp(f, 0, 1))
end

-- agent Karola, 27.11: bieg w rytmie taśmy — faza kroku i droga taśmy narastają w pętli (zmiana tempa nie szarpie)
local TASMA = 7 -- st/s taśmy przy tempie 1
local KADENCJA = 1.35 -- cykli biegu na sekundę przy tempie 1 (dwa kroki na cykl → krok ok. 2,6 st taśmy)
local fazaBiegu = 0
local drogaTasmy = 0

-- agent Karola, 27.11: rzut kośćmi Szczęścia (wyniki z serwera); czasy w s od zdarzenia "punkt"
type RzutKosci = { wyniki: { number }, t0: number, cele: { CFrame }, obroty: { Vector3 }, pokazano: boolean, ile: number }
local rzutKosci: RzutKosci? = nil
local KOSC_WYLOT, KOSC_LAD, KOSC_SPOCZYNEK = 0.14, 0.74, 0.98 -- kość wylatuje z kubka, ląduje, nieruchomieje (wynik)
local KOSC_ZBIERA, KOSC_W_KUBKU = 2.8, 3.15 -- kości wracają do kubka

local POZY: { [string]: (f: number, t: number, r: Rig, M: Miary) -> { [string]: CFrame } } = {
	Sila = function(f)
		local p = if f < 0.5 then dzwon(f * 2) else 0
		local l = if f >= 0.5 then dzwon(f * 2 - 1) else 0
		return {
			RightShoulder = R(12 * p, 0, 10), RightElbow = R(18 + 122 * p), RightWrist = R(-10 * p),
			LeftShoulder = R(12 * l, 0, -10), LeftElbow = R(18 + 122 * l), LeftWrist = R(-10 * l),
			Waist = R(0, 6 * (p - l), 0), Neck = R(-4),
		}
	end,
	Kondycja = function(f, _, r, M)
		-- ręce do nieba (do przodu ciała), dłonie prosto nad barkami; agent Karola, sesja 25.11: dół ruchu nad klatką
		-- z ubraniem (sztanga nie wchodzi w szatę), dłonie trochę szerzej niż barki, poniżej linii barków (nie w brodzie)
		local d = torSztangi(M, f)
		local x, y = math.abs(M.bark.X) + 0.12 * M.wysTulowia, M.bark.Y - 0.12 * M.wysTulowia
		local bP, lP = celuj(r, "Right", Vector3.new(x, y, -d), 0.5)
		local bL, lL = celuj(r, "Left", Vector3.new(-x, y, -d), 0.5)
		if not (bP and bL) then
			-- szkielet bez zaczepów stawów: dawna poza (agent Karola, 27.11: ten sam rytm co tor sztangi)
			local a = 62 * (1 - wyciskanie(f))
			bP, lP, bL, lL = R(90 - a, 0, 8 + a * 0.25), R(2 * a), R(90 - a, 0, -8 - a * 0.25), R(2 * a)
		end
		return {
			RightShoulder = bP, RightElbow = lP, RightWrist = R(-15),
			LeftShoulder = bL, LeftElbow = lL, LeftWrist = R(-15),
			RightHip = R(8), LeftHip = R(8), RightKnee = R(-14), LeftKnee = R(-14),
			Neck = R(6),
		}
	end,
	Zrecznosc = function(_, _, _, M)
		-- agent Karola, 27.11 (Karol: „bieżnia się rusza, ale ludek stoi w miejscu”): prawdziwy bieg na każdym szkielecie
		-- — noga w przód (biodro), w fazie przenoszenia mocno zgięte kolano, przy odbiciu prawie proste; ręce zgięte
		-- pracują naprzemiennie z nogami, tułów lekko pochylony i skręca się z krokiem, dwa podskoki na cykl
		local fi = fazaBiegu
		local function noga(faza: number): (number, number, number)
			local s, c = math.sin(faza), math.cos(faza)
			return 46 * s, -(10 + 88 * math.max(0, c) ^ 1.2), 14 * c -- biodro, kolano, kostka
		end
		local hP, kP, aP = noga(fi)
		local hL, kL, aL = noga(fi + math.pi)
		local s = math.sin(fi)
		local podskok = 0.12 * M.wysTulowia * math.abs(math.cos(fi)) -- kot ok. 0,1 st, człowiek ok. 0,2 st
		return {
			Root = CFrame.new(0, podskok - 0.04 * M.wysTulowia, 0) * R(-9),
			Waist = R(-4, -10 * s, 0), Neck = R(8, 8 * s, 0),
			RightHip = R(hP), RightKnee = R(kP), RightAnkle = R(aP),
			LeftHip = R(hL), LeftKnee = R(kL), LeftAnkle = R(aL),
			RightShoulder = R(-55 * s, 0, 8), LeftShoulder = R(55 * s, 0, -8),
			RightElbow = R(95 + 15 * s), LeftElbow = R(95 - 15 * s),
			RightWrist = R(-10), LeftWrist = R(-10),
		}
	end,
	Inteligencja = function(f, _, r, M)
		-- agent Karola, 26.11: łapy na dolnych rogach książki, od strony stron (ukladKsiazki); głowa lekko pochylona
		local kiw = math.sin(f * math.pi * 2) * 3
		local cf, s = ukladKsiazki(M)
		local x = 0.9 * 1.05 * s -- prawie przy zewnętrznej krawędzi okładki
		local y = 0.36 * math.sqrt(M.wysTulowia / 0.85) -- łapa nad stroną (kot 0,36; człowiek ok. 0,48)
		local z = 0.75 * s - 0.25 * s -- ćwierć skali w górę od dolnej krawędzi
		local bP, lP = celuj(r, "Right", (cf * CFrame.new(x, y, z)).Position, 0.5)
		local bL, lL = celuj(r, "Left", (cf * CFrame.new(-x, y, z)).Position, 0.5)
		if not (bP and bL) then
			-- szkielet bez Motor6D (awatar na AnimationConstraint): ręce przed sobą, dłonie pod dolnymi rogami książki
			bP, lP, bL, lL = R(55, 0, -8), R(40), R(55, 0, 8), R(40)
		end
		return {
			RightShoulder = bP, RightElbow = lP, RightWrist = R(-10),
			LeftShoulder = bL, LeftElbow = lL, LeftWrist = R(-10),
			Neck = R(-12 + kiw), Waist = R(-4),
		}
	end,
	Pancerz = function(f)
		-- tarcza przed sobą; uderzenie pomidora w 0,55 → odrzut
		local odrzut = if f > 0.55 and f < 0.8 then dzwon((f - 0.55) / 0.25) else 0
		return {
			LeftShoulder = R(82 - 14 * odrzut, 0, 30), LeftElbow = R(72 + 10 * odrzut),
			RightShoulder = R(14, 0, 10), RightElbow = R(35),
			Waist = R(5 * odrzut, -8, 0), Neck = R(-6),
			RightHip = R(-6), LeftHip = R(14), LeftKnee = R(-18), RightKnee = R(-8),
		}
	end,
	Szczescie = function(_, t)
		-- agent Karola, sesja 25.11: kubek przed klatką, nie przy twarzy (było bark 50 / łokieć 75), rzut łapą w przód i w dół
		-- na niższy stolik. Agent Karola, 27.11: przez cały pasek potrząsanie kubkiem; rzut tylko na końcu paska (zdarzenie
		-- "punkt" z wynikiem z serwera), potem ręka czeka, aż kości wrócą do kubka
		local bark, lokiec, nadg = 38, 50, 0
		local u = if rzutKosci then os.clock() - rzutKosci.t0 else math.huge
		if u < KOSC_WYLOT then
			local k = u / KOSC_WYLOT
			bark, lokiec = 38 + 36 * k, 50 - 40 * k -- rzut
		elseif u < KOSC_WYLOT + 0.4 then
			local k = (u - KOSC_WYLOT) / 0.4
			bark, lokiec = 74 - 36 * k, 10 + 40 * k -- powrót
		elseif u >= KOSC_W_KUBKU then
			nadg = 25 * math.sin(t * math.pi * 7) -- potrząsanie kubkiem (3,5 na sekundę)
			lokiec = 50 + 6 * math.sin(t * math.pi * 7 + 1)
		end
		return {
			RightShoulder = R(bark, 0, 6), RightElbow = R(lokiec), RightWrist = R(nadg),
			LeftShoulder = R(10, 0, -8), LeftElbow = R(20), Neck = R(-10),
		}
	end,
}

------------------------------------------------------------ rekwizyty w ruchu
local pomidorLot: BasePart? = nil

-- agent Karola, 27.11: kości Szczęścia — widoczność u gracza, obrót kładący ściankę wyniku do góry, cel na blacie
local function widocznosc(m: Instance, ltm: number)
	for _, p in ipairs(m:GetDescendants()) do
		if p:IsA("BasePart") then
			p.LocalTransparencyModifier = ltm
		end
	end
end

-- obrót w układzie kości, po którym ścianka o wartości w patrzy w górę (+Y); ścianki z D.kosci.sciany (jak na serwerze)
local function obrotWyniku(w: number): CFrame
	for _, sc in ipairs(D.kosci.sciany) do
		if sc.w == w then
			if sc.n.Y > 0.5 then
				return CFrame.identity
			elseif sc.n.Y < -0.5 then
				return CFrame.Angles(math.pi, 0, 0)
			end
			return CFrame.fromAxisAngle(sc.n:Cross(Vector3.yAxis).Unit, math.pi / 2)
		end
	end
	return CFrame.identity
end

local function rzucKosciU(wyniki: { number }, ile: number)
	local o = ukladO()
	local n = #wyniki
	local cele, obroty = {}, {}
	for i, w in ipairs(wyniki) do
		local x = (i - (n + 1) / 2) * 0.85 + (math.random() - 0.5) * 0.3
		local z = -2.6 + (math.random() - 0.5) * 0.6
		cele[i] = o * CFrame.new(x, 2.25 + D.kosci.bok / 2, z) * CFrame.Angles(0, math.random() * math.pi * 2, 0) * obrotWyniku(w)
		obroty[i] = Vector3.new(math.random(4, 7) * math.pi, math.random(3, 6) * math.pi, math.random(4, 7) * math.pi)
	end
	rzutKosci = { wyniki = wyniki, t0 = os.clock(), cele = cele, obroty = obroty, pokazano = false, ile = ile }
end

-- po wylądowaniu (kość leży ścianką wyniku do góry): na ekranie duże „+N LUCK” i drgnięcie panelu
local function pokazWynikKosci(rz: RzutKosci)
	local s = D.stanowisko(D.kosci.stanowisko)
	wyskok("+" .. tostring(rz.ile) .. " " .. (if s then s.nazwa else "LUCK"), if s then s.kolor else Color3.new(1, 1, 1), true)
	local sc = panel:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
	sc.Parent = panel
	sc.Scale = 1.06
	TS:Create(sc, TweenInfo.new(0.18), { Scale = 1 }):Play()
end

local function wDloni(dlon: BasePart?, przes: CFrame): CFrame?
	return dlon and dlon.CFrame * CFrame.new(0, -dlon.Size.Y / 2 - 0.15, 0) * przes
end

local function plama(pozycja: Vector3)
	for _ = 1, 6 do
		local p = Instance.new("Part")
		p.Shape = Enum.PartType.Ball
		p.Size = Vector3.one * 0.25
		p.Color = Color3.fromRGB(214, 50, 40)
		p.CanCollide = false
		p.CanQuery = false
		p.Position = pozycja
		p.AssemblyLinearVelocity = Vector3.new(math.random(-8, 8), math.random(4, 10), math.random(-8, 8))
		p.Parent = workspace
		table.insert(lokalne, p)
		task.delay(0.8, function()
			p:Destroy()
		end)
	end
end

local function ruszRekwizyty(f: number, t: number, r: Rig)
	local o = ukladO()
	local id = aktywne
	if id == "Sila" then
		local L, P = grupa("Hantla_L"), grupa("Hantla_P")
		zapamietajGrupe(L)
		zapamietajGrupe(P)
		local cl, cp = wDloni(r.dlonL, CFrame.identity), wDloni(r.dlonP, CFrame.identity)
		if L and cl then
			L:PivotTo(cl)
		end
		if P and cp then
			P:PivotTo(cp)
		end
	elseif id == "Kondycja" then
		local g = grupa("Sztanga")
		zapamietajGrupe(g)
		if g and r.dlonL and r.dlonP and r.korzen then
			-- agent Karola, sesja 25.11: sztanga w dłoniach od strony nieba i nigdy bliżej klatki niż ubranie + 0,25
			local srodek = (r.dlonL.Position + r.dlonP.Position) / 2 + r.korzen.CFrame.LookVector * 0.1
			local ut = r.model:FindFirstChild("UpperTorso") :: BasePart?
			if ut and miary then
				local p = ut.CFrame:PointToObjectSpace(srodek)
				if -p.Z < miary.klatka + 0.25 then
					srodek = ut.CFrame:PointToWorldSpace(Vector3.new(p.X, p.Y, -(miary.klatka + 0.25)))
				end
			end
			local prawo = r.korzen.CFrame.RightVector
			g:PivotTo(CFrame.fromMatrix(srodek, prawo, r.korzen.CFrame.UpVector))
		end
	elseif id == "Zrecznosc" then
		-- paski taśmy jadą do tyłu (+Z układu o) 7 st/s × tempo i wracają na przód
		for i = 1, 6 do
			local p = stanowiskoM and stanowiskoM:FindFirstChild("Tasma_" .. i, true) :: BasePart?
			if p then
				if bazowe[p] == nil then
					bazowe[p] = p.CFrame
				end
				local z0 = -2.6 + (i - 1) * 1.0
				-- agent Karola, 27.11: droga taśmy narasta w pętli (TASMA × tempo), w tym samym rytmie co kroki biegu
				p.CFrame = o * CFrame.new(0, 0.84, ((z0 + 2.8 + drogaTasmy) % 6) - 2.8)
			end
		end
	elseif id == "Inteligencja" then
		local k, kart = grupa("Ksiazka"), grupa("Kartka")
		zapamietajGrupe(k)
		zapamietajGrupe(kart)
		local ut = r.model:FindFirstChild("UpperTorso") :: BasePart?
		if k and ut and miary then
			-- agent Karola, 26.11: książka przed klatką, dolna krawędź w łapach (ukladKsiazki), skala z wymiarów postaci
			local uk, skala = ukladKsiazki(miary)
			if math.abs(k:GetScale() - skala) > 0.01 then
				k:ScaleTo(skala)
			end
			local cf = ut.CFrame * uk
			k:PivotTo(cf)
			local ark = kart and kart:FindFirstChild("Arkusz") :: BasePart?
			if kart and ark then
				-- kartka przewraca się z prawej na lewą w drugiej połowie powtórzenia; w połowie obrotu jest krótsza
				-- w poprzek (zwija się), więc nie wchodzi w twarz. Grupa zostaje w skali 1 — rozmiar kartki ustawiamy sami
				if rozmiary[ark] == nil then
					rozmiary[ark] = ark.Size
					bazowe[ark] = ark.CFrame
				end
				local kat = if f < 0.5 then 0 elseif f < 0.9 then math.pi * ((f - 0.5) / 0.4) else math.pi
				local os_ = cf * CFrame.new(0, 0.09 * skala, 0) * CFrame.Angles(0, 0, kat)
				kart:PivotTo(os_)
				local w = 0.92 * skala * KARTKA_SZER * (1 - KARTKA_ZWIJA * math.sin(kat))
				ark.Size = Vector3.new(w, 0.03 * skala, 1.32 * skala)
				ark.CFrame = os_ * CFrame.new(w / 2 + 0.01 * skala, 0, 0)
			end
		end
	elseif id == "Pancerz" then
		local tarcza, ramie = grupa("Tarcza"), grupa("Rzucajacy_Ramie")
		zapamietajGrupe(tarcza)
		zapamietajGrupe(ramie)
		local srodekTarczy: Vector3? = nil
		if tarcza and r.dlonL and r.korzen then
			local pos = r.dlonL.Position + r.korzen.CFrame.LookVector * 0.5
			local cf = CFrame.new(pos) * r.korzen.CFrame.Rotation * CFrame.Angles(0, math.rad(90), 0)
			tarcza:PivotTo(cf)
			srodekTarczy = pos + r.korzen.CFrame.LookVector * 0.2
		end
		if ramie then
			-- zamach (0–0,25) i rzut (0,25–0,35)
			local kat = if f < 0.25 then -130 * (f / 0.25) elseif f < 0.35 then -130 + 200 * ((f - 0.25) / 0.1) else 70 * (1 - math.clamp((f - 0.35) / 0.4, 0, 1))
			ramie:PivotTo(bazowe[ramie] * CFrame.Angles(math.rad(kat), 0, 0))
			local wReku = ramie:FindFirstChild("Pomidor w ręce") :: BasePart?
			if wReku then
				wReku.LocalTransparencyModifier = if f > 0.32 and f < 0.9 then 1 else 0
			end
			-- pomidor w locie 0,32 → 0,55, potem plama
			if f > 0.32 and f < 0.55 and srodekTarczy and wReku then
				if not pomidorLot then
					local p = Instance.new("Part")
					p.Shape = Enum.PartType.Ball
					p.Size = Vector3.one * 0.6
					p.Color = Color3.fromRGB(214, 50, 40)
					p.Anchored = true
					p.CanCollide = false
					p.CanQuery = false
					p.Parent = workspace
					table.insert(lokalne, p)
					pomidorLot = p
				end
				local k = (f - 0.32) / 0.23
				local start = bazowe[ramie].Position + Vector3.new(0, 1.2, 0)
				local poz = start:Lerp(srodekTarczy, k) + Vector3.new(0, 3 * math.sin(math.pi * k), 0)
				;(pomidorLot :: BasePart).CFrame = CFrame.new(poz)
			elseif pomidorLot and f >= 0.55 then
				plama(pomidorLot.Position)
				pomidorLot:Destroy()
				pomidorLot = nil
			end
		end
	elseif id == "Szczescie" then
		local kub = grupa("Kubek")
		zapamietajGrupe(kub)
		local cp = wDloni(r.dlonP, CFrame.new(0, 0.2, 0))
		if kub and cp then
			kub:PivotTo(cp)
		end
		-- agent Karola, 27.11 (Karol: „niech też rzuca się prawdziwymi kośćmi, wypadają prawdziwe wyniki”): przez pasek
		-- kości są w kubku (schowane); po "punkt" lecą na stolik, koziołkując coraz wolniej, i lądują ścianką wyniku
		-- z serwera do góry (rz.cele), po chwili wracają do kubka
		local rz = rzutKosci
		local u = if rz then os.clock() - rz.t0 else math.huge
		local n = math.max(if rz then #rz.wyniki else 0, (D.kosciRzutu()))
		for i = 1, n do
			local g = grupa("Kosc_" .. i)
			zapamietajGrupe(g)
			local cel = rz and rz.cele[i]
			if g and cp then
				if not (rz and cel) or u < KOSC_WYLOT or u >= KOSC_W_KUBKU then
					g:PivotTo(cp * CFrame.new(0, 0.3, 0))
					widocznosc(g, 1)
				elseif u < KOSC_LAD then
					local k = (u - KOSC_WYLOT) / (KOSC_LAD - KOSC_WYLOT)
					local rem = (1 - k) ^ 2
					local a = rz.obroty[i]
					local poz = cp.Position:Lerp(cel.Position, k) + Vector3.new(0, 1.1 * math.sin(math.pi * k), 0)
					g:PivotTo(CFrame.new(poz) * cel.Rotation * CFrame.Angles(a.X * rem, a.Y * rem, a.Z * rem))
					widocznosc(g, 0)
				elseif u < KOSC_SPOCZYNEK then
					local k = (u - KOSC_LAD) / (KOSC_SPOCZYNEK - KOSC_LAD)
					g:PivotTo(cel + Vector3.new(0, 0.22 * math.sin(math.pi * k) * (1 - k), 0)) -- odbicie od blatu
					widocznosc(g, 0)
				elseif u < KOSC_ZBIERA then
					g:PivotTo(cel)
					widocznosc(g, 0)
				else
					local k = (u - KOSC_ZBIERA) / (KOSC_W_KUBKU - KOSC_ZBIERA)
					local poz = cel.Position:Lerp(cp.Position, k) + Vector3.new(0, 0.6 * math.sin(math.pi * k), 0)
					g:PivotTo(CFrame.new(poz) * cel.Rotation)
					widocznosc(g, if k > 0.85 then 1 else 0)
				end
			end
		end
		if rz and not rz.pokazano and u >= KOSC_SPOCZYNEK then
			rz.pokazano = true
			pokazWynikKosci(rz)
		end
	end
end

------------------------------------------------------------ pętla animacji (po pętli bohatera Karola)
local czas = 0
local ruchStoi = 0
local ostatniePozy: { [string]: CFrame }? = nil
local TEMPO_POZY = { Kondycja = 1 / 1.6 } -- agent Karola, 27.11: ruchów na powtórzenie paska (domyślnie 1)

-- agent Karola, 27.11: stawy AnimationConstraint (awatar) przyjmują Transform w PreSimulation — po kroku Animatora;
-- ta sama poza co w pętli renderowania jeszcze raz (Motor6D bohatera i kota rysują się z pętli renderowania)
RunService.PreSimulation:Connect(function()
	local r, cele = rig, ostatniePozy
	if not (aktywne and r and cele) then
		return
	end
	for _, lista in ipairs({ r.stawy, r.lustro or {} }) do
		for n, j in pairs(lista) do
			if j:IsA("AnimationConstraint") then
				j.Transform = cele[n] or CFrame.identity
			end
		end
	end
end)

RunService:BindToRenderStep("TreningAFK", Enum.RenderPriority.Last.Value + 1, function(dt)
	if not aktywne then
		return
	end
	czas += dt
	postep = math.min(postep + dt * tempo / D.czasPowtorzenia, pasekReps - 0.001)
	fazaBiegu = (fazaBiegu + dt * math.pi * 2 * KADENCJA * tempo) % (math.pi * 2) -- agent Karola, 27.11
	drogaTasmy = (drogaTasmy + dt * TASMA * tempo) % 6
	rysuj(dt)
	-- agent Karola, 27.11: kot Pawła powstaje po wyborze rasy — gdy pojawi się w trakcie treningu, szkielet od nowa
	if rig and rig.rodzaj == "awatar" and rig.korzen and kotPawla(rig.korzen) then
		oddajBron(rig)
		zerujStawy(rig.stawy) -- Animate i Animator awatara zostają wyłączone (ten sam gracz)
		rig = nil
	end
	if not rig or not rig.model.Parent then
		rig = znajdzRig()
		if rig then
			przejmijAwatara(rig)
			miary = zmierz(rig) -- agent Karola, sesja 25.11
		end
	end
	local r = rig
	if not r then
		return
	end
	-- agent Karola, 27.11: wyciskanie sztangi wolniej niż jedno powtórzenie paska (ok. 1,9 s na ruch — czytelny)
	local f = (postep * (TEMPO_POZY[aktywne :: string] or 1)) % 1
	-- agent Karola, 27.11: bieg ma własną pozę na każdym szkielecie (klip "bieg" bohatera nie ruszał nóg na kotwicy)
	schowajBron(r) -- agent Karola, sesja 25.11: nic w łapach na czas treningu
	local poza = POZY[aktywne :: string]
	if poza then
		local cele = poza(f, czas, r, miary or zmierz(r))
		ostatniePozy = cele
		for n, j in pairs(r.stawy) do
			j.Transform = cele[n] or CFrame.identity
		end
		for n, j in pairs(r.lustro or {}) do -- kot Pawła kopiuje pozę ze stawów awatara
			j.Transform = cele[n] or CFrame.identity
		end
	end
	-- bohater leży na ławce razem z postacią (jego pętla trzyma go pionowo)
	if r.rodzaj == "bohater" and aktywne == "Kondycja" and r.korzen then
		local char = player.Character
		local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
		if hrp then
			r.korzen.CFrame = hrp.CFrame * CFrame.new(0, -0.6, 0)
		end
	end
	ruszRekwizyty(f, czas, r)
	-- ruch gałką / WASD = zejście ze stanowiska
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if hum and hum.MoveDirection.Magnitude > 0.2 then
		ruchStoi += dt
		if ruchStoi > 0.15 then
			ruchStoi = -10
			Z:FireServer("stop")
		end
	else
		ruchStoi = math.min(ruchStoi, 0) + 0
		if ruchStoi < 0 then
			ruchStoi = math.min(0, ruchStoi + dt * 20)
		end
	end
end)

------------------------------------------------------------ skill check
local numerCheck: number? = nil
local function schowajCheck()
	numerCheck = nil
	check.Visible = false
end
check.Activated:Connect(function()
	if numerCheck then
		Z:FireServer("check", numerCheck)
		schowajCheck()
	end
end)

------------------------------------------------------------ zdarzenia z serwera
local function koniec()
	oddajBron(rig) -- agent Karola, sesja 25.11
	miary = nil
	ostatniePozy = nil -- agent Karola, 27.11
	rzutKosci = nil
	oddajSzkielet(rig)
	przywrocRekwizyty()
	rig = nil
	schowajCheck()
	aktywne = nil
	gui.Enabled = false
	wzmDo = 0
	-- agent Karola, 27.11: po ławce (Kondycja) Humanoid zostawał ok. 1 s w FallingDown i postać się ślizgała — wstaje od razu
	local hum = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	if hum and hum:GetState() == Enum.HumanoidStateType.FallingDown then
		hum:ChangeState(Enum.HumanoidStateType.GettingUp)
	end
end

-- agent Karola, 27.11: Szczęście pokazuje zakres rzutu („+1-6 LCK / ROLL”), reszta przyrost za pasek
local function tekstPrzyrostu(s: any, mnoznik: number): string
	if s.id == D.kosci.stanowisko then
		local liczba, scianki = D.kosciRzutu()
		return string.format("+%d-%d %s / ROLL", math.floor(liczba * mnoznik + 0.5), math.floor(liczba * scianki * mnoznik + 0.5),
			s.skrot)
	end
	return "+" .. tostring(mnoznik) .. " " .. s.skrot .. " / BAR"
end

Z.OnClientEvent:Connect(function(akcja, a, b, c, d, e, f)
	if akcja == "start" then
		koniec()
		aktywne = a
		local s = D.stanowisko(a)
		local k = workspace:FindFirstChild("TreningAFK")
		stanowiskoM = k and k:FindFirstChild(a)
		postep, tempo, czas = b or 0, 1, 0
		pasekReps = if typeof(d) == "number" and d > 0 then d else D.powtorzenNaPasek -- agent Karola, 27.11: sklep
		wzmDo = if typeof(e) == "number" and e > 0 then os.clock() + e else 0
		pokazLimit(f == true) -- agent Karola, 27.11: limit treningu
		pokazanyProcent = math.clamp(postep / pasekReps, 0, 1)
		tytul.Text = s and s.nazwa or "TRAINING"
		czynnoscL.Text = s and s.czynnosc or ""
		ikona.Image = s and s.ikona or ""
		przyrostL.Text = s and tekstPrzyrostu(s, c or 1) or ""
		gui.Enabled = true
		ruchStoi = -10 -- chwila na puszczenie klawiszy po wejściu
	elseif akcja == "postep" then
		postep, tempo = a, b or 1
	elseif akcja == "punkt" then
		local s = aktywne and D.stanowisko(aktywne)
		postep = c or 0
		if typeof(d) == "number" and d > 0 then -- agent Karola, 27.11: limit treningu zmienia długość paska
			pasekReps = d
		end
		pokazLimit(e == true)
		pokazanyProcent = 1
		-- agent Karola, 27.11: Szczęście — f = oczka z serwera; rzut na stolik, „+N LUCK” dopiero po wylądowaniu kości
		local kosci = if s and s.id == D.kosci.stanowisko and typeof(f) == "table" and #f > 0 then f else nil
		if kosci then
			local suma = 0
			for _, v in ipairs(kosci) do
				suma += if typeof(v) == "number" then v else 0
			end
			rzucKosciU(kosci, b or suma)
			if s and suma > 0 and typeof(b) == "number" then -- przyrost po końcu wzmacniacza wraca do zwykłego
				przyrostL.Text = tekstPrzyrostu(s, math.max(1, math.floor(b / suma + 0.5)))
			end
		else
			wyskok("+" .. tostring(b) .. " " .. (s and s.skrot or ""), s and s.kolor or Color3.new(1, 1, 1))
			if s then -- agent Karola, 27.11: przyrost po końcu wzmacniacza wraca do zwykłego
				przyrostL.Text = tekstPrzyrostu(s, b)
			end
			local sc = panel:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
			sc.Parent = panel
			sc.Scale = 1.06
			TS:Create(sc, TweenInfo.new(0.18), { Scale = 1 }):Play()
		end
		task.delay(0.12, function()
			pokazanyProcent = 0
		end)
	elseif akcja == "skillcheck" then
		numerCheck = a
		local okno = b or 1.2
		check.Position = UDim2.fromScale(0.3 + math.random() * 0.4, 0.25 + math.random() * 0.3)
		check.Visible = true
		pierscien.Size = UDim2.fromScale(2.2, 2.2)
		TS:Create(pierscien, TweenInfo.new(okno, Enum.EasingStyle.Linear), { Size = UDim2.fromScale(1, 1) }):Play()
		local moj = a
		task.delay(okno + 0.1, function()
			if numerCheck == moj then
				schowajCheck()
			end
		end)
	elseif akcja == "trafiony" then
		tempo = D.mnoznikSkillCheck
		wyskok("x" .. tostring(D.mnoznikSkillCheck) .. " SPEED!", Color3.fromRGB(255, 214, 90))
	elseif akcja == "koniec" then
		koniec()
	end
end)

stop.Activated:Connect(function()
	Z:FireServer("stop")
end)

------------------------------------------------------------ okno trenera (agent Karola, 26.11, polecenie Karola)
--[[ E przy trenerze w Training Center (pakiet bazaru woła ReplicatedStorage.OknoMiejsca:Fire(D.trener.miejsce)) otwiera
	okno sześciu ćwiczeń: ikona i nazwa statystyki, czynność, obecna wartość gracza, w kolorze stanowiska; stanowisko
	zajęte przez kogoś innego (atrybut Zajete z serwera) — szare z napisem BUSY. Klik = "wybierz", id; serwer sprawdza
	odległość od trenera i stawia gracza na stanowisku tak jak E przy macie ("start" zamyka okno). Zamykanie: X,
	przycisk B pada, Escape, stuknięcie obok okna, odejście od trenera dalej niż D.trener.zasieg.
	Układ w pikselach z rozmiaru ekranu (bez paska Robloxa): poziomo 3 × 2 kafelki, pionowo 2 × 3. Telefon 667 × 375
	(pasek 36): okno 635 × 315, kafelek 199 × 121 px; przy pasku 58 — 199 × 110; pionowo 375 × 667 — 157 × 100.
	Agent Karola, 27.11 (polecenie Pawła: „u trenera … panel sklepu/ulepszeń”): w nagłówku dwie zakładki (TRAIN, SHOP,
		każda ≥ 44 px). SHOP: sześć kafelków stanowisk (ten sam układ siatki) z poziomem ulepszenia i dwoma przyciskami
		(ulepszenie za Rybki, wzmacniacz ×2 na 10 min za Rybki; przycisk ≥ 44 px wysokości). Klik = "kup", rodzaj, id —
		cenę, saldo, odległość od trenera i limit liczy serwer; stan sklepu przychodzi jako "sklep". Tytuł w SHOP pokazuje
		saldo Rybek. ]]
local GuiService = game:GetService("GuiService")
local UIS = game:GetService("UserInputService")

local function bindable(nazwa: string): BindableEvent
	local e = RS:FindFirstChild(nazwa)
	if not e then
		e = Instance.new("BindableEvent")
		e.Name = nazwa
		e.Parent = RS
	end
	return e :: BindableEvent
end
local okna = bindable("OknoMiejsca")
okna:SetAttribute(D.trener.miejsce, true) -- okno jest: bazar nie pokazuje dymka trenera

local ZLOTY = Color3.fromRGB(252, 227, 176)
local NAPIS_MENU = "CHOOSE YOUR TRAINING"
local MENU = { pasek = 52, margines = 10, odstep = 8, maksSzer = 640, maksWys = 380, brzegX = 16, brzegY = 12,
	zakladka = 124, przycisk = 44 }
local NAPIS_SKLEPU = "SHOP"

local menu = Instance.new("ScreenGui")
menu.Name = "TreningAFKMenu"
menu.ResetOnSpawn = false
menu.IgnoreGuiInset = false -- okno pod paskiem Robloxa
menu.DisplayOrder = 16
menu.Enabled = false
menu:SetAttribute("Otwarte", false)

local tlo = Instance.new("TextButton") -- stuknięcie obok okna zamyka
tlo.Name = "Tlo"
tlo.Text = ""
tlo.AutoButtonColor = false
tlo.Selectable = false
tlo.BackgroundColor3 = Color3.new(0, 0, 0)
tlo.BackgroundTransparency = 0.5
tlo.BorderSizePixel = 0
tlo.Size = UDim2.fromScale(1, 1)
tlo.Parent = menu

local okno = Instance.new("TextButton") -- przycisk bez akcji: stuknięcie w okno nie trafia w tło
okno.Name = "Okno"
okno.Text = ""
okno.AutoButtonColor = false
okno.Selectable = false
okno.BackgroundColor3 = Color3.fromRGB(58, 42, 32)
okno.BorderSizePixel = 0
okno.AnchorPoint = Vector2.new(0.5, 0.5)
okno.Position = UDim2.fromScale(0.5, 0.5)
okno.ZIndex = 2
okno.Parent = menu
rog(okno, 0.06)
obrys(okno, 3).ApplyStrokeMode = Enum.ApplyStrokeMode.Border

local tytulMenu = napis(okno, "Tytul", UDim2.new(), UDim2.new(), ZLOTY)
tytulMenu.Text = NAPIS_MENU
tytulMenu.TextXAlignment = Enum.TextXAlignment.Left
tytulMenu.ZIndex = 3

local zamknijB = Instance.new("TextButton")
zamknijB.Name = "Zamknij"
zamknijB.Text = "X"
zamknijB.FontFace = FONT
zamknijB.TextScaled = true
zamknijB.TextColor3 = Color3.new(1, 1, 1)
zamknijB.BackgroundColor3 = Color3.fromRGB(214, 70, 64)
zamknijB.AnchorPoint = Vector2.new(1, 0)
zamknijB.ZIndex = 3
zamknijB.Parent = okno
rog(zamknijB, 0.25)
obrys(zamknijB, 2).ApplyStrokeMode = Enum.ApplyStrokeMode.Border
local zp = Instance.new("UIPadding")
zp.PaddingTop, zp.PaddingBottom = UDim.new(0.18, 0), UDim.new(0.14, 0)
zp.Parent = zamknijB

-- agent Karola, 27.11: zakładki TRAIN / SHOP w nagłówku
local function zakladkaB(nazwa: string, tekst: string): TextButton
	local b = Instance.new("TextButton")
	b.Name = nazwa
	b.Text = tekst
	b.FontFace = FONT
	b.TextScaled = true
	b.TextColor3 = Color3.new(1, 1, 1)
	b.BackgroundColor3 = Color3.fromRGB(96, 70, 52)
	b.ZIndex = 3
	b.Parent = okno
	rog(b, 0.25)
	obrys(b, 2).ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	local pd = Instance.new("UIPadding")
	pd.PaddingTop, pd.PaddingBottom = UDim.new(0.2, 0), UDim.new(0.16, 0)
	pd.PaddingLeft, pd.PaddingRight = UDim.new(0.08, 0), UDim.new(0.08, 0)
	pd.Parent = b
	return b
end
local zakladkaTrening = zakladkaB("ZakladkaTrening", "TRAIN")
local zakladkaSklep = zakladkaB("ZakladkaSklep", NAPIS_SKLEPU)

local cwiczenia = Instance.new("Frame")
cwiczenia.Name = "Cwiczenia"
cwiczenia.BackgroundTransparency = 1
cwiczenia.ZIndex = 2
cwiczenia.Parent = okno
local siatkaM = Instance.new("UIGridLayout")
siatkaM.SortOrder = Enum.SortOrder.LayoutOrder
siatkaM.HorizontalAlignment = Enum.HorizontalAlignment.Center
siatkaM.VerticalAlignment = Enum.VerticalAlignment.Center
siatkaM.Parent = cwiczenia

local function maksTekst(t: TextLabel, px: number)
	local c = Instance.new("UITextSizeConstraint")
	c.MaxTextSize = px
	c.Parent = t
end
maksTekst(tytulMenu, 32)

type Kafel = { b: TextButton, ikona: ImageLabel, wartosc: TextLabel, zajete: Frame, s: any }
local kafle: { Kafel } = {}
for i, s in ipairs(D.stanowiska) do
	local b = Instance.new("TextButton")
	b.Name = s.id
	b.Text = ""
	b.LayoutOrder = i
	b.BackgroundColor3 = s.kolor
	b.BorderSizePixel = 0
	b.ZIndex = 3
	b.Parent = cwiczenia
	rog(b, 0.12)
	obrys(b, 2.5).ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	local ik = Instance.new("ImageLabel")
	ik.Name = "Ikona"
	ik.BackgroundTransparency = 1
	ik.Image = s.ikona
	ik.ScaleType = Enum.ScaleType.Fit
	ik.Position, ik.Size = UDim2.fromScale(0.05, 0.06), UDim2.fromScale(0.4, 0.42)
	ik.ZIndex = 4
	ik.Parent = b
	local w = napis(b, "Wartosc", UDim2.fromScale(0.45, 0.08), UDim2.fromScale(0.5, 0.38), Color3.new(1, 1, 1))
	w.TextXAlignment = Enum.TextXAlignment.Right
	w.ZIndex = 4
	maksTekst(w, 40)
	local n = napis(b, "Nazwa", UDim2.fromScale(0.05, 0.5), UDim2.fromScale(0.9, 0.26), Color3.new(1, 1, 1))
	n.Text = s.nazwa
	n.ZIndex = 4
	maksTekst(n, 30)
	local c = napis(b, "Czynnosc", UDim2.fromScale(0.05, 0.76), UDim2.fromScale(0.9, 0.18), ZLOTY)
	c.Text = s.czynnosc
	c.ZIndex = 4
	maksTekst(c, 22)
	local z = Instance.new("Frame")
	z.Name = "Zajete"
	z.BackgroundColor3 = Color3.fromRGB(40, 40, 44)
	z.BackgroundTransparency = 0.35
	z.Size = UDim2.fromScale(1, 1)
	z.Visible = false
	z.ZIndex = 5
	z.Parent = b
	rog(z, 0.12)
	local zn = napis(z, "Napis", UDim2.fromScale(0.1, 0.3), UDim2.fromScale(0.8, 0.4), Color3.new(1, 1, 1))
	zn.Text = "BUSY"
	zn.Rotation = -8
	zn.ZIndex = 6
	table.insert(kafle, { b = b, ikona = ik, wartosc = w, zajete = z, s = s })
end

-- agent Karola, 27.11: zakładka SHOP — kafelek stanowiska: ikona, nazwa, poziom ulepszenia i premia, dwa przyciski
local sklepF = Instance.new("Frame")
sklepF.Name = "Sklep"
sklepF.BackgroundTransparency = 1
sklepF.ZIndex = 2
sklepF.Visible = false
sklepF.Parent = okno
local siatkaS = Instance.new("UIGridLayout")
siatkaS.SortOrder = Enum.SortOrder.LayoutOrder
siatkaS.HorizontalAlignment = Enum.HorizontalAlignment.Center
siatkaS.VerticalAlignment = Enum.VerticalAlignment.Center
siatkaS.Parent = sklepF

local function przyciskSklepu(rodzic: Instance, nazwa: string, kolor: Color3): TextButton
	local b = Instance.new("TextButton")
	b.Name = nazwa
	b.Text = ""
	b.FontFace = FONT
	b.TextScaled = true
	b.TextColor3 = Color3.new(1, 1, 1)
	b.BackgroundColor3 = kolor
	b.ZIndex = 5
	b.Parent = rodzic
	rog(b, 0.2)
	obrys(b, 2).ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	local pd = Instance.new("UIPadding")
	pd.PaddingTop, pd.PaddingBottom = UDim.new(0.1, 0), UDim.new(0.08, 0)
	pd.PaddingLeft, pd.PaddingRight = UDim.new(0.06, 0), UDim.new(0.06, 0)
	pd.Parent = b
	maksTekst(b :: any, 20)
	return b
end

type KafelSklepu = { f: Frame, poziom: TextLabel, ulepsz: TextButton, wzm: TextButton, s: any }
local kafleS: { KafelSklepu } = {}
for i, s in ipairs(D.stanowiska) do
	local f = Instance.new("Frame")
	f.Name = s.id
	f.LayoutOrder = i
	f.BackgroundColor3 = s.kolor
	f.BorderSizePixel = 0
	f.ZIndex = 3
	f.Parent = sklepF
	rog(f, 0.1)
	obrys(f, 2.5).ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	local gora = Instance.new("Frame")
	gora.Name = "Gora"
	gora.BackgroundTransparency = 1
	gora.ZIndex = 4
	gora.Parent = f
	local ik = Instance.new("ImageLabel")
	ik.Name = "Ikona"
	ik.BackgroundTransparency = 1
	ik.Image = s.ikona
	ik.ScaleType = Enum.ScaleType.Fit
	ik.Position, ik.Size = UDim2.fromScale(0.03, 0.05), UDim2.fromScale(0.26, 0.9)
	ik.ZIndex = 4
	ik.Parent = gora
	local n = napis(gora, "Nazwa", UDim2.fromScale(0.31, 0.04), UDim2.fromScale(0.66, 0.5), Color3.new(1, 1, 1))
	n.Text = s.nazwa
	n.TextXAlignment = Enum.TextXAlignment.Left
	n.ZIndex = 4
	maksTekst(n, 26)
	local pz = napis(gora, "Poziom", UDim2.fromScale(0.31, 0.54), UDim2.fromScale(0.66, 0.42), ZLOTY)
	pz.TextXAlignment = Enum.TextXAlignment.Left
	pz.ZIndex = 4
	maksTekst(pz, 20)
	local u = przyciskSklepu(f, "Ulepsz", Color3.fromRGB(70, 150, 70))
	local w = przyciskSklepu(f, "Wzmacniacz", Color3.fromRGB(214, 150, 40))
	table.insert(kafleS, { f = f, poziom = pz, ulepsz = u, wzm = w, s = s })
end

local function uloz()
	local ekran = menu.AbsoluteSize
	if ekran.X < 50 or ekran.Y < 50 then
		ekran = workspace.CurrentCamera.ViewportSize
	end
	local M = MENU
	local kol = if ekran.X >= ekran.Y then 3 else 2
	local rzedy = math.ceil(#kafle / kol)
	local w = math.floor(math.min(ekran.X - 2 * M.brzegX, M.maksSzer))
	local h = math.floor(math.min(ekran.Y - 2 * M.brzegY, M.maksWys))
	okno.Size = UDim2.fromOffset(w, h)
	zamknijB.Position, zamknijB.Size = UDim2.new(1, -4, 0, 2), UDim2.fromOffset(M.pasek - 4, M.pasek - 4)
	-- agent Karola, 27.11: zakładki w nagłówku (≥ 44 px), tytuł za nimi
	local zw = math.floor(math.min(M.zakladka, (w - 2 * M.margines - M.pasek - 8) / 3))
	zakladkaTrening.Position, zakladkaTrening.Size = UDim2.fromOffset(M.margines, 3), UDim2.fromOffset(zw, M.pasek - 6)
	zakladkaSklep.Position, zakladkaSklep.Size = UDim2.fromOffset(M.margines + zw + 6, 3), UDim2.fromOffset(zw, M.pasek - 6)
	local tx = M.margines + 2 * (zw + 6) + 4
	tytulMenu.Position = UDim2.fromOffset(tx, 10)
	tytulMenu.Size = UDim2.fromOffset(w - tx - M.pasek - 8, M.pasek - 18)
	local sw, sh = w - 2 * M.margines, h - M.pasek - 2 - M.margines
	cwiczenia.Position, cwiczenia.Size = UDim2.fromOffset(M.margines, M.pasek + 2), UDim2.fromOffset(sw, sh)
	siatkaM.CellPadding = UDim2.fromOffset(M.odstep, M.odstep)
	local cw = math.floor((sw - (kol - 1) * M.odstep) / kol)
	local ch = math.floor((sh - (rzedy - 1) * M.odstep) / rzedy)
	siatkaM.CellSize = UDim2.fromOffset(cw, ch)
	sklepF.Position, sklepF.Size = cwiczenia.Position, cwiczenia.Size
	siatkaS.CellPadding, siatkaS.CellSize = siatkaM.CellPadding, siatkaM.CellSize
	-- przyciski sklepu: wysokość z kafelka (44 … 56 px), dwa obok siebie na dole
	local bh = math.clamp(math.floor(ch * 0.42), M.przycisk, 56)
	local bw = math.floor((cw - 18) / 2)
	for _, k in ipairs(kafleS) do
		k.ulepsz.Position, k.ulepsz.Size = UDim2.new(0, 6, 1, -bh - 6), UDim2.fromOffset(bw, bh)
		k.wzm.Position, k.wzm.Size = UDim2.new(0, 12 + bw, 1, -bh - 6), UDim2.fromOffset(bw, bh)
		local g = k.f:FindFirstChild("Gora") :: Frame
		g.Position, g.Size = UDim2.fromOffset(4, 3), UDim2.new(1, -8, 1, -bh - 12)
	end
end

local function punktTrenera(): Vector3
	local o: Instance? = workspace
	for _, n in ipairs(string.split(D.trener.punkt, "/")) do
		o = o and o:FindFirstChild(n)
	end
	return if o and o:IsA("BasePart") then o.Position else D.trener.pozycja
end

local menuOtwarte = false
local komunikatDo = 0
local czekaDo = 0
-- agent Karola, 27.11: sklep — ostatni stan z serwera ("sklep"), końce wzmacniaczy u klienta, otwarta zakładka
local stanSklepu: any = nil
local wzmKoniec: { [string]: number } = {}
local wSklepie = false

local function czasNapis(s: number): string
	return string.format("%d:%02d", math.floor(s / 60), math.floor(s % 60))
end

local function odswiezSklep()
	local zloto = player:GetAttribute("Gold")
	zloto = if typeof(zloto) == "number" then math.floor(zloto) else 0
	local U = D.sklep.ulepszenia
	for _, k in ipairs(kafleS) do
		local s = k.s
		local lv = (stanSklepu and stanSklepu.u and stanSklepu.u[s.id]) or 0
		k.poziom.Text = string.format("LV %d/%d  +%d%%", lv, U.maks, math.floor(lv * U.premia * 100 + 0.5))
		local cena = D.cenaUlepszenia(lv)
		if cena then
			k.ulepsz.Text = string.format("LV UP %d", cena)
			k.ulepsz.BackgroundColor3 = if zloto >= cena then Color3.fromRGB(70, 150, 70) else Color3.fromRGB(110, 110, 116)
		else
			k.ulepsz.Text = "MAX"
			k.ulepsz.BackgroundColor3 = Color3.fromRGB(110, 110, 116)
		end
		local zostalo = (wzmKoniec[s.atrybut] or 0) - os.clock()
		if zostalo > 0 then
			k.wzm.Text = "X" .. tostring(D.sklep.wzmacniacze.mnoznik) .. " " .. czasNapis(zostalo)
			k.wzm.BackgroundColor3 = Color3.fromRGB(240, 190, 60)
		else
			k.wzm.Text = string.format("X%d %d", D.sklep.wzmacniacze.mnoznik, D.sklep.wzmacniacze.cena)
			k.wzm.BackgroundColor3 = if zloto >= D.sklep.wzmacniacze.cena then Color3.fromRGB(214, 150, 40)
				else Color3.fromRGB(110, 110, 116)
		end
		k.f:SetAttribute("Poziom", lv)
		k.f:SetAttribute("Wzmacniacz", math.max(0, math.floor(zostalo)))
	end
	if wSklepie and os.clock() > komunikatDo then
		tytulMenu.Text = string.format("%s  %d FISH", NAPIS_SKLEPU, zloto)
		tytulMenu.TextColor3 = ZLOTY
	end
end

local function pokazZakladke(sklep: boolean)
	wSklepie = sklep
	cwiczenia.Visible = not sklep
	sklepF.Visible = sklep
	zakladkaTrening.BackgroundColor3 = if sklep then Color3.fromRGB(96, 70, 52) else Color3.fromRGB(214, 160, 60)
	zakladkaSklep.BackgroundColor3 = if sklep then Color3.fromRGB(214, 160, 60) else Color3.fromRGB(96, 70, 52)
	menu:SetAttribute("Sklep", sklep)
	komunikatDo = 0
	if sklep then
		Z:FireServer("sklep")
		odswiezSklep()
	else
		tytulMenu.Text = NAPIS_MENU
		tytulMenu.TextColor3 = ZLOTY
	end
end

local function odswiezMenu()
	local k = workspace:FindFirstChild("TreningAFK")
	for _, kf in ipairs(kafle) do
		local m = k and k:FindFirstChild(kf.s.id)
		local zajete = m ~= nil and m:GetAttribute("Zajete") == true and aktywne ~= kf.s.id
		local v = player:GetAttribute(kf.s.atrybut)
		kf.wartosc.Text = tostring(if typeof(v) == "number" then math.floor(v) else 0)
		kf.zajete.Visible = zajete
		kf.b.AutoButtonColor = not zajete
		kf.b.BackgroundColor3 = if zajete then Color3.fromRGB(120, 120, 126) else kf.s.kolor
		kf.ikona.ImageTransparency = if zajete then 0.5 else 0
		kf.b:SetAttribute("Zajete", zajete)
	end
	if os.clock() > komunikatDo and not wSklepie then
		tytulMenu.Text = NAPIS_MENU
		tytulMenu.TextColor3 = ZLOTY
	end
	if wSklepie then
		odswiezSklep()
	end
end

local function komunikatMenu(tekst: string, kolor: Color3?)
	tytulMenu.Text = tekst
	tytulMenu.TextColor3 = kolor or Color3.fromRGB(255, 140, 120)
	komunikatDo = os.clock() + 1.8
end

local function zamknijMenu()
	if not menuOtwarte then
		return
	end
	menuOtwarte = false
	menu.Enabled = false
	menu:SetAttribute("Otwarte", false)
	local wybrany = GuiService.SelectedObject
	if wybrany and wybrany:IsDescendantOf(menu) then
		GuiService.SelectedObject = nil
	end
end

local function otworzMenu()
	if menuOtwarte then
		return
	end
	menuOtwarte = true
	komunikatDo = 0
	uloz()
	pokazZakladke(false) -- agent Karola, 27.11: okno otwiera się na ćwiczeniach
	Z:FireServer("sklep")
	odswiezMenu()
	menu.Enabled = true
	menu:SetAttribute("Otwarte", true)
	if UIS.GamepadEnabled then
		for _, kf in ipairs(kafle) do
			if not kf.zajete.Visible then
				GuiService.SelectedObject = kf.b
				break
			end
		end
	end
end

for _, kf in ipairs(kafle) do
	kf.b.Activated:Connect(function()
		if not menuOtwarte or os.clock() < czekaDo then
			return
		end
		if kf.zajete.Visible then
			komunikatMenu(kf.s.nazwa .. " IS BUSY")
			return
		end
		czekaDo = os.clock() + D.trener.odstep + 0.1
		Z:FireServer("wybierz", kf.s.id)
	end)
end
-- agent Karola, 27.11: zakładki i przyciski sklepu (serwer sprawdza wszystko jeszcze raz)
zakladkaTrening.Activated:Connect(function()
	pokazZakladke(false)
end)
zakladkaSklep.Activated:Connect(function()
	pokazZakladke(true)
end)
for _, k in ipairs(kafleS) do
	local function kup(rodzaj: string)
		if not menuOtwarte or not wSklepie or os.clock() < czekaDo then
			return
		end
		czekaDo = os.clock() + D.sklep.odstep + 0.1
		Z:FireServer("kup", rodzaj, k.s.id)
	end
	k.ulepsz.Activated:Connect(function()
		kup("ulepszenie")
	end)
	k.wzm.Activated:Connect(function()
		kup("wzmacniacz")
	end)
end
tlo.Activated:Connect(zamknijMenu)
zamknijB.Activated:Connect(zamknijMenu)
UIS.InputBegan:Connect(function(input)
	if menuOtwarte and (input.KeyCode == Enum.KeyCode.ButtonB or input.KeyCode == Enum.KeyCode.Escape) then
		zamknijMenu()
	end
end)
okna.Event:Connect(function(id)
	if id == D.trener.miejsce then
		otworzMenu()
	end
end)
Z.OnClientEvent:Connect(function(akcja, powod, id, brakuje)
	if akcja == "start" then
		zamknijMenu()
	elseif akcja == "odmowa" and menuOtwarte then
		if powod == "za_malo" and typeof(brakuje) == "number" then -- agent Karola, 27.11: odmowy sklepu
			komunikatMenu(string.format("NEED %d MORE FISH", math.ceil(brakuje)))
			return
		end
		komunikatMenu(if powod == "zajete" then "SOMEONE IS TRAINING THERE"
			elseif powod == "daleko" then "COME CLOSER TO THE TRAINER"
			elseif powod == "trening" then "STOP YOUR TRAINING FIRST"
			elseif powod == "za_malo" then "NOT ENOUGH FISH"
			elseif powod == "maks" then "ALREADY MAX LEVEL"
			elseif powod == "aktywny" then "BOOST ALREADY ACTIVE"
			elseif powod == "wczytywanie" then "STILL LOADING TRY AGAIN"
			elseif powod == "sklep" then "SHOP IS CLOSED"
			else "TRY AGAIN")
	elseif akcja == "sklep" and typeof(powod) == "table" then
		stanSklepu = powod
		table.clear(wzmKoniec)
		if typeof(powod.w) == "table" then
			for atrybut, s in pairs(powod.w) do
				if typeof(s) == "number" then
					wzmKoniec[atrybut] = os.clock() + s
				end
			end
		end
		if menuOtwarte and wSklepie then
			odswiezSklep()
		end
	elseif akcja == "kupiono" and menuOtwarte then
		local s = typeof(id) == "string" and D.stanowisko(id)
		if s then
			komunikatMenu(if powod == "ulepszenie" then s.nazwa .. " UPGRADED"
				else s.skrot .. string.format(" X%d FOR %d MIN", D.sklep.wzmacniacze.mnoznik,
					math.floor(D.sklep.wzmacniacze.czas / 60)), Color3.fromRGB(150, 240, 110))
		end
	end
end)
menu:GetPropertyChangedSignal("AbsoluteSize"):Connect(function()
	if menuOtwarte then
		uloz()
	end
end)
player.CharacterAdded:Connect(zamknijMenu)
task.spawn(function()
	while true do
		task.wait(0.5)
		if menuOtwarte then
			local char = player.Character
			local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
			local p = punktTrenera()
			if not hrp or Vector2.new(hrp.Position.X - p.X, hrp.Position.Z - p.Z).Magnitude > D.trener.zasieg then
				zamknijMenu()
			else
				odswiezMenu()
			end
		end
	end
end)
menu.Parent = player:WaitForChild("PlayerGui")
