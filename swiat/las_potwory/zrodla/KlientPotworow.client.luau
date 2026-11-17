--[[
	KlientPotworow — kliencka połowa pakietu „potwory w ruchu” w Borze Pod Ukłonem (Script, RunContext = Client;
	działa z kontenera Workspace/LasPotwory). Kontrakt: swiat/las_potwory/PROJEKT.md, rozdz. 4, 5.1, 8.3, 8.6.

	Klient tylko POKAZUJE (D-016): niczego nie liczy za serwer i nie wysyła liczb. Prośbę o walkę wysyła przyjęty
	odtwarzacz walki v2 (Workspace/TestWalki2/Moduly/OdtwarzaczWalki2) do LasPotwory/Zdalne/RozpocznijWalke2 — ładunek
	{ klasa, przeciwnik = id potwora, poziom } to trzy napisy z list.

	Co robi, po kolei:
		• czeka do 40 s (kontrakt: 15 s; poprawka recenzji, patrz CZEKANIE_NA_SERWER) na atrybuty kontenera
		  SerwerGotowy i SzablonyGotowe albo zły StanBiomu i wybiera tryb (rozdz. 4.3):
		  „aktorzy” (modele z kopii szablonów w ReplicatedStorage/LasPotworySzablony + klipy prototypu) albo
		  „zastepczy” (jedna bryła na potwora, bez klipów). Zły las (StanBiomu) → jeden dymek i nic więcej;
		• co 0,5 s wybiera widoki (rozdz. 4.1): 12 najbliższych kamerze w promieniu 120 buduje, poza 14 albo dalej niż
		  135 niszczy; suma brył ≤ 4000; najwyżej jeden klon na 0,1 s; klipy tylko dla 12 najbliższych widoków;
		• co klatkę (RunService.PreSimulation, jak moduł Klipy): wygładzanie punktu bazowego z atrybutu Pozycja (4 Hz),
		  jeden promień w dół do gruntu BiomLas na każdy nowy cel, obrót do Kierunek 8 rad/s, klip „ruch” albo
		  „spoczynek” (rozdz. 4.2), ikona mieczy przy Stan = "zajety";
		• tabliczka „poz. N” (czerwona, gdy poziom ≥ poziom bohatera + 3) i miecze z ramek, bez obrazków (rozdz. 4.4);
		• co 0,1 s podpowiedź E (na telefonie stuknięcie) przy najbliższym dozwolonym potworze (rozdz. 4.5);
		• panel bohatera (klasa i poziom — reguła testowa T1, rozdz. 5.2), start walki w odtwarzaczu, odczyt
		  OstatniWynik po walce, ukrycie pokonanego, baner po Strażniku (rozdz. 4.6);
		• stan gracza (17.11.2026, swiat/stan_gracza, propozycja): gdy jest kontener Stale.KONTENER_STANU, a las nie ma
		  atrybutu Stale.ATRYBUT_TESTU_BOHATERA = true, panel tylko pokazuje „Twój bohater: <klasa> · poziom N” (klasa
		  z atrybutu gracza Class, poziom z Level; tabliczki czerwienieją względem poziomu gracza), a prośba o walkę
		  niesie klasę gracza i "auto" — serwer i tak bierze bohatera z danych gracza;
		• M6 (17.11.2026, przejście gry): kotwica podpowiedzi E staje nad postacią, gdy punkt nad potworem jest poza
		  kadrem (ProximityPrompt działa tylko w kadrze), bieżący kandydat ma zapas zasięgu Stale.HISTEREZA_E (pomiar w
		  Play: chodzący slime wychodził z bramki klienta w czasie reakcji gracza), a gdy walka się nie zaczęła (blokada po
		  walce, odmowa serwera, E bez podpowiedzi tuż obok potwora) gracz dostaje dymek Stale.GUI_KOMUNIKATU zamiast ciszy.

	Odczytania kontraktu (najprostsze; opisane też w UWAGI_K.md):
		• w czasie walki (Odtwarzacz.czyTrwa()) wybór widoków i budowa stoją, a klipy nie są liczone — kamera stoi
		  wtedy przy arenie prototypu, ponad 2000 studów od lasu, więc „najbliższe kamerze” wyrzuciłoby wszystkie
		  widoki, a po walce las budowałby się od nowa; położenia widoków dalej idą za serwerem (tanie);
		• tabliczka ma 76 × 30 px na środku BillboardGui 140 × 30, a miecze stoją obok w tym samym BillboardGui
		  (nie poza jego brzegiem — nie zakładamy, że BillboardGui nie przycina potomków);
		• tryb wybrany po czekaniu na serwer już się nie zmienia (gdy szablony przyjdą później — trzeba zatrzymać i uruchomić Play);
		• po walce, gdy kamera mimo sprzątania odtwarzacza została skryptowa, klient wraca do zwykłej kamery postaci
		  (zabezpieczenie; odtwarzacz sam przywraca kamerę i sterowanie);
		• przy złym lesie KlientTryb = "brak_biomu" (poza listą "aktorzy" / "zastepczy" z rozdz. 8.3).

	Haczyk testowy (tylko Studio): Sygnaly/SterowanieKlienta (BindableFunction), Invoke(polecenie, …):
		"stan"                    → { tryb, widoki, animowane, czesciWidokow, najblizszy = id?, podpowiedz = bool,
		                              bohater = { klasa, poziom }, walka = bool, ukryte = liczba, bledy = liczba }
		"walcz", id               → zaczyna walkę z tym potworem jak po E (serwer i tak sprawdza odległość) → bool
		"bohater", klasa, poziom  → ustawia wybór z panelu → bool
		"wymus", id | nil         → (16.11, przelot lasu-pasa) ten widok zawsze budowany i przed innymi → true
		"klip", id, nazwa         → (16.11) jednorazowy klip na widoku (ryk Strażnika), potem spoczynek → bool
	Atrybuty lokalne kontenera (tylko u tego klienta, do testów): KlientGotowy, KlientTryb, KlientKlasa, KlientPoziom,
	KlientWidoki, KlientBledy, KlientOstatniaWalka ("<id>/<wynik>").
]]
if not game:GetService("RunService"):IsStudio() then
	return -- pakiet działa wyłącznie w Studio; poza Studio serwer i tak usuwa cały kontener
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local Stale = require(moduly:WaitForChild("Stale"))
local folderStanu = kontener:WaitForChild("Stan")
local sygnaly = kontener:WaitForChild("Sygnaly")
local gracz = Players.LocalPlayer
local K = Stale.KOLORY
local KOMIKS = Enum.Font.Bangers
local P = Stale.PREFIKS

------------------------------------------------------------------ gatunki (z DanePotworow; zapas z rozdz. 2.2)
-- zapas tylko na wypadek braku modułu danych: wymiary = { szer, wys, dł } bryły zastępczej, promien do bramki E
local GATUNKI_ZAPASOWE = {
	lesny_slime = { nazwa = "Leśny Slime", predkosc = 6, promien = 1.35, wymiary = { 2.7, 2.7, 2.7 } },
	muchomornik = { nazwa = "Muchomornik", predkosc = 5, promien = 1.475, wymiary = { 2.95, 3.6, 2.7 } },
	cierniowy_wilk = { nazwa = "Cierniowy Wilk", predkosc = 10, promien = 3.85, wymiary = { 2.25, 4.4, 7.7 } },
	straznik_lasu = { nazwa = "Strażnik Gaju", predkosc = 0, promien = 4.45, wymiary = { 8.9, 14.5, 5.0 } },
}
local gatunki: { [string]: any } = GATUNKI_ZAPASOWE
-- prostokąt lasu (płyta biomu z danych + zapas) — panel bohatera widać tylko w nim (Stale.PANEL_TYLKO_W_LESIE)
local obszarLasu: { x1: number, x2: number, z1: number, z2: number }? = nil
do
	local modul = moduly:WaitForChild("DanePotworow", 15)
	local ok, dane = false, nil
	if modul then
		ok, dane = pcall(require, modul)
	end
	if ok and type(dane) == "table" and type(dane.gatunki) == "table" then
		gatunki = dane.gatunki
		local plyta = type(dane.biom) == "table" and dane.biom.plyta
		if type(plyta) == "table" and type(plyta.pozycja) == "table" and type(plyta.rozmiar) == "table" then
			local z = Stale.PANEL_ZAPAS or 0
			local px, pz = plyta.pozycja[1], plyta.pozycja[3]
			local rx, rz = plyta.rozmiar[1] / 2 + z, plyta.rozmiar[3] / 2 + z
			obszarLasu = { x1 = px - rx, x2 = px + rx, z1 = pz - rz, z2 = pz + rz }
		end
	else
		warn(P .. "brak modułu DanePotworow albo pola gatunki — klient używa wymiarów zapasowych (" .. tostring(dane) .. ")")
	end
end

local function gatunek(klucz: any)
	return (type(klucz) == "string" and (gatunki[klucz] or GATUNKI_ZAPASOWE[klucz])) or nil
end

local function wymiary(klucz: any): { number }
	local g = gatunek(klucz)
	local w = g and g.wymiary
	if type(w) == "table" and type(w[1]) == "number" and type(w[2]) == "number" and type(w[3]) == "number" then
		return w
	end
	return { 3, 3, 3 }
end

