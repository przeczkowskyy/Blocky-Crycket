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

	API:  uruchom(kontener, wybor, opcje?) → boolean | pomin() | zamknij() | jeszczeRaz() | ustawTempo(t) | czyTrwa()
	      wolnaZa() → s | stan() → tabela (do testów) | przewin(s) (tylko opcje.reczny)
	opcje (testy): tempo (startowe), reczny (czas stoi; przesuwa go przewin), etykietaCzasu, pominPo, zamknijPo, obrys.
	Wynik ostatniego odtworzenia → atrybuty kontenera (u klienta): Ostatni* (patrz Sesja:pokazWynik).
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

local Odtwarzacz = {}
local sesja = nil
local wolnaOd = 0
local zapamietaneTempo = 1

local function wolnaZa(): number
	return math.max(0, wolnaOd - workspace:GetServerTimeNow())
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
	local wyklucz = { self.scena }
	for _, n in { "Arena", "Aktorzy", "Galeria" } do
		local d = self.kontener:FindFirstChild(n)
		if d then
			table.insert(wyklucz, d)
		end
	end
	local plyta = workspace:FindFirstChild("Baseplate")
	if plyta then
		table.insert(wyklucz, plyta)
	end
	table.insert(wyklucz, workspace.Terrain)
	local filtr = OverlapParams.new()
	filtr.FilterType = Enum.RaycastFilterType.Exclude
	filtr.FilterDescendantsInstances = wyklucz
	local pudlo = CFrame.new(U.OBSZAR_SRODEK)
	self.skanujObcych = function()
		for _, czesc in workspace:GetPartBoundsInBox(pudlo, U.OBSZAR_ROZMIAR, filtr) do
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
		-- tylko wybór z listy (trzy napisy); żadnych liczb
		local odpowiedz = zdalna:InvokeServer({ klasa = self.wybor.klasa, przeciwnik = self.wybor.przeciwnik, poziom = self.wybor.poziom })
		self.czasSerwera = (os.clock() - t) * 1000
		if self.zakonczona then
			error("przerwano")
		end
		local powod = if type(odpowiedz) == "table" then odpowiedz.powod else nil
		local ponowZa = if type(odpowiedz) == "table" then tonumber(odpowiedz.ponowZa) else nil
		if type(odpowiedz) == "table" and odpowiedz.ok and odpowiedz.walka then
			local dobre, opis = Dziennik.sprawdz(odpowiedz.walka)
			if not dobre then
				error("serwer przysłał niepoprawny dziennik: " .. tostring(opis))
			end
			wolnaOd = tonumber(odpowiedz.nastepnaOd) or 0
			self:atrybut("NastepnaWalkaOd", wolnaOd)
			return odpowiedz.walka
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
function Sesja:przygotujScene()
	self.scena = self:nowa("Folder", { Name = "ScenaLokalna" }, self.kontener)
	self:posprzataj(function()
		self.scena:Destroy()
	end)
	-- szablony aktorów w galerii chowamy tylko u tego klienta
	local szablony = self.kontener:FindFirstChild("Aktorzy")
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
	self:schowajObcych()
	self.dzwieki = {}
	if U.DZWIEKI_WLACZONE then
		for nazwa, id in U.DZWIEKI do
			self.dzwieki[nazwa] = self:nowa("Sound", { Name = nazwa, SoundId = id, Volume = 0.45 }, self.ui.gui)
		end
	end
end

function Sesja:dzwiek(nazwa: string, szybkosc: number?)
	local d = self.dzwieki and self.dzwieki[nazwa]
	if d and not self.pominieto then
		d.PlaybackSpeed = (szybkosc or 1) * math.min(self.tempo, 1.5)
		d:Play()
	end
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
	self.cfSceny = U.scena()
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
	-- przód tułowia: pierś albo ok. ¼ głębokości bryły (brzuch Trolla wystaje dalej niż punkt piersi)
	local piersB = math.max(0.5, wb.piersPrzod or 0.6, (wb.glebokosc or 0) * 0.28)
	local piersA = math.max(0.5, wa.piersPrzod or 0.6, (wa.glebokosc or 0) * 0.22)
	local d = zasieg + piersB - 0.15
	return math.max(d, piersA + piersB + 0.5)
end

