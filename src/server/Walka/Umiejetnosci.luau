--[[
	Umiejetnosci — tura walki: zwykły cios, umiejętności w slotach i efekty (silnik walki v2). Czysty moduł.
	Port w Pythonie: tools/walka/silnik.py, sekcja Umiejetnosci.luau (te same nazwy funkcji, ta sama kolejność rzutów).

	Stan walki `w` (tworzy go Silnik.symuluj):
		w.strony = { gracz = wartości bojowe, wrog = wartości bojowe }
		w.stan   = { gracz = { hp, efekty = { ... }, liczniki = { ... } }, wrog = ... }
		w.dziennik, w.czas (setne sekundy), w.tura (numer tury w całej walce), w.los (generator)

	Zasady:
	• Zwykły cios: zawsze pięć rzutów (rozrzut, unik, blok, krytyk, zaklęcie). Kolejność rozstrzygania: unik → blok →
	  krytyk → zwykłe trafienie. Unik zeruje cios, blok (tylko tarcza) przepuszcza czesc_przez_blok obrażeń,
	  krytyk mnoży surowe obrażenia przez mnożnik krytyka klasy.
	• Obrona: Pancerz (ciosy fizyczne) i odporność na magię z Inteligencji (ciosy magiczne) to PUNKTY odejmowane od
	  ciosu; dolna granica — zawsze przechodzi co najmniej min_czesc_po_obronie surowych obrażeń i nie mniej niż 1.
	• Umiejętność (PROPOZYCJA mechanizmu dla walki automatycznej): każda umiejętność w slocie ma odnowienie N
	  własnych akcji. Na swojej turze postać odlicza wszystkie sloty o 1 i używa PIERWSZEJ gotowej (licznik ≤ 0)
	  w kolejności slotów ZAMIAST zwykłego ciosu; użyta wraca do N. Pierwszy raz odpala się w N-tej akcji.
	  Umiejętność na przeciwnika to atak jak zwykły cios: można jej uniknąć (zdarzenie "unik" z identyfikatorem
	  umiejętności) i przyjąć ją na tarczę ("blok"; wtedy bez krytyka i bez efektów); może być krytykiem.
	  Siła = cios × mnożnik umiejętności × moc (Inteligencja). Umiejętność „na siebie” (tarcza, wzmocnienie) zawsze działa.
	• Efekty trwają N tur NOSICIELA: na końcu każdej jego tury tracą 1 (oprócz tury, w której nosiciel sam je
	  nałożył). Obrażenia w czasie tykają na początku tury nosiciela i omijają Pancerz i odporność; tarcza pochłania
	  wszystkie obrażenia (także tyknięcia), aż się wyczerpie; spowolnienie zabiera najbliższą turę; zdarcie
	  zmniejsza Pancerz o ułamek; wzmocnienie zwiększa obrażenia. Ten sam efekt nie kumuluje się — odświeża się.
]]

local Dane = require(script.Parent.Dane)
local Los = require(script.Parent.Los)

local Umiejetnosci = {}

local STALE = Dane.stale
local CZASY = Dane.stale.czasy

local function inna(strona: string): string
	return if strona == "gracz" then "wrog" else "gracz"
end
Umiejetnosci.inna = inna

local function wzmocnienie(stanStrony): number
	local m = 1
	for _, ef in stanStrony.efekty do
		if ef.typ == "wzmocnienie" then
			m = m + ef.wartosc
		end
	end
	return m
end

local function pancerzEfektywny(walczacy, stanStrony): number
	local p = walczacy.pancerz
	for _, ef in stanStrony.efekty do
		if ef.typ == "zdarcie" then
			p = p * (1 - ef.wartosc)
		end
	end
	return p
end

function Umiejetnosci.maEfekt(stanStrony, typ: string): boolean
	for _, ef in stanStrony.efekty do
		if ef.typ == typ then
			return true
		end
	end
	return false
end

local function poObronie(w, surowe: number, rodzaj: string, cel: string): number
	local obrona
	if rodzaj == "fizyczne" then
		obrona = pancerzEfektywny(w.strony[cel], w.stan[cel])
	else
		obrona = w.strony[cel].odpornosc
	end
	return math.max(surowe * STALE.min_czesc_po_obronie, surowe - obrona)
end

-- najpierw tarcze pochłaniające (w kolejności nałożenia), reszta schodzi z życia; zwraca (obrażenia życia, pochłonięte)
local function przyjmij(w, cel: string, obrazenia: number): (number, number)
	local s = w.stan[cel]
	local reszta = obrazenia
	local pochloniete = 0
	for _, ef in s.efekty do
		if ef.typ == "tarcza" and reszta > 0 and ef.zostalo > 0 then
			local ile = math.min(ef.zostalo, reszta)
			ef.zostalo = ef.zostalo - ile
			reszta = reszta - ile
			pochloniete = pochloniete + ile
		end
	end
	s.hp = math.max(0, s.hp - reszta)
	return reszta, pochloniete
end

