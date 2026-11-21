--[[
	SerwerZabawek — serwer dwóch zabawek (Script, RunContext Server, w Workspace/ZabawkiGra). Bez strażnika „tylko Studio”:
	działa także w prywatnej wersji testowej na telefonie. Bez zapisu, złota i warstw — tylko czynność.

	Od klienta tylko Sygnaly/Akcja (rodzaj, a, b): "wybor", 1|2 · "menu" · "ruch", x, z (zabawka 1, długość ≤ 1) · "dash" ·
	"rzut", kat, moc (zabawka 2). Serwer sprawdza typy, tryb gracza i wiadro tempa. Do klientów: Sygnaly/Stan1 i Stan2
	(UnreliableRemoteEvent, bufory) i Sygnaly/Zdarzenia (lista zdarzeń). Haczyki prób tylko po stronie serwera:
	Sygnaly/SterowanieSerwera (BindableFunction — klient nie ma do niej dostępu).
]]
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local kontener = script.Parent
local Moduly = kontener:WaitForChild("Moduly")
local D = require(Moduly:WaitForChild("DaneZabawek"))
local L = require(Moduly:WaitForChild("LogikaZabawek"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evAkcja = Sygnaly:WaitForChild("Akcja")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local evStan1 = Sygnaly:WaitForChild("Stan1")
local evStan2 = Sygnaly:WaitForChild("Stan2")
local sterowanie = Sygnaly:WaitForChild("SterowanieSerwera")
local Z, W = D.zjadacz, D.wabik
local C1 = Vector3.new(Z.srodek[1], Z.srodek[2], Z.srodek[3])
local C2 = Vector3.new(W.srodek[1], W.srodek[2], W.srodek[3])

kontener:SetAttribute("SerwerGotowy", false)
-- wzorce potworów → ReplicatedStorage (klienci je klonują; w Workspace byłyby widoczne)
do
	local RS = game:GetService("ReplicatedStorage")
	local stary = RS:FindFirstChild("ZabawkiWzorce")
	local wz = kontener:FindFirstChild("Wzorce")
	if wz then
		if stary then
			stary:Destroy()
		end
		wz.Name = "ZabawkiWzorce"
		wz.Parent = RS
	end
end
local los = Random.new()
local function r01(): number
	return los:NextNumber()
end
local S1 = L.nowyStan1(D, r01)
for _, m in Z.boty_masy do
	L.dodajByt(S1, 0, m)
end
local S2 = L.nowyStan2(D, r01)

------------------------------------------------------------------ gracze
type Gracz = { slot: number, tryb: string, byt: any, wiadro: { t: number, z: number }, nazwa: string }
local gracze: { [Player]: Gracz } = {}
local poSlocie: { [number]: Player } = {}
local liczniki: { [string]: number } = {}
local wymusOdmiane: string? = nil

local function licz(n: string)
	liczniki[n] = (liczniki[n] or 0) + 1
end

local function wolnySlot(): number?
	for i = 1, W.zagrod do
		if not poSlocie[i] then
			return i
		end
	end
	return nil
end

local function postacNa(plr: Player, cf: CFrame)
	local c = plr.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart")
	if c and hrp and hrp:IsA("BasePart") then
		hrp.Anchored = true
		c:PivotTo(cf)
	end
end

local function ustawPostac(plr: Player, g: Gracz)
	if g.tryb == "z1" then
		-- zabawka 1: gracz jest potworem; awatar schowany pod polem
		postacNa(plr, CFrame.new(C1 + Vector3.new(0, -30, 0)))
	elseif g.tryb == "z2" then
		local zp = W.zagrodyPoz[g.slot]
		postacNa(plr, CFrame.lookAt(C2 + Vector3.new(zp[1], 3.2, zp[2] + W.zagroda_gl / 2 - 1.5), C2 + Vector3.new(zp[1], 3.2, 100)))
	end
end

local function atrybuty2(plr: Player, g: Gracz)
	local G = S2.gracze[g.slot]
	plr:SetAttribute("ZW_Ile", if G then G.zwabione else 0)
	plr:SetAttribute("ZW_Zasieg", L.zasieg(W, if G then G.zwabione else 0))
	local n = G and G.najlepszy
	plr:SetAttribute("ZW_Najlepszy", if n then ((if n.odm then string.upper(n.odm) .. " " else "") .. D.pety[n.nr].nazwa) else "")
	plr:SetAttribute("ZW_NajlepszyRz", if n then D.pety[n.nr].stopien else 0)
end

local function wybierz(plr: Player, g: Gracz, tryb: string)
	if g.byt then
		-- wyjście z zabawki 1: potwór znika
		local zost = {}
		for _, b in S1.byty do
			if b ~= g.byt then
				table.insert(zost, b)
			end
		end
		S1.byty = zost
		g.byt = nil
	end
	g.tryb = tryb
	if tryb == "z1" then
		g.byt = L.dodajByt(S1, g.slot, 1)
		plr:SetAttribute("ZT_Byt", g.byt.id)
	else
		plr:SetAttribute("ZT_Byt", 0)
	end
	if tryb == "z2" then
		L.gracz2(S2, g.slot)
		atrybuty2(plr, g)
	end
	plr:SetAttribute("ZT_Tryb", tryb)
	ustawPostac(plr, g)
	licz("wybor_" .. tryb)
end

local function dolacz(plr: Player)
	local slot = wolnySlot()
	if not slot then
		plr:SetAttribute("ZT_Slot", 0)
		return
	end
	local g: Gracz = { slot = slot, tryb = "menu", byt = nil, wiadro = { t = os.clock(), z = 10 }, nazwa = plr.DisplayName }
	gracze[plr] = g
	poSlocie[slot] = plr
	plr:SetAttribute("ZT_Slot", slot)
	plr:SetAttribute("ZT_Tryb", "menu")
	plr.CharacterAdded:Connect(function(c)
		c:WaitForChild("HumanoidRootPart", 10)
		task.wait()
		if gracze[plr] then
			ustawPostac(plr, gracze[plr])
		end
	end)
end

local function odejdz(plr: Player)
	local g = gracze[plr]
	if not g then
		return
	end
	wybierz(plr, g, "menu")
	L.usunGracza2(S2, g.slot)
	poSlocie[g.slot] = nil
	gracze[plr] = nil
end

------------------------------------------------------------------ akcje
local function wiadro(g: Gracz): boolean
	local t = os.clock()
	g.wiadro.z = math.min(Z.wiadro_zapas, g.wiadro.z + (t - g.wiadro.t) * Z.wiadro_na_s)
	g.wiadro.t = t
	if g.wiadro.z < 1 then
		return false
	end
	g.wiadro.z -= 1
	return true
end

local doWyslania1, doWyslania2 = {}, {}

evAkcja.OnServerEvent:Connect(function(plr: Player, rodzaj: any, a: any, b: any)
	local g = gracze[plr]
	if not g or type(rodzaj) ~= "string" or not wiadro(g) then
		return
	end
	if rodzaj == "ruch" then
		if g.tryb == "z1" and g.byt and not g.byt.martwyDo then
			L.steruj(g.byt, a, b)
		end
	elseif rodzaj == "dash" then
		if g.tryb == "z1" and g.byt and L.dash(S1, g.byt) then
			table.insert(doWyslania1, { t = "dash", id = g.byt.id })
			licz("dash")
		end
	elseif rodzaj == "rzut" then
		if g.tryb == "z2" and type(a) == "number" and type(b) == "number" and a == a and b == b then
			local pr = L.rzut2(S2, g.slot, a, b)
			if pr then
				table.insert(doWyslania2, { t = "przyneta", slot = g.slot, x0 = pr.x0, z0 = pr.z0, x = pr.x, z = pr.z, czas = pr.czas })
				licz("rzut")
			end
		end
	elseif rodzaj == "wybor" then
		if a == 1 or a == 2 then
			wybierz(plr, g, if a == 1 then "z1" else "z2")
		end
	elseif rodzaj == "menu" then
		wybierz(plr, g, "menu")
	end
end)

------------------------------------------------------------------ migawki
local ROZ1 = 18
local function migawka1(): buffer
	local n = #S1.byty
	local nk = #Z.kulkiPoz
	local nb = math.ceil(nk / 8)
	local b = buffer.create(12 + nb + n * ROZ1)
	buffer.writef64(b, 0, workspace:GetServerTimeNow())
	buffer.writeu16(b, 8, n)
	buffer.writeu16(b, 10, S1.apex % 65536)
	for i = 0, nb - 1 do
		local bajt = 0
		for k = 0, 7 do
			local idx = i * 8 + k + 1
			if idx <= nk and S1.kulki[idx] == 0 then
				bajt += 2 ^ k
			end
		end
		buffer.writeu8(b, 12 + i, bajt)
	end
	local o0 = 12 + nb
	for i, e in S1.byty do
		local o = o0 + (i - 1) * ROZ1
		local f = 0
		if e.tarczaDo > S1.czas then
			f += 1
		end
		if e.dashDo > S1.czas then
			f += 2
		end
		if e.martwyDo then
			f += 4
		end
		buffer.writeu16(b, o, e.id % 65536)
		buffer.writeu8(b, o + 2, e.slot)
		buffer.writeu8(b, o + 3, f)
		buffer.writef32(b, o + 4, e.x)
		buffer.writef32(b, o + 8, e.z)
		buffer.writef32(b, o + 12, e.m)
		buffer.writei16(b, o + 16, math.clamp(math.floor(e.kier * 1000 + 0.5), -32000, 32000))
	end
	return b
end

local ROZ2 = 16
local STANY = { laka = 0, ucieka = 1, idzie = 2, zagroda = 3 }
local function migawka2(): buffer
	local n = #S2.potwory
	local b = buffer.create(10 + n * ROZ2)
	buffer.writef64(b, 0, workspace:GetServerTimeNow())
	buffer.writeu16(b, 8, n)
	for i, p in S2.potwory do
		local o = 10 + (i - 1) * ROZ2
		local f = if p.odm == "giant" then 16 elseif p.odm == "golden" then 32 elseif p.odm == "big" then 8 else 0
		if p.rzadki then
			f += 64
		end
		buffer.writeu16(b, o, p.id % 65536)
		buffer.writeu8(b, o + 2, p.nr)
		buffer.writeu8(b, o + 3, (STANY[p.stan] or 0) + 16 * p.strefa)
		buffer.writeu8(b, o + 4, p.wl)
		buffer.writeu8(b, o + 5, f)
		buffer.writef32(b, o + 6, p.x)
		buffer.writef32(b, o + 10, p.z)
		buffer.writei16(b, o + 14, math.clamp(math.floor(p.kier * 1000 + 0.5), -32000, 32000))
	end
	return b
end

------------------------------------------------------------------ pętla
local zb1, zb2, doStan1, doStan2 = 0, 0, 0, 0
local czasKroku, ileKrokow = 0, 0

local function wyslijDo(tryb: string, lista)
	if #lista == 0 then
		return
	end
	for plr, g in gracze do
		if g.tryb == tryb then
			evZdarzenia:FireClient(plr, lista)
		end
	end
end

local function ileW(tryb: string): number
	local n = 0
	for _, g in gracze do
		if g.tryb == tryb then
			n += 1
		end
	end
	return n
end

RunService.Heartbeat:Connect(function(dt: number)
	local t0 = os.clock()
	zb1 = math.min(zb1 + dt, Z.krok_s * 4)
	while zb1 >= Z.krok_s do
		zb1 -= Z.krok_s
		for _, z in L.krok1(S1, Z.krok_s) do
			licz(z.t)
			if z.t ~= "kulka" or z.s > 0 then
				table.insert(doWyslania1, z)
			end
			if z.t == "apex" and z.s > 0 and poSlocie[z.s] then
				table.insert(doWyslania1, { t = "ogloszenie", tekst = string.format(D.ui.ogl_apex, gracze[poSlocie[z.s]].nazwa) })
			end
		end
	end
	zb2 = math.min(zb2 + dt, W.krok_s * 4)
	while zb2 >= W.krok_s do
		zb2 -= W.krok_s
		local zd = L.krok2(S2, W.krok_s, function()
			if wymusOdmiane then
				local x = 0
				for _, o in W.odmiany do
					if o.id == wymusOdmiane then
						wymusOdmiane = nil
						return x + o.szansa * 0.5
					end
					x += o.szansa
				end
				wymusOdmiane = nil
			end
			return los:NextNumber()
		end)
		for _, z in zd do
			licz(z.t)
			table.insert(doWyslania2, z)
			if z.t == "zwabiony" and poSlocie[z.slot] then
				atrybuty2(poSlocie[z.slot], gracze[poSlocie[z.slot]])
			end
		end
	end
	czasKroku += os.clock() - t0
	ileKrokow += 1
	doStan1 -= dt
	if doStan1 <= 0 then
		doStan1 = Z.stan_co_s
		if ileW("z1") > 0 then
			local b = migawka1()
			for plr, g in gracze do
				if g.tryb == "z1" then
					evStan1:FireClient(plr, b)
				end
			end
		end
	end
	doStan2 -= dt
	if doStan2 <= 0 then
		doStan2 = W.stan_co_s
		if ileW("z2") > 0 then
			local b = migawka2()
			for plr, g in gracze do
				if g.tryb == "z2" then
					evStan2:FireClient(plr, b)
				end
			end
		end
	end
	wyslijDo("z1", doWyslania1)
	wyslijDo("z2", doWyslania2)
	doWyslania1, doWyslania2 = {}, {}
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
	if polecenie == "stan" then
		local byty = {}
		for _, e in S1.byty do
			table.insert(byty, { id = e.id, slot = e.slot, m = e.m, x = e.x, z = e.z, forma = e.forma, martwy = e.martwyDo ~= nil,
				tarcza = e.tarczaDo > S1.czas, zjadl = e.zjadl })
		end
		local pot = {}
		for _, p in S2.potwory do
			table.insert(pot, { id = p.id, nr = p.nr, stan = p.stan, wl = p.wl, x = p.x, z = p.z, strefa = p.strefa, odm = p.odm,
				rzadki = p.rzadki })
		end
		local G2 = g and S2.gracze[g.slot]
		return { gotowy = true, tryb = g and g.tryb, slot = g and g.slot, byt = g and g.byt and g.byt.id, byty = byty, apex = S1.apex,
			kulek = (function()
				local n = 0
				for _, k in S1.kulki do
					if k == 0 then
						n += 1
					end
				end
				return n
			end)(), kulkiZywe = (function()
				local w = {}
				for i, k in S1.kulki do
					if k == 0 then
						table.insert(w, i)
					end
				end
				return w
			end)(), potwory = pot, zwabione = G2 and G2.zwabione or 0, zasieg = L.zasieg(W, G2 and G2.zwabione or 0),
			liczniki = liczniki, krok_ms = if ileKrokow > 0 then czasKroku / ileKrokow * 1000 else 0 }
	elseif polecenie == "wybor" then
		if plr and g then
			wybierz(plr, g, a)
		end
		return true
	elseif polecenie == "masa" then
		if g and g.byt then
			g.byt.m = a
		end
		return true
	elseif polecenie == "przenies" then
		local e = L.bytPoId(S1, a)
		if e then
			e.x, e.z = b, c
			e.vx, e.vz = 0, 0
		end
		return e ~= nil
	elseif polecenie == "bot_masa" then
		local e = L.bytPoId(S1, a)
		if e then
			e.m = b
		end
		return e ~= nil
	elseif polecenie == "bot_stoj" then
		-- bot stoi w miejscu przez b sekund (próba zjedzenia)
		local e = L.bytPoId(S1, a)
		if e then
			e.wx, e.wz = 0, 0
			e.myslDo = S1.czas + (b or 3)
		end
		return e ~= nil
	elseif polecenie == "tarcza_zeruj" then
		if g and g.byt then
			g.byt.tarczaDo = 0
		end
		return true
	elseif polecenie == "potwor_tu" then
		-- potwór łąki a stoi w (b, c) przez chwilę (cel próby trafienia)
		for _, p in S2.potwory do
			if p.id == a then
				p.x, p.z, p.cx, p.cz = b, c, b, c
				p.stan = "laka"
			end
		end
		return true
	elseif polecenie == "wymus_odmiane" then
		wymusOdmiane = a
		return true
	elseif polecenie == "zwabione" then
		if g then
			L.gracz2(S2, g.slot).zwabione = a
			atrybuty2(plr :: Player, g)
		end
		return true
	elseif polecenie == "rzadki_teraz" then
		S2.nastRzadki = S2.czas
		return true
	elseif polecenie == "liczniki_zeruj" then
		liczniki = {}
		czasKroku, ileKrokow = 0, 0
		return true
	elseif polecenie == "ladowanie" then
		-- gdzie wyląduje przynęta (kat, moc) przy obecnym zasięgu gracza
		if g then
			local G2 = L.gracz2(S2, g.slot)
			local x, z, t = L.ladowanie(W, g.slot, a, b, L.zasieg(W, G2.zwabione))
			return { x = x, z = z, t = t }
		end
		return nil
	end
	return nil
end
