--[[
	SerwerKowala — serwer kowala na próbę (D-102, D-051; swiat/kowal_proba). Script, RunContext = Server, w kontenerze
	Workspace/KowalProba. Poza Studio usuwa cały kontener (w opublikowanej grze próby nie ma).

	Właściciel stanu gracza to StanGracza (swiat/stan_gracza) — tu NIC nie jest trwałe poza jego profilem:
	  • przedmioty i materiały gracza = Sygnaly/DanePakietu ("czytaj" / "zapisz", pakiet D.stan.pakiet) — przyszły zapis
	    profilu obejmie je razem ze Złotem;
	  • wpływ na walkę = Sygnaly/Modyfikatory ("ustaw", gracz, "kowal", wpis z L.mod) z ZAŁOŻONYCH przedmiotów
	    (atrybut gracza StrojProba_<klasa> z przymierzalni swiat/stroje_proba; bez przymierzalni — wszystkie posiadane);
	  • Złoto = Sygnaly/WydajZloto (nigdy poniżej zera; za mało = odmowa z brakującą kwotą, bez zmian).
	Bez StanGracza kuźnia odmawia napisem „Kuźnia nieczynna…”, a przymierzalnia działa jak dawniej (atrybutu
	KowalDostepne nie ma). Kontener StanGracza sprawdzamy co D.stan.coIleS s — po jego przebudowie wpisy wracają.

	Łup przedmiotów: wygraną poznajemy po przyroście atrybutu gracza TokenyKrainy_<kraina> (pisze go StanGracza przy
	pokazaniu łupu); przyrost 1..D.lup.progi.maks → ranga (zwykły / rzadki / strażnik) → L.lup (Random serwera).
	Nowy przedmiot od razu zakładamy w przymierzalni (gdy jest), zapas czeka na rozbiórkę.

	Zdalne/Kuznia (RemoteFunction): InvokeServer(akcja, id?) → { ok, powod?, tekst?, widok? }
		"widok"            okno (teksty i liczby liczy serwer; klient tylko pokazuje)
		"rozbierz", id     zapasowy egzemplarz → materiały (gracz przy kowalu)
		"ulepsz", id       Złoto przez WydajZloto + materiały → poziom +1 (gracz przy kowalu)
	Klient wysyła tylko nazwę akcji i id z katalogu; serwer sprawdza typy, długość, klasę, posiadanie, odległość od
	punktu E kowala (D.kuznia.zasieg + zapasSerwera), limit jednego zapytania na D.limit s i blokadę na czas ulepszania.
	Zdalne/ZdarzeniaKowala (RemoteEvent, serwer → klient): "lup", nazwa, nowy · "ulepszono", id, poziom.
	Sygnaly/SterowanieSerwera (BindableFunction, haczyk testowy): "stan" | "widok" | "przelicz", gracz ·
		"lup", gracz, ranga, los2 (pewny łup) · "daj", gracz, id · "materialy", gracz, n · "zgodnosc".

	Sygnaly/Sklep (BindableFunction, D-106) — wejście dla pakietu sklepu (swiat/sklep_proba); kowal jest właścicielem
	posiadanych przedmiotów i to on płaci (źródło wydatku D.stan.zrodloWydatku, cel D.sklep.celWydatku):
		Invoke("oferta", gracz)   → { ok, oferta, zloto, poziom, klasa }
		Invoke("kup", gracz, id)  → { ok, powod?, brakuje?, wymagany?, zalozony, zloto, id?, nazwa?, cena?, czesc? }
		Invoke("zaloz", gracz, id) → { ok, powod?, zalozony, zloto, nazwa? }
	Kupno: L.kup (klasa, poziom z atrybutu Level, posiadanie, Złoto) → WydajZloto (odmowa = nic nie zapisane) → zapis
	posiadania (DanePakietu) → założenie według reguły L.czyZalozyc (pusty slot albo założony przedmiot niższego
	stopnia) → Modyfikatory. Atrybut gracza D.sklep.atrybutStacNa = ile przedmiotów gracz może teraz kupić.
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneKowala"))
local L = require(moduly:WaitForChild("LogikaKowala"))
local zdalne = kontener:WaitForChild("Zdalne")
local kuzniaF = zdalne:WaitForChild("Kuznia")
local zdarzenia = zdalne:WaitForChild("ZdarzeniaKowala")
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera")
local S = D.stan
local T = D.teksty
local los = Random.new()

local stany = {}       -- [gracz] = { dane, klasa, tokeny = { [atrybut] = n }, zajety }
local polaczenia = {}  -- [gracz] = { połączenia zdarzeń }
local ostatnie = {}
local liczniki = { LicznikLupow = 0, LicznikUlepszen = 0, LicznikRozbiorek = 0, LicznikOdmow = 0, LicznikKupna = 0 }
local AKCJE = { widok = true, rozbierz = true, ulepsz = true }

local function dolicz(nazwa)
	liczniki[nazwa] += 1
	kontener:SetAttribute(nazwa, liczniki[nazwa])
end

------------------------------------------------------------------ styk z innymi pakietami (FindFirstChild + pcall)
local function sygnalStanu(nazwa)
	local k = workspace:FindFirstChild(S.kontener)
	local s = k and k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild(nazwa)
	if f and f:IsA("BindableFunction") then
		return f
	end
	return nil
end

local function wolaj(f, a, b, c, d)
	if not f then
		return false, nil
	end
	local ok, w = pcall(function()
		return f:Invoke(a, b, c, d)
	end)
	if not ok then
		warn(D.prefiks .. "błąd sygnału " .. f.Name .. ": " .. tostring(w))
		return false, nil
	end
	return true, w
end

local function stanCzynny()
	return sygnalStanu(S.danePakietu) ~= nil and sygnalStanu(S.modyfikatory) ~= nil
end

local function przymierzalnia()
	local k = workspace:FindFirstChild(D.przymierzalnia.kontener)
	local s = k and k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild(D.przymierzalnia.sterowanie)
	if f and f:IsA("BindableFunction") then
		return f
	end
	return nil
end

------------------------------------------------------------------ dane gracza (profil StanGracza)
local function zapisz(gracz, st, dane)
	local ok, w = wolaj(sygnalStanu(S.danePakietu), "zapisz", gracz, S.pakiet, dane)
	if ok and type(w) == "table" and w.ok == true then
		st.dane = dane
		return true
	end
	warn(D.prefiks .. "zapis danych kowala odrzucony: " .. tostring(type(w) == "table" and w.powod or w))
	return false
end

local function zlotoGracza(gracz)
	local z = gracz:GetAttribute(S.atrybutZlota)
	return if type(z) == "number" and z == z then math.floor(z) else 0
end

local function poziomGracza(gracz)
	return L.poziomGracza(gracz:GetAttribute(D.sklep.atrybutPoziomu))
end

-- wskazówka „stać cię na nowy przedmiot”: ile przedmiotów klasy gracz może teraz kupić
local function publikujStacNa(gracz)
	local st = stany[gracz]
	if st then
		gracz:SetAttribute(D.sklep.atrybutStacNa, L.stacNa(D, st.dane, st.klasa, poziomGracza(gracz), zlotoGracza(gracz)))
	end
end

local function napisStroju(gracz, klasa)
	if not przymierzalnia() then
		return nil
	end
	local v = gracz:GetAttribute(D.przymierzalnia.atrybut .. klasa)
	return if type(v) == "string" then v else nil
end

-- atrybuty dla przymierzalni i HUD, strój bez nieposiadanych przedmiotów, wpis Modyfikatory z założonych
local function publikuj(gracz)
	local st = stany[gracz]
	if not st then
		return
	end
	gracz:SetAttribute(D.atrybuty.dostepne, L.dostepne(D, st.dane))
	gracz:SetAttribute(D.atrybuty.materialy, st.dane.materialy)
	-- zapasowe egzemplarze (do rozbiórki) — haczyk dla wskazówki celu („rozbierz u kowala”)
	local zapasy = 0
	for _, v in st.dane.przedmioty do
		zapasy += v.zapas
	end
	gracz:SetAttribute(D.atrybuty.zapasy, zapasy)
	gracz:SetAttribute(D.atrybuty.ulepszen, L.sumaPoziomow(st.dane))
	gracz:SetAttribute(D.atrybuty.ulepsz, L.moznaUlepszyc(D, st.klasa, st.dane, zlotoGracza(gracz)))
	publikujStacNa(gracz)
	local f = przymierzalnia()
	if f then
		local nowy = L.strojDoUstawienia(D, st.klasa, st.dane, napisStroju(gracz, st.klasa))
		if nowy ~= nil then
			wolaj(f, "ustaw", gracz, st.klasa, nowy)
		end
	end
	local zal = L.zalozone(D, st.klasa, st.dane, napisStroju(gracz, st.klasa))
	local m = L.mod(D, st.klasa, st.dane, zal)
	local ok, w = wolaj(sygnalStanu(S.modyfikatory), "ustaw", gracz, S.zrodloModyfikatorow, m)
	if not ok or type(w) ~= "table" or w.ok ~= true then
		warn(D.prefiks .. "Modyfikatory odrzuciły wpis kowala: " .. tostring(type(w) == "table" and w.powod or w))
	end
	kontener:SetAttribute("OstatnieModyfikatory", string.format("%s:%s:%d przedm.", gracz.Name, st.klasa, #zal))
end

local function zaladuj(gracz)
	if not stanCzynny() then
		return nil
	end
	local ok, v = wolaj(sygnalStanu(S.danePakietu), "czytaj", gracz, S.pakiet)
	if not ok then
		return nil
	end
	local klasa = L.klasaZ(D, gracz:GetAttribute(S.atrybutKlasy))
	local dane = L.czyste(D, v)
	local st = { dane = dane, klasa = klasa, tokeny = {}, zajety = false }
	local poPodstawowym, dodane = L.podstawowe(D, dane, klasa)
	if v == nil or #dodane > 0 then
		zapisz(gracz, st, poPodstawowym)
	end
	-- tokeny krainy: punkt wyjścia (bez losowania za to, co gracz już miał)
	for nazwa, n in gracz:GetAttributes() do
		if type(nazwa) == "string" and string.sub(nazwa, 1, #D.lup.atrybut) == D.lup.atrybut and type(n) == "number" then
			st.tokeny[nazwa] = n
		end
	end
	stany[gracz] = st
	publikuj(gracz)
	return st
end

------------------------------------------------------------------ łup przedmiotów
-- zakłada posiadany przedmiot w jego slocie przez przymierzalnię (dotychczasowy przedmiot slotu schodzi)
local function zalozWSlocie(gracz, st, id)
	local f = przymierzalnia()
	local napis = napisStroju(gracz, st.klasa)
	if not f or napis == nil then
		return false
	end
	gracz:SetAttribute(D.atrybuty.dostepne, L.dostepne(D, st.dane))
	wolaj(f, "ustaw", gracz, st.klasa, L.strojZPrzedmiotem(D, napis, id))
	return true
end

-- nowy przedmiot (łup albo kupno): zakłada się sam tylko w pusty slot albo w miejsce przedmiotu niższego stopnia
local function zalozNowy(gracz, st, id)
	local zal = L.zalozone(D, st.klasa, st.dane, napisStroju(gracz, st.klasa))
	if table.find(zal, id) == nil and L.czyZalozyc(D, zal, id) then
		zalozWSlocie(gracz, st, id)
	end
end

local function czyZalozony(gracz, st, id)
	return table.find(L.zalozone(D, st.klasa, st.dane, napisStroju(gracz, st.klasa)), id) ~= nil
end

local function losuj(gracz, ranga, los1, los2)
	local st = stany[gracz]
	if not st then
		return nil
	end
	local dane, lup = L.lup(D, st.dane, st.klasa, ranga, los1, los2)
	if not zapisz(gracz, st, dane) then
		return nil
	end
	if lup then
		dolicz("LicznikLupow")
		if lup.nowy then
			zalozNowy(gracz, st, lup.id)
		end
		publikuj(gracz)
		kontener:SetAttribute("OstatniLup", string.format("%s:%s:%s:%s", gracz.Name, ranga, lup.id,
			if lup.nowy then "nowy" else "zapas"))
		zdarzenia:FireClient(gracz, "lup", D.przedmioty[lup.id].nazwa, lup.nowy)
	end
	return lup
end

local function zmianaTokenow(gracz, nazwa)
	local st = stany[gracz]
	if not st then
		return
	end
	local n = gracz:GetAttribute(nazwa)
	local stare = st.tokeny[nazwa]
	if type(n) ~= "number" then
		st.tokeny[nazwa] = nil
		return
	end
	st.tokeny[nazwa] = n
	local roznica = n - (stare or 0)
	if stare == nil and roznica > D.lup.progi.maks then
		return -- wczytanie albo zbiór wielu walk: punkt wyjścia bez losowania
	end
	local ranga = L.ranga(D, roznica)
	if ranga then
		losuj(gracz, ranga, los:NextNumber(), los:NextNumber())
	end
end

------------------------------------------------------------------ okno
local function opisBohatera(gracz)
	local ok, opis = wolaj(sygnalStanu(S.bohater), gracz)
	if not ok then
		return ""
	end
	return L.opisBohatera(D, opis)
end

local function widok(gracz)
	local st = stany[gracz]
	local zal = L.zalozone(D, st.klasa, st.dane, napisStroju(gracz, st.klasa))
	return L.widok(D, st.dane, st.klasa, zal, zlotoGracza(gracz), opisBohatera(gracz))
end

local function przyKowalu(gracz)
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp then
		return false
	end
	local p = hrp.Position
	local e = D.kuznia.e
	local dx, dz = p.X - e[1], p.Z - e[3]
	local r = D.kuznia.zasieg + D.kuznia.zapasSerwera
	return dx * dx + dz * dz <= r * r
end

local function odmowa(gracz, powod, ile)
	dolicz("LicznikOdmow")
	local w = { ok = false, powod = powod, tekst = L.komunikat(D, powod, ile) }
	if stany[gracz] then
		w.widok = widok(gracz)
	end
	return w
end

local function wykonaj(gracz, akcja, id)
	if type(akcja) ~= "string" or not AKCJE[akcja] then
		return { ok = false, powod = "zla_akcja", tekst = T.blad }
	end
	if id ~= nil and (type(id) ~= "string" or #id > 64) then
		return { ok = false, powod = "zly_argument", tekst = T.blad }
	end
	local st = stany[gracz] or zaladuj(gracz)
	if not st or not stanCzynny() then
		return odmowa(gracz, "brak_stanu")
	end
	if akcja == "widok" then
		return { ok = true, widok = widok(gracz) }
	end
	if not przyKowalu(gracz) then
		return odmowa(gracz, "daleko")
	end
	if akcja == "rozbierz" then
		local ok, w, zysk = L.rozbierz(D, st.dane, st.klasa, id)
		if not ok then
			return odmowa(gracz, w)
		end
		if not zapisz(gracz, st, w) then
			return odmowa(gracz, "brak_stanu")
		end
		dolicz("LicznikRozbiorek")
		publikuj(gracz)
		return { ok = true, tekst = string.format(T.ok_rozbierz, L.ileMaterialow(D, zysk)), widok = widok(gracz) }
	end
	-- ulepsz: materiały sprawdzone przed wydaniem Złota; Złoto wydaje StanGracza (nigdy poniżej zera)
	local ok, k, ile = L.planUlepszenia(D, st.dane, st.klasa, id)
	if not ok then
		return odmowa(gracz, k, ile)
	end
	local okW, r = wolaj(sygnalStanu(S.wydaj), gracz, { ile = k.zloto, zrodlo = S.zrodloWydatku, cel = S.celWydatku })
	if not okW or type(r) ~= "table" then
		return odmowa(gracz, "brak_stanu")
	end
	if r.ok ~= true then
		if r.powod == "za_malo" then
			return odmowa(gracz, "za_malo_zlota", if type(r.brakuje) == "number" then r.brakuje else k.zloto)
		end
		warn(D.prefiks .. "WydajZloto odmówił: " .. tostring(r.powod))
		return odmowa(gracz, "brak_stanu")
	end
	local w = L.ulepsz(D, st.dane, id, k)
	if not zapisz(gracz, st, w) then
		st.dane = w -- Złoto już wydane: ulepszenie zostaje w pamięci serwera, zapis spróbuje przy następnej zmianie
	end
	dolicz("LicznikUlepszen")
	publikuj(gracz)
	local poziom = st.dane.przedmioty[id].poziom
	zdarzenia:FireClient(gracz, "ulepszono", id, poziom)
	return { ok = true, tekst = string.format(T.ok_ulepsz, D.przedmioty[id].nazwa, poziom), widok = widok(gracz) }
end

kuzniaF.OnServerInvoke = function(gracz, akcja, id)
	local t = os.clock()
	if ostatnie[gracz] and t - ostatnie[gracz] < D.limit then
		dolicz("LicznikOdmow")
		return { ok = false, powod = "za_szybko", tekst = T.za_szybko }
	end
	ostatnie[gracz] = t
	local st = stany[gracz]
	if st and st.zajety then
		return { ok = false, powod = "za_szybko", tekst = T.za_szybko }
	end
	if st then
		st.zajety = true
	end
	local ok, w = pcall(wykonaj, gracz, akcja, id)
	if st then
		st.zajety = false
	end
	if not ok then
		warn(D.prefiks .. "błąd kuźni: " .. tostring(w))
		return { ok = false, powod = "blad", tekst = T.blad }
	end
	return w
end

------------------------------------------------------------------ gracze
local function zmianaKlasy(gracz)
	local st = stany[gracz]
	if not st then
		return
	end
	local klasa = L.klasaZ(D, gracz:GetAttribute(S.atrybutKlasy))
	if klasa == st.klasa then
		return
	end
	st.klasa = klasa
	local dane, dodane = L.podstawowe(D, st.dane, klasa)
	if #dodane > 0 or dane ~= st.dane then
		zapisz(gracz, st, dane)
	end
	publikuj(gracz)
end

local function dolaczyl(gracz)
	if polaczenia[gracz] then
		return
	end
	local lista = {}
	table.insert(lista, gracz.AttributeChanged:Connect(function(nazwa)
		local st = stany[gracz]
		if not st or type(nazwa) ~= "string" then
			return
		end
		if string.sub(nazwa, 1, #D.lup.atrybut) == D.lup.atrybut then
			zmianaTokenow(gracz, nazwa)
		elseif nazwa == S.atrybutKlasy then
			zmianaKlasy(gracz)
		elseif nazwa == S.atrybutZlota then
			gracz:SetAttribute(D.atrybuty.ulepsz, L.moznaUlepszyc(D, st.klasa, st.dane, zlotoGracza(gracz)))
			publikujStacNa(gracz)
		elseif nazwa == D.sklep.atrybutPoziomu then
			publikujStacNa(gracz)
		elseif nazwa == D.przymierzalnia.atrybut .. st.klasa then
			publikuj(gracz)
		end
	end))
	polaczenia[gracz] = lista
	zaladuj(gracz)
end

Players.PlayerAdded:Connect(dolaczyl)
Players.PlayerRemoving:Connect(function(gracz)
	for _, c in polaczenia[gracz] or {} do
		c:Disconnect()
	end
	polaczenia[gracz] = nil
	stany[gracz] = nil
	ostatnie[gracz] = nil
end)
for _, gracz in Players:GetPlayers() do
	dolaczyl(gracz)
end

-- StanGracza pojawił się, zniknął albo został przebudowany: dane i wpisy od nowa (wpisy Modyfikatory żyją u niego)
local ostatniStan = workspace:FindFirstChild(S.kontener)
local ostatniaPrzymierzalnia = przymierzalnia()
local function pilnuj()
	local k = workspace:FindFirstChild(S.kontener)
	local czynny = stanCzynny()
	if k ~= ostatniStan or (czynny and kontener:GetAttribute("StanGraczaPodlaczony") ~= true) then
		ostatniStan = k
		for _, gracz in Players:GetPlayers() do
			stany[gracz] = nil
			if czynny then
				zaladuj(gracz)
			end
		end
	end
	-- przymierzalnia pojawiła się (albo przebudowana) po starcie: strój z posiadanych i wpis od nowa
	local p = przymierzalnia()
	if p ~= ostatniaPrzymierzalnia then
		ostatniaPrzymierzalnia = p
		for _, gracz in Players:GetPlayers() do
			publikuj(gracz)
		end
	end
	kontener:SetAttribute("StanGraczaPodlaczony", czynny)
	task.delay(S.coIleS, pilnuj)
end
kontener:SetAttribute("StanGraczaPodlaczony", stanCzynny())
task.delay(S.coIleS, pilnuj)

sterowanie.OnInvoke = function(polecenie, gracz, a, b)
	if polecenie == "zgodnosc" then
		local ok, n, zle = L.sprawdzPrzypadki(D)
		return { ok = ok, n = n, zle = zle }
	end
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") then
		return { ok = false, powod = "zly_gracz" }
	end
	local st = stany[gracz] or zaladuj(gracz)
	if not st then
		return { ok = false, powod = "brak_stanu" }
	end
	if polecenie == "stan" then
		local zal = L.zalozone(D, st.klasa, st.dane, napisStroju(gracz, st.klasa))
		return { ok = true, dane = L.kopia(st.dane), klasa = st.klasa, zalozone = zal, mod = L.mod(D, st.klasa, st.dane, zal) }
	elseif polecenie == "widok" then
		return { ok = true, widok = widok(gracz) }
	elseif polecenie == "przelicz" then
		publikuj(gracz)
		return { ok = true }
	elseif polecenie == "lup" then
		local lup = losuj(gracz, if type(a) == "string" then a else "zwykly", 0, if type(b) == "number" then b else 0)
		return { ok = lup ~= nil, lup = lup }
	elseif polecenie == "daj" and type(a) == "string" and D.przedmioty[a] ~= nil then
		local dane = L.kopia(st.dane)
		if dane.przedmioty[a] then
			dane.przedmioty[a].zapas += 1
		else
			dane.przedmioty[a] = { poziom = 0, zapas = 0 }
		end
		local ok = zapisz(gracz, st, dane)
		publikuj(gracz)
		return { ok = ok }
	elseif polecenie == "materialy" and type(a) == "number" and a >= 0 and math.floor(a) == a then
		local dane = L.kopia(st.dane)
		dane.materialy = a
		local ok = zapisz(gracz, st, dane)
		publikuj(gracz)
		return { ok = ok }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end

------------------------------------------------------------------ sklep (D-106): wejście dla pakietu sklepu
local function kupPrzedmiot(gracz, st, id)
	local zloto = zlotoGracza(gracz)
	local ok, w, info = L.kup(D, st.dane, st.klasa, poziomGracza(gracz), zloto, id)
	if not ok then
		dolicz("LicznikOdmow")
		return { ok = false, powod = w, brakuje = info, zalozony = false, zloto = zloto,
			wymagany = if w == "za_niski_poziom" then D.przedmioty[id].poziom else nil }
	end
	if info.cena > 0 then
		local okW, r = wolaj(sygnalStanu(S.wydaj), gracz, { ile = info.cena, zrodlo = S.zrodloWydatku, cel = D.sklep.celWydatku })
		if not okW or type(r) ~= "table" then
			dolicz("LicznikOdmow")
			return { ok = false, powod = "brak_stanu", zalozony = false, zloto = zloto }
		end
		if r.ok ~= true then
			dolicz("LicznikOdmow")
			if r.powod == "za_malo" then
				return { ok = false, powod = "za_malo_zlota", zalozony = false, zloto = zlotoGracza(gracz),
					brakuje = if type(r.brakuje) == "number" then r.brakuje else info.cena }
			end
			warn(D.prefiks .. "WydajZloto odmówił zakupu: " .. tostring(r.powod))
			return { ok = false, powod = "brak_stanu", zalozony = false, zloto = zlotoGracza(gracz) }
		end
	end
	if not zapisz(gracz, st, w) then
		st.dane = w -- Złoto już wydane: przedmiot zostaje w pamięci serwera, zapis spróbuje przy następnej zmianie
	end
	dolicz("LicznikKupna")
	zalozNowy(gracz, st, id)
	publikuj(gracz)
	local zalozony = czyZalozony(gracz, st, id)
	kontener:SetAttribute("OstatnieKupno", string.format("%s:%s:%d:%s", gracz.Name, id, info.cena,
		if zalozony then "zalozony" else "schowany"))
	return { ok = true, id = id, nazwa = D.przedmioty[id].nazwa, cena = info.cena, czesc = info.czesc,
		zalozony = zalozony, zloto = zlotoGracza(gracz) }
end

local function zalozPrzedmiot(gracz, st, id)
	local zloto = zlotoGracza(gracz)
	if type(id) ~= "string" or D.przedmioty[id] == nil or D.przedmioty[id].klasa ~= st.klasa then
		return { ok = false, powod = "nieznany_przedmiot", zalozony = false, zloto = zloto }
	end
	if not L.posiada(st.dane, id) then
		return { ok = false, powod = "nie_masz", zalozony = false, zloto = zloto }
	end
	local nazwa = D.przedmioty[id].nazwa
	if czyZalozony(gracz, st, id) then
		return { ok = true, zalozony = true, zloto = zloto, nazwa = nazwa }
	end
	if not zalozWSlocie(gracz, st, id) then
		return { ok = false, powod = "brak_przymierzalni", zalozony = false, zloto = zloto }
	end
	publikuj(gracz)
	local zalozony = czyZalozony(gracz, st, id)
	return { ok = zalozony, powod = if zalozony then nil else "nie_zalozono", zalozony = zalozony, zloto = zloto,
		nazwa = nazwa }
end

local function sklep(polecenie, gracz, id)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") then
		return { ok = false, powod = "zly_gracz" }
	end
	if id ~= nil and (type(id) ~= "string" or #id > 64) then
		return { ok = false, powod = "nieznany_przedmiot", zalozony = false, zloto = zlotoGracza(gracz) }
	end
	local st = stany[gracz] or zaladuj(gracz)
	if not st or not stanCzynny() then
		return { ok = false, powod = "brak_stanu" }
	end
	if polecenie == "oferta" then
		local poziom, zloto = poziomGracza(gracz), zlotoGracza(gracz)
		local zal = L.zalozone(D, st.klasa, st.dane, napisStroju(gracz, st.klasa))
		return { ok = true, oferta = L.oferta(D, st.dane, st.klasa, poziom, zloto, zal), zloto = zloto, poziom = poziom,
			klasa = st.klasa }
	end
	if polecenie ~= "kup" and polecenie ~= "zaloz" then
		return { ok = false, powod = "nieznane_polecenie" }
	end
	if st.zajety then
		return { ok = false, powod = "za_szybko", zalozony = false, zloto = zlotoGracza(gracz) }
	end
	st.zajety = true
	local ok, w = pcall(if polecenie == "kup" then kupPrzedmiot else zalozPrzedmiot, gracz, st, id)
	st.zajety = false
	if not ok then
		warn(D.prefiks .. "błąd sklepu: " .. tostring(w))
		return { ok = false, powod = "blad", zalozony = false, zloto = zlotoGracza(gracz) }
	end
	return w
end

local sklepF = kontener:WaitForChild("Sygnaly"):FindFirstChild(D.sklep.sygnal)
if sklepF and sklepF:IsA("BindableFunction") then
	sklepF.OnInvoke = sklep
end
kontener:SetAttribute("WejscieSklepu", sklepF ~= nil)

-- podpowiedź E przy kowalu: zbudowana wyłączona (Edit), włączona w Play (tylko w Studio)
local podpowiedzi = 0
for _, d in kontener:GetDescendants() do
	if d:IsA("ProximityPrompt") and d:GetAttribute("Akcja") == "kowal" then
		d.Enabled = true
		podpowiedzi += 1
	end
end
local okZ, nZ, zleZ = L.sprawdzPrzypadki(D)
kontener:SetAttribute("ZgodnoscLogikiKowala", if okZ then string.format("OK %d/%d", nZ, nZ)
	else "BŁĄD " .. table.concat(zleZ, ", "))
kontener:SetAttribute("PodpowiedziWlaczone", podpowiedzi)
kontener:SetAttribute("SkrotSerwera", D.skrot)
kontener:SetAttribute("SerwerKowalaGotowy", true)
