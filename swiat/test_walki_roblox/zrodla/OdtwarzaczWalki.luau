--[[
	OdtwarzaczWalki — kliencka cutscenka auto-walki 3D. Niczego nie liczy: prosi serwer o walkę i ODTWARZA
	dziennik zdarzeń na LOKALNYCH klonach aktorów (każdy gracz widzi własną walkę, inni jej nie widzą).

	Co robi w trakcie:
		• animacje domyślne R15 (idle, toolnone, toolslash, toollunge, cheer / laugh) + ruch proceduralny
		  (doskok, zamach, odrzut, garda z tarczą, unik, upadek) liczony co klatkę jako funkcja czasu sceny;
		• kamera skryptowa: plan ogólny → zza ramienia → zbliżenie z drżeniem → zwolnienie i zawężenie kąta
		  widzenia przy krytyku → objazd przy zwycięstwie;
		• interfejs (InterfejsWalki): paski życia, komiksowe napisy, „POMIŃ”, panel wyniku z łupem;
		• na czas walki: blokada sterowania, ukrycie pozostałych ScreenGui i CoreGui, wyłączona podpowiedź;
		• arena stoi w świecie wspólnym dla wszystkich, więc lokalnie chowamy wszystko obce, co trafiłoby w kadr:
		  postacie WSZYSTKICH graczy (także własną — stoi przy tablicy, obok kamery planu ogólnego), obiekty
		  z tagiem Ustawienia.TAG_UKRYJ i każdą obcą część w pudle sceny (Ustawienia.OBSZAR_*) — patrz schowajObcych.
	Po zakończeniu albo przerwaniu (śmierć postaci, usunięcie postaci, zniknięcie kontenera) wszystko wraca
	do stanu sprzed walki, a to, co lokalne, jest niszczone — patrz Sesja:zakoncz.

	API:  uruchom(kontener, opcje?) → boolean   |   pomin()   |   zamknij()   |   czyTrwa() → boolean   |   wolnaZa() → s
	opcje (tylko do testów): tempo (np. 0.25 — zwolnione odtwarzanie), etykietaCzasu (true — licznik czasu sceny),
	pominPo (s — samoczynne „POMIŃ”), zamknijPo (s — samoczynne zamknięcie panelu wyniku).

	Wynik ostatniego odtworzenia trafia do atrybutów kontenera (po stronie klienta): OstatniStan,
	OstatniCzasTrwania, OstatniaSredniaKlatki, OstatniP95Klatki, OstatniaMaksKlatki, OstatniaLiczbaKlatek,
	OstatniaLiczbaInstancji, OstatnioPominieto, OstatniWynik, OstatnieZiarno, OstatniaLiczbaWymian,
	OstatniCzasPrzygotowania, OstatniCzasSerwera, LicznikOdtworzen, OstatniKosztSkryptuSredni / P95 / Maks
	(czas procesora zajęty przez sam ten kod w jednej klatce, w ms — bez renderowania).
]]
if not game:GetService("RunService"):IsStudio() then
	local function nic()
		return false
	end
	return { uruchom = nic, pomin = nic, zamknij = nic, czyTrwa = nic, wolnaZa = function()
		return 0
	end }
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")
local StarterGui = game:GetService("StarterGui")
local StarterPlayer = game:GetService("StarterPlayer")
local GuiService = game:GetService("GuiService")
local ContextActionService = game:GetService("ContextActionService")
local TweenService = game:GetService("TweenService")

local moduly = script.Parent
local Ustawienia = require(moduly:WaitForChild("Ustawienia"))
local InterfejsWalki = require(moduly:WaitForChild("InterfejsWalki"))
local SilnikWalki = require(moduly:WaitForChild("SilnikWalki"))

local Odtwarzacz = {}
local sesja = nil -- jedyna aktywna sesja (albo nil)
-- czas serwera (workspace:GetServerTimeNow()), od którego serwer przyjmie następną walkę — przysyła go z każdą walką.
-- To tylko podpowiedź dla interfejsu (odliczanie na „JESZCZE RAZ” i na podpowiedzi); limit i tak pilnuje serwer.
local wolnaOd = 0

local function wolnaZa(): number
	return math.max(0, wolnaOd - workspace:GetServerTimeNow())
end

local KROK = "TestWalkiCutscenka"
local AKCJA_BLOKADY = "TestWalkiBlokadaSterowania"
local AKCJA_POMIN = "TestWalkiPomin"
local K = Ustawienia.KOLORY
local rad = math.rad
local los = Random.new()

------------------------------------------------------------------ choreografia (stałe)
local DOSKOK = 5.4 -- o tyle studów atakujący doskakuje do przeciwnika
-- zwolnienie przy krytyku: przez ZW_PRZED s przed trafieniem i ZW_PO s po nim scena biegnie z prędkością ZW_TEMPO
local ZW_PRZED, ZW_PO, ZW_TEMPO = 0.26, 0.46, 0.2
local ZALEGLOSC = (1 - ZW_TEMPO) * (ZW_PRZED + ZW_PO) -- tyle sekund scena „gubi” na zwolnieniu
local WSTRZAS = { cios = 0.24, blok = 0.15, krytyk = 0.6, unik = 0 }

------------------------------------------------------------------ krzywe
local function gladko(x: number): number -- 0 → 1, łagodny start i koniec
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end
local function wyjscie(x: number): number -- 0 → 1, szybki start, łagodny koniec
	x = math.clamp(x, 0, 1)
	return 1 - (1 - x) * (1 - x)
end
local function luk(u: number, a: number, b: number): number -- 0 → 1 → 0 po paraboli na odcinku [a, b]
	if u <= a or u >= b then
		return 0
	end
	local x = (u - a) / (b - a)
	return 4 * x * (1 - x)
end
-- 0 → 1 na [a, b], trzyma 1 do c, wraca do 0 na [c, d]
local function okno(u: number, a: number, b: number, c: number, d: number): number
	if u <= a or u >= d then
		return 0
	elseif u < b then
		return gladko((u - a) / (b - a))
	elseif u <= c then
		return 1
	end
	return 1 - gladko((u - c) / (d - c))
end
-- odrzut po trafieniu: 0 w chwili 0, szczyt w „szczyt”, powrót do 0 w „koniec”
local function odrzut(u: number, szczyt: number, koniec: number): number
	if u <= 0 or u >= koniec then
		return 0
	elseif u < szczyt then
		return wyjscie(u / szczyt)
	end
	return 1 - gladko((u - szczyt) / (koniec - szczyt))
end
-- czas rzeczywisty względem trafienia → czas sceny i lokalne tempo (zwolnienie tylko przy krytyku)
local function zakrzyw(krytyk: boolean, x: number): (number, number)
	if not krytyk then
		return x, 1
	elseif x < -ZW_PRZED then
		return x + ZW_PRZED * (1 - ZW_TEMPO), 1
	elseif x <= ZW_PO then
		return x * ZW_TEMPO, ZW_TEMPO
	end
	return x - ZW_PO * (1 - ZW_TEMPO), 1
end

------------------------------------------------------------------ sesja
local Sesja = {}
Sesja.__index = Sesja

function Sesja:posprzataj(funkcja: () -> ())
	table.insert(self.sprzatanie, funkcja)
end

function Sesja:polacz(sygnal: RBXScriptSignal, funkcja): RBXScriptConnection
	local p = sygnal:Connect(funkcja)
	self:posprzataj(function()
		p:Disconnect()
	end)
	return p
end

function Sesja:atrybut(nazwa: string, wartosc: any)
	pcall(function()
		self.kontener:SetAttribute(nazwa, wartosc)
	end)
end

