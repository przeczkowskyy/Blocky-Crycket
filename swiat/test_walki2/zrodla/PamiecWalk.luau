--[[
	PamiecWalk — co serwer pamięta o walkach gracza, żeby zdecydować o POMIJANIU (D-078). CZYSTA logika (bez usług
	Roblox; czas „teraz” podaje wywołujący), używa jej SerwerWalki2. Testy bez Studio (testy/test_odtwarzacza.py)
	wykonują ten plik interpreterem tools/walka/luau_mini.py — stąd brak metatablic i funkcji spoza podzbioru.

	D-078: pierwszą walkę z danym gatunkiem potwora gracz ogląda w całości (bez pomijania, z tempem ×1/×2/×4);
	walkę z gatunkiem, z którym już walczył, może pominąć. Decyduje SERWER: klient dostaje zgodę razem z walką
	i nie może jej sam wydać — prośba „pomiń” bez zgody serwera jest odrzucana.

	Pamięć (na razie TYLKO w pamięci serwera, jak PamiecGracza lasu-pasa): klucz = UserId gracza (przeżywa respawn
	i ponowne wejście na ten sam serwer; ginie przy restarcie serwera i przy zatrzymaniu Play). Jedna pamięć dla
	wszystkich źródeł walk: tablica prototypu (TestWalki2), las-pas (LasPasGra), stary las (LasPotwory) — gatunek
	poznany przy tablicy da się pominąć w lesie i odwrotnie. Gatunek = id przeciwnika z silnika (np. lesny_slime);
	pojedynek z postacią ma gatunek "postac:<klasa>".

	Kiedy gatunek jest „poznany”: gdy walka z nim się SKOŃCZYŁA (obejrzana albo pominięta) — czyli gdy minął jej
	koniec (pełny czas ×1 z serwera), gdy gracz ją pominął, albo gdy z tego samego źródła przyszła następna walka
	(serwer źródła wpuszcza ją dopiero po końcu poprzedniej). Przerwana walka (reset postaci) liczy się po czasie.

	API (p = PamiecWalk.nowa(); klucz = UserId; zrodlo = nazwa kontenera; teraz, koniec = czas serwera):
		przyjmij(p, klucz, zrodlo, gatunek, teraz, koniec) → pomijanie (boolean) — nowa walka; ta sama walka
		    zgłoszona drugi raz (ten sam gatunek i koniec) zwraca to samo
		czyMozna(p, klucz, zrodlo, teraz) → (boolean, powód) — powód: "ok" | "brak_walki" | "pierwsza_walka"
		pomin(p, klucz, zrodlo, teraz) → (boolean, powód) — powód jak wyżej albo "juz_pominieta"
		poznane(p, klucz, teraz) → lista gatunków (posortowana) — do testów i atrybutów
		zapomnij(p, klucz) — tylko testy (wyjście gracza pamięć ZOSTAWIA, jak PamiecGracza)

	MIEJSCE NA ZAPIS (później, gdy powstanie zapis postaci — skill roblox-data): poznane gatunki to lista napisów
	w profilu gracza; wczytać przy wejściu, oznaczyć do zapisu, gdy przybywa gatunek (patrz zamknij()).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local M = {}

function M.nowa(): any
	return { gracze = {} }
end

local function wpis(p: any, klucz: any): any
	local w = p.gracze[klucz]
	if not w then
		w = { poznane = {}, walki = {} }
		p.gracze[klucz] = w
	end
	return w
end

-- walka się skończyła: gatunek poznany (miejsce na zapis: tu oznaczyć profil do zapisu)
local function zamknij(w: any, zrodlo: string)
	local wk = w.walki[zrodlo]
	if wk then
		if wk.gatunek ~= "" then
			w.poznane[wk.gatunek] = true
		end
		w.walki[zrodlo] = nil
	end
end

local function zamknijSkonczone(w: any, teraz: number)
	local konczace = {}
	for zrodlo, wk in w.walki do
		if teraz >= wk.koniec then
			table.insert(konczace, zrodlo)
		end
	end
	for _, zrodlo in konczace do
		zamknij(w, zrodlo)
	end
end

function M.przyjmij(p: any, klucz: any, zrodlo: string, gatunek: string, teraz: number, koniec: number): boolean
	local w = wpis(p, klucz)
	local stara = w.walki[zrodlo]
	if stara and stara.gatunek == gatunek and math.abs(stara.koniec - koniec) < 0.01 then
		return stara.pomijanie
	end
	-- nowa walka z tego źródła = poprzednia się skończyła (źródło pilnuje sesji walki gracza)
	zamknij(w, zrodlo)
	zamknijSkonczone(w, teraz)
	local pomijanie = gatunek ~= "" and w.poznane[gatunek] == true
	w.walki[zrodlo] = { gatunek = gatunek, koniec = koniec, pomijanie = pomijanie, pominieta = false }
	return pomijanie
end

function M.czyMozna(p: any, klucz: any, zrodlo: string, teraz: number): (boolean, string)
	local w = p.gracze[klucz]
	if not w then
		return false, "brak_walki"
	end
	zamknijSkonczone(w, teraz)
	local wk = w.walki[zrodlo]
	if not wk then
		return false, "brak_walki"
	end
	if not wk.pomijanie then
		return false, "pierwsza_walka"
	end
	if wk.pominieta then
		return false, "juz_pominieta"
	end
	return true, "ok"
end

function M.pomin(p: any, klucz: any, zrodlo: string, teraz: number): (boolean, string)
	local ok, powod = M.czyMozna(p, klucz, zrodlo, teraz)
	if not ok then
		return false, powod
	end
	local w = p.gracze[klucz]
	w.walki[zrodlo].pominieta = true
	zamknij(w, zrodlo)
	return true, "ok"
end

function M.poznane(p: any, klucz: any, teraz: number): any
	local w = p.gracze[klucz]
	local lista = {}
	if not w then
		return lista
	end
	zamknijSkonczone(w, teraz)
	for gatunek in w.poznane do
		-- wstawianie z sortowaniem (bez table.sort — podzbiór luau_mini)
		local i = #lista + 1
		while i > 1 and lista[i - 1] > gatunek do
			lista[i] = lista[i - 1]
			i -= 1
		end
		lista[i] = gatunek
	end
	return lista
end

function M.zapomnij(p: any, klucz: any)
	p.gracze[klucz] = nil
end

return M