------------------------------------------------------------------ błędy w pętlach (rozdz. 8.5)
local licznikBledow = 0
local ostatniBlad, czasOstatniegoBledu = "", -math.huge
local function zglosBlad(gdzie: string, blad: any)
	licznikBledow += 1
	pcall(function()
		kontener:SetAttribute("KlientBledy", licznikBledow)
	end)
	local tekst = tostring(blad)
	local teraz = os.clock()
	-- jeden warn na błąd; ten sam błąd co klatkę najwyżej raz na 5 s
	if tekst ~= ostatniBlad or teraz - czasOstatniegoBledu > 5 then
		ostatniBlad, czasOstatniegoBledu = tekst, teraz
		warn(P .. "błąd klienta (" .. gdzie .. "): " .. tekst)
	end
end

------------------------------------------------------------------ interfejs: pomocnicze
local function nowy(klasa: string, w: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in w do
		(o :: any)[k] = v
	end
	o.Parent = rodzic
	return o
end

-- obrys tuszem: domyślnie wokół ramki (Border); naTekscie = true → wokół liter (Contextual na TextLabel / TextButton)
local function obrys(o: GuiObject, grubosc: number, naTekscie: boolean?)
	return nowy("UIStroke", { Color = K.tusz, Thickness = grubosc, LineJoinMode = Enum.LineJoinMode.Round,
		ApplyStrokeMode = if naTekscie then Enum.ApplyStrokeMode.Contextual else Enum.ApplyStrokeMode.Border }, o)
end

local function rog(o: GuiObject, ulamek: number)
	return nowy("UICorner", { CornerRadius = UDim.new(ulamek, 0) }, o)
end

-- baner na środku u góry ekranu (po Strażniku; także jedyny dymek przy złym lesie)
local function pokazBaner(tytul: string, podpis: string?, sekundy: number)
	local playerGui = gracz:FindFirstChildOfClass("PlayerGui")
	if not playerGui then
		return
	end
	local stary = playerGui:FindFirstChild(Stale.GUI_BANERA)
	if stary then
		stary:Destroy()
	end
	local gui = nowy("ScreenGui", { Name = Stale.GUI_BANERA, ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 6,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, nil)
	gui:SetAttribute("Wygenerowane", true)
	local ramka = nowy("Frame", { Name = "Ramka", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.26),
		Size = UDim2.fromScale(0.72, 0.2), BackgroundColor3 = K.krem, BorderSizePixel = 0, Rotation = -1.5 }, gui)
	nowy("UISizeConstraint", { MaxSize = Vector2.new(860, 170) }, ramka)
	rog(ramka, 0.2)
	obrys(ramka, 4)
	local t = nowy("TextLabel", { Name = "Tytul", BackgroundTransparency = 1, Position = UDim2.fromScale(0.04, if podpis then 0.07 else 0.15),
		Size = UDim2.fromScale(0.92, if podpis then 0.56 else 0.7), Font = KOMIKS, TextScaled = true, Text = tytul,
		TextColor3 = if podpis then K.czerwony else K.tusz }, ramka)
	if podpis then
		obrys(t, 2, true)
		nowy("TextLabel", { Name = "Podpis", BackgroundTransparency = 1, Position = UDim2.fromScale(0.04, 0.64),
			Size = UDim2.fromScale(0.92, 0.29), Font = KOMIKS, TextScaled = true, Text = podpis, TextColor3 = K.tusz }, ramka)
	end
	gui.Parent = playerGui
	task.delay(sekundy, function()
		if gui.Parent then
			gui:Destroy()
		end
	end)
end

-- M6 (17.11.2026): krótki dymek, gdy walka się nie zaczęła (zamiast ciszy); jeden naraz, znika po Stale.KOMUNIKAT_S
local function pokazKomunikat(tekst: string)
	local playerGui = gracz:FindFirstChildOfClass("PlayerGui")
	if not playerGui then
		return
	end
	local stary = playerGui:FindFirstChild(Stale.GUI_KOMUNIKATU)
	if stary then
		stary:Destroy()
	end
	local gui = nowy("ScreenGui", { Name = Stale.GUI_KOMUNIKATU, ResetOnSpawn = false, IgnoreGuiInset = true, DisplayOrder = 7,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, nil)
	gui:SetAttribute("Wygenerowane", true)
	gui:SetAttribute("Tekst", tekst)
	local dymek = nowy("TextLabel", { Name = "Dymek", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.3),
		Size = UDim2.fromScale(0.62, 0.085), BackgroundColor3 = K.krem, BorderSizePixel = 0, Rotation = -1.5, Font = KOMIKS,
		TextScaled = true, Text = tekst, TextColor3 = K.tusz }, gui)
	nowy("UISizeConstraint", { MaxSize = Vector2.new(760, 70) }, dymek)
	nowy("UIPadding", { PaddingLeft = UDim.new(0.03, 0), PaddingRight = UDim.new(0.03, 0), PaddingTop = UDim.new(0.12, 0),
		PaddingBottom = UDim.new(0.12, 0) }, dymek)
	rog(dymek, 0.25)
	obrys(dymek, 3)
	gui.Parent = playerGui
	kontener:SetAttribute("KlientOstatniKomunikat", tekst) -- lokalnie, do testów
	task.delay(Stale.KOMUNIKAT_S, function()
		if gui.Parent then
			gui:Destroy()
		end
	end)
end

------------------------------------------------------------------ czekanie na serwer i wybór trybu (rozdz. 4.3)
local ZLE_STANY_BIOMU = { brak_biomu = true, zle_polozenie = true }
-- Poprawka recenzji: kontrakt mówi 15 s, ale serwer może potrzebować do 15 s na BiomLas i do 2 × 10 s na
-- TestWalki2/Aktorzy, zanim ustawi StanBiomu i SerwerGotowy. Przy 15 s klient przy brakującym lesie nie zdążył
-- zobaczyć StanBiomu i zamiast dymka cicho przechodził w tryb zastępczy. W zwykłym przypadku pętla kończy się po
-- ok. 1 s, więc dłuższy limit niczego nie spowalnia.
local CZEKANIE_NA_SERWER = 40
do
	local t0 = os.clock()
	while os.clock() - t0 < CZEKANIE_NA_SERWER do
		if ZLE_STANY_BIOMU[kontener:GetAttribute("StanBiomu")] then
			break
		end
		-- serwer gotowy i powiedział już, czy są szablony (true albo false)
		if kontener:GetAttribute("SerwerGotowy") == true and kontener:GetAttribute("SzablonyGotowe") ~= nil then
			break
		end
		task.wait(0.2)
	end
end

local stanBiomu = kontener:GetAttribute("StanBiomu")
if ZLE_STANY_BIOMU[stanBiomu] then
	-- serwer nie wystawił potworów: jeden dymek i nic więcej (rozdz. 1.3)
	kontener:SetAttribute("KlientTryb", "brak_biomu")
	pokazBaner("Las Potworów: brak lasu w tym miejscu (szczegóły w Output)", nil, 8)
	local h = sygnaly:WaitForChild("SterowanieKlienta", 5)
	if h and h:IsA("BindableFunction") then
		h.OnInvoke = function(polecenie: string)
			if polecenie == "stan" then
				return { tryb = "brak_biomu", widoki = 0, animowane = 0, czesciWidokow = 0, podpowiedz = false, walka = false }
			end
			return false
		end
	end
	kontener:SetAttribute("KlientGotowy", true)
	return
end

-- moduły prototypu (ModuleScripty nie są bryłami, więc są u klienta mimo streamingu — ryzyko z rozdz. 10)
local prototyp = workspace:WaitForChild(Stale.NAZWA_PROTOTYPU, 5)
local modulyProtot = prototyp and prototyp:WaitForChild("Moduly", 5)

local Klipy: any, Tabela: any = nil, nil
local daneAktorow: { [string]: any } = {}
local szablonyRS: Instance? = nil
local tryb = "zastepczy"

local function przygotujAktorow(): (boolean, string?)
	if kontener:GetAttribute("SzablonyGotowe") ~= true then
		return false, "SzablonyGotowe ~= true po czekaniu na serwer"
	end
	if not modulyProtot then
		return false, "brak Workspace/" .. Stale.NAZWA_PROTOTYPU .. "/Moduly"
	end
	local folder = ReplicatedStorage:WaitForChild(Stale.NAZWA_SZABLONOW, 5)
	if not folder then
		return false, "brak ReplicatedStorage/" .. Stale.NAZWA_SZABLONOW
	end
	local mKlipy = modulyProtot:WaitForChild("Klipy", 5)
	local mTabela = modulyProtot:WaitForChild("TabelaAktorow", 5)
	local fDanych = modulyProtot:WaitForChild("DaneAktorow", 5)
	if not mKlipy or not mTabela or not fDanych then
		return false, "brak modułów Klipy / TabelaAktorow / DaneAktorow w prototypie"
	end
	local ok1, k = pcall(require, mKlipy)
	local ok2, t = pcall(require, mTabela)
	if not ok1 or not ok2 or type(k) ~= "table" or type(t) ~= "table" or type(t.aktorzy) ~= "table" then
		return false, "nie wczytały się Klipy / TabelaAktorow: " .. tostring(if ok1 then t else k)
	end
	for _, klucz in Stale.SZABLONY do
		local m = folder:WaitForChild(klucz, 5)
		if not m or not m:IsA("Model") or not m:WaitForChild("HumanoidRootPart", 2) then
			return false, "brak szablonu " .. klucz .. " w ReplicatedStorage/" .. Stale.NAZWA_SZABLONOW
		end
		if type(t.aktorzy[klucz]) ~= "table" then
			return false, "brak aktora " .. klucz .. " w TabelaAktorow"
		end
		local md = fDanych:WaitForChild(klucz, 5)
		local okd, d = false, nil
		if md then
			okd, d = pcall(require, md)
		end
		if not okd or type(d) ~= "table" then
			return false, "nie wczytały się dane klipów " .. klucz .. ": " .. tostring(d)
		end
		daneAktorow[klucz] = d
	end
	Klipy, Tabela, szablonyRS = k, t, folder
	return true, nil
end

do
	-- pcall zwraca (true, gotowe, powód) albo (false, błąd)
	local ok, gotowe, powod = pcall(przygotujAktorow)
	if ok and gotowe == true then
		tryb = "aktorzy"
	else
		tryb = "zastepczy"
		warn(P .. "klient w trybie zastępczym (bryły zamiast modeli): " .. tostring(if ok then powod else gotowe))
	end
end
kontener:SetAttribute("KlientTryb", tryb)

-- odtwarzacz walki prototypu (ten sam egzemplarz modułu co w KlientWalki2 — dwie walki naraz nie ruszą).
-- Wczytujemy go w osobnym wątku: jego zależności czekają WaitForChild bez limitu, więc przy niepełnym prototypie
-- require mógłby zawisnąć — reszta klienta (widoki, podpowiedź z „Walka niedostępna”) działa wtedy dalej.
local Odtwarzacz: any = nil
task.spawn(function()
	local m = modulyProtot and modulyProtot:WaitForChild("OdtwarzaczWalki2", 5)
	if not m then
		warn(P .. "brak Workspace/" .. Stale.NAZWA_PROTOTYPU .. "/Moduly/OdtwarzaczWalki2 — walki niedostępne")
		return
	end
	local ok, o = pcall(require, m)
	if ok and type(o) == "table" and type(o.uruchom) == "function" then
		Odtwarzacz = o
	else
		warn(P .. "nie wczytał się OdtwarzaczWalki2 — walki niedostępne: " .. tostring(o))
	end
end)
task.delay(15, function()
	if not Odtwarzacz and modulyProtot and modulyProtot:FindFirstChild("OdtwarzaczWalki2") then
		warn(P .. "OdtwarzaczWalki2 wciąż się wczytuje po 15 s (czeka na brakujący moduł prototypu?) — walki niedostępne")
	end
end)

local function walkaTrwa(): boolean
	return Odtwarzacz ~= nil and Odtwarzacz.czyTrwa() == true
end

------------------------------------------------------------------ bohater (reguła testowa T1, rozdz. 5.2)
local NAZWY_KLAS = { wojownik = "Wojownik", zwiadowca = "Zwiadowca", mag = "Mag" }
local bohater = { klasa = Stale.KLASY[1], poziom = Stale.POZIOMY_BOHATERA[1] } -- wojownik, auto
local naZmianeBohatera: (() -> ())? = nil

local function naLiscie(lista: { string }, x: any): boolean
	return type(x) == "string" and table.find(lista, x) ~= nil
end

-- stan gracza (17.11.2026, swiat/stan_gracza, propozycja): gdy jest kontener Stale.KONTENER_STANU, a las nie ma
-- atrybutu Stale.ATRYBUT_TESTU_BOHATERA = true, bohater to klasa i poziom gracza (serwer i tak bierze je z danych
-- gracza) — panel tylko je pokazuje; w trybie testowym (i bez kontenera) panel T1 działa jak dawniej
local function trybTestowyBohatera(): boolean
	if kontener:GetAttribute(Stale.ATRYBUT_TESTU_BOHATERA) == true then
		return true
	end
	local k = workspace:FindFirstChild(Stale.KONTENER_STANU)
	return k == nil or k:GetAttribute("Wygenerowane") ~= true
end

local function poziomGracza(): number
	local v = gracz:GetAttribute(Stale.ATRYBUT_POZIOMU_GRACZA)
	return if type(v) == "number" and v >= 1 then math.floor(v) else 1
end

local function poziomBohatera(): number?
	if not trybTestowyBohatera() then
		return poziomGracza() -- tabliczka czerwienieje względem prawdziwego poziomu gracza
	end
	if bohater.poziom == "auto" then
		return nil -- przy „auto” bohater ma zawsze poziom potwora: tabliczka nie czerwienieje
	end
	return tonumber(bohater.poziom)
end

local function ustawBohatera(klasa: any, poziom: any): boolean
	if not naLiscie(Stale.KLASY, klasa) or not naLiscie(Stale.POZIOMY_BOHATERA, poziom) then
		return false
	end
	bohater.klasa, bohater.poziom = klasa, poziom
	kontener:SetAttribute("KlientKlasa", klasa)
	kontener:SetAttribute("KlientPoziom", poziom)
	if naZmianeBohatera then
		naZmianeBohatera()
	end
	return true
end

-- poza trybem testowym wybór panelu = klasa gracza (z atrybutu Class) i "auto" (napisy z list, D-016)
local function zsynchronizujBohatera()
	if trybTestowyBohatera() then
		if naZmianeBohatera then
			naZmianeBohatera() -- napis panelu T1 (np. po włączeniu trybu testowego)
		end
		return
	end
	local id = gracz:GetAttribute(Stale.ATRYBUT_KLASY_GRACZA)
	local klasa = (type(id) == "string" and Stale.KLASY_GRACZA[id]) or Stale.KLASY[1]
	if bohater.klasa ~= klasa or bohater.poziom ~= Stale.POZIOMY_BOHATERA[1] then
		ustawBohatera(klasa, Stale.POZIOMY_BOHATERA[1])
	elseif naZmianeBohatera then
		naZmianeBohatera()
	end
end

------------------------------------------------------------------ widoki
local folderWidokow = Instance.new("Folder")
folderWidokow.Name = "Widoki"
folderWidokow.Parent = kontener -- lokalny: inni gracze go nie mają

local widoki: { [string]: any } = {}     -- id → widok
local ukryte: { [string]: boolean } = {} -- pokonani przez nas (do usunięcia przez serwer)
local zepsute: { [string]: boolean } = {} -- gatunki, których model nie zbudował się — pokazujemy bryłę
local sumaCzesci = 0
local liczbaAnimowanych = 0
local kolejkaBudowy: { string } = {}
-- widok wymuszony haczykiem „wymus” (przelot kamery lasu-pasa, 16.11: Strażnik budowany zawczasu, przed innymi)
local wymuszony: string? = nil

local biom: Instance? = workspace:FindFirstChild(Stale.NAZWA_BIOMU)
local promien = RaycastParams.new()
promien.FilterType = Enum.RaycastFilterType.Include
promien.FilterDescendantsInstances = if biom then { biom } else {}

local function cfZiemi(poz: Vector3, yaw: number): CFrame
	return CFrame.new(poz) * CFrame.Angles(0, yaw, 0)
end

-- jeden promień w dół: trafienie w BiomLas w ±3 od y serwera → stoimy na nim, inaczej na y z serwera (rozdz. 4.2)
local function grunt(p: Vector3): Vector3
	if not biom or not biom.Parent then
		return p
	end
	local wynik = workspace:Raycast(p + Vector3.new(0, 6, 0), Vector3.new(0, -14, 0), promien)
	if wynik and math.abs(wynik.Position.Y - p.Y) <= 3 then
		return Vector3.new(p.X, wynik.Position.Y, p.Z)
	end
	return p
end

local function kosztWidoku(klucz: string): number
	if tryb == "aktorzy" and not zepsute[klucz] and Tabela and Tabela.aktorzy[klucz] then
		return tonumber(Tabela.aktorzy[klucz].liczbaCzesci) or 0
	end
	return 1
end

local function kolorZastepczy(klucz: string, wariant: any): Color3
	if wariant == "bursztynowy" then
		return Stale.KOLOR_BURSZTYNOWY
	elseif klucz == "lesny_slime" then
		return K.zielony
	elseif klucz == "muchomornik" then
		return K.czerwony
	elseif klucz == "cierniowy_wilk" then
		return K.fiolet
	end
	return K.szary
end

-- model z kopii szablonu, tymi samymi krokami co Aktorzy.nowy w prototypie (rozdz. 4.3)
local function budujAktora(w, cfg: Instance, cf: CFrame)
	local wpis = (Tabela :: any).aktorzy[w.gatunek]
	local szablon = (szablonyRS :: Instance):FindFirstChild(w.gatunek)
	if not szablon then
		error("brak szablonu " .. w.gatunek)
	end
	local model = szablon:Clone() :: Model
	w.model = model -- od razu: przy błędzie niżej sprzątanie zniszczy klon
	model.Name = w.id
	model:SetAttribute("Lokalny", true)
	local hrp = model:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not hrp then
		error("szablon " .. w.gatunek .. " nie ma HumanoidRootPart")
	end
	hrp.Anchored = true
	model:PivotTo(cf)
	if cfg:GetAttribute("Wariant") == "bursztynowy" then
		-- Bursztynowy Slime: galareta (bryły z atrybutem Skora, budowa/szablon.luau) w kolorze bursztynu
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") and d:GetAttribute("Skora") ~= nil then
				d.Color = Stale.KOLOR_BURSZTYNOWY
			end
		end
	end
	local h = wpis.hrp
	w.przes = CFrame.new(h[1], h[2], h[3])
	local glowa = Instance.new("Attachment")
	glowa.Name = "Glowa" -- punkt „Pasek” z Aktor:punkt (nad głową), w układzie korzenia
	glowa.Position = Vector3.new(-h[1], (tonumber(wpis.pasek) or 3) - h[2], -h[3])
	glowa.Parent = hrp
	w.hrp, w.glowa, w.wpis = hrp, glowa, wpis
	model.Parent = folderWidokow
	local klipy = (Klipy :: any).nowy(model, daneAktorow[w.gatunek], { reczny = true })
	w.klipy = klipy
	local spoczynek = wpis.klipy and wpis.klipy.spoczynek
	if type(spoczynek) == "string" then
		klipy:graj(spoczynek, { petla = true, przejscie = 0 })
	end
	w.akcja = "spoczynek"
	klipy:krok(0)
	klipy:zastosuj()
	w.koszt = tonumber(wpis.liczbaCzesci) or 0
end

local function budujZastepczy(w, cfg: Instance, cf: CFrame)
	local wym = wymiary(w.gatunek)
	local model = Instance.new("Model")
	model.Name = w.id
	model:SetAttribute("Lokalny", true)
	local p = Instance.new("Part")
	p.Name = "Bryla"
	p.Size = Vector3.new(wym[1], wym[2], wym[3])
	p.Color = kolorZastepczy(w.gatunek, cfg:GetAttribute("Wariant"))
	p.Material = Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	w.przes = CFrame.new(0, wym[2] / 2, 0)
	p.CFrame = cf * w.przes
	p.Parent = model
	model.PrimaryPart = p
	local glowa = Instance.new("Attachment")
	glowa.Name = "Glowa"
	glowa.Position = Vector3.new(0, wym[2] / 2 + 0.9, 0)
	glowa.Parent = p
	w.model, w.hrp, w.glowa, w.wpis, w.klipy = model, p, glowa, nil, nil
	w.koszt = 1
	model.Parent = folderWidokow
end

-- tabliczka „poz. N” i miecze (rozdz. 4.4)
local SZER_TABLICZKI = 76
local SZER_BILLBOARDU = 140 -- tabliczka na środku, miecze obok w środku tego samego BillboardGui

local function odswiezTabliczke(w)
	if not w.etykieta then
		return -- tabliczka się nie zbudowała (błąd zgłoszony w pętli budowy)
	end
	local poziom = w.cfg:GetAttribute("Poziom")
	local tekst = "poz. " .. tostring(poziom or "?")
	if w.etykieta.Text ~= tekst then
		w.etykieta.Text = tekst
	end
	local pb = poziomBohatera()
	local czerwona = pb ~= nil and type(poziom) == "number" and poziom >= pb + Stale.CZERWONA_OD
	if w.czerwona ~= czerwona then
		w.czerwona = czerwona
		w.etykieta.BackgroundColor3 = if czerwona then K.czerwony else K.krem
	end
end

local function dodajTabliczke(w)
	local bb = Instance.new("BillboardGui")
	bb.Name = "Tabliczka"
	bb.Adornee = w.glowa
	bb.Size = UDim2.fromOffset(SZER_BILLBOARDU, 30)
	bb.MaxDistance = Stale.TABLICZKA_ZASIEG
	bb.AlwaysOnTop = false
	bb.LightInfluence = 0
	local etykieta = nowy("TextLabel", { Name = "Poziom", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(SZER_TABLICZKI, 30), BackgroundColor3 = K.krem, BorderSizePixel = 0, Font = KOMIKS,
		TextScaled = true, TextColor3 = K.bialy, Text = "poz. ?" }, bb)
	rog(etykieta, 0.3)
	obrys(etykieta, 2, true) -- biały tekst z obrysem tuszu
	nowy("UIPadding", { PaddingTop = UDim.new(0, 2), PaddingBottom = UDim.new(0, 2), PaddingLeft = UDim.new(0, 4),
		PaddingRight = UDim.new(0, 4) }, etykieta)
	-- miecze: dwa paski 4 × 24 obrócone o ±45° z poprzeczkami 10 × 3 (bez obrazków — zakaz uploadu)
	local miecze = nowy("Frame", { Name = "Miecze", AnchorPoint = Vector2.new(0, 0.5),
		Position = UDim2.new(0.5, SZER_TABLICZKI / 2 + 4, 0.5, 0), Size = UDim2.fromOffset(28, 28),
		BackgroundTransparency = 1, Visible = false }, bb)
	for i, kat in { 45, -45 } do
		local miecz = nowy("Frame", { Name = "Miecz" .. i, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromOffset(28, 28), BackgroundTransparency = 1, Rotation = kat }, miecze)
		local ostrze = nowy("Frame", { Name = "Ostrze", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromOffset(4, 24), BackgroundColor3 = K.bialy, BorderSizePixel = 0 }, miecz)
		obrys(ostrze, 1)
		local jelec = nowy("Frame", { Name = "Jelec", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 0.5, 7),
			Size = UDim2.fromOffset(10, 3), BackgroundColor3 = K.zolty, BorderSizePixel = 0 }, miecz)
		obrys(jelec, 1)
	end
	bb.Parent = w.model
	w.etykieta, w.miecze, w.czerwona = etykieta, miecze, nil
	odswiezTabliczke(w)
