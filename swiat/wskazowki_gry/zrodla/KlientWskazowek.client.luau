--[[
	KlientWskazowek — wskazówki celu dla nowego gracza (Script, RunContext = Client, w kontenerze Workspace/WskazowkiGry).
	Status: propozycja (raport przejścia gry 17.11.2026, M3: „brak celu w pierwszej minucie”).

	Co robi (tylko u tego gracza, niczego nie wysyła do serwera i nie zmienia cudzych instancji):
		1. Linijka celu u góry ekranu (własny ScreenGui „WskazowkiGry”) z krzyżykiem — jedno kliknięcie chowa wskazówki
		   do końca sesji (haczyk testowy "wlacz" je przywraca).
		2. Strzałka obok przycisku TELEPORT w HUD Pawła (tylko czyta jego położenie — HUD-u nie zmienia) albo znacznik
		   w świecie nad celem: najbliższy potwór, Strażnik Gaju, Kamień Powrotu, trener, brama za Strażnikiem,
		   jajko biomu (od 26.11.2026 nowe jajka ze scenką Pawła: leśne w mieście przy zagrodzie, Bagna i Dżungli przy
		   przybyciu biomu — gdy Rybek wystarcza na pierwsze jajko tego biomu; w lesie znacznik nad Kamieniem Powrotu).
		3. Krok wynika ze stanu gracza (LogikaWskazowek.krok): klasa, wynik ostatniej walki w lesie, pokonany Strażnik,
		   położenie (prostokąty biomów z ich danych: las-pas, Bagno), stan gracza (swiat/stan_gracza: poziomy i trening), a nie ze
		   sztywnego scenariusza. Bez StanGracza kroki o poziomach i treningu się nie pokazują.
		4. Schowane, gdy trwa walka, przelot, chmury, mini-gra, wybór klasy albo gdy HUD jest schowany — nie zasłania
		   HUD-u ani ekranu walki.
	Źródła (tylko odczyt): atrybuty gracza Class, Level, PokonalStraznikaLasu, TreningAFK (z danych); atrybuty klienta kontenerów
	lasu (OstatniWynik, OstatnieZiarno, KlientOstatniaWalka — ustawia je odtwarzacz walki); moduł DanePasa lasu-pasa;
	Stan potworów lasu; punkty E trenera i Kamienia Powrotu; StanGracza (SerwerStanuGotowy, TreningPodlaczony);
	TeleportChmury (Trwa); ScreenGui HUD, TestWalki2Cutscenka, ClassSelect.
	Haczyk testowy: Sygnaly/SterowanieKlienta ("stan" | "wylacz" | "wlacz" | "zeruj" | "ustaw", pole, wartość).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneWskazowek"))
local L = require(moduly:WaitForChild("LogikaWskazowek"))
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieKlienta")
local ekrany = gracz:WaitForChild("PlayerGui")

local U = D.ui
local Z = D.zrodla
local CZCIONKA = Enum.Font[U.czcionka]

local function kolor(h)
	return Color3.fromHex(h)
end

-- ścieżka "A/B/C" od Workspace (albo od podanego korzenia)
local function sciezka(tekst, korzen)
	local o = korzen or workspace
	for _, n in string.split(tekst, "/") do
		if o == nil then
			return nil
		end
		o = o:FindFirstChild(n)
	end
	return o
end

local function pozycja(o)
	if o == nil then
		return nil
	end
	if o:IsA("BasePart") then
		return o.Position
	elseif o:IsA("Model") then
		return o:GetPivot().Position
	elseif o:IsA("Attachment") then
		return o.WorldPosition
	end
	return nil
end

------------------------------------------------------------------ stan sesji (tylko w pamięci klienta)
local function nowyLicznik()
	return { wygrane = 0, przegrane = 0, ostatni = nil, trenowal = false }
end
local sesja = {
	ogolem = nowyLicznik(), -- wszystkie walki (dla miasta)
	krainy = {}, -- id biomu → licznik walk w tym biomie (las, bagno)
	wylaczone = false,
}
local wymuszone = {} -- haczyk "ustaw": pole → wartość (tylko testy)

local function licznik(kraina)
	if not sesja.krainy[kraina] then
		sesja.krainy[kraina] = nowyLicznik()
	end
	return sesja.krainy[kraina]
end

local function zapiszWynik(l, w)
	if w == "wygrana" then
		l.wygrane += 1
		l.ostatni = w
	elseif w == "przegrana" then
		l.przegrane += 1
		l.ostatni = w
		l.trenowal = false
	end
end

-- wyniki walk: odtwarzacz ustawia u klienta na kontenerze biomu OstatnieZiarno na starcie walki, a przy pokazaniu
-- wyniku OstatniWynik i OstatniStan = "wynik". Liczymy jedną walkę na wejście w stan „wynik” z nowym ziarnem (walka
-- przerwana resetem nie ma wyniku i się nie liczy; dwie z rzędu z tym samym potworem — tak).
local ostatnieZiarna = {}
local function podepnijKontener(k, kraina)
	local function sprawdz()
		if k:GetAttribute(Z.atrybut_stanu_walki) ~= Z.stan_wyniku then
			return
		end
		local z = tostring(k:GetAttribute(Z.atrybut_ziarna))
		if ostatnieZiarna[k] == z then
			return
		end
		ostatnieZiarna[k] = z
		local w = L.wynikWalki(k:GetAttribute(Z.atrybut_wyniku))
		zapiszWynik(sesja.ogolem, w)
		zapiszWynik(licznik(kraina), w)
	end
	ostatnieZiarna[k] = tostring(k:GetAttribute(Z.atrybut_ziarna)) -- walk sprzed startu skryptu nie liczymy
	k:GetAttributeChangedSignal(Z.atrybut_stanu_walki):Connect(function()
		task.defer(sprawdz)
	end)
end
local podpiete = {}
local function podepnijLasy()
	for nazwa, kraina in Z.walki do
		local k = workspace:FindFirstChild(nazwa)
		if k and not podpiete[k] then
			podpiete[k] = true
			podepnijKontener(k, kraina)
		end
	end
end

-- trening: wejście na stanowisko (atrybut gracza z danych: od 26.11.2026 TreningAFK — stanowiska AFK; wcześniej TreningGra
-- mini-gier) po przegranej = „potrenował” (w każdym biomie)
gracz:GetAttributeChangedSignal(Z.atrybut_treningu):Connect(function()
	if gracz:GetAttribute(Z.atrybut_treningu) == nil then
		return
	end
	for _, l in sesja.krainy do
		if l.ostatni == "przegrana" then
			l.trenowal = true
		end
	end
	if sesja.ogolem.ostatni == "przegrana" then
		sesja.ogolem.trenowal = true
	end
end)

------------------------------------------------------------------ dane biomów (moduły innych pakietów, tylko odczyt)
local daneBiomow = {} -- id → tabela DanePasa
local function daneBiomu(b)
	if daneBiomow[b.id] then
		return daneBiomow[b.id]
	end
	local m = sciezka(b.dane)
	if m and m:IsA("ModuleScript") then
		local ok, w = pcall(require, m)
		if ok and type(w) == "table" and w.wejscie then
			daneBiomow[b.id] = w
		end
	end
	return daneBiomow[b.id]
end

local function biom(id)
	for _, b in Z.biomy do
		if b.id == id then
			return b
		end
	end
	return nil
end

local function v3(t)
	return if type(t) == "table" then Vector3.new(t[1], t[2], t[3]) else nil
end

------------------------------------------------------------------ czy coś innego zajmuje ekran
local function ekranWlaczony(nazwa)
	local g = ekrany:FindFirstChild(nazwa)
	return g ~= nil and g:IsA("ScreenGui") and g.Enabled
end

local function ukryte()
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then
		return true
	end
	if not ekranWlaczony(Z.hud) or ekranWlaczony(Z.ekran_walki) or ekranWlaczony(Z.ekran_klasy) then
		return true
	end
	local kamera = workspace.CurrentCamera
	if not kamera or kamera.CameraType ~= Enum.CameraType.Custom then
		return true -- przelot, walka, stanowisko mini-gry, scenki
	end
	if gracz:GetAttribute(Z.atrybut_treningu) ~= nil then
		return true
	end
	local chmury = workspace:FindFirstChild(Z.chmury)
	if chmury and chmury:GetAttribute(Z.chmury_trwa) == true then
		return true
	end
	return false
end

------------------------------------------------------------------ ekran: linijka celu i strzałka przy TELEPORT
local gui = Instance.new("ScreenGui")
gui.Name = "WskazowkiGry"
gui.ResetOnSpawn = false
gui.DisplayOrder = U.kolejnosc_wyswietlania
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
gui.Parent = ekrany

local pasek = Instance.new("Frame")
pasek.Name = "Cel"
pasek.AnchorPoint = Vector2.new(0.5, 0)
pasek.Position = UDim2.new(0.5, 0, 0, U.y_px)
pasek.Size = UDim2.fromOffset(0, U.wys_px)
pasek.AutomaticSize = Enum.AutomaticSize.X
pasek.BackgroundColor3 = kolor(U.tlo)
pasek.BackgroundTransparency = U.tlo_przezroczystosc
pasek.Visible = false
pasek.Parent = gui
local rog = Instance.new("UICorner")
rog.CornerRadius = UDim.new(0.5, 0)
rog.Parent = pasek
local obrys = Instance.new("UIStroke")
obrys.Color = kolor(U.akcent)
obrys.Thickness = 2
obrys.Parent = pasek
local uklad = Instance.new("UIListLayout")
uklad.FillDirection = Enum.FillDirection.Horizontal
uklad.VerticalAlignment = Enum.VerticalAlignment.Center
uklad.Padding = UDim.new(0, math.floor(U.margines_px / 2))
uklad.Parent = pasek
local wciecie = Instance.new("UIPadding")
wciecie.PaddingLeft = UDim.new(0, U.margines_px)
wciecie.Parent = pasek

local napis = Instance.new("TextLabel")
napis.Name = "Tekst"
napis.BackgroundTransparency = 1
napis.Size = UDim2.fromOffset(0, U.wys_px)
napis.AutomaticSize = Enum.AutomaticSize.X
napis.Font = CZCIONKA
napis.TextSize = U.tekst_px
napis.TextColor3 = kolor(U.tekst)
napis.Text = ""
napis.LayoutOrder = 1
napis.Parent = pasek
local ograniczenie = Instance.new("UISizeConstraint")
ograniczenie.MaxSize = Vector2.new(U.maks_szer_px, U.wys_px)
ograniczenie.Parent = napis
napis.TextTruncate = Enum.TextTruncate.AtEnd

local zamknij = Instance.new("TextButton")
zamknij.Name = "Zamknij"
zamknij.BackgroundTransparency = 1
zamknij.Size = UDim2.fromOffset(U.zamknij_px, U.zamknij_px)
zamknij.Font = CZCIONKA
zamknij.TextSize = U.zamknij_tekst_px
zamknij.TextColor3 = kolor(U.akcent)
zamknij.Text = U.zamknij_tekst
zamknij.LayoutOrder = 2
zamknij.Parent = pasek

local strzalka = Instance.new("TextLabel")
strzalka.Name = "Strzalka"
strzalka.BackgroundTransparency = 1
strzalka.AnchorPoint = Vector2.new(0, 0.5)
strzalka.Size = UDim2.fromOffset(U.strzalka_px, U.strzalka_px)
-- „◀” w GothamBold rysuje się zastępczą, malutką czcionką (wspólna próba 17.11.2026) — zwykły znak w grubej czcionce
strzalka.Font = Enum.Font[U.czcionka_znakow]
strzalka.TextSize = U.strzalka_px
strzalka.TextColor3 = kolor(U.akcent)
strzalka.TextStrokeTransparency = 0.2
strzalka.Text = U.strzalka
strzalka.Visible = false
strzalka.Parent = gui

------------------------------------------------------------------ znacznik w świecie (lokalna kotwica, tylko u gracza)
local kotwica = Instance.new("Part")
kotwica.Name = "KotwicaWskazowki"
kotwica.Anchored = true
kotwica.CanCollide = false
kotwica.CanQuery = false
kotwica.CanTouch = false
kotwica.Transparency = 1
kotwica.Size = Vector3.new(0.2, 0.2, 0.2)
kotwica.Parent = kontener

local znacznik = Instance.new("BillboardGui")
znacznik.Name = "WskazowkiGryZnacznik"
znacznik.Adornee = kotwica
znacznik.AlwaysOnTop = true
znacznik.LightInfluence = 0
znacznik.ResetOnSpawn = false
znacznik.MaxDistance = U.znacznik_zasieg
znacznik.Size = UDim2.fromOffset(U.znacznik_px, U.znacznik_px)
znacznik.Enabled = false
znacznik.Parent = ekrany
-- znacznik: obrócony kwadrat (romb) zamiast znaku „▼”, którego czcionka gry nie ma
local grot = Instance.new("Frame")
grot.Name = "Grot"
grot.AnchorPoint = Vector2.new(0.5, 0.5)
grot.Position = UDim2.fromScale(0.5, 0.5)
grot.Size = UDim2.fromScale(0.6, 0.6)
grot.Rotation = 45
grot.BackgroundColor3 = kolor(U.akcent)
grot.Parent = znacznik
local obrysGrotu = Instance.new("UIStroke")
obrysGrotu.Color = kolor(U.znacznik_obrys)
obrysGrotu.Thickness = 3
obrysGrotu.Parent = grot

------------------------------------------------------------------ cele
-- D-096: w zasięgu najpierw potwór o poziomie najbliższym poziomowi gracza (w scalonych zagrodach chodzą różne
-- poziomy — nowy gracz ma iść do najsłabszego), dopiero przy równym poziomie najbliższy w studach
local function najblizszyPotwor(od)
	local lv = tonumber(gracz:GetAttribute("Level"))
	local najlepszy, odl, roznica = nil, math.huge, math.huge
	for nazwa in Z.walki do
		local k = workspace:FindFirstChild(nazwa)
		local stanP = k and k:FindFirstChild(Z.stan_potworow)
		if stanP then
			for _, c in stanP:GetChildren() do
				local p = c:GetAttribute("Pozycja")
				if typeof(p) == "Vector3" and c:GetAttribute("Straznik") ~= true then
					local d = (p - od).Magnitude
					local poz = tonumber(c:GetAttribute("Poziom"))
					local r = if lv and poz then math.abs(poz - lv) else 0
					if d < D.czasy.potwor_promien and (r < roznica or (r == roznica and d < odl)) then
						najlepszy, odl, roznica = p, d, r
					end
				end
			end
		end
	end
	return najlepszy
end

local function punktStraznika(b)
	local k = workspace:FindFirstChild(b.kontener)
	local stanP = k and k:FindFirstChild(Z.stan_potworow)
	if stanP then
		for _, c in stanP:GetChildren() do
			local p = c:GetAttribute("Pozycja")
			if c:GetAttribute("Straznik") == true and typeof(p) == "Vector3" then
				return p
			end
		end
	end
	local dl = daneBiomu(b)
	return dl and dl.straznik and v3(dl.straznik.poz)
end

local function najblizszyTrener(od)
	local najlepszy, odl = nil, math.huge
	for _, s in Z.trenerzy do
		local p = pozycja(sciezka(s))
		if p and (p - od).Magnitude < odl then
			najlepszy, odl = p, (p - od).Magnitude
		end
	end
	return najlepszy
end

-- kraina: biom, w którym stoi gracz (w mieście: las — tam prowadzą kroki z miasta)
local function punktCelu(cel, od, kraina)
	local b = biom(kraina or "las")
	if cel == "potwor" then
		return najblizszyPotwor(od)
	elseif cel == "trener" then
		return najblizszyTrener(od)
	elseif cel == "jajko" then
		-- jajko biomu ze scenką (punkt E, a gdy streaming go jeszcze nie dał — model jajka); w mieście: leśne
		for _, s in (if b and b.jajko then b.jajko else {}) do
			local p = pozycja(sciezka(s))
			if p then
				return p
			end
		end
		return nil
	elseif cel == "kowal" then
		return pozycja(sciezka(Z.kowal_e)) -- punkt E kowala w bazarze (swiat/kowal_proba)
	elseif not b then
		return nil
	elseif cel == "straznik" then
		return punktStraznika(b)
	elseif cel == "kamien" then
		local p = pozycja(sciezka(b.kamien))
		if p then
			return p
		end
		local dl = daneBiomu(b)
		return dl and dl.powrot and v3(dl.powrot.punkt)
	elseif cel == "brama" then
		local dl = daneBiomu(b)
		return dl and dl.zaBrama and v3(dl.zaBrama.punkt)
	end
	return nil
end

------------------------------------------------------------------ stan → krok
local function stanGracza()
	local s = {
		klasa = gracz:GetAttribute(Z.atrybut_klasy) ~= nil,
		ukryte = ukryte(),
		wylaczone = sesja.wylaczone,
		poziom = gracz:GetAttribute(Z.atrybut_poziomu),
		miejsce = "miasto",
	}
	for _, b in Z.biomy do
		s[b.pole_straznika] = gracz:GetAttribute(b.atrybut_straznika) == true
		if b.id == "bagno" then
			s.bagno = workspace:FindFirstChild(b.kontener) ~= nil
		elseif b.id == "dzungla" then
			s.dzungla = workspace:FindFirstChild(b.kontener) ~= nil
		end
	end
	local sg = workspace:FindFirstChild(Z.stan_gracza)
	s.stan_gracza = sg ~= nil and sg:GetAttribute(Z.stan_gracza_gotowy) == true
	s.trening_wzmacnia = s.stan_gracza and sg:GetAttribute(Z.stan_gracza_trening) == true
	local korzen = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
	if korzen then
		-- od ostatniego biomu: początek Bagna leży w prostokącie lasu (za jego bramą) — Bagno ma pierwszeństwo
		for i = #Z.biomy, 1, -1 do
			local b = Z.biomy[i]
			local dl = workspace:FindFirstChild(b.kontener) and daneBiomu(b)
			if dl then
				local m = L.miejsce(korzen.Position.X, korzen.Position.Z, dl.wejscie, dl.brama and dl.brama.x)
				if m ~= "miasto" then
					s.kraina, s.miejsce = b.id, m
					break
				end
			end
		end
	end
	local l = if s.kraina then licznik(s.kraina) else sesja.ogolem
	s.wygrane, s.przegrane, s.ostatni, s.trenowal = l.wygrane, l.przegrane, l.ostatni, l.trenowal
	-- jajko biomu, w którym stoi gracz (w mieście: lasu; swiat/pety_proba): cena następnego jajka i liczba kupionych
	-- jajek tego biomu to atrybuty gracza (pisze je serwer pakietu petów)
	local bj = biom(s.kraina or "las")
	local cena = bj and bj.atrybut_ceny_jajka and gracz:GetAttribute(bj.atrybut_ceny_jajka)
	local zloto = gracz:GetAttribute(Z.atrybut_zlota)
	s.jajko = workspace:FindFirstChild(Z.pety) ~= nil and type(cena) == "number" and type(zloto) == "number" and zloto >= cena
	local kupione = bj and bj.atrybut_kupionych_jajek and gracz:GetAttribute(bj.atrybut_kupionych_jajek)
	s.kupione = if type(kupione) == "number" then kupione else 0
	-- kowal na próbę (swiat/kowal_proba, 18.11.2026): atrybuty gracza pisze jego serwer; bez kontenera — nic
	s.kowal = workspace:FindFirstChild(Z.kowal) ~= nil and type(gracz:GetAttribute(Z.atrybut_kowal_dostepne)) == "string"
	local zapasy = gracz:GetAttribute(Z.atrybut_kowal_zapasy)
	local ulepszen = gracz:GetAttribute(Z.atrybut_kowal_ulepszen)
	s.kowal_zapas = s.kowal and type(zapasy) == "number" and zapasy > 0
	s.kowal_ulepsz = s.kowal and gracz:GetAttribute(Z.atrybut_kowal_ulepsz) == true
	s.kowal_ulepszen = if type(ulepszen) == "number" then ulepszen else 0
	for pole, w in wymuszone do
		s[pole] = w
	end
	return s, korzen
end

------------------------------------------------------------------ pokazywanie
local biezacy = nil -- { id, tekst, cel }
local strzalkaWidoczna, znacznikWidoczny = false, false
local strzalkaX, strzalkaY = 0, 0 -- piksele: prawy brzeg przycisku TELEPORT i jego środek

local function puls()
	local skala = pasek:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
	skala.Parent = pasek
	skala.Scale = 1.12
	TweenService:Create(skala, TweenInfo.new(U.puls_s, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

local function odswiez()
	podepnijLasy()
	local s, korzen = stanGracza()
	local k = L.krok(D, s)
	if not k then
		biezacy = nil
		pasek.Visible = false
		strzalka.Visible = false
		znacznik.Enabled = false
		strzalkaWidoczna, znacznikWidoczny = false, false
		return
	end
	if not biezacy or biezacy.id ~= k.id or biezacy.tekst ~= k.tekst then
		napis.Text = k.tekst
		if biezacy then
			puls()
		end
	end
	biezacy = k
	pasek.Visible = true
	-- strzałka przy przycisku TELEPORT (tylko odczyt położenia przycisku z HUD)
	strzalkaWidoczna = false
	if k.cel == "teleport" then
		local hud = ekrany:FindFirstChild(Z.hud)
		local przycisk = hud and sciezka(string.sub(Z.przycisk_teleportu, #Z.hud + 2), hud)
		if hud and hud:IsA("ScreenGui") and przycisk and przycisk:IsA("GuiObject") and przycisk.Visible then
			-- nasz ekran zaczyna się pod paskiem Robloxa; HUD może go ignorować — wtedy przesuwamy o wcięcie
			local a, r = przycisk.AbsolutePosition, przycisk.AbsoluteSize
			local wciecieGory = if hud.IgnoreGuiInset then GuiService:GetGuiInset() else Vector2.zero
			strzalkaX = a.X + r.X + U.strzalka_odstep_px - wciecieGory.X
			strzalkaY = a.Y + r.Y / 2 - wciecieGory.Y
			strzalkaWidoczna = true
		end
	end
	strzalka.Visible = strzalkaWidoczna
	-- znacznik nad celem w świecie
	znacznikWidoczny = false
	if k.cel and k.cel ~= "teleport" and korzen then
		local p = punktCelu(k.cel, korzen.Position, s.kraina)
		if p then
			kotwica.Position = p + Vector3.new(0, U.znacznik_nad, 0)
			znacznikWidoczny = true
		end
	end
	znacznik.Enabled = znacznikWidoczny
end

zamknij.Activated:Connect(function()
	sesja.wylaczone = true
	odswiez()
end)

-- ruch strzałki i znacznika (co klatkę, bez nowych obiektów)
RunService.RenderStepped:Connect(function()
	local t = os.clock()
	if strzalkaWidoczna then
		strzalka.Position = UDim2.fromOffset(strzalkaX + math.abs(math.sin(t * 4)) * U.strzalka_ruch_px, strzalkaY)
	end
	if znacznikWidoczny then
		znacznik.StudsOffsetWorldSpace = Vector3.new(0, math.abs(math.sin(t * 3)) * U.znacznik_ruch, 0)
	end
end)

task.spawn(function()
	while kontener.Parent do
		local ok, blad = pcall(odswiez)
		if not ok then
			warn(D.prefiks .. "odświeżenie nie wyszło: " .. tostring(blad))
			task.wait(2)
		end
		task.wait(D.czasy.odswiez_s)
	end
	gui:Destroy()
	znacznik:Destroy()
end)

------------------------------------------------------------------ haczyk testowy
sterowanie.OnInvoke = function(polecenie, a, b)
	if polecenie == "stan" then
		local s = stanGracza()
		return {
			krok = biezacy and biezacy.id, tekst = biezacy and biezacy.tekst, cel = biezacy and biezacy.cel,
			widoczne = pasek.Visible, strzalka = strzalka.Visible, znacznik = znacznik.Enabled,
			znacznikNad = if znacznik.Enabled then kotwica.Position else nil, -- 26.11.2026: punkt znacznika (próby)
			ukryte = s.ukryte, kraina = s.kraina, miejsce = s.miejsce, wygrane = s.wygrane, przegrane = s.przegrane,
			ostatni = s.ostatni, trenowal = s.trenowal, wylaczone = sesja.wylaczone, bagno = s.bagno,
			straznik = s.straznik, straznik_bagna = s.straznik_bagna, straznik_dzungli = s.straznik_dzungli,
			dzungla = s.dzungla,
			stan_gracza = s.stan_gracza, trening_wzmacnia = s.trening_wzmacnia, daneLasu = daneBiomow.las ~= nil,
			jajko = s.jajko, kupione = s.kupione, kowal = s.kowal, kowal_zapas = s.kowal_zapas,
			kowal_ulepsz = s.kowal_ulepsz, kowal_ulepszen = s.kowal_ulepszen,
		}
	elseif polecenie == "wylacz" then
		sesja.wylaczone = true
	elseif polecenie == "wlacz" then
		sesja.wylaczone = false
	elseif polecenie == "zeruj" then
		sesja.ogolem = nowyLicznik()
		table.clear(sesja.krainy)
		table.clear(wymuszone)
	elseif polecenie == "ustaw" and type(a) == "string" then
		wymuszone[a] = b
	else
		return false
	end
	odswiez()
	return true
end

kontener:SetAttribute("KlientWskazowekGotowy", true)
