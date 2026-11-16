--[[
	SerwerPasa — serwerowa połowa „lasu-pasa w grze” (Script, RunContext = Server, w kontenerze Workspace/LasPasGra).
	Potworami w przegrodach zajmuje się osobny SerwerPotworow (ten sam kod co w starym lesie, swiat/las_potwory) —
	ten skrypt robi resztę: bramę do Bagna, teleport i Kamień Powrotu, ratunek przed spadnięciem i przelot kamery
	przy pierwszym wejściu (D-077). Wszystko autorytatywnie (D-016): klient tylko pokazuje i zgłasza, że skończył.

	Co robi, po kolei:
		1. strażnik Studio: poza Studio niszczy CAŁY kontener (także potwory i silnik) i kończy;
		2. czeka na mapę Workspace/<DanePasa.mapa.nazwa> (Wygenerowane = true; do 15 s) — bez mapy nic nie robi
		   (StanMapy = "brak_mapy"), a brama w miasteczku dalej prowadzi do starego lasu; TestBezBiomu = true
		   (ten sam atrybut co u potworów) pomija kontrolę;
		3. punkty: przybycie, przed bramą, za bramą (grunt mierzony promieniem w dół), miasteczko (z
		   Workspace/LasTeleport, gdy jest, inaczej z planu); atrybuty PunktPrzybyciaLasu / PatrzPrzybyciaLasu;
		4. przekierowanie bramy w miasteczku: dzisiejszy Workspace/LasTeleport (swiat/biom_las/teleport.py) czyta cel
		   z atrybutów PunktLas / PatrzLas przy każdym E — w trybie Play ustawiamy je na przybycie pasa i oddajemy
		   stare wartości przy usunięciu kontenera (tylko w czasie gry; w trybie Edit nic się nie zmienia). Wyłączenie:
		   atrybut kontenera PrzekierujBrameMiasteczka = false;
		5. Kamień Powrotu (Punkty/KamienPowrotu, podpowiedź E) → miasteczko;
		6. Sygnaly/WynikWalki (BindableEvent, strzela SerwerPotworow przy każdej przyjętej walce): wygrana ze
		   Strażnikiem → PamiecGracza.pokonalStraznikaLasu i atrybut gracza PokonalStraznikaLasu = true;
		7. co OKRES s dla każdego gracza: brama (nieuprawniony za bramą → cofnięcie przed bramę i komunikat), ratunek
		   (spadł poniżej yMin → przybycie / przed / za bramą) i automat przelotu LogikaPasa.krokPrzelotu;
		8. zdalne Zdalne/ZdarzeniaPasa (RemoteEvent): serwer → klient "przygotuj" | "start" | "przerwij" (id) |
		   "komunikat" (napis); klient → serwer "gotowy" | "koniec" (id, ok) | "odmowa" (id) — sprawdzane typy,
		   id bieżącego przelotu i limit wiadomości;
		9. uchwyty: Sygnaly/PrzeniesDoLasu (BindableFunction dla innych skryptów serwera, np. przejścia przez chmury)
		   i Sygnaly/SterowaniePasa (testy).

	Przelot (D-077): przy pierwszym wejściu gracza do lasu (flaga w PamiecGracza, ustawiana NA STARCIE, więc przelot
	nie zapętla się po błędzie) postać zostaje zakotwiczona, dostaje atrybut Stale.ATRYBUT_BLOKADY (SerwerPotworow
	odmawia wtedy walki), serwer prosi o wczytanie mapy wokół trasy (RequestStreamAroundAsync), klient gra lot, a w
	trakcie serwer co sekundę prosi o mapę przed kamerą. Gdy klient nie odpowie w czas + zapas, serwer sam kończy i
	wysyła „przerwij”. Postać i walki wracają zawsze (akcja „odblokuj” w każdej ścieżce wyjścia z automatu).

	Uchwyt dla innych skryptów serwera (np. swiat/teleport_chmury):
		local f = workspace:WaitForChild("LasPasGra"):WaitForChild("Sygnaly"):WaitForChild("PrzeniesDoLasu")
		local w = f:Invoke(gracz, { punkt = "las", przelotPo = 0 })
		-- w = { ok = true, punkt = Vector3, patrz = Vector3 } | { ok = false, powod = "brak_mapy" | "brak_postaci" |
		--     "za_szybko" | "przelot_trwa" | "nieznany_punkt" | "zly_gracz" }
		-- punkt: "las" (Polana Przybycia; domyślnie), "przed_brama", "za_brama" (tylko po pokonaniu Strażnika);
		-- przelotPo: s (0–10) — o ile opóźnić ewentualny pierwszy przelot (gdy wołający ma własną animację kamery)
]]
if not game:GetService("RunService"):IsStudio() then
	-- poza Studio (opublikowane miejsce) pakiet usuwa cały kontener, zanim ktokolwiek dołączy
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local Stale = require(moduly:WaitForChild("Stale"))
local D = require(moduly:WaitForChild("DanePasa"))
local L = require(moduly:WaitForChild("LogikaPasa"))
local Pamiec = require(moduly:WaitForChild("PamiecGracza"))
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaPasa")
local sygnaly = kontener:WaitForChild("Sygnaly")
local przeniesF: BindableFunction = sygnaly:WaitForChild("PrzeniesDoLasu")
local sterowanie: BindableFunction = sygnaly:WaitForChild("SterowaniePasa")
local wynikWalki: BindableEvent = sygnaly:WaitForChild(Stale.SYGNAL_WYNIKU)
local folderPunktow = kontener:WaitForChild("Punkty")