function Sesja:nowa(klasa: string, wlasciwosci: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in wlasciwosci do
		o[k] = v
	end
	o.Parent = rodzic
	self.utworzono += 1
	return o
end

------------------------------------------------------------------ przejęcie i oddanie sterowania, GUI, kamery
function Sesja:zablokujSterowanie()
	-- 1) moduł sterowania Roblox (w nowszych wersjach leży w StarterPlayer, w starszych w PlayerScripts)
	local sterowanie = nil
	pcall(function()
		local skrypty = self.gracz:FindFirstChild("PlayerScripts")
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
	-- 2) pas bezpieczeństwa: akcje ruchu i skoku „toną”, zanim dotrą do sterowania
	local wejscia = Enum.PlayerActions:GetEnumItems()
	table.insert(wejscia, Enum.KeyCode.Thumbstick1)
	table.insert(wejscia, Enum.KeyCode.ButtonA)
	ContextActionService:BindActionAtPriority(AKCJA_BLOKADY, function()
		return Enum.ContextActionResult.Sink
	end, false, 10000, table.unpack(wejscia))
	-- 3) przyciski dotykowe (telefon)
	local dotykBylo = nil
	pcall(function()
		dotykBylo = GuiService.TouchControlsEnabled
		GuiService.TouchControlsEnabled = false
	end)
	self:posprzataj(function()
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
	-- skrót klawiszowy „pomiń”
	ContextActionService:BindActionAtPriority(AKCJA_POMIN, function(_, stan)
		if stan == Enum.UserInputState.Begin then
			self:pomin()
		end
		return Enum.ContextActionResult.Sink
	end, false, 10001, Enum.KeyCode.Space, Enum.KeyCode.ButtonB)
	self:posprzataj(function()
		ContextActionService:UnbindAction(AKCJA_POMIN)
	end)
end

function Sesja:ukryjInneGui()
	local playerGui = self.gracz:FindFirstChildOfClass("PlayerGui")
	local ukryte: { [ScreenGui]: boolean } = {}
	local POMIJANE = { TouchGui = true, Freecam = true, LoadingScreen = true }
	local function sprawdz(g: Instance)
		if g:IsA("ScreenGui") and g ~= self.ui.gui and not POMIJANE[g.Name] and g.Enabled then
			ukryte[g] = true
			g.Enabled = false
		end
	end
	local function dopilnuj(g: Instance)
		if g:IsA("ScreenGui") and g ~= self.ui.gui then
			sprawdz(g)
			-- gdyby gra włączyła ten ekran w trakcie walki (np. HUD po ekranie ładowania): schowaj i zapamiętaj
			self:polacz(g:GetPropertyChangedSignal("Enabled"), function()
				if not self.zakonczona then
					sprawdz(g)
				end
			end)
		end
	end
	if playerGui then
		for _, g in playerGui:GetChildren() do
			dopilnuj(g)
		end
		self:polacz(playerGui.ChildAdded, dopilnuj)
	end
	-- elementy Roblox: lista graczy, czat, plecak, emotki, pasek zdrowia
	local rdzen = {}
	for _, typ in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat, Enum.CoreGuiType.Backpack, Enum.CoreGuiType.EmotesMenu, Enum.CoreGuiType.Health } do
		local ok, wlaczone = pcall(function()
			return StarterGui:GetCoreGuiEnabled(typ)
		end)
		if ok and wlaczone then
			table.insert(rdzen, typ)
			pcall(function()
				StarterGui:SetCoreGuiEnabled(typ, false)
			end)
		end
	end
	self:posprzataj(function()
		for g in ukryte do
			if g.Parent then
				g.Enabled = true
			end
		end
		for _, typ in rdzen do
			pcall(function()
				StarterGui:SetCoreGuiEnabled(typ, true)
			end)
		end
	end)
end

function Sesja:wylaczPodpowiedz()
	local podpowiedz = self.kontener:FindFirstChild("PodpowiedzWalki", true)
	if podpowiedz and podpowiedz:IsA("ProximityPrompt") and podpowiedz.Enabled then
		podpowiedz.Enabled = false -- zmiana lokalna, widzi ją tylko ten klient
		self:posprzataj(function()
			if podpowiedz.Parent then
				podpowiedz.Enabled = true
			end
		end)
	end
end

function Sesja:pilnujPrzerwania()
	local function przerwij()
		self:zakoncz("przerwano")
	end
	local postac = self.gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if hum then
		self:polacz(hum.Died, przerwij)
	end
	self:polacz(self.gracz.CharacterRemoving, przerwij)
	self:polacz(self.kontener.AncestryChanged, function()
		if not self.kontener:IsDescendantOf(workspace) then
			przerwij()
		end
	end)
	self:polacz(self.ui.gui.AncestryChanged, function()
		if not self.ui.gui:IsDescendantOf(game) then
			przerwij()
		end
	end)
end

function Sesja:przejmijKamere()
	local kamera = workspace.CurrentCamera
	self.kamera = kamera
	local typ, kat, podmiot = kamera.CameraType, kamera.FieldOfView, kamera.CameraSubject
	kamera.CameraType = Enum.CameraType.Scriptable
	self:posprzataj(function()
		kamera.FieldOfView = kat
		kamera.CameraType = typ
		local postac = self.gracz.Character
		local hum = postac and postac:FindFirstChildOfClass("Humanoid")
		kamera.CameraSubject = hum or podmiot
	end)
end

------------------------------------------------------------------ serwer
function Sesja:poprosSerwer()
	local zdalna = self.kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke") :: RemoteFunction
	for _ = 1, 3 do
		local t = os.clock()
		local odpowiedz = zdalna:InvokeServer() -- sama prośba, bez danych
		self.czasSerwera = (os.clock() - t) * 1000
		if self.zakonczona then
			error("przerwano")
		end
		local powod = if type(odpowiedz) == "table" then odpowiedz.powod else nil
		local ponowZa = if type(odpowiedz) == "table" then tonumber(odpowiedz.ponowZa) else nil
		if type(odpowiedz) == "table" and odpowiedz.ok and odpowiedz.walka then
			local dobre, opis = SilnikWalki.sprawdz(odpowiedz.walka)
			if not dobre then
				error("serwer przysłał niepoprawny dziennik: " .. tostring(opis))
			end
			wolnaOd = tonumber(odpowiedz.nastepnaOd) or 0
			self:atrybut("NastepnaWalkaOd", wolnaOd)
			return odpowiedz.walka
		elseif (powod == "za_szybko" or powod == "walka_trwa") and ponowZa and ponowZa <= 3 then
			-- krótka różnica zegarów albo podwójne kliknięcie: odczekaj pod zasłoną i spróbuj jeszcze raz
			task.wait(math.clamp(ponowZa, 0.1, 3) + 0.05)
			if self.zakonczona then
				error("przerwano")
			end
		elseif powod == "za_daleko" or powod == "walka_trwa" or powod == "brak_postaci" or powod == "za_szybko" then
			-- zwykła odmowa serwera (nie błąd kodu): sesja kończy się po cichu, powód trafia do atrybutu OstatniaOdmowa
			if powod == "walka_trwa" and ponowZa then
				wolnaOd = workspace:GetServerTimeNow() + ponowZa
			end
			self.odmowa = powod
			self:atrybut("OstatniaOdmowa", powod)
			error("serwer odmówił: " .. powod)
		else
			error("serwer odmówił: " .. tostring(powod or odpowiedz))
		end
	end
	self.odmowa = "za_szybko"
	self:atrybut("OstatniaOdmowa", "za_szybko")
	error("serwer wciąż odmawia (limit próśb)")
end

------------------------------------------------------------------ scena: lokalne klony aktorów
local function idAnimacji(gracz: Player, nazwa: string): string
	-- identyfikatory domyślnych animacji bierzemy ze skryptu Animate postaci gracza; bezczynność zawsze domyślna
	if nazwa ~= "idle" then
		local postac = gracz.Character
		local animate = postac and postac:FindFirstChild("Animate")
		local wartosc = animate and animate:FindFirstChild(nazwa)
		local animacja = wartosc and wartosc:FindFirstChildWhichIsA("Animation")
		if animacja and animacja.AnimationId ~= "" then
			return animacja.AnimationId
		end
	end
	return Ustawienia.ANIMACJE[nazwa]
end

function Sesja:tor(aktor, nazwa: string, priorytet: Enum.AnimationPriority, petla: boolean): AnimationTrack
	local animacja = self:nowa("Animation", { Name = nazwa, AnimationId = idAnimacji(self.gracz, nazwa) }, aktor.model)
	local tor = aktor.animator:LoadAnimation(animacja)
	tor.Priority = priorytet
	tor.Looped = petla
	return tor
end

