--[[
	SerwerPetArena — serwer gry Pet Arena (Script, RunContext Server, w Workspace/PetArenaGra). Jedyne źródło prawdy:
	walka w 2D (LogikaPetArena, stały krok), rzuty, umiejętności, złoto, nagroda za głowę, dzikie pety, odpoczynek petów,
	profile graczy (w pamięci — zapis do magazynu w etapie 2).

	Od klienta tylko Sygnaly/Akcja (rodzaj, a, b, c): "rzut", nr w drużynie, x, z · "umiejetnosc" · "wybierz", nr —
	serwer sprawdza typy, wiadro tempa (wspólne), cel na arenie, limit areny, jeden pet gracza naraz, odpoczynek.
	Do klientów: Sygnaly/Stan (UnreliableRemoteEvent, bufor: pety co walka.stan_co_s) i Sygnaly/Zdarzenia (lista
	zdarzeń z kroku: rzut, ladowanie, cios, umiejetnosc, ringout, ko, krol, zloto, odmowa…). Stan gracza w atrybutach
	PA_* (ustawia tylko serwer). Haczyki prób: Sygnaly/SterowanieSerwera. W próbie (znacznik ZapisProbaDo z
	tools/zapis_prob.py) zamiast nazw kont „Player 1”, „Player 2”.
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
local D = require(Moduly:WaitForChild("DanePetArena"))
local L = require(Moduly:WaitForChild("LogikaPetArena"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evAkcja = Sygnaly:WaitForChild("Akcja")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local evStan = Sygnaly:WaitForChild("Stan")
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

------------------------------------------------------------------ wzorce petów → ReplicatedStorage (klienci je klonują)
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
		warn(P .. "brak folderu Wzorce w kontenerze — pety będą zastępczymi bryłami")
		kontener:SetAttribute("WzorceGotowe", false)
	end
end

local los = Random.new()
local S = L.nowyStan(D, function()
	return los:NextNumber()
end)
local proba = kontener:GetAttribute("ZapisProbaDo") ~= nil
kontener:SetAttribute("ZapisStan", "w pamięci (etap 1, bez magazynu)")
local odpoczynekS = D.odpoczynek
local liczniki: { [string]: number } = {}
local doWyslania = {}

local function teraz(): number
	return workspace:GetServerTimeNow()
end

------------------------------------------------------------------ gracze
type Gracz = { slot: number, profil: any, druzyna: { any }, wybrany: number, naArenie: number?, wiadro: any, nazwa: string,
	odrzucone: number, gs: number }
local gracze: { [Player]: Gracz } = {}
local poSlocie: { [number]: Player } = {}
local nrProby = 0

local function wolnySlot(): number?
	for i = 1, #D.sloty do
		if not poSlocie[i] then
			return i
		end
	end
	return nil
end

local function postacNaSlot(plr: Player, g: Gracz)
	local c = plr.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart")
	if not hrp then
		return
	end
	local s = D.sloty[g.slot]
	local poz = Vector3.new(s.poz[1], s.poz[2] + 3.2, s.poz[3])
	c:PivotTo(CFrame.lookAt(poz, Vector3.new(0, poz.Y, 0)))
end

local function atrybutyDruzyny(plr: Player, g: Gracz)
	local ids, odp, prob = {}, {}, {}
	for _, w in g.druzyna do
		table.insert(ids, w.id)
		table.insert(odp, string.format("%.2f", w.odpoczynek or 0))
		table.insert(prob, if w.probny then "1" else "0")
	end
	plr:SetAttribute("PA_Druzyna", table.concat(ids, ","))
	plr:SetAttribute("PA_Odpoczynek", table.concat(odp, ","))
	plr:SetAttribute("PA_Probny", table.concat(prob, ","))
	plr:SetAttribute("PA_Wybrany", g.wybrany)
	plr:SetAttribute("PA_NaArenie", g.naArenie or 0)
end

local function dodajZloto(plr: Player, g: Gracz, ile: number)
	g.profil.zloto += ile
	plr:SetAttribute("PA_Zloto", g.profil.zloto)
end

local function dolacz(plr: Player)
	local slot = wolnySlot()
	if not slot then
		plr:SetAttribute("PA_Slot", 0)
		return
	end
	nrProby += 1
	local profil = L.profilNowy(D)
	local g: Gracz = { slot = slot, profil = profil, druzyna = L.druzyna(D, profil, los:NextNumber()), wybrany = 1,
		naArenie = nil, wiadro = {}, nazwa = if proba then string.format(D.ui.gracz_proby, nrProby) else plr.DisplayName,
		odrzucone = 0, gs = 0 }
	gracze[plr] = g
	poSlocie[slot] = plr
	plr:SetAttribute("PA_Slot", slot)
	plr:SetAttribute("PA_Nazwa", g.nazwa)
	plr:SetAttribute("PA_Zloto", profil.zloto)
	plr:SetAttribute("PA_GS", 0)
	plr:SetAttribute("PA_Pet", 0)
	plr:SetAttribute("PA_Rzucil", false)
	plr:SetAttribute("PA_Wybicia", 0)
	atrybutyDruzyny(plr, g)
	plr.CharacterAdded:Connect(function(c)
		c:WaitForChild("HumanoidRootPart", 10)
		task.wait()
		if gracze[plr] then
			postacNaSlot(plr, gracze[plr])
		end
	end)
	if plr.Character then
		postacNaSlot(plr, g)
	end
end

local function odejdz(plr: Player)
	local g = gracze[plr]
	if not g then
		return
	end
	local p = L.petGracza(S, g.slot)
	if p then
		-- pet odchodzącego gracza zostaje dziki do końca walki
		p.dziki = true
		p.wl = 0
	end
	poSlocie[g.slot] = nil
	gracze[plr] = nil
end

------------------------------------------------------------------ zdarzenia kroku → nagrody, odpoczynek, do klientów
local ostatnie = {}
local function wyslij(z)
	liczniki[z.t] = (liczniki[z.t] or 0) + 1
	if z.t == "cios" or z.t == "ringout" or z.t == "ko" or z.t == "krol" or z.t == "umiejetnosc" then
		table.insert(ostatnie, { t = z.t, a = z.a, b = z.b, id = z.id, v = z.v, k = z.k, przez = z.przez, premia = z.premia,
			nagroda = z.nagroda, krol = z.krol })
		if #ostatnie > 40 then
			table.remove(ostatnie, 1)
		end
	end
	table.insert(doWyslania, z)
end

local function obsluzZdarzenia(lista)
	for _, z in lista do
		if z.t == "ringout" or z.t == "ko" then
			local ofiara = poSlocie[z.wl]
			if z.wl > 0 and not z.dziki and ofiara and gracze[ofiara] then
				local g = gracze[ofiara]
				local w = g.naArenie and g.druzyna[g.naArenie]
				if w then
					w.odpoczynek = teraz() + odpoczynekS
				end
				g.naArenie = nil
				ofiara:SetAttribute("PA_Pet", 0)
				atrybutyDruzyny(ofiara, g)
			end
			local zabojca = poSlocie[z.przez]
			if z.przez > 0 and zabojca and gracze[zabojca] and (z.premia > 0 or z.nagroda > 0) then
				local g = gracze[zabojca]
				dodajZloto(zabojca, g, z.premia + z.nagroda)
				g.profil.wybicia += 1
				zabojca:SetAttribute("PA_Wybicia", g.profil.wybicia)
			end
			z.wlPrzez = z.przez
		end
		wyslij(z)
	end
end

------------------------------------------------------------------ dzikie pety
local nastBot = D.boty.pierwszy_s
local czekajBota: { [number]: number } = {}

local function rzutDzikiego(nr: number?, x: number?, z: number?)
	local n = nr or L.losujPetaBota(D, los:NextNumber(), los:NextNumber())
	local g = math.floor(los:NextNumber() * D.scena.gejzery)
	local a = 2 * math.pi * (g + 0.5) / D.scena.gejzery
	local x0, z0 = math.sin(a) * D.scena.gejzer_r, math.cos(a) * D.scena.gejzer_r
	local r = los:NextNumber() * 14
	local b = los:NextNumber() * 2 * math.pi
	local tx, tz = x or math.sin(b) * r, z or math.cos(b) * r
	local p = L.dodajPeta(S, n, 0, true, x0, D.scena.woda_y, z0, tx, tz)
	wyslij({ t = "rzut", id = p.id, nr = p.nr, wl = 0, dziki = true, x0 = x0, y0 = D.scena.woda_y, z0 = z0, x = tx, z = tz,
		czas = p.lotCzas })
	return p
end

local function botyKrok()
	if S.czas >= nastBot and L.ileBotowBrakuje(S) > 0 then
		rzutDzikiego()
		nastBot = S.czas + (S.botyCo or D.boty.co_s)
	end
	local zd = {}
	for _, p in S.pety do
		if p.dziki and p.faza == "walka" then
			local c = czekajBota[p.id]
			if not c then
				c = D.boty.czekaj_s[1] + los:NextNumber() * (D.boty.czekaj_s[2] - D.boty.czekaj_s[1])
				czekajBota[p.id] = c
			end
			if L.botChce(S, p, c) then
				L.uzyj(S, p, zd)
				czekajBota[p.id] = nil
			end
		end
	end
	obsluzZdarzenia(zd)
end

------------------------------------------------------------------ akcje graczy
local function odmowa(plr: Player, powod: string)
	local g = gracze[plr]
	if g then
		g.odrzucone += 1
	end
	evZdarzenia:FireClient(plr, { { t = "odmowa", powod = powod } })
end

local function rzut(plr: Player, g: Gracz, nr: any, x: any, z: any)
	if type(nr) ~= "number" or nr ~= math.floor(nr) or nr < 1 or nr > #g.druzyna then
		return odmowa(plr, "zle")
	end
	if L.petGracza(S, g.slot) then
		return odmowa(plr, "masz")
	end
	local w = g.druzyna[nr]
	if not L.gotowy(w, teraz()) then
		return odmowa(plr, "odpoczywa")
	end
	local ok, powod = L.mozeRzucic(S, x, z)
	if not ok then
		return odmowa(plr, powod or "zle")
	end
	local s = D.sloty[g.slot]
	local start = Vector3.new(s.poz[1], s.poz[2] + 4, s.poz[3])
	local c = plr.Character
	local reka = c and (c:FindFirstChild("RightHand") or c:FindFirstChild("Right Arm") or c:FindFirstChild("HumanoidRootPart"))
	if reka and reka:IsA("BasePart") and (reka.Position - start).Magnitude < 12 then
		start = reka.Position + Vector3.new(0, 1, 0)
	end
	local p = L.dodajPeta(S, w.nr, g.slot, false, start.X, start.Y, start.Z, x, z)
	g.naArenie = nr
	g.wybrany = nr
	g.profil.rzuty += 1
	plr:SetAttribute("PA_Pet", p.id)
	plr:SetAttribute("PA_Rzucil", true)
	atrybutyDruzyny(plr, g)
	wyslij({ t = "rzut", id = p.id, nr = p.nr, wl = g.slot, dziki = false, x0 = start.X, y0 = start.Y, z0 = start.Z, x = x, z = z,
		czas = p.lotCzas })
end

evAkcja.OnServerEvent:Connect(function(plr: Player, rodzaj: any, a: any, b: any, c: any)
	local g = gracze[plr]
	if not g or type(rodzaj) ~= "string" then
		return
	end
	if not L.wiadro(g.wiadro, os.clock(), D.rzut.wiadro_na_s, D.rzut.wiadro_zapas) then
		g.odrzucone += 1
		return
	end
	if rodzaj == "rzut" then
		rzut(plr, g, a, b, c)
	elseif rodzaj == "umiejetnosc" then
		local p = L.petGracza(S, g.slot)
		local zd = {}
		if p and L.uzyj(S, p, zd) then
			obsluzZdarzenia(zd)
		else
			odmowa(plr, "pasek")
		end
	elseif rodzaj == "wybierz" then
		if type(a) == "number" and a == math.floor(a) and a >= 1 and a <= #g.druzyna then
			g.wybrany = a
			plr:SetAttribute("PA_Wybrany", a)
		end
	else
		g.odrzucone += 1
	end
end)

------------------------------------------------------------------ stan do klientów (bufor)
local ROZMIAR_PETA = 22
local function migawka(): buffer
	local n = #S.pety
	local b = buffer.create(14 + n * ROZMIAR_PETA)
	buffer.writef64(b, 0, teraz())
	buffer.writeu16(b, 8, n)
	buffer.writeu16(b, 10, S.krol or 0)
	buffer.writeu16(b, 12, math.clamp(math.floor(S.nagroda + 0.5), 0, 65535))
	local t = S.czas
	for i, p in S.pety do
		local o = 14 + (i - 1) * ROZMIAR_PETA
		local f = 0
		if p.ogl > t then
			f += 1
		end
		if p.lod > t then
			f += 2
		end
		if p.skor > t then
			f += 4
		end
		if p.pal > t then
			f += 8
		end
		if p.akcja and p.akcja.typ ~= "skok" then
			f += 16
		end
		if p.akcja and p.akcja.typ == "skok" then
			f += 32
		end
		if S.krol == p.id then
			f += 64
		end
		if p.osz > t then
			f += 128
		end
		buffer.writeu16(b, o, p.id % 65536)
		buffer.writeu8(b, o + 2, p.nr)
		buffer.writeu8(b, o + 3, if p.dziki then 0 else p.wl)
		buffer.writeu8(b, o + 4, if p.faza == "walka" then 1 else 0)
		buffer.writeu8(b, o + 5, f)
		buffer.writef32(b, o + 6, p.x)
		buffer.writef32(b, o + 10, p.z)
		buffer.writeu16(b, o + 14, math.clamp(math.floor(p.hp * 10 + 0.5), 0, 65535))
		buffer.writeu16(b, o + 16, math.clamp(math.floor(p.hpMax * 10 + 0.5), 0, 65535))
		buffer.writeu8(b, o + 18, math.clamp(math.floor(p.pasek * 255 + 0.5), 0, 255))
		buffer.writeu8(b, o + 19, math.clamp(math.floor(p.zl + 0.5), 0, 255))
		buffer.writei16(b, o + 20, math.clamp(math.floor((p.kier or 0) * 1000 + 0.5), -32000, 32000))
	end
	return b
end

------------------------------------------------------------------ pętla
local zbior = 0
local doStanu = 0
local doZlota = 1
local pauza = false
local czasKroku, ileKrokow = 0, 0

RunService.Heartbeat:Connect(function(dt: number)
	if pauza then
		return
	end
	local krok = D.walka.krok_s
	zbior = math.min(zbior + dt, krok * 4)
	local t0 = os.clock()
	while zbior >= krok do
		zbior -= krok
		obsluzZdarzenia(L.krok(S, krok))
		botyKrok()
		doZlota -= krok
		if doZlota <= 0 then
			doZlota += 1
			local w = L.zlotoTick(S)
			for plr, g in gracze do
				local ile = w[g.slot] or 0
				g.gs = ile
				plr:SetAttribute("PA_GS", ile)
				if ile > 0 then
					dodajZloto(plr, g, ile)
					local p = L.petGracza(S, g.slot)
					if p then
						evZdarzenia:FireClient(plr, { { t = "zloto", id = p.id, ile = ile } })
					end
				end
			end
		end
	end
	czasKroku += os.clock() - t0
	ileKrokow += 1
	doStanu -= dt
	if doStanu <= 0 then
		doStanu = D.walka.stan_co_s
		evStan:FireAllClients(migawka())
	end
	if #doWyslania > 0 then
		local lista = doWyslania
		doWyslania = {}
		evZdarzenia:FireAllClients(lista)
	end
end)

Players.PlayerAdded:Connect(dolacz)
Players.PlayerRemoving:Connect(odejdz)
for _, plr in Players:GetPlayers() do
	task.spawn(dolacz, plr)
end
kontener:SetAttribute("SerwerGotowy", true)
print(P .. "serwer gotowy (" .. D.skrot .. ")")

------------------------------------------------------------------ haczyki prób
local function opisPeta(p)
	return { id = p.id, nr = p.nr, pet = p.P.id, nazwa = p.P.nazwa, wl = p.wl, dziki = p.dziki, x = p.x, z = p.z, hp = p.hp,
		hpMax = p.hpMax, faza = p.faza, pasek = p.pasek, krol = S.krol == p.id, zl = p.zl,
		akcja = if p.akcja then p.akcja.typ else nil, r = L.dlug(p.x, p.z) }
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any, c: any)
	if polecenie == "stan" then
		local pety = {}
		for _, p in S.pety do
			table.insert(pety, opisPeta(p))
		end
		local lista = {}
		local tn = teraz()
		for plr, g in gracze do
			local dr = {}
			for _, w in g.druzyna do
				table.insert(dr, { id = w.id, odpoczynek_s = L.zostalo(w, tn), probny = w.probny })
			end
			table.insert(lista, { nazwa = g.nazwa, slot = g.slot, zloto = g.profil.zloto, gs = g.gs,
				pet = plr:GetAttribute("PA_Pet"), druzyna = dr, wybrany = g.wybrany, naArenie = g.naArenie,
				wybicia = g.profil.wybicia, rzuty = g.profil.rzuty, odrzucone = g.odrzucone })
		end
		return { gotowy = true, czas = S.czas, pety = pety, krol = S.krol, nagroda = S.nagroda, gracze = lista,
			dzikich = L.ileDzikich(S), liczniki = liczniki, ostatnie = ostatnie, zapis = kontener:GetAttribute("ZapisStan"), odpoczynek = odpoczynekS,
			srKroku_ms = if ileKrokow > 0 then czasKroku / ileKrokow * 1000 else 0 }
	elseif polecenie == "boty" then
		S.botyDo = a
		S.botyMaks = a
		S.botyCo = b
		return true
	elseif polecenie == "usun_dzikie" then
		local zostaja = {}
		for _, p in S.pety do
			if not p.dziki then
				table.insert(zostaja, p)
			end
		end
		S.pety = zostaja
		if S.krol and not L.petPoId(S, S.krol) then
			S.krol = nil
			S.nagroda = 0
		end
		return true
	elseif polecenie == "dziki" then
		local p = rzutDzikiego(a, b, c)
		return p.id
	elseif polecenie == "zycie" then
		local p = L.petPoId(S, a)
		if p then
			p.hp = b
		end
		return p ~= nil
	elseif polecenie == "pasek" then
		local p = L.petPoId(S, a)
		if p then
			p.pasek = b
		end
		return p ~= nil
	elseif polecenie == "pchnij" then
		local p = L.petPoId(S, a)
		if p then
			p.kx, p.kz = b, c
			p.osz = S.czas + 0.5
		end
		return p ~= nil
	elseif polecenie == "przenies" then
		local p = L.petPoId(S, a)
		if p then
			p.x, p.z = b, c
			p.kx, p.kz = 0, 0
		end
		return p ~= nil
	elseif polecenie == "stoj" then
		-- próby: pet stoi w miejscu przez a sekund (ogłuszenie bez obrażeń)
		local p = L.petPoId(S, a)
		if p then
			p.ogl = S.czas + b
		end
		return p ~= nil
	elseif polecenie == "cd" then
		-- zatrzymaj ciosy peta (próby: spokojny dziki pet do wybicia)
		local p = L.petPoId(S, a)
		if p then
			p.cd = b
		end
		return p ~= nil
	elseif polecenie == "odpoczynek" then
		odpoczynekS = a or D.odpoczynek
		return odpoczynekS
	elseif polecenie == "zloto" then
		for plr, g in gracze do
			g.profil.zloto = a or 0
			plr:SetAttribute("PA_Zloto", g.profil.zloto)
		end
		return true
	elseif polecenie == "druzyna" then
		-- próby: drużyna gracza 1 z podanych id (np. { "lesny_troll", … })
		for plr, g in gracze do
			local nowe = {}
			for _, id in a do
				local nr = L.nrPeta(D, id)
				if nr then
					table.insert(nowe, { id = id, nr = nr, probny = false, odpoczynek = 0 })
				end
			end
			g.druzyna = nowe
			g.wybrany = 1
			atrybutyDruzyny(plr, g)
		end
		return true
	elseif polecenie == "pauza" then
		pauza = a == true
		return pauza
	elseif polecenie == "liczniki_zeruj" then
		liczniki = {}
		czasKroku, ileKrokow = 0, 0
		return true
	end
	return nil
end
