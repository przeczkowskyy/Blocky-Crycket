--[[
	KlientPasa — kliencka połowa „lasu-pasa w grze” (Script, RunContext = Client, w kontenerze Workspace/LasPasGra).
	Klient tylko pokazuje (D-016): o przelocie, bramie i przeniesieniach decyduje SerwerPasa; tu nic nie jest liczone
	za serwer, a do serwera idą tylko zgłoszenia „gotowy”, „koniec” (id, ok) i „odmowa” (id) przez Zdalne/ZdarzeniaPasa.

	Co robi:
		• PRZELOT KAMERY (D-077) na polecenie serwera: „przygotuj” (zasłona, kamera skryptowa, sterowanie i dotyk
		  wyłączone, inne ScreenGui schowane, Strażnik budowany zawczasu przez KlientPotworow) → „start” (lot krzywą
		  Catmull-Rom z DanePasa.przelot — LogikaPasa.punktKrzywej / celKrzywej, ta sama krzywa co sprawdz_plan.py —
		  postój na Strażniku i jego klip „ryk” od rykOd) → zaciemnienie 0,5 s → kamera za plecami gracza. Nie da się
		  go pominąć (żadne wejście nic nie robi; akcje gracza są pochłaniane). „przerwij” od serwera, śmierć postaci,
		  usunięcie kontenera albo błąd w trakcie → to samo sprzątanie: kamera, sterowanie, dotyk i GUI wracają ZAWSZE
		  (lista sprzątania wykonywana od końca, każdy krok w pcall).
		• BRAMA DO BAGNA: gdy atrybut gracza PokonalStraznikaLasu = true (ustawia serwer), części grupy wrót mapy
		  (DanePasa.mapa.grupaWrot) i niewidzialna Brama/Zapora tracą kolizję i zapytania TYLKO u tego klienta, wrota
		  płynnie znikają (LocalTransparencyModifier), napis „ZAMKNIĘTE” gaśnie; po walce baner „BRAMA DO BAGNA OTWARTA”.
		  Nieuprawnionego i tak cofa serwer.
		• KOMUNIKAT: krótki napis u góry ekranu na polecenie serwera („komunikat”, tekst).
	Lokalne atrybuty kontenera (tylko u tego klienta): KlientPrzelot (true w czasie przelotu — MglaPasa rozrzedza mgłę),
	KlientPasaGotowy, KlientPasaBledy, KlientPasaOstatniPrzelot ("<id>/<ok>/<powód>").
	Uchwyt testowy: Sygnaly/SterowaniePasaKlienta (BindableFunction), Invoke("stan") → { przelot, brama, bledy, … }.
]]
if not game:GetService("RunService"):IsStudio() then
	return -- pakiet działa wyłącznie w Studio; poza Studio serwer i tak usuwa cały kontener
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local StarterPlayer = game:GetService("StarterPlayer")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local Stale = require(moduly:WaitForChild("Stale"))
local D = require(moduly:WaitForChild("DanePasa"))
local L = require(moduly:WaitForChild("LogikaPasa"))
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaPasa")
local sygnaly = kontener:WaitForChild("Sygnaly")
local gracz = Players.LocalPlayer
local P = Stale.PREFIKS
local K = Stale.KOLORY
local KOMIKS = Enum.Font.Bangers

local KROK_KAMERY = "LasPasGraPrzelot" -- nazwa BindToRenderStep
local AKCJA_BLOKADY = "LasPasGraPrzelotBlokada"
local NAZWA_GUI = "LasPasGraEkran"

------------------------------------------------------------------ błędy
local licznikBledow = 0
local function zglosBlad(gdzie: string, blad: any)
	licznikBledow += 1
	pcall(function()
		kontener:SetAttribute("KlientPasaBledy", licznikBledow)
	end)
	warn(P .. "błąd klienta pasa (" .. gdzie .. "): " .. tostring(blad))
end

