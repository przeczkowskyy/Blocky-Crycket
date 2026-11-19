--[[
	KlientBonk — klient gry BONK (Script, RunContext Client, w Workspace/BonkGra). Rysuje to, co policzył serwer:
	potwory (kopie wzorców z ReplicatedStorage/BonkWzorce, tylko w zasięgu kamery), trafienia, loty po BONK, monety,
	napisy, bramy (wrota otwarte tylko u gracza, który ma Moc), muzykę krainy; wysyła BONK (klik / E / pad / przycisk).

	W BONK (atrybut gracza BonkAktywny) chowa u siebie cudze ekrany (ScreenGui wprost w PlayerGui: HUD, wybór klasy…
	— Enabled = false lokalnie, pilnowane) i przywraca je po wyjściu. Własny ekran: PlayerGui/BonkUI/BonkEkran.
	Gdy przy wejściu trwa ekran wyboru klasy obecnej gry, zdejmuje też jego kamerę (RenderStep „ClassSelectCam”).

	Etap 2: okna (OknaBonk: sklep pałek, pety, Księga, prezent, przycisk przy stoisku / inkubatorze z jawnymi szansami),
	efektowne wyklucie (jajko przed kamerą trzęsie się, pęka w kolorze rzadkości, pet wyskakuje), pety za graczami (z
	atrybutu gracza BonkPety — rysuje każdy klient, tylko w zasięgu), Moc nad głową każdego gracza, pasek życia Strażnika
	(wspólny), lot Strażnika w niebo, komunikaty serwera. Akcje gracza idą przez Sygnaly/Akcja (sprawdza serwer).

	Haczyki prób: Sygnaly/SterowanieKlienta (BindableFunction u klienta): "stan", "bonk", "pomiar_zeruj", "trzymaj",
	"emulacja", "akcja", "okno".
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local Moduly = kontener:WaitForChild("Moduly")
local D = require(Moduly:WaitForChild("DaneBonk"))
local L = require(Moduly:WaitForChild("LogikaBonk"))
local Efekty = require(Moduly:WaitForChild("EfektyBonk"))
local Interfejs = require(Moduly:WaitForChild("InterfejsBonk"))
local Okna = require(Moduly:WaitForChild("OknaBonk"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evBonk = Sygnaly:WaitForChild("Bonk")
local evAkcja = Sygnaly:WaitForChild("Akcja")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local sterowanie = Sygnaly:WaitForChild("SterowanieKlienta")
local P = D.prefiks

local gotowy = false
local stanDoProby: any = { gotowy = false }
sterowanie.OnInvoke = function(polecenie)
	if not gotowy then
		return stanDoProby
	end
	return nil
end

if kontener:GetAttribute(D.wylacznik) == false then
	stanDoProby = { gotowy = false, wylaczony = true }
	return
end

local wzorce = ReplicatedStorage:WaitForChild(D.folderWzorcow, 40)
if not wzorce then
	warn(P .. "brak ReplicatedStorage/" .. D.folderWzorcow .. " — potwory jako zastępcze bryły")
end
local folderPotworow = kontener:WaitForChild("Stan", 40) and kontener.Stan:WaitForChild("Potwory", 20)
if not folderPotworow then
	warn(P .. "brak stanu potworów z serwera — klient BONK nie rusza")
	return
end
local mapa = kontener:FindFirstChild("Mapa")
local folderBram = kontener:FindFirstChild("Bramy")

local lokalne = Instance.new("Folder")
lokalne.Name = "BonkLokalne"
lokalne.Parent = workspace
local E = Efekty.nowe(lokalne, D)
local kamera = workspace.CurrentCamera

------------------------------------------------------------------ dźwięki (odcinki arkusza efektów) i muzyka
local folderDzwiekow = Instance.new("Folder")
folderDzwiekow.Name = "BonkDzwieki"
folderDzwiekow.Parent = game:GetService("SoundService")
local pule: { [string]: { s: { Sound }, i: number } } = {}
local DZ = D.dzwieki
if DZ.arkusz and DZ.arkusz > 0 then
	for rola, e in DZ.efekty do
		local lista = {}
		for i = 1, (if rola == "cios" or rola == "monety" then 4 else 2) do
			local s = Instance.new("Sound")
			s.Name = rola .. i
			s.SoundId = "rbxassetid://" .. tostring(DZ.arkusz)
			s.Volume = e.glosnosc
			s.PlaybackRegionsEnabled = true
			s.PlaybackRegion = NumberRange.new(e.od, e.koniec)
			s.Parent = folderDzwiekow
			table.insert(lista, s)
		end
		pule[rola] = { s = lista, i = 1 }
	end
end
local graneDzwieki = 0
local function zagraj(rola: string, wysokosc: number?)
	local p = pule[rola]
	if not p then
		return
	end
	local s = p.s[p.i]
	p.i = (p.i % #p.s) + 1
	s.PlaybackSpeed = wysokosc or 1
	s.TimePosition = DZ.efekty[rola].od
	s:Play()
	graneDzwieki += 1
end

local muzyka = Instance.new("Sound")
muzyka.Name = "MuzykaBonk"
muzyka.Looped = true
muzyka.Volume = DZ.glosnosc_muzyki
muzyka.Parent = folderDzwiekow
local function muzykaKrainy(nr: number?)
	local id = nr and D.krainy[nr] and DZ.muzyka[D.krainy[nr].id] or 0
	local sid = if id and id > 0 then "rbxassetid://" .. tostring(id) else ""
	if sid == "" then
		muzyka:Stop()
		return
	end
	if muzyka.SoundId ~= sid then
		muzyka.SoundId = sid
		muzyka.TimePosition = 0
	end
	if not muzyka.IsPlaying then
		muzyka:Play()
	end
end

------------------------------------------------------------------ cudze ekrany (tylko lokalnie)
local pg = gracz:WaitForChild("PlayerGui")
local folderUI = pg:FindFirstChild("BonkUI")
if folderUI then
	folderUI:Destroy()
end
folderUI = Instance.new("Folder")
folderUI.Name = "BonkUI"
folderUI.Parent = pg

local aktywny = false
local schowane: { [ScreenGui]: boolean } = {}
local straze: { RBXScriptConnection } = {}

local function schowaj(g: Instance)
	if not g:IsA("ScreenGui") then
		return
	end
	if g.Enabled then
		schowane[g] = true
		g.Enabled = false
	end
	table.insert(straze, g:GetPropertyChangedSignal("Enabled"):Connect(function()
		if aktywny and g.Enabled then
			schowane[g] = true
			g.Enabled = false
		end
	end))
end

-- ekran wyboru klasy obecnej gry (src/client/ClassSelectClient) trwa: trzyma kamerę w sali i swoje światło sali, póki
-- gracz nie wybierze klasy i rasy. Przy AutoStart w obecnym miejscu BONK rusza dopiero po nim (w osobnym miejscu go nie ma).
local function wyborKlasyTrwa(): boolean
	local g = pg:FindFirstChild("ClassSelect")
	if not g or not g:IsA("ScreenGui") then
		return false
	end
	-- koniec wyboru: klasa wybrana, ekran zamknięty, kamera wróciła do postaci (rasa bywa wybierana w tym samym ekranie)
	return not (gracz:GetAttribute("Class") ~= nil and not g.Enabled and kamera.CameraType ~= Enum.CameraType.Scriptable)
end

local function schowajCudze()
	for _, g in pg:GetChildren() do
		schowaj(g)
	end
	table.insert(straze, pg.ChildAdded:Connect(schowaj))
end

local function przywrocCudze()
	for _, c in straze do
		c:Disconnect()
	end
	straze = {}
	for g in schowane do
		-- ekranu wyboru klasy nie przywracamy, gdy klasa została już wybrana (ekran sam by się zamknął)
		if g.Parent and not (g.Name == "ClassSelect" and gracz:GetAttribute("Class") ~= nil) then
			g.Enabled = true
		end
	end
	schowane = {}
end

local function kameraNaPostac()
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if hum then
		kamera.CameraType = Enum.CameraType.Custom
		kamera.CameraSubject = hum
	end
end

------------------------------------------------------------------ widoki potworów
local widoki: { [Configuration]: any } = {}
local loty: { any } = {}
local wysokosci: { [string]: number } = {}
local czesciWidokow = 0

local function wzorzec(klucz: string): Model
	local wz = wzorce and wzorce:FindFirstChild(klucz)
	if wz then
		return wz:Clone()
	end
	-- zastępcza bryła (bez wzorców)
	local m = Instance.new("Model")
	local p = Instance.new("Part")
	p.Name = "Korzen"
	p.Size = Vector3.new(3, 3, 3)
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Color = Color3.fromRGB(140, 200, 90)
	p.Parent = m
	m.PrimaryPart = p
	return m
end

local function liczCzesci(m: Model): number
	local n = 0
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			n += 1
		end
	end
	return n
end

local function zbuduj(cfg: Configuration): any
	local klucz = cfg:GetAttribute("Gatunek")
	if type(klucz) ~= "string" then
		return nil
	end
	local m = wzorzec(klucz)
	local korzen = m.PrimaryPart
	if not korzen then
		m:Destroy()
		return nil
	end
	korzen.Anchored = true
	local rzadki = cfg:GetAttribute("Rzadki") == true
	if rzadki then
		m:ScaleTo(D.rzadki.skala)
		local h = Instance.new("Highlight")
		h.FillColor = Color3.fromHex(D.rzadki.kolor)
		h.FillTransparency = 0.55
		h.OutlineColor = Color3.fromHex(D.rzadki.kolor)
		h.DepthMode = Enum.HighlightDepthMode.Occluded
		h.Parent = m
	end
	m.Name = cfg.Name
	m.Parent = lokalne
	local n = liczCzesci(m)
	czesciWidokow += n
	return { cfg = cfg, model = m, korzen = korzen, nr = cfg:GetAttribute("Nr") or 0, faza = math.random() * 6,
		drganie = 0, pasek = nil, wypelnienie = nil, pasekDo = 0, yaw = math.pi / 2, rzadki = rzadki, czesci = n,
		etykieta = nil }
end

local function usunNaglowek(w: any)
	if w.pasek then
		w.pasek:Destroy()
		w.pasek = nil
	end
	if w.etykieta then
		w.etykieta:Destroy()
		w.etykieta = nil
	end
end

local liczbaObrysow = 0
local OBRYSY_MAKS = 10 -- komiksowy obrys (Highlight) najbliższych potworów; silnik pozwala na 31 naraz u gracza

local function usunWidok(w: any)
	czesciWidokow -= w.czesci
	if w.obrys then
		liczbaObrysow -= 1
		w.obrys = nil
	end
	usunNaglowek(w)
	w.model:Destroy()
end

local function polozenie(cfg: Configuration, t: number): Vector3?
	local od, cel = cfg:GetAttribute("Od"), cfg:GetAttribute("Cel")
	if typeof(od) ~= "Vector3" or typeof(cel) ~= "Vector3" then
		return nil
	end
	local x, z = L.pozycja(od.X, od.Z, cel.X, cel.Z, cfg:GetAttribute("T0") or 0, cfg:GetAttribute("Pr") or 0, t)
	return Vector3.new(x, od.Y, z)
end

local warstwa: ScreenGui? = nil -- napisy i paski nad potworami (ekran, rzut ze świata), istnieje w BONK

local function pasekZycia(w: any)
	if w.pasek or not warstwa or w.cfg:GetAttribute("Straznik") then
		return -- Strażnik: wspólny pasek u góry ekranu (OknaBonk)
	end
	local tlo = Instance.new("Frame")
	tlo.Name = "Pasek"
	tlo.AnchorPoint = Vector2.new(0.5, 1)
	tlo.Size = UDim2.fromOffset(84, 13)
	tlo.BackgroundColor3 = Color3.fromHex(D.ui.kolory.tusz)
	tlo.BorderSizePixel = 0
	tlo.Visible = false
	local wyp = Instance.new("Frame")
	wyp.Position = UDim2.fromOffset(2, 2)
	wyp.Size = UDim2.new(1, -4, 1, -4)
	wyp.BackgroundColor3 = Color3.fromRGB(120, 230, 90)
	wyp.BorderSizePixel = 0
	wyp.Parent = tlo
	tlo.Parent = warstwa
	w.pasek, w.wypelnienie = tlo, wyp
end

local function etykietaRzadkiego(w: any)
	if w.etykieta or not warstwa then
		return
	end
	local t = Instance.new("TextLabel")
	t.Name = "Rzadki"
	t.AnchorPoint = Vector2.new(0.5, 1)
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromOffset(90, 30)
	t.Text = D.ui.rzadki
	t.TextScaled = true
	t.Font = Enum.Font[D.ui.czcionka] or Enum.Font.LuckiestGuy
	t.TextColor3 = Color3.fromHex(D.rzadki.kolor)
	t.Visible = false
	local o = Instance.new("UIStroke")
	o.Thickness = 2
	o.Color = Color3.fromHex(D.ui.kolory.tusz)
	o.Parent = t
	t.Parent = warstwa
	w.etykieta = t
end

-- pasek życia i RARE nad głową: rzut punktu nad modelem na ekran
local function naglowek(w: any, glowa: Vector3)
	if w.pasek then
		local jest, x, y = Efekty.rzut(glowa + Vector3.new(0, 0.8, 0), 90)
		w.pasek.Visible = jest
		w.pasek.Position = UDim2.fromOffset(x, y)
	end
	if w.etykieta then
		local jest, x, y = Efekty.rzut(glowa + Vector3.new(0, 1.6, 0), 120)
		w.etykieta.Visible = jest
		w.etykieta.Position = UDim2.fromOffset(x, y - (if w.pasek and w.pasek.Visible then 16 else 0))
	end
end

------------------------------------------------------------------ cel w zasięgu (pierścień) i BONK
-- pierścień pod celem w zasięgu: niewidzialna część + krąg z otworem (CylinderHandleAdornment)
local pierscien = Instance.new("Part")
pierscien.Name = "CelBonk"
pierscien.Anchored = true
pierscien.CanCollide = false
pierscien.CanQuery = false
pierscien.CanTouch = false
pierscien.CastShadow = false
pierscien.Transparency = 1
pierscien.Size = Vector3.new(0.2, 0.2, 0.2)
local krag = Instance.new("CylinderHandleAdornment")
krag.Adornee = pierscien
krag.Color3 = Color3.fromHex(D.ui.kolory.przycisk)
krag.Transparency = 0.15
krag.Height = 0.25
krag.Radius = 3
krag.InnerRadius = 2.5
krag.CFrame = CFrame.Angles(math.pi / 2, 0, 0)
krag.Parent = pierscien
local celTeraz: Configuration? = nil

local ui: any = nil
local okna: any = nil
local ostatniBonk = 0
local trzymane: { [any]: boolean } = {}
local wyslane = 0

local function hrp(): BasePart?
	local postac = gracz.Character
	local h = postac and postac:FindFirstChild("HumanoidRootPart")
	return if h and h:IsA("BasePart") then h else nil
end

local function bonkRaz()
	if not aktywny then
		return
	end
	local zegar = os.clock()
	if zegar - ostatniBonk < 1 / D.bonk.uderzen_na_s then
		return
	end
	ostatniBonk = zegar
	wyslane += 1
	evBonk:FireServer()
	local h = hrp()
	if h then
		E:zamach(h.CFrame * CFrame.new(0, 0.5, 0))
	end
end

local function cokolwiekTrzymane(): boolean
	return next(trzymane) ~= nil
end

UserInputService.InputBegan:Connect(function(wejscie, przetworzone)
	if not aktywny or przetworzone then
		return
	end
	local k = wejscie.KeyCode
	local typ = wejscie.UserInputType
	if k == Enum.KeyCode.E or k == Enum.KeyCode.ButtonX or k == Enum.KeyCode.ButtonR2 then
		trzymane[k] = true
		bonkRaz()
	elseif typ == Enum.UserInputType.MouseButton1 then
		trzymane[typ] = true
		bonkRaz()
	end
end)
UserInputService.InputEnded:Connect(function(wejscie)
	trzymane[wejscie.KeyCode] = nil
	trzymane[wejscie.UserInputType] = nil
	if wejscie.UserInputType == Enum.UserInputType.Touch then
		trzymane["dotyk"] = nil
	end
	if ui and not cokolwiekTrzymane() then
		ui:wcisnij(false)
	end
end)

------------------------------------------------------------------ bramy (wrota u gracza)
local function odblokowane(): number
	return tonumber(gracz:GetAttribute("BonkOdblokowane")) or 1
end

-- czy gracz pokonał Strażnika krainy nr (atrybut BonkStraznicy „1,0,0” od serwera)
local function pokonal(nr: number): boolean
	local napis = gracz:GetAttribute("BonkStraznicy")
	if type(napis) ~= "string" then
		return false
	end
	local i = 0
	for kawalek in string.gmatch(napis, "[^,]+") do
		i += 1
		if i == nr then
			return (tonumber(kawalek) or 0) > 0
		end
	end
	return false
end

local kolizjeWrot: { [BasePart]: boolean } = setmetatable({}, { __mode = "k" }) -- kolizje wrót z mapy (przed otwarciem)
local function uaktualnijBramy()
	local n = odblokowane()
	for k, K in D.krainy do
		local otwarta = k < n
		local sciana = folderBram and folderBram:FindFirstChild("Brama" .. k)
		if sciana and sciana:IsA("BasePart") then
			sciana.CanCollide = not otwarta
			local napis = sciana:FindFirstChild("Napis", true)
			if napis and napis:IsA("TextLabel") then
				if k >= #D.krainy then
					napis.Text = D.ui.brama_dalej
				elseif otwarta then
					napis.Text = D.ui.brama_otwarta
				elseif (tonumber(gracz:GetAttribute("BonkMoc")) or 1) >= K.brama.wymagana and not pokonal(k) then
					napis.Text = D.ui.straznik_brama
				else
					napis.Text = string.format(D.ui.brama_zamknieta, L.format(K.brama.wymagana))
				end
			end
		end
		local folderKrainy = mapa and mapa:FindFirstChild(K.folder)
		local wrota: Instance? = folderKrainy
		if wrota then
			for kawalek in string.gmatch(K.brama.wrota, "[^/]+") do
				wrota = wrota and wrota:FindFirstChild(kawalek)
			end
		end
		if wrota then
			for _, d in wrota:GetDescendants() do
				if d:IsA("BasePart") then
					if kolizjeWrot[d] == nil then
						kolizjeWrot[d] = d.CanCollide
					end
					d.LocalTransparencyModifier = if otwarta then 1 else 0
					d.CanCollide = not otwarta and kolizjeWrot[d]
				end
			end
		end
	end
end

------------------------------------------------------------------ pety za graczami (każdy klient rysuje wszystkich w zasięgu)
local PU = D.petyUst
local petyGraczy: { [Player]: any } = {}
local czesciPetow = 0

local function usunPety(g: Player)
	local w = petyGraczy[g]
	if not w then
		return
	end
	for _, p in w.modele do
		czesciPetow -= p.czesci
		p.model:Destroy()
	end
	petyGraczy[g] = nil
end

local function modelPeta(id: string): any
	local P = D.pety[id]
	if not P then
		return nil
	end
	local m = wzorzec(P.wzorzec)
	local korzen = m.PrimaryPart
	if not korzen then
		m:Destroy()
		return nil
	end
	korzen.Anchored = true
	m.Name = "Pet_" .. id
	m.Parent = lokalne
	local n = liczCzesci(m)
	czesciPetow += n
	return { model = m, korzen = korzen, czesci = n, id = id, poz = nil, yaw = 0, faza = math.random() * 6 }
end

local function krokPetow(dt: number, oko: Vector3, zegar: number)
	for _, g in Players:GetPlayers() do
		local napis = g:GetAttribute("BonkPety")
		local postac = g.Character
		local h = postac and postac:FindFirstChild("HumanoidRootPart")
		local hum = postac and postac:FindFirstChildOfClass("Humanoid")
		local widoczny = g:GetAttribute("BonkAktywny") == true and type(napis) == "string" and napis ~= "" and h ~= nil
			and h:IsA("BasePart") and hum ~= nil and (h.Position - oko).Magnitude <= PU.za_graczem.widok
		local w = petyGraczy[g]
		if not widoczny then
			if w then
				usunPety(g)
			end
			continue
		end
		if w and w.napis ~= napis then
			usunPety(g)
			w = nil
		end
		if not w then
			w = { napis = napis, modele = {} }
			for id in string.gmatch(napis, "[^,]+") do
				local p = modelPeta(id)
				if p then
					table.insert(w.modele, p)
				end
			end
			petyGraczy[g] = w
		end
		local korzenG: any = h
		local humG: any = hum
		local cf = korzenG.CFrame
		local ziemiaY = korzenG.Position.Y - humG.HipHeight - korzenG.Size.Y / 2
		local ruch = korzenG.AssemblyLinearVelocity.Magnitude > 2
		local n = #w.modele
		for i, p in w.modele do
			local x = (i - (n + 1) / 2) * PU.za_graczem.bok
			local z = PU.za_graczem.odstep + (if i == 2 and n == 3 then 1.4 else 0)
			local cel = (cf * CFrame.new(x, 0, z)).Position
			cel = Vector3.new(cel.X, ziemiaY, cel.Z)
			if not p.poz or (p.poz - cel).Magnitude > 40 then
				p.poz = cel
			end
			local a = math.min(1, dt * PU.za_graczem.predkosc * 0.6)
			p.poz = p.poz:Lerp(cel, a)
			local d = cel - p.poz
			local docelowy = if d.Magnitude > 0.3 then math.atan2(-d.X, -d.Z) else select(2, cf:ToOrientation())
			local roznica = (docelowy - p.yaw + math.pi) % (2 * math.pi) - math.pi
			p.yaw += roznica * math.min(1, dt * 8)
			local skok = if ruch then math.abs(math.sin(zegar * 9 + p.faza)) * 0.6 else math.abs(math.sin(zegar * 2.5 + p.faza)) * 0.15
			p.korzen.CFrame = CFrame.new(p.poz + Vector3.new(0, skok, 0)) * CFrame.Angles(0, p.yaw, 0)
		end
	end
	for g in petyGraczy do
		if not g.Parent then
			usunPety(g)
		end
	end
end

------------------------------------------------------------------ Moc nad głową każdego gracza (warstwa ekranu)
local etykietyMocy: { [Player]: TextLabel } = {}

local function usunEtykiety()
	for g, t in etykietyMocy do
		t:Destroy()
		etykietyMocy[g] = nil
	end
end

local function krokEtykiet(oko: Vector3)
	if not warstwa then
		return
	end
	for _, g in Players:GetPlayers() do
		local postac = g.Character
		local glowa = postac and postac:FindFirstChild("Head")
		local t = etykietyMocy[g]
		local jest = g:GetAttribute("BonkAktywny") == true and glowa ~= nil and glowa:IsA("BasePart")
			and (glowa.Position - oko).Magnitude <= D.pokazanie.nad_glowa
		if not jest then
			if t then
				t.Visible = false
			end
			continue
		end
		if not t then
			t = Instance.new("TextLabel")
			t.Name = "Moc_" .. g.UserId
			t.AnchorPoint = Vector2.new(0.5, 1)
			t.Size = UDim2.fromOffset(110, 26)
			t.BackgroundTransparency = 1
			t.TextScaled = true
			t.Font = Enum.Font[D.ui.czcionka_cyfr] or Enum.Font.FredokaOne
			t.TextColor3 = Color3.fromHex(D.ui.kolory.moc)
			t.ZIndex = 3
			local o = Instance.new("UIStroke")
			o.Thickness = 2.5
			o.Color = Color3.fromHex(D.ui.kolory.tusz)
			o.Parent = t
			t.Parent = warstwa
			etykietyMocy[g] = t
		end
		local korona = g:GetAttribute("BonkKorona") == true
		local g0: any = glowa
		local widac, x, y = Efekty.rzut(g0.Position + Vector3.new(0, if korona then 2.4 else 1.6, 0), D.pokazanie.nad_glowa)
		t.Visible = widac
		t.Position = UDim2.fromOffset(x, y)
		t.Text = L.format(tonumber(g:GetAttribute("BonkMoc")) or 1) .. " " .. D.ui.moc
	end
	for g, t in etykietyMocy do
		if not g.Parent then
			t:Destroy()
			etykietyMocy[g] = nil
		end
	end
end

------------------------------------------------------------------ wyklucie: scena na środku ekranu (ViewportFrame w oknach)
-- jajko trzęsie się coraz mocniej, pęka błyskiem w kolorze rzadkości, pet wyskakuje i rośnie, NEW PET! / DUPLICATE
local wyklucie: any = nil

local function koniecWyklucia()
	if not wyklucie then
		return
	end
	if okna then
		okna:wyklucie(nil)
	end
	wyklucie = nil
end

local function startWyklucia(z)
	koniecWyklucia()
	local J = D.jajka[z.jajko]
	local P = D.pety[z.pet]
	local vf = okna and okna:scena(true)
	if not J or not P or not vf then
		return
	end
	local jajko = wzorzec(J.wzorzec)
	jajko:PivotTo(CFrame.new())
	jajko.Parent = vf
	wyklucie = { t = 0, jajko = jajko, pet = nil, z = z, J = J, P = P, pekniete = false, vf = vf }
	zagraj("trzesienie", 0.9)
	-- inni widzą błysk nad inkubatorem
	E:iskry(Vector3.new(J.miejsce[1], J.miejsce[2] + 5, J.miejsce[3]), Color3.fromHex(D.rzadkosci[z.rzadkosc].kolor), 10, 0.8)
end

local function krokWyklucia(dt: number)
	local w = wyklucie
	if not w then
		return
	end
	w.t += dt
	local wysJ = w.J.wysokosc
	if w.t < 1.6 then
		local sila = 0.05 + w.t * 0.14
		local kiw = math.sin(w.t * (18 + w.t * 14)) * sila
		w.jajko:PivotTo(CFrame.new(0, 2.3 - wysJ / 2, 0) * CFrame.Angles(0, 0, kiw))
		if w.t > 0.8 and not w.drugie then
			w.drugie = true
			zagraj("trzesienie", 1.15)
		end
	elseif not w.pekniete then
		w.pekniete = true
		w.jajko:Destroy()
		w.jajko = nil
		local pet = wzorzec(w.P.wzorzec)
		pet:PivotTo(CFrame.new())
		pet.Parent = w.vf
		w.pet = pet
		zagraj("wyklucie")
		if w.z.rzadkosc >= 4 then
			zagraj("brama")
		end
		local R = D.rzadkosci[w.z.rzadkosc]
		if okna then
			okna:blysk(R.kolor)
			okna:wyklucie({ nowy = w.z.nowy, nazwa = w.P.nazwa, rzadkosc = R.nazwa, kolor = R.kolor, kopie = w.z.kopie })
		end
	end
	if w.pet then
		local tp = w.t - 1.6
		local s = if tp < 0.25 then 0.4 + tp / 0.25 * 0.9 elseif tp < 0.45 then 1.3 - (tp - 0.25) / 0.2 * 0.3 else 1
		local skok = if tp < 0.4 then math.sin(tp / 0.4 * math.pi) * 1.2 else 0
		local m = 4.2 / math.max(1, w.P.wysokosc) -- pet wypełnia scenę jak jajko
		pcall(function()
			w.pet:ScaleTo(math.max(0.2, s * m))
		end)
		local h = w.P.wysokosc * s * m
		w.pet:PivotTo(CFrame.new(0, 2.3 - h / 2 + skok, 0) * CFrame.Angles(0, math.sin(tp * 2.2) * 0.6, 0))
		if tp > 3.0 then
			koniecWyklucia()
		end
	end
end

------------------------------------------------------------------ strefy: stoisko pałek i inkubator (przycisk na dole)
local function krokStref(hp: Vector3?)
	if not okna then
		return
	end
	if not hp then
		okna:kontekst(nil)
		return
	end
	local rodzaj, nr, naj = nil, nil, math.huge
	for _, sk in D.sklepy do
		local d = Vector2.new(hp.X - sk.miejsce[1], hp.Z - sk.miejsce[3]).Magnitude
		if d <= D.sklep.zasieg and d < naj then
			rodzaj, nr, naj = "sklep", sk.kraina, d
		end
	end
	for _, J in D.jajka do
		local d = Vector2.new(hp.X - J.miejsce[1], hp.Z - J.miejsce[3]).Magnitude
		if d <= PU.zasieg_inkubatora and d < naj then
			rodzaj, nr, naj = "jajko", J.nr, d
		end
	end
	if wyklucie then
		rodzaj, nr = nil, nil -- w trakcie wyklucia przycisk i szanse schowane (scena na środku)
	end
	okna:kontekst(rodzaj, nr)
end

-- wspólny pasek życia najbliższego Strażnika (w zasięgu)
local function krokStraznika(hp: Vector3?)
	if not okna then
		return
	end
	local naj, odl = nil, math.huge
	if hp then
		for _, S in D.straznicy do
			local d = Vector2.new(hp.X - S.miejsce[1], hp.Z - S.miejsce[3]).Magnitude
			if d <= D.straznik.pasek_zasieg and d < odl then
				naj, odl = S, d
			end
		end
	end
	if not naj then
		okna:straznik(nil)
		return
	end
	local cfg = folderPotworow:FindFirstChild("straznik_" .. naj.kraina)
	if not cfg then
		okna:straznik(nil)
		return
	end
	local powrot = cfg:GetAttribute("Powrot")
	okna:straznik({ nazwa = naj.nazwa, hp = tonumber(cfg:GetAttribute("Hp")) or 0, hpMax = tonumber(cfg:GetAttribute("HpMax")) or 1,
		zywy = cfg:GetAttribute("Zywy") == true,
		powrotZa = if type(powrot) == "number" then powrot - workspace:GetServerTimeNow() else 0 })
end

------------------------------------------------------------------ włączenie i wyłączenie BONK u gracza
local krainaTeraz = 0
local podpowiedzNr: number? = nil

local function odswiezLiczby(przyrostMocy: number?, przyrostMonet: number?)
	if not ui then
		return
	end
	ui:moc(tonumber(gracz:GetAttribute("BonkMoc")) or 1, przyrostMocy)
	ui:monety(tonumber(gracz:GetAttribute("BonkMonety")) or 0, przyrostMonet)
end

local function wlacz()
	if aktywny then
		return
	end
	aktywny = true
	schowajCudze()
	local dotyk = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
	local emulacja = kontener:GetAttribute("EmulacjaEkranu")
	if typeof(emulacja) ~= "Vector2" then
		emulacja = nil
	end
	ui = Interfejs.nowy(folderUI, D, L, { dotyk = dotyk or emulacja ~= nil, emulacja = emulacja })
	warstwa = Instance.new("ScreenGui")
	warstwa.Name = "BonkNapisy"
	warstwa.IgnoreGuiInset = true
	warstwa.ResetOnSpawn = false
	warstwa.DisplayOrder = 4
	warstwa.Parent = folderUI
	E:warstwa2D(warstwa)
	okna = Okna.nowe(folderUI, D, L, { dotyk = dotyk or emulacja ~= nil, emulacja = emulacja }, function(rodzaj, arg)
		zagraj("klik")
		evAkcja:FireServer(rodzaj, arg)
	end, wzorce)
	ui.przycisk.InputBegan:Connect(function(wejscie)
		local typ = wejscie.UserInputType
		if typ == Enum.UserInputType.Touch or typ == Enum.UserInputType.MouseButton1 then
			trzymane[if typ == Enum.UserInputType.Touch then "dotyk" else typ] = true
			ui:wcisnij(true)
			bonkRaz()
		end
	end)
	ui.przycisk.InputEnded:Connect(function(wejscie)
		local typ = wejscie.UserInputType
		trzymane[if typ == Enum.UserInputType.Touch then "dotyk" else typ] = nil
		if not cokolwiekTrzymane() then
			ui:wcisnij(false)
		end
	end)
	ui.przycisk.Activated:Connect(function(wejscie)
		if wejscie and wejscie.UserInputType == Enum.UserInputType.Gamepad1 then
			bonkRaz()
		end
	end)
	odswiezLiczby()
	krainaTeraz = 0
	podpowiedzNr = if gracz:GetAttribute("BonkSamouczek") == true then nil else 1
	ui:podpowiedz(podpowiedzNr)
	pierscien.Parent = lokalne
	uaktualnijBramy()
end

local function wylacz()
	if not aktywny then
		return
	end
	aktywny = false
	trzymane = {}
	if ui then
		ui:zniszcz()
		ui = nil
	end
	koniecWyklucia()
	if okna then
		okna:zniszcz()
		okna = nil
	end
	for g in petyGraczy do
		usunPety(g)
	end
	usunEtykiety()
	przywrocCudze()
	muzyka:Stop()
	pierscien.Parent = nil
	for cfg, w in widoki do
		usunWidok(w)
		widoki[cfg] = nil
	end
	E:wyczysc()
	E:warstwa2D(nil)
	if warstwa then
		warstwa:Destroy()
		warstwa = nil
	end
end

local czekaNaWybor = false
local function uzgodnijAktywny()
	if gracz:GetAttribute("BonkAktywny") ~= true then
		wylacz()
		return
	end
	if czekaNaWybor then
		return
	end
	czekaNaWybor = true
	while wyborKlasyTrwa() and gracz:GetAttribute("BonkAktywny") == true do
		task.wait(0.3)
	end
	czekaNaWybor = false
	if gracz:GetAttribute("BonkAktywny") == true then
		wlacz()
		kameraNaPostac()
	end
end
gracz:GetAttributeChangedSignal("BonkAktywny"):Connect(function()
	task.spawn(uzgodnijAktywny)
end)
gracz:GetAttributeChangedSignal("BonkMoc"):Connect(function()
	odswiezLiczby()
end)
gracz:GetAttributeChangedSignal("BonkMonety"):Connect(function()
	odswiezLiczby()
end)
gracz:GetAttributeChangedSignal("BonkOdblokowane"):Connect(uaktualnijBramy)
gracz:GetAttributeChangedSignal("BonkStraznicy"):Connect(uaktualnijBramy)
-- okna od nowa po zmianie stanu z serwera (zbiorczo, raz na klatkę)
local doOdswiezenia = false
for _, a in { "BonkPalka", "BonkPety", "BonkPetyMam", "BonkKsiega", "BonkAutoPety", "BonkPrezentMozna", "BonkPrezentDzien",
	"BonkMonety", "BonkMnoznikPetow" } do
	gracz:GetAttributeChangedSignal(a):Connect(function()
		if doOdswiezenia then
			return
		end
		doOdswiezenia = true
		task.defer(function()
			doOdswiezenia = false
			if okna then
				okna:odswiez()
			end
		end)
	end)
end
gracz:GetAttributeChangedSignal("BonkSamouczek"):Connect(function()
	if aktywny and ui and gracz:GetAttribute("BonkSamouczek") == false and podpowiedzNr == nil then
		podpowiedzNr = 1
		ui:podpowiedz(1)
	end
end)

------------------------------------------------------------------ zdarzenia z serwera
local function widokDla(id: string): (Configuration?, any)
	local cfg = folderPotworow:FindFirstChild(id)
	if not cfg or not cfg:IsA("Configuration") then
		return nil, nil
	end
	return cfg, widoki[cfg]
end

local function kolorGatunku(cfg: Configuration): Color3
	return if cfg:GetAttribute("Rzadki") == true then Color3.fromHex(D.rzadki.kolor) else Color3.fromRGB(255, 240, 200)
end

local slowoNr = 0
local ostatnieWyklucie: any = nil
local ostatnieOgloszenie: string? = nil
local promienZiemi = RaycastParams.new()
promienZiemi.FilterType = Enum.RaycastFilterType.Include
promienZiemi.FilterDescendantsInstances = if mapa then { mapa } else {}
promienZiemi.RespectCanCollide = true

local function startLotu(z, cfg: Configuration?, w: any)
	local od: Vector3 = z.od
	if (od - kamera.CFrame.Position).Magnitude > D.widok.lot_widoczny then
		if w and cfg then
			usunWidok(w)
			widoki[cfg] = nil
		end
		return
	end
	if not w and cfg then
		w = zbuduj(cfg)
	elseif w and cfg then
		widoki[cfg] = nil -- lot przejmuje model; odrodzony potwór dostanie nowy widok
	end
	if not w then
		return
	end
	usunNaglowek(w)
	local nosnik = Instance.new("Part")
	nosnik.Anchored = true
	nosnik.CanCollide = false
	nosnik.CanQuery = false
	nosnik.CanTouch = false
	nosnik.Transparency = 1
	nosnik.Size = Vector3.new(0.2, 0.2, 0.2)
	nosnik.Position = od
	nosnik.Parent = lokalne
	local klucz = w.cfg:GetAttribute("Gatunek")
	local wys = D.gatunki[klucz] and D.gatunki[klucz].wysokosc or 3
	E:smuga(nosnik, if z.hr then Color3.fromHex(D.ui.kolory.monety) else Color3.fromRGB(255, 255, 255), math.clamp(wys * 0.5, 1, 4))
	local kierunek = Vector3.new(z.ko.X - od.X, 0, z.ko.Z - od.Z)
	local os = if kierunek.Magnitude > 0.01 then kierunek.Unit:Cross(Vector3.yAxis) else Vector3.xAxis
	table.insert(loty, { w = w, z = z, t = 0, nosnik = nosnik, os = os, obroty = 2 + z.czas * 1.5, wys = wys,
		faza = "lot", ziemia = nil, yaw = w.yaw })
end

evZdarzenia.OnClientEvent:Connect(function(z)
	if type(z) ~= "table" then
		return
	end
	if z.t == "wyklucie" then
		startWyklucia(z)
		ostatnieWyklucie = z
		return
	elseif z.t == "kupiono" then
		zagraj("zakup")
		local P = D.palki[z.nr]
		if okna and P then
			okna:toast(P.nazwa .. "!  " .. string.format(D.ui.mnoznik, L.format(P.mnoznik)), D.ui.kolory.monety)
		end
		return
	elseif z.t == "odmowa" then
		if okna then
			okna:toast(if z.powod == "monety" then D.ui.za_malo elseif z.powod == "jutro" then D.ui.prezent_jutro else "...", "FF8A8A")
		end
		return
	elseif z.t == "prezent" then
		zagraj("monety")
		zagraj("wyklucie")
		if okna then
			okna:toast("+" .. L.format(z.monety) .. " " .. D.ui.monety, D.ui.kolory.monety)
		end
		if ui then
			ui:monety(tonumber(gracz:GetAttribute("BonkMonety")) or 0, z.monety)
		end
		return
	elseif z.t == "nagroda_straznika" then
		zagraj("brama")
		if okna then
			okna:toast(string.format(D.ui.straznik_pokonany, z.nazwa) .. "  +" .. L.format(z.monety) .. " " .. D.ui.monety,
				D.ui.kolory.monety)
		end
		if ui then
			ui:moc(tonumber(gracz:GetAttribute("BonkMoc")) or 1, z.moc)
		end
		return
	elseif z.t == "ogloszenie" then
		ostatnieOgloszenie = z.tekst
		if okna then
			okna:ogloszenie(z.tekst, z.kolor)
		end
		return
	end
	local moj = z.g == gracz.UserId
	local cfg, w = widokDla(z.id)
	if z.t == "cios" then
		if w then
			w.drganie = 0.18
			pasekZycia(w)
			w.pasekDo = os.clock() + 3
			local hpMax = tonumber(cfg and cfg:GetAttribute("HpMax")) or 1
			if w.wypelnienie then
				w.wypelnienie.Size = UDim2.new(math.clamp(z.hp / hpMax, 0, 1), -4, 1, -4)
			end
			local glowa = w.korzen.Position + Vector3.new(0, (wysokosci[w.cfg.Name] or 3) + 0.5, 0)
			E:liczba(glowa, "-" .. L.format(z.ile), Color3.fromRGB(255, 255, 255))
			if moj then
				E:iskry(glowa - Vector3.new(0, 1, 0), Color3.fromRGB(255, 235, 160), 4, 0.6)
			end
		end
		if moj then
			zagraj("cios", 1 + (math.random() - 0.5) * 0.15)
		end
	elseif z.t == "lot" then
		startLotu(z, cfg, w)
		local nad = z.od + Vector3.new(0, 4, 0)
		if (z.od - kamera.CFrame.Position).Magnitude < D.widok.lot_widoczny then
			slowoNr = (slowoNr % #D.ui.slowa) + 1
			local slowo = if z.hr then D.ui.home_run else D.ui.slowa[slowoNr]
			E:slowo(nad, slowo, if z.hr then Color3.fromHex(D.ui.kolory.monety) else Color3.fromHex(D.ui.kolory.przycisk),
				if z.hr then 1.4 else 1)
			E:iskry(nad - Vector3.new(0, 2, 0), if cfg then kolorGatunku(cfg) else Color3.new(1, 1, 1), 10, 1)
		end
		if moj then
			zagraj(if z.hr then "home_run" else "bonk", 1 + (math.random() - 0.5) * 0.1)
			local h = hrp()
			local ile = math.clamp(math.floor(math.log(z.monety + 1, 2)) + 2, 3, 10)
			E:monety(z.od, ile, h, function()
				zagraj("monety")
			end)
			if ui then
				ui:moc(tonumber(gracz:GetAttribute("BonkMoc")) or 1, z.moc)
				ui:monety(tonumber(gracz:GetAttribute("BonkMonety")) or 0, z.monety)
				if z.hr then
					ui:homeRun()
				end
			end
			if podpowiedzNr == 1 or podpowiedzNr == 2 then
				podpowiedzNr = 3
				if ui then
					ui:podpowiedz(3)
				end
				task.delay(6, function()
					if podpowiedzNr == 3 then
						podpowiedzNr = nil
						if ui then
							ui:podpowiedz(nil)
						end
					end
				end)
			end
			if z.brama then
				zagraj("brama")
			end
		else
			-- cudzy BONK: monety lecą do tamtego gracza (gdy blisko)
			local inny = Players:GetPlayerByUserId(z.g)
			local ih = inny and inny.Character and inny.Character:FindFirstChild("HumanoidRootPart")
			if ih and ih:IsA("BasePart") and (z.od - kamera.CFrame.Position).Magnitude < 120 then
				E:monety(z.od, 3, ih)
			end
		end
	end
end)

------------------------------------------------------------------ pętla klatki
local pomiar = { klatek = 0, suma = 0, maks = 0, petlaSuma = 0, petlaMaks = 0 }
local akumBram = 0
local nrKlatki = 0

local function krokLotow(dt: number)
	local i = 1
	while i <= #loty do
		local l = loty[i]
		l.t += dt
		local z = l.z
		local korzen = l.w.korzen
		local skonczony = false
		if l.faza == "lot" then
			local f = math.clamp(l.t / z.czas, 0, 1)
			local x, y, zz = L.punktLotu(z.od.X, z.od.Y, z.od.Z, z.ko.X, z.ko.Y, z.ko.Z, z.wys, f)
			local p = Vector3.new(x, y, zz)
			l.nosnik.Position = p + Vector3.new(0, l.wys * 0.4, 0)
			local obrot = CFrame.fromAxisAngle(l.os, f * l.obroty * 2 * math.pi) * CFrame.Angles(0, f * 3, 0)
			korzen.CFrame = CFrame.new(p + Vector3.new(0, l.wys * 0.5, 0)) * obrot * CFrame.Angles(0, l.yaw, 0)
				* CFrame.new(0, -l.wys * 0.5, 0)
			if f >= 1 and z.niebo then
				-- Strażnik znika w niebie z błyskiem
				E:iskry(p, Color3.fromHex(D.ui.kolory.monety), 22, 1.6)
				E:slowo(p, D.ui.home_run, Color3.fromHex(D.ui.kolory.monety), 1.2)
				skonczony = true
			elseif f >= 1 then
				local traf = workspace:Raycast(p + Vector3.new(0, 25, 0), Vector3.new(0, -70, 0), promienZiemi)
				if traf then
					l.faza = "lezy"
					l.t = 0
					local ziemia = traf.Position
					korzen.CFrame = CFrame.new(ziemia) * CFrame.Angles(0, l.yaw + math.random(), 0)
						* CFrame.Angles(math.rad(-80), 0, 0) * CFrame.new(0, -l.wys * 0.15, 0)
					if (ziemia - kamera.CFrame.Position).Magnitude < 160 then
						E:plask(ziemia, Color3.fromRGB(235, 225, 200))
						E:slowo(ziemia + Vector3.new(0, 2, 0), D.ui.plask, Color3.fromRGB(255, 255, 255), 0.7)
						if z.g == gracz.UserId then
							zagraj("plask")
						end
					end
				else
					l.faza = "spada"
					l.t = 0
					l.spad = p
				end
			end
		elseif l.faza == "lezy" then
			if l.t > 0.7 then
				skonczony = true
			end
		elseif l.faza == "spada" then
			l.spad -= Vector3.new(0, 60 * dt, 0)
			korzen.CFrame = CFrame.new(l.spad) * CFrame.Angles(l.t * 5, l.t * 3, 0)
			if l.t > 0.9 then
				skonczony = true
			end
		end
		if skonczony then
			if l.faza == "lezy" then
				E:iskry(korzen.Position + Vector3.new(0, 1, 0), Color3.fromRGB(230, 230, 230), 6, 0.5)
			end
			l.nosnik:Destroy()
			usunWidok(l.w)
			table.remove(loty, i)
		else
			i += 1
		end
	end
end

RunService.RenderStepped:Connect(function(dt)
	local t0 = os.clock()
	nrKlatki += 1
	pomiar.klatek += 1
	pomiar.suma += dt
	if dt > pomiar.maks then
		pomiar.maks = dt
	end
	E:krok(dt)
	krokLotow(dt)
	krokWyklucia(dt)
	if ui then
		ui:krok(dt)
	end
	if okna then
		okna:krok(dt)
	end
	if not aktywny then
		return
	end
	local oko = kamera.CFrame.Position
	local h = hrp()
	local hp = h and h.Position
	local t = workspace:GetServerTimeNow()
	local zegar = os.clock()
	local W = D.widok
	local najblizszy, najOdl = nil, math.huge
	for _, cfg in folderPotworow:GetChildren() do
		if not cfg:IsA("Configuration") then
			continue
		end
		local w = widoki[cfg]
		local zywy = cfg:GetAttribute("Zywy") == true
		local poz = polozenie(cfg, t)
		if not zywy or not poz then
			-- po BONK widok czeka chwilę na zdarzenie „lot” (ono zabiera model do lotu); bez lotu znika
			if w then
				if not w.martwy then
					w.martwy = zegar
				elseif zegar - w.martwy > 0.6 then
					usunWidok(w)
					widoki[cfg] = nil
				end
			end
			continue
		end
		local odl = (poz - oko).Magnitude
		if w and (w.nr ~= cfg:GetAttribute("Nr") or odl > W.usuniecie) then
			usunWidok(w)
			widoki[cfg] = nil
			w = nil
		end
		if not w and odl <= W.budowa then
			w = zbuduj(cfg)
			if w then
				widoki[cfg] = w
				local klucz = cfg:GetAttribute("Gatunek")
				wysokosci[cfg.Name] = (D.gatunki[klucz] and D.gatunki[klucz].wysokosc or 3) * (if w.rzadki then D.rzadki.skala else 1)
			end
		end
		if w then
			if odl <= W.ruch_blisko or (nrKlatki + math.floor(w.faza * 10)) % 4 == 0 or w.drganie > 0 then
				-- obrót: do gracza, gdy blisko; inaczej w stronę kroku
				local cel: Vector3? = nil
				if hp and (hp - poz).Magnitude < 28 then
					cel = hp
				else
					local c = cfg:GetAttribute("Cel")
					if typeof(c) == "Vector3" and (c - poz).Magnitude > 0.3 then
						cel = c
					end
				end
				if cel then
					local d = Vector3.new(cel.X - poz.X, 0, cel.Z - poz.Z)
					if d.Magnitude > 0.1 then
						local docelowy = math.atan2(-d.X, -d.Z)
						local roznica = (docelowy - w.yaw + math.pi) % (2 * math.pi) - math.pi
						w.yaw += roznica * math.min(1, dt * 6)
					end
				end
				local bujanie = math.abs(math.sin(zegar * 4 + w.faza)) * 0.35
				local przes = Vector3.zero
				if w.drganie > 0 then
					w.drganie -= dt
					przes = Vector3.new(math.random() - 0.5, 0, math.random() - 0.5) * 0.8
				end
				local sciskanie = math.sin(zegar * 2 + w.faza) * 0.04
				w.korzen.CFrame = CFrame.new(poz + Vector3.new(0, bujanie, 0) + przes) * CFrame.Angles(0, w.yaw, sciskanie)
			end
			if w.pasek and zegar > w.pasekDo then
				w.pasek:Destroy()
				w.pasek = nil
			end
			if not w.rzadki then
				if odl < 45 and not w.obrys and liczbaObrysow < OBRYSY_MAKS then
					local h = Instance.new("Highlight")
					h.FillTransparency = 1
					h.OutlineColor = Color3.fromHex(D.ui.kolory.tusz)
					h.OutlineTransparency = 0.15
					h.DepthMode = Enum.HighlightDepthMode.Occluded
					h.Parent = w.model
					w.obrys = h
					liczbaObrysow += 1
				elseif odl > 55 and w.obrys then
					w.obrys:Destroy()
					w.obrys = nil
					liczbaObrysow -= 1
				end
			end
			if w.rzadki and not w.etykieta and odl < 120 then
				etykietaRzadkiego(w)
			end
			if w.pasek or w.etykieta then
				naglowek(w, w.korzen.Position + Vector3.new(0, wysokosci[cfg.Name] or 3, 0))
			end
			if hp then
				local dx, dz = poz.X - hp.X, poz.Z - hp.Z
				local promien = (cfg:GetAttribute("Promien") or 1.5) * (if w.rzadki then D.rzadki.skala else 1)
				local d = math.sqrt(dx * dx + dz * dz) - promien
				if d <= D.bonk.zasieg and d < najOdl and math.abs(poz.Y - (hp.Y - 3)) < 14 then
					najblizszy, najOdl = cfg, d
				end
			end
		end
	end
	celTeraz = najblizszy
	if najblizszy and widoki[najblizszy] then
		local w = widoki[najblizszy]
		local r = (najblizszy:GetAttribute("Promien") or 1.5) * (if w.rzadki then D.rzadki.skala else 1) + 0.8
		krag.Radius = r + 0.25 * math.sin(zegar * 8)
		krag.InnerRadius = krag.Radius - 0.45
		local p = w.korzen.Position
		pierscien.CFrame = CFrame.new(p.X, p.Y + 0.15, p.Z)
		krag.Visible = true
	else
		krag.Visible = false
	end
	-- trzymany przycisk: BONK co przytrzymanie_s
	if cokolwiekTrzymane() and zegar - ostatniBonk >= D.bonk.przytrzymanie_s then
		bonkRaz()
	end
	-- podpowiedzi: 1 → 2, gdy potwór w zasięgu
	if podpowiedzNr == 1 and najblizszy then
		podpowiedzNr = 2
		ui:podpowiedz(2)
	end
	-- kraina: nazwa przy wejściu i muzyka
	if hp then
		local nr = L.kraina(hp.X, D)
		if nr ~= krainaTeraz then
			krainaTeraz = nr
			ui:kraina(D.krainy[nr].nazwa)
			muzykaKrainy(nr)
		end
	end
	krokPetow(dt, oko, zegar)
	krokEtykiet(oko)
	if nrKlatki % 6 == 0 then
		krokStref(hp)
		krokStraznika(hp)
	end
	akumBram += dt
	if akumBram > 1 then
		akumBram = 0
		uaktualnijBramy() -- wrota mogły się właśnie wczytać (streaming)
	end
	local koszt = os.clock() - t0
	pomiar.petlaSuma += koszt
	if koszt > pomiar.petlaMaks then
		pomiar.petlaMaks = koszt
	end
end)

------------------------------------------------------------------ haczyki prób
-- grające dźwięki innych pakietów (np. muzyka stref obecnej gry) — do próby
local function inneDzwieki(): { string }
	local w = {}
	for _, d in game:GetDescendants() do
		local ok, jest = pcall(function()
			return d:IsA("Sound") and d.IsPlaying and d.Volume > 0 and not d:IsDescendantOf(folderDzwiekow)
		end)
		if ok and jest then
			table.insert(w, d:GetFullName() .. string.format(" (%.2f)", d.Volume))
		end
	end
	return w
end

local function nazwyWlaczonych(): { string }
	local w = {}
	for _, g in pg:GetChildren() do
		if g:IsA("ScreenGui") and g.Enabled then
			table.insert(w, g.Name)
		end
	end
	table.sort(w)
	return w
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any)
	if polecenie == "stan" then
		local n = 0
		for _ in widoki do
			n += 1
		end
		local h = hrp()
		local schowaneNazwy = {}
		for g in schowane do
			table.insert(schowaneNazwy, g.Name)
		end
		table.sort(schowaneNazwy)
		return {
			gotowy = true, aktywny = aktywny, widokow = n, czesciWidokow = czesciWidokow, obrysow = liczbaObrysow, lotow = #loty, efektow = E:ile(),
			schowane = schowaneNazwy, wlaczoneCudze = nazwyWlaczonych(), ui = if ui then ui:stan() else nil,
			kraina = krainaTeraz, cel = if celTeraz then celTeraz.Name else nil, wyslane = wyslane,
			muzyka = if muzyka.IsPlaying then muzyka.SoundId else nil, dzwiekow = graneDzwieki,
			podpowiedz = podpowiedzNr, odblokowane = odblokowane(), wzorce = wzorce ~= nil,
			poz = if h then { h.Position.X, h.Position.Y, h.Position.Z } else nil,
			kamera = kamera.CameraType.Name, czekaNaWyborKlasy = czekaNaWybor, inneDzwieki = inneDzwieki(),
			klatki = pomiar.klatek, srKlatki = if pomiar.klatek > 0 then pomiar.suma / pomiar.klatek else 0,
			maksKlatki = pomiar.maks, srPetli = if pomiar.klatek > 0 then pomiar.petlaSuma / pomiar.klatek else 0,
			maksPetli = pomiar.petlaMaks,
			okna = if okna then okna:stan() else nil, petow = (function()
				local n, modele = 0, 0
				for _, w in petyGraczy do
					n += 1
					modele += #w.modele
				end
				return { graczy = n, modeli = modele, czesci = czesciPetow }
			end)(), etykietMocy = (function()
				local n, tekst = 0, nil
				for g, t in etykietyMocy do
					if t.Visible then
						n += 1
						if g == gracz then
							tekst = t.Text
						end
					end
				end
				return { widoczne = n, moja = tekst }
			end)(), wyklucie = if wyklucie then wyklucie.t else nil, ostatnieWyklucie = ostatnieWyklucie,
			ogloszenie = ostatnieOgloszenie,
			pozPetow = (function()
				local w = petyGraczy[gracz]
				local lista = {}
				if w then
					for _, p in w.modele do
						local q = p.korzen.Position
						table.insert(lista, { p.id, q.X, q.Y, q.Z })
					end
				end
				return lista
			end)(),
		}
	elseif polecenie == "akcja" then
		-- próby: ta sama droga co przycisk (Sygnaly/Akcja, sprawdza serwer)
		evAkcja:FireServer(a, b)
		return true
	elseif polecenie == "okno" then
		if not okna then
			return false
		end
		if a then
			okna:otworz(a)
		else
			okna:zamknij()
		end
		return okna:stan()
	elseif polecenie == "bonk" then
		ostatniBonk = 0
		bonkRaz()
		return wyslane
	elseif polecenie == "trzymaj" then
		trzymane["proba"] = if a then true else nil
		return true
	elseif polecenie == "emulacja" then
		-- próby: ekran telefonu (Vector2 w punktach) albo nil; przebudowa ekranu BONK
		kontener:SetAttribute("EmulacjaEkranu", a)
		if aktywny then
			wylacz()
			wlacz()
		end
		return ui ~= nil
	elseif polecenie == "pomiar_zeruj" then
		pomiar = { klatek = 0, suma = 0, maks = 0, petlaSuma = 0, petlaMaks = 0 }
		return true
	end
	return nil
end

gotowy = true
kontener:SetAttribute("KlientGotowy", true)
if gracz:GetAttribute("BonkAktywny") == true then
	task.spawn(uzgodnijAktywny)
end
