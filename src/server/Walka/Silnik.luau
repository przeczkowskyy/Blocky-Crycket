--[[
	Silnik — walka v3: opis gracza + przeciwnik + ziarno → dziennik zdarzeń, wynik i łup. Czysta funkcja.

	Nie dotyka świata gry, nie używa zegara ani Random: te same dane dają zawsze ten sam dziennik (własny generator,
	stała kolejność rzutów, te same zaokrąglenia). Serwer liczy walkę RAZ i wysyła dziennik, klient go tylko odtwarza
	(D-016); klient nie przysyła żadnych liczb. Sam moduł niczego nie uruchamia — działa dopiero wywołany.
	Port w Pythonie: tools/walka/silnik.py (sekcja Silnik.luau). Niezmienniki dziennika: ReplicatedStorage.Shared.Walka.Dziennik.
	Zasady v3 (mana, statusy, tarcza procentowa, blok każdej klasy, limit Pancerza, pasywki): tools/walka/ZMIANY_SESJA_1611.md.

	DŁUGOŚĆ WALKI WYNIKA WYŁĄCZNIE ZE STATYSTYK I LOSOWOŚCI: strony działają na zmianę, aż życie jednej spadnie do
	zera. Nie ma minimalnej ani docelowej liczby tur, „ostatniego dechu”, ciosu rozstrzygającego, narastających
	obrażeń, ściskania czasu ani osobnych zasad dla bossów. Czas całości = wstęp + suma naturalnych czasów zdarzeń
	+ finał. Jedyny bezpiecznik to techniczny limit tur (Dane.stale.maks_tur), w praktyce nieosiągalny.

	Tura strony: (1) tyknięcia jej efektów; (2) jeśli jest ogłuszona — traci turę; inaczej akcja (umiejętność z many
	albo zwykły cios, Umiejetnosci.akcja); (3) koniec tury — jej efekty tracą 1. Pierwszy ruch: rzut 50/50.
	Przed pierwszą turą: pasywki „na starcie” działające na przeciwnika (zdarcie części jego Pancerza na całą walkę).

	Silnik.symuluj(gracz, przeciwnik, ziarno) → {
		wersja = 3, ziarno,
		strony = { gracz = { nazwa, rodzaj, id, ranga, poziom, zycie, mana, mana_maks }, wrog = { ... } },
		dziennik = { zdarzenie, ... },     -- format: ReplicatedStorage.Shared.Walka.Dziennik
		wynik = "wygrana" | "przegrana",   -- z punktu widzenia gracza
		tury, bezpiecznik,                 -- liczba tur obu stron razem; true tylko po limicie tur
		lup = { zloto, doswiadczenie, tokeny_krainy, gemy, shard_ewolucji, kraina },
		czesc_przez_blok,                  -- ile ciosu przechodzi przez blok (0 = blok zatrzymuje cały cios)
		czas_wstepu, czas_finalu, czas,    -- sekundy
	}
	gracz: opis postaci (Statystyki); przeciwnik: { potwor = id, poziom = n } albo { postac = opis postaci }.
	Złe dane: błąd z czytelnym opisem („Walka: …”).
]]

local Dane = require(script.Parent.Dane)
local Los = require(script.Parent.Los)
local Statystyki = require(script.Parent.Statystyki)
local Przeciwnicy = require(script.Parent.Przeciwnicy)
local Umiejetnosci = require(script.Parent.Umiejetnosci)

local Silnik = {}

Silnik.WERSJA = 3
local STALE = Dane.stale

local function nowyStan(walczacy)
	return { hp = walczacy.zycie, efekty = {}, mana = walczacy.mana_start, nastepna = 1, wskrzeszenie = walczacy.wskrzeszenie }
end

local function opisStrony(walczacy)
	return {
		nazwa = walczacy.nazwa,
		rodzaj = walczacy.rodzaj,
		id = walczacy.id,
		ranga = walczacy.ranga,
		poziom = walczacy.poziom,
		zycie = walczacy.zycie,
		mana = walczacy.mana_start,
		mana_maks = STALE.mana_maks,
	}
end

