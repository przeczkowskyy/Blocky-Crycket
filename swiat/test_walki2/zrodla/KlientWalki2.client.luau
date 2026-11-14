--[[
	KlientWalki2 — kliencka połowa prototypu walki v2 (Script, RunContext = Client; działa z kontenera w Workspace).
	Spina wejścia z panelem wyboru i odtwarzaczem:
		• ProximityPrompt „PodpowiedzWalki2” na tablicy (E / dotknięcie) → panel wyboru (WyborWalki2) → WALCZ →
		  OdtwarzaczWalki2.uruchom(wybór). Panel zamyka się sam, gdy gracz odejdzie od tablicy;
		• podpowiedź pokazuje odliczanie, gdy serwer jeszcze nie przyjmie walki (zmiana lokalna);
		• haczyki testowe (tylko Studio, jak w v1):
			Sygnaly/PokazAktora (BindableEvent, z etapu 1) — Fire(klucz, akcja?, opcje?) pokaz klonu aktora; Fire() sprząta;
			Sygnaly/Sterowanie (BindableFunction) — Invoke(polecenie, ...):
				"start", wybor, opcje   → uruchamia walkę bez panelu (opcje jak w OdtwarzaczWalki2)
				"pomin" | "zamknij" | "jeszczeRaz" | "tempo", t | "przewin", s | "przewinDo", τ | "stan" | "wybor" (otwiera panel)
				| "kadr" (czy aktorzy są w kadrze i nie zasłaniają się) | "napisy" (napisy nad postaciami)
		• odmowa serwera → komunikat z powodem (panel wyboru z polem Status albo dymek); atrybut OstatniKomunikat.
	Sam nic nie liczy i nie wysyła liczb — prośbę z wyborem z listy wysyła odtwarzacz.
]]
if not game:GetService("RunService"):IsStudio() then
	return -- prototyp działa wyłącznie w Studio; w opublikowanej grze jest bezwładny
end

local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local sygnaly = kontener:WaitForChild("Sygnaly")
kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke2")
local Ustawienia = require(moduly:WaitForChild("Ustawienia"))
local Aktorzy = require(moduly:WaitForChild("Aktorzy"))
local Odtwarzacz = require(moduly:WaitForChild("OdtwarzaczWalki2"))
local Wybor = require(moduly:WaitForChild("WyborWalki2"))

local gracz = Players.LocalPlayer
local MAKS_ODLEGLOSC_PANELU = 18

local function uruchom(wybor, opcje)
	Wybor.zamknij()
	task.spawn(Odtwarzacz.uruchom, kontener, wybor, opcje)
end

local function deska(): BasePart?
	local a = kontener:FindFirstChild("Arena")
	local t = a and a:FindFirstChild("Tablica")
	return t and t:FindFirstChild("Deska") :: BasePart?
end

local function przyTablicy(): boolean
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart") :: BasePart?
	local d = deska()
	return hrp ~= nil and d ~= nil and (hrp.Position - d.Position).Magnitude <= MAKS_ODLEGLOSC_PANELU
end

local otworzPanel

-- odmowa serwera po WALCZ / JESZCZE RAZ: krótki komunikat z powodem (zamiast samego zaciemnienia i powrotu).
-- Przy tablicy wraca panel wyboru z napisem w polu Status; dalej od tablicy — dymek na środku ekranu na 3,5 s.
local KOMUNIKATY_ODMOWY = {
	za_daleko = "Za daleko od tablicy — podejdź bliżej i spróbuj jeszcze raz.",
	walka_trwa = "Poprzednia walka jeszcze trwa — spróbuj za chwilę.",
	walka_trwa_lokalnie = "Poprzednia walka jeszcze trwa — spróbuj za chwilę.",
	za_szybko = "Za szybko — spróbuj za chwilę.",
	zly_wybor = "Serwer nie przyjął tego wyboru — wybierz jeszcze raz.",
	brak_postaci = "Poczekaj, aż pojawi się twoja postać.",
}
local function pokazOdmowe(powod: string)
	local tekst = KOMUNIKATY_ODMOWY[powod] or "Serwer nie rozpoczął walki — spróbuj jeszcze raz."
	kontener:SetAttribute("OstatniKomunikat", tekst)
	if przyTablicy() and otworzPanel then
		otworzPanel()
		local panel = Wybor.otwarty()
		if panel then
			panel:komunikat(tekst)
			return
		end
	end
	local playerGui = gracz:FindFirstChildOfClass("PlayerGui")
	if not playerGui then
		return
	end
	local stary = playerGui:FindFirstChild("TestWalki2Komunikat")
	if stary then
		stary:Destroy()
	end
	local gui = Instance.new("ScreenGui")
	gui.Name = "TestWalki2Komunikat"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 102
	local dymek = Instance.new("TextLabel")
	dymek.Name = "Dymek"
	dymek.AnchorPoint = Vector2.new(0.5, 0.5)
	dymek.Position = UDim2.fromScale(0.5, 0.3)
	dymek.Size = UDim2.fromScale(0.7, 0.1)
	dymek.BackgroundColor3 = Ustawienia.KOLORY.krem
	dymek.TextColor3 = Ustawienia.KOLORY.tusz
	dymek.Font = Enum.Font.Bangers
	dymek.TextScaled = true
	dymek.Text = tekst
	dymek.Rotation = -1.5
	local rog = Instance.new("UICorner")
	rog.CornerRadius = UDim.new(0.25, 0)
	rog.Parent = dymek
	local obrys = Instance.new("UIStroke")
	obrys.Thickness = 3
	obrys.Color = Ustawienia.KOLORY.tusz
	obrys.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	obrys.Parent = dymek
	local wciecie = Instance.new("UIPadding")
	wciecie.PaddingLeft = UDim.new(0.04, 0)
	wciecie.PaddingRight = UDim.new(0.04, 0)
	wciecie.PaddingTop = UDim.new(0.12, 0)
	wciecie.PaddingBottom = UDim.new(0.12, 0)
	wciecie.Parent = dymek
	dymek.Parent = gui
	gui.Parent = playerGui
	task.delay(3.5, function()
		gui:Destroy()
	end)