function Sesja:nowyAktor(strona: string, szablon: Model)
	local model = szablon:Clone()
	model.Name = szablon.Name .. "_lokalny"
	local hrp = model:FindFirstChild("HumanoidRootPart") :: BasePart
	local hum = model:FindFirstChildOfClass("Humanoid")
	if not hrp or not hum then
		error("szablon „" .. szablon.Name .. "” jest niepełny (jeszcze się nie doczytał?)")
	end
	hrp.Anchored = true
	local dom = Ustawienia.miejsce(strona)
	model:PivotTo(dom)
	model.Parent = self.scena
	self.utworzono += #model:GetDescendants() + 1
	local animator = hum:FindFirstChildOfClass("Animator")
	if not animator then
		animator = self:nowa("Animator", {}, hum)
	end
	local aktor = {
		strona = strona, model = model, hrp = hrp, dom = dom, animator = animator, tory = {}, stawy = {},
		obrys = model:FindFirstChildOfClass("Highlight"),
		maTarcze = model:FindFirstChild("Tarcza", true) ~= nil,
		znakBoku = if strona == "gracz" then 1 else -1, -- lokalne +X aktora to strona kamery (gracz) albo przeciwna (wróg)
		poza = {}, blyskOstatni = -1,
	}
	-- Stawy do ruchu proceduralnego. Nowe rigi R15 mają AnimationConstraint (C0 jest tam tylko do odczytu —
	-- obracamy więc zaczep po stronie części nadrzędnej), starsze mają Motor6D (obracamy C0). Obrót składa się
	-- z animacją: część podrzędna = zaczep × obrót × animacja.
	for _, nazwa in { "RightShoulder", "LeftShoulder", "LeftElbow", "Waist" } do
		local staw = model:FindFirstChild(nazwa, true)
		if staw and staw:IsA("Motor6D") then
			aktor.stawy[nazwa] = { obiekt = staw, pole = "C0", c0 = staw.C0, ostatni = nil }
		elseif staw and staw:IsA("AnimationConstraint") and staw.Attachment0 then
			local zaczep = staw.Attachment0
			aktor.stawy[nazwa] = { obiekt = zaczep, pole = "CFrame", c0 = zaczep.CFrame, ostatni = nil }
		end
	end
	aktor.tory.idle = self:tor(aktor, "idle", Enum.AnimationPriority.Idle, true)
	aktor.tory.bron = self:tor(aktor, "toolnone", Enum.AnimationPriority.Movement, true)
	aktor.tory.wypad = self:tor(aktor, "toollunge", Enum.AnimationPriority.Action, false)
	aktor.tory.ciecie = self:tor(aktor, "toolslash", Enum.AnimationPriority.Action2, false)
	aktor.tory.wiwat = self:tor(aktor, if strona == "gracz" then "cheer" else "laugh", Enum.AnimationPriority.Action3, true)
	return aktor
end

function Sesja:przygotujScene()
	local szablony = self.kontener:WaitForChild("Aktorzy", 5)
	if not szablony then
		error("brak folderu Aktorzy w kontenerze")
	end
	self.scena = self:nowa("Folder", { Name = "ScenaLokalna" }, self.kontener)
	self:posprzataj(function()
		self.scena:Destroy()
	end)
	self.aktorzy = {}
	for _, strona in { "gracz", "wrog" } do
		local szablon = szablony:WaitForChild(Ustawienia.AKTORZY[strona], 5)
		if not szablon then
			error("brak szablonu aktora: " .. Ustawienia.AKTORZY[strona])
		end
		self.aktorzy[strona] = self:nowyAktor(strona, szablon :: Model)
	end
	-- szablony chowamy tylko u tego klienta (LocalTransparencyModifier nie jest replikowany)
	local schowane, obrysy = {}, {}
	for _, d in szablony:GetDescendants() do
		if d:IsA("BasePart") then
			d.LocalTransparencyModifier = 1
			table.insert(schowane, d)
		elseif d:IsA("Highlight") and d.Enabled then
			d.Enabled = false
			table.insert(obrysy, d)
		end
	end
	self:posprzataj(function()
		for _, d in schowane do
			d.LocalTransparencyModifier = 0
		end
		for _, d in obrysy do
			d.Enabled = true
		end
	end)
	self:schowajObcych()
	-- dźwięki (wbudowane w klienta)
	self.dzwieki = {}
	if Ustawienia.DZWIEKI_WLACZONE then
		for nazwa, id in Ustawienia.DZWIEKI do
			self.dzwieki[nazwa] = self:nowa("Sound", { Name = nazwa, SoundId = id, Volume = 0.45 }, self.ui.gui)
		end
	end
	self.efekty = { iskry = {}, wolne = {}, lup = {} }
	-- poczekaj (krótko), aż animacje się wczytają — inaczej pierwsza wymiana odbyłaby się „na sztywno”
	local t0 = os.clock()
	while os.clock() - t0 < 2.5 do
		local gotowe = true
		for _, aktor in self.aktorzy do
			for _, tor in aktor.tory do
				if tor.Length <= 0 then
					gotowe = false
				end
			end
		end
		if gotowe then
			break
		end
		task.wait(0.05)
		if self.zakonczona then
			error("przerwano")
		end
	end
end

------------------------------------------------------------------ obcy w kadrze
--[[
	Arena stoi w świecie wspólnym dla wszystkich graczy, a walka odtwarza się tylko u jednego. Bez tego inni gracze,
	ich pety i pociski wchodziliby w kadr i przenikali przez lokalne klony. Na czas cutscenki chowamy więc LOKALNIE
	(zmiany widzi tylko ten klient, nic nie jest replikowane):
		• postacie wszystkich graczy, także własną i tych, którzy odrodzą się albo dołączą w trakcie;
		• obiekty z tagiem Ustawienia.TAG_UKRYJ (hak dla systemów gry: pety, pociski, efekty);
		• każdą obcą część w pudle sceny (zapytanie co SKAN_CO s; części z CanQuery = false zapytanie pomija — od tego jest tag).
	Chowamy: części i naklejki (LocalTransparencyModifier = 1), napisy, obrysy, cząsteczki, smugi i światła (Enabled = false),
	tabliczki z nazwą (Humanoid.DisplayDistanceType). Wartości sprzed walki wracają przy sprzątaniu.
]]
local SKAN_CO = 0.2

function Sesja:schowajObcych()
	local zapamietane: { [Instance]: { [string]: any } } = {}
	local czesci: { [BasePart]: boolean } = {}
	local modele: { [Instance]: boolean } = {}
	self.schowaneCzesci = czesci
	self.liczbaSchowanych = 0
	-- przywracanie rejestrujemy PIERWSZE, więc wykona się po odłączeniu wszystkich połączeń z tej funkcji
	self:posprzataj(function()
		self.schowaneCzesci = nil
		for obiekt, pola in zapamietane do
			for pole, wartosc in pola do
				pcall(function()
					(obiekt :: any)[pole] = wartosc
				end)
			end
		end
		table.clear(zapamietane)
	end)

	local function ustaw(obiekt: Instance, pole: string, wartosc: any)
		local pola = zapamietane[obiekt]
		if not pola then
			pola = {}
			zapamietane[obiekt] = pola
		end
		if pola[pole] == nil then
			local ok, stara = pcall(function()
				return (obiekt :: any)[pole]
			end)
			if not ok then
				return
			end
			pola[pole] = stara
		end
		pcall(function()
			(obiekt :: any)[pole] = wartosc
		end)
	end
	local function schowajJeden(d: Instance)
		if d:IsA("BasePart") then
			if not d:IsA("Terrain") then
				ustaw(d, "LocalTransparencyModifier", 1)
				czesci[d] = true
			end
		elseif d:IsA("Decal") then -- także Texture
			ustaw(d, "LocalTransparencyModifier", 1)
		elseif d:IsA("LayerCollector") or d:IsA("Highlight") or d:IsA("ParticleEmitter") or d:IsA("Trail") or d:IsA("Beam")
			or d:IsA("Fire") or d:IsA("Smoke") or d:IsA("Sparkles") or d:IsA("Light") then
			ustaw(d, "Enabled", false)
		elseif d:IsA("Humanoid") then
			ustaw(d, "DisplayDistanceType", Enum.HumanoidDisplayDistanceType.None)
		end
	end
	local function schowajCalosc(korzen: Instance)
		if modele[korzen] or self.zakonczona then
			return
		end
		modele[korzen] = true
		self.liczbaSchowanych += 1
		schowajJeden(korzen)
		for _, d in korzen:GetDescendants() do
			schowajJeden(d)
		end
		-- doczytywane później akcesoria, broń w ręce, efekty
		self:polacz(korzen.DescendantAdded, function(d)
			if not self.zakonczona then
				schowajJeden(d)
			end
		end)
	end
	-- część postaci → cała postać (model z humanoidem); inna część → tylko ona (nie chowamy całych modeli mapy)
	local function korzenCzesci(czesc: BasePart): Instance
		local m = czesc:FindFirstAncestorOfClass("Model")
		while m do
			if m:FindFirstChildOfClass("Humanoid") then
				return m
			end
			m = m:FindFirstAncestorOfClass("Model")
		end
		return czesc
	end

	-- 1) postacie wszystkich graczy
	local function sledzGracza(p: Player)
		if p.Character then
			schowajCalosc(p.Character)
		end
		self:polacz(p.CharacterAdded, function(postac)
			schowajCalosc(postac)
		end)
	end
	for _, p in Players:GetPlayers() do
		sledzGracza(p)
	end
	self:polacz(Players.PlayerAdded, sledzGracza)

	-- 2) obiekty oznaczone tagiem
	for _, o in CollectionService:GetTagged(Ustawienia.TAG_UKRYJ) do
		schowajCalosc(o)
	end
	self:polacz(CollectionService:GetInstanceAddedSignal(Ustawienia.TAG_UKRYJ), schowajCalosc)

	-- 3) obce części w pudle sceny (nasza arena, szablony i scena lokalna nie są obce; płyta pod areną też nie)
	local wyklucz = { self.scena }
	for _, n in { "Arena", "Aktorzy" } do
		local d = self.kontener:FindFirstChild(n)
		if d then
			table.insert(wyklucz, d)
		end
	end
	local plyta = workspace:FindFirstChild("Baseplate") -- tylko odczyt: nie dotykamy
	if plyta then
		table.insert(wyklucz, plyta)
	end
	table.insert(wyklucz, workspace.Terrain)
	local filtr = OverlapParams.new()
	filtr.FilterType = Enum.RaycastFilterType.Exclude
	filtr.FilterDescendantsInstances = wyklucz
	local pudlo = CFrame.new(Ustawienia.SRODEK + Ustawienia.OBSZAR_PRZESUNIECIE)
	self.skanujObcych = function()
		for _, czesc in workspace:GetPartBoundsInBox(pudlo, Ustawienia.OBSZAR_ROZMIAR, filtr) do
			if not czesci[czesc] then
				schowajCalosc(korzenCzesci(czesc))
			end
		end
	end
	self.skanCzas = 0
	self.skanujObcych()
