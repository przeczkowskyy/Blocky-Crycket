--[[
	KlientBazaru — kliencka połowa „miasteczka-bazaru w grze” (Script, RunContext = Client, w kontenerze
	Workspace/MiasteczkoBazarGra). Niczego nie przenosi i niczego nie wysyła do serwera: E obsługuje serwer
	(SerwerBazaru), a tu przychodzą tylko jego polecenia przez Zdalne/ZdarzeniaBazaru:
		"okno", id              → okno 2D miejsca:
		                           1) ReplicatedStorage.OknoMiejsca:Fire(id, info) — JEDNO zdarzenie dla okien Pawła;
		                           2) gdy miejsce ma przypisany przycisk HUD (DaneBazaru.miejsca[id].hud, np. "Shop"),
		                              także ReplicatedStorage.HUDButtonPressed:Fire(hud) — istniejące okno HUD otworzy się
		                              od razu, bez zmian w plikach Pawła;
		                           3) jeśli po czasy.czekaj_na_okno_s nic się nie otworzyło (żaden ekran nie został
		                              włączony), okno nie zgłosiło się atrybutem, a dymki nie są wyłączone — dymek nad
		                              sprzedawcą, np. „Zbrojmistrz: sklep w budowie”;
		"dymek", id, tekst      → dymek nad miejscem (odmowa, „Zamknięte”);
		"chmury", id            → Workspace/TeleportChmury/Otworz:Fire() (przejście przez chmury), bez niego dymek;
		"przeniesiono", id, cel → tylko zapis (haczyk testowy).

	PODPIĘCIE OKNA PAWŁA — jedna linijka w jego skrypcie klienta (ten sam wzór co bindable() w EquipmentPanelClient):
		bindable("OknoMiejsca").Event:Connect(function(id) if id == "zbrojownia" then open() end end)
	id: karczma, mistrz_gier, sklep_magiczny, zbrojownia, training_center, zagroda_petow, tablica, dzialka, lochy.
	Dymek „w budowie” wyłącza: (a) samo otwarcie okna (klient widzi, że jakiś ScreenGui się włączył),
	(b) atrybut zdarzenia: bindable("OknoMiejsca"):SetAttribute("zbrojownia", true), (c) atrybut kontenera w Edit:
	DymkiWylaczone = true (wszystkie) albo BezDymku = "zbrojownia,karczma" (wybrane).

	Lochy (D-042): gdy serwer ustawi graczowi atrybut BazarLochyOtwarte = true, klient chowa U SIEBIE kłódkę
	Workspace/MiasteczkoBazar/BramaLochow/Blokada (LocalTransparencyModifier, nic nie idzie na serwer).
	Haczyk testowy: Sygnaly/SterowanieKlienta ("stan" | "okno", id | "dymek", id, tekst | "chmury", id).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneBazaru"))
local L = require(moduly:WaitForChild("LogikaBazaru"))
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaBazaru")
local sterowanie: BindableFunction = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieKlienta")
local folderPunktow = kontener:WaitForChild("Punkty")
local ekrany = gracz:WaitForChild("PlayerGui")

local KREM, TUSZ = Color3.fromHex("FFF6E0"), Color3.fromHex("17121F")
local PREFIKS_DYMKU = "MiasteczkoBazarDymek "

local function v3(t): Vector3
	return Vector3.new(t[1], t[2], t[3])
end

local function sciezka(tekst: string): Instance?
	local o: Instance? = workspace
	for i, n in string.split(tekst, "/") do
		if not (i == 1 and n == "Workspace") then
			o = o and o:FindFirstChild(n)
		end
	end
	return o
end

------------------------------------------------------------------ jedno zdarzenie dla okien 2D (tylko u klienta)
local function zdarzenieOkien(): BindableEvent?
	local e = ReplicatedStorage:FindFirstChild(D.zdarzenie_okien)
	if not e then
		local nowe = Instance.new("BindableEvent")
		nowe.Name = D.zdarzenie_okien
		nowe.Parent = ReplicatedStorage
		return nowe
	end
	if e:IsA("BindableEvent") then
		return e
	end
	warn(D.prefiks .. "ReplicatedStorage." .. D.zdarzenie_okien .. " nie jest BindableEvent — okna przez zdarzenie wyłączone")
	return nil
end
local okna = zdarzenieOkien()

------------------------------------------------------------------ historia (haczyk testowy)
local historia = {}
local licznikOkien = 0

local function zapisz(wpis)
	table.insert(historia, wpis)
	while #historia > 12 do
		table.remove(historia, 1)
	end
end

