--[[
	LogikaBohatera — czysta logika „bohatera w świecie” (propozycja, swiat/bohater_swiat). Bez instancji i usług Roblox,
	więc ten sam plik wykonuje bez Studio interpreter tools/walka/luau_mini.py (testy: lustro logika_bohatera.py).
	D = require(DaneBohatera), R = D.ruch, W = D.widocznosc.

	L.klasa(D, id) → klucz | nil                 atrybut gracza Class („Warrior”…) → bohater („wojownik”…)
	L.kluczStroju(napis) → napis                 atrybut stroju do porównań; brak atrybutu = „~” (strój odniesienia)
	L.tempo(v, naturalna, R) → liczba            tempo klipu chodu dla prędkości poziomej v (studs/s)
	L.pochylenie(v, R) → 0…1                     waga pochylenia tułowia w biegu
	L.nowaPamiec() → pam                         pamięć automatu ruchu jednego bohatera
	L.krok(pam, we, R, dt, B?) → wy              automat ruchu; we = { zyje, stan (nazwa stanu Humanoida), naZiemi,
	                                             vpoz, vpion, zdalny, wymuszony (klip z umowy albo nil) };
	                                             B = D.klasy[klasa].bieg (bez B biegu nie ma);
	                                             wy = { tryb, baza, petla, poza?, v, bieg? } — tryb: idle | chod | bieg |
	                                             skok | spadanie | ladowanie | upadek albo klip z umowy; baza: akcja
	                                             klipu (spoczynek | ruch | radosc | upadek); poza: nazwa pozy
	                                             proceduralnej; bieg = true: gra proceduralny cykl biegu
	L.kadencja(B, v) → f, d                      kadencja biegu [cykli/s] i udział podporu w cyklu dla prędkości v
	L.czasBiegu(dt, droga, v, wMiejscu) → s      czas cyklu biegu w tej klatce (z drogi postaci; w miejscu — z zegara)
	L.fazaBiegu(faza, f, dt) → faza              faza cyklu biegu po czasie dt (zawija się w 0…1)
	L.bieg(B, faza, d) → poza                    cykl biegu: { biodraY, udoL, lydkaL, stopaL, udoP, lydkaP, stopaP
	                                             (kąty stawów, radiany), rekaL, rekaP, skret (dodatki do klipu) }
	L.krokWag(wagi, cele, dt, czasy, kolejnosc)  wagi póz idą liniowo do celów (czas przejścia z danych)
	L.podStopami(hip, wysHrp, nogi) → studs      odległość środka HumanoidRootPart od ziemi pod postacią
	L.wysokoscRigu(spod, podniesienie, waga)     pionowa poprawka rigu: stopy na ziemi (spód rigu, chód pod ziemią)
	L.przesun(x, y, z, maks) → x, y, z           przesunięcie z umowy: bez NaN, długość najwyżej maks
	L.widoczny(odl, byl, W) → bool               zasięg bohatera z histerezą
	L.okres(odl, W) → n                          co ile klatek liczyć animację bohatera
	L.wybierz(kandydaci, maks) → { [id] = true } lokalny zawsze, potem najbliżsi (razem najwyżej maks)
	L.nowyRuch() → wym                           stan umowy RuchBohatera (klip, licznik, przesunięcie)
	L.polecenieRuchu(D, wym, bohater, polecenie, a, x, y, z) → wynik
	                                             umowa z mini-grami: "stan" | "klip", nazwa|nil | "przesun", jest, x, y, z;
	                                             bohater = nil (brak) albo { klasa, tryb }
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local W_POWIETRZU = { Jumping = true, Freefall = true }
local BEZ_POWIETRZA = { Climbing = true, Swimming = true, Seated = true }

local function ogranicz(x, a, b)
	return math.max(a, math.min(b, x))
end

function L.klasa(D, id)
	if type(id) ~= "string" then
		return nil
	end
	local k = D.klasy_gracza[id]
	if k ~= nil and D.klasy[k] ~= nil then
		return k
	end
	return nil
end

function L.kluczStroju(napis)
	if type(napis) == "string" then
		return napis
	end
	return "~"
end

function L.tempo(v, naturalna, R)
	if naturalna <= 0 then
		return 1
	end
	return ogranicz(v / naturalna, R.tempo_min, R.tempo_max)
end

function L.pochylenie(v, R)
	return ogranicz((v - R.pochylenie_od) / (R.pochylenie_do - R.pochylenie_od), 0, 1)
end

function L.nowaPamiec()
	return { tryb = "idle", wPowietrzu = 0, naZiemi = 0, ladowanie = 0, idzie = false, lot = false, biegnie = false,
		spada = false }
end

-- B = D.klasy[klasa].bieg (liczby cyklu biegu klasy) albo nil — wtedy biegu nie ma, zostaje klip chodu
function L.krok(pam, we, R, dt, B)
	if not we.zyje then
		pam.tryb = "upadek"
		pam.wPowietrzu = 0
		pam.naZiemi = 0
		pam.ladowanie = 0
		pam.idzie = false
		pam.lot = false
		pam.biegnie = false
		pam.spada = false
		return { tryb = "upadek", baza = "upadek", petla = false, v = 0 }
	end
	local w = we.wymuszony
	if w ~= nil then
		pam.tryb = w
		pam.wPowietrzu = 0
		pam.naZiemi = 0
		pam.ladowanie = 0
		pam.idzie = false
		pam.lot = false
		pam.biegnie = false
		pam.spada = false
		if w == "bieg" then
			if B ~= nil then
				return { tryb = w, baza = "spoczynek", petla = true, v = R.bieg_predkosc, bieg = true }
			end
			return { tryb = w, baza = "ruch", petla = true, v = R.bieg_predkosc }
		elseif w == "radosc" then
			return { tryb = w, baza = "radosc", petla = false, v = 0 }
		end
		return { tryb = w, baza = "spoczynek", petla = true, poza = w, v = 0 }
	end
	-- w powietrzu? własna postać: stan Humanoida i podłoże; cudza: stan albo duża prędkość pionowa (podłoże cudzej
	-- postaci nie jest u tego klienta pewne)
	local powietrze
	if we.zdalny then
		powietrze = W_POWIETRZU[we.stan] == true or math.abs(we.vpion) > R.prog_pionu_zdalny
	else
		powietrze = W_POWIETRZU[we.stan] == true or (not we.naZiemi and BEZ_POWIETRZA[we.stan] ~= true)
	end
	if powietrze then
		pam.wPowietrzu += dt
		pam.naZiemi = 0
	else
		pam.naZiemi += dt
		pam.wPowietrzu = 0
	end
	if powietrze and (we.stan == "Jumping" or pam.wPowietrzu >= R.min_czas_w_powietrzu_s) then
		pam.lot = true
	end
	if pam.lot and not powietrze and pam.naZiemi >= R.min_czas_na_ziemi_s then
		pam.lot = false
		pam.ladowanie = R.czas_ladowania_s
	end
	if pam.lot then
		pam.ladowanie = 0
		-- kto już spada, wraca do pozy skoku dopiero przy wyraźnym wznoszeniu (odbicie przy lądowaniu to nie skok)
		local prog = if pam.spada then R.prog_ponownego_wznoszenia else R.prog_wznoszenia
		local tryb = if we.vpion > prog then "skok" else "spadanie"
		pam.spada = tryb == "spadanie"
		pam.tryb = tryb
		return { tryb = tryb, baza = "spoczynek", petla = true, poza = tryb, v = 0 }
	end
	pam.spada = false
	local v = we.vpoz
	if we.stan == "Climbing" then
		v = math.max(v, math.abs(we.vpion))
	elseif we.stan == "Swimming" then
		v = math.sqrt(we.vpoz * we.vpoz + we.vpion * we.vpion)
	elseif we.stan == "Seated" then
		v = 0
	end
	if pam.idzie then
		if v < R.prog_ruchu_stop then
			pam.idzie = false
		end
	elseif v > R.prog_ruchu_start then
		pam.idzie = true
	end
	-- bieg: powyżej prędkości, przy której klip chodu przestaje nadążać (z histerezą vOd / vDo klasy)
	if B == nil or not pam.idzie then
		pam.biegnie = false
	elseif pam.biegnie then
		if v < B.vDo then
			pam.biegnie = false
		end
	elseif v > B.vOd then
		pam.biegnie = true
	end
	local baza = if pam.idzie and not pam.biegnie then "ruch" else "spoczynek"
	local bieg = if pam.biegnie then true else nil
	if pam.ladowanie > 0 then
		pam.ladowanie = math.max(0, pam.ladowanie - dt)
		pam.tryb = "ladowanie"
		return { tryb = "ladowanie", baza = baza, petla = true, poza = "ladowanie", v = v, bieg = bieg }
	end
	pam.tryb = if pam.biegnie then "bieg" elseif pam.idzie then "chod" else "idle"
	return { tryb = pam.tryb, baza = baza, petla = true, v = v, bieg = bieg }
end

------------------------------------------------------------------ proceduralny cykl biegu
--[[ B = D.klasy[klasa].bieg. Kostka każdej nogi idzie po torze w płaszczyźnie biegu (przód, góra) względem stawu
	biodra: w podporze (faza nogi 0…d) stoi na ziemi i cofa się od +krok/2 do −krok/2 ze stałą prędkością, w wymachu
	(d…1) wraca do przodu łukiem. Przy kadencji f [cykli/s] stopa w podporze cofa się względem bioder z prędkością
	krok · f / d — gdy d = krok · f / v, jest to dokładnie prędkość postaci, więc stopa stoi w miejscu na ziemi.
	Kąty uda i łydki z toru kostki: odwrotna kinematyka dwóch kości (kolano do przodu). ]]

-- kadencja [cykli/s] i udział podporu w cyklu dla prędkości poziomej v
function L.kadencja(B, v)
	local f = ogranicz(v * B.podpor / B.krok, B.kadencjaMin, B.kadencjaMaks)
	local d = B.podpor
	if v > 0 then
		d = math.min(B.podpor, B.krok * f / v)
	end
	return f, math.max(B.podporMin, d)
end

-- czas, o który przesuwa się cykl biegu w tej klatce: z DROGI postaci (droga / prędkość), nie z zegara — wtedy stopa
-- w podporze cofa się względem bioder dokładnie o tyle, o ile postać przesunęła się naprzód, także gdy klatki są
-- nierówne; bieg w miejscu (klip umowy) i postać prawie stojąca idą zegarem; skok położenia (teleport) jest przycięty
function L.czasBiegu(dt, droga, v, wMiejscu)
	if wMiejscu or v < 1 then
		return dt
	end
	return math.min(droga / v, 3 * dt)
end

function L.fazaBiegu(faza, f, dt)
	local n = faza + f * dt
	return n - math.floor(n)
end

-- kąty nogi (udo, łydka względem uda; radiany, > 0 = do przodu) dla kostki: przod (studs przed biodrem), wys (< 0)
local function nogaIK(B, przod, wys)
	local r = math.sqrt(przod * przod + wys * wys)
	local maks = (B.udo + B.lydka) * 0.999
	if r > maks then
		przod = przod * maks / r
		wys = wys * maks / r
		r = maks
	end
	local kolano = math.acos(ogranicz((B.udo * B.udo + B.lydka * B.lydka - r * r) / (2 * B.udo * B.lydka), -1, 1))
	local doKostki = math.atan2(przod, -wys)
	local odchylenie = math.acos(ogranicz((B.udo * B.udo + r * r - B.lydka * B.lydka) / (2 * B.udo * r), -1, 1))
	return doKostki + odchylenie, kolano - math.pi
end

-- tor kostki jednej nogi: przód względem biodra, wysokość nad ziemią, pochylenie stopy (radiany)
local function torKostki(B, fz, d)
	if fz < d then
		return B.krok / 2 - B.krok * (fz / d), B.kostka, 0
	end
	local u = (fz - d) / (1 - d)
	local s = math.sin(math.pi * u)
	return -(B.krok / 2) * math.cos(math.pi * u), B.kostka + B.unoszenie * s, B.stopaWymach * s
end

-- poza cyklu biegu w fazie 0…1 (0 = lewa stopa staje z przodu); d = udział podporu z L.kadencja
function L.bieg(B, faza, d)
	-- biodra: najniżej w połowie podporu, najwyżej w połowie lotu (dwa podskoki na cykl)
	local biodra = B.kostka + B.biodraPodpor - B.podskok * math.cos(4 * math.pi * (faza - d / 2))
	local fazaP = faza + 0.5
	if fazaP >= 1 then
		fazaP -= 1
	end
	local przodL, wysL, stopaL = torKostki(B, faza, d)
	local przodP, wysP, stopaP = torKostki(B, fazaP, d)
	local udoL, lydkaL = nogaIK(B, przodL, wysL - biodra)
	local udoP, lydkaP = nogaIK(B, przodP, wysP - biodra)
	local c = math.cos(2 * math.pi * faza)
	return {
		biodraY = biodra - B.biodro,
		udoL = udoL, lydkaL = lydkaL, stopaL = stopaL - udoL - lydkaL,
		udoP = udoP, lydkaP = lydkaP, stopaP = stopaP - udoP - lydkaP,
		-- ręce przeciwnie do nóg (dodatek do pozy z klipu): lewa do tyłu, gdy lewa stopa z przodu
		rekaL = -B.rekaL * c, rekaP = B.rekaP * c,
		skret = B.skret * math.sin(2 * math.pi * faza),
	}
end

function L.krokWag(wagi, cele, dt, czasy, kolejnosc)
	for _, nazwa in kolejnosc do
		local cel = cele[nazwa] or 0
		local w = wagi[nazwa] or 0
		local czas = czasy[nazwa] or 0
		local krok = if czas > 0 then dt / czas else 1
		if w < cel then
			w = math.min(cel, w + krok)
		elseif w > cel then
			w = math.max(cel, w - krok)
		end
		if w <= 0 then
			wagi[nazwa] = nil
		else
			wagi[nazwa] = w
		end
	end
	return wagi
end

function L.podStopami(hip, wysHrp, nogi)
	return hip + wysHrp / 2 + nogi
end

function L.wysokoscRigu(spod, podniesienie, waga)
	return podniesienie * waga - spod
end

function L.przesun(x, y, z, maks)
	if type(x) ~= "number" or type(y) ~= "number" or type(z) ~= "number" then
		return 0, 0, 0
	end
	if x ~= x or y ~= y or z ~= z then
		return 0, 0, 0
	end
	local d = math.sqrt(x * x + y * y + z * z)
	if d > maks then
		if d == math.huge then
			return 0, 0, 0
		end
		local s = maks / d
		return x * s, y * s, z * s
	end
	return x, y, z
end

function L.widoczny(odl, byl, W)
	if byl then
		return odl <= W.promien * W.histereza
	end
	return odl <= W.promien
end

function L.okres(odl, W)
	if odl <= W.promien_pelnej_animacji then
		return 1
	end
	return W.okres_daleko
end

-- kandydaci = { { id = …, odl = studs, lokalny = bool } }; lokalny zawsze, reszta od najbliższego, razem ≤ maks
function L.wybierz(kandydaci, maks)
	local wynik = {}
	local n = 0
	for _, k in kandydaci do
		if k.lokalny and wynik[k.id] == nil then
			wynik[k.id] = true
			n += 1
		end
	end
	while n < maks do
		local najlepszy = nil
		for _, k in kandydaci do
			if wynik[k.id] == nil and (najlepszy == nil or k.odl < najlepszy.odl) then
				najlepszy = k
			end
		end
		if najlepszy == nil then
			break
		end
		wynik[najlepszy.id] = true
		n += 1
	end
	return wynik
end

function L.nowyRuch()
	return { licznik = 0 }
end

local function klipUmowy(D, nazwa)
	if type(nazwa) ~= "string" then
		return false
	end
	return table.find(D.kontrakt.klipy, nazwa) ~= nil
end

function L.polecenieRuchu(D, wym, bohater, polecenie, a, x, y, z)
	if polecenie == "stan" then
		if bohater == nil then
			return nil
		end
		return { aktywny = true, klasa = bohater.klasa, klip = bohater.tryb, wymuszony = wym.klip }
	elseif polecenie == "klip" then
		if bohater == nil then
			return false
		end
		if a == nil then
			wym.klip = nil
			wym.licznik += 1
			return true
		end
		if not klipUmowy(D, a) then
			return false
		end
		wym.klip = a
		wym.licznik += 1
		return true
	elseif polecenie == "przesun" then
		if bohater == nil then
			return false
		end
		if a ~= true then
			wym.px = nil
			wym.py = nil
			wym.pz = nil
			return true
		end
		local px, py, pz = L.przesun(x, y, z, D.kontrakt.przesun_maks)
		wym.px = px
		wym.py = py
		wym.pz = pz
		return true
	end
	return nil
end

-- koniec umowy bez bohatera (wyłącznik, brak klasy, odrodzenie): pozy i przesunięcie nie zostają na następnego
function L.zerujRuch(wym)
	wym.klip = nil
	wym.px = nil
	wym.py = nil
	wym.pz = nil
	wym.licznik += 1
	return wym
end

return L
