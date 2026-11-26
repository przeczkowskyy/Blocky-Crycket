--[[
	LogikaPetow — czysta logika petów na próbę (ModuleScript w Workspace/PetyProba/Moduly; używa go SerwerPetow
	i KlientPetow). Bez Roblox: niczego nie zmienia w świecie, nie używa zegara ani Random (losową liczbę r podaje
	serwer). Lustro w Pythonie: swiat/pety_proba/logika_petow.py (te same nazwy w snake_case); testy uruchamiają ten
	plik w interpreterze tools/walka/luau_mini.py i porównują z lustrem. Dlatego tylko podzbiór Luau, który rozumie
	luau_mini: bez string.match, table.sort, table.clone, ipairs i `::`.

	D = DanePetow (wygenerowane przez dane_petow.py). Funkcje:
		pet(D, id), jajko(D, id), rzadkosc(D, id)  → wpis albo nil
		jajkoPeta(D, idPeta), jajkoKrainy(D, kraina) → jajko albo nil (każdy pet jest w puli jednego jajka)
		kupione(D, jajko, wydatki, tryb?)         → ile jajek liczy się do ceny (licznik osobny / wspólny)
		cena(D, jajko, kupione, tryb?)            → cena NASTĘPNEGO jajka: "stala" (domyślnie, decyzja 17.11),
		                                            "rosnaca" (rośnie z kupionymi do maks) albo "kalkulator"
		opisCeny(D, jajko, tryb?)                 → „cena: 300 Rybek” albo „od 300 Rybek · rośnie z każdym jajkiem”
		forma(formy, n), ileRybek(D, n, przypadek?) → „3 Rybki” (waluta Rybki = atrybut Gold, D-146; przypadek "m"
		                                            mianownik — domyślnie, "b" biernik „Kup za 1 Rybkę”, "d" dopełniacz)
		losuj(D, jajko, r)                        → id peta (r ∈ [0, 1), jawne szanse po kolei)
		procent(szansa), opisSkilla(D, pet), premiaPeta(D, id), tekstBraku(D, brakuje, zloto, cena)
		modPeta(D, id)                            → modyfikator bohatera od peta (Sygnaly/Modyfikatory stanu gracza)
		wierszeSzans(D, jajko), wierszeZagrody(D, kopie, aktywny), decyzja(D, stan), czasWyklucia(D)
		zagroda — Rybki (25.11.2026, propozycja, liczby robocze): stawka(D, id), poziomZagrody(D, wydatki),
		miejscaZagrody(D, poziom), cenaUlepszenia(D, poziom) (nil = najwyższy), czystyWybor(D, wybor) (nil = najrzadsze),
		wZagrodzie(D, kopie, aktywny, wybor, miejsc, poza), przychodS(D, lista), opisPrzychodu(D, s),
		stanZagrody(D, kopie, aktywny, wybor, wydatki, poza), zmienWybor(D, …, pet, tak) → wybór, powód,
		poWyborze(D, wybor, stary, nowy), poOdstawieniu(D, wybor, stary), tik(D, reszta, s, dt) → ile, reszta,
		tekstBrakuUlepszenia(D, brakuje, zloto, cena)
		rowne(a, b), sprawdzPrzypadki(D) → ok, n, bledy
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local function liczba(v): boolean
	return type(v) == "number" and v == v and v > -math.huge and v < math.huge
end

local function calkowitaNieujemna(v): boolean
	return liczba(v) and v >= 0 and math.floor(v) == v
end

function L.pet(D, id)
	for _, p in D.pety do
		if p.id == id then
			return p
		end
	end
	return nil
end

function L.jajko(D, id)
	for _, j in D.jajka do
		if j.id == id then
			return j
		end
	end
	return nil
end

function L.rzadkosc(D, id)
	for _, r in D.rzadkosci do
		if r.id == id then
			return r
		end
	end
	return nil
end

function L.jajkoPeta(D, id)
	for _, j in D.jajka do
		for _, x in j.pula do
			if x == id then
				return j
			end
		end
	end
	return nil
end

function L.jajkoKrainy(D, kraina)
	for _, j in D.jajka do
		if j.kraina == kraina then
			return j
		end
	end
	return nil
end

-- ile jajek liczy się do ceny jajka j: "osobny" — kupione jajka j; "wspolny" — kupione jajka wszystkich biomów
function L.kupione(D, j, wydatki, tryb): number
	local t = tryb or D.licznik_ceny.tryb
	local function n(id): number
		local v = if type(wydatki) == "table" then wydatki[id] else nil
		return if calkowitaNieujemna(v) then v else 0
	end
	if t == "wspolny" then
		local s = 0
		for _, x in D.jajka do
			s += n(x.id)
		end
		return s
	end
	return n(j.id)
end

function L.cena(D, j, kupione, tryb): number
	local c = j.cena
	local t = tryb or c.tryb
	local n = if calkowitaNieujemna(kupione) then kupione else 0
	if t == "stala" then
		return c.stala
	end
	if t == "kalkulator" then
		return c.kalkulator
	end
	return math.min(c.maks, c.start + c.krok * n)
end

-- odmiana przy liczbie: formy = { 1, 2–4, 5+ }; 0 i 12–14 jak 5+, 22–24, 32–34… jak 2–4
function L.forma(formy, n: number)
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

local PRZYPADKI_RYBEK = { m = "formy_rybki", b = "formy_rybki_biernik", d = "formy_rybki_dopelniacz" }

-- waluta Rybki (atrybut Gold, D-146): „1 Rybka / 3 Rybki / 5 Rybek” (m), „Kup za 1 Rybkę” (b), „Brakuje ci 1 Rybki” (d)
function L.ileRybek(D, n: number, przypadek: string?): string
	return string.format("%d %s", n, L.forma(D.teksty[PRZYPADKI_RYBEK[przypadek or "m"]], n))
end

function L.opisCeny(D, j, tryb): string
	local T = D.teksty
	local t = tryb or j.cena.tryb
	if t == "rosnaca" then
		return string.format(T.cena_od, L.ileRybek(D, L.cena(D, j, 0, t), "d")) .. " · " .. T.rosnie
	end
	return string.format(T.cena_tablica, L.ileRybek(D, L.cena(D, j, 0, t)))
end

function L.losuj(D, j, r): string
	if not liczba(r) or r < 0 then
		r = 0
	end
	local suma = 0
	for _, s in j.szanse do
		suma += s.szansa
		if r < suma then
			return s.pet
		end
	end
	return j.szanse[#j.szanse].pet
end

function L.procent(szansa: number): string
	local p = szansa * 100
	local calk = math.floor(p + 0.5)
	if math.abs(p - calk) < 1e-9 then
		return string.format("%d%%", calk)
	end
	local dz = math.floor(p * 10 + 0.5)
	return string.format("%d,%d%%", math.floor(dz / 10), dz - 10 * math.floor(dz / 10))
end

local function proc(v: number): number
	return math.floor(v * 100 + 0.5)
end

local function lista(nazwy): string
	if #nazwy == 1 then
		return nazwy[1]
	end
	local t = nazwy[1]
	for i = 2, #nazwy - 1 do
		t = t .. ", " .. nazwy[i]
	end
	return t .. " i " .. nazwy[#nazwy]
end

-- części opisu skilla (D-101): żywioł, premie do statystyk (równe razem), premia do łupu
function L.czesciSkilla(D, p)
	local s = p.skill
	local T = D.teksty
	local m = s.mod
	local czesci = {}
	if s.zywiol then
		local Z = D.zywioly[s.zywiol]
		table.insert(czesci, Z.nazwa .. ": " .. Z.opis)
	end
	local pr = m.procent or {}
	local grupy = {}
	for _, a in D.kolejnosc_statystyk do
		local v = pr[a]
		if v and v ~= 0 then
			local n = proc(v)
			local znaleziona = false
			for _, g in grupy do
				if g.n == n then
					table.insert(g.nazwy, D.statystyki[a])
					znaleziona = true
					break
				end
			end
			if not znaleziona then
				table.insert(grupy, { n = n, nazwy = { D.statystyki[a] } })
			end
		end
	end
	for _, g in grupy do
		table.insert(czesci, string.format("+%d%% ", g.n) .. lista(g.nazwy))
	end
	local lup = m.lup or {}
	local z, x = proc(lup.zloto or 0), proc(lup.doswiadczenie or 0)
	if z > 0 and x > 0 and z == x then
		table.insert(czesci, string.format(T.skill_oba, z))
	else
		if z > 0 then
			table.insert(czesci, string.format(T.skill_zloto, z))
		end
		if x > 0 then
			table.insert(czesci, string.format(T.skill_xp, x))
		end
	end
	return czesci
end

-- skill jednym krótkim zdaniem (tablica szans, okno zagrody, napis po wykluciu)
function L.opisSkilla(D, p): string
	return table.concat(L.czesciSkilla(D, p), ", ")
end

-- najkrócej (tablica zagrody): nazwa żywiołu albo pierwsza premia
function L.opisSkillaKrotki(D, p): string
	if p.skill.zywiol then
		return D.zywioly[p.skill.zywiol].nazwa
	end
	return L.czesciSkilla(D, p)[1]
end

local function niepusta(t): boolean
	if type(t) ~= "table" then
		return false
	end
	for _ in t do
		return true
	end
	return false
end

-- modyfikator bohatera dla StanGracza/Sygnaly/Modyfikatory (źródło "pety"): procent, lup, pasywki żywiołu
function L.modPeta(D, id)
	local p = L.pet(D, id)
	if not p then
		return nil
	end
	local m = p.skill.mod
	local w = {}
	if niepusta(m.procent) then
		local t = {}
		for k, v in m.procent do
			t[k] = v
		end
		w.procent = t
	end
	if niepusta(m.lup) then
		local t = {}
		for k, v in m.lup do
			t[k] = v
		end
		w.lup = t
	end
	if p.skill.zywiol then
		local Z = D.zywioly[p.skill.zywiol]
		local t = {}
		for _, n in Z.pasywki do
			table.insert(t, n)
		end
		if #t > 0 then
			w.pasywki = t
		end
		if Z.zaklecie then
			w.zaklecie = Z.zaklecie -- zaklęcie broni silnika: podpalenie / trucizna przy ciosie gracza
		end
	end
	return w
end

-- premia do łupu {zloto, doswiadczenie} dla Pety("kup" / "aktywny") (zgodność wstecz stanu gracza)
function L.premiaPeta(D, id)
	local p = L.pet(D, id)
	local lup = if p then (p.skill.mod.lup or {}) else {}
	return { zloto = lup.zloto or 0, doswiadczenie = lup.doswiadczenie or 0 }
end

function L.tekstBraku(D, brakuje: number, zloto: number, c: number): string
	return string.format(D.teksty.za_malo, L.ileRybek(D, brakuje, "d"), zloto, c)
end

function L.wierszeSzans(D, j)
	local w = {}
	for _, s in j.szanse do
		local p = L.pet(D, s.pet)
		local r = L.rzadkosc(D, p.rzadkosc)
		table.insert(w, { pet = p.id, nazwa = p.nazwa, rzadkosc = r.nazwa, kolor = r.kolor, szansa = L.procent(s.szansa),
			skill = L.opisSkilla(D, p) })
	end
	return w
end

function L.wierszeZagrody(D, kopie, aktywny)
	local w = {}
	for _, p in D.pety do
		local n = if type(kopie) == "table" then kopie[p.id] else nil
		if calkowitaNieujemna(n) and n > 0 then
			local r = L.rzadkosc(D, p.rzadkosc)
			table.insert(w, { pet = p.id, nazwa = p.nazwa, rzadkosc = r.nazwa, kolor = r.kolor, kopie = n,
				skill = L.opisSkilla(D, p), krotko = L.opisSkillaKrotki(D, p), aktywny = p.id == aktywny, jajko = p.jajko })
		end
	end
	return w
end

function L.decyzja(D, stan)
	local T = D.teksty
	if not stan.stan_gracza then
		return { ok = false, powod = "brak_stanu", tekst = T.brak_stanu }
	end
	if L.jajko(D, stan.jajko) == nil then
		return { ok = false, powod = "nieznane_jajko", tekst = T.nieznane }
	end
	if stan.zajety then
		return { ok = false, powod = "trwa_wyklucie", tekst = T.trwa }
	end
	return { ok = true, powod = "ok", tekst = "" }
end

function L.czasWyklucia(D): number
	local W = D.wyklucie
	return W.trzesienie_s + W.pekniecie_s + W.wyskok_s + W.radosc_s
end

-- równość głęboka (tabele: te same klucze i wartości; liczby z tolerancją 1e-9)
------------------------------------------------------------------ zagroda: Rybki (25.11.2026, propozycja)
-- Pety stojące w zagrodzie dają Rybki (atrybut Gold, D-146) na sekundę; pet idący za graczem i pety na wyprawie
-- (`poza` — wypraw jeszcze nie ma) nie stoją w zagrodzie. Miejsca z D.zagroda.poziomy (2 → 4 → 6 → 8), poziom z licznika
-- wydatków na cel D.zagroda.cel_ulepszenia w profilu StanGracza. Liczby robocze (ustawienia.json → zagroda).
function L.stawka(D, id): number
	local p = L.pet(D, id)
	return if p then p.rybki_s else 0
end

function L.poziomZagrody(D, wydatki): number
	local v = if type(wydatki) == "table" then wydatki[D.zagroda.cel_ulepszenia] else nil
	local n = if calkowitaNieujemna(v) then v else 0
	return math.min(1 + n, #D.zagroda.poziomy)
end

function L.miejscaZagrody(D, poziom): number
	local poz = D.zagroda.poziomy
	local i = if calkowitaNieujemna(poziom) then poziom else 1
	return poz[math.max(1, math.min(i, #poz))].miejsc
end

function L.cenaUlepszenia(D, poziom): number?
	local poz = D.zagroda.poziomy
	local i = if calkowitaNieujemna(poziom) then poziom else 1
	if i >= #poz then
		return nil
	end
	return poz[math.max(1, i) + 1].cena
end

local function zawiera(lista, x): boolean
	for _, v in lista do
		if v == x then
			return true
		end
	end
	return false
end

function L.czystyWybor(D, wybor)
	if type(wybor) ~= "table" then
		return nil
	end
	local n = 0
	for k in wybor do
		if type(k) ~= "number" or k < 1 or math.floor(k) ~= k then
			return nil
		end
		n += 1
	end
	local w = {}
	for i = 1, n do
		local x = wybor[i]
		if type(x) == "string" and L.pet(D, x) ~= nil and not zawiera(w, x) and #w < #D.pety then
			table.insert(w, x)
		end
	end
	return w
end

local function nrRzadkosci(D, id): number
	local p = L.pet(D, id)
	for i, r in D.rzadkosci do
		if p and r.id == p.rzadkosc then
			return i
		end
	end
	return 0
end

local function przed(D, a, b, kolejnosc): boolean
	local ra, rb = nrRzadkosci(D, a), nrRzadkosci(D, b)
	if ra ~= rb then
		return ra > rb
	end
	local sa, sb = L.stawka(D, a), L.stawka(D, b)
	if sa ~= sb then
		return sa > sb
	end
	return kolejnosc[a] < kolejnosc[b]
end

function L.wZagrodzie(D, kopie, aktywny, wybor, miejsc, poza)
	local k = if type(kopie) == "table" then kopie else {}
	local pz = if type(poza) == "table" then poza else {}
	local kolejnosc, kandydaci = {}, {}
	for i, p in D.pety do
		kolejnosc[p.id] = i
		local n = k[p.id]
		if calkowitaNieujemna(n) and n > 0 and p.id ~= aktywny and not pz[p.id] then
			table.insert(kandydaci, p.id)
		end
	end
	local m = if calkowitaNieujemna(miejsc) then miejsc else 0
	local czysty = L.czystyWybor(D, wybor)
	local w = {}
	if czysty ~= nil then
		for _, x in czysty do
			if zawiera(kandydaci, x) and #w < m then
				table.insert(w, x)
			end
		end
		return w
	end
	-- wstawianie (luau_mini bez table.sort i table.insert z pozycją) — ta sama kolejność co w lustrze Pythona
	local lista = {}
	for _, x in kandydaci do
		local i = #lista + 1
		while i > 1 and przed(D, x, lista[i - 1], kolejnosc) do
			lista[i] = lista[i - 1]
			i -= 1
		end
		lista[i] = x
	end
	for i = 1, math.min(m, #lista) do
		w[i] = lista[i]
	end
	return w
end

function L.przychodS(D, lista): number
	local s = 0
	for _, x in (if type(lista) == "table" then lista else {}) do
		s += L.stawka(D, x)
	end
	return s
end

function L.opisPrzychodu(D, s): string
	local v = if liczba(s) and s > 0 then s * 60 else 0
	local t
	if v >= 10 then
		t = string.format("%d", math.floor(v + 0.5))
	else
		local dz = math.floor(v * 10 + 0.5)
		t = if dz % 10 == 0 then string.format("%d", math.floor(dz / 10))
			else string.format("%d,%d", math.floor(dz / 10), dz % 10)
	end
	-- przy ułamku dopełniacz liczby pojedynczej („+2,4 Rybki/min”), przy całej liczbie odmiana („+3 Rybki”, „+12 Rybek”)
	local T = D.teksty
	local slowo = if string.find(t, ",", 1, true) then T.formy_rybki_dopelniacz[1]
		else L.forma(T.formy_rybki, tonumber(t) or 0)
	return string.format(T.przychod_min, t, slowo)
end

function L.stanZagrody(D, kopie, aktywny, wybor, wydatki, poza)
	local poziom = L.poziomZagrody(D, wydatki)
	local miejsc = L.miejscaZagrody(D, poziom)
	local stoja = L.wZagrodzie(D, kopie, aktywny, wybor, miejsc, poza)
	local s = L.przychodS(D, stoja)
	return { poziom = poziom, miejsc = miejsc, miejsc_maks = D.zagroda.poziomy[#D.zagroda.poziomy].miejsc,
		stoja = stoja, stawka_s = s, opis = L.opisPrzychodu(D, s), cena = L.cenaUlepszenia(D, poziom),
		reczny = L.czystyWybor(D, wybor) ~= nil }
end

local function bez(lista, x)
	local w = {}
	for _, v in lista do
		if v ~= x then
			table.insert(w, v)
		end
	end
	return w
end

function L.zmienWybor(D, kopie, aktywny, wybor, wydatki, poza, id, tak)
	local st = L.stanZagrody(D, kopie, aktywny, wybor, wydatki, poza)
	local stoja = st.stoja
	local n = if type(kopie) == "table" and type(id) == "string" then kopie[id] else nil
	if L.pet(D, id) == nil or not (calkowitaNieujemna(n) and n > 0) then
		return L.czystyWybor(D, wybor), "nie_masz"
	end
	if tak then
		if id == aktywny then
			return L.czystyWybor(D, wybor), "aktywny"
		end
		if zawiera(stoja, id) then
			return stoja, "juz"
		end
		if #stoja >= st.miejsc then
			return L.czystyWybor(D, wybor), "pelna"
		end
		local w = bez(stoja, nil)
		table.insert(w, id)
		return w, "ok"
	end
	if not zawiera(stoja, id) then
		return L.czystyWybor(D, wybor), "nie_stoi"
	end
	return bez(stoja, id), "ok"
end

function L.poWyborze(D, wybor, stary, nowy)
	local w = L.czystyWybor(D, wybor)
	if w == nil then
		return nil
	end
	if not zawiera(w, nowy) then
		return w
	end
	local zamiana = type(stary) == "string" and L.pet(D, stary) ~= nil and not zawiera(w, stary)
	local wynik = {}
	for _, x in w do
		if x ~= nowy then
			table.insert(wynik, x)
		elseif zamiana then
			table.insert(wynik, stary)
		end
	end
	return wynik
end

function L.poOdstawieniu(D, wybor, stary)
	local w = L.czystyWybor(D, wybor)
	if w == nil then
		return nil
	end
	if type(stary) == "string" and L.pet(D, stary) ~= nil and not zawiera(w, stary) then
		table.insert(w, stary)
	end
	return w
end

function L.tik(D, reszta, s, dt): (number, number)
	local d = math.min(math.max(if liczba(dt) then dt else 0, 0), D.zagroda.tik_maks_s)
	local r = if liczba(reszta) and reszta >= 0 and reszta < 1 then reszta else 0
	local st = if liczba(s) and s > 0 then s else 0
	local suma = r + st * d
	local ile = math.floor(suma + 1e-9)
	return ile, math.max(0, suma - ile)
end

function L.tekstBrakuUlepszenia(D, brakuje: number, zloto: number, c: number): string
	return string.format(D.teksty.za_malo_ulepszenie, L.ileRybek(D, brakuje, "d"), zloto, c)
end

function L.rowne(a, b): boolean
	if type(a) ~= type(b) then
		return false
	end
	if type(a) == "number" then
		return math.abs(a - b) <= 1e-9
	end
	if type(a) ~= "table" then
		return a == b
	end
	for k, v in a do
		if not L.rowne(v, b[k]) then
			return false
		end
	end
	for k in b do
		if a[k] == nil then
			return false
		end
	end
	return true
end

------------------------------------------------------------------ przypadki wzorcowe (lustro w Pythonie je liczy)
function L.sprawdzPrzypadki(D)
	local P = D.przypadki
	local bledy, n = {}, 0
	local function sprawdz(nazwa: string, i: number, ok: boolean)
		n += 1
		if not ok then
			table.insert(bledy, nazwa .. " #" .. tostring(i))
		end
	end
	for i, c in P.cena do
		sprawdz("cena", i, L.cena(D, L.jajko(D, c.jajko), c.kupione, c.tryb) == c.wynik)
	end
	for i, c in P.opis_ceny do
		sprawdz("opis_ceny", i, L.opisCeny(D, L.jajko(D, c.jajko), c.tryb) == c.wynik)
	end
	for i, c in P.kupione do
		sprawdz("kupione", i, L.kupione(D, L.jajko(D, c.jajko), c.wydatki, c.tryb) == c.wynik)
	end
	for i, c in P.jajko_peta do
		local j = L.jajkoPeta(D, c.pet)
		sprawdz("jajko_peta", i, j ~= nil and j.id == c.wynik)
	end
	for i, c in P.kraina do
		local j = L.jajkoKrainy(D, c.kraina)
		sprawdz("kraina", i, (if j then j.id else nil) == c.wynik)
	end
	for i, c in P.losuj do
		sprawdz("losuj", i, L.losuj(D, L.jajko(D, c.jajko), c.r) == c.wynik)
	end
	for i, c in P.procent do
		sprawdz("procent", i, L.procent(c.szansa) == c.wynik)
	end
	for i, c in P.skill do
		local p = L.pet(D, c.pet)
		sprawdz("skill", i, p ~= nil and L.opisSkilla(D, p) == c.wynik and L.opisSkillaKrotki(D, p) == c.krotko
			and L.rowne(L.premiaPeta(D, c.pet), c.premia) and L.rowne(L.modPeta(D, c.pet), c.mod))
	end
	for i, c in P.zagroda do
		local w = L.wierszeZagrody(D, c.kopie, c.aktywny)
		local oczek = c.wynik
		if #oczek == 0 then
			sprawdz("zagroda", i, #w == 0)
		else
			sprawdz("zagroda", i, L.rowne(w, oczek))
		end
	end
	for i, c in P.decyzja do
		sprawdz("decyzja", i, L.rowne(L.decyzja(D, c.stan), c.wynik))
	end
	for i, c in P.szanse do
		sprawdz("szanse", i, L.rowne(L.wierszeSzans(D, L.jajko(D, c.jajko)), c.wynik))
	end
	-- zagroda: Rybki, miejsca, wybór (25.11.2026)
	for i, c in P.stawka do
		sprawdz("stawka", i, L.rowne(L.stawka(D, c.pet), c.wynik))
	end
	for i, c in P.poziom_zagrody do
		sprawdz("poziom_zagrody", i, L.poziomZagrody(D, c.wydatki) == c.wynik)
	end
	for i, c in P.miejsca_zagrody do
		sprawdz("miejsca_zagrody", i, L.miejscaZagrody(D, c.poziom) == c.wynik and L.cenaUlepszenia(D, c.poziom) == c.cena)
	end
	for i, c in P.opis_przychodu do
		sprawdz("opis_przychodu", i, L.opisPrzychodu(D, c.s) == c.wynik)
	end
	for i, c in P.rybki or {} do
		sprawdz("rybki", i, L.ileRybek(D, c.n) == c.m and L.ileRybek(D, c.n, "b") == c.b and L.ileRybek(D, c.n, "d") == c.d
			and L.tekstBraku(D, c.n, 7, 300) == c.brak and L.tekstBrakuUlepszenia(D, c.n, 7, 1000) == c.brakUlepszenia)
	end
	for i, c in P.stan_zagrody do
		sprawdz("stan_zagrody", i, L.rowne(L.stanZagrody(D, c.kopie, c.aktywny, c.wybor, c.wydatki, c.poza), c.wynik))
	end
	for i, c in P.zmien_wybor do
		local w, powod = L.zmienWybor(D, c.kopie, c.aktywny, c.wybor, c.wydatki, nil, c.pet, c.tak)
		sprawdz("zmien_wybor", i, L.rowne(w, c.wynik) and powod == c.powod)
	end
	for i, c in P.po_wyborze do
		sprawdz("po_wyborze", i, L.rowne(L.poWyborze(D, c.wybor, c.stary, c.nowy), c.wynik)
			and L.rowne(L.poOdstawieniu(D, c.wybor, c.stary), c.odstaw))
	end
	for i, c in P.tik do
		local ile, reszta = L.tik(D, c.r, c.s, c.dt)
		sprawdz("tik", i, ile == c.ile and L.rowne(reszta, c.reszta))
	end
	return #bledy == 0, n, bledy
end

return L
