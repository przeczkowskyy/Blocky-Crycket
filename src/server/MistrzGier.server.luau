--!strict
--[[
	MistrzGier — plansza i kostka u mistrza gier w karczmie (D-053, Paweł 24.11: okno ma działać, „żeby coś robiło”).
	Wersja bazowa u Pawła; okno: src/client/OknoMistrzaGierClient.client.luau, grafika src/gui/OknoMistrzaGier.

	Zasady (D-053): rzut kostką sześcienną, pionek idzie po 25 polach planszy (od startu, razem 26), każde pole ma stałą, zawsze dodatnią
	nagrodę w Rybkach (D-146) — im dalej, tym lepszą; złota gwiazda na końcu = duża nagroda i nowa, lepsza plansza
	(nagrody × 1,5 za każdą). Bez stawek i bez ryzyka. Darmowy rzut co DARMOWY_CO sekund; kolejne rzuty płatne, cena
	rośnie z każdym płatnym rzutem (wraca do startu przy darmowym).

	Decyduje serwer (klient wysyła tylko „stan” i „rzut”). Stan planszy jest na czas sesji (atrybuty gracza
	MistrzPole, MistrzPlansza) — zapis profilu dojdzie razem z pakietem Karola.
	Rybki (atrybut Gold) zmienia wyłącznie stan gracza Karola (Workspace/StanGracza):
	  - nagroda pola: Sygnaly/SterowanieSerwera("przyznaj", gracz, lup) — w bazie to haczyk testowy Karola; docelowo
	    mistrz gier powinien mieć własne źródło nagród (pytanie dla Karola w Pytania otwarte);
	  - płatny rzut: Sygnaly/WydajZloto(gracz, { ile, zrodlo = "MistrzGier", cel = "rzut" }) — dopóki Karol nie dopisze
	    „MistrzGier” do listy źródeł wydatków (DaneStanu.wydatki.zrodla), stan gracza odmawia, a okno mówi, że płatne
	    rzuty czekają na podpięcie.
	Bez StanGracza plansza działa, ale nic nie wypłaca (komunikat w oknie).

	Zdalne: ReplicatedStorage.MistrzGier (RemoteFunction)
		"stan"           → { ok, pole, plansza, nagrody = {26}, darmowyZa, cena, pol }
		"rzut", platny   → { ok, kostka, z, do, nagroda, wyplacono, nowaPlansza, ...stan } | { ok = false, tekst }
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local POL = 26 -- start + 25 pól; ostatnie to złota gwiazda
local DARMOWY_CO = 60 -- s (próba; docelowo np. 4 h — do ustalenia)
local CENA_START, CENA_KROK, CENA_MAKS = 50, 1.6, 2000
local LIMIT = 0.6 -- s między zapytaniami
local ZASIEG = 18 -- studów od punktu E mistrza gier

local zdalne = RS:FindFirstChild("MistrzGier") :: RemoteFunction?
if not zdalne then
	local f = Instance.new("RemoteFunction")
	f.Name = "MistrzGier"
	f.Parent = RS
	zdalne = f
end
local F = zdalne :: RemoteFunction

type Stan = { nastepnyDarmowy: number, platnych: number, ostatnie: number }
local stany: { [Player]: Stan } = {}
local los = Random.new()

local function stan(gracz: Player): Stan
	local s = stany[gracz]
	if not s then
		s = { nastepnyDarmowy = 0, platnych = 0, ostatnie = 0 }
		stany[gracz] = s
		if gracz:GetAttribute("MistrzPole") == nil then
			gracz:SetAttribute("MistrzPole", 1)
		end
		if gracz:GetAttribute("MistrzPlansza") == nil then
			gracz:SetAttribute("MistrzPlansza", 1)
		end
	end
	return s
end

local function nagroda(plansza: number, pole: number): number
	local mn = 1.5 ^ (plansza - 1)
	if pole >= POL then
		return math.floor(300 * mn + 0.5)
	end
	return math.floor((10 + 6 * pole) * mn + 0.5)
end

local function nagrody(plansza: number): { number }
	local t = {}
	for i = 1, POL do
		t[i] = if i == 1 then 0 else nagroda(plansza, i)
	end
	return t
end

local function cena(s: Stan): number
	return math.min(CENA_MAKS, math.floor(CENA_START * CENA_KROK ^ s.platnych + 0.5))
end

local function sygnal(nazwa: string): BindableFunction?
	local k = workspace:FindFirstChild("StanGracza")
	local sy = k and k:FindFirstChild("Sygnaly")
	local f = sy and sy:FindFirstChild(nazwa)
	return if f and f:IsA("BindableFunction") then f else nil
end

local function przyMistrzu(gracz: Player): boolean
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart") :: BasePart?
	local gra = workspace:FindFirstChild("MiasteczkoBazarGra")
	local punkt = gra and gra:FindFirstChild("Punkty")
	local e = punkt and punkt:FindFirstChild("E mistrz_gier")
	if not hrp then
		return false
	end
	if not (e and e:IsA("BasePart")) then
		return true -- bez punktu E (inny układ mapy) nie blokujemy próby
	end
	local d = hrp.Position - e.Position
	return Vector3.new(d.X, 0, d.Z).Magnitude <= ZASIEG
end

local function widok(gracz: Player, s: Stan)
	local plansza = gracz:GetAttribute("MistrzPlansza") or 1
	return { ok = true, pole = gracz:GetAttribute("MistrzPole") or 1, plansza = plansza, nagrody = nagrody(plansza),
		darmowyZa = math.max(0, math.ceil(s.nastepnyDarmowy - os.clock())), cena = cena(s), pol = POL,
		stanGracza = sygnal("SterowanieSerwera") ~= nil }
end

local function rzut(gracz: Player, platny: boolean)
	local s = stan(gracz)
	if not przyMistrzu(gracz) then
		return { ok = false, tekst = "Podejdź do mistrza gier" }
	end
	local darmowy = os.clock() >= s.nastepnyDarmowy
	local zaplacono = 0
	if not darmowy then
		if not platny then
			return { ok = false, tekst = "Darmowy rzut jeszcze się ładuje" }
		end
		local wyd = sygnal("WydajZloto")
		if not wyd then
			return { ok = false, tekst = "Płatne rzuty działają ze stanem gracza (Karol)" }
		end
		local c = cena(s)
		local okW, w = pcall(function()
			return wyd:Invoke(gracz, { ile = c, zrodlo = "MistrzGier", cel = "rzut" })
		end)
		if not okW or type(w) ~= "table" or not w.ok then
			local powod = if okW and type(w) == "table" then tostring(w.powod) else "blad"
			if powod == "za_malo" then
				return { ok = false, tekst = string.format("Brakuje %d Rybek", (w :: any).brakuje or c) }
			elseif powod == "zle_zrodlo" then
				return { ok = false, tekst = "Płatne rzuty czekają na podpięcie u Karola (źródło MistrzGier)" }
			end
			return { ok = false, tekst = "Nie udało się zapłacić (" .. powod .. ")" }
		end
		zaplacono = c
		s.platnych += 1
	else
		s.nastepnyDarmowy = os.clock() + DARMOWY_CO
		s.platnych = 0
	end
	local plansza = gracz:GetAttribute("MistrzPlansza") or 1
	local z = gracz:GetAttribute("MistrzPole") or 1
	local kostka = los:NextInteger(1, 6)
	local na = math.min(POL, z + kostka)
	local ile = nagroda(plansza, na)
	local wyplacono = false
	local przyznaj = sygnal("SterowanieSerwera")
	if przyznaj and ile > 0 then
		local okP, w = pcall(function()
			return przyznaj:Invoke("przyznaj", gracz, { zloto = ile, doswiadczenie = 0, tokeny_krainy = 0, kraina = "" })
		end)
		wyplacono = okP and type(w) == "table" and w.ok == true
	end
	local nowaPlansza = false
	if na >= POL then
		nowaPlansza = true
		gracz:SetAttribute("MistrzPlansza", plansza + 1)
		gracz:SetAttribute("MistrzPole", 1)
	else
		gracz:SetAttribute("MistrzPole", na)
	end
	local w = widok(gracz, s) :: any
	w.kostka, w.z, w.na, w.nagroda, w.wyplacono, w.nowaPlansza, w.zaplacono = kostka, z, na, ile, wyplacono, nowaPlansza,
		zaplacono
	w.planszaRzutu = plansza
	return w
end

F.OnServerInvoke = function(gracz: Player, akcja: any, arg: any)
	local s = stan(gracz)
	local t = os.clock()
	if t - s.ostatnie < LIMIT then
		return { ok = false, tekst = "Za szybko" }
	end
	s.ostatnie = t
	if akcja == "stan" then
		return widok(gracz, s)
	elseif akcja == "rzut" then
		local ok, w = pcall(rzut, gracz, arg == true)
		if ok then
			return w
		end
		warn("[MistrzGier] " .. tostring(w))
		return { ok = false, tekst = "Błąd planszy" }
	end
	return { ok = false, tekst = "?" }
end

Players.PlayerRemoving:Connect(function(g)
	stany[g] = nil
end)
