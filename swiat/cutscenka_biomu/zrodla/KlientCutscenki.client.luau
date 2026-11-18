--[[
	KlientCutscenki — kliencka połowa cutscenki biomu (D-077; Script, RunContext = Client, w kontenerze
	Workspace/CutscenkaBiomu). Klient tylko pokazuje: o tym, czy i kiedy cutscenka gra, decyduje SerwerCutscenki.

	Przebieg u gracza, który wszedł do biomu pierwszy raz:
		„pytaj” (id, biom)  → gdy trwa walka, przejście przez chmury, mini-gra albo kamerę trzyma inny skrypt: „odmowa”
		                      (serwer zapyta ponownie); inaczej zasłona, schowany HUD i podpowiedzi E, sterowanie
		                      wyłączone, kamera skryptowa, strażnik budowany zawczasu → „gotowe”;
		„start” (id)        → czarne pasy, plansza z nazwą biomu, lot po trasie z DaneCutscenki (krzywa
		                      LogikaCutscenki.krzywa), podpisy przegród przy zwolnieniach, na końcu zbliżenie na
		                      strażnika: napis z imieniem, klip ryku (haczyk klienta potworów), dźwięk z katalogu
		                      DzwiekGra (gdy jest), wstrząs kamery; zaciemnienie → „koniec” (id, czy pominięta);
		„przerwij” (id)     → to samo sprzątanie co na końcu.
	Przycisk POMIŃ (dotyk, mysz, klawisze z danych) kończy cutscenkę od razu — tylko gdy atrybut kontenera Pomijanie
	= true (domyślnie false: cutscenki nie da się pominąć). Sprzątanie jest JEDNO dla każdego
	zakończenia (koniec, pominięcie, śmierć albo zniknięcie postaci, przerwanie przez serwer, błąd, usunięcie
	kontenera): lista kroków wykonywana od końca, każdy w pcall — kamera wraca za plecy postaci (typ sprzed
	cutscenki), wracają kąt widzenia, sterowanie, dotyk, ekrany, podpowiedzi E i elementy Roblox (lista graczy, czat).
	Postaci nie ruszamy (kotwiczy ją serwer), bohater z BohaterSwiat i pet zostają przy niej.

	Lokalne atrybuty kontenera: KlientGotowy, KlientTrwa (true w czasie cutscenki), KlientBledy, KlientOstatnia.
	Uchwyt testowy: Sygnaly/SterowanieCutscenkiKlienta (BindableFunction): "stan" | "pomin" | "uklad", w, h | "ekran".
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local StarterGui = game:GetService("StarterGui")
local StarterPlayer = game:GetService("StarterPlayer")
local ProximityPromptService = game:GetService("ProximityPromptService")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneCutscenki"))
local L = require(moduly:WaitForChild("LogikaCutscenki"))
local zdarzenia = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaCutscenki")
local sygnaly = kontener:WaitForChild("Sygnaly")
local gracz = Players.LocalPlayer

local P = "[CutscenkaBiomu] "
local O = D.oprawa
local KROK_KAMERY = "CutscenkaBiomuLot"
local AKCJA_BLOKADY = "CutscenkaBiomuBlokada"
local TUSZ = Color3.fromHex("17121F")
local KREM = Color3.fromHex("FFF3D1")
local ZOLTY = Color3.fromHex("FFD23F")
local CZARNY = Color3.new(0, 0, 0)
local KOMIKS = Enum.Font.Bangers

local biomWedlugId = {}
for _, b in D.biomy do
	biomWedlugId[b.id] = b
end

------------------------------------------------------------------ błędy
local licznikBledow = 0
local function zglosBlad(gdzie, blad)
	licznikBledow += 1
	pcall(function()
		kontener:SetAttribute("KlientBledy", licznikBledow)
	end)
	warn(P .. "błąd klienta (" .. gdzie .. "): " .. tostring(blad))
end

------------------------------------------------------------------ ekran
local function nowy(klasa, w, rodzic)
	local o = Instance.new(klasa)
	for k, v in w do
		o[k] = v
	end
	o.Parent = rodzic
	return o
end

local function napis(nazwa, kolor, obrys, wyrownanie, rodzic)
	local t = nowy("TextLabel", { Name = nazwa, BackgroundTransparency = 1, Font = KOMIKS, Text = "", TextColor3 = kolor,
		TextTransparency = 1, TextXAlignment = wyrownanie, TextYAlignment = Enum.TextYAlignment.Center, TextWrapped = false,
		Visible = false, ZIndex = 4 }, rodzic)
	nowy("UIStroke", { Name = "Obrys", Color = TUSZ, Thickness = obrys, Transparency = 1 }, t)
	return t
end

local ekranTla = nowy("ScreenGui", { Name = "CutscenkaBiomuTlo", ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 60,
	Enabled = false, ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, nil)
ekranTla:SetAttribute("Wygenerowane", true)
local pasGora = nowy("Frame", { Name = "PasGora", BackgroundColor3 = CZARNY, BorderSizePixel = 0, ZIndex = 2 }, ekranTla)
local pasDol = nowy("Frame", { Name = "PasDol", BackgroundColor3 = CZARNY, BorderSizePixel = 0, ZIndex = 2 }, ekranTla)
local zaslona = nowy("Frame", { Name = "Zaslona", Size = UDim2.fromScale(1, 1), BackgroundColor3 = CZARNY,
	BackgroundTransparency = 1, BorderSizePixel = 0, ZIndex = 3 }, ekranTla)

local ekranNapisow = nowy("ScreenGui", { Name = "CutscenkaBiomuNapisy", ResetOnSpawn = false, IgnoreGuiInset = true,
	DisplayOrder = 61, Enabled = false, ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, nil)
ekranNapisow:SetAttribute("Wygenerowane", true)
pcall(function()
	ekranNapisow.ScreenInsets = Enum.ScreenInsets.DeviceSafeInsets -- wcięcie ekranu telefonu nie zasłania napisów
end)
local napisNadtytulu = napis("Nadtytul", KREM, 2, Enum.TextXAlignment.Center, ekranNapisow)
local napisNazwy = napis("NazwaBiomu", ZOLTY, 3, Enum.TextXAlignment.Center, ekranNapisow)
local napisPodpisu = napis("PodpisPrzegrody", KREM, 2, Enum.TextXAlignment.Left, ekranNapisow)
local napisStraznika = napis("NapisStraznika", ZOLTY, 3, Enum.TextXAlignment.Left, ekranNapisow)
local przycisk = nowy("TextButton", { Name = "Pomin", BackgroundColor3 = KREM, BorderSizePixel = 0, Font = KOMIKS,
	Text = O.pomijanie.napis, TextColor3 = TUSZ, AutoButtonColor = true, Visible = false, ZIndex = 6 }, ekranNapisow)
nowy("UICorner", { CornerRadius = UDim.new(0.3, 0) }, przycisk)
nowy("UIStroke", { Color = TUSZ, Thickness = 3, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, przycisk)

local playerGui = gracz:WaitForChild("PlayerGui")
ekranTla.Parent = playerGui
ekranNapisow.Parent = playerGui

local ostatniUklad = nil
local function ustaw(o, r)
	o.Position = UDim2.fromOffset(r.x, r.y)
	o.Size = UDim2.fromOffset(r.w, r.h)
	o.TextSize = r.tekst
end

local function uloz()
	local rozmiar = ekranNapisow.AbsoluteSize
	if rozmiar.X < 1 or rozmiar.Y < 1 then
		return
	end
	local u = L.uklad(rozmiar.X, rozmiar.Y, 0, 0, 0, 0, O.uklad)
	ostatniUklad = u
	ustaw(napisNadtytulu, u.nadtytul)
	ustaw(napisNazwy, u.nazwa)
	ustaw(napisPodpisu, u.podpis)
	ustaw(napisStraznika, u.straznik)
	ustaw(przycisk, u.pomin)
end
ekranNapisow:GetPropertyChangedSignal("AbsoluteSize"):Connect(uloz)

local function ustawPasy(udzial)
	local wys = ekranTla.AbsoluteSize.Y
	local pas = math.floor(wys * O.pasy + 0.5)
	pasGora.Size = UDim2.new(1, 0, 0, pas)
	pasDol.Size = UDim2.new(1, 0, 0, pas)
	pasGora.Position = UDim2.fromOffset(0, math.floor(-pas * (1 - udzial)))
	pasDol.Position = UDim2.new(0, 0, 1, -math.floor(pas * udzial))
	pasGora.Visible = udzial > 0
	pasDol.Visible = udzial > 0
end

local function pokaz(o, widocznosc)
	local obrys = o:FindFirstChild("Obrys")
	o.Visible = widocznosc > 0.01
	o.TextTransparency = 1 - widocznosc
	if obrys then
		obrys.Transparency = 1 - widocznosc
	end
end

-- płynna zasłona do przezroczystości `cel` (0 = czarno, 1 = nic) w `czas` s; czeka do końca
local wersjaZaslony = 0
local function zaslonaDo(cel, czas)
	wersjaZaslony += 1
	local moja = wersjaZaslony
	local od = zaslona.BackgroundTransparency
	local t0 = os.clock()
	while czas > 0 and os.clock() - t0 < czas do
		if wersjaZaslony ~= moja then
			return
		end
		zaslona.BackgroundTransparency = od + (cel - od) * ((os.clock() - t0) / czas)
		RunService.Heartbeat:Wait()
	end
	if wersjaZaslony == moja then
		zaslona.BackgroundTransparency = cel
	end
end

------------------------------------------------------------------ czy gracz jest zajęty
local Odtwarzacz = nil
task.spawn(function()
	local proto = workspace:WaitForChild(D.zajetosc.walka.kontener, 10)
	local m = proto and proto:WaitForChild("Moduly", 5)
	local o = m and m:WaitForChild(D.zajetosc.walka.modul, 5)
	if o then
		local ok, w = pcall(require, o)
		if ok and type(w) == "table" and type(w.czyTrwa) == "function" then
			Odtwarzacz = w
		end
	end
end)

local function postacZyje()
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	return hum ~= nil and hum.Health > 0
end

local function zajety()
	if not postacZyje() then
		return "postac"
	end
	if Odtwarzacz ~= nil and Odtwarzacz.czyTrwa() == true then
		return "walka"
	end
	local chmury = workspace:FindFirstChild(D.zajetosc.chmury.kontener)
	if chmury and chmury:GetAttribute(D.zajetosc.chmury.atrybut) == true then
		return "chmury"
	end
	if gracz:GetAttribute(D.zajetosc.trening) ~= nil then
		return "trening"
	end
	if workspace.CurrentCamera.CameraType ~= Enum.CameraType.Custom then
		return "kamera" -- kamerę trzyma inny skrypt (walka, stanowisko mini-gry, scenka)
	end
	return nil
end

------------------------------------------------------------------ strażnik i dźwięk
local function uchwytPotworow(b)
	local gra = workspace:FindFirstChild(b.kontenerGry)
	if not gra or gra:GetAttribute(D.potwory.gotowy) ~= true then
		return nil, nil
	end
	local s = gra:FindFirstChild("Sygnaly")
	local h = s and s:FindFirstChild(D.potwory.uchwyt)
	if not h or not h:IsA("BindableFunction") then
		return nil, gra
	end
	return h, gra
end

local function steruj(b, polecenie, x, y)
	local h = uchwytPotworow(b)
	if not h then
		return nil
	end
	local ok, w = pcall(function()
		return h:Invoke(polecenie, x, y)
	end)
	return if ok then w else nil
end

local function idStraznika(b)
	local gra = workspace:FindFirstChild(b.kontenerGry)
	local stan = gra and gra:FindFirstChild(D.potwory.stan)
	if not stan then
		return nil
	end
	for _, c in stan:GetChildren() do
		if c:GetAttribute(D.potwory.straznik) == true then
			return c.Name
		end
	end
	return nil
end

local function zagrajRyk()
	local dz = workspace:FindFirstChild(D.dzwiek.kontener)
	local m = dz and dz:FindFirstChild("Moduly")
	local modul = m and m:FindFirstChild(D.dzwiek.modul)
	if not modul then
		return false
	end
	local ok, kat = pcall(require, modul)
	if not ok or type(kat) ~= "table" or type(kat.arkusz) ~= "table" or type(kat.zdarzenia) ~= "table" then
		return false
	end
	local zd = kat.zdarzenia[D.dzwiek.ryk]
	local e = zd and kat.efekty and kat.efekty[zd.efekt]
	if not e or type(kat.arkusz.id) ~= "number" or kat.arkusz.id == 0 then
		return false
	end
	local d = nowy("Sound", { Name = "RykStraznika", SoundId = "rbxassetid://" .. tostring(kat.arkusz.id),
		Volume = (e.glosnosc or 1) * (kat.arkusz.glosnosc or 1), PlaybackRegionsEnabled = true,
		PlaybackRegion = NumberRange.new(e.poczatek, e.koniec) }, ekranTla)
	d:Play()
	task.delay(e.koniec - e.poczatek + 0.5, function()
		d:Destroy()
	end)
	return true
end

------------------------------------------------------------------ cutscenka
local biezaca = nil -- { id, biom, b, lot, t0, zakonczony, pomin, sprzatanie = { fn }, … }
local ostatnia = nil

local function sprzataj(s)
	for i = #s.sprzatanie, 1, -1 do
		local ok, blad = pcall(s.sprzatanie[i])
		if not ok then
			zglosBlad("sprzątanie", blad)
		end
	end
	table.clear(s.sprzatanie)
end

local function miaryKlatek(s)
	local lista = s.klatki
	if #lista == 0 then
		return { n = 0, sr = 0, maks = 0, p95 = 0 }
	end
	local suma = 0
	for _, dt in lista do
		suma += dt
	end
	local kopia = table.clone(lista)
	table.sort(kopia)
	return { n = #lista, sr = suma / #lista * 1000, maks = kopia[#kopia] * 1000, p95 = kopia[math.max(1, math.floor(#kopia * 0.95))] * 1000 }
end

local function zakoncz(ok, powod)
	local s = biezaca
	if not s or s.zakonczony then
		return
	end
	s.zakonczony = true
	biezaca = nil
	sprzataj(s)
	ostatnia = { id = s.id, biom = s.biom, ok = ok, powod = powod or "", pominieta = s.pomin == true,
		czas = if s.t0 then os.clock() - s.t0 else 0, ryk = s.ryk == true, dzwiek = s.dzwiek == true, straznik = s.straznik or "",
		plansza = s.plansza or "", napisStraznika = s.napisStraznika or "", podpisy = s.podpisy, klatki = miaryKlatek(s),
		kameraPo = workspace.CurrentCamera.CameraType.Name }
	pcall(function()
		kontener:SetAttribute("KlientOstatnia", string.format("%d/%s/%s/%s", s.id, s.biom, tostring(ok), powod or ""))
	end)
	if not ok and powod then
		warn(P .. "cutscenka " .. s.id .. " przerwana: " .. powod)
	end
	zdarzenia:FireServer("koniec", s.id, s.pomin == true)
	task.spawn(function()
		zaslonaDo(1, O.koniec.rozjasnienie)
		if biezaca == nil then
			ekranTla.Enabled = false
			ekranNapisow.Enabled = false
		end
	end)
end

local POMIJANE_GUI = { TouchGui = true, Freecam = true, LoadingScreen = true }
local ELEMENTY_ROBLOX = { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat, Enum.CoreGuiType.Backpack,
	Enum.CoreGuiType.EmotesMenu, Enum.CoreGuiType.Health }

local function ukryjInterfejs(s)
	local ukryte = {}
	local polaczenia = {}
	local function sprawdz(g)
		if g:IsA("ScreenGui") and g ~= ekranTla and g ~= ekranNapisow and not POMIJANE_GUI[g.Name] and g.Enabled then
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
	local elementy = {}
	for _, typ in ELEMENTY_ROBLOX do
		local ok, bylo = pcall(function()
			return StarterGui:GetCoreGuiEnabled(typ)
		end)
		if ok and bylo then
			elementy[typ] = true
			pcall(function()
				StarterGui:SetCoreGuiEnabled(typ, false)
			end)
		end
	end
	local podpowiedzi = ProximityPromptService.Enabled
	ProximityPromptService.Enabled = false
	table.insert(s.sprzatanie, function()
		for _, p in polaczenia do
			p:Disconnect()
		end
		for g in ukryte do
			if g.Parent then
				g.Enabled = true
			end
		end
		for typ in elementy do
			pcall(function()
				StarterGui:SetCoreGuiEnabled(typ, true)
			end)
		end
		ProximityPromptService.Enabled = podpowiedzi
	end)
end

local function zablokujSterowanie(s)
	local ster = nil
	pcall(function()
		local skrypty = gracz:FindFirstChild("PlayerScripts")
		local modul = (skrypty and skrypty:FindFirstChild("PlayerModule")) or StarterPlayer:FindFirstChild("PlayerModule")
		if modul and modul:IsA("ModuleScript") then
			ster = require(modul):GetControls()
		end
	end)
	if ster then
		pcall(function()
			ster:Disable()
		end)
	end
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
		if ster then
			pcall(function()
				ster:Enable()
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
	s.kameraPrzed = typ.Name
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
			-- kamera za plecami postaci (moduł kamery Roblox bierze kierunek z bieżącego CFrame)
			local przod = hrp.CFrame.LookVector
			local oko = hrp.Position - przod * O.koniec.zaPlecami + Vector3.yAxis * O.koniec.nad
			k.CFrame = CFrame.lookAt(oko, hrp.Position + przod * 6 + Vector3.yAxis * 1.5)
		end
		k.CameraType = if typ == Enum.CameraType.Scriptable then Enum.CameraType.Custom else typ
		k.CameraSubject = hum or podmiot
	end)
end

local function wymusStraznika(s)
	local id = idStraznika(s.b)
	if not id then
		return
	end
	s.straznik = id
	steruj(s.b, "wymus", id)
	table.insert(s.sprzatanie, function()
		steruj(s.b, "wymus", nil)
	end)
end

local function rozrzedzMgle(s)
	-- mgła biomu (MglaPasa pakietu gry) rzednie na czas przelotu — ten sam lokalny atrybut co przy starym przelocie
	local gra = workspace:FindFirstChild(s.b.kontenerGry)
	if gra and gra:GetAttribute(D.mgla) ~= true then
		gra:SetAttribute(D.mgla, true)
		table.insert(s.sprzatanie, function()
			if gra.Parent then
				gra:SetAttribute(D.mgla, nil)
			end
		end)
	end
end

local function ryknij(s)
	local id = s.straznik or idStraznika(s.b)
	s.ryk = id ~= nil and steruj(s.b, "klip", id, s.b.straznik.klip) == true
	s.dzwiek = zagrajRyk()
end

local function pomijanieWlaczone()
	-- domyślnie wyłączone (ustalenie właściciela: przelotu nie da się pominąć); włącza je atrybut kontenera = true
	return O.pomijanie.wlaczone == true and kontener:GetAttribute(O.pomijanie.atrybut) == true
end

local function pomin()
	local s = biezaca
	if not s or not s.lot or s.zakonczony or s.pomin or not pomijanieWlaczone() then
		return false
	end
	if os.clock() - s.t0 < O.pomijanie.od then
		return false
	end
	s.pomin = true
	return true
end
przycisk.Activated:Connect(pomin)

local KLAWISZE = {}
for _, nazwa in O.pomijanie.klawisze do
	local ok, kod = pcall(function()
		return Enum.KeyCode[nazwa]
	end)
	if ok and kod then
		KLAWISZE[kod] = true
	end
end
UserInputService.InputBegan:Connect(function(wejscie)
	if biezaca and KLAWISZE[wejscie.KeyCode] and UserInputService:GetFocusedTextBox() == nil then
		pomin()
	end
end)

local function przygotuj(id, biom)
	local b = biomWedlugId[biom]
	if biezaca then
		zakoncz(false, "nowa cutscenka")
	end
	local powod = if b then zajety() else "biom"
	if powod then
		zdarzenia:FireServer("odmowa", id, powod)
		return false
	end
	local s = { id = id, biom = biom, b = b, lot = false, t0 = os.clock(), zakonczony = false, pomin = false, sprzatanie = {},
		klatki = {}, podpisy = 0, rykOd = b.trasa.lot + O.straznik.rykPo }
	biezaca = s
	local ok, blad = xpcall(function()
		kontener:SetAttribute("KlientTrwa", true)
		table.insert(s.sprzatanie, function()
			kontener:SetAttribute("KlientTrwa", nil)
			pokaz(napisNadtytulu, 0)
			pokaz(napisNazwy, 0)
			pokaz(napisPodpisu, 0)
			pokaz(napisStraznika, 0)
			przycisk.Visible = false
			ustawPasy(0)
		end)
		ustawPasy(0)
		ekranTla.Enabled = true
		ekranNapisow.Enabled = true
		uloz()
		zaslonaDo(0, O.zaslona)
		if s.zakonczony then
			return
		end
		ukryjInterfejs(s)
		zablokujSterowanie(s)
		przejmijKamere(s)
		rozrzedzMgle(s)
		wymusStraznika(s)
		local px, py, pz = L.krzywa(b.trasa.poz, b.trasa.n, b.trasa.krok, 0)
		local cx, cy, cz = L.krzywa(b.trasa.patrz, b.trasa.n, b.trasa.krok, 0)
		workspace.CurrentCamera.CFrame = CFrame.lookAt(Vector3.new(px, py, pz), Vector3.new(cx, cy, cz))
	end, debug.traceback)
	if not ok then
		zglosBlad("przygotowanie", blad)
		zakoncz(false, "błąd przygotowania")
		return false
	end
	if s.zakonczony then
		return false
	end
	zdarzenia:FireServer("gotowe", id)
	task.delay(D.serwer.ladowanie + 5, function()
		if biezaca == s and not s.lot then
			zakoncz(false, "brak startu od serwera")
		end
	end)
	return true
end

local function klatka(s, dt)
	local tr = s.b.trasa
	local t = os.clock() - s.t0
	if #s.klatki < 4000 then
		table.insert(s.klatki, dt)
	end
	local tt = math.min(t, tr.czas)
	local px, py, pz = L.krzywa(tr.poz, tr.n, tr.krok, tt)
	local cx, cy, cz = L.krzywa(tr.patrz, tr.n, tr.krok, tt)
	local cf = CFrame.lookAt(Vector3.new(px, py, pz), Vector3.new(cx, cy, cz))
	local sila = L.wstrzas(t, s.rykOd, O.straznik.wstrzasCzas, O.straznik.wstrzas)
	if sila > 0 then
		local faza = (t - s.rykOd) * O.straznik.wstrzasHz * 2 * math.pi
		cf = cf * CFrame.new(math.sin(faza) * sila, math.sin(faza * 1.31 + 1.7) * sila, 0)
	end
	local k = workspace.CurrentCamera
	if k.CameraType ~= Enum.CameraType.Scriptable then
		k.CameraType = Enum.CameraType.Scriptable
	end
	k.CFrame = cf
	local postoj = math.max(0.1, tr.czas - tr.lot - O.koniec.zaciemnienie)
	local n = math.clamp((t - tr.lot) / postoj, 0, 1)
	k.FieldOfView = O.kat - O.straznik.najazd * n * n * (3 - 2 * n)
	-- oprawa
	ustawPasy(math.clamp(t / O.pasyWjazd, 0, 1))
	local wp = L.widocznosc(t, O.plansza.od, O.plansza.pelnaOd, O.plansza.pelnaDo, O.plansza.doKiedy)
	pokaz(napisNadtytulu, wp)
	pokaz(napisNazwy, wp)
	local najlepszy, tekst = 0, ""
	if O.podpisy.wlaczone then
		for _, p in s.b.przystanki do
			local od = p.t - O.podpisy.przed
			local w = L.widocznosc(t, od, od + 0.25, od + O.podpisy.trwa - 0.3, od + O.podpisy.trwa)
			if w > najlepszy then
				najlepszy, tekst = w, p.nazwa
			end
		end
	end
	if najlepszy > 0 and napisPodpisu.Text ~= tekst then
		napisPodpisu.Text = tekst
		s.podpisy += 1
	end
	pokaz(napisPodpisu, najlepszy)
	local od = tr.lot - O.straznik.napisPrzed
	local ws = L.widocznosc(t, od, od + 0.3, tr.czas - O.straznik.napisDoKonca, tr.czas - O.straznik.napisDoKonca + 0.25)
	if ws > 0 and s.napisStraznika == nil then
		s.napisStraznika = napisStraznika.Text
	end
	pokaz(napisStraznika, ws)
	przycisk.Visible = pomijanieWlaczone() and t >= O.pomijanie.od and not s.pomin
end

local function lot(s)
	local tr = s.b.trasa
	s.t0 = os.clock()
	napisNadtytulu.Text = O.plansza.nadtytul
	napisNazwy.Text = s.b.napis
	napisStraznika.Text = s.b.straznik.napis
	przycisk.Text = if UserInputService.KeyboardEnabled and not UserInputService.TouchEnabled
		then O.pomijanie.napis .. " · " .. O.pomijanie.podpowiedz else O.pomijanie.napis
	s.plansza = napisNazwy.Text
	RunService:BindToRenderStep(KROK_KAMERY, Enum.RenderPriority.Camera.Value + 1, function(dt)
		if not s.zakonczony then
			klatka(s, dt)
		end
	end)
	table.insert(s.sprzatanie, function()
		RunService:UnbindFromRenderStep(KROK_KAMERY)
	end)
	task.spawn(zaslonaDo, 1, O.zaslona)
	local ryknal = false
	while not s.zakonczony and not s.pomin do
		local t = os.clock() - s.t0
		if not ryknal and t >= s.rykOd then
			ryknal = true
			task.spawn(ryknij, s)
		end
		if t >= tr.czas - O.koniec.zaciemnienie then
			break
		end
		if not postacZyje() then
			s.przerwana = "postać zginęła" -- zwykłe zdarzenie gry, nie błąd: sprzątamy bez zgłoszenia
			return
		end
		RunService.Heartbeat:Wait()
	end
	if s.zakonczony then
		return
	end
	zaslonaDo(0, if s.pomin then O.koniec.zaciemnienie / 2 else O.koniec.zaciemnienie)
end

local function start(id)
	local s = biezaca
	if not s or s.id ~= id or s.lot then
		return
	end
	s.lot = true
	task.spawn(function()
		local ok, blad = xpcall(lot, debug.traceback, s)
		if not ok then
			zglosBlad("lot", blad)
		end
		if biezaca == s then
			if s.przerwana then
				zakoncz(false, s.przerwana)
			else
				zakoncz(ok, if ok then nil else "błąd w locie")
			end
		end
	end)
end

zdarzenia.OnClientEvent:Connect(function(polecenie, a, b)
	local ok, blad = xpcall(function()
		if polecenie == "pytaj" and type(a) == "number" and type(b) == "string" then
			przygotuj(a, b)
		elseif polecenie == "start" and type(a) == "number" then
			start(a)
		elseif polecenie == "przerwij" and type(a) == "number" then
			if biezaca and biezaca.id == a then
				zakoncz(false, "przerwane przez serwer")
			end
		end
	end, debug.traceback)
	if not ok then
		zglosBlad("zdarzenie " .. tostring(polecenie), blad)
		if biezaca then
			zakoncz(false, "błąd zdarzenia")
		end
	end
end)

gracz.CharacterRemoving:Connect(function()
	if biezaca then
		zakoncz(false, "postać usunięta")
	end
end)

kontener.AncestryChanged:Connect(function()
	if not kontener:IsDescendantOf(game) then
		if biezaca then
			pcall(zakoncz, false, "kontener usunięty")
		end
		ekranTla:Destroy()
		ekranNapisow:Destroy()
	end
end)

------------------------------------------------------------------ uchwyt testowy (tylko Studio)
local function prostokat(o)
	return { x = o.AbsolutePosition.X, y = o.AbsolutePosition.Y, w = o.AbsoluteSize.X, h = o.AbsoluteSize.Y,
		tekst = o.TextSize, widoczny = o.Visible, napis = o.Text, przezroczystosc = o.TextTransparency }
end

local uchwyt = sygnaly:WaitForChild("SterowanieCutscenkiKlienta", 5)
if uchwyt and uchwyt:IsA("BindableFunction") then
	uchwyt.OnInvoke = function(polecenie, a, b)
		if polecenie == "stan" then
			local s = biezaca
			local k = workspace.CurrentCamera
			return {
				trwa = if s then { id = s.id, biom = s.biom, lot = s.lot, t = os.clock() - s.t0, pomin = s.pomin,
					straznik = s.straznik or "", ryk = s.ryk == true, dzwiek = s.dzwiek == true } else false,
				ostatnia = ostatnia or false,
				kamera = k.CameraType.Name,
				kat = k.FieldOfView,
				pasy = pasGora.Visible and ekranTla.Enabled,
				zaslona = zaslona.BackgroundTransparency,
				podpowiedzi = ProximityPromptService.Enabled,
				zajety = zajety() or "",
				bledy = licznikBledow,
			}
		elseif polecenie == "pomin" then
			return pomin()
		elseif polecenie == "uklad" then
			return L.uklad(a, b, 0, 0, 0, 0, O.uklad)
		elseif polecenie == "ekran" then
			return { szer = ekranNapisow.AbsoluteSize.X, wys = ekranNapisow.AbsoluteSize.Y, uklad = ostatniUklad or false,
				nadtytul = prostokat(napisNadtytulu), nazwa = prostokat(napisNazwy), podpis = prostokat(napisPodpisu),
				straznik = prostokat(napisStraznika), pomin = prostokat(przycisk),
				pasGora = { y = pasGora.AbsolutePosition.Y, h = pasGora.AbsoluteSize.Y, widoczny = pasGora.Visible },
				pasDol = { y = pasDol.AbsolutePosition.Y, h = pasDol.AbsoluteSize.Y, widoczny = pasDol.Visible } }
		end
		return nil
	end
end

kontener:SetAttribute("KlientGotowy", true)
zdarzenia:FireServer("gotowy")
print(P .. "klient gotowy")