------------------------------------------------------------------ własny ekran: zasłona, komunikat, baner
local function nowy(klasa: string, w: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in w do
		o[k] = v
	end
	o.Parent = rodzic
	return o
end

local ekran = nowy("ScreenGui", { Name = NAZWA_GUI, ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 40,
	ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, nil)
ekran:SetAttribute("Wygenerowane", true)
local zaslona = nowy("Frame", { Name = "Zaslona", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.new(0, 0, 0),
	BackgroundTransparency = 1, BorderSizePixel = 0, Visible = false, ZIndex = 10 }, ekran)
local napisKomunikatu = nowy("TextLabel", { Name = "Komunikat", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.17),
	Size = UDim2.fromScale(0.7, 0.07), BackgroundColor3 = K.krem, BorderSizePixel = 0, Font = KOMIKS, TextScaled = true,
	TextColor3 = K.tusz, Text = "", Visible = false, ZIndex = 5 }, ekran)
nowy("UISizeConstraint", { MaxSize = Vector2.new(720, 56), MinSize = Vector2.new(220, 30) }, napisKomunikatu)
nowy("UICorner", { CornerRadius = UDim.new(0.3, 0) }, napisKomunikatu)
nowy("UIStroke", { Color = K.tusz, Thickness = 3, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, napisKomunikatu)
nowy("UIPadding", { PaddingLeft = UDim.new(0, 10), PaddingRight = UDim.new(0, 10), PaddingTop = UDim.new(0, 4),
	PaddingBottom = UDim.new(0, 4) }, napisKomunikatu)
ekran.Parent = gracz:WaitForChild("PlayerGui")

local wersjaKomunikatu = 0
local function pokazKomunikat(tekst: string, sekundy: number)
	wersjaKomunikatu += 1
	local moja = wersjaKomunikatu
	napisKomunikatu.Text = tekst
	napisKomunikatu.Visible = true
	task.delay(sekundy, function()
		if wersjaKomunikatu == moja then
			napisKomunikatu.Visible = false
		end
	end)
end

local function pokazBaner(tytul: string, podpis: string, sekundy: number)
	local stary = ekran:FindFirstChild("Baner")
	if stary then
		stary:Destroy()
	end
	local ramka = nowy("Frame", { Name = "Baner", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.44),
		Size = UDim2.fromScale(0.64, 0.18), BackgroundColor3 = K.krem, BorderSizePixel = 0, Rotation = 1.5, ZIndex = 6 }, ekran)
	nowy("UISizeConstraint", { MaxSize = Vector2.new(760, 150) }, ramka)
	nowy("UICorner", { CornerRadius = UDim.new(0.2, 0) }, ramka)
	nowy("UIStroke", { Color = K.tusz, Thickness = 4 }, ramka)
	local t = nowy("TextLabel", { Name = "Tytul", BackgroundTransparency = 1, Position = UDim2.fromScale(0.04, 0.08),
		Size = UDim2.fromScale(0.92, 0.55), Font = KOMIKS, TextScaled = true, Text = tytul, TextColor3 = K.zielony, ZIndex = 7 }, ramka)
	nowy("UIStroke", { Color = K.tusz, Thickness = 2, ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual }, t)
	nowy("TextLabel", { Name = "Podpis", BackgroundTransparency = 1, Position = UDim2.fromScale(0.04, 0.64),
		Size = UDim2.fromScale(0.92, 0.28), Font = KOMIKS, TextScaled = true, Text = podpis, TextColor3 = K.tusz, ZIndex = 7 }, ramka)
	task.delay(sekundy, function()
		if ramka.Parent then
			ramka:Destroy()
		end
	end)
end

-- płynna zasłona: do przezroczystości `cel` (0 = czarno, 1 = nic) w `czas` s; czeka do końca
local wersjaZaslony = 0
local function zaslonaDo(cel: number, czas: number)
	wersjaZaslony += 1
	local moja = wersjaZaslony
	zaslona.Visible = true
	local od = zaslona.BackgroundTransparency
	local t0 = os.clock()
	while czas > 0 and os.clock() - t0 < czas do
		if wersjaZaslony ~= moja then
			return
		end
		zaslona.BackgroundTransparency = od + (cel - od) * ((os.clock() - t0) / czas)
		task.wait()
	end
	if wersjaZaslony == moja then
		zaslona.BackgroundTransparency = cel
		zaslona.Visible = cel < 1
	end
end

------------------------------------------------------------------ odtwarzacz walki prototypu (tylko: czy trwa walka)
local Odtwarzacz: any = nil
task.spawn(function()
	local proto = workspace:WaitForChild(Stale.NAZWA_PROTOTYPU, 10)
	local m = proto and proto:WaitForChild("Moduly", 5)
	local o = m and m:WaitForChild("OdtwarzaczWalki2", 5)
	if o then
		local ok, w = pcall(require, o)
		if ok and type(w) == "table" and type(w.czyTrwa) == "function" then
			Odtwarzacz = w
		end
	end
end)
local function walkaTrwa(): boolean
	return Odtwarzacz ~= nil and Odtwarzacz.czyTrwa() == true
end

------------------------------------------------------------------ potwory pasa (KlientPotworow w tym samym kontenerze)
-- BindableFunction bez ustawionego OnInvoke czekałaby w nieskończoność — wołamy dopiero, gdy klient potworów
-- zgłosił gotowość (lokalny atrybut KlientGotowy ustawia on PO podłączeniu haczyka)
local function sterujPotworami(polecenie: string, a: any, b: any): any
	if kontener:GetAttribute("KlientGotowy") ~= true then
		return nil
	end
	local h = sygnaly:FindFirstChild("SterowanieKlienta")
	if not h or not h:IsA("BindableFunction") then
		return nil
	end
	local ok, w = pcall(function()
		return h:Invoke(polecenie, a, b)
	end)
	return if ok then w else nil
end

local function idStraznika(): string?
	local stan = kontener:FindFirstChild("Stan")
	if not stan then
		return nil
	end
	for _, c in stan:GetChildren() do
		if c:GetAttribute("Straznik") == true then
			return c.Name
		end
	end
	return nil
end

------------------------------------------------------------------ brama do Bagna (tylko u tego klienta)
local wrota: Instance? = nil
local brama: Instance? = nil
local otwarta = false
local zapamietane: { [BasePart]: { any } } = {}

local function czesciBramy(): { BasePart }
	local lista = {}
	if wrota and wrota.Parent then
		for _, d in wrota:GetDescendants() do
			if d:IsA("BasePart") then
				table.insert(lista, d)
			end
		end
	end
	local zapora = brama and brama:FindFirstChild("Zapora")
	if zapora and zapora:IsA("BasePart") then
		table.insert(lista, zapora)
	end
	return lista
end

local function otworzCzesc(c: BasePart, animuj: boolean)
	if not zapamietane[c] then
		zapamietane[c] = { c.CanCollide, c.CanQuery }
	end
	c.CanCollide = false
	c.CanQuery = false
	if c.Name == "Zapora" then
		return
	end
	if not animuj then
		c.LocalTransparencyModifier = 1
		return
	end
	task.spawn(function()
		local t0 = os.clock()
		while otwarta and c.Parent and os.clock() - t0 < 0.6 do
			c.LocalTransparencyModifier = (os.clock() - t0) / 0.6
			task.wait()
		end
		if otwarta and c.Parent then
			c.LocalTransparencyModifier = 1
		end
	end)
end

local function ustawNapisBramy(widoczny: boolean)
	local napis = brama and brama:FindFirstChild("Napis")
	local bb = napis and napis:FindFirstChildOfClass("BillboardGui")
	if bb then
		bb.Enabled = widoczny
	end
end

local function ustawBrame(otworz: boolean, animuj: boolean)
	otwarta = otworz
	for _, c in czesciBramy() do
		if otworz then
			otworzCzesc(c, animuj)
		else
			local z = zapamietane[c]
			if z then
				c.CanQuery = z[2]
				c.CanCollide = z[1]
				zapamietane[c] = nil
			end
			c.LocalTransparencyModifier = 0
		end
	end
	ustawNapisBramy(not otworz)
end

local function szukaj(korzen: Instance, sciezka: string, czas: number): Instance?
	local o: Instance? = korzen
	for _, nazwa in string.split(sciezka, "/") do
		o = if o then o:WaitForChild(nazwa, czas) else nil
	end
	return o
end

task.spawn(function()
	brama = kontener:WaitForChild("Brama", 15)
	local m = workspace:WaitForChild(D.mapa.nazwa, 30)
	if m then
		wrota = szukaj(m, D.mapa.grupaWrot, 30)
	end
	if not wrota then
		warn(P .. "nie znalazłem wrót " .. D.mapa.nazwa .. "/" .. D.mapa.grupaWrot .. " — otwiera się tylko niewidzialna zapora pakietu")
	else
		wrota.DescendantAdded:Connect(function(d)
			if otwarta and d:IsA("BasePart") then
				otworzCzesc(d, false)
			end
		end)
	end
	if gracz:GetAttribute("PokonalStraznikaLasu") == true then
		ustawBrame(true, false)
	end
end)

gracz:GetAttributeChangedSignal("PokonalStraznikaLasu"):Connect(function()
	local teraz = gracz:GetAttribute("PokonalStraznikaLasu") == true
	if teraz == otwarta then
		return
	end
	ustawBrame(teraz, teraz)
	if teraz then
		-- baner dopiero po walce (odtwarzacz chowa inne ScreenGui) i po banerze KlientPotworow
		task.spawn(function()
			local t0 = os.clock()
			while walkaTrwa() and os.clock() - t0 < 300 do
				task.wait(0.25)
			end
			task.wait(1.5)
			if otwarta then
				pokazBaner("BRAMA DO BAGNA OTWARTA!", "Idź za arenę — dalej Bagno (wkrótce)", 5)
			end
		end)
	end
end)

------------------------------------------------------------------ przelot kamery
local przelot = nil -- { id, lot, t0, zakonczony, sprzatanie = { fn } }
local ostatniPrzelot = nil

local function sprzataj(s)
	for i = #s.sprzatanie, 1, -1 do
		local ok, blad = pcall(s.sprzatanie[i])
		if not ok then
			zglosBlad("sprzątanie przelotu", blad)
		end
	end
	table.clear(s.sprzatanie)
end

local function zakonczPrzelot(ok: boolean, powod: string?)
	local s = przelot
	if not s or s.zakonczony then
		return
	end
	s.zakonczony = true
	przelot = nil
	sprzataj(s)
	ostatniPrzelot = { id = s.id, ok = ok, powod = powod or "", czas = if s.t0 then os.clock() - s.t0 else 0,
		ryk = s.ryk == true, straznik = s.straznik or "" }
	pcall(function()
		kontener:SetAttribute("KlientPasaOstatniPrzelot", string.format("%d/%s/%s", s.id, tostring(ok), powod or ""))
	end)
	if not ok and powod then
		warn(P .. "przelot " .. s.id .. " przerwany: " .. powod)
	end
	zdarzenia:FireServer("koniec", s.id, ok)
	-- zasłona znika zawsze (także po błędzie w połowie lotu)
	task.spawn(zaslonaDo, 1, D.przelot.rozjasnienie)
end

local POMIJANE_GUI = { TouchGui = true, Freecam = true, LoadingScreen = true }

local function ukryjInneGui(s)
	local playerGui = gracz:FindFirstChildOfClass("PlayerGui")
	if not playerGui then
		return
	end
	local ukryte: { [ScreenGui]: boolean } = {}
	local polaczenia = {}
	local function sprawdz(g: Instance)
		if g:IsA("ScreenGui") and g ~= ekran and not POMIJANE_GUI[g.Name] and g.Enabled then
			ukryte[g] = true
			g.Enabled = false
		end
	end
	for _, g in playerGui:GetChildren() do
		sprawdz(g)
		if g:IsA("ScreenGui") then
			table.insert(polaczenia, g:GetPropertyChangedSignal("Enabled"):Connect(function()
				if not s.zakonczony then
					sprawdz(g)
				end
			end))
		end
	end
	table.insert(polaczenia, playerGui.ChildAdded:Connect(function(g)
		if not s.zakonczony then
			sprawdz(g)
		end
	end))
	table.insert(s.sprzatanie, function()
		for _, p in polaczenia do
			p:Disconnect()
		end
		for g in ukryte do
			if g.Parent then
				g.Enabled = true
			end
		end
	end)
end

local function zablokujSterowanie(s)
	local sterowanie = nil
	pcall(function()
		local skrypty = gracz:FindFirstChild("PlayerScripts")
		local modul = (skrypty and skrypty:FindFirstChild("PlayerModule")) or StarterPlayer:FindFirstChild("PlayerModule")
		if modul and modul:IsA("ModuleScript") then
			sterowanie = require(modul):GetControls()
		end
	end)
	if sterowanie then
		pcall(function()
			sterowanie:Disable()
		end)
	end
	-- przelotu nie da się pominąć ani przerwać ruchem: wszystkie akcje gracza są pochłaniane
	local wejscia = Enum.PlayerActions:GetEnumItems()
	table.insert(wejscia, Enum.KeyCode.Thumbstick1)
	table.insert(wejscia, Enum.KeyCode.ButtonA)
	ContextActionService:BindActionAtPriority(AKCJA_BLOKADY, function()
		return Enum.ContextActionResult.Sink
	end, false, 10000, table.unpack(wejscia))
	local dotykBylo = nil
	pcall(function()
		dotykBylo = GuiService.TouchControlsEnabled
		GuiService.TouchControlsEnabled = false
	end)
	table.insert(s.sprzatanie, function()
		ContextActionService:UnbindAction(AKCJA_BLOKADY)
		if sterowanie then
			pcall(function()
				sterowanie:Enable()
			end)
		end
		if dotykBylo ~= nil then
			pcall(function()
				GuiService.TouchControlsEnabled = dotykBylo
			end)
		end
	end)
end

local function przejmijKamere(s)
	local kamera = workspace.CurrentCamera
	local typ, podmiot, kat = kamera.CameraType, kamera.CameraSubject, kamera.FieldOfView
	kamera.CameraType = Enum.CameraType.Scriptable
	table.insert(s.sprzatanie, function()
		pcall(function()
			RunService:UnbindFromRenderStep(KROK_KAMERY)
		end)
		local k = workspace.CurrentCamera
		k.FieldOfView = kat
		local postac = gracz.Character
		local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
		local hum = postac and postac:FindFirstChildOfClass("Humanoid")
		if hrp and hrp:IsA("BasePart") then
			-- kamera za plecami gracza (moduł kamery Roblox bierze kierunek z bieżącego CFrame)
			local przod = hrp.CFrame.LookVector
			local oko = hrp.Position - przod * 14 + Vector3.new(0, 6, 0)
			k.CFrame = CFrame.lookAt(oko, hrp.Position + przod * 6 + Vector3.new(0, 1.5, 0))
		end
		k.CameraType = if typ == Enum.CameraType.Scriptable then Enum.CameraType.Custom else typ
		k.CameraSubject = hum or podmiot
	end)
end

local function wymusStraznika(s)
	local id = idStraznika()
	if not id then
		return
	end
	s.straznik = id
	sterujPotworami("wymus", id)
	table.insert(s.sprzatanie, function()
		sterujPotworami("wymus", nil)
	end)
end

local function ryknij(s)
	local id = s.straznik or idStraznika()
	local zagral = if id then sterujPotworami("klip", id, D.przelot.klip) else nil
	s.ryk = zagral == true
end

local function przygotuj(id: number): boolean
	if przelot then
		zakonczPrzelot(false, "nowy przelot")
	end
	if walkaTrwa() then
		zdarzenia:FireServer("odmowa", id) -- serwer spróbuje ponownie za kilka sekund
		return false
	end
	local s = { id = id, lot = false, t0 = os.clock(), zakonczony = false, sprzatanie = {}, straznik = nil, ryk = false }
	przelot = s
	local ok, blad = xpcall(function()
		kontener:SetAttribute("KlientPrzelot", true)
		table.insert(s.sprzatanie, function()
			kontener:SetAttribute("KlientPrzelot", nil)
		end)
		wersjaZaslony += 1
		zaslona.BackgroundTransparency = 0
		zaslona.Visible = true
		ukryjInneGui(s)
		zablokujSterowanie(s)
		przejmijKamere(s)
		wymusStraznika(s)
	end, debug.traceback)
	if not ok then
		zglosBlad("przygotowanie przelotu", blad)
		zakonczPrzelot(false, "błąd przygotowania")
		return false
	end
	-- straż: gdy serwer nie wyśle „start”, nie zostajemy za zasłoną
	task.delay(D.przelot.ladowanie + 4, function()
		if przelot == s and not s.lot then
			zakonczPrzelot(false, "brak startu od serwera")
		end
	end)
	return true
end

local function postacZyje(): boolean
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	return hum ~= nil and hum.Health > 0
end

local function lot(s)
	local punkty = D.przelot.punkty
	local T = D.przelot.czas
	local t0 = os.clock()
	s.t0 = t0
	local function ustaw(t: number)
		local px, py, pz = L.punktKrzywej(punkty, t)
		local cx, cy, cz = L.celKrzywej(punkty, t)
		local k = workspace.CurrentCamera
		if k.CameraType ~= Enum.CameraType.Scriptable then
			k.CameraType = Enum.CameraType.Scriptable
		end
		k.CFrame = CFrame.lookAt(Vector3.new(px, py, pz), Vector3.new(cx, cy, cz))
	end
	ustaw(0)
	RunService:BindToRenderStep(KROK_KAMERY, Enum.RenderPriority.Camera.Value + 1, function()
		ustaw(math.min(os.clock() - t0, T))
	end)
	table.insert(s.sprzatanie, function()
		RunService:UnbindFromRenderStep(KROK_KAMERY)
	end)
	task.spawn(zaslonaDo, 1, D.przelot.rozjasnienie)
	local ryknal = false
	while not s.zakonczony do
		local t = os.clock() - t0
		if not ryknal and t >= D.przelot.rykOd then
			ryknal = true
			task.spawn(ryknij, s)
		end
		if t >= T then
			break
		end
		if not postacZyje() then
			error("postać zginęła albo zniknęła w czasie przelotu")
		end
		task.wait()
	end
	if s.zakonczony then
		return
	end
	zaslonaDo(0, D.przelot.zaciemnienie) -- zaciemnienie 0,5 s; kamerę za plecy gracza ustawia sprzątanie (zakonczPrzelot)
end

local function start(id: number)
	local s = przelot
	if not s or s.id ~= id then
		if not przygotuj(id) then
			return
		end
		s = przelot
	end
	if not s or s.lot then
		return
	end
	s.lot = true
	task.spawn(function()
		local ok, blad = xpcall(lot, debug.traceback, s)
		if not ok then
			zglosBlad("przelot", blad)
		end
		if przelot == s then
			zakonczPrzelot(ok, if ok then nil else "błąd w locie")
		end
	end)
end

zdarzenia.OnClientEvent:Connect(function(polecenie: any, a: any)
	local ok, blad = xpcall(function()
		if polecenie == "przygotuj" and type(a) == "number" then
			przygotuj(a)
		elseif polecenie == "start" and type(a) == "number" then
			start(a)
		elseif polecenie == "przerwij" and type(a) == "number" then
			if przelot and przelot.id == a then
				zakonczPrzelot(false, "przerwane przez serwer")
			end
		elseif polecenie == "komunikat" and type(a) == "string" then
			pokazKomunikat(a, 4)
		end
	end, debug.traceback)
	if not ok then
		zglosBlad("zdarzenie " .. tostring(polecenie), blad)
		if przelot then
			zakonczPrzelot(false, "błąd zdarzenia")
		end
	end
end)

gracz.CharacterRemoving:Connect(function()
	if przelot then
		zakonczPrzelot(false, "postać usunięta")
	end
end)

kontener.AncestryChanged:Connect(function()
	if not kontener:IsDescendantOf(game) then
		if przelot then
			pcall(zakonczPrzelot, false, "kontener usunięty")
		end
		ekran:Destroy()
	end
end)

------------------------------------------------------------------ uchwyt testowy (tylko Studio)
local sterowanieKlienta = sygnaly:WaitForChild("SterowaniePasaKlienta", 5)
if sterowanieKlienta and sterowanieKlienta:IsA("BindableFunction") then
	sterowanieKlienta.OnInvoke = function(polecenie: any)
		if polecenie == "stan" then
			local k = workspace.CurrentCamera
			return {
				przelot = if przelot then { id = przelot.id, lot = przelot.lot, t = os.clock() - (przelot.t0 or os.clock()),
					straznik = przelot.straznik or "", ryk = przelot.ryk } else false,
				ostatniPrzelot = ostatniPrzelot or false,
				brama = otwarta,
				wrota = wrota ~= nil,
				kamera = k.CameraType.Name,
				zaslona = zaslona.Visible,
				bledy = licznikBledow,
				mgla = kontener:GetAttribute("WagaMglyPasa"),
			}
		end
		return nil
	end
end

kontener:SetAttribute("KlientPasaGotowy", true)
zdarzenia:FireServer("gotowy")
print(P .. "klient pasa gotowy")
