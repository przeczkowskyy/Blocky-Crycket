--[[
	LogikaKowala — czysta logika kowala na próbę (D-102, D-051; swiat/kowal_proba). Bez instancji i usług Roblox, więc
	ten sam plik wykonuje bez Studio interpreter tools/walka/luau_mini.py (testy: lustro logika_kowala.py).

	D = require(DaneKowala). „dane gracza” = tabela pakietu „kowal” w profilu StanGracza (Sygnaly/DanePakietu):
		{ wersja = 1, przedmioty = { [id] = { poziom, zapas } }, materialy, bezLupu, klasy = { [klasa] = true } }
	Jeden egzemplarz przedmiotu na id (z poziomem ulepszenia) + zapasowe egzemplarze z łupu (`zapas`). Rozbiórka bierze
	tylko zapas. Funkcje zmieniające zwracają NOWĄ tabelę — serwer podmienia swoją dopiero po udanym zapisie.

	L.nowe(D) · L.czyste(D, v) · L.klasaZ(D, Class) · L.posiada(dane, id) · L.podstawowe(D, dane, klasa) → dane, dodane
	L.statystyki(D, id, poziom) · L.koszt(D, id, poziom) → { zloto, materialy } | nil
	L.zalozone(D, klasa, dane, napisStroju | nil) → { id… } · L.mod(D, klasa, dane, zalozone) → wpis Modyfikatory
	L.dostepne(D, dane) → napis · L.strojDoUstawienia(D, klasa, dane, napis | nil) → napis | nil (bez zmian)
	L.rozbierz(D, dane, klasa, id) → true, dane, zysk | false, powod, 0
	L.planUlepszenia(D, dane, klasa, id) → true, koszt, 0 | false, powod, brakuje
	L.ulepsz(D, dane, id, koszt) → dane · L.ranga(D, przyrostTokenow) → ranga | nil
	L.lup(D, dane, klasa, ranga, los1, los2) → dane, { id, nowy } | nil
	L.widok(D, dane, klasa, zalozone, zloto, opisBohatera) → okno (teksty i liczby; klient tylko pokazuje)
	L.opisBohatera(D, opis) · L.komunikat(D, powod, ile) · L.zNapisu / L.naNapis · L.sprawdzPrzypadki(D) → ok, n, zle
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}
local NIL = "<nil>"

local function calkowita(v, lo, hi)
	if type(v) ~= "number" or v ~= v or math.floor(v) ~= v or v < lo then
		return false
	end
	return hi == nil or v <= hi
end

local function kopia(t)
	if type(t) ~= "table" then
		return t
	end
	local w = {}
	for k, v in t do
		w[k] = kopia(v)
	end
	return w
end
L.kopia = kopia

function L.zaokr4(v)
	return math.floor(v * 10000 + 0.5) / 10000
end

function L.nowe(D)
	return { wersja = D.wersjaDanych, przedmioty = {}, materialy = 0, bezLupu = 0, klasy = {} }
end

function L.czyste(D, dane)
	local w = L.nowe(D)
	if type(dane) ~= "table" then
		return w
	end
	local p = dane.przedmioty
	if type(p) == "table" then
		for id, v in p do
			if type(id) == "string" and D.przedmioty[id] ~= nil and type(v) == "table" then
				w.przedmioty[id] = {
					poziom = if calkowita(v.poziom, 0, D.ulepszenie.maks) then v.poziom else 0,
					zapas = if calkowita(v.zapas, 0, 999) then v.zapas else 0,
				}
			end
		end
	end
	w.materialy = if calkowita(dane.materialy, 0, 999999) then dane.materialy else 0
	w.bezLupu = if calkowita(dane.bezLupu, 0, 999999) then dane.bezLupu else 0
	if type(dane.klasy) == "table" then
		for nazwa, v in dane.klasy do
			if type(nazwa) == "string" and D.klasy[nazwa] ~= nil and v == true then
				w.klasy[nazwa] = true
			end
		end
	end
	return w
end

function L.klasaZ(D, idKlasy)
	if type(idKlasy) == "string" and D.klasyGracza[idKlasy] ~= nil then
		return D.klasyGracza[idKlasy]
	end
	return D.klasaDomyslna
end

function L.posiada(dane, id)
	return dane.przedmioty[id] ~= nil
end

function L.podstawowe(D, dane, klasa)
	if D.klasy[klasa] == nil or dane.klasy[klasa] then
		return dane, {}
	end
	local w = kopia(dane)
	local dodane = {}
	for _, id in D.klasy[klasa].podstawowe do
		if w.przedmioty[id] == nil then
			w.przedmioty[id] = { poziom = 0, zapas = 0 }
			table.insert(dodane, id)
		end
	end
	w.klasy[klasa] = true
	return w, dodane
end

function L.statystyki(D, id, poziom)
	local P = D.przedmioty[id]
	local w = {}
	for _, s in D.statystyki do
		local k = s.id
		local v = (P.baza[k] or 0) + poziom * (P.krok[k] or 0)
		if v ~= 0 then
			w[k] = if k == "tarcza" then L.zaokr4(v) else v
		end
	end
	return w
end

function L.koszt(D, id, poziom)
	if poziom >= D.ulepszenie.maks then
		return nil
	end
	local K = D.przedmioty[id].koszt
	return { zloto = K.zloto[poziom + 1], materialy = K.materialy[poziom + 1] }
end

function L.zNapisu(napis)
	if type(napis) ~= "string" then
		return nil
	end
	local wynik = {}
	local start = 1
	while start <= #napis + 1 do
		local a = string.find(napis, ",", start, true)
		local kawalek = string.sub(napis, start, if a then a - 1 else #napis)
		if kawalek ~= "" then
			table.insert(wynik, kawalek)
		end
		if not a then
			break
		end
		start = a + 1
	end
	return wynik
end

function L.naNapis(ids)
	return table.concat(ids, ",")
end

function L.zalozone(D, klasa, dane, napis)
	local lista = D.klasy[klasa].przedmioty
	local w = {}
	if napis == nil then
		for _, id in lista do
			if L.posiada(dane, id) then
				table.insert(w, id)
			end
		end
		return w
	end
	local zb = {}
	for _, id in L.zNapisu(napis) or {} do
		zb[id] = true
	end
	for _, id in lista do
		if zb[id] and L.posiada(dane, id) then
			table.insert(w, id)
		end
	end
	return w
end

local BOJOWE = { bron = true, pancerz = true, tarcza = true }

local function maTarcze(D, zal)
	for _, id in zal do
		if D.przedmioty[id].slot == "OffHand" then
			return true
		end
	end
	return false
end

function L.mod(D, klasa, dane, zal)
	local suma = {}
	for _, id in zal do
		for k, v in L.statystyki(D, id, dane.przedmioty[id].poziom) do
			suma[k] = (suma[k] or 0) + v
		end
	end
	local K = D.klasy[klasa]
	if K.tarcza and not maTarcze(D, zal) then
		suma.tarcza = (suma.tarcza or 0) - D.blokTarczy
	end
	local w = {}
	local st = {}
	local ileSt = 0
	for _, s in D.statystyki do
		local k = s.id
		local v = suma[k] or 0
		if BOJOWE[k] then
			if k == "tarcza" then
				v = L.zaokr4(v)
				if v ~= 0 and K.tarcza then
					w[k] = v
				end
			elseif v ~= 0 then
				w[k] = v
			end
		elseif v ~= 0 then
			st[k] = v
			ileSt += 1
		end
	end
	if ileSt > 0 then
		w.statystyki = st
	end
	return w
end

function L.dostepne(D, dane)
	local w = {}
	for _, id in D.kolejnosc do
		if L.posiada(dane, id) then
			table.insert(w, id)
		end
	end
	return L.naNapis(w)
end

function L.strojDoUstawienia(D, klasa, dane, napis)
	if napis == nil then
		return L.naNapis(L.zalozone(D, klasa, dane, nil))
	end
	local ids = L.zNapisu(napis) or {}
	local zb = {}
	for _, id in ids do
		zb[id] = true
	end
	local dobre = {}
	local zle = false
	for _, id in ids do
		local calosc = D.czesci[id]
		if calosc ~= nil then
			if not (zb[calosc] and L.posiada(dane, calosc)) then
				zle = true
			end
		elseif D.przedmioty[id] ~= nil and D.przedmioty[id].klasa == klasa and L.posiada(dane, id) then
			dobre[id] = true
		else
			zle = true
		end
	end
	if not zle then
		return nil
	end
	local w = {}
	for _, id in D.klasy[klasa].przedmioty do
		if dobre[id] then
			table.insert(w, id)
		end
	end
	return L.naNapis(w)
end

local function przedmiotKlasy(D, klasa, id)
	return type(id) == "string" and D.przedmioty[id] ~= nil and D.przedmioty[id].klasa == klasa
end

function L.rozbierz(D, dane, klasa, id)
	if not przedmiotKlasy(D, klasa, id) then
		return false, "nieznany_przedmiot", 0
	end
	if not L.posiada(dane, id) then
		return false, "nie_masz", 0
	end
	if dane.przedmioty[id].zapas < 1 then
		return false, "brak_zapasu", 0
	end
	local w = kopia(dane)
	w.przedmioty[id].zapas -= 1
	local zysk = D.rozbiorka.materialy
	w.materialy += zysk
	return true, w, zysk
end

function L.planUlepszenia(D, dane, klasa, id)
	if not przedmiotKlasy(D, klasa, id) then
		return false, "nieznany_przedmiot", 0
	end
	if not L.posiada(dane, id) then
		return false, "nie_masz", 0
	end
	local k = L.koszt(D, id, dane.przedmioty[id].poziom)
	if k == nil then
		return false, "najwyzszy", 0
	end
	if dane.materialy < k.materialy then
		return false, "za_malo_materialow", k.materialy - dane.materialy
	end
	return true, k, 0
end

function L.ulepsz(D, dane, id, k)
	local w = kopia(dane)
	w.materialy -= k.materialy
	w.przedmioty[id].poziom += 1
	return w
end

-- wskazówka celu „kowal”: Złoto i materiały na ulepszenie któregoś posiadanego przedmiotu klasy
function L.moznaUlepszyc(D, klasa, dane, zloto)
	for _, id in D.klasy[klasa].przedmioty do
		if L.posiada(dane, id) then
			local k = L.koszt(D, id, dane.przedmioty[id].poziom)
			if k ~= nil and dane.materialy >= k.materialy and zloto >= k.zloto then
				return true
			end
		end
	end
	return false
end

function L.sumaPoziomow(dane)
	local n = 0
	for _, v in dane.przedmioty do
		n += v.poziom
	end
	return n
end

function L.ranga(D, roznica)
	local G = D.lup.progi
	if not calkowita(roznica, 1, G.maks) then
		return nil
	end
	if roznica >= G.straznik then
		return "straznik"
	elseif roznica >= G.rzadki then
		return "rzadki"
	end
	return "zwykly"
end

function L.lup(D, dane, klasa, ranga, los1, los2)
	local w = kopia(dane)
	local szansa = D.lup.szansa[ranga] or 0
	if los1 >= szansa and w.bezLupu + 1 < D.lup.ochrona then
		w.bezLupu += 1
		return w, nil
	end
	w.bezLupu = 0
	local lista = D.klasy[klasa].przedmioty
	local i = math.min(#lista, math.floor(los2 * #lista) + 1)
	local id = lista[i]
	if w.przedmioty[id] ~= nil then
		w.przedmioty[id].zapas += 1
		return w, { id = id, nowy = false }
	end
	w.przedmioty[id] = { poziom = 0, zapas = 0 }
	return w, { id = id, nowy = true }
end

------------------------------------------------------------------ teksty okna
-- odmiana przy liczbie: formy = { 1, 2–4, 5+ }; 12–14 i 0 jak 5+, 22–24, 32–34… jak 2–4
function L.forma(formy, n)
	n = math.floor(math.abs(n))
	if n == 1 then
		return formy[1]
	end
	local j, d = n % 10, n % 100
	if j >= 2 and j <= 4 and not (d >= 12 and d <= 14) then
		return formy[2]
	end
	return formy[3]
end

function L.ileMaterialow(D, n)
	return string.format("%d %s", n, L.forma(D.teksty.formy_materialu, n))
end

function L.ileMaterialowDop(D, n)
	return string.format("%d %s", n, L.forma(D.teksty.formy_materialu_dopelniacz, n))
end

function L.liczbaTekst(v)
	return string.format("%d", v)
end

function L.tekstStat(D, k, v)
	local nazwa = D.nazwyStatystyk[k]
	local znak = if v >= 0 then "+" else "−"
	if k == "tarcza" then
		return string.format("%s %s%d%%", nazwa, znak, math.floor(math.abs(v) * 100 + 0.5))
	end
	return string.format("%s %s%s", nazwa, znak, L.liczbaTekst(math.abs(v)))
end

function L.tekstStatLista(D, st)
	local czesci = {}
	for _, s in D.statystyki do
		if st[s.id] ~= nil then
			table.insert(czesci, L.tekstStat(D, s.id, st[s.id]))
		end
	end
	return table.concat(czesci, " · ")
end

function L.wiersz(D, dane, klasa, id, zal, zloto)
	local T = D.teksty
	local P = D.przedmioty[id]
	local zalozony = table.find(zal, id) ~= nil
	local w = { id = id, nazwa = P.nazwa, slot = D.sloty[P.slot], posiadany = L.posiada(dane, id), zalozony = zalozony,
		poziom = 0, zapas = 0, staty = "", nastepny = "", koszt = "", ulepsz = false, powod = "", rozbierz = false,
		rozbiorka = "" }
	if not w.posiadany then
		w.staty = T.nie_masz
		return w
	end
	local s = dane.przedmioty[id]
	w.poziom = s.poziom
	w.zapas = s.zapas
	local opis = L.tekstStatLista(D, L.statystyki(D, id, s.poziom))
	if P.slot == "OffHand" and D.klasy[klasa].tarcza then
		local wz = string.format(T.blok_wzoru, math.floor(D.blokTarczy * 100 + 0.5))
		opis = if opis == "" then wz else wz .. " · " .. opis
	end
	w.staty = if opis ~= "" then opis else T.bez_statystyk
	local k = L.koszt(D, id, s.poziom)
	if k == nil then
		w.nastepny = T.maks
	else
		local przyrost = {}
		for _, x in D.statystyki do
			local v = P.krok[x.id] or 0
			if v ~= 0 then
				przyrost[x.id] = v
			end
		end
		w.nastepny = string.format(T.nastepny, L.tekstStatLista(D, przyrost))
		w.koszt = string.format(T.koszt, k.zloto, L.ileMaterialow(D, k.materialy))
		if dane.materialy < k.materialy then
			w.powod = string.format(T.za_malo_materialow, L.ileMaterialowDop(D, k.materialy - dane.materialy))
		elseif zloto < k.zloto then
			w.powod = string.format(T.za_malo_zlota, k.zloto - zloto)
		else
			w.ulepsz = true
		end
	end
	if s.zapas > 0 then
		w.rozbierz = true
		w.rozbiorka = string.format(T.rozbiorka, L.ileMaterialow(D, D.rozbiorka.materialy))
	end
	return w
end

function L.widok(D, dane, klasa, zal, zloto, bohater)
	local T = D.teksty
	local lista = D.klasy[klasa].przedmioty
	local wiersze = {}
	for _, id in lista do
		if L.posiada(dane, id) then
			table.insert(wiersze, L.wiersz(D, dane, klasa, id, zal, zloto))
		end
	end
	for _, id in lista do
		if not L.posiada(dane, id) then
			table.insert(wiersze, L.wiersz(D, dane, klasa, id, zal, zloto))
		end
	end
	local uwaga = ""
	if D.klasy[klasa].tarcza and not maTarcze(D, zal) then
		uwaga = T.bez_tarczy
	end
	return { tytul = T.tytul, klasa = D.nazwyKlas[klasa], materialy = string.format(T.materialy, dane.materialy),
		zloto = string.format(T.zloto, zloto),
		bohater = if type(bohater) == "string" and bohater ~= "" then string.format(T.bohater, bohater) else "",
		uwaga = uwaga, wiersze = wiersze }
end

function L.opisBohatera(D, opis)
	if type(opis) ~= "table" then
		return ""
	end
	local czesci = {}
	local b = opis.bron
	if type(b) == "table" and type(b.obrazenia) == "number" then
		table.insert(czesci, D.nazwyStatystyk.bron .. " " .. L.liczbaTekst(math.floor(b.obrazenia + 0.5)))
	end
	local p = opis.pancerz_przedmiotow
	if type(p) == "number" then
		table.insert(czesci, D.nazwyStatystyk.pancerz .. " " .. L.liczbaTekst(math.floor(p + 0.5)))
	end
	local t = opis.tarcza
	if type(t) == "table" and type(t.blok) == "number" then
		table.insert(czesci, string.format("%s %d%%", D.nazwyStatystyk.tarcza, math.floor(t.blok * 100 + 0.5)))
	end
	return table.concat(czesci, " · ")
end

local MAPA_KOMUNIKATOW = { brak_zapasu = "brak_zapasu", nie_masz = "nie_masz_przedmiotu", najwyzszy = "najwyzszy",
	daleko = "podejdz", za_szybko = "za_szybko", brak_stanu = "nieczynna" }

function L.komunikat(D, powod, ile)
	local T = D.teksty
	if powod == "za_malo_materialow" then
		return string.format(T.za_malo_materialow, L.ileMaterialowDop(D, ile or 0))
	elseif powod == "za_malo_zlota" then
		return string.format(T.za_malo_zlota, ile or 0)
	end
	return T[MAPA_KOMUNIKATOW[powod] or "blad"]
end

------------------------------------------------------------------ zgodność z lustrem (przypadki z dane.py)
local function rowne(a, b)
	if a == NIL then
		return b == nil
	end
	if type(a) ~= type(b) then
		return false
	end
	if type(a) == "number" then
		return math.abs(a - b) < 1e-9
	end
	if type(a) ~= "table" then
		return a == b
	end
	for k, v in a do
		if not rowne(v, b[k]) then
			return false
		end
	end
	for k, v in b do
		if a[k] == nil and v ~= nil then
			return false
		end
	end
	return true
end
L.rowne = rowne

local function arg(v)
	if v == NIL then
		return nil
	end
	return v
end

function L.sprawdzPrzypadki(D)
	local P = D.przypadki
	local n, zle = 0, {}
	local function sprawdz(nazwa, i, oczekiwane, wynik)
		n += 1
		if not rowne(oczekiwane, wynik) then
			table.insert(zle, nazwa .. " " .. tostring(i))
		end
	end
	for i, p in P.czyste do
		sprawdz("czyste", i, p.wynik, L.czyste(D, arg(p.v)))
	end
	for i, p in P.mod do
		local zal = L.zalozone(D, p.klasa, p.dane, arg(p.napis))
		sprawdz("zalozone", i, p.zalozone, zal)
		sprawdz("mod", i, p.wynik, L.mod(D, p.klasa, p.dane, zal))
	end
	for i, p in P.koszt do
		sprawdz("koszt", i, p.wynik, L.koszt(D, p.id, p.poziom))
	end
	for i, p in P.rozbierz do
		local ok, w, zysk = L.rozbierz(D, p.dane, p.klasa, p.id)
		sprawdz("rozbierz", i, { p.ok, p.wynik, p.zysk }, { ok, w, zysk })
	end
	for i, p in P.plan do
		local ok, w, ile = L.planUlepszenia(D, p.dane, p.klasa, p.id)
		sprawdz("plan", i, { p.ok, p.wynik, p.ile }, { ok, w, ile })
	end
	for i, p in P.lup do
		local w, lup = L.lup(D, p.dane, p.klasa, p.ranga, p.l1, p.l2)
		sprawdz("lup", i, p.wynik, w)
		sprawdz("lup_przedmiot", i, p.lup, lup)
	end
	for i, p in P.stroj do
		sprawdz("stroj", i, p.wynik, L.strojDoUstawienia(D, p.klasa, p.dane, arg(p.napis)))
	end
	for i, p in P.ranga do
		sprawdz("ranga", i, p.wynik, L.ranga(D, p.r))
	end
	for i, p in P.widok do
		sprawdz("widok", i, p.wynik, L.widok(D, p.dane, p.klasa, p.zalozone, p.zloto, p.bohater))
	end
	for i, p in P.opis do
		sprawdz("opis", i, p.wynik, L.opisBohatera(D, p.opis))
	end
	for i, p in P.mozna do
		sprawdz("mozna", i, { p.wynik, p.suma }, { L.moznaUlepszyc(D, p.klasa, p.dane, p.zloto), L.sumaPoziomow(p.dane) })
	end
	for i, p in P.odmiana do
		sprawdz("odmiana", i, { p.mianownik, p.dopelniacz }, { L.ileMaterialow(D, p.n), L.ileMaterialowDop(D, p.n) })
	end
	return #zle == 0, n, zle
end

return L
