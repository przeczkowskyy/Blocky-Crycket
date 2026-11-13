--[[
	Magazyn telemetrii — zapis kubełków godzinowych do Data Store i wpisu „na żywo” serwera do Memory Store.

	- Kubełki: klucz "g_RRRRMMDD_GG" (UTC), zapis przez UpdateAsync (czyta aktualną wartość i dopisuje przyrost,
	  więc wiele serwerów może pisać do tej samej godziny). Nieudany zapis ponawiamy z rosnącą przerwą; gdy i to
	  zawiedzie, przyrost wraca do agregatora i pójdzie przy następnym zapisie.
	- Budżet: przed zapisem pytamy, czy serwer ma jeszcze wolne żądania (GetRequestBudgetForRequestType); gdy nie,
	  czekamy do następnej tury. Przy zamykaniu serwera zapisujemy mimo wszystko.
	- Serwer na żywo: wpis w sorted mapie Memory Store pod kluczem JobId, odnawiany co minutę, wygasa sam po
	  `wygasanie_s` sekundach — po awarii serwera wpis znika bez sprzątania.
	- Magazyn i mapa są WSTRZYKIWANE (opcje.magazyn, opcje.mapa): prawdziwe usługi Roblox albo atrapy w pamięci
	  (Magazyn.w_pamieci(), Magazyn.mapa_w_pamieci()) — w Studio i w testach nic nie trafia do prawdziwych danych.

	Limity z dokumentacji Roblox (stan na 13.11.2026, adresy w notatce „Telemetria gry” w sejfie):
	- serwer: 60 + 40 × liczba graczy zapisów i tyle samo odczytów na minutę; UpdateAsync zużywa jedno i drugie;
	- cała gra: 300 + 40 × gracze odczytów i 300 + 20 × gracze zapisów na minutę, WSPÓLNIE z Open Cloud (panel)
	  i z zapisami profili graczy — telemetria to kilka UpdateAsync na serwer co 5 minut;
	- jeden klucz: do 4 MB zapisu na minutę ze wszystkich serwerów razem, wartość do 4 194 304 znaków;
	- Memory Store: wartość do 32 KB, klucz do 128 znaków, wygasanie najwyżej 45 dni.
]]

local Agregator = require(script.Parent.Agregator)

local Magazyn = {}
Magazyn.__index = Magazyn

Magazyn.KLUCZ_STANU = "stan"

-- --------------------------------------------------------------------------- atrapy do Studio i testów
-- Data Store w pamięci: ma UpdateAsync i GetAsync jak prawdziwy.
function Magazyn.w_pamieci()
	local atrapa = { dane = {}, zapisy = 0 }

	function atrapa:UpdateAsync(klucz, przeksztalc)
		local nowa = przeksztalc(self.dane[klucz])
		if nowa ~= nil then
			self.dane[klucz] = nowa
			self.zapisy += 1
		end
		return nowa
	end

	function atrapa:GetAsync(klucz)
		return self.dane[klucz]
	end

	return atrapa
end

-- Sorted mapa Memory Store w pamięci: ma SetAsync i RemoveAsync jak prawdziwa.
function Magazyn.mapa_w_pamieci()
	local atrapa = { dane = {} }

	function atrapa:SetAsync(klucz, wartosc, wygasa_s, klucz_sortowania)
		local bylo = self.dane[klucz] ~= nil
		self.dane[klucz] = { wartosc = wartosc, wygasa_s = wygasa_s, klucz_sortowania = klucz_sortowania }
		return bylo
	end

	function atrapa:RemoveAsync(klucz)
		self.dane[klucz] = nil
	end

	return atrapa
end

-- --------------------------------------------------------------------------- magazyn
--[[
	opcje:
		agregator   (wymagany) obiekt z Agregator.nowy()
		magazyn     (wymagany) Data Store albo atrapa: UpdateAsync(klucz, funkcja)
		mapa        sorted mapa Memory Store albo atrapa: SetAsync(klucz, wartość, wygasanie, kluczSortowania),
		            RemoveAsync(klucz); nil = bez wpisu „na żywo”
		budzet      funkcja → ile zapisów serwer może teraz zrobić (nil = nie wiadomo, zapisujemy)
		zegar       funkcja → sekundy Unix (domyślnie os.time)
		czekaj      funkcja(sekundy) (domyślnie task.wait)
		log         funkcja(tekst) (domyślnie warn)
		id_serwera  klucz wpisu „na żywo” (game.JobId)
		proby       ile razy próbować zapisu jednego kubełka (domyślnie 3)
		wygasanie_s po ilu sekundach bez odnowienia znika wpis „na żywo” (domyślnie 180)
]]
function Magazyn.nowy(opcje)
	if type(opcje) ~= "table" or opcje.agregator == nil or opcje.magazyn == nil then
		error("Magazyn.nowy: podaj opcje.agregator i opcje.magazyn")
	end
	local self = setmetatable({}, Magazyn)
	self.agregator = opcje.agregator
	self.magazyn = opcje.magazyn
	self.mapa = opcje.mapa
	self.budzet = opcje.budzet or function()
		return nil
	end
	self.zegar = opcje.zegar or os.time
	self.czekaj = opcje.czekaj or task.wait
	self.log = opcje.log or warn
	self.id_serwera = opcje.id_serwera or "serwer"
	self.proby = opcje.proby or 3
	self.wygasanie_s = opcje.wygasanie_s or 180
	self.start = self.zegar()
	self.ostatni_zapis = 0 -- kiedy ostatnio próbowano zapisu
	self.ostatni_udany_zapis = 0
	self.zapisane_kubelki = 0
	self.nieudane_zapisy = 0
	self.ostatni_blad = nil
	self._trwa = false
	return self
