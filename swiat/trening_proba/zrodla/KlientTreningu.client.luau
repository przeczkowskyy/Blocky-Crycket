--[[
	KlientTreningu — kliencka połowa próby Training Center (Script, RunContext = Client, w kontenerze
	Workspace/TreningProba). Własny ScreenGui „TreningProba” tworzony tym skryptem (HUD-u i plików src/ nie rusza).

	Co robi:
		1. TYMCZASOWY wybór mini-gry (sześć kafelków: Siła i Pancerz grywalne, cztery „w projekcie”) — wyraźnie
		   opisany jako tymczasowy; docelowe okno 2D robi Paweł (D-093). Otwiera go: E przy trenerze w bazarze
		   (zdarzenie ReplicatedStorage.OknoMiejsca z id "training_center"), E przy własnej tablicy wejścia i przy
		   tablicy w arenie (serwer → "wybor"), przycisk INNA GRA.
		   Gdy okno Pawła będzie gotowe: atrybut kontenera WyborTymczasowy = false (ten wybór się nie otwiera),
		   a okno Pawła wywołuje u klienta:  workspace.TreningProba.Sygnaly.WybierzGre:Invoke("sila")
		2. Stanowisko: kamera stała (Scriptable), klawisze ruchu pochłonięte (ContextActionService, wysoki priorytet),
		   dotykowe sterowanie Robloxa wyłączone na czas stanowiska; po wyjściu wszystko wraca.
		3. Runda: naciśnięcie → natychmiastowy efekt z lokalnej kopii logiki (LogikaTreningu) i zgłoszenie do serwera;
		   licznik serii i przyrost poprawia werdykt serwera ("wynik"). Efekty: licznik serii z „podskokiem”, krótki
		   napis, błysk ekranu, odłamki, wstrząs kamery, dźwięki z plików wbudowanych w klienta (rbxasset://sounds/).
		4. Siła — „Rozbijanie”: miotacz rzuca skrzynki w cztery strefy wokół gracza; strzałka / WASD / przycisk w
		   stronę skrzynki, gdy dolatuje do kółka. Pancerz — „Blok”: golem bierze zamach, pierścień zbiega się do kółka;
		   BLOK w chwili uderzenia; fioletowy pierścień to zmyłka — nie blokować.
	Haczyk testowy: Sygnaly/SterowanieKlienta ("stan" | "wybor" | "okno" | "graj", gra | "start" | "nacisnij", w |
	"autograj", celnosc, blokujZmylki | "spam", n, w | "surowe", w, dt | "wyjdz" | "inna" | "zamknij" | "przerwij").
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneTreningu"))
local L = require(moduly:WaitForChild("LogikaTreningu"))
local zdalne: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaTreningu")
local sygnaly = kontener:WaitForChild("Sygnaly")
local sterowanie: BindableFunction = sygnaly:WaitForChild("SterowanieKlienta")
local wybierzF: BindableFunction = sygnaly:WaitForChild("WybierzGre")
local ekrany = gracz:WaitForChild("PlayerGui")

local U = D.ui
local T = D.teksty
local KOL = U.kolory
local PX = U.tekst_px

local function kolor(h)
	return Color3.fromHex(h)
end

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

local function teraz()
	return workspace:GetServerTimeNow()
end

local function sciezka(korzen, tekst)
	local o = korzen
	for i, n in string.split(tekst, "/") do
		if o == nil then
			return nil
		end
		if not (i == 1 and n == "Workspace") then
			o = o:FindFirstChild(n)
		end
	end
	return o
end

local losowe = Random.new()

------------------------------------------------------------------ stan
local stan = {
	ekran = "brak", -- brak | stanowisko | runda | podsumowanie
	wybor = false, -- tymczasowy wybór na ekranie
	zrodlo = nil,
	gra = nil, -- id gry na stanowisku
	runda = nil, -- dane rundy z serwera { id, gra, t0, dlugosc, plan }
	R = nil, -- lokalna kopia rundy (natychmiastowe efekty)
	lokalne = {}, -- nr → true / false (werdykt pokazany)
	wyniki = {}, -- ostatnie werdykty serwera (haczyk)
	rozbieznosci = 0, -- werdykt serwera ≠ lokalny
	odliczanie = nil,
	wstrzas = nil,
	miecz = nil, -- { t, k }
	tarcza = nil, -- { t }
	ostatnieOdliczanie = nil,
	podsumowanie = nil,
}

------------------------------------------------------------------ ekran: pomocnicze (rozmiary tylko z D.ui)
local gui = Instance.new("ScreenGui")
gui.Name = "TreningProba"
gui.ResetOnSpawn = false
gui.DisplayOrder = U.kolejnosc_wyswietlania
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
gui.Enabled = false
gui.Parent = ekrany

local skale = {}
local przyciski = {} -- { obiekt, szer, wys } (bazowo)
local napisy = {} -- { obiekt, rozmiar } (bazowo)

local function zaokraglij(o, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, r)
	c.Parent = o
end

local function obrysuj(o, grubosc, h)
	local s = Instance.new("UIStroke")
	s.Thickness = grubosc
	s.Color = kolor(h or KOL.tusz)
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = o
	return s
end

local function panel(nazwa, szer, wys, pozycja, kotwica, tlo)
	local f = Instance.new("Frame")
	f.Name = nazwa
	f.Size = UDim2.fromOffset(szer, wys)
	f.Position = pozycja
	f.AnchorPoint = kotwica
	if tlo == "" then
		f.BackgroundTransparency = 1
	else
		f.BackgroundColor3 = kolor(tlo or KOL.krem)
	end
	f.BorderSizePixel = 0
	f.Visible = false
	local s = Instance.new("UIScale")
	s.Parent = f
	table.insert(skale, s)
	f.Parent = gui
	return f
end

local function napis(rodzic, nazwa, tekst, rozmiar, x, y, szer, wys, h, wyrownaj)
	local l = Instance.new("TextLabel")
	l.Name = nazwa
	l.BackgroundTransparency = 1
	l.Position = UDim2.fromOffset(x, y)
	l.Size = UDim2.fromOffset(szer, wys)
	l.Font = Enum.Font.FredokaOne
	l.TextSize = PX[rozmiar]
	l.TextColor3 = kolor(h or KOL.tusz)
	l.TextXAlignment = wyrownaj or Enum.TextXAlignment.Center
	l.TextWrapped = true
	l.Text = tekst
	l.Parent = rodzic
	table.insert(napisy, { obiekt = l, rozmiar = PX[rozmiar] })
	return l
end

local function przycisk(rodzic, nazwa, tekst, x, y, szer, wys, tlo, akcja, rozmiar)
	local b = Instance.new("TextButton")
	b.Name = nazwa
	b.Position = UDim2.fromOffset(x, y)
	b.Size = UDim2.fromOffset(szer, wys)
	b.BackgroundColor3 = kolor(tlo)
	b.AutoButtonColor = true
	b.Font = Enum.Font.FredokaOne
	b.TextSize = PX[rozmiar or "sredni"]
	b.TextColor3 = kolor(KOL.krem)
	b.Text = tekst
	b.Parent = rodzic
	zaokraglij(b, 10)
	obrysuj(b, 2)
	table.insert(przyciski, { obiekt = b, szer = szer, wys = wys })
	table.insert(napisy, { obiekt = b, rozmiar = PX[rozmiar or "sredni"] })
	if akcja then
		b.Activated:Connect(akcja)
	end
	return b
end

local KATY = { gora = 0, prawo = 90, dol = 180, lewo = 270 }

-- strzałka z dwóch kresek (bez obrazków): ^ obrócone o kąt kierunku
local function strzalka(rodzic, kierunek)
	local a = math.rad(KATY[kierunek])
	for i, dx in { -4.5, 4.5 } do
		local k = Instance.new("Frame")
		k.Name = "Kreska" .. i
		k.AnchorPoint = Vector2.new(0.5, 0.5)
		k.Size = UDim2.fromOffset(5, 17)
		k.Position = UDim2.new(0.5, dx * math.cos(a), 0.4, dx * math.sin(a))
		k.Rotation = (if i == 1 then 45 else -45) + KATY[kierunek]
		k.BackgroundColor3 = kolor(KOL.krem)
		k.BorderSizePixel = 0
		zaokraglij(k, 3)
		k.Parent = rodzic
	end
end

------------------------------------------------------------------ ekran: panele
local ui = {}

-- status (prawy górny róg: wolny od HUD-u)
ui.status = panel("Status", 268, 92, UDim2.new(1, -8, 0, 8), Vector2.new(1, 0))
zaokraglij(ui.status, 12)
obrysuj(ui.status, 3)
ui.nazwaGry = napis(ui.status, "Gra", "", "maly", 10, 4, 190, 20, KOL.tusz, Enum.TextXAlignment.Left)
ui.czas = napis(ui.status, "Czas", "", "sredni", 196, 4, 62, 22, KOL.tusz, Enum.TextXAlignment.Right)
ui.seria = napis(ui.status, "Seria", "SERIA 0", "duzy", 10, 24, 160, 36, KOL.tusz, Enum.TextXAlignment.Left)
ui.mnoznik = napis(ui.status, "Mnoznik", "", "sredni", 168, 30, 90, 26, KOL.zloto, Enum.TextXAlignment.Right)
ui.pasek = Instance.new("Frame")
ui.pasek.Name = "Pasek"
ui.pasek.Position = UDim2.fromOffset(10, 60)
ui.pasek.Size = UDim2.fromOffset(248, 7)
ui.pasek.BackgroundColor3 = kolor(KOL.szary)
ui.pasek.BorderSizePixel = 0
zaokraglij(ui.pasek, 3)
ui.pasek.Parent = ui.status
ui.wypelnienie = Instance.new("Frame")
ui.wypelnienie.Name = "Wypelnienie"
ui.wypelnienie.Size = UDim2.fromScale(0, 1)
ui.wypelnienie.BackgroundColor3 = kolor(KOL.zloto)
ui.wypelnienie.BorderSizePixel = 0
zaokraglij(ui.wypelnienie, 3)
ui.wypelnienie.Parent = ui.pasek
ui.suma = napis(ui.status, "Suma", "", "maly", 10, 69, 248, 20, KOL.szary, Enum.TextXAlignment.Left)
local skalaSerii = Instance.new("UIScale")
skalaSerii.Parent = ui.seria

ui.przerwij = panel("Przerwij", U.przycisk_maly_px, U.przycisk_maly_px, UDim2.new(1, -8, 0, 108), Vector2.new(1, 0), "")

-- sterowanie Siły: krzyż czterech przycisków (lewo od prawej kolumny HUD-u)
local b = U.przycisk_px
local g = U.odstep_px
ui.krzyz = panel("SterowanieSila", 3 * b + 2 * g, 3 * b + 2 * g, UDim2.new(1 - U.sterowanie_od_prawej, 0, 1, -8), Vector2.new(1, 1), "")
ui.blok = panel("SterowaniePancerz", U.blok_px, U.blok_px, UDim2.new(1 - U.sterowanie_od_prawej, 0, 1, -8), Vector2.new(1, 1), "")

-- panel startu (dół środka)
ui.start = panel("Start", 400, 132, UDim2.new(0.5, 0, 1, -8), Vector2.new(0.5, 1))
zaokraglij(ui.start, 12)
obrysuj(ui.start, 3)
ui.opis = napis(ui.start, "Opis", "", "maly", 10, 4, 380, 40, KOL.tusz)
ui.podp = napis(ui.start, "Podpowiedz", T.start_podpowiedz, "maly", 10, 46, 380, 20, KOL.szary)

-- podsumowanie rundy (środek)
ui.koniec = panel("Podsumowanie", 400, 244, UDim2.new(0.5, 0, 0.5, 0), Vector2.new(0.5, 0.5))
zaokraglij(ui.koniec, 14)
obrysuj(ui.koniec, 3)
ui.kTytul = napis(ui.koniec, "Tytul", T.koniec, "duzy", 0, 8, 400, 32, KOL.tusz)
ui.k1 = napis(ui.koniec, "Trafienia", "", "sredni", 10, 46, 380, 24, KOL.tusz)
ui.k2 = napis(ui.koniec, "Seria", "", "sredni", 10, 72, 380, 24, KOL.tusz)
ui.k3 = napis(ui.koniec, "Przyrost", "", "duzy", 10, 98, 380, 32, KOL.dobrze)
ui.k4 = napis(ui.koniec, "Sesja", "", "maly", 10, 134, 380, 34, KOL.szary)

-- komunikat (odmowa)
ui.toast = panel("Komunikat", 380, 44, UDim2.new(0.5, 0, 0.3, 0), Vector2.new(0.5, 0.5))
zaokraglij(ui.toast, 10)
obrysuj(ui.toast, 2)
ui.toastTekst = napis(ui.toast, "Tekst", "", "sredni", 8, 4, 364, 36, KOL.tusz)

-- napis środkowy (odliczanie, TRAFIONE!) i błysk
ui.srodek = panel("Napis", 460, 80, UDim2.new(0.42, 0, 0.34, 0), Vector2.new(0.5, 0.5), "")
ui.srodekTekst = napis(ui.srodek, "Tekst", "", "wielki", 0, 0, 460, 80, KOL.krem)
local obrysSrodka = Instance.new("UIStroke")
obrysSrodka.Thickness = 3
obrysSrodka.Color = kolor(KOL.tusz)
obrysSrodka.Parent = ui.srodekTekst
local skalaSrodka = ui.srodek:FindFirstChildOfClass("UIScale")

ui.blysk = Instance.new("Frame")
ui.blysk.Name = "Blysk"
ui.blysk.Size = UDim2.fromScale(1, 1)
ui.blysk.BackgroundColor3 = Color3.new(1, 1, 1)
ui.blysk.BackgroundTransparency = 1
ui.blysk.BorderSizePixel = 0
ui.blysk.Active = false
ui.blysk.Parent = gui

-- pierścienie Pancerza (cel stały + dwa zbiegające się)
ui.pierscienie = panel("Pierscienie", 64, 64, UDim2.new(0.42, 0, 0.64, 0), Vector2.new(0.5, 0.5), "")
local celPierscienia = Instance.new("Frame")
celPierscienia.Name = "Cel"
celPierscienia.Size = UDim2.fromScale(1, 1)
celPierscienia.BackgroundTransparency = 1
zaokraglij(celPierscienia, 32)
obrysuj(celPierscienia, 4, KOL.krem)
celPierscienia.Parent = ui.pierscienie
local pierscienie = {}
for i = 1, 2 do
	local p = Instance.new("Frame")
	p.Name = "Pierscien" .. i
	p.AnchorPoint = Vector2.new(0.5, 0.5)
	p.Position = UDim2.fromScale(0.5, 0.5)
	p.Size = UDim2.fromScale(1, 1)
	p.BackgroundTransparency = 1
	p.Visible = false
	zaokraglij(p, 999)
	local s = obrysuj(p, 5, KOL.cios)
	p.Parent = ui.pierscienie
	pierscienie[i] = { ramka = p, obrys = s }
end

------------------------------------------------------------------ dźwięki (pliki wbudowane w klienta Roblox)
local function graj(nazwa, szybkosc)
	local d = D.dzwieki[nazwa]
	if not d then
		return
	end
	local dzwiek = Instance.new("Sound")
	dzwiek.SoundId = "rbxasset://sounds/" .. d.plik
	dzwiek.Volume = d.glosnosc
	dzwiek.PlaybackSpeed = szybkosc or d.szybkosc
	dzwiek.Parent = gui
	dzwiek:Play()
	task.delay(d.maks or 2.5, function()
		dzwiek:Stop()
		dzwiek:Destroy()
	end)
end

local function melodia(nuty)
	for i, n in nuty do
		task.delay((i - 1) * D.dzwieki.odstep_melodii_s, function()
			graj("nuta", n)
		end)
	end
end

------------------------------------------------------------------ efekty ekranu
local function pokazWidocznosc()
	ui.status.Visible = stan.gra ~= nil
	ui.start.Visible = stan.ekran == "stanowisko" and not stan.wybor
	ui.koniec.Visible = stan.ekran == "podsumowanie" and not stan.wybor
	ui.krzyz.Visible = stan.ekran == "runda" and stan.gra == "sila"
	ui.blok.Visible = stan.ekran == "runda" and stan.gra == "pancerz"
	ui.pierscienie.Visible = stan.ekran == "runda" and stan.gra == "pancerz"
	ui.przerwij.Visible = stan.ekran == "runda"
	if ui.wybor then
		ui.wybor.Visible = stan.wybor
	end
	gui.Enabled = stan.gra ~= nil or stan.wybor or ui.toast.Visible
end

local licznikToastu = 0
local function komunikat(tekst)
	licznikToastu += 1
	local moj = licznikToastu
	ui.toastTekst.Text = tekst
	ui.toast.Visible = true
	pokazWidocznosc()
	task.delay(2.6, function()
		if moj == licznikToastu then
			ui.toast.Visible = false
			pokazWidocznosc()
		end
	end)
end

local licznikNapisu = 0
local function napisSrodek(tekst, h, rozmiar, czas)
	licznikNapisu += 1
	local moj = licznikNapisu
	ui.srodekTekst.Text = tekst
	ui.srodekTekst.TextColor3 = kolor(h or KOL.krem)
	ui.srodekTekst.TextSize = PX[rozmiar or "seria"]
	ui.srodek.Visible = true
	skalaSrodka.Scale = (skale[1] and skale[1].Scale or 1) * 1.35
	TweenService:Create(skalaSrodka, TweenInfo.new(0.16, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
		{ Scale = skale[1] and skale[1].Scale or 1 }):Play()
	task.delay(czas or 0.55, function()
		if moj == licznikNapisu then
			ui.srodek.Visible = false
		end
	end)
end

local function blysk(przezr, h)
	ui.blysk.BackgroundColor3 = kolor(h or "FFFFFF")
	ui.blysk.BackgroundTransparency = przezr
	TweenService:Create(ui.blysk, TweenInfo.new(0.18), { BackgroundTransparency = 1 }):Play()
end

local function podskokSerii()
	skalaSerii.Scale = 1.3
	TweenService:Create(skalaSerii, TweenInfo.new(0.18, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

local function wstrzas(sila)
	stan.wstrzas = { t = os.clock(), sila = sila }
end

------------------------------------------------------------------ lokalne obiekty 3D (tylko u tego gracza)
local efekty = Instance.new("Folder")
efekty.Name = "TreningProbaEfekty"
efekty.Parent = workspace.CurrentCamera

local function czesc(nazwa, rozmiar, h, material, ksztalt)
	local obj = Instance.new("Part")
	obj.Name = nazwa
	obj.Anchored = true
	obj.CanCollide = false
	obj.CanQuery = false
	obj.CanTouch = false
	obj.Size = rozmiar
	obj.Color = kolor(h)
	obj.Material = material or Enum.Material.SmoothPlastic
	if ksztalt then
		obj.Shape = ksztalt
	end
	obj.TopSurface = Enum.SurfaceType.Smooth
	obj.BottomSurface = Enum.SurfaceType.Smooth
	return obj
end

local function odlamki(pozycja, h, n, rozrzut)
	for _ = 1, n do
		local obj = czesc("Odlamek", Vector3.new(0.45, 0.45, 0.45), h)
		obj.CFrame = CFrame.new(pozycja) * CFrame.Angles(losowe:NextNumber(0, 6), losowe:NextNumber(0, 6), 0)
		obj.Parent = efekty
		local kier = Vector3.new(losowe:NextNumber(-1, 1), losowe:NextNumber(0.2, 1.2), losowe:NextNumber(-1, 1)).Unit
		TweenService:Create(obj, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			CFrame = CFrame.new(pozycja + kier * (rozrzut or 3)) * CFrame.Angles(losowe:NextNumber(0, 6), 2, 1),
			Transparency = 1, Size = Vector3.new(0.15, 0.15, 0.15),
		}):Play()
		task.delay(0.5, function()
			obj:Destroy()
		end)
	end
end

local function obrysModelu(rodzic)
	local h = Instance.new("Highlight")
	h.FillTransparency = 1
	h.OutlineColor = kolor(KOL.tusz)
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Parent = rodzic
end

-- miecz (Siła) i tarcza (Pancerz): modele z kilku części, przesuwane PivotTo
local modelGracza = nil
local function zbudujMiecz()
	local model = Instance.new("Model")
	model.Name = "Miecz"
	local r = czesc("Rekojesc", Vector3.new(0.35, 1.1, 0.35), "6B4A2F")
	r.Parent = model
	local j = czesc("Jelec", Vector3.new(1.4, 0.3, 0.45), KOL.zloto)
	j.CFrame = CFrame.new(0, 0.7, 0)
	j.Parent = model
	local o = czesc("Ostrze", Vector3.new(0.25, 3.6, 0.7), "D8DEE9", Enum.Material.Metal)
	o.CFrame = CFrame.new(0, 2.65, 0)
	o.Parent = model
	model.PrimaryPart = r
	obrysModelu(model)
	model.Parent = efekty
	return model
end

local function zbudujTarcze()
	local model = Instance.new("Model")
	model.Name = "Tarcza"
	local t = czesc("Plyta", Vector3.new(2.6, 2.9, 0.35), D.statystyki[6].kolor)
	t.Parent = model
	local r = czesc("Rama", Vector3.new(2.95, 3.25, 0.25), KOL.zloto)
	r.CFrame = CFrame.new(0, 0, 0.12)
	r.Parent = model
	local k = czesc("Guz", Vector3.new(0.9, 0.9, 0.9), KOL.zloto, nil, Enum.PartType.Ball)
	k.CFrame = CFrame.new(0, 0, -0.25)
	k.Parent = model
	model.PrimaryPart = t
	obrysModelu(model)
	model.Parent = efekty
	return model
end

-- części areny animowane lokalnie (własny kontener; zmiany widzi tylko ten gracz)
local arena = {}
local function zapamietajArene()
	local function z(nazwa)
		local o = sciezka(kontener, nazwa)
		if o and o:IsA("BasePart") then
			return { obj = o, cf = o.CFrame, kolor = o.Color, przezr = o.Transparency }
		end
		return nil
	end
	arena.ramie = z(D.nazwy.miotacz_ramie)
	arena.piesc = z(D.nazwy.golem_piesc)
	arena.oczy = {}
	for _, n in D.nazwy.golem_oczy do
		table.insert(arena.oczy, z(n))
	end
	arena.strefy = {}
	local f = sciezka(kontener, D.nazwy.strefy)
	for _, k in D.gry.sila.akcje do
		local s = f and f:FindFirstChild(k)
		if s and s:IsA("BasePart") then
			arena.strefy[k] = { obj = s, cf = s.CFrame, kolor = s.Color, przezr = s.Transparency }
		end
	end
end

local function przywrocArene()
	for _, w in { arena.ramie, arena.piesc } do
		if w then
			w.obj.CFrame = w.cf
		end
	end
	for _, w in arena.oczy or {} do
		if w then
			w.obj.Color = w.kolor
		end
	end
	for _, w in arena.strefy or {} do
		w.obj.Color = w.kolor
		w.obj.Transparency = w.przezr
	end
end

------------------------------------------------------------------ wizualizacja zdarzeń rundy
local wizualne = {} -- nr → { obj, k }

local function usunWizualne()
	for _, v in wizualne do
		if v.obj then
			local obj = v.obj
			v.obj = nil
			obj:Destroy()
		end
	end
	wizualne = {}
end

local KOLORY_SKRZYN = { "B07A45", "D9822B", "8C5A3C" }
local function nowyPrzedmiot(nr)
	local rodzaj = nr % 3 + 1
	local obj
	if rodzaj == 2 then
		obj = czesc("Dzban", Vector3.new(1.7, 1.7, 1.7), KOLORY_SKRZYN[rodzaj], nil, Enum.PartType.Ball)
	elseif rodzaj == 3 then
		obj = czesc("Beczulka", Vector3.new(1.9, 1.5, 1.5), KOLORY_SKRZYN[rodzaj], Enum.Material.WoodPlanks, Enum.PartType.Cylinder)
	else
		obj = czesc("Skrzynka", Vector3.new(1.6, 1.6, 1.6), KOLORY_SKRZYN[rodzaj], Enum.Material.WoodPlanks)
	end
	obrysModelu(obj)
	obj.Parent = efekty
	return obj
end

local function machnijRamieniem()
	local w = arena.ramie
	if not w then
		return
	end
	local bark = w.cf * CFrame.new(0, 1.3, 0)
	local gora = bark * CFrame.Angles(-2.4, 0, 0) * CFrame.new(0, -1.3, 0)
	TweenService:Create(w.obj, TweenInfo.new(0.12), { CFrame = gora }):Play()
	task.delay(0.16, function()
		TweenService:Create(w.obj, TweenInfo.new(0.25), { CFrame = w.cf }):Play()
	end)
end

local function bezier(a, H, C, Z)
	local q = 1 - a
	return H * (q * q) + C * (2 * q * a) + Z * (a * a)
end

local function tekstTrafienia(seria, lista)
	local i = math.min(#lista, 1 + math.floor(seria / 5))
	return lista[i]
end

-- mnożnik serii dla następnego trafienia (jednostki paska względem trafienia bez serii)
local function mnoznikSerii(seria)
	return L.przyrost(D, seria + 1) / L.przyrost(D, 1)
end

local function odswiezStatus()
	local R = stan.R
	local seria = if R then R.seria else 0
	local suma = if R then R.suma else 0
	ui.seria.Text = string.format("SERIA %d", seria)
	ui.mnoznik.Text = string.format("×%.2f", mnoznikSerii(seria))
	local st = stan.gra and L.statystyka(D, stan.gra)
	if st then
		ui.nazwaGry.Text = string.format("%s · %s", st.nazwa, st.gra)
		ui.suma.Text = string.format("+%d %s w rundzie · sesja +%d", suma, st.nazwa, gracz:GetAttribute(st.atrybut_sesji) or 0)
	end
	local pasek, prog = 0, 1
	if R then
		pasek, prog = R.pasek, L.prog(D, R.W, R.pula)
	end
	ui.wypelnienie.Size = UDim2.fromScale(math.clamp(pasek / math.max(prog, 1e-6), 0, 1), 1)
end

-- werdykt (lokalny albo z serwera) → efekty; każde zdarzenie pokazane raz
local function efekt(w)
	if w.nr ~= nil and stan.lokalne[w.nr] ~= nil then
		return
	end
	if w.nr ~= nil then
		stan.lokalne[w.nr] = w.trafienie
	end
	local W = stan.gra and D.swiat[stan.gra]
	if w.trafienie then
		local nuty = D.dzwieki.skale_nuty
		graj("trafienie")
		graj("nuta", nuty[math.min(#nuty, math.max(1, w.seria))])
		blysk(0.82)
		podskokSerii()
		local lista = if stan.gra == "pancerz" then T.trafienia_blok else T.trafienia
		local tekst = if w.powod == "przetrwana_zmylka" then T.zmylka_ok else tekstTrafienia(w.seria, lista)
		local prog = false
		for _, p in D.przyrost.progi_serii do
			if w.seria == p then
				prog = true
			end
		end
		local st = stan.gra and L.statystyka(D, stan.gra)
		if (w.przyrost or 0) > 0 and st then
			-- pasek treningu pełny: punkt statystyki (to widzi gracz jako nagrodę)
			graj("seria")
			melodia(D.dzwieki.melodia_koniec)
			napisSrodek(string.format("+%d %s!", w.przyrost, st.nazwa), KOL.zloto, "wielki", 1.0)
		elseif prog then
			graj("seria")
			napisSrodek(string.format(T.seria, w.seria), KOL.zloto, "wielki", 0.9)
		else
			napisSrodek(tekst, KOL.krem, "seria")
		end
		if stan.gra == "sila" then
			local v = wizualne[w.nr]
			if v and v.obj then
				odlamki(v.obj.Position, v.obj.Color:ToHex(), 9, 3.5)
				local obj = v.obj
				v.obj = nil
				obj:Destroy()
			end
			wstrzas(0.12)
		elseif w.powod ~= "przetrwana_zmylka" and W then
			odlamki(v3(W.piesc_cel), KOL.zloto, 7, 2.5)
			wstrzas(0.25)
		end
	else
		graj("pudlo")
		napisSrodek(T.pudlo[w.powod] or T.pudlo.przepuszczone, KOL.zle, "duzy", 0.6)
		if w.powod == "przepuszczone" and stan.gra == "pancerz" then
			graj("oberwanie")
			blysk(0.75, KOL.zle)
			wstrzas(0.5)
		end
	end
	odswiezStatus()
end

------------------------------------------------------------------ naciśnięcia
local function animujAkcje(wartosc)
	if stan.gra == "sila" and KATY[wartosc] ~= nil then
		stan.miecz = { t = os.clock(), k = wartosc }
		graj("swist")
	elseif stan.gra == "pancerz" then
		stan.tarcza = { t = os.clock() }
	end
end

local function nacisnij(wartosc)
	if stan.ekran ~= "runda" or stan.R == nil or stan.runda == nil then
		return "brak_rundy"
	end
	animujAkcje(wartosc)
	local t = teraz()
	local w = L.zgloszenie(D, stan.R, wartosc, t, t)
	if not w.przyjete then
		return w.powod
	end
	zdalne:FireServer("akcja", stan.runda.id, wartosc, t)
	efekt(w)
	return w.powod
end

------------------------------------------------------------------ przyciski sterowania
for k, poz in { gora = { 1, 0 }, lewo = { 0, 1 }, prawo = { 2, 1 }, dol = { 1, 2 } } do
	local s = D.sterowanie[k]
	local p = przycisk(ui.krzyz, "Przycisk_" .. k, "", poz[1] * (b + g), poz[2] * (b + g), b, b, D.statystyki[1].kolor, function()
		nacisnij(k)
	end)
	strzalka(p, k)
	napis(p, "Klawisz", s.skrot, "maly", 0, b - 20, b, 18, KOL.krem)
end
do
	local s = D.sterowanie.blok
	local p = przycisk(ui.blok, "Przycisk_blok", "", 0, 0, U.blok_px, U.blok_px, D.statystyki[6].kolor, function()
		nacisnij("blok")
	end)
	zaokraglij(p, U.blok_px)
	napis(p, "Napis", s.napis, "duzy", 0, U.blok_px * 0.22, U.blok_px, 32, KOL.krem)
	napis(p, "Klawisz", s.skrot, "maly", 0, U.blok_px * 0.6, U.blok_px, 18, KOL.krem)
end

local function wyslijStart()
	if stan.ekran == "stanowisko" or stan.ekran == "podsumowanie" then
		graj("przycisk")
		zdalne:FireServer("start")
	end
end

local function wyslijWyjdz()
	graj("przycisk")
	zdalne:FireServer("wyjdz")
end

local function przerwij()
	if stan.ekran == "runda" then
		zdalne:FireServer("przerwij")
	end
end

przycisk(ui.przerwij, "Przycisk_przerwij", "X", 0, 0, U.przycisk_maly_px, U.przycisk_maly_px, KOL.zle, przerwij)

------------------------------------------------------------------ tymczasowy wybór mini-gry
local function pokazWybor(zrodlo)
	if stan.ekran == "runda" then
		komunikat(T.odmowa.trwa_runda)
		return false
	end
	stan.wybor = true
	stan.zrodlo = zrodlo
	pokazWidocznosc()
	return true
end

local function ukryjWybor()
	stan.wybor = false
	pokazWidocznosc()
end

local function wybierz(gra)
	if stan.ekran == "runda" then
		komunikat(T.odmowa.trwa_runda)
		return "trwa_runda"
	end
	graj("przycisk")
	zdalne:FireServer("wejdz", gra)
	return "wyslano"
end

do
	local W = panel("Wybor", 478, 304, UDim2.new(0.5, 0, 0.5, 0), Vector2.new(0.5, 0.5))
	ui.wybor = W
	zaokraglij(W, 14)
	obrysuj(W, 3)
	napis(W, "Tytul", T.tytul_wyboru, "sredni", 12, 6, 400, 26, KOL.tusz, Enum.TextXAlignment.Left)
	napis(W, "Tymczasowy", T.tymczasowy, "maly", 12, 32, 400, 36, KOL.zmylka, Enum.TextXAlignment.Left)
	przycisk(W, "Zamknij", "X", 478 - 12 - U.przycisk_maly_px, 8, U.przycisk_maly_px, U.przycisk_maly_px, KOL.zle, ukryjWybor)
	for i, st in D.statystyki do
		local kol, rz = (i - 1) % 3, math.floor((i - 1) / 3)
		local k = Instance.new("Frame")
		k.Name = "Kafelek_" .. st.id
		k.Position = UDim2.fromOffset(12 + kol * 154, 72 + rz * 114)
		k.Size = UDim2.fromOffset(146, 106)
		k.BackgroundColor3 = Color3.new(1, 1, 1)
		k.BorderSizePixel = 0
		zaokraglij(k, 10)
		obrysuj(k, 2, st.kolor)
		k.Parent = W
		local pasek = Instance.new("Frame")
		pasek.Name = "Pasek"
		pasek.Size = UDim2.new(1, 0, 0, 6)
		pasek.BackgroundColor3 = kolor(st.kolor)
		pasek.BorderSizePixel = 0
		pasek.Parent = k
		napis(k, "Nazwa", st.nazwa, "sredni", 4, 8, 138, 22, KOL.tusz)
		napis(k, "Gra", st.gra, "maly", 4, 30, 138, 18, KOL.szary)
		if st.stan == "grywalna" then
			przycisk(k, "Graj", T.graj, 13, 50, 120, U.przycisk_maly_px, KOL.dobrze, function()
				wybierz(st.id)
			end)
		else
			napis(k, "WProjekcie", T.w_projekcie, "maly", 4, 62, 138, 20, KOL.szary)
			k.BackgroundTransparency = 0.35
		end
	end
end

-- przyciski panelu startu i podsumowania (po utworzeniu wyboru)
przycisk(ui.start, "InnaGra", T.inna_gra, 10, 72, 116, U.przycisk_maly_px, KOL.szary, function()
	pokazWybor("stanowisko")
end)
przycisk(ui.start, "Start", D.sterowanie.start.napis, 138, 70, 124, U.przycisk_px, KOL.dobrze, wyslijStart, "duzy")
przycisk(ui.start, "Wyjdz", T.wyjdz, 274, 72, 116, U.przycisk_maly_px, KOL.zle, wyslijWyjdz)
przycisk(ui.koniec, "JeszczeRaz", T.jeszcze_raz, 10, 176, 150, U.przycisk_maly_px, KOL.dobrze, wyslijStart)
przycisk(ui.koniec, "InnaGra", T.inna_gra, 172, 176, 112, U.przycisk_maly_px, KOL.szary, function()
	pokazWybor("podsumowanie")
end)
przycisk(ui.koniec, "Wyjdz", T.wyjdz, 296, 176, 94, U.przycisk_maly_px, KOL.zle, wyslijWyjdz)

-- wybór i komunikat nad wszystkim (ZIndexBehavior.Sibling: później dodany = wyżej)
ui.wybor.Parent = nil
ui.wybor.Parent = gui
ui.toast.Parent = nil
ui.toast.Parent = gui

------------------------------------------------------------------ skala UI (baza 667 × 375; min. 44 px przycisku, 12 pt tekstu)
local function odswiezSkale()
	local cam = workspace.CurrentCamera
	local s = L.skalaUI(D, cam.ViewportSize.X, cam.ViewportSize.Y)
	for _, sk in skale do
		if sk ~= skalaSrodka then
			sk.Scale = s
		end
	end
	-- przesunięcia (Position) nie skalują się z UIScale: przycisk przerwania zawsze tuż pod statusem
	ui.przerwij.Position = UDim2.new(1, -8, 0, 8 + (ui.status.Size.Y.Offset + 8) * s)
end
odswiezSkale()
workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(odswiezSkale)

------------------------------------------------------------------ klawisze, kamera, dotyk
local AKCJA = "TreningProbaKlawisze"
local mapaGry, mapaStart, mapaWyjdz = {}, {}, {}
local dotykPrzed = nil

local function obsluzKlawisz(_, stanWejscia, wejscie)
	if stanWejscia ~= Enum.UserInputState.Begin then
		return Enum.ContextActionResult.Sink
	end
	local kod = wejscie.KeyCode.Name
	if stan.wybor then
		return Enum.ContextActionResult.Sink
	end
	if stan.ekran == "runda" then
		local a = mapaGry[kod]
		if a then
			nacisnij(a)
		end
	elseif stan.ekran == "stanowisko" or stan.ekran == "podsumowanie" then
		if mapaStart[kod] then
			wyslijStart()
		elseif mapaWyjdz[kod] then
			wyslijWyjdz()
		end
	end
	return Enum.ContextActionResult.Sink
end

local function odepnij()
	ContextActionService:UnbindAction(AKCJA)
end

local function przypnij(gra)
	odepnij()
	mapaGry, mapaStart, mapaWyjdz = {}, {}, {}
	local wszystkie, byly = {}, {}
	local function dodaj(n)
		if not byly[n] and Enum.KeyCode[n] then
			byly[n] = true
			table.insert(wszystkie, Enum.KeyCode[n])
		end
	end
	for _, a in D.gry[gra].akcje do
		local s = D.sterowanie[a]
		for _, n in s.klawisze do
			mapaGry[n] = a
			dodaj(n)
		end
		for _, n in s.pad do
			mapaGry[n] = a
			dodaj(n)
		end
	end
	for _, lista in { { D.sterowanie.start, mapaStart }, { D.sterowanie.wyjdz, mapaWyjdz } } do
		for _, n in lista[1].klawisze do
			lista[2][n] = true
			dodaj(n)
		end
		for _, n in lista[1].pad do
			lista[2][n] = true
			dodaj(n)
		end
	end
	for _, n in D.sterowanie.blokuj_ruch do
		dodaj(n)
	end
	ContextActionService:BindActionAtPriority(AKCJA, obsluzKlawisz, false, Enum.ContextActionPriority.High.Value + 50, table.unpack(wszystkie))
end

local function kameraNaStanowisko(gra)
	local cam = workspace.CurrentCamera
	local W = D.swiat[gra]
	cam.CameraType = Enum.CameraType.Scriptable
	cam.CFrame = CFrame.lookAt(v3(W.oko), v3(W.cel))
end

local function kameraPrzywroc()
	local cam = workspace.CurrentCamera
	cam.CameraType = Enum.CameraType.Custom
	local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
	if hum then
		cam.CameraSubject = hum
	end
end

local function usunModelGracza()
	if modelGracza then
		local model = modelGracza
		modelGracza = nil
		model:Destroy()
	end
end

local function wejdzNaStanowisko(gra)
	usunWizualne()
	usunModelGracza()
	przywrocArene()
	if not arena.piesc or not arena.ramie then
		zapamietajArene() -- arena jest Persistent, ale gdyby nie była jeszcze wczytana przy starcie skryptu
	end
	stan.gra = gra
	stan.runda = nil
	stan.R = nil
	stan.lokalne = {}
	stan.wybor = false
	stan.ekran = "stanowisko"
	przypnij(gra)
	if dotykPrzed == nil then
		dotykPrzed = GuiService.TouchControlsEnabled
	end
	GuiService.TouchControlsEnabled = false
	kameraNaStanowisko(gra)
	modelGracza = if gra == "sila" then zbudujMiecz() else zbudujTarcze()
	ui.opis.Text = if gra == "sila" then T.sterowanie_sila else T.sterowanie_pancerz
	odswiezStatus()
	ui.czas.Text = string.format("%d:%02d", math.floor(D.runda.dlugosc_s / 60), D.runda.dlugosc_s % 60)
	pokazWidocznosc()
end

local function zejdzZeStanowiska()
	odepnij()
	usunWizualne()
	usunModelGracza()
	przywrocArene()
	if dotykPrzed ~= nil then
		GuiService.TouchControlsEnabled = dotykPrzed
		dotykPrzed = nil
	end
	kameraPrzywroc()
	stan.gra = nil
	stan.runda = nil
	stan.R = nil
	stan.ekran = "brak"
	stan.wybor = false
	pokazWidocznosc()
end

------------------------------------------------------------------ klatka: odliczanie, lot skrzynek, zamach golema, kamera
local function wyglad(t)
	local W = stan.gra and D.swiat[stan.gra]
	if not W then
		return
	end
	-- miecz / tarcza gracza
	if modelGracza and stan.gra == "sila" then
		local spoczynek = CFrame.new(v3(W.miecz)) * CFrame.Angles(math.rad(25), 0, math.rad(-20))
		local cf = spoczynek
		if stan.miecz then
			local dt = os.clock() - stan.miecz.t
			if dt < 0.34 then
				local piers = v3(W.podest) + Vector3.new(0.8, 3.4, -0.4)
				local cios = CFrame.lookAt(piers, v3(W.strefy[stan.miecz.k])) * CFrame.Angles(-math.pi / 2, 0, 0)
				local f = if dt < 0.09 then dt / 0.09 else 1 - (dt - 0.09) / 0.25
				cf = spoczynek:Lerp(cios, math.clamp(f, 0, 1))
			end
		end
		modelGracza:PivotTo(cf)
	elseif modelGracza then
		local spoczynek = CFrame.lookAt(v3(W.tarcza), v3(W.tarcza) + Vector3.new(0, 0, -1))
		local blok = CFrame.lookAt(v3(W.tarcza_blok), v3(W.tarcza_blok) + Vector3.new(0, 0, -1))
		local f = 0
		if stan.tarcza then
			local dt = os.clock() - stan.tarcza.t
			f = if dt < 0.06 then dt / 0.06 elseif dt < 0.24 then 1 else 1 - (dt - 0.24) / 0.2
		end
		modelGracza:PivotTo(spoczynek:Lerp(blok, math.clamp(f, 0, 1)))
	end
	local cam = workspace.CurrentCamera
	if stan.ekran ~= "brak" and cam.CameraType == Enum.CameraType.Scriptable then
		local baza = CFrame.lookAt(v3(W.oko), v3(W.cel))
		if stan.wstrzas then
			local dt = os.clock() - stan.wstrzas.t
			if dt < 0.25 then
				local s = stan.wstrzas.sila * (1 - dt / 0.25)
				baza = baza * CFrame.new(losowe:NextNumber(-s, s), losowe:NextNumber(-s, s), 0)
			else
				stan.wstrzas = nil
			end
		end
		cam.CFrame = baza
	end
	local Rd = stan.runda
	if stan.ekran ~= "runda" or not Rd then
		return
	end
	-- odliczanie i czas
	if t < Rd.t0 then
		local n = math.ceil(Rd.t0 - t)
		if n ~= stan.ostatnieOdliczanie then
			stan.ostatnieOdliczanie = n
			napisSrodek(tostring(n), KOL.krem, "wielki", 0.8)
			graj("nuta", 1)
		end
	elseif stan.ostatnieOdliczanie ~= 0 then
		stan.ostatnieOdliczanie = 0
		napisSrodek(D.sterowanie.start.napis .. "!", KOL.zloto, "wielki", 0.6)
		graj("nuta", 2)
	end
	local zostalo = math.max(0, Rd.t0 + Rd.dlugosc - math.max(t, Rd.t0))
	ui.czas.Text = string.format("%d:%02d", math.floor(zostalo / 60), math.floor(zostalo % 60))
	-- zdarzenia, których nie odbito (lokalnie, z tym samym zapasem co serwer)
	if stan.R and not stan.R.koniec then
		for _, w in L.przeterminowane(D, stan.R, t) do
			efekt(w)
		end
	end
	if stan.gra == "sila" then
		local G = D.gry.sila
		local swiec = {}
		for _, e in Rd.plan do
			local ti = Rd.t0 + e.t
			local start = ti - G.lot_s
			local v = wizualne[e.nr]
			if v == nil and t >= start and t < ti + 0.5 then
				v = { obj = nowyPrzedmiot(e.nr), k = e.wartosc }
				wizualne[e.nr] = v
				machnijRamieniem()
			end
			if v and v.obj then
				local a = (t - start) / G.lot_s
				local H, Z = v3(W.reka), v3(W.strefy[v.k])
				local C = (H + Z) / 2 + v3(W.luki[v.k])
				local p = if a <= 1 then bezier(math.max(0, a), H, C, Z) else Z + (Z - C) * (2 * (a - 1))
				v.obj.CFrame = CFrame.new(p) * CFrame.Angles(a * 5, a * 3, 0)
				if a > 1.8 then
					local obj = v.obj
					v.obj = nil
					obj:Destroy()
				end
			end
			if stan.lokalne[e.nr] == nil and math.abs(t - ti) <= e.okno then
				swiec[e.wartosc] = true
			end
		end
		for k, w in arena.strefy or {} do
			if swiec[k] then
				w.obj.Color = kolor(KOL.zloto)
				w.obj.Transparency = 0.2
			else
				w.obj.Color = w.kolor
				w.obj.Transparency = w.przezr
			end
		end
	else
		local G = D.gry.pancerz
		local spoczynek, zamach, cel = v3(W.piesc_spoczynek), v3(W.piesc_zamach), v3(W.piesc_cel)
		local poz = spoczynek
		local oczy = nil
		local wolne = 1
		for _, p in pierscienie do
			p.ramka.Visible = false
		end
		for _, e in Rd.plan do
			local ti = Rd.t0 + e.t
			local od = ti - G.zamach_s
			if t >= od and t < ti + 0.25 then
				local f = (t - od) / (G.zamach_s - 0.12)
				if t < ti - 0.12 then
					poz = spoczynek:Lerp(zamach, math.clamp(f, 0, 1))
				elseif e.wartosc == "cios" and t < ti then
					poz = zamach:Lerp(cel, (t - (ti - 0.12)) / 0.12)
				elseif e.wartosc == "cios" then
					poz = cel:Lerp(spoczynek, math.clamp((t - ti) / 0.25, 0, 1))
				else
					poz = zamach:Lerp(spoczynek, math.clamp((t - (ti - 0.12)) / 0.37, 0, 1))
				end
				oczy = if e.wartosc == "zmylka" then KOL.zmylka else KOL.cios
			end
			if t >= od and t < ti + 0.1 and wolne <= #pierscienie and stan.lokalne[e.nr] == nil then
				local p = pierscienie[wolne]
				wolne += 1
				local s = 1 + 1.6 * math.clamp((ti - t) / G.zamach_s, 0, 1)
				p.ramka.Size = UDim2.fromScale(s, s)
				p.obrys.Color = kolor(if e.wartosc == "zmylka" then KOL.zmylka else KOL.cios)
				p.ramka.Visible = true
			end
		end
		if arena.piesc then
			arena.piesc.obj.CFrame = CFrame.new(poz)
		end
		for _, w in arena.oczy do
			if w then
				w.obj.Color = if oczy then kolor(oczy) else w.kolor
			end
		end
	end
end
RunService.RenderStepped:Connect(function()
	wyglad(teraz())
end)

------------------------------------------------------------------ wiadomości z serwera
local function zapiszWynik(w)
	table.insert(stan.wyniki, w)
	while #stan.wyniki > 16 do
		table.remove(stan.wyniki, 1)
	end
end

zdalne.OnClientEvent:Connect(function(rodzaj, a, b)
	if rodzaj == "wybor" then
		pokazWybor(a)
	elseif rodzaj == "odmowa" then
		komunikat(b or tostring(a))
	elseif rodzaj == "przybycie" then
		wejdzNaStanowisko(a)
	elseif rodzaj == "runda" then
		if stan.gra ~= a.gra then
			wejdzNaStanowisko(a.gra)
		end
		usunWizualne()
		przywrocArene()
		stan.runda = a
		stan.R = L.nowaRunda(D, a.gra, a.id, a.t0, a.plan, { pasek = a.pasek, W = a.W, pula = a.pula })
		stan.lokalne = {}
		stan.ostatnieOdliczanie = nil
		stan.wybor = false
		stan.ekran = "runda"
		odswiezStatus()
		pokazWidocznosc()
	elseif rodzaj == "wynik" then
		zapiszWynik(a)
		local R = stan.R
		if R and stan.runda and stan.runda.id == a.id then
			if a.nr ~= nil and stan.lokalne[a.nr] ~= nil and stan.lokalne[a.nr] ~= a.trafienie then
				stan.rozbieznosci += 1
			end
			if a.nr ~= nil and R.rozstrzygniete[a.nr] == nil then
				R.rozstrzygniete[a.nr] = if a.trafienie then "T" else "P"
			end
			R.seria = a.seria
			R.suma = a.suma
			if type(a.pasek) == "number" then
				R.pasek = a.pasek
				R.W = (stan.runda.W or 0) + a.suma
			end
			if a.nr ~= nil and stan.lokalne[a.nr] == nil then
				efekt(a)
			end
			odswiezStatus()
		end
	elseif rodzaj == "koniec" then
		stan.podsumowanie = a
		if stan.R then
			stan.R.koniec = true
			stan.R.seria = 0
		end
		usunWizualne()
		przywrocArene()
		local st = L.statystyka(D, a.gra)
		ui.kTytul.Text = if a.przerwana then T.koniec .. " (przerwana)" else T.koniec
		ui.k1.Text = string.format("Trafienia %d z %d (%d%%)", a.trafienia, a.n, a.celnosc)
		ui.k2.Text = string.format("Najdłuższa seria %d", a.najdluzsza)
		ui.k3.Text = string.format("%s +%d", st.nazwa, a.suma)
		ui.k4.Text = string.format("Pasek %d/%d · w tej sesji +%d (atrybut %s, bez zapisu)", math.floor(a.pasek or 0),
			math.ceil(a.prog or 0), a.sesja, st.atrybut_sesji)
		stan.ekran = "podsumowanie"
		melodia(D.dzwieki.melodia_koniec)
		odswiezStatus()
		pokazWidocznosc()
	elseif rodzaj == "wyjscie" then
		zejdzZeStanowiska()
	end
end)

gracz.CharacterAdded:Connect(function()
	if stan.gra then
		zejdzZeStanowiska()
	end
end)

------------------------------------------------------------------ E przy trenerze w bazarze: zdarzenie OknoMiejsca
-- BindableEvent w ReplicatedStorage (tworzy go pierwszy, kto potrzebuje — bazar albo ten skrypt); słuchamy każdego
-- o tej nazwie, gdyby dwa skrypty utworzyły go naraz. Atrybut "training_center" = true wyłącza dymek bazaru
-- „Trener: mini-gry w budowie”, póki działa ten tymczasowy wybór.
local zdarzeniaOkien = {}
local function tymczasowyWlaczony()
	return kontener:GetAttribute("WyborTymczasowy") ~= false
end

local function podepnijOkna(okna)
	if zdarzeniaOkien[okna] or okna.Name ~= D.zdarzenie_okien or not okna:IsA("BindableEvent") then
		return
	end
	zdarzeniaOkien[okna] = true
	okna.Event:Connect(function(id)
		if id == D.id_miejsca_bazaru and tymczasowyWlaczony() then
			pokazWybor("bazar")
		end
	end)
	if tymczasowyWlaczony() then
		okna:SetAttribute(D.id_miejsca_bazaru, true)
	end
end
for _, c in ReplicatedStorage:GetChildren() do
	podepnijOkna(c)
end
ReplicatedStorage.ChildAdded:Connect(podepnijOkna)
if not ReplicatedStorage:FindFirstChild(D.zdarzenie_okien) then
	local nowe = Instance.new("BindableEvent")
	nowe.Name = D.zdarzenie_okien
	nowe.Parent = ReplicatedStorage
end

-- uchwyt dla docelowego okna Pawła (klient): workspace.TreningProba.Sygnaly.WybierzGre:Invoke("sila")
wybierzF.OnInvoke = function(gra)
	return wybierz(gra)
end

------------------------------------------------------------------ haczyk testowy
local function autograj(celnosc, blokujZmylki)
	local Rd = stan.runda
	if not Rd or stan.ekran ~= "runda" then
		return 0
	end
	local n = 0
	for _, e in Rd.plan do
		local akcja = if stan.gra == "pancerz" then "blok" else e.wartosc
		if losowe:NextNumber() < (celnosc or 1) and (e.wartosc ~= "zmylka" or blokujZmylki) then
			n += 1
			task.delay(math.max(0, Rd.t0 + e.t - teraz()), function()
				if stan.runda == Rd then
					nacisnij(akcja)
				end
			end)
		end
	end
	return n
end

local function widoczny(o)
	if not gui.Enabled then
		return false
	end
	while o and o ~= gui do
		if o:IsA("GuiObject") and not o.Visible then
			return false
		end
		o = o.Parent
	end
	return o == gui
end

local function stanTestowy()
	local cam = workspace.CurrentCamera
	local minBaza, minTekst, minEkran = math.huge, math.huge, math.huge
	for _, p in przyciski do
		minBaza = math.min(minBaza, p.szer, p.wys)
		if widoczny(p.obiekt) then
			minEkran = math.min(minEkran, p.obiekt.AbsoluteSize.X, p.obiekt.AbsoluteSize.Y)
		end
	end
	for _, n in napisy do
		minTekst = math.min(minTekst, n.rozmiar)
	end
	local kafelki, grywalne = 0, 0
	for _, k in ui.wybor:GetChildren() do
		if string.sub(k.Name, 1, 8) == "Kafelek_" then
			kafelki += 1
			if k:FindFirstChild("Graj") then
				grywalne += 1
			end
		end
	end
	local R = stan.R
	return {
		ekran = stan.ekran, wybor = stan.wybor, zrodlo = stan.zrodlo, gra = stan.gra, guiWlaczone = gui.Enabled,
		runda = if stan.runda then { id = stan.runda.id, gra = stan.runda.gra, n = #stan.runda.plan, t0 = stan.runda.t0 } else nil,
		lokalnie = if R then { trafienia = R.trafienia, pudla = R.pudla, puste = R.puste, spam = R.spam, seria = R.seria, suma = R.suma } else nil,
		wyniki = stan.wyniki, rozbieznosci = stan.rozbieznosci, podsumowanie = stan.podsumowanie,
		ui = {
			skala = L.skalaUI(D, cam.ViewportSize.X, cam.ViewportSize.Y), ekranPx = { cam.ViewportSize.X, cam.ViewportSize.Y },
			przyciskBazaMin = minBaza, tekstBazaMin = minTekst, przyciskNaEkranieMin = if minEkran < math.huge then minEkran else nil,
			przycisk667 = minBaza * L.skalaUI(D, 667, 375), tekst667 = minTekst * L.skalaUI(D, 667, 375),
			przycisk568 = minBaza * L.skalaUI(D, 568, 320), tekst568 = minTekst * L.skalaUI(D, 568, 320),
		},
		kamera = cam.CameraType.Name, dotyk = GuiService.TouchControlsEnabled,
		kafelki = kafelki, grywalne = grywalne, zdarzeniaOkien = (function()
			local n = 0
			for _ in zdarzeniaOkien do
				n += 1
			end
			return n
		end)(),
	}
end

sterowanie.OnInvoke = function(polecenie, a, b2)
	if polecenie == "stan" then
		return stanTestowy()
	elseif polecenie == "wybor" then
		return pokazWybor(a or "test")
	elseif polecenie == "okno" then
		for okna in zdarzeniaOkien do
			okna:Fire(D.id_miejsca_bazaru, { nazwa = "Trener", postac = "Trener", akcja = "okno" })
		end
		return true
	elseif polecenie == "graj" then
		return wybierz(a)
	elseif polecenie == "start" then
		wyslijStart()
		return true
	elseif polecenie == "nacisnij" then
		return nacisnij(a)
	elseif polecenie == "autograj" then
		return autograj(a, b2)
	elseif polecenie == "zaplanuj" then
		-- a = { { nr = 2, w = "lewo", dt = 0 }, … }: naciśnięcia w chwili t0 + t zdarzenia nr + dt (ta sama droga co klawisz)
		local Rd = stan.runda
		if not Rd then
			return 0
		end
		local n = 0
		for _, p in a do
			local e = Rd.plan[p.nr]
			if e then
				n += 1
				task.delay(math.max(0, Rd.t0 + e.t + (p.dt or 0) - teraz()), function()
					if stan.runda == Rd then
						nacisnij(p.w)
					end
				end)
			end
		end
		return n
	elseif polecenie == "spam" then
		local id = stan.runda and stan.runda.id or 0
		for _ = 1, a or 1 do
			zdalne:FireServer("akcja", id, b2, teraz())
		end
		return a
	elseif polecenie == "surowe" then
		if stan.runda then
			zdalne:FireServer("akcja", stan.runda.id, a, teraz() + (b2 or 0))
		end
		return true
	elseif polecenie == "wyjdz" then
		wyslijWyjdz()
		return true
	elseif polecenie == "inna" then
		return pokazWybor("stanowisko")
	elseif polecenie == "zamknij" then
		ukryjWybor()
		return true
	elseif polecenie == "przerwij" then
		przerwij()
		return true
	end
	return nil
end

zapamietajArene()
pokazWidocznosc()
kontener:SetAttribute("KlientTreninguGotowy", true)
