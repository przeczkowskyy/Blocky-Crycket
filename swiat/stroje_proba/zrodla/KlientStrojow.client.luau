--[[
	KlientStrojow — kliencka połowa przymierzalni (próba D-071, swiat/stroje_proba). Script, RunContext = Client,
	w kontenerze Workspace/StrojeProba.

	• Podgląd: na podeście stojaka (Przymierzalnia/Podest) stoi LOKALNY bohater wybranej klasy w stroju gracza —
	  budowany tym samym kodem co aktor walki (Workspace/TestWalki2/Moduly/Aktorzy.nowy → Ubieranie), więc gra te
	  same klipy; bez próby walki w miejscu — model bez ruchu z własnego szkieletu (Ubieranie.zbuduj). Odświeża się,
	  gdy serwer zmieni atrybut stroju gracza.
	• Punkt E (ProximityPrompt z atrybutem Akcja = "przymierzalnia") otwiera TYMCZASOWE okno (OknoStrojow): zakładki
	  klas, po jednym przedmiocie na slot (< >), zestawy, dawny wygląd, ruch podglądu. Okno tylko PROSI serwer
	  (Zdalne/ZmienStroj) — o stroju decyduje SerwerStrojow. Kamera na podgląd, postać gracza schowana i bez ruchu
	  do zamknięcia okna (X albo odejście dalej niż D.stojak.zasieg_okna).
	• Haczyk testowy Sygnaly/SterowanieKlienta (BindableFunction): "stan" | "otworz" | "zamknij" | "klasa", k |
	  "graj", akcja | "zmien", akcja, klasa, arg (przez serwer, jak okno) | "pomiar" (najniższy punkt podglądu nad
	  podestem — całość, ciało, każda grupa — i największe odejście bryły od miejsca na kości) | "przebieg", akcja
	  (klip klatka po klatce z pomiarem w każdej: najniżej, odejście, pomiar ostatniej klatki).
	Atrybuty kontenera (tylko u tego klienta): KlientGotowy, OknoOtwarte, PodgladKlasa, PodgladStroj, PodgladBryly,
	PodgladZRuchem, OstatniKomunikat.
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ContextActionService = game:GetService("ContextActionService")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneStrojow"))
local L = require(moduly:WaitForChild("LogikaStrojow"))
local Ubieranie = require(moduly:WaitForChild("Ubieranie"))
local Okno = require(moduly:WaitForChild("OknoStrojow"))
local zmien = kontener:WaitForChild("Zdalne"):WaitForChild("ZmienStroj")
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieKlienta")
-- 26.11.2026 (sprzątanie mapy): przymierzalni przy starym starcie już nie ma (D.stojak.w_grze = false) — wtedy klient
-- nie buduje podglądu i nie otwiera okna, tylko odpowiada haczykowi testowemu; strój gracza dalej zmienia serwer
-- (Zdalne/ZmienStroj) i widać go w walce
local stojak = if D.stojak.w_grze == false then kontener:FindFirstChild("Przymierzalnia") else kontener:WaitForChild("Przymierzalnia")
local podest = stojak and stojak:WaitForChild("Podest")
local gracz = Players.LocalPlayer
local T = D.teksty

local stan = {
	klasa = D.kolejnoscKlas[1],
	aktor = nil,
	model = nil,
	okno = nil,
	ruch = 1,
	wersja = 0,
	pokaz = 0,
	kamera = nil,
}

------------------------------------------------------------------ aktorzy próby walki (opcjonalnie)
local Aktorzy = nil
local function aktorzyWalki()
	if Aktorzy then
		return Aktorzy
	end
	local tw = workspace:FindFirstChild("TestWalki2")
	local m = tw and tw:GetAttribute("Wygenerowane") == true and tw:FindFirstChild("Moduly")
	m = m and m:FindFirstChild("Aktorzy")
	if not m or not m:IsA("ModuleScript") then
		return nil
	end
	local ok, A = pcall(require, m)
	if ok and type(A) == "table" and type(A.nowy) == "function" then
		Aktorzy = A
	end
	return Aktorzy
end

-- akcje podglądu: wspólne z danych + umiejętności klasy z tabeli aktorów walki (te, które mają klip)
local function ruchy(klasa)
	local lista = {}
	local A = aktorzyWalki()
	for _, a in D.klipyPodgladu do
		if not A or A.klip(klasa, a) then
			table.insert(lista, a)
		end
	end
	local w = A and A.wpis(klasa)
	if w and w.umiejetnosci then
		local u = {}
		for nazwa, klip in w.umiejetnosci do
			if type(klip) == "string" then
				table.insert(u, nazwa)
			end
		end
		table.sort(u)
		for _, nazwa in u do
			table.insert(lista, nazwa)
		end
	end
	return lista
end

------------------------------------------------------------------ podgląd na podeście
local function cfPodgladu()
	return podest.CFrame * CFrame.new(0, podest.Size.Y / 2, 0)
end

local function folderPodgladu()
	local f = kontener:FindFirstChild("PodgladLokalny")
	if not f then
		f = Instance.new("Folder")
		f.Name = "PodgladLokalny"
		f.Parent = kontener
	end
	return f
end

-- widoczna bryła postaci (bez korzenia, kości, obrysu-skorupy i znaczników punktów)
local function bryla(d)
	return d:IsA("BasePart") and d.Transparency < 1 and d.Name ~= "HumanoidRootPart" and d:GetAttribute("Obrys") == nil
		and d:GetAttribute("Punkt") == nil
end

local function widoczne(model)
	local n = 0
	for _, d in model:GetDescendants() do
		if bryla(d) then
			n += 1
		end
	end
	return n
end

local function usunPodglad()
	if stan.aktor then
		pcall(function()
			stan.aktor:zniszcz()
		end)
	elseif stan.model then
		stan.model:Destroy()
	end
	stan.aktor, stan.model = nil, nil
end

-- szablon walki z korzeniem i wszystkimi kośćmi (miejsce ma strumieniowanie: szablony stoją daleko od stojaka i
-- tuż po starcie klienta mogą jeszcze nie dojść)
local function szablonGotowy(klasa)
	local tw = workspace:FindFirstChild("TestWalki2")
	local f = tw and tw:FindFirstChild("Aktorzy")
	local m = f and f:WaitForChild(klasa, 5)
	if not m or not m:WaitForChild("HumanoidRootPart", 5) then
		return false
	end
	for _, k in D.klasy[klasa].kosci do
		if not m:WaitForChild(k[1], 2) then
			return false
		end
	end
	return true
end

local function zbudujPodglad()
	if not podest then
		return -- bez przymierzalni nie ma podglądu (26.11.2026)
	end
	stan.wersja += 1
	local moja = stan.wersja
	stan.pokaz += 1
	local klasa = stan.klasa
	local A = aktorzyWalki()
	local gotowy = A ~= nil and szablonGotowy(klasa)
	if moja ~= stan.wersja then
		return -- w międzyczasie ruszyła nowsza budowa
	end
	usunPodglad()
	local ids = Ubieranie.strojGracza(gracz, klasa)
	local cf = cfPodgladu()
	local folder = folderPodgladu()
	if A and gotowy then
		local ok, a = pcall(A.nowy, klasa, cf, { rodzic = folder, stroj = if ids == nil then false else ids })
		if ok then
			stan.aktor, stan.model = a, a.model
		else
			warn("[StrojeProba] podgląd z próby walki nie powstał: " .. tostring(a))
		end
	end
	if not stan.model then
		local ok, plan = L.plan(D, klasa, ids or D.klasy[klasa].odniesienie)
		if ok then
			local m = Ubieranie.zbuduj(klasa, plan, nil)
			m.Name = klasa .. "_podglad"
			m:PivotTo(cf)
			m.Parent = folder
			stan.model = m
		end
	end
	if stan.model then
		stan.model:SetAttribute("Podglad", klasa)
		kontener:SetAttribute("PodgladKlasa", klasa)
		kontener:SetAttribute("PodgladStroj", stan.model:GetAttribute("Stroj") or "dawny")
		kontener:SetAttribute("PodgladBryly", widoczne(stan.model))
		kontener:SetAttribute("PodgladZRuchem", stan.aktor ~= nil)
	end
end

local function graj(akcja)
	local a = stan.aktor
	if not a then
		return nil
	end
	local tor = a:graj(akcja, { przejscie = 0.12, potem = a:maKlip("spoczynek") })
	return if tor then tor.dlugosc else nil
end

local function grajWszystkie()
	stan.pokaz += 1
	local moj = stan.pokaz
	task.spawn(function()
		for _, akcja in ruchy(stan.klasa) do
			if stan.pokaz ~= moj or not stan.aktor then
				return
			end
			local dl = graj(akcja)
			if dl then
				task.wait(dl + 0.35)
			end
		end
	end)
end

------------------------------------------------------------------ kamera, postać gracza, sterowanie
local function kadr()
	local K = D.klasy[stan.klasa]
	local C = D.kamera
	local cf = cfPodgladu()
	local h = K.wysokosc
	local d = math.max(C.odleglosc_min, h * C.odleglosc_na_wzrost)
	local bok = C.bok * d
	local oko = (cf * CFrame.new(bok, h * C.wysokosc_oka, -d)).Position
	local srodek = (cf * CFrame.new(bok, h * 0.5, 0)).Position
	-- środek postaci na wysokości C.srodek_ekranu (ułamek od góry): oś kamery pochylona o kąt alfa poniżej kierunku
	-- na środek postaci (tan alfa = przesunięcie od środka ekranu · 2 · tan(pół kąta widzenia))
	local alfa = math.atan((0.5 - C.srodek_ekranu) * 2 * math.tan(math.rad(C.fov / 2)))
	local doSrodka = srodek - oko
	local poziom = Vector3.new(doSrodka.X, 0, doSrodka.Z)
	local pochylenie = math.atan2(doSrodka.Y, poziom.Magnitude) - alfa
	local kier = poziom.Unit * math.cos(pochylenie) + Vector3.yAxis * math.sin(pochylenie)
	return CFrame.lookAt(oko, oko + kier)
end

local function ukryjPostac(x)
	local postac = gracz.Character
	if not postac then
		return
	end
	for _, d in postac:GetDescendants() do
		if d:IsA("BasePart") or d:IsA("Decal") then
			d.LocalTransparencyModifier = x
		end
	end
end

local function blokada(_nazwa, _stan, _wejscie)
	return Enum.ContextActionResult.Sink
end

local odswiezOkno

local function zamknij()
	if not stan.okno then
		return
	end
	stan.okno:zniszcz()
	stan.okno = nil
	ContextActionService:UnbindAction("StrojeProbaBlokada")
	RunService:UnbindFromRenderStep("StrojeProbaKamera")
	local kam = workspace.CurrentCamera
	if stan.kamera then
		kam.CameraType = stan.kamera.typ
		kam.FieldOfView = stan.kamera.fov
		stan.kamera = nil
	end
	ukryjPostac(0)
	kontener:SetAttribute("OknoOtwarte", false)
end

local function komunikat(tekst, blad)
	kontener:SetAttribute("OstatniKomunikat", tekst)
	if stan.okno then
		stan.okno:komunikat(tekst, blad)
	end
end

local function prosba(akcja, klasa, arg)
	local ok, w = pcall(function()
		return zmien:InvokeServer(akcja, klasa, arg)
	end)
	if not ok or type(w) ~= "table" then
		w = { ok = false, powod = "blad" }
	end
	if w.ok then
		komunikat(if akcja == "dawny" then T.dawny_ok else T.zmiana_ok, false)
	else
		komunikat(if w.powod == "za_szybko" then T.za_szybko else T.odmowa, true)
	end
	return w
end

local function ustawKlase(k)
	if D.klasy[k] == nil then
		return
	end
	stan.klasa = k
	stan.ruch = 1
	zbudujPodglad()
	if stan.okno then
		stan.kadr = kadr()
		workspace.CurrentCamera.CFrame = stan.kadr
		odswiezOkno()
	end
end

-- 18.11.2026 (swiat/kowal_proba, D-102): przy działającym kowalu na próbę (kontener KowalProba i atrybut gracza
-- KowalDostepne od jego serwera) okno pokazuje tylko posiadane przedmioty i chowa „Dawny wygląd” (serwer i tak
-- sprawdza to samo); bez kowala — pełna oferta jak dawniej
local function ofertaGracza(klasa)
	local oferta = L.oferta(D, klasa)
	local v = gracz:GetAttribute("KowalDostepne")
	if not workspace:FindFirstChild("KowalProba") or type(v) ~= "string" then
		return oferta, false
	end
	local zb = {}
	for _, id in L.zNapisu(v) or {} do
		zb[id] = true
	end
	local w = {}
	for _, s in oferta do
		local ids = {}
		for _, id in s.przedmioty do
			if zb[id] then
				table.insert(ids, id)
			end
		end
		if #ids > 0 then
			table.insert(w, { slot = s.slot, nazwa = s.nazwa, przedmioty = ids })
		end
	end
	return w, true
end

function odswiezOkno()
	if not stan.okno then
		return
	end
	local lista = ruchy(stan.klasa)
	stan.ruch = math.clamp(stan.ruch, 1, math.max(1, #lista))
	local oferta, tylkoPosiadane = ofertaGracza(stan.klasa)
	stan.okno:pokaz({ klasa = stan.klasa, oferta = oferta, stroj = Ubieranie.strojGracza(gracz, stan.klasa),
		ruch = lista[stan.ruch] and (D.nazwyRuchow[lista[stan.ruch]] or lista[stan.ruch]), bezDawnego = tylkoPosiadane })
end

-- klasa gracza z atrybutu Class (ekran wyboru Pawła; ta sama mapa co swiat/stan_gracza i Stale lasu) albo nil
local KLASY_GRACZA = { Warrior = "wojownik", Scout = "zwiadowca", Mage = "mag" }
local function klasaGracza()
	local id = gracz:GetAttribute("Class")
	local k = type(id) == "string" and KLASY_GRACZA[id] or nil
	return if k and D.klasy[k] ~= nil then k else nil
end

local function otworz()
	if stan.okno or not podest then
		return
	end
	-- 17.11.2026: okno otwiera się na klasie gracza (u Maga — zakładka Maga); bez klasy — jak dawniej
	local mojaKlasa = klasaGracza()
	if mojaKlasa and mojaKlasa ~= stan.klasa then
		stan.klasa = mojaKlasa
		stan.ruch = 1
		zbudujPodglad()
	end
	local emulacja = kontener:GetAttribute("EmulacjaEkranu")
	stan.okno = Okno.nowe(gracz:WaitForChild("PlayerGui"), D, {
		emulacja = emulacja,
		naKlase = ustawKlase,
		naWybor = function(slot, id)
			if id then
				prosba("zaloz", stan.klasa, id)
			else
				prosba("zdejmij", stan.klasa, slot)
			end
		end,
		naZestaw = function(nazwa)
			prosba("zestaw", stan.klasa, nazwa)
		end,
		naDawny = function()
			prosba("dawny", stan.klasa)
		end,
		naRuch = function(krok)
			local lista = ruchy(stan.klasa)
			if #lista > 0 then
				stan.ruch = ((stan.ruch - 1 + krok) % #lista) + 1
				odswiezOkno()
			end
		end,
		naZagraj = function()
			local lista = ruchy(stan.klasa)
			if lista[stan.ruch] then
				stan.pokaz += 1
				graj(lista[stan.ruch])
			end
		end,
		naWszystkie = grajWszystkie,
		naZamknij = zamknij,
	})
	local kam = workspace.CurrentCamera
	stan.kamera = { typ = kam.CameraType, fov = kam.FieldOfView }
	kam.CameraType = Enum.CameraType.Scriptable
	kam.FieldOfView = D.kamera.fov
	stan.kadr = kadr()
	kam.CFrame = stan.kadr
	-- kamera trzymana co klatkę (po module kamery Roblox): inne skrypty nie przestawią kadru, póki okno jest otwarte
	RunService:BindToRenderStep("StrojeProbaKamera", Enum.RenderPriority.Camera.Value + 2, function()
		local c = workspace.CurrentCamera
		if stan.okno and stan.kadr then
			c.CameraType = Enum.CameraType.Scriptable
			c.FieldOfView = D.kamera.fov
			c.CFrame = stan.kadr
		end
	end)
	ukryjPostac(1)
	ContextActionService:BindActionAtPriority("StrojeProbaBlokada", blokada, false,
		Enum.ContextActionPriority.High.Value, Enum.PlayerActions.CharacterForward, Enum.PlayerActions.CharacterBackward,
		Enum.PlayerActions.CharacterLeft, Enum.PlayerActions.CharacterRight, Enum.PlayerActions.CharacterJump)
	kontener:SetAttribute("OknoOtwarte", true)
	if not aktorzyWalki() then
		komunikat(T.brak_walki, true)
	end
	odswiezOkno()
	task.spawn(function()
		while stan.okno do
			local postac = gracz.Character
			local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
			if not hrp or (hrp.Position - podest.Position).Magnitude > D.stojak.zasieg_okna then
				zamknij()
				break
			end
			ukryjPostac(1)
			task.wait(0.3)
		end
	end)
end

ProximityPromptService.PromptTriggered:Connect(function(podpowiedz, kto)
	if kto == gracz and podpowiedz:GetAttribute("Akcja") == "przymierzalnia" and podpowiedz:IsDescendantOf(kontener) then
		otworz()
	end
end)

-- serwer zmienił strój → podgląd i okno od nowa
for _, k in D.kolejnoscKlas do
	gracz:GetAttributeChangedSignal(Ubieranie.atrybut(k)):Connect(function()
		if k == stan.klasa then
			zbudujPodglad()
			odswiezOkno()
		end
	end)
end

------------------------------------------------------------------ haczyk testowy
local ROGI = { Vector3.new(1, 1, 1), Vector3.new(1, 1, -1), Vector3.new(1, -1, 1), Vector3.new(1, -1, -1),
	Vector3.new(-1, 1, 1), Vector3.new(-1, 1, -1), Vector3.new(-1, -1, 1), Vector3.new(-1, -1, -1) }

-- najniższy punkt brył nad podestem (całość, ciało = bryły na kościach, i każda grupa: broń, kapelusz, włosy…)
-- i największe odejście bryły od miejsca na kości (Weld: Part0.CFrame * C0 ≠ położenie bryły = coś odpadło)
local function pomiar()
	local m = stan.model
	if not m then
		return { ok = false }
	end
	local ziemia = cfPodgladu().Position.Y
	local najnizej, cialo, odchylenie, n = math.huge, math.huge, 0, 0
	local grupy = {}
	for _, d in m:GetDescendants() do
		if bryla(d) then
			n += 1
			local h = d.Size / 2
			local y = math.huge
			for _, s in ROGI do
				y = math.min(y, (d.CFrame * (h * s)).Y - ziemia)
			end
			najnizej = math.min(najnizej, y)
			local g = d.Parent
			if g and g:IsA("Model") and g ~= m then
				grupy[g.Name] = math.min(grupy[g.Name] or math.huge, y)
			else
				cialo = math.min(cialo, y)
			end
			local w = d:FindFirstChild("SpawStroju")
			if w and w:IsA("Weld") and w.Part0 then
				odchylenie = math.max(odchylenie, ((w.Part0.CFrame * w.C0).Position - d.Position).Magnitude)
			end
		end
	end
	return { ok = true, najnizej = najnizej, cialo = cialo, grupy = grupy, odchylenie = odchylenie, bryly = n }
end

-- klip akcji klatka po klatce (30 kl./s czasu klipu, każda klatka po jednym kroku silnika): pomiar w każdej
local function przebieg(akcja)
	local a = stan.aktor
	if not a then
		return { ok = false, powod = "bez_ruchu" }
	end
	local nazwa = a:maKlip(akcja)
	if not nazwa then
		return { ok = false, powod = "brak_klipu" }
	end
	stan.pokaz += 1
	local dl = a.klipy:dlugoscKlipu(nazwa) or 0
	local kroki = math.max(1, math.floor(dl * 30 + 0.5))
	local w = { ok = true, akcja = akcja, klip = nazwa, klatki = kroki + 1, najnizej = math.huge, odchylenie = 0 }
	for i = 0, kroki do
		a.klipy:poza(nazwa, dl * i / kroki)
		RunService.Heartbeat:Wait()
		local p = pomiar()
		w.najnizej = math.min(w.najnizej, p.najnizej)
		w.odchylenie = math.max(w.odchylenie, p.odchylenie)
		if i == kroki then
			w.koniec = p
		end
	end
	a:spoczynek(0)
	return w
end

sterowanie.OnInvoke = function(polecenie, a, b, c)
	if polecenie == "stan" then
		return { okno = stan.okno ~= nil, klasa = stan.klasa, stroj = Ubieranie.strojGracza(gracz, stan.klasa),
			model = stan.model and stan.model.Name, strojModelu = stan.model and stan.model:GetAttribute("Stroj"),
			bryly = stan.model and widoczne(stan.model) or 0, zRuchem = stan.aktor ~= nil, ruchy = ruchy(stan.klasa),
			skrot = D.skrot, stojak = podest ~= nil }
	elseif polecenie == "otworz" then
		otworz()
	elseif polecenie == "zamknij" then
		zamknij()
	elseif polecenie == "klasa" then
		ustawKlase(a)
	elseif polecenie == "graj" then
		stan.pokaz += 1
		return graj(a)
	elseif polecenie == "zmien" then
		return prosba(a, b, c)
	elseif polecenie == "pomiar" then
		return pomiar()
	elseif polecenie == "przebieg" then
		return przebieg(a)
	elseif polecenie == "kadr" then
		-- gdzie na ekranie jest podgląd (ułamki ekranu) i góra okna; najmniejszy tekst okna (punkty)
		local m, kam = stan.model, workspace.CurrentCamera
		if not m then
			return { ok = false }
		end
		local cf, rozmiar = m:GetBoundingBox()
		local x0, y0, x1, y1 = math.huge, math.huge, -math.huge, -math.huge
		for _, s in ROGI do
			local p = kam:WorldToViewportPoint((cf * CFrame.new(rozmiar / 2 * s)).Position)
			x0, x1, y0, y1 = math.min(x0, p.X), math.max(x1, p.X), math.min(y0, p.Y), math.max(y1, p.Y)
		end
		local vp = kam.ViewportSize
		local o = stan.okno and stan.okno.okno
		return { ok = true, x0 = x0 / vp.X, x1 = x1 / vp.X, y0 = y0 / vp.Y, y1 = y1 / vp.Y,
			oknoGora = o and o.AbsolutePosition.Y / vp.Y, oknoLewo = o and o.AbsolutePosition.X / vp.X,
			oknoPrawo = o and (o.AbsolutePosition.X + o.AbsoluteSize.X) / vp.X, tekst = stan.okno and stan.okno.rozmiarTekstu,
			kamera = { kam.CFrame.Position.X, kam.CFrame.Position.Y, kam.CFrame.Position.Z },
			patrz = { (kam.CFrame.Position + kam.CFrame.LookVector * 10).X, (kam.CFrame.Position + kam.CFrame.LookVector * 10).Y,
				(kam.CFrame.Position + kam.CFrame.LookVector * 10).Z }, fov = kam.FieldOfView, ekran = { vp.X, vp.Y } }
	end
	return true
end

task.spawn(function()
	zbudujPodglad()
	kontener:SetAttribute("KlientGotowy", true)
	-- bez szablonu walki podgląd stoi bez ruchu: jeszcze jedna próba, gdy szablony dojdą
	for _ = 1, 3 do
		if stan.aktor or not workspace:FindFirstChild("TestWalki2") then
			break
		end
		task.wait(5)
		zbudujPodglad()
	end
end)
