--[[
	SilnikWalki — czysta funkcja: statystyki obu stron + ziarno → dziennik zdarzeń, wynik i łup.

	Nie dotyka świata gry, nie używa zegara ani Random: ten sam zestaw danych wejściowych daje zawsze
	ten sam dziennik (własny generator liczb, patrz nowyLos). Serwer liczy walkę RAZ i wysyła dziennik,
	a klient tylko go odtwarza (propozycja D-016) — wygląd walki można zmienić bez ruszania balansu.

	Zdarzenie dziennika: { t, kto, akcja, obrazenia, hp_po }
		t         — sekunda cutscenki, w której cios dochodzi celu
		kto       — "gracz" albo "wrog": strona, która ATAKUJE
		akcja     — wynik ataku: "cios" (zwykłe trafienie), "krytyk" (cios krytyczny),
		            "blok" (broniący przyjął cios na tarczę / gardę), "unik" (broniący zszedł z linii ciosu)
		obrazenia — ile życia stracił broniący (0 przy uniku)
		hp_po     — życie broniącego po tej wymianie

	Zasady prototypu (umowny balans — chodzi o sprawdzenie architektury, nie liczb):
		• strony biją na zmianę; zaczyna ta, która wygra rzut ważony szybkością;
		• od 4. wymiany obie strony biją coraz mocniej (walka nie może się ciągnąć);
		• „ostatni dech”: przed 4. wymianą nikt nie pada — zostaje mu 1 punkt życia;
		• w 6. wymianie inicjatywę przejmuje strona z większą częścią życia i zadaje cios rozstrzygający.
	Dzięki temu walka ma zawsze 4–6 wymian, a cała cutscenka 8–10 s.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local SilnikWalki = {}

SilnikWalki.MIN_WYMIAN = 4
SilnikWalki.MAKS_WYMIAN = 6
SilnikWalki.MIN_CZAS = 8.0 -- s: najkrótsza cutscenka (od startu do panelu wyniku)
SilnikWalki.MAKS_CZAS = 10.0 -- s: najdłuższa

local CZAS_WSTEPU = 1.1 -- s: plan ogólny i napis „WALKA!” przed pierwszą wymianą
local CZAS_FINALU = 1.9 -- s: od końca ostatniej wymiany do panelu wyniku (upadek, wiwat, łup, objazd kamery)
-- ile sekund zajmuje wymiana przed trafieniem (zamach, doskok) i po nim (odrzut, powrót na miejsce)
local PRZED = { cios = 0.58, blok = 0.58, unik = 0.58, krytyk = 0.85 }
local PO = { cios = 0.56, blok = 0.56, unik = 0.50, krytyk = 0.90 }

local CZESC_PRZEZ_BLOK = 0.18 -- jaka część obrażeń przechodzi przez blok
local ESKALACJA = 0.45 -- o tyle rosną obrażenia z każdą wymianą po trzeciej
local WYMAGANE = { "hp", "atak", "obrona", "szybkosc", "krytyk", "mnoznikKrytyka", "blok", "unik" }

-- Generator liczb pseudolosowych (Park–Miller, minstd): w całości na liczbach całkowitych < 2^53,
-- więc daje identyczne wyniki na każdej platformie — i w Luau, i w kontrolnym porcie w Pythonie.
local MODUL = 2147483647
local function nowyLos(ziarno: number): () -> number
	local stan = math.floor(math.abs(ziarno)) % MODUL
	if stan == 0 then
		stan = 20261113
	end
	local function los(): number
		stan = (stan * 48271) % MODUL
		return (stan - 1) / (MODUL - 1) -- liczba z przedziału [0, 1)
	end
	for _ = 1, 8 do
		los() -- rozgrzewka: sąsiednie ziarna dają na początku podobne liczby
	end
	return los
end

local function zaokraglij(x: number): number
	return math.floor(x + 0.5)
end

local function sprawdzStrone(nazwa: string, s: any)
	if type(s) ~= "table" then
		error("SilnikWalki: brak statystyk strony „" .. nazwa .. "”", 3)
	end
	for _, pole in WYMAGANE do
		local v = s[pole]
		if type(v) ~= "number" or v ~= v or v < 0 then
			error("SilnikWalki: zła wartość „" .. pole .. "” strony „" .. nazwa .. "”", 3)
		end
	end
	if s.hp < 1 or s.atak <= 0 or s.szybkosc <= 0 then
		error("SilnikWalki: hp, atak i szybkosc strony „" .. nazwa .. "” muszą być dodatnie", 3)
	end
end

--[[
	symuluj(gracz, wrog, ziarno) → {
		wersja, ziarno,
		strony = { gracz = { nazwa, poziom, hp }, wrog = { nazwa, poziom, hp } },
		dziennik = { { t, kto, akcja, obrazenia, hp_po }, ... },
		wynik = "wygrana" | "przegrana",      -- z punktu widzenia gracza
		lup = { zloto, doswiadczenie, jajko },
		czas,                                  -- s: długość cutscenki do panelu wyniku
	}
	Statystyki strony: nazwa, poziom, hp, atak, obrona, szybkosc, krytyk (0–1), mnoznikKrytyka, blok (0–1), unik (0–1).
]]
function SilnikWalki.symuluj(gracz, wrog, ziarno: number)
	sprawdzStrone("gracz", gracz)
	sprawdzStrone("wrog", wrog)
	if type(ziarno) ~= "number" or ziarno ~= ziarno then
		error("SilnikWalki: ziarno musi być liczbą", 2)
	end

	local los = nowyLos(ziarno)
	local strony = { gracz = gracz, wrog = wrog }
	local hp = { gracz = math.floor(gracz.hp), wrog = math.floor(wrog.hp) }
	local dziennik = {}

	local kolej = if los() < gracz.szybkosc / (gracz.szybkosc + wrog.szybkosc) then "gracz" else "wrog"
	local zwyciezca = nil

	for nr = 1, SilnikWalki.MAKS_WYMIAN do
		local ostatnia = nr == SilnikWalki.MAKS_WYMIAN
		if ostatnia then
			-- inicjatywę przejmuje strona, której zostało procentowo więcej życia (remis → gracz)
			kolej = if hp.gracz / gracz.hp >= hp.wrog / wrog.hp then "gracz" else "wrog"
		end
		local atakujacy = kolej
		local broniacy = if kolej == "gracz" then "wrog" else "gracz"
		local A, D = strony[atakujacy], strony[broniacy]

		-- zawsze dwa rzuty na wymianę, w tej samej kolejności (ważne dla powtarzalności)
		local rozrzut = 0.85 + 0.30 * los()
		local rzut = los()
		local mnoznik = 1 + ESKALACJA * math.max(0, nr - 3)
		local baza = A.atak * rozrzut * (100 / (100 + D.obrona)) * mnoznik

		local akcja, obrazenia
		if ostatnia then
			akcja = "krytyk" -- cios rozstrzygający
			obrazenia = math.max(zaokraglij(baza * A.mnoznikKrytyka), hp[broniacy])
		elseif rzut < D.unik then
			akcja, obrazenia = "unik", 0
		elseif rzut < D.unik + A.krytyk then
			akcja, obrazenia = "krytyk", math.max(1, zaokraglij(baza * A.mnoznikKrytyka))
		elseif rzut < D.unik + A.krytyk + D.blok then
			akcja, obrazenia = "blok", math.max(1, zaokraglij(baza * CZESC_PRZEZ_BLOK))
		else
			akcja, obrazenia = "cios", math.max(1, zaokraglij(baza))
		end

		if nr < SilnikWalki.MIN_WYMIAN and obrazenia >= hp[broniacy] then
			obrazenia = hp[broniacy] - 1 -- „ostatni dech”
		end

		hp[broniacy] = math.max(0, hp[broniacy] - obrazenia)
		table.insert(dziennik, { t = 0, kto = atakujacy, akcja = akcja, obrazenia = obrazenia, hp_po = hp[broniacy] })

		if hp[broniacy] <= 0 then
			zwyciezca = atakujacy
			break
		end
		kolej = broniacy
	end

	-- Oś czasu: wstęp + wymiany + finał, ściśnięte albo rozciągnięte tak, by całość trwała 8–10 s.
	local sumaWymian = 0
	for _, z in dziennik do
		sumaWymian += PRZED[z.akcja] + PO[z.akcja]
	end
	local czas = math.clamp(CZAS_WSTEPU + sumaWymian + CZAS_FINALU, SilnikWalki.MIN_CZAS, SilnikWalki.MAKS_CZAS)
	local skala = (czas - CZAS_WSTEPU - CZAS_FINALU) / sumaWymian
	local t = CZAS_WSTEPU
	for _, z in dziennik do
		t += PRZED[z.akcja] * skala
		z.t = zaokraglij(t * 100) / 100
		t += PO[z.akcja] * skala
	end

	-- Łup (umowny): za wygraną złoto, doświadczenie i czasem jajko; za przegraną odrobina doświadczenia.
	local wygrana = zwyciezca == "gracz"
	local poziomWroga = math.max(1, math.floor(wrog.poziom or 1))
	local rzutZlota, rzutDosw, rzutJajka = los(), los(), los()
	local lup
	if wygrana then
		lup = {
			zloto = zaokraglij(poziomWroga * 45 * (0.9 + 0.6 * rzutZlota)),
			doswiadczenie = zaokraglij(poziomWroga * 18 * (1 + 0.5 * rzutDosw)),
			jajko = if rzutJajka < 0.4 then 1 else 0,
		}
	else
		lup = { zloto = 0, doswiadczenie = zaokraglij(poziomWroga * 4 * (1 + 0.5 * rzutDosw)), jajko = 0 }
	end

	return {
		wersja = 1,
		ziarno = ziarno,
		strony = {
			gracz = { nazwa = tostring(gracz.nazwa or "Gracz"), poziom = gracz.poziom or 1, hp = math.floor(gracz.hp) },
			wrog = { nazwa = tostring(wrog.nazwa or "Wróg"), poziom = wrog.poziom or 1, hp = math.floor(wrog.hp) },
		},
		dziennik = dziennik,
		wynik = if wygrana then "wygrana" else "przegrana",
		lup = lup,
		czas = zaokraglij(czas * 100) / 100,
	}
end

--[[
	sprawdz(walka) → true albo (false, opis błędu). Niezmienniki dziennika — używane w testach
	i przez klienta, zanim zacznie cokolwiek odtwarzać.
]]
function SilnikWalki.sprawdz(walka): (boolean, string?)
	if type(walka) ~= "table" or type(walka.dziennik) ~= "table" or type(walka.strony) ~= "table" then
		return false, "brak dziennika albo stron"
	end
	local n = #walka.dziennik
	if n < SilnikWalki.MIN_WYMIAN or n > SilnikWalki.MAKS_WYMIAN then
		return false, "liczba wymian poza zakresem: " .. n
	end
	if type(walka.czas) ~= "number" or walka.czas < SilnikWalki.MIN_CZAS or walka.czas > SilnikWalki.MAKS_CZAS then
		return false, "czas poza zakresem"
	end
	local hp = { gracz = walka.strony.gracz.hp, wrog = walka.strony.wrog.hp }
	local poprzedniT = 0
	for i, z in walka.dziennik do
		if z.kto ~= "gracz" and z.kto ~= "wrog" then
			return false, "zdarzenie " .. i .. ": nieznana strona"
		end
		if z.akcja ~= "cios" and z.akcja ~= "blok" and z.akcja ~= "krytyk" and z.akcja ~= "unik" then
			return false, "zdarzenie " .. i .. ": nieznana akcja"
		end
		if type(z.t) ~= "number" or z.t <= poprzedniT or z.t >= walka.czas then
			return false, "zdarzenie " .. i .. ": zły czas"
		end
		poprzedniT = z.t
		local cel = if z.kto == "gracz" then "wrog" else "gracz"
		if type(z.obrazenia) ~= "number" or z.obrazenia < 0 or (z.akcja == "unik" and z.obrazenia ~= 0) then
			return false, "zdarzenie " .. i .. ": złe obrażenia"
		end
		local oczekiwane = math.max(0, hp[cel] - z.obrazenia)
		if z.hp_po ~= oczekiwane then
			return false, "zdarzenie " .. i .. ": hp_po = " .. tostring(z.hp_po) .. ", oczekiwano " .. oczekiwane
		end
		hp[cel] = oczekiwane
		if oczekiwane == 0 and i ~= n then
			return false, "zdarzenie " .. i .. ": walka trwa po nokaucie"
		end
	end
	local ostatnie = walka.dziennik[n]
	if ostatnie.hp_po ~= 0 then
		return false, "ostatnia wymiana nie kończy walki"
	end
	local oczekiwanyWynik = if ostatnie.kto == "gracz" then "wygrana" else "przegrana"
	if walka.wynik ~= oczekiwanyWynik then
		return false, "wynik niezgodny z dziennikiem"
	end
	if type(walka.lup) ~= "table" then
		return false, "brak łupu"
	end
	return true
end

return SilnikWalki