local P = Stale.PREFIKS
local OKRES = 0.25 -- s między tyknięciami bramy, ratunku i przelotu
local ODSTEP_PRZENIESIEN = 2 -- s między przeniesieniami jednego gracza (jak TeleportLasu)
local ODSTEP_KOMUNIKATOW = 3 -- s
local LIMIT_WIADOMOSCI = 10 -- najwyżej tyle wiadomości od klienta na 2 s
local CZEKANIE_NA_MAPE = 15

local function v3(t): Vector3
	return Vector3.new(t[1], t[2], t[3])
end

------------------------------------------------------------------ atrybuty kontenera (start)
kontener:SetAttribute("SerwerPasaGotowy", false)
kontener:SetAttribute("StanMapy", nil)
kontener:SetAttribute("LicznikPrzelotow", 0)
kontener:SetAttribute("LicznikCofniec", 0)
kontener:SetAttribute("LicznikRatunkow", 0)
kontener:SetAttribute("Przekierowanie", "nie")

local function dolicz(nazwa: string)
	kontener:SetAttribute(nazwa, (kontener:GetAttribute(nazwa) or 0) + 1)
end

------------------------------------------------------------------ zgodność logiki (te same 39 przypadków co w Pythonie)
local okLogiki, nLogiki, bledyLogiki = L.sprawdzPrzypadki()
if okLogiki then
	kontener:SetAttribute("ZgodnoscLogikiPasa", string.format("OK %d/%d", nLogiki, nLogiki))
