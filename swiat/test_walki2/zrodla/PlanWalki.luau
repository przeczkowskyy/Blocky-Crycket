--[[
	PlanWalki — CZYSTA logika odtwarzacza walki pod dziennik v3 (ModuleScript w Moduly; bez usług Roblox, bez
	instancji). Używa jej OdtwarzaczWalki2; testy bez Studio (testy/test_odtwarzacza.py) wykonują DOKŁADNIE ten plik
	interpreterem tools/walka/luau_mini.py na tysiącach dzienników z portu silnika, więc kod trzyma się podzbioru Luau
	(bez metatablic, table.remove/sort/clone, string.upper/gsub, math.clamp i rzutowań `::`).

	Co tu jest:
	  • normalizuj(walka) → (walka, ostrzeżenia) | (nil, błąd) — kopia dziennika z KAŻDYM polem w znanym rodzaju:
	    brakujące pole dostaje wartość domyślną (życie i mana przechodzą z poprzedniego zdarzenia), nieznane pole
	    i nieznany typ zdarzenia dają ostrzeżenie (raz na nazwę), a odtwarzanie idzie dalej (wymóg paczki v3);
	    zdarzenie bez strony (kto) jest pomijane z ostrzeżeniem — nie da się go narysować;
	  • plan(walka) → zdarzenia z: turą (ta sama księgowość co silnik: walka.tury), użyciem many (koszt = wartosc),
	    maną przed i po (z dziennika — klient NIE liczy many), progiem i gotowością paska (próg = koszt NASTĘPNEGO
	    użycia tej strony z dziennika albo pełny pasek), powaleniem przed wskrzeszeniem, ciosem kończącym, źródłem
	    efektu (umiejętność, która go nałożyła);
	  • stan efektów: nowyStan / nalozony / tykniecie / koniec / koniecTury / lista — liczniki tur, stosy trucizny,
	    procent tarczy (typ „oslona”); ta sama logika rysuje ikony w interfejsie;
	  • opisPasywki(Dane, id, zrodlo, etykiety) — zapowiedź pasywki na starcie walki: nazwa i premie z danych silnika
	    (np. „+4% życia · +2% obrażeń”); etykiety słów są w Choreografie.MODYFIKATORY, liczby tylko z danych;
	  • blokZatrzymuje(walka) — ile procent ciosu zabiera blok (z walka.czesc_przez_blok).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local P = {}

-- typy zdarzeń dziennika v3, które odtwarzacz zna (test: = Dziennik.TYPY)
P.TYPY = {
	"cios",
	"krytyk",
	"blok",
	"unik",
	"umiejetnosc",
	"efekt_tick",
	"efekt_nalozony",
	"efekt_koniec",
	"utrata_tury",
	"wskrzeszenie",
}
-- pola zdarzenia v3 i ich rodzaj (test: zbiór pól = pola każdego zdarzenia z silnika — nowe pole silnika = błąd testu)
P.POLA_ZDARZENIA = {
	typ = "napis",
	kto = "strona",
	cel = "strona",
	obrazenia = "liczba",
	pochloniete = "liczba",
	rodzaj = "napis",
	umiejetnosc = "napis",
	efekt = "napis",
	krytyk = "logiczna",
	wartosc = "liczba",
	tury = "liczba",
	stosy = "liczba",
	t = "liczba",
	trwa = "liczba",
	hp_gracz = "liczba",
	hp_wrog = "liczba",
	mana_gracz = "liczba",
	mana_wrog = "liczba",
}
-- pola walki i strony (test: = pola z silnika)
P.POLA_WALKI = {
	wersja = true,
	ziarno = true,
	strony = true,
	wynik = true,
	tury = true,
	bezpiecznik = true,
	lup = true,
	czesc_przez_blok = true,
	czas_wstepu = true,
	czas_finalu = true,
	czas = true,
	dziennik = true,
}
P.POLA_STRONY = {
	nazwa = true,
	rodzaj = true,
	id = true,
	ranga = true,
	poziom = true,
	zycie = true,
	mana = true,
	mana_maks = true,
}
P.POLA_LUPU = { zloto = true, doswiadczenie = true, tokeny_krainy = true, gemy = true, shard_ewolucji = true, kraina = true }
-- zdarzenia, które są akcją strony na jej turze (zmiana strony = nowa tura) — jak w silniku
P.AKCJE_TURY = {
	cios = true,
	krytyk = true,
	blok = true,
	unik = true,
	umiejetnosc = true,
	utrata_tury = true,
	efekt_tick = true,
}
-- zdarzenia z trafieniem w chwili eHit (paski i mana zmieniają się wtedy, nie na początku zdarzenia)
P.Z_TRAFIENIEM = { cios = true, krytyk = true, blok = true, unik = true, efekt_tick = true }

local STRONY = { "gracz", "wrog" }

local function liczba(v: any, domyslna: any): any
	if type(v) == "number" and v == v and v ~= math.huge and v ~= -math.huge then
		return v
	end
	return domyslna
end

local function zaokraglij(x: number): number
	return math.floor(x + 0.5)
end

------------------------------------------------------------------ normalizacja (odporność na nieznane i brakujące)
function P.normalizuj(walka: any): (any, any)
	local ostrzezenia = {}
	local widziane = {}
	local function ostrzez(tekst: string)
		if not widziane[tekst] then
			widziane[tekst] = true
			table.insert(ostrzezenia, tekst)
		end
	end
	if type(walka) ~= "table" or type(walka.dziennik) ~= "table" or type(walka.strony) ~= "table" then
		return nil, "brak dziennika albo stron"
	end
	for k in walka do
		if not P.POLA_WALKI[k] then
			ostrzez("nieznane pole walki: " .. tostring(k))
		end
	end
	local strony = {}
	for _, s in STRONY do
		local d = walka.strony[s]
		if type(d) ~= "table" then
			return nil, "brak strony " .. s
		end
		for k in d do
			if not P.POLA_STRONY[k] then
				ostrzez("nieznane pole strony: " .. tostring(k))
			end
		end
		local zycie = liczba(d.zycie, 0)
		if zycie < 1 then
			return nil, "złe życie strony " .. s
		end
		local manaMaks = liczba(d.mana_maks, nil)
		if manaMaks == nil or manaMaks < 1 then
			ostrzez("brak pola strony: mana_maks")
			manaMaks = 100
		end
		local mana = liczba(d.mana, nil)
		if mana == nil then
			ostrzez("brak pola strony: mana")
			mana = 0
		end
		strony[s] = {
			nazwa = if type(d.nazwa) == "string" then d.nazwa else s,
			rodzaj = if type(d.rodzaj) == "string" then d.rodzaj else "postac",
			id = if type(d.id) == "string" then d.id else "",
			ranga = if type(d.ranga) == "string" then d.ranga else "zwykly",
			poziom = liczba(d.poziom, 1),
			zycie = zycie,
			mana = math.max(0, math.min(mana, manaMaks)),
			mana_maks = manaMaks,
		}
	end
	local znane = {}
	for _, t in P.TYPY do
		znane[t] = true
	end
	local poprz = {
		hp_gracz = strony.gracz.zycie,
		hp_wrog = strony.wrog.zycie,
		mana_gracz = strony.gracz.mana,
		mana_wrog = strony.wrog.mana,
	}
	local t = liczba(walka.czas_wstepu, 0)
	local dziennik = {}
	for i = 1, #walka.dziennik do
		local z = walka.dziennik[i]
		if type(z) ~= "table" then
			ostrzez("zdarzenie " .. tostring(i) .. " nie jest tabelą — pomijam je")
		elseif z.kto ~= "gracz" and z.kto ~= "wrog" then
			ostrzez("zdarzenie bez strony (kto) — pomijam je")
		else
			for pole in z do
				if P.POLA_ZDARZENIA[pole] == nil then
					ostrzez("nieznane pole zdarzenia: " .. tostring(pole))
				end
			end
			for pole in P.POLA_ZDARZENIA do
				if z[pole] == nil then
					ostrzez("brak pola zdarzenia: " .. pole)
				end
			end
			local n = {}
			n.typ = if type(z.typ) == "string" then z.typ else "?"
			n.nieznany = not znane[n.typ]
			if n.nieznany then
				ostrzez("nieznany typ zdarzenia: " .. n.typ)
			end
			n.kto = z.kto
			n.cel = if z.cel == "gracz" or z.cel == "wrog" then z.cel else z.kto
			for _, pole in { "obrazenia", "pochloniete", "wartosc", "tury", "stosy" } do
				n[pole] = math.max(0, liczba(z[pole], 0))
			end
			for _, pole in { "rodzaj", "umiejetnosc", "efekt" } do
				n[pole] = if type(z[pole]) == "string" then z[pole] else ""
			end
			n.krytyk = z.krytyk == true
			n.t = liczba(z.t, t)
			n.trwa = liczba(z.trwa, 0.5)
			if n.trwa <= 0 then
				n.trwa = 0.5
			end
			t = n.t + n.trwa
			for _, pole in { "hp_gracz", "hp_wrog", "mana_gracz", "mana_wrog" } do
				n[pole] = math.max(0, liczba(z[pole], poprz[pole]))
				poprz[pole] = n[pole]
			end
			table.insert(dziennik, n)
		end
	end
	if #dziennik == 0 then
		return nil, "pusty dziennik"
	end
	local lup = {}
	local zrodloLupu = if type(walka.lup) == "table" then walka.lup else {}
	for pole in P.POLA_LUPU do
		if pole == "kraina" then
			lup.kraina = if type(zrodloLupu.kraina) == "string" then zrodloLupu.kraina else ""
		else
			lup[pole] = math.max(0, liczba(zrodloLupu[pole], 0))
		end
	end
	local przezBlok = liczba(walka.czesc_przez_blok, nil)
	if przezBlok == nil then
		ostrzez("brak pola walki: czesc_przez_blok")
		przezBlok = 0
	end
	local wynik = walka.wynik
	if wynik ~= "wygrana" and wynik ~= "przegrana" then
		ostrzez("zły wynik walki")
		local ost = dziennik[#dziennik]
		wynik = if ost.hp_wrog <= 0 then "wygrana" else "przegrana"
	end
	local ostatni = dziennik[#dziennik]
	local czasFinalu = liczba(walka.czas_finalu, 1.9)
	return {
		wersja = walka.wersja,
		ziarno = liczba(walka.ziarno, 0),
		strony = strony,
		dziennik = dziennik,
		lup = lup,
		wynik = wynik,
		tury = liczba(walka.tury, 0),
		bezpiecznik = walka.bezpiecznik == true,
		czesc_przez_blok = math.max(0, math.min(1, przezBlok)),
		czas_wstepu = liczba(walka.czas_wstepu, 0),
		czas_finalu = czasFinalu,
		czas = liczba(walka.czas, ostatni.t + ostatni.trwa + czasFinalu),
	}, ostrzezenia
end

------------------------------------------------------------------ plan zdarzeń (tury, mana, powalenia)
-- czy zdarzenie to użycie umiejętności przez stronę z = kto (mana spada o koszt w polu wartosc) — jak Dziennik.sprawdz
function P.uzycie(z: any): boolean
	return z.umiejetnosc ~= "" and (z.typ == "umiejetnosc" or z.typ == "unik" or z.typ == "blok")
end

function P.plan(w: any): any
	local d = w.dziennik
	local n = #d
	local zdarzenia = {}
	local tura, stronaTury = 0, nil
	local maks = { gracz = w.strony.gracz.mana_maks, wrog = w.strony.wrog.mana_maks }
	local mana = { gracz = w.strony.gracz.mana, wrog = w.strony.wrog.mana }
	for i = 1, n do
		local z = d[i]
		local e = { nr = i, nowaTura = false }
		if P.AKCJE_TURY[z.typ] and z.kto ~= stronaTury then
			tura += 1
			stronaTury = z.kto
			e.nowaTura = true
		end
		e.tura = tura
		e.stronaTury = stronaTury
		e.uzycie = P.uzycie(z)
		e.koszt = if e.uzycie then z.wartosc else 0
		e.manaPrzed = { gracz = mana.gracz, wrog = mana.wrog }
		e.manaPo = { gracz = z.mana_gracz, wrog = z.mana_wrog }
		mana = { gracz = z.mana_gracz, wrog = z.mana_wrog }
		zdarzenia[i] = e
	end
	-- próg i gotowość paska many: próg = koszt NASTĘPNEGO użycia tej strony z dziennika (albo pełny pasek, gdy
	-- strona już niczego nie użyje); gotowa = mana po zdarzeniu ≥ próg — pasek „dobija” do progu i świeci
	local nastKoszt = {}
	for i = n, 1, -1 do
		local e, z = zdarzenia[i], d[i]
		e.prog = {}
		e.gotowa = {}
		for _, s in STRONY do
			local prog = nastKoszt[s] or maks[s]
			e.prog[s] = prog
			e.gotowa[s] = e.manaPo[s] >= prog
		end
		if e.uzycie then
			nastKoszt[z.kto] = z.wartosc
		end
	end
	local start = { mana = { gracz = w.strony.gracz.mana, wrog = w.strony.wrog.mana }, prog = {}, gotowa = {} }
	for _, s in STRONY do
		start.prog[s] = nastKoszt[s] or maks[s]
		start.gotowa[s] = start.mana[s] >= start.prog[s]
	end
	-- powalenie przed wskrzeszeniem i cios kończący (wskrzeszenie idzie ZARAZ po zdarzeniu, które zbiło życie do zera)
	local pokonany = if w.wynik == "wygrana" then "wrog" else "gracz"
	local nrKonczacego = nil
	local wskrzeszenia = {}
	for i = 1, n do
		local z = d[i]
		if z.typ == "wskrzeszenie" then
			zdarzenia[i].wstaje = z.kto
			wskrzeszenia[z.kto] = i
		else
			for _, s in STRONY do
				if z["hp_" .. s] <= 0 then
					local nast = d[i + 1]
					if nast and nast.typ == "wskrzeszenie" and nast.kto == s then
						zdarzenia[i].powala = s
					elseif s == pokonany and nrKonczacego == nil then
						nrKonczacego = i
					end
				end
			end
		end
	end
	if nrKonczacego then
		zdarzenia[nrKonczacego].smiertelny = true
	end
	-- źródło efektu: efekt_nalozony idzie zaraz po swoim ataku albo umiejętności (kilka nałożeń pod rząd — to samo;
	-- cios, który „zabił”, a cel wstał: atak → wskrzeszenie → efekt_nalozony — wskrzeszenie przeskakujemy)
	for i = 1, n do
		local z = d[i]
		if z.typ == "efekt_nalozony" then
			local j = i - 1
			local zrodlo = ""
			while j >= 1 do
				local p = d[j]
				if p.typ ~= "efekt_nalozony" and p.typ ~= "wskrzeszenie" then
					if p.kto == z.kto then
						zrodlo = p.umiejetnosc
					end
					break
				end
				j -= 1
			end
			zdarzenia[i].zrodlo = zrodlo
		end
	end
	return {
		zdarzenia = zdarzenia,
		tury = tura,
		start = start,
		pokonany = pokonany,
		zwyciezca = if pokonany == "gracz" then "wrog" else "gracz",
		nrKonczacego = nrKonczacego,
		wskrzeszenia = wskrzeszenia,
	}
end

------------------------------------------------------------------ stan efektów (ikony z licznikiem tur i stosami)
function P.nowyStan(): any
	return { gracz = {}, wrog = {} }
end

-- efekt_nalozony: ten sam efekt odświeża się (nowe tury, stosy, siła) w tym samym miejscu listy
function P.nalozony(stan: any, z: any, tura: number, efekty: any)
	local lista = stan[z.cel]
	local def = efekty and efekty[z.efekt]
	local nowy = {
		id = z.efekt,
		tury = z.tury,
		odTury = tura,
		stosy = math.max(1, z.stosy),
		procent = if def and def.typ == "oslona" then z.wartosc else nil,
	}
	for i = 1, #lista do
		if lista[i].id == z.efekt then
			lista[i] = nowy
			return nowy
		end
	end
	table.insert(lista, nowy)
	return nowy
end

-- efekt_tick: liczba stosów z dziennika (trucizna może je mieć do limitu z pasywką)
function P.tykniecie(stan: any, z: any)
	for _, e in stan[z.cel] do
		if e.id == z.efekt and z.stosy >= 1 then
			e.stosy = z.stosy
		end
	end
end

-- efekt_koniec → usunięty wpis (albo nil, gdy odtwarzacz go nie znał)
function P.koniec(stan: any, z: any): any
	local lista = stan[z.cel]
	local nowa = {}
	local usuniety = nil
	for i = 1, #lista do
		if lista[i].id == z.efekt then
			usuniety = lista[i]
		else
			table.insert(nowa, lista[i])
		end
	end
	stan[z.cel] = nowa
	return usuniety
end

-- koniec tury strony: jej efekty tracą jedną turę (oprócz nałożonych w tej turze — jak silnik)
function P.koniecTury(stan: any, strona: string, tura: number)
	for _, e in stan[strona] do
		if e.odTury ~= tura then
			e.tury -= 1
		end
	end
end

-- ikony do interfejsu: { id, tury (≥ 1), stosy, procent }
function P.lista(stan: any, strona: string): any
	local wynik = {}
	for _, e in stan[strona] do
		table.insert(wynik, { id = e.id, tury = math.max(1, e.tury), stosy = e.stosy, procent = e.procent })
	end
	return wynik
end

------------------------------------------------------------------ teksty z danych
-- odmiana: 1 tura, 2–4 tury (12–14 tur), 5+ tur
function P.liczebnik(n: number, jeden: string, kilka: string, wiele: string): string
	local forma
	if n == 1 then
		forma = jeden
	elseif n % 10 >= 2 and n % 10 <= 4 and (n % 100 < 12 or n % 100 > 14) then
		forma = kilka
	else
		forma = wiele
	end
	return tostring(n) .. " " .. forma
end

-- liczba z jedną cyfrą po przecinku tylko wtedy, gdy jest potrzebna („4”, „2,5”)
local function ladnie(x: number): string
	local dz = zaokraglij(math.abs(x) * 10)
	local calosc = math.floor(dz / 10)
	local reszta = dz - calosc * 10
	if reszta == 0 then
		return string.format("%d", calosc)
	end
	return string.format("%d,%d", calosc, reszta)
end

local function znak(x: number): string
	return if x < 0 then "−" else "+"
end

-- jedna premia: etykieta = { tekst, jednostka = "%" | "pp" | "pkt" | "tury" | "stosy" | "x", odwrot? }
local function premia(wartosc: number, etykieta: any): string
	local j = etykieta.jednostka
	if j == "%" then
		return znak(wartosc) .. ladnie(wartosc * 100) .. "% " .. etykieta.tekst
	elseif j == "pp" then
		return znak(wartosc) .. ladnie(wartosc * 100) .. " pp " .. etykieta.tekst
	elseif j == "tury" then
		return znak(wartosc) .. P.liczebnik(zaokraglij(math.abs(wartosc)), "tura", "tury", "tur") .. " " .. etykieta.tekst
	elseif j == "stosy" then
		return znak(wartosc) .. P.liczebnik(zaokraglij(math.abs(wartosc)), "stos", "stosy", "stosów") .. " " .. etykieta.tekst
	elseif j == "x" then
		local setne = zaokraglij(math.abs(wartosc) * 100)
		local calosc = math.floor(setne / 100)
		return znak(wartosc) .. string.format("%d,%02d", calosc, setne - calosc * 100) .. " " .. etykieta.tekst
	end
	return znak(wartosc) .. ladnie(wartosc) .. " " .. etykieta.tekst
end

--[[ Zapowiedź pasywki: zrodlo = "slot" (Dane.pasywne) albo "bron" (Dane.pasywki_broni). → { id, nazwa, linia,
	legendarna, braki } albo nil. Premie w kolejności etykiety.kolejnosc; modyfikator bez etykiety idzie surowo
	(„klucz +0,1”) i trafia do braki (test pilnuje, że braków nie ma). ]]
function P.opisPasywki(Dane: any, id: string, zrodlo: string, etykiety: any): any
	local tabela = if zrodlo == "bron" then Dane.pasywki_broni else Dane.pasywne
	local def = tabela and tabela[id]
	if not def then
		return nil
	end
	local czesci = {}
	local braki = {}
	local wsk = liczba(def.wskrzeszenie, 0)
	if wsk > 0 then
		table.insert(czesci, "raz na walkę: powrót z " .. ladnie(wsk * 100) .. "% życia")
	end
	local mods = def.modyfikatory or {}
	local uzyte = {}
	for _, klucz in etykiety.kolejnosc do
		local v = liczba(mods[klucz], nil)
		if v ~= nil and v ~= 0 then
			uzyte[klucz] = true
			table.insert(czesci, premia(v, etykiety[klucz]))
		end
	end
	for klucz, v in mods do
		if not uzyte[klucz] and liczba(v, 0) ~= 0 then
			table.insert(braki, klucz)
			table.insert(czesci, tostring(klucz) .. " " .. znak(v) .. ladnie(v))
		end
	end
	return {
		id = id,
		nazwa = if type(def.nazwa) == "string" then def.nazwa else id,
		linia = table.concat(czesci, " · "),
		legendarna = def.legendarna == true or wsk > 0,
		zrodlo = zrodlo,
		braki = braki,
	}
end

-- ile procent ciosu zabiera blok (czesc_przez_blok z walki: 0,25 → 75)
function P.blokZatrzymuje(w: any): number
	return zaokraglij((1 - (w.czesc_przez_blok or 0)) * 100)
end

return P
