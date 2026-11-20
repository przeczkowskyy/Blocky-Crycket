--[[
	SerwerPetArena — serwer gry Pet Arena (Script, RunContext Server, w Workspace/PetArenaGra). Jedyne źródło prawdy:
	walka w 2D (LogikaPetArena, stały krok), rzuty, umiejętności, złoto, nagroda za głowę, dzikie pety, odpoczynek petów;
	etap 2: jajka i kolekcja (gwiazdki, Księga), drużyna, trener (poziom, mata), wydarzenia (BOSS, GOLDEN PET z
	zapowiedzią), tarcza słabszego (w logice), tablice, komunikaty, zapis (własny magazyn z ochroną prób).

	Od klienta tylko Sygnaly/Akcja (rodzaj, a, b, c): "rzut", nr w drużynie, x, z · "umiejetnosc" · "wybierz", nr ·
	"jajko", nr · "druzyna", { id, … } · "trening", bool — serwer sprawdza typy, wiadro tempa (wspólne), cel, limit
	areny, jednego peta gracza, odpoczynek, złoto, posiadanie petów. Do klientów: Sygnaly/Stan (UnreliableRemoteEvent,
	bufor: pety co walka.stan_co_s) i Sygnaly/Zdarzenia (lista zdarzeń). Stan gracza w atrybutach PA_* (ustawia tylko
	serwer). Haczyki prób: Sygnaly/SterowanieSerwera. W próbie (znacznik ZapisProbaDo z tools/zapis_prob.py) zamiast
	nazw kont „Player 1”, „Player 2”, a magazyn nie jest czytany ani pisany (gracz w pamięci).
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

------------------------------------------------------------------ wzorce → ReplicatedStorage (klienci je klonują)
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
local proba = kontener:GetAttribute(D.zapis.znacznik_proby) ~= nil
local odpoczynekS = D.odpoczynek
local liczniki: { [string]: number } = {}
local doWyslania = {}

local function teraz(): number
	return workspace:GetServerTimeNow()
end

------------------------------------------------------------------ zapis
local Z = D.zapis
local magazyn: any = nil
do
	local nazwa, stan = L.magazyn(Z, RunService:IsStudio(), kontener:GetAttribute(Z.znacznik_proby), os.time(),
		kontener:GetAttribute(Z.znacznik_magazynu) == true)
	if nazwa then
		local ok, ds = pcall(function()
			return game:GetService("DataStoreService"):GetDataStore(nazwa)
		end)
		if ok and ds then
			magazyn = ds
		else
			stan = "w pamięci (magazyn niedostępny)"
		end
	end
	kontener:SetAttribute("ZapisStan", stan)
	kontener:SetAttribute("ZapisMagazyn", if magazyn then nazwa else nil)
end

------------------------------------------------------------------ gracze
type Gracz = { slot: number, profil: any, odp: { [string]: number }, wybrany: number, naArenie: string?, wiadro: any,
	nazwa: string, odrzucone: number, gs: number, zapisywalny: boolean, wczytany: boolean, trening: boolean, ostJajko: number,
	ostZapis: number, krolOd: number? }
local gracze: { [Player]: Gracz } = {}
local poSlocie: { [number]: Player } = {}
local nrProby = 0

local function klucz(plr: Player): string
	return "g_" .. plr.UserId
end

local function wolnySlot(): number?
	for i = 1, #D.sloty do
		if not poSlocie[i] then
			return i
		end
	end
	return nil
end

local function postacNa(plr: Player, gdzie: { number })
	local c = plr.Character
	local hrp = c and c:FindFirstChild("HumanoidRootPart")
	if not hrp then
		return
	end
	local poz = Vector3.new(gdzie[1], gdzie[2] + 3.2, gdzie[3])
	c:PivotTo(CFrame.lookAt(poz, Vector3.new(0, poz.Y, 0)))
end

local function postacNaSlot(plr: Player, g: Gracz)
	local s = D.sloty[g.slot]
	postacNa(plr, if g.trening then s.mata else s.poz)
end

local function druzyna(g: Gracz)
	return L.druzyna(D, g.profil, g.odp)
end

local function poziomGracza(g: Gracz): number
	return (L.poziom(D, g.profil.xp))
end

local function najlepszy(profil): (string?, number)
	local best, bs, bg = nil, -1, 0
	for id, gw in profil.pety do
		local nr = L.nrPeta(D, id)
		if nr then
			local s = D.pety[nr].stopien * 10 + gw
			if s > bs then
				best, bs, bg = D.pety[nr].nazwa, s, gw
			end
		end
	end
	return best, bg
end

local function atrybuty(plr: Player, g: Gracz)
	local pr = g.profil
	local dr, odp = {}, {}
	local tn = teraz()
	for _, w in druzyna(g) do
		table.insert(dr, w.id .. ":" .. w.gwiazdki)
		table.insert(odp, string.format("%.2f", math.max(0, w.odpoczynek)))
	end
	local kol, ks = {}, {}
	for id, gw in pr.pety do
		table.insert(kol, id .. ":" .. gw)
	end
	for id in pr.ksiega do
		table.insert(ks, id)
	end
	plr:SetAttribute("PA_Druzyna", table.concat(dr, ","))
	plr:SetAttribute("PA_Odpoczynek", table.concat(odp, ","))
	plr:SetAttribute("PA_Kolekcja", table.concat(kol, ","))
	plr:SetAttribute("PA_Ksiega", table.concat(ks, ","))
	plr:SetAttribute("PA_Wybrany", g.wybrany)
	local naArenie = 0
	for i, id in pr.druzyna do
		if id == g.naArenie then
			naArenie = i
		end
	end
	plr:SetAttribute("PA_NaArenie", naArenie)
	plr:SetAttribute("PA_Zloto", pr.zloto)
	local lv, x, potrzeba = L.poziom(D, pr.xp)
	plr:SetAttribute("PA_Poziom", lv)
	plr:SetAttribute("PA_Xp", x)
	plr:SetAttribute("PA_XpPotrzeba", potrzeba)
	plr:SetAttribute("PA_Samouczek", (if pr.samouczek.rzut then "1" else "0") .. (if pr.samouczek.jajko then "1" else "0"))
	plr:SetAttribute("PA_Wybicia", pr.wybicia)
	plr:SetAttribute("PA_Trening", g.trening)
	local b, bg = najlepszy(pr)
	plr:SetAttribute("PA_Najlepszy", if b then b .. ":" .. bg else "")
	plr:SetAttribute("PA_Rzucil", pr.samouczek.rzut)
	local _ = tn
end

local function dodajZloto(plr: Player, g: Gracz, ile: number)
	g.profil.zloto += ile
	plr:SetAttribute("PA_Zloto", g.profil.zloto)
end

local function dodajXp(plr: Player, g: Gracz, ile: number)
	local przed = poziomGracza(g)
	g.profil.xp += ile
	local lv, x, potrzeba = L.poziom(D, g.profil.xp)
	plr:SetAttribute("PA_Poziom", lv)
	plr:SetAttribute("PA_Xp", x)
	plr:SetAttribute("PA_XpPotrzeba", potrzeba)
	if lv > przed then
		evZdarzenia:FireClient(plr, { { t = "poziom", poziom = lv } })
	end
end

local function zapisz(plr: Player, powod: string): boolean
	local g = gracze[plr]
	if not g or not g.wczytany then
		return false
	end
	local ok = L.zapiszProfil(D, magazyn, klucz(plr), g.profil, g.zapisywalny)
	if ok then
		g.ostZapis = os.clock()
		kontener:SetAttribute("LicznikZapisow", (kontener:GetAttribute("LicznikZapisow") or 0) + 1)
	elseif magazyn and g.zapisywalny then
		warn(P .. "zapis (" .. powod .. ") nie powiódł się")
	end
	return ok
end

local function dolacz(plr: Player)
	local slot = wolnySlot()
	if not slot then
		plr:SetAttribute("PA_Slot", 0)
		return
	end
	nrProby += 1
	local g: Gracz = { slot = slot, profil = L.profilNowy(D), odp = {}, wybrany = 1, naArenie = nil, wiadro = {},
		nazwa = if proba then string.format(D.ui.gracz_proby, nrProby) else plr.DisplayName, odrzucone = 0, gs = 0,
		zapisywalny = false, wczytany = false, trening = false, ostJajko = 0, ostZapis = os.clock(), krolOd = nil }
	gracze[plr] = g
	poSlocie[slot] = plr
	plr:SetAttribute("PA_Slot", slot)
	plr:SetAttribute("PA_Nazwa", g.nazwa)
	plr:SetAttribute("PA_GS", 0)
	plr:SetAttribute("PA_Pet", 0)
	atrybuty(plr, g)
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
	-- wczytanie (bez wczytania nie zapisujemy)
	task.spawn(function()
		local profil, zapisywalny = L.wczytajProfil(D, magazyn, klucz(plr), function(n)
			task.wait(n)
		end)
		if gracze[plr] ~= g then
			return
		end
		g.profil, g.zapisywalny, g.wczytany = profil, zapisywalny, true
		plr:SetAttribute("PA_ProfilGotowy", true)
		atrybuty(plr, g)
	end)
end

local function odejdz(plr: Player)
	local g = gracze[plr]
	if not g then
		return
	end
	zapisz(plr, "wyjście")
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
	if z.t ~= "ladowanie" and z.t ~= "koniec_akcji" then
		table.insert(ostatnie, { t = z.t, a = z.a, b = z.b, id = z.id, v = z.v, k = z.k, o = z.o, przez = z.przez, premia = z.premia,
			nagroda = z.nagroda, krol = z.krol, boss = z.boss, zloty = z.zloty, wl = z.wl, ile = z.ile })
		if #ostatnie > 60 then
			table.remove(ostatnie, 1)
		end
	end
	table.insert(doWyslania, z)
end

local function ogloszenie(tekst: string, kolor: string)
	wyslij({ t = "ogloszenie", tekst = tekst, kolor = kolor })
end

local function zakonczKrola(id: number)
	-- najdłuższe panowanie (tablica LONGEST KING) dla właściciela peta
	for plr, g in gracze do
		if g.krolOd and g.krolId == id then
			g.profil.krolS = math.max(g.profil.krolS, math.floor(S.czas - g.krolOd))
			g.krolOd, g.krolId = nil, nil
		end
	end
end

local function obsluzZdarzenia(lista)
	for _, z in lista do
		if z.t == "ringout" or z.t == "ko" then
			if z.krol then
				zakonczKrola(z.id)
			end
			local ofiara = poSlocie[z.wl]
			if z.wl > 0 and not z.dziki and ofiara and gracze[ofiara] then
				local g = gracze[ofiara]
				if g.naArenie then
					g.odp[g.naArenie] = teraz() + odpoczynekS
				end
				g.naArenie = nil
				ofiara:SetAttribute("PA_Pet", 0)
				atrybuty(ofiara, g)
			end
			local zabojca = poSlocie[z.przez]
			if z.przez > 0 and zabojca and gracze[zabojca] and (z.premia > 0 or z.nagroda > 0) then
				local g = gracze[zabojca]
				dodajZloto(zabojca, g, z.premia + z.nagroda)
				g.profil.wybicia += 1
				zabojca:SetAttribute("PA_Wybicia", g.profil.wybicia)
				dodajXp(zabojca, g, D.trener.za_wybicie)
				if z.krol and z.nagroda >= D.pokazanie.nagroda_ogloszenie then
					ogloszenie(string.format(D.ui.ogl_krol, g.nazwa, L.format(z.nagroda)), D.ui.kolory.zloto)
				end
			end
			if z.boss and z.nagrody then
				local lista2 = {}
				for wl, ile in z.nagrody do
					local plr = poSlocie[wl]
					if plr and gracze[plr] then
						dodajZloto(plr, gracze[plr], ile)
						dodajXp(plr, gracze[plr], D.trener.za_bossa)
						table.insert(lista2, { wl = wl, ile = ile })
					end
				end
				z.nagrody = lista2
				local B = D.boss.modele[S.bossModel or 1]
				ogloszenie(string.format(D.ui.ogl_boss, B and B.nazwa or "BOSS"), D.ui.kolory.zloto)
			end
		elseif z.t == "zloto_cios" then
			local plr = poSlocie[z.wl]
			if plr and gracze[plr] then
				dodajZloto(plr, gracze[plr], z.ile)
			end
		elseif z.t == "krol" then
			local plr = poSlocie[z.wl]
			if z.wl > 0 and not z.dziki and plr and gracze[plr] then
				gracze[plr].krolOd = S.czas
				gracze[plr].krolId = z.id
			end
		elseif z.t == "krol_stracil" then
			zakonczKrola(z.id)
		end
		wyslij(z)
	end
end

------------------------------------------------------------------ dzikie pety i wydarzenia
local nastBot = D.boty.pierwszy_s
local czekajBota: { [number]: number } = {}
local nastWyd = D.wydarzenia.pierwsze_s
local nrWyd = 1
local nrBossa = 0

local function zGejzera()
	local g = math.floor(los:NextNumber() * D.scena.gejzery)
	local a = 2 * math.pi * (g + 0.5) / D.scena.gejzery
	return math.sin(a) * D.scena.gejzer_r, math.cos(a) * D.scena.gejzer_r
end

local function rzutDzikiego(nr: number?, x: number?, z: number?)
	local n = nr or L.losujPetaBota(D, los:NextNumber(), los:NextNumber())
	local x0, z0 = zGejzera()
	local r = los:NextNumber() * 14
	local b = los:NextNumber() * 2 * math.pi
	local tx, tz = x or math.sin(b) * r, z or math.cos(b) * r
	local p = L.dodajPeta(S, n, 0, true, x0, D.scena.woda_y, z0, tx, tz)
	wyslij({ t = "rzut", id = p.id, nr = p.nr, wl = 0, dziki = true, x0 = x0, y0 = D.scena.woda_y, z0 = z0, x = tx, z = tz,
		czas = p.lotCzas })
	return p
end

local function wydarzenieAtrybuty()
	kontener:SetAttribute("PA_WydTyp", L.typWydarzenia(D, nrWyd))
	kontener:SetAttribute("PA_WydT", teraz() + math.max(0, nastWyd - S.czas))
end

local function zacznijWydarzenie()
	local typ = L.typWydarzenia(D, nrWyd)
	local graczy = 0
	for _ in gracze do
		graczy += 1
	end
	if typ == "boss" then
		nrBossa = (nrBossa % #D.boss.modele) + 1
		S.bossModel = nrBossa
		local p = L.dodajBossa(S, nrBossa, math.max(1, graczy))
		wyslij({ t = "boss", id = p.id, nr = nrBossa, nazwa = p.P.nazwa, czas = p.lotCzas, hp = p.hpMax })
	else
		local x0, z0 = zGejzera()
		local p = L.dodajZlotego(S, x0, D.scena.woda_y, z0, 0, 0)
		wyslij({ t = "zloty", id = p.id, nr = p.nr, x0 = x0, y0 = D.scena.woda_y, z0 = z0, x = 0, z = 0, czas = p.lotCzas })
	end
	nrWyd += 1
	nastWyd = S.czas + D.wydarzenia.co_s
	wydarzenieAtrybuty()
end

local function botyKrok()
	if S.czas >= nastBot and L.ileBotowBrakuje(S) > 0 then
		rzutDzikiego()
		nastBot = S.czas + (S.botyCo or D.boty.co_s)
	end
	if S.czas >= nastWyd and not S.bezWydarzen then
		zacznijWydarzenie()
	end
	local zd = {}
	for _, p in S.pety do
		if p.dziki and p.faza == "walka" and not p.boss and not p.zloty then
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
	local dr = druzyna(g)
	if type(nr) ~= "number" or nr ~= math.floor(nr) or nr < 1 or nr > #dr then
		return odmowa(plr, "zle")
	end
	if L.petGracza(S, g.slot) then
		return odmowa(plr, "masz")
	end
	local w = dr[nr]
	if not L.gotowy(w, teraz()) then
		return odmowa(plr, "odpoczywa")
	end
	local ok, powod = L.mozeRzucic(S, x, z)
	if not ok then
		return odmowa(plr, powod or "zle")
	end
	local s = D.sloty[g.slot]
	local baza = if g.trening then s.mata else s.poz
	local start = Vector3.new(baza[1], baza[2] + 4, baza[3])
	local c = plr.Character
	local reka = c and (c:FindFirstChild("RightHand") or c:FindFirstChild("Right Arm") or c:FindFirstChild("HumanoidRootPart"))
	if reka and reka:IsA("BasePart") and (reka.Position - start).Magnitude < 12 then
		start = reka.Position + Vector3.new(0, 1, 0)
	end
	local p = L.dodajPeta(S, w.nr, g.slot, false, start.X, start.Y, start.Z, x, z, L.mnoznikPeta(D, w.gwiazdki, poziomGracza(g)))
	g.naArenie = w.id
	g.wybrany = nr
	g.profil.rzuty += 1
	g.profil.samouczek.rzut = true
	plr:SetAttribute("PA_Pet", p.id)
	atrybuty(plr, g)
	wyslij({ t = "rzut", id = p.id, nr = p.nr, wl = g.slot, dziki = false, x0 = start.X, y0 = start.Y, z0 = start.Z, x = x, z = z,
		czas = p.lotCzas, gwiazdki = w.gwiazdki })
end

local function jajko(plr: Player, g: Gracz, nr: any)
	if type(nr) ~= "number" or nr ~= math.floor(nr) or nr < 1 or nr > #D.jajka then
		return odmowa(plr, "zle")
	end
	if os.clock() - g.ostJajko < 2.6 then
		return odmowa(plr, "czekaj")
	end
	local J = D.jajka[nr]
	local darmowe = nr == 1 and not g.profil.samouczek.jajko
	local cena = if darmowe then 0 else J.cena
	if g.profil.zloto < cena then
		return odmowa(plr, "zloto")
	end
	g.ostJajko = os.clock()
	g.profil.zloto -= cena
	g.profil.samouczek.jajko = true
	g.profil.jajek += 1
	local pnr, rz = L.losujZJajka(D, nr, los:NextNumber(), los:NextNumber())
	local Pd = D.pety[pnr]
	local w = L.dodajDoKolekcji(D, g.profil, Pd.id, J.cena)
	atrybuty(plr, g)
	evZdarzenia:FireClient(plr, { { t = "wyklucie", jajko = nr, pet = pnr, rzadkosc = rz, nowy = w.nowy, gwiazdki = w.gwiazdki,
		maks = w.maks, zwrot = w.zwrot, cena = cena } })
	liczniki.wyklucie = (liczniki.wyklucie or 0) + 1
	if rz >= 4 then
		ogloszenie(string.format(D.ui.ogl_legendarny, g.nazwa, string.upper(D.rzadkosci[rz].nazwa), Pd.nazwa), D.rzadkosci[rz].kolor)
	end
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
		if type(a) == "number" and a == math.floor(a) and a >= 1 and a <= #g.profil.druzyna then
			g.wybrany = a
			plr:SetAttribute("PA_Wybrany", a)
		end
	elseif rodzaj == "jajko" then
		jajko(plr, g, a)
	elseif rodzaj == "druzyna" then
		if L.ustawDruzyne(D, g.profil, a) then
			g.wybrany = math.min(g.wybrany, #g.profil.druzyna)
			atrybuty(plr, g)
		else
			odmowa(plr, "zle")
		end
	elseif rodzaj == "trening" then
		if type(a) == "boolean" then
			g.trening = a
			postacNaSlot(plr, g)
			plr:SetAttribute("PA_Trening", a)
		end
	else
		g.odrzucone += 1
	end
end)

------------------------------------------------------------------ tablice (ściana dołu)
local folderTablic = kontener:FindFirstChild("Tablice")
local function odswiezTablice()
	if not folderTablic then
		return
	end
	local zrodla = { {}, {}, {} }
	for _, g in gracze do
		local krol = g.profil.krolS
		if g.krolOd then
			krol = math.max(krol, math.floor(S.czas - g.krolOd))
		end
		table.insert(zrodla[1], { nazwa = g.nazwa, w = g.gs })
		table.insert(zrodla[2], { nazwa = g.nazwa, w = krol })
		table.insert(zrodla[3], { nazwa = g.nazwa, w = g.profil.wybicia })
	end
	for i, T in D.tablice do
		local m = folderTablic:FindFirstChild("Tablica" .. i)
		local sg = m and m:FindFirstChild("Ekran", true)
		if sg then
			local top = L.top(zrodla[i], T.wierszy)
			for r = 1, T.wierszy do
				local l = sg:FindFirstChild("Rzad" .. r, true)
				if l then
					local w = top[r]
					l.Text = if w then string.format("%d. %s  %s%s", r, w.nazwa, L.format(w.w), if i == 1 then " G/s" elseif i == 2 then "s" else "")
						else ""
				end
			end
		end
	end
end

------------------------------------------------------------------ stan do klientów (bufor)
local ROZMIAR_PETA = 24
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
		local f2 = 0
		if not p.dziki and L.chroniony(S, p) then
			f2 += 1
		end
		if p.boss then
			f2 += 2
		end
		if p.zloty then
			f2 += 4
		end
		buffer.writeu16(b, o, p.id % 65536)
		buffer.writeu8(b, o + 2, if p.boss then 200 + (p.nrModelu or 1) else p.nr)
		buffer.writeu8(b, o + 3, if p.dziki then 0 else p.wl)
		buffer.writeu8(b, o + 4, if p.faza == "walka" then 1 else 0)
		buffer.writeu8(b, o + 5, f)
		buffer.writef32(b, o + 6, p.x)
		buffer.writef32(b, o + 10, p.z)
		buffer.writeu16(b, o + 14, math.clamp(math.floor(p.hp + 0.5), 0, 65535))
		buffer.writeu16(b, o + 16, math.clamp(math.floor(p.hpMax + 0.5), 0, 65535))
		buffer.writeu8(b, o + 18, math.clamp(math.floor(p.pasek * 255 + 0.5), 0, 255))
		buffer.writeu8(b, o + 19, math.clamp(math.floor(p.zl + 0.5), 0, 255))
		buffer.writei16(b, o + 20, math.clamp(math.floor((p.kier or 0) * 1000 + 0.5), -32000, 32000))
		buffer.writeu8(b, o + 22, p.gwiazdki or 1)
		buffer.writeu8(b, o + 23, f2)
	end
	return b
end

------------------------------------------------------------------ pętla
local zbior = 0
local doStanu = 0
local doZlota = 1
local doTablic = 0
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
				local xp = 0
				if ile > 0 then
					dodajZloto(plr, g, ile)
					local p = L.petGracza(S, g.slot)
					if p then
						evZdarzenia:FireClient(plr, { { t = "zloto", id = p.id, ile = ile } })
					end
				end
				if L.petGracza(S, g.slot) then
					xp += D.trener.za_s_na_arenie
				end
				if g.trening then
					xp += D.trener.mata_na_s
				end
				if xp > 0 then
					dodajXp(plr, g, xp)
				end
				if os.clock() - g.ostZapis > D.zapis.co_s then
					g.ostZapis = os.clock()
					task.spawn(zapisz, plr, "okresowy")
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
	doTablic -= dt
	if doTablic <= 0 then
		doTablic = D.tabliceCo
		odswiezTablice()
		wydarzenieAtrybuty()
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
game:BindToClose(function()
	for plr in gracze do
		zapisz(plr, "zamknięcie")
	end
end)
wydarzenieAtrybuty()
kontener:SetAttribute("SerwerGotowy", true)
print(P .. "serwer gotowy (" .. D.skrot .. ")")

------------------------------------------------------------------ haczyki prób
local function opisPeta(p)
	return { id = p.id, nr = p.nr, pet = p.P.id, nazwa = p.P.nazwa, wl = p.wl, dziki = p.dziki, x = p.x, z = p.z, hp = p.hp,
		hpMax = p.hpMax, faza = p.faza, pasek = p.pasek, krol = S.krol == p.id, zl = p.zl, boss = p.boss == true,
		zloty = p.zloty == true, gwiazdki = p.gwiazdki, chroniony = L.chroniony(S, p), mnSila = p.mnSila,
		akcja = if p.akcja then p.akcja.typ else nil, r = L.dlug(p.x, p.z) }
end

local function pierwszy(): (Player?, Gracz?)
	for plr, g in gracze do
		return plr, g
	end
	return nil, nil
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
			for _, w in druzyna(g) do
				table.insert(dr, { id = w.id, odpoczynek_s = L.zostalo(w, tn), gwiazdki = w.gwiazdki })
			end
			local naArenie = 0
			for i, id in g.profil.druzyna do
				if id == g.naArenie then
					naArenie = i
				end
			end
			table.insert(lista, { nazwa = g.nazwa, slot = g.slot, zloto = g.profil.zloto, gs = g.gs, pet = plr:GetAttribute("PA_Pet"),
				druzyna = dr, wybrany = g.wybrany, naArenie = naArenie, wybicia = g.profil.wybicia, rzuty = g.profil.rzuty,
				odrzucone = g.odrzucone, pety = g.profil.pety, ksiega = g.profil.ksiega, xp = g.profil.xp, poziom = poziomGracza(g),
				samouczek = g.profil.samouczek, trening = g.trening, zapisywalny = g.zapisywalny, wczytany = g.wczytany,
				jajek = g.profil.jajek, krolS = g.profil.krolS })
		end
		return { gotowy = true, czas = S.czas, pety = pety, krol = S.krol, nagroda = S.nagroda, gracze = lista,
			dzikich = L.ileDzikich(S), liczniki = liczniki, ostatnie = ostatnie, zapis = kontener:GetAttribute("ZapisStan"),
			odpoczynek = odpoczynekS, srKroku_ms = if ileKrokow > 0 then czasKroku / ileKrokow * 1000 else 0,
			nastWyd = nastWyd - S.czas, typWyd = L.typWydarzenia(D, nrWyd), bossUdzial = S.bossUdzial }
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
			p.akcja = nil
		end
		return p ~= nil
	elseif polecenie == "stoj" then
		local p = L.petPoId(S, a)
		if p then
			p.ogl = S.czas + b
		end
		return p ~= nil
	elseif polecenie == "cd" then
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
		-- próby: dopisz pety do kolekcji (gwiazdki b) i ustaw drużynę
		for plr, g in gracze do
			for _, id in a do
				if L.nrPeta(D, id) then
					g.profil.pety[id] = b or g.profil.pety[id] or 1
					g.profil.ksiega[id] = true
				end
			end
			L.ustawDruzyne(D, g.profil, a)
			g.wybrany = 1
			g.odp = {}
			atrybuty(plr, g)
		end
		return true
	elseif polecenie == "odpoczynki_zeruj" then
		for plr, g in gracze do
			g.odp = {}
			atrybuty(plr, g)
		end
		return true
	elseif polecenie == "profil_nowy" then
		for plr, g in gracze do
			g.profil = L.profilNowy(D)
			g.odp = {}
			g.wybrany = 1
			atrybuty(plr, g)
		end
		return true
	elseif polecenie == "xp" then
		local plr, g = pierwszy()
		if plr and g then
			dodajXp(plr, g, a)
		end
		return g and g.profil.xp
	elseif polecenie == "wydarzenie" then
		-- a: "boss" | "zloty"; b = sekund do startu (0 — teraz)
		for n, typ in D.wydarzenia.kolejnosc do
			if typ == a then
				nrWyd = n
			end
		end
		nastWyd = S.czas + (b or 0)
		wydarzenieAtrybuty()
		return true
	elseif polecenie == "bez_wydarzen" then
		S.bezWydarzen = a == true
		if a then
			nastWyd = S.czas + 9999
		end
		wydarzenieAtrybuty()
		return true
	elseif polecenie == "zapisz" then
		local plr = pierwszy()
		return plr and zapisz(plr, "próba") or false
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