end
Odtwarzacz.naOdmowe = pokazOdmowe

function otworzPanel()
	if Odtwarzacz.czyTrwa() then
		return
	end
	local panel = Wybor.pokaz(gracz:WaitForChild("PlayerGui"), {
		naWalcz = function(wybor)
			uruchom(wybor, nil)
		end,
		wolnaZa = Odtwarzacz.wolnaZa,
	})
	-- panel znika, gdy gracz odejdzie od tablicy
	task.spawn(function()
		while Wybor.otwarty() == panel do
			local postac = gracz.Character
			local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
			local d = deska()
			if not hrp or not d or (hrp.Position - d.Position).Magnitude > MAKS_ODLEGLOSC_PANELU then
				panel:zamknij()
				break
			end
			task.wait(0.3)
		end
	end)
	kontener:SetAttribute("PanelOtwarty", true)
end

ProximityPromptService.PromptTriggered:Connect(function(podpowiedz: ProximityPrompt, kto: Player)
	if kto ~= gracz then
		return
	end
	if podpowiedz.Name == "PodpowiedzWalki2" and podpowiedz:IsDescendantOf(kontener) then
		otworzPanel()
	end
end)

task.spawn(function()
	while kontener.Parent do
		local p = kontener:FindFirstChild("PodpowiedzWalki2", true)
		if p and p:IsA("ProximityPrompt") then
			local zostalo = Odtwarzacz.wolnaZa()
			local tekst = if zostalo > 0 then string.format("Wybierz walkę (za %d s)", math.ceil(zostalo)) else "Wybierz walkę"
			if p.ActionText ~= tekst then
				p.ActionText = tekst
			end
		end
		task.wait(0.25)
	end
end)

------------------------------------------------------------------ haczyk z etapu 1: pokaz aktora
local pokazane = {}
local scena: Folder? = nil
local function sprzataj()
	for _, a in pokazane do
		a:zniszcz()
	end
	table.clear(pokazane)
	if scena then
		scena:Destroy()
		scena = nil
	end
end
sygnaly:WaitForChild("PokazAktora").Event:Connect(function(klucz: string?, akcja: string?, opcje: any?)
	if not klucz then
		sprzataj()
		return
	end
	if not scena then
		local f = Instance.new("Folder")
		f.Name = "PokazLokalny"
		f.Parent = kontener
		scena = f
	end
	opcje = opcje or {}
	local cf = opcje.cf or (Ustawienia.scena() * CFrame.lookAt(Vector3.zero, Vector3.new(0, 0, 1)))
	local a = Aktorzy.nowy(klucz, cf, { rodzic = scena, obrys = opcje.obrys })
	table.insert(pokazane, a)
	if akcja and akcja ~= "spoczynek" then
		a:graj(akcja, { potem = a:maKlip("spoczynek") })
	end
end)

------------------------------------------------------------------ haczyk testowy: sterowanie odtwarzaczem
local sterowanie = sygnaly:WaitForChild("Sterowanie") :: BindableFunction
sterowanie.OnInvoke = function(polecenie: string, a: any, b: any)
	if polecenie == "start" then
		uruchom(a, b)
		return true
	elseif polecenie == "pomin" then
		Odtwarzacz.pomin()
	elseif polecenie == "zamknij" then
		Odtwarzacz.zamknij()
	elseif polecenie == "jeszczeRaz" then
		Odtwarzacz.jeszczeRaz()
	elseif polecenie == "tempo" then
		Odtwarzacz.ustawTempo(a)
	elseif polecenie == "przewin" then
		Odtwarzacz.przewin(a)
		return Odtwarzacz.stan()
	elseif polecenie == "przewinDo" then
		Odtwarzacz.przewinDo(a)
		return Odtwarzacz.stan()
	elseif polecenie == "stan" then
		return Odtwarzacz.stan()
	elseif polecenie == "kadr" then
		return Odtwarzacz.kadr()
	elseif polecenie == "napisy" then
		return Odtwarzacz.napisy()
	elseif polecenie == "wybor" then
		otworzPanel()
	end
	return true
end

kontener:SetAttribute("KlientGotowy", true)
