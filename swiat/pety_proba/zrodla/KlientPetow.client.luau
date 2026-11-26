--[[
	KlientPetow — kliencka połowa „jajek i petów na próbę” (Script, RunContext = Client, w kontenerze
	Workspace/PetyProba). Niczego nie losuje i nie podaje cen (D-016): zakup i wybór peta decyduje SerwerPetow.

	Co robi (wszystko u tego gracza; obiekty w świecie tylko lokalne, w folderze PetyLokalne kontenera):
		1. Inkubatory (jeden na jajko z D.jajka — las-pas, Bagno): jajko z serwera (widać je w Edit) chowa u siebie
		   i stawia lokalną, animowaną kopię (kołysanie); napis z ceną dla tego gracza (atrybut jajko.atrybuty.cena)
		   i tekst podpowiedzi E „Kup za N Złota”.
		2. "wyklucie" od serwera → jajko tego inkubatora trzęsie się, pęka (kolor rzadkości w środku, błysk, iskry,
		   dźwięk), pet wyskakuje i ląduje przed gniazdem, radość, napis NOWY PET! / KOPIA +1 z nazwą, rzadkością i skillem.
		   Reset postaci w trakcie nie przerywa animacji (pet jest już u gracza — zdecydował serwer).
		3. Pet przy graczu: dla KAŻDEGO gracza z atrybutem aktywnego peta (pisze go StanGracza) lokalny model idzie
		   za nim płynnie (wygładzanie, grunt z promienia w dół, bez kolizji), chód / spoczynek / radość przy skoku.
		   Znika w walce, przelocie, chmurach, mini-grze i przy wyborze klasy: u siebie od razu (wtedy też wszystkie
		   cudze — nie wchodzą w kadr walki), a innym przez "czekaj" do serwera (atrybut gracza).
		4. Zagroda w bazarze: pety STOJĄCE w zagrodzie (lista od serwera — wybór gracza albo najrzadsze, tyle, ile miejsc
		   ma poziom zagrody; 25.11.2026) na miejscach z mapy (tyle, ile znaczników zagroda_miejsce_N — dziś 6 albo 8;
		   pety ponad liczbę znaczników dają Rybki bez modelu), lokalnie, tylko u tego gracza; napis „+N Rybek” nad
		   zagrodą, gdy serwer dopisze Rybki (tylko gdy gracz jest blisko); w oknie wiersz zagrody (miejsca, Rybki na
		   minutę, „Więcej miejsc” za Rybki, „Najrzadsze”) i przy każdym pecie „Do zagrody” / „Z zagrody”;
		   tablica „TWOJE PETY · PRÓBA” w dwóch kolumnach (jajko po jajku) z liczbą kopii (= shardy peta, D-058), okno
		   wyboru aktywnego peta „PRÓBA” (przewijane, podzielone na jajka) — otwiera je E opiekunki
		   (ReplicatedStorage.OknoMiejsca, id zagrody — pakiet swiat/miasteczko_bazar_gra) albo zapasowe E tablicy.
		5. Premia peta przy łupie: komunikat "premia" od StanGracza → krótki napis „+N Złota od peta: …”.
	Haczyk testowy: Sygnaly/SterowanieKlienta ("stan" | "okno" | "zamknij" | "wybierz", id | "do_zagrody", id
	| "z_zagrody", id | "ulepsz" | "najrzadsze" (jak przyciski okna, 25.11.2026) | "wyklucie", pet, nowy,
	jajko? | "pokaz", pet, Vector3 | "pokaz_usun").
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DanePetow"))
local L = require(moduly:WaitForChild("LogikaPetow"))
local Rig = require(moduly:WaitForChild("RigPetow"))
local folderRigow = moduly:WaitForChild("Rigi")
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaPetow")
local sterowanie: BindableFunction = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieKlienta")
local ekrany = gracz:WaitForChild("PlayerGui")

local T = D.teksty
local PP = D.pet_przy_graczu
local S = D.stan_gracza
local AG = D.atrybuty_gracza
local U = D.ukrycie
local W = D.wyklucie
local CZCIONKA = Enum.Font.GothamBold
local CZCIONKA_TYTULU = Enum.Font.LuckiestGuy

local function kolor(h: string): Color3
	return Color3.fromHex(h)
end

local function v3(t): Vector3
	return Vector3.new(t[1], t[2], t[3])
end

------------------------------------------------------------------ dane rigów (moduły Moduly/Rigi/*)
local daneRigow = {}
local function daneRigu(nazwa: string)
	if daneRigow[nazwa] == nil then
		local m = folderRigow:WaitForChild(nazwa, 10)
		local ok, w = false, nil
		if m and m:IsA("ModuleScript") then
			ok, w = pcall(require, m)
		end
		daneRigow[nazwa] = if ok and type(w) == "table" and w.kosci then w else false
		if not daneRigow[nazwa] then
			warn(D.prefiks .. "brak danych rigu " .. nazwa)
		end
	end
	return daneRigow[nazwa] or nil
end

local function danePeta(id: any)
	if type(id) ~= "string" or not D.rigi[id] then
		return nil
	end
	return daneRigu(D.rigi[id])
end

local function skalaPeta(id: string): number
	local p = L.pet(D, id)
	return if p then p.skala else 1
end

local function rzadkoscPeta(id: string)
	local p = L.pet(D, id)
	local r = p and L.rzadkosc(D, p.rzadkosc)
	local nr = 1
	for i, x in D.rzadkosci do
		if r and x.id == r.id then
			nr = i
		end
	end
	return r, nr
end

-- lokalne modele (tylko u tego gracza)
local lokalne = Instance.new("Folder")
lokalne.Name = "PetyLokalne"
lokalne.Parent = kontener

local animowane = {}

------------------------------------------------------------------ dźwięk (wbudowany ton, jak w KlientStanu)
local function dzwiek(nuty, glosnosc: number?)
	task.spawn(function()
		for _, n in nuty do
			local s = Instance.new("Sound")
			s.Name = "PetyProbaTon"
			s.SoundId = "rbxasset://sounds/volume_slider.ogg"
			s.Volume = glosnosc or 0.5
			s.PlaybackSpeed = n
			s.Parent = SoundService
			s:Play()
			task.delay(1, function()
				s:Destroy()
			end)
			task.wait(0.09)
		end
	end)
end

------------------------------------------------------------------ ekran: komunikaty
local gui = Instance.new("ScreenGui")
gui.Name = "PetyProba"
gui.ResetOnSpawn = false
gui.DisplayOrder = 25
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
gui.Parent = ekrany

local pasekKom = Instance.new("TextLabel")
pasekKom.Name = "Komunikat"
pasekKom.AnchorPoint = Vector2.new(0.5, 1)
pasekKom.Position = UDim2.new(0.5, 0, 1, -150)
pasekKom.Size = UDim2.fromOffset(0, 44)
pasekKom.AutomaticSize = Enum.AutomaticSize.X
pasekKom.BackgroundColor3 = kolor("1D1916")
pasekKom.BackgroundTransparency = 0.15
pasekKom.TextColor3 = kolor("FFF6E0")
pasekKom.Font = CZCIONKA
pasekKom.TextSize = 20
pasekKom.Text = ""
pasekKom.Visible = false
pasekKom.Parent = gui
do
	local r = Instance.new("UICorner")
	r.CornerRadius = UDim.new(0.5, 0)
	r.Parent = pasekKom
	local o = Instance.new("UIStroke")
	o.Color = kolor("FFC94A")
	o.Thickness = 2
	o.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	o.Parent = pasekKom
	local w = Instance.new("UIPadding")
	w.PaddingLeft = UDim.new(0, 18)
	w.PaddingRight = UDim.new(0, 18)
	w.Parent = pasekKom
end
local numerKom = 0
local function komunikat(tekst: string, kol: Color3?, czas: number?)
	numerKom += 1
	local moj = numerKom
	pasekKom.Text = tekst
	pasekKom.TextColor3 = kol or kolor("FFF6E0")
	pasekKom.Visible = true
	task.delay(czas or 3, function()
		if numerKom == moj then
			pasekKom.Visible = false
		end
	end)
end

------------------------------------------------------------------ czy coś zajmuje ekran (walka, przelot, chmury, mini-gra)
local function ekranWlaczony(nazwa: string): boolean
	local g = ekrany:FindFirstChild(nazwa)
	return g ~= nil and g:IsA("ScreenGui") and g.Enabled
end

local function ukryteLokalnie(): boolean
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if not hum or hum.Health <= 0 then
		return true
	end
	local hud = ekrany:FindFirstChild(U.hud)
	if (hud and hud:IsA("ScreenGui") and not hud.Enabled) or ekranWlaczony(U.ekran_walki) or ekranWlaczony(U.ekran_klasy) then
		return true
	end
	local kamera = workspace.CurrentCamera
	-- TestKameraProby (atrybut kontenera u klienta, tylko próby w Play): kamera do zrzutów nie chowa petów
	if not kamera or (kamera.CameraType ~= Enum.CameraType.Custom and kontener:GetAttribute("TestKameraProby") ~= true) then
		return true
	end
	if gracz:GetAttribute(U.atrybut_treningu) ~= nil or gracz:GetAttribute(U.atrybut_blokady) == true then
		return true
	end
	local chmury = workspace:FindFirstChild(U.chmury)
	return chmury ~= nil and chmury:GetAttribute(U.chmury_trwa) == true
end

local wyslaneCzekaj, czasCzekaj = nil, 0
local function zglosCzekaj(czeka: boolean)
	if czeka ~= wyslaneCzekaj and os.clock() - czasCzekaj >= PP.odstep_czekaj_s then
		wyslaneCzekaj = czeka
		czasCzekaj = os.clock()
		zdarzenia:FireServer("czekaj", czeka)
	end
end

------------------------------------------------------------------ pet przy graczu (dla każdego gracza, lokalnie)
local towarzysze = {}
local wylegaSie = false
local poWykluciu: CFrame? = nil -- skąd lokalny pet rusza za graczem po wykluciu
local promien = RaycastParams.new()
promien.FilterType = Enum.RaycastFilterType.Exclude
promien.IgnoreWater = false

local function usunTowarzysza(p: Player)
	local t = towarzysze[p]
	if t then
		animowane[t.u] = nil
		t.model:Destroy()
		towarzysze[p] = nil
	end
end

local function ziemia(punkt: Vector3): number?
	local r = workspace:Raycast(punkt + Vector3.new(0, 6, 0), Vector3.new(0, -24, 0), promien)
	return r and r.Position.Y
end

local function kat(a: number, b: number, t: number): number
	local d = (b - a + math.pi) % (2 * math.pi) - math.pi
	return a + d * t
end

local function aktualizujTowarzyszy(dt: number, ukryte: boolean)
	local wyklucz = { lokalne }
	for _, p in Players:GetPlayers() do
		if p.Character then
			table.insert(wyklucz, p.Character)
		end
	end
	promien.FilterDescendantsInstances = wyklucz
	local kamera = workspace.CurrentCamera
	local obecni = {}
	for _, p in Players:GetPlayers() do
		obecni[p] = true
		local petId = p:GetAttribute(S.atrybut_aktywnego)
		local postac = p.Character
		local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
		local hum = postac and postac:FindFirstChildOfClass("Humanoid")
		local dane = danePeta(petId)
		local widac = dane ~= nil and hrp ~= nil and hum ~= nil and hum.Health > 0 and p:GetAttribute(AG.czeka) ~= true
			and not ukryte and not (p == gracz and wylegaSie)
			and (kamera == nil or (kamera.CFrame.Position - hrp.Position).Magnitude < PP.promien_widocznosci)
		local t = towarzysze[p]
		if t and (not widac or t.pet ~= petId) then
			usunTowarzysza(p)
			t = nil
		end
		if widac then
			local cf = hrp.CFrame
			local cel = (cf * CFrame.new(PP.w_bok, 0, PP.w_tyl)).Position
			local y = ziemia(cel) or (hrp.Position.Y - hum.HipHeight - hrp.Size.Y / 2)
			cel = Vector3.new(cel.X, y + (PP.unoszenie[petId] or 0), cel.Z)
			if not t then
				local model, u = Rig.zbuduj(dane, skalaPeta(petId), "Pet " .. petId)
				model.Parent = lokalne
				animowane[u] = true
				Rig.graj(u, "spoczynek")
				local start = cel
				if p == gracz and poWykluciu then
					start = poWykluciu.Position
					poWykluciu = nil
				end
				local lv = cf.LookVector
				t = { pet = petId, model = model, u = u, pos = start, yaw = math.atan2(-lv.X, -lv.Z), wPowietrzu = false }
				towarzysze[p] = t
			end
			if (t.pos - cel).Magnitude > PP.skok_powyzej then
				t.pos = cel
			end
			local nowa = t.pos:Lerp(cel, 1 - math.exp(-PP.wygladzanie * dt))
			local ruch = nowa - t.pos
			local predkosc = Vector3.new(ruch.X, 0, ruch.Z).Magnitude / math.max(dt, 1e-3)
			t.pos = nowa
			local lv = cf.LookVector
			local docelowy = if predkosc > PP.ruch_od then math.atan2(-ruch.X, -ruch.Z) else math.atan2(-lv.X, -lv.Z)
			t.yaw = kat(t.yaw, docelowy, 1 - math.exp(-10 * dt))
			Rig.ustaw(t.u, CFrame.new(t.pos) * CFrame.Angles(0, t.yaw, 0))
			local wPowietrzu = hum.FloorMaterial == Enum.Material.Air
			if wPowietrzu and not t.wPowietrzu and hum:GetState() == Enum.HumanoidStateType.Jumping then
				Rig.graj(t.u, "radosc", 1, "spoczynek")
			end
			t.wPowietrzu = wPowietrzu
			local chce = if predkosc > PP.ruch_od then "chod" else "spoczynek"
			if not (t.u.klip == "radosc" and not t.u.koniec) and t.u.klip ~= chce then
				Rig.graj(t.u, chce)
			end
		end
	end
	for p in towarzysze do
		if not obecni[p] then
			usunTowarzysza(p)
		end
	end
end

------------------------------------------------------------------ inkubatory: lokalne, animowane jajka i napisy z ceną
local jajkaLok = {} -- id jajka → { model, u, podstawa, skala, napis, j }

local function przygotujInkubator(j)
	local folder = kontener:WaitForChild(j.folder, 30)
	if not folder then
		return
	end
	local wzor = folder:FindFirstChild("Jajko")
	local dane = daneRigu(j.rig)
	local podstawa = folder:GetAttribute("PodstawaJajka")
	if not (wzor and dane and typeof(podstawa) == "CFrame") then
		return
	end
	for _, d in wzor:GetDescendants() do
		if d:IsA("BasePart") then
			d.LocalTransparencyModifier = 1
		end
	end
	wzor.DescendantAdded:Connect(function(d)
		if d:IsA("BasePart") then
			d.LocalTransparencyModifier = 1
		end
	end)
	local skala = folder:GetAttribute("SkalaJajka") or j.skala_jajka
	local model, u = Rig.zbuduj(dane, skala, "Jajko lokalne " .. j.id)
	model.Parent = lokalne
	Rig.ustaw(u, podstawa)
	animowane[u] = true
	Rig.graj(u, "spoczynek")
	-- napis ceny nad lokalnym jajkiem (nie zależy od wczytania części serwera przez streaming)
	local b = Instance.new("BillboardGui")
	b.Name = "PetyProbaCena_" .. j.id
	b.Adornee = u.korzen
	b.AlwaysOnTop = false
	b.LightInfluence = 0
	b.ResetOnSpawn = false
	b.MaxDistance = 90
	b.Size = UDim2.fromOffset(300, 54)
	-- nad całym jajkiem (18.11: kwiatek na czubku jajka Bagna zasłaniał liczbę, gdy napis był na 0,8 wysokości)
	b.StudsOffsetWorldSpace = Vector3.new(0, (dane.wysokosc or 2.8) * skala + 0.9, 0)
	b.Parent = ekrany
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromScale(1, 1)
	t.Font = CZCIONKA
	t.TextScaled = true
	t.TextStrokeTransparency = 0.3
	t.TextColor3 = kolor("FFF6E0")
	t.Text = ""
	t.Parent = b
	jajkaLok[j.id] = { model = model, u = u, podstawa = podstawa, skala = skala, napis = t, j = j }
end

-- podpowiedź E inkubatora (szukana przy każdym odświeżeniu — część mogła dojść później)
local function znajdzPodpowiedz(j): ProximityPrompt?
	local e = kontener:FindFirstChild("Punkty")
	e = e and e:FindFirstChild(j.punkt_e)
	local pp = e and e:FindFirstChild("Podpowiedz")
	return if pp and pp:IsA("ProximityPrompt") then pp else nil
end

local function odswiezCene()
	local zloto = gracz:GetAttribute(S.atrybut_zlota)
	for _, j in D.jajka do
		local cena = gracz:GetAttribute(j.atrybuty.cena)
		if type(cena) == "number" then
			local stac = type(zloto) == "number" and zloto >= cena
			local lok = jajkaLok[j.id]
			if lok then
				-- cena stała (domyślna, decyzja 17.11): „Cena: 300 Złota”; rosnąca (przełącznik): twoja i następna
				local c = j.cena
				if c.tryb == "rosnaca" then
					local nast = math.min(c.maks, cena + c.krok)
					lok.napis.Text = string.format(T.twoja_cena, cena)
						.. (if nast ~= cena then "  ·  " .. string.format(T.nastepna, nast) else "")
				else
					lok.napis.Text = string.format(T.cena, cena)
				end
				lok.napis.TextColor3 = if stac then kolor("9CFF8A") else kolor("FFF6E0")
			end
			local pp = znajdzPodpowiedz(j)
			if pp then
				pp.ActionText = string.format(D.inkubator.napis_akcja_cena, cena) -- tylko u tego gracza
			end
		end
	end
end
for _, j in D.jajka do
	gracz:GetAttributeChangedSignal(j.atrybuty.cena):Connect(odswiezCene)
end
gracz:GetAttributeChangedSignal(S.atrybut_zlota):Connect(odswiezCene)

------------------------------------------------------------------ wyklucie
local function wybuch(pozycja: Vector3, kol: Color3, nr: number)
	local kula = Instance.new("Part")
	kula.Name = "Blysk"
	kula.Shape = Enum.PartType.Ball
	kula.Material = Enum.Material.Neon
	kula.Color = kol
	kula.Anchored = true
	kula.CanCollide = false
	kula.CanQuery = false
	kula.CanTouch = false
	kula.CastShadow = false
	kula.Size = Vector3.new(1, 1, 1)
	kula.Transparency = 0.4
	kula.Position = pozycja
	kula.Parent = lokalne
	local rozmiar = 3.5 + nr * 0.8 -- nie obejmuje gracza przy E ani kamery (zrzut 03 z próby: cały kadr różowy)
	TweenService:Create(kula, TweenInfo.new(0.55, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Size = Vector3.new(rozmiar, rozmiar, rozmiar), Transparency = 1 }):Play()
	local a = Instance.new("Attachment")
	a.Parent = kula
	local iskry = Instance.new("ParticleEmitter")
	iskry.Color = ColorSequence.new(kol, Color3.new(1, 1, 1))
	iskry.LightEmission = 1
	iskry.Speed = NumberRange.new(8, 16)
	iskry.Lifetime = NumberRange.new(0.6, 1.1)
	iskry.SpreadAngle = Vector2.new(180, 180)
	iskry.Size = NumberSequence.new(0.5, 0)
	iskry.Rate = 0
	iskry.Parent = a
	iskry:Emit(20 + nr * 15)
	if nr >= 4 then -- epicki i legendarny: słup światła
		local slup = Instance.new("Part")
		slup.Name = "SlupBlasku"
		slup.Shape = Enum.PartType.Cylinder
		slup.Material = Enum.Material.Neon
		slup.Color = kol
		slup.Anchored = true
		slup.CanCollide = false
		slup.CanQuery = false
		slup.CanTouch = false
		slup.CastShadow = false
		slup.Size = Vector3.new(40, 2.2, 2.2)
		slup.CFrame = CFrame.new(pozycja + Vector3.new(0, 19, 0)) * CFrame.Angles(0, 0, math.rad(90))
		slup.Transparency = 0.35
		slup.Parent = lokalne
		TweenService:Create(slup, TweenInfo.new(1.6), { Transparency = 1, Size = Vector3.new(40, 0.4, 0.4) }):Play()
		task.delay(1.7, function()
			slup:Destroy()
		end)
	end
	task.delay(1.3, function()
		kula:Destroy()
	end)
end

local function napisNadPetem(adornee: BasePart, info, kol: Color3, r)
	local p = L.pet(D, info.pet)
	local b = Instance.new("BillboardGui")
	b.Name = "PetyProbaWyklucie"
	b.Adornee = adornee
	b.AlwaysOnTop = false -- (z AlwaysOnTop napisu nie było na zrzutach narzędzia; nad petem i tak go widać)
	b.MaxDistance = 120
	b.LightInfluence = 0
	b.ResetOnSpawn = false
	b.Size = UDim2.fromOffset(440, 132)
	b.StudsOffsetWorldSpace = Vector3.new(0, 3.2, 0)
	b.Parent = ekrany
	local lista = Instance.new("UIListLayout")
	lista.HorizontalAlignment = Enum.HorizontalAlignment.Center
	lista.Parent = b
	local function linia(tekst: string, wys: number, k: Color3, czcionka)
		local t = Instance.new("TextLabel")
		t.BackgroundTransparency = 1
		t.Size = UDim2.new(1, 0, 0, wys)
		t.Font = czcionka or CZCIONKA
		t.TextScaled = true
		t.TextColor3 = k
		t.TextStrokeTransparency = 0.1
		t.Text = tekst
		t.Parent = b
		return t
	end
	linia(if info.nowy then W.napis_nowy else W.napis_kopia, 34, kolor("FFF6E0"), CZCIONKA_TYTULU)
	linia(p and p.nazwa or info.pet, 40, kol, CZCIONKA_TYTULU)
	linia((r and r.nazwa or "") .. "  ·  " .. (p and L.opisSkilla(D, p) or ""), 24, kolor("FFF6E0"))
	if not info.nowy then
		linia(string.format("×%d", info.kopie or 1), 22, kolor("FFF6E0"))
	end
	b.Size = UDim2.fromOffset(440, if info.nowy then 110 else 132)
	return b
end

local function sekwencjaWyklucia(info)
	-- jajko z serwera (info.jajko); haczyk testowy bez jajka → jajko, z którego jest pet
	local j = L.jajko(D, info.jajko) or L.jajkoPeta(D, info.pet) or D.jajka[1]
	local dp = danePeta(info.pet)
	local dj = daneRigu(j.rig)
	if not dp or not dj then
		return
	end
	local r, nr = rzadkoscPeta(info.pet)
	local kol = if r then kolor(r.kolor) else Color3.new(1, 1, 1)
	local G = j.polozenie
	local lok = jajkaLok[j.id]
	local podstawa = if lok then lok.podstawa else CFrame.new(v3(G.gniazdo) + Vector3.new(0, j.y_jajka, 0))
	local skala = if lok then lok.skala else j.skala_jajka
	if lok then
		lok.model.Parent = nil
	end
	local em, eu = Rig.zbuduj(dj, skala, "Jajko wyklucie")
	em.Parent = lokalne
	Rig.ustaw(eu, podstawa)
	animowane[eu] = true
	-- 1. trzęsie się
	Rig.graj(eu, "trzesienie", Rig.dlugosc(dj, "trzesienie") / W.trzesienie_s)
	dzwiek({ 0.8, 0.9, 0.8, 1.0 }, 0.35)
	task.wait(W.trzesienie_s)
	-- 2. pęka: środek w kolorze rzadkości, światło, błysk, iskry
	for _, c in Rig.czesci(eu) do
		if c.Name == "Wnetrze" then
			c.Color = kol
		end
	end
	local swiatlo = Instance.new("PointLight")
	swiatlo.Color = kol
	swiatlo.Range = 12 + nr * 3
	swiatlo.Brightness = 2 + nr
	swiatlo.Parent = eu.korzen
	Rig.graj(eu, "pekniecie", Rig.dlugosc(dj, "pekniecie") / W.pekniecie_s)
	wybuch(podstawa.Position + Vector3.new(0, 1.5 * skala, 0), kol, nr)
	local nuty = { 1, 1.26, 1.5 }
	for i = 4, nr + 1 do
		table.insert(nuty, 1.5 + 0.25 * (i - 3))
	end
	dzwiek(nuty, 0.55)
	task.wait(W.pekniecie_s * 0.6)
	-- 3. pet wyskakuje z jajka i ląduje przed gniazdem (w stronę punktu E)
	local pm, pu = Rig.zbuduj(dp, skalaPeta(info.pet), "Pet wyklucie")
	pm.Parent = lokalne
	animowane[pu] = true
	local e = v3(G.e)
	local srodek = podstawa.Position
	local kierunek = Vector3.new(e.X - srodek.X, 0, e.Z - srodek.Z)
	kierunek = if kierunek.Magnitude > 0.01 then kierunek.Unit else Vector3.new(0, 0, -1)
	local bok = Vector3.new(-kierunek.Z, 0, kierunek.X)
	-- ląduje obok gracza stojącego przy E, nie w nim (próba 17.11: pet wylądował w postaci)
	local cel = srodek + kierunek * W.przed_gniazdem + bok * W.w_bok
	local yCel = ziemia(cel) or (srodek.Y - j.y_jajka)
	cel = Vector3.new(cel.X, yCel, cel.Z)
	local start = srodek + Vector3.new(0, 1.5 * skala * 0.75, 0)
	local yaw = math.atan2(-kierunek.X, -kierunek.Z) -- przodem do gracza (od gniazda na zewnątrz)
	Rig.graj(pu, "wyklucie", Rig.dlugosc(dp, "wyklucie") / W.wyskok_s)
	for _, c in Rig.czesci(eu) do
		TweenService:Create(c, TweenInfo.new(0.6), { Transparency = 1 }):Play()
	end
	local t0 = os.clock()
	while os.clock() - t0 < W.wyskok_s do
		local a = math.clamp((os.clock() - t0) / W.wyskok_s, 0, 1)
		local poz = start:Lerp(cel, a)
		Rig.ustaw(pu, CFrame.new(poz) * CFrame.Angles(0, yaw, 0))
		RunService.RenderStepped:Wait()
	end
	Rig.ustaw(pu, CFrame.new(cel) * CFrame.Angles(0, yaw, 0))
	animowane[eu] = nil
	em:Destroy()
	-- 4. radość i napis
	Rig.graj(pu, "radosc", Rig.dlugosc(dp, "radosc") / W.radosc_s, "spoczynek")
	local napis = napisNadPetem(pu.korzen, info, kol, r)
	local p = L.pet(D, info.pet)
	komunikat(string.format("%s: %s (%s) — %s", if info.nowy then "Wykluł się" else "Kopia peta",
		p and p.nazwa or info.pet, r and r.nazwa or "", p and L.opisSkilla(D, p) or ""), kol, 4)
	task.wait(W.radosc_s + 0.8)
	-- 5. pet dołącza (aktywny idzie za graczem stąd) albo wraca do zagrody
	poWykluciu = CFrame.new(cel)
	if lok then
		lok.model.Parent = lokalne
		Rig.graj(lok.u, "spoczynek")
	end
	task.delay(1.6, function()
		napis:Destroy()
	end)
	animowane[pu] = nil
	pm:Destroy()
end

local function wyklucie(info: any)
	if type(info) ~= "table" or type(info.pet) ~= "string" or wylegaSie then
		return
	end
	wylegaSie = true
	task.spawn(function()
		local ok, blad = pcall(sekwencjaWyklucia, info)
		if not ok then
			warn(D.prefiks .. "wyklucie: " .. tostring(blad))
		end
		wylegaSie = false
	end)
end

------------------------------------------------------------------ zagroda: pety na miejscach, tablica, okno „PRÓBA”
local wierszeZagrody = nil -- ostatnia lista od serwera ({ wiersze, aktywny } albo { brak, tekst })
local petyZagrody = {} -- id → { model, u, nastepna }
local bliskoZagrody = false
local czasListy = 0

local function prosOListe()
	if os.clock() - czasListy > 0.6 then
		czasListy = os.clock()
		zdarzenia:FireServer("lista")
	end
end

local function odleglZagrody(): number
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp then
		return math.huge
	end
	local e = D.polozenia.zagroda_e
	return Vector3.new(hrp.Position.X - e[1], 0, hrp.Position.Z - e[3]).Magnitude
end

local function usunPetyZagrody()
	for id, z in petyZagrody do
		animowane[z.u] = nil
		z.model:Destroy()
		petyZagrody[id] = nil
	end
end

-- pety stojące w zagrodzie (od serwera: lista.zagroda.stoja); starszy serwer bez zagrody — wszystkie poza aktywnym
local function stojaWZagrodzie(): { [string]: boolean }?
	local z = wierszeZagrody and wierszeZagrody.zagroda
	if type(z) ~= "table" or type(z.stoja) ~= "table" then
		return nil
	end
	local w = {}
	for _, id in z.stoja do
		w[id] = true
	end
	return w
end

local function ustawPetyZagrody()
	usunPetyZagrody()
	if not bliskoZagrody or not wierszeZagrody or not wierszeZagrody.wiersze then
		return
	end
	local miejsca = D.polozenia.miejsca_petow -- tyle miejsc, ile znaczników zagroda_miejsce_N na mapie (6 albo 8)
	local e = v3(D.polozenia.zagroda_e)
	-- na miejscach pety, które STOJĄ w zagrodzie (dają Rybki), w kolejności od serwera; bez listy — najrzadsze
	local stoja = stojaWZagrodzie()
	local kolejka = {}
	if stoja then
		local z = wierszeZagrody.zagroda
		for _, id in z.stoja do
			for _, w in wierszeZagrody.wiersze do
				if w.pet == id then
					table.insert(kolejka, w)
				end
			end
		end
	else
		for _, w in wierszeZagrody.wiersze do
			if not w.aktywny then
				table.insert(kolejka, w)
			end
		end
		local nrRz = {}
		for _, w in kolejka do
			local _r, nr = rzadkoscPeta(w.pet)
			nrRz[w.pet] = nr
		end
		table.sort(kolejka, function(a, b)
			return nrRz[a.pet] > nrRz[b.pet]
		end)
	end
	local i = 0
	for _, w in kolejka do
		if i < #miejsca then
			i += 1
			local dane = danePeta(w.pet)
			if dane then
				local m, u = Rig.zbuduj(dane, skalaPeta(w.pet), "Zagroda " .. w.pet)
				m.Parent = lokalne
				local poz = v3(miejsca[i])
				local y = ziemia(poz) or poz.Y
				local do_e = Vector3.new(e.X - poz.X, 0, e.Z - poz.Z)
				local yaw = if do_e.Magnitude > 0.01 then math.atan2(-do_e.Unit.X, -do_e.Unit.Z) else 0
				Rig.ustaw(u, CFrame.new(poz.X, y, poz.Z) * CFrame.Angles(0, yaw, 0))
				animowane[u] = true
				Rig.graj(u, "spoczynek")
				u.t = math.random() * 2
				local b = Instance.new("BillboardGui")
				b.Name = "Imie"
				b.Adornee = u.korzen
				b.LightInfluence = 0
				b.MaxDistance = 45
				b.Size = UDim2.fromOffset(150, 34)
				b.StudsOffsetWorldSpace = Vector3.new(0, (dane.wysokosc or 2) * skalaPeta(w.pet) + 0.6, 0)
				b.Parent = m
				local t = Instance.new("TextLabel")
				t.BackgroundTransparency = 1
				t.Size = UDim2.fromScale(1, 1)
				t.Font = CZCIONKA
				t.TextScaled = true
				t.TextColor3 = kolor(w.kolor)
				t.TextStrokeTransparency = 0.2
				t.Text = string.format("%s ×%d", w.nazwa, w.kopie)
				t.Parent = b
				petyZagrody[w.pet] = { model = m, u = u, nastepna = os.clock() + 4 + math.random() * 6 }
			end
		end
	end
end

-- napis „+N Rybek” nad zagrodą, gdy serwer dopisze Rybki za pety w zagrodzie (tylko gdy gracz jest blisko)
local kotwicaPlus: BasePart? = nil
local plusow, ostatniPlus = 0, nil -- do próby w Play (haczyk "stan")
local function plusZagrody(ile: any)
	if type(ile) ~= "number" or ile < 1 then
		return
	end
	plusow += 1
	ostatniPlus = ile
	if not bliskoZagrody then
		return
	end
	if not kotwicaPlus then
		local srodek = Vector3.new(0, 0, 0)
		local miejsca = D.polozenia.miejsca_petow
		for _, m in miejsca do
			srodek += v3(m)
		end
		srodek = if #miejsca > 0 then srodek / #miejsca else v3(D.polozenia.zagroda_e)
		local k = Instance.new("Part")
		k.Name = "PlusZagrody"
		k.Anchored = true
		k.CanCollide = false
		k.CanQuery = false
		k.CanTouch = false
		k.Transparency = 1
		k.Size = Vector3.new(0.2, 0.2, 0.2)
		k.Position = srodek + Vector3.new(0, 4.5, 0)
		k.Parent = lokalne
		kotwicaPlus = k
	end
	local napis = Instance.new("BillboardGui")
	napis.Name = "Plus"
	napis.Adornee = kotwicaPlus
	napis.LightInfluence = 0
	napis.MaxDistance = D.zagroda.zasieg_pokazu
	napis.Size = UDim2.fromOffset(170, 40)
	napis.StudsOffsetWorldSpace = Vector3.new(0, 0, 0)
	napis.Parent = lokalne
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromScale(1, 1)
	t.Font = CZCIONKA_TYTULU
	t.TextScaled = true
	t.TextColor3 = kolor("FFD54A")
	t.TextStrokeTransparency = 0.2
	-- odmiana (26.11): 1 Rybka, 2–4 / 22–24… Rybki, reszta Rybek
	local d, s = ile % 10, ile % 100
	local wzor = if ile == 1 then T.plus_1 elseif d >= 2 and d <= 4 and (s < 12 or s > 14) then T.plus_2_4 else T.plus
	t.Text = string.format(wzor or T.plus, ile)
	t.Parent = napis
	local czas = D.zagroda.plus_s
	TweenService:Create(napis, TweenInfo.new(czas, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ StudsOffsetWorldSpace = Vector3.new(0, 2.5, 0) }):Play()
	TweenService:Create(t, TweenInfo.new(czas, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
		{ TextTransparency = 1, TextStrokeTransparency = 1 }):Play()
	task.delay(czas + 0.1, function()
		napis:Destroy()
	end)
end

-- tablica przy zagrodzie: SurfaceGui u tego gracza na części Zagroda/Tablica — kolumna na każde jajko
local tablicaGui: SurfaceGui? = nil
local tablicaKolumny = {} -- id jajka → Frame z wierszami
local function przygotujTablice()
	local z = kontener:WaitForChild("Zagroda", 20)
	local czesc = z and z:WaitForChild("Tablica", 20)
	if not czesc or not czesc:IsA("BasePart") then
		return
	end
	local s = Instance.new("SurfaceGui")
	s.Name = "PetyProbaTablica"
	s.Adornee = czesc
	s.Face = Enum.NormalId.Front
	s.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	s.PixelsPerStud = 60
	s.LightInfluence = 0
	s.ResetOnSpawn = false
	s.Parent = ekrany
	local tlo = Instance.new("Frame")
	tlo.Size = UDim2.fromScale(1, 1)
	tlo.BackgroundColor3 = kolor("2B2118")
	tlo.Parent = s
	local naglowek = Instance.new("TextLabel")
	naglowek.BackgroundTransparency = 1
	naglowek.Size = UDim2.new(1, 0, 0.2, 0)
	naglowek.Font = CZCIONKA_TYTULU
	naglowek.TextScaled = true
	naglowek.TextColor3 = kolor("FFC94A")
	naglowek.Text = D.zagroda.napis_tablicy .. "  ·  " .. D.zagroda.napis_proby
	naglowek.Parent = tlo
	local n = #D.jajka
	for i, j in D.jajka do
		local kol = Instance.new("Frame")
		kol.Name = "Kolumna_" .. j.id
		kol.BackgroundTransparency = 1
		kol.Position = UDim2.new(0.03 + (i - 1) * 0.95 / n, 0, 0.21, 0)
		kol.Size = UDim2.new(0.95 / n - 0.02, 0, 0.77, 0)
		kol.Parent = tlo
		local tytulKol = Instance.new("TextLabel")
		tytulKol.Name = "Tytul"
		tytulKol.BackgroundTransparency = 1
		tytulKol.Size = UDim2.new(1, 0, 0.14, 0)
		tytulKol.Font = CZCIONKA_TYTULU
		tytulKol.TextScaled = true
		tytulKol.TextXAlignment = Enum.TextXAlignment.Left
		tytulKol.TextColor3 = kolor(j.kolor_swiatla)
		tytulKol.Text = j.tytul
		tytulKol.Parent = kol
		local lista = Instance.new("Frame")
		lista.Name = "Lista"
		lista.BackgroundTransparency = 1
		lista.Position = UDim2.new(0, 0, 0.16, 0)
		lista.Size = UDim2.new(1, 0, 0.84, 0)
		lista.Parent = kol
		local ul = Instance.new("UIListLayout")
		ul.Padding = UDim.new(0.02, 0)
		ul.Parent = lista
		tablicaKolumny[j.id] = lista
	end
	tablicaGui = s
end

local function rysujTablice()
	if not tablicaGui then
		return
	end
	for _, lista in tablicaKolumny do
		for _, d in lista:GetChildren() do
			if d:IsA("TextLabel") then
				d:Destroy()
			end
		end
	end
	local function wiersz(lista: Frame?, tekst: string, k: Color3)
		if not lista then
			return
		end
		local t = Instance.new("TextLabel")
		t.BackgroundTransparency = 1
		t.Size = UDim2.new(1, 0, 0.18, 0)
		t.Font = CZCIONKA
		t.TextScaled = true
		t.TextXAlignment = Enum.TextXAlignment.Left
		t.TextColor3 = k
		t.Text = tekst
		t.Parent = lista
	end
	local pierwsza = tablicaKolumny[D.jajka[1].id]
	if not wierszeZagrody or wierszeZagrody.brak then
		wiersz(pierwsza, if wierszeZagrody then wierszeZagrody.tekst else "…", kolor("FFF6E0"))
		return
	end
	if #wierszeZagrody.wiersze == 0 then
		wiersz(pierwsza, T.brak_petow, kolor("FFF6E0"))
		return
	end
	local ile = {}
	for _, w in wierszeZagrody.wiersze do
		ile[w.jajko] = (ile[w.jajko] or 0) + 1
		wiersz(tablicaKolumny[w.jajko], string.format("%s%s ×%d · %s", if w.aktywny then "► " else "", w.nazwa, w.kopie,
			w.krotko or w.skill), kolor(w.kolor))
	end
	for _, j in D.jajka do
		if not ile[j.id] then
			wiersz(tablicaKolumny[j.id], T.brak_z_jajka, kolor("BFB6A8"))
		end
	end
end

-- okno wyboru aktywnego peta (tymczasowe — docelowe okno Pets w HUD robi Paweł)
local okno = Instance.new("ScreenGui")
okno.Name = "PetyProbaOkno"
okno.ResetOnSpawn = false
okno.DisplayOrder = 30
okno.Enabled = false
okno.Parent = ekrany
local ramka = Instance.new("Frame")
ramka.Name = "Ramka"
ramka.AnchorPoint = Vector2.new(0.5, 0.5)
ramka.Position = UDim2.fromScale(0.5, 0.5)
ramka.Size = UDim2.fromScale(0.9, 0.78)
ramka.BackgroundColor3 = kolor("2B2118")
ramka.Parent = okno
do
	local og = Instance.new("UISizeConstraint")
	og.MaxSize = Vector2.new(600, 540)
	og.Parent = ramka
	local r = Instance.new("UICorner")
	r.CornerRadius = UDim.new(0, 14)
	r.Parent = ramka
	local o = Instance.new("UIStroke")
	o.Color = kolor("FFC94A")
	o.Thickness = 3
	o.Parent = ramka
end
local tytul = Instance.new("TextLabel")
tytul.BackgroundTransparency = 1
tytul.Position = UDim2.new(0, 16, 0, 8)
tytul.Size = UDim2.new(1, -150, 0, 44)
tytul.Font = CZCIONKA_TYTULU
tytul.TextScaled = true
tytul.TextXAlignment = Enum.TextXAlignment.Left
tytul.TextColor3 = kolor("FFC94A")
tytul.Text = D.zagroda.napis_tablicy
tytul.Parent = ramka
local znakProby = Instance.new("TextLabel")
znakProby.AnchorPoint = Vector2.new(1, 0)
znakProby.Position = UDim2.new(1, -64, 0, 14)
znakProby.Size = UDim2.fromOffset(86, 30)
znakProby.BackgroundColor3 = kolor("C7302B")
znakProby.Font = CZCIONKA
znakProby.TextScaled = true
znakProby.TextColor3 = kolor("FFFFFF")
znakProby.Text = D.zagroda.napis_proby
znakProby.Parent = ramka
local zamknij = Instance.new("TextButton")
zamknij.Name = "Zamknij"
zamknij.AnchorPoint = Vector2.new(1, 0)
zamknij.Position = UDim2.new(1, -10, 0, 8)
zamknij.Size = UDim2.fromOffset(44, 44)
zamknij.BackgroundTransparency = 1
zamknij.Font = CZCIONKA
zamknij.TextSize = 30
zamknij.TextColor3 = kolor("FFC94A")
zamknij.Text = "×"
zamknij.Parent = ramka
local przewijane = Instance.new("ScrollingFrame") -- dziesięć petów z dwóch jajek nie mieści się — przewijane
przewijane.Name = "Lista"
przewijane.Position = UDim2.new(0, 12, 0, 60)
przewijane.Size = UDim2.new(1, -24, 1, -128)
przewijane.BackgroundTransparency = 1
przewijane.ScrollBarThickness = 8
przewijane.AutomaticCanvasSize = Enum.AutomaticSize.Y
przewijane.CanvasSize = UDim2.new()
przewijane.Parent = ramka
local ulOkna = Instance.new("UIListLayout")
ulOkna.Padding = UDim.new(0, 8)
ulOkna.SortOrder = Enum.SortOrder.LayoutOrder
ulOkna.Parent = przewijane
local odstawBtn = Instance.new("TextButton")
odstawBtn.Name = "Odstaw"
odstawBtn.AnchorPoint = Vector2.new(0.5, 1)
odstawBtn.Position = UDim2.new(0.5, 0, 1, -12)
odstawBtn.Size = UDim2.new(0.5, 0, 0, 48)
odstawBtn.BackgroundColor3 = kolor("5E3A22")
odstawBtn.Font = CZCIONKA
odstawBtn.TextScaled = true
odstawBtn.TextColor3 = kolor("FFF6E0")
odstawBtn.Text = T.odstaw
odstawBtn.Parent = ramka
do
	local r = Instance.new("UICorner")
	r.CornerRadius = UDim.new(0, 10)
	r.Parent = odstawBtn
end

local function rysujOkno()
	for _, d in przewijane:GetChildren() do
		if d:IsA("Frame") or d:IsA("TextLabel") then
			d:Destroy()
		end
	end
	if not wierszeZagrody or wierszeZagrody.brak or #wierszeZagrody.wiersze == 0 then
		local t = Instance.new("TextLabel")
		t.BackgroundTransparency = 1
		t.Size = UDim2.new(1, 0, 0, 60)
		t.Font = CZCIONKA
		t.TextScaled = true
		t.TextColor3 = kolor("FFF6E0")
		t.Text = if wierszeZagrody and wierszeZagrody.brak then wierszeZagrody.tekst else T.brak_petow
		t.Parent = przewijane
		odstawBtn.Visible = false
		return
	end
	odstawBtn.Visible = wierszeZagrody.aktywny ~= nil
	local kolejnosc = 0
	local ostatnieJajko = nil
	-- wiersz zagrody (25.11.2026): ile miejsc zajętych, Rybki na minutę, więcej miejsc za Rybki, „Najrzadsze”
	local z = wierszeZagrody.zagroda
	local stoja = stojaWZagrodzie() or {}
	if type(z) == "table" then
		kolejnosc += 1
		local f = Instance.new("Frame")
		f.Name = "Zagroda"
		f.LayoutOrder = kolejnosc
		f.Size = UDim2.new(1, -10, 0, 92)
		f.BackgroundColor3 = kolor("2F4A2A")
		f.Parent = przewijane
		local r = Instance.new("UICorner")
		r.CornerRadius = UDim.new(0, 10)
		r.Parent = f
		local t = Instance.new("TextLabel")
		t.Name = "Stan"
		t.BackgroundTransparency = 1
		t.Position = UDim2.new(0, 12, 0, 4)
		t.Size = UDim2.new(1, -24, 0, 36)
		t.Font = CZCIONKA_TYTULU
		t.TextScaled = true
		t.TextXAlignment = Enum.TextXAlignment.Left
		t.TextColor3 = kolor("FFD54A")
		t.Text = string.format(T.zagroda_stan, #z.stoja, z.miejsc, if #z.stoja > 0 then z.opis else T.przychod_pusta)
		t.Parent = f
		local ulepsz = Instance.new("TextButton")
		ulepsz.Name = "Ulepsz"
		ulepsz.AnchorPoint = Vector2.new(1, 1)
		ulepsz.Position = UDim2.new(1, -10, 1, -6)
		ulepsz.Size = UDim2.new(0.56, 0, 0, 42)
		ulepsz.BackgroundColor3 = if z.cena then kolor("C98A1E") else kolor("5E5244")
		ulepsz.AutoButtonColor = z.cena ~= nil
		ulepsz.Font = CZCIONKA
		ulepsz.TextScaled = true
		ulepsz.TextColor3 = kolor("FFFFFF")
		ulepsz.Text = if z.cena then string.format(T.ulepsz, L.miejscaZagrody(D, z.poziom + 1), z.cena)
			else string.format(T.ulepsz_max, z.miejsc)
		ulepsz.Parent = f
		local ru = Instance.new("UICorner")
		ru.CornerRadius = UDim.new(0, 10)
		ru.Parent = ulepsz
		if z.cena then
			ulepsz.Activated:Connect(function()
				zdarzenia:FireServer("ulepsz_zagrode")
			end)
		end
		if z.reczny then
			local auto = Instance.new("TextButton")
			auto.Name = "Najrzadsze"
			auto.AnchorPoint = Vector2.new(0, 1)
			auto.Position = UDim2.new(0, 12, 1, -6)
			auto.Size = UDim2.new(0.34, 0, 0, 42)
			auto.BackgroundColor3 = kolor("5E3A22")
			auto.Font = CZCIONKA
			auto.TextScaled = true
			auto.TextColor3 = kolor("FFF6E0")
			auto.Text = T.najrzadsze
			auto.Parent = f
			local ra = Instance.new("UICorner")
			ra.CornerRadius = UDim.new(0, 10)
			ra.Parent = auto
			auto.Activated:Connect(function()
				zdarzenia:FireServer("zagroda_auto")
			end)
		end
	end
	for _, w in wierszeZagrody.wiersze do
		if w.jajko ~= ostatnieJajko then -- nagłówek jajka (lista jest w kolejności katalogu: jajko po jajku)
			ostatnieJajko = w.jajko
			local j = L.jajko(D, w.jajko)
			kolejnosc += 1
			local h = Instance.new("TextLabel")
			h.Name = "Naglowek_" .. tostring(w.jajko)
			h.LayoutOrder = kolejnosc
			h.BackgroundTransparency = 1
			h.Size = UDim2.new(1, -10, 0, 30)
			h.Font = CZCIONKA_TYTULU
			h.TextScaled = true
			h.TextXAlignment = Enum.TextXAlignment.Left
			h.TextColor3 = if j then kolor(j.kolor_swiatla) else kolor("FFC94A")
			h.Text = if j then j.tytul else tostring(w.jajko)
			h.Parent = przewijane
		end
		kolejnosc += 1
		local f = Instance.new("Frame")
		f.Name = "Wiersz_" .. w.pet
		f.LayoutOrder = kolejnosc
		f.Size = UDim2.new(1, -10, 0, 64)
		f.BackgroundColor3 = kolor("3A2D21")
		f.Parent = przewijane
		local r = Instance.new("UICorner")
		r.CornerRadius = UDim.new(0, 10)
		r.Parent = f
		local pasek = Instance.new("Frame")
		pasek.Size = UDim2.new(0, 10, 1, 0)
		pasek.BackgroundColor3 = kolor(w.kolor)
		pasek.BorderSizePixel = 0
		pasek.Parent = f
		local nazwa = Instance.new("TextLabel")
		nazwa.BackgroundTransparency = 1
		nazwa.Position = UDim2.new(0, 20, 0, 4)
		nazwa.Size = UDim2.new(0.58, -20, 0, 30)
		nazwa.Font = CZCIONKA_TYTULU
		nazwa.TextScaled = true
		nazwa.TextXAlignment = Enum.TextXAlignment.Left
		nazwa.TextColor3 = kolor(w.kolor)
		nazwa.Text = string.format("%s  ×%d", w.nazwa, w.kopie)
			.. (if stoja[w.pet] then "  ·  " .. string.format(T.w_zagrodzie, L.opisPrzychodu(D, L.stawka(D, w.pet))) else "")
		nazwa.Parent = f
		local opis = Instance.new("TextLabel")
		opis.BackgroundTransparency = 1
		opis.Position = UDim2.new(0, 20, 0, 35)
		opis.Size = UDim2.new(0.58, -20, 0, 22)
		opis.Font = CZCIONKA
		opis.TextScaled = true
		opis.TextXAlignment = Enum.TextXAlignment.Left
		opis.TextColor3 = kolor("FFF6E0")
		opis.Text = w.rzadkosc .. "  ·  " .. w.skill
		opis.Parent = f
		if w.aktywny then
			local t = Instance.new("TextLabel")
			t.AnchorPoint = Vector2.new(1, 0.5)
			t.Position = UDim2.new(1, -10, 0.5, 0)
			t.Size = UDim2.new(0.34, 0, 0, 40)
			t.BackgroundTransparency = 1
			t.Font = CZCIONKA
			t.TextScaled = true
			t.TextColor3 = kolor("9CFF8A")
			t.Text = T.aktywny
			t.Parent = f
		else
			if type(z) == "table" then -- „Do zagrody” / „Z zagrody” (25.11.2026)
				local wz = stoja[w.pet] == true
				local bz = Instance.new("TextButton")
				bz.Name = if wz then "ZZagrody" else "DoZagrody"
				bz.AnchorPoint = Vector2.new(1, 0.5)
				bz.Position = UDim2.new(1, -10, 0.5, 0)
				bz.Size = UDim2.new(0.18, 0, 0, 44)
				bz.BackgroundColor3 = if wz then kolor("5E3A22") else kolor("2E7D6B")
				bz.Font = CZCIONKA
				bz.TextScaled = true
				bz.TextColor3 = kolor("FFFFFF")
				bz.Text = if wz then T.z_zagrody else T.do_zagrody
				bz.Parent = f
				local rz = Instance.new("UICorner")
				rz.CornerRadius = UDim.new(0, 10)
				rz.Parent = bz
				local idz = w.pet
				bz.Activated:Connect(function()
					if wz then
						zdarzenia:FireServer("zagroda_zdejmij", idz)
					else
						zdarzenia:FireServer("zagroda_dodaj", idz)
					end
				end)
			end
			local b = Instance.new("TextButton")
			b.Name = "Wybierz"
			b.AnchorPoint = Vector2.new(1, 0.5)
			b.Position = if type(z) == "table" then UDim2.new(0.82, -16, 0.5, 0) else UDim2.new(1, -10, 0.5, 0)
			b.Size = if type(z) == "table" then UDim2.new(0.2, 0, 0, 44) else UDim2.new(0.3, 0, 0, 44)
			b.BackgroundColor3 = kolor("4C8A35")
			b.Font = CZCIONKA
			b.TextScaled = true
			b.TextColor3 = kolor("FFFFFF")
			b.Text = T.wybierz
			b.Parent = f
			local rb = Instance.new("UICorner")
			rb.CornerRadius = UDim.new(0, 10)
			rb.Parent = b
			local id = w.pet
			b.Activated:Connect(function()
				zdarzenia:FireServer("wybierz", id)
			end)
		end
	end
end

local function otworzOkno()
	okno.Enabled = true
	rysujOkno()
	czasListy = 0
	prosOListe()
end
zamknij.Activated:Connect(function()
	okno.Enabled = false
end)
odstawBtn.Activated:Connect(function()
	zdarzenia:FireServer("odstaw")
end)

-- E opiekunki w bazarze: jedno zdarzenie okien (pakiet swiat/miasteczko_bazar_gra) — dymek „w budowie” wyłączony
local function zdarzenieOkien(): BindableEvent?
	local e = ReplicatedStorage:FindFirstChild(D.zagroda.zdarzenie_okna)
	if not e then
		local nowe = Instance.new("BindableEvent")
		nowe.Name = D.zagroda.zdarzenie_okna
		nowe.Parent = ReplicatedStorage
		e = nowe
	end
	return if e:IsA("BindableEvent") then e else nil
end
local okna = zdarzenieOkien()
if okna then
	okna:SetAttribute(D.zagroda.id_okna, true)
	okna.Event:Connect(function(id: any)
		if id == D.zagroda.id_okna then
			otworzOkno()
		end
	end)
end

------------------------------------------------------------------ premia peta przy łupie (komunikat StanGracza)
local podpietyStan: RemoteEvent? = nil
local function podepnijStanGracza()
	local k = workspace:FindFirstChild(S.kontener)
	local z = k and k:FindFirstChild("Zdalne")
	local e = z and z:FindFirstChild(S.zdarzenia)
	if not e or not e:IsA("RemoteEvent") or e == podpietyStan then
		return
	end
	podpietyStan = e
	e.OnClientEvent:Connect(function(polecenie: any, zloto: any, xp: any, pet: any)
		if polecenie ~= "premia" then
			return
		end
		local p = L.pet(D, pet)
		local nazwa = if p then p.nazwa else "?"
		local czesci = {}
		if type(zloto) == "number" and zloto > 0 then
			table.insert(czesci, string.format("+%d Złota", zloto))
		end
		if type(xp) == "number" and xp > 0 then
			table.insert(czesci, string.format("+%d doświadczenia", xp))
		end
		if #czesci > 0 then
			local r = p and L.rzadkosc(D, p.rzadkosc)
			komunikat(table.concat(czesci, ", ") .. " od peta: " .. nazwa, if r then kolor(r.kolor) else nil, 3.5)
		end
	end)
end
podepnijStanGracza()
workspace.ChildAdded:Connect(function(o)
	if o.Name == S.kontener then
		task.delay(2, podepnijStanGracza)
	end
end)

------------------------------------------------------------------ zdarzenia od serwera
zdarzenia.OnClientEvent:Connect(function(polecenie: any, a: any, b: any)
	if polecenie == "wyklucie" then
		wyklucie(a)
	elseif polecenie == "odmowa" then
		if type(a) == "string" then
			komunikat(a, kolor("FFB0A0"), 3.5)
		end
	elseif polecenie == "lista" then
		if type(a) == "table" then
			wierszeZagrody = a
			rysujTablice()
			ustawPetyZagrody()
			if okno.Enabled then
				rysujOkno()
			end
		end
	elseif polecenie == "wybrany" then
		local p = L.pet(D, a)
		komunikat(if p then string.format(T.wybrany, p.nazwa) else T.odstawiony, nil, 3)
		local t = towarzysze[gracz]
		if t then
			Rig.graj(t.u, "radosc", 1, "spoczynek")
		end
	elseif polecenie == "okno" then
		otworzOkno()
	elseif polecenie == "zagroda_plus" then
		plusZagrody(a)
	elseif polecenie == "zagroda_ulepszona" then
		if type(a) == "number" then
			komunikat(string.format(T.ulepszona, a), kolor("FFD54A"), 3)
		end
	end
end)

-- lista na nowo, gdy zmieni się kolekcja albo aktywny pet (a gracz jest przy zagrodzie)
for _, atr in { S.atrybut_liczby, S.atrybut_aktywnego } do
	gracz:GetAttributeChangedSignal(atr):Connect(function()
		if bliskoZagrody or okno.Enabled then
			prosOListe()
		end
	end)
end

------------------------------------------------------------------ pętla co klatkę
local pokazowe = {}
local czasBledu = -math.huge
RunService.RenderStepped:Connect(function(dt: number)
	local ukryte = ukryteLokalnie()
	zglosCzekaj(ukryte)
	local ok, blad = pcall(aktualizujTowarzyszy, dt, ukryte)
	if not ok and os.clock() - czasBledu > 5 then
		czasBledu = os.clock()
		warn(D.prefiks .. "pet przy graczu: " .. tostring(blad))
	end
	-- zagroda: pety pokazują się, gdy gracz jest blisko
	local blisko = odleglZagrody() < D.zagroda.zasieg_pokazu
	if blisko ~= bliskoZagrody then
		bliskoZagrody = blisko
		if blisko then
			prosOListe()
		else
			usunPetyZagrody()
		end
	end
	local t = os.clock()
	for _, z in petyZagrody do
		if t > z.nastepna then
			z.nastepna = t + 6 + math.random() * 6
			Rig.graj(z.u, "radosc", 1, "spoczynek")
		end
	end
	for u in animowane do
		if u.model.Parent then
			Rig.krok(u, dt)
		end
	end
end)

------------------------------------------------------------------ start
for _, j in D.jajka do
	task.spawn(function()
		przygotujInkubator(j)
		odswiezCene()
	end)
end
odswiezCene()
task.spawn(function()
	przygotujTablice()
	rysujTablice()
end)

------------------------------------------------------------------ haczyk testowy
sterowanie.OnInvoke = function(polecenie: string, a: any, b: any, c: any)
	if polecenie == "stan" then
		local t = towarzysze[gracz]
		local postac = gracz.Character
		local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
		local n = 0
		for _ in towarzysze do
			n += 1
		end
		local wZagrodzie = 0
		for _ in petyZagrody do
			wZagrodzie += 1
		end
		local napisy, akcje, lokalneJajka = {}, {}, 0
		for _, j in D.jajka do
			local lok = jajkaLok[j.id]
			local pp = znajdzPodpowiedz(j)
			napisy[j.id] = lok and lok.napis.Text
			akcje[j.id] = pp and pp.ActionText
			lokalneJajka += if lok then 1 else 0
		end
		-- akcjaE / napisCeny: jajko inkubatora najbliżej gracza (wcześniej zawsze pierwsze — leśne — co myliło próbę
		-- przy inkubatorze Bagna); serwer i tak sam sprawdza, przy którym inkubatorze stoi gracz
		local pierwsze, najblizej = D.jajka[1].id, math.huge
		if hrp then
			for _, j in D.jajka do
				local e = j.polozenie.e
				local d = Vector3.new(hrp.Position.X - e[1], 0, hrp.Position.Z - e[3]).Magnitude
				if d < najblizej then
					pierwsze, najblizej = j.id, d
				end
			end
		end
		return {
			jajkoPrzy = pierwsze, odlegloscOdE = if najblizej < math.huge then najblizej else nil,
			towarzysze = n, mojPet = t and t.pet, klip = t and t.u.klip,
			odleglosc = if t and hrp then (t.pos - hrp.Position).Magnitude else nil,
			wylegaSie = wylegaSie, ukryte = ukryteLokalnie(), okno = okno.Enabled, petyWZagrodzie = wZagrodzie,
			bliskoZagrody = bliskoZagrody, napisCeny = napisy[pierwsze], akcjaE = akcje[pierwsze],
			jajkoLokalne = jajkaLok[pierwsze] ~= nil, napisy = napisy, akcjeE = akcje, jajekLokalnych = lokalneJajka,
			wiersze = wierszeZagrody and wierszeZagrody.wiersze and #wierszeZagrody.wiersze, komunikat = pasekKom.Visible
				and pasekKom.Text or nil,
			zagroda = wierszeZagrody and wierszeZagrody.zagroda, plusow = plusow, ostatniPlus = ostatniPlus,
			wierszZagrodyWOknie = przewijane:FindFirstChild("Zagroda") ~= nil, miejscNaMapie = #D.polozenia.miejsca_petow,
		}
	elseif polecenie == "do_zagrody" and type(a) == "string" then
		zdarzenia:FireServer("zagroda_dodaj", a)
	elseif polecenie == "z_zagrody" and type(a) == "string" then
		zdarzenia:FireServer("zagroda_zdejmij", a)
	elseif polecenie == "ulepsz" then
		zdarzenia:FireServer("ulepsz_zagrode")
	elseif polecenie == "najrzadsze" then
		zdarzenia:FireServer("zagroda_auto")
	elseif polecenie == "okno" then
		otworzOkno()
	elseif polecenie == "zamknij" then
		okno.Enabled = false
	elseif polecenie == "wybierz" and type(a) == "string" then
		zdarzenia:FireServer("wybierz", a)
	elseif polecenie == "wyklucie" and type(a) == "string" then
		wyklucie({ pet = a, nowy = b ~= false, kopie = if b == false then 2 else 1, jajko = c })
	elseif polecenie == "pokaz" and type(a) == "string" and typeof(b) == "Vector3" then
		local dane = danePeta(a)
		if not dane then
			return false
		end
		local m, u = Rig.zbuduj(dane, skalaPeta(a), "Pokaz " .. a)
		m.Parent = lokalne
		Rig.ustaw(u, CFrame.new(b))
		animowane[u] = true
		Rig.graj(u, "spoczynek")
		table.insert(pokazowe, m)
	elseif polecenie == "pokaz_usun" then
		for _, m in pokazowe do
			m:Destroy()
		end
		table.clear(pokazowe)
	else
		return false
	end
	return true
end

kontener:SetAttribute("KlientPetowGotowy", true)