end

local function zniszczWidok(id: string)
	local w = widoki[id]
	if not w then
		return
	end
	widoki[id] = nil
	sumaCzesci -= w.koszt or 0
	if w.klipy then
		pcall(function()
			w.klipy:zniszcz()
		end)
	end
	if w.model then
		w.model:Destroy()
	end
end

local function zbudujWidok(cfg: Instance)
	local id = cfg.Name
	local klucz = cfg:GetAttribute("Gatunek")
	local pozA = cfg:GetAttribute("Pozycja")
	if type(klucz) ~= "string" or typeof(pozA) ~= "Vector3" then
		return
	end
	local yaw = cfg:GetAttribute("Kierunek")
	yaw = if type(yaw) == "number" then yaw else 0
	local poz = grunt(pozA)
	local cf = cfZiemi(poz, yaw)
	local w = { id = id, cfg = cfg, gatunek = klucz, poz = poz, cel = poz, predkosc = Vector3.zero, zostalo = 0,
		ostatniaPozycja = pozA, yaw = yaw, akcja = nil, stan = nil, animowany = false, koszt = 0,
		-- rozłożenie rzadszych klipów dalekich widoków na różne klatki (patrz krokWidoku)
		odl = (poz - workspace.CurrentCamera.CFrame.Position).Magnitude, dtKlipow = 0, klatkiKlipow = math.random(0, 2) }
	local gotowe = false
	if tryb == "aktorzy" and not zepsute[klucz] and Tabela and Tabela.aktorzy[klucz] and daneAktorow[klucz] then
		local ok, blad = pcall(budujAktora, w, cfg, cf)
		if ok then
			gotowe = true
		else
			zepsute[klucz] = true
			warn(P .. "nie zbudował się model " .. klucz .. " — ten gatunek pokazuję jako bryłę: " .. tostring(blad))
			if w.klipy then
				pcall(function()
					w.klipy:zniszcz()
				end)
			end
			if w.model then
				w.model:Destroy()
			end
			w.model, w.klipy, w.wpis = nil, nil, nil
		end
	end
	if not gotowe then
		budujZastepczy(w, cfg, cf)
	end
	-- poprawka recenzji: widok rejestrujemy PRZED tabliczką — gdyby tabliczka rzuciła błąd, model byłby już w
	-- Widoki, ale poza rejestrem, a pętla budowy klonowałaby go co 0,1 s od nowa (wyciek brył)
	widoki[id] = w
	sumaCzesci += w.koszt
	dodajTabliczke(w)