local POLA_ZDARZENIA = { "obrazenia", "pochloniete", "rodzaj", "umiejetnosc", "efekt", "krytyk", "wartosc", "tury" }

-- dopisuje zdarzenie do dziennika; t = początek zdarzenia, trwa = jego naturalny czas (z danych)
function Umiejetnosci.zdarzenie(w, typ: string, kto: string, cel: string, trwa: number, pola)
	local z = {
		typ = typ,
		kto = kto,
		cel = cel,
		obrazenia = 0,
		pochloniete = 0,
		rodzaj = "",
		umiejetnosc = "",
		efekt = "",
		krytyk = false,
		wartosc = 0,
		tury = 0,
		t = w.czas / 100,
		trwa = trwa / 100,
	}
	for _, k in POLA_ZDARZENIA do
		if pola[k] ~= nil then
			z[k] = pola[k]
		end
	end
	z.hp_gracz = w.stan.gracz.hp
	z.hp_wrog = w.stan.wrog.hp
	w.czas = w.czas + trwa
	table.insert(w.dziennik, z)
	return z
end
local zdarzenie = Umiejetnosci.zdarzenie

local function usunZuzyteTarcze(w, cel: string)
	local s = w.stan[cel]
	if s.hp <= 0 then
		return -- walka i tak się kończy; po nokaucie nie ma już zdarzeń
	end
	local zostaja = {}
	for _, ef in s.efekty do
		if ef.typ == "tarcza" and ef.zostalo <= 0 then
			zdarzenie(w, "efekt_koniec", cel, cel, CZASY.efekt_koniec, { efekt = ef.id })
		else
			table.insert(zostaja, ef)
		end
	end
	s.efekty = zostaja
end

local function nalozEfekt(w, zrodlo: string, cel: string, idEfektu: string, moc: number)
	local E = Dane.efekty[idEfektu]
	local A = w.strony[zrodlo]
	local nowy = {
		id = idEfektu,
		typ = E.typ,
		trwa = E.trwa,
		od_tury = w.tura,
		wartosc = E.wartosc or 0,
		tick = 0,
		zostalo = 0,
		rodzaj = E.rodzaj,
	}
	local pokaz = 0
	if E.typ == "obrazenia_w_czasie" then
		nowy.tick = math.max(1, Los.zaokraglij(A.cios * E.udzial * moc))
		pokaz = nowy.tick
	elseif E.typ == "tarcza" then
		nowy.zostalo = math.max(1, Los.zaokraglij(A.cios * E.udzial * moc))
		pokaz = nowy.zostalo
	else
		pokaz = Los.zaokraglij(nowy.wartosc * 100)
	end
	local s = w.stan[cel]
	local podmieniony = false
	for i = 1, #s.efekty do
		if s.efekty[i].id == idEfektu then
			s.efekty[i] = nowy -- ten sam efekt nie kumuluje się — odświeża siłę i czas
			podmieniony = true
		end
	end
	if not podmieniony then
		table.insert(s.efekty, nowy)
	end
	zdarzenie(w, "efekt_nalozony", zrodlo, cel, CZASY.efekt_nalozony, { efekt = idEfektu, wartosc = pokaz, tury = nowy.trwa })
end

local function zwyklyCios(w, kto: string, cel: string)
	local A = w.strony[kto]
	local D = w.strony[cel]
	-- zawsze pięć rzutów w tej samej kolejności
	local rRozrzut = w.los()
	local rUnik = w.los()
	local rBlok = w.los()
	local rKryt = w.los()
	local rZakl = w.los()
	local rozrzut = STALE.rozrzut_min + STALE.rozrzut_zakres * rRozrzut
	local typ
	if rUnik < D.unik then
		typ = "unik"
	elseif rBlok < D.blok then
		typ = "blok"
	elseif rKryt < A.krytyk then
		typ = "krytyk"
	else
		typ = "cios"
	end
	if typ == "unik" then
		zdarzenie(w, "unik", kto, cel, CZASY.unik, { rodzaj = A.rodzaj_ciosu })
		return
	end
	local surowe = A.cios * rozrzut * wzmocnienie(w.stan[kto])
	if typ == "krytyk" then
		surowe = surowe * A.mnoznik_krytyka
	end
	local wynik = poObronie(w, surowe, A.rodzaj_ciosu, cel)
	if typ == "blok" then
		wynik = wynik * STALE.czesc_przez_blok
	end
	local obrazenia = math.max(1, Los.zaokraglij(wynik))
	local reszta, pochloniete = przyjmij(w, cel, obrazenia)
	zdarzenie(w, typ, kto, cel, CZASY[typ], {
		obrazenia = reszta,
		pochloniete = pochloniete,
		rodzaj = A.rodzaj_ciosu,
		krytyk = typ == "krytyk",
	})
	usunZuzyteTarcze(w, cel)
	if w.stan[cel].hp > 0 and A.zaklecie ~= "" and typ ~= "blok" then
		local z = Dane.zaklecia[A.zaklecie]
		if rZakl < z.szansa then
			nalozEfekt(w, kto, cel, z.efekt, 1)
		end
	end
