--[[
	MuzykaStref — muzyka stref i kontekstów gry (Script, RunContext = Client, w kontenerze Workspace/DzwiekGra; pakiet
	swiat/dzwiek_gra).

	Co robi (tylko u tego klienta, nic nie wysyła do serwera; cudze kontenery i atrybuty TYLKO CZYTA):
		• co 0,5 s sprawdza, w której strefie stoi postać: prostokąty stref z Moduly/KatalogDzwiekow (policzone przy
		  budowie z gruntu map); strefa liczy się tylko wtedy, gdy jej mapa stoi w Workspace;
		• gra utwory strefy na zmianę, każdy raz do końca, potem płynne przejście w następny (jedyny utwór — w siebie);
		  zmiana strefy albo wyjście ze stref = płynne przejście (katalog: muzyka.przejscie s);
		• utwór to osobny plik (grany w całości) albo ODCINEK arkusza muzyki (wpis z polami poczatek / koniec:
		  Sound.PlaybackRegionsEnabled + Sound.PlaybackRegion; pozycja odtwarzania to sekundy w pliku arkusza);
		• strefa z utworami zastępczymi (Bagno, Dżungla): dopóki żaden własny utwór nie ma identyfikatora, grają
		  zastępcze (utwory lasu, ciszej) — żeby nie zapadła cisza;
		• KONTEKSTY (katalog: muzyka.konteksty) zastępują muzykę strefy i oddają jej miejsce po sobie:
		    walka           — trwa walka (odtwarzacz prototypu TestWalki2: czyTrwa) i odtwarzanie już ruszyło;
		    walka_straznik  — jak wyżej, a przeciwnik to Strażnik krainy. Odtwarzacz zapisuje u klienta na kontenerze,
		                      z którego ruszyła walka, atrybuty OstatniStan („odtwarzanie” / „wynik”) i OstatniWybor
		                      („klasa/przeciwnik/poziom”). Tablica prototypu podaje gatunek (lista gatunki w katalogu);
		                      walka w krainie — identyfikator potwora, którego opis leży w <kontener>/Stan/<id>
		                      (atrybut Straznik = true albo Gatunek z listy). Bez własnego utworu gra utwór walki;
		    trening         — gracz jest na stanowisku mini-gry Training Center: atrybut gracza z katalogu
		                      (atrybutGracza, dziś TreningGra — ustawia go serwer mini-gier od wejścia do wyjścia).
		  Kontekst gra tylko wtedy, gdy jego utwór ma identyfikator I plik się wczytał (wczytujemy go na zapas);
		  inaczej zostaje zachowanie sprzed kontekstów: muzyka strefy, w walce przyciszona (muzyka.przyciszenieWalki).
		  Muzyka walki nie jest przyciszana w czasie walki; cichnie dopiero przy oknie wyniku. Po kontekście utwór
		  strefy jest wznawiany od miejsca, w którym ucichł (gdy jego tor nie został w tym czasie zajęty);
		• utwór bez identyfikatora (0 = jeszcze nie wgrany) jest pomijany; źródło bez żadnego utworu = cisza, bez
		  komunikatów w konsoli. Menu główne (ekran Pawła) NIE jest tu podpięte — tylko pozycja w katalogu.
	Uchwyt testowy: Sygnaly/SterowanieMuzyki (BindableFunction):
		Invoke("stan") → { strefa, kontekst, zrodlo, zastepcze, utwor, id, glosnosc, gra, wczytany, pozycja, region,
			przyciszenie, przyciszenieKontekstu, walka, walkaKontekst, walkaFaza, gotowy, bledy, zmiany, wznowienia, korekty }
		Invoke("wymus", strefa | nil) → wymuszona strefa (nil = wg pozycji)
		Invoke("wymus_kontekst", kontekst | "brak" | nil) → wymuszony kontekst ("brak" = żaden; nil = wg wykrywania)
		Invoke("probny", strefa | kontekst, id | contentId | nil, { poczatek, koniec }?) → na czas sesji Play podstawia
			identyfikator (i odcinek) pierwszego utworu strefy albo kontekstu; dopóki próba trwa, źródło gra tylko ten
			utwór (próba bez wgranych plików). Identyfikator 0 = „źródło bez własnego utworu” (strefa gra zastępcze).
	Lokalne atrybuty kontenera: MuzykaStrefa, MuzykaKontekst, MuzykaUtwor, MuzykaGotowa, MuzykaBledy.
]]
if not game:GetService("RunService"):IsStudio() then
	return -- pakiet działa wyłącznie w Studio (jak reszta prototypu)
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local kontener = script.Parent
local gracz = Players.LocalPlayer
local P = "[DzwiekGra] "

