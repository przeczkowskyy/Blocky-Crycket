--[[
	SerwerWalki2 — serwerowa połowa prototypu walki v2 (Script, RunContext = Server). Wzór: v1 (SerwerWalki).

	Jedyny punkt styku z klientem to RemoteFunction Zdalne/RozpocznijWalke2:
		klient → wybor = { klasa = "wojownik" | "zwiadowca" | "mag", przeciwnik = id potwora lasu, poziom = "1" | "5" | "10" }
		serwer → sprawdza wybór z ZAMKNIĘTĄ listą (inne wartości, liczby i dodatkowe pola: odmowa „zly_wybor” albo
		         pominięcie), sam buduje postać wzorcową (Moduly/Wzorcowe = tools/walka/wzorcowe.py) i przeciwnika,
		         losuje ziarno, woła Moduly/Walka/Silnik.symuluj i odsyła dziennik { ok, walka, nastepnaOd }.
	Klient nie przysyła liczb (poziom to napis z listy, nie liczba), a resztę argumentów serwer ignoruje (D-016).

	Kiedy wolno zacząć walkę (kolejno, jak w v1):
		1. nie częściej niż jedna prośba na ODSTEP_PROSB s (także odrzucona) — „za_szybko”;
		2. wybór z listy — „zly_wybor”;
		3. postać żyje i stoi najwyżej MAKS_ODLEGLOSC studów od tablicy — „brak_postaci” / „za_daleko”;
		4. poprzednia walka gracza się skończyła: serwer pamięta czas jej końca (teraz + walka.czas, czyli PEŁNY czas
		   dziennika przy tempie ×1) — „walka_trwa”. Tempo ×2 / ×4 i „POMIŃ” skracają tylko odtwarzanie u klienta.
	Łup liczy silnik w tym samym wywołaniu co walkę — bez walki nie ma łupu (w grze tu byłby zapis).

	Do testów (tylko po stronie serwera, klient tego nie zmieni): atrybut kontenera „ZiarnoTestowe” (liczba ≥ 1)
	wymusza ziarno; atrybut „TestBezSesji” = true wyłącza blokadę sesji walki (tylko narzędzie klatek, które ogląda
	dziesiątki walk pod rząd; zmiana atrybutu u klienta się nie replikuje, więc klient go nie ustawi).

	v3 (17.11.2026):
		• wybór ma czwarte, OPCJONALNE pole zestaw = "wzorcowa" | "mana" | "pasywki" | "wskrzeszenie" (brak = wzorcowa;
		  Moduly/Wzorcowe → W.zestaw, wzorzec swiat/test_walki2/zestawy.py) i przeciwnika "lustro" (postać tej samej
		  klasy i zestawu — wskrzeszenie przeciwnika). Nic z liczb nie przychodzi od klienta.
		• odpowiedź z walką niesie też pomijanie (D-078, decyzja serwera) i pasywki stron (do zapowiedzi na starcie).
		• POMIJANIE (D-078): pamięć poznanych gatunków gracza jest TU (Moduly/PamiecWalk, w pamięci serwera, według
		  UserId — jedna dla tablicy, lasu-pasa i starego lasu). Zdalne/PominiecieWalki2 (RemoteFunction):
		      "czy", zrodlo  → { ok, powod }      czy bieżącą walkę gracza z tego źródła wolno pominąć
		      "pomin", zrodlo → { ok, powod, nastepnaOd? }   pominięcie: tablica zwalnia sesję od razu; las — gdy jego
		                                                      kontener ma Sygnaly/ZwolnijPoPominieciu (README)
		  zrodlo = nazwa kontenera z zamkniętej listy (TestWalki2, LasPasGra, LasPotwory, BagnoPasGra). Bez zgody → odmowa.
		• walki z lasów liczy ich własny serwer (SerwerPotworow) — tutaj trafiają przez MOSTEK: serwer słucha
		  Sygnaly/WynikWalki (BindableEvent) kontenerów LasPasGra i LasPotwory, gdy go mają (las-pas ma; stary las
		  nie ma — wtedy jego walki są „nieznane” i pomijać ich nie wolno, bezpieczne zachowanie domyślne).
]]
if not game:GetService("RunService"):IsStudio() then
	-- Prototyp działa wyłącznie w Studio. Poza Studio (opublikowane miejsce) serwer usuwa CAŁY kontener — arenę,
	-- galerię, szablony aktorów, kopię silnika i podpowiedź — zanim ktokolwiek dołączy.
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local Ustawienia = require(moduly:WaitForChild("Ustawienia"))
local Wzorcowe = require(moduly:WaitForChild("Wzorcowe"))
local folderWalki = moduly:WaitForChild("Walka")
local Silnik = require(folderWalki:WaitForChild("Silnik"))
local Dane = require(folderWalki:WaitForChild("Dane"))
local PamiecWalk = require(moduly:WaitForChild("PamiecWalk"))
local zdalna = kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke2") :: RemoteFunction
local zdalnaPominiecia = kontener:WaitForChild("Zdalne"):WaitForChild("PominiecieWalki2") :: RemoteFunction
local deska = kontener:WaitForChild("Arena"):WaitForChild("Tablica"):WaitForChild("Deska") :: BasePart

