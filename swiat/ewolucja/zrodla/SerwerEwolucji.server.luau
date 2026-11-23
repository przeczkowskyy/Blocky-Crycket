--[[
	SerwerEwolucji — serwer Monster Evolution (Script, RunContext Server, w Workspace/EwolucjaGra). Strażnik „tylko
	Studio” na początku (zbuduj.py --publikacja go usuwa) i wyłącznik (atrybut EwolucjaWlaczona kontenera).
	Serwer liczy wszystko: jedzenie, wzrost, ewolucję, złoto, zakupy. Klient tylko przewiduje własny ruch.

	Od klienta tylko Sygnaly/Akcja (rodzaj, ...): "ruch", kx, kz, px, pz (kierunek ≤ 1 i pozycja z przewidywania) ·
	"gryz" · "zryw" · "umiejetnosc", "ogien"|"moc" · "ewoluuj" · "kup", id. Serwer sprawdza typy, stan bytu i wiadro tempa.
	Do klientów: Sygnaly/Stan (UnreliableRemoteEvent, bufor) i Sygnaly/Zdarzenia (lista). Atrybuty gracza EW_*.
	Miary (w pamięci, bez DataStore): atrybut EW_Miary (JSON) i haczyk "miary". Haczyki prób tylko po stronie
	serwera: Sygnaly/SterowanieSerwera (BindableFunction — klient nie ma do niej dostępu).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local RunService = game:GetService("RunService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local kontener = script.Parent
local Moduly = kontener:WaitForChild("Moduly")
local D = require(Moduly:WaitForChild("DaneEwolucji"))
kontener:SetAttribute("SerwerGotowy", false)
if kontener:GetAttribute(D.wylacznik) == false then
	return
end
local L = require(Moduly:WaitForChild("LogikaEwolucji"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evAkcja = Sygnaly:WaitForChild("Akcja")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local evStan = Sygnaly:WaitForChild("Stan")
local sterowanie = Sygnaly:WaitForChild("SterowanieSerwera")
local C = Vector3.new(D.pole.srodek[1], D.pole.srodek[2], D.pole.srodek[3])
local MAKS_GRACZY = 12

-- wzorce potworów → ReplicatedStorage (klienci je klonują)
do
	local stary = ReplicatedStorage:FindFirstChild(D.wzorceRS)
	local wz = kontener:FindFirstChild("Wzorce")
	if wz then
		if stary then
			stary:Destroy()
		end
		wz.Name = D.wzorceRS
		wz.Parent = ReplicatedStorage
	end
end

-- magazyn zapisu: w Studio i przy znaczniku próby (tools/zapis_prob.py) ZAWSZE magazyn w pamięci — nigdy prawdziwy DataStore
local znacznik = kontener:GetAttribute(D.zapis.znacznik_proby)
local wProbie = RunService:IsStudio() or (type(znacznik) == "number" and os.time() < znacznik)
local magazyn = if wProbie then L.pamiec() else DataStoreService:GetDataStore(D.zapis.magazyn)
kontener:SetAttribute("ZapisTryb", if wProbie then "pamiec" else "datastore")
local JOB = if game.JobId ~= "" then game.JobId else "studio"
-- pomiar prób: anonimowe podsumowania sesji (osobny magazyn; w Studio i przy znaczniku — tylko w pamięci)
local magazynProb = if wProbie then L.pamiec() else DataStoreService:GetDataStore(D.zapis.magazyn_prob)
local zapisowProb = 0
local magazynRank = if wProbie then nil else DataStoreService:GetOrderedDataStore(D.ranking.magazyn)
local rankPamiec = {}
local rankNazwy = {}
local AnalyticsService = game:GetService("AnalyticsService")
-- AnalyticsService: tylko serwer opublikowanej gry (w Studio wywołania są pomijane — nie wołamy ich wcale)
local function analityka(metoda: string, ...)
	if RunService:IsStudio() then
		return
	end
	local a = table.pack(...)
	pcall(function()
		(AnalyticsService :: any)[metoda](AnalyticsService, table.unpack(a, 1, a.n))
	end)
end
local function pole(x: any): string
	return string.sub(tostring(x), 1, 40)
end
local function klucz(plr: Player): string
	return "player_" .. tostring(plr.UserId)
end

local los = Random.new()
local S = L.nowyStan(D, function()
	return los:NextNumber()
end)
for f, ile in D.boty.formy do
	for _ = 1, ile do
		L.dodajByt(S, 0, f)
	end
end
for f, ile in D.boty.las_formy do
	for _ = 1, ile do
		L.dodajByt(S, 0, f, nil, nil, 2)
	end
end
local boss = L.dodajBossa(S)
L.dodajOwce(S)
kontener:SetAttribute("BossId", boss.id)
kontener:SetAttribute("BossHP", 1)

------------------------------------------------------------------ gracze
type Gracz = { slot: number, byt: any, wiadro: { t: number, z: number }, nazwa: string, start: number, miary: any,
	ostKorekta: number, atr: { [string]: any }, zapisywalny: boolean?, wczytany: boolean?, nowy: boolean?, dni: number?,
	sesja: string, wDomuOst: boolean?, krokOnb: number, maksEtap: number, zapisanoProbe: boolean? }
local gracze: { [Player]: Gracz } = {}
local poSlocie: { [number]: Player } = {}
local liczniki: { [string]: number } = {}
local doWyslania = {}

local function licz(n: string)
	liczniki[n] = (liczniki[n] or 0) + 1
end

local function wolnySlot(): number?
	for i = 1, MAKS_GRACZY do
		if not poSlocie[i] then
			return i
		end
	end
	return nil
end

-- awatar schowany pod polem (gracz jest potworem)
local function schowajAwatar(plr: Player)
	local c = plr.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart")
	if c and hrp and hrp:IsA("BasePart") then
		hrp.Anchored = true
		c:PivotTo(CFrame.new(C + Vector3.new(0, -40, 0)))
	end
end

local function miaryJSON(g: Gracz): string
	local M = g.miary
	M.sesja_s = math.floor((os.clock() - g.start) * 10 + 0.5) / 10
	return HttpService:JSONEncode(M)
end

local function ustawAtr(plr: Player, g: Gracz, n: string, v: any)
	if g.atr[n] ~= v then
		g.atr[n] = v
		plr:SetAttribute(n, v)
	end
end

local function atrybuty(plr: Player, g: Gracz)
	local b = g.byt
	ustawAtr(plr, g, "EW_Byt", b.id)
	ustawAtr(plr, g, "EW_Forma", b.forma)
	ustawAtr(plr, g, "EW_MaxForma", b.maxForma)
	ustawAtr(plr, g, "EW_Wzrost", math.floor(b.wzrost))
	ustawAtr(plr, g, "EW_Potrzeba", L.potrzeba(D, b.forma))
	ustawAtr(plr, g, "EW_Zloto", math.floor(b.zloto))
	ustawAtr(plr, g, "EW_ZlotoLeg", math.floor(b.zlotoLeg))
	ustawAtr(plr, g, "EW_ZlotoNaS", math.floor(L.stawkaB(D, b) * 10 + 0.5) / 10)
	local w, tr = {}, {}
	for f = 1, #D.formy do
		w[f] = b.warianty[f] or ""
		tr[f] = tostring(L.poziomTrofeum(b, f))
	end
	ustawAtr(plr, g, "EW_Warianty", table.concat(w, ","))
	ustawAtr(plr, g, "EW_Trofea", table.concat(tr, ","))
	ustawAtr(plr, g, "EW_BossTrofea", b.bossTrofea or 0)
	ustawAtr(plr, g, "EW_Wariant", b.wariantTeraz or "")
	local wd = L.wLegowisku(D, b)
	if wd and not g.wDomuOst then
		g.miary.leg = (g.miary.leg or 0) + 1
	end
	g.wDomuOst = wd
	ustawAtr(plr, g, "EW_WDomu", wd)
	for _, U in D.ulepszenia do
		ustawAtr(plr, g, "EW_Poz_" .. U.id, L.poziom(b, U.id))
	end
	ustawAtr(plr, g, "EW_Martwy", b.martwyDo ~= nil)
	-- odrodzenie1: odrodzenia, linia, mnożnik, postęp pozostałych linii (JSON), jajo dnia
	ustawAtr(plr, g, "EW_Odrodzenia", b.odrodzenia or 0)
	ustawAtr(plr, g, "EW_Linia", b.linia or 1)
	ustawAtr(plr, g, "EW_Mnoznik", math.floor(L.mnoznikOdr(D, b) * 1000 + 0.5) / 1000)
	ustawAtr(plr, g, "EW_JajoDnia", L.jajoDostepne(D, b, os.time() + (S.dzienPrzes or 0) * 86400))
	local li = {}
	for l, q in b.linie or {} do
		local w2, t2 = {}, {}
		for f = 1, #D.formy do
			w2[f] = (q.warianty and q.warianty[f]) or ""
			t2[f] = (q.trofea and q.trofea[f]) or 1
		end
		li[tostring(l)] = { m = q.maxForma, w = w2, t = t2 }
	end
	ustawAtr(plr, g, "EW_Linie", HttpService:JSONEncode(li))
	-- retencja1: seria, zadania dnia, przyspieszenie, leaderstats
	ustawAtr(plr, g, "EW_Seria", (b.seria and b.seria.dni) or 0)
	ustawAtr(plr, g, "EW_Boost", math.ceil(b.boostS or 0))
	if b.zadania then
		local zl = {}
		for _, q in b.zadania.lista do
			table.insert(zl, { id = q.id, p = q.postep, c = q.cel, g = q.gotowe })
		end
		ustawAtr(plr, g, "EW_Zadania", HttpService:JSONEncode(zl))
	end
	if g.ls then
		g.ls.stage.Value = b.forma
		g.ls.rebirths.Value = b.odrodzenia or 0
	end
end

local function wczytajGracza(plr: Player, g: Gracz)
	local prof, zapisywalny, powod
	for proba = 1, D.zapis.proby do
		prof, zapisywalny, powod = L.wczytaj(D, magazyn, klucz(plr), JOB, os.time())
		if zapisywalny or not gracze[plr] then
			break
		end
		task.wait(1.5 * proba)
	end
	if not gracze[plr] or gracze[plr] ~= g then
		return
	end
	g.zapisywalny = zapisywalny
	g.wczytany = true
	local zarobek, sek = L.zProfilu(D, g.byt, prof, os.time())
	g.nowy = prof.ostatnio == 0
	g.dni = math.floor((os.time() - g.byt.pierwszy) / 86400)
	plr:SetAttribute("EW_Zapis", if zapisywalny then "ok" else ("bez zapisu: " .. tostring(powod)))
	local pow = L.logowanie(D, g.byt, os.time() + (S.dzienPrzes or 0) * 86400, S.los())
	atrybuty(plr, g)
	if zarobek > 0 then
		evZdarzenia:FireClient(plr, { { t = "powrot", ile = zarobek, sek = sek } })
	end
	evZdarzenia:FireClient(plr, { { t = "powitanie", dni = pow.dni, nagroda = pow.nagroda, wariant = pow.wariant, f = pow.f, lepszy = pow.lepszy,
		zarobek = zarobek, nowy = g.nowy } })
	if pow.nagroda then
		analityka("LogCustomEvent", plr, "LoginStreakDay", pow.dni)
		analityka("LogEconomyEvent", plr, Enum.AnalyticsEconomyFlowType.Source, "Gold", pow.nagroda.zloto or 0, math.floor(g.byt.zloto),
			Enum.AnalyticsEconomyTransactionType.Gameplay.Name, "streak_day_" .. tostring(pow.dni))
	end
	licz("wczytano")
end

local function zapiszGracza(plr: Player, g: Gracz, zwolnij: boolean): boolean
	if not g.zapisywalny or not g.wczytany then
		return false
	end
	local ok = L.zapisz(D, magazyn, klucz(plr), JOB, L.doProfilu(D, g.byt, os.time()), os.time(), zwolnij)
	if ok then
		licz("zapisano")
	end
	return ok
end

-- jeden krok lejka startu (pierwsza minuta), każdy raz na gracza
local function onboarding(plr: Player, g: Gracz, krok: number, nazwa: string)
	if krok == g.krokOnb + 1 then
		g.krokOnb = krok
		analityka("LogOnboardingFunnelStepEvent", plr, krok, nazwa)
	end
end

-- anonimowe podsumowanie sesji do osobnego magazynu (raz na sesję; limit zapisów na serwer i długości rekordu)
local function zapiszProbe(plr: Player, g: Gracz)
	if g.zapisanoProbe or zapisowProb >= D.zapis.prob_na_serwer then
		return nil
	end
	g.zapisanoProbe = true
	zapisowProb += 1
	g.miary.sesja_s = math.floor(os.clock() - g.start)
	local dzien = os.date("!%Y-%m-%d")
	local r = L.podsumowanie(D, g.miary, dzien, g.nowy == true, g.dni or 0)
	local tekst = HttpService:JSONEncode(r)
	if #tekst > D.zapis.prob_maks_znakow then
		r.t, r.war = nil, nil
	end
	local klucz = dzien .. "_" .. string.sub(HttpService:GenerateGUID(false), 1, 12)
	local ok = pcall(function()
		magazynProb.UpdateAsync(magazynProb, klucz, function()
			return r
		end)
	end)
	licz(if ok then "proba_zapisana" else "proba_blad")
	return klucz
end

local function dolacz(plr: Player)
	if gracze[plr] then
		return
	end
	local slot = wolnySlot()
	if not slot then
		plr:SetAttribute("EW_Slot", 0)
		return
	end
	local g: Gracz = { slot = slot, byt = L.dodajByt(S, slot, 1), wiadro = { t = os.clock(), z = D.siec.wiadro_zapas },
		-- w Studio (próby, zrzuty, filmy) bez nazwy konta: „Player N”
		nazwa = if RunService:IsStudio() then ("Player " .. tostring(slot)) else plr.DisplayName, start = os.clock(), ostKorekta = 0, atr = {},
		miary = { formy = { ["1"] = 0 }, smierci = 0, po_smierci = {}, ulepszenia = {}, sesja_s = 0, leg = 0, zb = 0, tr = 0, bs = 0, war = {} },
		sesja = string.sub(HttpService:GenerateGUID(false), 1, 8), krokOnb = 0, maksEtap = 1 }
	gracze[plr] = g
	poSlocie[slot] = plr
	plr:SetAttribute("EW_Slot", slot)
	-- retencja1: leaderstats (Stage, Rebirths) — lista graczy Roblox
	local ls = plr:FindFirstChild("leaderstats") or Instance.new("Folder")
	ls.Name = "leaderstats"
	local function wartosc(n: string): IntValue
		local v = ls:FindFirstChild(n)
		if not (v and v:IsA("IntValue")) then
			v = Instance.new("IntValue")
			v.Name = n
			v.Parent = ls
		end
		return v :: IntValue
	end
	g.ls = { stage = wartosc("Stage"), rebirths = wartosc("Rebirths") }
	ls.Parent = plr
	atrybuty(plr, g)
	plr:SetAttribute("EW_Miary", miaryJSON(g))
	plr.CharacterAdded:Connect(function(c)
		c:WaitForChild("HumanoidRootPart", 10)
		task.wait()
		if gracze[plr] then
			schowajAwatar(plr)
		end
	end)
	schowajAwatar(plr)
	licz("dolaczyl")
	onboarding(plr, g, 1, "Spawned")
	task.spawn(wczytajGracza, plr, g)
end

local function odejdz(plr: Player)
	local g = gracze[plr]
	if not g then
		return
	end
	zapiszGracza(plr, g, true)
	task.spawn(zapiszProbe, plr, g)
	for _, z in g.miary.po_smierci do
		if z.dalej == nil then
			z.dalej = false
		end
	end
	L.usunByt(S, g.byt)
	poSlocie[g.slot] = nil
	gracze[plr] = nil
end

------------------------------------------------------------------ akcje (walidacja i wiadro tempa)
local function wiadro(g: Gracz): boolean
	local t = os.clock()
	g.wiadro.z = math.min(D.siec.wiadro_zapas, g.wiadro.z + (t - g.wiadro.t) * D.siec.wiadro_na_s)
	g.wiadro.t = t
	if g.wiadro.z < 1 then
		return false
	end
	g.wiadro.z -= 1
	return true
end

local function aktywny(g: Gracz)
	-- miara: czy po śmierci gracz grał dalej (akcja w ciągu gral_dalej_s od odrodzenia)
	for _, z in g.miary.po_smierci do
		if z.dalej == nil and z.wrocil then
			z.dalej = true
		end
	end
end

local function wyslijGraczowi(plr: Player, lista)
	if #lista > 0 then
		evZdarzenia:FireClient(plr, lista)
	end
end

local RODZAJE = { ruch = true, gryz = true, zryw = true, umiejetnosc = true, ewoluuj = true, kup = true, kup_trofeum = true, odrodzenie = true,
	jajo_dnia = true }

evAkcja.OnServerEvent:Connect(function(plr: Player, rodzaj: any, a: any, b: any, c: any, d: any)
	local g = gracze[plr]
	if not g or type(rodzaj) ~= "string" or not RODZAJE[rodzaj] or not wiadro(g) then
		return
	end
	local byt = g.byt
	if rodzaj == "ruch" then
		if not L.steruj(byt, a, b) then
			return
		end
		if (a ~= 0 or b ~= 0) then
			aktywny(g)
		end
		if c ~= nil then
			if not L.pozycjaKlienta(S, byt, c, d) and not L.sterowanyPrzezSerwer(S, byt) and os.clock() - g.ostKorekta > 0.25 then
				g.ostKorekta = os.clock()
				licz("korekta")
				wyslijGraczowi(plr, { { t = "korekta", x = byt.x, z = byt.z } })
			end
		end
		return
	end
	aktywny(g)
	if rodzaj == "gryz" then
		if L.gryz(S, byt, doWyslania) then
			licz("gryz")
		end
	elseif rodzaj == "zryw" then
		if L.zryw(S, byt) then
			table.insert(doWyslania, { t = "zryw", id = byt.id })
			licz("zryw")
		end
	elseif rodzaj == "umiejetnosc" then
		-- a: linia "ogien" (FIRE) albo "moc" (POWER) — logika odrzuca wszystko inne
		if type(a) == "string" and L.zdolnosc(S, byt, a, doWyslania) then
			licz("umiejetnosc")
		end
	elseif rodzaj == "ewoluuj" then
		if L.ewoluuj(S, byt, doWyslania) then
			licz("ewoluuj")
		end
	elseif rodzaj == "odrodzenie" then
		-- REBIRTH: tylko na ostatnim stadium, poza kokonem i walką sterowaną przez serwer (sprawdza logika)
		if L.odrodzenie(S, byt, doWyslania) then
			licz("rebirth")
			g.miary.odr = (g.miary.odr or 0) + 1
		end
	elseif rodzaj == "jajo_dnia" then
		local ok, id, lepszy, f = L.jajoDnia(S, byt, os.time() + (S.dzienPrzes or 0) * 86400, S.los())
		if ok then
			licz("jajo_dnia")
		end
		atrybuty(plr, g)
		wyslijGraczowi(plr, { { t = "jajo_dnia", ok = ok, wariant = if ok then id else nil, powod = if ok then nil else id, lepszy = lepszy, f = f } })
	elseif rodzaj == "kup" then
		local ok, powod = L.kup(S, byt, a)
		if ok then
			local p = L.poziom(byt, a)
			table.insert(g.miary.ulepszenia, { id = a, poziom = p, t = math.floor(os.clock() - g.start) })
			analityka("LogEconomyEvent", plr, Enum.AnalyticsEconomyFlowType.Sink, "Gold", L.ulepszenie(D, a).ceny[p - 1] or 0, math.floor(byt.zloto),
				Enum.AnalyticsEconomyTransactionType.Shop.Name, "upgrade_" .. a)
			onboarding(plr, g, 5, "FirstUpgrade")
			plr:SetAttribute("EW_Miary", miaryJSON(g))
			licz("kup")
		end
		atrybuty(plr, g)
		wyslijGraczowi(plr, { { t = "kup", id = if type(a) == "string" then a else "", ok = ok, powod = powod } })
	elseif rodzaj == "kup_trofeum" then
		local ok, powod = L.kupTrofeum(S, byt, a)
		if ok then
			licz("kup_trofeum")
			g.miary.tr = (g.miary.tr or 0) + 1
			analityka("LogEconomyEvent", plr, Enum.AnalyticsEconomyFlowType.Sink, "Gold", 1, math.floor(byt.zloto),
				Enum.AnalyticsEconomyTransactionType.Shop.Name, "trophy_" .. tostring(a))
		end
		atrybuty(plr, g)
		wyslijGraczowi(plr, { { t = "kup", id = "trofeum", f = if type(a) == "number" then a else 0, ok = ok, powod = powod } })
	end
end)

------------------------------------------------------------------ migawki (bufor)
local ROZ = 18
local NR_WARIANTU = {}
for i, W in D.warianty do
	NR_WARIANTU[W.id] = i
end
-- bajt akcji (walka1): numer zdolności (1–7) + 16 zamach + 32 kanał oddechu; 64 przewrót (po ciosie z odrzutem)
local NR_ZDOLNOSCI = {}
do
	local i = 0
	for _, linia in { "ogien", "moc" } do
		for _, A in D.zdolnosci[linia] do
			i += 1
			NR_ZDOLNOSCI[A.id] = i
		end
	end
end
local function migawka(): buffer
	local n = #S.byty
	local nk = #D.kulkiPoz
	local nb = math.ceil(nk / 8)
	local no = if S.owce then #S.owce else 0
	local b = buffer.create(12 + nb + n * ROZ + 1 + no * 11)
	buffer.writef64(b, 0, workspace:GetServerTimeNow())
	buffer.writeu16(b, 8, n)
	buffer.writeu16(b, 10, S.olbrzym % 65536)
	for i = 0, nb - 1 do
		local bajt = 0
		for k = 0, 7 do
			local idx = i * 8 + k + 1
			if idx <= nk and S.kulki[idx] == 0 then
				bajt += 2 ^ k
			end
		end
		buffer.writeu8(b, 12 + i, bajt)
	end
	local o0 = 12 + nb
	for i, e in S.byty do
		local o = o0 + (i - 1) * ROZ
		local f = 0
		if e.tarczaDo > S.czas then
			f += 1
		end
		if e.zrywDo > S.czas or e.szarzaDo > S.czas then
			f += 2
		end
		if e.martwyDo then
			f += 4
		end
		if e.kokonDo then
			f += 8
		end
		if e.ogluszonyDo > S.czas then
			f += 16
		end
		if e.skok then
			f += 32
		end
		if e.gryzDo > S.czas then
			f += 64
		end
		if e.boss then
			f += 128
		end
		buffer.writeu16(b, o, e.id % 65536)
		buffer.writeu8(b, o + 2, e.slot)
		buffer.writeu8(b, o + 3, f)
		buffer.writeu8(b, o + 4, e.forma)
		buffer.writef32(b, o + 5, e.x)
		buffer.writef32(b, o + 9, e.z)
		buffer.writei16(b, o + 13, math.clamp(math.floor(e.kier * 1000 + 0.5), -32000, 32000))
		buffer.writeu8(b, o + 15, L.kodWariantu(if e.slot > 0 and e.wariantTeraz then (NR_WARIANTU[e.wariantTeraz] or 0) else 0, e.linia or 1))
		buffer.writeu8(b, o + 16, math.clamp(math.floor((e.hp or 0) / math.max(1, e.hpMaks or 1) * 255 + 0.5), 0, 255))
		local ak = 0
		if e.zamach then
			ak = (NR_ZDOLNOSCI[e.zamach.A.id] or 0) + 16
		elseif e.kanal then
			ak = (NR_ZDOLNOSCI[e.kanal.A.id] or 0) + 32
		end
		if (e.przewrotDo or 0) > S.czas then
			ak += 64
		end
		buffer.writeu8(b, o + 17, ak)
	end
	-- owce (swiat1): liczba, potem po 11 bajtów: x f32, z f32, kier i16 (× 1000), stan u8 (0 stoi, 1 idzie, 2 ucieka, 3 zjedzona)
	local oo = o0 + n * ROZ
	buffer.writeu8(b, oo, no)
	for i = 1, no do
		local w = S.owce[i]
		local q = oo + 1 + (i - 1) * 11
		buffer.writef32(b, q, w.x)
		buffer.writef32(b, q + 4, w.z)
		buffer.writei16(b, q + 8, math.clamp(math.floor((w.kier or 0) * 1000 + 0.5), -32000, 32000))
		buffer.writeu8(b, q + 10, if w.martwyDo then 3 else w.stan)
	end
	return b
end

------------------------------------------------------------------ zdarzenia logiki → miary, ogłoszenia
local function poZdarzeniu(z)
	licz(z.t)
	if z.s and z.s > 0 and poSlocie[z.s] then
		local plr = poSlocie[z.s]
		local g = gracze[plr]
		if z.t == "zadanie" then
			g.miary.zad = (g.miary.zad or 0) + 1
			analityka("LogCustomEvent", plr, "QuestCompleted", 1, { [Enum.AnalyticsCustomFieldKeys.CustomField01.Name] = "Quest - " .. pole(z.zad) })
			analityka("LogEconomyEvent", plr, Enum.AnalyticsEconomyFlowType.Source, "Gold", z.zloto, math.floor(g.byt.zloto),
				Enum.AnalyticsEconomyTransactionType.Gameplay.Name, "quest_" .. pole(z.zad))
		elseif z.t == "kulka" then
			onboarding(plr, g, 2, "FirstOrb")
		elseif z.t == "zebrano" then
			g.miary.zb = (g.miary.zb or 0) + 1
			analityka("LogEconomyEvent", plr, Enum.AnalyticsEconomyFlowType.Source, "Gold", z.ile, math.floor(g.byt.zloto),
				Enum.AnalyticsEconomyTransactionType.Gameplay.Name, "hoard")
			onboarding(plr, g, 4, "HoardCollected")
		elseif z.t == "smierc" then
			analityka("LogCustomEvent", plr, "Death", 1, { [Enum.AnalyticsCustomFieldKeys.CustomField01.Name] = "Stage - " .. pole(z.forma) })
			g.miary.smierci += 1
			table.insert(g.miary.po_smierci, { t = math.floor(os.clock() - g.start), forma = z.forma, dalej = nil, wrocil = false })
			plr:SetAttribute("EW_Miary", miaryJSON(g))
		elseif z.t == "odrodzenie" then
			for _, m in g.miary.po_smierci do
				if not m.wrocil then
					m.wrocil = true
					m.wrocilT = os.clock()
				end
			end
		elseif z.t == "ewolucja" and z.nowa then
			g.miary.formy[tostring(z.forma)] = math.floor((os.clock() - g.start) * 10 + 0.5) / 10
			plr:SetAttribute("EW_Miary", miaryJSON(g))
		end
		if z.t == "ewolucja" then
			if z.wariant then
				g.miary.war[z.wariant] = (g.miary.war[z.wariant] or 0) + 1
				analityka("LogCustomEvent", plr, "VariantRolled", 1, { [Enum.AnalyticsCustomFieldKeys.CustomField01.Name] = "Variant - " .. pole(z.wariant),
					[Enum.AnalyticsCustomFieldKeys.CustomField02.Name] = "Stage - " .. pole(z.forma) })
			end
			if z.forma > g.maksEtap then
				g.maksEtap = z.forma
				analityka("LogFunnelStepEvent", plr, "DragonStages", g.sesja, z.forma, D.formy[z.forma].nazwa)
			end
			if z.forma == 2 then
				onboarding(plr, g, 3, "FirstEvolve")
			end
		elseif z.t == "olbrzym" then
			table.insert(doWyslania, { t = "ogloszenie", tekst = string.format(D.ui.ogl_olbrzym, g.nazwa) })
		elseif z.t == "las_otwarty" then
			g.miary.las = math.floor((os.clock() - g.start) * 10 + 0.5) / 10
		elseif z.t == "boss_pokonany" then
			g.miary.boss_pokonany = g.miary.boss_pokonany or math.floor((os.clock() - g.start) * 10 + 0.5) / 10
			g.miary["boss_stopien_" .. tostring(z.stopien)] = math.floor((os.clock() - g.start) * 10 + 0.5) / 10
			g.miary.bs = math.max(g.miary.bs or 0, z.stopien)
			analityka("LogCustomEvent", plr, "BossTierBeaten", z.stopien)
			analityka("LogEconomyEvent", plr, Enum.AnalyticsEconomyFlowType.Source, "Gold", z.zloto, math.floor(g.byt.zloto),
				Enum.AnalyticsEconomyTransactionType.Gameplay.Name, "boss_chest")
			table.insert(doWyslania, { t = "ogloszenie", tekst = string.format(D.ui.ogl_boss, g.nazwa, D.boss.nazwa .. " " .. string.rep("*", z.stopien)) })
			plr:SetAttribute("EW_Miary", miaryJSON(g))
		elseif z.t == "olbrzym_obalony" then
			table.insert(doWyslania, { t = "ogloszenie", tekst = string.format(D.ui.ogl_obalony, g.nazwa) })
		end
	end
end

------------------------------------------------------------------ pętla
local zb, doStan, doAtr, doMiar, doZapisu = 0, 0, 0, 0, D.zapis.co_s
local czasKroku, ileKrokow = 0, 0

RunService.Heartbeat:Connect(function(dt: number)
	local t0 = os.clock()
	zb = math.min(zb + dt, D.ruch.krok_s * 4)
	while zb >= D.ruch.krok_s do
		zb -= D.ruch.krok_s
		S.zegar = os.time() + (S.dzienPrzes or 0) * 86400 -- zegar UTC: wydarzenia, dzień zadań i serii
		for _, z in L.krok(S, D.ruch.krok_s) do
			table.insert(doWyslania, z)
		end
	end
	for _, z in doWyslania do
		poZdarzeniu(z)
	end
	czasKroku += os.clock() - t0
	ileKrokow += 1
	-- zdarzenia: kulki zjedzone przez boty idą tylko w migawce (bitmapa)
	local lista = {}
	for _, z in doWyslania do
		if z.t ~= "kulka" or z.s > 0 then
			table.insert(lista, z)
		end
	end
	doWyslania = {}
	if #lista > 0 then
		for plr in gracze do
			evZdarzenia:FireClient(plr, lista)
		end
	end
	doStan -= dt
	if doStan <= 0 then
		doStan = D.siec.stan_co_s
		if next(gracze) then
			local b = migawka()
			for plr in gracze do
				evStan:FireClient(plr, b)
			end
		end
	end
	doAtr -= dt
	if doAtr <= 0 then
		doAtr = 0.2
		local bb = L.bytPoId(S, S.boss)
		kontener:SetAttribute("BossHP", if bb and not bb.martwyDo then math.floor(bb.hp / bb.hpMaks * 1000) / 1000 else 0)
		kontener:SetAttribute("BossStopien", S.bossStopien or 1)
		-- wydarzenia zegarowe: chwile w czasie serwera (workspace:GetServerTimeNow) dla odliczania u klientów
		local E = L.wyd(S)
		local tn = workspace:GetServerTimeNow()
		kontener:SetAttribute("WydDeszczNast", if E.deszczNast < math.huge then tn + (E.deszczNast - S.czas) else 0)
		kontener:SetAttribute("WydDeszczDo", if E.deszczDo then tn + (E.deszczDo - S.czas) else 0)
		kontener:SetAttribute("WydRampNast", if E.rampNast < math.huge then tn + (E.rampNast - S.czas) else 0)
		kontener:SetAttribute("WydRampDo", if E.rampDo then tn + (E.rampDo - S.czas) else 0)
		for plr, g in gracze do
			atrybuty(plr, g)
			for _, m in g.miary.po_smierci do
				if m.dalej == nil and m.wrocil and os.clock() - m.wrocilT > D.smierc.gral_dalej_s then
					m.dalej = false
				end
			end
		end
	end
	doMiar -= dt
	if doMiar <= 0 then
		doMiar = 5
		for plr, g in gracze do
			plr:SetAttribute("EW_Miary", miaryJSON(g))
		end
	end
	doZapisu -= dt
	if doZapisu <= 0 then
		doZapisu = D.zapis.co_s
		for plr, g in gracze do
			task.spawn(zapiszGracza, plr, g, false)
		end
	end
end)

local function odswiezRanking()
	local lista = {}
	if wProbie then
		for _, g in gracze do
			rankPamiec["S" .. tostring(g.slot)] = { n = g.nazwa, r = g.byt.odrodzenia or 0 }
		end
		for _, e in rankPamiec do
			table.insert(lista, e)
		end
	else
		for plr, g in gracze do
			local r = g.byt.odrodzenia or 0
			if g.wczytany and g.rankZapis ~= r and r > 0 then
				local ok = pcall(function()
					magazynRank:SetAsync(tostring(plr.UserId), r)
				end)
				if ok then
					g.rankZapis = r
				end
			end
		end
		local ok, strona = pcall(function()
			return magazynRank:GetSortedAsync(false, D.ranking.ile):GetCurrentPage()
		end)
		if ok and type(strona) == "table" then
			for _, e in strona do
				local uid = tonumber(e.key)
				local n = uid and rankNazwy[uid]
				if uid and not n then
					local ok2, nn = pcall(function()
						return Players:GetNameFromUserIdAsync(uid)
					end)
					n = if ok2 then nn else "?"
					rankNazwy[uid] = n
				end
				table.insert(lista, { n = n or "?", r = e.value })
			end
		end
	end
	table.sort(lista, function(a, b)
		return a.r > b.r
	end)
	while #lista > D.ranking.ile do
		table.remove(lista)
	end
	kontener:SetAttribute("Ranking", HttpService:JSONEncode(lista))
	licz("ranking")
end
task.spawn(function()
	task.wait(3)
	while kontener.Parent do
		odswiezRanking()
		task.wait(D.ranking.odswiez_s)
	end
end)

game:BindToClose(function()
	for plr, g in gracze do
		zapiszGracza(plr, g, true)
		zapiszProbe(plr, g)
	end
end)

Players.PlayerAdded:Connect(dolacz)
Players.PlayerRemoving:Connect(odejdz)
for _, plr in Players:GetPlayers() do
	task.spawn(dolacz, plr)
end
kontener:SetAttribute("SerwerGotowy", true)
print(D.prefiks .. "serwer gotowy")

------------------------------------------------------------------ haczyki prób (tylko serwer)
local function pierwszy(): (Player?, Gracz?)
	for plr, g in gracze do
		return plr, g
	end
	return nil, nil
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any, c: any)
	local plr, g = pierwszy()
	local byt = g and g.byt
	if polecenie == "stan" then
		local byty = {}
		for _, e in S.byty do
			table.insert(byty, { id = e.id, slot = e.slot, forma = e.forma, x = e.x, z = e.z, martwy = e.martwyDo ~= nil,
				tarcza = e.tarczaDo > S.czas, kokon = e.kokonDo ~= nil, cel = e.cel, zjadl = e.zjadl, strefa = e.strefa })
		end
		local zywe = 0
		for _, k in S.kulki do
			if k == 0 then
				zywe += 1
			end
		end
		return { gotowy = true, czas = S.czas, byt = byt and byt.id, forma = byt and byt.forma, maxForma = byt and byt.maxForma,
			wzrost = byt and byt.wzrost, potrzeba = byt and L.potrzeba(D, byt.forma), zloto = byt and byt.zloto,
			stawka = byt and L.stawkaB(D, byt), poziomy = byt and byt.poziomy, x = byt and byt.x, z = byt and byt.z,
			zlotoLeg = byt and byt.zlotoLeg, slot = g and g.slot, kokon = byt and byt.kokonDo ~= nil, olbrzymId = S.olbrzym,
			martwy = byt and byt.martwyDo ~= nil, tarcza = byt and byt.tarczaDo > S.czas, byty = byty, kulek = zywe, strefy = #S.strefy,
			laska = byt and byt.laskaDo > S.czas,
			liczniki = liczniki, krok_ms = if ileKrokow > 0 then czasKroku / ileKrokow * 1000 else 0, owce = (function()
				local w = {}
				for _, o in S.owce or {} do
					table.insert(w, { i = o.i, x = o.x, z = o.z, martwa = o.martwyDo ~= nil })
				end
				return w
			end)() }
	elseif polecenie == "proby" then
		-- próba: zawartość magazynu podsumowań (tylko magazyn w pamięci) + tryb
		local w = {}
		if magazynProb.dane then
			for k, v in magazynProb.dane do
				w[k] = v
			end
		end
		return { tryb = if magazynProb.dane then "pamiec" else "datastore", zapisow = zapisowProb, rekordy = w }
	elseif polecenie == "zapisz_probe" then
		if plr and g then
			g.zapisanoProbe = false
			return zapiszProbe(plr :: Player, g)
		end
		return nil
	elseif polecenie == "logowanie" then
		-- próba: wejście jeszcze raz (seria, nagroda dnia, zadania) i ekran powitania
		if byt and plr then
			local pow = L.logowanie(D, byt, os.time() + (S.dzienPrzes or 0) * 86400, S.los())
			atrybuty(plr, g)
			evZdarzenia:FireClient(plr, { { t = "powitanie", dni = pow.dni, nagroda = pow.nagroda, wariant = pow.wariant, f = pow.f, lepszy = pow.lepszy,
				zarobek = 0, nowy = false } })
			return { dni = pow.dni, nagroda = pow.nagroda, zloto = byt.zloto }
		end
		return nil
	elseif polecenie == "seria_ustaw" then
		-- próba: ostatnie wejście a dni temu przy serii b
		if byt then
			byt.seria = { dzien = L.dzienUTC(os.time() + (S.dzienPrzes or 0) * 86400) - a, dni = b or 1 }
		end
		return true
	elseif polecenie == "zadania_ustaw" then
		-- próba: zadania na dziś z listy id (cel z puli albo c)
		if byt then
			local lista = {}
			for _, id in a do
				local Q = L.zadanieDef(D, id)
				if Q then
					table.insert(lista, { id = id, cel = c or Q.cel, postep = 0, gotowe = false })
				end
			end
			byt.zadania = { dzien = L.dzienUTC(os.time() + (S.dzienPrzes or 0) * 86400), lista = lista }
			if plr then
				atrybuty(plr, g)
			end
		end
		return true
	elseif polecenie == "zadania" then
		return byt and byt.zadania
	elseif polecenie == "ranking_odswiez" then
		odswiezRanking()
		return HttpService:JSONDecode(kontener:GetAttribute("Ranking") or "[]")
	elseif polecenie == "boty_stoj_wszystkie" then
		-- próby pomiaru stóp: wszystkie boty stoją i nie gryzą przez a s (bez potrąceń na torze pomiaru)
		for _, e in S.byty do
			if e.slot == 0 and not e.boss then
				e.wx, e.wz, e.vx, e.vz = 0, 0, 0, 0
				e.myslDo = S.czas + (a or 5)
				e.gryzGotowy = S.czas + (a or 5)
			end
		end
		return true
	elseif polecenie == "wydarzenia_zegar" then
		-- próby: rozkład z zegara UTC włączony (true) albo wyłączony (false; zostają tylko wymuszone)
		S.wydBezZegara = a == false
		return true
	elseif polecenie == "wymus_deszcz" then
		L.wymusWydarzenie(S, "deszcz")
		return true
	elseif polecenie == "wymus_rampage" then
		L.wymusWydarzenie(S, "rampage")
		return true
	elseif polecenie == "wyd" then
		local E = L.wyd(S)
		local zywe = 0
		for i in D.kulkiPoz do
			if S.kulki[i] == 0 and L.deszczNa(S, i) then
				zywe += 1
			end
		end
		local bb = L.bytPoId(S, S.boss)
		return { deszcz = E.deszczDo ~= nil, rampage = E.rampDo ~= nil, zloteKule = zywe, bossX = bb and bb.x, bossZ = bb and bb.z,
			bossLas = bb ~= nil and L.wLesie(D, bb.x, bb.z), stopien = S.bossStopien, bossHp = bb and bb.hp, bossMartwy = bb ~= nil and bb.martwyDo ~= nil }
	elseif polecenie == "dzien_przesun" then
		S.dzienPrzes = (S.dzienPrzes or 0) + (a or 1)
		return S.dzienPrzes
	elseif polecenie == "odrodzenie" then
		-- próba: gracz na ANCIENT i REBIRTH od razu (jak przycisk)
		if byt then
			byt.kokonDo, byt.skok, byt.martwyDo = nil, nil, nil
			byt.forma = #D.formy
			byt.maxForma = #D.formy
			return L.odrodzenie(S, byt, doWyslania)
		end
		return false
	elseif polecenie == "odr_stan" then
		local li = {}
		for l, q in (byt and byt.linie) or {} do
			li[tostring(l)] = q.maxForma
		end
		return byt and { odrodzenia = byt.odrodzenia or 0, linia = byt.linia or 1, mnoznik = L.mnoznikOdr(D, byt), forma = byt.forma,
			maxForma = byt.maxForma, linie = li, stawka = L.stawkaB(D, byt), dzienJaja = byt.dzienJaja }
	elseif polecenie == "wymus_wariant" then
		S.wymusWariant = a
		return true
	elseif polecenie == "boss_stopien" then
		S.bossStopien = a
		local bb = L.bytPoId(S, S.boss)
		if bb then
			bb.hpMaks = D.boss.stopnie_hp[a]
			bb.hp = bb.hpMaks
			if bb.martwyDo then
				bb.martwyDo = nil
				bb.x, bb.z = bb.domX, bb.domZ
			end
		end
		return true
	elseif polecenie == "forma_gracza" then
		if byt then
			byt.kokonDo, byt.skok, byt.martwyDo = nil, nil, nil
			byt.forma = a
			byt.maxForma = math.max(byt.maxForma, a)
			byt.wzrost = 0
			if a == #D.formy then
				byt.olbrzymHp = D.olbrzym.hp
				S.olbrzym = byt.id
			end
		end
		return true
	elseif polecenie == "zloto_leg" then
		if byt then
			byt.zlotoLeg = a
		end
		return true
	elseif polecenie == "do_legowiska" then
		if byt then
			byt.x, byt.z = L.legowiskoPoz(D, byt.slot)
			byt.ostRaport = S.czas
		end
		return true
	elseif polecenie == "wyjdz_wroc" then
		-- próba wyjścia i powrotu: zapis (zwolnienie sesji), czas nieobecności a sekund, nowe wejście z wczytaniem
		if not (plr and g and g.wczytany) then
			return nil
		end
		local przed = { zloto = math.floor(g.byt.zloto), zlotoLeg = math.floor(g.byt.zlotoLeg), maxForma = g.byt.maxForma,
			poziomy = L.kopia(g.byt.poziomy), stawka = L.stawkaB(D, g.byt) }
		local okZ = zapiszGracza(plr :: Player, g, true)
		if magazyn.dane and magazyn.dane[klucz(plr :: Player)] then
			magazyn.dane[klucz(plr :: Player)].ostatnio -= a
		end
		L.usunByt(S, g.byt)
		g.byt = L.dodajByt(S, g.slot, 1)
		g.wczytany = false
		wczytajGracza(plr :: Player, g)
		return { zapisano = okZ, przed = przed, po = { zloto = math.floor(g.byt.zloto), zlotoLeg = math.floor(g.byt.zlotoLeg), forma = g.byt.forma,
			maxForma = g.byt.maxForma, poziomy = g.byt.poziomy }, magazyn = kontener:GetAttribute("ZapisTryb") }
	elseif polecenie == "boss" then
		local bb = L.bytPoId(S, S.boss)
		return bb and { id = bb.id, hp = bb.hp, hpMaks = bb.hpMaks, x = bb.x, z = bb.z, martwy = bb.martwyDo ~= nil, cel = bb.cel }
	elseif polecenie == "boss_hp" then
		local bb = L.bytPoId(S, S.boss)
		if bb then
			bb.hp = a
			bb.ostRana = S.czas
		end
		return true
	elseif polecenie == "boss_stoj" then
		local bb = L.bytPoId(S, S.boss)
		if bb then
			bb.wx, bb.wz = 0, 0
			bb.myslDo = S.czas + (a or 3)
			bb.cel = 0
			bb.bossZamach = nil
			bb.gryzGotowy = S.czas + (a or 3)
		end
		return true
	elseif polecenie == "miary" then
		return if g then HttpService:JSONDecode(miaryJSON(g)) else nil
	elseif polecenie == "wzrost_pelny" then
		if byt then
			byt.wzrost = L.potrzeba(D, byt.forma)
		end
		return true
	elseif polecenie == "wzrost" then
		if byt then
			byt.wzrost = a
		end
		return true
	elseif polecenie == "zloto" then
		if byt then
			byt.zloto = a
		end
		return true
	elseif polecenie == "przenies" then
		local e = L.bytPoId(S, a)
		if e then
			e.x, e.z = b, c
			e.vx, e.vz = 0, 0
			e.ostRaport = S.czas
		end
		return e ~= nil
	elseif polecenie == "bot_forma" then
		local e = L.bytPoId(S, a)
		if e and e.slot == 0 then
			e.forma = b
		end
		return e ~= nil
	elseif polecenie == "bot_stoj" then
		local e = L.bytPoId(S, a)
		if e then
			e.wx, e.wz = 0, 0
			e.myslDo = S.czas + (b or 3)
		end
		return e ~= nil
	elseif polecenie == "hp" then
		-- próba walki: życie bytu a (albo gracza) na b
		local e = if a then L.bytPoId(S, a) else byt
		if e then
			e.hp = b
			e.ostRana = S.czas
		end
		return e ~= nil
	elseif polecenie == "walka_info" then
		local e = if a then L.bytPoId(S, a) else byt
		return e and { hp = e.hp, hpMaks = e.hpMaks, forma = e.forma, lancuch = e.lancuch, zamach = e.zamach and e.zamach.A.id,
			kanal = e.kanal and e.kanal.A.id, gotowy = e.gotowy, x = e.x, z = e.z, martwy = e.martwyDo ~= nil, skok = e.skok ~= nil,
			naWyspie = L.naWyspie(D, e.x, e.z), ogluszony = e.ogluszonyDo > S.czas }
	elseif polecenie == "boty_cisza" then
		-- próba: wszystkie boty bez BITE i zdolności przez a sekund (pomiary HUD i poślizgu bez walki w tle)
		for _, e in S.byty do
			if e.slot == 0 and not e.boss then
				e.gryzGotowy = S.czas + (a or 10)
				e.gotowy = { ogien = S.czas + (a or 10), moc = S.czas + (a or 10) }
			end
		end
		return true
	elseif polecenie == "bot_cisza" then
		-- próba: bot a nie gryzie i nie używa zdolności przez b sekund (manekin)
		local e = L.bytPoId(S, a)
		if e and e.slot == 0 then
			e.gryzGotowy = S.czas + (b or 3)
			e.gotowy = { ogien = S.czas + (b or 3), moc = S.czas + (b or 3) }
		end
		return e ~= nil
	elseif polecenie == "zdolnosci_zeruj" then
		if byt then
			byt.gotowy = { ogien = 0, moc = 0 }
		end
		return true
	elseif polecenie == "bot_cel" then
		local e = L.bytPoId(S, a)
		if e and e.slot == 0 then
			e.cel, e.celOd = b, S.czas
			e.napastnik, e.napastnikDo = b, S.czas + 30
		end
		return e ~= nil
	elseif polecenie == "laska_zeruj" then
		if byt then
			byt.laskaDo = 0
		end
		return true
	elseif polecenie == "tarcza_zeruj" then
		if byt then
			byt.tarczaDo = 0
		end
		return true
	elseif polecenie == "liczniki_zeruj" then
		liczniki = {}
		czasKroku, ileKrokow = 0, 0
		return true
	end
	return nil
end