local K = nil
do
	local m = kontener:WaitForChild("Moduly"):WaitForChild("KatalogDzwiekow", 10)
	local ok, w = false, nil
	if m then
		ok, w = pcall(require, m)
	end
	if ok and type(w) == "table" and type(w.muzyka) == "table" then
		K = w
	else
		warn(P .. "brak modułu KatalogDzwiekow — muzyka stref wyłączona (" .. tostring(w) .. ")")
		return
	end
end
local M = K.muzyka
local KONTEKSTY: { [string]: any } = if type(M.konteksty) == "table" then M.konteksty else {}

local bledy = 0
local function zglosBlad(gdzie: string, blad: any)
	bledy += 1
	pcall(function()
		kontener:SetAttribute("MuzykaBledy", bledy)
	end)
	warn(P .. "błąd muzyki (" .. gdzie .. "): " .. tostring(blad))
end

------------------------------------------------------------------ czy trwa walka (odtwarzacz prototypu, tylko odczyt)
local Odtwarzacz: any = nil
task.spawn(function()
	local proto = workspace:WaitForChild("TestWalki2", 30)
	local m = proto and proto:WaitForChild("Moduly", 10)
	local o = m and m:WaitForChild("OdtwarzaczWalki2", 10)
	if o then
		local ok, w = pcall(require, o)
		if ok and type(w) == "table" and type(w.czyTrwa) == "function" then
			Odtwarzacz = w
		end
	end
end)
local function walkaTrwa(): boolean
	return Odtwarzacz ~= nil and Odtwarzacz.czyTrwa() == true
end

------------------------------------------------------------------ dźwięki (tylko u tego klienta)
local folder = Instance.new("Folder")
folder.Name = "MuzykaLokalna" -- tylko u tego klienta; Sound w folderze (nie w części) gra bez położenia
folder.Parent = kontener

local function contentId(id: any): string?
	if type(id) == "number" and id > 0 then
		return "rbxassetid://" .. tostring(math.floor(id))
	elseif type(id) == "string" and id ~= "" then
		return id -- tylko próby: pełny adres, np. rbxasset://sounds/… (dźwięk wbudowany w klienta)
	end
	return nil
end

-- wczytanie pliku na zapas (niemy dźwięk w folderze): muzyka kontekstu wchodzi dopiero, gdy jej plik jest wczytany —
-- niewczytany (gra nie ma prawa do zasobu, moderacja, brak sieci) nie może uciszyć muzyki strefy
local wczytywane: { [string]: Sound } = {}
local function wczytany(adres: string): boolean
	local s = wczytywane[adres]
	if not s then
		s = Instance.new("Sound")
		s.Name = "Wczytanie"
		s.Volume = 0
		s.SoundId = adres
		s.Parent = folder
		wczytywane[adres] = s
	end
	return s.IsLoaded and s.TimeLength > 0
end

------------------------------------------------------------------ utwory stref i kontekstów
-- strefa albo kontekst → { id, od, do_ } (haczyk "probny"), tylko na czas sesji
local probne: { [string]: any } = {}
local wymuszona: string? = nil
local wymuszonyKontekst: string? = nil -- nazwa kontekstu, "brak" albo nil (wg wykrywania)

-- wpisy katalogu → utwory do grania { nazwa, adres, od, do_, glosnosc, kontekst }; wpis bez identyfikatora odpada
local function listaUtworow(wpisy: any, glosnosc: number, proba: any, kontekst: string?): { any }
	local lista = {}
	if type(wpisy) ~= "table" then
		return lista
	end
	for i, u in wpisy do
		local od, do_ = u.poczatek, u.koniec
		local id = u.id
		if proba ~= nil then
			if i > 1 then
				break -- próba: gra tylko pierwszy utwór z podstawionym plikiem (wynik próby nie zależy od reszty listy)
			end
			id, od, do_ = proba.id, proba.od, proba.do_ -- inny plik, więc i odcinek z próby (nil = cały plik)
		end
		if type(od) ~= "number" or type(do_) ~= "number" or do_ <= od then
			od, do_ = nil, nil
		end
		local adres = contentId(id)
		if adres then
			table.insert(lista, { nazwa = u.nazwa, adres = adres, od = od, do_ = do_, glosnosc = glosnosc, kontekst = kontekst })
		end
	end
	return lista