else
	kontener:SetAttribute("ZgodnoscLogikiPasa", string.format("BŁĄD %d/%d: %s", nLogiki - #bledyLogiki, nLogiki, tostring(bledyLogiki[1])))
	warn(P .. "zgodność logiki pasa: " .. tostring(bledyLogiki[1]))
end

------------------------------------------------------------------ mapa
local mapa: Instance? = nil
local stanMapy = "brak_mapy"
if kontener:GetAttribute("TestBezBiomu") == true then
	stanMapy = "test"
	mapa = workspace:FindFirstChild(D.mapa.nazwa)
	warn(P .. "TestBezBiomu = true — las-pas działa bez kontroli mapy " .. D.mapa.nazwa)
else
	local m = workspace:WaitForChild(D.mapa.nazwa, CZEKANIE_NA_MAPE)
	if not m then
		warn(P .. "nie ma Workspace/" .. D.mapa.nazwa .. " (czekano " .. CZEKANIE_NA_MAPE .. " s) — brama, przelot i teleport pasa wyłączone; brama w miasteczku prowadzi do starego lasu")
	elseif m:GetAttribute("Wygenerowane") ~= true then
		warn(P .. D.mapa.nazwa .. " nie ma atrybutu Wygenerowane = true — las-pas wyłączony")
	else
		mapa = m
		stanMapy = "ok"
	end
end
kontener:SetAttribute("StanMapy", stanMapy)
local gotowy = stanMapy ~= "brak_mapy"

------------------------------------------------------------------ punkty (grunt mierzony promieniem w dół)
local function grunt(x: number, z: number, domyslnie: number): number
	local filtr = {}
	if mapa then
		table.insert(filtr, mapa)
	end
	local zaBrama = kontener:FindFirstChild("ZaBrama")
	if zaBrama then
		table.insert(filtr, zaBrama)
	end
	if #filtr == 0 then
		return domyslnie
	end
	-- pas jest płaski (plan: y = 0, wysokość mają tylko rekwizyty): promień z 8 st nad poziomem z danych i tylko po
	-- częściach z kolizją — nie stawiamy gracza na koronie drzewa ani na kuli mgły zapowiedzi Bagna
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Include
	par.FilterDescendantsInstances = filtr
	par.RespectCanCollide = true
	local r = workspace:Raycast(Vector3.new(x, domyslnie + 8, z), Vector3.new(0, -20, 0), par)
	return if r then r.Position.Y else domyslnie
end

local function naGruncie(t, wysokosc: number): Vector3
	return Vector3.new(t[1], grunt(t[1], t[3], t[2]) + wysokosc, t[3])
end

local WYS = D.przybycie.wysokosc
local punkty = {
	las = { punkt = naGruncie(D.przybycie.punkt, WYS), patrz = v3(D.przybycie.patrz) },
	przed_brama = { punkt = naGruncie(D.przedBrama.punkt, WYS), patrz = v3(D.przedBrama.patrz) },
	za_brama = { punkt = naGruncie(D.zaBrama.punkt, WYS), patrz = v3(D.zaBrama.patrz) },
}
punkty.przybycie = punkty.las
kontener:SetAttribute("PunktPrzybyciaLasu", punkty.las.punkt)
kontener:SetAttribute("PatrzPrzybyciaLasu", punkty.las.patrz)

-- miasteczko: punkt zmierzony przez swiat/biom_las/teleport.py (atrybuty LasTeleport) albo z planu + promień w dół
local function punktMiasteczka()
	local t = workspace:FindFirstChild(D.miasteczko.teleport)
	if t then
		local p, q = t:GetAttribute("PunktMiasteczka"), t:GetAttribute("PatrzMiasteczko")
		if typeof(p) == "Vector3" and typeof(q) == "Vector3" then
			return { punkt = p, patrz = q }
		end
	end
	local x, z = D.miasteczko.punkt[1], D.miasteczko.punkt[3]
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	local pomin = { kontener }
	for _, g in Players:GetPlayers() do
		if g.Character then
			table.insert(pomin, g.Character)
		end
	end
	par.FilterDescendantsInstances = pomin
	par.RespectCanCollide = true
	local r = workspace:Raycast(Vector3.new(x, 60, z), Vector3.new(0, -160, 0), par)
	local y = (if r then r.Position.Y else 0) + WYS
	return { punkt = Vector3.new(x, y, z), patrz = Vector3.new(D.miasteczko.patrz[1], y, D.miasteczko.patrz[3]) }
end

------------------------------------------------------------------ przenoszenie postaci (wspólne dla wszystkiego)
local stany: { [Player]: any } = {}

local function stanGracza(gracz: Player)
	local s = stany[gracz]
	if not s then
		s = {
			przelot = L.nowyStanPrzelotu(),
			gotowy = false, -- klient zgłosił, że słucha (wiadomość „gotowy”)
			postac = nil, -- postać, z którą zaczął się przelot
			kotwica = nil, -- { czesc, bylo } — HumanoidRootPart zakotwiczony na czas przelotu
			strumienie = 0, -- ile próśb o wczytanie mapy jeszcze trwa
			koniecId = 0,
			przerwij = nil,
			przenoszenie = false,
			ostatnioPrzeniesiony = -math.huge,
			ostatniKomunikat = -math.huge,
			wiadomosci = {},
		}
		stany[gracz] = s
	end
	return s
end

-- → (ok, powód?)
local function przenies(gracz: Player, cel, wymus: boolean?): (boolean, string?)
	local s = stanGracza(gracz)
	local teraz = os.clock()
	if not wymus then
		if teraz - s.ostatnioPrzeniesiony < ODSTEP_PRZENIESIEN then
			return false, "za_szybko"
		end
		if s.przelot.faza ~= "brak" then
			return false, "przelot_trwa"
		end
	end
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not postac or not hum or hum.Health <= 0 or not hrp or not hrp:IsA("BasePart") then
		return false, "brak_postaci"
	end
	s.ostatnioPrzeniesiony = teraz
	-- okolica celu musi być wczytana u gracza, zanim postać tam stanie (miejsce ma włączony streaming)
	pcall(function()
		gracz:RequestStreamAroundAsync(cel.punkt, 5)
	end)
	if gracz.Character ~= postac or postac.Parent == nil then
		return false, "brak_postaci"
	end
	local punkt: Vector3 = cel.punkt
	local naWprost = Vector3.new(cel.patrz.X, punkt.Y, cel.patrz.Z)
	if (naWprost - punkt).Magnitude < 0.1 then
		naWprost = punkt + Vector3.new(1, 0, 0)
	end
	postac:PivotTo(CFrame.lookAt(punkt, naWprost))
	hrp.AssemblyLinearVelocity = Vector3.zero
	hrp.AssemblyAngularVelocity = Vector3.zero
	return true, nil
end

local function komunikat(gracz: Player, tekst: string)
	local s = stanGracza(gracz)
	local teraz = os.clock()
	if teraz - s.ostatniKomunikat < ODSTEP_KOMUNIKATOW then
		return
	end
	s.ostatniKomunikat = teraz
	zdarzenia:FireClient(gracz, "komunikat", tekst)
end

------------------------------------------------------------------ przekierowanie bramy w miasteczku (tylko w trybie Play)
local przekierowanie = nil

local function przekieruj(): string
	if kontener:GetAttribute("PrzekierujBrameMiasteczka") == false then
		return "wylaczone"
	end
	local t = workspace:WaitForChild(D.miasteczko.teleport, 5)
	if not t then
		return "brak_teleportu"
	end
	if t:GetAttribute("Wygenerowane") ~= true then
		return "obcy_teleport"
	end
	przekierowanie = { teleport = t, punkt = t:GetAttribute("PunktLas"), patrz = t:GetAttribute("PatrzLas") }
	t:SetAttribute("PunktLas", punkty.las.punkt)
	t:SetAttribute("PatrzLas", punkty.las.patrz)
	kontener:SetAttribute("StaryPunktLas", przekierowanie.punkt)
	return "tak"
end

local function oddajPrzekierowanie()
	local p = przekierowanie
	przekierowanie = nil
	if p and p.teleport.Parent then
		p.teleport:SetAttribute("PunktLas", p.punkt)
		p.teleport:SetAttribute("PatrzLas", p.patrz)
	end
end
kontener.Destroying:Connect(oddajPrzekierowanie)

------------------------------------------------------------------ przelot: wykonanie akcji automatu
local function zablokuj(gracz: Player, s)
	local postac = s.postac
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if hrp and hrp:IsA("BasePart") then
		s.kotwica = { czesc = hrp, bylo = hrp.Anchored }
		hrp.AssemblyLinearVelocity = Vector3.zero
		hrp.Anchored = true
	end
	gracz:SetAttribute(Stale.ATRYBUT_BLOKADY, true)
end

local function odblokuj(gracz: Player, s)
	local k = s.kotwica
	s.kotwica = nil
	if k and k.czesc.Parent then
		k.czesc.Anchored = k.bylo
	end
	gracz:SetAttribute(Stale.ATRYBUT_BLOKADY, nil)
	s.strumienie = 0
end

local function laduj(gracz: Player, s)
	local id = s.przelot.id
	s.strumienie = #D.przelot.strumien
	for _, p in D.przelot.strumien do
		task.spawn(function()
			pcall(function()
				gracz:RequestStreamAroundAsync(v3(p), D.przelot.ladowanie)
			end)
			if s.przelot.id == id and s.strumienie > 0 then
				s.strumienie -= 1
			end
		end)
	end
end

local function podtrzymaj(gracz: Player, s, teraz: number)
	local x, y, z = L.punktWyprzedzenia(D.przelot.punkty, teraz - s.przelot.od, D.przelot.wyprzedzenie)
	task.spawn(function()
		pcall(function()
			gracz:RequestStreamAroundAsync(Vector3.new(x, y, z), 2)
		end)
	end)
end

local function ustawWidzial(gracz: Player, wartosc: boolean)
	Pamiec.ustaw(gracz, "widzialPrzelotLasu", wartosc)
	gracz:SetAttribute("WidzialPrzelotLasu", wartosc)
end

local function wykonaj(gracz: Player, s, akcja: string, teraz: number)
	if akcja == "widzial" then
		ustawWidzial(gracz, true)
		dolicz("LicznikPrzelotow")
	elseif akcja == "zapomnij" then
		ustawWidzial(gracz, false)
	elseif akcja == "zablokuj" then
		zablokuj(gracz, s)
	elseif akcja == "przygotuj" then
		zdarzenia:FireClient(gracz, "przygotuj", s.przelot.id)
	elseif akcja == "laduj" then
		laduj(gracz, s)
	elseif akcja == "start" then
		zdarzenia:FireClient(gracz, "start", s.przelot.id)
	elseif akcja == "podtrzymaj" then
		podtrzymaj(gracz, s, teraz)
	elseif akcja == "przerwij" then
		zdarzenia:FireClient(gracz, "przerwij", s.przelot.id)
	elseif akcja == "odblokuj" then
		odblokuj(gracz, s)
	else
		warn(P .. "nieznana akcja przelotu: " .. tostring(akcja))
	end
end

------------------------------------------------------------------ tyknięcie jednego gracza: brama, ratunek, przelot
local function tyknijGracza(gracz: Player, teraz: number)
	local s = stanGracza(gracz)
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local zywa = hrp ~= nil and hrp:IsA("BasePart") and hum ~= nil and hum.Health > 0
	local poz: Vector3? = if zywa and hrp then hrp.Position else nil

	-- 1. brama i ratunek (w czasie przelotu postać stoi zakotwiczona — nic do pilnowania)
	if poz and s.przelot.faza == "brak" and not s.przenoszenie then
		local uprawniony = Pamiec.czytaj(gracz, "pokonalStraznikaLasu")
		local cel = nil
		if L.decyzjaBramy(poz.X, poz.Z, uprawniony, D.brama) == "cofnij" then
			cel = "przed_brama"
			dolicz("LicznikCofniec")
		elseif L.potrzebaRatunku(poz.X, poz.Y, poz.Z, D.ratunek) then
			cel = L.celRatunku(poz.X, poz.Z, uprawniony, D.brama)
			dolicz("LicznikRatunkow")
		end
		if cel then
			s.przenoszenie = true
			task.spawn(function()
				przenies(gracz, punkty[cel], true)
				s.przenoszenie = false
				if cel == "przed_brama" and not uprawniony then
					komunikat(gracz, "Brama do Bagna jest zamknięta — pokonaj Strażnika Gaju.")
				end
			end)
		end
	end

	-- 2. przelot kamery (automat z LogikaPasa; akcje wykonujemy w podanej kolejności)
	if s.przelot.faza == "brak" then
		s.postac = postac
	end
	local w = {
		widzial = Pamiec.czytaj(gracz, "widzialPrzelotLasu"),
		wPasie = poz ~= nil and L.wProstokacie(poz.X, poz.Z, D.wejscie) and poz.Y > D.ratunek.yMin,
		gotowy = s.gotowy,
		postac = zywa and postac == s.postac,
		strumienie = s.strumienie,
		koniec = s.przelot.id > 0 and s.koniecId == s.przelot.id,
		przerwij = s.przerwij,
	}
	s.przerwij = nil
	for _, akcja in L.krokPrzelotu(s.przelot, w, teraz, D.przelot) do
		wykonaj(gracz, s, akcja, teraz)
	end
end

------------------------------------------------------------------ wynik walki ze Strażnikiem → brama otwarta dla zwycięzcy
local function ustawPokonal(gracz: Player, wartosc: boolean)
	Pamiec.ustaw(gracz, "pokonalStraznikaLasu", wartosc)
	gracz:SetAttribute("PokonalStraznikaLasu", wartosc)
end

wynikWalki.Event:Connect(function(gracz: any, info: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or not L.otwieraBrame(info) then
		return
	end
	if not Pamiec.czytaj(gracz, "pokonalStraznikaLasu") then
		ustawPokonal(gracz, true)
		print(P .. gracz.Name .. " pokonał Strażnika Gaju — brama do Bagna otwarta dla niego")
	end
end)

------------------------------------------------------------------ wiadomości od klienta (D-016: tylko zgłoszenia, bez liczb gry)
zdarzenia.OnServerEvent:Connect(function(gracz: Player, polecenie: any, id: any, _ok: any)
	local s = stanGracza(gracz)
	local teraz = os.clock()
	-- limit: najwyżej LIMIT_WIADOMOSCI w ostatnich 2 s (reszta przepada po cichu)
	local swieze = {}
	for _, t in s.wiadomosci do
		if teraz - t < 2 then
			table.insert(swieze, t)
		end
	end
	if #swieze >= LIMIT_WIADOMOSCI then
		s.wiadomosci = swieze
		return
	end
	table.insert(swieze, teraz)
	s.wiadomosci = swieze
	if type(polecenie) ~= "string" then
		return
	end
	if polecenie == "gotowy" then
		s.gotowy = true
		return
	end
	if type(id) ~= "number" or id ~= s.przelot.id or s.przelot.id <= 0 then
		return -- stary albo cudzy przelot
	end
	if polecenie == "koniec" then
		if s.przelot.faza == "trwa" then
			s.koniecId = id
		elseif s.przelot.faza ~= "brak" then
			s.przerwij = "klient" -- klient skończył przed startem lotu (błąd po jego stronie)
		end
	elseif polecenie == "odmowa" then
		if s.przelot.faza ~= "brak" then
			s.przerwij = "odmowa" -- np. trwa walka: przelot spróbuje ponownie po D.przelot.ponowPoOdmowie s
		end
	end
end)

------------------------------------------------------------------ gracze
local function nowyGracz(gracz: Player)
	Pamiec.wczytaj(gracz)
	stanGracza(gracz)
	gracz:SetAttribute("WidzialPrzelotLasu", Pamiec.czytaj(gracz, "widzialPrzelotLasu"))
	gracz:SetAttribute("PokonalStraznikaLasu", Pamiec.czytaj(gracz, "pokonalStraznikaLasu"))
end
Players.PlayerAdded:Connect(nowyGracz)
for _, g in Players:GetPlayers() do
	nowyGracz(g)
end
Players.PlayerRemoving:Connect(function(gracz: Player)
	stany[gracz] = nil -- pamięć (przelot, brama) zostaje w PamiecGracza
end)

------------------------------------------------------------------ uchwyt dla innych skryptów serwera
local PUNKTY_UCHWYTU = { las = true, przed_brama = true, za_brama = true }

local function przeniesDoLasu(gracz: any, opcje: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") then
		return { ok = false, powod = "zly_gracz" }
	end
	if not gotowy then
		return { ok = false, powod = "brak_mapy" }
	end
	local nazwa, po = "las", 0
	if type(opcje) == "table" then
		if type(opcje.punkt) == "string" then
			nazwa = opcje.punkt
		end
		if type(opcje.przelotPo) == "number" and opcje.przelotPo == opcje.przelotPo then
			po = math.clamp(opcje.przelotPo, 0, 10)
		end
	end
	if not PUNKTY_UCHWYTU[nazwa] or (nazwa == "za_brama" and not Pamiec.czytaj(gracz, "pokonalStraznikaLasu")) then
		return { ok = false, powod = "nieznany_punkt" }
	end
	local s = stanGracza(gracz)
	if po > 0 then
		s.przelot.wolnyOd = math.max(s.przelot.wolnyOd, os.clock() + po)
	end
	local cel = punkty[nazwa]
	local ok, powod = przenies(gracz, cel, false)
	if not ok then
		return { ok = false, powod = powod }
	end
	return { ok = true, punkt = cel.punkt, patrz = cel.patrz }
end
przeniesF.OnInvoke = przeniesDoLasu

------------------------------------------------------------------ Kamień Powrotu → miasteczko
do
	local kamien = folderPunktow:WaitForChild("KamienPowrotu", 5)
	local podp = kamien and kamien:FindFirstChildOfClass("ProximityPrompt")
	if podp then
		podp.Enabled = gotowy
		podp.Triggered:Connect(function(gracz: Player)
			if gotowy then
				task.spawn(przenies, gracz, punktMiasteczka(), false)
			end
		end)
	else
		warn(P .. "brak Punkty/KamienPowrotu z podpowiedzią — powrót do miasteczka tylko przez uchwyt testowy")
	end
end

------------------------------------------------------------------ pomiar kosztu (tylko testy)
local koszt = { 0, 0, 0 } -- suma, n, maks (s)
local kosztOd = os.clock()

------------------------------------------------------------------ uchwyt testowy (tylko Studio)
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
	local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
	local poz = if hrp and hrp:IsA("BasePart") then hrp.Position else nil
	return {
		pamiec = Pamiec.opis(gracz),
		faza = s.przelot.faza,
		id = s.przelot.id,
		gotowy = s.gotowy,
		zablokowany = s.kotwica ~= nil,
		blokadaWalki = gracz:GetAttribute(Stale.ATRYBUT_BLOKADY) == true,
		wPasie = poz ~= nil and L.wProstokacie(poz.X, poz.Z, D.wejscie),
		zaBrama = poz ~= nil and L.zaBrama(poz.X, poz.Z, D.brama),
		pozycja = poz,
	}
end

sterowanie.OnInvoke = function(polecenie: any, a: any, b: any)
	if polecenie == "stan" then
		local gracze = {}
		for _, g in Players:GetPlayers() do
			gracze[g.Name] = opisGracza(g)
		end
		return { gotowy = gotowy, stanMapy = stanMapy, przekierowanie = kontener:GetAttribute("Przekierowanie"),
			punktLas = punkty.las.punkt, gracze = gracze }
	elseif polecenie == "gracz" then
		local g = znajdzGracza(a)
		return if g then opisGracza(g) else nil
	elseif polecenie == "odtworzPrzelot" or polecenie == "zapomnijPrzelot" then
		local g = znajdzGracza(a)
		if not g then
			return false
		end
		local s = stanGracza(g)
		if s.przelot.faza == "brak" then
			ustawWidzial(g, false)
			s.przelot.wolnyOd = 0
			if polecenie == "zapomnijPrzelot" then
				s.przelot.wolnyOd = math.huge -- nie startuj sam, póki test nie zawoła odtworzPrzelot
			end
		else
			s.przerwij = "reset"
		end
		return true
	elseif polecenie == "otworzBrame" or polecenie == "zamknijBrame" then
		local g = znajdzGracza(a)
		if not g then
			return false
		end
		ustawPokonal(g, polecenie == "otworzBrame")
		return true
	elseif polecenie == "przenies" then
		local g = znajdzGracza(a)
		if not g then
			return { ok = false, powod = "zly_gracz" }
		end
		if b == "miasteczko" then
			local ok, powod = przenies(g, punktMiasteczka(), true)
			return { ok = ok, powod = powod }
		end
		local cel = punkty[b or "las"]
		if not cel then
			return { ok = false, powod = "nieznany_punkt" }
		end
		local ok, powod = przenies(g, cel, true)
		return { ok = ok, powod = powod }
	elseif polecenie == "koszt" then
		local okno = os.clock() - kosztOd
		local wynik = { okno = okno, sr = if koszt[2] > 0 then koszt[1] / koszt[2] * 1000 else 0, maks = koszt[3] * 1000,
			n = koszt[2], naSekunde = if okno > 0 then koszt[1] * 1000 / okno else 0 }
		if a == true then
			koszt = { 0, 0, 0 }
			kosztOd = os.clock()
		end
		return wynik
	elseif polecenie == "zgodnosc" then
		local ok, n, bledy = L.sprawdzPrzypadki()
		return { ok = ok, n = n, bledy = bledy }
	end
	warn(P .. "SterowaniePasa: nieznane polecenie " .. tostring(polecenie))
	return nil
end

------------------------------------------------------------------ start
if not gotowy then
	return -- bez mapy: uchwyty odpowiadają (brak_mapy), brama w miasteczku zostaje jak była
end

kontener:SetAttribute("Przekierowanie", przekieruj())

task.spawn(function()
	local bledyZRzedu = 0
	while kontener.Parent do
		task.wait(OKRES)
		local t0 = os.clock()
		local teraz = os.clock()
		for _, gracz in Players:GetPlayers() do
			local udalo, blad = xpcall(tyknijGracza, debug.traceback, gracz, teraz)
			if udalo then
				bledyZRzedu = 0
			else
				bledyZRzedu += 1
				warn(P .. "błąd w tyknięciu gracza " .. gracz.Name .. ": " .. tostring(blad))
				local s = stany[gracz]
				if s then
					-- sprzątanie po błędzie: postać i walki wracają zawsze
					pcall(odblokuj, gracz, s)
					s.przelot.faza = "brak"
				end
			end
		end
		local dt = os.clock() - t0
		koszt[1] += dt
		koszt[2] += 1
		koszt[3] = math.max(koszt[3], dt)
		if bledyZRzedu >= 20 then
			warn(P .. "pętla pasa zatrzymana po 20 błędach z rzędu — brama i przelot wyłączone")
			kontener:SetAttribute("SerwerPasaGotowy", false)
			for g, s in stany do
				pcall(odblokuj, g, s)
			end
			break
		end
	end
end)

kontener:SetAttribute("SerwerPasaGotowy", true)
print(string.format("%sserwer pasa gotowy: mapa %s, przekierowanie bramy miasteczka: %s, przybycie (%.1f, %.1f, %.1f), zgodność logiki %d/%d",
	P, stanMapy, tostring(kontener:GetAttribute("Przekierowanie")), punkty.las.punkt.X, punkty.las.punkt.Y, punkty.las.punkt.Z,
	nLogiki - #bledyLogiki, nLogiki))
