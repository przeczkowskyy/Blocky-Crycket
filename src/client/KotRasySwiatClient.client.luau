--!nonstrict
--[[
	KotRasySwiatClient — PODGLĄD u Pawła (26.11), propozycja: po wyborze klasy i rasy każdy gracz chodzi po świecie
	kotem swojej rasy (modele według rzutów Pawła: swiat/postacie/koty_wg_rzutow.py + kot_demon.wg_rzutow; wzory
	z klipami w ReplicatedStorage.KotyRasSwiat.Race_<Id>, tools/studio/koty_wg_rzutow_swiat.luau). Koty wszystkich
	graczy składa każdy klient u siebie (rasa i klasa to atrybuty gracza, widoczne dla wszystkich).

	Postać Roblox zostaje (fizyka, sterowanie, kamera); awatar jest chowany przez Transparency (z zapamiętaniem
	dawnych wartości), kot stoi w jego miejscu i znika razem z nim (LocalTransparencyModifier głowy — walka, stół
	mistrza gier, pierwsza osoba). Bohatera klasy z pakietu Karola wyłącza w czasie gry serwer
	(src/server/KotRasySwiat.server.luau) jego własnym wyłącznikiem; pliki Karola bez zmian.

	Animacje (klipy z AnimSaves figury, Animator): spoczynek, chód, bieg, skok, spadanie, upadek po śmierci —
	idle / chod / upadek to klipy Kota-Maga Karola, bieg / skok / spadanie dorobione 26.11 (koty_wg_rzutow.klipy_ruchu).
	Klipy rejestruje KeyframeSequenceProvider — działa TYLKO w Studio; do prawdziwej gry trzeba je wgrać.
	Trening AFK ustawia pozy na stawach awatara — kot przejmuje je co klatkę (te same nazwy stawów).

	Broń startowa klasy (WyborKlasyModele.Weapon_<Klasa>_Kot) siedzi w prawej łapce na zaczepie kostura. Slot „1”
	na dole ekranu (klawisz 1 albo dotknięcie) wyjmuje ją i chowa; stan (atrybut gracza BronWyjeta) widzą wszyscy.
	Gdy broń jest schowana, prawa łapa nie trzyma pozy „niosę broń”, tylko pracuje jak lewa.

	Wyłącznik: atrybut Wlaczone folderu KotyRasSwiat; skala kota: atrybut Skala.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UIS = game:GetService("UserInputService")
local TS = game:GetService("TweenService")
local KSP = game:GetService("KeyframeSequenceProvider")

local player = Players.LocalPlayer
local folder = RS:WaitForChild("KotyRasSwiat", 30)
if not folder then
	return
end
local bronEv = RS:WaitForChild("KotRasySwiatBron", 10)

local KLIPY = { "idle", "chod", "bieg", "skok", "spadanie", "upadek", "czar", "wiwat", "atak", "kula_ognia",
	"lodowy_pocisk", "bariera", "unik", "trafienie" }
local RUCH = { idle = true, chod = true, bieg = true, skok = true, spadanie = true } -- klipy w pętli
local AKCJE = { "czar", "wiwat", "atak", "kula_ognia", "lodowy_pocisk", "bariera", "unik", "trafienie", "upadek" }
local IKONY_BRONI = { -- ikony broni startowych (assets/manifest.json: WeaponClub, WeaponStaff, WeaponSlingshot)
	Warrior = "rbxassetid://73877053632813",
	Mage = "rbxassetid://128671874530213",
	Scout = "rbxassetid://90364220695668",
}
local STAWY_PRAWEJ = { "RightShoulder", "RightElbow", "RightWrist" }

local lokalne = Instance.new("Folder")
lokalne.Name = "KotyRasSwiatLokalne"
lokalne.Parent = workspace

local idKlipu: { [string]: string } = {} -- klipy są wspólne dla wszystkich ras (ten sam szkielet): rejestrujemy raz
local koty: { [Player]: any } = {}

------------------------------------------------------------ kurz spod łap
-- Kreskówkowy obłoczek (Paweł 26.11): dwie–trzy jasnoszare kulki z czarnym konturem jak reszta gry; szybko rosną,
-- odpływają do tyłu i w górę, potem kurczą się do zera i bledną. Widzi je każdy klient u siebie (koty są lokalne).
local kurz = Instance.new("Model")
kurz.Name = "KotyRasSwiatKurz"
do
	local h = Instance.new("Highlight")
	h.FillTransparency, h.OutlineColor, h.OutlineTransparency = 1, Color3.fromRGB(29, 21, 34), 0.15
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Parent = kurz
end
kurz.Parent = workspace
local KOLORY_KURZU = { Color3.fromRGB(206, 201, 194), Color3.fromRGB(186, 181, 175), Color3.fromRGB(224, 220, 213) }
local los = Random.new()

-- Rysowany kurz z Higgsfield (Paweł 26.11: „bardziej kreskówkowy, z obramowaniem jak nasze”): cztery klatki jednego
-- obłoczka (assets/processed/KurzBiegu1–4.png). Identyfikatory wpisujemy po wgraniu do Roblox; dopóki lista jest
-- pusta, kurz robią kulki poniżej.
local KURZ_KLATKI: { string } = { -- wgrane 26.11 po „tak” Pawła (assets/manifest.json: KurzBiegu1–4)
	"rbxassetid://110676510504127", "rbxassetid://139600645021042", "rbxassetid://109464770833882", "rbxassetid://137204037845094",
}
local ROZMIAR_KLATKI = { 0.55, 0.85, 1.0, 0.8 }

local function obloczekRysowany(poz: Vector3, doTylu: Vector3, skala: number)
	local bok = doTylu:Cross(Vector3.yAxis)
	local p = Instance.new("Part")
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
	p.Transparency, p.Size = 1, Vector3.one * 0.05
	local start = poz + doTylu * los:NextNumber(0.15, 0.35) + bok * los:NextNumber(-0.2, 0.2) + Vector3.new(0, 0.3 * skala, 0)
	p.Position = start
	local w = 1.1 * skala * los:NextNumber(0.85, 1.15)
	local bb = Instance.new("BillboardGui")
	bb.Adornee, bb.LightInfluence, bb.MaxDistance = p, 0, 120
	bb.Size = UDim2.fromScale(w * ROZMIAR_KLATKI[1], w * ROZMIAR_KLATKI[1])
	local im = Instance.new("ImageLabel")
	im.BackgroundTransparency, im.Size, im.ScaleType = 1, UDim2.fromScale(1, 1), Enum.ScaleType.Fit
	im.Image, im.Rotation = KURZ_KLATKI[1], los:NextNumber(-14, 14)
	im.Parent = bb
	bb.Parent = p
	p.Parent = kurz
	TS:Create(p, TweenInfo.new(0.46, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Position = start + doTylu * los:NextNumber(0.35, 0.6) + Vector3.new(0, los:NextNumber(0.3, 0.5), 0) }):Play()
	task.spawn(function()
		for i = 2, 4 do
			task.wait(0.11)
			im.Image = KURZ_KLATKI[i]
			bb.Size = UDim2.fromScale(w * ROZMIAR_KLATKI[i], w * ROZMIAR_KLATKI[i])
		end
		TS:Create(im, TweenInfo.new(0.13), { ImageTransparency = 1 }):Play()
		task.wait(0.14)
		p:Destroy()
	end)
end

function obloczek(poz: Vector3, doTylu: Vector3, skala: number)
	if #KURZ_KLATKI >= 4 then
		obloczekRysowany(poz, doTylu, skala)
		return
	end
	local bok = doTylu:Cross(Vector3.yAxis)
	for i = 1, 3 do
		local p = Instance.new("Part")
		p.Shape = Enum.PartType.Ball
		p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
		p.Material, p.Color = Enum.Material.SmoothPlastic, KOLORY_KURZU[los:NextInteger(1, #KOLORY_KURZU)]
		local r = los:NextNumber(0.3, 0.46) * skala
		local start = poz + doTylu * los:NextNumber(0.1, 0.3) + bok * los:NextNumber(-0.25, 0.25) + Vector3.new(0, r * 0.45, 0)
		p.Size, p.Position, p.Transparency = Vector3.one * r, start, 0.1
		p.Parent = kurz
		local cel = start + doTylu * los:NextNumber(0.25, 0.55) + bok * los:NextNumber(-0.2, 0.2) + Vector3.new(0, los:NextNumber(0.2, 0.45), 0)
		local rosnie = TS:Create(p, TweenInfo.new(0.16, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
			{ Size = Vector3.one * r * 2.1, Position = start:Lerp(cel, 0.5) })
		rosnie.Completed:Once(function()
			TS:Create(p, TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
				{ Size = Vector3.one * 0.04, Position = cel, Transparency = 0.85 }):Play()
		end)
		rosnie:Play()
		task.delay(0.5 + i * 0.02, function()
			p:Destroy()
		end)
	end
end

------------------------------------------------------------ awatar
local function schowajAwatara(char: Model)
	for _, d in ipairs(char:GetDescendants()) do
		if (d:IsA("BasePart") or d:IsA("Decal")) and d.Transparency < 1 then
			d:SetAttribute("KotRasyT", d.Transparency)
			d.Transparency = 1
		end
	end
end

local function odslonAwatara(char: Model?)
	if not char then
		return
	end
	for _, d in ipairs(char:GetDescendants()) do
		if d:IsA("BasePart") or d:IsA("Decal") then
			local t = d:GetAttribute("KotRasyT")
			if typeof(t) == "number" then
				d.Transparency = t
				d:SetAttribute("KotRasyT", nil)
			end
		end
	end
end

------------------------------------------------------------ budowa kota
local function usun(gracz: Player)
	local s = koty[gracz]
	if not s then
		return
	end
	koty[gracz] = nil
	s.model:Destroy()
	odslonAwatara(s.char)
end

-- agent Karola, 27.11 (Karol: „UI broni … bronie zakładane na kota”): założona broń z puli Lv 1–10. Kowal Karola zakłada
-- ją w przymierzalni (atrybut gracza StrojProba_<klasa> = „id,id,…”, widoczny dla wszystkich); model to Accessory
-- ReplicatedStorage.BronieKlas.<id> (uchwyt Handle, zaczep chwytu = środek pięści, oś broni +Y — jak broń startowa).
local KLASA_KOWALA = { Warrior = "wojownik", Scout = "zwiadowca", Mage = "mag" }
local function bronZKowala(gracz: Player?, klasa: string): Accessory?
	local bronie = RS:FindFirstChild("BronieKlas")
	local k = KLASA_KOWALA[klasa]
	local napis = gracz and k and gracz:GetAttribute("StrojProba_" .. k)
	if not (bronie and type(napis) == "string") then
		return nil
	end
	for id in string.gmatch(napis, "[^,]+") do
		local a = bronie:FindFirstChild(id)
		if a and a:IsA("Accessory") then
			return a
		end
	end
	return nil
end
local function idBroni(gracz: Player, klasa: string): string
	local a = bronZKowala(gracz, klasa)
	return if a then a.Name else ""
end
local function modelBroni(a: Accessory): Model?
	local h = a:FindFirstChild("Handle")
	local z = h and (h:FindFirstChild("RightGripAttachment") or h:FindFirstChild("LeftGripAttachment"))
	if not (h and h:IsA("BasePart") and z and z:IsA("Attachment")) then
		return nil
	end
	local m = Instance.new("Model")
	m.Name = a.Name
	local hc = h:Clone()
	hc.Parent = m
	m.PrimaryPart = hc
	m.WorldPivot = hc.CFrame * z.CFrame -- pivot = środek chwytu (tak PivotTo niżej kładzie broń startową)
	return m
end

local function dajBron(s: any, klasa: string, gracz: Player?)
	local modele = RS:FindFirstChild("WyborKlasyModele")
	local wzor = modele and (modele:FindFirstChild("Weapon_" .. klasa .. "_Kot") or modele:FindFirstChild("Weapon_" .. klasa))
	local zKowala = bronZKowala(gracz, klasa) -- agent Karola, 27.11: założona broń z puli zamiast startowej
	local wlasna = zKowala and modelBroni(zKowala)
	s.bronId = if wlasna and zKowala then zKowala.Name else ""
	local zaczep = s.model:FindFirstChild("RightGripAttachment", true)
	if not ((wlasna or (wzor and wzor:IsA("Model"))) and zaczep and zaczep:IsA("Attachment")) then
		return
	end
	local b = wlasna or wzor:Clone()
	b.Name = "Bron"
	-- Paweł 26.11: broń niesiona prawie poziomo przed kotem, końcem lekko ku ziemi (nie pionowo jak kostur maga).
	-- Ustawiamy ją w pozie spoczynkowej (łapa zwisa): oś broni (+Y modelu) = przód kota pochylony w dół; kąt
	-- pochylenia najwyżej 15° i taki, żeby koniec broni nie wchodził w ziemię.
	local _, rozmiar = b:GetBoundingBox()
	local dlugosc = math.max(rozmiar.Y, 0.5)
	local nadZiemia = zaczep.WorldPosition.Y - (s.hrp.Position.Y - s.wys)
	local kat = math.clamp(math.asin(math.clamp((nadZiemia - 0.25) / dlugosc, -1, 1)), math.rad(4), math.rad(15))
	local przod, gora, prawo = s.hrp.CFrame.LookVector, s.hrp.CFrame.UpVector, s.hrp.CFrame.RightVector
	local osBroni = (przod * math.cos(kat) - gora * math.sin(kat)).Unit
	b:PivotTo(CFrame.fromMatrix(zaczep.WorldPosition, prawo, osBroni, prawo:Cross(osBroni)))
	local czesci = {}
	for _, d in ipairs(b:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored, d.CanCollide, d.CanQuery, d.CanTouch, d.Massless = false, false, false, false, true
			local w = Instance.new("WeldConstraint")
			w.Part0, w.Part1 = zaczep.Parent, d
			w.Parent = d
			table.insert(czesci, d)
			table.insert(s.czesci, d)
		end
	end
	b.Parent = s.model
	s.bron, s.bronCzesci = b, czesci
end

local function zbuduj(gracz: Player, rasa: string, klasa: string, char: Model)
	usun(gracz)
	local wzor = folder:FindFirstChild("Race_" .. rasa)
	if not (wzor and wzor:IsA("Model")) then
		return nil
	end
	local m = wzor:Clone()
	m.Name = gracz.Name
	local skala = folder:GetAttribute("Skala") or 1
	if skala ~= 1 then
		m:ScaleTo(skala)
	end
	local hrp = m:FindFirstChild("HumanoidRootPart") :: BasePart
	local s = {
		model = m, hrp = hrp, czesci = {}, tory = {}, stawy = {}, rasa = rasa, klasa = klasa, char = char,
		wys = (wzor:GetAttribute("WysHRP") or 0.75) * skala, przezr = 0, stan = "", bronWidac = true,
		poprzPoz = nil, ostatnieChowanie = 0,
	}
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = d == hrp
			d.CanCollide, d.CanQuery, d.CanTouch, d.Massless = false, false, false, true
			table.insert(s.czesci, d)
		elseif d:IsA("Motor6D") then
			s.stawy[d.Name] = d
		end
	end
	dajBron(s, klasa, gracz) -- w pozie spoczynkowej, zanim ruszą klipy
	m.Parent = lokalne
	local ac = m:FindFirstChildOfClass("AnimationController")
	local animator = ac and (ac:FindFirstChildOfClass("Animator") or Instance.new("Animator", ac))
	local saves = m:FindFirstChild("AnimSaves")
	if animator and saves then
		for _, nazwa in ipairs(KLIPY) do
			local ks = saves:FindFirstChild(nazwa)
			if ks and ks:IsA("KeyframeSequence") then
				if not idKlipu[nazwa] then
					local ok, id = pcall(function()
						return KSP:RegisterKeyframeSequence(ks)
					end)
					if ok then
						idKlipu[nazwa] = id
					else
						warn("[KotRasySwiat] klip " .. nazwa .. " nie dał się zarejestrować (poza Studio trzeba wgrać animacje): " .. tostring(id))
					end
				end
				if idKlipu[nazwa] then
					local a = Instance.new("Animation")
					a.AnimationId = idKlipu[nazwa]
					local t = animator:LoadAnimation(a)
					t.Looped = RUCH[nazwa] == true
					t.Priority = if nazwa == "idle" then Enum.AnimationPriority.Idle
						elseif RUCH[nazwa] then Enum.AnimationPriority.Movement
						else Enum.AnimationPriority.Action
					s.tory[nazwa] = t
				end
			end
		end
	end
	if s.tory.idle then
		s.tory.idle:Play(0)
	end
	schowajAwatara(char)
	koty[gracz] = s
	return s
end

------------------------------------------------------------ klatka
local function ustawStan(s: any, stan: string, tempo: number)
	if s.stan ~= stan then
		local stary = s.tory[s.stan]
		if stary and s.stan ~= "idle" then
			stary:Stop(0.14)
		end
		local nowy = s.tory[stan]
		if nowy and stan ~= "idle" then
			nowy:Play(if stan == "upadek" then 0.1 else 0.14)
		end
		s.stan = stan
	end
	local t = s.tory[stan]
	if t and stan ~= "idle" then
		if stan == "upadek" then
			-- nie w pętli: zatrzymaj na ostatniej klatce (kot leży do odrodzenia)
			if t.Length > 0 and t.TimePosition >= t.Length - 0.05 then
				t:AdjustSpeed(0)
			end
		else
			t:AdjustSpeed(tempo)
		end
	end
end

local function klatka(gracz: Player, s: any, dt: number)
	local char = s.char
	local chrp = char:FindFirstChild("HumanoidRootPart") :: BasePart?
	local hum = char:FindFirstChildOfClass("Humanoid")
	if not (chrp and hum) then
		return
	end
	-- awatar: części dochodzą po czasie (akcesoria), więc co pół sekundy chowamy to, co doszło
	local teraz = os.clock()
	if teraz - s.ostatnieChowanie > 0.5 then
		s.ostatnieChowanie = teraz
		schowajAwatara(char)
	end
	-- kot stoi stopami w punkcie pod postacią i przyjmuje jej obrót (także gdy trening kładzie postać na ławce)
	s.hrp.CFrame = chrp.CFrame * CFrame.new(0, s.wys - hum.HipHeight - chrp.Size.Y / 2, 0)
	-- znika razem z awatarem
	local glowa = char:FindFirstChild("Head")
	local x = if glowa and glowa:IsA("BasePart") then glowa.LocalTransparencyModifier else 0
	if math.abs(x - s.przezr) > 0.01 then
		s.przezr = x
		for _, p in ipairs(s.czesci) do
			p.LocalTransparencyModifier = x
		end
	end
	-- broń wyjęta albo schowana
	local wyjeta = gracz:GetAttribute("BronWyjeta") == true
	if s.bronCzesci and wyjeta ~= s.bronWidac then
		s.bronWidac = wyjeta
		for _, p in ipairs(s.bronCzesci) do
			p.Transparency = if wyjeta then (p:GetAttribute("KotRasyT0") or 0) else 1
		end
	end
	-- trening AFK przejął awatara (jego skrypt Animate jest wyłączony): kot powtarza pozę stawów awatara
	local animate = char:FindFirstChild("Animate")
	s.trening = gracz == player and animate ~= nil and animate:IsA("LocalScript") and animate.Disabled and hum.Health > 0
	s.zywy, s.wyjeta = hum.Health > 0, wyjeta
	if s.trening then
		ustawStan(s, "idle", 1) -- pozy stawów przepisuje poAnimatorze()
		return
	end
	-- stan ruchu: prędkość z fizyki dla siebie, z przesunięcia dla innych graczy (ich prędkość nie zawsze dochodzi)
	local v = chrp.AssemblyLinearVelocity
	if gracz ~= player and s.poprzPoz and dt > 0 then
		local d = (chrp.Position - s.poprzPoz) / dt
		if d.Magnitude < 200 then
			v = v:Lerp(d, 0.5)
		end
	end
	s.poprzPoz = chrp.Position
	local predkosc = Vector3.new(v.X, 0, v.Z).Magnitude
	local stanH = hum:GetState()
	local wPowietrzu = hum.FloorMaterial == Enum.Material.Air or stanH == Enum.HumanoidStateType.Freefall
		or stanH == Enum.HumanoidStateType.Jumping
	if hum.Health <= 0 then
		ustawStan(s, "upadek", 1)
	elseif wPowietrzu then
		ustawStan(s, if v.Y > 3 then "skok" else "spadanie", 1)
	elseif predkosc > 9 then
		ustawStan(s, "bieg", math.clamp(predkosc / 16, 0.6, 1.6))
	elseif predkosc > 0.8 then
		ustawStan(s, "chod", math.clamp(predkosc / 4.5, 0.6, 2))
	else
		ustawStan(s, "idle", 1)
	end
	-- kurz spod łap: obłoczek przy każdym kroku biegu i większy przy lądowaniu
	local ziemia = s.hrp.Position.Y - s.wys
	if s.bylWPowietrzu and not wPowietrzu and s.przezr < 0.5 then
		for _ = 1, 4 do
			obloczek(Vector3.new(s.hrp.Position.X, ziemia, s.hrp.Position.Z), -s.hrp.CFrame.LookVector, 1.25)
		end
	end
	s.bylWPowietrzu, s.wPowietrzu = wPowietrzu, wPowietrzu
	if s.stan == "bieg" and s.przezr < 0.5 then
		s.kurzT = (s.kurzT or 0) - dt
		if s.kurzT <= 0 then
			s.kurzT = 0.2 / math.clamp(predkosc / 16, 0.6, 1.6)
			s.kurzLewa = not s.kurzLewa
			local stopa = s.model:FindFirstChild(if s.kurzLewa then "LeftFoot" else "RightFoot")
			local p = if stopa and stopa:IsA("BasePart") then stopa.Position else s.hrp.Position
			obloczek(Vector3.new(p.X, ziemia, p.Z), -s.hrp.CFrame.LookVector, 1)
		end
	end
end

-- Po Animatorze (PreSimulation): to, co tu wpiszemy w stawy, zostaje do narysowania klatki. Wpisane w pętli
-- renderowania byłoby nadpisane przez Animator jeszcze przed rysowaniem — dlatego prawa łapa stała w miejscu.
local function poAnimatorze(gracz: Player, s: any)
	if not s.zywy then
		return
	end
	if s.trening then
		-- trening AFK przejął awatara: kot powtarza pozę jego stawów (te same nazwy)
		for nazwa, staw in pairs(s.stawy) do
			local a = s.char:FindFirstChild(nazwa, true)
			if a and (a:IsA("Motor6D") or a:IsA("AnimationConstraint")) then
				staw.Transform = (a :: any).Transform
			end
		end
		return
	end
	if s.akcja and s.akcja.IsPlaying then
		return -- klip akcji (atak, czar, wiwat…) sam prowadzi prawą łapę
	end
	-- Prawa łapa (Paweł 26.11): klipy ruchu Kota-Maga trzymają ją nieruchomo w pozie „niosę kostur pionowo”.
	-- Tutaj pracuje jak lewa — w chodzie i biegu naprzemiennie, w locie lustrzanie — więc łapa (i broń w niej)
	-- kołysze się z krokiem. Z wyjętą bronią wymach jest mniejszy (0,6), żeby broń nie latała jak wahadło.
	local lewy, lokiec = s.stawy.LeftShoulder, s.stawy.LeftElbow
	if lewy and s.stawy.RightShoulder then
		local rx, ry, rz = lewy.Transform:ToEulerAnglesXYZ()
		local cel = if s.wPowietrzu then CFrame.Angles(rx, -ry, -rz) else CFrame.Angles(-rx, -ry, -rz)
		s.stawy.RightShoulder.Transform = if s.wyjeta then CFrame.identity:Lerp(cel, 0.6) else cel
	end
	if lokiec and s.stawy.RightElbow then
		local rx, ry, rz = lokiec.Transform:ToEulerAnglesXYZ()
		s.stawy.RightElbow.Transform = CFrame.Angles(rx, -ry, -rz)
	end
	if s.stawy.RightWrist then
		s.stawy.RightWrist.Transform = CFrame.identity
	end
end
RunService.PreSimulation:Connect(function()
	for gracz, s in pairs(koty) do
		poAnimatorze(gracz, s)
	end
end)

-- po animatorze i po pętli treningu AFK (Last + 1), żeby pozy z tej klatki były już policzone
RunService:BindToRenderStep("KotRasySwiat", Enum.RenderPriority.Last.Value + 2, function(dt)
	local wlaczone = folder:GetAttribute("Wlaczone") ~= false
	for _, gracz in ipairs(Players:GetPlayers()) do
		local rasa, klasa = gracz:GetAttribute("Race"), gracz:GetAttribute("Class")
		local char = gracz.Character
		local s = koty[gracz]
		if wlaczone and typeof(rasa) == "string" and typeof(klasa) == "string" and char and char.Parent
			and char:FindFirstChild("HumanoidRootPart") then
			if not s or s.rasa ~= rasa or s.klasa ~= klasa or s.char ~= char
				or s.bronId ~= idBroni(gracz, klasa) then -- agent Karola, 27.11: zmiana broni u kowala
				s = zbuduj(gracz, rasa, klasa, char)
				if not s then
					koty[gracz] = nil
				end
			end
			if s then
				klatka(gracz, s, dt)
			end
		elseif s then
			usun(gracz)
		end
	end
end)
Players.PlayerRemoving:Connect(usun)

------------------------------------------------------------ slot broni „1”
local gui = Instance.new("ScreenGui")
gui.Name = "PasekBroni"
gui.ResetOnSpawn, gui.IgnoreGuiInset, gui.DisplayOrder, gui.Enabled = false, true, 4, false
local slot = Instance.new("ImageButton")
slot.Name = "Slot1"
slot.AnchorPoint, slot.Position = Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -18)
slot.Size = UDim2.fromScale(0.07, 0.07)
-- ramka slotu z Higgsfield, dwa stany (assets/manifest.json: SlotBroni, SlotBroniAktywny; wgrane 26.11 po „tak” Pawła)
local SLOT_OBRAZ, SLOT_OBRAZ_AKTYWNY = "rbxassetid://121603960879005", "rbxassetid://98255064349130"
slot.BackgroundTransparency, slot.AutoButtonColor, slot.Image, slot.ScaleType = 1, false, SLOT_OBRAZ, Enum.ScaleType.Fit
local proporcje = Instance.new("UIAspectRatioConstraint")
proporcje.AspectRatio, proporcje.DominantAxis = 1, Enum.DominantAxis.Width
proporcje.Parent = slot
local minimum = Instance.new("UISizeConstraint")
minimum.MinSize, minimum.MaxSize = Vector2.new(64, 64), Vector2.new(108, 108)
minimum.Parent = slot
local rog = Instance.new("UICorner")
rog.CornerRadius = UDim.new(0.2, 0)
rog.Parent = slot
local ramka = Instance.new("UIStroke")
ramka.Thickness, ramka.Color, ramka.Enabled = 3, Color3.fromRGB(26, 20, 16), false -- ramkę rysuje obraz
ramka.Parent = slot
local ikona = Instance.new("ImageLabel")
ikona.Name = "Ikona"
ikona.BackgroundTransparency = 1
ikona.AnchorPoint, ikona.Position, ikona.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.53, 0.56), UDim2.fromScale(0.56, 0.56)
ikona.ScaleType = Enum.ScaleType.Fit
ikona.Parent = slot
local numer = Instance.new("TextLabel")
numer.Name = "Numer"
numer.Position, numer.Size = UDim2.fromScale(0.045, 0.035), UDim2.fromScale(0.26, 0.26) -- na złotej plakietce obrazu
numer.BackgroundTransparency, numer.TextColor3, numer.Text = 1, Color3.fromRGB(74, 46, 26), "1"
numer.FontFace, numer.TextScaled = Font.new("rbxasset://fonts/families/LuckiestGuy.json"), true
local numerRog = Instance.new("UICorner")
numerRog.CornerRadius = UDim.new(0.5, 0)
numerRog.Parent = numer
local numerRamka = Instance.new("UIStroke")
numerRamka.Thickness, numerRamka.Color, numerRamka.Enabled = 2, Color3.fromRGB(26, 20, 16), false
numerRamka.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
numerRamka.Parent = numer
numer.Parent = slot
local skalaSlotu = Instance.new("UIScale")
skalaSlotu.Parent = slot
slot.Parent = gui
gui.Parent = player:WaitForChild("PlayerGui")

local function rysujSlot()
	local wyjeta = player:GetAttribute("BronWyjeta") == true
	slot.Image = if wyjeta then SLOT_OBRAZ_AKTYWNY else SLOT_OBRAZ
	ikona.ImageTransparency = if wyjeta then 0 else 0.35
	local zKowala = bronZKowala(player, player:GetAttribute("Class") or "") -- agent Karola, 27.11
	ikona.Image = (zKowala and zKowala:GetAttribute("Ikona")) or IKONY_BRONI[player:GetAttribute("Class") or ""] or ""
end

local function przelacz()
	if not (gui.Enabled and bronEv) then
		return
	end
	bronEv:FireServer(player:GetAttribute("BronWyjeta") ~= true)
	skalaSlotu.Scale = 0.88
	TS:Create(skalaSlotu, TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

slot.Activated:Connect(przelacz)
UIS.InputBegan:Connect(function(input, zajete)
	if not zajete and (input.KeyCode == Enum.KeyCode.One or input.KeyCode == Enum.KeyCode.KeypadOne) then
		przelacz()
	end
end)
player:GetAttributeChangedSignal("BronWyjeta"):Connect(rysujSlot)
player:GetAttributeChangedSignal("Class"):Connect(rysujSlot)
player.AttributeChanged:Connect(function(n) -- agent Karola, 27.11: broń założona u kowala
	if string.sub(n, 1, 11) == "StrojProba_" then
		rysujSlot()
	end
end)
rysujSlot()

-- Podgląd klipów Kota-Maga Karola na kocie gracza (Paweł 26.11: „żebym widział je na każdym modelu kotka”) — tylko
-- w Studio. Klipy są skopiowane do figur przy budowie; pliki Karola bez zmian. Widzi je tylko ten gracz.
if RunService:IsStudio() then
	local panel = Instance.new("Frame")
	panel.Name = "PodgladKlipow"
	panel.AnchorPoint, panel.Position = Vector2.new(1, 1), UDim2.new(1, -12, 1, -18)
	panel.Size = UDim2.fromOffset(132, #AKCJE * 24 + 30)
	panel.BackgroundColor3, panel.BackgroundTransparency, panel.BorderSizePixel = Color3.fromRGB(43, 33, 26), 0.15, 0
	local pr = Instance.new("UICorner")
	pr.CornerRadius = UDim.new(0, 8)
	pr.Parent = panel
	local tytul = Instance.new("TextLabel")
	tytul.BackgroundTransparency, tytul.Size, tytul.Position = 1, UDim2.new(1, 0, 0, 22), UDim2.fromOffset(0, 3)
	tytul.Font, tytul.TextSize, tytul.TextColor3, tytul.Text = Enum.Font.GothamBold, 12, Color3.fromRGB(255, 196, 64), "ANIMACJE (podgląd)"
	tytul.Parent = panel
	for i, nazwa in ipairs(AKCJE) do
		local b = Instance.new("TextButton")
		b.Name = nazwa
		b.Position, b.Size = UDim2.fromOffset(6, 26 + (i - 1) * 24), UDim2.new(1, -12, 0, 21)
		b.BackgroundColor3, b.BorderSizePixel = Color3.fromRGB(92, 62, 34), 0
		b.Font, b.TextSize, b.TextColor3, b.Text = Enum.Font.GothamMedium, 12, Color3.new(1, 1, 1), nazwa
		local br = Instance.new("UICorner")
		br.CornerRadius = UDim.new(0, 5)
		br.Parent = b
		b.Activated:Connect(function()
			local s = koty[player]
			local t = s and s.tory[nazwa]
			if not t then
				return
			end
			if s.akcja and s.akcja.IsPlaying then
				s.akcja:Stop(0.1)
			end
			t:Play(0.1)
			t:AdjustSpeed(1)
			s.akcja = t
		end)
		b.Parent = panel
	end
	panel.Parent = gui
end

-- slot widać wtedy, gdy gracz ma kota i widać zwykły HUD (nie przy wyborze klasy, w walce ani przy stole mistrza gier)
task.spawn(function()
	while true do
		local hud = player.PlayerGui:FindFirstChild("HUD")
		gui.Enabled = koty[player] ~= nil and hud ~= nil and hud:IsA("ScreenGui") and hud.Enabled
		task.wait(0.25)
	end
end)

-- Paweł 28.11 („wygląda to bardzo dobrze, zapisz”): lekki ciemny obrys własnego kota i własnego peta. Tylko u tego
-- gracza i tylko jego para — silnik rysuje naraz najwyżej 31 Highlightów, a gra ma ich już ponad 30 (sala wyboru
-- klasy, plansza mistrza gier), więc obrysy wszystkich graczy by się nie zmieściły. Z tego samego powodu kontury makiet
-- (MiasteczkoLowPolyPodglad, LasLowPolyPodglad) są włączone tylko wtedy, gdy kamera jest blisko nich.
-- Pet to model „Pet <id>” z lokalnych petów Karola (Workspace/PetyProba/PetyLokalne): dokładamy mu tylko obrys.
local TUSZ_KONTURU = Color3.fromRGB(46, 32, 34)
local MAKIETY = { MiasteczkoLowPolyPodglad = Vector3.new(976, 0, -500), LasLowPolyPodglad = Vector3.new(826, 0, -500) }
local function konturNa(m: Instance)
	if m:FindFirstChild("KonturGracza") then
		return
	end
	local h = Instance.new("Highlight")
	h.Name = "KonturGracza"
	h.FillTransparency, h.OutlineTransparency = 1, 0.25
	h.OutlineColor = TUSZ_KONTURU
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Parent = m
end
task.spawn(function()
	while true do
		local s = koty[player]
		if s and s.model and s.model.Parent then
			konturNa(s.model)
			local petyGra = workspace:FindFirstChild("PetyProba")
			local pety = petyGra and petyGra:FindFirstChild("PetyLokalne")
			local aktywny = player:GetAttribute("PetAktywny")
			if pety then
				local najblizszy, odl = nil, 40
				if type(aktywny) == "string" and aktywny ~= "" then
					local tu = s.model:GetPivot().Position
					for _, c in ipairs(pety:GetChildren()) do
						if c:IsA("Model") and c.Name == "Pet " .. aktywny then
							local d = (c:GetPivot().Position - tu).Magnitude
							if d < odl then
								najblizszy, odl = c, d
							end
						end
					end
				end
				for _, c in ipairs(pety:GetChildren()) do
					local h = c:FindFirstChild("KonturGracza")
					if h and c ~= najblizszy then
						h:Destroy()
					end
				end
				if najblizszy then
					konturNa(najblizszy)
				end
			end
		end
		local kam = workspace.CurrentCamera.CFrame.Position
		for nazwa, srodek in pairs(MAKIETY) do
			local k = workspace:FindFirstChild(nazwa)
			if k then
				local blisko = (Vector3.new(kam.X, 0, kam.Z) - srodek).Magnitude < 260
				for _, g in ipairs(k:GetChildren()) do
					local h = g:FindFirstChild("Kontur")
					if h and h:IsA("Highlight") and h.Enabled ~= blisko then
						h.Enabled = blisko
					end
				end
			end
		end
		task.wait(0.5)
	end
end)