end

-- utwory strefy: własne z identyfikatorem, a gdy żaden go nie ma — zastępcze; (lista, czyZastepcze); pusta = cisza
local function utworyStrefy(nazwa: string): ({ any }, boolean)
	local s = M.strefy[nazwa]
	if not s or s.podpiete == false then
		return {}, false
	end
	local lista = listaUtworow(s.utwory, s.glosnosc or 0.35, probne[nazwa], nil)
	if #lista == 0 and type(s.zastepcze) == "table" then
		return listaUtworow(s.zastepcze.utwory, s.zastepcze.glosnosc or s.glosnosc or 0.35, nil, nil), true
	end
	return lista, false
end

-- utwory kontekstu: z identyfikatorem i już wczytane (pusta = kontekst nie gra, zostaje muzyka strefy)
local function utworyKontekstu(nazwa: string): { any }
	local k = KONTEKSTY[nazwa]
	local lista = {}
	if type(k) ~= "table" then
		return lista
	end
	for _, u in listaUtworow(k.utwory, k.glosnosc or 0.35, probne[nazwa], nazwa) do
		if wczytany(u.adres) then
			table.insert(lista, u)
		end
	end
	return lista
end

local function strefaTeraz(): string?
	if wymuszona then
		return wymuszona
	end
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp or not hrp:IsA("BasePart") then
		return nil
	end
	local p = hrp.Position
	for nazwa, s in M.strefy do
		if s.podpiete ~= false and type(s.prostokaty) == "table" and #s.prostokaty > 0
			and (not s.kontener or workspace:FindFirstChild(s.kontener) ~= nil) then
			for _, r in s.prostokaty do
				if p.X >= r[1] and p.X <= r[2] and p.Z >= r[3] and p.Z <= r[4] then
					return nazwa
				end
			end
		end
	end
	return nil
end

------------------------------------------------------------------ kontekst: walka, walka ze Strażnikiem, mini-gra
local walkaKlucz: string? = nil -- "<kontener>|<wybór>" walki, dla której kontekst jest już ustalony
local walkaKontekst: string? = nil -- "walka" | "walka_straznik"; nil = odtwarzanie jeszcze nie ruszyło
local walkaFaza: string? = nil -- OstatniStan kontenera walki: "odtwarzanie" | "wynik"

local function czyStraznik(kont: Instance, przeciwnik: string): boolean
	local ks = KONTEKSTY.walka_straznik
	local gatunki = if type(ks) == "table" then ks.gatunki else nil
	if type(gatunki) ~= "table" then
		return false
	end
	if table.find(gatunki, przeciwnik) then
		return true -- tablica prototypu: przeciwnik to gatunek
	end
	-- walka w krainie: przeciwnik to identyfikator potwora; jego opis (Configuration) leży w <kontener>/Stan
	local stan = kont:FindFirstChild("Stan")
	local cfg = stan and stan:FindFirstChild(przeciwnik)
	if cfg then
		local g = cfg:GetAttribute("Gatunek")
		return cfg:GetAttribute("Straznik") == true or (type(g) == "string" and table.find(gatunki, g) ~= nil)
	end
	return false
end

-- kontekst trwającej walki; ustalany raz, gdy odtwarzanie ruszy (potem opis potwora może zniknąć — serwer usuwa
-- pokonanego), i trzymany do końca walki („JESZCZE RAZ” = ten sam przeciwnik, więc kontekst zostaje)
local function kontekstWalki(): string?
	local kont, faza, wybor = nil, nil, nil
	for _, d in workspace:GetChildren() do
		local st = d:GetAttribute("OstatniStan")
		if st == "odtwarzanie" or st == "wynik" then
			local w = d:GetAttribute("OstatniWybor")
			if type(w) == "string" then
				kont, faza, wybor = d, st, w
				break
			end
		end
	end
	walkaFaza = faza
	if not kont or not wybor then
		return walkaKontekst
	end
	local klucz = kont.Name .. "|" .. wybor
	if klucz ~= walkaKlucz then
		walkaKlucz = klucz
		local przeciwnik = string.match(wybor, "^[^/]*/(.*)/[^/]*$") or ""
		walkaKontekst = if czyStraznik(kont, przeciwnik) then "walka_straznik" else "walka"
	end
	return walkaKontekst