end

------------------------------------------------------------------ wybór widoków (co 0,5 s) i budowa (co 0,1 s)
local function wybierzWidoki()
	if walkaTrwa() then
		return -- kamera stoi przy arenie prototypu: wybór „najbliższych kamerze” poczeka do końca walki
	end
	if not biom or not biom.Parent then
		biom = workspace:FindFirstChild(Stale.NAZWA_BIOMU)
		promien.FilterDescendantsInstances = if biom then { biom } else {}
	end
	local oko = workspace.CurrentCamera.CFrame.Position
	local lista = {}
	for _, cfg in folderStanu:GetChildren() do
		if cfg:IsA("Configuration") and not ukryte[cfg.Name] then
			local poz = cfg:GetAttribute("Pozycja")
			if typeof(poz) == "Vector3" then
				table.insert(lista, { cfg = cfg, d = (poz - oko).Magnitude })
			end
		end
	end
	table.sort(lista, function(a, b)
		return a.d < b.d
	end)
	if wymuszony then
		for i, e in lista do
			if e.cfg.Name == wymuszony then
				table.remove(lista, i)
				table.insert(lista, 1, e)
				break
			end
		end
	end
	local ranga: { [string]: number } = {}
	local odleglosc: { [string]: number } = {}
	for i, e in lista do
		ranga[e.cfg.Name] = i
		odleglosc[e.cfg.Name] = e.d
	end
	-- niszczenie: poza 14 najbliższymi, dalej niż 135, ukryty albo zniknął
	for id in widoki do
		local r = ranga[id]
		if not r or r > Stale.MAKS_WIDOKOW_TWARDO or (odleglosc[id] > Stale.PROMIEN_USUNIECIA and id ~= wymuszony) then
			zniszczWidok(id)
		end
	end
	-- budowa: pierwsza dwunastka w promieniu 120 (kolejka w kolejności odległości)
	table.clear(kolejkaBudowy)
	for i = 1, math.min(#lista, Stale.MAKS_WIDOKOW) do
		local e = lista[i]
		if (e.d <= Stale.PROMIEN_WIDOKU or e.cfg.Name == wymuszony) and not widoki[e.cfg.Name] then
			table.insert(kolejkaBudowy, e.cfg.Name)
		end
	end
	-- klipy tylko dla 12 najbliższych istniejących widoków; dalsze stoją w ostatniej pozie
	local n = 0
	for _, e in lista do
		local w = widoki[e.cfg.Name]
		if w then
			n += 1
			w.animowany = n <= Stale.MAKS_WIDOKOW
			w.odl, w.ranga = e.d, n
		end
	end
	liczbaAnimowanych = math.min(n, Stale.MAKS_WIDOKOW)
	kontener:SetAttribute("KlientWidoki", n)
end

local function zbudujKolejny()
	if walkaTrwa() then
		return
	end
	while #kolejkaBudowy > 0 do
		local id = table.remove(kolejkaBudowy, 1) :: string
		local cfg = folderStanu:FindFirstChild(id)
		if cfg and not widoki[id] and not ukryte[id] then
			local klucz = cfg:GetAttribute("Gatunek")
			if type(klucz) == "string" and sumaCzesci + kosztWidoku(klucz) <= Stale.BUDZET_CZESCI then
				zbudujWidok(cfg)
				return -- najwyżej jeden klon na BUDOWA_CO
			end
			-- przekroczyłby budżet brył: nie budujemy (następny wybór spróbuje znowu)
		end
	end
end

folderStanu.ChildRemoved:Connect(function(cfg)
	zniszczWidok(cfg.Name)
	ukryte[cfg.Name] = nil
end)

------------------------------------------------------------------ podpowiedź E (rozdz. 4.5)
local kotwica = Instance.new("Part")
kotwica.Name = "KotwicaE"
kotwica.Size = Vector3.new(0.5, 0.5, 0.5)
kotwica.Transparency = 1
kotwica.Anchored = true
kotwica.CanCollide = false
kotwica.CanQuery = false
kotwica.CanTouch = false
kotwica.CastShadow = false
kotwica.CFrame = CFrame.new(0, 100, 0) -- byle gdzie (podpowiedź wyłączona); nie poniżej FallenPartsDestroyHeight
kotwica.Parent = folderWidokow

local podpowiedz = Instance.new("ProximityPrompt")
podpowiedz.Name = "PodpowiedzLasu"
podpowiedz.KeyboardKeyCode = Enum.KeyCode.E
podpowiedz.GamepadKeyCode = Enum.KeyCode.ButtonX
podpowiedz.HoldDuration = 0
podpowiedz.RequiresLineOfSight = false
podpowiedz.ClickablePrompt = true -- na telefonie podpowiedź jest przyciskiem do stuknięcia
podpowiedz.MaxActivationDistance = 40 -- bramkę (8 + promień, wysokość ≤ 6) robimy sami
podpowiedz.ActionText = "Walcz"
podpowiedz.ObjectText = ""
podpowiedz.Enabled = false
podpowiedz.Parent = kotwica

local kandydat: string? = nil

local function wybierzKandydata(): string?
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp or not hrp:IsA("BasePart") then
		return nil
	end
	local p = hrp.Position
	local najlepszy, najblizej = nil, math.huge
	for _, cfg in folderStanu:GetChildren() do
		if not cfg:IsA("Configuration") or ukryte[cfg.Name] or cfg:GetAttribute("Stan") == "zajety" then
			continue
		end
		local poz = cfg:GetAttribute("Pozycja")
		if typeof(poz) ~= "Vector3" or math.abs(poz.Y - p.Y) > Stale.MAKS_ROZNICA_WYSOKOSCI then
			continue
		end
		local g = gatunek(cfg:GetAttribute("Gatunek"))
		local zasieg = Stale.ZASIEG_E + (if g and type(g.promien) == "number" then g.promien else 0)
		-- M6: bieżący kandydat ma zapas (podpowiedź nie miga przy chodzącym potworze; serwer ma większy zapas)
		if cfg.Name == kandydat and kontener:GetAttribute(Stale.ATRYBUT_KOTWICY_STAREJ) ~= true then
			zasieg += Stale.HISTEREZA_E
		end
		local d = Vector2.new(poz.X - p.X, poz.Z - p.Z).Magnitude
		if d <= zasieg and d < najblizej then
			najlepszy, najblizej = cfg.Name, d
		end
	end
	return najlepszy
end

-- punkt nad głową kandydata: głowa widoku albo Pozycja + pół wysokości.
-- Poprawka wdrożenia (15.11, Studio): ProximityPrompt działa tylko wtedy, gdy jego kotwica jest na ekranie. Punkt
-- „Pasek” Strażnika jest ok. 15,6 studa nad posadzką, więc gracz stojący przy nim miał kotwicę nad górną krawędzią
-- kadru — podpowiedź była włączona, ale niewidoczna, i E nic nie robiło. Kotwica stoi więc najwyżej
-- KOTWICA_MAKS_WYS nad ziemią (slime, muchomornik i wilk są niżsi, więc u nich nic się nie zmienia).
local KOTWICA_MAKS_WYS = 5.5
local function punktKotwicy(id: string): Vector3?
	local w = widoki[id]
	if w and w.glowa and w.glowa.Parent then
		local p = w.glowa.WorldPosition
		local sufit = w.poz.Y + KOTWICA_MAKS_WYS
		return if p.Y > sufit then Vector3.new(p.X, sufit, p.Z) else p
	end
	local cfg = folderStanu:FindFirstChild(id)
	local poz = cfg and cfg:GetAttribute("Pozycja")
	if typeof(poz) == "Vector3" then
		return poz + Vector3.new(0, math.min(wymiary(cfg:GetAttribute("Gatunek"))[2] / 2, KOTWICA_MAKS_WYS), 0)
	end
	return nil
end

-- M6 (17.11.2026, przejście gry: E przy chodzących potworach zaczęło walkę w 6 z 15 prób, z kamerą za plecami postaci
-- — od razu): ProximityPrompt pokazuje się i przyjmuje E tylko wtedy, gdy jego kotwica jest w kadrze (linii widzenia
-- nie wymaga — RequiresLineOfSight = false). Gdy kamera patrzy na postać z przodu albo z boku, potwór obok niej bywa
-- za kamerą albo poza kadrem: podpowiedź znikała, a E nic nie robiło. Teraz, gdy punkt nad potworem jest poza kadrem,
-- kotwica staje nad głową postaci (lekko w stronę potwora) — w kamerze trzeciej osoby postać jest zawsze w kadrze.
local function naEkranie(p: Vector3): boolean
	local kamera = workspace.CurrentCamera
	if not kamera then
		return true
	end
	local v, widac = kamera:WorldToViewportPoint(p)
	local r = kamera.ViewportSize
	local m = Stale.MARGINES_EKRANU_E
	return widac and v.Z > 0 and v.X >= r.X * m and v.X <= r.X * (1 - m) and v.Y >= r.Y * m and v.Y <= r.Y * (1 - m)
end

local function punktPodpowiedzi(id: string): Vector3?
	local p = punktKotwicy(id)
	if not p or kontener:GetAttribute(Stale.ATRYBUT_KOTWICY_STAREJ) == true or naEkranie(p) then
		return p
	end
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp or not hrp:IsA("BasePart") then
		return p
	end
	local ku = Vector3.new(p.X - hrp.Position.X, 0, p.Z - hrp.Position.Z)
	local krok = if ku.Magnitude > 0.1 then ku.Unit * Stale.KOTWICA_KU_POTWOROWI else Vector3.zero
	local nadGlowa = hrp.Position + krok + Vector3.new(0, Stale.KOTWICA_NAD_POSTACIA, 0)
	if naEkranie(nadGlowa) then
		return nadGlowa
	end
	-- kamera tuż przy postaci (np. między nią a potworem): kotwica przed kamerą, pod środkiem kadru — zawsze widać
	local kamera = workspace.CurrentCamera
	if kamera then
		local przed = kamera.CFrame.Position + kamera.CFrame.LookVector * Stale.KOTWICA_PRZED_KAMERA
			- kamera.CFrame.UpVector * (Stale.KOTWICA_PRZED_KAMERA * 0.25)
		if (przed - hrp.Position).Magnitude < podpowiedz.MaxActivationDistance - 2 then
			return przed
		end
	end
	return nadGlowa
end

local function odswiezPodpowiedz()
	kandydat = if walkaTrwa() then nil else wybierzKandydata()
	local cfg = kandydat and folderStanu:FindFirstChild(kandydat)
	if not cfg then
		kandydat = nil
		if podpowiedz.Enabled then
			podpowiedz.Enabled = false
		end
		return
	end
	local nazwa = cfg:GetAttribute("Nazwa")
	local obiekt = string.format("%s · poz. %s", tostring(nazwa or "?"), tostring(cfg:GetAttribute("Poziom") or "?"))
	local akcja
	if not Odtwarzacz then
		akcja = "Walka niedostępna"
	else
		local zostalo = Odtwarzacz.wolnaZa()
		akcja = if zostalo > 0 then string.format("Walcz (za %d s)", math.ceil(zostalo)) else "Walcz"
	end
	if podpowiedz.ObjectText ~= obiekt then
		podpowiedz.ObjectText = obiekt
	end
	if podpowiedz.ActionText ~= akcja then
		podpowiedz.ActionText = akcja
	end
	local punkt = punktPodpowiedzi(kandydat :: string)
	if punkt then
		kotwica.CFrame = CFrame.new(punkt)
	end
	if not podpowiedz.Enabled then
		podpowiedz.Enabled = true
	end
end

------------------------------------------------------------------ walka (rozdz. 4.6, 5.1)
-- Poprawka P2 w odtwarzaczu (rozdz. 6) jest wgrana: panel wyniku bez JESZCZE RAZ (rewanż po przegranej = ponowne E).
local OPCJE_WALKI = { bezPowtorki = true }
local mojaWalka: { id: string, gatunek: string, straznik: boolean }? = nil
local poWalce: () -> () -- niżej

local prosbaWalkiOd = -math.huge -- M6: kiedy ten las ostatnio poprosił o walkę (odmowa po tym czasie → dymek)

local function zacznijWalke(id: string): boolean
	-- M6: odmowa po stronie klienta nie jest już cicha (np. blokada po przewiniętej walce: serwer liczy pełny czas ×1)
	if not Odtwarzacz then
		pokazKomunikat(Stale.KOMUNIKATY_ODMOWY.brak_odtwarzacza)
		return false
	end
	if Odtwarzacz.czyTrwa() then
		return false
	end
	local zostalo = Odtwarzacz.wolnaZa()
	if zostalo > 0 then
		pokazKomunikat(string.format(Stale.KOMUNIKATY_ODMOWY.odpoczynek, math.max(1, math.ceil(zostalo))))
		return false
	end
	if mojaWalka then
		poWalce() -- wynik poprzedniej walki jeszcze nieodczytany (pętla co 0,25 s) — najpierw on
	end
	local cfg = folderStanu:FindFirstChild(id)
	local klucz = cfg and cfg:GetAttribute("Gatunek")
	mojaWalka = {
		id = id,
		gatunek = if type(klucz) == "string" then klucz else "",
		straznik = cfg ~= nil and (cfg:GetAttribute("Straznik") == true or klucz == "straznik_lasu"),
	}
	kontener:SetAttribute("OstatniWynik", nil) -- lokalnie; odtwarzacz ustawi go w Sesja:pokazWynik
	kontener:SetAttribute("OstatniaOdmowa", nil) -- M6: odtwarzacz wpisze tu powód odmowy serwera → dymek (niżej)
	prosbaWalkiOd = os.clock()
	zsynchronizujBohatera() -- poza trybem testowym: klasa gracza (stan gracza)
	-- odtwarzacz sam wysyła prośbę do kontener.Zdalne.RozpocznijWalke2: trzy napisy z list (D-016)
	task.spawn(Odtwarzacz.uruchom, kontener, { klasa = bohater.klasa, przeciwnik = id, poziom = bohater.poziom }, OPCJE_WALKI)
	return true
end

podpowiedz.Triggered:Connect(function(kto: Player)
	if kto ~= gracz then
		return
	end
	local id = kandydat
	if id then
		zacznijWalke(id)
	end
end)

-- M6: E bez podpowiedzi (potwór właśnie odszedł z zasięgu) — zamiast ciszy dymek „Podejdź bliżej”, gdy jakiś wolny
-- potwór jest niedaleko (do Stale.ZASIEG_E + promień + Stale.ZASIEG_DYMKU_E); daleko od potworów E nic nie mówi
game:GetService("UserInputService").InputBegan:Connect(function(wejscie: InputObject, przetworzone: boolean)
	if przetworzone or wejscie.KeyCode ~= Enum.KeyCode.E or podpowiedz.Enabled or walkaTrwa() then
		return
	end
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp or not hrp:IsA("BasePart") then
		return
	end
	local p = hrp.Position
	for _, cfg in folderStanu:GetChildren() do
		local poz = cfg:GetAttribute("Pozycja")
		if typeof(poz) == "Vector3" and cfg:GetAttribute("Stan") ~= "zajety" and not ukryte[cfg.Name]
			and math.abs(poz.Y - p.Y) <= Stale.MAKS_ROZNICA_WYSOKOSCI then
			local g = gatunek(cfg:GetAttribute("Gatunek"))
			local zasieg = Stale.ZASIEG_E + (if g and type(g.promien) == "number" then g.promien else 0) + Stale.ZASIEG_DYMKU_E
			if Vector2.new(poz.X - p.X, poz.Z - p.Z).Magnitude <= zasieg then
				pokazKomunikat(Stale.KOMUNIKATY_ODMOWY.za_daleko)
				return
			end
		end
	end
end)

function poWalce()
	local walka = mojaWalka
	if not walka then
		return
	end
	mojaWalka = nil
	local wynik = kontener:GetAttribute("OstatniWynik")
	kontener:SetAttribute("KlientOstatniaWalka", walka.id .. "/" .. tostring(wynik))
	if wynik == "wygrana" then
		-- widok znika od razu; serwer usunie potwora po zajetyDo (inni widzą do tego czasu miecze).
		-- Poprawka wdrożenia: odtwarzanie trwa dłużej niż walka.czas (wejście i okno wyniku), więc serwer zwykle usunął
		-- już Configuration — wtedy nie wpisujemy id na listę ukrytych (ChildRemoved już przeszło i nie wyczyściłoby go).
		if folderStanu:FindFirstChild(walka.id) then
			ukryte[walka.id] = true
		end
		zniszczWidok(walka.id)
		if walka.straznik then
			-- jeden baner (17.11.2026): podpis może podmienić inny skrypt kontenera (las-pas: brama do Bagna otwarta);
			-- atrybut jest lokalny i zużywany tutaj — skrypt, który go ustawił, nie pokazuje już własnego banera
			local podpis = kontener:GetAttribute("PodpisBaneraStraznika")
			if type(podpis) == "string" and podpis ~= "" then
				kontener:SetAttribute("PodpisBaneraStraznika", nil)
				kontener:SetAttribute("BanerStraznikaZPodpisem", podpis)
			else
				podpis = Stale.PODPIS_STRAZNIKA
			end
			pokazBaner(Stale.TYTUL_BANERA_STRAZNIKA, podpis, Stale.BANER_S)
		end
	end
	-- zabezpieczenie: odtwarzacz przywraca kamerę sam; gdyby jednak została skryptowa — zwykła kamera postaci
	task.delay(0.5, function()
		local kamera = workspace.CurrentCamera
		if not walkaTrwa() and kamera.CameraType == Enum.CameraType.Scriptable then
			local postac = gracz.Character
			local hum = postac and postac:FindFirstChildOfClass("Humanoid")
			kamera.CameraType = Enum.CameraType.Custom
			if hum then
				kamera.CameraSubject = hum
			end
		end
	end)
end

------------------------------------------------------------------ panel bohatera (rozdz. 4.6)
local panelPrzycisk: GuiObject? = nil
local panelOkno: GuiObject? = nil
local panelWidoczny: boolean? = nil

-- czy postać stoi w lesie tego kontenera (płyta biomu z zapasem); bez danych o płycie — zawsze (jak dawniej)
local function wLesie(): boolean
	if not Stale.PANEL_TYLKO_W_LESIE or not obszarLasu then
		return true
	end
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp or not hrp:IsA("BasePart") then
		return false
	end
	local p = hrp.Position
	local o = obszarLasu :: any
	return p.X >= o.x1 and p.X <= o.x2 and p.Z >= o.z1 and p.Z <= o.z2
end

-- jeden panel na ekranie (17.11.2026): przycisk i okno tylko w lesie tego kontenera; ScreenGui zostaje włączony
-- (Enabled przełącza odtwarzacz walki, gdy chowa GUI na czas walki — tu go nie ruszamy)
local function odswiezWidocznoscPanelu()
	local widac = wLesie()
	if panelPrzycisk and panelPrzycisk.Visible ~= widac then
		panelPrzycisk.Visible = widac
	end
	if not widac and panelOkno and panelOkno.Visible then
		panelOkno.Visible = false
	end
	if panelWidoczny ~= widac then
		panelWidoczny = widac
		kontener:SetAttribute("KlientPanelWidoczny", widac) -- lokalnie, do testów
	end
end

local function zbudujPanel()
	local playerGui = gracz:WaitForChild("PlayerGui")
	local stary = playerGui:FindFirstChild(Stale.GUI_BOHATERA)
	if stary then
		stary:Destroy()
	end
	local gui = nowy("ScreenGui", { Name = Stale.GUI_BOHATERA, ResetOnSpawn = false, IgnoreGuiInset = false, DisplayOrder = 5,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, nil)
	gui:SetAttribute("Wygenerowane", true)
	-- wdrożenie 15.11: kontrakt mówi „lewy górny róg”, ale tam stoi HUD gry (portret gracza) i przycisk na niego
	-- nachodził — przycisk stoi więc u góry na środku, gdzie ekran jest wolny (także w emulatorze telefonu)
	local przycisk = nowy("TextButton", { Name = "Przycisk", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, Stale.PANEL_Y),
		Size = UDim2.fromOffset(250, 34),
		BackgroundColor3 = K.krem, TextColor3 = K.tusz, Font = KOMIKS, TextScaled = true, AutoButtonColor = false,
		BorderSizePixel = 0, Text = "" }, gui)
	rog(przycisk, 0.3)
	obrys(przycisk, 3)
	nowy("UIPadding", { PaddingLeft = UDim.new(0, 8), PaddingRight = UDim.new(0, 8), PaddingTop = UDim.new(0, 4),
		PaddingBottom = UDim.new(0, 4) }, przycisk)

	local okno = nowy("Frame", { Name = "Okno", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(360, 220), BackgroundColor3 = K.krem, BorderSizePixel = 0, Visible = false, ZIndex = 2 }, gui)
	rog(okno, 0.08)
	obrys(okno, 4)
	nowy("TextLabel", { Name = "Tytul", BackgroundTransparency = 1, Position = UDim2.fromOffset(12, 6), Size = UDim2.new(1, -24, 0, 28),
		Font = KOMIKS, TextScaled = true, Text = "TWÓJ BOHATER (TEST)", TextColor3 = K.tusz, ZIndex = 3 }, okno)
	-- Poprawka kontroli (15.11, wycinek ekranu telefonu): szare nagłówki na kremowym tle były ledwo widoczne,
	-- więc nagłówki mają kolor tuszu jak tytuł; od tytułu różnią się wielkością.
	local function naglowek(tekst: string, y: number)
		nowy("TextLabel", { Name = "Naglowek", BackgroundTransparency = 1, Position = UDim2.fromOffset(12, y), Size = UDim2.new(1, -24, 0, 16),
			Font = KOMIKS, TextScaled = true, Text = tekst, TextColor3 = K.tusz, TextXAlignment = Enum.TextXAlignment.Left, ZIndex = 3 }, okno)
	end
	local function opcja(nazwa: string, tekst: string, x: number, y: number, szer: number)
		local b = nowy("TextButton", { Name = nazwa, Position = UDim2.fromOffset(x, y), Size = UDim2.fromOffset(szer, 40),
			BackgroundColor3 = K.bialy, TextColor3 = K.tusz, Font = KOMIKS, TextScaled = true, AutoButtonColor = false,
			BorderSizePixel = 0, Text = tekst, ZIndex = 3 }, okno)
		rog(b, 0.2)
		obrys(b, 3)
		nowy("UIPadding", { PaddingTop = UDim.new(0, 6), PaddingBottom = UDim.new(0, 6), PaddingLeft = UDim.new(0, 4),
			PaddingRight = UDim.new(0, 4) }, b)
		return b
	end

	naglowek("KLASA", 38)
	local przyciskiKlas: { [string]: TextButton } = {}
	for i, klasa in Stale.KLASY do
		local b = opcja("Klasa_" .. klasa, string.upper(NAZWY_KLAS[klasa] or klasa), 12 + (i - 1) * 114, 56, 108)
		przyciskiKlas[klasa] = b
		b.Activated:Connect(function()
			ustawBohatera(klasa, bohater.poziom)
		end)
	end
	naglowek("POZIOM BOHATERA (AUTO = POZIOM POTWORA)", 102)
	local przyciskiPoziomow: { [string]: TextButton } = {}
	for i, poziom in Stale.POZIOMY_BOHATERA do
		local b = opcja("Poziom_" .. poziom, if poziom == "auto" then "AUTO" else poziom, 12 + (i - 1) * 85, 120, 79)
		przyciskiPoziomow[poziom] = b
		b.Activated:Connect(function()
			ustawBohatera(bohater.klasa, poziom)
		end)
	end
	local gotowe = nowy("TextButton", { Name = "Gotowe", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 170),
		Size = UDim2.fromOffset(170, 40), BackgroundColor3 = K.zielony, TextColor3 = K.bialy, Font = KOMIKS, TextScaled = true,
		AutoButtonColor = false, BorderSizePixel = 0, Text = "GOTOWE", ZIndex = 3 }, okno)
	rog(gotowe, 0.25)
	obrys(gotowe, 3)
	obrys(gotowe, 2, true) -- białe litery z obrysem tuszu
	nowy("UIPadding", { PaddingTop = UDim.new(0, 6), PaddingBottom = UDim.new(0, 6) }, gotowe)

	local function odswiez()
		if trybTestowyBohatera() then
			przycisk.Text = Stale.PANEL_PREFIKS .. string.format("Bohater: %s · poz. %s", NAZWY_KLAS[bohater.klasa] or bohater.klasa, bohater.poziom)
		else
			-- stan gracza: tylko napis (klasa ze startu, poziom gracza); okna wyboru T1 nie ma
			przycisk.Text = Stale.PANEL_PREFIKS .. string.format("Twój bohater: %s · poziom %d", NAZWY_KLAS[bohater.klasa] or bohater.klasa, poziomGracza())
			okno.Visible = false
		end
		for klasa, b in przyciskiKlas do
			b.BackgroundColor3 = if klasa == bohater.klasa then K.zolty else K.bialy
			b:SetAttribute("Wybrany", klasa == bohater.klasa)
		end
		for poziom, b in przyciskiPoziomow do
			b.BackgroundColor3 = if poziom == bohater.poziom then K.zolty else K.bialy
			b:SetAttribute("Wybrany", poziom == bohater.poziom)
		end
	end
	przycisk.Activated:Connect(function()
		okno.Visible = trybTestowyBohatera() and not okno.Visible
	end)
	gotowe.Activated:Connect(function()
		okno.Visible = false
	end)
	naZmianeBohatera = function()
		odswiez()
		for _, w in widoki do
			odswiezTabliczke(w)
		end
	end
	odswiez()
	panelPrzycisk, panelOkno = przycisk, okno
	odswiezWidocznoscPanelu()
	gui.Parent = playerGui
	return gui
