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

local function rysuj(dt: number)
	local cel = math.clamp(postep / D.powtorzenNaPasek, 0, 1)
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
end

local function wyskok(tekst: string, kolor: Color3)
	local t = napis(gui, "Wyskok", UDim2.new(0.5, 0, 0.72, 0), UDim2.fromScale(0.3, 0.08), kolor)
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Text = tekst
	t.Rotation = math.random(-6, 6)
	TS:Create(t, TweenInfo.new(1.1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Position = UDim2.new(0.5, 0, 0.58, 0), TextTransparency = 1 }):Play()
	task.delay(1.2, function()
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

type Rig = { model: Model, rodzaj: string, stawy: { [string]: any }, korzen: BasePart?, dlonL: BasePart?, dlonP: BasePart? }
local rig: Rig? = nil

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
	local stawy = {}
	for _, d in ipairs(model:GetDescendants()) do
		if (d:IsA("Motor6D") or d:IsA("AnimationConstraint")) and CZY_STAW[d.Name] and stawy[d.Name] == nil then
			stawy[d.Name] = d
		end
	end
	return {
		model = model,
		rodzaj = rodzaj,
		stawy = stawy,
		korzen = model:FindFirstChild("HumanoidRootPart") :: BasePart?,
		dlonL = model:FindFirstChild("LeftHand") :: BasePart?,
		dlonP = model:FindFirstChild("RightHand") :: BasePart?,
	}
end

local animateWylaczony: LocalScript? = nil
local function przejmijAwatara(r: Rig)
	if r.rodzaj ~= "awatar" then
		return
	end
	local a = r.model:FindFirstChild("Animate")
	if a and a:IsA("LocalScript") and not a.Disabled then
		a.Disabled = true
		animateWylaczony = a
	end
	local hum = r.model:FindFirstChildOfClass("Humanoid")
	local an = hum and hum:FindFirstChildOfClass("Animator")
	if an then
		for _, tr in ipairs(an:GetPlayingAnimationTracks()) do
			tr:Stop(0.1)
		end
	end
end

local function oddajSzkielet(r: Rig?)
	if animateWylaczony then
		animateWylaczony.Disabled = false
		animateWylaczony = nil
	end
	if r then
		for _, j in pairs(r.stawy) do
			pcall(function()
				j.Transform = CFrame.identity
			end)
		end
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
	if r.rodzaj == "bohater" and (bronModel ~= r.model or (bronCzesci[1] and bronCzesci[1].Parent == nil)) then
		bronModel = r.model
		bronCzesci = {}
		for _, m in ipairs(r.model:GetChildren()) do
			if m:IsA("Model") and czyBron(m) then
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

local function staw(r: Rig, n: string): Motor6D?
	local j = r.stawy[n]
	return if j and j:IsA("Motor6D") then j else nil
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

-- książka w łapach przed klatką: środek i nachylenie (układ UpperTorso) i skala (kot ma tułów 0,85 st → 0,45, człowiek ok. 1,5 → 0,8)
local function ukladKsiazki(M: Miary): (CFrame, number)
	local k = math.clamp(M.wysTulowia / 1.9, 0.42, 1)
	local th = math.rad(65) -- strony zwrócone ku twarzy
	local pol = 0.75 * k -- połowa długości książki (grzbiet wzdłuż Z)
	-- górna krawędź pod brodą (z zapasem na pochyloną głowę — Neck −12° przy czytaniu)
	local y = math.min(M.glowaDol - 0.18 - pol * math.sin(th), M.bark.Y - 0.1)
	y = math.max(y, -M.wysTulowia * 0.45)
	local z = -(M.klatka + 0.1 + pol * math.cos(th) + 0.07 * k) -- dolna krawędź przed ubraniem
	return CFrame.new(0, y, z) * CFrame.Angles(th, 0, 0), k
end

-- sztanga: odległość dłoni od środka tułowia ku niebu (dół nad ubraniem, góra = wyprost)
local function torSztangi(M: Miary, f: number): number
	local dol = M.klatka + 0.32
	local gora = math.max(dol + 0.4, M.zasieg * 0.95)
	return dol + (gora - dol) * math.sin(math.pi * math.clamp(f, 0, 1))
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
local function przywrocRekwizyty()
	for i, cf in pairs(bazowe) do
		if i.Parent then
			if i:IsA("Model") then
				if i:GetScale() ~= 1 then
					i:ScaleTo(1) -- agent Karola, sesja 25.11: książka zmniejszona do wzrostu postaci wraca do rozmiaru
				end
				i:PivotTo(cf)
			elseif i:IsA("BasePart") then
				i.CFrame = cf
				i.LocalTransparencyModifier = 0
			end
		end
	end
	bazowe = {}
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
			-- szkielet bez Motor6D (awatar na AnimationConstraint): dawna poza
			local a = 62 * (1 - dzwon(f))
			bP, lP, bL, lL = R(90 - a, 0, 8 + a * 0.25), R(2 * a), R(90 - a, 0, -8 - a * 0.25), R(2 * a)
		end
		return {
			RightShoulder = bP, RightElbow = lP, RightWrist = R(-15),
			LeftShoulder = bL, LeftElbow = lL, LeftWrist = R(-15),
			RightHip = R(8), LeftHip = R(8), RightKnee = R(-14), LeftKnee = R(-14),
			Neck = R(6),
		}
	end,
	Zrecznosc = function(_, t)
		local fi = t * math.pi * 2 * (1 / D.czasPowtorzenia) * tempo
		local s = math.sin(fi)
		return {
			Root = CFrame.new(0, 0.18 * math.abs(math.cos(fi)), 0) * R(-6),
			RightHip = R(38 * s), LeftHip = R(-38 * s),
			RightKnee = R(-(12 + 62 * (0.5 - 0.5 * math.cos(fi)))), LeftKnee = R(-(12 + 62 * (0.5 + 0.5 * math.cos(fi)))),
			RightShoulder = R(-34 * s, 0, 6), LeftShoulder = R(34 * s, 0, -6),
			RightElbow = R(85), LeftElbow = R(85),
		}
	end,
	Inteligencja = function(f, _, r, M)
		-- agent Karola, sesja 25.11: łapy trzymają dolne rogi książki, która leży przed klatką pod brodą (ukladKsiazki)
		local kiw = math.sin(f * math.pi * 2) * 3
		local cf, k = ukladKsiazki(M)
		local bP, lP = celuj(r, "Right", (cf * CFrame.new(0.95 * k, -0.08, 0.55 * k)).Position, 0.5)
		local bL, lL = celuj(r, "Left", (cf * CFrame.new(-0.95 * k, -0.08, 0.55 * k)).Position, 0.5)
		if not (bP and bL) then
			bP, lP, bL, lL = R(30, 0, -10), R(70), R(30, 0, 10), R(70) -- szkielet bez Motor6D
		end
		return {
			RightShoulder = bP, RightElbow = lP, RightWrist = R(-25),
			LeftShoulder = bL, LeftElbow = lL, LeftWrist = R(-25),
			Neck = R(-12 + kiw), Waist = R(-4), -- było −20: pochylona głowa kota wchodziła w książkę
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
	Szczescie = function(f)
		-- agent Karola, sesja 25.11: kubek przed klatką, nie przy twarzy (było bark 50 / łokieć 75), rzut łapą w przód i w dół
		-- na niższy stolik
		local bark, lokiec, nadg = 38, 50, 0
		if f < 0.35 then
			nadg = 25 * math.sin(f * math.pi * 14) -- potrząsanie kubkiem
		elseif f < 0.5 then
			local k = (f - 0.35) / 0.15
			bark, lokiec = 38 + 34 * k, 50 - 38 * k -- rzut
		elseif f < 0.8 then
			local k = (f - 0.5) / 0.3
			bark, lokiec = 72 - 34 * k, 12 + 38 * k -- powrót
		end
		return {
			RightShoulder = R(bark, 0, 6), RightElbow = R(lokiec), RightWrist = R(nadg),
			LeftShoulder = R(10, 0, -8), LeftElbow = R(20), Neck = R(-10),
		}
	end,
}

------------------------------------------------------------ rekwizyty w ruchu
local losKosci = { Vector3.new(-0.5, 0, 0.1), Vector3.new(0.4, 0, -0.2) }
local ostatniaFaza = 0
local pomidorLot: BasePart? = nil

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
				p.CFrame = o * CFrame.new(0, 0.84, ((z0 + 2.8 + t * 7 * tempo) % 6) - 2.8)
			end
		end
	elseif id == "Inteligencja" then
		local k, kart = grupa("Ksiazka"), grupa("Kartka")
		zapamietajGrupe(k)
		zapamietajGrupe(kart)
		local ut = r.model:FindFirstChild("UpperTorso") :: BasePart?
		if k and ut and miary then
			-- agent Karola, sesja 25.11: książka przed klatką pod brodą (nie przy dłoniach, które u kota sięgały twarzy),
			-- zmniejszona do wzrostu postaci; łapy trzymają jej dolne rogi (POZY.Inteligencja)
			local uk, skala = ukladKsiazki(miary)
			if math.abs(k:GetScale() - skala) > 0.01 then
				k:ScaleTo(skala)
				if kart then
					kart:ScaleTo(skala)
				end
			end
			local cf = ut.CFrame * uk
			k:PivotTo(cf)
			if kart then
				-- kartka przewraca się z prawej na lewą w drugiej połowie powtórzenia
				local kat = if f < 0.5 then 0 elseif f < 0.9 then math.pi * ((f - 0.5) / 0.4) else math.pi
				kart:PivotTo(cf * CFrame.new(0, 0.09 * skala, 0) * CFrame.Angles(0, 0, kat))
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
		for i = 1, 2 do
			local g = grupa("Kosc_" .. i)
			zapamietajGrupe(g)
			if g and cp then
				local cel = o * CFrame.new(losKosci[i].X, 2.48, -2.6 + losKosci[i].Z) -- blat niżej (agent Karola, sesja 25.11)
				if f < 0.42 then
					g:PivotTo(cp * CFrame.new(0, 0.6, 0)) -- w kubku (schowane wyżej przez kubek)
				elseif f < 0.62 then
					local k = (f - 0.42) / 0.2
					local poz = cp.Position:Lerp(cel.Position, k) + Vector3.new(0, 1.2 * math.sin(math.pi * k), 0)
					g:PivotTo(CFrame.new(poz) * CFrame.Angles(k * 9 + i, k * 7, k * 5))
				else
					local k = math.clamp((f - 0.62) / 0.18, 0, 1)
					g:PivotTo(cel * CFrame.Angles(math.floor((1 - k) * 4 + i) * math.pi / 2, (1 - k) * 2, 0))
				end
			end
		end
		if f < ostatniaFaza then
			-- nowe powtórzenie: inne miejsce wypadnięcia kości
			for i = 1, 2 do
				losKosci[i] = Vector3.new(math.random(-8, 8) / 10, 0, math.random(-4, 4) / 10)
			end
		end
	end
	ostatniaFaza = f
end

------------------------------------------------------------ pętla animacji (po pętli bohatera Karola)
local czas = 0
local ruchStoi = 0
RunService:BindToRenderStep("TreningAFK", Enum.RenderPriority.Last.Value + 1, function(dt)
	if not aktywne then
		return
	end
	czas += dt
	postep = math.min(postep + dt * tempo / D.czasPowtorzenia, D.powtorzenNaPasek - 0.001)
	rysuj(dt)
	if not rig or not rig.model.Parent then
		rig = znajdzRig()
		if rig then
			przejmijAwatara(rig)
			miary = zmierz(rig) -- agent Karola, sesja 25.11
			if rig.rodzaj == "bohater" and aktywne == "Zrecznosc" then
				local ruch = ruchBohatera()
				if ruch then
					pcall(function()
						ruch:Invoke("klip", "bieg")
					end)
				end
			end
		end
	end
	local r = rig
	if not r then
		return
	end
	local f = postep % 1
	-- bieg na bohaterze gra jego własny klip; na awatarze nasz
	schowajBron(r) -- agent Karola, sesja 25.11: nic w łapach na czas treningu
	local poza = POZY[aktywne :: string]
	if poza and not (r.rodzaj == "bohater" and aktywne == "Zrecznosc") then
		local cele = poza(f, czas, r, miary or zmierz(r))
		for n, j in pairs(r.stawy) do
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
	oddajSzkielet(rig)
	przywrocRekwizyty()
	rig = nil
	schowajCheck()
	aktywne = nil
	gui.Enabled = false
end

Z.OnClientEvent:Connect(function(akcja, a, b, c)
	if akcja == "start" then
		koniec()
		aktywne = a
		local s = D.stanowisko(a)
		local k = workspace:FindFirstChild("TreningAFK")
		stanowiskoM = k and k:FindFirstChild(a)
		postep, tempo, czas = b or 0, 1, 0
		pokazanyProcent = math.clamp(postep / D.powtorzenNaPasek, 0, 1)
		tytul.Text = s and s.nazwa or "TRAINING"
		czynnoscL.Text = s and s.czynnosc or ""
		ikona.Image = s and s.ikona or ""
		przyrostL.Text = s and ("+" .. tostring(c or 1) .. " " .. s.skrot .. " / BAR") or ""
		gui.Enabled = true
		ruchStoi = -10 -- chwila na puszczenie klawiszy po wejściu
	elseif akcja == "postep" then
		postep, tempo = a, b or 1
	elseif akcja == "punkt" then
		local s = aktywne and D.stanowisko(aktywne)
		postep = c or 0
		pokazanyProcent = 1
		wyskok("+" .. tostring(b) .. " " .. (s and s.skrot or ""), s and s.kolor or Color3.new(1, 1, 1))
		local sc = panel:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
		sc.Parent = panel
		sc.Scale = 1.06
		TS:Create(sc, TweenInfo.new(0.18), { Scale = 1 }):Play()
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
