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
		opisCeny(D, jajko, tryb?)                 → „cena: 300 Złota” albo „od 300 Złota · rośnie z każdym jajkiem”
		losuj(D, jajko, r)                        → id peta (r ∈ [0, 1), jawne szanse po kolei)
		procent(szansa), opisSkilla(D, pet), premiaPeta(D, id), tekstBraku(D, brakuje, zloto, cena)
		wierszeSzans(D, jajko), wierszeZagrody(D, kopie, aktywny), decyzja(D, stan), czasWyklucia(D)
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

function L.opisCeny(D, j, tryb): string
	local T = D.teksty
	local t = tryb or j.cena.tryb
	if t == "rosnaca" then
		return string.format(T.cena_od, L.cena(D, j, 0, t)) .. " · " .. T.rosnie
	end
	return string.format(T.cena_tablica, L.cena(D, j, 0, t))
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

function L.opisSkilla(D, p): string
	local s = p.skill
	local T = D.teksty
	local z = math.floor(s.zloto * 100 + 0.5)
	local x = math.floor(s.doswiadczenie * 100 + 0.5)
	if z > 0 and x > 0 and z == x then
		return string.format(T.skill_oba, z)
	end
	if z > 0 and x > 0 then
		return string.format(T.skill_zloto, z) .. ", " .. string.format(T.skill_xp, x)
	end
	if z > 0 then
		return string.format(T.skill_zloto, z)
	end
	return string.format(T.skill_xp, x)
end

function L.premiaPeta(D, id)
	local p = L.pet(D, id)
	if not p then
		return { zloto = 0, doswiadczenie = 0 }
	end
	return { zloto = p.skill.zloto, doswiadczenie = p.skill.doswiadczenie }
end

function L.tekstBraku(D, brakuje: number, zloto: number, c: number): string
	return string.format(D.teksty.za_malo, brakuje, zloto, c)
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
				skill = L.opisSkilla(D, p), aktywny = p.id == aktywny, jajko = p.jajko })
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
		sprawdz("skill", i, p ~= nil and L.opisSkilla(D, p) == c.wynik and L.rowne(L.premiaPeta(D, c.pet), c.premia))
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
	return #bledy == 0, n, bledy
end

return L