end

-- pomiar kosztu (wdrożenie 15.11; tylko do testów): koszt[nazwa] = { suma, n, maks } w sekundach
local koszt: { [string]: { number } } = {}
local kosztOd = os.clock()
local function zmierz(nazwa: string, s: number)
	local k = koszt[nazwa]
	if not k then
		k = { 0, 0, 0 }
		koszt[nazwa] = k
	end
	k[1] += s
	k[2] += 1
	if s > k[3] then
		k[3] = s
	end
end

local function opisKosztu(zeruj: any)
	local okno = os.clock() - kosztOd
	local wynik = { okno = okno }
	for nazwa, k in koszt do
		-- sr i maks w ms na wywołanie; naSekunde = ms pracy na sekundę gry
		wynik[nazwa] = { sr = if k[2] > 0 then k[1] / k[2] * 1000 else 0, maks = k[3] * 1000, n = k[2],
			naSekunde = if okno > 0 then k[1] * 1000 / okno else 0 }
	end
	if zeruj == true then
		table.clear(koszt)
		kosztOd = os.clock()
	end
	return wynik
end

------------------------------------------------------------------ klatka (wygładzanie, grunt, obrót, klipy — rozdz. 4.2)
-- Poprawka wdrożenia (15.11, pomiar w Studio): 7 wilków w Ostępach kosztowało 2,2 ms na klatkę (cel: < 1 ms). Prawie
-- cały koszt to przestawienie korzenia (hrp.CFrame) modelu z 544 bryłami na spawach — ok. 0,31 ms na wilka na klatkę;
-- klipy (Klipy:krok + zastosuj) to tylko ok. 0,02 ms. Dlatego (1) widok spoza KLATKA_PELNA_RANGA najbliższych i dalej
-- niż KLATKA_PELNA_DO od kamery przestawiamy i animujemy co KLATKA_CO_DALEJ klatek (dalej niż KLATKA_POLOWA_DO — co
-- KLATKA_CO_DALEKO), z sumą dt, więc tempo ruchu i klipów się nie zmienia (rozdz. 10, łagodniejsza wersja cięcia 3);
-- (2) korzenia nie przestawiamy, gdy położenie i obrót się nie zmieniły (stojący potwór).
local lodKlipow = true -- haczyk „lod”, false → każdy widok co klatkę (do porównań)
local function krokWidoku(w, dt: number, liczKlipy: boolean)
	local cfg = w.cfg
	local pa = cfg:GetAttribute("Pozycja")
	if typeof(pa) == "Vector3" and pa ~= w.ostatniaPozycja then
		w.ostatniaPozycja = pa
		local cel = grunt(pa)
		if (cel - w.poz).Magnitude > Stale.SKOK_WYGLADZANIA then
			w.poz, w.cel, w.zostalo = cel, cel, 0 -- duży skok: przestawienie bez wygładzania
		else
			-- dojdzie do celu dokładnie wtedy, gdy przyjdzie następny (4 Hz)
			w.cel = cel
			w.predkosc = (cel - w.poz) / Stale.OKRES_RUCHU
			w.zostalo = Stale.OKRES_RUCHU
		end
	end
	if w.zostalo > 0 then
		local k = math.min(dt, w.zostalo)
		w.poz += w.predkosc * k
		w.zostalo -= k
		if w.zostalo <= 0 then
			w.poz = w.cel
		end
	end
	local kier = cfg:GetAttribute("Kierunek")
	if type(kier) == "number" then
		local roznica = (kier - w.yaw + math.pi) % (2 * math.pi) - math.pi -- najkrótsza droga
		local maks = Stale.OBROT_NA_S * dt
		w.yaw = (w.yaw + math.clamp(roznica, -maks, maks)) % (2 * math.pi)
	end
	local stan = cfg:GetAttribute("Stan")
	if stan ~= w.stan and w.miecze then
		w.stan = stan
		w.miecze.Visible = stan == "zajety"
	end
	-- co ile klatek przestawiamy model i liczymy klipy (położenie w pamięci i tak idzie co klatkę)
	w.dtKlipow += dt
	w.klatkiKlipow += 1
	local co = 1
	if lodKlipow then
		local odl, ranga = w.odl or 0, w.ranga or 1
		if ranga > Stale.KLATKA_PELNA_RANGA and odl > Stale.KLATKA_PELNA_DO then
			co = if odl <= Stale.KLATKA_POLOWA_DO then Stale.KLATKA_CO_DALEJ else Stale.KLATKA_CO_DALEKO
		end
	end
	if w.klatkiKlipow < co then
		return
	end
	local dtk = w.dtKlipow
	w.dtKlipow, w.klatkiKlipow = 0, 0
	if w.poz ~= w.zapisanaPoz or w.yaw ~= w.zapisanyYaw then
		w.zapisanaPoz, w.zapisanyYaw = w.poz, w.yaw
		local t0 = os.clock()
		w.hrp.CFrame = cfZiemi(w.poz, w.yaw) * w.przes
		zmierz("korzen", os.clock() - t0)
	end
	if w.klipy and w.animowany and liczKlipy then
		local akcja = if stan == "idzie" then "ruch" else "spoczynek"
		if akcja ~= w.akcja then
			w.akcja = akcja
			local nazwa = w.wpis and w.wpis.klipy and w.wpis.klipy[akcja]
			if type(nazwa) == "string" then
				w.klipy:graj(nazwa, { petla = true, przejscie = 0.2 })
			end
		end
		local t0 = os.clock()
		w.klipy:krok(dtk)
		w.klipy:zastosuj()
		zmierz("klipy", os.clock() - t0)
	end