-- podpowiedź jest zbudowana jako wyłączona; włącza ją dopiero serwer w Studio
local podpowiedz = deska:WaitForChild("PodpowiedzWalki2") :: ProximityPrompt
podpowiedz.ActionText = "Wybierz walkę"
podpowiedz.Enabled = true

local ODSTEP_PROSB = 1.0
local MAKS_ODLEGLOSC = 20
local ZAPAS_SESJI = 0.4

-- ZAMKNIĘTE listy wyboru (dane testowe prototypu)
local KLASY = {}
for _, k in Wzorcowe.KLASY do
	KLASY[k] = true
end
local PRZECIWNICY = {}
local DANE_PRZECIWNIKA = {}
for _, d in Dane.przeciwnicy do
	PRZECIWNICY[d.id] = true
	DANE_PRZECIWNIKA[d.id] = d
end
PRZECIWNICY[Wzorcowe.LUSTRO] = true
local POZIOMY = { ["1"] = 1, ["5"] = 5, ["10"] = 10 }
local ZESTAWY = {}
for _, z in Wzorcowe.ZESTAWY do
	ZESTAWY[z] = true
end
-- źródła walk dla pamięci pomijania: ten kontener i kontenery lasów (mostek przez Sygnaly/WynikWalki);
-- 17.11.2026: też Bagno (BagnoPasGra, swiat/bagno_pas_gra — ten sam kod potworów co las-pas)
local ZRODLA = { [kontener.Name] = true, LasPasGra = true, LasPotwory = true, BagnoPasGra = true }
local ZRODLA_LASU = { LasPasGra = true, LasPotwory = true, BagnoPasGra = true }

local ostatniaProsba: { [Player]: number } = {}
local ostatniePominiecie: { [Player]: number } = {}
local walkaDo: { [Player]: number } = {}
local generator = Random.new()
local pamiec = PamiecWalk.nowa()

local function pasywkiOpisu(opis): any
	-- pasywne umiejętności ze slotów i pasywka broni (do zapowiedzi u klienta; liczby są w dzienniku)
	local sloty = {}
	for _, u in opis.umiejetnosci or {} do
		if Dane.pasywne[u] then
			table.insert(sloty, u)
		end
	end
	return { sloty = sloty, bron = (opis.bron and opis.bron.pasywka) or "" }
end

local function pasywkiPotwora(id: string): any
	local sloty = {}
	local d = DANE_PRZECIWNIKA[id]
	for _, u in (d and d.umiejetnosci) or {} do
		if Dane.pasywne[u] then
			table.insert(sloty, u)
		end
	end
	return { sloty = sloty, bron = "" }
end