end

local function uzyjUmiejetnosci(w, kto: string, cel: string, idUm: string)
	local U = Dane.umiejetnosci[idUm]
	local A = w.strony[kto]
	-- zawsze cztery rzuty + jeden na każdy efekt, w tej samej kolejności
	local rRozrzut = w.los()
	local rUnik = w.los()
	local rBlok = w.los()
	local rKryt = w.los()
	local rEfekty = {}
	for _ in U.efekty do
		table.insert(rEfekty, w.los())
	end
	if U.cel == "sam" then
		zdarzenie(w, "umiejetnosc", kto, kto, U.czas, { umiejetnosc = idUm })
		for i = 1, #U.efekty do
			local wpis = U.efekty[i]
			if rEfekty[i] < wpis.szansa then
				nalozEfekt(w, kto, kto, wpis.efekt, A.moc)
			end
		end
		return
	end
	local D = w.strony[cel]
	-- umiejętność na przeciwnika to atak jak każdy inny: można jej uniknąć i przyjąć ją na tarczę
	if rUnik < D.unik then
		zdarzenie(w, "unik", kto, cel, U.czas, { umiejetnosc = idUm, rodzaj = U.rodzaj })
		return
	end
	local zablokowana = rBlok < D.blok
	local reszta, pochloniete, krytyk = 0, 0, false
	if U.mnoznik > 0 then
		local rozrzut = STALE.rozrzut_min + STALE.rozrzut_zakres * rRozrzut
		local surowe = A.cios * U.mnoznik * A.moc * rozrzut * wzmocnienie(w.stan[kto])
		krytyk = not zablokowana and rKryt < A.krytyk + U.premia_krytyka
		if krytyk then
			surowe = surowe * A.mnoznik_krytyka
		end
		local wynik = poObronie(w, surowe, U.rodzaj, cel)
		if zablokowana then
			wynik = wynik * STALE.czesc_przez_blok
		end
		reszta, pochloniete = przyjmij(w, cel, math.max(1, Los.zaokraglij(wynik)))
	end
	zdarzenie(w, if zablokowana then "blok" else "umiejetnosc", kto, cel, U.czas, {
		umiejetnosc = idUm,
		obrazenia = reszta,
		pochloniete = pochloniete,
		rodzaj = U.rodzaj,
		krytyk = krytyk,
	})
	usunZuzyteTarcze(w, cel)
	if w.stan[cel].hp > 0 and not zablokowana then
		for i = 1, #U.efekty do
			local wpis = U.efekty[i]
			if rEfekty[i] < wpis.szansa then
				nalozEfekt(w, kto, cel, wpis.efekt, A.moc)
			end
		end
	end
end

-- akcja strony na jej turze: pierwsza gotowa umiejętność w kolejności slotów albo zwykły cios
function Umiejetnosci.akcja(w, kto: string, cel: string)
	local A = w.strony[kto]
	local s = w.stan[kto]
	for i = 1, #A.umiejetnosci do
		s.liczniki[i] = s.liczniki[i] - 1
	end
	local wybrana = 0
	for i = 1, #A.umiejetnosci do
		if wybrana == 0 and s.liczniki[i] <= 0 then
			wybrana = i
		end
	end
	if wybrana ~= 0 then
		local idUm = A.umiejetnosci[wybrana]
		s.liczniki[wybrana] = Dane.umiejetnosci[idUm].odnowienie
		uzyjUmiejetnosci(w, kto, cel, idUm)
	else
		zwyklyCios(w, kto, cel)
	end
end

-- obrażenia rozłożone w czasie (trucizna, podpalenie, krwawienie) na początku tury nosiciela
function Umiejetnosci.tykniecia(w, kto: string)
	local s = w.stan[kto]
	for _, ef in s.efekty do
		if ef.typ == "obrazenia_w_czasie" and s.hp > 0 then
			local reszta, pochloniete = przyjmij(w, kto, ef.tick)
			zdarzenie(w, "efekt_tick", kto, kto, CZASY.efekt_tick, {
				efekt = ef.id,
				obrazenia = reszta,
				pochloniete = pochloniete,
				rodzaj = ef.rodzaj,
			})
		end
	end
	usunZuzyteTarcze(w, kto)
end

-- koniec tury nosiciela: efekty tracą 1 (oprócz nałożonych w tej turze), wygasłe znikają ze zdarzeniem
function Umiejetnosci.koniecTury(w, kto: string)
	local s = w.stan[kto]
	local zostaja = {}
	for _, ef in s.efekty do
		if ef.od_tury ~= w.tura then
			ef.trwa = ef.trwa - 1
		end
		if ef.trwa <= 0 then
			zdarzenie(w, "efekt_koniec", kto, kto, CZASY.efekt_koniec, { efekt = ef.id })
		else
			table.insert(zostaja, ef)
		end
	end
	s.efekty = zostaja
end

return Umiejetnosci