end

local polaczenieKlatki: RBXScriptConnection? = nil
polaczenieKlatki = RunService.PreSimulation:Connect(function(dt: number)
	if not kontener.Parent then
		if polaczenieKlatki then
			polaczenieKlatki:Disconnect()
		end
		return
	end
	local t0 = os.clock()
	local ok, blad = xpcall(function()
		local liczKlipy = not walkaTrwa()
		for _, w in widoki do
			if w.cfg.Parent then
				krokWidoku(w, dt, liczKlipy)
			end
		end
		if kandydat and podpowiedz.Enabled then
			local punkt = punktPodpowiedzi(kandydat)
			if punkt then
				kotwica.CFrame = CFrame.new(punkt)
			end
		end
	end, debug.traceback)
	zmierz("klatka", os.clock() - t0)
	if not ok then
		zglosBlad("klatka", blad)
	end
end)

------------------------------------------------------------------ pętle
local function petla(nazwa: string, okres: number, f: () -> ())
	task.spawn(function()
		while kontener.Parent do
			local t0 = os.clock()
			local ok, blad = xpcall(f, debug.traceback)
			zmierz(nazwa, os.clock() - t0)
			if not ok then
				zglosBlad(nazwa, blad)
			end
			task.wait(okres)
		end
	end)
end

