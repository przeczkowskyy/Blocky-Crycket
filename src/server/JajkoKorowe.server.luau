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

	26.11 (Paweł: „niech zrobi agent Karola, wzorując się na animacji jaja lasu”): to samo stanowisko dla jajek Bagna
	i Dżungli (swiat/jajka_biomow) — modele z atrybutem JajkoId (jajko_bagienne, jajko_dzungli) w
	Workspace/JajkaBiomowPodglad, podpowiedź E na ich punkcie „Punkt <nazwa modelu>”, zakup tym samym haczykiem z id
	jajka z atrybutu. Bez modelu jajka biomu nic się nie dzieje (stanowisko po prostu nie powstaje).

	Zdalne: ReplicatedStorage.JajkoKorowe (RemoteFunction) — "info", idJajka? (bez id — leśne) → { ok, cena,
	        szanse = { { pet, nazwa, rzadkosc, rzadkoscNazwa, kolor, szansa } } }
	        ReplicatedStorage.JajkoKoroweZdarzenia (RemoteEvent, serwer → klienci) — "wyklucie", userId kupującego, wynik
	        { pet, nazwa, rzadkosc, rzadkoscNazwa, kolor, nowy, kopie, jajko } (do wszystkich: jajko w świecie pęka
	        u każdego; jajko = id jajka, które pęka); "odmowa", tekst, idJajka (tylko do kupującego).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local JAJKO = "jajko_lesne" -- leśne jajo Pawła (jajka biomów: id z atrybutu JajkoId modelu)
local BIOMY = "JajkaBiomowPodglad" -- kontener jajek Bagna i Dżungli (swiat/jajka_biomow)
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
-- stanowisko = jajko w świecie: id jajka w danych petów Karola, model, nazwa punktu E i jego wysokość nad modelem
type Stanowisko = { id: string, model: Model, punkt: string, wysokosc: number }
local stanowiska: { [string]: Stanowisko } = {} -- id jajka → stanowisko (leśne i jajka biomów, które stoją w świecie)
local kup: (Player, number, Stanowisko) -> any

local function stanowisko(): Model?
	local k = workspace:FindFirstChild("JajkoKorowePodglad")
	local m = k and k:FindFirstChild("Jajko korowe")
	return if m and m:IsA("Model") then m else nil
end

-- podpowiedź E na modelu i wyłączenie pokazu klipów z kontenera (klipy gra klient)
local function podepnij(st: Stanowisko)
	local m = st.model
	stanowiska[st.id] = st
	m:SetAttribute("Zajety", true)
	-- podpowiedź na osobnym, niewidzialnym punkcie obok modelu (na HumanoidRootPart modelu z animatorem Roblox
	-- jej nie pokazuje — sprawdzone 24.11)
	local k = m.Parent :: Instance
	local punkt = k:FindFirstChild(st.punkt) :: BasePart?
	if not punkt then
		local p = Instance.new("Part")
		p.Name = st.punkt
		p.Anchored, p.CanCollide, p.CanTouch = true, false, false
		p.Transparency = 1
		p.Size = Vector3.new(1, 1, 1)
		p.CFrame = CFrame.new(m:GetPivot().Position + Vector3.new(0, st.wysokosc, 0))
		p.Parent = k
		punkt = p
	end
	if not (punkt :: BasePart):FindFirstChild("PodpowiedzJajka") then
		local pp = Instance.new("ProximityPrompt")
		pp.Name = "PodpowiedzJajka"
		pp.ActionText = "Kup jajko"
		pp.ObjectText = if st.id == JAJKO then "Jajko korowe" else m.Name
		pp.KeyboardKeyCode = Enum.KeyCode.E
		pp.HoldDuration = 0
		pp.MaxActivationDistance = 12
		pp.RequiresLineOfSight = false
		pp.Parent = punkt
	end
	local pp = (punkt :: BasePart):FindFirstChild("PodpowiedzJajka") :: ProximityPrompt
	pp.Triggered:Connect(function(gracz)
		local w = kup(gracz, 1, st)
		if not w.ok then
			zdarzenia:FireClient(gracz, "odmowa", w.tekst or "…", st.id)
			return
		end
		for _, wynik in ipairs(w.wyniki) do
			zdarzenia:FireAllClients("wyklucie", gracz.UserId, wynik)
		end
	end)
end

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
	podepnij({ id = JAJKO, model = m :: Model, punkt = "PunktJajka", wysokosc = 2 })
end)