------------------------------------------------------------------ plan: zdarzenia, tury, efekty, ujęcia, zwolnienia
local AKCJE_TURY = { cios = true, krytyk = true, blok = true, unik = true, umiejetnosc = true, utrata_tury = true, efekt_tick = true }
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
	local tura, stronaTury = 0, nil
	local zwolnienia = {}
	local ujecia = { { start = 0, typ = "ogolny", prio = 3 } }
	local losU = Random.new(walka.ziarno % 2147483647)
	local ostatnieTyp = "ogolny"
	local licznikZwyklych = 0
	for i, z in walka.dziennik do
		local ev = { nr = i, z = z, typ = z.typ, kto = z.kto, cel = z.cel, t = z.t, trwa = z.trwa, koniec = z.t + z.trwa }
		if AKCJE_TURY[z.typ] and z.kto ~= stronaTury then
			tura += 1
			stronaTury = z.kto
			ev.nowaTura = true
		end
		ev.tura = tura
		ev.stronaTury = stronaTury
		ev.obsluga = Ch.ZDARZENIA[z.typ]
		ev.smiertelny = i == n and (z.hp_gracz == 0 or z.hp_wrog == 0)
		ev.atak = ATAKI[z.typ] or (z.typ == "umiejetnosc" and z.kto ~= z.cel)
		ev.naSiebie = z.typ == "umiejetnosc" and z.kto == z.cel
		if ev.atak or ev.naSiebie then
			local klucz = self.aktorzy[z.kto].klucz
			ev.choreo, ev.znana = self:wpisChoreo(z, klucz)
			ev.styl = if ev.naSiebie then "na_siebie" else (ev.choreo.styl or "wrecz")
			self:policzCzasy(ev)
			local krytyk = z.krytyk == true
			if krytyk then
				local zw = Ch.ZWOLNIENIE.krytyk
				table.insert(zwolnienia, { od = ev.t + ev.eHit - zw.przed, ["do"] = ev.t + ev.eHit + zw.po, tempo = zw.tempo })
			elseif ev.smiertelny then
				local zw = Ch.ZWOLNIENIE.nokaut
				table.insert(zwolnienia, { od = ev.t + ev.eHit - zw.przed, ["do"] = ev.t + ev.eHit + zw.po, tempo = zw.tempo })
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
			if (z.krytyk or ev.smiertelny) and ev.styl ~= "pocisk" and ev.styl ~= "chmura" then
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
		elseif z.typ == "efekt_tick" and ev.nowaTura then
			uj = { typ = "efekt", atakujacy = A, broniacy = A, prio = if ev.smiertelny then 3 else 1 }
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
	-- finał: objazd po upadku
	self.tObjazdu = if ostatni.eHit then ostatni.t + ostatni.eHit + 0.7 else ostatni.koniec
	self.plan = plan
	self.zwolnienia = zwolnienia
	self.ujeciaPlan = ujecia
end

-- czasy ataku / umiejętności w zdarzeniu (sekundy od jego początku, w czasie sceny)
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
	local lot = 0
	local wyrownanie = eHit
	if styl == "pocisk" then
		local pr = ev.choreo.predkosc or 30
		lot = math.clamp(self.geo.S / pr, 0.2, 0.6)
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
		ev.tDoskoku = math.clamp(eHit - 0.04 - eStart * 0.3, 0.22, 0.42)
		if styl == "skok" then
			ev.tDoskoku = math.clamp(eHit * 0.75, 0.35, 0.8)
		end
		ev.tPowrotu = math.clamp(trwa - eHit - 0.3, 0.2, 0.5)
	else
		ev.doskok = 0
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
function Sesja:efektyStrony(strona: string)
	local lista = {}
	for _, e in self.stanEfektow[strona] do
		local ch = Ch.EFEKTY[e.id] or Ch.EFEKT_ZASTEPCZY
		table.insert(lista, { id = e.id, ikona = ch.ikona, kolor = ch.kolor, tury = math.max(1, e.tury), zapas = e.zapas })
	end
	return lista
end

function Sesja:odswiezEfekty()
	local zapas = { gracz = 0, wrog = 0 }
	for strona, lista in self.stanEfektow do
		for _, e in lista do
			zapas[strona] += e.zapas or 0
		end
		self.ui:ustawEfekty(strona, self:efektyStrony(strona))
		self.ui:ustawTarcze(strona, zapas[strona])
	end
end

function Sesja:koniecTury(strona: string, tura: number)
	for _, e in self.stanEfektow[strona] do
		if e.odTury ~= tura then
			e.tury -= 1
		end
	end
