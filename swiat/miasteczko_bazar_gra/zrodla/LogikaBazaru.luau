--[[
	LogikaBazaru — czysta logika pakietu „miasteczko-bazar w grze” (ModuleScript Moduly/LogikaBazaru w kontenerze
	Workspace/MiasteczkoBazarGra). Bez instancji Roblox: te same funkcje ma lustro w Pythonie
	(swiat/miasteczko_bazar_gra/logika_bazaru.py), a przypadki wzorcowe z lustra są w DaneBazaru.przypadki —
	SerwerBazaru sprawdza je przy starcie (atrybut ZgodnoscLogikiBazaru), a test offline wykonuje ten plik
	interpreterem tools/walka/luau_mini.py.

	Tylko podzbiór biblioteki, który ma luau_mini: math.floor/ceil/abs/sqrt/min/max, string.format/sub/find (zwykły),
	table.insert, type, tostring, pcall, error; iteracja `for k, v in t do`; bez typeof, ipairs, table.sort.

	decyzja(D, id, s, teraz, swiat) → co zrobić po E gracza w miejscu id:
		{ akcja = "okno", id }                      — okno 2D (klient: OknoMiejsca, sygnał HUD, ewentualnie dymek)
		{ akcja = "dymek", id, tekst, powod }       — krótki dymek w świecie (odmowa albo „zamknięte”)
		{ akcja = "chmury", id }                    — przejście przez chmury (klient: TeleportChmury/Otworz)
		{ akcja = "las", id }                       — serwer przenosi uchwytem LasPasGra/Sygnaly/PrzeniesDoLasu
		{ akcja = "nic", powod }                    — za daleko / za szybko po poprzednim E / nieznane miejsce
	(do 26.11.2026 była też akcja „przenies” — przejścia stare ↔ nowe miasteczko; stare miasteczko zniknęło z miejsca)
	swiat = { odleglosc = st od podpowiedzi (nil = nie sprawdzaj), chmury, las, poziom }
	s (stan gracza, zmieniany): { ostatnieE, ostatniePrzejscie, wTrakcie, lochy }
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local NIGDY = -1e9

function L.nowyStan()
	return { ostatnieE = NIGDY, ostatniePrzejscie = NIGDY, wTrakcie = false, lochy = false }
end

function L.kopia(t)
	local k = {}
	for a, b in t do
		k[a] = b
	end
	return k
end

------------------------------------------------------------------ decyzja po E
function L.lochyOtwarte(D, s, poziom): boolean
	if s.lochy == true then
		return true
	end
	local wym = D.lochy.wymagany_poziom
	return wym ~= nil and type(poziom) == "number" and poziom >= wym
end

function L.tekstOdmowy(D, powod, zostalo): string
	local t = D.teksty[powod] or D.teksty.blad
	if powod == "za_szybko" then
		return string.format(t, math.max(1, math.ceil(zostalo or 0)))
	end
	return t
end

function L.decyzja(D, id, s, teraz, swiat)
	local m = D.miejsca[id]
	if m == nil then
		return { akcja = "nic", powod = "nieznane_miejsce" }
	end
	local odl = swiat.odleglosc
	if odl ~= nil and odl > m.zasieg + D.podpowiedz.zapas then
		return { akcja = "nic", powod = "za_daleko" }
	end
	if teraz - s.ostatnieE < D.czasy.odstep_e_s then
		return { akcja = "nic", powod = "spam" }
	end
	s.ostatnieE = teraz
	local a = m.akcja
	if a == "okno" then
		return { akcja = "okno", id = id }
	end
	if a == "lochy" then
		if L.lochyOtwarte(D, s, swiat.poziom) then
			return { akcja = "okno", id = id }
		end
		return { akcja = "dymek", id = id, tekst = m.dymek, powod = "zamkniete" }
	end
	if a == "chmury" then
		if not swiat.chmury then
			return { akcja = "dymek", id = id, tekst = m.dymek, powod = "brak_chmur" }
		end
		return { akcja = "chmury", id = id }
	end
	if a == "las" then
		if s.wTrakcie then
			return { akcja = "dymek", id = id, tekst = L.tekstOdmowy(D, "trwa"), powod = "trwa" }
		end
		local zostalo = s.ostatniePrzejscie + D.czasy.odstep_przejsc_s - teraz
		if zostalo > 0 then
			return { akcja = "dymek", id = id, tekst = L.tekstOdmowy(D, "za_szybko", zostalo), powod = "za_szybko" }
		end
		if not swiat.las then
			return { akcja = "dymek", id = id, tekst = L.tekstOdmowy(D, "brak_lasu"), powod = "brak_lasu" }
		end
		return { akcja = a, id = id }
	end
	return { akcja = "nic", powod = "nieznana_akcja" }
end

-- blokada czasu przejść: w trakcie nikt nie przenosi drugi raz, po udanym przejściu odstep_przejsc_s przerwy
function L.poczatekPrzejscia(s)
	s.wTrakcie = true
end

function L.koniecPrzejscia(s, ok, teraz)
	s.wTrakcie = false
	if ok then
		s.ostatniePrzejscie = teraz
	end
end

------------------------------------------------------------------ dymek „okno w budowie” (klient)
function L.przytnij(t: string): string
	local a, b = 1, #t
	while a <= b and string.sub(t, a, a) == " " do
		a += 1
	end
	while b >= a and string.sub(t, b, b) == " " do
		b -= 1
	end
	return string.sub(t, a, b)
end

-- czy id jest na liście „a,b, c” (atrybut BezDymku)
function L.naLiscie(lista, id): boolean
	if type(lista) ~= "string" or type(id) ~= "string" then
		return false
	end
	local poz = 1
	while poz <= #lista + 1 do
		local k = string.find(lista, ",", poz, true)
		local koniec = if k then k - 1 else #lista
		if L.przytnij(string.sub(lista, poz, koniec)) == id then
			return true
		end
		if not k then
			break
		end
		poz = k + 1
	end
	return false
end

-- dymek tylko wtedy, gdy po E nic się nie otworzyło, okno nie zgłosiło się atrybutem i dymki nie są wyłączone
function L.dymekOkna(id, otwarto, zgloszone, wylaczone, bez): boolean
	if otwarto or zgloszone == true or wylaczone == true then
		return false
	end
	return not L.naLiscie(bez, id)
end

------------------------------------------------------------------ tablica z rankingiem
local function przed(a, b): boolean
	local pa = if a.poziom ~= nil then a.poziom else -1
	local pb = if b.poziom ~= nil then b.poziom else -1
	if pa ~= pb then
		return pa > pb
	end
	local xa = if a.xp ~= nil then a.xp else 0
	local xb = if b.xp ~= nil then b.xp else 0
	if xa ~= xb then
		return xa > xb
	end
	local ma = if a.moc ~= nil then a.moc else 0
	local mb = if b.moc ~= nil then b.moc else 0
	if ma ~= mb then
		return ma > mb
	end
	return a.nazwa < b.nazwa
end

-- gracze: { { nazwa, poziom?, xp?, moc? } } → najwyżej n wierszy { miejsce, nazwa, poziom?, xp?, moc? }
function L.ranking(gracze, n)
	local t = {}
	for i, g in gracze do
		t[i] = g
	end
	for i = 2, #t do
		local v = t[i]
		local j = i - 1
		while j >= 1 and przed(v, t[j]) do
			t[j + 1] = t[j]
			j -= 1
		end
		t[j + 1] = v
	end
	local wynik = {}
	for i = 1, math.min(#t, n) do
		local g = t[i]
		table.insert(wynik, { miejsce = i, nazwa = g.nazwa, poziom = g.poziom, xp = g.xp, moc = g.moc })
	end
	return wynik
end

function L.liczba(x): string
	if x == nil then
		return "—"
	end
	if x == math.floor(x) then
		return string.format("%d", x)
	end
	return string.format("%.1f", x)
end

function L.wiersz(w): string
	return string.format("%d. %s — poz. %s · moc %s", w.miejsce, w.nazwa, L.liczba(w.poziom), L.liczba(w.moc))
end

------------------------------------------------------------------ zgodność z lustrem w Pythonie
function L.rowne(a, b): boolean
	if type(a) == "number" and type(b) == "number" then
		return math.abs(a - b) <= 1e-6
	end
	if type(a) ~= type(b) then
		return false
	end
	if type(a) ~= "table" then
		return a == b
	end
	for k, v in a do
		if not L.rowne(v, b[k]) then
			return false
		end
	end
	for k, _ in b do
		if a[k] == nil then
			return false
		end
	end
	return true
end

function L.wykonajPrzypadek(D, p)
	if p.f == "decyzja" then
		local s = L.kopia(p.stan)
		return L.decyzja(D, p.id, s, p.teraz, p.swiat), s
	elseif p.f == "sekwencja" then
		local s = L.nowyStan()
		local wyniki = {}
		for _, k in p.kroki do
			if k.typ == "e" then
				table.insert(wyniki, L.decyzja(D, k.id, s, k.teraz, k.swiat))
			elseif k.typ == "poczatek" then
				L.poczatekPrzejscia(s)
				table.insert(wyniki, { krok = "poczatek" })
			else
				L.koniecPrzejscia(s, k.ok, k.teraz)
				table.insert(wyniki, { krok = "koniec" })
			end
		end
		return wyniki, s
	elseif p.f == "tekst" then
		return L.tekstOdmowy(D, p.powod, p.zostalo), nil
	elseif p.f == "ranking" then
		return L.ranking(p.gracze, p.n), nil
	elseif p.f == "wiersz" then
		return L.wiersz(p.w), nil
	elseif p.f == "dymek" then
		return L.dymekOkna(p.id, p.otwarto, p.zgloszone, p.wylaczone, p.bez), nil
	end
	error("nieznany rodzaj przypadku: " .. tostring(p.f))
end

-- → (wszystko zgodne, liczba przypadków, lista opisów niezgodnych)
function L.sprawdzPrzypadki(D)
	local bledy = {}
	local n = 0
	for _, p in D.przypadki do
		n += 1
		local ok, w, s = pcall(L.wykonajPrzypadek, D, p)
		if not ok then
			table.insert(bledy, tostring(p.opis) .. ": błąd " .. tostring(w))
		elseif not L.rowne(w, p.wynik) then
			table.insert(bledy, tostring(p.opis))
		elseif p.stan_po ~= nil and not L.rowne(s, p.stan_po) then
			table.insert(bledy, tostring(p.opis) .. " (stan)")
		end
	end
	return #bledy == 0, n, bledy
end

return L
