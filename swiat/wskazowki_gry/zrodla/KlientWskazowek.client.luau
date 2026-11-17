--[[
	KlientWskazowek — wskazówki celu dla nowego gracza (Script, RunContext = Client, w kontenerze Workspace/WskazowkiGry).
	Status: propozycja (raport przejścia gry 17.11.2026, M3: „brak celu w pierwszej minucie”).

	Co robi (tylko u tego gracza, niczego nie wysyła do serwera i nie zmienia cudzych instancji):
		1. Linijka celu u góry ekranu (własny ScreenGui „WskazowkiGry”) z krzyżykiem — jedno kliknięcie chowa wskazówki
		   do końca sesji (haczyk testowy "wlacz" je przywraca).
		2. Strzałka obok przycisku TELEPORT w HUD Pawła (tylko czyta jego położenie — HUD-u nie zmienia) albo znacznik
		   w świecie nad celem: najbliższy potwór, Strażnik Gaju, Kamień Powrotu, trener, brama za Strażnikiem.
		3. Krok wynika ze stanu gracza (LogikaWskazowek.krok): klasa, wynik ostatniej walki w lesie, pokonany Strażnik,
		   położenie (prostokąt lasu z danych lasu-pasa), stan gracza (swiat/stan_gracza: poziomy i trening), a nie ze
		   sztywnego scenariusza. Bez StanGracza kroki o poziomach i treningu się nie pokazują.
		4. Schowane, gdy trwa walka, przelot, chmury, mini-gra, wybór klasy albo gdy HUD jest schowany — nie zasłania
		   HUD-u ani ekranu walki.
	Źródła (tylko odczyt): atrybuty gracza Class, Level, PokonalStraznikaLasu, TreningGra; atrybuty klienta kontenerów
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
local sesja = {
	wygrane = 0,
	przegrane = 0,
	ostatni = nil, -- "wygrana" | "przegrana"
	trenowal = false, -- po ostatniej przegranej był na stanowisku Training Center
	wylaczone = false,
}
local wymuszone = {} -- haczyk "ustaw": pole → wartość (tylko testy)

-- wyniki walk w lesie: odtwarzacz ustawia u klienta na kontenerze lasu OstatnieZiarno na starcie walki, a przy
-- pokazaniu wyniku OstatniWynik i OstatniStan = "wynik". Liczymy jedną walkę na wejście w stan „wynik” z nowym
-- ziarnem (walka przerwana resetem nie ma wyniku i się nie liczy; dwie z rzędu z tym samym potworem — tak).
local ostatnieZiarna = {}
local function podepnijLas(las)
	local function sprawdz()
		if las:GetAttribute(Z.atrybut_stanu_walki) ~= Z.stan_wyniku then
			return
		end
		local z = tostring(las:GetAttribute(Z.atrybut_ziarna))
		if ostatnieZiarna[las] == z then
			return
		end
		ostatnieZiarna[las] = z
		local w = L.wynikWalki(las:GetAttribute(Z.atrybut_wyniku))
		if w == "wygrana" then
			sesja.wygrane += 1
			sesja.ostatni = w
		elseif w == "przegrana" then
			sesja.przegrane += 1
			sesja.ostatni = w
			sesja.trenowal = false
		end
	end
	ostatnieZiarna[las] = tostring(las:GetAttribute(Z.atrybut_ziarna)) -- walk sprzed startu skryptu nie liczymy
	las:GetAttributeChangedSignal(Z.atrybut_stanu_walki):Connect(function()
		task.defer(sprawdz)
	end)
end
local podpiete = {}
local function podepnijLasy()
	for _, n in Z.lasy_walk do
		local las = workspace:FindFirstChild(n)
		if las and not podpiete[las] then
			podpiete[las] = true
			podepnijLas(las)
		end
	end
end

-- trening: wejście na stanowisko (atrybut gracza TreningGra) po przegranej = „potrenował”
gracz:GetAttributeChangedSignal(Z.atrybut_treningu):Connect(function()
	if gracz:GetAttribute(Z.atrybut_treningu) ~= nil and sesja.ostatni == "przegrana" then
		sesja.trenowal = true
	end
end)

------------------------------------------------------------------ dane lasu-pasa (moduł innego pakietu, tylko odczyt)
local daneLasu = nil
local function wczytajDaneLasu()
	if daneLasu then
		return daneLasu
	end
	local m = sciezka(Z.dane_lasu)
	if m and m:IsA("ModuleScript") then
		local ok, w = pcall(require, m)
		if ok and type(w) == "table" and w.wejscie then
			daneLasu = w
		end
	end
	return daneLasu
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
strzalka.Font = CZCIONKA
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
local grot = Instance.new("TextLabel")
grot.Name = "Grot"
grot.BackgroundTransparency = 1
grot.Size = UDim2.fromScale(1, 1)
grot.Font = CZCIONKA
grot.TextSize = U.znacznik_px
grot.TextColor3 = kolor(U.akcent)
grot.TextStrokeTransparency = 0
grot.Text = U.znacznik
grot.Parent = znacznik

------------------------------------------------------------------ cele
local function najblizszyPotwor(od)
	local najlepszy, odl = nil, D.czasy.potwor_promien
	for _, n in Z.lasy_walk do
		local las = workspace:FindFirstChild(n)
		local stanP = las and las:FindFirstChild(Z.stan_potworow)
		if stanP then
			for _, c in stanP:GetChildren() do
				local p = c:GetAttribute("Pozycja")
				if typeof(p) == "Vector3" and c:GetAttribute("Straznik") ~= true then
					local d = (p - od).Magnitude
					if d < odl then
						najlepszy, odl = p, d
					end
				end
			end
		end
	end
	return najlepszy
end

local function punktStraznika()
	local las = workspace:FindFirstChild(Z.las)
	local stanP = las and las:FindFirstChild(Z.stan_potworow)
	if stanP then
		for _, c in stanP:GetChildren() do
			local p = c:GetAttribute("Pozycja")
			if c:GetAttribute("Straznik") == true and typeof(p) == "Vector3" then
				return p
			end
		end
	end
	local dl = wczytajDaneLasu()
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

local function punktCelu(cel, od)
	if cel == "potwor" then
		return najblizszyPotwor(od)
	elseif cel == "straznik" then
		return punktStraznika()
	elseif cel == "kamien" then
		local p = pozycja(sciezka(Z.kamien))
		if p then
			return p
		end
		local dl = wczytajDaneLasu()
		return dl and dl.powrot and v3(dl.powrot.punkt)
	elseif cel == "trener" then
		return najblizszyTrener(od)
	elseif cel == "brama" then
		local dl = wczytajDaneLasu()
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
		wygrane = sesja.wygrane,
		przegrane = sesja.przegrane,
		ostatni = sesja.ostatni,
		trenowal = sesja.trenowal,
		straznik = gracz:GetAttribute(Z.atrybut_straznika) == true,
		poziom = gracz:GetAttribute(Z.atrybut_poziomu),
		bagno = workspace:FindFirstChild(Z.bagno) ~= nil,
		miejsce = "miasto",
	}
	local sg = workspace:FindFirstChild(Z.stan_gracza)
	s.stan_gracza = sg ~= nil and sg:GetAttribute(Z.stan_gracza_gotowy) == true
	s.trening_wzmacnia = s.stan_gracza and sg:GetAttribute(Z.stan_gracza_trening) == true
	local korzen = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
	local dl = wczytajDaneLasu()
	if korzen and dl then
		s.miejsce = L.miejsce(korzen.Position.X, korzen.Position.Z, dl.wejscie, dl.brama and dl.brama.x)
	end
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
		local p = punktCelu(k.cel, korzen.Position)
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
			ukryte = s.ukryte, miejsce = s.miejsce, wygrane = sesja.wygrane, przegrane = sesja.przegrane,
			ostatni = sesja.ostatni, trenowal = sesja.trenowal, wylaczone = sesja.wylaczone,
			stan_gracza = s.stan_gracza, trening_wzmacnia = s.trening_wzmacnia, daneLasu = daneLasu ~= nil,
		}
	elseif polecenie == "wylacz" then
		sesja.wylaczone = true
	elseif polecenie == "wlacz" then
		sesja.wylaczone = false
	elseif polecenie == "zeruj" then
		sesja.wygrane, sesja.przegrane, sesja.ostatni, sesja.trenowal = 0, 0, nil, false
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