function Silnik.symuluj(gracz: any, przeciwnik: any, ziarno: any)
	Statystyki.sprawdzPostac(gracz, "gracz")
	local A = Statystyki.wartosciPostaci(gracz)
	local B = Przeciwnicy.wartosciPrzeciwnika(przeciwnik)
	-- tylko całkowite ziarno w [0, 2^31): powyżej 2^53 Luau (liczby double) i port w Pythonie (dokładne liczby
	-- całkowite) liczą resztę z dzielenia inaczej i dałyby różne walki — takie ziarno odrzucamy czytelnym błędem
	if not Los.calkowita(ziarno) or ziarno < 0 or ziarno >= Los.ZIARNO_GRANICA then
		Los.blad("ziarno musi być liczbą całkowitą od 0 do " .. string.format("%d", Los.ZIARNO_GRANICA - 1))
	end
	-- pasywki „na starcie walki” działające na przeciwnika: zdarcie części jego Pancerza na całą walkę
	local pa, pb = A.pancerz, B.pancerz
	A.pancerz = pa * (1 + B.mod.pancerz_wroga)
	B.pancerz = pb * (1 + A.mod.pancerz_wroga)
	local los = Los.nowyLos(ziarno)
	local w = {
		strony = { gracz = A, wrog = B },
		stan = { gracz = nowyStan(A), wrog = nowyStan(B) },
		dziennik = {},
		czas = STALE.czas_wstepu,
		tura = 0,
		los = los,
	}
	local kolej = if los() < STALE.szansa_pierwszego_ruchu then "gracz" else "wrog"
	local zwyciezca = ""
	local bezpiecznik = false
	while zwyciezca == "" do
		if w.tura >= STALE.maks_tur then
			-- TECHNICZNY bezpiecznik przeciw pętli bez końca — w praktyce nieosiągalny (test na wielu ziarnach);
			-- rozstrzyga większy procent pozostałego życia (mnożenie na krzyż, bez dzielenia), remis → gracz
			bezpiecznik = true
			if w.stan.gracz.hp * B.zycie >= w.stan.wrog.hp * A.zycie then
				zwyciezca = "gracz"
			else
				zwyciezca = "wrog"
			end
			break
		end
		w.tura = w.tura + 1
		local kto = kolej
		local cel = Umiejetnosci.inna(kto)
		Umiejetnosci.tykniecia(w, kto)
		if w.stan[kto].hp <= 0 then
			zwyciezca = cel
			break
		end
		if Umiejetnosci.maEfekt(w.stan[kto], "ogluszenie") then
			Umiejetnosci.zdarzenie(w, "utrata_tury", kto, kto, STALE.czasy.utrata_tury, {})
		else
			Umiejetnosci.akcja(w, kto, cel)
			if w.stan[cel].hp <= 0 then
				zwyciezca = kto
				break
			end
		end
		Umiejetnosci.koniecTury(w, kto)
		kolej = cel
	end
	local wygrana = zwyciezca == "gracz"
	local lup = Przeciwnicy.losujLup(B, wygrana, los)
	local czas = w.czas + STALE.czas_finalu
	return {
		wersja = Silnik.WERSJA,
		ziarno = ziarno,
		strony = { gracz = opisStrony(A), wrog = opisStrony(B) },
		dziennik = w.dziennik,
		wynik = if wygrana then "wygrana" else "przegrana",
		tury = w.tura,
		bezpiecznik = bezpiecznik,
		lup = lup,
		czesc_przez_blok = STALE.czesc_przez_blok,
		czas_wstepu = STALE.czas_wstepu / 100,
		czas_finalu = STALE.czas_finalu / 100,
		czas = czas / 100,
	}
end

-- lista przeciwników lasu dla interfejsu i paczki modeli (kolejność z danych)
function Silnik.przeciwnicy()
	local lista = {}
	for _, d in Dane.przeciwnicy do
		table.insert(lista, { id = d.id, nazwa = d.nazwa, ranga = d.ranga, kraina = d.kraina, klasa = d.klasa, wyglad = d.wyglad })
	end
	return lista
end

return Silnik