petla("wybór widoków", Stale.WYBOR_CO, wybierzWidoki)
petla("budowa widoków", Stale.BUDOWA_CO, zbudujKolejny)
petla("podpowiedź", Stale.PODPOWIEDZ_CO, odswiezPodpowiedz)
petla("koniec walki", 0.25, function()
	if mojaWalka and not walkaTrwa() then
		poWalce()
	end
end)
petla("panel bohatera", 0.5, odswiezWidocznoscPanelu)

local guiBohatera: Instance? = nil
do
	local ok, wynik = pcall(zbudujPanel)
	if ok then
		guiBohatera = wynik
	else
		zglosBlad("panel bohatera", wynik)
	end
end
kontener:SetAttribute("KlientKlasa", bohater.klasa)
kontener:SetAttribute("KlientPoziom", bohater.poziom)

-- stan gracza: panel idzie za klasą i poziomem gracza, za trybem testowym i za kontenerem stanu (pojawia się / znika)
local function poZmianieStanuGracza()
	local udalo, blad = pcall(zsynchronizujBohatera)
	if not udalo then
		zglosBlad("stan gracza", blad)
	end
end
gracz:GetAttributeChangedSignal(Stale.ATRYBUT_KLASY_GRACZA):Connect(poZmianieStanuGracza)
gracz:GetAttributeChangedSignal(Stale.ATRYBUT_POZIOMU_GRACZA):Connect(poZmianieStanuGracza)
kontener:GetAttributeChangedSignal(Stale.ATRYBUT_TESTU_BOHATERA):Connect(poZmianieStanuGracza)
workspace.ChildAdded:Connect(function(d: Instance)
	if d.Name == Stale.KONTENER_STANU then
		task.delay(1, poZmianieStanuGracza)
	end
end)
workspace.ChildRemoved:Connect(function(d: Instance)
	if d.Name == Stale.KONTENER_STANU then
		poZmianieStanuGracza()
	end
end)
poZmianieStanuGracza()

