--[[
	SerwerBonk — serwer gry BONK (Script, RunContext Server, w Workspace/BonkGra). Jedyne źródło prawdy:
	potwory (życie, miejsce, odrodzenie), BONK (wybór celu, obrażenia = Moc, limit tempa, lot), nagrody, Moc, monety,
	bramy krain, wejście i wyjście portalem, zapis postępu.

	Stan potworów: Workspace/BonkGra/Stan/Potwory/<id> (Configuration z atrybutami — klient rysuje z nich modele).
	Stan gracza: atrybuty gracza Bonk* (BonkAktywny, BonkMoc, BonkMonety, BonkOdblokowane…) i BezBohatera
	(swiat/bohater_swiat nie rysuje bohatera klasy graczowi w BONK).
	Zdarzenia do klientów: Sygnaly/Zdarzenia (t = "cios" | "lot" | "wyklucie" | "kupiono" | "odmowa" | "prezent" |
	"nagroda_straznika" | "ogloszenie"). Od klienta: Sygnaly/Bonk (bez argumentów; serwer sam wybiera cel) i
	Sygnaly/Akcja (rodzaj, arg) — zakup pałki, jajko, wybór petów, tryb automatyczny, prezent; wszystko sprawdzane tu
	(odległość od stoiska / inkubatora, monety, kolejność, wiadro tempa). Haczyki prób: Sygnaly/SterowanieSerwera.

	Etap 2: pałki (profil.palka → BonkMnoznikPalki, model w prawej dłoni), jajka i pety (profil.pety, aktywne →
	BonkMnoznikPetow = 1 + suma premii, BonkPety dla klientów), Strażnicy (w liście potworów, wspólne życie, nagroda dla
	każdego, kto trafił, brama: L.mozePrzejsc z profil.straznicy), tablice, korona, leaderstats Power, komunikaty,
	dzienny prezent. W próbie (znacznik próby) zamiast nazw graczy „Player 1”, „Player 2”.
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
local evAkcja = Sygnaly:WaitForChild("Akcja")
local sterowanie = Sygnaly:WaitForChild("SterowanieSerwera")
local los = Random.new()
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
	p.rzadki = p.S == nil and math.random() < D.rzadki.szansa
	p.hpMax = L.zycie(p.G, p.rzadki, D)
	p.hp = p.hpMax
	p.zywy = true
	if p.S then
		-- Strażnik: stoi na arenie, nie wędruje; obrażenia liczone od nowa
		local m = p.S.miejsce
		local y = ziemia(m[1], m[2], m[3])
		p.domX, p.domZ, p.y = m[1], m[3], y
		p.ox, p.oz, p.cx, p.cz, p.t0 = m[1], m[3], m[1], m[3], teraz()
		p.wedrowka = math.huge
		p.obrazenia = {}
		p.cfg:SetAttribute("Powrot", nil)
	else
		rozstaw(p)
		p.wedrowka = os.clock() + losuj(PT.wedrowka_s[1], PT.wedrowka_s[2])
	end
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
-- Strażnicy: po jednym na krainę, w tej samej liście (ten sam BONK, widok i lot u klienta)
local straznicy: { any } = {}
for _, S in D.straznicy do
	local G = D.gatunki[S.gatunek]
	local id = "straznik_" .. S.kraina
	local cfg = Instance.new("Configuration")
	cfg.Name = id
	cfg:SetAttribute("Gatunek", S.gatunek)
	cfg:SetAttribute("Kraina", S.kraina)
	cfg:SetAttribute("Zagroda", "straznik")
	cfg:SetAttribute("Straznik", S.kraina)
	cfg:SetAttribute("Pr", 0)
	cfg:SetAttribute("Promien", G.promien)
	local p: any = {
		id = id, cfg = cfg, kraina = S.kraina, zagroda = nil, klucz = S.gatunek, G = G, slot = 1, S = S,
		domX = 0, domZ = 0, y = 0, ox = 0, oz = 0, cx = 0, cz = 0, t0 = 0, obrazenia = {},
		hp = 1, hpMax = 1, zywy = false, rzadki = false, nr = 0, odrodzenie = 0, wedrowka = math.huge,
	}
	odrodz(p)
	cfg.Parent = folderPotworow
	table.insert(potwory, p)
	poId[id] = p
	straznicy[S.kraina] = p
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
local nrGracza = 0 -- kolejny numer gracza (nazwy w próbie: „Player 1”, „Player 2”)

local function wProbie(): boolean
	return kontener:GetAttribute("ZapisStan") ~= "włączony"
end

-- nazwa gracza na tablicach i w komunikatach; w próbie (znacznik próby) bez nazwy konta
local function nazwaGracza(gracz: Player): string
	local s = stany[gracz]
	if wProbie() then
		return string.format(D.ui.gracz_proby, if s then s.nrProby else 0)
	end
	return gracz.DisplayName
end

local function zdarzenie(t)
	evZdarzenia:FireAllClients(t)
end

local function ogloszenie(tekst: string, kolor: string)
	zdarzenie({ t = "ogloszenie", tekst = tekst, kolor = kolor })
end

local function lista(tab: { string }): string
	return table.concat(tab, ",")
end

-- pety jako napis „id:kopie,…” (atrybut BonkPetyMam — okna klienta), Księga „id,…”
local function napisPetow(pr): (string, string)
	local mam, ks = {}, {}
	for _, id in D.petyKolejnosc do
		if pr.pety[id] then
			table.insert(mam, id .. ":" .. tostring(pr.pety[id]))
		end
		if pr.ksiega[id] then
			table.insert(ks, id)
		end
	end
	return lista(mam), lista(ks)
end

local function prezentDoAtrybutow(gracz: Player, pr)
	local mozna, nagroda, k = L.prezent(pr, L.dzien(os.time()), D)
	gracz:SetAttribute("BonkPrezentMozna", mozna)
	gracz:SetAttribute("BonkPrezentNagroda", nagroda)
	gracz:SetAttribute("BonkPrezentDzien", k)
end

local function przelicz(gracz: Player): (number, number)
	local s = stany[gracz]
	if not s then
		return 1, 1
	end
	local pr = s.profil
	if pr.autoPety then
		pr.aktywne = L.najlepszePety(pr.pety, D)
	end
	local palka = L.mnoznikPalki(pr.palka, D)
	local pety = L.mnoznikPetow(pr.aktywne, D)
	local moc = L.moc(pr.moc, palka, pety)
	local stare = pr.odblokowane
	pr.odblokowane = L.odblokowane(moc, D, pr, pr.odblokowane)
	gracz:SetAttribute("BonkMnoznikPalki", palka)
	gracz:SetAttribute("BonkMnoznikPetow", pety)
	gracz:SetAttribute("BonkMoc", moc)
	gracz:SetAttribute("BonkMocBaza", pr.moc)
	gracz:SetAttribute("BonkMonety", pr.monety)
	gracz:SetAttribute("BonkOdblokowane", pr.odblokowane)
	gracz:SetAttribute("BonkBonki", pr.bonki)
	gracz:SetAttribute("BonkNajdalej", math.floor(pr.najdalej))
	gracz:SetAttribute("BonkSamouczek", pr.samouczek)
	gracz:SetAttribute("BonkKraina", pr.kraina)
	gracz:SetAttribute("BonkPalka", pr.palka)
	gracz:SetAttribute("BonkPety", lista(pr.aktywne))
	gracz:SetAttribute("BonkAutoPety", pr.autoPety)
	local mam, ks = napisPetow(pr)
	gracz:SetAttribute("BonkPetyMam", mam)
	gracz:SetAttribute("BonkKsiega", ks)
	local st = {}
	for i = 1, #D.krainy do
		st[i] = tostring(pr.straznicy[i] or 0)
	end
	gracz:SetAttribute("BonkStraznicy", lista(st))
	prezentDoAtrybutow(gracz, pr)
	local ls = gracz:FindFirstChild("leaderstats")
	local v = ls and ls:FindFirstChild("Power")
	if v and v:IsA("IntValue") then
		v.Value = math.min(moc, 2 ^ 53)
	end
	if s.gotowy and pr.odblokowane > stare then
		ogloszenie(string.format(D.ui.ogl_kraina, nazwaGracza(gracz), D.krainy[pr.odblokowane].nazwa), D.ui.kolory.monety)
	end
	return stare, pr.odblokowane
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

------------------------------------------------------------------ pałka w dłoni, korona, leaderstats (widzą wszyscy)
local folderWzorcowRS = ReplicatedStorage:FindFirstChild(D.folderWzorcow)

local function bezFizyki(m: Instance)
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = false
			d.Massless = true
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.CastShadow = false
		end
	end
end

-- model pałki z wzorca (bryły w układzie RightGripAttachment) przyspawany do prawej dłoni
local function zalozPalke(gracz: Player)
	local s = stany[gracz]
	local postac = gracz.Character
	if not postac then
		return
	end
	local stara = postac:FindFirstChild("BonkPalka")
	local nr = if s and s.wBonk then s.profil.palka else 0
	if stara and stara:GetAttribute("Nr") == nr then
		return
	end
	if stara then
		stara:Destroy()
	end
	local P = D.palki[nr]
	local wz = P and folderWzorcowRS and folderWzorcowRS:FindFirstChild(P.wzorzec)
	if not wz then
		return
	end
	local dlon = postac:FindFirstChild("RightHand") or postac:FindFirstChild("Right Arm")
	if not dlon or not dlon:IsA("BasePart") then
		return
	end
	local zaczep = dlon:FindFirstChild("RightGripAttachment")
	local cf = if zaczep and zaczep:IsA("Attachment") then dlon.CFrame * zaczep.CFrame
		else dlon.CFrame * CFrame.new(0, -dlon.Size.Y / 2, 0) * CFrame.Angles(-math.pi / 2, 0, 0)
	local m = wz:Clone()
	m.Name = "BonkPalka"
	m:SetAttribute("Nr", nr)
	m:PivotTo(cf)
	bezFizyki(m)
	local w = Instance.new("WeldConstraint")
	w.Part0 = dlon
	w.Part1 = m.PrimaryPart
	w.Parent = m.PrimaryPart
	m.Parent = postac
end

local function korona(gracz: Player, tak: boolean)
	local postac = gracz.Character
	local glowa = postac and postac:FindFirstChild("Head")
	local stara = postac and postac:FindFirstChild("BonkKorona")
	gracz:SetAttribute("BonkKorona", tak)
	if not tak or not glowa or not glowa:IsA("BasePart") then
		if stara then
			stara:Destroy()
		end
		return
	end
	if stara then
		return
	end
	local zloto = Color3.fromHex(D.pokazanie.korona.kolor)
	local m = Instance.new("Model")
	m.Name = "BonkKorona"
	local baza = glowa.CFrame * CFrame.new(0, glowa.Size.Y / 2 + 0.45, 0)
	local function czesc(nazwa, rozmiar, cf, kolor, ksztalt, material)
		local p = Instance.new("Part")
		p.Name = nazwa
		p.Size = rozmiar
		p.CFrame = cf
		p.Color = kolor
		p.Shape = ksztalt or Enum.PartType.Block
		p.Material = material or Enum.Material.SmoothPlastic
		p.Reflectance = 0.15
		p.TopSurface = Enum.SurfaceType.Smooth
		p.BottomSurface = Enum.SurfaceType.Smooth
		p.Parent = m
		return p
	end
	local obrecz = czesc("Obrecz", Vector3.new(0.5, 1.5, 1.5), baza * CFrame.Angles(0, 0, math.pi / 2), zloto, Enum.PartType.Cylinder)
	m.PrimaryPart = obrecz
	for i = 0, 4 do
		local a = i * 2 * math.pi / 5
		local cf = baza * CFrame.Angles(0, a, 0) * CFrame.new(0, 0.45, -0.62)
		czesc("Zab" .. i, Vector3.new(0.34, 0.5, 0.34), cf * CFrame.Angles(0, math.pi / 4, 0), zloto)
		czesc("Kamien" .. i, Vector3.new(0.22, 0.22, 0.22), cf * CFrame.new(0, 0.32, 0), Color3.fromHex("E0223A"),
			Enum.PartType.Ball, Enum.Material.Neon)
	end
	bezFizyki(m)
	for _, p in m:GetChildren() do
		if p ~= obrecz and p:IsA("BasePart") then
			local w = Instance.new("WeldConstraint")
			w.Part0 = obrecz
			w.Part1 = p
			w.Parent = p
		end
	end
	local w = Instance.new("WeldConstraint")
	w.Part0 = glowa
	w.Part1 = obrecz
	w.Parent = obrecz
	m.Parent = postac
end

local function leaderstats(gracz: Player, tak: boolean)
	local ls = gracz:FindFirstChild("leaderstats")
	if not tak then
		local v = ls and ls:FindFirstChild("Power")
		if v then
			v:Destroy()
		end
		if ls and ls:GetAttribute("Bonk") == true and #ls:GetChildren() == 0 then
			ls:Destroy()
		end
		return
	end
	if not ls then
		ls = Instance.new("Folder")
		ls.Name = "leaderstats"
		ls:SetAttribute("Bonk", true)
		ls.Parent = gracz
	end
	if not ls:FindFirstChild("Power") then
		local v = Instance.new("IntValue")
		v.Name = "Power"
		v.Value = math.min(tonumber(gracz:GetAttribute("BonkMoc")) or 1, 2 ^ 53)
		v.Parent = ls
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
	leaderstats(gracz, true)
	task.spawn(naStart, gracz)
	task.delay(0.6, zalozPalke, gracz)
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
	leaderstats(gracz, false)
	korona(gracz, false)
	zalozPalke(gracz)
	task.spawn(zapisz, gracz, "wyjście portalem")
	local wyj = kontener:GetAttribute("PortalWyjscie")
	local pp = kontener:GetAttribute("PortalPoz")
	if typeof(wyj) == "Vector3" and typeof(pp) == "Vector3" then
		task.spawn(przenies, gracz, wyj, wyj + (wyj - pp))
	end
end

local function dolacz(gracz: Player)
	nrGracza += 1
	local s: any = {
		profil = L.nowyProfil(D), zapisywalny = false, wBonk = false, wiadro = nil, odrzucone = 0, przerwa = 0,
		gotowy = false, ostatniZapis = os.clock(), trafienia = 0, nrProby = nrGracza, wiadroAkcji = nil,
		odrzuconeAkcje = 0, ostatnieJajko = 0, akcji = 0,
	}
	stany[gracz] = s
	gracz:SetAttribute("BonkAktywny", false)
	gracz:SetAttribute("BonkMnoznikPalki", D.moc.mnoznik_palki)
	gracz:SetAttribute("BonkMnoznikPetow", D.moc.mnoznik_petow)
	local profil, zapisywalny = wczytaj(gracz)
	if stany[gracz] ~= s then
		return -- wyszedł w trakcie wczytywania
	end
	s.profil, s.zapisywalny = profil, zapisywalny
	przelicz(gracz)
	s.gotowy = true
	gracz:SetAttribute("BonkProfilGotowy", true)
	local function poOdrodzeniu(postac: Model)
		if not s.wBonk then
			return
		end
		task.wait(0.4)
		if gracz.Character == postac and s.wBonk then
			naStart(gracz)
			zalozPalke(gracz)
			korona(gracz, gracz:GetAttribute("BonkKorona") == true)
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

------------------------------------------------------------------ Strażnik pokonany
local function pokonajStraznika(p: any, zabojca: Player, lot: any, mx: number, mz: number, pos: Vector3)
	local S = p.S
	local nazwy = {}
	local monetyZabojcy, mocZabojcy = 0, 0
	for uid, dmg in p.obrazenia do
		local g = Players:GetPlayerByUserId(uid)
		local s = g and stany[g]
		if s and s.gotowy then
			local monety, moc = L.nagrodaStraznika(S, dmg / math.max(1, p.hpMax), D)
			local pr = s.profil
			pr.monety += monety
			pr.moc += moc
			pr.straznicy[S.kraina] = (pr.straznicy[S.kraina] or 0) + 1
			przelicz(g)
			table.insert(nazwy, nazwaGracza(g))
			evZdarzenia:FireClient(g, { t = "nagroda_straznika", monety = monety, moc = moc, nazwa = S.nazwa,
				udzial = dmg / math.max(1, p.hpMax) })
			if g == zabojca then
				monetyZabojcy, mocZabojcy = monety, moc
			end
		end
	end
	table.sort(nazwy)
	if #nazwy > 3 then
		nazwy = { nazwy[1], nazwy[2], string.format("%d more", #nazwy - 2) }
	end
	ogloszenie(string.format(D.ui.ogl_straznik, table.concat(nazwy, ", "), S.nazwa), "FF6A3D")
	p.zywy = false
	p.hp = 0
	p.obrazenia = {}
	p.odrodzenie = os.clock() + losuj(D.straznik.odrodzenie_s[1], D.straznik.odrodzenie_s[2])
	p.cfg:SetAttribute("Powrot", teraz() + (p.odrodzenie - os.clock()))
	p.cfg:SetAttribute("Hp", 0)
	p.cfg:SetAttribute("Zywy", false)
	-- wielki lot w niebo: daleko od gracza i wysoko
	local kx, kz = L.koniecLotu(mx, mz, mx - pos.X, mz - pos.Z, 120, 0)
	zdarzenie({
		t = "lot", id = p.id, nr = p.nr, g = zabojca.UserId, ile = lot.ile, od = Vector3.new(mx, p.y, mz),
		ko = Vector3.new(kx, p.y + D.straznik.lot_wys, kz), wys = D.straznik.lot_wys * 0.25, czas = D.straznik.lot_czas,
		hr = true, rz = false, monety = monetyZabojcy, moc = mocZabojcy, niebo = true,
	})
end

------------------------------------------------------------------ BONK
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
	if p.S then
		p.obrazenia[gracz.UserId] = (p.obrazenia[gracz.UserId] or 0) + math.min(moc, p.hp)
	end
	if p.hp > moc then
		p.hp -= moc
		p.cfg:SetAttribute("Hp", p.hp)
		zdarzenie({ t = "cios", id = p.id, nr = p.nr, ile = moc, hp = p.hp, g = gracz.UserId })
		return
	end
	-- BONK: lot, nagroda, odrodzenie
	local mx, mz = lista[i].x, lista[i].z
	if p.S then
		pokonajStraznika(p, gracz, { ile = moc }, mx, mz, pos)
		return
	end
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
	local stareOdbl = przelicz(gracz)
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

------------------------------------------------------------------ akcje gracza (sklep, jajko, pety, prezent)
local function blisko(gracz: Player, punkt: { number }, zasieg: number): boolean
	local hrp = hrpGracza(gracz)
	if not hrp then
		return false
	end
	local d = Vector3.new(hrp.Position.X - punkt[1], 0, hrp.Position.Z - punkt[3]).Magnitude
	return d <= zasieg + 4 -- zapas na opóźnienie ruchu
end

local function przySklepie(gracz: Player): boolean
	for _, sk in D.sklepy do
		if blisko(gracz, sk.miejsce, D.sklep.zasieg) then
			return true
		end
	end
	return false
end

local function odmowa(gracz: Player, powod: string?)
	evZdarzenia:FireClient(gracz, { t = "odmowa", powod = powod or "?" })
end

local AKCJE = { palka = true, jajko = true, pety = true, auto = true, prezent = true }

evAkcja.OnServerEvent:Connect(function(gracz: Player, rodzaj: any, arg: any)
	local s = stany[gracz]
	if not s or not s.wBonk or not s.gotowy then
		return
	end
	if type(rodzaj) ~= "string" or not AKCJE[rodzaj] then
		return
	end
	local ok
	ok, s.wiadroAkcji = L.wiadro(s.wiadroAkcji, os.clock(), D.akcje.na_s, D.akcje.zapas)
	if not ok then
		s.odrzuconeAkcje += 1
		return
	end
	s.akcji += 1
	local pr = s.profil
	if rodzaj == "palka" then
		if type(arg) ~= "number" or not przySklepie(gracz) then
			return odmowa(gracz, "daleko")
		end
		local kupiono, powod = L.kupPalke(pr, arg, D)
		if not kupiono then
			return odmowa(gracz, powod)
		end
		przelicz(gracz)
		zalozPalke(gracz)
		evZdarzenia:FireClient(gracz, { t = "kupiono", nr = arg })
	elseif rodzaj == "jajko" then
		local J = type(arg) == "number" and D.jajka[arg]
		if not J or not blisko(gracz, J.miejsce, D.petyUst.zasieg_inkubatora) then
			return odmowa(gracz, "daleko")
		end
		if os.clock() - s.ostatnieJajko < D.petyUst.przerwa_wyklucia_s then
			return odmowa(gracz, "czekaj")
		end
		local wyklute, w = L.wyklujJajko(pr, arg, los:NextNumber(), D)
		if not wyklute then
			return odmowa(gracz, w)
		end
		s.ostatnieJajko = os.clock()
		przelicz(gracz)
		evZdarzenia:FireClient(gracz, { t = "wyklucie", jajko = arg, pet = w.pet, nowy = w.nowy, kopie = w.kopie,
			rzadkosc = w.rzadkosc })
		if w.rzadkosc >= #D.rzadkosci then
			local P = D.pety[w.pet]
			task.delay(2.4, ogloszenie, string.format(D.ui.ogl_legendarny, nazwaGracza(gracz), P.nazwa),
				D.rzadkosci[w.rzadkosc].kolor)
		end
	elseif rodzaj == "pety" then
		if type(arg) ~= "table" or #arg > 10 then
			return
		end
		pr.autoPety = false
		pr.aktywne = L.aktywneZListy(arg, pr.pety, D)
		przelicz(gracz)
	elseif rodzaj == "auto" then
		pr.autoPety = arg == true
		przelicz(gracz)
	elseif rodzaj == "prezent" then
		local odebrano, nagroda, k = L.odbierzPrezent(pr, L.dzien(os.time()), D)
		if not odebrano then
			return odmowa(gracz, "jutro")
		end
		przelicz(gracz)
		evZdarzenia:FireClient(gracz, { t = "prezent", monety = nagroda, dzien = k })
	end
end)

------------------------------------------------------------------ tablice, korona, prezent (co kilka sekund)
local folderTablic = kontener:FindFirstChild("Stanowiska")
local function wiersze(nr: number, w: { string })
	local t = folderTablic and folderTablic:FindFirstChild("Tablica" .. nr)
	if not t then
		return
	end
	for i = 1, D.pokazanie.wierszy do
		local napis = t:FindFirstChild("Rzad" .. i, true)
		if napis and napis:IsA("TextLabel") then
			napis.Text = w[i] or ""
		end
	end
end

local function odswiezPokazanie()
	local gracze = {}
	for g, s in stany do
		if s.gotowy and g.Parent then
			local n = L.ksiega(s.profil, D)
			table.insert(gracze, { g = g, nazwa = nazwaGracza(g), moc = tonumber(g:GetAttribute("BonkMoc")) or 1,
				lot = s.profil.najdalej, ksiega = n, wBonk = s.wBonk })
		end
	end
	local function tablica(nr: number, pole: string, format: (any) -> string)
		table.sort(gracze, function(a, b)
			if a[pole] ~= b[pole] then
				return a[pole] > b[pole]
			end
			return a.nazwa < b.nazwa
		end)
		local w = {}
		for i = 1, math.min(#gracze, D.pokazanie.wierszy) do
			local x = gracze[i]
			w[i] = string.format("%d. %s — %s", i, x.nazwa, format(x[pole]))
		end
		wiersze(nr, w)
	end
	local razem = #D.petyKolejnosc
	tablica(3, "ksiega", function(n)
		return string.format("%d/%d", n, razem)
	end)
	tablica(2, "lot", function(n)
		return L.format(n) .. " studs"
	end)
	tablica(1, "moc", function(n)
		return L.format(n)
	end)
	-- korona: najsilniejszy w BONK (Moc > 1)
	local krol = gracze[1]
	for _, x in gracze do
		korona(x.g, krol ~= nil and x.g == krol.g and x.wBonk and x.moc > 1)
	end
	for g, s in stany do
		if s.gotowy then
			prezentDoAtrybutow(g, s.profil)
		end
	end
end

------------------------------------------------------------------ pętla: odrodzenia, wędrówka, portale, bramy, zapis
local portalPoz = kontener:GetAttribute("PortalPoz")
local powrot = kontener:GetAttribute("PowrotPoz")
if typeof(powrot) ~= "Vector3" then
	powrot = Vector3.new(D.powrot[1], D.powrot[2], D.powrot[3])
end
local akum, akumGraczy, akumPokazania = 0, 0, 0
RunService.Heartbeat:Connect(function(dt)
	akum += dt
	akumGraczy += dt
	akumPokazania += dt
	if akumPokazania >= D.pokazanie.co_s then
		akumPokazania = 0
		task.spawn(odswiezPokazanie)
	end
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
			local pr = s.profil
			local ls = gracz:FindFirstChild("leaderstats")
			local power = ls and ls:FindFirstChild("Power")
			local postac = gracz.Character
			local palka = postac and postac:FindFirstChild("BonkPalka")
			table.insert(w.gracze, { bonk = s.wBonk, gotowy = s.gotowy, zapisywalny = s.zapisywalny, moc = gracz:GetAttribute("BonkMoc"),
				mocBaza = pr.moc, monety = pr.monety, bonki = pr.bonki, odblokowane = pr.odblokowane,
				kraina = pr.kraina, najdalej = pr.najdalej, homeRuny = pr.homeRuny,
				odrzucone = s.odrzucone, trafienia = s.trafienia, samouczek = pr.samouczek,
				palka = pr.palka, pety = pr.pety, aktywne = pr.aktywne, autoPety = pr.autoPety, ksiega = (L.ksiega(pr, D)),
				straznicy = pr.straznicy, prezent = pr.prezent, jajek = pr.jajek, akcji = s.akcji, odrzuconeAkcje = s.odrzuconeAkcje,
				mnoznikPalki = gracz:GetAttribute("BonkMnoznikPalki"), mnoznikPetow = gracz:GetAttribute("BonkMnoznikPetow"),
				power = if power then power.Value else nil, korona = postac ~= nil and postac:FindFirstChild("BonkKorona") ~= nil,
				palkaWDloni = if palka then palka:GetAttribute("Nr") else nil,
				palkaCzesci = if palka then #palka:GetChildren() else 0, nazwa = nazwaGracza(gracz) })
		end
		w.straznicy = {}
		for nr, p in straznicy do
			local n = 0
			for _ in p.obrazenia do
				n += 1
			end
			w.straznicy[nr] = { hp = p.hp, hpMax = p.hpMax, zywy = p.zywy, bijacych = n, powrot = p.cfg:GetAttribute("Powrot") }
		end
		w.tablice = {}
		for nr = 1, 3 do
			local t = folderTablic and folderTablic:FindFirstChild("Tablica" .. nr)
			local r1 = t and t:FindFirstChild("Rzad1", true)
			w.tablice[nr] = if r1 and r1:IsA("TextLabel") then r1.Text else nil
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
			zalozPalke(g)
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
		zalozPalke(g)
		return { moc = profil.moc, monety = profil.monety, zapisywalny = zapisywalny, palka = profil.palka, pety = profil.pety,
			aktywne = profil.aktywne, straznicy = profil.straznicy, prezent = profil.prezent, ksiega = (L.ksiega(profil, D)),
			v = profil.v }
	end
	-- etap 2 (tylko w Studio)
	local g = pierwszy()
	local s = g and stany[g]
	if not s or not RunService:IsStudio() then
		return nil
	end
	if polecenie == "monety" then
		s.profil.monety = tonumber(a) or s.profil.monety
		przelicz(g)
		return s.profil.monety
	elseif polecenie == "zapisz_v1" then
		-- tylko magazyn próby: rekord w formacie etapu 1 (do próby migracji v1 → v2)
		if not magazyn or kontener:GetAttribute("ZapisStan") ~= "włączony (magazyn próby)" then
			return false
		end
		local v1 = { v = 1, moc = 3000, monety = 900, bonki = 40, najdalej = 130, homeRuny = 2, rzadkie = 1, odblokowane = 1,
			kraina = 1, samouczek = true, palka = 1, pety = {}, straznicy = {}, zapisano = os.time() }
		return (pcall(function()
			magazyn:SetAsync(klucz(g), v1)
		end))
	elseif polecenie == "prezent_wczoraj" then
		s.profil.prezent.dzien = L.dzien(os.time()) - (tonumber(a) or 1)
		przelicz(g)
		return true
	elseif polecenie == "straznik_hp" then
		local p = straznicy[a]
		if not p or not p.zywy then
			return false
		end
		p.hp = math.max(1, tonumber(b) or p.hp)
		p.cfg:SetAttribute("Hp", p.hp)
		return p.hp
	elseif polecenie == "straznik_odrodz" then
		local p = straznicy[a]
		if not p then
			return false
		end
		if not p.zywy then
			odrodz(p)
		end
		return true
	elseif polecenie == "straznicy_profil" then
		-- haczyk próby: pokonani Strażnicy w profilu (lista liczb)
		if type(a) == "table" then
			for i = 1, #D.krainy do
				s.profil.straznicy[i] = tonumber(a[i]) or 0
			end
			przelicz(g)
		end
		return s.profil.straznicy
	elseif polecenie == "odswiez" then
		odswiezPokazanie()
		return true
	end
	return nil
end

kontener:SetAttribute("SerwerGotowy", true)
print(P .. string.format("serwer gotowy: %d potworów w %d krainach, zapis: %s", #potwory, #D.krainy,
	tostring(kontener:GetAttribute("ZapisStan"))))