end

local function kontekstTeraz(): string?
	if wymuszonyKontekst ~= nil then
		return if wymuszonyKontekst == "brak" then nil else wymuszonyKontekst
	end
	if walkaTrwa() then
		return kontekstWalki()
	end
	walkaKlucz, walkaKontekst, walkaFaza = nil, nil, nil
	local kt = KONTEKSTY.trening
	if type(kt) == "table" and type(kt.atrybutGracza) == "string" and gracz:GetAttribute(kt.atrybutGracza) ~= nil then
		return "trening"
	end
	return nil
end

------------------------------------------------------------------ odtwarzanie (dwa tory na zmianę, przenikanie)
local tory = {}
for i = 1, 2 do
	local s = Instance.new("Sound")
	s.Name = "Tor" .. i
	s.Volume = 0
	s.Looped = false
	s.Parent = folder
	tory[i] = { dzwiek = s, waga = 0, cel = 0, glosnosc = 0, nazwa = nil, adres = nil, zrodlo = nil, od = nil, do_ = nil,
		kontekst = nil, zastepcze = false, pauza = false, wstrzymany = false, korektaOd = 0, start = 0 }
end
local biezacy = 0 -- indeks toru, który gra „na głos” (0 = żaden)
local nrUtworu: { [string]: number } = {}
local zmiany = 0
local wznowienia = 0
local korekty = 0
local przyciszenie = 1 -- muzyka strefy w czasie walki
local przyciszenieK = 1 -- muzyka walki przy oknie wyniku