-- jajka biomów: modele z atrybutem JajkoId w Workspace/JajkaBiomowPodglad (punkt E „Punkt <nazwa modelu>” stawia
-- swiat/jajka_biomow/studio/jajko_<biom>_ustaw.luau, 3 studa nad jajem); bez modelu — nic
task.spawn(function()
	local k = workspace:WaitForChild(BIOMY, 60)
	if not k then
		return
	end
	local function sprawdz(m: Instance)
		local id = m:GetAttribute("JajkoId")
		local bylo = if type(id) == "string" then stanowiska[id] else nil
		if m:IsA("Model") and type(id) == "string" and id ~= JAJKO and not (bylo and bylo.model.Parent) then
			podepnij({ id = id, model = m, punkt = "Punkt " .. m.Name, wysokosc = 3 })
		end
	end
	for _, m in ipairs(k:GetChildren()) do
		sprawdz(m)
	end
	k.ChildAdded:Connect(function(m)
		task.wait(0.5) -- atrybuty i części dochodzą chwilę po modelu
		sprawdz(m)
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

local function jajko(D: any, id: string): any
	for _, j in ipairs(D.jajka or {}) do
		if j.id == id then
			return j
		end
	end
	return nil
end

local function przyJajku(gracz: Player, st: Stanowisko): boolean
	local m = if st.model.Parent then st.model else nil
	local char = gracz.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not (m and hrp) then
		return false
	end
	local d = hrp.Position - m:GetPivot().Position
	return Vector3.new(d.X, 0, d.Z).Magnitude <= ZASIEG
end

local ostatnie: { [Player]: { [string]: number } } = {} -- ostatnie „info” gracza dla każdego jajka
local zajety: { [Player]: number | boolean } = {}

kup = function(gracz: Player, n: number, st: Stanowisko): any
	if zajety[gracz] then
		return { ok = false, tekst = "Jajko już pęka…" }
	end
	local D, haczyk = pety()
	if not D or not haczyk then
		return { ok = false, tekst = "Jajka nieczynne (brak serwera petów Karola)" }
	end
	local j = jajko(D, st.id)
	if not j then
		return { ok = false, tekst = if st.id == JAJKO then "Brak jajka leśnego w danych" else "Brak jajka w danych: " .. st.id }
	end
	if not przyJajku(gracz, st) then
		return { ok = false, tekst = "Podejdź do jajka" }
	end
	zajety[gracz] = true
	local ile = if n == 3 then 3 else 1
	local wyniki = {}
	local tekst: string? = nil
	for _ = 1, ile do
		local ok, w = pcall(function()
			return haczyk:Invoke("kup", gracz, st.id)
		end)
		if not ok or type(w) ~= "table" or not w.ok then
			tekst = if ok and type(w) == "table" and type(w.tekst) == "string" then w.tekst else "Nie udało się kupić"
			break
		end
		local o = opisPeta(D, w.pet)
		o.nowy, o.kopie = w.nowy == true, w.kopie
		o.jajko = st.id -- które jajko w świecie pęka (JajkoKoroweClient)
		table.insert(wyniki, o)
		pcall(function()
			haczyk:Invoke("zwolnij", gracz) -- jego blokada wyklucia: animację gramy tutaj
		end)
	end
	if #wyniki == 0 then
		-- nic nie kupione (np. brak Złota): bez blokady — inaczej następne E przez 45 s dostawało „Jajko już pęka…”
		-- (znalezione w próbie 26.11: odmowa „Brakuje ci…”, dopisane Złoto, E → „pęka”)
		zajety[gracz] = nil
		return { ok = false, wyniki = wyniki, tekst = tekst }
	end
	-- questy (src/server/Questy.server.luau): każde kupione jajko liczy się do „Hatch eggs”
	local q = game:GetService("ServerStorage"):FindFirstChild("QuestPostep")
	if #wyniki > 0 and q and q:IsA("BindableEvent") then
		q:Fire(gracz, "jajka", #wyniki)
	end
	-- kupujący otwiera jajo klikaniem we własnym tempie: blokadę zdejmuje jego „koniec” (niżej), najpóźniej po 45 s
	local znacznik = os.clock()
	zajety[gracz] = znacznik
	task.delay(45, function()
		if zajety[gracz] == znacznik then
			zajety[gracz] = nil
		end
	end)
	return { ok = #wyniki > 0, wyniki = wyniki, cena = gracz:GetAttribute(j.atrybuty.cena), tekst = tekst }
end

F.OnServerInvoke = function(gracz: Player, akcja: any, idJajka: any)
	-- id jajka od klienta tylko spośród stanowisk, które stoją w świecie (bez id — leśne, jak dotąd)
	local id = if type(idJajka) == "string" and stanowiska[idJajka] then idJajka else JAJKO
	local t = os.clock()
	local o = ostatnie[gracz] or {}
	ostatnie[gracz] = o
	if o[id] and t - o[id] < LIMIT then
		return { ok = false, tekst = "Za szybko" }
	end
	o[id] = t
	local D = pety()
	if not D then
		return { ok = false, tekst = "Jajka nieczynne (brak PetyProba)" }
	end
	local j = jajko(D, id)
	if not j then
		return { ok = false, tekst = if id == JAJKO then "Brak jajka leśnego w danych" else "Brak jajka w danych: " .. id }
	end
	local cena = gracz:GetAttribute(j.atrybuty.cena)
	if akcja == "info" then
		local szanse = {}
		-- opis umiejętności jak na tablicy Karola (LogikaPetow.opisSkilla)
		local L: any = nil
		local k = workspace:FindFirstChild("PetyProba")
		local mod = k and k:FindFirstChild("Moduly")
		local lm = mod and mod:FindFirstChild("LogikaPetow")
		if lm and lm:IsA("ModuleScript") then
			local okL, wynik = pcall(require, lm)
			L = if okL then wynik else nil
		end
		for _, s in ipairs(j.szanse) do
			local o = opisPeta(D, s.pet)
			o.szansa = s.szansa
			if L and L.opisSkilla and L.pet then
				local okS, opis = pcall(function()
					return L.opisSkilla(D, L.pet(D, s.pet))
				end)
				o.skill = if okS and type(opis) == "string" then opis else ""
			end
			table.insert(szanse, o)
		end
		return { ok = true, cena = cena, szanse = szanse }
	end
	return { ok = false, tekst = "?" }
end

zdarzenia.OnServerEvent:Connect(function(gracz, rodzaj)
	if rodzaj == "koniec" then
		zajety[gracz] = nil
	end
end)

Players.PlayerRemoving:Connect(function(g)
	ostatnie[g] = nil
	zajety[g] = nil
end)
