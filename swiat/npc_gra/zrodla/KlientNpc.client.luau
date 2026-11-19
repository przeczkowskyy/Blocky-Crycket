--[[
	KlientNpc — postacie niezależne u klienta (D-109; swiat/npc_gra). Script, RunContext = Client, w kontenerze
	Workspace/NpcGra. Wszystko jest lokalne: rigi z klocków powstają u gracza w folderze Workspace/NpcLokalni
	(nic nie replikuje się z serwera poza modułami danych), klipy grają przez Motor6D.Transform.

	Stanowisko = miejsce, gdzie stoi NPC:
		• z danych (DaneNpc.stanowiska — bazar): stopy i kierunek figury z mapy; figurę z klocków („zastepuje”)
		  klient chowa u siebie (LocalTransparencyModifier), dopóki stoi NPC — kolizje figury i podpowiedzi E zostają;
		  gdy inny pakiet pokaże nad stanowiskiem swój dymek (bazar po E), tabliczka NPC znika na ten czas;
		• z kotwicy: każda część z tagiem D.tag_kotwicy i atrybutem Npc = id postaci (opcjonalnie NpcSkala, NpcKlucz,
		  NpcImie, NpcRola, NpcZastepuje = ścieżka Modelu do schowania, NpcZostaw = nazwy części tego Modelu, które
		  mają zostać widoczne — po przecinku, gwiazdka na końcu = początek nazwy) — stopy w środku części, przód = jej przód;
		• z polecenia: Sygnaly/Polecenie:Invoke("postaw", klucz, idNpc, CFrame, skala?).
	Zachowanie (LogikaNpc): rig powstaje blisko gracza i znika daleko; rusza się tylko w zasięgu animacji (dalej stoi
	w pierwszej klatce spoczynku); spoczynek w pętli, co jakiś czas gest roli, powitanie po podejściu gracza, głowa
	i tułów obracają się ku graczowi; nad głową tabliczka z imieniem i rolą.

	Sygnaly/Polecenie (BindableFunction, dla innych pakietów u klienta):
		Invoke("graj", klucz, "gest" | "powitanie" | "spoczynek" | "akcja") → czas klipu w sekundach albo false
		        („akcja” = jeden krótki ruch mini-gry; mają ją trener Siły — rzut — i trenerka Kondycji — uderzenie pałką)
		Invoke("postaw", klucz, idNpc, CFrame, skala?) → true/false   ·   Invoke("usun", klucz) → true/false
		Invoke("stan", klucz) → { zbudowany, tryb, klip } albo nil    ·   Invoke("lista") → { klucze }
	Sygnaly/SterowanieKlienta (haczyk prób): "stan" → pełny odczyt, "pomiar_zeruj".
	Wyłącznik: atrybut kontenera D.wylacznik (false → NPC znikają, figury z klocków wracają).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneNpc"))
local L = require(moduly:WaitForChild("LogikaNpc"))
local Rig = require(moduly:WaitForChild("RigNpc"))
local rigi = moduly:WaitForChild("Rigi")
local sygnaly = kontener:WaitForChild("Sygnaly")
local Z, C, W, T = D.zasiegi, D.czasy, D.wzrok, D.tabliczka

local folder = Instance.new("Folder")
folder.Name = D.folder_lokalny
folder.Parent = workspace

local stanowiska = {} -- klucz → stanowisko
local lista = {} -- kolejność przeglądu
local aktywne = {} -- stanowiska, które się ruszają
local daneRigow = {}
local obce = {} -- klucz → { model, tabliczka }
local wlaczone = kontener:GetAttribute(D.wylacznik) ~= false
local pomiar = { suma = 0, klatek = 0, maks = 0 }
local bledy = 0

local function daneRigu(npc)
	local d = daneRigow[npc.id]
	if d == nil then
		local m = npc.rig and rigi:FindFirstChild(npc.rig)
		d = if m then require(m) else false
		daneRigow[npc.id] = d
	end
	return d or nil
end

local function znajdz(sciezka: string)
	local o = game
	for kawalek in string.gmatch(sciezka, "[^/]+") do
		o = o:FindFirstChild(kawalek)
		if not o then
			return nil
		end
	end
	return o
end

------------------------------------------------------------------ figura z klocków, którą NPC zastępuje
local function zostaje(s, nazwa: string): boolean
	if s.zostaw then
		for _, wzor in s.zostaw do
			if nazwa == wzor or (string.sub(wzor, -1) == "*" and string.sub(nazwa, 1, #wzor - 1) == string.sub(wzor, 1, -2)) then
				return true
			end
		end
	end
	return false
end

local function schowajCzesc(s, p: Instance)
	if p:IsA("BasePart") and not zostaje(s, p.Name) then
		s.ukryte[p] = true
		p.LocalTransparencyModifier = 1
	end
end

local function schowajFigure(s)
	if not s.zastepuje or s.figura then
		return
	end
	local m = znajdz(s.zastepuje)
	if not m then
		return
	end
	s.figura = m
	s.ukryte = {}
	for _, d in m:GetDescendants() do
		schowajCzesc(s, d)
	end
	s.polFigury = m.DescendantAdded:Connect(function(d)
		schowajCzesc(s, d)
	end)
end

local function pokazFigure(s)
	if s.polFigury then
		s.polFigury:Disconnect()
		s.polFigury = nil
	end
	if s.ukryte then
		for p in s.ukryte do
			if p.Parent then
				p.LocalTransparencyModifier = 0
			end
		end
	end
	s.ukryte = nil
	s.figura = nil
end

------------------------------------------------------------------ tabliczka: imię i rola (nad nią tekst powitania)
local function napis(rodzic: Instance, nazwa: string, tekst: string, kolor: string, y: number, wys: number)
	local t = Instance.new("TextLabel")
	t.Name = nazwa
	t.Position = UDim2.fromScale(0.04, y)
	t.Size = UDim2.fromScale(0.92, wys)
	t.BackgroundTransparency = 1
	t.Text = tekst
	t.TextColor3 = Color3.fromHex(kolor)
	t.TextScaled = true
	t.Font = Enum.Font[T.czcionka]
	t.Parent = rodzic
	return t
end

local function tabliczka(cf: CFrame, wysokosc: number, imie: string, rola: string, powitanie: string)
	local p = Instance.new("Part")
	p.Name = "Tabliczka"
	p.Size = Vector3.new(0.2, 0.2, 0.2)
	p.Transparency = 1
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.CastShadow = false
	p.CFrame = CFrame.new(cf.Position + Vector3.new(0, wysokosc + T.nad_glowa + T.wys * 0.8, 0))
	local bg = Instance.new("BillboardGui")
	bg.Name = "Nazwa"
	bg.Size = UDim2.fromScale(T.szer, T.wys * 1.6)
	bg.MaxDistance = T.zasieg
	bg.LightInfluence = 0
	bg.Adornee = p
	local ramka = Instance.new("Frame")
	ramka.Name = "Ramka"
	ramka.Position = UDim2.fromScale(0, 0.375)
	ramka.Size = UDim2.fromScale(1, 0.625)
	ramka.BackgroundColor3 = Color3.fromHex(T.tlo)
	ramka.BackgroundTransparency = T.przezroczystosc_tla
	ramka.BorderSizePixel = 0
	local rog = Instance.new("UICorner")
	rog.CornerRadius = UDim.new(0.25, 0)
	rog.Parent = ramka
	napis(ramka, "Imie", imie, T.imie, 0.06, 0.52)
	napis(ramka, "Rola", rola, T.rola, 0.58, 0.36)
	ramka.Parent = bg
	local pow = napis(bg, "Powitanie", powitanie, T.powitanie, 0, 0.33)
	pow.Visible = false
	bg.Parent = p
	return p, pow
end

------------------------------------------------------------------ budowa i usuwanie NPC na stanowisku
local function graj(s, rola: string)
	Rig.graj(s.uchwyt, s.npc.klipy[rola], if rola == "akcja" then C.przejscie_akcji_s else C.przejscie_s)
	s.liczniki[rola] = (s.liczniki[rola] or 0) + 1
	if rola == "powitanie" and s.napisPowitania and s.npc.powitanie ~= "" then
		s.napisPowitania.Visible = true
		local nr = s.liczniki.powitanie
		task.delay(C.tekst_powitania_s, function()
			if s.napisPowitania and s.liczniki.powitanie == nr then
				s.napisPowitania.Visible = false
			end
		end)
	end
end

local function zbuduj(s): boolean
	local dane = daneRigu(s.npc)
	if not dane then
		return false
	end
	local model, u = Rig.zbuduj(dane, s.skala, "Npc_" .. s.klucz)
	Rig.ustaw(u, s.cf)
	model:SetAttribute("Npc", s.npc.id)
	s.model, s.uchwyt = model, u
	local tab, pow = tabliczka(s.cf, s.npc.czubek * s.skala, s.imie, s.rola, s.npc.powitanie)
	tab.Nazwa.Enabled = s.dymki == nil
	tab.Parent = model
	s.tab, s.napisPowitania = tab, pow
	s.stan = L.nowy_stan(math.random(), C)
	s.tulow, s.glowa, s.pochyl, s.dt = 0, 0, 0, 0
	Rig.graj(u, s.npc.klipy.spoczynek, 0)
	Rig.krok(u, 0, 0, 0, 0)
	model.Parent = folder
	schowajFigure(s)
	return true
end

local function usun(s)
	if s.model then
		s.model:Destroy()
	end
	s.model, s.uchwyt, s.tab, s.napisPowitania, s.stan = nil, nil, nil, nil, nil
	pokazFigure(s)
end

local function zdejmij(klucz: string): boolean
	local s = stanowiska[klucz]
	if not s then
		return false
	end
	usun(s)
	stanowiska[klucz] = nil
	local i = table.find(lista, s)
	if i then
		table.remove(lista, i)
	end
	i = table.find(aktywne, s)
	if i then
		table.remove(aktywne, i)
	end
	return true
end

local function postaw(klucz: string, idNpc: string, cf: CFrame, skala: number?, opcje): boolean
	local npc = D.npc[idNpc]
	if type(klucz) ~= "string" or not npc or not npc.rig or typeof(cf) ~= "CFrame" then
		return false
	end
	zdejmij(klucz)
	local przod = Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z)
	if przod.Magnitude < 0.01 then
		przod = Vector3.new(0, 0, -1)
	end
	opcje = opcje or {}
	local s = {
		klucz = klucz, npc = npc, cf = CFrame.lookAt(cf.Position, cf.Position + przod),
		skala = if type(skala) == "number" and skala > 0 then skala else npc.skala,
		imie = opcje.imie or npc.imie, rola = opcje.rola or npc.rola, zastepuje = opcje.zastepuje,
		zostaw = if type(opcje.zostaw) == "string" and opcje.zostaw ~= "" then string.split(opcje.zostaw, ",") else nil,
		tryb = "brak", liczniki = {}, dt = 0, odSzukania = 0,
	}
	stanowiska[klucz] = s
	table.insert(lista, s)
	return true
end

------------------------------------------------------------------ kotwice (tag) — tak stanowiska dają inne pakiety
local kluczeKotwic = {}

local function odKotwicy(a: Instance)
	if not a:IsA("BasePart") then
		return
	end
	local id = a:GetAttribute("Npc")
	if type(id) ~= "string" or not D.npc[id] or not D.npc[id].rig then
		warn(D.prefiks .. "kotwica " .. a:GetFullName() .. " bez poprawnego atrybutu Npc")
		return
	end
	local klucz = a:GetAttribute("NpcKlucz")
	if type(klucz) ~= "string" or klucz == "" then
		klucz = "kotwica:" .. a:GetFullName()
	end
	kluczeKotwic[a] = klucz
	postaw(klucz, id, a.CFrame, a:GetAttribute("NpcSkala"), {
		imie = a:GetAttribute("NpcImie"), rola = a:GetAttribute("NpcRola"), zastepuje = a:GetAttribute("NpcZastepuje"),
		zostaw = a:GetAttribute("NpcZostaw"),
	})
end

local function bezKotwicy(a: Instance)
	local klucz = kluczeKotwic[a]
	if klucz then
		kluczeKotwic[a] = nil
		zdejmij(klucz)
	end
end

------------------------------------------------------------------ tabliczki nad modelami innych pakietów (kowal)
local function przegladObcych()
	for _, o in D.obce do
		local wpis = obce[o.klucz]
		if wpis and (not wlaczone or not wpis.model.Parent) then
			wpis.tabliczka:Destroy()
			obce[o.klucz] = nil
			wpis = nil
		end
		if not wpis and wlaczone then
			local m = znajdz(o.model)
			local npc = D.npc[o.npc]
			if m and m:IsA("Model") and npc then
				local cf, rozmiar = m:GetBoundingBox()
				local dol = Vector3.new(cf.Position.X, cf.Position.Y - rozmiar.Y / 2, cf.Position.Z)
				local wysokosc = rozmiar.Y
				if o.dol then
					-- stała wysokość spodu tabliczki nad stopami i wysunięcie przed model (jego przód = −Z korzenia)
					local korzen = m.PrimaryPart or m:FindFirstChild("Korzen")
					local przod = if korzen then korzen.CFrame.LookVector else cf.LookVector
					dol += Vector3.new(przod.X, 0, przod.Z) * (o.przod or 0)
					wysokosc = o.dol - T.nad_glowa
				end
				local tab = tabliczka(CFrame.new(dol), wysokosc, npc.imie, npc.rola, "")
				tab.Name = "Tabliczka_" .. o.klucz
				tab.Parent = folder
				obce[o.klucz] = { model = m, tabliczka = tab }
			end
		end
	end
end

------------------------------------------------------------------ przegląd odległości: budowa, usypianie, lista ruchu
local function przeglad(poz: Vector3?, dt: number)
	table.clear(aktywne)
	for _, s in lista do
		local odl = if poz then (poz - s.cf.Position).Magnitude else nil
		s.odl = odl
		local nowy = if wlaczone then L.tryb(odl, s.tryb, Z) else "brak"
		if nowy ~= s.tryb then
			if s.tryb == "brak" then
				if not zbuduj(s) then
					nowy = "brak"
				end
			elseif nowy == "brak" then
				usun(s)
			end
			if nowy == "uspiony" and s.uchwyt then
				L.wymus(s.stan, "spoczynek", s.npc)
				Rig.graj(s.uchwyt, s.npc.klipy.spoczynek, 0)
				Rig.krok(s.uchwyt, 0, 0, 0, 0)
				s.tulow, s.glowa, s.pochyl = 0, 0, 0
			end
			s.tryb = nowy
		end
		if nowy == "blisko" or nowy == "daleko" then
			table.insert(aktywne, s)
		end
		if s.dymki then
			for i = #s.dymki, 1, -1 do
				if not s.dymki[i].Parent then
					table.remove(s.dymki, i)
				end
			end
			if #s.dymki == 0 then
				s.dymki = nil
				if s.tab then
					s.tab.Nazwa.Enabled = true
				end
			end
		end
		if s.model and s.zastepuje and not s.figura then
			s.odSzukania += dt
			if s.odSzukania >= C.szukaj_modelu_s then
				s.odSzukania = 0
				schowajFigure(s)
			end
		end
	end
	przegladObcych()
end

local odPrzegladu = math.huge
local nrKlatki = 0

local function klatka(dt: number)
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local poz = if hrp then hrp.Position else nil
	odPrzegladu += dt
	if odPrzegladu >= C.przeglad_s then
		przeglad(poz, if odPrzegladu == math.huge then 0 else odPrzegladu)
		odPrzegladu = 0
	end
	nrKlatki += 1
	for i, s in aktywne do
		s.dt += dt
		if s.tryb == "blisko" or (nrKlatki + i) % L.co_ile(s.tryb) == 0 then
			local krok = s.dt
			s.dt = 0
			local kat, pochyl, poziom = 0, 0, math.huge
			local odl = nil
			if poz then
				local l = s.cf:PointToObjectSpace(poz + Vector3.new(0, 1.5, 0))
				poziom = math.sqrt(l.X * l.X + l.Z * l.Z)
				kat = math.atan2(-l.X, -l.Z)
				pochyl = math.atan2(l.Y - W.wysokosc_oczu * s.skala, math.max(poziom, 0.05))
				odl = (poz - s.cf.Position).Magnitude
			end
			local polecenie = L.krok(s.stan, odl, krok, math.random(), D, s.npc)
			if polecenie then
				graj(s, polecenie)
			end
			local ct, cg, cp = L.wzrok(kat, pochyl, poziom, W)
			s.tulow = L.wygladz(s.tulow, ct, krok, W.tempo)
			s.glowa = L.wygladz(s.glowa, cg, krok, W.tempo)
			s.pochyl = L.wygladz(s.pochyl, cp, krok, W.tempo)
			Rig.krok(s.uchwyt, krok, s.tulow, s.glowa, s.pochyl)
		end
	end
end

RunService.Heartbeat:Connect(function(dt)
	local t0 = os.clock()
	local ok, blad = pcall(klatka, dt)
	if not ok then
		bledy += 1
		if bledy <= 3 then
			warn(D.prefiks .. "błąd pętli: " .. tostring(blad))
		end
	end
	local ms = (os.clock() - t0) * 1000
	pomiar.suma += ms
	pomiar.klatek += 1
	pomiar.maks = math.max(pomiar.maks, ms)
end)

kontener:GetAttributeChangedSignal(D.wylacznik):Connect(function()
	wlaczone = kontener:GetAttribute(D.wylacznik) ~= false
	odPrzegladu = math.huge
end)

------------------------------------------------------------------ cudzy dymek nad NPC: tabliczka znika na ten czas
-- Dymek innego pakietu (BillboardGui zawsze na wierzchu, zaczepiony przy stanowisku nad głową NPC — np. tekst bazaru
-- po E) wypada w miejscu tabliczki; żeby napisy nie leżały na sobie, tabliczka stanowiska chowa się, dopóki dymek istnieje.
local function cudzyDymek(g: Instance)
	if not g:IsA("BillboardGui") or not g.AlwaysOnTop or g:IsDescendantOf(folder) then
		return
	end
	local a = g.Adornee
	if not a or not a:IsA("BasePart") then
		return
	end
	local najblizsze, odl = nil, C.dymek_zasieg
	for _, s in lista do
		local d = Vector3.new(a.Position.X - s.cf.Position.X, 0, a.Position.Z - s.cf.Position.Z).Magnitude
		if d < odl then
			najblizsze, odl = s, d
		end
	end
	local s = najblizsze
	if not s then
		return
	end
	-- tylko dymek nad głową NPC (tam, gdzie tabliczka); podpowiedź E Roblox to też BillboardGui na wierzchu, ale
	-- wisi przy tułowiu sprzedawcy i tabliczce nie przeszkadza
	local wysokosc = a.Position.Y + g.StudsOffsetWorldSpace.Y + g.StudsOffset.Y
	if wysokosc < s.cf.Position.Y + s.npc.czubek * s.skala - 0.5 then
		return
	end
	-- koniec dymka wykrywa przegląd odległości (zdarzenia zniszczonej instancji przy odroczonych sygnałach nie dochodzą)
	s.dymki = s.dymki or {}
	table.insert(s.dymki, g)
	if s.tab then
		s.tab.Nazwa.Enabled = false
	end
end
task.spawn(function()
	gracz:WaitForChild("PlayerGui").DescendantAdded:Connect(cudzyDymek)
end)

------------------------------------------------------------------ stanowiska z danych i z kotwic
for _, st in D.stanowiska do
	local poz = Vector3.new(st.poz[1], st.poz[2], st.poz[3])
	postaw(st.klucz, st.npc, CFrame.lookAt(poz, poz + Vector3.new(st.kier[1], 0, st.kier[2])), st.skala,
		{ rola = st.rola, zastepuje = st.zastepuje })
end
for _, a in CollectionService:GetTagged(D.tag_kotwicy) do
	odKotwicy(a)
end
CollectionService:GetInstanceAddedSignal(D.tag_kotwicy):Connect(odKotwicy)
CollectionService:GetInstanceRemovedSignal(D.tag_kotwicy):Connect(bezKotwicy)

------------------------------------------------------------------ polecenia dla innych pakietów
sygnaly:WaitForChild("Polecenie").OnInvoke = function(polecenie, klucz, a, b, c)
	if polecenie == "lista" then
		local w = {}
		for k in stanowiska do
			table.insert(w, k)
		end
		table.sort(w)
		return w
	elseif polecenie == "postaw" then
		return postaw(klucz, a, b, c)
	elseif polecenie == "usun" then
		return type(klucz) == "string" and zdejmij(klucz)
	end
	local s = type(klucz) == "string" and stanowiska[klucz] or nil
	if polecenie == "stan" then
		if not s then
			return nil
		end
		return { zbudowany = s.model ~= nil, tryb = s.tryb, klip = s.stan and s.stan.klip or nil }
	elseif polecenie == "graj" then
		if not s or not s.uchwyt or (s.tryb ~= "blisko" and s.tryb ~= "daleko") then
			return false
		end
		if not L.wymus(s.stan, a, s.npc) then
			return false
		end
		graj(s, a)
		return if a == "spoczynek" then 0 else s.npc.dlugosci[a]
	end
	return nil
end

------------------------------------------------------------------ haczyk prób (Play w Studio)
local function odczyt(s)
	local w = {
		klucz = s.klucz, npc = s.npc.id, tryb = s.tryb, odl = s.odl, skala = s.skala, zbudowany = s.model ~= nil,
		klip = s.stan and s.stan.klip or nil, imie = s.imie, rola = s.rola, zastepuje = s.zastepuje,
		figura = s.figura ~= nil, tulow = s.tulow, glowa = s.glowa, pochyl = s.pochyl,
		powitan = s.liczniki.powitanie or 0, gestow = s.liczniki.gest or 0,
		poz = { s.cf.Position.X, s.cf.Position.Y, s.cf.Position.Z },
	}
	if s.model then
		local czesci, widoczne, fizyka, dol = 0, 0, 0, math.huge
		for _, p in s.model:GetDescendants() do
			if p:IsA("BasePart") then
				czesci += 1
				if p.CanCollide or p.CanTouch or p.CanQuery then
					fizyka += 1
				end
				if p.Transparency < 1 then
					widoczne += 1
					local r, cf = p.Size / 2, p.CFrame
					for _, zx in { -1, 1 } do
						for _, zy in { -1, 1 } do
							for _, zz in { -1, 1 } do
								dol = math.min(dol, (cf * Vector3.new(r.X * zx, r.Y * zy, r.Z * zz)).Y)
							end
						end
					end
				end
			end
		end
		local g = s.uchwyt.kosci[s.uchwyt.dane.glowa]
		w.czesci, w.bryl, w.fizyka, w.spod = czesci, widoczne, fizyka, dol - s.cf.Position.Y
		w.glowaPoz = { g.Position.X, g.Position.Y, g.Position.Z }
		w.glowaPrzod = { g.CFrame.LookVector.X, g.CFrame.LookVector.Y, g.CFrame.LookVector.Z }
		w.tabliczka = s.tab.Position.Y - s.cf.Position.Y
		w.napisy = { s.tab.Nazwa.Ramka.Imie.Text, s.tab.Nazwa.Ramka.Rola.Text }
		w.powitanieWidac = s.napisPowitania.Visible
		w.tabliczkaWidac = s.tab.Nazwa.Enabled
	end
	if s.figura then
		local ukryte, widoczne = 0, 0
		for _, p in s.figura:GetDescendants() do
			if p:IsA("BasePart") and p.Transparency < 1 then
				if p.LocalTransparencyModifier >= 1 then
					ukryte += 1
				else
					widoczne += 1
				end
			end
		end
		w.figuraUkryte, w.figuraWidoczne = ukryte, widoczne
	end
	return w
end

sygnaly:WaitForChild("SterowanieKlienta").OnInvoke = function(polecenie)
	if polecenie == "stan" then
		local st = {}
		for _, s in lista do
			table.insert(st, odczyt(s))
		end
		local tabliczkiObce = {}
		for k in obce do
			table.insert(tabliczkiObce, k)
		end
		return {
			gotowy = true, wlaczone = wlaczone, skrot = D.skrot, stanowiska = st, ruszaSie = #aktywne, obce = tabliczkiObce,
			bledy = bledy, petla_ms = if pomiar.klatek > 0 then pomiar.suma / pomiar.klatek else 0,
			petla_maks_ms = pomiar.maks, klatek = pomiar.klatek,
		}
	elseif polecenie == "pomiar_zeruj" then
		pomiar.suma, pomiar.klatek, pomiar.maks = 0, 0, 0
		return true
	end
	return nil
end

kontener:SetAttribute("SkrotKlienta", D.skrot)
kontener:SetAttribute("KlientGotowy", true)
