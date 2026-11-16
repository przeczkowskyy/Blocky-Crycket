--[[
	SerwerTeleportu — serwerowa połowa „teleportu przez chmury” (Script, RunContext = Server, w kontenerze
	Workspace/TeleportChmury; wymaganie Karola z 16.11.2026, D-075 z doprecyzowaniem). Budowa: swiat/teleport_chmury/zbuduj.py.

	Serwer jest jedyną stroną, która przenosi postać. Klient (KlientTeleportu) robi tylko kamerę, chmury i wybór na
	makiecie, a potem prosi zdalną funkcję Zdalne/Teleport:
		InvokeServer("stan")            → { odblokowane = { id, … }, zostalo = s do końca blokady, odstep = s }
		InvokeServer("przenies", id)    → { ok = true, punkt = Vector3, patrz = Vector3, zrodlo = "…" }
		                                  albo { ok = false, powod = "zamknieta" | "za_szybko" | "trwa" | "nieznana" |
		                                         "brak_postaci" | "brak_punktu" | "za_duzo" | "zle_dane" | "blad" }
	Kontrole w tej kolejności: dane → limit próśb → przeniesienie w toku → blokada czasu (odstęp) → znana kraina →
	odblokowana DLA TEGO GRACZA → żywa postać → punkt przybycia. Potem ta sama bezpieczna droga co w
	swiat/biom_las/zrodla/TeleportLasu.server.luau: RequestStreamAroundAsync (okolica celu wczytana u gracza),
	dopiero wtedy PivotTo i zerowanie prędkości.

	Odblokowanie trzyma serwer, osobno dla każdego gracza (na razie tylko w pamięci, bez zapisu): na start krainy
	z od_poczatku = true (Miasteczko, Las). Później strażnik biomu odblokuje następną krainę jednym wywołaniem:
		workspace.TeleportChmury.Sygnaly.SterowanieSerwera:Invoke("odblokuj", "bagno", gracz)

	Punkty przybycia (krainy.json → przybycie, pierwszy pasujący):
		{ gdy_jest = "LasPas", xz = {…}, patrz_xz = {…} }  — tylko gdy w Workspace jest ten obiekt; wysokość z rzutu
		                                                       promienia w dół (tylko części z kolizją, bez postaci)
		{ atrybut = { "LasTeleport", "PunktLas", "PatrzLas" } } — odczyt atrybutów cudzego kontenera (tylko odczyt)
		{ xyz = {…}, patrz_xyz = {…} }                       — zapas wpisany w danych
		{ xz = {…}, patrz_xz = {…} }                         — rzut promienia (krainy jeszcze niezbudowane)

	Działa tylko w Roblox Studio: poza Studio skrypt usuwa cały kontener, jak pozostałe prototypy.
	Haczyk testowy: BindableFunction Sygnaly/SterowanieSerwera (polecenia w funkcji sterowanie niżej).
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local Dane = require(kontener:WaitForChild("Dane"))
local zdalna = kontener:WaitForChild("Zdalne"):WaitForChild("Teleport") :: RemoteFunction
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera") :: BindableFunction

local PREFIKS = "[TeleportChmury] "
local S = Dane.serwer
local KRAINY: { [string]: any } = {}
for _, k in Dane.krainy do
	KRAINY[k.id] = k
end

type Wpis = { odblokowane: { [string]: boolean }, ostatnio: number, wTrakcie: boolean, prosby: { number },
	ostatniWynik: any? }
local gracze: { [Player]: Wpis } = {}

local function wpis(gracz: Player): Wpis
	local w = gracze[gracz]
	if not w then
		w = { odblokowane = {}, ostatnio = -1e9, wTrakcie = false, prosby = {} }
		for _, k in Dane.krainy do
			if k.od_poczatku then
				w.odblokowane[k.id] = true
			end
		end
		gracze[gracz] = w
	end
	return w
end

local function listaOdblokowanych(w: Wpis): { string }
	local t = {}
	for _, k in Dane.krainy do
		if w.odblokowane[k.id] then
			table.insert(t, k.id)
		end
	end
	return t
end

------------------------------------------------------------------ punkt przybycia
local function postacieGraczy(): { Instance }
	local t: { Instance } = {}
	for _, g in Players:GetPlayers() do
		if g.Character then
			table.insert(t, g.Character)
		end
	end
	table.insert(t, kontener)
	return t
end

-- wysokość środka HumanoidRootPart nad gruntem dla tej postaci
local function wysokoscKorzenia(humanoid: Humanoid, korzen: BasePart): number
	if humanoid.RigType == Enum.HumanoidRigType.R15 then
		return humanoid.HipHeight + korzen.Size.Y / 2 + S.zapas_nad_gruntem
	end
	return 3 + S.zapas_nad_gruntem
end

local function wolneMiejsce(pozycja: Vector3, korzen: BasePart): boolean
	local op = OverlapParams.new()
	op.FilterType = Enum.RaycastFilterType.Exclude
	op.FilterDescendantsInstances = postacieGraczy()
	op.RespectCanCollide = true
	local wys = korzen.Size.Y * 2.2
	local czesci = workspace:GetPartBoundsInBox(CFrame.new(pozycja + Vector3.new(0, wys * 0.12, 0)),
		Vector3.new(2.2, wys * 0.8, 2.2), op)
	return #czesci == 0
end

local function rzut(x: number, z: number, humanoid: Humanoid, korzen: BasePart): Vector3?
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	par.FilterDescendantsInstances = postacieGraczy()
	par.RespectCanCollide = true
	-- środek, potem pierścienie dookoła (gdyby w punkcie coś stało)
	local proby = { Vector2.zero }
	for _, r in { 3, 6, 9 } do
		for i = 0, 7 do
			local a = math.rad(i * 45)
			table.insert(proby, Vector2.new(math.cos(a) * r, math.sin(a) * r))
		end
	end
	for _, d in proby do
		local wynik = workspace:Raycast(Vector3.new(x + d.X, S.rzut_od_y, z + d.Y), Vector3.new(0, -S.rzut_dlugosc, 0), par)
		if wynik then
			local p = Vector3.new(x + d.X, wynik.Position.Y + wysokoscKorzenia(humanoid, korzen), z + d.Y)
			if wolneMiejsce(p, korzen) then
				return p
			end
		end
	end
	return nil
end

local function wektor(t: any): Vector3?
	if type(t) == "table" and #t == 3 then
		return Vector3.new(t[1], t[2], t[3])
	end
	return nil
end

local function punktPrzybycia(kraina: any, humanoid: Humanoid, korzen: BasePart): (Vector3?, Vector3?, string)
	for _, p in kraina.przybycie do
		if p.gdy_jest and not workspace:FindFirstChild(p.gdy_jest) then
			continue
		end
		if p.atrybut then
			local k = workspace:FindFirstChild(p.atrybut[1])
			local punkt = k and k:GetAttribute(p.atrybut[2])
			local patrz = k and k:GetAttribute(p.atrybut[3])
			if typeof(punkt) == "Vector3" and typeof(patrz) == "Vector3" then
				return punkt, patrz, "atrybut " .. p.atrybut[1] .. "." .. p.atrybut[2]
			end
		elseif p.xyz then
			return wektor(p.xyz), wektor(p.patrz_xyz), "zapas z danych"
		elseif p.xz then
			local punkt = rzut(p.xz[1], p.xz[2], humanoid, korzen)
			if punkt then
				local patrz = Vector3.new(p.patrz_xz[1], punkt.Y, p.patrz_xz[2])
				return punkt, patrz, (p.gdy_jest and (p.gdy_jest .. ", ") or "") .. "rzut promienia"
			end
		end
	end
	return nil, nil, "brak"
end

------------------------------------------------------------------ przeniesienie
local function przenies(gracz: Player, id: string): any
	local w = wpis(gracz)
	if w.wTrakcie then
		return { ok = false, powod = "trwa" }
	end
	local zostalo = w.ostatnio + S.odstep_s - os.clock()
	if zostalo > 0 then
		return { ok = false, powod = "za_szybko", zostalo = zostalo }
	end
	local kraina = KRAINY[id]
	if not kraina then
		return { ok = false, powod = "nieznana" }
	end
	if not w.odblokowane[id] then
		return { ok = false, powod = "zamknieta" }
	end
	local postac = gracz.Character
	local humanoid = postac and postac:FindFirstChildOfClass("Humanoid")
	local korzen = postac and postac:FindFirstChild("HumanoidRootPart")
	if not postac or not humanoid or humanoid.Health <= 0 or not korzen or not korzen:IsA("BasePart") then
		return { ok = false, powod = "brak_postaci" }
	end
	w.wTrakcie = true
	local ok, wynik = pcall(function()
		local punkt, patrz, zrodlo = punktPrzybycia(kraina, humanoid, korzen)
		if not punkt or not patrz then
			return { ok = false, powod = "brak_punktu" }
		end
		-- okolica celu musi być wczytana u gracza, zanim postać tam stanie (miejsce ma włączone strumieniowanie)
		local t0 = os.clock()
		pcall(function()
			gracz:RequestStreamAroundAsync(punkt, S.limit_wczytania_s)
		end)
		local wczytanie = os.clock() - t0
		if postac.Parent == nil or gracz.Character ~= postac or humanoid.Health <= 0 then
			return { ok = false, powod = "brak_postaci" }
		end
		if humanoid.SeatPart then
			humanoid.Sit = false
			task.wait()
		end
		local naWprost = Vector3.new(patrz.X, punkt.Y, patrz.Z)
		if (naWprost - punkt).Magnitude < 0.1 then
			naWprost = punkt + Vector3.new(0, 0, -1)
		end
		postac:PivotTo(CFrame.lookAt(punkt, naWprost))
		korzen.AssemblyLinearVelocity = Vector3.zero
		korzen.AssemblyAngularVelocity = Vector3.zero
		return { ok = true, punkt = punkt, patrz = naWprost, zrodlo = zrodlo, wczytanie = wczytanie }
	end)
	w.wTrakcie = false
	if not ok then
		warn(PREFIKS .. "błąd przeniesienia: " .. tostring(wynik))
		wynik = { ok = false, powod = "blad" }
	end
	if wynik.ok then
		w.ostatnio = os.clock()
	end
	w.ostatniWynik = { id = id, ok = wynik.ok, powod = wynik.powod, zrodlo = wynik.zrodlo, czas = os.clock() }
	return wynik
end

local function limitProsb(w: Wpis): boolean
	local teraz = os.clock()
	local nowe = {}
	for _, t in w.prosby do
		if teraz - t < S.prosby_okno_s then
			table.insert(nowe, t)
		end
	end
	if #nowe >= S.prosby_max then
		w.prosby = nowe
		return false
	end
	table.insert(nowe, teraz)
	w.prosby = nowe
	return true
end

zdalna.OnServerInvoke = function(gracz: Player, polecenie: any, id: any): any
	if type(polecenie) ~= "string" or (id ~= nil and (type(id) ~= "string" or #id > 32)) then
		return { ok = false, powod = "zle_dane" }
	end
	local w = wpis(gracz)
	if not limitProsb(w) then
		return { ok = false, powod = "za_duzo" }
	end
	if polecenie == "stan" then
		return {
			ok = true,
			odblokowane = listaOdblokowanych(w),
			zostalo = math.max(0, w.ostatnio + S.odstep_s - os.clock()),
			odstep = S.odstep_s,
		}
	elseif polecenie == "przenies" and id then
		return przenies(gracz, id)
	end
	return { ok = false, powod = "zle_dane" }
end

Players.PlayerRemoving:Connect(function(gracz: Player)
	gracze[gracz] = nil
end)

------------------------------------------------------------------ haczyk testowy i API dla innych skryptów serwera
local function ktory(arg: any): Player?
	if typeof(arg) == "Instance" and arg:IsA("Player") then
		return arg
	elseif type(arg) == "string" then
		return Players:FindFirstChild(arg) :: Player?
	end
	return Players:GetPlayers()[1]
end

sterowanie.OnInvoke = function(polecenie: any, a: any, b: any): any
	if polecenie == "stan" then
		local g = ktory(a)
		if not g then
			return { ok = false, powod = "brak_gracza" }
		end
		local w = wpis(g)
		local korzen = g.Character and g.Character:FindFirstChild("HumanoidRootPart")
		return {
			ok = true,
			gracz = g.Name,
			odblokowane = listaOdblokowanych(w),
			wTrakcie = w.wTrakcie,
			odOstatniego = os.clock() - w.ostatnio,
			ostatni = w.ostatniWynik,
			pozycja = korzen and { korzen.Position.X, korzen.Position.Y, korzen.Position.Z } or nil,
		}
	elseif polecenie == "odblokuj" or polecenie == "zablokuj" then
		local g = ktory(b)
		if not g or type(a) ~= "string" or not KRAINY[a] then
			return { ok = false, powod = "zle_dane" }
		end
		wpis(g).odblokowane[a] = (polecenie == "odblokuj") or nil
		return { ok = true, odblokowane = listaOdblokowanych(wpis(g)) }
	elseif polecenie == "przenies" then
		-- test: przeniesienie bez kamery i bez blokady czasu (np. postawienie gracza w miasteczku przed próbą)
		local g = ktory(b)
		if not g or type(a) ~= "string" then
			return { ok = false, powod = "zle_dane" }
		end
		wpis(g).ostatnio = -1e9
		local wynik = przenies(g, a)
		wpis(g).ostatnio = -1e9
		return wynik
	elseif polecenie == "zeruj" then
		local g = ktory(a)
		if g then
			wpis(g).ostatnio = -1e9
		end
		return { ok = g ~= nil }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end

kontener:SetAttribute("SerwerGotowy", true)
