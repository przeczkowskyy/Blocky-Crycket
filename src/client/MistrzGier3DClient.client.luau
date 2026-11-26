--!strict
--[[
	MistrzGier3DClient — plansza mistrza gier jako model 3D na jego stole (Paweł 25.11: „na stole rzeczywista plansza
	z polami, po E kamera przenosi się na planszę, w tle widać mistrza gier, gracz rzeczywiście rzuca kostkami”;
	wersja robocza — Karol może ją poprawić). Zastępuje płaskie okno (src/client/OknoMistrzaGierClient), które ustępuje,
	gdy ten skrypt zgłosi atrybut OknoMiejsca.mistrz_gier_3d.

	Zasady i nagrody liczy serwer bez zmian: src/server/MistrzGier.server.luau (ReplicatedStorage.MistrzGier:
	"stan" | "rzut"). Tutaj tylko obraz: plansza 8 × 7 pól po obwodzie (26 pól jak na serwerze), kostka, pionek, kamera.

	Plansza powstaje LOKALNIE u gracza przy starcie (nic nie zapisuje się w Studio ani u innych graczy): stoi na blacie
	stołu w karczmie bazaru (Workspace/MiasteczkoBazar/Karczma/„Stół blat”). Ozdobna plansza, pionki i kostka z mapy
	Karola są u gracza ukrywane (tylko przezroczystość po stronie klienta) — pliki i obiekty Karola bez zmian.

	Sterowanie: E „Zagraj” przy mistrzu (ReplicatedStorage.OknoMiejsca "mistrz_gier") → kamera nad stół; ROLL albo
	spacja = rzut; LEAVE, Esc albo odejście = powrót kamery.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")
local PPS = game:GetService("ProximityPromptService")

local player = Players.LocalPlayer
local F = RS:WaitForChild("MistrzGier") :: RemoteFunction

local SZER, GLEB = 8, 7 -- pola po obwodzie: 2 × (8 + 7) − 4 = 26
local KROK = 0.5 -- odstęp pól w studach
local POLE = 0.44
local FONT = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
local IKONY = {
	rybki = "rbxassetid://76704302626777",
	gwiazda = "rbxassetid://76704302626777",
	diamenty = "rbxassetid://130974323293639",
	przedmiot = "rbxassetid://71553702739963",
}
local KOLORY = {
	start = Color3.fromRGB(120, 210, 164),
	rybki = Color3.fromRGB(143, 221, 244),
	diamenty = Color3.fromRGB(190, 120, 240),
	przedmiot = Color3.fromRGB(255, 192, 106),
	gwiazda = Color3.fromRGB(255, 214, 90),
}
local OZDOBY_KAROLA = { ["Plansza"] = true, ["Plansza pole"] = true, ["Pionek"] = true, ["Kostka"] = true, ["Kostka oczko"] = true }

local function bindable(name: string): BindableEvent
	local e = RS:FindFirstChild(name)
	if not e then
		e = Instance.new("BindableEvent")
		e.Name = name
		e.Parent = RS
	end
	return e :: BindableEvent
end
local okna = bindable("OknoMiejsca")

------------------------------------------------------------ układ stołu
local karczma = workspace:WaitForChild("MiasteczkoBazar", 120)
karczma = karczma and karczma:WaitForChild("Karczma", 60)
local blat = karczma and karczma:WaitForChild("Stół blat", 60)
if not (karczma and blat and blat:IsA("BasePart")) then
	warn("[MistrzGier3D] brak stołu mistrza gier (MiasteczkoBazar/Karczma/Stół blat) — zostaje płaskie okno")
	return
end

local srodekBlatu = (blat :: BasePart).Position
local gora = srodekBlatu.Y + math.min((blat :: BasePart).Size.X, (blat :: BasePart).Size.Y, (blat :: BasePart).Size.Z) / 2
-- kierunek „do mistrza”: od punktu E gracza przez stół (bez punktu: −Z jak na mapie z 25.11)
local przod = Vector3.new(0, 0, -1)
do
	local gra = workspace:FindFirstChild("MiasteczkoBazarGra")
	local inter = (karczma :: Instance):FindFirstChild("_Interakcja")
	local punkt = inter and inter:FindFirstChild("Punkt E mistrz_gier")
	if not punkt and gra then
		local p = gra:FindFirstChild("Punkty")
		punkt = p and p:FindFirstChild("E mistrz_gier")
	end
	local mistrz = (karczma :: Instance):FindFirstChild("MistrzGier")
	if mistrz and mistrz:IsA("Model") then
		local d = mistrz:GetPivot().Position - srodekBlatu
		d = Vector3.new(d.X, 0, d.Z)
		if d.Magnitude > 0.5 then
			przod = d.Unit
		end
	elseif punkt and punkt:IsA("BasePart") then
		local d = srodekBlatu - punkt.Position
		d = Vector3.new(d.X, 0, d.Z)
		if d.Magnitude > 0.5 then
			przod = d.Unit
		end
	end
end
local UP = Vector3.yAxis
local prawo = przod:Cross(UP).Unit
local baza = Vector3.new(srodekBlatu.X, gora, srodekBlatu.Z)
local uklad = CFrame.fromMatrix(baza, prawo, UP) -- X = w prawo gracza, Y = w górę, −Z = do mistrza

-- SurfaceGui na ścianie Top ma „górę” napisu w lewo części: obrót części ustawia napis czytelnie dla gracza
local OBROT_NAPISU = CFrame.Angles(0, -math.pi / 2, 0)

local function miejsce(x: number, y: number, z: number): Vector3
	return baza + prawo * x + UP * y + przod * z
end

-- ozdoby z mapy Karola: tylko u tego gracza i tylko przezroczystość (plansza 3 × 3, pionki, kostka)
for _, p in ipairs((karczma :: Instance):GetChildren()) do
	if p:IsA("BasePart") and OZDOBY_KAROLA[p.Name] and (p.Position - baza).Magnitude < 5 then
		p.Transparency = 1
		p.CanCollide = false
	end
end

------------------------------------------------------------ model planszy
local model = Instance.new("Model")
model.Name = "MistrzGierPlansza3D"

local function czesc(nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3, material: Enum.Material?): Part
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
	p.Size, p.CFrame, p.Color = rozmiar, cf, kolor
	p.Material = material or Enum.Material.SmoothPlastic
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Parent = model
	return p
end

local szerPlanszy, glebPlanszy = SZER * KROK + 0.2, GLEB * KROK + 0.2
czesc("Rama", Vector3.new(szerPlanszy + 0.16, 0.1, glebPlanszy + 0.16), uklad * CFrame.new(0, 0.05, 0), Color3.fromRGB(74, 46, 26), Enum.Material.Wood)
czesc("Deska", Vector3.new(szerPlanszy, 0.12, glebPlanszy), uklad * CFrame.new(0, 0.06, 0), Color3.fromRGB(170, 110, 62), Enum.Material.Wood)
local sukno = czesc("Sukno", Vector3.new((SZER - 2) * KROK - 0.08, 0.13, (GLEB - 2) * KROK - 0.08), uklad * CFrame.new(0, 0.065, 0),
	Color3.fromRGB(58, 140, 92), Enum.Material.Fabric)

-- pozycje pól: bliski rząd od lewej do prawej, prawa kolumna w głąb, daleki rząd wraca, lewa kolumna do gracza
local pozycje: { Vector3 } = {}
do
	local x0, z0 = -(SZER - 1) * KROK / 2, -(GLEB - 1) * KROK / 2
	local function dodaj(ix: number, iz: number)
		table.insert(pozycje, miejsce(x0 + ix * KROK, 0.12, z0 + iz * KROK))
	end
	for ix = 0, SZER - 1 do
		dodaj(ix, 0)
	end
	for iz = 1, GLEB - 1 do
		dodaj(SZER - 1, iz)
	end
	for ix = SZER - 2, 0, -1 do
		dodaj(ix, GLEB - 1)
	end
	for iz = GLEB - 2, 1, -1 do
		dodaj(0, iz)
	end
end
local POL = #pozycje

type Pole = { czesc: Part, napis: TextLabel, ikona: ImageLabel }
local pola: { Pole } = {}
for i, poz in ipairs(pozycje) do
	local p = czesc(string.format("Pole%02d", i), Vector3.new(POLE, 0.06, POLE), CFrame.fromMatrix(poz + UP * 0.03, prawo, UP) * OBROT_NAPISU,
		KOLORY.rybki)
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Top
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 220
	sg.LightInfluence = 0
	local ik = Instance.new("ImageLabel")
	ik.BackgroundTransparency = 1
	ik.Position, ik.Size = UDim2.fromScale(0.2, 0.04), UDim2.fromScale(0.6, 0.56)
	ik.ScaleType = Enum.ScaleType.Fit
	ik.Parent = sg
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position, t.Size = UDim2.fromScale(0.02, 0.56), UDim2.fromScale(0.96, 0.42)
	t.FontFace, t.TextScaled, t.TextColor3, t.Text = FONT, true, Color3.new(1, 1, 1), ""
	local st = Instance.new("UIStroke")
	st.Thickness, st.Color = 2, Color3.fromRGB(26, 20, 16)
	st.Parent = t
	t.Parent = sg
	sg.Parent = p
	pola[i] = { czesc = p, napis = t, ikona = ik }
end

-- napis planszy na suknie
local napisPlanszy: TextLabel
do
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Top
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 120
	sg.LightInfluence = 0
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position, t.Size = UDim2.fromScale(0.1, 0.06), UDim2.fromScale(0.8, 0.2)
	t.FontFace, t.TextScaled, t.TextColor3, t.TextTransparency, t.Text = FONT, true, Color3.fromRGB(252, 227, 176), 0.25, "BOARD 1"
	t.Parent = sg
	local plytka = czesc("NapisPlanszy", Vector3.new(sukno.Size.Z, 0.01, sukno.Size.X), uklad * CFrame.new(0, 0.135, 0) * OBROT_NAPISU,
		Color3.new(1, 1, 1))
	plytka.Transparency = 1
	sg.Parent = plytka
	napisPlanszy = t
end

-- pionek
local pionek = Instance.new("Model")
pionek.Name = "Pionek"
local pionekSpod = czesc("Spod", Vector3.new(0.1, 0.3, 0.3), CFrame.new(), Color3.fromRGB(236, 110, 102))
pionekSpod.Shape = Enum.PartType.Cylinder
local pionekTulow = czesc("Tulow", Vector3.new(0.2, 0.26, 0.2), CFrame.new(), Color3.fromRGB(236, 110, 102))
local pionekGlowa = czesc("Glowa", Vector3.new(0.24, 0.24, 0.24), CFrame.new(), Color3.fromRGB(255, 214, 90))
pionekGlowa.Shape = Enum.PartType.Ball
for _, p in ipairs({ pionekSpod, pionekTulow, pionekGlowa }) do
	p.Parent = pionek
end
pionek.Parent = model
local function ustawPionek(poz: Vector3)
	pionekSpod.CFrame = CFrame.new(poz + UP * 0.08) * CFrame.Angles(0, 0, math.pi / 2)
	pionekTulow.CFrame = CFrame.new(poz + UP * 0.26)
	pionekGlowa.CFrame = CFrame.new(poz + UP * 0.48)
end

-- kostka: ściany jak w Robloxie — góra 1, dół 6, przód 2, tył 5, prawo 3, lewo 4
local kostka = czesc("Kostka", Vector3.new(0.36, 0.36, 0.36), CFrame.new(miejsce(0, 0.31, 0)), Color3.fromRGB(255, 248, 230))
do
	local OCZKA = {
		[1] = { { 0.5, 0.5 } },
		[2] = { { 0.27, 0.27 }, { 0.73, 0.73 } },
		[3] = { { 0.25, 0.25 }, { 0.5, 0.5 }, { 0.75, 0.75 } },
		[4] = { { 0.27, 0.27 }, { 0.73, 0.27 }, { 0.27, 0.73 }, { 0.73, 0.73 } },
		[5] = { { 0.25, 0.25 }, { 0.75, 0.25 }, { 0.5, 0.5 }, { 0.25, 0.75 }, { 0.75, 0.75 } },
		[6] = { { 0.27, 0.22 }, { 0.73, 0.22 }, { 0.27, 0.5 }, { 0.73, 0.5 }, { 0.27, 0.78 }, { 0.73, 0.78 } },
	}
	local SCIANY = { [1] = Enum.NormalId.Top, [6] = Enum.NormalId.Bottom, [2] = Enum.NormalId.Front, [5] = Enum.NormalId.Back,
		[3] = Enum.NormalId.Right, [4] = Enum.NormalId.Left }
	for wartosc, sciana in pairs(SCIANY) do
		local sg = Instance.new("SurfaceGui")
		sg.Face = sciana
		sg.CanvasSize = Vector2.new(100, 100)
		sg.LightInfluence = 0.3
		for _, o in ipairs(OCZKA[wartosc]) do
			local f = Instance.new("Frame")
			f.AnchorPoint = Vector2.new(0.5, 0.5)
			f.Position, f.Size = UDim2.fromScale(o[1], o[2]), UDim2.fromScale(0.2, 0.2)
			f.BackgroundColor3 = if wartosc == 1 then Color3.fromRGB(200, 50, 50) else Color3.fromRGB(40, 30, 24)
			f.BorderSizePixel = 0
			local c = Instance.new("UICorner")
			c.CornerRadius = UDim.new(0.5, 0)
			c.Parent = f
			f.Parent = sg
		end
		sg.Parent = kostka
	end
end
local OBROT_WYNIKU: { [number]: CFrame } = {
	[1] = CFrame.new(), [6] = CFrame.Angles(math.pi, 0, 0), [2] = CFrame.Angles(math.pi / 2, 0, 0),
	[5] = CFrame.Angles(-math.pi / 2, 0, 0), [3] = CFrame.Angles(0, 0, math.pi / 2), [4] = CFrame.Angles(0, 0, -math.pi / 2),
}

model.Parent = workspace

------------------------------------------------------------ nakładka 2D
-- Grafika z jednej generacji (Higgsfield 25.11, tools/mistrz_gier_ui.py; ID w assets/manifest.json: MistrzTytul,
-- MistrzRoll, MistrzLeave, MistrzCena, MistrzWstega, MistrzGwiazda). Układ jak na makiecie zaakceptowanej przez Pawła:
-- położenie i szerokość w ułamkach ekranu, wysokość z proporcji obrazka.
local GRAFIKA = {
	tytul = "rbxassetid://113072079774411", roll = "rbxassetid://122880810258615", leave = "rbxassetid://73797764327522",
	cena = "rbxassetid://108268009960610", wstega = "rbxassetid://121251992074776", gwiazda = "rbxassetid://138613041337013",
}
local KREM, BIALY, ZLOTY, CIEMNY = Color3.fromRGB(252, 227, 176), Color3.new(1, 1, 1), Color3.fromRGB(255, 214, 90), Color3.fromRGB(74, 46, 26)

local gui = Instance.new("ScreenGui")
gui.Name = "MistrzGier3D"
gui.ResetOnSpawn, gui.IgnoreGuiInset, gui.Enabled, gui.DisplayOrder = false, true, false, 26

local function obraz(klasa: string, nazwa: string, obrazek: string, x: number, y: number, szer: number, proporcje: number): any
	local o = Instance.new(klasa) :: any
	o.Name = nazwa
	o.BackgroundTransparency = 1
	o.Image, o.ScaleType = obrazek, Enum.ScaleType.Stretch
	o.Position, o.Size = UDim2.fromScale(x, y), UDim2.fromScale(szer, 1)
	if klasa == "ImageButton" then
		o.AutoButtonColor = false
	end
	local ar = Instance.new("UIAspectRatioConstraint")
	ar.AspectRatio, ar.AspectType, ar.DominantAxis = proporcje, Enum.AspectType.ScaleWithParentSize, Enum.DominantAxis.Width
	ar.Parent = o
	o.Parent = gui
	return o
end

local function napis(rodzic: Instance, tekst: string, x: number, y: number, w: number, h: number, kolor: Color3, maks: number, obrys: number): TextLabel
	local l = Instance.new("TextLabel")
	l.Name = "Label"
	l.BackgroundTransparency = 1
	l.Position, l.Size = UDim2.fromScale(x, y), UDim2.fromScale(w, h)
	l.FontFace, l.TextScaled, l.TextColor3, l.Text = FONT, true, kolor, tekst
	local lim = Instance.new("UITextSizeConstraint")
	lim.MaxTextSize, lim.MinTextSize = maks, 6
	lim.Parent = l
	if obrys > 0 then
		local st = Instance.new("UIStroke")
		st.Thickness, st.Color = obrys, Color3.fromRGB(26, 20, 16)
		st.Parent = l
	end
	l.Parent = rodzic
	return l
end

local function sprezyna(b: GuiButton)
	local sc = Instance.new("UIScale")
	sc.Parent = b
	b.MouseButton1Down:Connect(function()
		TS:Create(sc, TweenInfo.new(0.08), { Scale = 0.94 }):Play()
	end)
	local function pusc()
		TS:Create(sc, TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	end
	b.MouseButton1Up:Connect(pusc)
	b.MouseLeave:Connect(pusc)
end

local tytulRama = obraz("ImageLabel", "Title", GRAFIKA.tytul, 0.018, 0.03, 0.30, 3.2)
local tytul = napis(tytulRama, "GAME MASTER", 0.08, 0.24, 0.84, 0.52, KREM, 40, 3)
local leaveBtn = obraz("ImageButton", "LeaveButton", GRAFIKA.leave, 0.845, 0.125, 0.135, 2.2756) :: ImageButton
napis(leaveBtn, "LEAVE", 0.36, 0.2, 0.56, 0.6, BIALY, 30, 3)
local cenaRama = obraz("ImageLabel", "Price", GRAFIKA.cena, 0.765, 0.545, 0.215, 3.1347)
local cenaIkona = Instance.new("ImageLabel")
cenaIkona.Name = "Icon"
cenaIkona.BackgroundTransparency = 1
cenaIkona.Position, cenaIkona.Size = UDim2.fromScale(0.07, 0.2), UDim2.fromScale(0.19, 0.6)
cenaIkona.ScaleType, cenaIkona.Image = Enum.ScaleType.Fit, IKONY.rybki
cenaIkona.Parent = cenaRama
local cenaL = napis(cenaRama, "FREE ROLL", 0.3, 0.2, 0.64, 0.6, ZLOTY, 30, 3)
local rollBtn = obraz("ImageButton", "RollButton", GRAFIKA.roll, 0.755, 0.675, 0.225, 2.2522) :: ImageButton
local rollNapis = napis(rollBtn, "ROLL", 0.38, 0.14, 0.56, 0.72, BIALY, 64, 4)
local wstega = obraz("ImageLabel", "Message", GRAFIKA.wstega, 0.02, 0.80, 0.33, 5.0443)
wstega.Visible = false
local msg = napis(wstega, "", 0.14, 0.1, 0.72, 0.58, CIEMNY, 24, 0)
msg.TextWrapped = true
sprezyna(rollBtn)
sprezyna(leaveBtn)
gui.Parent = player:WaitForChild("PlayerGui")

-- wstęga widać tylko wtedy, gdy jest co powiedzieć
local function komunikat(t: string)
	msg.Text = t
	wstega.Visible = t ~= ""
end

------------------------------------------------------------ stan i rysowanie
local stan: any = nil
local otwarte, toczy = false, false
local miejsceOtwarcia: Vector3? = nil

local function rysuj()
	if not stan then
		return
	end
	for i = 1, math.min(POL, stan.pol) do
		local n = stan.nagrody[i]
		local p = pola[i]
		p.czesc.Color = KOLORY[n.typ] or KOLORY.rybki
		if n.typ == "start" then
			p.napis.Text, p.ikona.Image = "GO", ""
		elseif n.typ == "przedmiot" then
			p.napis.Text, p.ikona.Image = "ITEM", IKONY.przedmiot
		else
			p.napis.Text, p.ikona.Image = "+" .. n.ile, IKONY[n.typ] or ""
		end
	end
	ustawPionek(pozycje[math.clamp(stan.pole, 1, POL)])
	napisPlanszy.Text = "BOARD " .. tostring(stan.plansza)
	tytul.Text = "GAME MASTER  ·  BOARD " .. tostring(stan.plansza)
end

local function rysujCene()
	if not stan then
		return
	end
	if stan.darmowyZa <= 0 then
		cenaL.Text = "FREE ROLL"
	else
		cenaL.Text = string.format("%d  ·  %d:%02d", stan.cena, stan.darmowyZa // 60, stan.darmowyZa % 60)
	end
end

local function odswiez()
	local ok, w = pcall(function()
		return F:InvokeServer("stan")
	end)
	if ok and type(w) == "table" and w.ok then
		stan = w
		rysuj()
		rysujCene()
	end
end

------------------------------------------------------------ animacje
local function czekaj(czas: number, krok: (u: number) -> ())
	local t0 = os.clock()
	while true do
		local u = math.clamp((os.clock() - t0) / czas, 0, 1)
		krok(u)
		if u >= 1 then
			break
		end
		RunService.RenderStepped:Wait()
	end
end

local function rzutKostka(wynik: number)
	local start = miejsce((math.random() - 0.5) * 1.2, 2.2, 1.6) -- znad dalszej krawędzi, od strony mistrza
	local cel = miejsce((math.random() - 0.5) * 1.6, 0.31, (math.random() - 0.5) * 1.0)
	local koniec = CFrame.fromMatrix(Vector3.zero, prawo, UP) * CFrame.Angles(0, math.random() * math.pi * 2, 0) * OBROT_WYNIKU[wynik]
	local a, b, c = math.random(5, 9) * math.pi, math.random(4, 8) * math.pi, math.random(5, 9) * math.pi
	czekaj(1.05, function(u)
		local w = (1 - u) ^ 2
		local poz = start:Lerp(cel, u)
		-- lot i dwa odbicia: wysokość gaśnie razem z obrotem
		local skok = if u < 0.55 then 0 else math.abs(math.sin((u - 0.55) / 0.45 * math.pi * 2)) * 0.5 * (1 - u)
		local y = start.Y + (cel.Y - start.Y) * math.min(1, u / 0.55) ^ 2 + skok
		kostka.CFrame = CFrame.new(poz.X, y, poz.Z) * koniec * CFrame.Angles(a * w, b * w, c * w)
	end)
end

local function skok(z: number, na: number)
	for i = z + 1, na do
		local a, b = pozycje[i - 1], pozycje[i]
		czekaj(0.17, function(u)
			ustawPionek(a:Lerp(b, u) + UP * math.sin(u * math.pi) * 0.35)
		end)
		local p = pola[i].czesc
		local kolor = p.Color
		p.Color = Color3.new(1, 1, 1)
		TS:Create(p, TweenInfo.new(0.25), { Color = kolor }):Play()
	end
end

local function pokazNagrode(pole: number, tekst: string, typ: string?)
	local bb = Instance.new("BillboardGui")
	bb.Adornee = pola[pole].czesc
	bb.Size = UDim2.fromScale(1.5, 1.5)
	bb.StudsOffsetWorldSpace = Vector3.new(0, 1.0, 0)
	bb.AlwaysOnTop = true
	local gw = Instance.new("ImageLabel")
	gw.BackgroundTransparency = 1
	gw.Size = UDim2.fromScale(1, 1)
	gw.Image, gw.ScaleType = GRAFIKA.gwiazda, Enum.ScaleType.Fit
	gw.Parent = bb
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position, t.Size = UDim2.fromScale(0.2, 0.3), UDim2.fromScale(0.6, 0.3)
	t.FontFace, t.TextScaled, t.TextColor3, t.Text = FONT, true, Color3.new(1, 1, 1), tekst
	local st = Instance.new("UIStroke")
	st.Thickness, st.Color = 3, Color3.fromRGB(26, 20, 16)
	st.Parent = t
	t.Parent = bb
	local ik = Instance.new("ImageLabel")
	ik.BackgroundTransparency = 1
	ik.Position, ik.Size = UDim2.fromScale(0.39, 0.58), UDim2.fromScale(0.22, 0.2)
	ik.ScaleType, ik.Image = Enum.ScaleType.Fit, IKONY[typ or "rybki"] or ""
	ik.Parent = bb
	bb.Parent = gui
	local zanik = TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In, 0, false, 1.0)
	TS:Create(bb, TweenInfo.new(1.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { StudsOffsetWorldSpace = Vector3.new(0, 1.7, 0) }):Play()
	TS:Create(gw, zanik, { ImageTransparency = 1 }):Play()
	TS:Create(t, zanik, { TextTransparency = 1 }):Play()
	TS:Create(st, zanik, { Transparency = 1 }):Play()
	TS:Create(ik, zanik, { ImageTransparency = 1 }):Play()
	task.delay(1.6, function()
		bb:Destroy()
	end)
end

local function rzuc()
	if toczy or not stan or not otwarte then
		return
	end
	toczy = true
	komunikat("")
	rollBtn.ImageColor3 = Color3.fromRGB(150, 150, 150)
	rollNapis.TextTransparency = 0.4
	local ok, w = pcall(function()
		return F:InvokeServer("rzut", stan.darmowyZa > 0)
	end)
	if not ok or type(w) ~= "table" or not w.ok then
		komunikat(if ok and type(w) == "table" and w.tekst then w.tekst else "…")
	else
		rzutKostka(w.kostka)
		task.wait(0.15)
		skok(w.z, w.na)
		if w.nowaPlansza then
			pokazNagrode(w.na, "STAR! +" .. w.nagroda, "rybki")
			komunikat(string.format("Board %d done! New, better board.", w.planszaRzutu))
			task.wait(1.3)
		elseif w.typ == "przedmiot" then
			pokazNagrode(w.na, "ITEM!", "przedmiot")
		else
			pokazNagrode(w.na, "+" .. w.nagroda, w.typ)
		end
		if not w.wyplacono and w.nagroda > 0 then
			komunikat("Reward not paid — player state (Karol) not running")
		end
		stan = w
		rysuj()
		rysujCene()
	end
	rollBtn.ImageColor3 = Color3.new(1, 1, 1)
	rollNapis.TextTransparency = 0
	toczy = false
end

------------------------------------------------------------ kamera i tryb gry
local kamera = workspace.CurrentCamera
local poprzedniFov = 70
local hudBylo: boolean? = nil

-- gracz nie chodzi w trybie stołu: moduł sterowania Robloxa, a gdy gra go nie ma — prędkość postaci 0
local predkosc: number? = nil
local function sterowanie(wlacz: boolean)
	local ps = player:FindFirstChild("PlayerScripts")
	local pm = ps and ps:FindFirstChild("PlayerModule")
	if pm and pm:IsA("ModuleScript") then
		pcall(function()
			local c = (require(pm) :: any):GetControls()
			if wlacz then
				c:Enable()
			else
				c:Disable()
			end
		end)
		return
	end
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not hum then
		return
	end
	if wlacz then
		if predkosc then
			hum.WalkSpeed = predkosc
			predkosc = nil
		end
	elseif not predkosc then
		predkosc = hum.WalkSpeed
		hum.WalkSpeed = 0
	end
end

-- Paweł 25.11 po teście: w kadrze cała plansza ORAZ mistrz gier (z głową), nic ich nie zasłania — kamera dalej
-- od stołu i mniej z góry; postać gracza jest u niego niewidoczna na czas gry przy stole (stoi przed kamerą)
local FOV_STOLU = 60
local function widokStolu(): CFrame
	local oko = miejsce(0, 4.6, -5.0) -- po stronie gracza, 5 studów od środka stołu
	local cel = miejsce(0, 1.26, 0.5) -- między planszą a głową mistrza: dół kadru = bliższy rząd pól, góra = kapelusz
	return CFrame.lookAt(oko, cel)
end

local ukrywanie: RBXScriptConnection? = nil
local function przezroczystoscPostaci(wartosc: number)
	local char = player.Character
	if not char then
		return
	end
	for _, d in ipairs(char:GetDescendants()) do
		if d:IsA("BasePart") or d:IsA("Decal") or d:IsA("Texture") then
			d.LocalTransparencyModifier = wartosc
		end
	end
end
local function ukryjPostac(ukryj: boolean)
	if ukrywanie then
		ukrywanie:Disconnect()
		ukrywanie = nil
	end
	if ukryj then
		-- co klatkę: obejmuje też części dołożone w trakcie (np. założony przedmiot)
		ukrywanie = RunService.RenderStepped:Connect(function()
			przezroczystoscPostaci(1)
		end)
	else
		przezroczystoscPostaci(0)
	end
end

local function otworz()
	local wybor = player.PlayerGui:FindFirstChild("ClassSelect")
	if otwarte or (wybor and wybor:IsA("ScreenGui") and wybor.Enabled) then
		return -- ekran wyboru rasy ma własną kamerę
	end
	otwarte = true
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	miejsceOtwarcia = root and root.Position or nil
	komunikat("")
	kamera = workspace.CurrentCamera
	poprzedniFov = kamera.FieldOfView
	kamera.CameraType = Enum.CameraType.Scriptable
	TS:Create(kamera, TweenInfo.new(0.7, Enum.EasingStyle.Quart, Enum.EasingDirection.Out), { CFrame = widokStolu(), FieldOfView = FOV_STOLU }):Play()
	sterowanie(false)
	ukryjPostac(true)
	local hud = player.PlayerGui:FindFirstChild("HUD")
	if hud and hud:IsA("ScreenGui") then
		hudBylo = hud.Enabled
		hud.Enabled = false
	end
	PPS.Enabled = false -- podpowiedzi E nie zasłaniają stołu
	gui.Enabled = true
	odswiez()
end

local function zamknij()
	if not otwarte then
		return
	end
	otwarte = false
	gui.Enabled = false
	PPS.Enabled = true
	kamera.CameraType = Enum.CameraType.Custom
	kamera.FieldOfView = poprzedniFov
	sterowanie(true)
	ukryjPostac(false)
	local hud = player.PlayerGui:FindFirstChild("HUD")
	if hud and hud:IsA("ScreenGui") and hudBylo ~= nil then
		hud.Enabled = hudBylo
	end
end

okna:SetAttribute("mistrz_gier", true) -- dymek „w budowie” bazaru wyłączony
okna:SetAttribute("mistrz_gier_3d", true) -- płaskie okno ustępuje
okna.Event:Connect(function(id)
	if id == "mistrz_gier" then
		otworz()
	end
end)
rollBtn.Activated:Connect(rzuc)
leaveBtn.Activated:Connect(zamknij)
UIS.InputBegan:Connect(function(input, processed)
	if not otwarte then
		return
	end
	if input.KeyCode == Enum.KeyCode.Escape then
		zamknij()
	elseif not processed and input.KeyCode == Enum.KeyCode.Space then
		rzuc()
	end
end)
player.CharacterAdded:Connect(zamknij)

-- plansza od razu pokazuje stan gracza (widać ją także bez wejścia w grę); licznik darmowego rzutu
task.spawn(function()
	task.wait(3)
	odswiez()
	while true do
		task.wait(1)
		if otwarte and stan then
			if stan.darmowyZa > 0 then
				stan.darmowyZa -= 1
				rysujCene()
			end
			local char = player.Character
			local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
			if root and miejsceOtwarcia and (root.Position - miejsceOtwarcia).Magnitude > 14 then
				zamknij()
			end
		end
	end
end)
