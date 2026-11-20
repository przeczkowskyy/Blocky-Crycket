--[[
	KlientPetArena — klient gry Pet Arena (Script, RunContext Client, w Workspace/PetArenaGra). Rysuje to, co liczy
	serwer: pety z wzorców (wygładzanie między migawkami Sygnaly/Stan), lot rzutu po łuku z ręki awatara, RING OUT
	(fosa, rozbryzg, gejzer, łuk do właściciela) i KO (gwiazdki, wirujący lot przez pół ekranu), koronę, cienkie paski
	życia nad petami (warstwa 2D), efekty, ekran (InterfejsPetArena) i okna (OknaPetArena: jajka, pety, Księga,
	wyklucie), kamerę stałą nad areną. Etap 2: większe pety, słowa komiksowe tylko dla własnego peta i wielkich chwil
	(najwyżej 2 duże naraz, krótko), błysk i podskok po ciosie, zatrzymanie i wstrząs kamery przy wielkich wybiciach,
	smuga lotu, zamach ręki awatara i pet w dłoni, ćwiczenia na macie, BOSS i GOLDEN PET, napisy nad graczami.

	Wejście: telefon — stuknięcie w arenę, komputer — klik (podgląd celu), 1/2/3 — wybór, spacja/Q — umiejętność,
	E — jajka, P — pety, T — trening; pad — lewa gałka celownik, A rzut, X umiejętność, LB/RB wybór, Y pety, w górę
	jajka, w dół trening, B zamyka okno (w oknie A klika zaznaczony przycisk). Do serwera tylko Sygnaly/Akcja.

	Haczyki prób: Sygnaly/SterowanieKlienta (BindableFunction): "stan", "rzut" (x, z — droga stuknięcia),
	"umiejetnosc", "wybierz", "emulacja", "pomiar_zeruj", "kamera_wolna", "kadr", "okno" (nazwa | nil), "jajko" (nr — jak
	przycisk HATCH), "druzyna_ui" (id — jak dotknięcie w kolekcji), "trening", "pad" (nazwa KeyCode), "kamera" (opcje
	kamery filmowej | nil).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local GuiService = game:GetService("GuiService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local Moduly = kontener:WaitForChild("Moduly")
local D = require(Moduly:WaitForChild("DanePetArena"))
local L = require(Moduly:WaitForChild("LogikaPetArena"))
local Efekty = require(Moduly:WaitForChild("EfektyPetArena"))
local Interfejs = require(Moduly:WaitForChild("InterfejsPetArena"))
local Okna = require(Moduly:WaitForChild("OknaPetArena"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evAkcja = Sygnaly:WaitForChild("Akcja")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local evStan = Sygnaly:WaitForChild("Stan")
local sterowanie = Sygnaly:WaitForChild("SterowanieKlienta")
local P = D.prefiks

kontener:SetAttribute("KlientGotowy", false)
if kontener:GetAttribute(D.wylacznik) == false then
	return
end

local wzorce = ReplicatedStorage:WaitForChild(D.folderWzorcow, 20)
local lokalne = Instance.new("Folder")
lokalne.Name = "PetArenaLokalne"
lokalne.Parent = workspace
local E = Efekty.nowe(lokalne, D)
local kamera = workspace.CurrentCamera
local K = D.ui.kolory
local tusz = Color3.fromHex(K.tusz)
local czcionka = Enum.Font[D.ui.czcionka] or Enum.Font.LuckiestGuy
local cyfry = Enum.Font[D.ui.czcionka_cyfr] or Enum.Font.FredokaOne
local R = D.scena.arena_r

local function teraz(): number
	return workspace:GetServerTimeNow()
end

local function mojSlot(): number
	return gracz:GetAttribute("PA_Slot") or 0
end

local function kolorSlotu(slot: number): string
	local s = D.sloty[slot]
	return if s then s.kolor else K.dziki
end

------------------------------------------------------------------ dźwięki (odcinki arkusza efektów)
local folderDzwiekow = Instance.new("Folder")
folderDzwiekow.Name = "PetArenaDzwieki"
folderDzwiekow.Parent = SoundService
local pule: { [string]: { s: { Sound }, i: number } } = {}
local DZ = D.dzwieki
local graneDzwieki = 0
if DZ.arkusz and DZ.arkusz > 0 then
	for rola, e in DZ.efekty do
		local lista = {}
		for i = 1, (if rola == "cios" then 4 else 2) do
			local s = Instance.new("Sound")
			s.Name = rola .. i
			s.SoundId = "rbxassetid://" .. tostring(DZ.arkusz)
			s.Volume = e.glosnosc
			s.PlaybackRegionsEnabled = true
			s.PlaybackRegion = NumberRange.new(e.od, e.koniec)
			s.Parent = folderDzwiekow
			table.insert(lista, s)
		end
		pule[rola] = { s = lista, i = 1 }
	end
end

local function dzwiek(rola: string, wysokosc: number?)
	local p = pule[rola]
	if not p then
		return
	end
	local s = p.s[p.i]
	p.i = (p.i % #p.s) + 1
	s.PlaybackSpeed = wysokosc or 1
	s.TimePosition = DZ.efekty[rola].od
	s:Play()
	graneDzwieki += 1
end

local function dzwiekiZaladowane(): (number, number)
	local n, z = 0, 0
	for _, s in folderDzwiekow:GetChildren() do
		if s:IsA("Sound") then
			n += 1
			if s.IsLoaded and s.TimeLength > 0 then
				z += 1
			end
		end
	end
	return z, n
end

------------------------------------------------------------------ warstwa 2D (napisy nad petami i graczami, słowa)
local playerGui = gracz:WaitForChild("PlayerGui")
local function skalaNapisow(): number
	local em = kontener:GetAttribute("EmulacjaEkranu")
	if typeof(em) ~= "Vector2" then
		return 1
	end
	local v = workspace.CurrentCamera.ViewportSize
	return math.min(v.X / em.X, (v.Y - 36) / em.Y)
end
local warstwa = Instance.new("ScreenGui")
warstwa.Name = "PetArenaNapisy"
warstwa.IgnoreGuiInset = true
warstwa.ResetOnSpawn = false
warstwa.DisplayOrder = 3
warstwa.Parent = playerGui
E:warstwa2D(warstwa)

-- słowa komiksowe: duże najwyżej 2 naraz i krótko; małe tylko przy ciosach własnego peta
local duzychSlow = 0
local duzychPomin = 0
local function duzeSlowo(poz: Vector3, tekst: string, kolor: Color3, wielkosc: number?)
	if duzychSlow >= 2 then
		duzychPomin += 1
		return
	end
	duzychSlow += 1
	E:slowo(poz, tekst, kolor, wielkosc or 1.1, 0.75, function()
		duzychSlow -= 1
	end)
end
local function maleSlowo(poz: Vector3, tekst: string, kolor: Color3)
	E:slowo(poz, tekst, kolor, 0.5, 0.5)
end

------------------------------------------------------------------ widoki petów
local widoki: { [number]: any } = {}
local czesciWidokow = 0
local krolId, nagrodaKrola = 0, 0
local nazwySlotow: { [number]: string } = {}
local pulsow = 0

local function opisBossa(nr: number)
	local B = D.boss.modele[nr - 200] or D.boss.modele[1]
	return { id = "boss", nazwa = B.nazwa, wzorzec = B.wzorzec, wysokosc = D.boss.wysokosc, promien = D.boss.promien, stopien = 5,
		umiejetnosc = { nazwa = "STOMP" }, boss = true }
end

local function wzorzec(nazwa: string): Model
	local wz = wzorce and wzorce:FindFirstChild(nazwa)
	if wz then
		return wz:Clone()
	end
	local m = Instance.new("Model")
	local p = Instance.new("Part")
	p.Name = "Korzen"
	p.Size = Vector3.new(3, 3, 3)
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Color = Color3.fromRGB(140, 200, 90)
	p.Parent = m
	m.PrimaryPart = p
	return m
end

local function liczCzesci(m: Instance): number
	local n = 0
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			n += 1
		end
	end
	return n
end

local function kolorKrazka(w): string
	if w.zloty then
		return D.zloty.kolor
	elseif w.boss then
		return "FF4D4D"
	elseif w.slot > 0 and w.slot == mojSlot() then
		return K.ty
	elseif w.slot > 0 then
		return kolorSlotu(w.slot)
	end
	return K.dziki
end

local function nowyWidok(id: number, nr: number, slot: number, x: number, z: number, f2: number?): any
	local Pd = if nr >= 200 then opisBossa(nr) else D.pety[nr]
	if not Pd then
		return nil
	end
	local m = wzorzec(Pd.wzorzec)
	local korzen = m.PrimaryPart :: BasePart
	korzen.Anchored = true
	m.Name = "Pet" .. id
	local zloty = f2 ~= nil and bit32.band(f2, 4) ~= 0
	local moj = slot > 0 and slot == mojSlot()
	local w: any = { id = id, nr = nr, Pd = Pd, slot = slot, model = m, korzen = korzen, x = x, z = z, tx = x, tz = z, y = 0, kier = 0,
		tkier = 0, hp = 1, hpMax = 1, pasek = 0, flagi = 0, f2 = f2 or 0, zl = 0, faza = 0, lot = nil, odlot = nil, skok = nil,
		trafienie = 0, blysk = 0, puls = nil, brak = 0, faza0 = math.random() * 6, gwiazdki = 1, boss = nr >= 200, zloty = zloty }
	local hl = Instance.new("Highlight")
	hl.FillTransparency = if zloty then 0.35 else 1
	hl.FillColor = Color3.fromHex(D.zloty.kolor)
	hl.OutlineColor = Color3.fromHex(kolorKrazka(w))
	hl.OutlineTransparency = if slot > 0 then 0 else 1
	hl.DepthMode = if moj then Enum.HighlightDepthMode.AlwaysOnTop else Enum.HighlightDepthMode.Occluded
	hl.Parent = m
	w.hl = hl
	local kr = Instance.new("Part")
	kr.Name = "Krazek"
	kr.Shape = Enum.PartType.Cylinder
	kr.Anchored = true
	kr.CanCollide = false
	kr.CanQuery = false
	kr.CanTouch = false
	kr.CastShadow = false
	kr.Material = Enum.Material.Neon
	kr.Color = Color3.fromHex(kolorKrazka(w))
	kr.Size = Vector3.new(0.12, Pd.promien * 2 + 1.2, Pd.promien * 2 + 1.2)
	kr.Parent = m
	w.krazek = kr
	m.Parent = lokalne
	-- napis nad petem: cienki pasek życia, gwiazdki, tarcza; własny: „+5 G/s”; dziki bez napisu (kolor krążka)
	local sn = skalaNapisow()
	local szer = math.clamp(Pd.promien * 18, 44, 80) * sn
	local et = Instance.new("Frame")
	et.Name = "Etykieta" .. id
	et.AnchorPoint = Vector2.new(0.5, 1)
	et.Size = UDim2.fromOffset(szer, 22 * sn)
	et.BackgroundTransparency = 1
	et.Visible = false
	et.Parent = warstwa
	local napis = Instance.new("TextLabel")
	napis.Name = "Napis"
	napis.BackgroundTransparency = 1
	napis.AnchorPoint = Vector2.new(0.5, 1)
	napis.Position = UDim2.new(0.5, 0, 1, -7 * sn)
	napis.Size = UDim2.fromOffset(szer * 1.6, 15 * sn)
	napis.TextScaled = true
	napis.Font = cyfry
	napis.TextColor3 = Color3.fromHex(if moj then K.ty else K.zloto)
	napis.Text = ""
	napis.Parent = et
	local o = Instance.new("UIStroke")
	o.Thickness = 1.5
	o.Color = tusz
	o.Parent = napis
	local ramka = Instance.new("Frame")
	ramka.Name = "Zycie"
	ramka.AnchorPoint = Vector2.new(0.5, 1)
	ramka.Position = UDim2.fromScale(0.5, 1)
	ramka.Size = UDim2.new(1, 0, 0, math.max(4, 5 * sn))
	ramka.BackgroundColor3 = tusz
	ramka.BorderSizePixel = 0
	ramka.Visible = not w.boss
	ramka.Parent = et
	local ob = Instance.new("UIStroke")
	ob.Thickness = if moj then 1.5 else 1
	ob.Color = Color3.fromHex(kolorKrazka(w))
	ob.Parent = ramka
	local pz = Instance.new("Frame")
	pz.Name = "W"
	pz.Size = UDim2.fromScale(1, 1)
	pz.BackgroundColor3 = Color3.fromHex(K.zycie)
	pz.BorderSizePixel = 0
	pz.Parent = ramka
	local ng = Instance.new("TextLabel")
	ng.Name = "Nagroda"
	ng.BackgroundTransparency = 1
	ng.AnchorPoint = Vector2.new(0.5, 1)
	ng.Position = UDim2.new(0.5, 0, 0, -16 * sn)
	ng.Size = UDim2.fromOffset(130 * sn, 20 * sn)
	ng.TextScaled = true
	ng.Font = cyfry
	ng.TextColor3 = Color3.fromHex(K.zloto)
	ng.Text = ""
	ng.Visible = false
	ng.Parent = et
	local o2 = Instance.new("UIStroke")
	o2.Thickness = 2
	o2.Color = tusz
	o2.Parent = ng
	w.etykieta, w.pasekZ, w.napis, w.nagrodaTekst = et, pz, napis, ng
	w.czesci = liczCzesci(m)
	czesciWidokow += w.czesci
	widoki[id] = w
	return w
end

local function usunWidok(w)
	czesciWidokow -= w.czesci
	w.model:Destroy()
	w.etykieta:Destroy()
	if widoki[w.id] == w then
		widoki[w.id] = nil
	end
end

------------------------------------------------------------------ korona króla (bryły, lokalnie)
local korona = Instance.new("Model")
korona.Name = "Korona"
do
	local zloto = Color3.fromHex("FFB000")
	local function c(rozmiar: Vector3, cf: CFrame, ksztalt: Enum.PartType?)
		local p = Instance.new("Part")
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.CastShadow = false
		p.Material = Enum.Material.SmoothPlastic
		p.Color = zloto
		p.Size = rozmiar
		p.Shape = ksztalt or Enum.PartType.Block
		p.CFrame = cf
		p.Parent = korona
		return p
	end
	local baza = c(Vector3.new(5, 1.3, 5), CFrame.new())
	korona.PrimaryPart = baza
	for i = 0, 4 do
		local a = i * math.pi * 2 / 5
		c(Vector3.new(1.1, 2.5, 1.1), CFrame.new(math.cos(a) * 2, 1.8, math.sin(a) * 2))
		c(Vector3.new(1, 1, 1), CFrame.new(math.cos(a) * 2, 3.3, math.sin(a) * 2), Enum.PartType.Ball)
	end
end
korona.Parent = nil

------------------------------------------------------------------ ekran i okna
local dotyk = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
local ui: any = nil
local okna: any = nil
local wybrany = 1
local ostatniaUmiejetnosc = 0
local uzylUmiejetnosci = false
local wyslane = 0
local padAktywny = false

local function kolekcja(): { [string]: number }
	local w = {}
	for _, s in string.split(gracz:GetAttribute("PA_Kolekcja") or "", ",") do
		local id, g = s:match("^([%w_]+):(%d+)$")
		if id then
			w[id] = tonumber(g)
		end
	end
	return w
end

local function druzynaLista()
	local wpisy = string.split(gracz:GetAttribute("PA_Druzyna") or "", ",")
	local odp = string.split(gracz:GetAttribute("PA_Odpoczynek") or "", ",")
	local naArenie = gracz:GetAttribute("PA_NaArenie") or 0
	local tn = teraz()
	local w = {}
	for i, s in wpisy do
		local id, g = s:match("^([%w_]+):(%d+)$")
		local nr = id and L.nrPeta(D, id)
		if nr then
			local Pd = D.pety[nr]
			local doKiedy = tonumber(odp[i]) or 0
			local stan = if naArenie == i then "arena" elseif doKiedy > tn then "odpoczynek" else "gotowy"
			table.insert(w, { id = id, nr = nr, nazwa = Pd.nazwa, kolor = D.rzadkosci[Pd.stopien].kolor, stan = stan,
				zostalo = math.max(0, math.ceil(doKiedy - tn)), gwiazdki = tonumber(g) or 1, wybrany = i == wybrany })
		end
	end
	return w
end

local function stanOkien()
	local sam = gracz:GetAttribute("PA_Samouczek") or "00"
	local dr = {}
	for _, w in druzynaLista() do
		table.insert(dr, w.id)
	end
	local ks = {}
	for _, id in string.split(gracz:GetAttribute("PA_Ksiega") or "", ",") do
		if id ~= "" then
			ks[id] = true
		end
	end
	return { zloto = gracz:GetAttribute("PA_Zloto") or 0, darmowe = string.sub(sam, 2, 2) ~= "1", kolekcja = kolekcja(), druzyna = dr, ksiega = ks }
end

local function wybierz(nr: number)
	wybrany = nr
	evAkcja:FireServer("wybierz", nr)
	wyslane += 1
	dzwiek("klik")
end

local function umiejetnosc()
	if os.clock() - ostatniaUmiejetnosc < 0.25 then
		return
	end
	ostatniaUmiejetnosc = os.clock()
	evAkcja:FireServer("umiejetnosc")
	wyslane += 1
end

local function przelaczOkno(nazwa: string)
	if okna:otwarte() == nazwa or (nazwa == "pety" and okna:otwarte() == "ksiega") then
		okna:zamknij()
	else
		okna.st = stanOkien()
		okna:otworz(nazwa)
		dzwiek("klik")
	end
end

local function trening()
	evAkcja:FireServer("trening", not (gracz:GetAttribute("PA_Trening") == true))
	wyslane += 1
	dzwiek("klik")
end

local function zbudujUI()
	if okna then
		okna:zamknij()
	end
	if ui then
		ui:zniszcz()
	end
	local em = kontener:GetAttribute("EmulacjaEkranu")
	if typeof(em) ~= "Vector2" then
		em = nil
	end
	ui = Interfejs.nowy(playerGui, D, L, { dotyk = dotyk or em ~= nil, emulacja = em, naWybor = wybierz, naUmiejetnosc = umiejetnosc,
		naJajka = function()
			przelaczOkno("jajka")
		end, naPety = function()
			przelaczOkno("pety")
		end, naTrening = trening })
	okna = Okna.nowe(ui.okno, D, L, wzorce, {
		skala = ui.skala,
		pad = function()
			return padAktywny
		end,
		naJajko = function(nr: number)
			evAkcja:FireServer("jajko", nr)
			wyslane += 1
			dzwiek("klik")
		end,
		naDruzyne = function(lista)
			evAkcja:FireServer("druzyna", lista)
			wyslane += 1
			dzwiek("klik")
		end,
		naPekniecie = function(rz: number)
			dzwiek("wyklucie")
			if rz >= 4 then
				dzwiek("krol")
			end
		end,
	})
end
zbudujUI()

------------------------------------------------------------------ kamera stała nad areną (wstrząs przy wielkich chwilach)
local kameraWolna = false
local kameraFilm: any = nil
local wstrzas = { do_ = 0, sila = 0 }
local stopDo = 0

local function pozycjaKamery(): (Vector3?, Vector3?)
	local s = D.sloty[mojSlot()]
	if not s then
		return nil, nil
	end
	local KK = D.kamera
	local e = math.rad(KK.nachylenie_st)
	local dx, dz = math.sin(s.katKamery), math.cos(s.katKamery)
	local odl = KK.cel_z + KK.odleglosc * math.cos(e)
	return Vector3.new(dx * odl, KK.odleglosc * math.sin(e), dz * odl), Vector3.new(dx * KK.cel_z, 0, dz * KK.cel_z)
end

local function wstrzasnij(sila: number, czas: number)
	wstrzas.sila = math.max(wstrzas.sila, sila)
	wstrzas.do_ = math.max(wstrzas.do_, os.clock() + czas)
end

local function zatrzymaj(czas: number)
	stopDo = math.max(stopDo, os.clock() + czas)
end

local function ustawKamere()
	if kameraWolna then
		return
	end
	local poz, cel = pozycjaKamery()
	if not poz or not cel then
		return
	end
	kamera.CameraType = Enum.CameraType.Scriptable
	kamera.FieldOfView = D.kamera.fov
	local cf = CFrame.lookAt(poz, cel)
	if kameraFilm then
		local f = kameraFilm
		if f.pozycja and f.cel then
			cf = CFrame.lookAt(f.pozycja, f.cel)
		elseif f.zoom then
			cf = CFrame.lookAt(poz:Lerp(cel, f.zoom), cel)
		end
		kamera.FieldOfView = f.fov or D.kamera.fov
	end
	local t = os.clock()
	if t < wstrzas.do_ then
		local s = wstrzas.sila * math.clamp((wstrzas.do_ - t) / 0.3, 0, 1)
		cf *= CFrame.new(math.noise(t * 25, 1) * s, math.noise(t * 25, 2) * s, 0)
	else
		wstrzas.sila = 0
	end
	kamera.CFrame = cf
end

-- sterowanie postacią wyłączone: gracz stoi na swoim miejscu, stuknięcia idą w arenę
task.spawn(function()
	local ok, modul = pcall(function()
		return require(gracz:WaitForChild("PlayerScripts"):WaitForChild("PlayerModule", 10))
	end)
	if ok and modul then
		pcall(function()
			modul:GetControls():Disable()
		end)
	end
end)

------------------------------------------------------------------ ręce awatarów: zamach przy rzucie, pet w dłoni, ćwiczenia
-- obrót stawu barku doklejony do Transform w PreSimulation (po animacjach) — sposób z BONK (stawy R15 to
-- AnimationConstraint albo Motor6D). Kąty w stopniach: x — ręka w przód/do góry, z — na bok.
local stawyPostaci: { [Model]: any } = {}
local zamachDo = 0
local zamachT0 = -1

local function staw(postac: Model, nazwa: string, nazwaR6: string): any
	local j = postac:FindFirstChild(nazwa, true)
	if not j then
		local tulow = postac:FindFirstChild("Torso")
		j = tulow and tulow:FindFirstChild(nazwaR6)
	end
	if j and (j:IsA("Motor6D") or j:IsA("AnimationConstraint")) then
		local rama = if j:IsA("Motor6D") then j.C0 else (j.Attachment0 and j.Attachment0.CFrame or CFrame.new())
		return { j = j, obr = rama.Rotation, dodatek = CFrame.new() }
	end
	return nil
end

local function ustawStaw(st: any, x: number, z: number)
	if st then
		st.dodatek = st.obr:Inverse() * CFrame.Angles(math.rad(x), 0, math.rad(z)) * st.obr
	end
end

local function doklejStaw(st: any)
	if not st then
		return
	end
	local j = st.j
	local biezacy = j.Transform
	local baza = if st.zapisany and biezacy == st.zapisany then st.baza else biezacy
	local n = st.dodatek * baza
	st.baza, st.zapisany = baza, n
	j.Transform = n
end

local function puscStaw(st: any)
	if st and st.zapisany and st.j.Transform == st.zapisany then
		st.j.Transform = st.baza
	end
	if st then
		st.zapisany, st.baza = nil, nil
		st.dodatek = CFrame.new()
	end
end

local function stawy(postac: Model): any
	local s = stawyPostaci[postac]
	if s then
		return s
	end
	s = { p = staw(postac, "RightShoulder", "Right Shoulder"), l = staw(postac, "LeftShoulder", "Left Shoulder"), wl = false }
	stawyPostaci[postac] = s
	return s
end

-- pet w dłoni (tylko własny awatar): zmniejszony model wybranego gotowego peta
local wDloni: Model? = nil
local wDloniId: string? = nil

local function krokRak(dt: number)
	local tn = os.clock()
	for _, g in Players:GetPlayers() do
		local postac = g.Character
		if postac and postac.Parent then
			local s = stawy(postac)
			local cwiczy = g:GetAttribute("PA_Trening") == true
			local moj = g == gracz
			local trzyma = moj and wDloni ~= nil and wDloni.Parent ~= nil
			local zamach = moj and tn < zamachDo
			if zamach then
				local t = tn - zamachT0
				local x = if t < 0.12 then 70 + (165 - 70) * (t / 0.12) elseif t < 0.22 then 165 - (165 - 25) * ((t - 0.12) / 0.1)
					else 25 + (70 - 25) * math.clamp((t - 0.22) / 0.2, 0, 1)
				ustawStaw(s.p, x, 8)
				ustawStaw(s.l, 0, 0)
				s.wl = true
			elseif cwiczy then
				local f = (math.sin(tn * 7) + 1) / 2
				ustawStaw(s.p, 0, 15 + 150 * f)
				ustawStaw(s.l, 0, -(15 + 150 * f))
				s.wl = true
			elseif trzyma then
				ustawStaw(s.p, 75, 10)
				ustawStaw(s.l, 0, 0)
				s.wl = true
			elseif s.wl then
				puscStaw(s.p)
				puscStaw(s.l)
				s.wl = false
			end
		end
	end
	for postac in stawyPostaci do
		if not postac.Parent then
			stawyPostaci[postac] = nil
		end
	end
	local _ = dt
end

RunService.PreSimulation:Connect(function()
	for _, s in stawyPostaci do
		if s.wl then
			doklejStaw(s.p)
			doklejStaw(s.l)
		end
	end
end)

local function rekaGracza(): BasePart?
	local c = gracz.Character
	local r = c and (c:FindFirstChild("RightHand") or c:FindFirstChild("Right Arm"))
	return if r and r:IsA("BasePart") then r else nil
end

local function odswiezDlon(lista)
	local id = nil
	if (gracz:GetAttribute("PA_Pet") or 0) == 0 then
		local w = lista[wybrany]
		if not (w and w.stan == "gotowy") then
			w = nil
			for _, x in lista do
				if x.stan == "gotowy" then
					w = x
					break
				end
			end
		end
		id = w and w.id
	end
	if id ~= wDloniId then
		if wDloni then
			wDloni:Destroy()
			wDloni = nil
		end
		wDloniId = id
		if id then
			local nr = L.nrPeta(D, id)
			local m = wzorzec(D.pety[nr].wzorzec)
			pcall(function()
				m:ScaleTo(2.2 / D.pety[nr].wysokosc)
			end)
			for _, d in m:GetDescendants() do
				if d:IsA("BasePart") then
					d.CastShadow = false
				end
			end
			m.PrimaryPart.Anchored = true
			m.Name = "PetWDloni"
			m.Parent = lokalne
			wDloni = m
		end
	end
	local r = rekaGracza()
	if wDloni and r then
		wDloni:PivotTo(r.CFrame * CFrame.new(0, -1.3, -0.4) * CFrame.Angles(0, math.pi, 0))
	end
end

------------------------------------------------------------------ rzut: ekran → arena
local znacznik = Instance.new("Part")
znacznik.Name = "ZnacznikCelu"
znacznik.Shape = Enum.PartType.Cylinder
znacznik.Anchored = true
znacznik.CanCollide = false
znacznik.CanQuery = false
znacznik.CanTouch = false
znacznik.CastShadow = false
znacznik.Material = Enum.Material.Neon
znacznik.Color = Color3.fromHex(K.ty)
znacznik.Transparency = 0.45
znacznik.Size = Vector3.new(0.15, 4, 4)
znacznik.Parent = nil
local celPada = Vector2.new(0, 6)

local function naArene(sx: number, sy: number, viewport: boolean?): Vector3?
	local promien = if viewport then kamera:ViewportPointToRay(sx, sy) else kamera:ScreenPointToRay(sx, sy)
	if promien.Direction.Y >= -1e-3 then
		return nil
	end
	local t = -promien.Origin.Y / promien.Direction.Y
	return promien.Origin + promien.Direction * t
end

local function wybierzGotowego(lista): number?
	local w = lista[wybrany]
	if w and w.stan == "gotowy" then
		return wybrany
	end
	for i, x in lista do
		if x.stan == "gotowy" then
			return i
		end
	end
	return nil
end

local function rzutW(x: number, z: number): boolean
	local r = math.sqrt(x * x + z * z)
	if r > R - D.rzut.margines then
		if r < D.scena.obrzeze_r[1] + 4 then
			ui:baner(D.ui.poza, Color3.fromHex("FF9A9A"), 1.0)
		end
		return false
	end
	if (gracz:GetAttribute("PA_Pet") or 0) > 0 then
		return false
	end
	local nr = wybierzGotowego(druzynaLista())
	if not nr then
		ui:baner(D.ui.odpoczywa, Color3.fromHex("FF9A9A"), 1.0)
		return false
	end
	wybrany = nr
	evAkcja:FireServer("rzut", nr, x, z)
	wyslane += 1
	zamachT0 = os.clock()
	zamachDo = zamachT0 + 0.45
	E:pierscien(Vector3.new(x, 0.2, z), 2.4, Color3.fromHex(K.ty), 0.9)
	dzwiek("klik", 1.2)
	return true
end

local function rzutEkran(sx: number, sy: number): boolean
	local p = naArene(sx, sy)
	if not p then
		return false
	end
	return rzutW(p.X, p.Z)
end

local function obsluzPad(k: Enum.KeyCode)
	padAktywny = true
	local otwarte = okna:otwarte()
	if k == Enum.KeyCode.ButtonA then
		if not otwarte then
			rzutW(celPada.X, celPada.Y)
		end
	elseif k == Enum.KeyCode.ButtonB then
		okna:zamknij()
	elseif k == Enum.KeyCode.ButtonX then
		umiejetnosc()
	elseif k == Enum.KeyCode.ButtonY then
		przelaczOkno("pety")
	elseif k == Enum.KeyCode.DPadUp then
		przelaczOkno("jajka")
	elseif k == Enum.KeyCode.DPadDown then
		trening()
	elseif (k == Enum.KeyCode.ButtonL1 or k == Enum.KeyCode.ButtonR1) and not otwarte then
		local n = #druzynaLista()
		if n > 0 then
			wybierz(((wybrany - 1 + (if k == Enum.KeyCode.ButtonR1 then 1 else -1)) % n) + 1)
		end
	end
end

UserInputService.InputBegan:Connect(function(wej: InputObject, przetworzone: boolean)
	local typ = wej.UserInputType
	if typ == Enum.UserInputType.Gamepad1 then
		if wej.KeyCode ~= Enum.KeyCode.ButtonA or not okna:otwarte() then
			obsluzPad(wej.KeyCode)
		end
		return
	end
	if przetworzone then
		return
	end
	if typ == Enum.UserInputType.MouseButton1 or typ == Enum.UserInputType.Touch then
		padAktywny = false
		if not okna:otwarte() then
			rzutEkran(wej.Position.X, wej.Position.Y)
		end
	elseif typ == Enum.UserInputType.Keyboard then
		padAktywny = false
		local k = wej.KeyCode
		if k == Enum.KeyCode.One or k == Enum.KeyCode.Two or k == Enum.KeyCode.Three then
			wybierz(if k == Enum.KeyCode.One then 1 elseif k == Enum.KeyCode.Two then 2 else 3)
		elseif k == Enum.KeyCode.Space or k == Enum.KeyCode.Q then
			umiejetnosc()
		elseif k == Enum.KeyCode.E then
			przelaczOkno("jajka")
		elseif k == Enum.KeyCode.P then
			przelaczOkno("pety")
		elseif k == Enum.KeyCode.T then
			trening()
		end
	end
end)

------------------------------------------------------------------ migawki stanu
local migawek = 0
evStan.OnClientEvent:Connect(function(b: buffer)
	if typeof(b) ~= "buffer" or buffer.len(b) < 14 then
		return
	end
	migawek += 1
	local n = buffer.readu16(b, 8)
	krolId = buffer.readu16(b, 10)
	nagrodaKrola = buffer.readu16(b, 12)
	local widziane = {}
	for i = 1, n do
		local o = 14 + (i - 1) * 24
		if o + 24 > buffer.len(b) then
			break
		end
		local id = buffer.readu16(b, o)
		local nr = buffer.readu8(b, o + 2)
		local slot = buffer.readu8(b, o + 3)
		local x, z = buffer.readf32(b, o + 6), buffer.readf32(b, o + 10)
		local f2 = buffer.readu8(b, o + 23)
		widziane[id] = true
		local w = widoki[id]
		if not w then
			w = nowyWidok(id, nr, slot, x, z, f2)
		end
		if w and not w.odlot then
			w.faza = buffer.readu8(b, o + 4)
			w.flagi = buffer.readu8(b, o + 5)
			if not w.lot then
				w.tx, w.tz = x, z
			end
			w.hp = buffer.readu16(b, o + 14)
			w.hpMax = math.max(1, buffer.readu16(b, o + 16))
			w.pasek = buffer.readu8(b, o + 18) / 255
			w.zl = buffer.readu8(b, o + 19)
			w.tkier = buffer.readi16(b, o + 20) / 1000
			w.gwiazdki = buffer.readu8(b, o + 22)
			w.f2 = f2
			w.brak = 0
			w.slot = slot
		end
	end
	for id, w in widoki do
		if not widziane[id] and not w.odlot and not w.lot then
			w.brak += 1
			if w.brak >= 3 then
				usunWidok(w)
			end
		end
	end
end)

------------------------------------------------------------------ zdarzenia
local liczZdarzen: { [string]: number } = {}

local function slowo(): string
	local s = D.ui.slowa
	return s[math.random(1, #s)]
end

local function pozSlotu(slot: number): Vector3
	local s = D.sloty[slot]
	if s then
		return Vector3.new(s.poz[1], s.poz[2] + 4, s.poz[3])
	end
	return Vector3.new(0, 60, 0)
end

local function mojId(): number
	return gracz:GetAttribute("PA_Pet") or 0
end

-- RING OUT: zsuwa się do fosy, rozbryzg, gejzer wystrzeliwuje go łukiem do właściciela (dziki — za trybunę)
local function odlotRingOut(w, z)
	local start = Vector3.new(z.x, 0, z.z)
	local kier = Vector3.new(z.kx, 0, z.kz)
	if kier.Magnitude < 0.1 then
		kier = Vector3.new(z.x, 0, z.z)
	end
	kier = kier.Unit
	local woda = start + kier * 5
	woda = Vector3.new(woda.X, D.scena.woda_y, woda.Z)
	local cel = if z.wl > 0 and not z.dziki then pozSlotu(z.wl) else (start.Unit * 90 + Vector3.new(0, 20, 0))
	local plusk, gejzer = false, false
	local t = 0
	pcall(function()
		local tr = E:smuga(w.korzen, Color3.fromRGB(190, 235, 255), 2.4)
		tr.Lifetime = 0.5
	end)
	w.odlot = function(dt: number): boolean
		t += dt
		local cf
		if t < 0.4 then
			local f = t / 0.4
			local p = start:Lerp(woda, f)
			p = Vector3.new(p.X, -f * f * (0 - D.scena.woda_y) + 1.5 * math.sin(f * math.pi), p.Z)
			cf = CFrame.new(p) * CFrame.Angles(f * 2, 0, f * 1.2)
		elseif t < 0.85 then
			if not plusk then
				plusk = true
				E:plask(woda + Vector3.new(0, 0.3, 0), Color3.fromRGB(150, 220, 255))
				E:iskry(woda + Vector3.new(0, 1, 0), Color3.fromRGB(170, 230, 255), 16, 1.5)
				dzwiek("plusk")
			end
			cf = CFrame.new(woda - Vector3.new(0, 4, 0))
		elseif t < 2.9 then
			if not gejzer then
				gejzer = true
				E:gejzer(woda)
			end
			local f = (t - 0.85) / 2.05
			local p = woda:Lerp(cel, f)
			p = Vector3.new(p.X, p.Y + 30 * math.sin(f * math.pi), p.Z)
			cf = CFrame.new(p) * CFrame.Angles(t * 10, t * 6, 0)
		else
			E:iskry(cel, Color3.fromRGB(255, 255, 255), 8, 0.6)
			return true
		end
		w.korzen.CFrame = cf
		w.krazek.Transparency = 1
		w.etykieta.Visible = false
		return false
	end
end

-- KO: gwiazdki, wirujący lot przez pół ekranu w kierunku ciosu
local function odlotKO(w, z)
	local start = Vector3.new(z.x, 0, z.z)
	local kier = Vector3.new(z.kx, 0, z.kz)
	if kier.Magnitude < 0.1 then
		kier = Vector3.new(math.random() - 0.5, 0, math.random() - 0.5)
	end
	kier = kier.Unit
	local cel = start + kier * 46 + Vector3.new(0, 6, 0)
	E:iskry(start + Vector3.new(0, 4, 0), Color3.fromHex(K.zloto), 18, 1.3)
	dzwiek("ko")
	pcall(function()
		E:smuga(w.korzen, Color3.fromRGB(255, 240, 160), 2.4)
	end)
	local t = 0
	w.odlot = function(dt: number): boolean
		t += dt
		if t >= 1.5 then
			E:iskry(w.korzen.Position, Color3.fromRGB(255, 255, 255), 10, 0.8)
			return true
		end
		local f = t / 1.5
		local p = start:Lerp(cel, f)
		p = Vector3.new(p.X, p.Y + 24 * math.sin(f * math.pi), p.Z)
		w.korzen.CFrame = CFrame.new(p) * CFrame.Angles(t * 16, t * 4, t * 9)
		w.krazek.Transparency = 1
		w.etykieta.Visible = false
		return false
	end
end

-- ucieczka bossa / złotego peta: w górę i poza dół
local function odlotUcieczka(w)
	local start = Vector3.new(w.x, 0, w.z)
	local t = 0
	w.odlot = function(dt: number): boolean
		t += dt
		if t >= 1.4 then
			return true
		end
		w.korzen.CFrame = CFrame.new(start + Vector3.new(0, t * t * 40, 0)) * CFrame.Angles(0, t * 6, 0)
		w.krazek.Transparency = 1
		w.etykieta.Visible = false
		return false
	end
end

local function zloteSlowo(poz: Vector3, ile: number)
	duzeSlowo(poz + Vector3.new(0, 7, 0), "+" .. L.format(ile) .. " G", Color3.fromHex(K.zloto), 1.0)
	local c = gracz.Character
	E:monety(poz, math.clamp(math.floor(ile / 5), 3, 10), c and c:FindFirstChild("HumanoidRootPart"), function()
		dzwiek("monety")
	end)
end

local function poz3(w, x: number, z: number): Vector3
	if w then
		return Vector3.new(w.x, w.y, w.z)
	end
	return Vector3.new(x, 0, z)
end

local function lotWidoku(w, od: Vector3, x: number, z: number, czas: number)
	local h = D.rzut.wysokosc + (od - Vector3.new(x, 0, z)).Magnitude * 0.12
	w.lot = { t = 0, czas = czas, od = od, x = x, z = z, h = h }
	w.tx, w.tz = x, z
	w.korzen.CFrame = CFrame.new(od)
	pcall(function()
		local tr = E:smuga(w.korzen, Color3.fromRGB(255, 255, 255), 2)
		task.delay(czas + 0.2, function()
			tr:Destroy()
		end)
	end)
end

local wyklucia = 0
local function zdarzenie(z)
	liczZdarzen[z.t] = (liczZdarzen[z.t] or 0) + 1
	local moj = mojSlot()
	local mid = mojId()
	if z.t == "rzut" or z.t == "zloty" then
		local w = widoki[z.id] or nowyWidok(z.id, z.nr, if z.dziki or z.t == "zloty" then 0 else z.wl, z.x, z.z, if z.t == "zloty" then 4 else 0)
		if w then
			lotWidoku(w, Vector3.new(z.x0, z.y0, z.z0), z.x, z.z, z.czas)
			if z.dziki or z.t == "zloty" then
				E:gejzer(Vector3.new(z.x0, z.y0, z.z0))
			end
			if z.wl == moj and not z.dziki and z.t == "rzut" then
				E:pierscien(Vector3.new(z.x, 0.2, z.z), 3, Color3.fromHex(K.ty), z.czas + 0.3)
				if wDloni then
					wDloni:Destroy()
					wDloni, wDloniId = nil, nil
				end
			end
		end
		if z.t == "zloty" then
			ui:baner(D.ui.zloty, Color3.fromHex(D.zloty.kolor), 1.8)
			dzwiek("krol")
		end
	elseif z.t == "boss" then
		local w = widoki[z.id] or nowyWidok(z.id, 200 + z.nr, 0, 0, 0, 2)
		if w then
			lotWidoku(w, Vector3.new(0, 80, 0), 0, 0, z.czas)
			w.lot.h = 0
		end
		ui:baner(D.ui.boss, Color3.fromHex("FF4D4D"), 2.0)
		dzwiek("boss")
	elseif z.t == "ladowanie" then
		local w = widoki[z.id]
		E:plask(Vector3.new(z.x, 0.1, z.z), Color3.fromRGB(220, 200, 160))
		if w then
			w.trafienie = 0.2
			if w.boss then
				wstrzasnij(1.6, 0.5)
				E:fala(Vector3.new(z.x, 0, z.z), 12)
				zatrzymaj(0.08)
			end
		end
	elseif z.t == "cios" then
		local w = widoki[z.b]
		local p = poz3(w, z.x, z.z) + Vector3.new(0, (if w then w.Pd.wysokosc * 0.5 else 3), 0)
		local mojeTrafienie = z.a == mid and mid > 0
		local wMnie = z.b == mid and mid > 0
		E:iskry(p, if z.k then Color3.fromHex("FFE14D") else Color3.fromRGB(255, 250, 230), if z.k then 10 else 5, if z.k then 1.1 else 0.7)
		if mojeTrafienie or wMnie then
			if z.o > 0 then
				E:liczba(p + Vector3.new(0, 2, 0), tostring(z.o), if wMnie then Color3.fromHex("FF9A9A") else Color3.fromRGB(255, 255, 255))
			end
		end
		if mojeTrafienie then
			maleSlowo(p + Vector3.new(0, 3, 0), if z.k then D.ui.kryt else slowo(), Color3.fromHex(if z.k then "FFE14D" else "FF8A3D"))
		end
		dzwiek(if z.k then "kryt" else "cios", 1 + math.random() * 0.25)
		if w then
			w.trafienie = 0.18
			w.blysk = 0.09
			if (mojeTrafienie or wMnie or (z.v or 0) > 25) and pulsow < 3 and not w.boss then
				w.puls = { t = 0 }
			end
		end
	elseif z.t == "zloto_cios" then
		if z.wl == moj then
			E:liczba(Vector3.new(z.x, 6, z.z), "+" .. z.ile .. " G", Color3.fromHex(K.zloto))
			dzwiek("monety", 1.2)
		end
		E:iskry(Vector3.new(z.x, 3, z.z), Color3.fromHex(K.zloto), 6, 0.8)
	elseif z.t == "umiejetnosc" then
		local w = widoki[z.id]
		local p = poz3(w, z.x, z.z)
		local mojePet = w and w.slot == moj and moj > 0
		if mojePet then
			duzeSlowo(p + Vector3.new(0, (w and w.Pd.wysokosc or 6) + 4, 0), z.nazwa .. "!", Color3.fromHex(K.ty), 1.1)
			uzylUmiejetnosci = true
		end
		dzwiek("umiejetnosc")
		if z.typ == "fala" then
			E:fala(p, z.r)
		elseif z.typ == "ogluszenie" then
			E:chmura(p, z.r)
		elseif z.typ == "zamrozenie" then
			local c = z.cel and widoki[z.cel]
			if c then
				E:lod(Vector3.new(c.x, 0, c.z))
				E:jezyk(p + Vector3.new(0, 4, 0), Vector3.new(c.x, 3, c.z))
			end
		elseif z.typ == "podpalenie" then
			E:plomien(p, Vector3.new(z.kx, 0, z.kz), z.zasieg, z.kat)
		elseif z.typ == "jezyk" then
			if z.x1 then
				E:jezyk(p + Vector3.new(0, 4, 0), Vector3.new(z.x1, 3, z.z1))
			end
		elseif z.typ == "skorupa" then
			E:pierscien(p, (w and w.Pd.promien or 2) + 1.5, Color3.fromRGB(120, 230, 120), z.czas)
		elseif z.typ == "skok" then
			if w then
				w.skok = { t = 0, czas = z.czas, h = z.wysokosc }
			end
			E:pierscien(Vector3.new(z.x1, 0.2, z.z1), z.r, Color3.fromHex("FF4D4D"), z.czas + 0.2)
		elseif z.typ == "szarza" then
			if w then
				pcall(function()
					local tr = E:smuga(w.korzen, Color3.fromRGB(255, 230, 160), 2)
					task.delay(1.2, function()
						tr:Destroy()
					end)
				end)
			end
		end
	elseif z.t == "ladowanie_skoku" or z.t == "boss_fala" then
		local p = Vector3.new(z.x, 0, z.z)
		E:fala(p, z.r)
		wstrzasnij(if z.t == "boss_fala" then 1.1 else 0.8, 0.35)
		dzwiek("kryt", 0.7)
	elseif z.t == "odbicie_slime" then
		local w = widoki[z.id]
		if w then
			w.x, w.z, w.tx, w.tz = z.x, z.z, z.x, z.z
			w.trafienie = 0.2
		end
	elseif z.t == "odbicie" then
		E:iskry(Vector3.new(z.x, 3, z.z), Color3.fromRGB(120, 230, 120), 8, 0.8)
	elseif z.t == "ringout" or z.t == "ko" then
		local w = widoki[z.id]
		local wazne = (z.wl == moj and not z.dziki and moj > 0) or (z.przez == moj and moj > 0) or z.boss or z.krol
		if w and not w.odlot then
			w.lot = nil
			if z.t == "ringout" then
				odlotRingOut(w, z)
			else
				odlotKO(w, z)
			end
		end
		local p = Vector3.new(z.x, 0, z.z)
		local nazwa = if z.t == "ringout" then D.ui.ring_out else D.ui.ko
		if wazne then
			zatrzymaj(0.07)
			wstrzasnij(if z.boss then 1.8 else 0.9, 0.3)
			duzeSlowo(p + Vector3.new(0, 9, 0), nazwa, Color3.fromHex(if z.t == "ringout" then "FF6A3D" else "FFE14D"), 1.2)
		end
		if z.boss then
			local mojaNagroda = 0
			for _, n in z.nagrody or {} do
				if n.wl == moj then
					mojaNagroda = n.ile
				end
			end
			ui:baner(if mojaNagroda > 0 then string.format(D.ui.boss_pokonany, L.format(mojaNagroda)) else D.ui.boss_pokonany_bez,
				Color3.fromHex(K.zloto), 2.4)
			local c = gracz.Character
			local hrp = c and c:FindFirstChild("HumanoidRootPart")
			for i = 1, 6 do
				task.delay(i * 0.12, function()
					E:monety(Vector3.new((math.random() - 0.5) * 30, 18, (math.random() - 0.5) * 30), 6, hrp, if i == 1 then function()
						dzwiek("monety")
					end else nil)
				end)
			end
		elseif z.wl == moj and not z.dziki and moj > 0 then
			ui:baner(nazwa, Color3.fromHex("FF6A6A"), 1.4)
		elseif z.przez == moj and moj > 0 and (z.premia + z.nagroda) > 0 then
			ui:baner(if z.nagroda > 0 then D.ui.nagroda .. " +" .. L.format(z.nagroda) .. "!" else nazwa .. " +" .. L.format(z.premia),
				Color3.fromHex(K.zloto), 1.5)
			zloteSlowo(p, z.premia + z.nagroda)
		end
	elseif z.t == "boss_uciekl" or z.t == "zloty_uciekl" then
		local w = widoki[z.id]
		if w and not w.odlot then
			w.lot = nil
			odlotUcieczka(w)
		end
		ui:baner(if z.t == "boss_uciekl" then D.ui.boss_uciekl else D.ui.zloty_uciekl, Color3.fromHex("FF9A9A"), 1.6)
	elseif z.t == "krol" then
		if z.wl == moj and not z.dziki and moj > 0 then
			ui:baner(D.ui.krol, Color3.fromHex(K.zloto), 1.6)
			dzwiek("krol")
		else
			ui:baner(D.ui.nowy_krol, Color3.fromHex(K.zloto), 0.9)
		end
	elseif z.t == "zloto" then
		local w = widoki[z.id]
		if w then
			E:liczba(Vector3.new(w.x, w.y + w.Pd.wysokosc + 1, w.z), "+" .. L.naSekunde(z.ile), Color3.fromHex(K.zloto))
		end
	elseif z.t == "wyklucie" then
		wyklucia += 1
		okna:zamknij()
		okna:wyklucie(z)
		dzwiek("trzesienie", 0.9)
	elseif z.t == "ogloszenie" then
		ui:ogloszenie(z.tekst, z.kolor)
	elseif z.t == "poziom" then
		ui:baner("LEVEL UP!  " .. string.format(D.ui.poziom, z.poziom), Color3.fromHex("9BE8FF"), 1.6)
		dzwiek("wyklucie", 1.2)
	elseif z.t == "odmowa" then
		local teksty = { pelna = D.ui.pelna, poza = D.ui.poza, odpoczywa = D.ui.odpoczywa, zloto = D.ui.za_malo }
		if teksty[z.powod] then
			ui:baner(teksty[z.powod], Color3.fromHex("FF9A9A"), 1.1)
		end
	end
end

evZdarzenia.OnClientEvent:Connect(function(lista)
	if type(lista) ~= "table" then
		return
	end
	for _, z in lista do
		if type(z) == "table" and type(z.t) == "string" then
			local ok, blad = pcall(zdarzenie, z)
			if not ok then
				warn(P .. "zdarzenie " .. z.t .. ": " .. tostring(blad))
			end
		end
	end
end)

------------------------------------------------------------------ napisy nad graczami (poziom trenera, najlepszy pet)
local napisyGraczy: { [Player]: TextLabel } = {}
local function krokNapisowGraczy()
	for _, g in Players:GetPlayers() do
		local l = napisyGraczy[g]
		local c = g.Character
		local glowa = c and c:FindFirstChild("Head")
		local slot = g:GetAttribute("PA_Slot") or 0
		if glowa and glowa:IsA("BasePart") and slot > 0 then
			if not l then
				l = Instance.new("TextLabel")
				l.Name = "Gracz_" .. slot
				l.AnchorPoint = Vector2.new(0.5, 1)
				l.BackgroundTransparency = 1
				l.TextScaled = true
				l.Font = cyfry
				local o = Instance.new("UIStroke")
				o.Thickness = 2
				o.Color = tusz
				o.Parent = l
				l.Parent = warstwa
				napisyGraczy[g] = l
			end
			local sn = skalaNapisow()
			l.Size = UDim2.fromOffset(170 * sn, 18 * sn)
			local naj = g:GetAttribute("PA_Najlepszy") or ""
			local nazwa, gw = string.match(naj, "^(.+):(%d+)$")
			l.Text = string.format(D.ui.poziom, g:GetAttribute("PA_Poziom") or 1) .. (if nazwa then "  " .. nazwa .. " " .. string.rep("★", tonumber(gw) or 1) else "")
			l.TextColor3 = Color3.fromHex(kolorSlotu(slot))
			local v, na = kamera:WorldToViewportPoint(glowa.Position + Vector3.new(0, 2.2, 0))
			l.Visible = na
			l.Position = UDim2.fromOffset(v.X, v.Y)
		elseif l then
			l:Destroy()
			napisyGraczy[g] = nil
		end
	end
	for g, l in napisyGraczy do
		if not g.Parent then
			l:Destroy()
			napisyGraczy[g] = nil
		end
	end
end

------------------------------------------------------------------ pętla rysowania
local pomiar = { klatek = 0, suma = 0, maks = 0, petlaSuma = 0, petlaMaks = 0 }
local doUI = 0
local doNazw = 0
local tGlob = 0

local function odswiezNazwy()
	for _, plr in Players:GetPlayers() do
		local s = plr:GetAttribute("PA_Slot")
		if type(s) == "number" and s > 0 then
			nazwySlotow[s] = plr:GetAttribute("PA_Nazwa") or ""
		end
	end
end

local function rysujWidok(w, dt: number, dtW: number)
	if w.odlot then
		if w.odlot(dtW) then
			usunWidok(w)
		end
		return
	end
	local Pd = w.Pd
	local y = 0
	local obrot = CFrame.new()
	if w.lot then
		local l = w.lot
		l.t += dtW
		local f = math.clamp(l.t / l.czas, 0, 1)
		local p = l.od:Lerp(Vector3.new(l.x, 0, l.z), f)
		p += Vector3.new(0, l.h * 4 * f * (1 - f), 0)
		w.x, w.z, y = p.X, p.Z, p.Y
		obrot = CFrame.Angles(-f * math.pi * 2, 0, 0)
		if f >= 1 then
			w.lot = nil
			w.x, w.z = l.x, l.z
		end
	else
		local a = 1 - math.exp(-dtW * 14)
		local dx, dz = w.tx - w.x, w.tz - w.z
		if dx * dx + dz * dz > 400 then
			w.x, w.z = w.tx, w.tz
		else
			w.x += dx * a
			w.z += dz * a
		end
		local predkosc = math.sqrt(dx * dx + dz * dz)
		if w.skok then
			local s = w.skok
			s.t += dtW
			local f = math.clamp(s.t / s.czas, 0, 1)
			y = s.h * 4 * f * (1 - f)
			obrot = CFrame.Angles(f * math.pi * 2, 0, 0)
			if f >= 1 then
				w.skok = nil
			end
		elseif predkosc > 0.12 and bit32.band(w.flagi, 2) == 0 and not w.boss then
			y = math.abs(math.sin(tGlob * 10 + w.faza0)) * 0.9
		end
		local dk = (w.tkier - w.kier + math.pi) % (2 * math.pi) - math.pi
		w.kier += dk * math.min(1, dtW * 10)
	end
	-- podskok i przechył po ciosie
	if w.trafienie > 0 then
		w.trafienie -= dtW
		y += math.sin(math.max(0, w.trafienie) / 0.18 * math.pi) * 1.2
	end
	w.y = y
	local cf = CFrame.new(w.x, y, w.z) * CFrame.Angles(0, w.kier + math.pi, 0) * obrot
	if w.trafienie > 0 then
		cf *= CFrame.Angles(-math.sin(math.max(0, w.trafienie) / 0.18 * math.pi) * 0.35, 0, 0)
	end
	if bit32.band(w.flagi, 1) ~= 0 then
		cf *= CFrame.Angles(0, 0, math.sin(tGlob * 18) * 0.25)
	end
	w.korzen.CFrame = cf
	-- spłaszczenie po ciosie (zmniejsza się i wraca z odbiciem) — tylko kilka naraz
	if w.puls then
		if w.puls.t == 0 then
			pulsow += 1
		end
		w.puls.t += dtW
		local f = w.puls.t / 0.24
		local s = if f >= 1 then 1 else 1 - math.sin(f * math.pi) * 0.2 + (if f > 0.5 then math.sin((f - 0.5) * 2 * math.pi) * 0.06 else 0)
		pcall(function()
			w.model:ScaleTo(s)
		end)
		if f >= 1 then
			w.puls = nil
			pulsow -= 1
		end
	end
	w.krazek.CFrame = CFrame.new(w.x, 0.28, w.z) * CFrame.Angles(0, 0, math.pi / 2)
	w.krazek.Transparency = if w.lot then 1 else (if w.slot > 0 and w.slot == mojSlot() then 0.1 elseif w.slot > 0 or w.zloty then 0.3 else 0.55)
	-- stany i błysk trafienia (wypełnienie obrysu)
	local f = w.flagi
	if w.blysk > 0 then
		w.blysk -= dt
		w.hl.FillColor = Color3.new(1, 1, 1)
		w.hl.FillTransparency = if w.boss then 0.8 else 0.2
	elseif bit32.band(f, 2) ~= 0 then
		w.hl.FillColor = Color3.fromRGB(150, 225, 255)
		w.hl.FillTransparency = 0.35
	elseif bit32.band(f, 4) ~= 0 then
		w.hl.FillColor = Color3.fromRGB(110, 230, 110)
		w.hl.FillTransparency = 0.45
	elseif bit32.band(f, 8) ~= 0 then
		w.hl.FillColor = Color3.fromRGB(255, 140, 40)
		w.hl.FillTransparency = 0.45 + math.sin(tGlob * 20) * 0.15
	elseif bit32.band(f, 1) ~= 0 then
		w.hl.FillColor = Color3.fromRGB(255, 240, 120)
		w.hl.FillTransparency = 0.55
	elseif w.zloty then
		w.hl.FillColor = Color3.fromHex(D.zloty.kolor)
		w.hl.FillTransparency = 0.3 + math.sin(tGlob * 6) * 0.1
	else
		w.hl.FillTransparency = 1
	end
	-- cienki pasek życia nad petem (warstwa 2D); własny: gwiazdki i „+G/s”; tarcza słabszego
	local krol = krolId == w.id
	local top = Vector3.new(w.x, y + Pd.wysokosc + (if krol then 4.6 else 0.6), w.z)
	local v, na = kamera:WorldToViewportPoint(top)
	w.etykieta.Visible = na and not w.lot and not w.boss
	if na and not w.boss then
		w.etykieta.Position = UDim2.fromOffset(v.X, v.Y)
		local fz = math.clamp(w.hp / w.hpMax, 0, 1)
		w.pasekZ.Size = UDim2.fromScale(fz, 1)
		w.pasekZ.BackgroundColor3 = Color3.fromHex(if fz < 0.35 then K.zycie_nisko else K.zycie)
		local moj = w.slot > 0 and w.slot == mojSlot()
		local gw = if w.gwiazdki > 1 then string.rep("★", w.gwiazdki) else ""
		local tarcza = if bit32.band(w.f2, 1) ~= 0 then "🛡 " else ""
		if moj then
			w.napis.Text = tarcza .. gw .. (if w.zl > 0 then (if gw ~= "" then " " else "") .. string.format(D.ui.na_s, L.naSekunde(w.zl)) else "")
		else
			w.napis.Text = tarcza .. gw
		end
		w.nagrodaTekst.Visible = krol
		if krol then
			w.nagrodaTekst.Text = D.ui.nagroda .. " " .. L.format(nagrodaKrola)
		end
	end
end

local function wydarzenieTekst(): string?
	local typ = kontener:GetAttribute("PA_WydTyp")
	local t = kontener:GetAttribute("PA_WydT")
	if type(t) ~= "number" or type(typ) ~= "string" then
		return nil
	end
	local zostalo = math.ceil(t - teraz())
	if zostalo > 60 or zostalo < 0 then
		return nil
	end
	local czas = string.format("%d:%02d", math.floor(zostalo / 60), zostalo % 60)
	return string.format(if typ == "boss" then D.ui.boss_za else D.ui.zloty_za, czas)
end

RunService.RenderStepped:Connect(function(dt: number)
	local t0 = os.clock()
	tGlob += dt
	local dtW = if os.clock() < stopDo then 0 else dt
	ustawKamere()
	for _, w in widoki do
		rysujWidok(w, dt, dtW)
	end
	krokRak(dt)
	-- korona nad królem
	local k = widoki[krolId]
	if k and not k.odlot and not k.lot then
		if korona.Parent ~= lokalne then
			korona.Parent = lokalne
		end
		korona:PivotTo(CFrame.new(k.x, k.y + k.Pd.wysokosc + 1.2 + math.sin(tGlob * 4) * 0.3, k.z) * CFrame.Angles(0, tGlob * 1.5, 0))
	elseif korona.Parent then
		korona.Parent = nil
	end
	-- celownik pada i podgląd celu pod myszą
	if padAktywny and not okna:otwarte() then
		local st = UserInputService:GetGamepadState(Enum.UserInputType.Gamepad1)
		for _, s in st do
			if s.KeyCode == Enum.KeyCode.Thumbstick1 and s.Position.Magnitude > 0.2 then
				local poz, cel = pozycjaKamery()
				if poz and cel then
					local przod = Vector3.new(cel.X - poz.X, 0, cel.Z - poz.Z).Unit
					local prawo = Vector3.new(-przod.Z, 0, przod.X)
					local d = (prawo * s.Position.X + przod * s.Position.Y) * dt * 26
					local n = celPada + Vector2.new(d.X, d.Z)
					if n.Magnitude > R - D.rzut.margines then
						n = n.Unit * (R - D.rzut.margines)
					end
					celPada = n
				end
			end
		end
		znacznik.Parent = lokalne
		znacznik.CFrame = CFrame.new(celPada.X, 0.3, celPada.Y) * CFrame.Angles(0, 0, math.pi / 2)
	elseif not dotyk and mojId() == 0 and not okna:otwarte() then
		local m = UserInputService:GetMouseLocation()
		local p = naArene(m.X, m.Y, true)
		if p and (p.X * p.X + p.Z * p.Z) <= (R - D.rzut.margines) ^ 2 then
			znacznik.Parent = lokalne
			znacznik.CFrame = CFrame.new(p.X, 0.3, p.Z) * CFrame.Angles(0, 0, math.pi / 2)
		else
			znacznik.Parent = nil
		end
	else
		znacznik.Parent = nil
	end
	E:krok(dt)
	ui:krok(dt)
	okna:krok(dt)
	-- ekran (10 razy na sekundę)
	doUI -= dt
	if doUI <= 0 then
		doUI = 0.1
		doNazw -= 0.1
		if doNazw <= 0 then
			doNazw = 1
			odswiezNazwy()
		end
		ui:zloto(gracz:GetAttribute("PA_Zloto") or 0, gracz:GetAttribute("PA_GS") or 0)
		ui:poziom(gracz:GetAttribute("PA_Poziom") or 1, gracz:GetAttribute("PA_Xp") or 0, gracz:GetAttribute("PA_XpPotrzeba") or 1)
		local lista = druzynaLista()
		ui:druzyna(lista)
		ui:pad(padAktywny)
		odswiezDlon(lista)
		local mojPet = widoki[mojId()]
		if mojPet and not mojPet.odlot then
			ui:umiejetnosc(not mojPet.lot, mojPet.pasek, mojPet.Pd.umiejetnosc.nazwa)
			ui:pet(true, mojPet.Pd.nazwa .. (if mojPet.gwiazdki > 1 then " " .. string.rep("★", mojPet.gwiazdki) else ""), nil, mojPet.hp,
				mojPet.hpMax, mojPet.pasek)
		else
			ui:umiejetnosc(false, 0, nil)
			ui:pet(false)
		end
		-- boss: pasek u góry
		local boss = nil
		for _, w in widoki do
			if w.boss and not w.odlot then
				boss = w
			end
		end
		ui:boss(if boss then boss.Pd.nazwa else nil, boss and boss.hp, boss and boss.hpMax)
		ui:wydarzenie(if boss then nil else wydarzenieTekst())
		local sam = gracz:GetAttribute("PA_Samouczek") or "00"
		local rzucil = string.sub(sam, 1, 1) == "1"
		local jajkoZrobione = string.sub(sam, 2, 2) == "1"
		ui:przyciski({ trening = gracz:GetAttribute("PA_Trening") == true, jajkoPulsuje = rzucil and not jajkoZrobione })
		okna:odswiez(stanOkien())
		local gotowych, najblizej = 0, math.huge
		for _, w in lista do
			if w.stan == "gotowy" then
				gotowych += 1
			elseif w.stan == "odpoczynek" then
				najblizej = math.min(najblizej, w.zostalo)
			end
		end
		local bezPeta = mojId() == 0
		if okna:otwarte() then
			ui:podpowiedz(nil)
		elseif rzucil and not jajkoZrobione then
			ui:podpowiedz(D.ui.podpowiedz_jajko)
		elseif bezPeta and (gotowych > 0 or not rzucil) then
			ui:podpowiedz(if padAktywny then D.ui.podpowiedz_pad elseif dotyk or ui.opcje.emulacja then D.ui.podpowiedz_dotyk
				else D.ui.podpowiedz_mysz)
		elseif bezPeta and najblizej < math.huge then
			ui:podpowiedz(string.format(D.ui.nastepny, najblizej))
		elseif mojPet and mojPet.pasek >= 1 and not uzylUmiejetnosci then
			ui:podpowiedz(D.ui.podpowiedz_umiejetnosc)
		else
			ui:podpowiedz(nil)
		end
		krokNapisowGraczy()
	end
	local dtP = os.clock() - t0
	pomiar.klatek += 1
	pomiar.suma += dt
	pomiar.maks = math.max(pomiar.maks, dt)
	pomiar.petlaSuma += dtP
	pomiar.petlaMaks = math.max(pomiar.petlaMaks, dtP)
end)

-- napisy stref na podłodze (x5, x2, x1) obrócone do kamery tego gracza (lokalnie)
task.spawn(function()
	while mojSlot() == 0 do
		task.wait(0.2)
	end
	local s = D.sloty[mojSlot()]
	local sc = kontener:FindFirstChild("Scena")
	local ar = sc and sc:FindFirstChild("Arena")
	if s and ar then
		for _, d in ar:GetChildren() do
			if d.Name == "NapisStrefy" and d:IsA("BasePart") then
				d.CFrame = CFrame.new(d.Position) * CFrame.Angles(0, s.katKamery - math.pi / 2, 0)
			end
		end
	end
end)

kontener:SetAttribute("KlientGotowy", true)
print(P .. "klient gotowy")

------------------------------------------------------------------ haczyki prób
local function kadr(szer: number, wys: number)
	local poz, cel = pozycjaKamery()
	if not poz or not cel then
		return nil
	end
	local cf = CFrame.lookAt(poz, cel)
	local t = math.tan(math.rad(D.kamera.fov / 2))
	local asp = szer / wys
	local xs0, xs1, ys0, ys1 = 1, 0, 1, 0
	for i = 0, 47 do
		local a = i / 48 * math.pi * 2
		local p = cf:PointToObjectSpace(Vector3.new(math.sin(a) * R, 0, math.cos(a) * R))
		local x = 0.5 + p.X / (-p.Z * t * asp) / 2
		local y = 0.5 - p.Y / (-p.Z * t) / 2
		xs0, xs1, ys0, ys1 = math.min(xs0, x), math.max(xs1, x), math.min(ys0, y), math.max(ys1, y)
	end
	return { x = { xs0, xs1 }, y = { ys0, ys1 } }
end

-- wysokość peta na ekranie (piksele okna i punkty telefonu 375 wys.)
local function rozmiarNaEkranie(w): (number, number)
	local a = kamera:WorldToViewportPoint(Vector3.new(w.x, w.y, w.z))
	local b = kamera:WorldToViewportPoint(Vector3.new(w.x, w.y + w.Pd.wysokosc, w.z))
	local px = math.abs(a.Y - b.Y)
	return px, px / kamera.ViewportSize.Y * 375
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any)
	if polecenie == "stan" then
		local lista = {}
		for id, w in widoki do
			local px, pt = rozmiarNaEkranie(w)
			table.insert(lista, { id = id, x = w.x, z = w.z, y = w.y, slot = w.slot, lot = w.lot ~= nil, odlot = w.odlot ~= nil,
				hp = w.hp, etykieta = w.etykieta.Visible, napis = w.napis.Text, px = px, pt = pt, boss = w.boss, zloty = w.zloty,
				gwiazdki = w.gwiazdki, tarcza = bit32.band(w.f2, 1) ~= 0, krazek = w.krazek.Color:ToHex() })
		end
		local z, n = dzwiekiZaladowane()
		local v = kamera.ViewportSize
		local st = ui:stan()
		local napisyG = 0
		for _, l in napisyGraczy do
			if l.Visible then
				napisyG += 1
			end
		end
		return {
			gotowy = true, slot = mojSlot(), widokow = #lista, widoki = lista, czesciWidokow = czesciWidokow, migawek = migawek,
			ui = st, okna = okna:stan(function(o)
				return ui:prost(o)
			end), kamera = { typ = kamera.CameraType.Name, fov = kamera.FieldOfView },
			viewport = { v.X, v.Y }, kadr = kadr(v.X, v.Y), zdarzenia = liczZdarzen, efektow = E:ile(), wyslane = wyslane,
			dzwiekow = graneDzwieki, dzwiekiZaladowane = z, dzwiekiRazem = n, krol = krolId, korona = korona.Parent ~= nil,
			klatki = pomiar.klatek, srKlatki = if pomiar.klatek > 0 then pomiar.suma / pomiar.klatek else 0, maksKlatki = pomiar.maks,
			srPetli = if pomiar.klatek > 0 then pomiar.petlaSuma / pomiar.klatek else 0, maksPetli = pomiar.petlaMaks,
			wybrany = wybrany, dotyk = dotyk, duzychSlow = duzychSlow, duzychPominietych = duzychPomin, wDloni = wDloniId,
			napisyGraczy = napisyG, wyklucia = wyklucia, pad = padAktywny,
		}
	elseif polecenie == "rzut" then
		local v, na = kamera:WorldToScreenPoint(Vector3.new(a, 0, b))
		if not na then
			return { wyslano = false, naEkranie = false }
		end
		return { wyslano = rzutEkran(v.X, v.Y), sx = v.X, sy = v.Y }
	elseif polecenie == "umiejetnosc" then
		ostatniaUmiejetnosc = 0
		umiejetnosc()
		return true
	elseif polecenie == "wybierz" then
		wybierz(a)
		return true
	elseif polecenie == "emulacja" then
		kontener:SetAttribute("EmulacjaEkranu", a)
		padAktywny = false
		zbudujUI()
		E.skala = skalaNapisow()
		for _, w in widoki do
			if not w.odlot then
				usunWidok(w)
			end
		end
		return true
	elseif polecenie == "pomiar_zeruj" then
		pomiar = { klatek = 0, suma = 0, maks = 0, petlaSuma = 0, petlaMaks = 0 }
		duzychPomin = 0
		return true
	elseif polecenie == "kamera_wolna" then
		kameraWolna = a == true
		return true
	elseif polecenie == "kamera" then
		-- film: { zoom = 0..1 } (bliżej celu) albo { pozycja = Vector3, cel = Vector3, fov = n }; nil — kamera gry
		kameraFilm = a
		return true
	elseif polecenie == "kadr" then
		return kadr(a, b)
	elseif polecenie == "okno" then
		if a == nil then
			okna:zamknij()
		else
			okna.st = stanOkien()
			okna:otworz(a)
		end
		return okna:otwarte()
	elseif polecenie == "jajko" then
		okna.opcje.naJajko(a)
		return true
	elseif polecenie == "druzyna_ui" then
		okna.st = stanOkien()
		if b then
			okna.slotDoZmiany = b
		end
		okna:wybierzPeta(a)
		return true
	elseif polecenie == "trening" then
		trening()
		return true
	elseif polecenie == "pad" then
		local k = Enum.KeyCode[a]
		if k then
			obsluzPad(k)
		end
		return { okno = okna:otwarte(), zaznaczony = if GuiService.SelectedObject then GuiService.SelectedObject.Name else nil }
	end
	return nil
end