------------------------------------------------------------------ dymki w świecie
-- BillboardGui wprost w PlayerGui (Adornee = część punktu E), tylko u tego gracza; ResetOnSpawn = false
local dymki = {} -- id → { gui, tekst, od }

local function kotwica(id: string): (BasePart?, Vector3)
	local czesc = folderPunktow:FindFirstChild("E " .. id)
	local m = D.miejsca[id]
	if not czesc or not czesc:IsA("BasePart") or not m then
		return nil, Vector3.zero
	end
	local nad = if m.dymek_nad then v3(m.dymek_nad) else czesc.Position + Vector3.new(0, D.dymek.nad_podpowiedzia, 0)
	local model = m.model and sciezka(m.model)
	if model and model:IsA("Model") then
		local cf, rozmiar = model:GetBoundingBox()
		nad = Vector3.new(cf.Position.X, cf.Position.Y + rozmiar.Y / 2 + D.dymek.nad_glowa, cf.Position.Z)
	end
	return czesc, nad - czesc.Position
end

local function pokazDymek(id: string, tekst: string)
	local czesc, przesuniecie = kotwica(id)
	if not czesc then
		return
	end
	local stary = dymki[id]
	if stary and stary.gui then
		stary.gui:Destroy()
	end
	local b = Instance.new("BillboardGui")
	b.Name = PREFIKS_DYMKU .. id
	b.Adornee = czesc
	b.StudsOffsetWorldSpace = przesuniecie
	b.Size = UDim2.fromOffset(D.dymek.szer_px, D.dymek.wys_px)
	b.MaxDistance = D.dymek.zasieg
	b.AlwaysOnTop = true
	b.LightInfluence = 0
	b.ResetOnSpawn = false
	local ramka = Instance.new("Frame")
	ramka.Name = "Ramka"
	ramka.Size = UDim2.fromScale(1, 1)
	ramka.BackgroundColor3 = KREM
	ramka.BorderSizePixel = 0
	ramka.Parent = b
	local skala = Instance.new("UIScale")
	skala.Scale = 0.6
	skala.Parent = ramka
	local rog = Instance.new("UICorner")
	rog.CornerRadius = UDim.new(0.3, 0)
	rog.Parent = ramka
	local obrys = Instance.new("UIStroke")
	obrys.Color = TUSZ
	obrys.Thickness = 3
	obrys.Parent = ramka
	local napis = Instance.new("TextLabel")
	napis.Name = "Tekst"
	napis.BackgroundTransparency = 1
	napis.Position = UDim2.fromScale(0.05, 0.1)
	napis.Size = UDim2.fromScale(0.9, 0.8)
	napis.Font = Enum.Font.FredokaOne
	napis.TextScaled = true
	napis.TextColor3 = TUSZ
	napis.Text = tekst
	napis.Parent = ramka
	b.Parent = ekrany
	local wpis = { gui = b, tekst = tekst, od = os.clock() }
	dymki[id] = wpis
	TweenService:Create(skala, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	task.delay(D.czasy.dymek_s, function()
		if dymki[id] ~= wpis then
			return
		end
		local t = TweenService:Create(skala, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.01 })
		t.Completed:Connect(function()
			if dymki[id] == wpis then
				dymki[id] = nil
			end
			b:Destroy()
		end)
		t:Play()
	end)
end

------------------------------------------------------------------ czy jakieś okno się otworzyło
local function migawkaOkien()
	local t = {}
	for _, g in ekrany:GetChildren() do
		if g:IsA("ScreenGui") then
			t[g] = g.Enabled
			for _, c in g:GetChildren() do
				if c:IsA("GuiObject") then
					t[c] = c.Visible
				end
			end
		end
	end
	return t
end

local function cosSieOtworzylo(przed): string?
	for _, g in ekrany:GetChildren() do
		if g:IsA("ScreenGui") and g.Enabled then
			if przed[g] ~= true then
				return g.Name
			end
			for _, c in g:GetChildren() do
				if c:IsA("GuiObject") and c.Visible and przed[c] == false then
					return g.Name .. "/" .. c.Name
				end
			end
		end
	end
	return nil
end

local function oknoJuzOtwarte(nazwa: string?): boolean
	if not nazwa then
		return false
	end
	local g = ekrany:FindFirstChild(nazwa)
	return g ~= nil and g:IsA("ScreenGui") and g.Enabled
end

