--!strict
--[[
	JajkoKorowe — stanowisko nowego jajka (Paweł 24.11: „zbuduj to jajko i oskryptuj animację jak najbliżej referencji,
	ze słupem światła”; baza u Pawła — jak trening AFK — do pokazania Karolowi, potem jego decyzja). Działa tylko
	w Studio, jak pakiety Karola, od których zależy.

	Model: Workspace/JajkoKorowePodglad/"Jajko korowe" (swiat/postacie/jajko_korowe.py, Blender, kontener budowany
	przez tools/studio/jajko_korowe_studio.py). Serwer: dokłada podpowiedź E „Jajko korowe” i wyłącza na tym modelu
	pokaz animacji z kontenera (atrybut Zajety) — klipy gra klient (src/client/OknoJajkaClient.client.luau).
	Zakup i losowanie robi serwer petów Karola (Workspace/PetyProba) — tutaj tylko wołamy jego haczyk
	Sygnaly/SterowanieSerwera("kup", gracz, "jajko_lesne") (te same szanse, cena i zapis peta w StanGracza, bez zmian
	w jego plikach); przy kilku jajkach naraz zwalniamy jego blokadę wyklucia ("zwolnij") między zakupami.
	Docelowo E inkubatora Karola może otwierać to okno zamiast kupować od razu — do ustalenia z Karolem.

	Paweł 24.11 (wieczorem): bez osobnego okna — przy jajku wisi podpowiedź z szansami (obrazek panelu petów), E kupuje
	od razu, wyklucie gra jajko w świecie (src/client/JajkoKoroweClient.client.luau).

	Zdalne: ReplicatedStorage.JajkoKorowe (RemoteFunction) — "info" → { ok, cena, szanse = { { pet, nazwa, rzadkosc,
	        rzadkoscNazwa, kolor, szansa } } }
	        ReplicatedStorage.JajkoKoroweZdarzenia (RemoteEvent, serwer → klienci) — "wyklucie", userId kupującego, wynik
	        { pet, nazwa, rzadkosc, rzadkoscNazwa, kolor, nowy, kopie } (do wszystkich: jajko w świecie pęka u każdego);
	        "odmowa", tekst (tylko do kupującego).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local JAJKO = "jajko_lesne"
local ZASIEG = 14
local LIMIT = 0.8

local zdalne = RS:FindFirstChild("JajkoKorowe") :: RemoteFunction?
if not zdalne then
	local f = Instance.new("RemoteFunction")
	f.Name = "JajkoKorowe"
	f.Parent = RS
	zdalne = f
end
local F = zdalne :: RemoteFunction
local Z = RS:FindFirstChild("JajkoKoroweZdarzenia") :: RemoteEvent?
if not Z then
	local e = Instance.new("RemoteEvent")
	e.Name = "JajkoKoroweZdarzenia"
	e.Parent = RS
	Z = e
end
local zdarzenia = Z :: RemoteEvent
local kup: (Player, number) -> any

local function stanowisko(): Model?
	local k = workspace:FindFirstChild("JajkoKorowePodglad")
	local m = k and k:FindFirstChild("Jajko korowe")
	return if m and m:IsA("Model") then m else nil
end

-- podpowiedź E na modelu i wyłączenie pokazu klipów z kontenera (klipy gra klient)
task.spawn(function()
	local m: Model? = nil
	for _ = 1, 60 do
		m = stanowisko()
		if m then
			break
		end
		task.wait(1)
	end
	if not m then
		warn("[JajkoKorowe] brak modelu Workspace/JajkoKorowePodglad/Jajko korowe")
		return
	end
	m:SetAttribute("Zajety", true)
	-- podpowiedź na osobnym, niewidzialnym punkcie obok modelu (na HumanoidRootPart modelu z animatorem Roblox
	-- jej nie pokazuje — sprawdzone 24.11)
	local k = m.Parent :: Instance
	local punkt = k:FindFirstChild("PunktJajka") :: BasePart?
	if not punkt then
		local p = Instance.new("Part")
		p.Name = "PunktJajka"
		p.Anchored, p.CanCollide, p.CanTouch = true, false, false
		p.Transparency = 1
		p.Size = Vector3.new(1, 1, 1)
		p.CFrame = CFrame.new(m:GetPivot().Position + Vector3.new(0, 2, 0))
		p.Parent = k
		punkt = p
	end
	if not (punkt :: BasePart):FindFirstChild("PodpowiedzJajka") then
		local pp = Instance.new("ProximityPrompt")
		pp.Name = "PodpowiedzJajka"
		pp.ActionText = "Kup jajko"
		pp.ObjectText = "Jajko korowe"
		pp.KeyboardKeyCode = Enum.KeyCode.E
		pp.HoldDuration = 0
		pp.MaxActivationDistance = 12
		pp.RequiresLineOfSight = false
		pp.Parent = punkt
	end
	local pp = (punkt :: BasePart):FindFirstChild("PodpowiedzJajka") :: ProximityPrompt
	pp.Triggered:Connect(function(gracz)
		local w = kup(gracz, 1)
		if not w.ok then
			zdarzenia:FireClient(gracz, "odmowa", w.tekst or "…")
			return
		end
		for _, wynik in ipairs(w.wyniki) do
			zdarzenia:FireAllClients("wyklucie", gracz.UserId, wynik)
		end
	end)
end)

local function pety(): (any, any)
	local k = workspace:FindFirstChild("PetyProba")
	local mod = k and k:FindFirstChild("Moduly")
	local d = mod and mod:FindFirstChild("DanePetow")
	local s = k and k:FindFirstChild("Sygnaly")
	local h = s and s:FindFirstChild("SterowanieSerwera")
	if not (d and d:IsA("ModuleScript")) then
		return nil, nil
	end
	local ok, D = pcall(require, d)
	return if ok then D else nil, if h and h:IsA("BindableFunction") then h else nil
end

local function opisPeta(D: any, id: string): any
	local r = { pet = id, nazwa = id, rzadkosc = "", rzadkoscNazwa = "", kolor = "FFFFFF" }
	for _, p in ipairs(D.pety or {}) do
		if p.id == id then
			r.nazwa, r.rzadkosc = p.nazwa, p.rzadkosc
		end
	end
	for _, rz in ipairs(D.rzadkosci or {}) do
		if rz.id == r.rzadkosc then
			r.kolor, r.rzadkoscNazwa = rz.kolor, rz.nazwa
		end
	end
	return r
end

local function jajko(D: any): any
	for _, j in ipairs(D.jajka or {}) do
		if j.id == JAJKO then
			return j
		end
	end
	return nil
end

local function przyJajku(gracz: Player): boolean
	local m = stanowisko()
	local char = gracz.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not (m and hrp) then
		return false
	end
	local d = hrp.Position - m:GetPivot().Position
	return Vector3.new(d.X, 0, d.Z).Magnitude <= ZASIEG
end

local ostatnie: { [Player]: number } = {}
local zajety: { [Player]: boolean } = {}

kup = function(gracz: Player, n: number): any
	if zajety[gracz] then
		return { ok = false, tekst = "Jajko już pęka…" }
	end
	local D, haczyk = pety()
	if not D or not haczyk then
		return { ok = false, tekst = "Jajka nieczynne (brak serwera petów Karola)" }
	end
	local j = jajko(D)
	if not j then
		return { ok = false, tekst = "Brak jajka leśnego w danych" }
	end
	if not przyJajku(gracz) then
		return { ok = false, tekst = "Podejdź do jajka" }
	end
	zajety[gracz] = true
	local ile = if n == 3 then 3 else 1
	local wyniki = {}
	local tekst: string? = nil
	for _ = 1, ile do
		local ok, w = pcall(function()
			return haczyk:Invoke("kup", gracz, JAJKO)
		end)
		if not ok or type(w) ~= "table" or not w.ok then
			tekst = if ok and type(w) == "table" and type(w.tekst) == "string" then w.tekst else "Nie udało się kupić"
			break
		end
		local o = opisPeta(D, w.pet)
		o.nowy, o.kopie = w.nowy == true, w.kopie
		table.insert(wyniki, o)
		pcall(function()
			haczyk:Invoke("zwolnij", gracz) -- jego blokada wyklucia: animację gramy tutaj
		end)
	end
	task.delay(3.5, function()
		zajety[gracz] = nil -- tyle trwa wyklucie w świecie
	end)
	return { ok = #wyniki > 0, wyniki = wyniki, cena = gracz:GetAttribute(j.atrybuty.cena), tekst = tekst }
end

F.OnServerInvoke = function(gracz: Player, akcja: any, n: any)
	local t = os.clock()
	if ostatnie[gracz] and t - ostatnie[gracz] < LIMIT then
		return { ok = false, tekst = "Za szybko" }
	end
	ostatnie[gracz] = t
	local D = pety()
	if not D then
		return { ok = false, tekst = "Jajka nieczynne (brak PetyProba)" }
	end
	local j = jajko(D)
	if not j then
		return { ok = false, tekst = "Brak jajka leśnego w danych" }
	end
	local cena = gracz:GetAttribute(j.atrybuty.cena)
	if akcja == "info" then
		local szanse = {}
		for _, s in ipairs(j.szanse) do
			local o = opisPeta(D, s.pet)
			o.szansa = s.szansa
			table.insert(szanse, o)
		end
		return { ok = true, cena = cena, szanse = szanse }
	end
	return { ok = false, tekst = "?" }
end

Players.PlayerRemoving:Connect(function(g)
	ostatnie[g] = nil
	zajety[g] = nil
end)
