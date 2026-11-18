--[[
	SerwerCutscenki — serwerowa połowa cutscenki biomu (D-077; Script, RunContext = Server, w kontenerze
	Workspace/CutscenkaBiomu). Serwer decyduje, KIEDY i KOMU cutscenka gra (D-016); klient tylko pokazuje i zgłasza.

	Co robi:
		1. strażnik Studio: poza Studio niszczy cały kontener i kończy;
		2. dla każdego biomu z DaneCutscenki.biomy czeka na kontener gry biomu (LasPasGra, BagnoPasGra, DzunglaPasGra)
		   i jego mapę. Biom przejmuje tylko wtedy, gdy serwer pasa ogłosił, że ustąpi (atrybut kontenera gry
		   DaneCutscenki.ustepuje = true — mały haczyk w swiat/las_pas_gra/zrodla/SerwerPasa.server.luau); wtedy
		   ustawia na WŁASNYM kontenerze atrybut „Przejmuje_<id biomu>” = true i stary przelot pasa nie startuje.
		   Bez haczyka albo bez biomu: StanBiomu_<id> mówi dlaczego, a biom zostaje przy starym przelocie;
		3. co `okres` s dla każdego gracza: biom, w którym stoi (prostokąt wejścia, wysokość, prawo wejścia), czy już
		   widział, i krok automatu LogikaCutscenki.krok; akcje automatu wykonuje w podanej kolejności;
		4. pamięć „widział”: tabela według UserId (przeżywa odrodzenie i ponowne wejście na ten sam serwer) oraz atrybut
		   gracza o nazwie z pakietu biomu (WidzialPrzelotLasu / Bagna / Dzungli) — te atrybuty zapis postępu
		   (swiat/stan_gracza, WYŁĄCZONY) ma już na liście; gdy ktoś go włączy, wartość z poprzedniej sesji wraca jako
		   atrybut i cutscenka nie gra drugi raz. Ten skrypt zapisu nie włącza i niczego nie zapisuje sam;
		5. na czas cutscenki: postać zakotwiczona (HumanoidRootPart, stan sprzed wraca), atrybut gracza
		   DaneCutscenki.blokada (SerwerPotworow odmawia wtedy walki), mapa wczytywana wzdłuż trasy
		   (RequestStreamAroundAsync) i co sekundę przed kamerą. Odblokowanie w KAŻDEJ ścieżce wyjścia z automatu,
		   przy błędzie tyknięcia i przy usunięciu kontenera;
		6. zdalne Zdalne/ZdarzeniaCutscenki: serwer → klient "pytaj" (id, biom) | "start" (id) | "przerwij" (id);
		   klient → serwer "gotowy" | "gotowe" (id) | "odmowa" (id, powód) | "koniec" (id, pominięta) — sprawdzane typy,
		   id bieżącej cutscenki i limit wiadomości. Cutscenkę dostaje tylko gracz, który wszedł (FireClient);
		7. uchwyt Sygnaly/SterowanieCutscenki (BindableFunction, serwer): "stan" | "gracz", kto | "odtworz", kto, biom |
		   "zapomnij", kto, biom? | "oznacz", kto, biom. Dla ludzi bez kodu: atrybut kontenera Odtworz = "las" |
		   "bagno" | "dzungla" ustawiony w widoku serwera odtwarza cutscenkę wszystkim graczom i sam się czyści.
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneCutscenki"))
local L = require(moduly:WaitForChild("LogikaCutscenki"))
local zdarzenia = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaCutscenki")
local sygnaly = kontener:WaitForChild("Sygnaly")
local sterowanie = sygnaly:WaitForChild("SterowanieCutscenki")

local P = "[CutscenkaBiomu] "
local K = D.serwer

kontener:SetAttribute("SerwerGotowy", false)
kontener:SetAttribute("LicznikCutscenek", 0)
kontener:SetAttribute("LicznikPominiec", 0)
kontener:SetAttribute("LicznikOdmow", 0)
kontener:SetAttribute("Odtworz", "")

local function dolicz(nazwa)
	kontener:SetAttribute(nazwa, (kontener:GetAttribute(nazwa) or 0) + 1)
end

local okLogiki, nLogiki, bledyLogiki = L.sprawdzPrzypadki()
kontener:SetAttribute("ZgodnoscLogiki", if okLogiki then string.format("OK %d/%d", nLogiki, nLogiki)
	else string.format("BŁĄD %d/%d: %s", nLogiki - #bledyLogiki, nLogiki, tostring(bledyLogiki[1])))
if not okLogiki then
	warn(P .. "zgodność logiki: " .. tostring(bledyLogiki[1]))
end

------------------------------------------------------------------ biomy: które przejmujemy
local biomWedlugId = {}
local aktywne = {} -- [id biomu] = true, gdy cutscenkę tego biomu gra ten pakiet
for _, b in D.biomy do
	biomWedlugId[b.id] = b
	kontener:SetAttribute("StanBiomu_" .. b.id, "czeka")
end

local function przejmij(b)
	local gra = workspace:WaitForChild(b.kontenerGry, K.czekanieNaBiom)
	local mapa = workspace:FindFirstChild(b.mapa)
	if not gra or not mapa or mapa:GetAttribute("Wygenerowane") ~= true then
		kontener:SetAttribute("StanBiomu_" .. b.id, "brak_biomu")
		return
	end
	local t0 = os.clock()
	while gra:GetAttribute(D.ustepuje) ~= true and os.clock() - t0 < K.czekanieNaBiom do
		task.wait(0.5)
	end
	if gra:GetAttribute(D.ustepuje) ~= true then
		kontener:SetAttribute("StanBiomu_" .. b.id, "brak_haczyka")
		warn(P .. b.kontenerGry .. " nie ogłosił atrybutu " .. D.ustepuje .. " — biom " .. b.id .. " zostaje przy starym przelocie (wgraj skrypty pasa z haczykiem)")
		return
	end
	aktywne[b.id] = true
	kontener:SetAttribute(D.przejecie .. b.id, true)
	kontener:SetAttribute("StanBiomu_" .. b.id, "przejety")
end

------------------------------------------------------------------ pamięć „widział”
local pamiec = {} -- [UserId] = { [id biomu] = true }

local function zapisAktywny()
	local stan = workspace:FindFirstChild(D.zapis.kontener)
	return stan ~= nil and stan:GetAttribute(D.zapis.atrybut) == true
end

local function widzial(gracz, b)
	local w = pamiec[gracz.UserId]
	if w ~= nil and w[b.id] == true then
		return true
	end
	-- zapis postępu (wyłączony): gdy działa, stan z poprzedniej sesji wraca jako atrybut gracza
	return zapisAktywny() and gracz:GetAttribute(b.atrybut) == true
end

local function ustawWidzial(gracz, b, wartosc)
	local w = pamiec[gracz.UserId]
	if not w then
		w = {}
		pamiec[gracz.UserId] = w
	end
	w[b.id] = if wartosc then true else nil
	gracz:SetAttribute(b.atrybut, wartosc)
end

------------------------------------------------------------------ stan graczy
local stany = {}

local function stanGracza(gracz)
	local s = stany[gracz]
	if not s then
		s = { automat = L.nowyStan(), gotowy = false, postac = nil, kotwica = nil, blokada = false, strumienie = 0,
			odpowiedz = nil, koniec = false, pominieta = false, przerwij = nil, wymus = nil, wiadomosci = {},
			ostatnia = nil }
		stany[gracz] = s
	end
	return s
end

local function odblokuj(gracz, s)
	local k = s.kotwica
	s.kotwica = nil
	if k and k.czesc.Parent then
		k.czesc.Anchored = k.bylo
	end
	if s.blokada then
		s.blokada = false
		if gracz.Parent then
			gracz:SetAttribute(D.blokada, nil)
		end
	end
	s.strumienie = 0
end

local function zakotwicz(s)
	local hrp = s.postac and s.postac:FindFirstChild("HumanoidRootPart")
	if hrp and hrp:IsA("BasePart") and not s.kotwica then
		s.kotwica = { czesc = hrp, bylo = hrp.Anchored }
		hrp.AssemblyLinearVelocity = Vector3.zero
		hrp.AssemblyAngularVelocity = Vector3.zero
		hrp.Anchored = true
	end
end

local function laduj(gracz, s, b)
	local id = s.automat.id
	s.strumienie = #b.strumien
	for _, p in b.strumien do
		task.spawn(function()
			pcall(function()
				gracz:RequestStreamAroundAsync(Vector3.new(p[1], p[2], p[3]), K.ladowanie)
			end)
			if s.automat.id == id and s.strumienie > 0 then
				s.strumienie -= 1
			end
		end)
	end
end

local function podtrzymaj(gracz, s, b, teraz)
	local t = math.min(b.trasa.czas, teraz - s.automat.od + K.wyprzedzenie)
	local x, _, z = L.krzywa(b.trasa.poz, b.trasa.n, b.trasa.krok, t)
	task.spawn(function()
		pcall(function()
			gracz:RequestStreamAroundAsync(Vector3.new(x, 0, z), 2)
		end)
	end)
end

local function wykonaj(gracz, s, akcja, teraz)
	local b = biomWedlugId[s.automat.biom]
	if akcja == "blokuj_walke" then
		s.blokada = true
		gracz:SetAttribute(D.blokada, true)
	elseif akcja == "pytaj" then
		zdarzenia:FireClient(gracz, "pytaj", s.automat.id, s.automat.biom)
	elseif akcja == "widzial" or akcja == "poddaj" then
		if b then
			ustawWidzial(gracz, b, true)
		end
		if akcja == "widzial" then
			dolicz("LicznikCutscenek")
		end
	elseif akcja == "zakotwicz" then
		zakotwicz(s)
	elseif akcja == "laduj" then
		if b then
			laduj(gracz, s, b)
		end
	elseif akcja == "start" then
		zdarzenia:FireClient(gracz, "start", s.automat.id)
	elseif akcja == "podtrzymaj" then
		if b then
			podtrzymaj(gracz, s, b, teraz)
		end
	elseif akcja == "przerwij" then
		zdarzenia:FireClient(gracz, "przerwij", s.automat.id)
	elseif akcja == "odblokuj" then
		odblokuj(gracz, s)
		s.ostatnia = { id = s.automat.id, biom = s.automat.biom, wynik = s.automat.wynik }
		if s.automat.wynik == "pominieta" then
			dolicz("LicznikPominiec")
		elseif s.automat.wynik == "odmowa" then
			dolicz("LicznikOdmow")
		end
	else
		warn(P .. "nieznana akcja: " .. tostring(akcja))
	end
end

local function tyknijGracza(gracz, teraz)
	local s = stanGracza(gracz)
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local zywa = hrp ~= nil and hrp:IsA("BasePart") and hum ~= nil and hum.Health > 0
	if s.automat.faza == "brak" then
		s.postac = postac
	end
	local cel = nil
	if zywa and s.gotowy then
		local poz = hrp.Position
		local nr = L.biomPunktu(D.biomy, poz.X, poz.Y, poz.Z)
		local b = D.biomy[nr]
		if b and aktywne[b.id] and not widzial(gracz, b) and (b.wymaganie == nil or gracz:GetAttribute(b.wymaganie) == true) then
			cel = b.id
		end
	end
	local wymus = nil
	if s.wymus ~= nil and s.gotowy then
		wymus = s.wymus
	end
	local b = biomWedlugId[s.automat.biom]
	local wejscie = {
		cel = cel,
		wymus = wymus,
		postac = zywa and postac == s.postac,
		odpowiedz = s.odpowiedz,
		strumienie = s.strumienie,
		czas = if b then b.trasa.czas else 0,
		koniec = s.koniec,
		pominieta = s.pominieta,
		przerwij = s.przerwij,
	}
	s.odpowiedz = nil
	s.koniec = false
	s.pominieta = false
	s.przerwij = nil
	local bylaFaza = s.automat.faza
	local akcje = L.krok(s.automat, wejscie, teraz, K)
	if bylaFaza == "brak" and s.automat.faza ~= "brak" then
		s.wymus = nil -- życzenie odtworzenia zużyte
	end
	for _, akcja in akcje do
		wykonaj(gracz, s, akcja, teraz)
	end
end

------------------------------------------------------------------ wiadomości od klienta (tylko zgłoszenia)
zdarzenia.OnServerEvent:Connect(function(gracz, polecenie, id, dodatek)
	local s = stanGracza(gracz)
	local teraz = os.clock()
	local swieze = {}
	for _, t in s.wiadomosci do
		if teraz - t < 2 then
			table.insert(swieze, t)
		end
	end
	if #swieze >= K.limitWiadomosci then
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
	if type(id) ~= "number" or id ~= s.automat.id or id <= 0 then
		return -- stara albo cudza cutscenka
	end
	local faza = s.automat.faza
	if polecenie == "gotowe" then
		if faza == "pyta" then
			s.odpowiedz = "gotowe"
		end
	elseif polecenie == "odmowa" then
		if faza == "pyta" then
			s.odpowiedz = "odmowa"
		elseif faza ~= "brak" then
			s.przerwij = "klient"
		end
	elseif polecenie == "koniec" then
		if faza == "trwa" then
			s.koniec = true
			s.pominieta = dodatek == true and D.oprawa.pomijanie.wlaczone == true
				and kontener:GetAttribute(D.oprawa.pomijanie.atrybut) ~= false
		elseif faza ~= "brak" then
			s.przerwij = "klient" -- klient skończył przed startem (błąd albo śmierć postaci po jego stronie)
		end
	end
end)

------------------------------------------------------------------ gracze
local function nowyGracz(gracz)
	stanGracza(gracz)
end
Players.PlayerAdded:Connect(nowyGracz)
for _, g in Players:GetPlayers() do
	nowyGracz(g)
end
Players.PlayerRemoving:Connect(function(gracz)
	local s = stany[gracz]
	if s then
		pcall(odblokuj, gracz, s)
	end
	stany[gracz] = nil -- pamięć „widział” zostaje w tabeli według UserId
end)

------------------------------------------------------------------ uchwyt (testy i ludzie)
local function znajdzGracza(a)
	if typeof(a) == "Instance" and a:IsA("Player") then
		return a
	elseif type(a) == "string" then
		local g = Players:FindFirstChild(a)
		return if g and g:IsA("Player") then g else nil
	end
	return Players:GetPlayers()[1]
end

local function opisGracza(gracz)
	local s = stanGracza(gracz)
	local widziane = {}
	for _, b in D.biomy do
		widziane[b.id] = widzial(gracz, b)
	end
	local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
	return {
		faza = s.automat.faza, id = s.automat.id, biom = s.automat.biom, wynik = s.automat.wynik, gotowy = s.gotowy,
		zakotwiczony = s.kotwica ~= nil, kotwicaCzesci = hrp ~= nil and hrp:IsA("BasePart") and hrp.Anchored,
		blokadaWalki = gracz:GetAttribute(D.blokada) == true, widziane = widziane, ostatnia = s.ostatnia or false,
		pozycja = if hrp and hrp:IsA("BasePart") then hrp.Position else nil,
	}
end

local function odtworz(gracz, biom)
	local b = biomWedlugId[biom]
	if not b or not gracz then
		return false
	end
	local s = stanGracza(gracz)
	if s.automat.faza ~= "brak" then
		return false
	end
	s.wymus = biom
	return true
end

sterowanie.OnInvoke = function(polecenie, a, b)
	if polecenie == "stan" then
		local gracze = {}
		for _, g in Players:GetPlayers() do
			gracze[g.Name] = opisGracza(g)
		end
		local biomy = {}
		for _, bm in D.biomy do
			biomy[bm.id] = kontener:GetAttribute("StanBiomu_" .. bm.id)
		end
		return { gotowy = kontener:GetAttribute("SerwerGotowy") == true, biomy = biomy, gracze = gracze,
			zapisAktywny = zapisAktywny(), skrot = D.skrot }
	elseif polecenie == "gracz" then
		local g = znajdzGracza(a)
		return if g then opisGracza(g) else nil
	elseif polecenie == "odtworz" then
		return odtworz(znajdzGracza(a), b)
	elseif polecenie == "zapomnij" or polecenie == "oznacz" then
		local g = znajdzGracza(a)
		if not g then
			return false
		end
		for _, bm in D.biomy do
			if b == nil or b == bm.id then
				ustawWidzial(g, bm, polecenie == "oznacz")
			end
		end
		local s = stanGracza(g)
		if polecenie == "zapomnij" and s.automat.faza == "brak" then
			s.automat.wolnyOd = 0
		end
		return true
	elseif polecenie == "przerwij" then
		local g = znajdzGracza(a)
		if not g then
			return false
		end
		stanGracza(g).przerwij = "reset"
		return true
	end
	warn(P .. "SterowanieCutscenki: nieznane polecenie " .. tostring(polecenie))
	return nil
end

kontener:GetAttributeChangedSignal("Odtworz"):Connect(function()
	local biom = kontener:GetAttribute("Odtworz")
	if type(biom) ~= "string" or biom == "" then
		return
	end
	kontener:SetAttribute("Odtworz", "")
	if not biomWedlugId[biom] then
		warn(P .. "Odtworz: nieznany biom " .. biom)
		return
	end
	for _, g in Players:GetPlayers() do
		odtworz(g, biom)
	end
end)

------------------------------------------------------------------ sprzątanie i start
kontener.Destroying:Connect(function()
	for g, s in stany do
		pcall(odblokuj, g, s)
	end
end)

for _, b in D.biomy do
	task.spawn(przejmij, b)
end

task.spawn(function()
	local bledyZRzedu = 0
	while kontener.Parent do
		task.wait(K.okres)
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
					pcall(function()
						zdarzenia:FireClient(gracz, "przerwij", s.automat.id)
					end)
					pcall(odblokuj, gracz, s)
					s.automat.faza = "brak"
				end
			end
		end
		if bledyZRzedu >= 20 then
			warn(P .. "pętla cutscenek zatrzymana po 20 błędach z rzędu — biomy wracają do starego przelotu")
			kontener:SetAttribute("SerwerGotowy", false)
			for _, b in D.biomy do
				aktywne[b.id] = nil
				kontener:SetAttribute(D.przejecie .. b.id, nil)
				kontener:SetAttribute("StanBiomu_" .. b.id, "zatrzymany")
			end
			for g, s in stany do
				pcall(odblokuj, g, s)
			end
			break
		end
	end
end)

kontener:SetAttribute("SerwerGotowy", true)
print(string.format("%sserwer gotowy: %d biomy, zgodność logiki %d/%d, skrót danych %s", P, #D.biomy, nLogiki - #bledyLogiki, nLogiki,
	tostring(D.skrot)))
