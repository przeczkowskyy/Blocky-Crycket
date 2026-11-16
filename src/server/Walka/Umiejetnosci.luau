--[[
	Umiejetnosci — tura walki: mana, zwykły cios, umiejętności w slotach i efekty (silnik walki v3). Czysty moduł.
	Port w Pythonie: tools/walka/silnik.py, sekcja Umiejetnosci.luau (te same nazwy funkcji, ta sama kolejność rzutów).

	Stan walki `w` (tworzy go Silnik.symuluj):
		w.strony = { gracz = wartości bojowe, wrog = wartości bojowe }
		w.stan   = { gracz = { hp, efekty = { ... }, mana, nastepna }, wrog = ... }   -- nastepna: indeks w rotacji aktywnych
		w.dziennik, w.czas (setne sekundy), w.tura (numer tury w całej walce), w.los (generator)

	Zasady:
	• MANA (zamiast odnowień): pasek 0..mana_maks. Rośnie o mana_za_cios za każdy własny zwykły cios (także chybiony)
	  i o mana_za_obrazenia × procent utraconego maks. życia, gdy strona przyjmuje obrażenia; oba zyski × mnożnik
	  zysku (przedmioty, drzewko, pasywki; spowolnienie go obniża). Na swojej turze strona sprawdza NASTĘPNĄ aktywną
	  umiejętność w rotacji slotów: jeśli mana ≥ jej koszt (koszt × (1 − zniżka)), używa jej zamiast zwykłego ciosu
	  i płaci koszt; inaczej zwykły cios. Rotacja idzie po aktywnych w kolejności slotów i wraca na początek.
	• Zwykły cios: zawsze pięć rzutów (rozrzut, unik, blok, krytyk, zaklęcie). Kolejność: unik → blok → krytyk →
	  zwykłe trafienie. Unik zeruje cios; blok (każda klasa ma mały, tarcza dodaje dużo) przepuszcza czesc_przez_blok;
	  krytyk mnoży przez mnożnik krytyka (klasa + Zręczność).
	• Obrona: Pancerz (fizyczne) i odporność na magię (magiczne) to PUNKTY odejmowane od ciosu (D-062); obrona nigdy
	  nie zatrzymuje więcej niż limit_redukcji surowego ciosu. Tarcza z umiejętności zmniejsza trafienia o procent.
	• Umiejętność na przeciwnika to atak jak zwykły cios: można jej uniknąć i ją zablokować (wtedy bez krytyka
	  i bez efektów). Siła = cios × mnożnik × moc (Inteligencja). Umiejętność „na siebie” działa zawsze.
	• Efekty trwają N tur NOSICIELA (na końcu każdej jego tury tracą 1, oprócz tury, w której je nałożono):
	  trucizna — stosy (do limitu), tyka długo, siła od ciosu atakującego; podpalenie — bez stosów, krótko, procent
	  maks. życia celu (z limitem względem ciosu); krwawienie — procent trafienia, które je nałożyło; obrażenia w czasie
	  omijają Pancerz, odporność i tarczę, nie da się ich uniknąć ani zablokować. Spowolnienie obniża unik i zysk many
	  (nie zabiera tury); ogłuszenie zabiera najbliższą turę; zdarcie zmniejsza Pancerz; tarcza (osłona) zmniejsza
	  trafienia o procent; wzmocnienie zwiększa obrażenia. Ten sam efekt się odświeża (trucizna dokłada przy tym stos).
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

function Umiejetnosci.maEfekt(stanStrony, typ: string): boolean
	for _, ef in stanStrony.efekty do
		if ef.typ == typ then
			return true
		end
	end
	return false
end

local function wzmocnienie(stanStrony): number
	local m = 1
	for _, ef in stanStrony.efekty do
		if ef.typ == "wzmocnienie" then
			m = m + ef.wartosc
		end
	end
	return m
end

-- tarcza z umiejętności (Kamienna skóra, Bariera): ułamek obrażeń, który PRZECHODZI (1 − redukcja)
local function oslona(stanStrony): number
	local m = 1
	for _, ef in stanStrony.efekty do
		if ef.typ == "oslona" then
			m = m * (1 - ef.wartosc)
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

local function unikEfektywny(walczacy, stanStrony): number
	local u = walczacy.unik
	for _, ef in stanStrony.efekty do
		if ef.typ == "spowolnienie" then
			u = u * (1 - ef.wartosc)
		end
	end
	return u
end

local function mnoznikMany(w, strona: string): number
	local m = w.strony[strona].zysk_many
	for _, ef in w.stan[strona].efekty do
		if ef.typ == "spowolnienie" then
			m = m * (1 - ef.mana_kara)
		end
	end
	return m
end

local function dodajMane(w, strona: string, ile: number)
	local s = w.stan[strona]
	s.mana = math.min(STALE.mana_maks, s.mana + ile)
end

local function poObronie(w, surowe: number, rodzaj: string, cel: string): number
	local obrona
	if rodzaj == "fizyczne" then
		obrona = pancerzEfektywny(w.strony[cel], w.stan[cel])
	else
		obrona = w.strony[cel].odpornosc
	end
	return math.max(surowe * (1 - STALE.limit_redukcji), surowe - obrona)
end

-- surowy cios → (obrażenia, pochłonięte): obrona, blok, tarcza procentowa celu; pochłonięte = ile zatrzymała tarcza
local function obrazeniaTrafienia(w, cel: string, surowe: number, rodzaj: string, zablokowane: boolean): (number, number)
	local wynik = poObronie(w, surowe, rodzaj, cel)
	if zablokowane then
		if STALE.czesc_przez_blok <= 0 then
			return 0, 0
		end
		wynik = wynik * STALE.czesc_przez_blok
	end
	local obrazenia = math.max(1, Los.zaokraglij(wynik * oslona(w.stan[cel])))
	local pochloniete = math.max(0, Los.zaokraglij(wynik) - obrazenia)
	return obrazenia, pochloniete
end

local zdarzenie

-- wskrzeszenie (propozycja D-094): gdy życie strony spadło do zera, a ma w slocie wskrzeszenie, którego jeszcze nie
-- użyła — wraca z ułamkiem maks. życia (bez losowania) i zdarzeniem "wskrzeszenie" zaraz po śmiertelnym; raz na walkę,
-- także po śmiertelnym tyknięciu trucizny, podpalenia albo krwawienia
local function wskrzes(w, strona: string)
	local s = w.stan[strona]
	if s.hp <= 0 and s.wskrzeszenie > 0 then
		s.hp = math.max(1, Los.zaokraglij(w.strony[strona].zycie * s.wskrzeszenie))
		s.wskrzeszenie = 0
		zdarzenie(w, "wskrzeszenie", strona, strona, CZASY.wskrzeszenie, { wartosc = s.hp })
	end
end
Umiejetnosci.wskrzes = wskrzes

-- życie schodzi o obrażenia; żywy cel ładuje manę proporcjonalnie do utraconego ULAMKA maks. życia
local function przyjmij(w, cel: string, obrazenia: number): number
	local s = w.stan[cel]
	local stracone = math.min(s.hp, obrazenia)
	s.hp = s.hp - stracone
	if stracone > 0 and s.hp > 0 then
		local zycie = w.strony[cel].zycie
		dodajMane(w, cel, Los.zaokraglij(STALE.mana_za_obrazenia * 100 * stracone / zycie * mnoznikMany(w, cel)))
	end
	return stracone
end

local POLA_ZDARZENIA = { "obrazenia", "pochloniete", "rodzaj", "umiejetnosc", "efekt", "krytyk", "wartosc", "tury", "stosy" }

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
		stosy = 0,
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
	z.mana_gracz = w.stan.gracz.mana
	z.mana_wrog = w.stan.wrog.mana
	w.czas = w.czas + trwa
	table.insert(w.dziennik, z)
	return z
end
zdarzenie = Umiejetnosci.zdarzenie

local function nalozEfekt(w, zrodlo: string, cel: string, idEfektu: string, moc: number, trafienie: number)
	local E = Dane.efekty[idEfektu]
	local A = w.strony[zrodlo]
	local D = w.strony[cel]
	local s = w.stan[cel]
	local trwa = E.trwa
	if E.mod_trwania ~= "" then
		trwa = trwa + Los.zaokraglij(A.mod[E.mod_trwania])
	end
	local stary = 0
	for i = 1, #s.efekty do
		if stary == 0 and s.efekty[i].id == idEfektu then
			stary = i
		end
	end
	local nowy = {
		id = idEfektu,
		typ = E.typ,
		trwa = trwa,
		od_tury = w.tura,
		wartosc = E.wartosc,
		tick = 0,
		stosy = 1,
		rodzaj = E.rodzaj,
		mana_kara = E.mana_kara,
	}
	local pokaz = 0
	if E.typ == "obrazenia_w_czasie" then
		local sila = 1
		if E.mod_sily ~= "" then
			sila = sila + A.mod[E.mod_sily]
		end
		local jeden
		if E.sila == "cios" then
			jeden = A.cios * E.udzial * moc * sila -- trucizna: od ciosu atakującego
		elseif E.sila == "zycie_celu" then
			jeden = math.min(D.zycie * E.udzial * moc, A.cios * E.limit_ciosu) * sila -- podpalenie: od życia celu
		else
			jeden = trafienie * E.udzial * sila -- krwawienie: od ciosu, który je nałożył
		end
		nowy.tick = math.max(1, Los.zaokraglij(jeden))
		local maks = E.stosy_maks
		if E.mod_stosow ~= "" then
			maks = maks + math.floor(A.mod[E.mod_stosow])
		end
		if stary ~= 0 then
			nowy.stosy = math.min(maks, s.efekty[stary].stosy + 1)
		end
		pokaz = nowy.tick * nowy.stosy
	elseif E.typ == "oslona" or E.typ == "wzmocnienie" then
		nowy.wartosc = math.min(E.limit, E.wartosc * moc)
		pokaz = Los.zaokraglij(nowy.wartosc * 100)
	else
		pokaz = Los.zaokraglij(E.wartosc * 100)
	end
	if stary ~= 0 then
		s.efekty[stary] = nowy -- ten sam efekt odświeża siłę i czas (trucizna dokłada przy tym stos)
	else
		table.insert(s.efekty, nowy)
	end
	zdarzenie(w, "efekt_nalozony", zrodlo, cel, CZASY.efekt_nalozony, {
		efekt = idEfektu,
		wartosc = pokaz,
		tury = trwa,
		stosy = nowy.stosy,
	})
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
	if rUnik < unikEfektywny(D, w.stan[cel]) then
		typ = "unik"
	elseif rBlok < D.blok then
		typ = "blok"
	elseif rKryt < A.krytyk then
		typ = "krytyk"
	else
		typ = "cios"
	end
	local zysk = Los.zaokraglij(STALE.mana_za_cios * mnoznikMany(w, kto))
	if typ == "unik" then
		dodajMane(w, kto, zysk)
		zdarzenie(w, "unik", kto, cel, CZASY.unik, { rodzaj = A.rodzaj_ciosu })
		return
	end
	local surowe = A.cios * A.cios_zwykly * rozrzut * wzmocnienie(w.stan[kto])
	if typ == "krytyk" then
		surowe = surowe * A.mnoznik_krytyka
	end
	local obrazenia, pochloniete = obrazeniaTrafienia(w, cel, surowe, A.rodzaj_ciosu, typ == "blok")
	przyjmij(w, cel, obrazenia)
	dodajMane(w, kto, zysk)
	zdarzenie(w, typ, kto, cel, CZASY[typ], {
		obrazenia = obrazenia,
		pochloniete = pochloniete,
		rodzaj = A.rodzaj_ciosu,
		krytyk = typ == "krytyk",
	})
	wskrzes(w, cel)
	if w.stan[cel].hp > 0 and A.zaklecie ~= "" and typ ~= "blok" then
		local z = Dane.zaklecia[A.zaklecie]
		if rZakl < z.szansa + A.mod.szansa_zaklecia then
			nalozEfekt(w, kto, cel, z.efekt, 1, obrazenia)
		end
	end
end

local function uzyjUmiejetnosci(w, kto: string, cel: string, idUm: string, koszt: number)
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
		zdarzenie(w, "umiejetnosc", kto, kto, U.czas, { umiejetnosc = idUm, wartosc = koszt })
		for i = 1, #U.efekty do
			local wpis = U.efekty[i]
			if rEfekty[i] < wpis.szansa then
				nalozEfekt(w, kto, kto, wpis.efekt, A.moc, 0)
			end
		end
		return
	end
	local D = w.strony[cel]
	-- umiejętność na przeciwnika to atak jak każdy inny: można jej uniknąć i przyjąć ją na blok
	if rUnik < unikEfektywny(D, w.stan[cel]) then
		zdarzenie(w, "unik", kto, cel, U.czas, { umiejetnosc = idUm, rodzaj = U.rodzaj, wartosc = koszt })
		return
	end
	local zablokowana = rBlok < D.blok
	local obrazenia, pochloniete, krytyk = 0, 0, false
	if U.mnoznik > 0 then
		local rozrzut = STALE.rozrzut_min + STALE.rozrzut_zakres * rRozrzut
		local surowe = A.cios * U.mnoznik * A.moc * rozrzut * wzmocnienie(w.stan[kto])
		krytyk = not zablokowana and rKryt < A.krytyk + U.premia_krytyka
		if krytyk then
			surowe = surowe * A.mnoznik_krytyka
		end
		obrazenia, pochloniete = obrazeniaTrafienia(w, cel, surowe, U.rodzaj, zablokowana)
		przyjmij(w, cel, obrazenia)
	end
	zdarzenie(w, if zablokowana then "blok" else "umiejetnosc", kto, cel, U.czas, {
		umiejetnosc = idUm,
		obrazenia = obrazenia,
		pochloniete = pochloniete,
		rodzaj = U.rodzaj,
		krytyk = krytyk,
		wartosc = koszt,
	})
	wskrzes(w, cel)
	if w.stan[cel].hp > 0 and not zablokowana then
		for i = 1, #U.efekty do
			local wpis = U.efekty[i]
			if rEfekty[i] < wpis.szansa then
				nalozEfekt(w, kto, cel, wpis.efekt, A.moc, obrazenia)
			end
		end
	end
end

function Umiejetnosci.kosztUmiejetnosci(walczacy, idUm: string): number
	return Los.miedzy(
		Los.zaokraglij(Dane.umiejetnosci[idUm].koszt_many * (1 - walczacy.koszt_many)),
		1,
		STALE.mana_maks
	)
end

-- akcja strony na jej turze: następna aktywna umiejętność w rotacji, jeśli starczy many, inaczej zwykły cios
function Umiejetnosci.akcja(w, kto: string, cel: string)
	local A = w.strony[kto]
	local s = w.stan[kto]
	local n = #A.aktywne
	if n > 0 then
		local idUm = A.aktywne[s.nastepna]
		local koszt = Umiejetnosci.kosztUmiejetnosci(A, idUm)
		if s.mana >= koszt then
			s.mana = s.mana - koszt
			s.nastepna = s.nastepna % n + 1
			uzyjUmiejetnosci(w, kto, cel, idUm, koszt)
			return
		end
	end
	zwyklyCios(w, kto, cel)
end

-- obrażenia w czasie (trucizna, podpalenie, krwawienie) na początku tury nosiciela; omijają obronę i tarczę
function Umiejetnosci.tykniecia(w, kto: string)
	local s = w.stan[kto]
	for _, ef in s.efekty do
		if ef.typ == "obrazenia_w_czasie" and s.hp > 0 then
			local obr = ef.tick * ef.stosy
			przyjmij(w, kto, obr)
			zdarzenie(w, "efekt_tick", kto, kto, CZASY.efekt_tick, {
				efekt = ef.id,
				obrazenia = obr,
				rodzaj = ef.rodzaj,
				stosy = ef.stosy,
			})
			wskrzes(w, kto)
		end
	end
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

Umiejetnosci.poObronie = poObronie
Umiejetnosci.obrazeniaTrafienia = obrazeniaTrafienia
Umiejetnosci.przyjmij = przyjmij
Umiejetnosci.nalozEfekt = nalozEfekt
Umiejetnosci.zwyklyCios = zwyklyCios
Umiejetnosci.uzyjUmiejetnosci = uzyjUmiejetnosci

return Umiejetnosci