local function atrybutyPamieci(gracz: Player)
	pcall(function()
		local lista = PamiecWalk.poznane(pamiec, gracz.UserId, workspace:GetServerTimeNow())
		gracz:SetAttribute("PoznaneGatunki", table.concat(lista, ","))
	end)
end

local function wybierzZiarno(): number
	local wymuszone = kontener:GetAttribute("ZiarnoTestowe")
	if type(wymuszone) == "number" and wymuszone >= 1 and wymuszone < 2147483647 then
		return math.floor(wymuszone)
	end
	return generator:NextInteger(1, 2147483646)
end

local function odlegloscOdTablicy(gracz: Player): number?
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if not hrp or not hrp:IsA("BasePart") or not hum or hum.Health <= 0 then
		return nil
	end
	return (hrp.Position - deska.Position).Magnitude
end

-- wybór od klienta → (klasa, przeciwnik, poziom, zestaw) albo nil; czytamy tylko te pola i tylko jako napisy z listy
-- (zestaw opcjonalny: brak = "wzorcowa"; zły zestaw = odmowa)
local function sprawdzWybor(wybor: any): (string?, string?, number?, string?)
	if type(wybor) ~= "table" then
		return nil
	end
	local klasa, przeciwnik, poziom = rawget(wybor, "klasa"), rawget(wybor, "przeciwnik"), rawget(wybor, "poziom")
	local zestaw = rawget(wybor, "zestaw")
	if type(klasa) ~= "string" or type(przeciwnik) ~= "string" or type(poziom) ~= "string" then
		return nil
	end
	if zestaw == nil then
		zestaw = "wzorcowa"
	end
	if type(zestaw) ~= "string" or not ZESTAWY[zestaw] then
		return nil
	end
	if not KLASY[klasa] or not PRZECIWNICY[przeciwnik] or not POZIOMY[poziom] then
		return nil
	end
	return klasa, przeciwnik, POZIOMY[poziom], zestaw
end

zdalna.OnServerInvoke = function(gracz: Player, wybor: any)
	local teraz = os.clock()
	local poprzednio = ostatniaProsba[gracz]
	if poprzednio and teraz - poprzednio < ODSTEP_PROSB then
		return { ok = false, powod = "za_szybko", ponowZa = ODSTEP_PROSB - (teraz - poprzednio) }
	end
	ostatniaProsba[gracz] = teraz

	local klasa, przeciwnik, poziom, zestaw = sprawdzWybor(wybor)
	if not klasa or not przeciwnik or not poziom or not zestaw then
		return { ok = false, powod = "zly_wybor" }
	end

	local odleglosc = odlegloscOdTablicy(gracz)
	if not odleglosc then
		return { ok = false, powod = "brak_postaci" }
	elseif odleglosc > MAKS_ODLEGLOSC then
		return { ok = false, powod = "za_daleko", odleglosc = math.floor(odleglosc) }
	end

	local czasSerwera = workspace:GetServerTimeNow()
	local koniec = walkaDo[gracz]
	if koniec and czasSerwera < koniec and kontener:GetAttribute("TestBezSesji") ~= true then
		return { ok = false, powod = "walka_trwa", ponowZa = koniec - czasSerwera }
	end

	local ziarno = wybierzZiarno()
	local postac = Wzorcowe.zestaw(zestaw, klasa, poziom)
	local lustro = przeciwnik == Wzorcowe.LUSTRO
	local opisWroga = if lustro then { postac = Wzorcowe.lustro(zestaw, klasa, poziom) } else { potwor = przeciwnik, poziom = poziom }
	local udalo, walka = pcall(Silnik.symuluj, postac, opisWroga, ziarno)
	if not udalo then
		warn("[TestWalki2] Silnik walki zgłosił błąd: " .. tostring(walka))
		return { ok = false, powod = "blad_silnika" }
	end
	walkaDo[gracz] = czasSerwera + walka.czas - ZAPAS_SESJI
	if kontener:GetAttribute("TestBezSesji") == true then
		walkaDo[gracz] = czasSerwera -- tylko narzędzie klatek (patrz nagłówek)
	end

	-- D-078: czy wolno pominąć — gatunek przeciwnika poznany w zakończonej walce (pamięć serwera, wszystkie źródła)
	local gatunek = if lustro then ("postac:" .. klasa) else przeciwnik
	local pomijanie = PamiecWalk.przyjmij(pamiec, gracz.UserId, kontener.Name, gatunek, czasSerwera, walkaDo[gracz])
	atrybutyPamieci(gracz)

	-- W prawdziwej grze dokładnie tutaj serwer przyznaje i zapisuje łup; klient dostaje tylko zapis do pokazania.
	kontener:SetAttribute("SerwerLicznikWalk", (kontener:GetAttribute("SerwerLicznikWalk") or 0) + 1)
	kontener:SetAttribute("SerwerOstatnieZiarno", ziarno)
	kontener:SetAttribute("SerwerOstatniWybor", string.format("%s/%s/%d/%s", klasa, przeciwnik, poziom, zestaw))
	kontener:SetAttribute("SerwerOstatniePominiecie", pomijanie)

	pcall(function()
		gracz:RequestStreamAroundAsync(Ustawienia.scena().Position, 3)
	end)

	return {
		ok = true,
		walka = walka,
		nastepnaOd = walkaDo[gracz],
		pomijanie = pomijanie,
		pasywki = {
			gracz = pasywkiOpisu(postac),
			wrog = if lustro then pasywkiOpisu(opisWroga.postac) else pasywkiPotwora(przeciwnik),
		},
	}
