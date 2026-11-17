--[[
	OdtwarzaczWalki2 — kliencka cutscenka walki v2. Niczego nie liczy: prosi serwer o walkę (wybór z listy) i ODTWARZA
	CAŁY dziennik v2 zdarzenie po zdarzeniu, każde z jego czasem t i trwaniem z dziennika (D-068: długość walki wynika
	tylko z silnika; odtwarzacz niczego nie skraca — przyspieszenie ×2 / ×4 i „POMIŃ” to wybór gracza).
	Wzór i źródło sprawdzonych rozwiązań: v1 (swiat/test_walki_roblox/zrodla/OdtwarzaczWalki.luau) — blokada
	sterowania, chowanie GUI gry i obcych w kadrze, zasłona, kamera skryptowa, sprzątanie po zamknięciu, resecie i błędzie.

	Jak to działa:
		• scena jest LOKALNA: klony aktorów (Moduly/Aktorzy, własne klipy z danych, bez uploadu) w folderze ScenaLokalna;
		• czas sceny τ biegnie z tempem gracza (×1/×2/×4) i zwalnia przy krytyku i ciosie kończącym (Choreografie.ZWOLNIENIE);
		  klipy, ruch aktorów, pociski i efekty liczą się w czasie sceny, więc tempo i zwolnienie działają na wszystko;
		• każde zdarzenie ma obsługę (Obsluga.<nazwa> wg Choreografie.ZDARZENIA), a atak / umiejętność — choreografię
		  w stylu z Choreografie (Choreo.<styl>): wrecz, skok, pocisk, chmura, korzenie, na_siebie;
		• paski życia dostają wartości z dziennika (hp_gracz / hp_wrog) w chwili trafienia; na początku każdego zdarzenia
		  odtwarzacz sprawdza, czy pasek zgadza się z poprzednim zdarzeniem (licznik niezgodności dla testów);
		• efekty na postaciach (Efekty3D.Wyglad) żyją od efekt_nalozony do efekt_koniec; ikony z licznikiem tur w interfejsie;
		• kamera: zróżnicowane ujęcia planowane na zdarzenia (plan ogólny, zza atakującego, zza broniącego, z boku,
		  zbliżenie, krytyk z „wjazdem”, lot pocisku, umiejętność na siebie, efekt), z najkrótszym czasem ujęcia w czasie
		  rzeczywistym — przy długiej walce i większym tempie mniej cięć i płynne przejścia zamiast cięć;
		• finał: upadek pokonanego, radość zwycięzcy, łup z dziennika, objazd kamery, panel wyniku (JESZCZE RAZ, ZAMKNIJ).

	API:  uruchom(kontener, wybor, opcje?) → boolean | pomin(wymus?) | zamknij() | jeszczeRaz() | ustawTempo(t) | czyTrwa()
	      wolnaZa() → s | stan() → tabela (do testów) | przewin(s) (tylko opcje.reczny)
	opcje (testy): tempo (startowe), reczny (czas stoi; przesuwa go przewin), etykietaCzasu, pominPo (wymuszone
	      pominięcie tylko pokazu — serwer i tak sam decyduje o sesji), zamknijPo, obrys;
	      bezPowtorki (las_potwory, P2: panel wyniku bez JESZCZE RAZ).
	Wynik ostatniego odtworzenia → atrybuty kontenera (u klienta): Ostatni* (patrz Sesja:pokazWynik).

	Dziennik v3 (17.11.2026, tools/walka/ZMIANY_SESJA_1611.md):
		• czysta logika w Moduly/PlanWalki (testowana bez Studio tym samym kodem): normalizacja dziennika — nieznane
		  pole albo typ zdarzenia daje ostrzeżenie w konsoli (raz) i odtwarzanie idzie dalej; plan many, tur, powaleń;
		• pasek many pod paskiem życia u obu stron — wartości wyłącznie z dziennika (mana_gracz / mana_wrog), próg =
		  koszt następnej umiejętności z dziennika, gotowa = świeci, użycie = błysk i spadek o koszt (wartosc);
		• statusy z charakterem: trucizna ×N (stosy), podpalenie, krwawienie, spowolnienie (lód, bez straty tury),
		  ogłuszenie (gwiazdki / pnącza, „TRACI TURĘ!”), zdarcie pancerza, wzmocnienie, tarcza −N% na 3 tury;
		• blok każdej klasy i potwora: z tarczą klip i iskry przy tarczy, bez tarczy parada (łuk odbicia, odchylenie),
		  napis „BLOK −N%” (N z czesc_przez_blok) i liczba tego, co przeszło;
		• wskrzeszenie: powalenie (zwolnienie, upadek) → słup światła → powrót z życiem z dziennika, „WSKRZESZENIE!”;
		• zapowiedź pasywek ze slotów i broni na starcie (opis z odpowiedzi serwera; nazwy i premie z danych silnika);
		• pomijanie (D-078): przycisk POMIŃ i spacja TYLKO, gdy serwer dał zgodę (odpowiedź z walką: pomijanie = true,
		  albo — dla walk z lasu — zapytanie Zdalne/PominiecieWalki2 prototypu); pominięcie zgłaszamy serwerowi,
		  który zwalnia sesję (tablica prototypu) albo odmawia. Klient sam zgody nie wyda.

		Własne dźwięki (17.11.2026, pakiet swiat/dzwiek_gra): gdy jest Workspace/DzwiekGra/Moduly/KatalogDzwiekow i arkusz
		ma identyfikator ≠ 0, zdarzenia walki grają ODCINKI jednego pliku-arkusza (Sound.PlaybackRegion) wg katalogu;
		uderzenia tak, żeby szczyt efektu wypadł na klatkę trafienia (start wcześniej; gdy się nie da — od chwili tuż przed
		atakiem efektu). Zdarzenie bez wpisu w katalogu i walka bez arkusza = dzisiejsze dźwięki wbudowane (U.DZWIEKI).
		Próba bez wgranych plików (tylko Play, lokalne atrybuty Workspace/DzwiekGra): TestArkuszId = dowolny dźwięk
		(np. "rbxasset://sounds/action_falling.mp3"), TestArkuszSkala = mnożnik czasów odcinków (krótszy plik).
]]
if not game:GetService("RunService"):IsStudio() then
	local function nic()
		return false
	end
	return { uruchom = nic, pomin = nic, zamknij = nic, czyTrwa = nic, jeszczeRaz = nic, ustawTempo = nic, stan = nic,
		przewin = nic, wolnaZa = function()
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
local U = require(moduly:WaitForChild("Ustawienia"))
local Aktorzy = require(moduly:WaitForChild("Aktorzy"))
local Ch = require(moduly:WaitForChild("Choreografie"))
local Efekty3D = require(moduly:WaitForChild("Efekty3D"))
local Interfejs = require(moduly:WaitForChild("InterfejsWalki2"))
local Dziennik = require(moduly:WaitForChild("Dziennik"))
local Dane = require(moduly:WaitForChild("Walka"):WaitForChild("Dane"))
local PlanWalki = require(moduly:WaitForChild("PlanWalki"))
local NAZWA_PROTOTYPU = moduly.Parent.Name -- TestWalki2: zdalne pomijania są w kontenerze tego modułu

-- zdalna funkcja pomijania prototypu (D-078): "czy" (walki z lasu) i "pomin"; nil, gdy kontener jej nie ma
local function zdalnaPominiecia(): RemoteFunction?
	local z = moduly.Parent:FindFirstChild("Zdalne")
	local f = z and z:FindFirstChild("PominiecieWalki2")
	return if f and f:IsA("RemoteFunction") then f else nil
end

local Odtwarzacz = {}
local sesja = nil
local wolnaOd = 0
local zapamietaneTempo = 1
local zapamietaneWyciszenie = false -- przycisk dźwięku: wybór gracza zostaje do końca sesji gry

local function wolnaZa(): number
	return math.max(0, wolnaOd - workspace:GetServerTimeNow())
end

-- katalog dźwięków gry (Workspace/DzwiekGra, swiat/dzwiek_gra) → { kat, adres, skala } albo nil (dźwięki wbudowane)
local function katalogArkusza()
	local k = workspace:FindFirstChild("DzwiekGra")
	local m = k and k:FindFirstChild("Moduly")
	m = m and m:FindFirstChild("KatalogDzwiekow")
	if not m or not m:IsA("ModuleScript") then
		return nil
	end
	local ok, kat = pcall(require, m)
	if not ok or type(kat) ~= "table" or type(kat.arkusz) ~= "table" or type(kat.efekty) ~= "table"
		or type(kat.zdarzenia) ~= "table" then
		return nil
	end
	local id = k:GetAttribute("TestArkuszId")
	if id == nil then
		id = kat.arkusz.id
	end
	local adres = if type(id) == "number" and id > 0 then "rbxassetid://" .. tostring(math.floor(id))
		elseif type(id) == "string" and id ~= "" then id
		else nil
	if not adres then
		return nil
	end
	local skala = k:GetAttribute("TestArkuszSkala")
	return { kat = kat, adres = adres, skala = if type(skala) == "number" and skala > 0 then skala else 1 }
end

-- arena walki biomu źródła (D-095, pakiet swiat/areny_walki): Workspace/ArenyWalki/Moduly/ArenyWalki; nil = stara arena
local function modulAren(): any
	local k = workspace:FindFirstChild("ArenyWalki")
	local m = if k and k:GetAttribute("Wygenerowane") == true then k:FindFirstChild("Moduly") else nil
	m = m and m:FindFirstChild("ArenyWalki")
	if not m or not m:IsA("ModuleScript") then
		return nil
	end
	local ok, mod = pcall(require, m)
	return if ok and type(mod) == "table" and type(mod.przygotuj) == "function" then mod else nil
end

local KROK = "TestWalki2Cutscenka"
local AKCJA_BLOKADY = "TestWalki2BlokadaSterowania"
local AKCJA_POMIN = "TestWalki2Pomin"
local K = U.KOLORY
local rad = math.rad
local los = Random.new()

------------------------------------------------------------------ krzywe (jak w v1)
local function gladko(x: number): number
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end
local function wyjscie(x: number): number
	x = math.clamp(x, 0, 1)
	return 1 - (1 - x) * (1 - x)
end
local function luk(u: number, a: number, b: number): number
	if u <= a or u >= b then
		return 0
	end
	local x = (u - a) / (b - a)
	return 4 * x * (1 - x)
end
local function okno(u: number, a: number, b: number, c: number, d: number): number
	if u <= a or u >= d then
		return 0
	elseif u < b then
		return gladko((u - a) / math.max(b - a, 1e-3))
	elseif u <= c then
		return 1
	end
	return 1 - gladko((u - c) / math.max(d - c, 1e-3))
end
local function odrzut(u: number, szczyt: number, koniec: number): number
	if u <= 0 or u >= koniec then
		return 0
	elseif u < szczyt then
		return wyjscie(u / szczyt)
	end
	return 1 - gladko((u - szczyt) / (koniec - szczyt))
end
local function inna(s: string): string
	return if s == "gracz" then "wrog" else "gracz"
end

------------------------------------------------------------------ sesja
local Sesja = {}
Sesja.__index = Sesja

function Sesja:posprzataj(f: () -> ())
	table.insert(self.sprzatanie, f)
end
function Sesja:polacz(sygnal: RBXScriptSignal, f): RBXScriptConnection
	local p = sygnal:Connect(f)
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
function Sesja:nowa(klasa: string, w: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in w do
		o[k] = v
	end
	o.Parent = rodzic
	self.utworzono += 1
	return o
end

------------------------------------------------------------------ przejęcie sterowania, GUI, kamery (jak w v1)
function Sesja:zablokujSterowanie()
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
	local p = self.kontener:FindFirstChild("PodpowiedzWalki2", true)
	if p and p:IsA("ProximityPrompt") and p.Enabled then
		p.Enabled = false -- lokalnie
		self:posprzataj(function()
			if p.Parent then
				p.Enabled = true
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
		-- gdyby przed walką kamera była już skryptowa (np. po przerwanej scenie), wracamy do zwykłej kamery gry
		kamera.CameraType = if typ == Enum.CameraType.Scriptable then Enum.CameraType.Custom else typ
		local postac = self.gracz.Character
		local hum = postac and postac:FindFirstChildOfClass("Humanoid")
		kamera.CameraSubject = hum or podmiot
	end)
end

------------------------------------------------------------------ obcy w kadrze (jak w v1)
local SKAN_CO = 0.2

function Sesja:schowajObcych()
	local zapamietane: { [Instance]: { [string]: any } } = {}
	local czesci: { [BasePart]: boolean } = {}
	local modele: { [Instance]: boolean } = {}
	self.schowaneCzesci = czesci
	self.liczbaSchowanych = 0
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
		elseif d:IsA("Decal") then
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
		self:polacz(korzen.DescendantAdded, function(d)
			if not self.zakonczona then
				schowajJeden(d)
			end
		end)
	end
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
	for _, o in CollectionService:GetTagged(U.TAG_UKRYJ) do
		schowajCalosc(o)
	end
	self:polacz(CollectionService:GetInstanceAddedSignal(U.TAG_UKRYJ), schowajCalosc)
	-- obce części w pudle sceny (nasza arena, galeria, szablony i scena lokalna nie są obce)
	-- P1 (las_potwory/PROJEKT.md, rozdz. 6): arena, szablony i galeria prototypu są „nasze” także wtedy, gdy walkę
	-- uruchamia inny kontener (moduly.Parent = Workspace/TestWalki2; przy tablicy prototypu to ten sam kontener)
	local wyklucz = { self.scena }
	for _, korzen in { self.kontener, moduly.Parent } do
		for _, n in { "Arena", "Aktorzy", "Galeria" } do
			local d = korzen:FindFirstChild(n)
			if d and not table.find(wyklucz, d) then
				table.insert(wyklucz, d)
			end
		end
	end
	local plyta = workspace:FindFirstChild("Baseplate")
	if plyta then
		table.insert(wyklucz, plyta)
	end
	table.insert(wyklucz, workspace.Terrain)
	if self.arena and self.arena.model then
		table.insert(wyklucz, self.arena.model) -- arena biomu (D-095) jest „nasza”
	end
	local filtr = OverlapParams.new()
	filtr.FilterType = Enum.RaycastFilterType.Exclude
	filtr.FilterDescendantsInstances = wyklucz
	local pudlo = CFrame.new(if self.arena then self.arena.pudloSrodek else U.OBSZAR_SRODEK)
	local rozmiarPudla = if self.arena then self.arena.pudloRozmiar else U.OBSZAR_ROZMIAR
	self.skanujObcych = function()
		for _, czesc in workspace:GetPartBoundsInBox(pudlo, rozmiarPudla, filtr) do
			if not czesci[czesc] then
				schowajCalosc(korzenCzesci(czesc))
			end
		end
	end
	self.skanCzas = 0
	self.skanujObcych()
end

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

------------------------------------------------------------------ serwer
local POWODY_CICHE = { za_daleko = true, walka_trwa = true, brak_postaci = true, za_szybko = true, zly_wybor = true }

function Sesja:poprosSerwer()
	local zdalna = self.kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke2") :: RemoteFunction
	for _ = 1, 3 do
		local t = os.clock()
		-- tylko wybór z listy (napisy); żadnych liczb. Serwery lasu dostają dokładnie trzy napisy (umowa
		-- swiat/las_potwory); tablica prototypu (v3) — czwarty napis: zestaw postaci z zamkniętej listy
		local odpowiedz
		if type(self.wybor.zestaw) == "string" then
			odpowiedz = zdalna:InvokeServer({ klasa = self.wybor.klasa, przeciwnik = self.wybor.przeciwnik, poziom = self.wybor.poziom,
				zestaw = self.wybor.zestaw })
		else
			odpowiedz = zdalna:InvokeServer({ klasa = self.wybor.klasa, przeciwnik = self.wybor.przeciwnik, poziom = self.wybor.poziom })
		end
		self.czasSerwera = (os.clock() - t) * 1000
		if self.zakonczona then
			error("przerwano")
		end
		local powod = if type(odpowiedz) == "table" then odpowiedz.powod else nil
		local ponowZa = if type(odpowiedz) == "table" then tonumber(odpowiedz.ponowZa) else nil
		if type(odpowiedz) == "table" and odpowiedz.ok and odpowiedz.walka then
			-- v3: Dziennik.sprawdz to kontrola, nie bramka — zły albo nowszy dziennik daje ostrzeżenie, a odtwarzacz
			-- gra kopię znormalizowaną przez PlanWalki (nieznane pola i typy nie wywracają odtwarzania)
			local dobre, opis = Dziennik.sprawdz(odpowiedz.walka)
			self.bladDziennika = if dobre then nil else tostring(opis)
			if not dobre then
				warn("[TestWalki2] Dziennik nie przeszedł Dziennik.sprawdz (gram dalej): " .. tostring(opis))
			end
			local walka, ostrzezenia = PlanWalki.normalizuj(odpowiedz.walka)
			if not walka then
				error("serwer przysłał dziennik, którego nie da się odtworzyć: " .. tostring(ostrzezenia))
			end
			self.ostrzezeniaDziennika = ostrzezenia
			for _, o in ostrzezenia do
				warn("[TestWalki2] Dziennik: " .. o)
			end
			wolnaOd = tonumber(odpowiedz.nastepnaOd) or 0
			self:atrybut("NastepnaWalkaOd", wolnaOd)
			-- D-078: zgoda na pomijanie od serwera (true / false); nil = serwer źródła o tym nie mówi (walka z lasu) —
			-- wtedy pytamy serwer prototypu (rozpocznij), a do odpowiedzi pomijać nie wolno
			self.pomijanie = if odpowiedz.pomijanie == true then true elseif odpowiedz.pomijanie == false then false else nil
			-- pasywki stron z serwera (tylko do zapowiedzi; liczby i tak są w dzienniku)
			self.pasywkiStron = if type(odpowiedz.pasywki) == "table" then odpowiedz.pasywki else nil
			return walka
		elseif (powod == "za_szybko" or powod == "walka_trwa") and ponowZa and ponowZa <= 3 then
			task.wait(math.clamp(ponowZa, 0.1, 3) + 0.05)
			if self.zakonczona then
				error("przerwano")
			end
		elseif powod and POWODY_CICHE[powod] then
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

------------------------------------------------------------------ scena
-- arena biomu (D-095): scena walki staje na arenie biomu źródła walki; bez kontenera ArenyWalki, bez areny dla źródła
-- albo przy błędzie — stara arena (U.scena()), jak dotąd. Nastrój i detale sprząta moduł (uchwyt:zakoncz) z sesją.
function Sesja:wybierzArene()
	self.arena = nil
	local A = modulAren()
	local powod = "brak_modulu"
	if A then
		local ok, uchwyt, p = pcall(A.przygotuj, { zrodlo = self.kontener.Name, kontener = self.kontener, folder = self.scena })
		if ok and type(uchwyt) == "table" and typeof(uchwyt.scena) == "CFrame" then
			self.arena = uchwyt
			self:posprzataj(function()
				pcall(uchwyt.zakoncz, uchwyt)
			end)
			powod = "ok"
		elseif ok then
			powod = tostring(p or "brak")
		else
			powod = "blad"
			warn("[TestWalki2] Arena biomu — zostaje stara arena: " .. tostring(uchwyt))
		end
	end
	self:atrybut("OstatniaArena", if self.arena then self.arena.nazwa else "stara")
	self:atrybut("OstatniaArenaPowod", powod)
end

function Sesja:przygotujScene()
	self.scena = self:nowa("Folder", { Name = "ScenaLokalna" }, self.kontener)
	self:posprzataj(function()
		self.scena:Destroy()
	end)
	-- szablony aktorów w galerii chowamy tylko u tego klienta
	local szablony = moduly.Parent:FindFirstChild("Aktorzy") -- P1: szablony zawsze z kontenera modułu (TestWalki2)
	local schowane = {}
	if szablony then
		for _, d in szablony:GetDescendants() do
			if d:IsA("BasePart") then
				d.LocalTransparencyModifier = 1
				table.insert(schowane, d)
			end
		end
	end
	self:posprzataj(function()
		for _, d in schowane do
			d.LocalTransparencyModifier = 0
		end
	end)
	self:wybierzArene()
	self:schowajObcych()
	-- dźwięki: po dwa (nuty po cztery) obiekty Sound na nazwę — wbudowane w klienta (rbxasset://), bez uploadu
	self.dzwieki = {}
	if U.DZWIEKI_WLACZONE then
		for nazwa, def in U.DZWIEKI do
			local pula = {}
			for i = 1, (if nazwa == "nuta" then 4 else 2) do
				table.insert(pula, self:nowa("Sound", { Name = nazwa .. i, SoundId = def.id, Volume = 0 }, self.ui.gui))
			end
			self.dzwieki[nazwa] = pula
		end
	end
	self.statDzwiekow = { zagrane = 0, pominiete = 0, maksNaraz = 0 }
	-- arkusz własnych dźwięków (Workspace/DzwiekGra): pula Sound z jednym plikiem, odcinki przez PlaybackRegion
	self.arkusz = nil
	local ark = U.DZWIEKI_WLACZONE and katalogArkusza()
	if ark then
		ark.pula = {}
		ark.nastepny = 1
		ark.log = {}
		ark.regiony = true
		for i = 1, math.clamp(ark.kat.arkusz.naraz or 6, 1, 12) do
			local s = self:nowa("Sound", { Name = "Arkusz" .. i, SoundId = ark.adres, Volume = 0 }, self.ui.gui)
			local ok = pcall(function()
				s.PlaybackRegionsEnabled = true
			end)
			ark.regiony = ark.regiony and ok
			table.insert(ark.pula, s)
		end
		self.arkusz = ark
	end
	self:atrybut("OstatniZestawDzwiekow", if self.arkusz then "arkusz" else "wbudowany")
end

------------------------------------------------------------------ odcinki arkusza (własne dźwięki, swiat/dzwiek_gra)
--[[ Arkusz do grania: tylko gdy plik się wczytał. Niewczytany (gra nie ma jeszcze prawa do zasobu, moderacja, brak
	sieci) = nil, czyli dźwięki wbudowane — walka nie może być przez to cicha. Sprawdzane przy każdym dźwięku, więc
	arkusz wchodzi sam, gdy tylko się wczyta. ]]
function Sesja:arkuszDoGrania()
	local ark = self.arkusz
	local s = ark and ark.pula[1]
	if s and s.IsLoaded and s.TimeLength > 0 then
		return ark
	end
	if ark then
		ark.niewczytane = (ark.niewczytane or 0) + 1
	end
	return nil
end

--[[ Odcinek efektu z arkusza od miejsca `od` (s od początku odcinka, czas katalogu). info = { nr = zdarzenie } do
	pomiaru zgodności szczytu z trafieniem. Zwraca true, gdy efekt jest w katalogu (zagrany albo świadomie cicho). ]]
function Sesja:grajOdcinek(efekt: string, od: number?, info: any?): boolean
	local ark = self:arkuszDoGrania()
	local e = ark and ark.kat.efekty[efekt]
	if not e then
		return false
	end
	if zapamietaneWyciszenie or self.zakonczona or (self.pominieto and efekt ~= (ark.kat.zdarzenia.przycisk or {}).efekt) then
		return true
	end
	local k = ark.skala
	local o = math.max(0, od or 0)
	local p0, p1 = (e.poczatek + o) * k, e.koniec * k
	if p1 - p0 < 0.02 then
		return true
	end
	-- wolny dźwięk z puli; gdy wszystkie grają — najstarszy (kolejno)
	local s = nil
	for _, kand in ark.pula do
		if not kand.IsPlaying then
			s = kand
			break
		end
	end
	if not s then
		s = ark.pula[ark.nastepny]
		ark.nastepny = (ark.nastepny % #ark.pula) + 1
		self.statDzwiekow.pominiete += 1
	end
	s:Stop()
	s.PlaybackSpeed = 1
	s.Volume = (e.glosnosc or 1) * (ark.kat.arkusz.glosnosc or 1)
	if ark.regiony then
		local ok = pcall(function()
			s.PlaybackRegion = NumberRange.new(p0, p1)
		end)
		ark.regiony = ok
	end
	s.TimePosition = p0
	s:Play()
	-- zabezpieczenie (i jedyny koniec, gdy PlaybackRegion nie działa): stop po długości odcinka
	local nr = (s:GetAttribute("Nr") or 0) + 1
	s:SetAttribute("Nr", nr)
	task.delay(p1 - p0 + 0.05, function()
		if s.Parent and s:GetAttribute("Nr") == nr and s.IsPlaying then
			s:Stop()
		end
	end)
	self.statDzwiekow.zagrane += 1
	if #ark.log < 60 then
		local teraz = os.clock()
		table.insert(ark.log, { e = efekt, od = math.floor(o * 1000 + 0.5) / 1000, p0 = math.floor(p0 * 1000 + 0.5) / 1000,
			p1 = math.floor(p1 * 1000 + 0.5) / 1000, t = teraz, szczyt = teraz + math.max(0, e.szczyt - o) * k,
			nr = info and info.nr, tau = self.tau })
	end
	return true
end

-- zdarzenie dźwięku: odcinek z katalogu, gdy jest; inaczej wbudowany dźwięk `wbudowany` (dzisiejszy zestaw)
function Sesja:dzwiekZdarzenia(zdarzenie: string, wbudowany: string?, szybkosc: number?)
	local ark = self:arkuszDoGrania()
	local w = ark and ark.kat.zdarzenia[zdarzenie]
	if w and self:grajOdcinek(w.efekt, 0) then
		return
	end
	if wbudowany then
		self:dzwiek(wbudowany, szybkosc)
	end
end

-- jak dzwiekZdarzenia, ale bez wbudowanego zastępstwa: true = odcinek z katalogu (wtedy pomijamy melodię z tonu)
function Sesja:odcinekZdarzenia(zdarzenie: string): boolean
	local ark = self:arkuszDoGrania()
	local w = ark and ark.kat.zdarzenia[zdarzenie]
	return w ~= nil and self:grajOdcinek(w.efekt, 0)
end

-- zdarzenie uderzenia z katalogu dla ataku (szczyt efektu na klatkę trafienia) albo nil
function Sesja:zdarzenieUderzenia(ev): string?
	local ark = self:arkuszDoGrania()
	if not ark then
		return nil
	end
	local z = ev.z
	local kand
	if z.typ == "unik" then
		kand = "unik"
	elseif z.typ == "blok" then
		kand = "blok"
	elseif z.umiejetnosc == "kula_ognia" or z.umiejetnosc == "lodowy_pocisk" then
		kand = z.umiejetnosc
	elseif ev.choreo and ev.choreo.wybuch == "kwas" then
		kand = "galareta"
	elseif z.krytyk then
		kand = "krytyk"
	elseif ev.styl == "wrecz" or ev.styl == "skok" or ev.styl == "w_klipie" or ev.styl == "korzenie" then
		kand = "cios"
	end
	local w = kand and ark.kat.zdarzenia[kand]
	if w and w.uderzenie and ark.kat.efekty[w.efekt] then
		return kand
	end
	return nil
end

--[[ Dźwięk uderzenia z arkusza: start w chwili sceny, od której do trafienia zostaje `szczyt` sekund RZECZYWISTYCH
	(przy bieżącym tempie gracza i zwolnieniach — Sesja:tempoSceny); gdy zdarzenie zaczyna się za późno, odcinek gra od
	razu z pominiętym wstępem, ale najwyżej do chwili tuż przed atakiem efektu (wtedy szczyt wypada trochę po trafieniu). ]]
function Sesja:zaplanujUderzenie(ev, zdarzenie: string)
	local ark = self.arkusz
	local w = ark.kat.zdarzenia[zdarzenie]
	local e = ark.kat.efekty[w.efekt]
	local k = ark.skala
	local szczyt = e.szczyt * k
	local tHit = ev.t + ev.eHit
	local tau, real = tHit, 0
	local krok = 1 / 120
	while tau > ev.t + 1e-6 and real < szczyt do
		local t1 = math.max(ev.t, tau - krok)
		real += (tau - t1) / math.max(self:tempoSceny(t1), 0.05)
		tau = t1
	end
	local od = 0
	if real < szczyt then
		od = math.min(szczyt - real, math.max(0, e.atak * k - 0.03)) / k
	end
	ev.dzwiekArkusza = zdarzenie
	self:zaplanujAkcje(tau, function()
		self:grajOdcinek(w.efekt, od, { nr = ev.nr })
	end)
end

-- odgłos potwora (galareta, wilk, troll, zarodniki, ryk strażnika) z katalogu: przy jego umiejętności i w radości
function Sesja:glosPotwora(strona: string, inny: string?)
	local ark = self.arkusz
	local a = self.aktorzy and self.aktorzy[strona]
	local zd = ark and a and ark.kat.glosyPotworow and ark.kat.glosyPotworow[a.klucz]
	if zd and zd ~= inny then
		self:odcinekZdarzenia(zd)
	end
end

-- ile dźwięków walki gra teraz
function Sesja:grajaceDzwieki(): number
	local n = 0
	for _, pula in self.dzwieki or {} do
		for _, s in pula do
			if s.IsPlaying then
				n += 1
			end
		end
	end
	return n
end

--[[ Dźwięk z U.DZWIEKI. Przy szybkim tempie dźwięki się nie zlewają: ta sama nazwa najwyżej co 0,06 / 0,1 / 0,16 s
	(×1 / ×2 / ×4), a naraz gra najwyżej U.DZWIEKI_NARAZ (reszta jest pomijana i liczona). wymus = melodia finału. ]]
function Sesja:dzwiek(nazwa: string, szybkosc: number?, wymus: boolean?)
	local pula = self.dzwieki and self.dzwieki[nazwa]
	local def = U.DZWIEKI[nazwa]
	if not pula or not def or (self.pominieto and nazwa ~= "przycisk") or zapamietaneWyciszenie or self.zakonczona then
		return
	end
	local st = self.statDzwiekow
	local teraz = os.clock()
	self.ostatniDzwiek = self.ostatniDzwiek or {}
	local odstep = if self.tempo >= 4 then 0.16 elseif self.tempo >= 2 then 0.1 else 0.06
	local graja = self:grajaceDzwieki()
	if not wymus and ((self.ostatniDzwiek[nazwa] or -1) > teraz - odstep or graja >= U.DZWIEKI_NARAZ) then
		st.pominiete += 1
		return
	end
	if wymus and graja >= U.DZWIEKI_NARAZ then
		-- melodia finału: zwalnia miejsce, zatrzymując jeden z grających dźwięków (limit naraz zostaje)
		for n, inna in self.dzwieki do
			if n ~= "nuta" then
				for _, s2 in inna do
					if s2.IsPlaying and graja >= U.DZWIEKI_NARAZ then
						s2:Stop()
						graja -= 1
					end
				end
			end
		end
	end
	local s = nil
	for _, kand in pula do
		if not kand.IsPlaying then
			s = kand
			break
		end
	end
	s = s or pula[1]
	self.ostatniDzwiek[nazwa] = teraz
	s.PlaybackSpeed = (szybkosc or 1) * def.szybkosc * (1 + 0.06 * (math.min(self.tempo, 4) - 1))
	s.Volume = def.glosnosc * U.GLOSNOSC
	s.TimePosition = 0
	s:Play()
	st.zagrane += 1
	st.maksNaraz = math.max(st.maksNaraz, graja + 1)
	if def.maks then
		local nr = (s:GetAttribute("Nr") or 0) + 1
		s:SetAttribute("Nr", nr)
		task.delay(def.maks / math.max(s.PlaybackSpeed, 0.1), function()
			if s.Parent and s:GetAttribute("Nr") == nr then
				s:Stop()
			end
		end)
	end
end

-- melodia finału (cztery nuty z wbudowanego tonu), w czasie rzeczywistym
function Sesja:melodia(nazwa: string)
	local m = U.MELODIE and U.MELODIE[nazwa]
	if not m then
		return
	end
	for i, nuta in m.nuty do
		task.delay((i - 1) * m.odstep, function()
			if not self.zakonczona and not self.pominieto then
				self:dzwiek("nuta", nuta, true)
			end
		end)
	end
end

function Sesja:przelaczDzwiek()
	zapamietaneWyciszenie = not zapamietaneWyciszenie
	if zapamietaneWyciszenie then
		for _, pula in self.dzwieki or {} do
			for _, s in pula do
				s:Stop()
			end
		end
		for _, s in (self.arkusz and self.arkusz.pula) or {} do
			s:Stop()
		end
	else
		self:dzwiekZdarzenia("przycisk", "przycisk")
	end
	self.ui:ustawDzwiek(zapamietaneWyciszenie)
	self:atrybut("OstatnieWyciszenie", zapamietaneWyciszenie)
end

-- punkt sceny (x, y, z) → świat
function Sesja:swiat(v: Vector3): Vector3
	return self.cfSceny:PointToWorldSpace(v)
end

function Sesja:usunAktorow()
	if self.aktorzy then
		for _, a in self.aktorzy do
			pcall(function()
				a:zniszcz()
			end)
		end
	end
	self.aktorzy = nil
	if self.fx then
		self.fx:wyczysc()
	end
end

--[[ Geometria walki z wymiarów aktorów (wpis.przod, zasięg broni w chwili trafienia, głębokość piersi):
	S = odstęp punktów stania; gracz stoi w x = −S/2 (patrzy w +X), przeciwnik w x = +S/2. ]]
function Sesja:ustawAktorow(walka)
	self:usunAktorow()
	self.fx = Efekty3D.nowe(self.scena, U)
	local kG, kW = walka.strony.gracz.id, walka.strony.wrog.id
	local wG, wW = Aktorzy.wpis(kG), Aktorzy.wpis(kW)
	if not wG or not wW then
		error("brak aktora dla " .. tostring(kG) .. " / " .. tostring(kW))
	end
	local S = math.max(9.5, wG.przod + wW.przod + 3.2)
	self.cfSceny = if self.arena then self.arena.scena else U.scena() -- arena biomu (D-095) albo stara arena
	local geo = { S = S, x = { gracz = -S / 2, wrog = S / 2 }, kier = { gracz = 1, wrog = -1 },
		h = { gracz = wG.wysokosc, wrog = wW.wysokosc },
		w = { gracz = math.max(wG.szerokosc, wG.glebokosc * 0.6), wrog = math.max(wW.szerokosc, wW.glebokosc * 0.6) } }
	geo.H = math.max(wG.wysokosc, wW.wysokosc)
	-- plan ogólny: obie postacie w kadrze 16:9 przy kącie 40°
	local polSzer = S / 2 + math.max(wG.przod, wW.przod) * 0.8 + 2.2
	-- (u góry kadru są tabliczki z paskami, więc wysokość liczymy z zapasem)
	geo.dist = math.max(polSzer / (math.tan(rad(20)) * 16 / 9), (geo.H * 0.72 + 1.8) / math.tan(rad(20)), 12)
	self.geo = geo
	self.aktorzy = {}
	for strona, klucz in { gracz = kG, wrog = kW } do
		local a = Aktorzy.nowy(klucz, self:cfDomu(strona), { rodzic = self.scena, reczny = true, obrys = self.opcje.obrys, bezSpoczynku = true })
		a.strona = strona
		a:graj("spoczynek", { przejscie = 0, petla = true, odCzasu = if strona == "wrog" then 0.9 else 0 })
		self.utworzono += a.liczbaInstancji
		self.aktorzy[strona] = a
	end
end

function Sesja:cfDomu(strona: string): CFrame
	local x = self.geo.x[strona]
	return self.cfSceny * CFrame.lookAt(Vector3.new(x, 0, 0), Vector3.new(x + self.geo.kier[strona], 0, 0))
end

-- odległość punktów stania przy ciosie wręcz: broń (zasięg klipu w chwili trafienia) sięga piersi celu
function Sesja:odlegloscCiosu(atakujacy, broniacy, akcja: string): number
	local wa, wb = atakujacy.wpis, broniacy.wpis
	local klip = atakujacy:maKlip(akcja) or atakujacy:maKlip("atak")
	local zasieg = (wa.zasiegi and klip and wa.zasiegi[klip]) or wa.przod
	-- celowanie (etap 9): atakujący obrócony o kąt obrotCiosu sięga bronią dalej wzdłuż osi (przód / cos(kąt))
	local obrot = wa.obrotCiosu and klip and wa.obrotCiosu[klip]
	if obrot then
		zasieg /= math.cos(obrot)
	end
	-- przód tułowia: pierś albo ok. ¼ głębokości bryły (brzuch Trolla wystaje dalej niż punkt piersi)
	local piersB = math.max(0.5, wb.piersPrzod or 0.6, (wb.glebokosc or 0) * 0.28)
	local piersA = math.max(0.5, wa.piersPrzod or 0.6, (wa.glebokosc or 0) * 0.22)
	local d = zasieg + piersB - 0.15
	return math.max(d, piersA + piersB + 0.5)
end

-- czy klip akcji sam przesuwa całą postać (wpis.ruchWKlipie z aktorzy.py „ruch_w_klipie”: odskok w uniku, odepchnięcie
-- na tarczy, wypad przy czarze, wyskok, tupnięcie) — wtedy odtwarzacz nie dokłada swojego ślizgu, odrzutu ani podskoku
-- (etap 8: własne klipy Wojownika i Maga; doskok do celu i odrzut po trafieniu zostają)
local function ruchWKlipie(aktor, akcja: string?): boolean
	local r = aktor and aktor.wpis.ruchWKlipie
	local k = r and akcja and aktor:maKlip(akcja)
	return k ~= nil and r[k] == true
end

------------------------------------------------------------------ plan: zdarzenia, tury, efekty, ujęcia, zwolnienia
local ATAKI = { cios = true, krytyk = true, blok = true, unik = true }

function Sesja:wpisChoreo(z, klucz: string)
	if z.umiejetnosc ~= "" then
		local w = Ch.UMIEJETNOSCI[z.umiejetnosc]
		if w then
			return w, true
		end
		self.brakiChoreo += 1
		local du = Dane.umiejetnosci[z.umiejetnosc]
		if du and du.cel == "sam" then
			return Ch.ZASTEPCZY.sam, false
		end
		return (if z.rodzaj == "magiczne" then Ch.ZASTEPCZY.magiczne else Ch.ZASTEPCZY.fizyczne), false
	end
	return Ch.ATAK[klucz] or Ch.ZWYKLY_CIOS, true
end

function Sesja:zaplanuj(walka)
	local plan = {}
	local n = #walka.dziennik
	local zwolnienia = {}
	local ujecia = { { start = 0, typ = "ogolny", prio = 3 } }
	local losU = Random.new(walka.ziarno % 2147483647)
	local ostatnieTyp = "ogolny"
	local licznikZwyklych = 0
	-- v3: tury, mana, powalenia przed wskrzeszeniem i cios kończący liczy czysty moduł PlanWalki (testy bez Studio)
	local pw = PlanWalki.plan(walka)
	self.planWalki = pw
	local nrKonczacego = pw.nrKonczacego
	for i, z in walka.dziennik do
		local pe = pw.zdarzenia[i]
		local ev = { nr = i, z = z, typ = z.typ, kto = z.kto, cel = z.cel, t = z.t, trwa = z.trwa, koniec = z.t + z.trwa, pw = pe }
		ev.nowaTura = pe.nowaTura
		ev.tura = pe.tura
		ev.stronaTury = pe.stronaTury
		ev.obsluga = if z.nieznany then Ch.NIEZNANE else Ch.ZDARZENIA[z.typ]
		ev.smiertelny = pe.smiertelny == true
		ev.powala = pe.powala -- strona powalona tym zdarzeniem, która zaraz wstaje (wskrzeszenie)
		ev.atak = ATAKI[z.typ] or (z.typ == "umiejetnosc" and z.kto ~= z.cel)
		ev.naSiebie = z.typ == "umiejetnosc" and z.kto == z.cel
		if ev.atak or ev.naSiebie then
			local klucz = self.aktorzy[z.kto].klucz
			ev.choreo, ev.znana = self:wpisChoreo(z, klucz)
			ev.styl = if ev.naSiebie then "na_siebie" else (ev.choreo.styl or "wrecz")
			self:policzCzasy(ev)
			local zw = if z.krytyk == true then Ch.ZWOLNIENIE.krytyk
				elseif ev.smiertelny then Ch.ZWOLNIENIE.nokaut
				elseif ev.powala then Ch.ZWOLNIENIE.powalenie
				else nil
			if zw then
				-- atak z lotem: zwolnienie dopiero przy dolocie (inaczej pocisk „stał” przed celem przez ponad sekundę)
				local zLot = (ev.lot or 0) > 0 and Ch.ZWOLNIENIE.lot or nil
				local przed = if zLot then zLot.przed else zw.przed
				table.insert(zwolnienia, { od = ev.t + ev.eHit - przed, ["do"] = ev.t + ev.eHit + zw.po, tempo = zw.tempo,
					rampa = zLot and zLot.rampa or nil })
			end
		elseif z.typ == "efekt_tick" then
			ev.eHit = 0.18
		elseif z.typ == "utrata_tury" then
			ev.eHit = 0.2
		end
		-- ujęcie
		local uj = nil
		local A, D = z.kto, z.cel
		if ev.atak then
			if (z.krytyk or ev.smiertelny or ev.powala) and ev.styl ~= "pocisk" and ev.styl ~= "chmura" then
				uj = { typ = "krytyk", atakujacy = A, broniacy = D, prio = 3 }
			elseif ev.styl == "pocisk" or ev.styl == "chmura" then
				uj = { typ = ev.choreo.kamera or "pocisk", atakujacy = A, broniacy = D, strona = ev.choreo.stronaKamery or 1,
					prio = if z.krytyk or ev.smiertelny then 3 elseif z.umiejetnosc ~= "" then 2 else 1 }
			elseif z.umiejetnosc ~= "" then
				local typ = ev.choreo.kamera
				if ev.styl == "skok" then
					typ = "boczny" -- wyskok nad celem: tylko z boku widać cały łuk (zza pleców wychodził ponad kadr)
				end
				if not typ then
					local pula = { "zaAtakujacym", "zaBroniacym", "boczny" }
					typ = pula[losU:NextInteger(1, #pula)]
					if typ == ostatnieTyp then
						typ = pula[(table.find(pula, typ) % #pula) + 1]
					end
				end
				uj = { typ = typ, atakujacy = A, broniacy = D, prio = 2 }
			else
				licznikZwyklych += 1
				local typ
				if licznikZwyklych % 5 == 1 then
					typ = "ogolny"
				else
					local pula = { "boczny", "zaAtakujacym", "zaBroniacym", "zblizenie", "ogolny" }
					typ = pula[losU:NextInteger(1, #pula)]
					if typ == ostatnieTyp then
						typ = pula[(table.find(pula, typ) % #pula) + 1]
					end
				end
				uj = { typ = typ, atakujacy = A, broniacy = D, prio = 1 }
			end
		elseif ev.naSiebie then
			uj = { typ = "naSiebie", atakujacy = A, broniacy = A, prio = 2 }
		elseif z.typ == "utrata_tury" then
			uj = { typ = "efekt", atakujacy = A, broniacy = A, prio = 1 }
		elseif z.typ == "efekt_tick" and (ev.nowaTura or ev.powala) then
			uj = { typ = "efekt", atakujacy = A, broniacy = A, prio = if ev.smiertelny or ev.powala then 3 else 1 }
		elseif z.typ == "wskrzeszenie" then
			-- wskrzeszenie: ujęcie na wstającego (mocne, krótkie — przerywa każde inne)
			uj = { typ = "efekt", atakujacy = A, broniacy = A, prio = 3 }
		end
		if uj then
			uj.start = ev.t + (if ev.atak then math.max(0, (ev.eStart or 0) - 0.05) else 0)
			uj.ev = ev
			uj.nr = i
			ev.ujecie = uj
			ostatnieTyp = uj.typ
		end
		plan[i] = ev
	end
	local ostatni = plan[n]
	self.tKoniecDziennika = ostatni.koniec
	--[[ Finał (wybór odtwarzacza, nie silnika — cały dziennik jest już odegrany): po ciosie kończącym krótkie ujęcie
		POKONANEGO, w którym kończy się jego klip upadku (kałuża z oczkami, stos głazów, leżący troll albo bohater), dopiero
		potem radość zwycięzcy, objazd, baner, łup i panel wyniku. Od chwili tuż przed ciosem kończącym finał gra zawsze
		w tempie ×1 (przy ×2/×4 ujęcie pokonanego trwałoby ułamek sekundy). Klip upadku dłuższy niż 1,9 s (Strażnik
		2,7 s) gra szybciej, żeby skończył się w ujęciu. ]]
	self.tPokonany = nil
	self.predkoscUpadku = 1
	self.tempoFinaluOd = math.huge
	local konczacy = nrKonczacego and plan[nrKonczacego]
	local P = self.aktorzy[self.pokonany]
	if konczacy and P then
		local tHit = konczacy.t + (konczacy.eHit or 0.2)
		local klip = P:maKlip("upadek")
		local dl = (klip and P.klipy:dlugoscKlipu(klip)) or 1.2
		self.predkoscUpadku = math.max(1, dl / 1.9)
		local koniecUpadku = tHit + dl / self.predkoscUpadku
		self.tPokonany = tHit + 0.38
		self.tRadosc = math.max(math.clamp(koniecUpadku + 0.3, self.tPokonany + 1.1, self.tPokonany + 1.8), ostatni.koniec + 0.05)
		self.tempoFinaluOd = tHit - 0.25
	else
		self.tRadosc = ostatni.koniec + 0.05
	end
	self.tObjazdu = self.tRadosc
	-- koniec sceny: tyle po radości, ile silnik przewidział na finał po ostatnim zdarzeniu (≥ czas dziennika)
	self.czasKonca = math.max(walka.czas, self.tRadosc + math.max(0.8, walka.czas - ostatni.koniec - 0.05))
	self.plan = plan
	self.zwolnienia = zwolnienia
	self.ujeciaPlan = ujecia
end

local UNIK_PRZED_SZEROKIM = 2.5 -- studs: o tyle krótszy doskok szerokiego atakującego (i dalsze zejście celu) przy uniku
-- finał: zwycięzca obraca się do kamery objazdu przez `czas` s, zaczynając `przed` s przed radością (w końcówce ujęcia
-- pokonanego), więc przy cięciu do objazdu stoi już twarzą do kamery (kąt twarzy ≤ 35°). Obrót zaczynany razem
-- z radością zostawiał przez 0,1–0,3 s objazdu twarz bokiem do kamery i broń przed nią (miecz Wojownika w gotowości:
-- oczy 100%, sztylet Zwiadowcy: 60–77%; pomiar swiat/postacie/przenikanie, 17.11.2026). Test:
-- testy/test_przenikania.py (Kamera) czyta te liczby stąd.
local OBROT_ZWYCIEZCY = { przed = 0.45, czas = 0.45 }

-- chwila klipu (s), w której punkt Bron schodzi z góry do wysokości wierzchu celu `wys` — z toru broni z tabeli aktorów
-- (8 klatek przed chwilą trafienia); gdy broń w chwili trafienia jest jeszcze nad celem albo przez cały tor w jego
-- wysokości (wysoki cel), zostaje chwila z modułu. Najwyżej 0,2 s klipu wcześniej.
function Sesja.chwilaKontaktu(wpis, klip: string, chw: number, wys: number): number
	local tor = wpis.torBroni and wpis.torBroni[klip]
	if not tor or type(tor.y) ~= "table" or #tor.y < 2 then
		return chw
	end
	local ys, n = tor.y, #tor.y
	if ys[n] >= wys then
		return chw
	end
	for i = n - 1, 1, -1 do
		if ys[i] >= wys then
			local u = (ys[i] - wys) / math.max(ys[i] - ys[i + 1], 1e-3)
			local t = (tor.od + (i - 1) + u) / tor.fps
			return math.max(t, chw - 0.2)
		end
	end
	return chw
end

-- czasy ataku / umiejętności w zdarzeniu (sekundy od jego początku, w czasie sceny)
local LOT_MIN, LOT_MAKS = 0.45, 0.7 -- s czasu sceny: lot pocisku (i bańki z klipu) ma być widać
function Sesja:policzCzasy(ev)
	local z = ev.z
	local A, D = self.aktorzy[z.kto], self.aktorzy[z.cel]
	local trwa = ev.trwa
	local udzial = Ch.TRAFIENIE[z.typ] or Ch.TRAFIENIE.umiejetnosc
	local eHit = trwa * udzial
	local akcja = if z.umiejetnosc ~= "" then z.umiejetnosc elseif z.typ == "krytyk" then "krytyk" else "atak"
	if not A:maKlip(akcja) then
		akcja = "atak"
	end
	ev.akcja = akcja
	local klip = A:maKlip(akcja)
	local dl = (klip and A.klipy:dlugoscKlipu(klip)) or 1
	local chw = A:chwila(akcja) or dl * 0.5
	local styl = ev.styl
	-- cios wręcz w NISKI cel (17.11.2026): chwila trafienia z modułu to broń przy ziemi, a niski cel (wilk, slime)
	-- broń mija wcześniej — trafienie (błysk, liczba, reakcja) w chwili, gdy broń schodzi do wierzchu celu
	if styl == "wrecz" and klip then
		ev.chwilaKlipu = chw
		chw = Sesja.chwilaKontaktu(A.wpis, klip, chw, D.wpis.wysokosc)
	end
	local lot = 0
	local wyrownanie = eHit
	if styl == "pocisk" then
		-- lot ma być czytelny (poprawka D2): 0,45–0,7 s czasu sceny, obrażenia w chwili, gdy pocisk dolatuje
		local pr = ev.choreo.predkosc or 20
		lot = math.clamp(self.geo.S / pr, LOT_MIN, LOT_MAKS)
		if eHit - lot < 0.3 then
			eHit = math.min(trwa - 0.3, 0.3 + lot)
		end
		wyrownanie = eHit - lot
	elseif styl == "chmura" then
		lot = 0.5
		if eHit - lot < 0.35 then
			eHit = math.min(trwa - 0.25, 0.35 + lot)
		end
		wyrownanie = eHit - lot
	elseif styl == "korzenie" then
		lot = 0.35
		wyrownanie = math.max(0.25, eHit - lot)
	elseif styl == "na_siebie" then
		wyrownanie = math.min(trwa * 0.4, 0.6)
	end
	local predkosc = 1
	if chw > wyrownanie then
		predkosc = chw / math.max(wyrownanie, 0.05)
	end
	predkosc = math.clamp(predkosc, 0.75, 2.6)
	local eStart = math.max(0, wyrownanie - chw / predkosc)
	ev.eHit = eHit
	ev.eRel = wyrownanie
	ev.lot = lot
	ev.predkosc = predkosc
	ev.eStart = eStart
	ev.dlKlipu = dl / predkosc
	-- wręcz: doskok do odległości ciosu
	if styl == "wrecz" or styl == "skok" then
		local d = self:odlegloscCiosu(A, D, akcja)
		ev.doskok = math.max(0, self.geo.S - d)
		-- celowanie: obrót na czas doskoku (+ = w lewo), żeby broń z boku osi spadła na cel (miażdżący cios Rycerza)
		ev.obrot = (A.wpis.obrotCiosu and klip and A.wpis.obrotCiosu[klip]) or 0
		ev.tDoskoku = math.clamp(eHit - 0.04 - eStart * 0.3, 0.22, 0.42)
		if styl == "skok" then
			ev.tDoskoku = math.clamp(eHit * 0.75, 0.35, 0.8)
		end
		ev.tPowrotu = math.clamp(trwa - eHit - 0.3, 0.2, 0.5)
		-- unik przed szeroką bronią (17.11.2026, Studio: maczuga Trolla przez 2–3 klatki przechodziła przez Wojownika mimo
		-- odskoku z klipu i zejścia 0,9 w tył): atakujący dużo szerszy od celu kończy doskok wcześniej, a resztę dystansu
		-- (gdy doskoku jest mniej) robi unikający, schodząc dalej w tył — broń opada przed nim
		if z.typ == "unik" and A.wpis.szerokosc >= 2 * D.wpis.szerokosc then
			local skrot = math.min(ev.doskok, UNIK_PRZED_SZEROKIM)
			ev.doskok -= skrot
			ev.zejscieUniku = UNIK_PRZED_SZEROKIM - skrot
		end
	else
		ev.doskok = 0
	end
	-- efekt w klipie (bańka i kałuża slime'a, korzenie strażnika): atakujący stoi, a kości efektu sięgają do celu —
	-- klip trafia na odległość wpis.zasiegi[klip], cel stoi w S (celPrzod: efekt ma trafić w przód celu, nie w środek)
	if styl == "w_klipie" then
		local wa = A.wpis
		local zasieg = (wa.zasiegi and klip and wa.zasiegi[klip]) or wa.przod
		local cel = self.geo.S
		if ev.choreo.celPrzod then
			local wb = D.wpis
			cel -= math.max(0.5, wb.piersPrzod or 0.6, (wb.glebokosc or 0) * 0.28) - 0.15
		end
		ev.wydluz = math.max(0, cel - zasieg)
		ev.zasiegEfektu = zasieg + ev.wydluz -- gdzie przed atakującym ląduje efekt (kałuża) w chwili trafienia
		-- cel trzymany przez efekt (korzenie) do chwili, gdy klip go puszcza (sekundy klipu po trafieniu przy prędkości 1)
		ev.trzymaDo = (ev.choreo.puszcza or 0) / predkosc
		--[[ Lot efektu z klipu (bańka kwasu, poprawka D2): w klipie bańka leci 10 klatek (0,33 s) — przy ok. 7 studach
			wydłużenia to za szybko, żeby ją zobaczyć. Klip gra trzema prędkościami: do wypuszczenia szybciej, lot wolniej
			(LOT_MIN–LOT_MAKS s czasu sceny), po trafieniu ×1 (kałuża stoi tyle, ile w modelu). Bańka nadal dolatuje
			dokładnie w chwili trafienia z dziennika (eHit). ]]
		local c = ev.choreo
		if c.lot and klip then
			local a, b = c.lot.od, chw
			local L = math.clamp(c.lot.czas or 0.55, LOT_MIN, LOT_MAKS)
			local pMaks = 2.6
			if wyrownanie - L < a / pMaks then
				L = math.max(0.25, wyrownanie - a / pMaks)
			end
			local p1 = math.clamp(a / math.max(wyrownanie - L, 0.05), 0.75, pMaks)
			local p2 = (b - a) / L
			ev.predkosc = p1
			ev.eStart = math.max(0, wyrownanie - (a / p1 + L))
			ev.odcinki = { { od = a, ["do"] = b, predkosc = p2 }, { od = b, ["do"] = 1e6, predkosc = 1 } }
			ev.lot = L
			ev.tWypuszczenia = ev.eStart + a / p1
			ev.dlKlipu = ev.tWypuszczenia + L + (dl - b)
			ev.trzymaDo = (c.puszcza or 0)
		end
	end
end

------------------------------------------------------------------ harmonogram (akcje w czasie sceny)
function Sesja:zaplanujAkcje(tAbs: number, f: (number) -> ())
	local h = self.harmonogram
	local i = #h
	while i > 0 and h[i].t > tAbs do
		i -= 1
	end
	table.insert(h, i + 1, { t = tAbs, f = f })
end

function Sesja:wykonajHarmonogram(tau: number)
	local h = self.harmonogram
	while #h > 0 and h[1].t <= tau do
		local a = table.remove(h, 1)
		local ok, blad = pcall(a.f, tau - a.t)
		if not ok then
			self.bledyObslugi += 1
			warn("[TestWalki2] Akcja choreografii: " .. tostring(blad))
		end
	end
end

-- klip aktora zsynchronizowany z czasem sceny (spóźnienie = ile sceny minęło od zaplanowanej chwili)
function Sesja:klip(aktor, akcja: string, opcje, spoznienie: number?)
	opcje = opcje or {}
	local predk = opcje.predkosc or 1
	opcje.odCzasu = (opcje.odCzasu or 0) + (spoznienie or 0) * predk
	if opcje.potem == nil and akcja ~= "upadek" and akcja ~= "radosc" and akcja ~= "spoczynek" then
		opcje.potem = aktor:maKlip("spoczynek")
	end
	if opcje.przejscie == nil then
		opcje.przejscie = 0.12
	end
	return aktor:graj(akcja, opcje)
end

------------------------------------------------------------------ efekty i stan stron (ikony z licznikiem tur)
-- ikony efektów strony: licznik tur, a znaczek wg Choreografie.EFEKTY[id].znaczek — „×N” (stosy > 1), „−N%” (tarcza)
function Sesja:efektyStrony(strona: string)
	local lista = {}
	for _, e in PlanWalki.lista(self.stanEfektow, strona) do
		local ch = Ch.EFEKTY[e.id] or Ch.EFEKT_ZASTEPCZY
		local znaczek = nil
		if ch.znaczek == "stosy" and (e.stosy or 1) > 1 then
			znaczek = "×" .. tostring(e.stosy)
		elseif ch.znaczek == "procent" and e.procent then
			znaczek = "−" .. tostring(math.floor(e.procent + 0.5)) .. "%"
		end
		table.insert(lista, { id = e.id, ikona = ch.ikona, kolor = ch.kolor, tury = e.tury, znaczek = znaczek, stosy = e.stosy })
	end
	return lista
end

function Sesja:odswiezEfekty()
	for strona in self.stanEfektow do
		self.ui:ustawEfekty(strona, self:efektyStrony(strona))
	end
end

-- czy na stronie trwa efekt danego typu z danych silnika (np. "spowolnienie" — kolor paska many)
function Sesja:maEfektTypu(strona: string, typ: string): boolean
	for _, e in self.stanEfektow[strona] do
		local def = Dane.efekty[e.id]
		if def and def.typ == typ then
			return true
		end
	end
	return false
end

function Sesja:koniecTury(strona: string, tura: number)
	PlanWalki.koniecTury(self.stanEfektow, strona, tura)
end

-- umiejętność, która nałożyła efekt (z planu: efekt_nalozony idzie zaraz po swoim ataku); "" = zwykły cios
function Sesja:zrodloEfektu(ev): string
	return (ev.pw and ev.pw.zrodlo) or ""
end

--[[ Mana z dziennika na paskach (v3): wartości po zdarzeniu ev (mana_gracz / mana_wrog), próg i gotowość z planu.
	strony = "obie" | strona; uzycie = błysk przy spadku o koszt. Klient niczego nie dolicza. ]]
function Sesja:ustawManeZdarzenia(ev, strony: string?, uzycie: boolean?)
	local pe = ev.pw
	for _, s in { "gracz", "wrog" } do
		if strony == nil or strony == "obie" or strony == s then
			self.ui:ustawMane(s, ev.z["mana_" .. s], {
				prog = pe and pe.prog[s], gotowa = pe and pe.gotowa[s], uzycie = uzycie and ev.z.kto == s,
				spowolniona = self:maEfektTypu(s, "spowolnienie"), natychmiast = self.pominieto,
			})
		end
	end
end

-- wygląd ozdoby efektu: ten sam efekt może wyglądać inaczej zależnie od umiejętności, która go nałożyła
-- (ogłuszenie: pnącza przy uścisku korzeni, gwiazdki przy ogłuszającym uderzeniu; spowolnienie: lód) —
-- Choreografie.WYGLAD_OD_UMIEJETNOSCI
function Sesja.wygladEfektu(id: string, umiejetnosc: string?): string
	local ch = Ch.EFEKTY[id] or Ch.EFEKT_ZASTEPCZY
	local wg = Ch.WYGLAD_OD_UMIEJETNOSCI[id]
	if wg and umiejetnosc and wg[umiejetnosc] then
		return wg[umiejetnosc]
	end
	return ch.wyglad
end

function Sesja:ozdobaEfektu(strona: string, id: string, umiejetnosc: string?)
	local klucz = strona .. ":" .. id
	local o = self.ozdoby[klucz]
	local wyglad = Sesja.wygladEfektu(id, umiejetnosc)
	if o and not o.zniszczona then
		if o.wyglad == wyglad then
			o:puls()
			return o
		end
		o:zniszcz() -- ten sam efekt odświeżony inną umiejętnością: nowy wygląd
	end
	if not Ch.EFEKTY[id] then
		self.brakiChoreo += 1
	end
	o = self.fx:wyglad(wyglad, self.aktorzy[strona])
	o.wyglad = wyglad
	self.ozdoby[klucz] = o
	return o
end

function Sesja:usunOzdobe(strona: string, id: string)
	local klucz = strona .. ":" .. id
	local o = self.ozdoby[klucz]
	if o then
		o:zniszcz()
		self.ozdoby[klucz] = nil
	end
end

function Sesja:usunOzdobyStrony(strona: string)
	for klucz, o in self.ozdoby do
		if string.sub(klucz, 1, #strona + 1) == strona .. ":" then
			o:zniszcz()
			self.ozdoby[klucz] = nil
		end
	end
end

------------------------------------------------------------------ napisy i trafienia
function Sesja:glowa(strona: string): Vector3
	local a = self.aktorzy[strona]
	return (a:cfZiemi() * CFrame.new(0, a.wpis.wysokosc * 0.9 + 0.4, 0)).Position
end

function Sesja:piers(strona: string): Vector3
	local a = self.aktorzy[strona]
	local p = a:punkt("Piers")
	return if p then p.Position else (a:cfZiemi() * CFrame.new(0, a.wpis.wysokosc * 0.55, 0)).Position
end

-- pierwszy punkt bryły aktora na odcinku od → do (części klonów mają CanQuery = false: na czas promienia włączamy je
-- lokalnie i przywracamy); nil = promień nie trafia w aktora
function Sesja:powierzchnia(strona: string, od: Vector3, do_: Vector3): Vector3?
	local a = self.aktorzy[strona]
	if not a then
		return nil
	end
	local zmienione = {}
	for _, c in a.model:GetDescendants() do
		if c:IsA("BasePart") and c ~= a.hrp and not c.CanQuery and c.Transparency < 0.9 then
			c.CanQuery = true
			table.insert(zmienione, c)
		end
	end
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { a.model }
	local kier = do_ - od
	local traf = workspace:Raycast(od, kier + kier.Unit * 0.5, params)
	for _, c in zmienione do
		c.CanQuery = false
	end
	return traf and traf.Position or nil
end

function Sesja:liczba(z, strona: string): (string, string, Color3?)
	local tekst = "−" .. tostring(z.obrazenia)
	if z.rodzaj == "magiczne" then
		return tekst, "magiczne", nil
	end
	return tekst, if strona == "gracz" then "otrzymane" else "zadane", nil
end

-- czy pokazać liczbę obrażeń nad celem: nie, gdy całe trafienie wzięła tarcza (wtedy „TARCZA −n”, a nie „−0")
function Sesja.pokazLiczbe(z): boolean
	return z.obrazenia > 0 or (z.pochloniete or 0) == 0
end

-- skutek trafienia (cios, krytyk, blok, unik, umiejętność na przeciwnika): paski, napisy, iskry, reakcja celu
function Sesja:skutekAtaku(ev, cicho: boolean)
	local z = ev.z
	self.ui:ustawZycie("gracz", z.hp_gracz, cicho)
	self.ui:ustawZycie("wrog", z.hp_wrog, cicho)
	self:ustawManeZdarzenia(ev, "obie", false)
	self:odswiezEfekty()
	if cicho then
		return
	end
	self.pomiarTwarzy = ev.nr
	if ev.dzwiekArkusza and self.arkusz then
		self.arkusz.trafienia = self.arkusz.trafienia or {}
		self.arkusz.trafienia[ev.nr] = os.clock()
	end
	local wbud = ev.dzwiekArkusza == nil -- uderzenie gra odcinek arkusza (zaplanowany wcześniej) — bez wbudowanego
	local D = self.aktorzy[z.cel]
	local glowa = self:glowa(z.cel)
	local piers = self:piers(z.cel)
	local s = math.clamp(D.wpis.wysokosc / 5.5, 0.8, 1.8)
	local magia = z.rodzaj == "magiczne"
	local kolorLiczby = if magia then Color3.fromHex(Ch.KOLOR_OBRAZEN.magiczne) else nil
	-- całość na tarczy (kamienna skóra, bariera): zamiast „−0” tylko napis „TARCZA −n” niżej — w każdej gałęzi
	local liczbaWidoczna = Sesja.pokazLiczbe(z)
	local cel = z.cel
	if z.typ == "unik" then
		self.ui:napis(glowa, "UNIK!", "unik", nil, los:NextNumber(-7, 7), nil, cel)
		if wbud then
			self:dzwiek("unik", los:NextNumber(0.95, 1.05))
		end
	elseif z.typ == "blok" then
		-- v3: blok zmniejsza cios (przechodzi czesc_przez_blok) — „BLOK −75%” i liczba tego, co przeszło
		local zatrzymal = PlanWalki.blokZatrzymuje(self.walka)
		self.ui:napis(glowa, if zatrzymal >= 100 then "BLOK!" else ("BLOK −" .. tostring(zatrzymal) .. "%"), "blok", nil, -5, nil, cel)
		if liczbaWidoczna then
			local t, st = self:liczba(z, z.cel)
			self.ui:napis(glowa, t, st, nil, 4, nil, cel)
		end
		-- z tarczą (klip bloku i punkt Tarcza — Wojownik): iskry przy godle; bez tarczy: parada bronią albo ręką —
		-- łuk odbicia przed punktem Bron (albo przed piersią) zwrócony do atakującego, iskry w tym samym miejscu
		local tarcza = D:maKlip("blok") and D:punkt("Tarcza")
		if tarcza then
			self.fx:wybuch("blok", tarcza.Position, s)
		else
			local bron = D:punkt("Bron")
			local miejsce = if bron then bron.Position:Lerp(piers, 0.35) else piers
			local doAtak = self:piers(z.kto) - miejsce
			local kier = if doAtak.Magnitude > 0.01 then doAtak.Unit else D:cfZiemi().LookVector
			local punkt = miejsce + kier * math.max(0.6, D.wpis.przod * 0.5)
			self.fx:parada(punkt, kier, Color3.fromHex(Ch.BLOK.kolor), s)
			self.fx:wybuch("blok", punkt, s)
			ev.parada = true
		end
		if wbud then
			self:dzwiek("blok", los:NextNumber(0.95, 1.05))
		end
		self:wstrzas(0.15)
	elseif z.krytyk then
		self.ui:napis(glowa, "KRYTYK!", "krytyk", nil, -6, nil, cel)
		if liczbaWidoczna then
			self.ui:napis(glowa, "−" .. tostring(z.obrazenia), "krytykLiczba", nil, 4, kolorLiczby, cel)
		end
		self.fx:wybuch("krytyk", piers, s)
		if wbud then
			self:dzwiek("krytyk", 1.0)
		end
		self:wstrzas(0.6)
	else
		if liczbaWidoczna then
			local t, st = self:liczba(z, z.cel)
			self.ui:napis(glowa, t, st, nil, los:NextNumber(-8, 8), nil, cel)
		end
		-- pocisk i efekt w klipie mają własny rozbłysk w miejscu trafienia (Choreo) — tu bez drugiego na piersi
		if not (ev.styl == "w_klipie" and ev.choreo.wybuch) then
			self.fx:wybuch(if ev.choreo and ev.choreo.wybuch and ev.styl ~= "pocisk" then ev.choreo.wybuch else "cios", piers, s)
		end
		local c = ev.choreo
		if not wbud then
			-- odcinek arkusza już gra (szczyt na tę klatkę)
		elseif c and c.wybuch == "kwas" then
			self:dzwiek("plusk", los:NextNumber(0.95, 1.05))
		elseif ev.styl == "pocisk" or ev.styl == "chmura" then
			self:dzwiek("wybuch", los:NextNumber(0.9, 1.1))
		else
			self:dzwiek("cios", los:NextNumber(0.9, 1.1))
		end
		self:wstrzas(math.max(0.22, ev.choreo and ev.choreo.wstrzas or 0.24))
	end
	if z.pochloniete > 0 then
		self.ui:napis(glowa, "TARCZA −" .. tostring(z.pochloniete), "efekt", nil, 3, Color3.fromHex("#9FE8FF"), cel)
		self.fx:wybuch("tarcza", piers, s)
	end
	-- dodatki umiejętności
	local c = ev.choreo
	if c and z.typ ~= "unik" and z.typ ~= "blok" then
		if c.fala then
			self.fx:fala(D:cfZiemi().Position + Vector3.new(0, 0.15, 0), Color3.fromHex(c.fala), math.max(3, D.wpis.wysokosc * 0.7))
		end
		if c.pazury then
			local cf = CFrame.lookAt(piers, self:piers(z.kto))
			self.fx:pazury(cf * CFrame.new(0, 0, -0.6), Color3.fromHex(c.pazury), math.max(1.4, D.wpis.wysokosc * 0.35))
		end
	end
	-- reakcja celu
	if ev.smiertelny then
		self:upadek(z.cel)
	elseif ev.powala == z.cel then
		self:upadek(z.cel, true)
	elseif z.typ == "blok" then
		-- klip bloku gra od wcześniej (garda przed ciosem); bez klipu — parada w aktualizujPozy (odchylenie)
	elseif z.typ ~= "unik" then
		self:klip(D, "trafienie", { predkosc = if z.krytyk then 0.9 else 1.15 })
	end
end

--[[ Upadek: pokonanego (cios albo tyknięcie kończące) w prędkości dobranej do ujęcia pokonanego; powalonego, który
	zaraz wstanie (wskrzeszenie, v3) — szybciej (klip kończy się przed światłem), bez zdejmowania ozdób efektów
	(efekty trwają po powrocie, np. trucizna tyka dalej). ]]
function Sesja:upadek(strona: string, powala: boolean?)
	local P = self.aktorzy[strona]
	if powala then
		local klip = P:maKlip("upadek")
		local dl = (klip and P.klipy:dlugoscKlipu(klip)) or 1
		self:klip(P, "upadek", { przejscie = 0.08, predkosc = math.max(1, dl / 0.85) })
		self:dzwiek("upadek", if strona == "gracz" then 1.0 else 0.75)
		return
	end
	self.torUpadku = self:klip(P, "upadek", { przejscie = 0.08, predkosc = self.predkoscUpadku or 1 })
	self:usunOzdobyStrony(strona)
	self:dzwiek("upadek", if strona == "gracz" then 1.0 else 0.75)
	self:dzwiek("lomot", 1.0)
end

function Sesja:wstrzas(sila: number)
	self.wstrzasKam.sila = math.max(self.wstrzasKam.sila * math.exp(-self.wstrzasKam.wiek * 9), sila)
	self.wstrzasKam.wiek = 0
end

------------------------------------------------------------------ choreografie stylów (atak i umiejętność)
local Choreo = {}

-- wspólne dla ataków: klip atakującego, reakcja broniącego przed trafieniem (unik, blok), trafienie w chwili eHit
local function zaplanujAtak(self, ev, f_wypuszczenie)
	local z = ev.z
	local A, D = self.aktorzy[z.kto], self.aktorzy[z.cel]
	local t0 = ev.t
	-- własne dźwięki (arkusz): uderzenie ze szczytem na trafieniu; potwór przy umiejętności daje głos (gdy jego
	-- odgłos nie jest już dźwiękiem tej umiejętności — galareta przy kwaśnym plusku, zarodniki przy chmurze)
	if self.arkusz then
		local zd = self:zdarzenieUderzenia(ev)
		if zd then
			self:zaplanujUderzenie(ev, zd)
		end
		if z.kto == "wrog" and z.umiejetnosc ~= "" then
			self:zaplanujAkcje(t0 + (ev.eStart or 0), function()
				self:glosPotwora("wrog", zd or (if ev.styl == "chmura" then "zarodniki" else nil))
			end)
		end
	end
	self:zaplanujAkcje(t0 + ev.eStart, function(sp)
		self:klip(A, ev.akcja, { predkosc = ev.predkosc, wydluz = ev.wydluz, odcinki = ev.odcinki }, sp)
	end)
	if ev.choreo and ev.choreo.smuga or z.krytyk then
		local kolor = Color3.fromHex(if type(ev.choreo.smuga) == "string" then ev.choreo.smuga else "#FFF3B0")
		self:zaplanujAkcje(t0 + math.max(ev.eStart, ev.eHit - 0.35), function()
			self.fx:smuga(A, kolor, 0.5)
		end)
	end
	if f_wypuszczenie then
		self:zaplanujAkcje(t0 + ev.eRel, function(sp)
			f_wypuszczenie(sp)
		end)
	end
	if z.typ == "unik" then
		local dl = (D:maKlip("unik") and D.klipy:dlugoscKlipu(D:maKlip("unik"))) or 0.8
		local pr = 1.2
		-- największy odskok w chwili trafienia: chwila uniku z tabeli (Wojownik, Mag), inaczej 40% klipu
		local szczyt = D:chwila("unik") or dl * 0.4
		self:zaplanujAkcje(t0 + math.max(0, ev.eHit - szczyt / pr), function(sp)
			self:klip(D, "unik", { predkosc = pr }, sp)
		end)
	elseif z.typ == "blok" then
		if D:maKlip("blok") then
			-- cios w tarczę klipu (rycerz.CHWILE: kl. 11 = 0,367 s) w chwili trafienia
			self:zaplanujAkcje(t0 + math.max(0, ev.eHit - (D:chwila("blok") or 0.38)), function(sp)
				self:klip(D, "blok", { predkosc = 1 }, sp)
			end)
		end
	end
	self:zaplanujAkcje(t0 + ev.eHit, function()
		self:skutekAtaku(ev, false)
	end)
end

Choreo.wrecz = function(self, ev)
	zaplanujAtak(self, ev, nil)
end

Choreo.skok = function(self, ev)
	zaplanujAtak(self, ev, nil)
	local D = self.aktorzy[ev.z.cel]
	if ev.choreo.fala then
		self:zaplanujAkcje(ev.t + ev.eHit, function()
			self.fx:fala(D:cfZiemi().Position + Vector3.new(0, 0.15, 0), Color3.fromHex(ev.choreo.fala), 4)
		end)
	end
end

Choreo.pocisk = function(self, ev)
	local z = ev.z
	local A, D = self.aktorzy[z.kto], self.aktorzy[z.cel]
	zaplanujAtak(self, ev, function(sp)
		local od = A:punkt("Pocisk")
		local start = if od then od.Position else self:piers(z.kto)
		local c = ev.choreo
		local nazwa = c.pocisk or "iskra"
		--[[ Lot kończy się na PRZEDNIEJ powierzchni celu (przegląd 15.11): punkt Piers leży w środku bryły, więc przy
			Trollu strzała wchodziła w jego ciało i znikała na 1,4 s przed trafieniem. Powierzchnia = promień od wylotu do
			piersi przecięty z bryłami celu; pocisk ustawia się tak, żeby grot (strzała) albo przód kuli dotykał tej
			powierzchni w chwili trafienia, a strzała zostaje wbita na czas reakcji celu. ]]
		local piers = self:piers(z.cel)
		local pow = self:powierzchnia(z.cel, start, piers) or piers
		-- ile przed środkiem pocisku jest jego przód (grot strzały 2,1 studa; Efekty3D liczy z tego koniec lotu)
		local przod = if nazwa == "strzala" then 2.1 elseif nazwa == "lod" then 0.85 else 0.35
		ev.punktTrafienia = pow
		self.fx:pocisk(nazwa, start, pow, math.max(0.05, ev.lot - sp), {
			luk = c.luk, chybiony = z.typ == "unik", grot = przod,
			zostaw = if nazwa == "strzala" and z.typ ~= "unik" then 0.75 else nil,
			przyczep = function()
				return D:cfZiemi()
			end,
		})
		if c.wybuch and z.typ ~= "unik" then
			self:zaplanujAkcje(ev.t + ev.eHit, function()
				local s = math.clamp(D.wpis.wysokosc / 5.5, 0.8, 1.8)
				self.fx:wybuch(c.wybuch, pow:Lerp(self:piers(z.cel), 0.3), s)
			end)
		end
		if c.pocisk == "strzala" then
			self:dzwiek("strzal", 1.0)
		elseif not ev.dzwiekArkusza then
			self:dzwiekZdarzenia("rzut", "czar", 1.0) -- kula ognia i lodowy pocisk: wystrzał jest we własnym odcinku
		end
	end)
end

Choreo.chmura = function(self, ev)
	local z = ev.z
	local A = self.aktorzy[z.kto]
	zaplanujAtak(self, ev, function(sp)
		local od = A:punkt("Pocisk")
		local start = if od then od.Position else self:piers(z.kto)
		local cel = self:piers(z.cel)
		self.fx:chmura(start, cel, math.max(0.05, ev.lot - sp), Color3.fromHex(ev.choreo.kolor or "#B07CFF"))
		self:odcinekZdarzenia("zarodniki")
	end)
	if ev.choreo.wybuch and z.typ ~= "unik" then
		self:zaplanujAkcje(ev.t + ev.eHit, function()
			self.fx:wybuch(ev.choreo.wybuch, self:piers(z.cel), 1)
		end)
	end
end

Choreo.korzenie = function(self, ev)
	local z = ev.z
	local D = self.aktorzy[z.cel]
	zaplanujAtak(self, ev, function(sp)
		local w = D.wpis
		local r = math.max(1.4, math.max(w.szerokosc, w.glebokosc) * 0.42)
		self.fx:korzenie(D:cfZiemi(), r, Color3.fromHex(ev.choreo.kolor or "#5A3A22"), math.max(0.05, ev.lot - sp),
			ev.trwa - ev.eRel + 0.2, math.max(2.2, w.wysokosc * 0.75))
		self:wstrzas(0.2)
	end)
end

-- efekt jest w klipie aktora (bańka i kałuża Leśnego Slime'a, korzenie Strażnika Gaju): bez osobnego pocisku i bez
-- korzeni z Efekty3D; klip gra z wydłużeniem (ev.wydluz), a rozbłysk — w punkcie efektu (np. kałuża) w chwili trafienia
Choreo.w_klipie = function(self, ev)
	local z = ev.z
	local A, D = self.aktorzy[z.kto], self.aktorzy[z.cel]
	zaplanujAtak(self, ev, nil)
	local c = ev.choreo
	-- lot efektu z klipu (bańka): smuga za kością i świst przy wypuszczeniu
	if c.lot and ev.tWypuszczenia then
		self:zaplanujAkcje(ev.t + ev.tWypuszczenia, function()
			local kosc = A.model:FindFirstChild(c.lot.kosc or "Kula")
			if kosc and kosc:IsA("BasePart") then
				self.fx:smugaCzesci(kosc, Color3.fromHex(c.lot.kolor or "#B8F55A"), ev.lot + 0.05, c.lot.szer or 0.45)
			end
			self:dzwiek("strzal", 0.8)
		end)
	end
	if c.wybuch and z.typ ~= "unik" then
		self:zaplanujAkcje(ev.t + ev.eHit, function()
			-- miejsce liczone, nie czytane z punktu: WorldCFrame punktu jest o klatkę za Transform, a kałuża w klipie
			-- przeskakuje ze schowka przed slime'a w jednej klatce (kl. 30 → 31) — rozprysk wypadał przy atakującym
			local s = math.clamp(D.wpis.wysokosc / 5.5, 0.8, 1.8)
			local cf = A:cfZiemi()
			local p = if ev.zasiegEfektu then cf.Position + cf.LookVector * ev.zasiegEfektu + Vector3.new(0, 0.3, 0)
				else self:piers(z.cel)
			self.fx:wybuch(c.wybuch, p, s * (c.skalaWybuchu or 1))
			-- kałuża kwasu przy celu: płaski dysk na ziemi tak długo, jak stoi kałuża w klipie (po trafieniu klip gra ×1)
			if c.kaluza and ev.zasiegEfektu then
				local ziemia = cf.Position + cf.LookVector * ev.zasiegEfektu
				local dlugo = math.max(0.4, (c.kaluza.koniec or 2.17) - (A:chwila(ev.akcja) or 1))
				self.fx:kaluza(ziemia, c.kaluza.promien or 2, Color3.fromHex(c.kaluza.kolor or "#9BF04A"), dlugo)
				self.fx:fala(ziemia + Vector3.new(0, 0.12, 0), Color3.fromHex(c.kaluza.kolor or "#9BF04A"), (c.kaluza.promien or 2) * 1.6)
			end
		end)
	end
end

Choreo.na_siebie = function(self, ev)
	local z = ev.z
	local A = self.aktorzy[z.kto]
	self:zaplanujAkcje(ev.t + ev.eStart, function(sp)
		self:klip(A, ev.akcja, { predkosc = ev.predkosc }, sp)
	end)
	self:zaplanujAkcje(ev.t + ev.eRel, function()
		local s = math.clamp(A.wpis.wysokosc / 5, 0.8, 2)
		self.fx:wybuch(ev.choreo.aura or "blask", self:piers(z.kto), s)
		self:dzwiekZdarzenia(if z.umiejetnosc == "bariera" then "tarcza" else "rzut", "czar", 1.0)
	end)
end
Sesja.Choreo = Choreo

------------------------------------------------------------------ obsługa zdarzeń (wg Choreografie.ZDARZENIA)
local Obsluga = {}

Obsluga.atak = function(self, ev)
	local f = Choreo[ev.styl] or Choreo.wrecz
	f(self, ev)
	if ev.z.umiejetnosc ~= "" then
		self:pokazNazwe(ev)
	end
end

Obsluga.umiejetnosc = function(self, ev)
	local f = Choreo[ev.styl] or (if ev.naSiebie then Choreo.na_siebie else Choreo.wrecz)
	f(self, ev)
	self:pokazNazwe(ev)
end

Obsluga.tykniecie = function(self, ev)
	local z = ev.z
	local A = self.aktorzy[z.kto]
	local ch = Ch.EFEKTY[z.efekt] or Ch.EFEKT_ZASTEPCZY
	self:zaplanujAkcje(ev.t + ev.eHit, function()
		self.ui:ustawZycie("gracz", z.hp_gracz)
		self.ui:ustawZycie("wrog", z.hp_wrog)
		PlanWalki.tykniecie(self.stanEfektow, z)
		self:ustawManeZdarzenia(ev, "obie", false)
		self:odswiezEfekty()
		if self.pominieto then
			return
		end
		local glowa = self:glowa(z.kto)
		if z.kto == "wrog" then
			self.pomiarTwarzy = ev.nr
		end
		if z.obrazenia > 0 then
			-- trucizna w stosach: „−24 ×3” (tyknięcie ze wszystkimi stosami, liczba stosów z dziennika)
			local tekst = "−" .. tostring(z.obrazenia)
			if ch.znaczek == "stosy" and z.stosy > 1 then
				tekst = tekst .. " ×" .. tostring(z.stosy)
			end
			self.ui:napis(glowa, tekst, "tyk", nil, los:NextNumber(-6, 6), Color3.fromHex(ch.kolor), z.kto)
		end
		if z.pochloniete > 0 then
			self.ui:napis(glowa, "TARCZA −" .. tostring(z.pochloniete), "efekt", nil, 3, Color3.fromHex("#9FE8FF"), z.kto)
		end
		local o = self.ozdoby[z.kto .. ":" .. z.efekt]
		if o then
			o:puls()
		end
		if ev.smiertelny then
			self:upadek(z.kto)
		elseif ev.powala == z.kto then
			self:upadek(z.kto, true)
		else
			self:klip(A, "trafienie", { predkosc = 1.5 })
			self:dzwiekZdarzenia(if z.efekt == "trucizna" then "tik_trucizna" elseif z.efekt == "podpalenie" then "tik_podpalenie"
				else "", "cios", 1.3)
		end
	end)
end

Obsluga.nalozenie = function(self, ev)
	local z = ev.z
	local nowy = PlanWalki.nalozony(self.stanEfektow, z, ev.tura, Dane.efekty)
	self:ustawManeZdarzenia(ev, "obie", false)
	self:odswiezEfekty()
	if self.pominieto then
		return
	end
	self:ozdobaEfektu(z.cel, z.efekt, self:zrodloEfektu(ev))
	local ch = Ch.EFEKTY[z.efekt] or Ch.EFEKT_ZASTEPCZY
	local tekst = ch.napis
	if nowy.procent then
		-- tarcza procentowa (v3): „KAMIENNA SKÓRA −42%” (procent z dziennika), 3 tury na ikonie
		tekst = string.sub(tekst, 1, #tekst - 1) .. " −" .. tostring(math.floor(nowy.procent + 0.5)) .. "%"
	elseif ch.znaczek == "stosy" and nowy.stosy > 1 then
		tekst = string.sub(tekst, 1, #tekst - 1) .. " ×" .. tostring(nowy.stosy)
	end
	self.ui:napis(self:glowa(z.cel), tekst, "efekt", nil, los:NextNumber(-4, 4), Color3.fromHex(ch.kolor), z.cel)
	if z.efekt == "ogluszenie" then
		self:odcinekZdarzenia("ogluszenie")
	end
end

Obsluga.koniec = function(self, ev)
	local z = ev.z
	PlanWalki.koniec(self.stanEfektow, z)
	self:ustawManeZdarzenia(ev, "obie", false)
	self:odswiezEfekty()
	self:usunOzdobe(z.cel, z.efekt)
	-- koniec efektu: znika ikona i ozdoba na postaci; bez napisu (w długiej walce napisów byłoby za dużo). Tarcza v3
	-- jest procentowa na 3 tury — nie „pęka”, tylko się kończy.
end

-- utrata tury (v3: tylko ogłuszenie — spowolnienie tury nie zabiera): „TRACI TURĘ!”, puls gwiazdek / pnączy
Obsluga.utrata = function(self, ev)
	local z = ev.z
	self:ustawManeZdarzenia(ev, "obie", false)
	self:zaplanujAkcje(ev.t + 0.12, function()
		if self.pominieto then
			return
		end
		self.ui:napis(self:glowa(z.kto), "TRACI TURĘ!", "efekt", nil, -5, Color3.fromHex("#FFE14A"), z.kto)
		for id in Ch.TRACI_TURE do
			local o = self.ozdoby[z.kto .. ":" .. id]
			if o then
				o:puls()
			end
		end
		self:dzwiek("unik", 0.7)
	end)
end

--[[ Wskrzeszenie (v3, propozycja D-094): mocna, krótka scena w czasie zdarzenia z dziennika (trwa 1,5 s):
	światło z góry na powalonego → wstaje (klip upadku wstecz, potem spoczynek; lekkie uniesienie) → pasek życia
	rośnie z 0 do życia po powrocie (wartosc = hp z dziennika) ze złotym blaskiem → „WSKRZESZENIE!”. Legenda przy
	portrecie szarzeje (raz na walkę). Efekty na postaci zostają (ozdoby nie zniknęły przy powaleniu). ]]
Obsluga.wskrzeszenie = function(self, ev)
	local z = ev.z
	local A = self.aktorzy[z.kto]
	local w = Ch.WSKRZESZENIE
	self:ustawManeZdarzenia(ev, "obie", false)
	self.wskrzeszenia[z.kto] = (self.wskrzeszenia[z.kto] or 0) + 1
	self:zaplanujAkcje(ev.t + ev.trwa * w.swiatlo, function()
		if self.pominieto then
			return
		end
		local s = math.clamp(A.wpis.wysokosc / 5, 0.8, 2.2)
		self.fx:wskrzeszenie(A:cfZiemi(), math.max(A.wpis.szerokosc, A.wpis.glebokosc), A.wpis.wysokosc, Color3.fromHex(w.kolor), ev.trwa)
		self.fx:wybuch("zloto", self:piers(z.kto), s)
		self:dzwiek("czar", 0.85)
	end)
	-- wstaje: klip upadku odegrany WSTECZ od bieżącej chwili do klatki 0 (w.wstaje → w.stoi; te same pozy co przy
	-- padaniu — kostur wraca do łapy po swoim torze), potem 0,15 s do spoczynku. Dawne przejście 0,45 s z leżenia
	-- do spoczynku mieszało kości po kolei i przeciągało kostur Maga przez głowę (0,21 studa), a jelec miecza
	-- Wojownika przez biodra (0,17; pomiar swiat/postacie/przenikanie, 17.11.2026). Bez klipu upadku, gdy upadek nie
	-- jest bieżącym klipem albo po pominięciu — jak dawniej.
	local wstecz = false
	self:zaplanujAkcje(ev.t + ev.trwa * w.wstaje, function(sp)
		local klipUpadku = A:maKlip("upadek")
		local tor = A.klipy:biezacy()
		local czas = ev.trwa * (w.stoi - w.wstaje)
		if not self.pominieto and klipUpadku and tor and tor.nazwa == klipUpadku and tor.czas > 0 and czas > 0 then
			wstecz = true
			self:klip(A, "upadek", { przejscie = 0, odCzasu = tor.czas, predkosc = -tor.czas / czas }, sp)
		else
			self:klip(A, "spoczynek", { przejscie = 0.45, petla = true }, sp)
		end
	end)
	self:zaplanujAkcje(ev.t + ev.trwa * w.stoi, function(sp)
		if wstecz then
			self:klip(A, "spoczynek", { przejscie = 0.15, petla = true }, sp)
		end
	end)
	self:zaplanujAkcje(ev.t + ev.trwa * w.zycie, function()
		self.ui:ustawZycie(z.kto, if z.kto == "gracz" then z.hp_gracz else z.hp_wrog)
		self.ui:ustawLegende(z.kto, self.legendy[z.kto] == true, true)
		if self.pominieto then
			return
		end
		self.ui:blaskZycia(z.kto)
		if not self:odcinekZdarzenia("awans") then -- arkusz: wznoszący się pasaż „awansu” zamiast melodii z tonu
			self:melodia("wskrzeszenie")
		end
	end)
	self:zaplanujAkcje(ev.t + ev.trwa * w.napis, function()
		if self.pominieto then
			return
		end
		self.ui:napis(self:glowa(z.kto), "WSKRZESZENIE!", "wskrzeszenie", nil, -4, nil, z.kto)
		self.ui:napis(self:glowa(z.kto), "+" .. tostring(z.wartosc), "zadane", nil, 4, Color3.fromHex(w.kolor), z.kto)
		self:wstrzas(0.3)
	end)
end

-- zdarzenie, którego odtwarzacz nie zna (nowszy silnik): ostrzeżenie (już przy normalizacji), paski i mana
-- z dziennika, żadnej animacji — walka gra dalej
Obsluga.nieznane = function(self, ev)
	local z = ev.z
	self.nieznane += 1
	self.ui:ustawZycie("gracz", z.hp_gracz)
	self.ui:ustawZycie("wrog", z.hp_wrog)
	self:ustawManeZdarzenia(ev, "obie", false)
end
Sesja.Obsluga = Obsluga

function Sesja:pokazNazwe(ev)
	local z = ev.z
	local du = Dane.umiejetnosci[z.umiejetnosc]
	local nazwa = (du and du.nazwa) or z.umiejetnosc
	self.ui:pokazUmiejetnosc(nazwa, z.kto)
	self.licznikNazw += 1
	local token = self.licznikNazw
	self:zaplanujAkcje(ev.koniec + 0.3, function()
		if self.licznikNazw == token then
			self.ui:ukryjUmiejetnosc()
		end
	end)
end

------------------------------------------------------------------ start jednego zdarzenia
function Sesja:startZdarzenia(ev)
	local z = ev.z
	-- kontrola: paski zgadzają się z poprzednim zdarzeniem dziennika
	local poprz = self.plan[ev.nr - 1]
	if poprz and not self.pominieto then
		if self.ui:zycie("gracz") ~= poprz.z.hp_gracz or self.ui:zycie("wrog") ~= poprz.z.hp_wrog then
			self.niezgodnosciPaskow += 1
			self.ui:ustawZycie("gracz", poprz.z.hp_gracz)
			self.ui:ustawZycie("wrog", poprz.z.hp_wrog)
		end
		-- v3: mana na paskach = mana z poprzedniego zdarzenia (licznik do testów, w testach zawsze 0)
		if self.ui:mana("gracz") ~= poprz.z.mana_gracz or self.ui:mana("wrog") ~= poprz.z.mana_wrog then
			self.niezgodnosciMany += 1
			self:ustawManeZdarzenia(poprz, "obie", false)
		end
	end
	if ev.nowaTura then
		if self.turaStrona then
			self:koniecTury(self.turaStrona, self.turaNr)
		end
		self.turaStrona, self.turaNr = ev.stronaTury, ev.tura
		self.ui:ustawTure(ev.tura)
		self:odswiezEfekty()
	end
	-- mana: użycie umiejętności = błysk i spadek o koszt w chwili rzucenia (początek zdarzenia); reszta zmian many
	-- przychodzi z trafieniem (skutekAtaku, tykniecie) albo w obsłudze zdarzenia bez trafienia
	if ev.pw then
		if ev.atak or ev.z.typ == "efekt_tick" then
			if ev.pw.uzycie then
				self:ustawManeZdarzenia(ev, ev.z.kto, true)
			end
		else
			-- bez trafienia (umiejętność na siebie, nałożenie, koniec, utrata tury, wskrzeszenie): obie strony od razu
			self:ustawManeZdarzenia(ev, "obie", ev.pw.uzycie)
		end
		if ev.pw.uzycie then
			self.uzyciaMany += 1
		end
	end
	self.biezace = ev.nr
	local f = Obsluga[ev.obsluga]
	if not f then
		self.brakiChoreo += 1
		warn("[TestWalki2] Brak obsługi zdarzenia " .. tostring(z.typ))
	else
		f(self, ev)
		self.obsluzone += 1
	end
	if ev.ujecie then
		self:proponujUjecie(ev.ujecie)
	end
end

------------------------------------------------------------------ co klatkę: pozy aktorów (ruch całego aktora)
function Sesja:aktualizujPozy(tau: number)
	local pozy = {}
	for strona in self.aktorzy do
		pozy[strona] = { przod = 0, bok = 0, gora = 0, pochyl = 0, przechyl = 0, obrot = 0 }
	end
	local n = #self.plan
	local od = math.max(1, (self.biezace or 1) - 6)
	local do_ = math.min(n, (self.biezace or 1) + 1)
	for i = od, do_ do
		local ev = self.plan[i]
		local e = tau - ev.t
		local poza = e > ev.trwa + 0.8 and not ev.smiertelny
		if e > -0.01 and not poza then
			local z = ev.z
			local pa, pd = pozy[z.kto], pozy[z.cel]
			local A, D = self.aktorzy[z.kto], self.aktorzy[z.cel]
			if ev.atak then
				-- klip ataku sam przesuwa atakującego (wyskok i wypad miażdżącego ciosu, wypad Maga przy czarze)
				local wlasnyRuch = ruchWKlipie(A, ev.akcja)
				-- doskok i powrót (wręcz / skok)
				if ev.doskok > 0 then
					local h = ev.eHit
					local w = okno(e, h - ev.tDoskoku, h - 0.03, h + 0.16, h + 0.16 + ev.tPowrotu)
					pa.przod += ev.doskok * w
					pa.obrot += (ev.obrot or 0) * w
					if ev.styl == "skok" then
						pa.gora += (ev.choreo.wysokosc or 4) * luk(e, h - ev.tDoskoku, h)
					elseif z.krytyk and not wlasnyRuch then
						pa.gora += 0.9 * luk(e, h - ev.tDoskoku, h)
					end
					pa.pochyl += rad(10) * okno(e, h - 0.15, h - 0.02, h + 0.1, h + 0.35)
				elseif (ev.styl == "pocisk" or ev.styl == "chmura") and not wlasnyRuch then
					pa.przod -= 0.35 * odrzut(e - ev.eRel, 0.06, 0.35)
					pa.pochyl -= rad(5) * odrzut(e - ev.eRel, 0.06, 0.35)
				elseif ev.styl == "korzenie" then
					pa.gora += 0.6 * luk(e, ev.eRel - 0.3, ev.eRel)
				end
				-- broniący
				local u = e - ev.eHit
				if z.typ == "unik" then
					local zej = okno(e, ev.eHit - 0.28, ev.eHit - 0.05, ev.eHit + 0.2, ev.eHit + 0.55)
					if not ruchWKlipie(D, "unik") then
						pd.bok -= 1.7 * zej
						pd.przod -= (0.9 + (ev.zejscieUniku or 0)) * zej
						pd.przechyl += rad(12) * zej
					else
						-- klip uniku z własnym odskokiem (Wojownik 1,7 studa w lewo, Mag ok. 1,6 w tył i w lewo): bez bocznego
						-- ślizgu i przechyłu, ale z zejściem w tył (etap 9, Studio: sam odskok z klipu zostawiał prawe ramię
						-- i nogę Wojownika na osi ciosu — wilk i maczuga trolla przechodziły przez niego; ślizg wypada
						-- w podskokach klipu, więc stopy nie jadą po ziemi)
						pd.przod -= (0.9 + (ev.zejscieUniku or 0)) * zej
					end
				elseif z.typ == "blok" then
					if not D:maKlip("blok") then
						-- parada bez tarczy (v3: blok ma każda klasa i potwór): odchylenie, krok w tył i pół obrotu bokiem
						-- (broń albo ramię do ciosu) w chwili odbicia; łuk odbicia rysuje Efekty3D (fx:parada)
						local w = okno(e, ev.eHit - 0.16, ev.eHit - 0.02, ev.eHit + 0.12, ev.eHit + 0.45)
						pd.przod -= Ch.BLOK.cofniecie * w
						pd.pochyl -= rad(Ch.BLOK.odchylenie) * w
						pd.obrot += rad(12) * w
					elseif not ruchWKlipie(D, "blok") then
						-- klip bloku sam cofa Wojownika o 0,41 studa przy ciosie w tarczę
						pd.przod -= 0.6 * odrzut(u, 0.07, 0.42)
					end
				elseif u >= 0 then
					local sila = if z.krytyk then 2.3 else 1.1
					-- efekt z klipu trzyma cel (korzenie strażnika): bez odrzutu, uniesiony, póki klip go nie puści
					local trzyma = (ev.trzymaDo or 0) > 0 and not ev.smiertelny
					if ev.smiertelny then
						pd.przod -= sila * 1.3 * wyjscie(u / 0.35)
					elseif not trzyma then
						pd.przod -= sila * odrzut(u, 0.09, 0.5)
						pd.pochyl -= (if z.krytyk then rad(22) else rad(12)) * odrzut(u, 0.08, 0.45)
					end
					if trzyma then
						pd.gora += 0.35 * okno(u, 0, 0.12, ev.trzymaDo, ev.trzymaDo + 0.25)
					elseif ev.styl == "korzenie" and not ev.smiertelny then
						pd.gora += 0.35 * okno(u, 0, 0.12, ev.trwa - ev.eHit - 0.2, ev.trwa - ev.eHit + 0.1)
					end
				end
			elseif ev.naSiebie then
				-- podskok przy rzuceniu — nie, gdy klip ma własny ruch (tupnięcie kamiennej skóry, biodra w górę przy kręgu bariery)
				if not ruchWKlipie(A, ev.akcja) then
					pozy[z.kto].gora += 0.35 * luk(e, ev.eRel - 0.25, ev.eRel + 0.2)
				end
			elseif z.typ == "utrata_tury" then
				pozy[z.kto].przechyl += rad(9) * math.sin(e * 11) * okno(e, 0, 0.12, ev.trwa - 0.15, ev.trwa)
			elseif z.typ == "efekt_tick" then
				pozy[z.kto].przechyl += rad(4) * math.sin(e * 25) * okno(e, ev.eHit, ev.eHit + 0.05, ev.eHit + 0.2, ev.eHit + 0.35)
			elseif z.typ == "wskrzeszenie" then
				-- wskrzeszenie: wstający unosi się lekko w świetle i opada na nogi
				local w = Ch.WSKRZESZENIE
				pozy[z.kto].gora += 0.55 * luk(e, ev.trwa * w.wstaje, ev.trwa * 0.92)
			end
		end
	end
	-- finał: zwycięzca w radości obraca się w stronę widza (kamery objazdu), żeby wiwat było widać z przodu (przegląd 15.11)
	local obrotZw = 0
	if self.final and (self.final.obrot or self.final.radosc) and self.obrotZwyciezcy and self.tRadosc then
		obrotZw = self.obrotZwyciezcy * gladko((tau - (self.tObrotu or self.tRadosc)) / OBROT_ZWYCIEZCY.czas)
	end
	for strona, a in self.aktorzy do
		local p = pozy[strona]
		local kier = self.geo.kier[strona]
		local x = self.geo.x[strona] + kier * p.przod
		-- obrót w lewo aktora (celowanie): u gracza (kier 1) kąt ujemny, u wroga dodatni (ten sam wzór co obrót zwycięzcy)
		local yaw = (if strona == self.zwyciezca then obrotZw else 0) - kier * p.obrot
		local cf = self.cfSceny * CFrame.lookAt(Vector3.new(x, p.gora, p.bok),
			Vector3.new(x + kier * math.cos(yaw), p.gora, p.bok + math.sin(yaw)))
		cf = cf * CFrame.Angles(-p.pochyl, 0, p.przechyl)
		a:ustaw(cf)
	end
end

------------------------------------------------------------------ zwolnienie czasu sceny (krytyk, nokaut)
function Sesja:zwolnienie(tau: number): number
	local t = 1
	for _, w in self.zwolnienia do
		local r = w.rampa or 0.08
		if tau > w.od - r and tau < w["do"] + 0.08 then
			local k
			if tau < w.od then
				k = gladko((tau - (w.od - r)) / r)
			elseif tau > w["do"] then
				k = 1 - gladko((tau - w["do"]) / 0.08)
			else
				k = 1
			end
			t = math.min(t, 1 + (w.tempo - 1) * k)
		end
	end
	return t
end

------------------------------------------------------------------ kamera
local MIN_UJECIA = 0.9 -- s czasu rzeczywistego: krótsze ujęcia nie są przerywane zwykłym zdarzeniem

-- odległość kamery, z której mieści się postać o wysokości h przy pionowym kącie kat (kadr 16:9) z zapasem
local function odlDlaWys(h: number, kat: number, szer: number?): number
	local t = math.tan(rad(kat / 2))
	return math.max((h * 0.62 + 1.1) / t, ((szer or 0) * 0.62 + 1.4) / (t * 16 / 9) + (szer or 0) * 0.35)
end

-- odległość, z której prostokąt pary (szerokość od lo do hi, wysokość od ziemi do gora) mieści się w kadrze 16:9
-- przy pionowym kącie kat; u góry kadru są tabliczki z paskami, u dołu przyciski — stąd zapas w pionie
local function odlDlaPary(lo: number, hi: number, gora: number, kat: number, zapas: number?): number
	local t = math.tan(rad(kat / 2))
	local z = zapas or 1
	local pw = (hi - lo) * 0.5 + 1.0 * z
	local ph = gora * 0.5 * (1 + 0.32 * z) + 0.8 * z
	return math.max(ph / t, pw / (t * 16 / 9))
end

--[[ Duży aktor (Troll, Strażnik Gaju 14,5 studa): u góry kadru tabliczki z paskami i wstęga zasłaniają ok. 22%
	wysokości, u dołu przyciski ok. 10% — głowa i korona mają stać pod tabliczkami. Odległość, z której szczyt `gora`
	mieści się w odkrytej części kadru, gdy kamera patrzy na wysokość srodekY przy pionowym kącie kat. ]]
local ODKRYTE_U_GORY = 0.56 -- odkryta część górnej połowy kadru (1 − 2 · 0,22)
local DUZY = 8 -- od tej wysokości pary (studs) kadr pilnuje tabliczek
local function odlDlaGory(gora: number, srodekY: number, kat: number): number
	return (gora + 0.4 - srodekY) / (ODKRYTE_U_GORY * math.tan(rad(kat / 2)))
end

-- bieżące położenie aktora w układzie sceny (ziemia pod nim: X wzdłuż walki, Y = wysokość skoku, Z w bok)
function Sesja:wScenie(strona: string): Vector3
	return self.cfSceny:PointToObjectSpace(self.aktorzy[strona]:cfZiemi().Position)
end

-- prostokąt obejmujący obu aktorów TERAZ (z doskokiem, skokiem, odrzutem): lewo, prawo, góra (w układzie sceny);
-- zDomem = także ich miejsca stania (kadr nie „oddycha” przy każdym doskoku)
function Sesja:obrysPary(A: string, D: string, zDomem: boolean?): (number, number, number)
	local g = self.geo
	local lo, hi, gora = math.huge, -math.huge, 0
	for _, s in { A, D } do
		local p = self:wScenie(s)
		local pol = g.w[s] * 0.5 + 0.3
		lo = math.min(lo, p.X - pol)
		hi = math.max(hi, p.X + pol)
		gora = math.max(gora, p.Y + g.h[s])
		if zDomem then
			lo = math.min(lo, g.x[s] - pol)
			hi = math.max(hi, g.x[s] + pol)
			gora = math.max(gora, g.h[s])
		end
	end
	return lo, hi, gora
end

function Sesja:proponujUjecie(uj)
	local teraz = self.zegar
	local odCiecia = teraz - (self.kam.ostatnieCiecie or 0)
	local tura = uj.ev and uj.ev.tura or 0
	local dluga = tura > 12
	-- atak po ujęciu jednej postaci (umiejętność na siebie, efekt) nie może zostać w tym ujęciu: atakujący byłby
	-- poza kadrem — taki atak zawsze dostaje swoje ujęcie (najwyżej z płynnym przejściem)
	local jednaPostac = self.kam.uj and (self.kam.uj.typ == "naSiebie" or self.kam.uj.typ == "efekt")
	-- to samo po zbliżeniu na broniącego, gdy teraz bije właśnie on: zbliżenie pokazuje tylko jego miejsce stania,
	-- więc po doskoku zostawał w kadrze sam atakujący, a cel był poza kadrem (Studio 17.11.2026, długa walka —
	-- zwykłe ujęcia są tam pomijane co drugie, więc stare zbliżenie zostawało na następny atak)
	if not jednaPostac and self.kam.uj and self.kam.uj.typ == "zblizenie" and uj.broniacy ~= nil
		and self.kam.uj.broniacy ~= uj.broniacy then
		jednaPostac = true
	end
	local wymuszone = jednaPostac and uj.ev ~= nil and uj.ev.atak == true
	if uj.prio < 2 and not wymuszone then
		local minimum = MIN_UJECIA * (if self.tempo >= 2 then 1.6 else 1) * (if dluga then 1.5 else 1)
		if odCiecia < minimum then
			return
		end
		-- w długiej walce tylko co drugie zwykłe ujęcie (reszta zostaje na poprzednim, kamera i tak płynie)
		if dluga then
			self.kam.pominiete = (self.kam.pominiete or 0) + 1
			if self.kam.pominiete % 2 == 1 then
				return
			end
		end
	end
	local przejscie = 0
	if uj.prio < 3 and (self.tempo >= 2 or dluga or uj.typ == self.kam.uj.typ) then
		przejscie = 0.45 -- płynne przejście zamiast cięcia
	end
	if przejscie > 0 and self.kam.ostatnie then
		self.kam.od = self.kam.ostatnie
		self.kam.przejscieStart = teraz
		self.kam.przejscie = przejscie
	else
		self.kam.od = nil
	end
	if uj.typ == "objazd" and not self.obrotZwyciezcy then
		self.katObjazduMin = nil -- liczony w pierwszej klatce objazdu (leżący pokonany już na ziemi)
	end
	self.kam.uj = uj
	self.kam.start = self.tau
	self.kam.ostatnieCiecie = teraz
	self.licznikUjec += 1
end

--[[ Twarz potwora (poprawka D5): kamera prawie zawsze widziała potwora z boku albo od tyłu. Kąt twarzy = kąt (w poziomie)
	między kierunkiem, w którym patrzy potwór, a kierunkiem od niego do kamery: 0° = prosto w twarz, 90° = profil.
	Po policzeniu ujęcia, gdy kąt > MAKS_KAT_TWARZY, kamera obraca się wokół punktu, na który patrzy (kadr zostaje), w
	stronę gracza — do ujęcia 3/4 od strony gracza. Nie dotyczy objazdu, ujęcia pokonanego i ujęć samego gracza. ]]
local MAKS_KAT_TWARZY = 56

function Sesja:katTwarzy(poz: Vector3): number
	local M = self.aktorzy and self.aktorzy.wrog
	if not M then
		return 0
	end
	local pM = self:wScenie("wrog")
	local f = self.cfSceny:VectorToObjectSpace(M:cfZiemi().LookVector)
	f = Vector3.new(f.X, 0, f.Z)
	local v = Vector3.new(poz.X - pM.X, 0, poz.Z - pM.Z)
	if v.Magnitude < 1e-3 or f.Magnitude < 1e-3 then
		return 0
	end
	return math.deg(math.acos(math.clamp(v.Unit:Dot(f.Unit), -1, 1)))
end

-- punkty próbne bryły aktora (walec z jego szerokości i głębokości, cztery wysokości) w układzie sceny — do szybkiego
-- pomiaru, jaka część postaci mieści się w kadrze z kamery, której jeszcze nie ustawiono
local PROBKI_KATY = { 0, 60, 120, 180, 240, 300 }
function Sesja:probkiAktora(strona: string): { Vector3 }
	local a = self.aktorzy[strona]
	local w = a.wpis
	local cf = self.cfSceny:ToObjectSpace(a:cfZiemi())
	local wynik = table.create(22)
	for _, uy in { 0.15, 0.5, 0.85 } do
		local y = w.wysokosc * uy
		table.insert(wynik, (cf * Vector3.new(0, y, 0)))
		for _, k in PROBKI_KATY do
			local r = rad(k)
			table.insert(wynik, (cf * Vector3.new(math.cos(r) * w.szerokosc * 0.4, y, math.sin(r) * w.glebokosc * 0.4)))
		end
	end
	table.insert(wynik, (cf * Vector3.new(0, w.wysokosc, 0))) -- czubek głowy (ucięta głowa = złe ujęcie)
	return wynik
end

--[[ Ocena postaci w kadrze 16:9 kamery (poz → cel, pionowy kąt kat): ułamek punktów w kadrze, góra i wysokość
	postaci w kadrze (−1 … 1 = dół … góra kadru), środek w poziomie i głębokość. ]]
local function rzutPostaci(probki: { Vector3 }, cf: CFrame, tv: number, th: number)
	local n, gora, dol, lewo, prawo, glebia = 0, -math.huge, math.huge, math.huge, -math.huge, 0
	for _, p in probki do
		local l = cf:PointToObjectSpace(p)
		local z = -l.Z
		if z > 0.3 then
			local x, y = l.X / (th * z), l.Y / (tv * z)
			gora, dol = math.max(gora, y), math.min(dol, y)
			lewo, prawo = math.min(lewo, x), math.max(prawo, x)
			glebia += z
			if math.abs(x) <= 1 and math.abs(y) <= 1 then
				n += 1
			end
		end
	end
	return { u = n / math.max(1, #probki), gora = gora, wys = gora - dol, x0 = lewo, x1 = prawo, y0 = dol, y1 = gora,
		z = glebia / math.max(1, #probki) }
end

-- ułamek punktów próbnych w kadrze 16:9 kamery (poz → cel, pionowy kąt kat)
local function ulamekWKadrze(probki: { Vector3 }, poz: Vector3, cel: Vector3, kat: number): number
	local tv = math.tan(rad(kat / 2))
	return rzutPostaci(probki, CFrame.lookAt(poz, cel), tv, tv * 16 / 9).u
end
Sesja.ulamekWKadrze = ulamekWKadrze

-- ułamek punktów postaci B, których nie zasłania postać A stojąca bliżej kamery (prostokąt A w kadrze, ściśnięty o 15%)
local function odsloniecie(probkiB: { Vector3 }, rzA, cf: CFrame, tv: number, th: number): number
	local mx, my = (rzA.x1 - rzA.x0) * 0.15, (rzA.y1 - rzA.y0) * 0.15
	local n, ile = 0, 0
	for _, p in probkiB do
		local l = cf:PointToObjectSpace(p)
		local z = -l.Z
		if z > 0.3 then
			ile += 1
			local x, y = l.X / (th * z), l.Y / (tv * z)
			local zaA = z > rzA.z and x > rzA.x0 + mx and x < rzA.x1 - mx and y > rzA.y0 + my and y < rzA.y1 - my
			if not zaA then
				n += 1
			end
		end
	end
	return n / math.max(1, ile)
end

--[[ Obrót do twarzy potwora i pilnowanie gracza w kadrze (przegląd 15.11: po obrocie Wojownik stał ogromny na
	pierwszym planie, tyłem, z głową uciętą górną krawędzią, a w zbliżeniu zasłaniał slime'a — „kto kogo bije” czytało
	się słabo). Kandydaci: pełny obrót i mniejsze (r = 1 … 0) × odjazd od punktu, na który kamera patrzy (f = 1 … 1,8).
	Warunki kandydata:
	  • gracz ≥ 62% punktów próbnych w kadrze (≥ 72%, gdy potwór bije gracza), potwór ≥ 65%;
	  • gracz nie bliżej kamery niż 0,85 odległości potwora (nie „wielki na pierwszym planie”), nie wyższy w kadrze niż
	    60% wysokości kadru (chyba że jest dużo wyższy od potwora), czubek głowy gracza co najmniej 10% pod górną
	    krawędzią kadru;
	  • potwór odsłonięty przez gracza w ≥ 70% punktów (i gracz przez potwora w ≥ 60%).
	Spośród spełniających — najtańszy (najmniej odjęty obrót, potem najmniejszy odjazd); gdy żaden — najlepsza ocena.
	Wybór liczony co 0,1 s i wygładzany, żeby kamera nie skakała. ]]
local TWARZ_R = { 1, 0.85, 0.7, 0.5, 0.25, 0 }
local TWARZ_F = { 1, 1.12, 1.25, 1.4, 1.6, 1.8 }
function Sesja:twarzPotwora(poz: Vector3, cel: Vector3, kat: number, uj): Vector3
	local rx, rz = poz.X - cel.X, poz.Z - cel.Z
	local function obroc(a: number): Vector3
		local c, s = math.cos(a), math.sin(a)
		return Vector3.new(cel.X + rx * c - rz * s, poz.Y, cel.Z + rx * s + rz * c)
	end
	-- pełny obrót do kąta twarzy ≤ MAKS_KAT_TWARZY
	local krok = rad(2)
	local znak = if self:katTwarzy(obroc(krok)) < self:katTwarzy(obroc(-krok)) then 1 else -1
	local phi = 0
	if self:katTwarzy(poz) > MAKS_KAT_TWARZY then
		for i = 1, 60 do
			phi = znak * krok * i
			if self:katTwarzy(obroc(phi)) <= MAKS_KAT_TWARZY then
				break
			end
		end
	end
	local function kandydat(r: number, f: number): Vector3
		local p = obroc(phi * r)
		return cel + (p - cel) * f
	end
	-- wybór (r, f) co 0,1 s czasu kamery; między wyborami wygładzanie
	local tw = self.kam.twarz
	if not tw or tw.uj ~= uj then
		tw = { uj = uj, r = nil, f = nil, rCel = 1, fCel = 1, t = -math.huge, zegar = self.zegar }
		self.kam.twarz = tw
	end
	if self.zegar - tw.t >= 0.1 then
		tw.t = self.zegar
		local pG, pW = self:probkiAktora("gracz"), self:probkiAktora("wrog")
		local srG, srW = self:wScenie("gracz") + Vector3.new(0, self.geo.h.gracz * 0.5, 0),
			self:wScenie("wrog") + Vector3.new(0, self.geo.h.wrog * 0.5, 0)
		local progG = if uj and uj.broniacy == "gracz" then 0.72 else 0.62
		local wyzszy = self.geo.h.gracz > 1.6 * self.geo.h.wrog
		-- ujęcia, w których gracz z założenia jest blisko kamery albo poza kadrem, mają łagodniejsze warunki:
		-- zza gracza i start lotu pocisku (gracz na pierwszym planie, ale w kadrze ≥ 72% gdy obrywa, inaczej ≥ 40%),
		-- zbliżenie potwora (z gracza widać rękę z bronią), ujęcia samego potwora (efekt, umiejętność na siebie)
		local typ = uj and uj.typ or "ogolny"
		local pierwszyPlan = typ == "zaAtakujacym" or typ == "zaBroniacym" or typ == "pocisk"
		local samPotwor = (typ == "efekt" or typ == "naSiebie") or (typ == "zblizenie" and uj.broniacy == "wrog")
		if pierwszyPlan and not (uj and uj.broniacy == "gracz") then
			progG = 0.4
		end
		local tv = math.tan(rad(kat / 2))
		local th = tv * 16 / 9
		local najlepszy, koszt = nil, math.huge
		local zapas, zapasOcena = nil, -math.huge
		for _, r in TWARZ_R do
			for _, f in TWARZ_F do
				local q = kandydat(r, f)
				local cf = CFrame.lookAt(q, cel)
				local G, M = rzutPostaci(pG, cf, tv, th), rzutPostaci(pW, cf, tv, th)
				local dG, dW = (q - srG).Magnitude, (q - srW).Magnitude
				local odsM = if G.z < M.z then odsloniecie(pW, G, cf, tv, th) else 1
				local odsG = if M.z < G.z then odsloniecie(pG, M, cf, tv, th) else 1
				local c = (1 - r) * 1.0 + (f - 1) * 0.9
				local oceny
				if samPotwor then
					oceny = { M.u / 0.65, odsM / 0.7 }
				elseif typ == "zblizenie" then
					oceny = { G.u / 0.72, odsG / 0.6 } -- zbliżenie gracza, gdy obrywa (z potwora widać część)
				elseif pierwszyPlan then
					oceny = { G.u / progG, M.u / 0.65, odsM / 0.7, odsG / 0.6 }
				else
					oceny = {
						G.u / progG, M.u / 0.65, dG / (0.85 * dW), odsM / 0.7, odsG / 0.6,
						if wyzszy then 1 else 1.2 / math.max(G.wys, 0.01), 0.8 / math.max(G.gora, 0.01),
					}
				end
				local najgorsza = math.huge
				for _, o in oceny do
					najgorsza = math.min(najgorsza, o)
				end
				if najgorsza >= 1 then
					if c < koszt then
						najlepszy, koszt = { r, f }, c
					end
				else
					local ocena = najgorsza - c * 0.05
					if ocena > zapasOcena then
						zapas, zapasOcena = { r, f }, ocena
					end
				end
			end
		end
		local wybor = najlepszy or zapas or { 1, 1 }
		tw.rCel, tw.fCel = wybor[1], wybor[2]
	end
	if tw.r == nil then
		tw.r, tw.f = tw.rCel, tw.fCel
	else
		local u = 1 - math.exp(-math.max(0, self.zegar - tw.zegar) * 7)
		tw.r += (tw.rCel - tw.r) * u
		tw.f += (tw.fCel - tw.f) * u
	end
	tw.zegar = self.zegar
	return kandydat(tw.r, tw.f)
end

-- ujęcie → (pozycja, cel, kąt) w układzie sceny, z poprawką „twarz potwora”
function Sesja:ujecie(uj, tau: number): (Vector3, Vector3, number)
	local poz, cel, kat = self:ujecieSurowe(uj, tau)
	local typ = uj.typ
	local tylkoGracz = (typ == "naSiebie" or typ == "efekt") and uj.atakujacy == "gracz"
	if typ ~= "objazd" and typ ~= "pokonany" and not tylkoGracz then
		poz = self:twarzPotwora(poz, cel, kat, uj)
	end
	return poz, cel, kat
end

-- prostokąt leżącego pokonanego w układzie sceny (X, Z) z obwiedni ostatniej klatki upadku (TabelaAktorow: lezy)
function Sesja:lezacy(strona: string): (number, number, number, number, number)
	local g = self.geo
	local p = self:wScenie(strona)
	local k = g.kier[strona]
	local lz = self.aktorzy[strona].wpis.lezy
	if lz then
		-- rig: przód −Z, prawa +X; scena: aktor patrzy w k·X, jego prawa = k·Z
		local xa, xb = p.X - k * lz.mn[3], p.X - k * lz.mx[3]
		local za, zb = p.Z + k * lz.mn[1], p.Z + k * lz.mx[1]
		return math.min(xa, xb), math.max(xa, xb), math.min(za, zb), math.max(za, zb), math.max(lz.mx[2], 0.8)
	end
	local r = math.max(g.w[strona], g.h[strona] * 0.5)
	return p.X - r, p.X + r, p.Z - r, p.Z + r, g.h[strona] * 0.5
end

--[[ Najmniejszy kąt objazdu (stopnie), od którego kamera nie wjeżdża w leżącego pokonanego: kamera poza jego
	prostokątem (z zapasem), widok na zwycięzcę nie przechodzi przez niego, a szczątki nie są bliżej kamery niż 0,95
	odległości do zwycięzcy (nie wchodzą na pierwszy plan). Duży pokonany (stos głazów Strażnika) → objazd bardziej
	z przodu zwycięzcy. ]]
function Sesja:katObjazdu(W: Vector3, znak: number, R: number): number
	local x0, x1, z0, z1 = self:lezacy(self.pokonany)
	local m = 1.2
	x0, x1, z0, z1 = x0 - m, x1 + m, z0 - m, z1 + m
	local function wPudle(x: number, z: number): boolean
		return x > x0 and x < x1 and z > z0 and z < z1
	end
	local function dobry(katSt: number): boolean
		local k = rad(katSt)
		local cx, cz = W.X + znak * R * math.cos(k), R * math.sin(k)
		if wPudle(cx, cz) then
			return false
		end
		for i = 1, 24 do
			local u = i / 25
			if wPudle(cx + (W.X - cx) * u, cz + (0 - cz) * u) then
				return false
			end
		end
		local dx = math.max(x0 - cx, 0, cx - x1)
		local dz = math.max(z0 - cz, 0, cz - z1)
		local doZw = math.sqrt((cx - W.X) ^ 2 + cz ^ 2)
		return math.sqrt(dx * dx + dz * dz) >= 0.95 * doZw
	end
	local katMin = 20
	for katSt = 140, 20, -2 do
		if not dobry(katSt) then
			katMin = katSt + 2
			break
		end
	end
	return katMin
end

function Sesja:ujecieSurowe(uj, tau: number): (Vector3, Vector3, number)
	local g = self.geo
	local lt = tau - (self.kam.start or 0)
	local typ = uj.typ
	local A = uj.atakujacy or "gracz"
	local D = uj.broniacy or "wrog"
	local xA, xD = g.x[A], g.x[D]
	local hA, hD = g.h[A], g.h[D]
	local wA, wD = g.w[A], g.w[D]
	local dir = if xD > xA then 1 elseif xD < xA then -1 else g.kier[A]
	-- zza pleców potwora nie widać jego twarzy (D5): ujęcie „zza pleców” zawsze zza gracza
	if typ == "zaAtakujacym" and A == "wrog" then
		typ = "zaBroniacym"
	elseif typ == "zaBroniacym" and D == "wrog" then
		typ = "zaAtakujacym"
	end
	-- zza pleców dużo większego aktora nic nie widać (Troll przed Wojownikiem) — wtedy ujęcie z boku
	-- …a przy bardzo różnym wzroście (Mag przy Strażniku) mały aktor ląduje w rogu kadru
	local roznica = math.max(hA, hD) / math.max(math.min(hA, hD), 0.5)
	if (typ == "zaAtakujacym" and hA > 1.3 * hD + 0.5) or (typ == "zaBroniacym" and hD > 1.3 * hA + 0.5)
		or ((typ == "zaAtakujacym" or typ == "zaBroniacym") and roznica > 1.8) then
		typ = "boczny"
	end
	-- zbliżenie małego celu pod dużo większym atakującym (Strażnik Gaju nad Zwiadowcą) nie pokazuje ciosu — z boku
	local olbrzym = hA > 1.8 * hD + 0.5
	if typ == "zblizenie" and olbrzym then
		typ = "boczny"
	end
	if typ == "ogolny" then
		local k = wyjscie(lt / 2.5)
		local dryf = math.sin(lt * 0.22) * g.S * 0.06
		return Vector3.new(dryf, g.H * 0.42 + 1.6, g.dist * (1.06 - 0.06 * k)), Vector3.new(dryf * 0.5, g.H * 0.46, 0), 40
	elseif typ == "boczny" then
		-- skos 3/4 od strony atakującego; kadr z miejsc stania i z bieżących położeń (wyskok, doskok, odrzut)
		local k = gladko(lt / 1.6)
		local lo, hi, gora = self:obrysPary(A, D, true)
		-- zamach nad głową (Choreografie: zamach — Miażdżący cios, 17.11.2026): wyskok i miecz z klipu w kadrze
		local zamach = uj.ev and uj.ev.choreo and uj.ev.choreo.zamach
		if type(zamach) == "number" then
			gora = math.max(gora, hA + zamach)
		end
		local d = math.max(odlDlaWys(g.H, 42) * 1.02, g.S * 1.05, odlDlaPary(lo, hi, gora, 42) + 0.4 * math.max(wA, wD))
		if gora > DUZY then
			d = math.max(d, odlDlaGory(gora, gora * 0.5, 42))
		end
		local srodek = (lo + hi) / 2
		-- skos od strony atakującego; gdy atakujący jest olbrzymem, od strony celu (inaczej jego bryła zasłania cel)
		-- …i gdy atakuje potwór — od strony gracza, czyli od strony twarzy potwora (D5)
		local strona = if olbrzym or A == "wrog" then -1 else 1
		local xKam, xCel = srodek - dir * strona * (g.S * 0.32 + 0.6 * k), srodek + dir * strona * g.S * 0.08
		-- kamera stoi w skosie: oba brzegi pary (np. szeroki slime z brzegu kadru) muszą zmieścić się w poziomie
		local tanPol = math.tan(rad(21)) * 16 / 9 * 0.86
		for _ = 1, 10 do
			local z = d - 0.8 * k
			local skret = math.atan2(xCel - xKam, z)
			local miesci = true
			for _, x in { lo, hi } do
				if math.abs(math.tan(math.atan2(x - xKam, z) - skret)) > tanPol then
					miesci = false
				end
			end
			if miesci then
				break
			end
			d *= 1.07
		end
		return Vector3.new(xKam, gora * 0.4 + 1.2, d - 0.8 * k), Vector3.new(xCel, gora * 0.5, 0), 42
	elseif typ == "zaAtakujacym" then
		local k = gladko(lt / 1.4)
		return Vector3.new(xA - dir * (2.4 + 0.4 * hA) + dir * 0.6 * k, 0.5 * hA + 0.25 * hD + 1.0, 3.0 + 0.65 * hA + 0.3 * hD + 0.4 * wA - 0.3 * k),
			Vector3.new(xD - dir * 0.5, 0.5 * hD, 0), 50
	elseif typ == "zaBroniacym" then
		local k = gladko(lt / 1.4)
		return Vector3.new(xD + dir * (2.4 + 0.4 * hD) - dir * 0.5 * k, 0.5 * hD + 0.25 * hA + 1.0, 3.0 + 0.65 * hD + 0.3 * hA + 0.4 * wD - 0.3 * k),
			Vector3.new(xA + dir * 0.6, 0.5 * hA, 0), 50
	elseif typ == "zblizenie" then
		local k = gladko(lt / 1.2)
		local d = odlDlaWys(hD, 44, wD) * 0.95
		if hD > DUZY then
			d = math.max(d, odlDlaGory(hD, 0.5 * hD, 44) / 0.94)
		end
		return Vector3.new(xD - dir * d * 0.35, 0.55 * hD + 0.6, d * 0.94 - 0.5 * k),
			Vector3.new(xD - dir * 0.6, 0.5 * hD, 0), 44
	elseif typ == "krytyk" then
		-- niska kamera z boku; w zwolnieniu „wjazd” optyczny (zawężenie kąta) na trafienie
		local ev = uj.ev
		local tHit = ev.t + (ev.eHit or 0.5)
		local k = gladko((tau - (tHit - 0.3)) / 0.45)
		-- kadr z BIEŻĄCYCH położeń obu aktorów (doskok, wyskok przy uderzeniu z góry, odrzut celu), a nie z miejsc stania:
		-- atakujący po doskoku i w powietrzu zostaje w kadrze
		local lo, hi, gora = self:obrysPary(A, D, false)
		gora = math.max(gora, math.max(hA, hD))
		local d = odlDlaPary(lo, hi, gora, 52) + 0.4 * math.max(wA, wD)
		local srodek = (lo + hi) / 2
		-- „wjazd” optyczny (zawężenie kąta) tylko do kadru, w którym obaj jeszcze się mieszczą (mniejszy zapas)
		local t = math.max(((hi - lo) * 0.5 + 1.0) / (d * 16 / 9), (gora * 0.5 * 1.2 + 0.55) / d)
		local yCel = 0.46 * gora
		if gora > DUZY then
			-- duży aktor: kamera patrzy na połowę wzrostu, stoi tak daleko, żeby korona była pod tabliczkami,
			-- a „wjazd” kończy się na tej granicy
			yCel = 0.5 * gora
			d = math.max(d, odlDlaGory(gora, yCel, 52))
			t = math.max(t, (gora + 0.4 - yCel) / (ODKRYTE_U_GORY * d))
		end
		local katMin = math.deg(2 * math.atan(t))
		local yKam = 0.28 * gora + 0.8
		if ev.styl == "skok" then
			-- uderzenie z góry (17.11.2026, Studio: przykucnięty po lądowaniu Zwiadowca zasłaniał 62% slime'a z niskiej
			-- kamery): kamera wyżej, ponad lądującym — cel widać zza jego pleców, a cel kadru zostaje
			yKam = math.max(yKam, math.max(hA, hD) + 1.6)
		end
		return Vector3.new(srodek - dir * 0.4 * k, yKam, d),
			Vector3.new(srodek + dir * 0.04 * (hi - lo) * k, yCel, 0), 52 - (52 - math.clamp(katMin, 40, 52)) * k
	elseif typ == "pocisk" then
		local ev = uj.ev
		local s = uj.strona or 1
		-- dwie fazy: przy wypuszczeniu kamera jest zza ramienia atakującego (widać wylot), a w czasie lotu przechodzi
		-- w skos 3/4 na obu — w chwili trafienia cel jest duży i odsłonięty, a strzelec w kadrze
		local lot = math.max(ev.lot or 0.4, 0.2)
		local k = gladko((tau - (ev.t + (ev.eRel or 0) - 0.1)) / (lot + 0.35))
		local pos0 = Vector3.new(xA - dir * (4.5 + 0.6 * hA + 0.3 * wA), 0.72 * hA + 1.4, s * (3.2 + 0.55 * hA + 0.5 * wA))
		-- cel nie może schować się za atakującym: kamera odsuwa się w bok tak daleko, żeby promień do piersi celu
		-- mijał bryłę atakującego (walec o promieniu z jego szerokości) z zapasem
		local pA, pD = self:wScenie(A), self:wScenie(D)
		local cel0 = Vector3.new(pD.X - dir * 0.3, pD.Y + 0.42 * hD + 0.3, pD.Z)
		local dCel = math.abs(cel0.X - pos0.X)
		local dAtak = math.abs(pA.X - pos0.X)
		if dCel > dAtak + 0.5 then
			local r = wA * 0.5 + wD * 0.3 + 0.7
			local potrzeba = r * dCel / (dCel - dAtak) + math.abs(pA.Z)
			if math.abs(pos0.Z) < potrzeba then
				pos0 = Vector3.new(pos0.X, pos0.Y, s * potrzeba)
			end
		end
		local lo, hi, gora = self:obrysPary(A, D, true)
		local d1 = odlDlaPary(lo, hi, gora, 48) + 0.4 * math.max(wA, wD)
		local c1 = (lo + hi) / 2
		local pos1 = Vector3.new(c1 - dir * g.S * 0.3, gora * 0.42 + 1.0, s * d1)
		local cel1 = Vector3.new(c1 + dir * g.S * 0.06, gora * 0.45, 0)
		return pos0:Lerp(pos1, k), cel0:Lerp(cel1, k), 48
	elseif typ == "naSiebie" then
		local k = gladko(lt / 1.4)
		local f = g.kier[A]
		local d = odlDlaWys(hA, 42, wA) * 1.05
		if hA > DUZY then
			d = math.max(d, odlDlaGory(hA, 0.5 * hA, 42) / 0.88)
		end
		return Vector3.new(xA + f * d * 0.45, 0.55 * hA + 0.5, d * 0.88 - 0.6 * k), Vector3.new(xA + f * 0.3, 0.5 * hA, 0), 42
	elseif typ == "efekt" then
		local k = gladko(lt / 1.4)
		local f = g.kier[A]
		local d = odlDlaWys(hA, 44, wA) * 1.15
		if hA > DUZY then
			d = math.max(d, odlDlaGory(hA, 0.48 * hA, 44) / 0.9)
		end
		return Vector3.new(xA + f * d * 0.4, 0.6 * hA + 0.8, d * 0.9 - 0.5 * k), Vector3.new(xA + f * 0.4, 0.48 * hA, 0), 44
	elseif typ == "pokonany" then
		-- finał (D1): pokonany z góry 3/4, od strony zwycięzcy i widza — widać koniec upadku (kałuża z oczkami, stos
		-- głazów, leżący troll albo bohater); kadr z obwiedni leżenia, na początku jeszcze z zapasem na stojącego
		local P = self.pokonany
		local kP = g.kier[P]
		local x0, x1, z0, z1, hLez = self:lezacy(P)
		-- na początku ujęcia pokonany jeszcze się przewraca: cel kamery i zapas w pionie przechodzą od stojącego do leżącego
		local u0 = gladko(lt / 0.9)
		local c = Vector3.new((x0 + x1) / 2, g.h[P] * 0.42 * (1 - u0) + hLez * 0.3 * u0, (z0 + z1) / 2)
		local rozp = math.max(x1 - x0, z1 - z0) * 0.5
		local k = gladko(lt / 1.6)
		local wys = math.max(hLez, g.h[P] * 0.8 * (1 - u0))
		local t = math.tan(rad(22))
		-- (perspektywa z góry powiększa bliższą krawędź leżącego — stąd zapas 1,3)
		local d = math.max(7, ((rozp * 1.2 + 1.0) / (t * 16 / 9) + rozp * 0.5) * 1.3, (wys * 0.9 + 1.2) / t)
		d *= 1.08 - 0.08 * k
		local a, e = rad(62), rad(30)
		local u = Vector3.new(kP * math.cos(a), 0, math.sin(a))
		return c + u * (d * math.cos(e)) + Vector3.new(0, d * math.sin(e), 0), c, 44
	end
	-- objazd wokół zwycięzcy (finał); kończy się ze zwycięzcą w jednej ćwiartce, panel wyniku w drugiej połowie
	local zw = self.zwyciezca
	local znak = g.kier[zw]
	local hZ = g.h[zw]
	local czas = math.max(0, tau - (self.kam.start or tau)) + self.tauWyniku
	local k = wyjscie(czas / 2.6)
	local dryf = math.min(math.max(0, czas - 2.6) * 1.2, 12)
	local W, R, przesuniecie = self:parametryObjazdu()
	-- objazd nie wjeżdża w leżącego pokonanego (stos głazów Strażnika) i nie ma go na pierwszym planie (D1)
	if self.katObjazduMin == nil then
		self:przygotujObjazd()
	end
	local kat = rad(math.max(62 - 22 * k - dryf, self.katObjazduMin))
	local cel = W + Vector3.new(znak * R * przesuniecie, hZ * 0.5, 0)
	return W + Vector3.new(znak * R * math.cos(kat), hZ * 0.55 + 1.6, R * math.sin(kat)), cel, 44
end

-- objazd zwycięzcy: punkt zwycięzcy W (scena), promień R i przesunięcie kadru
function Sesja:parametryObjazdu(): (Vector3, number, number)
	local g = self.geo
	local zw = self.zwyciezca
	local hZ = g.h[zw]
	local R = 1.25 * hZ + 6.5
	local przesuniecie = 0.32
	if hZ > DUZY then
		-- duży zwycięzca (Troll, Strażnik): dalej i bliżej środka kadru — inaczej korona i bok były ucięte
		R = math.max(R, odlDlaGory(hZ, 0.5 * hZ, 44)) * 1.15
		przesuniecie = 0.2
	end
	return Vector3.new(g.x[zw], 0, 0), R, przesuniecie
end

--[[ Kąt objazdu (bez szczątków na pierwszym planie) i obrót zwycięzcy do widza. Kamera objazdu stoi pod kątem
	`kat` od kierunku, w którym zwycięzca patrzy (na pokonanego). Gdy leżący zmusza kamerę do dużego kąta (stos głazów,
	kałuża przed zwycięzcą), kamera stawała za plecami zwycięzcy i wiwatu nie było widać (przegląd 15.11) — teraz
	zwycięzca w radości obraca się w stronę kamery tak, żeby kąt twarzy (0° = przodem do kamery) był ≤ 35° na początku
	objazdu; objazd potem zmniejsza kąt najwyżej o ok. 34° (wjazd i dryf), więc twarz zostaje w kadrze. ]]
function Sesja:przygotujObjazd()
	local W, R = self:parametryObjazdu()
	self.katObjazduMin = self:katObjazdu(W, self.geo.kier[self.zwyciezca], R)
	local katStart = math.max(62, self.katObjazduMin)
	self.obrotZwyciezcy = rad(math.clamp(katStart - 35, 0, 150))
end

-- kąt twarzy dowolnej postaci z punktu sceny poz (0° = przodem do punktu, 90° = profil, 180° = tyłem)
function Sesja:katTwarzyStrony(strona: string, poz: Vector3): number
	local a = self.aktorzy and self.aktorzy[strona]
	if not a then
		return 0
	end
	local p = self:wScenie(strona)
	local f = self.cfSceny:VectorToObjectSpace(a:cfZiemi().LookVector)
	f = Vector3.new(f.X, 0, f.Z)
	local v = Vector3.new(poz.X - p.X, 0, poz.Z - p.Z)
	if v.Magnitude < 1e-3 or f.Magnitude < 1e-3 then
		return 0
	end
	return math.deg(math.acos(math.clamp(v.Unit:Dot(f.Unit), -1, 1)))
end

function Sesja:aktualizujKamere(tau: number, dt: number)
	local kam = self.kam
	local poz, cel, kat = self:ujecie(kam.uj, tau)
	if kam.od then
		local u = gladko((self.zegar - kam.przejscieStart) / kam.przejscie)
		if u >= 1 then
			kam.od = nil
		else
			poz = kam.od[1]:Lerp(poz, u)
			cel = kam.od[2]:Lerp(cel, u)
			kat = kam.od[3] + (kat - kam.od[3]) * u
		end
	end
	kam.ostatnie = { poz, cel, kat }
	local drzenie = Vector3.zero
	local ws = self.wstrzasKam
	if ws.sila > 0 then
		ws.wiek += dt
		local amp = ws.sila * math.exp(-ws.wiek * 9)
		if amp < 0.004 then
			ws.sila = 0
		else
			drzenie = Vector3.new(los:NextNumber(-1, 1), los:NextNumber(-1, 1), los:NextNumber(-1, 1)) * amp
		end
	end
	local s = self.cfSceny
	self.kamera.CFrame = CFrame.lookAt(s:PointToWorldSpace(poz) + drzenie, s:PointToWorldSpace(cel) + drzenie * 0.35)
	local pelny = 2 * math.atan(math.tan(rad(kat) / 2) / self.ui.wspolczynnikPasa)
	self.kamera.FieldOfView = math.clamp(math.deg(pelny), 5, 120)
end

------------------------------------------------------------------ pasywki i pomijanie (v3, D-078)
--[[ Zapowiedź pasywek na starcie: lista z odpowiedzi serwera (odpowiedz.pasywki = { gracz = { sloty = { id… },
	bron = id | "" }, wrog = … }); nazwy i premie z danych silnika (PlanWalki.opisPasywki + Choreografie.MODYFIKATORY).
	Legendarna pasywka (wskrzeszenie) zapala złote pióro przy portrecie. Walki z lasu tej listy nie niosą — wtedy
	zapowiedzi nie ma (premie i tak są w liczbach dziennika). ]]
function Sesja:zapowiedzPasywki()
	for _, s in { "gracz", "wrog" } do
		local opisy = {}
		local ps = self.pasywkiStron and self.pasywkiStron[s]
		if type(ps) == "table" then
			if type(ps.sloty) == "table" then
				for _, id in ps.sloty do
					local o = if type(id) == "string" then PlanWalki.opisPasywki(Dane, id, "slot", Ch.MODYFIKATORY) else nil
					if o then
						table.insert(opisy, o)
						if o.legendarna then
							self.legendy[s] = true
						end
					end
				end
			end
			if type(ps.bron) == "string" and ps.bron ~= "" then
				local o = PlanWalki.opisPasywki(Dane, ps.bron, "bron", Ch.MODYFIKATORY)
				if o then
					table.insert(opisy, o)
				end
			end
		end
		self.opisyPasywek[s] = opisy
		self.ui:ustawLegende(s, self.legendy[s], false)
		if #opisy > 0 then
			self:zaplanujAkcje(0.75, function()
				if not self.pominieto then
					self.ui:zapowiedzPasywki(s, opisy, 1.25)
				end
			end)
		end
	end
end

-- zgoda serwera na pominięcie tej walki (wolno) i powód; przycisk tylko ze zgodą, do baneru finału
function Sesja:ustawPominiecie(wolno: boolean, powod: string?)
	self.pomijanie = wolno
	self.powodPominiecia = powod or (if wolno then "ok" else "pierwsza_walka")
	self:atrybut("OstatniePominiecieDozwolone", wolno)
	self:atrybut("OstatniPowodPominiecia", self.powodPominiecia)
	if wolno and self.faza == "odtwarzanie" and not (self.final and self.final.baner) and not self.pominieto then
		self.ui:ukryjInfoPominiecia()
		self.ui:pokazPomin(function()
			self:pomin()
		end)
	else
		self.ui:ukryjPomin()
		if not wolno and self.powodPominiecia == "pierwsza_walka" and self.faza == "odtwarzanie" then
			self.ui:pokazInfoPominiecia("PIERWSZE SPOTKANIE — BEZ POMIJANIA", 2.5)
		end
	end
end

-- walka z lasu: zgoda z pamięci serwera prototypu (mostek SerwerWalki2 ← Sygnaly/WynikWalki kontenera lasu);
-- do odpowiedzi pomijać nie wolno. „brak_walki” zaraz po starcie = mostek jeszcze nie dostał sygnału: jedna powtórka.
function Sesja:zapytajOPominiecie()
	local f = zdalnaPominiecia()
	if not f then
		self:ustawPominiecie(false, "brak_zdalnej")
		return
	end
	local walka = self.walka
	task.spawn(function()
		for proba = 1, 2 do
			local ok, odp = pcall(function()
				return f:InvokeServer("czy", self.zrodlo)
			end)
			if self.zakonczona or self.walka ~= walka then
				return
			end
			local tak = ok and type(odp) == "table" and odp.ok == true
			local powod = if ok and type(odp) == "table" and type(odp.powod) == "string" then odp.powod else "blad"
			if tak or powod ~= "brak_walki" or proba == 2 then
				self:ustawPominiecie(tak, powod)
				return
			end
			task.wait(0.6)
		end
	end)
end

-- pominięcie zgłaszamy serwerowi (w tle — pokaz i tak już się skończył): tablica prototypu zwalnia sesję od razu
-- (nastepnaOd = teraz), lasy — gdy ich serwer ma Sygnaly/ZwolnijPoPominieciu (README); odmowa zostawia sesję
function Sesja:zglosPominiecie()
	local f = zdalnaPominiecia()
	if not f then
		self:atrybut("OstatniaOdpowiedzPominiecia", "brak_zdalnej")
		return
	end
	local walka = self.walka
	task.spawn(function()
		local ok, odp = pcall(function()
			return f:InvokeServer("pomin", self.zrodlo)
		end)
		local powod = if ok and type(odp) == "table" then (if odp.ok == true then "ok" else tostring(odp.powod)) else "blad"
		self:atrybut("OstatniaOdpowiedzPominiecia", powod)
		local od = ok and type(odp) == "table" and odp.ok == true and tonumber(odp.nastepnaOd)
		if od and self.walka == walka then
			wolnaOd = od
			self:atrybut("NastepnaWalkaOd", wolnaOd)
		end
	end)
end

------------------------------------------------------------------ start jednej walki (także „Jeszcze raz”)
function Sesja:rozpocznij(walka)
	self.walka = walka
	self.harmonogram = {}
	self.ozdoby = {}
	self.stanEfektow = PlanWalki.nowyStan()
	self.niezgodnosciPaskow = 0
	self.niezgodnosciMany = 0
	self.uzyciaMany = 0
	self.nieznane = 0
	self.odrzuconePominiecia = 0
	self.wskrzeszenia = { gracz = 0, wrog = 0 }
	self.legendy = { gracz = false, wrog = false }
	self.opisyPasywek = { gracz = {}, wrog = {} }
	self.brakiChoreo = 0
	self.bledyObslugi = 0
	self.obsluzone = 0
	self.licznikNazw = 0
	self.licznikUjec = 0
	self.turaStrona, self.turaNr = nil, 0
	self.biezace = nil
	self.nastepne = 1
	self.tau = 0
	self.tauWyniku = 0
	self.pominieto = false
	self.klatki = table.create(2000)
	self.koszt = table.create(2000)
	self.zegarStartu = os.clock()
	self.wstrzasKam = { sila = 0, wiek = 0 }
	self.katyTwarzy = {}
	self.pomiarTwarzy = nil
	self.torUpadku = nil
	self.czasUjeciaPokonanego = nil
	self.upadekWUjeciu = nil
	self.katObjazduMin = nil
	self.obrotZwyciezcy = nil
	self.tObrotu = nil
	self.statDzwiekow = { zagrane = 0, pominiete = 0, maksNaraz = 0 }
	self.zwyciezca = if walka.wynik == "wygrana" then "gracz" else "wrog"
	self.pokonany = inna(self.zwyciezca)
	self:ustawAktorow(walka)
	self:zaplanuj(walka)
	self.final = { radosc = false, baner = false, lup = false, objazd = false, pokonany = false }
	self.wstep = { pokazany = false, schowany = false }
	self.kam = { uj = { typ = "ogolny", prio = 3 }, start = 0, ostatnieCiecie = self.zegar }
	self.ui:usunNapisy()
	self.ui:zerujStatystykiNapisow()
	self.ui:ukryjWynik()
	self.ui:ukryjBaner(true)
	self.ui:ukryjUmiejetnosc()
	self.ui:ustawStrony(walka.strony, { gracz = walka.strony.gracz.id, wrog = walka.strony.wrog.id })
	self.ui:pokazPaski(true)
	-- mana na starcie (z dziennika: strony.*.mana) z progiem pierwszej umiejętności z planu
	local st = self.planWalki.start
	for _, s in { "gracz", "wrog" } do
		self.ui:ustawMane(s, st.mana[s], { prog = st.prog[s], gotowa = st.gotowa[s], natychmiast = true })
	end
	self.ui:ukryjPasywki() -- karteczki poprzedniej walki („Jeszcze raz”); nowe planuje zapowiedzPasywki
	self:zapowiedzPasywki()
	self.ui:ukryjPomin()
	self.ui:ukryjInfoPominiecia()
	self.ui:pokazTempo(self.tempo, function(t)
		self:ustawTempo(t)
		self:dzwiekZdarzenia("przycisk", "przycisk", 1.2)
	end)
	self.ui.skalaZycia = if self.tempo >= 4 then 0.7 elseif self.tempo >= 2 then 0.85 else 1
	self.ui:pokazDzwiek(zapamietaneWyciszenie, function()
		self:przelaczDzwiek()
	end)
	self.zaslonaCel = 0
	self.faza = "odtwarzanie"
	-- D-078: przycisk POMIŃ tylko ze zgodą serwera (odpowiedź z walką albo — walka z lasu — zapytanie prototypu)
	self.zrodlo = self.kontener.Name
	local zgoda = self.pomijanie
	self.pomijanie = false
	if zgoda == nil and self.zrodlo ~= NAZWA_PROTOTYPU then
		self:ustawPominiecie(false, "czekam")
		self:zapytajOPominiecie()
	else
		self:ustawPominiecie(zgoda == true, if zgoda == true then "ok" elseif zgoda == false then "pierwsza_walka" else "brak_zgody")
	end
	self:atrybut("OstatniStan", "odtwarzanie")
	self:atrybut("OstatnieZiarno", walka.ziarno)
	self:atrybut("OstatniaLiczbaZdarzen", #walka.dziennik)
	self:atrybut("OstatniaLiczbaTur", walka.tury)
	self:atrybut("OstatniWybor", string.format("%s/%s/%s", self.wybor.klasa, self.wybor.przeciwnik, self.wybor.poziom))
	self:atrybut("OstatniaLiczbaTurOdtworzona", 0)
end

function Sesja:ustawTempo(t: number)
	if t ~= 1 and t ~= 2 and t ~= 4 then
		return
	end
	self.tempo = t
	zapamietaneTempo = t
	self.ui:ustawTempo(t)
	-- przy ×2 / ×4 napisy żyją krócej (kolejka przy postaci nie rośnie)
	self.ui.skalaZycia = if t >= 4 then 0.7 elseif t >= 2 then 0.85 else 1
	self:atrybut("OstatnieTempo", t)
end

------------------------------------------------------------------ krok sceny (czas sceny d)
function Sesja:krokSceny(d: number, dt: number)
	local tau = math.min(self.tau + d, self.czasKonca)
	self.tau = tau
	-- początki zdarzeń
	while self.nastepne <= #self.plan and self.plan[self.nastepne].t <= tau do
		local ev = self.plan[self.nastepne]
		self.nastepne += 1
		-- najpierw wszystko, co miało się stać przed tym zdarzeniem (przy ×4 kilka zdarzeń mieści się w jednej klatce)
		self:wykonajHarmonogram(ev.t)
		local ok, blad = xpcall(function()
			self:startZdarzenia(ev)
		end, debug.traceback)
		if not ok then
			self.bledyObslugi += 1
			warn("[TestWalki2] Zdarzenie " .. ev.nr .. " (" .. ev.typ .. "): " .. tostring(blad))
		end
	end
	self:wykonajHarmonogram(tau)
	-- wstęp
	if not self.wstep.pokazany and tau >= 0.1 then
		self.wstep.pokazany = true
		if not self.pominieto then
			self.ui:pokazBaner("WALKA!", K.bialy, K.niebieski)
		end
	end
	if self.wstep.pokazany and not self.wstep.schowany and tau >= math.min(0.85, (self.plan[1] and self.plan[1].t or 1) - 0.15) then
		self.wstep.schowany = true
		self.ui:ukryjBaner(false)
	end
	-- finał: ujęcie pokonanego (koniec jego upadku), potem radość zwycięzcy, objazd, baner, łup, panel wyniku
	if self.tPokonany and not self.final.pokonany and tau >= self.tPokonany then
		self.final.pokonany = true
		self.final.pokonanyZegar = self.zegar
		self:proponujUjecie({ typ = "pokonany", prio = 3 })
	end
	-- obrót zwycięzcy do kamery objazdu zaczyna się OBROT_ZWYCIEZCY.przed s przed radością (tylko po ciosie kończącym:
	-- wtedy radość jest ≥ 1,48 s po trafieniu, atak zwycięzcy już się skończył, a pokonany leży)
	if not self.final.obrot and self.tPokonany and tau >= self.tRadosc - OBROT_ZWYCIEZCY.przed then
		self.final.obrot = true
		self.tObrotu = self.tRadosc - OBROT_ZWYCIEZCY.przed
		self:przygotujObjazd() -- kąt objazdu i obrót zwycięzcy do widza (aktualizujPozy)
	end
	if not self.final.radosc and tau >= self.tRadosc then
		self.final.radosc = true
		if self.final.pokonanyZegar then
			self.czasUjeciaPokonanego = self.zegar - self.final.pokonanyZegar
			local tor = self.torUpadku
			self.upadekWUjeciu = tor ~= nil and (tor.zakonczony or tor.czas >= tor.dlugosc - 0.02)
		end
		if not self.final.obrot then
			self:przygotujObjazd() -- kąt objazdu i obrót zwycięzcy do widza (aktualizujPozy)
		end
		self:klip(self.aktorzy[self.zwyciezca], "radosc", { petla = true, przejscie = 0.2 })
		self.ui:ustawTure(self.turaNr)
		self:atrybut("OstatniaLiczbaTurOdtworzona", self.turaNr)
	end
	if not self.final.objazd and tau >= self.tObjazdu then
		self.final.objazd = true
		self:proponujUjecie({ typ = "objazd", prio = 3 })
	end
	local f = tau - self.tRadosc
	if f >= 0.2 and not self.final.baner then
		self.final.baner = true
		self.ui:ukryjPomin()
		self.ui:ukryjInfoPominiecia()
		self.ui:ukryjPasywki()
		self.ui:ukryjTempo()
		self.ui:ukryjDzwiek()
		self.ui:ukryjUmiejetnosc()
		if self.zwyciezca == "gracz" then
			self.ui:pokazBaner("ZWYCIĘSTWO!", K.zolty, K.czerwony, 0.83)
			if not self:odcinekZdarzenia("zwyciestwo") then
				self:melodia("zwyciestwo")
			end
		else
			self.ui:pokazBaner("PORAŻKA!", K.bialy, K.fiolet, 0.83)
			if not self:odcinekZdarzenia("porazka") then
				self:melodia("porazka")
			end
			self:glosPotwora("wrog") -- zwycięski potwór ryczy / warczy w radości (arkusz; bez arkusza nic)
		end
	end
	if f >= 0.3 and not self.final.lup then
		self.final.lup = true
		if self.zwyciezca == "gracz" then
			self:wyrzucLup(false)
		end
	end
	self:aktualizujPozy(tau)
	for _, a in self.aktorzy do
		a.klipy:krok(d)
		a.klipy:zastosuj()
	end
	self.fx:krok(d)
	self:aktualizujKamere(tau, dt)
end

function Sesja:wyrzucLup(natychmiast: boolean)
	local P = self.aktorzy[self.pokonany]
	local zrodlo = P:cfZiemi().Position + Vector3.new(0, P.wpis.wysokosc * 0.4, 0)
	local w = self.aktorzy[self.zwyciezca]
	local cel = P:cfZiemi().Position:Lerp(w:cfZiemi().Position, 0.35)
	local podloga = self.cfSceny.Position.Y + 0.02
	self.liczbaLupu = self.fx:lup(zrodlo, cel, self.walka.lup, natychmiast, podloga)
	self:dzwiekZdarzenia("monety", "lup", 1)
end

------------------------------------------------------------------ pętla klatki
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
	local reczny = self.opcje.reczny and self.faza == "odtwarzanie"
	if not reczny then
		self.zegar += dt
	end
	if self.faza == "odtwarzanie" then
		table.insert(self.klatki, dt)
		local d = 0
		if not self.opcje.reczny then
			d = dt * self:tempoSceny(self.tau)
		end
		self:krokSceny(d, if reczny then 0 else dt)
		self:mierzTwarz()
		if self.opcje.pominPo and self.tau >= self.opcje.pominPo then
			self:pomin(true)
		end
	else
		self.tauWyniku += dt
		for _, a in self.aktorzy do
			a.klipy:krok(dt)
			a.klipy:zastosuj()
		end
		self.fx:krok(dt)
		self:aktualizujKamere(self.tau, dt)
	end
	self:ustawKotwice()
	-- w trybie poklatkowym (testy, filmy) napisy starzeją się tylko przy przewijaniu — w czasie „jak w grze”
	ui:aktualizuj(dt, kamera, if reczny then 0 else dt)
	if self.opcje.etykietaCzasu then
		ui:ustawZegar(string.format("t = %.2f / %.2f s  zd. %s/%d  tura %d  ujęcie %s  ×%d", self.tau, self.walka.czas,
			tostring(self.biezace), #self.plan, self.turaNr, self.kam.uj.typ, self.tempo))
	end
	if self.faza == "odtwarzanie" and self.tau >= self.czasKonca then
		self:pokazWynik()
	end
end

--[[ Prędkość czasu sceny w chwili τ: tempo gracza × zwolnienie (krytyk, nokaut, powalenie). Od chwili tuż przed ciosem
	kończącym (finał) zawsze ×1 z pełnym zwolnieniem. Przy ×2 / ×4 zwolnienie w trakcie walki jest słabsze (wykładnik
	1 / tempo: krytyk 0,22 → 0,47 przy ×2, 0,69 przy ×4) — 17.11.2026, próba 3e: przy ×4 każdy krytyk grał prawie w czasie
	rzeczywistym (0,22 × 4 = 0,88), siedem krytyków najdłuższej walki dokładało ok. 4 s ponad czas dziennika / 4. ]]
function Sesja:tempoSceny(tau: number): number
	local t = if tau >= (self.tempoFinaluOd or math.huge) then 1 else self.tempo
	local z = self:zwolnienie(tau)
	if t > 1 and z < 1 then
		z = z ^ (1 / t)
	end
	return t * z
end

-- tempo sceny teraz: wybór gracza, a od chwili tuż przed ciosem kończącym (finał) zawsze ×1
function Sesja:tempoTeraz(): number
	if self.tau >= (self.tempoFinaluOd or math.huge) then
		return 1
	end
	return self.tempo
end

-- kotwice napisów: prostokąty postaci na ekranie (z wymiarów aktora wokół jego ziemi)
function Sesja:ustawKotwice()
	if not self.aktorzy or not self.ui or not self.ui.kadrPx then
		return
	end
	local kam = self.kamera or workspace.CurrentCamera
	local kotwice = {}
	-- prostokąt walca (szerokość × głębokość aktora) od ziemi do wysokości — ciaśniej niż narożniki pudła, które
	-- z ukosa poszerzały postać o ok. 40% (napisy dużego celu nie mieściły się obok niego); głowa = górna ćwiartka
	local function rzut(cf: CFrame, rx: number, rz: number, y0: number, y1: number)
		local x0, yy0, x1, yy1 = math.huge, math.huge, -math.huge, -math.huge
		local przed = 0
		for i = 0, 7 do
			local r = rad(i * 45)
			for _, y in { y0, y1 } do
				local p, widac = kam:WorldToViewportPoint((cf * CFrame.new(math.cos(r) * rx, y, math.sin(r) * rz)).Position)
				if widac then
					przed += 1
					x0, yy0, x1, yy1 = math.min(x0, p.X), math.min(yy0, p.Y), math.max(x1, p.X), math.max(yy1, p.Y)
				end
			end
		end
		if przed == 0 then
			return nil
		end
		return { x0 = x0, y0 = yy0, x1 = x1, y1 = yy1 }
	end
	for strona, a in self.aktorzy do
		local w = a.wpis
		local cf = a:cfZiemi()
		local r = rzut(cf, w.szerokosc * 0.5, w.glebokosc * 0.5, 0, w.wysokosc)
		if r then
			r.widac = true
			r.glowa = rzut(cf, w.szerokosc * 0.3, w.glebokosc * 0.3, w.wysokosc * 0.74, w.wysokosc)
			kotwice[strona] = r
		end
	end
	self.ui:ustawKotwice(kotwice)
end

-- pomiar twarzy potwora (D5): w chwili trafienia ataku albo tyknięcia na potworze — kąt twarzy z bieżącej kamery
function Sesja:mierzTwarz()
	local p = self.pomiarTwarzy
	if not p or not self.kamera then
		return
	end
	self.pomiarTwarzy = nil
	local poz = self.cfSceny:PointToObjectSpace(self.kamera.CFrame.Position)
	local o = self.kam.ostatnie
	local uG, uW = -1, -1
	if o then
		uG = math.floor(ulamekWKadrze(self:probkiAktora("gracz"), o[1], o[2], o[3]) * 100 + 0.5)
		uW = math.floor(ulamekWKadrze(self:probkiAktora("wrog"), o[1], o[2], o[3]) * 100 + 0.5)
	end
	table.insert(self.katyTwarzy, { kat = math.floor(self:katTwarzy(poz) + 0.5), typ = self.kam.uj.typ, nr = p, uG = uG, uW = uW })
end

-- testy: ręczne przesunięcie czasu (opcje.reczny) o `sekundy` czasu „jak w grze” (tempo gracza, zwolnienia), drobnymi
-- krokami; napisy, przejścia kamery i wstrząs liczą się w tym samym czasie, więc film poklatkowy wygląda jak gra
function Sesja:przewin(sekundy: number)
	local zostalo = sekundy
	while zostalo > 1e-6 and self.faza == "odtwarzanie" do
		local d = math.min(zostalo, 1 / 60)
		zostalo -= d
		self.zegar += d
		self:krokSceny(d * self:tempoSceny(self.tau), d)
		self:mierzTwarz()
		self:ustawKotwice()
		self.ui:aktualizuj(d, self.kamera, d)
		if self.tau >= self.czasKonca then
			self:pokazWynik()
		end
	end
end

-- testy: przewiń do chwili sceny τ (krokami czasu sceny; napisy i kamera dostają odpowiadający im czas „jak w grze”)
function Sesja:przewinDo(cel: number)
	while self.faza == "odtwarzanie" and self.tau < cel - 1e-6 do
		local d = math.min(cel - self.tau, 1 / 60)
		local dr = d / math.max(self:tempoSceny(self.tau), 0.05)
		self.zegar += dr
		self:krokSceny(d, dr)
		self:mierzTwarz()
		self:ustawKotwice()
		self.ui:aktualizuj(dr, self.kamera, dr)
		if self.tau >= self.czasKonca then
			self:pokazWynik()
		end
	end
end

------------------------------------------------------------------ pomiń, wynik, jeszcze raz
-- wymus = tylko testy (opcje.pominPo, Sygnaly/Sterowanie "pomin", true): skraca POKAZ bez zgody; serwer i tak
-- dostaje zgłoszenie i sam decyduje (bez zgody odmawia — sesja walki zostaje)
function Sesja:pomin(wymus: boolean?)
	if self.faza ~= "odtwarzanie" or self.pominieto then
		return
	end
	if not self.pomijanie and not wymus then
		-- D-078: bez zgody serwera (pierwsza walka z gatunkiem) spacja i przycisk nic nie robią — tylko informacja
		self.odrzuconePominiecia += 1
		self:atrybut("OstatnieOdrzuconePominiecia", self.odrzuconePominiecia)
		self.ui:pokazInfoPominiecia(if self.powodPominiecia == "pierwsza_walka" then "PIERWSZE SPOTKANIE — BEZ POMIJANIA"
			else "TEJ WALKI NIE MOŻNA POMINĄĆ", 2)
		return
	end
	self:zglosPominiecie()
	self:dzwiekZdarzenia("przycisk", "przycisk")
	self.pominieto = true
	self.ui:usunNapisy()
	self.ui:ukryjBaner(true)
	self.ui:ukryjUmiejetnosc()
	self.ui:ukryjPasywki()
	self.ui:ukryjInfoPominiecia()
	-- reszta dziennika „po cichu”: stan efektów, tury i paski jak na końcu walki
	while self.nastepne <= #self.plan do
		local ev = self.plan[self.nastepne]
		self.nastepne += 1
		pcall(function()
			self:startZdarzenia(ev)
		end)
	end
	table.clear(self.harmonogram)
	self.ui:ukryjUmiejetnosc()
	self.fx:wyczysc()
	table.clear(self.ozdoby)
	local ost = self.plan[#self.plan].z
	self.ui:ustawZycie("gracz", ost.hp_gracz, true)
	self.ui:ustawZycie("wrog", ost.hp_wrog, true)
	self:ustawManeZdarzenia(self.plan[#self.plan], "obie", false)
	for _, s in { "gracz", "wrog" } do
		if self.wskrzeszenia[s] > 0 then
			self.ui:ustawLegende(s, self.legendy[s], true)
		end
	end
	self.stanEfektow = PlanWalki.nowyStan()
	self:odswiezEfekty()
	self.ui:ustawTure(self.turaNr)
	-- aktorzy na miejsca: pokonany leży, zwycięzca się cieszy
	for strona, a in self.aktorzy do
		a:ustaw(self:cfDomu(strona))
	end
	local P = self.aktorzy[self.pokonany]
	if P:maKlip("upadek") then
		local dl = P.klipy:dlugoscKlipu(P:maKlip("upadek")) or 1
		P:graj("upadek", { przejscie = 0, odCzasu = dl })
	end
	self.aktorzy[self.zwyciezca]:graj("radosc", { przejscie = 0, petla = true })
	self.final = { radosc = true, baner = true, lup = true, objazd = true, pokonany = true, obrot = true }
	self.tau = self.czasKonca
	-- objazd i zwycięzca obrócony do widza, jak w zwykłym finale
	self:przygotujObjazd()
	do
		local zw = self.zwyciezca
		local x, kier, yaw = self.geo.x[zw], self.geo.kier[zw], self.obrotZwyciezcy or 0
		self.aktorzy[zw]:ustaw(self.cfSceny * CFrame.lookAt(Vector3.new(x, 0, 0), Vector3.new(x + kier * math.cos(yaw), 0, math.sin(yaw))))
	end
	self.kam.uj = { typ = "objazd", prio = 3 }
	self.kam.start = self.tau
	self.kam.od = nil
	self.tauWyniku = 1.6
	self.wstrzasKam.sila = 0
	if self.zwyciezca == "gracz" then
		self:wyrzucLup(true)
	end
end

function Sesja:pokazWynik()
	self.faza = "wynik"
	local ui = self.ui
	ui:ukryjPomin()
	ui:ukryjInfoPominiecia()
	ui:ukryjPasywki()
	ui:ukryjTempo()
	ui:ukryjDzwiek()
	-- pomiary poprawek z 15.11 (D1, D3, D4, D5)
	self:atrybut("OstatnieUjeciePokonanego", if self.czasUjeciaPokonanego then math.floor(self.czasUjeciaPokonanego * 100 + 0.5) / 100 else -1)
	self:atrybut("OstatniUpadekWUjeciu", self.upadekWUjeciu == true)
	self:atrybut("OstatniKatObjazdu", self.katObjazduMin or -1)
	local sn = ui.statNapisow or {}
	self:atrybut("OstatnieNapisyMaksNaraz", sn.maksNaraz or 0)
	self:atrybut("OstatnieNapisyNakladania", sn.nakladania or 0)
	self:atrybut("OstatnieNapisyNaCelu", sn.naCelu or 0)
	self:atrybut("OstatnieNapisyNaInnym", sn.naInnym or 0)
	self:atrybut("OstatnieNapisyNaGlowie", math.floor((sn.naGlowie or 0) * 100 + 0.5) / 100)
	self:atrybut("OstatnieNapisyPokazane", sn.pokazane or 0)
	local sd = self.statDzwiekow or {}
	self:atrybut("OstatnieDzwiekiZagrane", sd.zagrane or 0)
	self:atrybut("OstatnieDzwiekiPominiete", sd.pominiete or 0)
	self:atrybut("OstatnieDzwiekiMaksNaraz", sd.maksNaraz or 0)
	-- własne dźwięki: odcinki arkusza (efekt, region w pliku, odchylenie szczytu od trafienia w s czasu rzeczywistego)
	if self.arkusz then
		local ark = self.arkusz
		-- ile razy arkusz nie był wczytany i zagrał dźwięk wbudowany (0 = własne dźwięki grały od początku)
		self:atrybut("OstatniArkuszNiewczytany", ark.niewczytane or 0)
		local lista = {}
		for _, w in ark.log do
			local traf = w.nr and ark.trafienia and ark.trafienia[w.nr]
			table.insert(lista, { e = w.e, od = w.od, p0 = w.p0, p1 = w.p1, nr = w.nr,
				dSzczyt = if traf then math.floor((w.szczyt - traf) * 1000 + 0.5) / 1000 else nil })
		end
		self:atrybut("OstatnieOdcinkiArkusza", game:GetService("HttpService"):JSONEncode(lista))
		self:atrybut("OstatnieRegionyArkusza", ark.regiony == true)
	else
		self:atrybut("OstatnieOdcinkiArkusza", "")
	end
	local katy = {}
	for _, k in self.katyTwarzy or {} do
		table.insert(katy, string.format("%d:%s:%d:%d:%d", k.nr, k.typ, k.kat, k.uG or -1, k.uW or -1))
	end
	self:atrybut("OstatnieKatyTwarzy", table.concat(katy, ","))
	ui:ukryjBaner(false)
	ui:ukryjUmiejetnosc()
	local klatki = self.klatki
	local n = #klatki
	local suma, maks = 0, 0
	for _, dt in klatki do
		suma += dt
		maks = math.max(maks, dt)
	end
	local pos = table.clone(klatki)
	table.sort(pos)
	local p95 = if n > 0 then pos[math.clamp(math.ceil(n * 0.95), 1, n)] else 0
	local function ms(x)
		return math.floor(x * 100000 + 0.5) / 100
	end
	self:atrybut("OstatniCzasTrwania", math.floor((os.clock() - self.zegarStartu) * 100 + 0.5) / 100)
	self:atrybut("OstatniaSredniaKlatki", if n > 0 then ms(suma / n) else 0)
	self:atrybut("OstatniP95Klatki", ms(p95))
	self:atrybut("OstatniaMaksKlatki", ms(maks))
	self:atrybut("OstatniaLiczbaKlatek", n)
	local koszt = table.clone(self.koszt or {})
	table.sort(koszt)
	local sk = 0
	for _, c in koszt do
		sk += c
	end
	local nk = #koszt
	self:atrybut("OstatniKosztSkryptuSredni", if nk > 0 then ms(sk / nk) else 0)
	self:atrybut("OstatniKosztSkryptuP95", if nk > 0 then ms(koszt[math.clamp(math.ceil(nk * 0.95), 1, nk)]) else 0)
	self:atrybut("OstatniKosztSkryptuMaks", if nk > 0 then ms(koszt[nk]) else 0)
	self:atrybut("OstatniaLiczbaInstancji", self.utworzono + ui.utworzono + (self.fx and self.fx.utworzono or 0))
	self:atrybut("OstatnioPominieto", self.pominieto)
	self:atrybut("OstatniWynik", self.walka.wynik)
	self:atrybut("OstatniaLiczbaUjec", self.licznikUjec)
	self:atrybut("OstatniCzasSerwera", math.floor((self.czasSerwera or 0) * 10 + 0.5) / 10)
	self:atrybut("OstatniaLiczbaSchowanych", self.liczbaSchowanych or 0)
	self:atrybut("OstatniaNiezgodnoscPaskow", self.niezgodnosciPaskow)
	-- v3: mana, wskrzeszenia, pasywki, dziennik, pomijanie (testy w Studio: testy/test_v3_play.py)
	self:atrybut("OstatniaNiezgodnoscMany", self.niezgodnosciMany)
	self:atrybut("OstatnieUzyciaMany", self.uzyciaMany)
	self:atrybut("OstatnieWskrzeszenia", string.format("%d/%d", self.wskrzeszenia.gracz, self.wskrzeszenia.wrog))
	self:atrybut("OstatnieNieznaneZdarzenia", self.nieznane)
	self:atrybut("OstatnieOstrzezeniaDziennika", #(self.ostrzezeniaDziennika or {}))
	self:atrybut("OstatniBladDziennika", self.bladDziennika or "")
	local nazwyPasywek = {}
	for _, s in { "gracz", "wrog" } do
		for _, o in self.opisyPasywek[s] do
			table.insert(nazwyPasywek, s .. ":" .. o.id)
		end
	end
	self:atrybut("OstatniePasywki", table.concat(nazwyPasywek, ","))
	self:atrybut("OstatniaManaKoniec", string.format("%s/%s", tostring(ui:mana("gracz")), tostring(ui:mana("wrog"))))
	self:atrybut("OstatnieBrakiChoreografii", self.brakiChoreo)
	self:atrybut("OstatnieBledyObslugi", self.bledyObslugi)
	self:atrybut("OstatniaLiczbaObsluzonych", self.obsluzone)
	self:atrybut("OstatniaLiczbaTurOdtworzona", self.turaNr)
	self:atrybut("OstatniePaskiKoniec", string.format("%s/%s", tostring(ui:zycie("gracz")), tostring(ui:zycie("wrog"))))
	self:atrybut("OstatnieTempo", self.tempo)
	self:atrybut("LicznikOdtworzen", (self.kontener:GetAttribute("LicznikOdtworzen") or 0) + 1)
	self:atrybut("OstatniStan", "wynik")
	ui:pokazWynik(self.walka, function()
		self:jeszczeRaz()
	end, function()
		self:zakoncz("zamknieto")
	end)
	-- P2 (las_potwory/PROJEKT.md, rozdz. 6): opcja bezPowtorki chowa JESZCZE RAZ (walka z potworem w lesie: rewanż = E)
	if self.opcje.bezPowtorki then
		local przycisk = ui.wynik and ui.wynik.jeszcze -- TextButton „Przycisk”; jego rodzic to ramka „JeszczeRaz” z cieniem
		if przycisk and przycisk.Parent then
			przycisk.Parent.Visible = false
		end
	end
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
	if self.faza ~= "wynik" or wolnaZa() > 0 or self.opcje.bezPowtorki then
		return
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
				warn("[TestWalki2] Nie udało się rozpocząć kolejnej walki: " .. tostring(wynik))
				self:zakoncz("blad")
			end
			return
		end
		while self.zaslona < 0.98 and not self.zakonczona do
			task.wait()
		end
		if not self.zakonczona then
			local ok2, blad = xpcall(function()
				self:rozpocznij(wynik)
			end, debug.traceback)
			if not ok2 then
				warn("[TestWalki2] Nie udało się przygotować walki: " .. tostring(blad))
				self:zakoncz("blad")
			end
		end
	end)
end

function Sesja:start()
	local t0 = os.clock()
	self:atrybut("OstatniStan", "prosba")
	local playerGui = self.gracz:WaitForChild("PlayerGui")
	self.ui = Interfejs.nowy(playerGui, U)
	self:posprzataj(function()
		self.ui:zniszcz()
	end)
	self.ui:pokazPaski(false)
	self.zaslona, self.zaslonaCel = 0, 1
	RunService:BindToRenderStep(KROK, Enum.RenderPriority.Camera.Value + 1, function(dt)
		local t1 = os.clock()
		local ok, blad = xpcall(function()
			self:krok(dt)
		end, debug.traceback)
		if self.faza == "odtwarzanie" and self.koszt then
			table.insert(self.koszt, os.clock() - t1)
		end
		if not ok then
			warn("[TestWalki2] Błąd w klatce cutscenki: " .. tostring(blad))
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
	while self.zaslona < 0.98 do
		task.wait()
		if self.zakonczona then
			error("przerwano")
		end
	end
	-- sesję zamknięto w czasie prośby do serwera (17.11.2026, próba lasu-pasa: „zamknij” zaraz po E) — bez tej kontroli
	-- scena, kamera skryptowa i chowanie obcych powstawały PO sprzątaniu i zostawały (E przy Kamieniu nie działało,
	-- widoki starego lasu schowane)
	if self.zakonczona then
		error("przerwano")
	end
	self:przygotujScene()
	self:posprzataj(function()
		self:usunAktorow()
	end)
	self:przejmijKamere()
	self:atrybut("OstatniCzasPrzygotowania", math.floor((os.clock() - t0) * 1000 + 0.5))
	self:rozpocznij(walka)
end

function Sesja:zakoncz(powod: string)
	if self.zakonczona then
		return
	end
	self.zakonczona = true
	self.faza = "koniec"
	if sesja == self then
		sesja = nil
	end
	if powod == "zamknieto" then
		local playerGui = self.gracz:FindFirstChildOfClass("PlayerGui")
		if playerGui then
			local przejscie = Instance.new("ScreenGui")
			przejscie.Name = "TestWalki2Przejscie"
			przejscie.IgnoreGuiInset = true
			przejscie.ResetOnSpawn = false
			przejscie.DisplayOrder = 103
			local czern = Instance.new("Frame")
			czern.Size = UDim2.fromScale(1, 1)
			czern.BackgroundColor3 = Color3.new(0, 0, 0)
			czern.BorderSizePixel = 0
			czern.Parent = przejscie
			przejscie.Parent = playerGui
			local tw = TweenService:Create(czern, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { BackgroundTransparency = 1 })
			tw.Completed:Once(function()
				przejscie:Destroy()
			end)
			tw:Play()
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
			warn("[TestWalki2] Sprzątanie po cutscence: " .. tostring(blad))
		end
	end
	table.clear(self.sprzatanie)
	self:atrybut("OstatniStan", powod)
	-- odmowa serwera (po WALCZ albo JESZCZE RAZ): klient pokazuje graczowi powód (KlientWalki2)
	if powod == "odmowa" and Odtwarzacz.naOdmowe then
		task.spawn(Odtwarzacz.naOdmowe, self.odmowa or "odmowa")
	end
end

------------------------------------------------------------------ API
function Odtwarzacz.uruchom(kontener: Instance, wybor: any, opcje: any?): boolean
	if sesja then
		return false
	end
	local gracz = Players.LocalPlayer
	if not gracz then
		return false
	end
	if wolnaZa() > 0 then
		pcall(function()
			kontener:SetAttribute("OstatniaOdmowa", "walka_trwa_lokalnie")
		end)
		if Odtwarzacz.naOdmowe then
			task.spawn(Odtwarzacz.naOdmowe, "walka_trwa_lokalnie")
		end
		return false
	end
	local o = if type(opcje) == "table" then opcje else {}
	local w = if type(wybor) == "table" then wybor else {}
	local tempo = tonumber(o.tempo) or zapamietaneTempo
	if tempo ~= 1 and tempo ~= 2 and tempo ~= 4 then
		tempo = 1
	end
	local s = setmetatable({
		kontener = kontener, gracz = gracz, opcje = o, tempo = tempo,
		wybor = { klasa = w.klasa, przeciwnik = w.przeciwnik, poziom = w.poziom, zestaw = if type(w.zestaw) == "string" then w.zestaw else nil },
		sprzatanie = {}, utworzono = 0, faza = "prosba", zakonczona = false, zaslona = 0, zaslonaCel = 0, tau = 0, tauWyniku = 0,
		licznikUjec = 0, zegar = 0,
	}, Sesja)
	sesja = s
	local ok, blad = xpcall(function()
		s:start()
	end, debug.traceback)
	if not ok then
		if s.odmowa then
			s:zakoncz("odmowa")
		else
			if not s.zakonczona then
				warn("[TestWalki2] Nie udało się uruchomić cutscenki: " .. tostring(blad))
			end
			s:zakoncz("blad")
		end
	end
	return ok
end

function Odtwarzacz.pomin(wymus: boolean?)
	if sesja then
		sesja:pomin(wymus == true)
	end
end
function Odtwarzacz.zamknij()
	if sesja then
		sesja:zakoncz("zamknieto")
	end
end
function Odtwarzacz.jeszczeRaz()
	if sesja then
		sesja:jeszczeRaz()
	end
end
function Odtwarzacz.ustawTempo(t: number)
	if sesja then
		sesja:ustawTempo(t)
	else
		zapamietaneTempo = t
	end
end
function Odtwarzacz.czyTrwa(): boolean
	return sesja ~= nil
end
function Odtwarzacz.wolnaZa(): number
	return wolnaZa()
end
function Odtwarzacz.przewin(sekundy: number)
	if sesja and sesja.faza == "odtwarzanie" then
		sesja:przewin(sekundy)
	end
end
function Odtwarzacz.przewinDo(tau: number)
	if sesja and sesja.faza == "odtwarzanie" then
		sesja:przewinDo(tau)
	end
end
-- odmowa serwera: funkcja(powód) ustawiana przez KlientWalki2 (komunikat dla gracza)
Odtwarzacz.naOdmowe = nil :: ((string) -> ())?
Odtwarzacz.pokazLiczbe = Sesja.pokazLiczbe
Odtwarzacz.wygladEfektu = Sesja.wygladEfektu

-- testy: czy aktorzy są w kadrze i czy jeden nie zasłania drugiego (z bieżącej kamery odtwarzacza).
-- Dla każdej strony: ułamek widocznych części aktora w kadrze 16:9 i ułamek NIEZASŁONIĘTYCH przez drugiego aktora
-- (promień z kamery do środka części przecina części drugiego aktora). Części klonów mają CanQuery = false —
-- na czas pomiaru włączamy je lokalnie i przywracamy.
function Odtwarzacz.kadr()
	local s = sesja
	if not s or not s.aktorzy or not s.ui then
		return nil
	end
	local kam = s.kamera or workspace.CurrentCamera
	local r = s.ui.kadrPx
	local o = kam.CFrame.Position
	local wynik = {}
	-- efekt z klipu, który TRZYMA albo trafia cel (korzenie Strażnika wokół celu, kałuża i bańka slime'a — kości z
	-- wydłużeniem w bieżącym klipie atakującego) nie zasłania celu w sensie kadru: to treść ujęcia (17.11.2026)
	local efektowe: { [string]: boolean } = {}
	local ev = s.plan and s.biezace and s.plan[s.biezace]
	if ev and ev.styl == "w_klipie" and ev.akcja then
		local A = s.aktorzy[ev.z.kto]
		local klip = A and A:maKlip(ev.akcja)
		local K = A and A.klipy
		local wybrane: { [number]: boolean } = {}
		for _, w in (klip and K.wydluzenia and K.wydluzenia[klip]) or {} do
			for _, idx in w.kosci or {} do
				wybrane[idx] = true -- indeksy kości (dane klipów); razem z dziećmi (korzeń K1A → K1B → K1C)
			end
		end
		if next(wybrane) ~= nil then
			for nazwa, idx in K.nazwyKosci do
				local i = idx
				while i and i ~= 0 do
					if wybrane[i] then
						efektowe[nazwa] = true
						break
					end
					i = K.rodzice[i]
				end
			end
		end
	end
	local function czescEfektu(c: BasePart): boolean
		if next(efektowe) == nil then
			return false
		end
		local sp = c:FindFirstChildOfClass("WeldConstraint")
		local kosc = if sp and sp.Part0 then sp.Part0.Name else c.Name
		return efektowe[kosc] == true
	end
	for strona, a in s.aktorzy do
		local inny = s.aktorzy[inna(strona)]
		local zmienione = {}
		local wylaczone = {}
		for _, c in inny.model:GetDescendants() do
			if c:IsA("BasePart") then
				if czescEfektu(c) then
					if c.CanQuery then
						c.CanQuery = false
						table.insert(wylaczone, c)
					end
				elseif not c.CanQuery then
					c.CanQuery = true
					table.insert(zmienione, c)
				end
			end
		end
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Include
		params.FilterDescendantsInstances = { inny.model }
		local n, wKadrze, odsloniete = 0, 0, 0
		for _, c in a.model:GetDescendants() do
			if c:IsA("BasePart") and c ~= a.hrp and c.Transparency < 0.9 then
				n += 1
				local p, przed = kam:WorldToViewportPoint(c.Position)
				if przed and p.X >= r.x and p.X <= r.x + r.sz and p.Y >= r.y and p.Y <= r.y + r.wys then
					wKadrze += 1
					local traf = workspace:Raycast(o, c.Position - o, params)
					if not traf then
						odsloniete += 1
					end
				end
			end
		end
		for _, c in zmienione do
			c.CanQuery = false
		end
		for _, c in wylaczone do
			c.CanQuery = true
		end
		wynik[strona] = { czesci = n, wKadrze = if n > 0 then wKadrze / n else 0, odsloniete = if n > 0 then odsloniete / n else 0 }
	end
	wynik.ujecie = s.kam and s.kam.uj and s.kam.uj.typ
	wynik.tau = s.tau
	-- kąt twarzy potwora z bieżącej kamery (0° = w twarz, 90° = profil) i najbliższa część pokonanego od kamery
	wynik.katTwarzy = s:katTwarzy(s.cfSceny:PointToObjectSpace(kam.CFrame.Position))
	if s.zwyciezca then
		wynik.katTwarzyZwyciezcy = s:katTwarzyStrony(s.zwyciezca, s.cfSceny:PointToObjectSpace(kam.CFrame.Position))
	end
	local P = s.aktorzy[s.pokonany]
	if P then
		local najblizej = math.huge
		for _, c in P.model:GetDescendants() do
			if c:IsA("BasePart") and c ~= P.hrp and c.Transparency < 0.9 then
				local lok = c.CFrame:PointToObjectSpace(o)
				local h = c.Size / 2
				local dx = math.max(math.abs(lok.X) - h.X, 0)
				local dy = math.max(math.abs(lok.Y) - h.Y, 0)
				local dz = math.max(math.abs(lok.Z) - h.Z, 0)
				najblizej = math.min(najblizej, math.sqrt(dx * dx + dy * dy + dz * dz))
			end
		end
		wynik.pokonanyOdKamery = najblizej
		wynik.zwyciezcaOdKamery = (s.aktorzy[s.zwyciezca]:cfZiemi().Position - o).Magnitude
	end
	return wynik
end

-- testy: napisy przy postaciach widoczne teraz (tekst, styl, postać, prostokąt w pikselach) i kotwice postaci
function Odtwarzacz.napisy()
	local s = sesja
	local lista = {}
	if s and s.ui then
		for _, p in s.ui.prostokatyNapisow or {} do
			local n = p.n
			if n.pole and n.pole.Parent then
				table.insert(lista, { tekst = n.tekst, styl = n.styl, klucz = n.klucz, wiek = n.wiek, zycie = n.zycie,
					x0 = p.x0, y0 = p.y0, x1 = p.x1, y1 = p.y1, widac = n.pole.Visible, widoczny = p.widoczny,
					przezr = n.napis.TextTransparency, skala = n.skala.Scale })
			end
		end
		local czekajace = {}
		for _, n in s.ui.kolejkaNapisow do
			table.insert(czekajace, { tekst = n.tekst, styl = n.styl, klucz = n.klucz, czeka = n.czeka })
		end
		return { napisy = lista, czekajace = czekajace, kotwice = s.ui.kotwice, kadr = s.ui.kadrPx,
			tau = s.tau, biezace = s.biezace }
	end
	return { napisy = lista }
end

-- stan do testów (bez instancji): faza, czas, bieżące zdarzenie, paski, kamera
function Odtwarzacz.stan()
	local s = sesja
	if not s then
		return { faza = "brak" }
	end
	local kam = workspace.CurrentCamera
	local wynik = {
		faza = s.faza, tau = s.tau, czas = s.walka and s.walka.czas, biezace = s.biezace, zdarzen = s.plan and #s.plan,
		tura = s.turaNr, tempo = s.tempo, ujecie = s.kam and s.kam.uj and s.kam.uj.typ,
		paskiGracz = s.ui and s.ui:zycie("gracz"), paskiWrog = s.ui and s.ui:zycie("wrog"),
		kamera = { kam.CFrame.Position.X, kam.CFrame.Position.Y, kam.CFrame.Position.Z },
		patrz = { (kam.CFrame.Position + kam.CFrame.LookVector * 10).X, (kam.CFrame.Position + kam.CFrame.LookVector * 10).Y,
			(kam.CFrame.Position + kam.CFrame.LookVector * 10).Z },
		fov = kam.FieldOfView,
		czasKonca = s.czasKonca, tPokonany = s.tPokonany, tRadosc = s.tRadosc, tempoTeraz = s.walka and s:tempoTeraz(),
		-- plan prędkości sceny (testy: oczekiwany czas odtwarzania przy danym tempie — testy/test_walki_play.py, 3e)
		zwolnienia = s.zwolnienia, tempoFinaluOd = if s.tempoFinaluOd and s.tempoFinaluOd < math.huge then s.tempoFinaluOd else nil,
		zegar = s.zegar, pokonany = s.pokonany, zwyciezca = s.zwyciezca,
		-- v3: mana na paskach, ikony efektów (tury, znaczek), pomijanie, wskrzeszenia
		manaGracz = s.ui and s.ui:mana("gracz"), manaWrog = s.ui and s.ui:mana("wrog"),
		pomijanie = s.pomijanie == true, powodPominiecia = s.powodPominiecia,
		pomijanieNaEkranie = s.ui ~= nil and s.ui.pomin.Visible, wskrzeszenia = s.wskrzeszenia,
	}
	if s.ui and s.stanEfektow then
		wynik.efekty = { gracz = s:efektyStrony("gracz"), wrog = s:efektyStrony("wrog") }
		local m = { gracz = s.ui.paski.gracz.mana, wrog = s.ui.paski.wrog.mana }
		wynik.manaGotowa = { gracz = m.gracz.gotowa, wrog = m.wrog.gotowa }
		wynik.manaProg = { gracz = m.gracz.progWartosc, wrog = m.wrog.progWartosc }
	end
	if s.plan and s.biezace then
		local ev = s.plan[s.biezace]
		wynik.typ = ev.typ
		wynik.umiejetnosc = ev.z.umiejetnosc
		wynik.t = ev.t
		wynik.trafienie = if ev.eHit then ev.t + ev.eHit else nil
		wynik.styl = ev.styl
		wynik.lot = ev.lot
		wynik.wypuszczenie = if ev.tWypuszczenia then ev.t + ev.tWypuszczenia elseif ev.eRel and ev.lot and ev.lot > 0 then ev.t + ev.eRel else nil
		wynik.cel = ev.z.cel
		wynik.krytyk = ev.z.krytyk == true
		local pt = ev.punktTrafienia
		wynik.punktTrafienia = if pt then { pt.X, pt.Y, pt.Z } else nil
	end
	local tor = s.torUpadku
	if tor then
		wynik.upadek = { czas = tor.czas, dlugosc = tor.dlugosc, koniec = tor.zakonczony }
	end
	return wynik
end

return Odtwarzacz
