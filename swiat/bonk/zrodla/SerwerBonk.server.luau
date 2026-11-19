--[[
	SerwerBonk — serwer gry BONK (Script, RunContext Server, w Workspace/BonkGra). Jedyne źródło prawdy:
	potwory (życie, miejsce, odrodzenie), BONK (wybór celu, obrażenia = Moc, limit tempa, lot), nagrody, Moc, monety,
	bramy krain, wejście i wyjście portalem, zapis postępu.

	Stan potworów: Workspace/BonkGra/Stan/Potwory/<id> (Configuration z atrybutami — klient rysuje z nich modele).
	Stan gracza: atrybuty gracza Bonk* (BonkAktywny, BonkMoc, BonkMonety, BonkOdblokowane…) i BezBohatera
	(swiat/bohater_swiat nie rysuje bohatera klasy graczowi w BONK).
	Zdarzenia do klientów: Sygnaly/Zdarzenia (t = "cios" | "lot"). Od klienta tylko Sygnaly/Bonk (bez argumentów).
	Haczyki prób: Sygnaly/SterowanieSerwera (BindableFunction, tylko serwer) — README.

	Etap 2: mnożniki pałki i petów czyta przelicz() z atrybutów gracza BonkMnoznikPalki / BonkMnoznikPetow;
	brama: L.mozePrzejsc(nr, moc, D, profil) — tam dojdzie Strażnik (profil.straznicy).
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local kontener = script.Parent
local Moduly = kontener:WaitForChild("Moduly")
local D = require(Moduly:WaitForChild("DaneBonk"))
local L = require(Moduly:WaitForChild("LogikaBonk"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evBonk = Sygnaly:WaitForChild("Bonk")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local sterowanie = Sygnaly:WaitForChild("SterowanieSerwera")
local P = D.prefiks

kontener:SetAttribute("SerwerGotowy", false)
kontener:SetAttribute("SkrotSerwera", D.skrot)
if kontener:GetAttribute(D.wylacznik) == false then
	sterowanie.OnInvoke = function()
		return { wylaczony = true }
	end
	return
end

------------------------------------------------------------------ wzorce potworów → ReplicatedStorage (klient je klonuje)
do
	local stary = ReplicatedStorage:FindFirstChild(D.folderWzorcow)
	if stary then
		stary:Destroy()
	end
	local wz = kontener:FindFirstChild("Wzorce")
	if wz then
		wz.Name = D.folderWzorcow
		wz.Parent = ReplicatedStorage
		kontener:SetAttribute("WzorceGotowe", true)
	else
		warn(P .. "brak folderu Wzorce w kontenerze — potwory będą zastępczymi bryłami")
		kontener:SetAttribute("WzorceGotowe", false)
	end
end

local mapa = kontener:FindFirstChild("Mapa")
local promienMapy = RaycastParams.new()
promienMapy.FilterType = Enum.RaycastFilterType.Include
promienMapy.FilterDescendantsInstances = if mapa then { mapa } else {}
promienMapy.RespectCanCollide = true

local function ziemia(x: number, yPrzybl: number, z: number): number
	if not mapa then
		return yPrzybl
	end
	local w = workspace:Raycast(Vector3.new(x, yPrzybl + 30, z), Vector3.new(0, -60, 0), promienMapy)
	if w then
		return w.Position.Y
	end
	return yPrzybl
end

local function teraz(): number
	return workspace:GetServerTimeNow()
end

------------------------------------------------------------------ potwory
local folderStanu = kontener:FindFirstChild("Stan")
if folderStanu then
	folderStanu:Destroy()
end
folderStanu = Instance.new("Folder")
folderStanu.Name = "Stan"
local folderPotworow = Instance.new("Folder")
folderPotworow.Name = "Potwory"
folderPotworow.Parent = folderStanu

local potwory: { any } = {}
local poId: { [string]: any } = {}
local PT = D.potwory

local function losuj(a: number, b: number): number
	return a + math.random() * (b - a)
end

local function rozstaw(p: any)
	local W = p.zagroda.wezly
	local w = W[((p.slot - 1) % #W) + 1]
	local r = PT.rozrzut_startu
	local x, z = w[1] + losuj(-r, r), w[3] + losuj(-r, r)
	local y = ziemia(x, w[2], z)
	if math.abs(y - w[2]) > 3 then
		x, z, y = w[1], w[3], ziemia(w[1], w[2], w[3])
	end
	p.domX, p.domZ, p.y = x, z, y
	p.ox, p.oz, p.cx, p.cz, p.t0 = x, z, x, z, teraz()
end

local function zapiszRuch(p: any)
	p.cfg:SetAttribute("Od", Vector3.new(p.ox, p.y, p.oz))
	p.cfg:SetAttribute("Cel", Vector3.new(p.cx, p.y, p.cz))
	p.cfg:SetAttribute("T0", p.t0)
end

local function odrodz(p: any)
	p.nr += 1
	p.rzadki = math.random() < D.rzadki.szansa
	p.hpMax = L.zycie(p.G, p.rzadki, D)
	p.hp = p.hpMax
	p.zywy = true
	rozstaw(p)
	p.wedrowka = os.clock() + losuj(PT.wedrowka_s[1], PT.wedrowka_s[2])
	local c = p.cfg
	c:SetAttribute("Rzadki", p.rzadki)
	c:SetAttribute("HpMax", p.hpMax)
	c:SetAttribute("Hp", p.hp)
	zapiszRuch(p)
	c:SetAttribute("Nr", p.nr)
	c:SetAttribute("Zywy", true)
end

for k, K in D.krainy do
	for _, Z in K.zagrody do
		local G = D.gatunki[Z.gatunek]
		for slot = 1, Z.ile do
			local id = string.format("%s_%d", Z.id, slot)
			local cfg = Instance.new("Configuration")
			cfg.Name = id
			cfg:SetAttribute("Gatunek", Z.gatunek)
			cfg:SetAttribute("Kraina", k)
			cfg:SetAttribute("Zagroda", Z.id)
			cfg:SetAttribute("Pr", PT.predkosc)
			cfg:SetAttribute("Promien", G.promien)
			local p: any = {
				id = id, cfg = cfg, kraina = k, zagroda = Z, klucz = Z.gatunek, G = G, slot = slot,
				domX = 0, domZ = 0, y = 0, ox = 0, oz = 0, cx = 0, cz = 0, t0 = 0,
				hp = 1, hpMax = 1, zywy = false, rzadki = false, nr = 0, odrodzenie = 0, wedrowka = 0,
			}
			odrodz(p)
			cfg.Parent = folderPotworow
			table.insert(potwory, p)
			poId[id] = p
		end
	end
end
folderStanu.Parent = kontener

local function polozenie(p: any, t: number): (number, number)
	return L.pozycja(p.ox, p.oz, p.cx, p.cz, p.t0, PT.predkosc, t)
end

------------------------------------------------------------------ zapis postępu
local Z = D.zapis
local magazyn: any = nil
do
	-- znacznik próby (tools/zapis_prob.py) → L.magazyn daje nil: magazynu nie otwieramy, gracz gra w pamięci
	local nazwa, stan = L.magazyn(Z, RunService:IsStudio(), kontener:GetAttribute(Z.znacznik_proby), os.time(),
		kontener:GetAttribute(Z.znacznik_magazynu) == true)
	if nazwa then
		local ok, ds = pcall(function()
			return game:GetService("DataStoreService"):GetDataStore(nazwa)
		end)
		if ok and ds then
			magazyn = ds
		else
			stan = "wyłączony (usługa danych niedostępna: " .. tostring(ds) .. ")"
		end
	end
	kontener:SetAttribute("ZapisStan", stan)
	kontener:SetAttribute("ZapisMagazyn", if magazyn then nazwa else nil)
	kontener:SetAttribute("ZapisAktywny", magazyn ~= nil)
	for _, n in { "LicznikWczytan", "LicznikZapisow", "LicznikBledowZapisu" } do
		kontener:SetAttribute(n, 0)
	end
end

local function licz(n: string)
	kontener:SetAttribute(n, (kontener:GetAttribute(n) or 0) + 1)
end

local function klucz(gracz: Player): string
	return "g_" .. tostring(gracz.UserId)
end

------------------------------------------------------------------ gracze
local stany: { [Player]: any } = {}

local function przelicz(gracz: Player)
	local s = stany[gracz]
	if not s then
		return
	end
	local pr = s.profil
	local palka = tonumber(gracz:GetAttribute("BonkMnoznikPalki")) or D.moc.mnoznik_palki
	local pety = tonumber(gracz:GetAttribute("BonkMnoznikPetow")) or D.moc.mnoznik_petow
	local moc = L.moc(pr.moc, palka, pety)
	pr.odblokowane = L.odblokowane(moc, D, pr, pr.odblokowane)
	gracz:SetAttribute("BonkMoc", moc)
	gracz:SetAttribute("BonkMocBaza", pr.moc)
	gracz:SetAttribute("BonkMonety", pr.monety)
	gracz:SetAttribute("BonkOdblokowane", pr.odblokowane)
	gracz:SetAttribute("BonkBonki", pr.bonki)
	gracz:SetAttribute("BonkNajdalej", math.floor(pr.najdalej))
	gracz:SetAttribute("BonkSamouczek", pr.samouczek)
	gracz:SetAttribute("BonkKraina", pr.kraina)
end

local function zapisz(gracz: Player, powod: string): boolean
	local s = stany[gracz]
	if not s or not magazyn or not s.zapisywalny then
		return false
	end
	local dane = table.clone(s.profil)
	dane.v = Z.wersja_profilu
	dane.zapisano = os.time()
	local ok, blad = pcall(function()
		magazyn:UpdateAsync(klucz(gracz), function()
			return dane
		end)
	end)
	if ok then
		s.ostatniZapis = os.clock()
		licz("LicznikZapisow")
	else
		licz("LicznikBledowZapisu")
		warn(P .. "zapis (" .. powod .. ") nie powiódł się: " .. tostring(blad))
	end
	return ok
end

local function wczytaj(gracz: Player): (any, boolean)
	if not magazyn then
		return L.nowyProfil(D), false
	end
	for proba = 1, Z.proby do
		local ok, w = pcall(function()
			return magazyn:GetAsync(klucz(gracz))
		end)
		if ok then
			licz("LicznikWczytan")
			return L.profil(w, D), true
		end
		warn(P .. "wczytanie, próba " .. proba .. ": " .. tostring(w))
		task.wait(proba)
	end
	-- bez wczytania nie zapisujemy (nie nadpiszemy prawdziwego postępu świeżym profilem)
	return L.nowyProfil(D), false
end

------------------------------------------------------------------ teleport, wejście i wyjście
local function hrpGracza(gracz: Player): BasePart?
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if hrp and hrp:IsA("BasePart") and hum and hum.Health > 0 then
		return hrp
	end
	return nil
end

local function przenies(gracz: Player, gdzie: Vector3, patrz: Vector3)
	local postac = gracz.Character
	if not postac then
		return
	end
	if workspace.StreamingEnabled then
		pcall(function()
			gracz:RequestStreamAroundAsync(gdzie, 5)
		end)
	end
	if postac.Parent then
		local cel = Vector3.new(patrz.X, gdzie.Y, patrz.Z)
		postac:PivotTo(CFrame.lookAt(gdzie + Vector3.new(0, 3.5, 0), cel + Vector3.new(0, 3.5, 0)))
		local hrp = postac:FindFirstChild("HumanoidRootPart")
		if hrp and hrp:IsA("BasePart") then
			hrp.AssemblyLinearVelocity = Vector3.zero
		end
	end
end

local function startKrainy(nr: number): (Vector3, Vector3)
	local K = D.krainy[nr]
	return Vector3.new(K.start[1], ziemia(K.start[1], K.start[2], K.start[3]), K.start[3]),
		Vector3.new(K.patrz[1], K.patrz[2], K.patrz[3])
end

local function wBonkuObszar(pos: Vector3): boolean
	local K1, KN = D.krainy[1], D.krainy[#D.krainy]
	return pos.X >= K1.xOd - 40 and pos.X <= KN.xDo + 40 and math.abs(pos.Z - K1.start[3]) <= 140
end

local function naStart(gracz: Player)
	local s = stany[gracz]
	if not s then
		return
	end
	local nr = math.clamp(s.profil.kraina or 1, 1, s.profil.odblokowane or 1)
	local gdzie, patrz = startKrainy(nr)
	przenies(gracz, gdzie, patrz)
	-- inne skrypty gry mogą jeszcze przestawić postać (wczytanie, odrodzenie) — sprawdzamy po chwili
	task.wait(1.5)
	local hrp = hrpGracza(gracz)
	if s.wBonk and hrp and not wBonkuObszar(hrp.Position) then
		przenies(gracz, gdzie, patrz)
	end
end

local function wejdz(gracz: Player, powod: string)
	local s = stany[gracz]
	if not s or s.wBonk or not s.gotowy then
		return
	end
	s.wBonk = true
	s.przerwa = os.clock() + D.portal.przerwa_s
	gracz:SetAttribute("BezBohatera", true)
	gracz:SetAttribute("BonkAktywny", true)
	kontener:SetAttribute("OstatnieWejscie", powod)
	task.spawn(naStart, gracz)
end

local function wyjdz(gracz: Player)
	local s = stany[gracz]
	if not s or not s.wBonk then
		return
	end
	s.wBonk = false
	s.przerwa = os.clock() + D.portal.przerwa_s
	gracz:SetAttribute("BonkAktywny", false)
	gracz:SetAttribute("BezBohatera", nil)
	task.spawn(zapisz, gracz, "wyjście portalem")
	local wyj = kontener:GetAttribute("PortalWyjscie")
	local pp = kontener:GetAttribute("PortalPoz")
	if typeof(wyj) == "Vector3" and typeof(pp) == "Vector3" then
		task.spawn(przenies, gracz, wyj, wyj + (wyj - pp))
	end
end

local function dolacz(gracz: Player)
	local s: any = {
		profil = L.nowyProfil(D), zapisywalny = false, wBonk = false, wiadro = nil, odrzucone = 0, przerwa = 0,
		gotowy = false, ostatniZapis = os.clock(), trafienia = 0,
	}
	stany[gracz] = s
	gracz:SetAttribute("BonkAktywny", false)
	gracz:SetAttribute("BonkMnoznikPalki", D.moc.mnoznik_palki)
	gracz:SetAttribute("BonkMnoznikPetow", D.moc.mnoznik_petow)
	local profil, zapisywalny = wczytaj(gracz)
	if stany[gracz] ~= s then
		return -- wyszedł w trakcie wczytywania
	end
	s.profil, s.zapisywalny, s.gotowy = profil, zapisywalny, true
	przelicz(gracz)
	gracz:SetAttribute("BonkProfilGotowy", true)
	for _, a in { "BonkMnoznikPalki", "BonkMnoznikPetow" } do
		gracz:GetAttributeChangedSignal(a):Connect(function()
			przelicz(gracz)
		end)
	end
	local function poOdrodzeniu(postac: Model)
		if not s.wBonk then
			return
		end
		task.wait(0.4)
		if gracz.Character == postac and s.wBonk then
			naStart(gracz)
		end
	end
	gracz.CharacterAdded:Connect(function(postac)
		task.spawn(poOdrodzeniu, postac)
	end)
	if kontener:GetAttribute(D.autostart) == true then
		if not gracz.Character then
			gracz.CharacterAdded:Wait()
		end
		task.wait(0.5)
		wejdz(gracz, "AutoStart")
	end
end

local function odejdz(gracz: Player)
	local s = stany[gracz]
	if not s then
		return
	end
	if s.gotowy then
		zapisz(gracz, "wyjście z gry")
	end
	stany[gracz] = nil
end

------------------------------------------------------------------ BONK
local function zdarzenie(t)
	evZdarzenia:FireAllClients(t)
end

evBonk.OnServerEvent:Connect(function(gracz: Player)
	local s = stany[gracz]
	if not s or not s.wBonk or not s.gotowy then
		return
	end
	local ok
	ok, s.wiadro = L.wiadro(s.wiadro, os.clock(), D.bonk.uderzen_na_s, D.bonk.zapas_uderzen)
	if not ok then
		s.odrzucone += 1
		return
	end
	local hrp = hrpGracza(gracz)
	if not hrp then
		return
	end
	local pos = hrp.Position
	local t = teraz()
	local lista = table.create(#potwory)
	for i, p in potwory do
		local x, z = polozenie(p, t)
		lista[i] = { x = x, z = z, promien = p.G.promien * (if p.rzadki then D.rzadki.skala else 1),
			zywy = p.zywy and math.abs(p.y - (pos.Y - 3)) < 14 }
	end
	local i = L.wybierzCel(pos.X, pos.Z, lista, D.bonk.zasieg)
	if not i then
		return
	end
	local p = potwory[i]
	local moc = gracz:GetAttribute("BonkMoc") or 1
	s.trafienia += 1
	if p.hp > moc then
		p.hp -= moc
		p.cfg:SetAttribute("Hp", p.hp)
		zdarzenie({ t = "cios", id = p.id, nr = p.nr, ile = moc, hp = p.hp, g = gracz.UserId })
		return
	end
	-- BONK: lot, nagroda, odrodzenie
	local mx, mz = lista[i].x, lista[i].z
	local lot = L.lot(moc, p.hpMax, D.lot)
	local kat = (math.random() * 2 - 1) * D.lot.rozrzut_kata
	local kx, kz = L.koniecLotu(mx, mz, mx - pos.X, mz - pos.Z, lot.odl, kat)
	local monety, zysk = L.nagroda(p.G, p.rzadki, lot.homeRun, D)
	local pr = s.profil
	pr.monety += monety
	pr.moc += zysk
	pr.bonki += 1
	if lot.odl > pr.najdalej then
		pr.najdalej = lot.odl
	end
	if lot.homeRun then
		pr.homeRuny += 1
	end
	if p.rzadki then
		pr.rzadkie += 1
	end
	if not pr.samouczek and pr.bonki >= 3 then
		pr.samouczek = true
	end
	local stareOdbl = pr.odblokowane
	przelicz(gracz)
	p.zywy = false
	p.hp = 0
	p.odrodzenie = os.clock() + losuj(PT.odrodzenie_s[1], PT.odrodzenie_s[2])
	p.cfg:SetAttribute("Hp", 0)
	p.cfg:SetAttribute("Zywy", false)
	zdarzenie({
		t = "lot", id = p.id, nr = p.nr, g = gracz.UserId, ile = moc,
		od = Vector3.new(mx, p.y, mz), ko = Vector3.new(kx, p.y, kz),
		wys = lot.wys, czas = lot.czas, hr = lot.homeRun, rz = p.rzadki, monety = monety, moc = zysk,
		brama = if pr.odblokowane > stareOdbl then pr.odblokowane else nil,
	})
end)

------------------------------------------------------------------ pętla: odrodzenia, wędrówka, portale, bramy, zapis
local portalPoz = kontener:GetAttribute("PortalPoz")
local powrot = kontener:GetAttribute("PowrotPoz")
if typeof(powrot) ~= "Vector3" then
	powrot = Vector3.new(D.powrot[1], D.powrot[2], D.powrot[3])
end
local akum, akumGraczy = 0, 0
RunService.Heartbeat:Connect(function(dt)
	akum += dt
	akumGraczy += dt
	if akum >= 0.2 then
		akum = 0
		local zegar = os.clock()
		local t = teraz()
		for _, p in potwory do
			if not p.zywy then
				if zegar >= p.odrodzenie then
					odrodz(p)
				end
			elseif zegar >= p.wedrowka then
				local x, z = polozenie(p, t)
				local r = PT.wedrowka_r
				local a = math.random() * 2 * math.pi
				local d = math.random() * r
				p.ox, p.oz = x, z
				p.cx, p.cz = p.domX + math.cos(a) * d, p.domZ + math.sin(a) * d
				p.t0 = t
				p.wedrowka = zegar + losuj(PT.wedrowka_s[1], PT.wedrowka_s[2])
				zapiszRuch(p)
			end
		end
	end
	if akumGraczy >= 0.2 then
		akumGraczy = 0
		local zegar = os.clock()
		for gracz, s in stany do
			local hrp = hrpGracza(gracz)
			if hrp and s.gotowy then
				local pos = hrp.Position
				if not s.wBonk then
					if typeof(portalPoz) == "Vector3" and zegar >= s.przerwa then
						local d = Vector3.new(pos.X - portalPoz.X, 0, pos.Z - portalPoz.Z).Magnitude
						if d <= D.portal.zasieg and math.abs(pos.Y - portalPoz.Y) < 9 then
							wejdz(gracz, "portal")
						end
					end
				else
					local d = Vector3.new(pos.X - powrot.X, 0, pos.Z - powrot.Z).Magnitude
					if zegar >= s.przerwa and typeof(portalPoz) == "Vector3" and d <= D.portal.zasieg
						and math.abs(pos.Y - powrot.Y) < 9 then
						wyjdz(gracz)
					elseif wBonkuObszar(pos) then
						-- bramy: dalej niż otwarte krainy nie wolno (klient otwiera wrota tylko u siebie)
						local nr = L.kraina(pos.X, D)
						local pr = s.profil
						local KN = D.krainy[#D.krainy]
						if (nr > pr.odblokowane or pos.X > KN.brama.x + 2) and zegar >= (s.cofniety or 0) then
							local K = if nr > pr.odblokowane then D.krainy[pr.odblokowane] else KN
							local cofnij = Vector3.new(K.brama.x - 8, pos.Y, K.start[3])
							s.cofniety = zegar + 1
							task.spawn(przenies, gracz, cofnij, cofnij - Vector3.new(10, 0, 0))
						elseif nr ~= pr.kraina then
							pr.kraina = nr
							gracz:SetAttribute("BonkKraina", nr)
						end
					end
				end
			end
			if s.zapisywalny and zegar - s.ostatniZapis >= Z.co_s then
				s.ostatniZapis = zegar
				task.spawn(zapisz, gracz, "co kilka minut")
			end
		end
	end
end)

Players.PlayerAdded:Connect(dolacz)
Players.PlayerRemoving:Connect(odejdz)
for _, g in Players:GetPlayers() do
	task.spawn(dolacz, g)
end
game:BindToClose(function()
	local zadania = 0
	for gracz in stany do
		zadania += 1
		task.spawn(function()
			zapisz(gracz, "zamknięcie serwera")
			zadania -= 1
		end)
	end
	local t0 = os.clock()
	while zadania > 0 and os.clock() - t0 < 20 do
		task.wait(0.1)
	end
end)

------------------------------------------------------------------ haczyki prób (tylko serwer)
local function pierwszy(): Player?
	return Players:GetPlayers()[1]
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any)
	if polecenie == "stan" then
		local t = teraz()
		local w = { gotowy = true, skrot = D.skrot, potworow = #potwory, zywych = 0, rzadkich = 0, gracze = {},
			zapis = kontener:GetAttribute("ZapisStan"), magazyn = kontener:GetAttribute("ZapisMagazyn"),
			zapisow = kontener:GetAttribute("LicznikZapisow"), wczytan = kontener:GetAttribute("LicznikWczytan"),
			bledow = kontener:GetAttribute("LicznikBledowZapisu"), krainy = {} }
		for k = 1, #D.krainy do
			w.krainy[k] = 0
		end
		for _, p in potwory do
			if p.zywy then
				w.zywych += 1
				w.krainy[p.kraina] = (w.krainy[p.kraina] or 0) + 1
			end
			if p.rzadki and p.zywy then
				w.rzadkich += 1
			end
		end
		for gracz, s in stany do
			table.insert(w.gracze, { bonk = s.wBonk, gotowy = s.gotowy, zapisywalny = s.zapisywalny, moc = gracz:GetAttribute("BonkMoc"),
				mocBaza = s.profil.moc, monety = s.profil.monety, bonki = s.profil.bonki, odblokowane = s.profil.odblokowane,
				kraina = s.profil.kraina, najdalej = s.profil.najdalej, homeRuny = s.profil.homeRuny,
				odrzucone = s.odrzucone, trafienia = s.trafienia, samouczek = s.profil.samouczek })
		end
		w.czas = t
		return w
	elseif polecenie == "moc" then
		-- haczyk próby: Moc z uderzeń ustawiona na `a` (tylko w Studio)
		local g = pierwszy()
		local s = g and stany[g]
		if not s or not RunService:IsStudio() then
			return false
		end
		s.profil.moc = tonumber(a) or s.profil.moc
		przelicz(g)
		return g:GetAttribute("BonkMoc")
	elseif polecenie == "wejdz" or polecenie == "wyjdz" then
		local g = pierwszy()
		if not g then
			return false
		end
		if polecenie == "wejdz" then
			wejdz(g, "polecenie")
		else
			wyjdz(g)
		end
		return true
	elseif polecenie == "kraina" then
		local g = pierwszy()
		if not g or not D.krainy[a] then
			return false
		end
		local gdzie, patrz = startKrainy(a)
		przenies(g, gdzie, patrz)
		return true
	elseif polecenie == "potwory" then
		local t = teraz()
		local w = {}
		for _, p in potwory do
			if (a == nil or p.kraina == a) then
				local x, z = polozenie(p, t)
				table.insert(w, { id = p.id, zywy = p.zywy, hp = p.hp, hpMax = p.hpMax, x = x, y = p.y, z = z, rzadki = p.rzadki,
					nr = p.nr, gatunek = p.klucz })
			end
		end
		return w
	elseif polecenie == "zapisz" then
		local g = pierwszy()
		return g ~= nil and zapisz(g, "polecenie")
	elseif polecenie == "odczyt" then
		-- surowy rekord z magazynu (tylko gdy magazyn otwarty — w próbie: magazyn próby)
		local g = pierwszy()
		if not g or not magazyn then
			return { magazyn = false }
		end
		local ok, v = pcall(function()
			return magazyn:GetAsync(klucz(g))
		end)
		return { magazyn = true, ok = ok, rekord = if ok then v else tostring(v) }
	elseif polecenie == "skasuj" or polecenie == "od_nowa" then
		-- tylko magazyn próby: rekord próby skasowany; "od_nowa" — świeży profil (zapis dalej działa),
		-- "skasuj" — koniec próby (bez zapisu przy wyjściu, żeby rekord próby nie wrócił)
		local g = pierwszy()
		local s = g and stany[g]
		if not s or not magazyn or kontener:GetAttribute("ZapisStan") ~= "włączony (magazyn próby)" then
			return false
		end
		local ok = pcall(function()
			magazyn:RemoveAsync(klucz(g))
		end)
		if polecenie == "od_nowa" then
			s.profil = L.nowyProfil(D)
			przelicz(g)
		else
			s.zapisywalny = false
		end
		return ok
	elseif polecenie == "wczytaj_ponownie" then
		local g = pierwszy()
		local s = g and stany[g]
		if not s then
			return false
		end
		local profil, zapisywalny = wczytaj(g)
		s.profil, s.zapisywalny = profil, zapisywalny
		przelicz(g)
		return { moc = profil.moc, monety = profil.monety, zapisywalny = zapisywalny }
	end
	return nil
end

kontener:SetAttribute("SerwerGotowy", true)
print(P .. string.format("serwer gotowy: %d potworów w %d krainach, zapis: %s", #potwory, #D.krainy,
	tostring(kontener:GetAttribute("ZapisStan"))))