end

-- Jeden kubełek: UpdateAsync z ponawianiem (przerwy 1 s, 2 s, 4 s…). Zwraca true po udanym zapisie.
function Magazyn:_zapisz_kubelek(klucz, przyrost, proby)
	for proba = 1, proby do
		local ok, blad = pcall(function()
			self.magazyn:UpdateAsync(klucz, function(stary)
				return Agregator.scal(stary, przyrost) -- funkcja nie może czekać (yield) — scal tylko liczy
			end)
		end)
		if ok then
			return true
		end
		self.ostatni_blad = tostring(blad)
		self.log(string.format("[Telemetria] zapis %s nieudany (próba %d z %d): %s", klucz, proba, proby, tostring(blad)))
		if proba < proby then
			self.czekaj(2 ^ (proba - 1))
		end
	end
	return false
end

-- Zapisuje wszystkie oczekujące kubełki. tryb "zamkniecie" = serwer się wyłącza: bez pytania o budżet i krócej.
-- Zwraca: czy wszystko zapisano, ile kubełków zapisano, ile wróciło do kolejki.
function Magazyn:zapisz(tryb)
	if self._trwa then
		return false, 0, 0
	end
	self._trwa = true
	local zapisane, nieudane = 0, 0
	local ok, blad = pcall(function()
		local zamykanie = tryb == "zamkniecie"
		local proby = self.proby
		if zamykanie then
			proby = math.min(proby, 2)
		end
		for _, partia in ipairs(self.agregator:zdejmij()) do
			local wolno = true
			if not zamykanie then
				local budzet = self.budzet()
				if budzet ~= nil and budzet < 1 then
					wolno = false -- budżet żądań wyczerpany: nie dokładamy, spróbujemy w następnej turze
				end
			end
			if wolno and self:_zapisz_kubelek(partia.klucz, partia.kubelek, proby) then
				zapisane += 1
			else
				nieudane += 1
				self.agregator:oddaj(partia.klucz, partia.kubelek)
			end
		end
	end)
	self._trwa = false
	self.ostatni_zapis = self.zegar()
	if not ok then
		self.ostatni_blad = tostring(blad)
		self.log("[Telemetria] błąd podczas zapisu: " .. tostring(blad))
		return false, zapisane, nieudane
	end
	self.zapisane_kubelki += zapisane
	self.nieudane_zapisy += nieudane
	if zapisane > 0 then
		self.ostatni_udany_zapis = self.ostatni_zapis
	end
	return nieudane == 0, zapisane, nieudane
end

-- Wpis "stan": ślad, że moduł działa (panel odróżnia dzięki niemu „wyłączony” od „nikt nie grał”).
function Magazyn:zapisz_stan()
	local teraz = self.zegar()
	local ok, blad = pcall(function()
		self.magazyn:UpdateAsync(Magazyn.KLUCZ_STANU, function(stary)
			return Agregator.scal_stan(stary, teraz)
		end)
	end)
	if not ok then
		self.ostatni_blad = tostring(blad)
		self.log("[Telemetria] nie udało się zapisać wpisu stanu: " .. tostring(blad))
	end
	return ok
end

-- Odnawia wpis „na żywo” tego serwera. stan: { gracze, pamiec_mb, fps, bledy, miejsce, wersja_miejsca }.
function Magazyn:puls(stan)
	if self.mapa == nil then
		return false
	end
	local gracze = 0
	if type(stan.gracze) == "number" then
		gracze = stan.gracze
	end
	local wartosc = {
		gracze = gracze,
		od = self.start,
		t = self.zegar(),
		pamiec_mb = stan.pamiec_mb,
		fps = stan.fps,
		bledy = stan.bledy,
		miejsce = stan.miejsce,
		wersja_miejsca = stan.wersja_miejsca,
	}
	local ok, blad = pcall(function()
		self.mapa:SetAsync(self.id_serwera, wartosc, self.wygasanie_s, gracze)
	end)
	if not ok then
		self.ostatni_blad = tostring(blad)
	end
	return ok
end

-- Zamknięcie serwera: czeka na zapis w toku (najwyżej kilka sekund), zapisuje resztę i usuwa wpis „na żywo”.
function Magazyn:zamknij()
	local koniec = self.zegar() + 8
	while self._trwa and self.zegar() < koniec do
		self.czekaj(0.2)
	end
	self._trwa = false
	local ok = self:zapisz("zamkniecie")
	if self.mapa ~= nil then
		pcall(function()
			self.mapa:RemoveAsync(self.id_serwera)
		end)
	end
	return ok
end

return Magazyn
