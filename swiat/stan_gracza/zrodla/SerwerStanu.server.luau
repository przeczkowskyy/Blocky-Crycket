--[[
	SerwerStanu — JEDYNY właściciel stanu gracza między systemami (Script, RunContext = Server, w kontenerze
	Workspace/StanGracza; budowa: swiat/stan_gracza/zbuduj.py; status: propozycja, opis w README pakietu).

	Szyną danych dla HUD i okien Pawła zostają ATRYBUTY GRACZA (Level, XP, XPMax, Gold, Gems, Class, Strength… —
	ich kodu nie ruszamy; HUD i okno ekwipunku same słuchają zmian). Ten skrypt:
		1. łup z walki w lesie (Sygnaly/PrzyznajLup, woła SerwerPotworow obu lasów) → profil od razu, atrybuty po walce:
		   gdy klient zgłosi, że HUD znów widać ("pokaz"), albo najpóźniej po czasie walki + D.publikacja.zapas_s;
		   łup młodszy niż min_s w chwili zgłoszenia (walka pominięta zaraz po starcie, D-107) pokazuje się sam, gdy
		   dojrzeje — bez czekania na następne zgłoszenie;
		   Gold i Gems czytamy i dopisujemy (odczyt-zapis), bo drzewko Pawła odejmuje Gems z tego samego atrybutu;
		2. awans: XP ≥ XPMax → Level + 1, nowe XPMax z krzywej (D.krzywa = tools/walka/tempo.py), komunikat "awans"
		   do klienta (baner „POZIOM N”);
		3. statystyki: po wyborze klasy i przy każdej zmianie Level sześć atrybutów dostaje rozkład klasy dla puli
		   poziomu (30 + 10 na poziom; rozkłady wzorcowe D.rozklady albo — D.rozklady_klas — z ClassData Pawła).
		   Pierwszy raz wpisuje cel + trening (zastępuje wartości testowe PlayerStatsDefaults), potem tylko różnicę —
		   to, co dopisał ktoś inny (darmowy „+” w oknie ekwipunku), zostaje. Atrybut kontenera StatystykiKlasy = false
		   wyłącza ten punkt (zostają wartości testowe Pawła, trening dalej dopisuje);
		4. trening: Workspace/TreningProba/Sygnaly/PrzyrostStatystyki → przyrost do atrybutu statystyki (i do profilu),
		   z ponownym podłączeniem, gdy kontener treningu zostanie przebudowany w czasie gry;
		5. bohater walki (Sygnaly/Bohater): klasa z Class, poziom z Level, sześć statystyk z atrybutów, broń, pancerz
		   z przedmiotów i sloty ze wzoru dla poziomu (LogikaStanu.opisBohatera = tools/walka/wzorcowe.postac);
		6. wydawanie Złota (Sygnaly/WydajZloto, 17.11.2026): kwota od pakietu z listy D.wydatki.zrodla, nigdy poniżej
		   zera; za mało Złota = odmowa z brakującą kwotą; licznik wydatków na cel w profilu;
		7. pety w profilu (Sygnaly/Pety, swiat/pety_proba): "kup" = wydatek + kopia peta w jednym wywołaniu (bez
		   przerwy między nimi), "aktywny" = pet za graczem i jego premia do łupu (+% Złota / doświadczenia z walk —
		   doliczana tu, przy przyjęciu łupu; komunikat "premia" do klienta przy pokazaniu), "stan"; atrybuty gracza
		   D.pety.atrybut_aktywnego i D.pety.atrybut_liczby dla klientów;
		8. kara za przegraną (17.11.2026, realizacja propozycji D-098, czeka na zatwierdzenie): przegrana w walce
		   z kontenera D.kara.zrodla (las-pas, stary las, Bagno; tablica próby i tryb testowy TestBohater łupu nie
		   przysyłają) zabiera przy pokazaniu łupu D.kara.procent posiadanego Złota (w dół), najwyżej łup zwykłego
		   potwora na poziomie przeciwnika, nigdy poniżej zera; doświadczenie z przegranej (20% z silnika) zostaje;
		   komunikat "przegrana", kara, doświadczenie do klienta (napis jak premia peta). D.kara.procent = 0 albo
		   atrybut kontenera D.kara.atrybut_wylacznika = false wyłącza karę (liczba 0..1 w atrybucie = inny ułamek);
		9. modyfikatory bohatera (18.11.2026, Sygnaly/Modyfikatory — pety D-101, Kowal D-102): każdy pakiet ma jeden
		   wpis na gracza (statystyki, procent, lup, bron, pancerz, tarcza, pasywki, zaklecie); bohater walki i premia do łupu
		   biorą złożenie wszystkich; dawna premia peta (Pety "kup" / "aktywny") liczy się jako źródło "pety", dopóki
		   pakiet petów sam nie zawoła Modyfikatory;
		10. dane pakietów w profilu (Sygnaly/DanePakietu): profil.pakiety[pakiet] — tylko wartości dające się zapisać,
		   z limitem rozmiaru (pod przyszły zapis razem z resztą profilu; profil wersja 3);
		11. punkty statystyk (18.11.2026, realizacja propozycji D-097, czeka na zatwierdzenie): za poziom
		   D.punkty.na_poziom do rozdania (atrybut gracza D.punkty.atrybut) + D.punkty.auto_na_poziom rozdzielane samo;
		   zmiana sześciu atrybutów statystyk, której ten serwer nie zrobił (darmowy „+” StatPoints w oknie ekwipunku
		   Pawła — jego plików nie zmieniamy), zdejmuje punkt z puli, a bez punktu jest cofana (komunikat
		   "brak_punktow"). ROZWIĄZANIE TYMCZASOWE, dopóki „+” nie zawoła stanu gracza wprost. Atrybut kontenera
		   D.punkty.atrybut_wylacznika = false: jak przed D-097 (10 samo na poziom, „+” za darmo);
		12. Gemy bez płacenia (18.11.2026, D-099 ✅, liczby do zmiany): D.gemy.za_poziom za każdy awans i
		   D.gemy.za_straznika za pierwsze pokonanie strażnika każdego biomu (profil.straznicy; komunikat
		   "gemy_straznika" do klienta);
		13. „szczęście początkującego” (18.11.2026): dopóki gracz nie ma żadnej wygranej, wewnętrzne źródło
		   modyfikatorów D.poczatek.zrodlo mnoży jego sześć statystyk w walce ×(1 + D.poczatek.procent); bez napisu dla
		   gracza; wyłącznik: procent 0 albo atrybut kontenera D.poczatek.atrybut_wylacznika = false.
	Stan: JEDNA tabela profilu na gracza (pole wersja) — pod przyszły zapis (DataStore / ProfileStore; dziś tylko
	pamięć serwera, profil znika przy wyjściu gracza, jak atrybuty).

	Uchwyty (tylko serwer, BindableFunction w Sygnaly; bez kontenera StanGracza inne pakiety działają jak dawniej):
		Modyfikatory:Invoke("ustaw", gracz, zrodlo, mod) → { ok = true } | { ok = false, powod }; ("usun", gracz, zrodlo)
		                  → { ok = true, bylo }; ("czytaj", gracz) → złożenie { statystyki, procent, lup, bron, pancerz,
		                  tarcza, pasywki, zrodla, ok = true }
		DanePakietu:Invoke("czytaj", gracz, pakiet) → kopia tabeli albo nil; ("zapisz", gracz, pakiet, tabela | nil)
		                  → { ok = true } | { ok = false, powod }
		Bohater:Invoke(gracz) → opis postaci dla Silnik.symuluj albo nil
		PrzyznajLup:Invoke(gracz, { lup = walka.lup, wynik, czas = walka.czas, zrodlo = nazwa kontenera lasu,
		                            gatunek, poziom }) → { ok = true } | { ok = false, powod }
		SterowanieSerwera:Invoke("stan", gracz?) | ("zgodnosc") | ("publikuj", gracz?) | ("bohater", gracz?)
		                  | ("przyznaj", gracz, lup) — testy (przyznaj pokazuje łup od razu)
		WydajZloto:Invoke(gracz, { ile, zrodlo = nazwa kontenera, cel }) → { ok = true, zloto, ile, licznik }
		                  | { ok = false, powod ("za_malo" z brakuje, zloto, ile | "zla_kwota" | "zle_zrodlo" | …) }
		Pety:Invoke("kup", gracz, { ile, zrodlo, cel, pet, premia = { zloto, doswiadczenie } }) → jak WydajZloto
		                  + pet, nowy, kopie, aktywny | ("aktywny", gracz, { pet, premia } | { odstaw = true })
		                  → { ok, aktywny } | ("stan", gracz) → { ok, kopie, aktywny, premia, wydatki, zloto }
		                  | ("przychod", gracz, { ile, zrodlo, cel }) → { ok, zloto, ile } — 25.11.2026: Rybki
		                  spoza walki (zagroda petów; źródło z listy D.przychody.zrodla, dopisane jak łup, bez premii)
		                  | ("sprzedaj", gracz, { pety = { [id] = n }, ile, zrodlo, cel }) → { ok, zloto, ile, kopie }
		                  | { ok = false, powod ("nie_masz", pet | "aktywny", pet | walidacja) } — 26.11.2026: sprzedaż
		                  petów (swiat/pety_proba): kopie zabrane i Rybki dopisane jednym wywołaniem, bez przerwy;
		                  ostatniej kopii peta za graczem nie sprzedaje (PetAktywny zawsze wskazuje posiadanego peta)
	Zdalne/ZdarzeniaStanu (RemoteEvent): serwer → klient "awans", poziom, ile; "premia", zloto, doswiadczenie, pet
	(dodatek peta w pokazanym łupie); "przegrana", kara, doswiadczenie (kara za przegraną w pokazanym łupie);
	klient → serwer "pokaz" (bez liczb; najwyżej raz na D.publikacja.odstep_pokaz_s —
	może tylko przyspieszyć pokazanie łupu, nigdy go zmienić).
	Działa tylko w Roblox Studio: poza Studio usuwa cały kontener, jak pozostałe prototypy.
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneStanu"))
local L = require(moduly:WaitForChild("LogikaStanu"))
local modulZapisu = moduly:FindFirstChild("ZapisStanu")
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaStanu")
local sygnaly = kontener:WaitForChild("Sygnaly")
local bohaterF: BindableFunction = sygnaly:WaitForChild("Bohater")
local lupF: BindableFunction = sygnaly:WaitForChild("PrzyznajLup")
local sterowanie: BindableFunction = sygnaly:WaitForChild("SterowanieSerwera")
local wydajF: BindableFunction = sygnaly:WaitForChild("WydajZloto")
local petyF: BindableFunction = sygnaly:WaitForChild("Pety")
local modyfikatoryF: BindableFunction = sygnaly:WaitForChild("Modyfikatory")
local danePakietuF: BindableFunction = sygnaly:WaitForChild("DanePakietu")

local P = D.prefiks
local A = D.atrybuty
local ZRODLA = {}
for _, z in D.zrodla do
	ZRODLA[z] = true
end
local ZRODLA_KARY = {}
for _, z in D.kara.zrodla do
	ZRODLA_KARY[z] = true
end

local function teraz(): number
	return workspace:GetServerTimeNow()
end

local function dolicz(nazwa: string)
	kontener:SetAttribute(nazwa, (kontener:GetAttribute(nazwa) or 0) + 1)
end

kontener:SetAttribute("SerwerStanuGotowy", false)
for _, n in { "LicznikLupow", "LicznikPokazan", "LicznikAwansow", "LicznikBohaterow", "LicznikTreningu", "LicznikOdmow",
	"LicznikWydatkow", "LicznikPetow", "LicznikKar", "LicznikModyfikatorow", "LicznikDanychPakietow",
	"LicznikPrzyznanychPunktow", "LicznikRozdanychPunktow", "LicznikCofnietychPunktow", "LicznikGemowStraznika" } do
	kontener:SetAttribute(n, 0)
end

------------------------------------------------------------------ zapis postępu: obiekt przy starcie (README „Zapis postępu”)
local zapis = nil
do
	local a = kontener:GetAttribute(D.zapis.atrybut)
	local wlaczony = a == true or (a ~= false and D.zapis.wlaczony == true)
	local stan = "wyłączony"
	-- próba gry w Play (19.11.2026, D-110): znacznik ZapisProbaDo (os.time() końca, ustawia tools/zapis_prob.py w Edit
	-- tuż przed Play) → prawdziwego zapisu NIE czytamy i NIE piszemy (świeży gracz w pamięci, jak przed zapisem);
	-- z ZapisProbaMagazyn = true — osobny magazyn próby (tylko on zna atrapę błędów ZapisProbaBledy)
	local PR = D.zapis.proba
	local studio = game:GetService("RunService"):IsStudio()
	local doKiedy = kontener:GetAttribute(PR.atrybut_do)
	local wProbie = studio and type(doKiedy) == "number" and os.time() < doKiedy
	local magazynProby = wProbie and kontener:GetAttribute(PR.atrybut_magazynu) == true
	local nazwa = D.zapis.magazyn .. (if studio then D.zapis.przyrostek_studio else "")
	if magazynProby then
		wlaczony = true
		nazwa ..= PR.przyrostek
	elseif wProbie then
		wlaczony = false
		stan = "wyłączony (próba gry)"
	end
	if wlaczony and modulZapisu then
		local ok, magazyn, uslugi = pcall(function()
			local DSS = game:GetService("DataStoreService")
			local ds = DSS:GetDataStore(nazwa)
			if magazynProby then
				-- atrapa błędów usługi tylko w magazynie próby: ZapisProbaBledy = ile kolejnych wywołań pada
				local surowy = ds
				ds = {
					UpdateAsync = function(_, klucz: string, fn)
						local n = kontener:GetAttribute(PR.atrybut_bledow)
						if type(n) == "number" and n >= 1 then
							kontener:SetAttribute(PR.atrybut_bledow, n - 1)
							error("błąd magazynu na próbę (" .. PR.atrybut_bledow .. ")")
						end
						return surowy:UpdateAsync(klucz, fn)
					end,
				}
			end
			return ds, DSS
		end)
		if ok and magazyn then
			local Z = require(modulZapisu)
			zapis = Z.nowy(D, L, {
				magazyn = magazyn,
				zeton = game:GetService("HttpService"):GenerateGUID(false),
				teraz = os.time,
				opoznij = task.delay,
				log = function(tekst: string)
					warn(P .. "zapis: " .. tekst)
				end,
				budzet = function()
					local okB, b = pcall(function()
						return uslugi:GetRequestBudgetForRequestType(Enum.DataStoreRequestType.UpdateAsync)
					end)
					return if okB then b else nil
				end,
				los = if math.random then math.random else nil,
			})
			stan = if magazynProby then "włączony (magazyn próby)" else "włączony"
		else
			stan = "wyłączony (usługa danych niedostępna: " .. tostring(magazyn) .. ")"
			warn(P .. "zapis: " .. stan)
		end
	end
	kontener:SetAttribute("ZapisAktywny", zapis ~= nil)
	kontener:SetAttribute("ZapisStan", stan)
	kontener:SetAttribute("ZapisMagazyn", if zapis ~= nil then nazwa else nil)
end
for _, n in { "LicznikWczytan", "LicznikZapisow", "LicznikBledowZapisu", "LicznikBezZapisu" } do
	kontener:SetAttribute(n, 0)
end

------------------------------------------------------------------ zgodność logiki (te same przypadki co w Pythonie)
local function zgodnosc(): string
	local ok, n, bledy = L.sprawdzPrzypadki(D)
	local tekst
	if ok then
		tekst = string.format("OK %d/%d", n, n)
	else
		tekst = string.format("BŁĄD %d/%d: %s", n - #bledy, n, tostring(bledy[1]))
		warn(P .. "zgodność logiki: " .. tostring(bledy[1]))
	end
	kontener:SetAttribute("ZgodnoscLogikiStanu", tekst)
	return tekst
end
zgodnosc()

------------------------------------------------------------------ rozkłady klas: wzorcowe albo ClassData Pawła (tylko odczyt)
-- 18.11.2026 (pytanie 56, odpowiedź Karola „b”, czeka na Pawła): D.rozklady_klas.tryb = "wzorcowe" — walka i punkty
-- według D.rozklady (tools/walka/wzorcowe.py), profil z ClassData tylko na karcie wyboru klasy; "classdata" — jak
-- dotąd, punkty według ClassData. Atrybut kontenera D.rozklady_klas.atrybut przełącza w czasie gry.
local rozkladyCD = {}
for _, k in D.klasy do
	rozkladyCD[k] = D.rozklady[k]
end
local inneWClassData = {} -- klasy, których profil z ClassData różni się od wzorcowego
local opisClassData = "dane (ClassData jeszcze nie wczytany)"

local function trybRozkladow(): string
	local v = kontener:GetAttribute(D.rozklady_klas.atrybut)
	if v == "wzorcowe" or v == "classdata" then
		return v
	end
	return D.rozklady_klas.tryb
end

local function rozkladKlasy(klasa: string)
	if trybRozkladow() == "classdata" then
		return rozkladyCD[klasa]
	end
	return D.rozklady[klasa]
end

local function opisRozkladow(): string
	if trybRozkladow() == "classdata" then
		return opisClassData
	end
	if #inneWClassData > 0 then
		return "wzorcowe (tools/walka); karta klasy pokazuje profil ClassData — inny dla: " .. table.concat(inneWClassData, ", ")
	end
	return "wzorcowe (tools/walka)"
end

local function wczytajRozklady(): string
	local folder = ReplicatedStorage:WaitForChild(D.klasy_pawla.folder, D.klasy_pawla.czekaj_s)
	local m = folder and folder:WaitForChild(D.klasy_pawla.modul, D.klasy_pawla.czekaj_s)
	if not m or not m:IsA("ModuleScript") then
		return "dane (brak ClassData)"
	end
	local ok, CD = pcall(require, m)
	if not ok or type(CD) ~= "table" or type(CD.Classes) ~= "table" then
		return "dane (ClassData nieczytelny: " .. tostring(CD) .. ")"
	end
	local n, rozne = 0, {}
	for _, c in CD.Classes do
		local klasa = type(c) == "table" and D.klasy_gracza[c.id]
		if klasa then
			local r, powod = L.rozkladZClassData(D, c.stats)
			if r then
				rozkladyCD[klasa] = r
				n += 1
				if not L.rowne(r, D.rozklady[klasa]) then
					table.insert(rozne, klasa)
				end
			else
				warn(P .. "ClassData " .. tostring(c.id) .. ": " .. powod .. " — rozkład z danych")
			end
		end
	end
	inneWClassData = rozne
	if #rozne > 0 then
		return "ClassData (" .. n .. " klas; INNE NIŻ WZORCOWE: " .. table.concat(rozne, ", ") .. ")"
	end
	return "ClassData (" .. n .. " klas)"
end
opisClassData = wczytajRozklady()

-- ostrzeżenie „balans!” tylko wtedy, gdy walka naprawdę idzie według ClassData różnego od wzorca
local function ogloscRozklady()
	kontener:SetAttribute("RozkladyZ", opisRozkladow())
	if trybRozkladow() == "classdata" and #inneWClassData > 0 then
		warn(P .. "rozkłady z ClassData różne od wzorcowych (balans!): " .. table.concat(inneWClassData, ", "))
	end
end
ogloscRozklady()

------------------------------------------------------------------ profil i atrybuty
local profile: { [Player]: any } = {}

local function profil(gracz: Player)
	local p = profile[gracz]
	if not p then
		p = L.nowyProfil(D)
		p.oczekujace = {}
		profile[gracz] = p
	end
	return p
end

local function liczba(gracz: Player, nazwa: string, domyslna: number): number
	local v = gracz:GetAttribute(nazwa)
	if type(v) == "number" and v == v and v > -math.huge and v < math.huge then
		return v
	end
	return domyslna
end

local function klasaGracza(gracz: Player): string
	local klasa = L.klasaSilnika(D, gracz:GetAttribute(A.klasa))
	return klasa
end

local function poziomGracza(gracz: Player): number
	return L.poziomZ(D, gracz:GetAttribute(A.poziom))
end

local function statystykiWlaczone(): boolean
	return kontener:GetAttribute("StatystykiKlasy") ~= false
end

-- punkty statystyk do rozdania (18.11.2026, propozycja D-097): włączone, gdy statystyki klasy są włączone i atrybut
-- kontenera D.punkty.atrybut_wylacznika nie jest false (false = jak przed D-097: 10 samo na poziom, darmowy „+”)
local function punktyWlaczone(): boolean
	return statystykiWlaczone() and kontener:GetAttribute(D.punkty.atrybut_wylacznika) ~= false
end

-- ostatnie wartości sześciu atrybutów statystyk, które serwer zapisał albo przyjął (pilnowanie „+”; nie w profilu)
local znane: { [Player]: { [string]: number } } = {}

local function ustawStatystyke(gracz: Player, s: string, v: number)
	local z = znane[gracz]
	if not z then
		z = {}
		znane[gracz] = z
	end
	z[s] = v
	if gracz:GetAttribute(D.atrybuty_statystyk[s]) ~= v then
		gracz:SetAttribute(D.atrybuty_statystyk[s], v)
	end
end

local function zapamietajStatystyki(gracz: Player)
	local z = {}
	for _, s in D.statystyki do
		z[s] = L.statystykaZ(D, gracz:GetAttribute(D.atrybuty_statystyk[s]))
	end
	znane[gracz] = z
end

-- lustro atrybutów w profilu (pod przyszły zapis); atrybuty są prawdą, bo piszą je też skrypty Pawła
local function zbierz(gracz: Player)
	local p = profil(gracz)
	p.klasa = klasaGracza(gracz)
	p.poziom = poziomGracza(gracz)
	p.xp = liczba(gracz, A.xp, 0)
	p.zloto = liczba(gracz, A.zloto, 0)
	p.gemy = liczba(gracz, A.gemy, 0)
	p.shardy = liczba(gracz, A.shardy, 0)
	local id = gracz:GetAttribute(A.klasa)
	p.idKlasy = if type(id) == "string" and D.klasy_gracza[id] ~= nil then id else nil
	return p
end

-- sześć atrybutów: rozkład klasy dla puli poziomu (pierwszy raz cel + trening, potem różnica)
local function zastosujBaze(gracz: Player)
	if not statystykiWlaczone() or not gracz.Parent then
		return
	end
	local p = profil(gracz)
	local klasa = klasaGracza(gracz)
	local poziom = poziomGracza(gracz)
	local tryb = punktyWlaczone()
	local trybR = trybRozkladow()
	if p.baza and p.baza.klasa == klasa and p.baza.poziom == poziom and p.baza.tryb == tryb and p.baza.rozklady == trybR then
		return
	end
	-- samo rozdzielana część puli (z punktami do rozdania: 30 + 5 na poziom; bez: 30 + 10); rozdane punkty i trening
	-- są w obecnych atrybutach i zostają (noweStatystyki dopisuje tylko różnicę celu)
	local cel = L.rozdziel(D, rozkladKlasy(klasa), L.pulaSama(D, poziom, tryb))
	local obecne = {}
	for _, s in D.statystyki do
		obecne[s] = gracz:GetAttribute(D.atrybuty_statystyk[s])
	end
	local dodatki = {}
	for _, s in D.statystyki do
		dodatki[s] = p.wytrenowane[s] + p.punkty.rozdane[s]
	end
	local nowe = L.noweStatystyki(D, obecne, if p.baza then p.baza.st else nil, cel, dodatki)
	p.baza = { klasa = klasa, poziom = poziom, st = cel, tryb = tryb, rozklady = trybR }
	for _, s in D.statystyki do
		ustawStatystyke(gracz, s, nowe[s])
	end
end

local function dopisz(gracz: Player, nazwa: string, ile: number)
	if ile > 0 then
		gracz:SetAttribute(nazwa, math.min(liczba(gracz, nazwa, 0) + ile, D.limity.waluta_maks))
	end
end

-- punkty i Gemy (D-099) za poziomy powyżej najwyższego, za który już są (awans z łupu albo Level ustawiony ręcznie
-- w teście); spadek poziomu niczego nie zabiera; przy wyłączonych punktach są tylko Gemy
local function przyznajPunkty(gracz: Player)
	local p = profil(gracz)
	local poziom = poziomGracza(gracz)
	if poziom > p.punkty.poziom then
		-- Gemy za awans (D-099): niezależnie od wyłącznika punktów
		dopisz(gracz, A.gemy, (poziom - p.punkty.poziom) * D.gemy.za_poziom)
		if punktyWlaczone() then
			p.punkty.pula += (poziom - p.punkty.poziom) * D.punkty.na_poziom
			dolicz("LicznikPrzyznanychPunktow")
		end
		p.punkty.poziom = poziom -- najwyższy poziom, za który już są punkty i Gemy (spadek i powrót niczego nie dają)
	end
	if D.punkty.na_poziom == 0 and p.punkty.pula > 0 then
		-- agent Karola, 27.11 (dźwignia A, BALANS_2711.md): punkty do rozdania ze starych zapisów nie mają już przycisku —
		-- ich wartość daje teraz pula rozdzielana samo (10 na poziom), więc stara pula znika (licznik na dole schowany)
		p.punkty.pula = 0
	end
	local v = if punktyWlaczone() then p.punkty.pula else nil
	if gracz:GetAttribute(D.punkty.atrybut) ~= v then
		gracz:SetAttribute(D.punkty.atrybut, v)
	end
end

-- zmiana atrybutu statystyki, której nie zrobił ten serwer (np. darmowy „+” StatPoints w oknie ekwipunku Pawła):
-- z punktem w puli — przyjęta, punkt zdjęty; bez punktu albo spadek — cofnięta (i komunikat "brak_punktow")
local function pilnujStatystyki(gracz: Player, s: string)
	if not gracz.Parent then
		return
	end
	local z = znane[gracz]
	local v = gracz:GetAttribute(D.atrybuty_statystyk[s])
	if not punktyWlaczone() or not z or z[s] == nil then
		if z then
			z[s] = L.statystykaZ(D, v)
		end
		return
	end
	if v == z[s] then
		return
	end
	local p = profil(gracz)
	local w, pula, wynik = L.zmianaStatystyki(D, z[s], v, p.punkty.pula)
	if wynik == "ok" then
		local d = w - z[s]
		z[s] = w
		if v ~= w then
			gracz:SetAttribute(D.atrybuty_statystyk[s], w)
		end
		if d > 0 then
			p.punkty.pula = pula
			p.punkty.rozdane[s] += d
			gracz:SetAttribute(D.punkty.atrybut, pula)
			dolicz("LicznikRozdanychPunktow")
		end
		return
	end
	ustawStatystyke(gracz, s, z[s])
	dolicz("LicznikCofnietychPunktow")
	if wynik == "brak_punktow" then
		zdarzenia:FireClient(gracz, "brak_punktow")
	end
end

local function ustawXpMax(gracz: Player)
	local cel = L.xpDoNastepnego(D, poziomGracza(gracz))
	if gracz:GetAttribute(A.xp_max) ~= cel then
		gracz:SetAttribute(A.xp_max, cel)
	end
end

------------------------------------------------------------------ modyfikatory bohatera (18.11.2026, Sygnaly/Modyfikatory)
-- Każdy pakiet (źródło: "pety", "kowal"…) ma jeden wpis na gracza; bohater walki i premia do łupu biorą złożenie
-- (LogikaStanu.zlozModyfikatory). Wpisy żyją w pamięci serwera, nie w profilu: pakiety odtwarzają je ze swoich danych
-- (Sygnaly/DanePakietu) po wejściu gracza. Zgodność wstecz: dopóki pakiet petów nie zawoła Modyfikatory dla źródła
-- D.modyfikatory.zrodlo_pety, premia peta z Pety("kup" / "aktywny") (profil.pety.premia) liczy się jako to źródło.
local modyfikatory: { [Player]: any } = {}

local function wpisy(gracz: Player)
	local m = modyfikatory[gracz]
	if not m then
		m = { lista = {}, przejete = false }
		modyfikatory[gracz] = m
	end
	return m
end

-- lista wpisów posortowana według nazwy źródła (+ dawna premia peta, gdy źródło petów nie jest jeszcze przejęte);
-- kolejność decyduje tylko o zaklęciu broni: przy kilku źródłach z zaklęciem wygrywa pierwsze według nazwy
local function listaModow(gracz: Player)
	local m = wpisy(gracz)
	local pary = {}
	for _, w in m.lista do
		table.insert(pary, w)
	end
	local p = profil(gracz)
	if not m.przejete then
		if p.pety.premia.zloto + p.pety.premia.doswiadczenie > 0 then
			table.insert(pary, { zrodlo = D.modyfikatory.zrodlo_pety, mod = { lup = p.pety.premia } })
		end
	end
	-- „szczęście początkującego”: do pierwszej wygranej sześć statystyk ×(1 + D.poczatek.procent) — pierwsza walka
	-- praktycznie pewna; atrybut kontenera D.poczatek.atrybut_wylacznika = false albo procent 0 wyłącza
	if p.walki.wygrane == 0 and D.poczatek.procent > 0 and kontener:GetAttribute(D.poczatek.atrybut_wylacznika) ~= false then
		local procent = {}
		for _, s in D.statystyki do
			procent[D.atrybuty_statystyk[s]] = D.poczatek.procent
		end
		table.insert(pary, { zrodlo = D.poczatek.zrodlo, mod = { procent = procent } })
	end
	for i = 2, #pary do -- sortowanie przez wstawianie (kilka wpisów)
		local x = pary[i]
		local j = i - 1
		while j >= 1 and pary[j].zrodlo > x.zrodlo do
			pary[j + 1] = pary[j]
			j -= 1
		end
		pary[j + 1] = x
	end
	local lista, zrodla = {}, {}
	for _, w in pary do
		table.insert(lista, w.mod)
		table.insert(zrodla, w.zrodlo)
	end
	return lista, zrodla
end

local function zlozenie(gracz: Player)
	local lista, zrodla = listaModow(gracz)
	return L.zlozModyfikatory(D, lista), zrodla
end

-- premia do łupu samego źródła petów (komunikat "premia" dla klienta petów mówi „od peta”)
local function lupPetow(gracz: Player)
	local m = wpisy(gracz)
	for _, w in m.lista do
		if w.zrodlo == D.modyfikatory.zrodlo_pety then
			return L.zlozModyfikatory(D, { w.mod }).lup
		end
	end
	if not m.przejete then
		return profil(gracz).pety.premia
	end
	return { zloto = 0, doswiadczenie = 0 }
end

------------------------------------------------------------------ kara za przegraną (17.11.2026, propozycja D-098)
-- ułamek Złota z D.kara.procent; atrybut kontenera D.kara.atrybut_wylacznika: false = wyłączona, liczba = inny ułamek
-- (próby w Studio), brak = z danych
local function procentKary(): number
	local v = kontener:GetAttribute(D.kara.atrybut_wylacznika)
	if v == false then
		return 0
	elseif type(v) == "number" and v == v and v >= 0 and v <= 1 then
		return v
	end
	return D.kara.procent
end

------------------------------------------------------------------ łup: przyjęcie i pokazanie
-- pokazuje (atrybuty) łupy gotowe do pokazania: po czasie albo — wymus — wszystkie starsze niż minWiek
-- (doCzasu: tylko łupy przyjęte nie później niż ta chwila — dokończenie zgłoszenia "pokaz", D-107)
local function publikuj(gracz: Player, wymus: boolean, minWiek: number, doCzasu: number?)
	local p = profile[gracz]
	if not p or not gracz.Parent or #p.oczekujace == 0 then
		return 0
	end
	local t = teraz()
	local gotowe, reszta, przegrane = {}, {}, {}
	local gemyStraznika = 0
	local premiaZ, premiaXp, premiaPet = 0, 0, nil
	for _, o in p.oczekujace do
		if t >= o.pokazOd or (wymus and t - o.przyjeto >= minWiek and (doCzasu == nil or o.przyjeto <= doCzasu)) then
			table.insert(gotowe, o.lup)
			if o.premia then
				premiaZ += o.premia.zloto
				premiaXp += o.premia.doswiadczenie
				premiaPet = o.pet
			end
			if o.kara then
				table.insert(przegrane, o)
			end
			if o.gemyStraznika then
				gemyStraznika += o.gemyStraznika
			end
		else
			table.insert(reszta, o)
		end
	end
	if #gotowe == 0 then
		return 0
	end
	p.oczekujace = reszta
	local suma = L.sumaLupow(D, gotowe)
	dopisz(gracz, A.zloto, suma.zloto)
	-- kara za przegraną: od Złota w chwili pokazania (po łupie z tej samej paczki), nigdy poniżej zera
	local kara, xpPrzegranych = 0, 0
	for _, o in przegrane do
		local k = L.karaPrzegranej(D, gracz:GetAttribute(A.zloto), o.kara.poziom, o.kara.procent)
		if k > 0 then
			local po = L.wydaj(D, gracz:GetAttribute(A.zloto), k)
			gracz:SetAttribute(A.zloto, po)
			kara += k
		end
		xpPrzegranych += o.lup.doswiadczenie
	end
	if #przegrane > 0 then
		kontener:SetAttribute("LicznikKar", (kontener:GetAttribute("LicznikKar") or 0) + #przegrane)
		kontener:SetAttribute("OstatniaKara", string.format("%s:-%dz:+%dxp", gracz.Name, kara, xpPrzegranych))
	end
	dopisz(gracz, A.gemy, suma.gemy)
	dopisz(gracz, A.shardy, suma.shard_ewolucji)
	for kraina, n in suma.tokeny do
		dopisz(gracz, A.tokeny_prefiks .. kraina, n)
		p.tokeny[kraina] = (p.tokeny[kraina] or 0) + n
	end
	local poziom, xp, ile = L.awans(D, poziomGracza(gracz), liczba(gracz, A.xp, 0), suma.doswiadczenie)
	gracz:SetAttribute(A.xp, xp)
	if ile > 0 then
		gracz:SetAttribute(A.poziom, poziom)
	end
	ustawXpMax(gracz)
	zastosujBaze(gracz)
	przyznajPunkty(gracz)
	zbierz(gracz)
	dolicz("LicznikPokazan")
	if ile > 0 then
		p.awanse += ile
		kontener:SetAttribute("LicznikAwansow", (kontener:GetAttribute("LicznikAwansow") or 0) + ile)
		zdarzenia:FireClient(gracz, "awans", poziom, ile)
	end
	if premiaZ + premiaXp > 0 then
		zdarzenia:FireClient(gracz, "premia", premiaZ, premiaXp, premiaPet)
	end
	if #przegrane > 0 then
		zdarzenia:FireClient(gracz, "przegrana", kara, xpPrzegranych)
	end
	if gemyStraznika > 0 then
		zdarzenia:FireClient(gracz, "gemy_straznika", gemyStraznika)
	end
	kontener:SetAttribute("OstatniePokazanie", string.format("%s:+%dz:+%dxp:poz.%d", gracz.Name, suma.zloto,
		suma.doswiadczenie, poziom))
	return #gotowe
end

local function odmowaLupu(powod: string)
	dolicz("LicznikOdmow")
	kontener:SetAttribute("OstatniaOdmowa", powod)
	return { ok = false, powod = powod }
end

local function przyjmijLup(gracz: any, info: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or gracz.Parent ~= Players then
		return odmowaLupu("zly_gracz")
	end
	if gracz:GetAttribute("StanGraczaWczytany") == false then
		return odmowaLupu("wczytywanie") -- zapis postępu: profil jeszcze się wczytuje (walka bez łupu)
	end
	if type(info) ~= "table" or type(info.zrodlo) ~= "string" or not ZRODLA[info.zrodlo] then
		return odmowaLupu("zle_zrodlo")
	end
	local lup, powod = L.czystyLup(D, info.lup)
	if not lup then
		return odmowaLupu(powod)
	end
	local czas = info.czas
	if type(czas) ~= "number" or czas ~= czas or czas < 0 or czas > D.limity.czas_walki_maks then
		czas = 0
	end
	local p = profil(gracz)
	if #p.oczekujace >= D.limity.oczekujace_maks then
		publikuj(gracz, true, 0)
	end
	-- premia do łupu ze złożenia modyfikatorów (pet, Kowal…): +% Złota i doświadczenia z tej walki, liczona tu i teraz;
	-- część petów osobno — do komunikatu "premia" (klient petów pisze „od peta”)
	-- Gemy za pierwsze pokonanie strażnika biomu (D-099): raz na gatunek strażnika, tylko walki biomów
	local gemyStraznika = 0
	if info.wynik == "wygrana" and ZRODLA_KARY[info.zrodlo] and L.czyStraznik(D, info.gatunek)
		and not p.straznicy[info.gatunek] then
		p.straznicy[info.gatunek] = true
		gemyStraznika = D.gemy.za_straznika
		lup.gemy += gemyStraznika
		dolicz("LicznikGemowStraznika")
	end
	local zl = zlozenie(gracz)
	local dodatek = L.premiaLupu(D, lup, zl.lup)
	local dodatekPeta = L.premiaLupu(D, lup, lupPetow(gracz))
	lup.zloto += dodatek.zloto
	lup.doswiadczenie += dodatek.doswiadczenie
	local t = teraz()
	-- kara za przegraną (D-098): tylko walki lasu-pasa, starego lasu i Bagna; ułamek ustalony przy przyjęciu, Złoto
	-- zabierane przy pokazaniu; poziom przeciwnika od serwera potworów (brak → poziom gracza)
	local kara = nil
	if info.wynik == "przegrana" and ZRODLA_KARY[info.zrodlo] then
		local procent = procentKary()
		if procent > 0 then
			kara = { procent = procent, poziom = if type(info.poziom) == "number" then info.poziom else poziomGracza(gracz) }
		end
	end
	table.insert(p.oczekujace, { lup = lup, przyjeto = t, pokazOd = t + czas + D.publikacja.zapas_s,
		premia = if dodatekPeta.zloto + dodatekPeta.doswiadczenie > 0 then dodatekPeta else nil, pet = p.pety.aktywny,
		kara = kara, gemyStraznika = if gemyStraznika > 0 then gemyStraznika else nil })
	if info.wynik == "wygrana" then
		p.walki.wygrane += 1
	else
		p.walki.przegrane += 1
	end
	dolicz("LicznikLupow")
	kontener:SetAttribute("OstatniLup", string.format("%s:%s:%s:%dz:%dxp", gracz.Name, info.zrodlo, tostring(info.wynik),
		lup.zloto, lup.doswiadczenie))
	task.delay(czas + D.publikacja.zapas_s + 0.1, function()
		publikuj(gracz, false, 0)
	end)
	return { ok = true }
end

lupF.OnInvoke = function(gracz: any, info: any)
	local ok, wynik = pcall(przyjmijLup, gracz, info)
	if ok then
		return wynik
	end
	warn(P .. "PrzyznajLup: " .. tostring(wynik))
	return { ok = false, powod = "blad" }
end

------------------------------------------------------------------ wydatki Złota i pety (17.11.2026, swiat/pety_proba)
-- Bez przerw (żadnego czekania) między sprawdzeniem a zapisem: dwa wywołania naraz nie wydadzą tego samego Złota.
local function graczOk(gracz: any): boolean
	-- zapis postępu: do wczytania profilu (atrybut StanGraczaWczytany = false) wydatki, pety, modyfikatory i dane
	-- pakietów odmawiają — pakiety czekają na StanGraczaWczytany ~= false
	return typeof(gracz) == "Instance" and gracz:IsA("Player") and gracz.Parent == Players
		and gracz:GetAttribute("StanGraczaWczytany") ~= false
end

local function skopiuj(t: any): any
	if type(t) ~= "table" then
		return t
	end
	local w = {}
	for k, v in t do
		w[k] = skopiuj(v)
	end
	return w
end

local function publikujPety(gracz: Player)
	local p = profil(gracz)
	local suma = 0
	for _, n in p.pety.kopie do
		suma += n
	end
	gracz:SetAttribute(D.pety.atrybut_liczby, suma)
	gracz:SetAttribute(D.pety.atrybut_aktywnego, p.pety.aktywny)
end

local function wydajZloto(gracz: any, info: any)
	if not graczOk(gracz) then
		return { ok = false, powod = "zly_gracz" }
	end
	local w, powod = L.czystyWydatek(D, info)
	if not w then
		return { ok = false, powod = powod }
	end
	-- łup zakończonej walki najpierw do atrybutów: gracz wydaje to, co widzi w HUD
	publikuj(gracz, true, D.publikacja.min_s)
	local zloto, brak = L.wydaj(D, gracz:GetAttribute(A.zloto), w.ile)
	if brak > 0 then
		return { ok = false, powod = "za_malo", brakuje = brak, zloto = zloto, ile = w.ile }
	end
	gracz:SetAttribute(A.zloto, zloto)
	local p = profil(gracz)
	p.zloto = zloto
	p.wydatki[w.cel] = (p.wydatki[w.cel] or 0) + 1
	dolicz("LicznikWydatkow")
	kontener:SetAttribute("OstatniWydatek", string.format("%s:%s:%s:%dz", gracz.Name, w.zrodlo, w.cel, w.ile))
	return { ok = true, zloto = zloto, ile = w.ile, licznik = p.wydatki[w.cel] }
end

wydajF.OnInvoke = function(gracz: any, info: any)
	local ok, wynik = pcall(wydajZloto, gracz, info)
	if ok then
		return wynik
	end
	warn(P .. "WydajZloto: " .. tostring(wynik))
	return { ok = false, powod = "blad" }
end

local function pety(polecenie: any, gracz: any, info: any)
	if not graczOk(gracz) then
		return { ok = false, powod = "zly_gracz" }
	end
	local p = profil(gracz)
	if polecenie == "stan" then
		return { ok = true, kopie = skopiuj(p.pety.kopie), aktywny = p.pety.aktywny, premia = skopiuj(p.pety.premia),
			wydatki = skopiuj(p.wydatki), zloto = liczba(gracz, A.zloto, 0) }
	end
	if type(info) ~= "table" then
		return { ok = false, powod = "zle_dane" }
	end
	if polecenie == "kup" then
		if not L.nazwaOk(D, info.pet) then
			return { ok = false, powod = "zly_pet" }
		end
		local premia, powodPremii = L.czystaPremia(D, info.premia)
		if not premia then
			return { ok = false, powod = powodPremii }
		end
		local rodzajow = 0
		for _ in p.pety.kopie do
			rodzajow += 1
		end
		local nowy = p.pety.kopie[info.pet] == nil
		if (nowy and rodzajow >= D.pety.rodzajow_maks) or (not nowy and p.pety.kopie[info.pet] >= D.pety.kopii_maks) then
			return { ok = false, powod = "limit_petow" }
		end
		local w = wydajZloto(gracz, info)
		if not w.ok then
			return w
		end
		p.pety.kopie[info.pet] = (p.pety.kopie[info.pet] or 0) + 1
		if p.pety.aktywny == nil then
			p.pety.aktywny = info.pet
			p.pety.premia = premia
		end
		publikujPety(gracz)
		dolicz("LicznikPetow")
		w.pet = info.pet
		w.nowy = nowy
		w.kopie = p.pety.kopie[info.pet]
		w.aktywny = p.pety.aktywny
		return w
	elseif polecenie == "aktywny" then
		if info.odstaw == true then
			p.pety.aktywny = nil
			p.pety.premia = { zloto = 0, doswiadczenie = 0 }
		else
			if not L.nazwaOk(D, info.pet) or p.pety.kopie[info.pet] == nil then
				return { ok = false, powod = "nie_masz" }
			end
			local premia, powodPremii = L.czystaPremia(D, info.premia)
			if not premia then
				return { ok = false, powod = powodPremii }
			end
			p.pety.aktywny = info.pet
			p.pety.premia = premia
		end
		publikujPety(gracz)
		return { ok = true, aktywny = p.pety.aktywny }
	elseif polecenie == "przychod" then
		-- Rybki spoza walki (25.11.2026, swiat/pety_proba — pety stojące w zagrodzie; kwotę liczy serwer petów co kilka
		-- sekund): kwota i źródło sprawdzone (D.przychody), dopisane do atrybutu Złota jak łup — bez premii z
		-- modyfikatorów, bez kary i bez licznika walk; profil od razu (zapis postępu bierze p.zloto)
		local w, powod = L.czystyPrzychod(D, info)
		if not w then
			return { ok = false, powod = powod }
		end
		dopisz(gracz, A.zloto, w.ile)
		p.zloto = liczba(gracz, A.zloto, 0)
		dolicz("LicznikPrzychodow")
		kontener:SetAttribute("OstatniPrzychod", string.format("%s:%s:%s:+%dz", gracz.Name, w.zrodlo, w.cel, w.ile))
		return { ok = true, zloto = p.zloto, ile = w.ile }
	elseif polecenie == "sprzedaj" then
		-- 26.11.2026 (swiat/pety_proba, sprzedaż petów): najpierw wszystko sprawdzone, potem kopie i Rybki razem —
		-- bez przerwy, więc dwa wywołania naraz nie sprzedadzą tej samej kopii
		local w, powod = L.czystaSprzedaz(D, info)
		if not w then
			return { ok = false, powod = powod }
		end
		for id, n in w.pety do
			local ma = p.pety.kopie[id] or 0
			if ma < n then
				return { ok = false, powod = "nie_masz", pet = id }
			end
			if ma == n and p.pety.aktywny == id then
				return { ok = false, powod = "aktywny", pet = id }
			end
		end
		for id, n in w.pety do
			local zostaje = p.pety.kopie[id] - n
			p.pety.kopie[id] = if zostaje > 0 then zostaje else nil
		end
		dopisz(gracz, A.zloto, w.ile)
		p.zloto = liczba(gracz, A.zloto, 0)
		publikujPety(gracz)
		dolicz("LicznikSprzedazy")
		kontener:SetAttribute("OstatniaSprzedaz", string.format("%s:%s:+%dz", gracz.Name, w.zrodlo, w.ile))
		return { ok = true, zloto = p.zloto, ile = w.ile, kopie = skopiuj(p.pety.kopie) }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end

petyF.OnInvoke = function(polecenie: any, gracz: any, info: any)
	local ok, wynik = pcall(pety, polecenie, gracz, info)
	if ok then
		return wynik
	end
	warn(P .. "Pety: " .. tostring(wynik))
	return { ok = false, powod = "blad" }
end

------------------------------------------------------------------ Sygnaly/Modyfikatory i Sygnaly/DanePakietu (18.11.2026)
local function modyfikatoryWywolanie(polecenie: any, gracz: any, zrodlo: any, mod: any)
	if not graczOk(gracz) then
		return { ok = false, powod = "zly_gracz" }
	end
	if polecenie == "czytaj" then
		local zl, zrodla = zlozenie(gracz)
		zl.zrodla = zrodla
		zl.ok = true
		return zl
	end
	if not L.nazwaOk(D, zrodlo) then
		return { ok = false, powod = "zle_zrodlo" }
	end
	local m = wpisy(gracz)
	if polecenie == "ustaw" then
		local w, powod = L.czystyModyfikator(D, mod)
		if not w then
			return { ok = false, powod = powod }
		end
		for _, wpis in m.lista do
			if wpis.zrodlo == zrodlo then
				wpis.mod = w
				if zrodlo == D.modyfikatory.zrodlo_pety then
					m.przejete = true
				end
				dolicz("LicznikModyfikatorow")
				return { ok = true }
			end
		end
		if #m.lista >= D.modyfikatory.zrodel_maks then
			return { ok = false, powod = "za_duzo_zrodel" }
		end
		table.insert(m.lista, { zrodlo = zrodlo, mod = w })
		if zrodlo == D.modyfikatory.zrodlo_pety then
			m.przejete = true
		end
		dolicz("LicznikModyfikatorow")
		return { ok = true }
	elseif polecenie == "usun" then
		local bylo = false
		for i, wpis in m.lista do
			if wpis.zrodlo == zrodlo then
				table.remove(m.lista, i)
				bylo = true
				break
			end
		end
		if zrodlo == D.modyfikatory.zrodlo_pety then
			m.przejete = true
		end
		return { ok = true, bylo = bylo }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end

modyfikatoryF.OnInvoke = function(polecenie: any, gracz: any, zrodlo: any, mod: any)
	local ok, wynik = pcall(modyfikatoryWywolanie, polecenie, gracz, zrodlo, mod)
	if ok then
		return wynik
	end
	warn(P .. "Modyfikatory: " .. tostring(wynik))
	return { ok = false, powod = "blad" }
end

local function danePakietu(polecenie: any, gracz: any, pakiet: any, tabela: any)
	if not graczOk(gracz) then
		return if polecenie == "czytaj" then nil else { ok = false, powod = "zly_gracz" }
	end
	if not L.nazwaOk(D, pakiet) then
		return if polecenie == "czytaj" then nil else { ok = false, powod = "zly_pakiet" }
	end
	local p = profil(gracz)
	if polecenie == "czytaj" then
		return skopiuj(p.pakiety[pakiet])
	elseif polecenie == "zapisz" then
		if tabela == nil then
			p.pakiety[pakiet] = nil
			return { ok = true }
		end
		local w, powod = L.czysteDanePakietu(D, tabela)
		if not w then
			return { ok = false, powod = powod }
		end
		if p.pakiety[pakiet] == nil then
			local n = 0
			for _ in p.pakiety do
				n += 1
			end
			if n >= D.pakiety.pakietow_maks then
				return { ok = false, powod = "za_duzo_pakietow" }
			end
		end
		p.pakiety[pakiet] = w
		dolicz("LicznikDanychPakietow")
		return { ok = true }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end

danePakietuF.OnInvoke = function(polecenie: any, gracz: any, pakiet: any, tabela: any)
	local ok, wynik = pcall(danePakietu, polecenie, gracz, pakiet, tabela)
	if ok then
		return wynik
	end
	warn(P .. "DanePakietu: " .. tostring(wynik))
	return if polecenie == "czytaj" then nil else { ok = false, powod = "blad" }
end

------------------------------------------------------------------ bohater walki
local function bohater(gracz: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or gracz.Parent ~= Players
		or gracz:GetAttribute("StanGraczaWczytany") == false then
		return nil
	end
	-- łup poprzedniej walki przed następną (gracz zaczyna walkę, gdy ekran wyniku już zniknął)
	publikuj(gracz, true, D.publikacja.min_s)
	local p = profil(gracz)
	if not p.baza then
		zastosujBaze(gracz)
	end
	local klasa = klasaGracza(gracz)
	local poziom = poziomGracza(gracz)
	local zapas = L.rozdziel(D, rozkladKlasy(klasa), L.pulaSama(D, poziom, punktyWlaczone()))
	local st = {}
	for _, s in D.statystyki do
		st[s] = L.statystykaZ(D, gracz:GetAttribute(D.atrybuty_statystyk[s]))
			or (zapas[s] + p.wytrenowane[s] + p.punkty.rozdane[s])
	end
	dolicz("LicznikBohaterow")
	kontener:SetAttribute("OstatniBohater", string.format("%s:%s:%d", gracz.Name, klasa, poziom))
	-- modyfikatory wszystkich źródeł (pety, Kowal…); bez nich opis jest dokładnie postacią wzorcową dla tych statystyk
	return L.opisZModyfikatorami(D, L.opisBohatera(D, klasa, poziom, st), (zlozenie(gracz)))
end

bohaterF.OnInvoke = function(gracz: any)
	local ok, wynik = pcall(bohater, gracz)
	if ok then
		return wynik
	end
	warn(P .. "Bohater: " .. tostring(wynik))
	return nil
end

------------------------------------------------------------------ trening (Workspace/TreningProba — tylko słuchamy)
local function przyrostTreningu(gracz: any, info: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or gracz.Parent ~= Players then
		return
	end
	local w = L.czystyPrzyrost(D, info)
	if not w then
		return
	end
	local s, n = w[1], w[2]
	local p = profil(gracz)
	p.wytrenowane[s] += n
	gracz:SetAttribute(D.trening.prefiks_wytrenowanych .. D.atrybuty_statystyk[s], p.wytrenowane[s])
	local nazwa = D.atrybuty_statystyk[s]
	local obecna = L.statystykaZ(D, gracz:GetAttribute(nazwa))
	if obecna ~= nil then
		ustawStatystyke(gracz, s, L.statystykaZ(D, obecna + n))
	elseif statystykiWlaczone() then
		p.baza = nil
		zastosujBaze(gracz)
	end
	dolicz("LicznikTreningu")
end

local polaczenieTreningu: RBXScriptConnection? = nil
local function podlaczTrening(k: Instance)
	if k.Name ~= D.trening.kontener then
		return
	end
	task.spawn(function()
		local s = k:WaitForChild("Sygnaly", 15)
		local e = s and s:WaitForChild(D.trening.sygnal, 15)
		if not e or not e:IsA("BindableEvent") or not k.Parent then
			return
		end
		if polaczenieTreningu then
			polaczenieTreningu:Disconnect()
		end
		polaczenieTreningu = e.Event:Connect(function(gracz: any, info: any)
			local ok, blad = pcall(przyrostTreningu, gracz, info)
			if not ok then
				warn(P .. "przyrost treningu: " .. tostring(blad))
			end
		end)
		kontener:SetAttribute("TreningPodlaczony", true)
		k.Destroying:Connect(function()
			kontener:SetAttribute("TreningPodlaczony", false)
		end)
	end)
end
kontener:SetAttribute("TreningPodlaczony", false)
for _, k in workspace:GetChildren() do
	podlaczTrening(k)
end
workspace.ChildAdded:Connect(podlaczTrening)

------------------------------------------------------------------ klient: "pokaz" (HUD znów widać — koniec ekranu walki)
local ostatniePokaz: { [Player]: number } = {}
zdarzenia.OnServerEvent:Connect(function(gracz: Player, polecenie: any)
	if polecenie ~= "pokaz" then
		return
	end
	local t = os.clock()
	if ostatniePokaz[gracz] and t - ostatniePokaz[gracz] < D.publikacja.odstep_pokaz_s then
		return
	end
	ostatniePokaz[gracz] = t
	publikuj(gracz, true, D.publikacja.min_s)
	-- D-107 (walka bez przestojów): walka pominięta zaraz po starcie kończy się, zanim jej łup ma min_s — dawniej
	-- czekał wtedy na następne "pokaz" albo na pełny czas walki + zapas_s. Teraz pokazujemy go, gdy tylko dojrzeje
	-- (najwyżej min_s po przyjęciu); tylko łupy przyjęte PRZED tym zgłoszeniem — łup następnej walki dalej czeka
	local p = profile[gracz]
	if p and #p.oczekujace > 0 then
		local granica = teraz()
		local najmlodszy = nil
		for _, o in p.oczekujace do
			if o.przyjeto <= granica and (najmlodszy == nil or o.przyjeto > najmlodszy) then
				najmlodszy = o.przyjeto
			end
		end
		if najmlodszy ~= nil and granica - najmlodszy < D.publikacja.min_s then
			task.delay(D.publikacja.min_s - (granica - najmlodszy) + 0.05, function()
				publikuj(gracz, true, D.publikacja.min_s, granica)
			end)
		end
	end
end)

------------------------------------------------------------------ gracze
local function przygotujGracza(gracz: Player)
	profil(gracz)
	gracz:GetAttributeChangedSignal(A.poziom):Connect(function()
		ustawXpMax(gracz)
		zastosujBaze(gracz)
		przyznajPunkty(gracz)
	end)
	gracz:GetAttributeChangedSignal(A.klasa):Connect(function()
		zastosujBaze(gracz)
	end)
	ustawXpMax(gracz)
	zastosujBaze(gracz)
	if not znane[gracz] or not punktyWlaczone() then
		zapamietajStatystyki(gracz)
	end
	przyznajPunkty(gracz)
	for _, s in D.statystyki do
		gracz:GetAttributeChangedSignal(D.atrybuty_statystyk[s]):Connect(function()
			pilnujStatystyki(gracz, s)
		end)
	end
	zbierz(gracz)
	publikujPety(gracz)
end

------------------------------------------------------------------ zapis postępu (18.11.2026; włączony 19.11.2026, D-110)
-- Moduly/ZapisStanu (DataStore, blokada sesji, ponawianie); tu: kiedy wczytać i zapisać i jak przenieść profil do
-- atrybutów. Włączony, gdy przy starcie serwera D.zapis.wlaczony (albo atrybut kontenera D.zapis.atrybut = true),
-- atrybut nie jest false i nie trwa próba gry (znacznik D.zapis.proba — wtedy najwyżej magazyn próby).
local zapisy: { [Player]: any } = {}
local wTrakcie = 0 -- zapisy w toku i w kolejce (BindToClose czeka, aż spadnie do zera)

local function atrybutyDoZapisu(gracz: Player)
	local w = {}
	for n, v in gracz:GetAttributes() do
		for _, pre in D.zapis.atrybuty_prefiksy do
			if string.sub(n, 1, #pre) == pre and (type(v) == "boolean" or type(v) == "string" or type(v) == "number") then
				w[n] = v
			end
		end
	end
	return w
end

-- profil z zapisu → atrybuty gracza (przed podłączeniem słuchaczy; statystyki liczy potem zastosujBaze od nowa:
-- rozkład klasy dla poziomu + trening + rozdane punkty)
-- 27.11.2026 (limit treningu AFK, BALANS_2711.md): wytrenowane punkty każdej statystyki (profil „wytrenowane”) jako
-- atrybuty gracza D.trening.prefiks_wytrenowanych .. atrybut statystyki — serwer TreningAFK liczy z nich limit
local function pokazWytrenowane(gracz: Player, p)
	for s, nazwa in D.atrybuty_statystyk do
		local v = p.wytrenowane[s] or 0
		if gracz:GetAttribute(D.trening.prefiks_wytrenowanych .. nazwa) ~= v then
			gracz:SetAttribute(D.trening.prefiks_wytrenowanych .. nazwa, v)
		end
	end
end

local function zastosujProfil(gracz: Player, p)
	pokazWytrenowane(gracz, p)
	gracz:SetAttribute(A.poziom, p.poziom)
	gracz:SetAttribute(A.xp, p.xp)
	gracz:SetAttribute(A.zloto, p.zloto)
	gracz:SetAttribute(A.gemy, p.gemy)
	gracz:SetAttribute(A.shardy, p.shardy)
	for kraina, n in p.tokeny do
		gracz:SetAttribute(A.tokeny_prefiks .. kraina, n)
	end
	for n, v in p.atrybuty do
		gracz:SetAttribute(n, v)
	end
	if p.idKlasy ~= nil then
		-- jedyny zapis atrybutu Class Pawła: przywrócenie wybranej klasy z zapisu (wyścig z ekranem wyboru klasy — README)
		gracz:SetAttribute(A.klasa, p.idKlasy)
	end
	p.baza = nil
	znane[gracz] = nil
end

local function wykonajZapis(gracz: Player, z, dane, zwolnij: boolean, potem)
	if z.stan ~= "aktywny" or not zapis then
		wTrakcie -= 1
		if potem then
			potem(false)
		end
		return
	end
	z.trwa = true
	zapis.zapisz(gracz.UserId, dane, zwolnij, function(ok: boolean, powod: string?)
		z.trwa = false
		wTrakcie -= 1
		if ok then
			dolicz("LicznikZapisow")
			kontener:SetAttribute("OstatniZapis", string.format("%d:%s", gracz.UserId, if zwolnij then "wyjscie" else "zapis"))
		else
			dolicz("LicznikBledowZapisu")
			if powod == "utracona_blokada" or powod == "przyszla_wersja" or powod == "zly_rekord" then
				z.stan = "bez_zapisu" -- inny serwer przejął profil albo rekord nie jest nasz: dalej tylko pamięć
				if gracz.Parent then
					gracz:SetAttribute("StanGraczaZapis", z.stan)
				end
			end
		end
		if potem then
			potem(ok)
		end
		local nast = table.remove(z.kolejka, 1)
		if nast then
			wykonajZapis(gracz, z, nast.dane, nast.zwolnij, nast.potem)
		end
	end)
end

-- dane bierzemy od razu (atrybuty i profil w tej chwili); zapis w toku → do kolejki (jeden zapis gracza naraz)
local function zapiszGracza(gracz: Player, zwolnij: boolean, potem)
	local z = zapisy[gracz]
	if not z or z.stan ~= "aktywny" or not zapis then
		if potem then
			potem(false)
		end
		return
	end
	if zwolnij then
		publikuj(gracz, true, 0) -- łup zakończonej walki do profilu przed ostatnim zapisem
	end
	local p = zbierz(gracz)
	p.atrybuty = atrybutyDoZapisu(gracz)
	local dane = L.profilDoZapisu(D, p)
	wTrakcie += 1
	if z.trwa then
		table.insert(z.kolejka, { dane = dane, zwolnij = zwolnij, potem = potem })
		return
	end
	wykonajZapis(gracz, z, dane, zwolnij, potem)
end

local function zaplanujZapis(gracz: Player)
	local los = if math.random then math.random() else 0.5
	task.delay(D.zapis.co_s + los * D.zapis.rozrzut_s, function()
		local z = zapisy[gracz]
		if z and z.stan == "aktywny" and not z.wyszedl then
			zapiszGracza(gracz, false, nil)
			zaplanujZapis(gracz)
		end
	end)
end

local function poWczytaniu(gracz: Player, stan: string, dane, powod: string?)
	local z = zapisy[gracz]
	if not z or z.wyszedl then
		-- wyszedł w trakcie wczytywania: oddajemy sesję, profilu nie ruszamy
		zapisy[gracz] = nil
		if zapis and (stan == "ok" or stan == "nowy") then
			zapis.zapisz(gracz.UserId, nil, true, function() end)
		end
		return
	end
	if stan == "ok" or stan == "nowy" then
		local p = dane
		if stan == "nowy" then
			-- nowy gracz: wartości startowe zamiast testowych z PlayerStatsDefaults (np. 1000 Gemów) — README
			p = L.nowyProfil(D)
			p.gemy = D.zapis.start.gemy
			p.zloto = D.zapis.start.zloto
		end
		p.oczekujace = {}
		profile[gracz] = p
		zastosujProfil(gracz, p)
		z.stan = "aktywny"
		dolicz("LicznikWczytan")
		zaplanujZapis(gracz)
	else
		z.stan = "bez_zapisu"
		dolicz("LicznikBezZapisu")
		if zapis and zapis.wylaczony then
			kontener:SetAttribute("ZapisAktywny", false)
			kontener:SetAttribute("ZapisStan", "wyłączony: " .. tostring(zapis.powod))
		end
		warn(P .. "zapis: gracz " .. tostring(gracz.UserId) .. " gra bez zapisu (" .. stan .. ", " .. tostring(powod) .. ")")
	end
	gracz:SetAttribute("StanGraczaZapis", z.stan)
	-- czas od wejścia do końca wczytania (ms) — do prób zapisu (proba_zapisu.py)
	gracz:SetAttribute("StanGraczaWczytanieMs", math.floor((os.clock() - (z.t0 or os.clock())) * 1000 + 0.5))
	przygotujGracza(gracz)
	gracz:SetAttribute("StanGraczaWczytany", true)
end

local function nowyGracz(gracz: Player)
	for _, nazwa in D.atrybuty_statystyk do -- agent Karola, 27.11: wytrenowane od wejścia 0 (wczytany profil nadpisze)
		if gracz:GetAttribute(D.trening.prefiks_wytrenowanych .. nazwa) == nil then
			gracz:SetAttribute(D.trening.prefiks_wytrenowanych .. nazwa, 0)
		end
	end
	if zapis and not zapis.wylaczony then
		zapisy[gracz] = { stan = "wczytywanie", trwa = false, kolejka = {}, wyszedl = false, t0 = os.clock() }
		gracz:SetAttribute("StanGraczaWczytany", false)
		zapis.wczytaj(gracz.UserId, function(stan: string, dane, powod: string?)
			poWczytaniu(gracz, stan, dane, powod)
		end)
		return
	end
	przygotujGracza(gracz)
end
Players.PlayerAdded:Connect(nowyGracz)
for _, g in Players:GetPlayers() do
	task.spawn(nowyGracz, g)
end
Players.PlayerRemoving:Connect(function(gracz: Player)
	local z = zapisy[gracz]
	if z then
		z.wyszedl = true
		if z.stan == "aktywny" then
			zapiszGracza(gracz, true, function()
				zapisy[gracz] = nil
			end)
		elseif z.stan ~= "wczytywanie" then
			zapisy[gracz] = nil
		end
	end
	profile[gracz] = nil
	modyfikatory[gracz] = nil
	znane[gracz] = nil
	ostatniePokaz[gracz] = nil
end)

-- zamknięcie serwera: ostatni zapis i zwolnienie sesji wszystkich graczy, najwyżej D.zapis.zamkniecie_s
game:BindToClose(function()
	if not zapis then
		return
	end
	for g, z in zapisy do
		if z.stan == "aktywny" and not z.wyszedl then
			z.wyszedl = true
			zapiszGracza(g, true, nil)
		end
	end
	local t0 = os.clock()
	while wTrakcie > 0 and os.clock() - t0 < D.zapis.zamkniecie_s do
		task.wait(0.5)
	end
	if wTrakcie > 0 then
		warn(P .. string.format("zapis: zamknięcie serwera — nie zdążyło %d zapisów", wTrakcie))
	end
end)

-- włączenie StatystykiKlasy w czasie gry: rozkład klasy od razu (wyłączenie zostawia atrybuty, jakie są)
-- przełączenie rozkładów klas w czasie gry: nowy cel, a trening, rozdane punkty i „+” zostają (różnica celów)
kontener:GetAttributeChangedSignal(D.rozklady_klas.atrybut):Connect(function()
	ogloscRozklady()
	for _, g in Players:GetPlayers() do
		zastosujBaze(g)
	end
end)

kontener:GetAttributeChangedSignal("StatystykiKlasy"):Connect(function()
	for _, g in Players:GetPlayers() do
		zastosujBaze(g)
		zapamietajStatystyki(g)
		przyznajPunkty(g)
	end
end)

-- wyłącznik punktów w czasie gry: przyjmujemy obecne wartości, pula samo rozdzielana wraca do 10 (albo 5) na poziom
kontener:GetAttributeChangedSignal(D.punkty.atrybut_wylacznika):Connect(function()
	for _, g in Players:GetPlayers() do
		zapamietajStatystyki(g)
		zastosujBaze(g)
		przyznajPunkty(g)
	end
end)

------------------------------------------------------------------ haczyk testowy
local function ktory(g: any): Player?
	if typeof(g) == "Instance" and g:IsA("Player") then
		return g
	end
	return Players:GetPlayers()[1]
end

local function kopia(t: any): any
	if type(t) ~= "table" then
		return t
	end
	local w = {}
	for k, v in t do
		w[k] = kopia(v)
	end
	return w
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any)
	if polecenie == "zgodnosc" then
		return zgodnosc()
	end
	local g = ktory(a)
	if not g then
		return nil
	end
	if polecenie == "stan" then
		local p = kopia(zbierz(g))
		local atrybuty = {}
		for _, s in D.statystyki do
			atrybuty[D.atrybuty_statystyk[s]] = g:GetAttribute(D.atrybuty_statystyk[s])
		end
		for _, n in { A.klasa, A.poziom, A.xp, A.xp_max, A.zloto, A.gemy, A.shardy } do
			atrybuty[n] = g:GetAttribute(n)
		end
		p.atrybuty = atrybuty
		p.oczekujace = #p.oczekujace
		p.rozklady = kontener:GetAttribute("RozkladyZ")
		p.statystykiKlasy = statystykiWlaczone()
		local zl, zrodla = zlozenie(g)
		p.modyfikatory = zl
		p.zrodlaModyfikatorow = zrodla
		p.procentKary = procentKary()
		p.zapis = if zapisy[g] then zapisy[g].stan else "wylaczony"
		return p
	elseif polecenie == "publikuj" then
		return publikuj(g, true, 0)
	elseif polecenie == "bohater" then
		return bohater(g)
	elseif polecenie == "przyznaj" then
		local w = przyjmijLup(g, { lup = b, wynik = "wygrana", czas = 0, zrodlo = D.zrodla[1] })
		if w.ok then
			publikuj(g, true, 0)
		end
		return w
	end
	warn(P .. "SterowanieSerwera: nieznane polecenie " .. tostring(polecenie))
	return nil
end

kontener:SetAttribute("SerwerStanuGotowy", true)
print(string.format("%sgotowy: logika %s, rozkłady %s, statystyki klasy %s, kara za przegraną %s", P,
	tostring(kontener:GetAttribute("ZgodnoscLogikiStanu")), tostring(kontener:GetAttribute("RozkladyZ")),
	if statystykiWlaczone() then "włączone" else "wyłączone (wartości testowe Pawła)",
	if procentKary() > 0 then string.format("%d%% Złota", math.floor(procentKary() * 100 + 0.5)) else "wyłączona"))