end

------------------------------------------------------------------ pomijanie (D-078): zapytanie i zgłoszenie
local function odmowaPominiecia(powod: string)
	kontener:SetAttribute("SerwerPominieciaOdrzucone", (kontener:GetAttribute("SerwerPominieciaOdrzucone") or 0) + 1)
	kontener:SetAttribute("SerwerOstatniaOdmowaPominiecia", powod)
	return { ok = false, powod = powod }
end

-- las z Sygnaly/ZwolnijPoPominieciu (BindableFunction; dopisek opisany w README) zwalnia gracza i potwora od razu
local function zwolnijWLesie(zrodlo: string, gracz: Player): boolean
	local k = workspace:FindFirstChild(zrodlo)
	local s = k and k:GetAttribute("Wygenerowane") == true and k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild("ZwolnijPoPominieciu")
	if not f or not f:IsA("BindableFunction") then
		return false
	end
	local ok, wynik = pcall(function()
		return f:Invoke(gracz)
	end)
	return ok and wynik == true
end

zdalnaPominiecia.OnServerInvoke = function(gracz: Player, polecenie: any, zrodlo: any)
	local teraz = os.clock()
	local poprzednio = ostatniePominiecie[gracz]
	if poprzednio and teraz - poprzednio < 0.2 then
		return odmowaPominiecia("za_szybko")
	end
	ostatniePominiecie[gracz] = teraz
	if (polecenie ~= "czy" and polecenie ~= "pomin") or type(zrodlo) ~= "string" or not ZRODLA[zrodlo] then
		return odmowaPominiecia("zly_wybor")
	end
	local czas = workspace:GetServerTimeNow()
	if polecenie == "czy" then
		local ok, powod = PamiecWalk.czyMozna(pamiec, gracz.UserId, zrodlo, czas)
		return { ok = ok, powod = powod }
	end
	local ok, powod = PamiecWalk.pomin(pamiec, gracz.UserId, zrodlo, czas)
	if not ok then
		return odmowaPominiecia(powod)
	end
	kontener:SetAttribute("SerwerPominieciaPrzyjete", (kontener:GetAttribute("SerwerPominieciaPrzyjete") or 0) + 1)
	atrybutyPamieci(gracz)
	if zrodlo == kontener.Name then
		-- tablica prototypu: po pominięciu gracz jest wolny od razu (ustawienie przyjęte przez właściciela)
		walkaDo[gracz] = czas
		return { ok = true, powod = "ok", nastepnaOd = czas }
	end
	if zwolnijWLesie(zrodlo, gracz) then
		return { ok = true, powod = "ok", nastepnaOd = czas }
	end
	-- las bez dopisku z README: pokaz skrócony, ale sesję i zajętość potwora trzyma serwer lasu do końca walki
	return { ok = true, powod = "sesja_zrodla" }