-- M6: odmowa serwera po E (odtwarzacz wpisuje powód do OstatniaOdmowa tego kontenera) → dymek lasu z powodem. Ogólny
-- dymek prototypu (KlientWalki2, „Serwer nie przyjął tego wyboru…”) w lesie mylił, więc zastępujemy go naszym.
kontener:GetAttributeChangedSignal("OstatniaOdmowa"):Connect(function()
	local powod = kontener:GetAttribute("OstatniaOdmowa")
	if type(powod) ~= "string" or os.clock() - prosbaWalkiOd > 20 then
		return
	end
	task.delay(0.1, function()
		local playerGui = gracz:FindFirstChildOfClass("PlayerGui")
		local ogolny = playerGui and playerGui:FindFirstChild(Stale.GUI_KOMUNIKATU_PROTOTYPU)
		if ogolny then
			ogolny:Destroy()
		end
		pokazKomunikat(Stale.KOMUNIKATY_ODMOWY[powod] or Stale.KOMUNIKATY_ODMOWY.blad_silnika)
	end)
end)

-- sprzątanie własnych ScreenGui, gdy kontener zniknie (np. koniec testu)
kontener.AncestryChanged:Connect(function()
	if not kontener:IsDescendantOf(game) then
		if guiBohatera then
			guiBohatera:Destroy()
		end
		local playerGui = gracz:FindFirstChildOfClass("PlayerGui")
		local baner = playerGui and playerGui:FindFirstChild(Stale.GUI_BANERA)
		if baner then
			baner:Destroy()
		end
	end
end)

------------------------------------------------------------------ haczyk testowy (rozdz. 8.6)
local sterowanie = sygnaly:WaitForChild("SterowanieKlienta", 5)
if sterowanie and sterowanie:IsA("BindableFunction") then
	sterowanie.OnInvoke = function(polecenie: string, a: any, b: any)
		if polecenie == "stan" then
			local n, nUkrytych = 0, 0
			for _ in widoki do
				n += 1
			end
			for _ in ukryte do
				nUkrytych += 1
			end
			return {
				tryb = tryb, widoki = n, animowane = liczbaAnimowanych, czesciWidokow = sumaCzesci, najblizszy = kandydat,
				podpowiedz = podpowiedz.Enabled, bohater = { klasa = bohater.klasa, poziom = bohater.poziom },
				walka = walkaTrwa(), ukryte = nUkrytych, bledy = licznikBledow,
			}
		elseif polecenie == "walcz" then
			if type(a) ~= "string" then
				return false
			end
			return zacznijWalke(a)
		elseif polecenie == "bohater" then
			return ustawBohatera(a, b)
		elseif polecenie == "koszt" then
			return opisKosztu(a)
		elseif polecenie == "lod" then
			lodKlipow = a ~= false
			return lodKlipow
		elseif polecenie == "wymus" then
			-- (16.11, przelot kamery lasu-pasa) ten widok budujemy zawsze i przed innymi; nil = koniec wymuszenia
			wymuszony = if type(a) == "string" then a else nil
			return true
		elseif polecenie == "klip" then
			-- (16.11) jednorazowy klip b na widoku a (np. ryk Strażnika w przelocie), potem spoczynek → bool
			local w = if type(a) == "string" then widoki[a] else nil
			if not w or not w.klipy or type(b) ~= "string" or not w.klipy:maKlip(b) then
				return false
			end
			local spoczynek = w.wpis and w.wpis.klipy and w.wpis.klipy.spoczynek
			w.klipy:graj(b, { petla = false, przejscie = 0.15, potem = if type(spoczynek) == "string" then spoczynek else nil })
			-- bieżąca akcja zostaje „ta sama”, więc krokWidoku nie przerwie klipu własnym spoczynkiem / ruchem
			w.akcja = if w.cfg:GetAttribute("Stan") == "idzie" then "ruch" else "spoczynek"
			return true
		end
		return false
	end
else
	warn(P .. "brak Sygnaly/SterowanieKlienta (BindableFunction) — haczyk testowy klienta wyłączony")
end

kontener:SetAttribute("KlientGotowy", true)
print(P .. "klient gotowy: tryb " .. tryb .. ", potworów w Stan: " .. #folderStanu:GetChildren())