end

-- co klatkę: kamera Roblox (TransparencyController) potrafi przywrócić przezroczystość własnej postaci — pilnujemy jej
function Sesja:pilnujSchowanych(dt: number)
	local czesci = self.schowaneCzesci
	if not czesci then
		return
	end
	self.skanCzas += dt
	if self.skanCzas >= SKAN_CO then
		self.skanCzas = 0
		self.skanujObcych()
	end
	for czesc in czesci do
		if czesc.LocalTransparencyModifier < 1 then
			czesc.LocalTransparencyModifier = 1
		end
	end
end

------------------------------------------------------------------ start jednej walki (także „Jeszcze raz”)
function Sesja:rozpocznij(walka)
	self.walka = walka
	self.tau = 0
	self.tauWyniku = 0
	self.pominieto = false
	self.klatki = table.create(700)
	self.koszt = table.create(700)
	self.zegarStartu = os.clock()
	self.utworzonoNaStarcie = self.utworzono
	self.wymiany = {}
	for i, z in walka.dziennik do
		table.insert(self.wymiany, {
			nr = i, t = z.t, kto = z.kto, cel = if z.kto == "gracz" then "wrog" else "gracz", akcja = z.akcja,
			obrazenia = z.obrazenia, hp_po = z.hp_po, smiertelny = z.hp_po <= 0, krytyk = z.akcja == "krytyk",
			wyzwolone = false, ciecie = false, wypad = false, wypadStop = false,
		})
	end
	local ostatnia = self.wymiany[#self.wymiany]
	self.zwyciezca, self.pokonany = ostatnia.kto, ostatnia.cel
	self.tFinalu = ostatnia.t + (if ostatnia.krytyk then ZALEGLOSC else 0)
	self.final = { wiwat = false, baner = false, lup = false }
	self.wstep = { pokazany = false, schowany = false }
	self.wstrzas = { sila = 0, wiek = 0 }

	-- ujęcia kamery: plan ogólny, potem jedno ujęcie na wymianę, na końcu objazd
	self.ujecia = { { start = 0, typ = "ogolny" } }
	local poprzednia = nil
	for _, w in self.wymiany do
		local start = w.t - (if w.krytyk then ZW_PRZED + 0.32 else 0.5)
		if poprzednia then
			start = math.max(start, poprzednia.t + (if poprzednia.krytyk then ZW_PO + 0.14 else 0.4))
		end
		start = math.min(start, w.t - 0.18)
		local typ = if w.krytyk then "krytyk" elseif w.kto == "gracz" then "zaRamieniem" else "zblizenie"
		table.insert(self.ujecia, { start = start, typ = typ, wymiana = w })
		poprzednia = w
	end
	-- objazd zaczyna się zaraz po zwolnieniu: pokonany jeszcze leci, a zwycięzca wraca na miejsce już w nowym kadrze
	-- (później ujęcie krytyka gubiło zwycięzcę za lewą krawędzią ekranu)
	table.insert(self.ujecia, { start = self.tFinalu + 0.05, typ = "objazd" })

	-- aktorzy na miejsca
	for strona, aktor in self.aktorzy do
		for _, tor in aktor.tory do
			tor:Stop(0)
		end
		aktor.tory.idle:Play(0)
		aktor.tory.idle:AdjustSpeed(1)
		aktor.tory.bron:Play(0)
		if strona == "wrog" then
			aktor.tory.idle.TimePosition = 1.4 -- żeby obaj nie kołysali się równo
		end
	end
	self:usunEfekty()
	self.ui:usunNapisy()
	self.ui:ukryjWynik()
	self.ui:ukryjBaner(true)
	self.ui:ustawStrony(walka.strony)
	self.ui:pokazPaski(true)
	self.ui:pokazPomin(function()
		self:pomin()
	end)
	self.zaslonaCel = 0
	self.faza = "odtwarzanie"
	self:atrybut("OstatniStan", "odtwarzanie")
	self:atrybut("OstatnieZiarno", walka.ziarno)
end

------------------------------------------------------------------ efekty 3D: iskry z klocków i łup
function Sesja:czescEfektu(): BasePart
	local p = table.remove(self.efekty.wolne)
	if not p then
		p = self:nowa("Part", {
			Name = "Iskra", Anchored = true, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false,
			Material = Enum.Material.Neon, Size = Vector3.one * 0.4,
		}, self.scena)
	end
	p.Transparency = 0
	return p
end

function Sesja:iskry(punkt: Vector3, akcja: string)
	local ile = if akcja == "krytyk" then 16 elseif akcja == "blok" then 9 else 8
	local paleta = if akcja == "blok" then { K.turkus, K.bialy, K.blekit }
		elseif akcja == "krytyk" then { K.zolty, K.pomarancz, K.bialy }
		else { K.bialy, K.zolty }
	local predkosc = if akcja == "krytyk" then 19 else 12
	for _ = 1, ile do
		local p = self:czescEfektu()
		local kierunek = Vector3.new(los:NextNumber(-1, 0.5), los:NextNumber(-0.15, 1), los:NextNumber(-1, 1)).Unit
		local rozmiar = los:NextNumber(0.28, 0.6) * (if akcja == "krytyk" then 1.35 else 1)
		p.Color = paleta[los:NextInteger(1, #paleta)]
		table.insert(self.efekty.iskry, {
			czesc = p, poz = punkt, v = kierunek * predkosc * los:NextNumber(0.55, 1.15), wiek = 0,
			zycie = los:NextNumber(0.3, 0.5), rozmiar = rozmiar,
			obrot = CFrame.Angles(los:NextNumber(0, 6), los:NextNumber(0, 6), los:NextNumber(0, 6)),
		})
	end
end

function Sesja:wyrzucLup(natychmiast: boolean)
	local lup = self.walka.lup
	local pokonany = self.aktorzy[self.pokonany]
	local podloga = Ustawienia.podloga().Position.Y
	local tyl = pokonany.dom.LookVector * -1
	local zrodlo = pokonany.dom.Position + tyl * 2.2 + Vector3.new(0, -Ustawienia.BIODRA + 1.4, 0)
	local doSrodka = -tyl
	local monet = math.clamp(math.floor(lup.zloto / 11), 5, 11)
	for i = 1, monet do
		local kat = los:NextNumber(0, math.pi * 2)
		local promien = los:NextNumber(1.3, 3.6)
		local cel = zrodlo + doSrodka * 2.2 + Vector3.new(-1.6 + math.cos(kat) * promien, 0, math.sin(kat) * promien)
		cel = Vector3.new(cel.X, podloga + 0.22, cel.Z)
		local moneta = self:nowa("Part", {
			Name = "Moneta", Anchored = true, CanCollide = false, CanQuery = false, CanTouch = false,
			Material = Enum.Material.SmoothPlastic, Color = if i % 3 == 0 then Color3.fromHex("#FFE98A") else K.zolty,
			Size = Vector3.new(0.85, 0.24, 0.85),
		}, self.scena)
		table.insert(self.efekty.lup, {
			czesci = { { moneta, CFrame.new() } }, start = zrodlo, cel = cel, wys = los:NextNumber(2.6, 4.6),
			opoznienie = (i - 1) * 0.035, trwa = los:NextNumber(0.5, 0.7), wiek = if natychmiast then 99 else 0,
			obrotKoncowy = CFrame.Angles(0, kat, 0), wiruje = true,
		})
	end
	if (lup.jajko or 0) > 0 then
		local cel = zrodlo + doSrodka * 3.4 + Vector3.new(-3.2, 0, 0)
		cel = Vector3.new(cel.X, podloga + 1.05, cel.Z)
		local czesci = {}
		local function klocek(rozmiar: Vector3, offset: CFrame, kolor: Color3, material: Enum.Material?)
			local p = self:nowa("Part", {
				Name = "Jajko", Anchored = true, CanCollide = false, CanQuery = false, CanTouch = false,
				Material = material or Enum.Material.SmoothPlastic, Color = kolor, Size = rozmiar,
			}, self.scena)
			table.insert(czesci, { p, offset })
		end
		klocek(Vector3.new(1.5, 1.3, 1.5), CFrame.new(0, -0.1, 0), Color3.fromHex("#FFFFFF"))
		klocek(Vector3.new(1.15, 0.5, 1.15), CFrame.new(0, 0.75, 0), Color3.fromHex("#FFFFFF"))
		klocek(Vector3.new(0.7, 0.35, 0.7), CFrame.new(0, 1.15, 0), Color3.fromHex("#F1F6FF"))
		klocek(Vector3.new(1.15, 0.4, 1.15), CFrame.new(0, -0.9, 0), Color3.fromHex("#E3ECF7"))
		klocek(Vector3.new(0.12, 0.34, 0.34), CFrame.new(-0.76, 0.1, 0.3), Color3.fromHex("#49D6F2"), Enum.Material.Neon)
		klocek(Vector3.new(0.12, 0.3, 0.3), CFrame.new(-0.76, -0.35, -0.3), Color3.fromHex("#49D6F2"), Enum.Material.Neon)
		klocek(Vector3.new(0.12, 0.26, 0.26), CFrame.new(-0.6, 0.72, -0.1), Color3.fromHex("#49D6F2"), Enum.Material.Neon)
		table.insert(self.efekty.lup, {
			czesci = czesci, start = zrodlo, cel = cel, wys = 5.2, opoznienie = 0.12, trwa = 0.8,
			wiek = if natychmiast then 99 else 0, obrotKoncowy = CFrame.new(), wiruje = false, kolysze = true,
		})
	end
end

function Sesja:usunEfekty()
	if not self.efekty then
		return
	end
	for _, i in self.efekty.iskry do
		i.czesc.Transparency = 1
		table.insert(self.efekty.wolne, i.czesc)
	end
	table.clear(self.efekty.iskry)
	for _, l in self.efekty.lup do
		for _, c in l.czesci do
			c[1]:Destroy()
		end
	end
	table.clear(self.efekty.lup)
end

function Sesja:aktualizujEfekty(dtSceny: number, dt: number)
	local iskry = self.efekty.iskry
	for i = #iskry, 1, -1 do
		local s = iskry[i]
		s.wiek += dtSceny
		local u = s.wiek / s.zycie
		if u >= 1 then
			s.czesc.Transparency = 1
			table.insert(self.efekty.wolne, s.czesc)
			table.remove(iskry, i)
		else
			s.v += Vector3.new(0, -34, 0) * dtSceny
			s.poz += s.v * dtSceny
			local r = s.rozmiar * (1 - u * u)
			s.czesc.Size = Vector3.one * math.max(r, 0.05)
			s.czesc.CFrame = CFrame.new(s.poz) * s.obrot
		end
	end
	for _, l in self.efekty.lup do
		if not l.spoczywa or l.kolysze then
			l.wiek += dt
			local u = math.clamp((l.wiek - l.opoznienie) / l.trwa, 0, 1)
			local cf
			if u < 1 then
				local poz = l.start:Lerp(l.cel, u) + Vector3.new(0, l.wys * 4 * u * (1 - u), 0)
				cf = CFrame.new(poz) * (if l.wiruje then CFrame.Angles(u * 9, u * 5, 0) else CFrame.Angles(0, 0, math.sin(u * 9) * 0.5))
			else
				l.spoczywa = true
				local kolysanie = if l.kolysze then CFrame.Angles(0, 0, math.sin((l.wiek - l.opoznienie - l.trwa) * 7) * 0.12) else CFrame.new()
				cf = CFrame.new(l.cel) * l.obrotKoncowy * kolysanie
			end
			local widac = l.wiek >= l.opoznienie
			for _, c in l.czesci do
				c[1].CFrame = cf * c[2]
				c[1].Transparency = if widac then 0 else 1
			end
		end
	end
end

function Sesja:dzwiek(nazwa: string, szybkosc: number?)
	local d = self.dzwieki and self.dzwieki[nazwa]
	if d then
		d.PlaybackSpeed = szybkosc or 1
		d:Play()
	end
end

------------------------------------------------------------------ zdarzenie dziennika dochodzi celu
function Sesja:trafienie(w, cicho: boolean)
	self.ui:ustawZycie(w.cel, w.hp_po, cicho)
	local obronca = self.aktorzy[w.cel]
	if w.smiertelny then
		obronca.tory.bron:Stop(0.25)
		obronca.tory.idle:AdjustSpeed(0)
	end
	if cicho then
		return
	end
	local atakujacy = self.aktorzy[w.kto]
	local glowa = obronca.dom.Position + Vector3.new(0, 2.5, 0)
	local stylLiczby = if w.cel == "gracz" then "otrzymane" else "zadane"
	local liczba = "−" .. tostring(w.obrazenia)
	if w.akcja == "unik" then
		self.ui:napis(glowa, "UNIK!", "unik", Vector2.new(0, -0.03), los:NextNumber(-7, 7))
	elseif w.akcja == "blok" then
		self.ui:napis(glowa, "BLOK!", "blok", Vector2.new(0, -0.1), -5)
		self.ui:napis(glowa, liczba, stylLiczby, Vector2.new(0.03, 0.05), 4)
	elseif w.akcja == "krytyk" then
		self.ui:napis(glowa, "KRYTYK!", "krytyk", Vector2.new(0, -0.115), -6)
		self.ui:napis(glowa, liczba, "krytykLiczba", Vector2.new(0.01, 0.05), 4)
	else
		self.ui:napis(glowa, liczba, stylLiczby, Vector2.new(0, -0.02), los:NextNumber(-8, 8))
	end
	self.wstrzas.sila = WSTRZAS[w.akcja] or 0
	self.wstrzas.wiek = 0
	if w.akcja ~= "unik" then
		local doAtakujacego = (atakujacy.dom.Position - obronca.dom.Position).Unit
		self:iskry(obronca.dom.Position + Vector3.new(-0.4, 0.5, 0) + doAtakujacego * 1.1, w.akcja)
		if w.akcja == "krytyk" then
			self:dzwiek("krytyk", 1.25)
		else
			self:dzwiek("cios", if w.akcja == "blok" then 1.5 else los:NextNumber(0.9, 1.1))
		end
	end
	if w.smiertelny then
		self:dzwiek("upadek", 1.1)
	end
end

------------------------------------------------------------------ co klatkę: pozy aktorów
local function ustawStaw(staw, obrot: CFrame?)
	if not staw then
		return
	end
	if obrot == nil then
		if staw.ostatni ~= nil then
			staw.ostatni = nil
			staw.obiekt[staw.pole] = staw.c0
		end
	else
		staw.ostatni = obrot
		staw.obiekt[staw.pole] = staw.c0 * obrot
	end
end

function Sesja:aktualizujScene(tau: number, tempo: number)
	local aktorzy = self.aktorzy
	for _, aktor in aktorzy do
		local p = aktor.poza
		p.przod, p.bok, p.gora, p.pochyl, p.przechyl = 0, 0, 0, 0, 0
		p.ramie, p.skret, p.garda, p.upadek, p.blysk = 0, 0, 0, 0, 0
	end
	local tempoSceny = 1

	for _, w in self.wymiany do
		local x = tau - w.t
		if x > -1.5 then
			local u, tempoLokalne = zakrzyw(w.krytyk, x)
			local atakujacy, obronca = aktorzy[w.kto], aktorzy[w.cel]
			local pa, pd = atakujacy.poza, obronca.poza
			if tempoLokalne < 1 then
				tempoSceny = tempoLokalne
			end

			-- ATAKUJĄCY: doskok, zamach, cięcie, powrót
			if u < 0.6 then
				pa.przod += DOSKOK * okno(u, -0.38, -0.07, 0.14, 0.54)
				pa.gora += (if w.krytyk then 2.0 else 0.5) * luk(u, -0.38, -0.03)
				local zamach = 0
				if u > -0.44 and u < 0.42 then
					if u < -0.15 then
						zamach = gladko((u + 0.44) / 0.29)
					elseif u < 0 then
						zamach = 1 - 1.25 * gladko((u + 0.15) / 0.15)
					else
						zamach = -0.25 * (1 - gladko(u / 0.42))
					end
				end
				local uderzenie = okno(u, -0.1, 0.03, 0.08, 0.42)
				pa.ramie += (if w.krytyk then rad(88) else rad(64)) * zamach
				pa.pochyl += rad(-9) * math.max(zamach, 0) + (if w.krytyk then rad(22) else rad(15)) * uderzenie
				pa.skret += rad(30) * math.max(zamach, 0) - rad(20) * uderzenie
			end
			-- animacje ataku (tylko „na żywo”; przy przeskoku do wyniku ich nie puszczamy)
			local swieze = x < 0.35 and not self.pominieto
			if w.krytyk and not w.wypad and u >= -0.5 then
				w.wypad = true
				if swieze then
					atakujacy.tory.wypad:Play(0.1, 1, tempoLokalne * tempo)
				end
			end
			if not w.ciecie and u >= -0.13 then
				w.ciecie = true
				if swieze then
					atakujacy.tory.ciecie:Play(0.03, 1, tempoLokalne * tempo)
				end
			end
			if w.krytyk and w.wypad and not w.wypadStop and u >= 0.3 then
				w.wypadStop = true
				atakujacy.tory.wypad:Stop(0.2)
			end
			if u > -0.6 and u < 0.7 then
				if atakujacy.tory.ciecie.IsPlaying then
					atakujacy.tory.ciecie:AdjustSpeed(tempoLokalne * tempo)
				end
				if atakujacy.tory.wypad.IsPlaying then
					atakujacy.tory.wypad:AdjustSpeed(tempoLokalne * tempo)
				end
			end

			-- BRONIĄCY
			if w.akcja == "unik" then
				local zejscie = okno(u, -0.26, -0.05, 0.2, 0.56)
				pd.bok += 2.4 * zejscie
				pd.przechyl += rad(17) * zejscie
				pd.pochyl += rad(-6) * zejscie
			elseif w.akcja == "blok" then
				local garda = okno(u, -0.28, -0.07, 0.2, 0.5)
				pd.garda += garda
				pd.pochyl += rad(7) * garda
				pd.przod -= 0.75 * odrzut(u, 0.07, 0.44)
			elseif u >= 0 then
				local sila = if w.krytyk then 2.5 else 1.3
				if w.smiertelny then
					pd.przod -= sila * 1.25 * wyjscie(u / 0.34)
					pd.upadek += gladko((u - 0.03) / 0.5)
					pd.gora += 1.2 * luk(u, 0, 0.5)
				else
					pd.przod -= sila * odrzut(u, 0.09, 0.5)
					pd.pochyl -= (if w.krytyk then rad(27) else rad(16)) * odrzut(u, 0.08, 0.46)
				end
				pd.blysk = math.max(pd.blysk, 1 - u / 0.17)
			end

			-- chwila trafienia
			if not w.wyzwolone and x >= 0 then
				w.wyzwolone = true
				self:trafienie(w, self.pominieto or x > 0.35)
			end
		end
	end

	-- wstęp: napis „WALKA!”
	if not self.wstep.pokazany and tau >= 0.12 then
		self.wstep.pokazany = true
		if tau < 0.6 then
			self.ui:pokazBaner("WALKA!", K.bialy, K.niebieski)
		else
			self.wstep.schowany = true
		end
	end
	if self.wstep.pokazany and not self.wstep.schowany and tau >= math.min(0.85, self.wymiany[1].t - 0.35) then
		self.wstep.schowany = true
		self.ui:ukryjBaner(false)
	end

	-- finał: wiwat zwycięzcy, baner, łup
	local f = tau - self.tFinalu
	if f >= 0.5 and not self.final.wiwat then
		self.final.wiwat = true
		local zwyciezca = aktorzy[self.zwyciezca]
		zwyciezca.tory.wiwat:Play(0.15)
		for _, aktor in aktorzy do
			aktor.tory.ciecie:Stop(0.1)
			aktor.tory.wypad:Stop(0.1)
		end
	end
	if f >= 0.55 and not self.final.baner then
		self.final.baner = true
		if not self.pominieto then
			-- walka rozstrzygnięta: „POMIŃ” nie ma już czego pomijać, a jego miejsce zajmuje baner u dołu kadru
			-- (u góry zasłaniałby głowę zwycięzcy w ujęciu końcowym)
			self.ui:ukryjPomin()
			if self.zwyciezca == "gracz" then
				self.ui:pokazBaner("ZWYCIĘSTWO!", K.zolty, K.czerwony, 0.83)
			else
				self.ui:pokazBaner("PORAŻKA!", K.bialy, K.fiolet, 0.83)
			end
		end
	end
	if f >= 0.6 and not self.final.lup then
		self.final.lup = true
		if self.zwyciezca == "gracz" then
			self:wyrzucLup(self.pominieto)
		end
	end

	-- zastosuj pozy
	local B = Ustawienia.BIODRA
	for _, aktor in aktorzy do
		local p = aktor.poza
		local upadek = math.clamp(p.upadek, 0, 1)
		local cf = aktor.dom * CFrame.new(p.bok * aktor.znakBoku, p.gora, -p.przod)
		cf = cf * CFrame.new(0, -B, 0) * CFrame.Angles(-p.pochyl + upadek * rad(84), 0, -p.przechyl * aktor.znakBoku) * CFrame.new(0, B, 0)
		if upadek > 0 then
			cf = CFrame.new(0, 0.42 * upadek, 0) * cf
		end
		aktor.hrp.CFrame = cf

		local stawy = aktor.stawy
		local ramie = p.ramie
		if not aktor.maTarcze and p.garda > 0 then
			ramie += rad(34) * p.garda -- bez tarczy: zasłona bronią
		end
		ustawStaw(stawy.RightShoulder, if ramie ~= 0 then CFrame.Angles(ramie, 0, 0) else nil)
		ustawStaw(stawy.Waist, if p.skret ~= 0 then CFrame.Angles(0, -p.skret, 0) else nil)
		if aktor.maTarcze and upadek < 0.5 then
			-- garda: przedramię z tarczą w poprzek ciała; przy bloku tarcza idzie w górę i do przodu
			local g = math.clamp(p.garda, 0, 1)
			ustawStaw(stawy.LeftShoulder, CFrame.Angles(rad(16 + 50 * g), 0, 0) * CFrame.Angles(0, rad(-76), 0))
			ustawStaw(stawy.LeftElbow, CFrame.Angles(rad(96 - 14 * g), 0, 0))
		elseif aktor.maTarcze then
			ustawStaw(stawy.LeftShoulder, nil)
			ustawStaw(stawy.LeftElbow, nil)
		end

		local blysk = math.clamp(p.blysk, 0, 1)
		if aktor.obrys and blysk ~= aktor.blyskOstatni then
			aktor.blyskOstatni = blysk
			aktor.obrys.FillTransparency = 1 - 0.55 * blysk -- biały błysk trafienia (słabszy, żeby postać nie znikała w zwolnieniu)
			aktor.obrys.OutlineColor = K.tusz:Lerp(K.bialy, blysk)
		end
	end
	return tempoSceny
end

------------------------------------------------------------------ co klatkę: kamera
-- pozycje w układzie podłogi podestu: X = wschód (w głąb kadru), Y = góra, Z = południe (w prawo na ekranie)
function Sesja:ujecie(uj, tau: number): (Vector3, Vector3, number)
	local lt = tau - uj.start
	if uj.typ == "ogolny" then
		local k = wyjscie(lt / 1.7)
		return Vector3.new(-25.5 + 4.5 * k, 6.4 - 1.1 * k, -3.2 + 1.6 * k), Vector3.new(0, 3.1, 0.2), 40
	elseif uj.typ == "zaRamieniem" then
		-- atakuje gracz: kamera z przodu‑boku Rycerza (3/4), cel ciosu widać obok jego barku, nie za plecami
		local k = gladko(lt / 1.3)
		return Vector3.new(-14.2 + 1.2 * k, 5.0 - 0.4 * k, -9.2 + 0.8 * k), Vector3.new(0, 2.5, 1.2), 44
	elseif uj.typ == "zblizenie" then
		-- atakuje wróg: lustrzane ujęcie od strony Zbira (Rycerz dalej po lewej, Zbir po prawej — strony ekranu się nie zmieniają)
		local k = gladko(lt / 1.3)
		return Vector3.new(-14.2 + 1.2 * k, 5.0 - 0.4 * k, 9.2 - 0.8 * k), Vector3.new(0, 2.5, -1.2), 44
	elseif uj.typ == "krytyk" then
		-- cios krytyczny: niska kamera z boku, w zwolnieniu „wjazd” optyczny (zawężenie kąta) na moment trafienia;
		-- obie postacie i lot pokonanego zostają w kadrze
		local w = uj.wymiana
		local znak = if w.kto == "gracz" then 1 else -1
		local k = gladko((tau - w.t + ZW_PRZED) / (ZW_PRZED + 0.12))
		return Vector3.new(-14.5 + 1.0 * k, 2.3 - 0.3 * k, znak * (0.6 + 0.4 * k)), Vector3.new(0, 3.5, znak * (1.6 + 0.6 * k)), 52 - 16 * k
	end
	-- objazd wokół zwycięzcy (po zatrzymaniu czasu sceny kamera płynie dalej, bardzo wolno). Kończy się tak, że zwycięzca
	-- stoi w lewej (po przegranej: prawej) ćwiartce kadru, a drugą połowę zajmuje panel wyniku.
	local znak = if self.zwyciezca == "gracz" then 1 else -1
	local czas = lt + self.tauWyniku
	local k = wyjscie(czas / 2.4)
	local dryf = math.min(math.max(0, czas - 2.4) * 1.5, 12)
	-- kamera zawsze po stronie, w którą patrzy zwycięzca (widać jego twarz, nie plecy)
	local kat = rad(45 - 17 * k - dryf)
	local promien = 19 - 2.5 * k
	local zwyciezca = Vector3.new(0, 3.0, -znak * Ustawienia.ODSTEP / 2)
	local cel = zwyciezca + Vector3.new(0, 0.6, znak * (4 + 2.5 * k))
	return zwyciezca + Vector3.new(-promien * math.cos(kat), 5.5 - 0.8 * k, znak * promien * math.sin(kat)), cel, 44
end

function Sesja:aktualizujKamere(tau: number, dt: number)
	local kamera = self.kamera
	local aktywne = self.ujecia[1]
	for _, uj in self.ujecia do
		if uj.start <= tau then
			aktywne = uj
		else
			break
		end
	end
	if aktywne ~= self.ujecieAktywne then
		self.ujecieAktywne = aktywne
		self.licznikUjec = (self.licznikUjec or 0) + 1
	end
	local poz, cel, kat = self:ujecie(aktywne, tau)
	local podloga = Ustawienia.podloga()
	-- drżenie po trafieniu
	local drzenie = Vector3.zero
	local ws = self.wstrzas
	if ws.sila > 0 then
		ws.wiek += dt
		local amplituda = ws.sila * math.exp(-ws.wiek * 9)
		if amplituda < 0.004 then
			ws.sila = 0
		else
			drzenie = Vector3.new(los:NextNumber(-1, 1), los:NextNumber(-1, 1), los:NextNumber(-1, 1)) * amplituda
		end
	end
	kamera.CFrame = CFrame.lookAt(podloga:PointToWorldSpace(poz) + drzenie, podloga:PointToWorldSpace(cel) + drzenie * 0.35)
	-- kąt widzenia jest projektowany dla kadru 16:9; przy czarnych pasach trzeba go poszerzyć na całe okno
	local pelny = 2 * math.atan(math.tan(rad(kat) / 2) / self.ui.wspolczynnikPasa)
	kamera.FieldOfView = math.clamp(math.deg(pelny), 5, 120)
end

------------------------------------------------------------------ pętla
function Sesja:krok(dt: number)
	local ui = self.ui
	self:pilnujSchowanych(dt)
	if self.faza == "wynik" then
		ui:ustawBlokadeJeszczeRaz(wolnaZa())
	end
	if self.zaslona ~= self.zaslonaCel then
		local krok = dt * 7
		if self.zaslona < self.zaslonaCel then
			self.zaslona = math.min(self.zaslonaCel, self.zaslona + krok)
		else
			self.zaslona = math.max(self.zaslonaCel, self.zaslona - krok)
		end
		ui:ustawZaslone(self.zaslona)
	end
	local kamera = self.kamera or workspace.CurrentCamera
	if self.faza ~= "odtwarzanie" and self.faza ~= "wynik" then
		ui:aktualizuj(dt, kamera)
		return
	end

	local tempo = self.tempo
	local czas = self.walka.czas
	if self.faza == "odtwarzanie" then
		table.insert(self.klatki, dt)
		self.tau = math.min(czas, self.tau + dt * tempo)
		if self.opcje.pominPo and self.tau >= self.opcje.pominPo then
			self:pomin()
		end
	else
		self.tauWyniku += dt
	end
	local tau = self.tau
	local tempoSceny = self:aktualizujScene(tau, tempo)
	self:aktualizujEfekty(dt * tempo * tempoSceny, dt)
	self:aktualizujKamere(tau, dt)
	ui:aktualizuj(dt, kamera)
	if self.opcje.etykietaCzasu then
		ui:ustawZegar(string.format("t = %.2f / %.2f s   %s   ujęcie: %s", tau, czas, self.faza, self.ujecieAktywne and self.ujecieAktywne.typ or "?"))
	end
	if self.faza == "odtwarzanie" and tau >= czas then
		self:pokazWynik()
	end
end

function Sesja:pomin()
	if self.faza ~= "odtwarzanie" or self.pominieto then
		return
	end
	self.pominieto = true
	self:dzwiek("przycisk")
	self.tau = self.walka.czas
	self.ui:usunNapisy()
	self.ui:ukryjBaner(true)
	for _, i in self.efekty.iskry do
		i.wiek = 99
	end
	for _, aktor in self.aktorzy do
		aktor.tory.ciecie:Stop(0)
		aktor.tory.wypad:Stop(0)
	end
	self.wstrzas.sila = 0
end

function Sesja:pokazWynik()
	self.faza = "wynik"
	self.tauWyniku = 0
	local ui = self.ui
	ui:ukryjPomin()
	ui:ukryjBaner(false)

	-- pomiary odtworzenia
	local klatki = self.klatki
	local n = #klatki
	local suma, maks = 0, 0
	for _, dt in klatki do
		suma += dt
		maks = math.max(maks, dt)
	end
	local posortowane = table.clone(klatki)
	table.sort(posortowane)
	local p95 = if n > 0 then posortowane[math.clamp(math.ceil(n * 0.95), 1, n)] else 0
	self:atrybut("OstatniCzasTrwania", math.floor((os.clock() - self.zegarStartu) * 100 + 0.5) / 100)
	self:atrybut("OstatniaSredniaKlatki", if n > 0 then math.floor(suma / n * 100000 + 0.5) / 100 else 0)
	self:atrybut("OstatniP95Klatki", math.floor(p95 * 100000 + 0.5) / 100)
	self:atrybut("OstatniaMaksKlatki", math.floor(maks * 100000 + 0.5) / 100)
	self:atrybut("OstatniaLiczbaKlatek", n)
	-- koszt naszego skryptu na klatkę (bez renderowania): średnia i 95. percentyl w ms
	local koszt = table.clone(self.koszt or {})
	table.sort(koszt)
	local sumaKosztu = 0
	for _, c in koszt do
		sumaKosztu += c
	end
	local nk = #koszt
	self:atrybut("OstatniKosztSkryptuSredni", if nk > 0 then math.floor(sumaKosztu / nk * 100000 + 0.5) / 100 else 0)
	self:atrybut("OstatniKosztSkryptuP95", if nk > 0 then math.floor(koszt[math.clamp(math.ceil(nk * 0.95), 1, nk)] * 100000 + 0.5) / 100 else 0)
	self:atrybut("OstatniKosztSkryptuMaks", if nk > 0 then math.floor(koszt[nk] * 100000 + 0.5) / 100 else 0)
	self:atrybut("OstatniaLiczbaInstancji", self.utworzono + ui.utworzono)
	self:atrybut("OstatnioPominieto", self.pominieto)
	self:atrybut("OstatniWynik", self.walka.wynik)
	self:atrybut("OstatniaLiczbaWymian", #self.walka.dziennik)
	self:atrybut("OstatniaLiczbaUjec", self.licznikUjec or 0)
	self:atrybut("OstatniCzasSerwera", math.floor((self.czasSerwera or 0) * 10 + 0.5) / 10)
	self:atrybut("OstatniaLiczbaSchowanych", self.liczbaSchowanych or 0) -- obce postacie / obiekty schowane lokalnie
	self:atrybut("LicznikOdtworzen", (self.kontener:GetAttribute("LicznikOdtworzen") or 0) + 1)
	self:atrybut("OstatniStan", "wynik")

	ui:pokazWynik(self.walka, function()
		self:jeszczeRaz()
	end, function()
		self:zakoncz("zamknieto")
	end)
	if self.opcje.zamknijPo then
		local walka = self.walka
		task.delay(self.opcje.zamknijPo, function()
			if not self.zakonczona and self.faza == "wynik" and self.walka == walka then
				self:zakoncz("zamknieto")
			end
		end)
	end
end

function Sesja:jeszczeRaz()
	if self.faza ~= "wynik" or wolnaZa() > 0 then
		return -- przycisk pokazuje odliczanie: serwer nie uznał jeszcze poprzedniej walki za skończoną
	end
	self.faza = "prosba"
	self:dzwiek("przycisk")
	self.ui:ukryjWynik()
	self.zaslonaCel = 1
	self:atrybut("OstatniStan", "prosba")
	task.spawn(function()
		local ok, wynik = pcall(function()
			return self:poprosSerwer()
		end)
		if self.zakonczona then
			return
		end
		if not ok then
			if self.odmowa then
				self:zakoncz("odmowa")
			else
				warn("[TestWalki] Nie udało się rozpocząć kolejnej walki: " .. tostring(wynik))
				self:zakoncz("blad")
			end
			return
		end
		while self.zaslona < 0.98 and not self.zakonczona do
			task.wait()
		end
		if not self.zakonczona then
			self.licznikUjec = 0
			self:rozpocznij(wynik)
		end
	end)
end

function Sesja:start()
	local t0 = os.clock()
	self:atrybut("OstatniStan", "prosba")
	local playerGui = self.gracz:WaitForChild("PlayerGui")
	self.ui = InterfejsWalki.nowy(playerGui, Ustawienia)
	self:posprzataj(function()
		self.ui:zniszcz()
	end)
	self.ui:pokazPaski(false)
	self.zaslona, self.zaslonaCel = 0, 1
	RunService:BindToRenderStep(KROK, Enum.RenderPriority.Camera.Value + 1, function(dt)
		local t0 = os.clock()
		local ok, blad = xpcall(function()
			self:krok(dt)
		end, debug.traceback)
		if self.faza == "odtwarzanie" and self.koszt then
			table.insert(self.koszt, os.clock() - t0) -- ile czasu procesora zajmuje nasz kod w jednej klatce
		end
		if not ok then
			warn("[TestWalki] Błąd w klatce cutscenki: " .. tostring(blad))
			self:zakoncz("blad")
		end
	end)
	self:posprzataj(function()
		RunService:UnbindFromRenderStep(KROK)
	end)
	self:zablokujSterowanie()
	self:ukryjInneGui()
	self:wylaczPodpowiedz()
	self:pilnujPrzerwania()

	local walka = self:poprosSerwer()
	while self.zaslona < 0.98 do -- scenę i kamerę przestawiamy dopiero pod pełną zasłoną
		task.wait()
		if self.zakonczona then
			error("przerwano")
		end
	end
	self:przygotujScene()
	self:przejmijKamere()
	self:atrybut("OstatniCzasPrzygotowania", math.floor((os.clock() - t0) * 1000 + 0.5))
	self:rozpocznij(walka)
end

-- Zakończenie z dowolnego powodu: "zamknieto", "przerwano", "blad". Bezpieczne przy wielokrotnym wywołaniu.
function Sesja:zakoncz(powod: string)
	if self.zakonczona then
		return
	end
	self.zakonczona = true
	self.faza = "koniec"
	if sesja == self then
		sesja = nil
	end
	-- miękki powrót do gry: krótka czarna zasłona, która sama się rozjaśnia i znika
	if powod == "zamknieto" then
		local playerGui = self.gracz:FindFirstChildOfClass("PlayerGui")
		if playerGui then
			local przejscie = Instance.new("ScreenGui")
			przejscie.Name = "TestWalkiPrzejscie"
			przejscie.IgnoreGuiInset = true
			przejscie.ResetOnSpawn = false
			przejscie.DisplayOrder = 61
			local czern = Instance.new("Frame")
			czern.Size = UDim2.fromScale(1, 1)
			czern.BackgroundColor3 = Color3.new(0, 0, 0)
			czern.BorderSizePixel = 0
			czern.Parent = przejscie
			przejscie.Parent = playerGui
			local rozjasnienie = TweenService:Create(czern, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { BackgroundTransparency = 1 })
			rozjasnienie.Completed:Once(function()
				przejscie:Destroy()
			end)
			rozjasnienie:Play()
			task.delay(1, function()
				if przejscie.Parent then
					przejscie:Destroy()
				end
			end)
		end
	end
	for i = #self.sprzatanie, 1, -1 do
		local ok, blad = pcall(self.sprzatanie[i])
		if not ok then
			warn("[TestWalki] Sprzątanie po cutscence: " .. tostring(blad))
		end
	end
	table.clear(self.sprzatanie)
	self:atrybut("OstatniStan", powod)
end

------------------------------------------------------------------ API
function Odtwarzacz.uruchom(kontener: Instance, opcje: any?): boolean
	if sesja then
		return false -- walka już trwa
	end
	local gracz = Players.LocalPlayer
	if not gracz then
		return false
	end
	if wolnaZa() > 0 then
		pcall(function()
			kontener:SetAttribute("OstatniaOdmowa", "walka_trwa_lokalnie")
		end)
		return false -- serwer i tak by odmówił; podpowiedź pokazuje odliczanie
	end
	local o = if type(opcje) == "table" then opcje else {}
	local s = setmetatable({
		kontener = kontener, gracz = gracz, opcje = o, tempo = math.clamp(tonumber(o.tempo) or 1, 0.02, 4),
		sprzatanie = {}, utworzono = 0, faza = "prosba", zakonczona = false, zaslona = 0, zaslonaCel = 0,
		tau = 0, tauWyniku = 0,
	}, Sesja)
	sesja = s
	local ok, blad = xpcall(function()
		s:start()
	end, debug.traceback)
	if not ok then
		if s.odmowa then
			s:zakoncz("odmowa") -- serwer odmówił (za daleko, walka trwa…): to nie błąd, bez ostrzeżenia
		else
			if not s.zakonczona then
				warn("[TestWalki] Nie udało się uruchomić cutscenki: " .. tostring(blad))
			end
			s:zakoncz("blad")
		end
	end
	return ok
end

function Odtwarzacz.pomin()
	if sesja then
		sesja:pomin()
	end
end

function Odtwarzacz.zamknij()
	if sesja then
		sesja:zakoncz("zamknieto")
	end
end

function Odtwarzacz.czyTrwa(): boolean
	return sesja ~= nil
end

-- ile sekund zostało, zanim serwer przyjmie następną walkę (0 = można)
function Odtwarzacz.wolnaZa(): number
	return wolnaZa()
end

return Odtwarzacz
