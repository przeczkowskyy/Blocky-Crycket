--[[
	SerwerBazaru — serwerowa połowa „miasteczka-bazaru w grze” (Script, RunContext = Server, w kontenerze
	Workspace/MiasteczkoBazarGra; budowa: swiat/miasteczko_bazar_gra/zbuduj.py). Działa tylko w Roblox Studio:
	poza Studio usuwa cały kontener, jak pozostałe prototypy (LasTeleport, LasPasGra, TeleportChmury).

	Co robi:
		1. zgodność logiki: przypadki wzorcowe z lustra w Pythonie (DaneBazaru.przypadki) → atrybut ZgodnoscLogikiBazaru;
		2. włącza podpowiedzi E w Punkty/E <id> (zbudowane w Edit z wyłączonym Enabled) i słucha Triggered;
		3. każde E: odległość gracza od podpowiedzi (zasięg + zapas), ochrona przed spamem, potem LogikaBazaru.decyzja:
		   okno     → klient (Zdalne/ZdarzeniaBazaru "okno", id): zdarzenie dla okien 2D Pawła, sygnał HUD, dymek;
		   dymek    → klient ("dymek", id, tekst): odmowa albo „Zamknięte” nad miejscem;
		   chmury   → klient ("chmury", id): Workspace/TeleportChmury/Otworz:Fire() (przejście przez chmury);
		   las      → uchwyt Workspace/LasPasGra/Sygnaly/PrzeniesDoLasu (przenosi serwer pasa: wczytanie okolicy,
		              własny odstęp 2 s); bez uchwytu czytelna odmowa;
		   przenies → ten serwer: stare miasteczko ↔ start bazaru (RequestStreamAroundAsync, potem PivotTo,
		              zerowanie prędkości), blokada czasu odstep_przejsc_s po udanym przejściu i „w trakcie”;
		4. lochy (D-042): stan osobno dla gracza, w pamięci serwera (bez zapisu); atrybut gracza BazarLochyOtwarte
		   (klient chowa u siebie kłódkę); odblokowanie haczykiem albo poziomem, gdy D.lochy.wymagany_poziom jest liczbą;
		5. tablica: SurfaceGui Tablica/Ekran/Ranking — ranking graczy serwera z atrybutów gracza (Level, XP, statystyki
		   ustawiane dziś przez src/server/PlayerStatsDefaults — PLACEHOLDER do czasu DataStore);
		6. uchwyty: Sygnaly/PrzeniesDoBazaru (BindableFunction dla innych skryptów serwera — przejście przez chmury
		   może lądować na starcie bazaru) i Sygnaly/SterowanieSerwera (testy).

	Uchwyt dla innych skryptów serwera (ten sam kształt co LasPasGra/Sygnaly/PrzeniesDoLasu):
		local f = workspace:FindFirstChild("MiasteczkoBazarGra") and workspace.MiasteczkoBazarGra.Sygnaly.PrzeniesDoBazaru
		local w = f:Invoke(gracz, { punkt = "start" })
		-- w = { ok = true, punkt = Vector3, patrz = Vector3 } | { ok = false, powod = "zly_gracz" | "trwa" |
		--     "brak_postaci" | "nieznany_punkt" | "blad" }
	Punkt startu jest też w atrybutach kontenera PunktStartuBazaru / PatrzStartuBazaru (Vector3, środek
	HumanoidRootPart) — wpis { atrybut = { "MiasteczkoBazarGra", "PunktStartuBazaru", "PatrzStartuBazaru" } }
	w swiat/teleport_chmury/krainy.json działa bez żadnej zmiany kodu przejścia przez chmury.
]]
if not game:GetService("RunService"):IsStudio() then
	-- poza Studio (opublikowane miejsce) pakiet usuwa cały kontener, zanim ktokolwiek dołączy
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneBazaru"))
local L = require(moduly:WaitForChild("LogikaBazaru"))
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaBazaru")
local sygnaly = kontener:WaitForChild("Sygnaly")
local przeniesF: BindableFunction = sygnaly:WaitForChild("PrzeniesDoBazaru")
local sterowanie: BindableFunction = sygnaly:WaitForChild("SterowanieSerwera")
local folderPunktow = kontener:WaitForChild("Punkty")

local P = D.prefiks

local function v3(t): Vector3
	return Vector3.new(t[1], t[2], t[3])
end