end

function Sesja:pochlon(strona: string, ile: number)
	if ile <= 0 then
		return
	end
	for _, e in self.stanEfektow[strona] do
		if e.zapas and e.zapas > 0 and ile > 0 then
			local m = math.min(e.zapas, ile)
			e.zapas -= m
			ile -= m
		end
	end
end

-- umiejętność, która nałożyła efekt (efekt_nalozony idzie zaraz po swoim ataku albo umiejętności); "" = zwykły cios
function Sesja:zrodloEfektu(ev): string
	local i = ev.nr - 1
	while i >= 1 do
		local p = self.plan[i]
		if p.typ ~= "efekt_nalozony" then
			return if p.z.kto == ev.z.kto then p.z.umiejetnosc else ""
		end
		i -= 1
	end
	return ""
end

-- wygląd ozdoby efektu: ten sam efekt może wyglądać inaczej zależnie od umiejętności (spowolnienie: lód przy lodowym
-- pocisku, pnącza przy uścisku korzeni, gwiazdki przy ogłuszeniu) — Choreografie.WYGLAD_SPOWOLNIENIA
function Sesja.wygladEfektu(id: string, umiejetnosc: string?): string
	local ch = Ch.EFEKTY[id] or Ch.EFEKT_ZASTEPCZY
	if id == "spowolnienie" and umiejetnosc and Ch.WYGLAD_SPOWOLNIENIA[umiejetnosc] then
		return Ch.WYGLAD_SPOWOLNIENIA[umiejetnosc]
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
	self:pochlon(z.cel, z.pochloniete)
	self:odswiezEfekty()
	if cicho then
		return
	end
	local D = self.aktorzy[z.cel]
	local glowa = self:glowa(z.cel)
	local piers = self:piers(z.cel)
	local s = math.clamp(D.wpis.wysokosc / 5.5, 0.8, 1.8)
	local magia = z.rodzaj == "magiczne"
	local kolorLiczby = if magia then Color3.fromHex(Ch.KOLOR_OBRAZEN.magiczne) else nil
	-- całość na tarczy (kamienna skóra, bariera): zamiast „−0” tylko napis „TARCZA −n” niżej — w każdej gałęzi
	local liczbaWidoczna = Sesja.pokazLiczbe(z)
	if z.typ == "unik" then
		self.ui:napis(glowa, "UNIK!", "unik", Vector2.new(0, -0.03), los:NextNumber(-7, 7))
	elseif z.typ == "blok" then
		self.ui:napis(glowa, "BLOK!", "blok", Vector2.new(0, -0.1), -5)
		if liczbaWidoczna then
			local t, st = self:liczba(z, z.cel)
			self.ui:napis(glowa, t, st, Vector2.new(0.03, 0.05), 4)
		end
		local tarcza = D:punkt("Tarcza")
		self.fx:wybuch("blok", if tarcza then tarcza.Position else piers, s)
		self:dzwiek("cios", 1.5)
		self:wstrzas(0.15)
	elseif z.krytyk then
		self.ui:napis(glowa, "KRYTYK!", "krytyk", Vector2.new(0, -0.115), -6)
		if liczbaWidoczna then
			self.ui:napis(glowa, "−" .. tostring(z.obrazenia), "krytykLiczba", Vector2.new(0.01, 0.05), 4, kolorLiczby)
		end
		self.fx:wybuch("krytyk", piers, s)
		self:dzwiek("krytyk", 1.25)
		self:wstrzas(0.6)
	else
		if liczbaWidoczna then
			local t, st = self:liczba(z, z.cel)
			self.ui:napis(glowa, t, st, Vector2.new(0, -0.02), los:NextNumber(-8, 8))
		end
		self.fx:wybuch(if ev.choreo and ev.choreo.wybuch and ev.styl ~= "pocisk" then ev.choreo.wybuch else "cios", piers, s)
		self:dzwiek("cios", los:NextNumber(0.9, 1.1))
		self:wstrzas(math.max(0.22, ev.choreo and ev.choreo.wstrzas or 0.24))
	end
	if z.pochloniete > 0 then
		self.ui:napis(glowa, "TARCZA −" .. tostring(z.pochloniete), "efekt", Vector2.new(0.05, 0.12), 3, Color3.fromHex("#9FE8FF"))
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
		self:klip(D, "upadek", { przejscie = 0.08 })
		self:usunOzdobyStrony(z.cel)
		self:dzwiek("upadek", 1.1)
	elseif z.typ == "blok" then
		-- klip bloku gra od wcześniej (garda przed ciosem)
	elseif z.typ ~= "unik" then
		self:klip(D, "trafienie", { predkosc = if z.krytyk then 0.9 else 1.15 })
	end
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
	self:zaplanujAkcje(t0 + ev.eStart, function(sp)
		self:klip(A, ev.akcja, { predkosc = ev.predkosc }, sp)
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
		self:zaplanujAkcje(t0 + math.max(0, ev.eHit - dl * 0.4 / pr), function(sp)
			self:klip(D, "unik", { predkosc = pr }, sp)
		end)
	elseif z.typ == "blok" then
		if D:maKlip("blok") then
			self:zaplanujAkcje(t0 + math.max(0, ev.eHit - 0.38), function(sp)
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
		local cel = self:piers(z.cel)
		local c = ev.choreo
		self.fx:pocisk(c.pocisk or "iskra", start, cel, math.max(0.05, ev.lot - sp), {
			luk = c.luk, chybiony = z.typ == "unik",
		})
		if c.wybuch and z.typ ~= "unik" then
			self:zaplanujAkcje(ev.t + ev.eHit, function()
				local s = math.clamp(D.wpis.wysokosc / 5.5, 0.8, 1.8)
				self.fx:wybuch(c.wybuch, self:piers(z.cel), s)
			end)
		end
		self:dzwiek("pocisk", 1.1)
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

Choreo.na_siebie = function(self, ev)
	local z = ev.z
	local A = self.aktorzy[z.kto]
	self:zaplanujAkcje(ev.t + ev.eStart, function(sp)
		self:klip(A, ev.akcja, { predkosc = ev.predkosc }, sp)
	end)
	self:zaplanujAkcje(ev.t + ev.eRel, function()
		local s = math.clamp(A.wpis.wysokosc / 5, 0.8, 2)
		self.fx:wybuch(ev.choreo.aura or "blask", self:piers(z.kto), s)
		self:dzwiek("czar", 1.0)
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
		self:pochlon(z.cel, z.pochloniete)
		self:odswiezEfekty()
		if self.pominieto then
			return
		end
		local glowa = self:glowa(z.kto)
		if z.obrazenia > 0 then
			self.ui:napis(glowa, "−" .. tostring(z.obrazenia), "tyk", Vector2.new(los:NextNumber(-0.03, 0.03), 0), los:NextNumber(-6, 6), Color3.fromHex(ch.kolor))
		end
		if z.pochloniete > 0 then
			self.ui:napis(glowa, "TARCZA −" .. tostring(z.pochloniete), "efekt", Vector2.new(0.05, 0.1), 3, Color3.fromHex("#9FE8FF"))
		end
		local o = self.ozdoby[z.kto .. ":" .. z.efekt]
		if o then
			o:puls()
		end
		if ev.smiertelny then
			self:klip(A, "upadek", { przejscie = 0.08 })
			self:usunOzdobyStrony(z.kto)
			self:dzwiek("upadek", 1.1)
		else
			self:klip(A, "trafienie", { predkosc = 1.5 })
		end
	end)
end

Obsluga.nalozenie = function(self, ev)
	local z = ev.z
	local lista = self.stanEfektow[z.cel]
	local nowy = { id = z.efekt, tury = z.tury, odTury = ev.tura, zapas = nil }
	local def = Dane.efekty[z.efekt]
	if def and def.typ == "tarcza" then
		nowy.zapas = z.wartosc
	end
	local podmieniony = false
	for i, e in lista do
		if e.id == z.efekt then
			lista[i] = nowy
			podmieniony = true
		end
	end
	if not podmieniony then
		table.insert(lista, nowy)
	end
	self:odswiezEfekty()
	if self.pominieto then
		return
	end
	self:ozdobaEfektu(z.cel, z.efekt, self:zrodloEfektu(ev))
	local ch = Ch.EFEKTY[z.efekt] or Ch.EFEKT_ZASTEPCZY
	local tekst = ch.napis
	if nowy.zapas then
		tekst = tekst .. " " .. tostring(nowy.zapas)
	end
	self.ui:napis(self:glowa(z.cel), tekst, "efekt", Vector2.new(0, -0.08), los:NextNumber(-4, 4), Color3.fromHex(ch.kolor))
end

Obsluga.koniec = function(self, ev)
	local z = ev.z
	local lista = self.stanEfektow[z.cel]
	local zapas = nil
	for i = #lista, 1, -1 do
		if lista[i].id == z.efekt then
			zapas = lista[i].zapas
			table.remove(lista, i)
		end
	end
	self:odswiezEfekty()
	self:usunOzdobe(z.cel, z.efekt)
	if self.pominieto then
		return
	end
	local nazwa = (Dane.efekty[z.efekt] and Dane.efekty[z.efekt].nazwa) or z.efekt
	if zapas ~= nil and zapas <= 0 then
		self.ui:napis(self:glowa(z.cel), "TARCZA PĘKŁA!", "efekt", Vector2.new(0, -0.14), -4, Color3.fromHex("#9FE8FF"))
		self.fx:wybuch("bariera", self:piers(z.cel), 1)
	end
	-- zwykły koniec efektu: znika ikona i ozdoba na postaci; bez napisu (w długiej walce napisów byłoby za dużo)
	local _ = nazwa
end

Obsluga.utrata = function(self, ev)
	local z = ev.z
	self:zaplanujAkcje(ev.t + 0.12, function()
		if self.pominieto then
			return
		end
		self.ui:napis(self:glowa(z.kto), "TRACI TURĘ!", "efekt", Vector2.new(0, -0.12), -5, Color3.fromHex("#FFE14A"))
		local o = self.ozdoby[z.kto .. ":spowolnienie"]
		if o then
			o:puls()
		end
	end)
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
	end
	if ev.nowaTura then
		if self.turaStrona then
			self:koniecTury(self.turaStrona, self.turaNr)
		end
		self.turaStrona, self.turaNr = ev.stronaTury, ev.tura
		self.ui:ustawTure(ev.tura)
		self:odswiezEfekty()
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
		pozy[strona] = { przod = 0, bok = 0, gora = 0, pochyl = 0, przechyl = 0 }
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
			if ev.atak then
				-- doskok i powrót (wręcz / skok)
				if ev.doskok > 0 then
					local h = ev.eHit
					pa.przod += ev.doskok * okno(e, h - ev.tDoskoku, h - 0.03, h + 0.16, h + 0.16 + ev.tPowrotu)
					if ev.styl == "skok" then
						pa.gora += (ev.choreo.wysokosc or 4) * luk(e, h - ev.tDoskoku, h)
					elseif z.krytyk then
						pa.gora += 0.9 * luk(e, h - ev.tDoskoku, h)
					end
					pa.pochyl += rad(10) * okno(e, h - 0.15, h - 0.02, h + 0.1, h + 0.35)
				elseif ev.styl == "pocisk" or ev.styl == "chmura" then
					pa.przod -= 0.35 * odrzut(e - ev.eRel, 0.06, 0.35)
					pa.pochyl -= rad(5) * odrzut(e - ev.eRel, 0.06, 0.35)
				elseif ev.styl == "korzenie" then
					pa.gora += 0.6 * luk(e, ev.eRel - 0.3, ev.eRel)
				end
				-- broniący
				local u = e - ev.eHit
				if z.typ == "unik" then
					local zej = okno(e, ev.eHit - 0.28, ev.eHit - 0.05, ev.eHit + 0.2, ev.eHit + 0.55)
					pd.bok -= 1.7 * zej
					pd.przod -= 0.9 * zej
					pd.przechyl += rad(12) * zej
				elseif z.typ == "blok" then
					pd.przod -= 0.6 * odrzut(u, 0.07, 0.42)
				elseif u >= 0 then
					local sila = if z.krytyk then 2.3 else 1.1
					if ev.smiertelny then
						pd.przod -= sila * 1.3 * wyjscie(u / 0.35)
					else
						pd.przod -= sila * odrzut(u, 0.09, 0.5)
						pd.pochyl -= (if z.krytyk then rad(22) else rad(12)) * odrzut(u, 0.08, 0.45)
					end
					if ev.styl == "korzenie" and not ev.smiertelny then
						pd.gora += 0.35 * okno(u, 0, 0.12, ev.trwa - ev.eHit - 0.2, ev.trwa - ev.eHit + 0.1)
					end
				end
			elseif ev.naSiebie then
				pozy[z.kto].gora += 0.35 * luk(e, ev.eRel - 0.25, ev.eRel + 0.2)
			elseif z.typ == "utrata_tury" then
				pozy[z.kto].przechyl += rad(9) * math.sin(e * 11) * okno(e, 0, 0.12, ev.trwa - 0.15, ev.trwa)
			elseif z.typ == "efekt_tick" then
				pozy[z.kto].przechyl += rad(4) * math.sin(e * 25) * okno(e, ev.eHit, ev.eHit + 0.05, ev.eHit + 0.2, ev.eHit + 0.35)
			end
		end
	end
	for strona, a in self.aktorzy do
		local p = pozy[strona]
		local kier = self.geo.kier[strona]
		local x = self.geo.x[strona] + kier * p.przod
		local cf = self.cfSceny * CFrame.lookAt(Vector3.new(x, p.gora, p.bok), Vector3.new(x + kier, p.gora, p.bok))
		cf = cf * CFrame.Angles(-p.pochyl, 0, p.przechyl)
		a:ustaw(cf)
	end
end

------------------------------------------------------------------ zwolnienie czasu sceny (krytyk, nokaut)
function Sesja:zwolnienie(tau: number): number
	local t = 1
	for _, w in self.zwolnienia do
		if tau > w.od - 0.08 and tau < w["do"] + 0.08 then
			local k
			if tau < w.od then
				k = gladko((tau - (w.od - 0.08)) / 0.08)
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
	local teraz = os.clock()
	local odCiecia = teraz - (self.kam.ostatnieCiecie or 0)
	local tura = uj.ev and uj.ev.tura or 0
	local dluga = tura > 12
	-- atak po ujęciu jednej postaci (umiejętność na siebie, efekt) nie może zostać w tym ujęciu: atakujący byłby
	-- poza kadrem — taki atak zawsze dostaje swoje ujęcie (najwyżej z płynnym przejściem)
	local jednaPostac = self.kam.uj and (self.kam.uj.typ == "naSiebie" or self.kam.uj.typ == "efekt")
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
	self.kam.uj = uj
	self.kam.start = self.tau
	self.kam.ostatnieCiecie = teraz
	self.licznikUjec += 1
end

-- ujęcie → (pozycja, cel, kąt) w układzie sceny (X w prawo, Y w górę, Z do kamery planu ogólnego)
function Sesja:ujecie(uj, tau: number): (Vector3, Vector3, number)
	local g = self.geo
	local lt = tau - (self.kam.start or 0)
	local typ = uj.typ
	local A = uj.atakujacy or "gracz"
	local D = uj.broniacy or "wrog"
	local xA, xD = g.x[A], g.x[D]
	local hA, hD = g.h[A], g.h[D]
	local wA, wD = g.w[A], g.w[D]
	local dir = if xD > xA then 1 elseif xD < xA then -1 else g.kier[A]
	-- zza pleców dużo większego aktora nic nie widać (Troll przed Wojownikiem) — wtedy ujęcie z boku
	-- …a przy bardzo różnym wzroście (Mag przy Strażniku) mały aktor ląduje w rogu kadru
	local roznica = math.max(hA, hD) / math.max(math.min(hA, hD), 0.5)
	if (typ == "zaAtakujacym" and hA > 1.3 * hD + 0.5) or (typ == "zaBroniacym" and hD > 1.3 * hA + 0.5)
		or ((typ == "zaAtakujacym" or typ == "zaBroniacym") and roznica > 1.8) then
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
		local d = math.max(odlDlaWys(g.H, 42) * 1.02, g.S * 1.05, odlDlaPary(lo, hi, gora, 42) + 0.4 * math.max(wA, wD))
		local srodek = (lo + hi) / 2
		return Vector3.new(srodek - dir * (g.S * 0.32 + 0.6 * k), gora * 0.4 + 1.2, d - 0.8 * k),
			Vector3.new(srodek + dir * g.S * 0.08, gora * 0.5, 0), 42
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
		local katMin = math.deg(2 * math.atan(t))
		return Vector3.new(srodek - dir * 0.4 * k, 0.28 * gora + 0.8, d),
			Vector3.new(srodek + dir * 0.04 * (hi - lo) * k, 0.46 * gora, 0), 52 - (52 - math.clamp(katMin, 40, 52)) * k
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
		return Vector3.new(xA + f * d * 0.45, 0.55 * hA + 0.5, d * 0.88 - 0.6 * k), Vector3.new(xA + f * 0.3, 0.5 * hA, 0), 42
	elseif typ == "efekt" then
		local k = gladko(lt / 1.4)
		local f = g.kier[A]
		local d = odlDlaWys(hA, 44, wA) * 1.15
		return Vector3.new(xA + f * d * 0.4, 0.6 * hA + 0.8, d * 0.9 - 0.5 * k), Vector3.new(xA + f * 0.4, 0.48 * hA, 0), 44
	end
	-- objazd wokół zwycięzcy (finał); kończy się ze zwycięzcą w jednej ćwiartce, panel wyniku w drugiej połowie
	local zw = self.zwyciezca
	local znak = g.kier[zw]
	local hZ = g.h[zw]
	local czas = math.max(0, tau - (self.kam.start or tau)) + self.tauWyniku
	local k = wyjscie(czas / 2.6)
	local dryf = math.min(math.max(0, czas - 2.6) * 1.2, 12)
	local kat = rad(62 - 22 * k - dryf)
	local R = 1.25 * hZ + 6.5
	local W = Vector3.new(g.x[zw], 0, 0)
	local cel = W + Vector3.new(znak * R * 0.32, hZ * 0.5, 0)
	return W + Vector3.new(znak * R * math.cos(kat), hZ * 0.55 + 1.6, R * math.sin(kat)), cel, 44
end

function Sesja:aktualizujKamere(tau: number, dt: number)
	local kam = self.kam
	local poz, cel, kat = self:ujecie(kam.uj, tau)
	if kam.od then
		local u = gladko((os.clock() - kam.przejscieStart) / kam.przejscie)
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

------------------------------------------------------------------ start jednej walki (także „Jeszcze raz”)
function Sesja:rozpocznij(walka)
	self.walka = walka
	self.harmonogram = {}
	self.ozdoby = {}
	self.stanEfektow = { gracz = {}, wrog = {} }
	self.niezgodnosciPaskow = 0
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
	self:ustawAktorow(walka)
	self:zaplanuj(walka)
	self.zwyciezca = if walka.wynik == "wygrana" then "gracz" else "wrog"
	self.pokonany = inna(self.zwyciezca)
	self.final = { radosc = false, baner = false, lup = false, objazd = false }
	self.wstep = { pokazany = false, schowany = false }
	self.kam = { uj = { typ = "ogolny", prio = 3 }, start = 0, ostatnieCiecie = os.clock() }
	self.ui:usunNapisy()
	self.ui:ukryjWynik()
	self.ui:ukryjBaner(true)
	self.ui:ukryjUmiejetnosc()
	self.ui:ustawStrony(walka.strony, { gracz = walka.strony.gracz.id, wrog = walka.strony.wrog.id })
	self.ui:pokazPaski(true)
	self.ui:pokazPomin(function()
		self:pomin()
	end)
	self.ui:pokazTempo(self.tempo, function(t)
		self:ustawTempo(t)
	end)
	self.zaslonaCel = 0
	self.faza = "odtwarzanie"
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
	self:atrybut("OstatnieTempo", t)
end

------------------------------------------------------------------ krok sceny (czas sceny d)
function Sesja:krokSceny(d: number, dt: number)
	local tau = math.min(self.tau + d, self.walka.czas)
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
	-- finał
	if not self.final.objazd and tau >= self.tObjazdu then
		self.final.objazd = true
		self:proponujUjecie({ typ = "objazd", prio = 3 })
	end
	local f = tau - self.tKoniecDziennika
	if f >= 0.05 and not self.final.radosc then
		self.final.radosc = true
		self:klip(self.aktorzy[self.zwyciezca], "radosc", { petla = true, przejscie = 0.2 })
		self.ui:ustawTure(self.turaNr)
		self:atrybut("OstatniaLiczbaTurOdtworzona", self.turaNr)
	end
	if f >= 0.25 and not self.final.baner then
		self.final.baner = true
		self.ui:ukryjPomin()
		self.ui:ukryjTempo()
		self.ui:ukryjUmiejetnosc()
		if self.zwyciezca == "gracz" then
			self.ui:pokazBaner("ZWYCIĘSTWO!", K.zolty, K.czerwony, 0.83)
		else
			self.ui:pokazBaner("PORAŻKA!", K.bialy, K.fiolet, 0.83)
		end
	end
	if f >= 0.35 and not self.final.lup then
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
	self:dzwiek("lup", 1)
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
	if self.faza == "odtwarzanie" then
		table.insert(self.klatki, dt)
		local d = 0
		if not self.opcje.reczny then
			d = dt * self.tempo * self:zwolnienie(self.tau)
		end
		self:krokSceny(d, dt)
		if self.opcje.pominPo and self.tau >= self.opcje.pominPo then
			self:pomin()
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
	ui:aktualizuj(dt, kamera)
	if self.opcje.etykietaCzasu then
		ui:ustawZegar(string.format("t = %.2f / %.2f s  zd. %s/%d  tura %d  ujęcie %s  ×%d", self.tau, self.walka.czas,
			tostring(self.biezace), #self.plan, self.turaNr, self.kam.uj.typ, self.tempo))
	end
	if self.faza == "odtwarzanie" and self.tau >= self.walka.czas then
		self:pokazWynik()
	end
end

-- testy: ręczne przesunięcie czasu sceny (opcje.reczny), drobnymi krokami jak w zwykłym odtwarzaniu
function Sesja:przewin(sekundy: number)
	local zostalo = sekundy
	while zostalo > 1e-6 and self.faza == "odtwarzanie" do
		local d = math.min(zostalo, 1 / 60)
		zostalo -= d
		self:krokSceny(d * self:zwolnienie(self.tau), 1 / 60)
		if self.tau >= self.walka.czas then
			self:pokazWynik()
		end
	end
	self.ui:aktualizuj(0.05, self.kamera)
end

-- testy: przewiń do chwili sceny τ (bez zwolnienia — cel jest w czasie sceny)
function Sesja:przewinDo(cel: number)
	while self.faza == "odtwarzanie" and self.tau < cel - 1e-6 do
		self:krokSceny(math.min(cel - self.tau, 1 / 60), 1 / 60)
		if self.tau >= self.walka.czas then
			self:pokazWynik()
		end
	end
	self.ui:aktualizuj(0.05, self.kamera)
end

------------------------------------------------------------------ pomiń, wynik, jeszcze raz
function Sesja:pomin()
	if self.faza ~= "odtwarzanie" or self.pominieto then
		return
	end
	self.pominieto = true
	self:dzwiek("przycisk")
	self.ui:usunNapisy()
	self.ui:ukryjBaner(true)
	self.ui:ukryjUmiejetnosc()
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
	self.stanEfektow = { gracz = {}, wrog = {} }
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
	self.final = { radosc = true, baner = true, lup = true, objazd = true }
	self.tau = self.walka.czas
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
	ui:ukryjTempo()
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
		kontener = kontener, gracz = gracz, opcje = o, tempo = tempo, wybor = { klasa = w.klasa, przeciwnik = w.przeciwnik, poziom = w.poziom },
		sprzatanie = {}, utworzono = 0, faza = "prosba", zakonczona = false, zaslona = 0, zaslonaCel = 0, tau = 0, tauWyniku = 0,
		licznikUjec = 0,
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
	for strona, a in s.aktorzy do
		local inny = s.aktorzy[inna(strona)]
		local zmienione = {}
		for _, c in inny.model:GetDescendants() do
			if c:IsA("BasePart") and not c.CanQuery then
				c.CanQuery = true
				table.insert(zmienione, c)
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
		wynik[strona] = { czesci = n, wKadrze = if n > 0 then wKadrze / n else 0, odsloniete = if n > 0 then odsloniete / n else 0 }
	end
	wynik.ujecie = s.kam and s.kam.uj and s.kam.uj.typ
	wynik.tau = s.tau
	return wynik
end

-- testy: napisy nad postaciami widoczne teraz (tekst i styl)
function Odtwarzacz.napisy()
	local s = sesja
	local lista = {}
	if s and s.ui then
		for _, n in s.ui.napisy do
			table.insert(lista, { tekst = n.napis.Text, styl = string.sub(n.pole.Name, 7) })
		end
	end
	return lista
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
	}
	if s.plan and s.biezace then
		local ev = s.plan[s.biezace]
		wynik.typ = ev.typ
		wynik.umiejetnosc = ev.z.umiejetnosc
		wynik.t = ev.t
		wynik.trafienie = if ev.eHit then ev.t + ev.eHit else nil
		wynik.styl = ev.styl
	end
	return wynik
end

return Odtwarzacz
