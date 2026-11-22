--[[
	SerwerEwolucji — serwer Monster Evolution (Script, RunContext Server, w Workspace/EwolucjaGra). Strażnik „tylko
	Studio” na początku (zbuduj.py --publikacja go usuwa) i wyłącznik (atrybut EwolucjaWlaczona kontenera).
	Serwer liczy wszystko: jedzenie, wzrost, ewolucję, złoto, zakupy. Klient tylko przewiduje własny ruch.

	Od klienta tylko Sygnaly/Akcja (rodzaj, ...): "ruch", kx, kz, px, pz (kierunek ≤ 1 i pozycja z przewidywania) ·
	"gryz" · "zryw" · "umiejetnosc" · "ewoluuj" · "kup", id. Serwer sprawdza typy, stan bytu i wiadro tempa.
	Do klientów: Sygnaly/Stan (UnreliableRemoteEvent, bufor) i Sygnaly/Zdarzenia (lista). Atrybuty gracza EW_*.
	Miary (w pamięci, bez DataStore): atrybut EW_Miary (JSON) i haczyk "miary". Haczyki prób tylko po stronie
	serwera: Sygnaly/SterowanieSerwera (BindableFunction — klient nie ma do niej dostępu).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
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
kontener:SetAttribute("BossId", boss.id)
kontener:SetAttribute("BossHP", 1)

------------------------------------------------------------------ gracze
type Gracz = { slot: number, byt: any, wiadro: { t: number, z: number }, nazwa: string, start: number, miary: any,
	ostKorekta: number, atr: { [string]: any } }
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
	ustawAtr(plr, g, "EW_ZlotoNaS", L.stawka(D, b.maxForma))
	for _, U in D.ulepszenia do
		ustawAtr(plr, g, "EW_Poz_" .. U.id, L.poziom(b, U.id))
	end
	ustawAtr(plr, g, "EW_Martwy", b.martwyDo ~= nil)
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
		nazwa = plr.DisplayName, start = os.clock(), ostKorekta = 0, atr = {},
		miary = { formy = { ["1"] = 0 }, smierci = 0, po_smierci = {}, ulepszenia = {}, sesja_s = 0 } }
	gracze[plr] = g
	poSlocie[slot] = plr
	plr:SetAttribute("EW_Slot", slot)
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
end

local function odejdz(plr: Player)
	local g = gracze[plr]
	if not g then
		return
	end
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

local RODZAJE = { ruch = true, gryz = true, zryw = true, umiejetnosc = true, ewoluuj = true, kup = true }

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
		if L.umiejetnosc(S, byt, doWyslania) then
			licz("umiejetnosc")
		end
	elseif rodzaj == "ewoluuj" then
		if L.ewoluuj(S, byt, doWyslania) then
			licz("ewoluuj")
		end
	elseif rodzaj == "kup" then
		local ok, powod = L.kup(S, byt, a)
		if ok then
			local p = L.poziom(byt, a)
			table.insert(g.miary.ulepszenia, { id = a, poziom = p, t = math.floor(os.clock() - g.start) })
			plr:SetAttribute("EW_Miary", miaryJSON(g))
			licz("kup")
		end
		atrybuty(plr, g)
		wyslijGraczowi(plr, { { t = "kup", id = if type(a) == "string" then a else "", ok = ok, powod = powod } })
	end
end)

------------------------------------------------------------------ migawki (bufor)
local ROZ = 15
local function migawka(): buffer
	local n = #S.byty
	local nk = #D.kulkiPoz
	local nb = math.ceil(nk / 8)
	local b = buffer.create(12 + nb + n * ROZ)
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
	end
	return b
end

------------------------------------------------------------------ zdarzenia logiki → miary, ogłoszenia
local function poZdarzeniu(z)
	licz(z.t)
	if z.s and z.s > 0 and poSlocie[z.s] then
		local plr = poSlocie[z.s]
		local g = gracze[plr]
		if z.t == "smierc" then
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
		elseif z.t == "olbrzym" then
			table.insert(doWyslania, { t = "ogloszenie", tekst = string.format(D.ui.ogl_olbrzym, g.nazwa) })
		elseif z.t == "las_otwarty" then
			g.miary.las = math.floor((os.clock() - g.start) * 10 + 0.5) / 10
		elseif z.t == "boss_pokonany" then
			g.miary.boss_pokonany = g.miary.boss_pokonany or math.floor((os.clock() - g.start) * 10 + 0.5) / 10
			table.insert(doWyslania, { t = "ogloszenie", tekst = string.format(D.ui.ogl_boss, g.nazwa, D.boss.nazwa) })
			plr:SetAttribute("EW_Miary", miaryJSON(g))
		end
	end
end

------------------------------------------------------------------ pętla
local zb, doStan, doAtr, doMiar = 0, 0, 0, 0
local czasKroku, ileKrokow = 0, 0

RunService.Heartbeat:Connect(function(dt: number)
	local t0 = os.clock()
	zb = math.min(zb + dt, D.ruch.krok_s * 4)
	while zb >= D.ruch.krok_s do
		zb -= D.ruch.krok_s
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
				tarcza = e.tarczaDo > S.czas, kokon = e.kokonDo ~= nil, cel = e.cel, zjadl = e.zjadl })
		end
		local zywe = 0
		for _, k in S.kulki do
			if k == 0 then
				zywe += 1
			end
		end
		return { gotowy = true, czas = S.czas, byt = byt and byt.id, forma = byt and byt.forma, maxForma = byt and byt.maxForma,
			wzrost = byt and byt.wzrost, potrzeba = byt and L.potrzeba(D, byt.forma), zloto = byt and byt.zloto,
			stawka = byt and L.stawka(D, byt.maxForma), poziomy = byt and byt.poziomy, x = byt and byt.x, z = byt and byt.z,
			martwy = byt and byt.martwyDo ~= nil, tarcza = byt and byt.tarczaDo > S.czas, byty = byty, kulek = zywe, strefy = #S.strefy,
			laska = byt and byt.laskaDo > S.czas,
			liczniki = liczniki, krok_ms = if ileKrokow > 0 then czasKroku / ileKrokow * 1000 else 0 }
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
