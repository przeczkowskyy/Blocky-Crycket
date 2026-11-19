--[[
	SerwerTreningu — serwerowa połowa próby Training Center (Script, RunContext = Server, w kontenerze
	Workspace/TreningProba; budowa: swiat/trening_proba/zbuduj.py). Działa tylko w Roblox Studio: poza Studio usuwa
	cały kontener, jak pozostałe prototypy (MiasteczkoBazarGra, LasPasGra, TeleportChmury).

	SERWER DECYDUJE O PRZYROSTACH. Klient zgłasza tylko naciśnięcie ("akcja", id rundy, wartość, czas klienta);
	serwer sprawdza (LogikaTreningu): kubełek żetonów na wiadomości i na zgłoszenia w rundzie (spam = odrzucone),
	czas klienta tylko w granicach [teraz − max_opoznienie, teraz + max_wyprzedzenie] (inaczej czas serwera),
	najbliższe nierozstrzygnięte zdarzenie w zasięgu przypisania, okno czasu i kierunek. Pierwsze zgłoszenie
	rozstrzyga zdarzenie; naciśnięcie bez zdarzenia w pobliżu łamie serię. Zdarzenia przepuszczone rozstrzyga pętla
	co tik_s. Sześć mini-gier w czterech rodzajach ocen: okno czasu (Siła, Pancerz, Kondycja „Bieżnia”, Zręczność
	„Kłody”), kolejność run bez okna czasu (Inteligencja „Runy”: naciśnięcia w czasie pokazu pomijane bez kary,
	ponowny pokaz po bezczynności) i tor koszyka w chwili upadku (Szczęście „Koniczyny”: zgłoszenie = ruch koszyka,
	werdykt daje dopiero upadek; koniczyna spada poza tor, na którym koszyk stał, gdy zaczęła spadać — stanie w miejscu
	nic nie daje). Przyrost trafia do ATRYBUTU SESYJNEGO gracza (np. TreningSila; bez DataStore) i do sygnału
	Sygnaly/PrzyrostStatystyki (BindableEvent dla przyszłego modułu statystyk — dziś nikt go nie słucha):
		workspace.TreningProba.Sygnaly.PrzyrostStatystyki.Event:Connect(function(gracz, p)
			-- p = { statystyka = "sila", atrybut = "Strength", atrybutSesji = "TreningSila", przyrost = 2,
			--       sumaSesji = 41, seria = 7, gra = "sila", runda = 3, zrodlo = "TreningProba" }
		end)
	Atrybutów statystyk gracza (Strength, Armor… z src/server/PlayerStatsDefaults) ten pakiet NIE zmienia.

	Wejście: podpowiedź E na własnej tablicy (TablicaWejscia, przy miejscu startu) i w arenie (Akcja = "wybor") →
	klient pokazuje TYMCZASOWY wybór; E przy trenerze w bazarze obsługuje klient (zdarzenie OknoMiejsca).
	"wejdz" sprawdza odległość od tablicy, od podpowiedzi trenera w bazarze (tylko odczyt) albo pobyt w arenie,
	zapamiętuje punkt powrotu (CFrame), przenosi na stanowisko. Wyjście (E przy bramie, przycisk WYJDŹ, Q) wraca
	tam, skąd gracz przyszedł.
	Zdalne/ZdarzeniaTreningu: klient → serwer "wejdz", gra | "start" | "akcja", id, wartosc, tk | "przerwij" |
	"wyjdz"; serwer → klient "wybor", zrodlo | "odmowa", powod, tekst | "przybycie", gra | "runda", dane |
	"wynik", w | "koniec", podsumowanie | "wyjscie", powod.
	Haczyk testowy: Sygnaly/SterowanieSerwera ("stan" | "zgodnosc" | "wejdz", gra, gracz? | "start", gracz? |
	"wyjdz", gracz? | "plan", gracz?).
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneTreningu"))
local L = require(moduly:WaitForChild("LogikaTreningu"))
local zdalne: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaTreningu")
local sygnaly = kontener:WaitForChild("Sygnaly")
local przyrostE: BindableEvent = sygnaly:WaitForChild("PrzyrostStatystyki")
local sterowanie: BindableFunction = sygnaly:WaitForChild("SterowanieSerwera")

local O = D.ochrona
local P = D.prefiks

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

local function teraz()
	return workspace:GetServerTimeNow()
end

local function dolicz(nazwa)
	kontener:SetAttribute(nazwa, (kontener:GetAttribute(nazwa) or 0) + 1)
end

kontener:SetAttribute("SerwerTreninguGotowy", false)
for _, n in { "LicznikWejsc", "LicznikRund", "LicznikTrafien", "LicznikPudel", "LicznikSpamu", "LicznikSygnalow", "LicznikOdmow" } do
	kontener:SetAttribute(n, 0)
end
kontener:SetAttribute("OstatniWynik", "")
kontener:SetAttribute("OstatniaOdmowa", "")

------------------------------------------------------------------ zgodność logiki (te same przypadki co w Pythonie)
local function zgodnosc()
	local ok, n, bledy = L.sprawdzPrzypadki(D)
	local tekst
	if ok then
		tekst = string.format("OK %d/%d", n, n)
	else
		tekst = string.format("BŁĄD %d/%d: %s", n - #bledy, n, tostring(bledy[1]))
		warn(P .. "zgodność logiki: " .. tostring(bledy[1]))
	end
	kontener:SetAttribute("ZgodnoscLogikiTreningu", tekst)
	return tekst
end
zgodnosc()

------------------------------------------------------------------ pomocnicze
local function sciezka(korzen, tekst)
	local o = korzen
	for i, n in string.split(tekst, "/") do
		if o == nil then
			return nil
		end
		if not (i == 1 and n == "Workspace") then
			o = o:FindFirstChild(n)
		end
	end
	return o
end

local function postacGracza(gracz)
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if hrp and hum and hrp:IsA("BasePart") and hum.Health > 0 then
		return postac, hrp, hum
	end
	return nil, nil, nil
end

-- punkty, przy których wolno wybrać mini-grę: własna tablica, trener w bazarze (cudzy kontener — tylko odczyt)
local function punktyWejscia()
	local lista = {}
	local t = sciezka(kontener, D.nazwy.tablica_wejscia)
	if t and t:IsA("BasePart") then
		table.insert(lista, t.Position)
	end
	local bz = workspace:FindFirstChild(D.bazar.kontener)
	local pb = bz and sciezka(bz, D.bazar.podpowiedz)
	if pb and pb:IsA("BasePart") then
		table.insert(lista, pb.Position)
	else
		table.insert(lista, v3(D.bazar.punkt_zapasowy))
	end
	return lista
end

local function odlegloscWejscia(p)
	local najmniej = nil
	for _, q in punktyWejscia() do
		local d = (p - q).Magnitude
		if najmniej == nil or d < najmniej then
			najmniej = d
		end
	end
	return najmniej
end

local function wysokoscKorzenia(hrp, hum)
	if hum.RigType == Enum.HumanoidRigType.R6 then
		return hrp.Size.Y / 2 + 2
	end
	return hum.HipHeight + hrp.Size.Y / 2
end

-- przeniesienie postaci (serwer): wczytanie okolicy, grunt z rzutu promienia, zerowanie prędkości
local function przenies(gracz, cel, patrz)
	local postac, hrp, hum = postacGracza(gracz)
	if not postac then
		return false, "brak_postaci"
	end
	pcall(function()
		gracz:RequestStreamAroundAsync(cel, O.limit_wczytania_s)
	end)
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	par.FilterDescendantsInstances = { postac }
	par.RespectCanCollide = true
	local r = workspace:Raycast(cel + Vector3.new(0, 6, 0), Vector3.new(0, -12, 0), par)
	local y = if r then r.Position.Y else cel.Y
	local p = Vector3.new(cel.X, y + wysokoscKorzenia(hrp, hum), cel.Z)
	local kier = Vector3.new(patrz.X - cel.X, 0, patrz.Z - cel.Z)
	if kier.Magnitude < 0.1 then
		kier = Vector3.new(0, 0, -1)
	end
	postac:PivotTo(CFrame.lookAt(p, p + kier.Unit))
	hrp.AssemblyLinearVelocity = Vector3.zero
	hrp.AssemblyAngularVelocity = Vector3.zero
	return true, "ok"
end

------------------------------------------------------------------ stan graczy (tylko w pamięci serwera)
local gracze = {}

local function stan(gracz)
	local S = gracze[gracz]
	if not S then
		S = L.nowyGracz()
		S.kubelek = L.nowyKubelek(O.wiadomosci_pojemnosc, teraz())
		S.ostatniaPodpowiedz = L.NIGDY
		gracze[gracz] = S
	end
	return S
end

------------------------------------------------------------------ zapis postępu (D-110, 19.11.2026): punkty i paski treningu
-- W (punkty wytrenowane: atrybut st.atrybut_sesji) i pasek każdej mini-gry trzymamy też w profilu StanGracza
-- (Workspace/StanGracza/Sygnaly/DanePakietu, pakiet "trening"), żeby malejący zysk nie wracał do zera po ponownym
-- wejściu. Do końca wczytania profilu (atrybut gracza StanGraczaWczytany = false) nic nie czytamy i nie piszemy, a piszemy
-- dopiero po odczycie (pusty stan nie nadpisze zapisanego). Bez StanGracza — jak dawniej (tylko pamięć serwera).
local ZP = { kontener = "StanGracza", gotowy = "SerwerStanuGotowy", sygnal = "DanePakietu", pakiet = "trening",
	atrybut = "StanGraczaWczytany" }

local function danePakietu()
	local k = workspace:FindFirstChild(ZP.kontener)
	if not k or k:GetAttribute(ZP.gotowy) ~= true then
		return nil
	end
	local s = k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild(ZP.sygnal)
	return if f and f:IsA("BindableFunction") then f else nil
end

local function liczbaOk(v)
	return type(v) == "number" and v == v and v >= 0 and v < math.huge
end

local function wczytajTrening(gracz)
	local f = danePakietu()
	if not f or gracz.Parent ~= Players or gracz:GetAttribute(ZP.atrybut) == false then
		return
	end
	local S = stan(gracz)
	local ok, v = pcall(function()
		return f:Invoke("czytaj", gracz, ZP.pakiet)
	end)
	if not ok then
		return
	end
	S.zProfilu = true
	if type(v) ~= "table" then
		return
	end
	for _, st in D.statystyki do
		local n = if type(v.w) == "table" then v.w[st.atrybut_sesji] else nil
		if liczbaOk(n) and n > (gracz:GetAttribute(st.atrybut_sesji) or 0) then
			gracz:SetAttribute(st.atrybut_sesji, n)
		end
	end
	if type(v.paski) == "table" then
		S.paski = S.paski or {}
		for gra, x in v.paski do
			if type(gra) == "string" and D.gry[gra] ~= nil and liczbaOk(x) then
				S.paski[gra] = x
			end
		end
	end
end

local function zapiszTrening(gracz)
	local S = gracze[gracz]
	if S and not S.zProfilu then
		wczytajTrening(gracz) -- StanGracza pojawił się później niż gracz: najpierw odczyt
	end
	local f = danePakietu()
	if not S or not S.zProfilu or not f or gracz:GetAttribute(ZP.atrybut) == false then
		return
	end
	local w, paski = {}, {}
	for _, st in D.statystyki do
		local n = gracz:GetAttribute(st.atrybut_sesji)
		if liczbaOk(n) and n > 0 then
			w[st.atrybut_sesji] = n
		end
	end
	for gra, x in S.paski or {} do
		if type(gra) == "string" and liczbaOk(x) then
			paski[gra] = x
		end
	end
	local ok, r = pcall(function()
		return f:Invoke("zapisz", gracz, ZP.pakiet, { w = w, paski = paski })
	end)
	if not ok or type(r) ~= "table" or r.ok ~= true then
		warn(P .. "trening w profilu stanu gracza odrzucony: " .. tostring(if ok and type(r) == "table" then r.powod else r))
	end
end

local function odmow(gracz, powod)
	dolicz("LicznikOdmow")
	kontener:SetAttribute("OstatniaOdmowa", gracz.Name .. ":" .. tostring(powod))
	zdalne:FireClient(gracz, "odmowa", powod, D.teksty.odmowa[powod] or D.teksty.odmowa.blad)
	return { ok = false, powod = powod }
end

local function zakoncz(gracz, S, R, przerwana)
	R.koniec = true
	local p = L.podsumowanie(D, R)
	local st = L.statystyka(D, R.gra)
	p.przerwana = przerwana
	p.id = R.id
	p.sesja = gracz:GetAttribute(st.atrybut_sesji) or 0
	S.ostatnia = p
	zdalne:FireClient(gracz, "koniec", p)
	zapiszTrening(gracz) -- pasek po rundzie do profilu (zapis postępu)
end

-- werdykt (trafienie / pudło) → atrybut sesyjny, sygnał dla modułu statystyk, wiadomość do klienta
local function wynik(gracz, R, w)
	if not w.przyjete or w.ruch then
		return -- ruch koszyka (Koniczyny) nie jest werdyktem; werdykt da upadek
	end
	local st = L.statystyka(D, R.gra)
	if w.trafienie then
		dolicz("LicznikTrafien")
	else
		dolicz("LicznikPudel")
	end
	if w.trafienie and w.przyrost > 0 then
		local nowa = (gracz:GetAttribute(st.atrybut_sesji) or 0) + w.przyrost
		gracz:SetAttribute(st.atrybut_sesji, nowa)
		przyrostE:Fire(gracz, {
			statystyka = st.id, atrybut = st.atrybut, atrybutSesji = st.atrybut_sesji, przyrost = w.przyrost,
			sumaSesji = nowa, seria = w.seria, gra = R.gra, runda = R.id, zrodlo = D.kontener,
		})
		dolicz("LicznikSygnalow")
	end
	gracz:SetAttribute("TreningSeria", R.seria)
	local S = gracze[gracz]
	if S then
		S.paski = S.paski or {}
		S.paski[R.gra] = R.pasek
		if w.trafienie and w.przyrost > 0 then
			zapiszTrening(gracz) -- nowy punkt: W i pasek do profilu od razu (wyjście w trakcie rundy go nie zgubi)
		end
	end
	kontener:SetAttribute("OstatniWynik", string.format("%s:%s:%s:%s", gracz.Name, R.gra, tostring(w.nr), w.powod))
	-- Runy: stan sekwencji po werdykcie (klient wyrównuje swoją kopię); Koniczyny: tor upadku
	zdalne:FireClient(gracz, "wynik", {
		id = R.id, nr = w.nr, trafienie = w.trafienie, powod = w.powod, seria = w.seria, przyrost = w.przyrost,
		jednostki = w.jednostki, suma = w.suma, pasek = w.pasek, prog = w.prog, d = w.d, tor = w.tor,
		zaklecie = w.zaklecie, dl = w.dl, poz = w.poz, offset = w.offset, pokazOd = w.pokazOd, pokazDo = w.pokazDo,
		pokazy = w.pokazy, ostatnia = w.ostatnia,
	})
end

------------------------------------------------------------------ wejście, runda, wyjście
local function wejdz(gracz, gra, test)
	local S = stan(gracz)
	local postac, hrp = postacGracza(gracz)
	if not postac then
		return odmow(gracz, "brak_postaci")
	end
	local p = hrp.Position
	local wA = L.wArenie(D, p.X, p.Y, p.Z)
	local odl = if test then 0 else odlegloscWejscia(p)
	local w = L.wejscie(D, gra, S, teraz(), odl, wA)
	if not w.ok then
		return odmow(gracz, w.powod)
	end
	if not wA then
		S.powrot = hrp.CFrame
	end
	local W = D.swiat[gra]
	local stara = S.gra
	S.runda = nil
	S.gra = gra
	local ok, powod = przenies(gracz, v3(W.podest), v3(W.patrz))
	if not ok then
		S.gra = stara
		return odmow(gracz, powod)
	end
	gracz:SetAttribute("TreningGra", gra)
	gracz:SetAttribute("TreningSeria", 0)
	dolicz("LicznikWejsc")
	zdalne:FireClient(gracz, "przybycie", gra)
	return { ok = true, powod = "ok" }
end

local licznikRund = 0

local function startRundy(gracz)
	local S = stan(gracz)
	local w = L.start(D, S, teraz())
	if not w.ok then
		return odmow(gracz, w.powod)
	end
	licznikRund += 1
	local t0 = teraz() + D.runda.odliczanie_s
	local z = L.ziarnoZCzasu(teraz(), licznikRund)
	local plan = L.plan(D, S.gra, z)
	-- pasek treningu tej statystyki: reszta z poprzednich rund (pamięć serwera), W = punkty wytrenowane w tej sesji
	-- (atrybut sesyjny), pula z poziomu gracza (atrybut Level z PlayerStatsDefaults — dziś placeholder)
	local st = L.statystyka(D, S.gra)
	S.paski = S.paski or {}
	local S0 = { pasek = S.paski[S.gra] or 0, W = gracz:GetAttribute(st.atrybut_sesji) or 0, pula = L.pula(D, gracz:GetAttribute("Level")) }
	S.runda = L.nowaRunda(D, S.gra, licznikRund, t0, plan, S0)
	S.runda.ziarno = z
	dolicz("LicznikRund")
	zdalne:FireClient(gracz, "runda", {
		id = licznikRund, gra = S.gra, t0 = t0, dlugosc = D.runda.dlugosc_s, plan = plan, pasek = S0.pasek, W = S0.W, pula = S0.pula,
	})
	return { ok = true, powod = "ok", id = licznikRund }
end

local function pierwszySpawn()
	for _, d in workspace:GetDescendants() do
		if d:IsA("SpawnLocation") and not d:IsDescendantOf(kontener) then
			return d
		end
	end
	return nil
end

local function wyjdz(gracz, powod)
	local S = stan(gracz)
	if S.runda and not S.runda.koniec then
		zakoncz(gracz, S, S.runda, true)
	end
	local cel = S.powrot
	S.gra = nil
	S.powrot = nil
	S.runda = nil
	gracz:SetAttribute("TreningGra", nil)
	gracz:SetAttribute("TreningSeria", nil)
	local postac, hrp = postacGracza(gracz)
	if postac and cel then
		pcall(function()
			gracz:RequestStreamAroundAsync(cel.Position, O.limit_wczytania_s)
		end)
		postac:PivotTo(cel)
		hrp.AssemblyLinearVelocity = Vector3.zero
	elseif postac then
		local sp = pierwszySpawn()
		if sp then
			przenies(gracz, sp.Position, sp.Position + sp.CFrame.LookVector * 10)
		else
			gracz:LoadCharacter()
		end
	end
	zdalne:FireClient(gracz, "wyjscie", powod or "ok")
end

------------------------------------------------------------------ zgłoszenia z klienta
zdalne.OnServerEvent:Connect(function(gracz, rodzaj, a, b, c)
	local S = stan(gracz)
	if not L.kubelek(S.kubelek, teraz(), O.wiadomosci_pojemnosc, O.wiadomosci_na_s) then
		if S.runda and not S.runda.koniec then
			S.runda.spam += 1
		end
		dolicz("LicznikSpamu")
		return
	end
	if rodzaj == "akcja" then
		local R = S.runda
		if type(a) ~= "number" or R == nil or R.koniec or R.id ~= a then
			return
		end
		local w = L.zgloszenie(D, R, b, c, teraz())
		if w.przyjete then
			wynik(gracz, R, w)
		elseif w.powod == "spam" then
			dolicz("LicznikSpamu")
		end
	elseif rodzaj == "wejdz" then
		wejdz(gracz, a, false)
	elseif rodzaj == "start" then
		startRundy(gracz)
	elseif rodzaj == "przerwij" then
		if S.runda and not S.runda.koniec then
			zakoncz(gracz, S, S.runda, true)
		end
	elseif rodzaj == "wyjdz" then
		if S.gra then
			wyjdz(gracz, "przycisk")
		end
	end
end)

-- zdarzenia, których nikt nie odbił w oknie (z zapasem na opóźnienie) i koniec rundy
local nastepnyTik = 0
RunService.Heartbeat:Connect(function()
	local t = teraz()
	if t < nastepnyTik then
		return
	end
	nastepnyTik = t + O.tik_s
	for gracz, S in gracze do
		local R = S.runda
		if R and not R.koniec then
			for _, w in L.przeterminowane(D, R, t) do
				wynik(gracz, R, w)
			end
			if R.koniec then
				zakoncz(gracz, S, R, false)
			end
		end
	end
end)

------------------------------------------------------------------ podpowiedzi E (włączane dopiero w Play)
local function podpowiedz(gracz, pp)
	local S = stan(gracz)
	local t = teraz()
	if t - S.ostatniaPodpowiedz < O.odstep_podpowiedzi_s then
		return
	end
	S.ostatniaPodpowiedz = t
	local postac, hrp = postacGracza(gracz)
	local czesc = pp.Parent
	if not postac or not czesc:IsA("BasePart") then
		return
	end
	if (hrp.Position - czesc.Position).Magnitude > pp.MaxActivationDistance + D.podpowiedz.zapas then
		return
	end
	local a = pp:GetAttribute("Akcja")
	if a == "wybor" then
		if S.runda and not S.runda.koniec then
			odmow(gracz, "trwa_runda")
			return
		end
		zdalne:FireClient(gracz, "wybor", pp:GetAttribute("Zrodlo") or "tablica")
	elseif a == "wyjscie" then
		wyjdz(gracz, "brama")
	end
end

local liczbaPodpowiedzi = 0
for _, pp in kontener:GetDescendants() do
	if pp:IsA("ProximityPrompt") and pp:GetAttribute("Akcja") ~= nil then
		pp.Enabled = true
		liczbaPodpowiedzi += 1
		pp.Triggered:Connect(function(gracz)
			podpowiedz(gracz, pp)
		end)
	end
end
kontener:SetAttribute("Podpowiedzi", liczbaPodpowiedzi)

------------------------------------------------------------------ gracze: wyjście z gry i odrodzenie w trakcie treningu
local function podepnij(gracz)
	-- zapis postępu: początek wczytywania profilu → odczyt jeszcze raz po jego końcu
	gracz:GetAttributeChangedSignal(ZP.atrybut):Connect(function()
		local S = gracze[gracz]
		if S then
			S.zProfilu = false
		end
		if gracz:GetAttribute(ZP.atrybut) ~= false then
			wczytajTrening(gracz)
		end
	end)
	task.spawn(wczytajTrening, gracz)
	gracz.CharacterAdded:Connect(function()
		local S = gracze[gracz]
		if S and S.gra then
			if S.runda and not S.runda.koniec then
				zakoncz(gracz, S, S.runda, true)
			end
			S.gra = nil
			S.powrot = nil
			S.runda = nil
			gracz:SetAttribute("TreningGra", nil)
			zdalne:FireClient(gracz, "wyjscie", "odrodzenie")
		end
	end)
end
for _, g in Players:GetPlayers() do
	podepnij(g)
end
Players.PlayerAdded:Connect(podepnij)
Players.PlayerRemoving:Connect(function(g)
	gracze[g] = nil
end)

------------------------------------------------------------------ haczyk testowy
local function ktory(g)
	if typeof(g) == "Instance" and g:IsA("Player") then
		return g
	end
	return Players:GetPlayers()[1]
end

sterowanie.OnInvoke = function(polecenie, a, b)
	if polecenie == "stan" then
		local o = {
			gotowy = kontener:GetAttribute("SerwerTreninguGotowy"), zgodnosc = kontener:GetAttribute("ZgodnoscLogikiTreningu"),
			podpowiedzi = liczbaPodpowiedzi, gracze = {},
		}
		for g, S in gracze do
			local R = S.runda
			local sesja = {}
			for _, st in D.statystyki do
				sesja[st.atrybut_sesji] = g:GetAttribute(st.atrybut_sesji)
			end
			o.gracze[g.Name] = {
				gra = S.gra, powrot = if S.powrot then S.powrot.Position else nil, ostatnia = S.ostatnia, sesja = sesja,
				runda = if R then {
					id = R.id, gra = R.gra, n = #R.plan, trafienia = R.trafienia, pudla = R.pudla, puste = R.puste,
					spam = R.spam, odrzucone = R.odrzucone, seria = R.seria, najdluzsza = R.najdluzsza, suma = R.suma,
					jednostki = R.jednostki, pasek = R.pasek, W = R.W, pula = R.pula, koniec = R.koniec, t0 = R.t0,
					dl = R.dl, poz = R.poz, offset = R.offset, pokazOd = R.pokazOd, pokazDo = R.pokazDo, pokazy = R.pokazy,
					zaklecia = R.zaklecia, ruchy = if R.ruchy then #R.ruchy else nil, zlapane = R.zlapane,
					kamienie = R.kamienie,
				} else nil,
			}
		end
		return o
	elseif polecenie == "zgodnosc" then
		return zgodnosc()
	elseif polecenie == "wejdz" then
		return wejdz(ktory(b), a, true)
	elseif polecenie == "start" then
		return startRundy(ktory(a))
	elseif polecenie == "wyjdz" then
		wyjdz(ktory(a), "haczyk")
		return true
	elseif polecenie == "plan" then
		local S = gracze[ktory(a)]
		return if S and S.runda then S.runda.plan else nil
	end
	return nil
end

kontener:SetAttribute("SerwerTreninguGotowy", true)
