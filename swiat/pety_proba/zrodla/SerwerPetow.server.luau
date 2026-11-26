--[[
	SerwerPetow — jajka i pety na próbę (Script, RunContext = Server, w kontenerze Workspace/PetyProba; budowa:
	swiat/pety_proba/zbuduj.py; status: propozycja, opis w swiat/pety_proba/PROJEKT.md).

	Decyduje WYŁĄCZNIE serwer (klient nie losuje i nie podaje ceny):
		1. Zakup jajka (D.jajka: las, Bagno, Dżungla) — od 26.11.2026 TYLKO przy nowych jajkach ze scenką Pawła
		   (src/server/JajkoKorowe.server.luau sprawdza, że gracz stoi przy jajku, i woła haczyk
		   Sygnaly/SterowanieSerwera("kup", gracz, id, { bezPokazu = true })); starych inkubatorów z własnym E nie ma.
		   kup(gracz, jajko): blokada (D.wyklucie.blokada_s) USTAWIONA PRZED wywołaniem stanu gracza — drugi zakup
		   w tym czasie dostaje odmowę „trwa wyklucie” (scenka zdejmuje ją haczykiem „zwolnij”);
		   cena = LogikaPetow.cena(…) — od 17.11 stała dla każdego jajka (decyzja Karola; licznik kupionych z profilu
		   liczy się tylko w trybie „rosnaca”, osobny albo wspólny — D.licznik_ceny);
		   pet = LogikaPetow.losuj(Random:NextNumber()) z jawnych szans; Złoto i pet — JEDNYM wywołaniem
		   Workspace/StanGracza/Sygnaly/Pety("kup") (właściciel stanu gracza: wydatek + kopia peta bez przerwy);
		   za mało Złota → odmowa z kwotą, której brakuje; potem "wyklucie" do klienta (animację gra klient).
		2. Zdalne/ZdarzeniaPetow od klienta: "lista" (pety gracza do zagrody), "wybierz", id (aktywny pet — tylko
		   posiadany i tylko przy zagrodzie), "odstaw", "czekaj", tak/nie (pet znika na czas walki, przelotu, chmur
		   i mini-gry — atrybut gracza widzą inni klienci). Każde zdarzenie najwyżej co D.limity.odstep_zdarzen_s.
		3. Zapasowe E przy tablicy zagrody (Zagroda/"E wybor") — włączone tylko, gdy nie ma Workspace/MiasteczkoBazarGra
		   (wtedy E opiekunki nie istnieje); otwiera okno wyboru u klienta.
		4. Skill aktywnego peta (D-101) → StanGracza/Sygnaly/Modyfikatory("ustaw", gracz, "pety", LogikaPetow.modPeta):
		   przy wejściu gracza, po zakupie, wyborze i odstawieniu ("usun"). Stan gracza składa go z innymi źródłami
		   w bohatera walki (procent statystyk → pole silnika pet, pasywki żywiołu → premie) i w premię do łupu.
		5. Zagroda daje Rybki (25.11.2026, sesja główna, propozycja — LICZBY ROBOCZE w ustawienia.json → zagroda):
		   co D.zagroda.tik_s serwer liczy pety STOJĄCE w zagrodzie (LogikaPetow.stanZagrody: posiadane, bez aktywnego
		   — on daje skill — i bez petów na wyprawie; wybór gracza albo najrzadsze; najwyżej tyle, ile miejsc ma poziom
		   zagrody) i dopisuje całe Rybki przez StanGracza/Sygnaly/Pety("przychod") — tylko graczom w grze, bez
		   zaległości (dt przycięte do tik_maks_s, przychodu offline nie ma); klient dostaje "zagroda_plus", ile (napis).
		   Miejsca 2 → 4 → 6 → 8: "ulepsz_zagrode" od klienta (przy zagrodzie) → Sygnaly/WydajZloto (cel
		   D.zagroda.cel_ulepszenia — licznik wydatków na ten cel w profilu JEST poziomem, zakup i poziom w jednym
		   wywołaniu). Wybór petów do zagrody ("zagroda_dodaj" / "zagroda_zdejmij", id; "zagroda_auto" = najrzadsze)
		   żyje w profilu przez Sygnaly/DanePakietu (pakiet D.zagroda.pakiet_danych, pole zagroda = lista id).
		6. Sprzedaż petów (26.11.2026, propozycja): Zdalne/SprzedajPety (RemoteFunction, okno Pets) albo haczyk
		   "sprzedaj" → sprzedaj(gracz, lista): lista = { id | { pet = id, ile = n } }; decyzja LogikaPetow.sprzedaz
		   (posiadane kopie, nie ostatnia kopia peta za graczem ani peta stojącego w zagrodzie, nie ostatni pet, suma do
		   D.sprzedaz.maks_kwoty), cena kopii z danych (D.pety[].sprzedaz), kopie i Rybki JEDNYM wywołaniem
		   StanGracza/Sygnaly/Pety("sprzedaj"); najwyżej raz na D.sprzedaz.odstep_s na gracza, jedna sprzedaż naraz.
		   Odpowiedź: { ok, powod, tekst (EN, HUD), tekst_pl, suma, sztuk, zloto, wyniki = { { pet, ile, ok, powod,
		   cena, tekst, tekst_pl } } }.
	Stan petów żyje w profilu StanGracza (jeden właściciel, pod przyszły zapis). Bez StanGracza: zakup odmawia
	z komunikatem, zagroda pokazuje „brak”, żadnych błędów. Atrybuty gracza tego pakietu: dla każdego jajka
	jajko.atrybuty.cena (cena następnego jajka — napis przy E i wskazówki celu) i jajko.atrybuty.kupione (ile takich
	jajek gracz kupił — wskazówka „stać cię na pierwsze jajko biomu”), oraz D.atrybuty_gracza.czeka.
	Haczyk (scenka jajka, okno Pets i testy): Sygnaly/SterowanieSerwera ("kup", gracz?, jajko, r? | { r?, bezPokazu? })
	| ("zwolnij", gracz?) | ("stan", gracz?) | ("sprzedaj", gracz?, lista, bezLimitu?)
	| ("wybierz", gracz?, pet, bezZasiegu?) | ("zgodnosc") | ("zagroda", gracz?) | ("nalicz", gracz?)
	| ("ulepsz", gracz?) | ("zagroda_zmien", gracz?, pet, tak) | ("zagroda_auto", gracz?) — bez sprawdzania zasięgu.
	Działa tylko w Roblox Studio: poza Studio usuwa cały kontener, jak pozostałe prototypy.
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DanePetow"))
local L = require(moduly:WaitForChild("LogikaPetow"))
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaPetow")
local sterowanie: BindableFunction = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera")

local P = D.prefiks
local S = D.stan_gracza
local AG = D.atrybuty_gracza
local los = Random.new()

local function dolicz(nazwa: string)
	kontener:SetAttribute(nazwa, (kontener:GetAttribute(nazwa) or 0) + 1)
end

kontener:SetAttribute("SerwerPetowGotowy", false)
for _, n in { "LicznikZakupow", "LicznikOdmow", "LicznikWyborow", "LicznikModyfikatorow", "LicznikPrzychodow",
	"LicznikUlepszen", "LicznikZmianZagrody", "LicznikSprzedazy", "LicznikOdmowSprzedazy" } do
	kontener:SetAttribute(n, 0)
end

local function zgodnosc(): string
	local ok, n, bledy = L.sprawdzPrzypadki(D)
	local tekst
	if ok then
		tekst = string.format("OK %d/%d", n, n)
	else
		tekst = string.format("BŁĄD %d/%d: %s", n - #bledy, n, tostring(bledy[1]))
		warn(P .. "zgodność logiki: " .. tostring(bledy[1]))
	end
	kontener:SetAttribute("ZgodnoscLogikiPetow", tekst)
	return tekst
end
zgodnosc()

local function teraz(): number
	return workspace:GetServerTimeNow()
end

local function graczOk(gracz: any): boolean
	return typeof(gracz) == "Instance" and gracz:IsA("Player") and gracz.Parent == Players
end

------------------------------------------------------------------ stan gracza (Workspace/StanGracza — tylko przez sygnał)
local function sygnalStanu(nazwa: string): BindableFunction?
	local k = workspace:FindFirstChild(S.kontener)
	if not k or k:GetAttribute("Wygenerowane") ~= true or k:GetAttribute(S.gotowy) ~= true then
		return nil
	end
	local s = k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild(nazwa)
	if f and f:IsA("BindableFunction") then
		return f
	end
	return nil
end

local function sygnalPetow(): BindableFunction?
	return sygnalStanu(S.sygnal_petow)
end

-- jedno wywołanie innego sygnału stanu gracza (WydajZloto, DanePakietu) → wynik albo nil
local function wolajSygnal(nazwa: string, a: any, b: any, c: any, d: any): any
	local f = sygnalStanu(nazwa)
	if not f then
		return nil
	end
	local ok, w = pcall(function()
		if d ~= nil then
			return f:Invoke(a, b, c, d)
		end
		return f:Invoke(a, b, c)
	end)
	if not ok then
		warn(P .. "StanGracza/" .. nazwa .. ": " .. tostring(w))
		return nil
	end
	return w
end

-- skill aktywnego peta (D-101) jako modyfikator bohatera: StanGracza/Sygnaly/Modyfikatory, źródło "pety" — procent
-- statystyk, premia do łupu, pasywki żywiołu. Pierwsze "ustaw" / "usun" przejmuje źródło w stanie gracza: od tej chwili
-- dawna premia z Pety("kup"/"aktywny") się nie liczy (bez podwójnej premii). Bez sygnału (starszy stan gracza) — nic:
-- premia do łupu idzie wtedy jak dawniej, przez Pety.
local function ustawModyfikator(gracz: Player, pet: string?)
	local f = sygnalStanu(S.sygnal_modyfikatorow)
	if not f or not graczOk(gracz) then
		return nil
	end
	local mod = if pet then L.modPeta(D, pet) else nil
	local ok, w = pcall(function()
		if mod then
			return f:Invoke("ustaw", gracz, S.zrodlo_modyfikatora, mod)
		end
		return f:Invoke("usun", gracz, S.zrodlo_modyfikatora)
	end)
	if ok and type(w) == "table" and w.ok then
		dolicz("LicznikModyfikatorow")
		kontener:SetAttribute("OstatniModyfikator", string.format("%s:%s", gracz.Name, tostring(if mod then pet else "brak")))
		return w
	end
	warn(P .. "StanGracza/Modyfikatory: " .. tostring(if ok and type(w) == "table" then w.powod else w))
	return nil
end

local function wolajPety(polecenie: string, gracz: Player, info: any)
	local f = sygnalPetow()
	if not f then
		return nil
	end
	local ok, w = pcall(function()
		return f:Invoke(polecenie, gracz, info)
	end)
	if ok and type(w) == "table" then
		return w
	end
	if not ok then
		warn(P .. "StanGracza/Pety " .. polecenie .. ": " .. tostring(w))
	end
	return nil
end

local function wydatki(st)
	return if st and type(st.wydatki) == "table" then st.wydatki else {}
end

-- atrybuty każdego jajka: cena następnego (licznik osobny albo wspólny) i ile takich jajek gracz kupił
local function ustawCeny(gracz: Player, wyd)
	for _, j in D.jajka do
		gracz:SetAttribute(j.atrybuty.cena, L.cena(D, j, L.kupione(D, j, wyd)))
		gracz:SetAttribute(j.atrybuty.kupione, L.kupione(D, j, wyd, "osobny"))
	end
end


------------------------------------------------------------------ kupno i wyklucie
local zajety: { [Player]: number } = {}

local function odmowa(gracz: Player, powod: string, tekst: string)
	dolicz("LicznikOdmow")
	kontener:SetAttribute("OstatniaOdmowa", powod)
	zdarzenia:FireClient(gracz, "odmowa", tekst, powod)
	return { ok = false, powod = powod, tekst = tekst }
end

local function polozenie(gracz: Player): Vector3?
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	return if hrp and hrp:IsA("BasePart") then hrp.Position else nil
end

-- bezPokazu: zakup ze scenki jajka w świecie (src/server/JajkoKorowe.server.luau, 26.11.2026) — klient nie gra
-- żadnej animacji, a napis „Wykluł się…” pokazuje dopiero, gdy scenka odsłoni peta (Sygnaly/PokazWyklucia u klienta)
local function kup(gracz: any, idJajka: any, wymuszoneR: any, bezPokazu: boolean?)
	if not graczOk(gracz) then
		return { ok = false, powod = "zly_gracz" }
	end
	local t = teraz()
	local d = L.decyzja(D, { stan_gracza = sygnalPetow() ~= nil, jajko = idJajka,
		zajety = zajety[gracz] ~= nil and t < zajety[gracz] })
	if not d.ok then
		return odmowa(gracz, d.powod, d.tekst)
	end
	local j = L.jajko(D, idJajka)
	zajety[gracz] = t + D.wyklucie.blokada_s -- przed wywołaniem: drugi E w tym czasie dostaje „trwa wyklucie”
	local st = wolajPety("stan", gracz)
	if not st or not st.ok then
		zajety[gracz] = nil
		return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
	end
	local wyd = wydatki(st)
	local cena = L.cena(D, j, L.kupione(D, j, wyd))
	local r = if type(wymuszoneR) == "number" and wymuszoneR >= 0 and wymuszoneR < 1 then wymuszoneR else los:NextNumber()
	local pet = L.losuj(D, j, r)
	local w = wolajPety("kup", gracz, { ile = cena, zrodlo = D.kontener, cel = j.id, pet = pet,
		premia = L.premiaPeta(D, pet) })
	if not w or not w.ok then
		zajety[gracz] = nil
		if w and w.powod == "za_malo" then
			return odmowa(gracz, "za_malo", L.tekstBraku(D, w.brakuje, w.zloto, cena))
		end
		return odmowa(gracz, if w then tostring(w.powod) else "brak_stanu", if w then D.teksty.blad else D.teksty.brak_stanu)
	end
	local poZakupie = {}
	for k, v in wyd do
		poZakupie[k] = v
	end
	poZakupie[j.id] = if type(w.licznik) == "number" then w.licznik else L.kupione(D, j, wyd, "osobny") + 1
	ustawCeny(gracz, poZakupie)
	local nastepna = L.cena(D, j, L.kupione(D, j, poZakupie))
	local info = { jajko = j.id, pet = pet, nowy = w.nowy == true, kopie = w.kopie, aktywny = w.aktywny, cena = cena,
		nastepna = nastepna, zloto = w.zloto, bezPokazu = bezPokazu == true }
	zdarzenia:FireClient(gracz, "wyklucie", info)
	ustawModyfikator(gracz, if type(w.aktywny) == "string" then w.aktywny else nil)
	dolicz("LicznikZakupow")
	kontener:SetAttribute("OstatniZakup", string.format("%s:%s:%s:%dz", gracz.Name, j.id, pet, cena))
	info.ok = true
	return info
end

------------------------------------------------------------------ zagroda: Rybki, miejsca, wybór (25.11.2026)
local wyborZagrody: { [Player]: any } = {} -- lista id (wybór gracza) albo nil (najrzadsze)
local wczytanyWybor: { [Player]: boolean } = {}
local tikZagrody: { [Player]: number } = {}
local resztaZagrody: { [Player]: number } = {}
local zmianaZagrody: { [Player]: boolean } = {} -- blokada na czas ulepszenia (dwa kliknięcia naraz nie kupią dwa razy)
local ostrzezonyPrzychod = false

-- Pety zabrane na wyprawę nie stoją w zagrodzie i nie dają Rybek. Wypraw jeszcze nie ma (25.11.2026): tu wpiąć ich
-- stan — tabela { [id peta] = true } albo nil.
local function naWyprawie(_gracz: Player): any
	return nil
end

local function stanZagrody(gracz: Player, st)
	return L.stanZagrody(D, st.kopie, st.aktywny, wyborZagrody[gracz], st.wydatki, naWyprawie(gracz))
end

-- wybór gracza z profilu (Sygnaly/DanePakietu); bez sygnału (starszy stan gracza) — tylko w pamięci serwera
local function wczytajWybor(gracz: Player)
	local v = wolajSygnal(S.sygnal_danych, "czytaj", gracz, D.zagroda.pakiet_danych)
	wyborZagrody[gracz] = if type(v) == "table" then L.czystyWybor(D, v.zagroda) else nil
	wczytanyWybor[gracz] = true
end

local function zapiszWybor(gracz: Player, w: any)
	wyborZagrody[gracz] = w
	local r = wolajSygnal(S.sygnal_danych, "zapisz", gracz, D.zagroda.pakiet_danych, if w then { zagroda = w } else {})
	if r ~= nil and (type(r) ~= "table" or not r.ok) then
		warn(P .. "DanePakietu zapisz: " .. tostring(if type(r) == "table" then r.powod else r))
	end
end

-- co D.zagroda.tik_s: Rybki za pety stojące w zagrodzie od poprzedniego razu (tylko gracz w grze, z wczytanym profilem)
local function naliczZagrode(gracz: Player, t: number)
	if not graczOk(gracz) or gracz:GetAttribute(S.atrybut_wczytania) == false or not wczytanyWybor[gracz] then
		tikZagrody[gracz] = nil
		return nil
	end
	local poprz = tikZagrody[gracz]
	tikZagrody[gracz] = t
	if poprz == nil then
		return nil
	end
	local st = wolajPety("stan", gracz)
	if not st or not st.ok then
		return nil
	end
	local z = stanZagrody(gracz, st)
	local ile, reszta = L.tik(D, resztaZagrody[gracz] or 0, z.stawka_s, t - poprz)
	resztaZagrody[gracz] = reszta
	if ile < 1 then
		return 0
	end
	local w = wolajPety("przychod", gracz, { ile = ile, zrodlo = D.kontener, cel = D.zagroda.cel_przychodu })
	if w and w.ok then
		dolicz("LicznikPrzychodow")
		kontener:SetAttribute("OstatniPrzychod", string.format("%s:+%d:%d", gracz.Name, ile, #z.stoja))
		zdarzenia:FireClient(gracz, "zagroda_plus", ile)
		return ile
	end
	if not ostrzezonyPrzychod then
		ostrzezonyPrzychod = true
		warn(P .. "StanGracza/Pety przychod odmówił (" .. tostring(if w then w.powod else "brak sygnału")
			.. ") — zagroda nie daje Rybek; przebuduj stan gracza (swiat/stan_gracza/zbuduj.py --skrypty)")
	end
	return nil
end

local function tikWszystkich()
	local t = teraz()
	for _, g in Players:GetPlayers() do
		local ok, blad = pcall(naliczZagrode, g, t)
		if not ok then
			warn(P .. "zagroda: " .. tostring(blad))
		end
	end
	task.delay(D.zagroda.tik_s, tikWszystkich)
end
task.delay(D.zagroda.tik_s, tikWszystkich)

------------------------------------------------------------------ zagroda: lista, wybór, odstawienie
local function przyZagrodzie(gracz: Player): boolean
	local p = polozenie(gracz)
	if not p then
		return false
	end
	local e = D.polozenia.zagroda_e
	local dx, dz = p.X - e[1], p.Z - e[3]
	return dx * dx + dz * dz <= D.zagroda.zasieg_wyboru * D.zagroda.zasieg_wyboru
end

local function wyslijListe(gracz: Player)
	local st = wolajPety("stan", gracz)
	if not st or not st.ok then
		zdarzenia:FireClient(gracz, "lista", { brak = true, tekst = D.teksty.brak_stanu })
		return
	end
	zdarzenia:FireClient(gracz, "lista", { wiersze = L.wierszeZagrody(D, st.kopie, st.aktywny), aktywny = st.aktywny,
		zagroda = stanZagrody(gracz, st) })
end

local function wybierz(gracz: Player, pet: any, bezZasiegu: boolean?)
	if type(pet) ~= "string" or #pet > D.limity.dlugosc_id or L.pet(D, pet) == nil then
		return odmowa(gracz, "nie_masz", D.teksty.nie_masz)
	end
	if not bezZasiegu and not przyZagrodzie(gracz) then
		return odmowa(gracz, "za_daleko", D.teksty.za_daleko)
	end
	local przed = wolajPety("stan", gracz)
	local stary = if przed and przed.ok and type(przed.aktywny) == "string" then przed.aktywny else nil
	local w = wolajPety("aktywny", gracz, { pet = pet, premia = L.premiaPeta(D, pet) })
	if not w then
		return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
	end
	if not w.ok then
		return odmowa(gracz, tostring(w.powod), D.teksty.nie_masz)
	end
	dolicz("LicznikWyborow")
	if wyborZagrody[gracz] ~= nil then -- wybór ręczny: nowy pet za graczem zwalnia miejsce w zagrodzie dla starego
		zapiszWybor(gracz, L.poWyborze(D, wyborZagrody[gracz], stary, pet))
	end
	ustawModyfikator(gracz, pet)
	zdarzenia:FireClient(gracz, "wybrany", pet)
	wyslijListe(gracz)
	return { ok = true, aktywny = pet }
end

local function odstaw(gracz: Player)
	if not przyZagrodzie(gracz) then
		return odmowa(gracz, "za_daleko", D.teksty.za_daleko)
	end
	local przed = wolajPety("stan", gracz)
	local stary = if przed and przed.ok and type(przed.aktywny) == "string" then przed.aktywny else nil
	local w = wolajPety("aktywny", gracz, { odstaw = true })
	if not w or not w.ok then
		return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
	end
	if wyborZagrody[gracz] ~= nil then -- wybór ręczny: odstawiony pet wraca do zagrody (gdy jest miejsce)
		zapiszWybor(gracz, L.poOdstawieniu(D, wyborZagrody[gracz], stary))
	end
	ustawModyfikator(gracz, nil)
	zdarzenia:FireClient(gracz, "wybrany", nil)
	wyslijListe(gracz)
	return { ok = true }
end

-- „Do zagrody” / „Z zagrody” (tak = true / false): wybór ręczny od tego, co dziś stoi
local function zmienZagrode(gracz: Player, pet: any, tak: boolean, bezZasiegu: boolean?)
	if type(pet) ~= "string" or #pet > D.limity.dlugosc_id then
		return odmowa(gracz, "nie_masz", D.teksty.nie_masz)
	end
	if not bezZasiegu and not przyZagrodzie(gracz) then
		return odmowa(gracz, "za_daleko", D.teksty.za_daleko)
	end
	local st = wolajPety("stan", gracz)
	if not st or not st.ok or not wczytanyWybor[gracz] then
		return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
	end
	local nowy, powod = L.zmienWybor(D, st.kopie, st.aktywny, wyborZagrody[gracz], st.wydatki, naWyprawie(gracz),
		pet, tak)
	if powod == "ok" then
		zapiszWybor(gracz, nowy)
		dolicz("LicznikZmianZagrody")
	elseif powod ~= "juz" and powod ~= "nie_stoi" then
		local teksty = { nie_masz = D.teksty.nie_masz, aktywny = D.teksty.aktywny_nie_w_zagrodzie, pelna = D.teksty.pelna }
		return odmowa(gracz, powod, teksty[powod] or D.teksty.blad)
	end
	wyslijListe(gracz)
	return { ok = true, powod = powod, wybor = wyborZagrody[gracz] }
end

local function zagrodaAuto(gracz: Player, bezZasiegu: boolean?)
	if not bezZasiegu and not przyZagrodzie(gracz) then
		return odmowa(gracz, "za_daleko", D.teksty.za_daleko)
	end
	zapiszWybor(gracz, nil)
	dolicz("LicznikZmianZagrody")
	wyslijListe(gracz)
	return { ok = true }
end

-- więcej miejsc u opiekunki: cena z poziomu (licznik wydatków na cel ulepszenia), Rybki przez WydajZloto — ten sam
-- licznik jest poziomem, więc zakup i poziom zapisują się razem; za mało Rybek = odmowa z kwotą, nic nie zmienione
local function ulepszZagrode(gracz: Player, bezZasiegu: boolean?)
	if not bezZasiegu and not przyZagrodzie(gracz) then
		return odmowa(gracz, "za_daleko", D.teksty.za_daleko)
	end
	if zmianaZagrody[gracz] then
		return odmowa(gracz, "zajeta", D.teksty.zagroda_zajeta)
	end
	zmianaZagrody[gracz] = true -- przed pierwszym wywołaniem stanu: drugie kliknięcie w tym czasie dostaje odmowę
	local ok, w = pcall(function()
		local st = wolajPety("stan", gracz)
		if not st or not st.ok or not sygnalStanu(S.sygnal_wydatkow) then
			return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
		end
		local poziom = L.poziomZagrody(D, st.wydatki)
		local cena = L.cenaUlepszenia(D, poziom)
		if cena == nil then
			return odmowa(gracz, "max", string.format(D.teksty.ulepsz_max, L.miejscaZagrody(D, poziom)))
		end
		local r = wolajSygnal(S.sygnal_wydatkow, gracz, { ile = cena, zrodlo = D.kontener, cel = D.zagroda.cel_ulepszenia })
		if type(r) ~= "table" then
			return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
		end
		if not r.ok then
			if r.powod == "za_malo" then
				return odmowa(gracz, "za_malo", L.tekstBrakuUlepszenia(D, r.brakuje, r.zloto, cena))
			end
			return odmowa(gracz, tostring(r.powod), D.teksty.blad)
		end
		local nowy = L.poziomZagrody(D, { [D.zagroda.cel_ulepszenia] = r.licznik })
		local miejsc = L.miejscaZagrody(D, nowy)
		dolicz("LicznikUlepszen")
		kontener:SetAttribute("OstatnieUlepszenie", string.format("%s:%d:%d:%dz", gracz.Name, nowy, miejsc, cena))
		zdarzenia:FireClient(gracz, "zagroda_ulepszona", miejsc)
		return { ok = true, poziom = nowy, miejsc = miejsc, cena = cena, zloto = r.zloto }
	end)
	zmianaZagrody[gracz] = nil
	if not ok then
		warn(P .. "ulepszenie zagrody: " .. tostring(w))
		return odmowa(gracz, "blad", D.teksty.blad)
	end
	if w.ok then
		wyslijListe(gracz)
	end
	return w
end

------------------------------------------------------------------ sprzedaż petów (26.11.2026, propozycja)
local SP = D.sprzedaz
local sprzedajeTeraz: { [Player]: boolean } = {}
local ostatniaSprzedaz: { [Player]: number } = {}

local function tekstSprzedazy(powod: string, jezyk: string): string
	local t = SP.teksty[powod] or SP.teksty.blad
	return t[jezyk] or ""
end

local function odmowaSprzedazy(powod: string)
	dolicz("LicznikOdmowSprzedazy")
	kontener:SetAttribute("OstatniaOdmowaSprzedazy", powod)
	return { ok = false, powod = powod, tekst = tekstSprzedazy(powod, "en"), tekst_pl = tekstSprzedazy(powod, "pl"),
		suma = 0, sztuk = 0, wyniki = {} }
end

-- „3 pets for 120 fish” / „3 pety za 120 Rybek”
local function tekstSprzedanych(sztuk: number, suma: number): (string, string)
	local en = SP.formy_peta.en[if sztuk == 1 then 1 else 2]
	return string.format(SP.teksty.ok.en, string.format("%d %s", sztuk, en), string.format("%d %s", suma, SP.jednostka_en)),
		string.format(SP.teksty.ok.pl, string.format("%d %s", sztuk, L.forma(SP.formy_peta.pl, sztuk)),
			L.ileRybek(D, suma, "b"))
end

local function sprzedaj(gracz: any, lista: any, bezLimitu: boolean?)
	if not graczOk(gracz) then
		return { ok = false, powod = "zly_gracz", wyniki = {}, suma = 0, sztuk = 0 }
	end
	local t = os.clock()
	if sprzedajeTeraz[gracz] then
		return odmowaSprzedazy("zajete")
	end
	if not bezLimitu and ostatniaSprzedaz[gracz] and t - ostatniaSprzedaz[gracz] < SP.odstep_s then
		return odmowaSprzedazy("za_szybko")
	end
	ostatniaSprzedaz[gracz] = t
	sprzedajeTeraz[gracz] = true -- przed pierwszym wywołaniem stanu: druga sprzedaż w tym czasie dostaje odmowę
	local ok, w = pcall(function()
		local st = wolajPety("stan", gracz)
		if not st or not st.ok or not wczytanyWybor[gracz] then
			return odmowaSprzedazy("brak_stanu")
		end
		local d = L.sprzedaz(D, st.kopie, st.aktywny, stanZagrody(gracz, st).stoja, lista)
		for _, r in d.wyniki do
			r.tekst, r.tekst_pl = tekstSprzedazy(r.powod, "en"), tekstSprzedazy(r.powod, "pl")
		end
		if not d.ok then
			local o = odmowaSprzedazy(d.powod)
			o.wyniki = d.wyniki
			return o
		end
		-- kopie i Rybki jednym wywołaniem właściciela stanu (sprawdza kopie i peta za graczem jeszcze raz)
		local r = wolajPety("sprzedaj", gracz, { pety = d.pozycje, ile = d.suma, zrodlo = D.kontener, cel = SP.cel })
		if not r or not r.ok then
			local powod = if r == nil then "brak_stanu" elseif r.powod == "nie_masz" or r.powod == "aktywny" then r.powod
				else "blad"
			if r and powod == "blad" then
				warn(P .. "StanGracza/Pety sprzedaj odmówił: " .. tostring(r.powod))
			end
			return odmowaSprzedazy(powod)
		end
		-- wybór ręczny zagrody bez petów, których gracz już nie ma
		local wyb = wyborZagrody[gracz]
		if wyb ~= nil and type(r.kopie) == "table" then
			local nowy = {}
			for _, id in wyb do
				if type(r.kopie[id]) == "number" and r.kopie[id] > 0 then
					table.insert(nowy, id)
				end
			end
			if #nowy ~= #wyb then
				zapiszWybor(gracz, nowy)
			end
		end
		dolicz("LicznikSprzedazy")
		kontener:SetAttribute("OstatniaSprzedaz", string.format("%s:%d:%dz", gracz.Name, d.sztuk, d.suma))
		d.zloto = r.zloto
		d.tekst, d.tekst_pl = tekstSprzedanych(d.sztuk, d.suma)
		wyslijListe(gracz) -- tablica, zagroda i tymczasowe okno u klienta
		return d
	end)
	sprzedajeTeraz[gracz] = nil
	if not ok then
		warn(P .. "sprzedaż: " .. tostring(w))
		return odmowaSprzedazy("blad")
	end
	return w
end

local zdalnaSprzedaz = kontener:WaitForChild("Zdalne"):FindFirstChild("SprzedajPety")
if zdalnaSprzedaz and zdalnaSprzedaz:IsA("RemoteFunction") then
	zdalnaSprzedaz.OnServerInvoke = function(gracz: Player, lista: any)
		return sprzedaj(gracz, lista, false) -- bez liczb od klienta: tylko id petów i liczba kopii
	end
else
	warn(P .. "brak Zdalne/SprzedajPety — przebuduj kontener (zbuduj.py); sprzedaż działa tylko przez haczyk")
end

------------------------------------------------------------------ zdarzenia od klienta (bez liczb, z limitem)
local ostatnie: { [Player]: number } = {}
zdarzenia.OnServerEvent:Connect(function(gracz: Player, polecenie: any, a: any)
	if type(polecenie) ~= "string" then
		return
	end
	local t = os.clock()
	local klucz = gracz
	if ostatnie[klucz] and t - ostatnie[klucz] < D.limity.odstep_zdarzen_s and polecenie ~= "czekaj" then
		return
	end
	ostatnie[klucz] = t
	local ok, blad = pcall(function()
		if polecenie == "lista" then
			wyslijListe(gracz)
		elseif polecenie == "wybierz" then
			wybierz(gracz, a, false)
		elseif polecenie == "odstaw" then
			odstaw(gracz)
		elseif polecenie == "zagroda_dodaj" then
			zmienZagrode(gracz, a, true, false)
		elseif polecenie == "zagroda_zdejmij" then
			zmienZagrode(gracz, a, false, false)
		elseif polecenie == "zagroda_auto" then
			zagrodaAuto(gracz, false)
		elseif polecenie == "ulepsz_zagrode" then
			ulepszZagrode(gracz, false)
		elseif polecenie == "czekaj" then
			local czeka = if a == true then true else nil
			if gracz:GetAttribute(AG.czeka) ~= czeka then
				gracz:SetAttribute(AG.czeka, czeka)
			end
		end
	end)
	if not ok then
		warn(P .. "zdarzenie " .. polecenie .. ": " .. tostring(blad))
	end
end)

------------------------------------------------------------------ zapasowe E zagrody (część z budowy w Edit)
local function podpowiedz(sciezka: { string }): ProximityPrompt?
	local o: Instance? = kontener
	for _, n in sciezka do
		o = o and o:FindFirstChild(n)
	end
	return if o and o:IsA("ProximityPrompt") then o else nil
end

local promptZagrody = podpowiedz({ "Zagroda", "E wybor", "Podpowiedz" })
local function zapasoweE()
	if promptZagrody then
		promptZagrody.Enabled = workspace:FindFirstChild(D.zagroda.kontener_bazaru) == nil
		kontener:SetAttribute("ZapasoweEZagrody", promptZagrody.Enabled)
	end
end
if promptZagrody then
	promptZagrody.Triggered:Connect(function(gracz: Player)
		zdarzenia:FireClient(gracz, "okno")
	end)
end
zapasoweE()
workspace.ChildAdded:Connect(function(o)
	if o.Name == D.zagroda.kontener_bazaru then
		zapasoweE()
	end
end)
workspace.ChildRemoved:Connect(function(o)
	if o.Name == D.zagroda.kontener_bazaru then
		zapasoweE()
	end
end)

------------------------------------------------------------------ gracze
-- ceny jajek i skill aktywnego peta z profilu stanu gracza
local function zProfilu(gracz: Player)
	local st = wolajPety("stan", gracz)
	ustawCeny(gracz, wydatki(st))
	wczytajWybor(gracz) -- wybór petów do zagrody (DanePakietu); od teraz zagroda nalicza Rybki
	-- modyfikator od razu przy wejściu (przejmuje źródło "pety" w stanie gracza, zanim przyjdzie pierwszy łup)
	ustawModyfikator(gracz, if st and type(st.aktywny) == "string" then st.aktywny else nil)
end

-- zapis postępu (D-110, 19.11.2026): StanGracza wczytuje profil po wejściu; do końca (atrybut gracza
-- StanGraczaWczytany = false) Pety i Modyfikatory odmawiają — ceny i skill peta ustawiamy, gdy atrybut zmieni się na true
local ATR_WCZYTANIA = S.atrybut_wczytania

local function nowyGracz(gracz: Player)
	ustawCeny(gracz, {})
	gracz:GetAttributeChangedSignal(ATR_WCZYTANIA):Connect(function()
		if gracz:GetAttribute(ATR_WCZYTANIA) == true and graczOk(gracz) and sygnalPetow() then
			zProfilu(gracz)
		end
	end)
	-- stan gracza może ruszyć później (kolejność skryptów) — cena z profilu, gdy będzie
	for _ = 1, 20 do
		if not graczOk(gracz) or gracz:GetAttribute(ATR_WCZYTANIA) == false then
			return -- wczytywanie profilu: resztę zrobi słuchacz atrybutu
		end
		if sygnalPetow() then
			zProfilu(gracz)
			return
		end
		task.wait(1)
	end
end
Players.PlayerAdded:Connect(nowyGracz)
for _, g in Players:GetPlayers() do
	task.spawn(nowyGracz, g)
end
Players.PlayerRemoving:Connect(function(gracz: Player)
	zajety[gracz] = nil
	ostatnie[gracz] = nil
	sprzedajeTeraz[gracz] = nil
	ostatniaSprzedaz[gracz] = nil
	-- zagroda: bez przychodu offline — po wyjściu nic się nie nalicza, po powrocie liczy się od nowa
	wyborZagrody[gracz] = nil
	wczytanyWybor[gracz] = nil
	tikZagrody[gracz] = nil
	resztaZagrody[gracz] = nil
	zmianaZagrody[gracz] = nil
end)

------------------------------------------------------------------ haczyk testowy
local function ktory(g: any): Player?
	if typeof(g) == "Instance" and g:IsA("Player") then
		return g
	end
	return Players:GetPlayers()[1]
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any, c: any)
	if polecenie == "zgodnosc" then
		return zgodnosc()
	end
	local g = ktory(a)
	if not g then
		return nil
	end
	if polecenie == "kup" then
		-- c: wymuszone r (liczba) albo opcje { r = liczba?, bezPokazu = true? } (scenka jajka w świecie)
		local opcje = if type(c) == "table" then c else nil
		return kup(g, b or D.jajka[1].id, if opcje then opcje.r else c, opcje ~= nil and opcje.bezPokazu == true)
	elseif polecenie == "sprzedaj" then
		return sprzedaj(g, b, c == true)
	elseif polecenie == "zwolnij" then
		zajety[g] = nil
		return true
	elseif polecenie == "wybierz" then
		return wybierz(g, b, c == true)
	elseif polecenie == "zagroda" then
		local st = wolajPety("stan", g)
		return { stan = if st and st.ok then stanZagrody(g, st) else nil, wybor = wyborZagrody[g],
			wczytany = wczytanyWybor[g] == true, reszta = resztaZagrody[g], tik = tikZagrody[g] }
	elseif polecenie == "nalicz" then
		return naliczZagrode(g, teraz())
	elseif polecenie == "ulepsz" then
		return ulepszZagrode(g, true)
	elseif polecenie == "zagroda_zmien" then
		return zmienZagrode(g, b, c == true, true)
	elseif polecenie == "zagroda_auto" then
		return zagrodaAuto(g, true)
	elseif polecenie == "stan" then
		local st = wolajPety("stan", g)
		local ceny, kupioneJ = {}, {}
		for _, j in D.jajka do
			ceny[j.id] = g:GetAttribute(j.atrybuty.cena)
			kupioneJ[j.id] = g:GetAttribute(j.atrybuty.kupione)
		end
		local fm = sygnalStanu(S.sygnal_modyfikatorow)
		local mod = nil
		if fm then
			local okm, wm = pcall(function()
				return fm:Invoke("czytaj", g)
			end)
			mod = if okm then wm else nil
		end
		return { stanGracza = sygnalPetow() ~= nil, modyfikatory = mod, zajety = zajety[g] ~= nil and teraz() < zajety[g],
			cena = ceny[D.jajka[1].id], ceny = ceny, kupione = kupioneJ, czeka = g:GetAttribute(AG.czeka), pety = st,
			zapasoweE = kontener:GetAttribute("ZapasoweEZagrody"),
			-- 26.11.2026: stan zagrody (kto stoi i daje Rybki) — okno Pets oznacza nim pety „w zagrodzie”
			zagroda = if st and st.ok then stanZagrody(g, st) else nil }
	end
	warn(P .. "SterowanieSerwera: nieznane polecenie " .. tostring(polecenie))
	return nil
end

kontener:SetAttribute("SerwerPetowGotowy", true)
local opisJajek = {}
for _, j in D.jajka do
	table.insert(opisJajek, string.format("%s od %d", j.id, L.cena(D, j, 0)))
end
print(string.format("%sgotowy: logika %s, stan gracza %s, jajka: %s (licznik ceny %s)", P,
	tostring(kontener:GetAttribute("ZgodnoscLogikiPetow")), if sygnalPetow() then "jest" else "BRAK (zakup odmawia)",
	table.concat(opisJajek, ", "), D.licznik_ceny.tryb))