local function dolicz(nazwa: string)
	kontener:SetAttribute(nazwa, (kontener:GetAttribute(nazwa) or 0) + 1)
end

kontener:SetAttribute("SerwerBazaruGotowy", false)
kontener:SetAttribute("LicznikE", 0)
kontener:SetAttribute("LicznikPrzejsc", 0)
kontener:SetAttribute("OstatnieE", "")
kontener:SetAttribute("PunktStartuBazaru", v3(D.start.korzen))
kontener:SetAttribute("PatrzStartuBazaru", v3(D.start.patrz))

------------------------------------------------------------------ zgodność logiki (te same przypadki co w Pythonie)
local okLogiki, nLogiki, bledyLogiki = L.sprawdzPrzypadki(D)
if okLogiki then
	kontener:SetAttribute("ZgodnoscLogikiBazaru", string.format("OK %d/%d", nLogiki, nLogiki))
else
	kontener:SetAttribute("ZgodnoscLogikiBazaru",
		string.format("BŁĄD %d/%d: %s", nLogiki - #bledyLogiki, nLogiki, tostring(bledyLogiki[1])))
	warn(P .. "zgodność logiki: " .. tostring(bledyLogiki[1]))
end

------------------------------------------------------------------ co jest w miejscu (cudze kontenery: tylko odczyt)
local function sciezka(tekst: string): Instance?
	local o: Instance? = workspace
	for i, n in string.split(tekst, "/") do
		if not (i == 1 and n == "Workspace") then
			o = o and o:FindFirstChild(n)
		end
	end
	return o
end

local function uchwytLasu(): BindableFunction?
	local f = sciezka(D.las.uchwyt)
	if f and f:IsA("BindableFunction") then
		return f
	end
	return nil
end

local function chmuryDostepne(): boolean
	local t = workspace:FindFirstChild(D.chmury.kontener)
	local o = t and t:FindFirstChild(D.chmury.zdarzenie)
	return o ~= nil and o:IsA("BindableEvent")
end

------------------------------------------------------------------ stan graczy
local stany = {}

local function stanGracza(gracz: Player)
	local s = stany[gracz]
	if not s then
		s = L.nowyStan()
		stany[gracz] = s
	end
	return s
end

local function postacGracza(gracz: Player): (Model?, Humanoid?, BasePart?)
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not postac or not hum or hum.Health <= 0 or not hrp or not hrp:IsA("BasePart") then
		return nil, nil, nil
	end
	return postac, hum, hrp
end

------------------------------------------------------------------ przenoszenie (stare miasteczko ↔ bazar)
local function pominDlaPromienia(): { Instance }
	local t: { Instance } = { kontener }
	for _, g in Players:GetPlayers() do
		if g.Character then
			table.insert(t, g.Character)
		end
	end
	return t
end

-- grunt pod punktem: promień z małej wysokości nad podanym poziomem, tylko części z kolizją (bez dachów i markiz)
local function grunt(x: number, z: number, y0: number): number
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	par.FilterDescendantsInstances = pominDlaPromienia()
	par.RespectCanCollide = true
	local r = workspace:Raycast(Vector3.new(x, y0 + 6, z), Vector3.new(0, -14, 0), par)
	return if r then r.Position.Y else y0
end

local function wysokoscKorzenia(hum: Humanoid, hrp: BasePart): number
	if hum.RigType == Enum.HumanoidRigType.R15 then
		return hum.HipHeight + hrp.Size.Y / 2 + 0.15
	end
	return 3.15
end

-- cel = { punkt = Vector3 (na gruncie), patrz = Vector3 } → (ok, powód?, punkt?)
local function przenies(gracz: Player, cel): (boolean, string?, Vector3?)
	local postac, hum, hrp = postacGracza(gracz)
	if not postac or not hum or not hrp then
		return false, "brak_postaci", nil
	end
	local y = grunt(cel.punkt.X, cel.punkt.Z, cel.punkt.Y)
	local punkt = Vector3.new(cel.punkt.X, y + wysokoscKorzenia(hum, hrp), cel.punkt.Z)
	-- okolica celu musi być wczytana u gracza, zanim postać tam stanie (miejsce może mieć streaming)
	pcall(function()
		gracz:RequestStreamAroundAsync(punkt, D.czasy.limit_wczytania_s)
	end)
	if gracz.Character ~= postac or postac.Parent == nil or hum.Health <= 0 then
		return false, "brak_postaci", nil
	end
	if hum.SeatPart then
		hum.Sit = false
		task.wait()
	end
	local patrz = Vector3.new(cel.patrz.X, punkt.Y, cel.patrz.Z)
	if (patrz - punkt).Magnitude < 0.1 then
		patrz = punkt + Vector3.new(1, 0, 0)
	end
	postac:PivotTo(CFrame.lookAt(punkt, patrz))
	hrp.AssemblyLinearVelocity = Vector3.zero
	hrp.AssemblyAngularVelocity = Vector3.zero
	dolicz("LicznikPrzejsc")
	return true, nil, punkt
end

local function celBazaru()
	return { punkt = v3(D.start.punkt), patrz = v3(D.start.patrz) }
end

-- punkt powrotu w starym miasteczku wybrał zbuduj.py w Studio (atrybuty kontenera, tylko odczyt)
local function celStarego()
	local p, q = kontener:GetAttribute("PunktPowrotuStare"), kontener:GetAttribute("PatrzPowrotuStare")
	if typeof(p) == "Vector3" and typeof(q) == "Vector3" then
		return { punkt = p, patrz = q }
	end
	return nil
end

local CELE = { bazar = celBazaru, stare = celStarego }

------------------------------------------------------------------ lochy (D-042, osobno dla gracza)
local function odswiezLochy(gracz: Player)
	local otwarte = L.lochyOtwarte(D, stanGracza(gracz), gracz:GetAttribute("Level"))
	if gracz:GetAttribute(D.lochy.atrybut_gracza) ~= otwarte then
		gracz:SetAttribute(D.lochy.atrybut_gracza, otwarte)
	end
end

------------------------------------------------------------------ wykonanie decyzji
local function wynikDoKlienta(gracz: Player, id: string, w)
	if w.akcja == "okno" then
		zdarzenia:FireClient(gracz, "okno", id)
	elseif w.akcja == "dymek" then
		zdarzenia:FireClient(gracz, "dymek", id, w.tekst)
	elseif w.akcja == "chmury" then
		zdarzenia:FireClient(gracz, "chmury", id)
	end
end

local function przejscie(gracz: Player, id: string, w)
	local s = stanGracza(gracz)
	L.poczatekPrzejscia(s)
	task.spawn(function()
		local udane, powod = false, "blad"
		local ok, blad = pcall(function()
			if w.akcja == "las" then
				local f = uchwytLasu()
				if not f then
					powod = "brak_lasu"
					return
				end
				local r = f:Invoke(gracz, { punkt = D.las.punkt, przelotPo = 0 })
				if type(r) == "table" and r.ok == true then
					udane = true
				elseif type(r) == "table" and type(r.powod) == "string" then
					powod = r.powod
				end
			else
				local zrob = CELE[w.cel]
				local cel = zrob and zrob()
				if not cel then
					powod = "brak_celu"
					return
				end
				local ok2, powod2 = przenies(gracz, cel)
				udane = ok2
				powod = powod2 or powod
			end
		end)
		if not ok then
			warn(P .. "błąd przejścia " .. id .. ": " .. tostring(blad))
		end
		L.koniecPrzejscia(s, udane, os.clock())
		if udane then
			zdarzenia:FireClient(gracz, "przeniesiono", id, if w.akcja == "las" then "las" else w.cel)
		else
			zdarzenia:FireClient(gracz, "dymek", id, L.tekstOdmowy(D, powod, 0))
		end
		kontener:SetAttribute("OstatniePrzejscie", string.format("%s:%s:%s", gracz.Name, id, if udane then "ok" else powod))
	end)
end

local function swiatDla(gracz: Player, id: string, czesc: BasePart?, bezOdleglosci: boolean?)
	local _, _, hrp = postacGracza(gracz)
	local m = D.miejsca[id]
	local zrob = m and m.cel and CELE[m.cel]
	return {
		odleglosc = if bezOdleglosci or not hrp or not czesc then nil else (hrp.Position - czesc.Position).Magnitude,
		chmury = chmuryDostepne(),
		las = uchwytLasu() ~= nil,
		cel = zrob ~= nil and zrob() ~= nil,
		poziom = gracz:GetAttribute("Level"),
	}
end

local function obsluz(gracz: Player, id: string, czesc: BasePart?, bezOdleglosci: boolean?)
	local s = stanGracza(gracz)
	local w = L.decyzja(D, id, s, os.clock(), swiatDla(gracz, id, czesc, bezOdleglosci))
	dolicz("LicznikE")
	kontener:SetAttribute("OstatnieE", string.format("%s:%s:%s%s", gracz.Name, id, w.akcja,
		if w.powod then "/" .. w.powod else ""))
	if w.akcja == "las" or w.akcja == "przenies" then
		przejscie(gracz, id, w)
	else
		wynikDoKlienta(gracz, id, w)
	end
	return w
end

------------------------------------------------------------------ podpowiedzi E
local czesciPunktow: { [string]: BasePart } = {}
local liczbaPodpowiedzi = 0
for _, czesc in folderPunktow:GetChildren() do
	local id = czesc:GetAttribute("Miejsce")
	local pp = czesc:FindFirstChild("Podpowiedz")
	if czesc:IsA("BasePart") and type(id) == "string" and D.miejsca[id] and pp and pp:IsA("ProximityPrompt") then
		czesciPunktow[id] = czesc
		pp.Triggered:Connect(function(gracz: Player)
			obsluz(gracz, id, czesc, false)
		end)
		pp.Enabled = true
		liczbaPodpowiedzi += 1
	end
end
kontener:SetAttribute("Podpowiedzi", liczbaPodpowiedzi)
if liczbaPodpowiedzi ~= #D.kolejnosc then
	warn(string.format("%spodpowiedzi E: %d zamiast %d (przebuduj: python -B swiat/miasteczko_bazar_gra/zbuduj.py)",
		P, liczbaPodpowiedzi, #D.kolejnosc))
end

------------------------------------------------------------------ tablica z rankingiem
local ekran = kontener:FindFirstChild("Tablica") and kontener.Tablica:FindFirstChild("Ekran")
local ranking = ekran and ekran:FindFirstChild("Ranking")
local tlo = ranking and ranking:FindFirstChild("Tlo")
local WAZNE = { Level = true, XP = true }
for _, a in D.tablica.statystyki do
	WAZNE[a] = true
end
local brudna = true
local ostatnieWiersze = {}

local function listaGraczy()
	local lista = {}
	for _, g in Players:GetPlayers() do
		local moc, ma = 0, false
		for _, a in D.tablica.statystyki do
			local v = g:GetAttribute(a)
			if type(v) == "number" then
				moc += v
				ma = true
			end
		end
		local poz, xp = g:GetAttribute("Level"), g:GetAttribute("XP")
		table.insert(lista, {
			nazwa = g.Name,
			poziom = if type(poz) == "number" then poz else nil,
			xp = if type(xp) == "number" then xp else nil,
			moc = if ma then moc else nil,
		})
	end
	return lista
end

local function odswiezTablice()
	brudna = false
	local wiersze = L.ranking(listaGraczy(), D.tablica.wiersze)
	ostatnieWiersze = {}
	for i = 1, D.tablica.wiersze do
		local tekst = if wiersze[i] then L.wiersz(wiersze[i]) elseif i == 1 then D.tablica.pusto else ""
		ostatnieWiersze[i] = tekst
		local l = tlo and tlo:FindFirstChild("W" .. i)
		if l and l:IsA("TextLabel") then
			l.Text = tekst
		end
	end
	kontener:SetAttribute("TablicaWierszy", #wiersze)
end

if not tlo then
	warn(P .. "brak Tablica/Ekran/Ranking/Tlo — tablica bez rankingu (przebuduj kontener)")
end

------------------------------------------------------------------ gracze
local function nowyGracz(gracz: Player)
	stanGracza(gracz)
	odswiezLochy(gracz)
	brudna = true
	gracz.AttributeChanged:Connect(function(a: string)
		if WAZNE[a] then
			brudna = true
		end
		if a == "Level" then
			odswiezLochy(gracz)
		end
	end)
end
Players.PlayerAdded:Connect(nowyGracz)
for _, g in Players:GetPlayers() do
	nowyGracz(g)
end
Players.PlayerRemoving:Connect(function(gracz: Player)
	stany[gracz] = nil
	brudna = true
end)

task.spawn(function()
	while kontener.Parent do
		if brudna then
			local ok, blad = pcall(odswiezTablice)
			if not ok then
				warn(P .. "tablica: " .. tostring(blad))
			end
		end
		task.wait(D.czasy.odswiez_tablice_s)
	end
end)

------------------------------------------------------------------ uchwyt dla innych skryptów serwera
przeniesF.OnInvoke = function(gracz: any, opcje: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") then
		return { ok = false, powod = "zly_gracz" }
	end
	if type(opcje) == "table" and opcje.punkt ~= nil and opcje.punkt ~= "start" then
		return { ok = false, powod = "nieznany_punkt" }
	end
	local s = stanGracza(gracz)
	if s.wTrakcie then
		return { ok = false, powod = "trwa" }
	end
	L.poczatekPrzejscia(s)
	local cel = celBazaru()
	local okP, ok, powod, punkt = pcall(przenies, gracz, cel)
	L.koniecPrzejscia(s, okP and ok == true, os.clock())
	if not okP then
		warn(P .. "PrzeniesDoBazaru: " .. tostring(ok))
		return { ok = false, powod = "blad" }
	end
	if not ok then
		return { ok = false, powod = powod or "blad" }
	end
	return { ok = true, punkt = punkt, patrz = cel.patrz }
end

------------------------------------------------------------------ haczyk testowy (tylko Studio)
local function znajdzGracza(a: any): Player?
	if typeof(a) == "Instance" and a:IsA("Player") then
		return a
	elseif type(a) == "string" then
		local g = Players:FindFirstChild(a)
		return if g and g:IsA("Player") then g else nil
	end
	return Players:GetPlayers()[1]
end

local function opisGracza(gracz: Player)
	local s = stanGracza(gracz)
	local _, _, hrp = postacGracza(gracz)
	return {
		stan = L.kopia(s),
		lochyOtwarte = gracz:GetAttribute(D.lochy.atrybut_gracza),
		pozycja = if hrp then hrp.Position else nil,
	}
end

sterowanie.OnInvoke = function(polecenie: any, a: any, b: any)
	if polecenie == "stan" then
		local gracze = {}
		for _, g in Players:GetPlayers() do
			gracze[g.Name] = opisGracza(g)
		end
		return {
			gotowy = kontener:GetAttribute("SerwerBazaruGotowy"),
			podpowiedzi = liczbaPodpowiedzi,
			las = uchwytLasu() ~= nil,
			chmury = chmuryDostepne(),
			stare = celStarego() ~= nil,
			zgodnosc = kontener:GetAttribute("ZgodnoscLogikiBazaru"),
			tablica = ostatnieWiersze,
			gracze = gracze,
		}
	elseif polecenie == "e" then
		-- E bez klawisza (jak Triggered, ale bez sprawdzania odległości): a = id miejsca, b = gracz
		local g = znajdzGracza(b)
		if not g or type(a) ~= "string" then
			return { akcja = "nic", powod = "zle_dane" }
		end
		return obsluz(g, a, czesciPunktow[a], true)
	elseif polecenie == "przenies" then
		-- test: przeniesienie bez blokady czasu; a = "bazar" | "stare", b = gracz
		local g = znajdzGracza(b)
		local zrob = type(a) == "string" and CELE[a]
		local cel = zrob and zrob()
		if not g or not cel then
			return { ok = false, powod = "zle_dane" }
		end
		local ok, powod, punkt = przenies(g, cel)
		return { ok = ok, powod = powod, punkt = punkt }
	elseif polecenie == "zeruj" then
		local g = znajdzGracza(a)
		if g then
			local s = stanGracza(g)
			s.ostatnieE, s.ostatniePrzejscie, s.wTrakcie = -1e9, -1e9, false
		end
		return g ~= nil
	elseif polecenie == "lochy" then
		-- odblokowanie lochów osobno dla gracza: a = true/false, b = gracz
		local g = znajdzGracza(b)
		if not g then
			return false
		end
		stanGracza(g).lochy = a == true
		odswiezLochy(g)
		return g:GetAttribute(D.lochy.atrybut_gracza)
	elseif polecenie == "tablica" then
		odswiezTablice()
		return ostatnieWiersze
	elseif polecenie == "zgodnosc" then
		return { ok = okLogiki, n = nLogiki, bledy = bledyLogiki }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end

kontener:SetAttribute("Las", if uchwytLasu() then "jest" else "brak")
kontener:SetAttribute("Chmury", if chmuryDostepne() then "jest" else "brak")
kontener:SetAttribute("SerwerBazaruGotowy", true)