-- klucz = źródło ("strefa:<nazwa>" | "kontekst:<nazwa>"), lista = jego utwory; poprzednie = źródło, które grało dotąd
local function graj(klucz: string, lista: { any }, zastepcze: boolean, poprzednie: string?): boolean
	if #lista == 0 then
		return false
	end
	local nastepny = if biezacy == 1 then 2 else 1
	local t = tory[nastepny]
	local stary = if biezacy ~= 0 then tory[biezacy] else nil
	-- powrót z kontekstu do strefy: utwór strefy gra dalej od miejsca, w którym ucichł (gdy jego tor nie został
	-- w tym czasie zajęty) — wstrzymany wznawiamy, a jeszcze wyciszany po prostu wraca na głos
	local wznow = false
	if (t.wstrzymany or t.pauza) and t.zrodlo == klucz and klucz ~= poprzednie then
		for _, u in lista do
			if u.nazwa == t.nazwa and u.adres == t.adres then
				wznow = true
				break
			end
		end
	end
	if wznow then
		if t.wstrzymany then
			t.waga = 0
			t.dzwiek.Volume = 0
			t.dzwiek:Resume()
		end
		t.wstrzymany, t.pauza = false, false
		t.cel = 1
		wznowienia += 1
	else
		local n = ((nrUtworu[klucz] or 0) % #lista) + 1
		nrUtworu[klucz] = n
		local u = lista[n]
		local d = t.dzwiek
		d:Stop()
		d.SoundId = u.adres
		local odcinek = u.od ~= nil
		local ok = pcall(function()
			d.PlaybackRegionsEnabled = odcinek
			if odcinek then
				d.PlaybackRegion = NumberRange.new(u.od, u.do_)
			end
		end)
		if not ok and odcinek then
			return false -- klient bez odcinków: nie gramy (poleciałby cały arkusz)
		end
		d.TimePosition = u.od or 0
		t.nazwa, t.adres, t.zrodlo = u.nazwa, u.adres, klucz
		t.od, t.do_ = u.od, u.do_
		t.kontekst, t.zastepcze = u.kontekst, zastepcze
		t.glosnosc = u.glosnosc
		t.wstrzymany, t.pauza = false, false
		t.waga, t.cel = 0, 1
		t.korektaOd = 0
		d.Volume = 0
		d:Play()
	end
	t.start = os.clock()
	if stary then
		stary.cel = 0
		-- strefa ustępuje kontekstowi: jej utwór po wyciszeniu czeka wstrzymany, a nie zatrzymany
		stary.pauza = stary.kontekst == nil and t.kontekst ~= nil
	end
	biezacy = nastepny
	zmiany += 1
	kontener:SetAttribute("MuzykaUtwor", t.nazwa)
	return true
end

local function wycisz()
	if biezacy ~= 0 then
		tory[biezacy].cel = 0
		tory[biezacy].pauza = false
		biezacy = 0
		kontener:SetAttribute("MuzykaUtwor", nil)
	end
end

local strefa: string? = nil
local kontekst: string? = nil -- kontekst, którego muzyka gra (nil = muzyka strefy albo cisza)
local zrodlo: string? = nil -- "strefa:<nazwa>" | "kontekst:<nazwa>" — co teraz gra (nil = cisza)
local przelicz = false -- haczyki testowe: przelicz źródło i utwór od nowa (także gdy źródło się nie zmienia)

local function sprawdz()
	local nowaStrefa = strefaTeraz()
	if nowaStrefa ~= strefa then
		strefa = nowaStrefa
		kontener:SetAttribute("MuzykaStrefa", nowaStrefa)
	end
	-- źródło: kontekst z grywalnym utworem, inaczej strefa
	local k = kontekstTeraz()
	local klucz: string? = nil
	local lista: { any } = {}
	local zastepcze = false
	if k == "walka_straznik" then
		lista = utworyKontekstu(k)
		if #lista == 0 then
			k = "walka" -- Strażnik bez własnego utworu: utwór zwykłej walki
		end
	end
	if k and #lista == 0 then
		lista = utworyKontekstu(k)
	end
	if k and #lista > 0 then
		klucz = "kontekst:" .. k
	else
		k = nil
		if nowaStrefa then
			lista, zastepcze = utworyStrefy(nowaStrefa)
			if #lista > 0 then
				klucz = "strefa:" .. nowaStrefa
			end
		end
	end
	if k ~= kontekst then
		kontekst = k
		kontener:SetAttribute("MuzykaKontekst", k)
	end
	if klucz ~= zrodlo or przelicz then
		przelicz = false
		local poprzednie = zrodlo
		zrodlo = klucz
		if not klucz or not graj(klucz, lista, zastepcze, poprzednie) then
			wycisz()
		end
		return
	end
	-- utwór dobiega końca: następny utwór źródła (na zmianę); jedyny utwór — od początku. Zapas 0,5 s na odstęp
	-- między sprawdzeniami, żeby wyciszenie skończyło się przed końcem pliku albo odcinka
	if klucz and biezacy ~= 0 then
		local t = tory[biezacy]
		local d = t.dzwiek
		if d.IsLoaded and d.TimeLength > 0 then
			local koniec = t.do_ or d.TimeLength
			-- drugi warunek to zabezpieczenie: wczytany utwór sam się skończył (np. zacięcie dłuższe niż przejście)
			if d.TimePosition >= koniec - (M.przejscie or 2.5) - 0.5
				or (not d.IsPlaying and not d.IsPaused and os.clock() - t.start > 3) then
				graj(klucz, lista, zastepcze, klucz)
			end
		end
	elseif klucz and biezacy == 0 then
		graj(klucz, lista, zastepcze, nil) -- np. identyfikator próbny podany po wejściu do strefy
	end
end

RunService.Heartbeat:Connect(function(dt: number)
	local ok, blad = pcall(function()
		local walka = walkaTrwa()
		local szybkoP = dt / math.max(M.przyciszenieCzas or 0.8, 0.05)
		local celP = if walka then (M.przyciszenieWalki or 0.25) else 1
		przyciszenie += math.clamp(celP - przyciszenie, -szybkoP, szybkoP)
		local celK = if walka and walkaFaza == "wynik" then (M.przyciszenieWalki or 0.25) else 1
		przyciszenieK += math.clamp(celK - przyciszenieK, -szybkoP, szybkoP)
		local szybko = dt / math.max(M.przejscie or 2.5, 0.05)
		for _, t in tory do
			local d = t.dzwiek
			if t.waga ~= t.cel then
				t.waga += math.clamp(t.cel - t.waga, -szybko, szybko)
			end
			local v = t.glosnosc * t.waga * (if t.kontekst then przyciszenieK else przyciszenie)
			if math.abs(d.Volume - v) > 1e-3 then
				d.Volume = v
			end
			if t.cel == 0 and t.waga <= 0 and d.IsPlaying then
				if t.pauza then
					d:Pause()
					t.pauza, t.wstrzymany = false, true
				else
					d:Stop()
				end
			end
			-- odcinek arkusza: gdyby odtwarzanie wyszło poza odcinek (np. start od zera przed wczytaniem pliku),
			-- wracamy na jego początek — najwyżej raz na pół sekundy
			if t.od and t.cel > 0 and d.IsPlaying and d.IsLoaded and os.clock() - t.korektaOd > 0.5 then
				local p = d.TimePosition
				if p < t.od - 0.25 or p > t.do_ + 0.25 then
					t.korektaOd = os.clock()
					d.TimePosition = t.od
					korekty += 1
				end
			end
		end
	end)
	if not ok then
		zglosBlad("klatka", blad)
	end
end)

-- pliki kontekstów wczytujemy na zapas od razu (arkusz muzyki ma kilka MB — pierwsza walka nie powinna na niego czekać)
for _, k in KONTEKSTY do
	if type(k) == "table" and type(k.utwory) == "table" then
		for _, u in k.utwory do
			local adres = contentId(u.id)
			if adres then
				wczytany(adres)
			end
		end
	end
end

task.spawn(function()
	while kontener.Parent do
		local ok, blad = pcall(sprawdz)
		if not ok then
			zglosBlad("strefa", blad)
		end
		task.wait(0.5)
	end
end)

------------------------------------------------------------------ haczyk testowy
local h = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieMuzyki", 5)
if h and h:IsA("BindableFunction") then
	h.OnInvoke = function(polecenie: string, a: any, b: any, c: any)
		if polecenie == "stan" then
			local t = if biezacy ~= 0 then tory[biezacy] else nil
			local d = t and t.dzwiek
			return {
				strefa = strefa, kontekst = kontekst, zrodlo = zrodlo, zastepcze = t ~= nil and t.zastepcze == true,
				utwor = t and t.nazwa, id = d and d.SoundId, glosnosc = d and d.Volume, gra = d ~= nil and d.IsPlaying,
				wczytany = d ~= nil and d.IsLoaded and d.TimeLength > 0, pozycja = d and d.TimePosition,
				region = if t and t.od then { t.od, t.do_ } else nil,
				przyciszenie = przyciszenie, przyciszenieKontekstu = przyciszenieK, walka = walkaTrwa(),
				walkaKontekst = walkaKontekst, walkaFaza = walkaFaza, gotowy = true, bledy = bledy, zmiany = zmiany,
				wznowienia = wznowienia, korekty = korekty,
			}
		elseif polecenie == "wymus" then
			wymuszona = if type(a) == "string" and M.strefy[a] then a else nil
			przelicz = true
			return wymuszona
		elseif polecenie == "wymus_kontekst" then
			wymuszonyKontekst = if type(a) == "string" and (a == "brak" or KONTEKSTY[a]) then a else nil
			return wymuszonyKontekst
		elseif polecenie == "probny" then
			if type(a) ~= "string" or not (M.strefy[a] or KONTEKSTY[a]) then
				return false
			end
			if b == nil then
				probne[a] = nil
			else
				local r = if type(c) == "table" then c else {}
				probne[a] = { id = b, od = r.poczatek, do_ = r.koniec }
				local adres = contentId(b)
				if adres and KONTEKSTY[a] then
					wczytany(adres) -- plik kontekstu zaczyna się wczytywać od razu
				end
			end
			-- próbny identyfikator dostaje pierwszy utwór — niech zagra jako pierwszy
			nrUtworu["strefa:" .. a], nrUtworu["kontekst:" .. a] = nil, nil
			przelicz = true
			return true
		end
		return nil
	end
end
kontener:SetAttribute("MuzykaGotowa", true)