end

------------------------------------------------------------------ mostek: walki lasów do pamięci pomijania
--[[ SerwerPotworow (stary las i las-pas) strzela Sygnaly/WynikWalki(gracz, { gatunek, koniec, … }) przy każdej
	przyjętej walce — o ile jego kontener ma ten BindableEvent (las-pas ma; stary las dziś nie). Tylko słuchamy:
	niczego w lesie nie zmieniamy. Kontener odbudowany w Play (ChildAdded) podłączamy na nowo. ]]
local mostki: { [Instance]: RBXScriptConnection } = {}
-- gatunki znane ŹRÓDŁU walki: nasza kopia Dane albo kopia Dane w kontenerze źródła (Bagno ma w swojej kopii
-- dopisanych przeciwników Bagna; tylko odczyt, raz na kontener)
local gatunkiZrodla: { [Instance]: { [string]: boolean } } = {}
local function znanyGatunek(k: Instance, gatunek: string): boolean
	if DANE_PRZECIWNIKA[gatunek] then
		return true
	end
	local znane = gatunkiZrodla[k]
	if not znane then
		znane = {}
		pcall(function()
			local m = k:FindFirstChild("Moduly")
			local w = m and m:FindFirstChild("Walka")
			local d = w and w:FindFirstChild("Dane")
			if d and d:IsA("ModuleScript") then
				for _, p in (require(d) :: any).przeciwnicy or {} do
					znane[p.id] = true
				end
			end
		end)
		gatunkiZrodla[k] = znane
	end
	return znane[gatunek] == true
end
local function podlaczMostek(k: Instance)
	if not ZRODLA_LASU[k.Name] or mostki[k] then
		return
	end
	task.spawn(function()
		local sygnaly = k:WaitForChild("Sygnaly", 15)
		local s = sygnaly and sygnaly:WaitForChild("WynikWalki", 15)
		if not s or not s:IsA("BindableEvent") or mostki[k] or not k.Parent then
			return
		end
		mostki[k] = s.Event:Connect(function(gracz: any, info: any)
			if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or type(info) ~= "table" then
				return
			end
			local gatunek, koniec = info.gatunek, info.koniec
			if type(gatunek) ~= "string" or not znanyGatunek(k, gatunek) or type(koniec) ~= "number" or koniec ~= koniec then
				return
			end
			PamiecWalk.przyjmij(pamiec, gracz.UserId, k.Name, gatunek, workspace:GetServerTimeNow(), koniec)
			atrybutyPamieci(gracz)
			kontener:SetAttribute("SerwerMostekWalk", (kontener:GetAttribute("SerwerMostekWalk") or 0) + 1)
		end)
		k.Destroying:Connect(function()
			gatunkiZrodla[k] = nil
			if mostki[k] then
				mostki[k]:Disconnect()
				mostki[k] = nil
			end
		end)
	end)
end
for _, k in workspace:GetChildren() do
	podlaczMostek(k)
end
workspace.ChildAdded:Connect(podlaczMostek)
kontener.Destroying:Connect(function()
	for _, p in mostki do
		p:Disconnect()
	end
	table.clear(mostki)
end)

Players.PlayerRemoving:Connect(function(gracz)
	ostatniaProsba[gracz] = nil
	ostatniePominiecie[gracz] = nil
	walkaDo[gracz] = nil
	-- pamięć poznanych gatunków ZOSTAJE (ponowne wejście na ten sam serwer pamięta — jak PamiecGracza lasu-pasa)
end)

kontener:SetAttribute("SerwerGotowy", true)