------------------------------------------------------------------ okno miejsca
local function otworzOkno(id: string)
	local m = D.miejsca[id]
	if not m then
		return
	end
	licznikOkien += 1
	local wpis = { id = id, czas = os.clock(), hud = nil, otwarto = nil, dymek = false, zdarzenie = okna ~= nil }
	local przed = migawkaOkien()
	if okna then
		okna:Fire(id, { nazwa = m.obiekt, postac = m.postac, akcja = m.akcja })
	end
	if m.hud and not oknoJuzOtwarte(m.gui) then
		local h = ReplicatedStorage:FindFirstChild(D.sygnal_hud)
		if h and h:IsA("BindableEvent") then
			h:Fire(m.hud)
			wpis.hud = m.hud
		end
	end
	zapisz(wpis)
	task.delay(D.czasy.czekaj_na_okno_s, function()
		wpis.otwarto = cosSieOtworzylo(przed)
		local zgloszone = if okna then okna:GetAttribute(id) else nil
		if L.dymekOkna(id, wpis.otwarto, zgloszone, kontener:GetAttribute("DymkiWylaczone"), kontener:GetAttribute("BezDymku")) then
			wpis.dymek = true
			local tekst = m.dymek
			if id == "lochy" and m.dymek_otwarte then
				tekst = m.dymek_otwarte
			end
			pokazDymek(id, tekst)
		end
	end)
end

------------------------------------------------------------------ portal krain → przejście przez chmury
local function otworzChmury(id: string)
	local t = workspace:FindFirstChild(D.chmury.kontener)
	local o = t and t:FindFirstChild(D.chmury.zdarzenie)
	if t and o and o:IsA("BindableEvent") then
		if t:GetAttribute(D.chmury.atrybut_trwa) == true then
			zapisz({ id = id, czas = os.clock(), chmury = "trwa" })
			return
		end
		o:Fire()
		zapisz({ id = id, czas = os.clock(), chmury = "otwarte" })
	else
		zapisz({ id = id, czas = os.clock(), chmury = "brak" })
		pokazDymek(id, D.miejsca[id].dymek)
	end
end

------------------------------------------------------------------ lochy: kłódka chowana tylko u tego gracza
local lochyOtwarte = false

local function lochyLokalnie()
	lochyOtwarte = gracz:GetAttribute(D.lochy.atrybut_gracza) == true
	local blokada = sciezka(D.lochy.blokada)
	if not blokada then
		return
	end
	for _, d in blokada:GetDescendants() do
		if d:IsA("BasePart") then
			d.LocalTransparencyModifier = if lochyOtwarte then 1 else 0
		end
	end
end
gracz:GetAttributeChangedSignal(D.lochy.atrybut_gracza):Connect(lochyLokalnie)
task.spawn(function()
	-- mapa może się wczytać później (streaming) — powtarzamy tylko, gdy lochy są otwarte
	while kontener.Parent do
		if lochyOtwarte then
			lochyLokalnie()
		end
		task.wait(2)
	end
end)
lochyLokalnie()

------------------------------------------------------------------ polecenia serwera
zdarzenia.OnClientEvent:Connect(function(polecenie: any, id: any, a: any)
	if type(polecenie) ~= "string" or type(id) ~= "string" or not D.miejsca[id] then
		return
	end
	if polecenie == "okno" then
		otworzOkno(id)
	elseif polecenie == "dymek" then
		if type(a) == "string" then
			zapisz({ id = id, czas = os.clock(), dymekSerwera = a })
			pokazDymek(id, a)
		end
	elseif polecenie == "chmury" then
		otworzChmury(id)
	elseif polecenie == "przeniesiono" then
		zapisz({ id = id, czas = os.clock(), przeniesiono = a })
	end
end)

------------------------------------------------------------------ haczyk testowy
sterowanie.OnInvoke = function(polecenie: any, a: any, b: any)
	if polecenie == "stan" then
		local widoczne = {}
		for id, w in dymki do
			widoczne[id] = w.tekst
		end
		local kopia = {}
		for i, w in historia do
			kopia[i] = { id = w.id, czas = w.czas, hud = w.hud, otwarto = w.otwarto, dymek = w.dymek,
				zdarzenie = w.zdarzenie, chmury = w.chmury, dymekSerwera = w.dymekSerwera, przeniesiono = w.przeniesiono }
		end
		return {
			gotowy = kontener:GetAttribute("KlientBazaruGotowy"),
			okna = licznikOkien,
			historia = kopia,
			dymki = widoczne,
			lochy = lochyOtwarte,
			zdarzenie = okna ~= nil and okna:GetFullName() or nil,
		}
	elseif polecenie == "okno" and type(a) == "string" then
		otworzOkno(a)
		return true
	elseif polecenie == "dymek" and type(a) == "string" and type(b) == "string" then
		pokazDymek(a, b)
		return true
	elseif polecenie == "chmury" and type(a) == "string" then
		otworzChmury(a)
		return true
	end
	return false
end

kontener:SetAttribute("KlientBazaruGotowy", true)
