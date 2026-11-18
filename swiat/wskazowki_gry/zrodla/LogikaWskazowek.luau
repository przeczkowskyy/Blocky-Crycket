--[[
	LogikaWskazowek — czysta logika wskazówek celu (ModuleScript Moduly/LogikaWskazowek w Workspace/WskazowkiGry).
	Lustro w Pythonie: swiat/wskazowki_gry/logika_wskazowek.py (ten sam opis stanu i te same przypadki wzorcowe —
	sprawdzPrzypadki porównuje z wynikami Pythona zapisanymi w DaneWskazowek.przypadki).

	L.krok(D, s) → nil | { id, tekst, cel }   — który krok pokazać (s: klasa, ukryte, wylaczone, kraina, miejsce, wygrane,
	                                             przegrane, ostatni, trenowal, straznik, straznik_bagna, straznik_dzungli,
	                                             stan_gracza, trening_wzmacnia, poziom, bagno, dzungla, jajko, kupione,
	                                             kowal, kowal_zapas, kowal_ulepsz,
	                                             kowal_ulepszen); krok „kowal” tylko zamiast c_* (18.11.2026)
	L.miejsce(x, z, prostokat, bramaX) → "las" | "za_brama" | "miasto"
	L.wynikWalki(napis) → "wygrana" | "przegrana" | nil
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local function zbuduj(D, kid, poziom)
	local k = D.kroki[kid]
	local tekst = k.tekst
	local i, j = string.find(tekst, "%d", 1, true) -- dane.py pilnuje: najwyżej jedno %d w tekście
	if i then
		local wartosc = "?"
		if type(poziom) == "number" then
			wartosc = tostring(math.floor(poziom))
		end
		tekst = string.sub(tekst, 1, i - 1) .. wartosc .. string.sub(tekst, j + 1)
	end
	return { id = kid, tekst = tekst, cel = k.cel }
end

-- kroki „zdobywaj poziomy / Strażnik czeka” każdego biomu (las bez przyrostka)
local C_POZIOMY = { las = "c_poziomy", bagno = "c_poziomy_bagno", dzungla = "c_poziomy_dzungla" }
local C_STRAZNIK = { las = "c_straznik", bagno = "c_straznik_bagno", dzungla = "c_straznik_dzungla" }

-- w biomie przed jego Strażnikiem (liczniki walk osobno dla każdego biomu)
local function postep(D, s, kraina)
	if s.ostatni == "przegrana" and not s.trenowal then
		if s.stan_gracza and s.trening_wzmacnia then
			return zbuduj(D, "d_trening")
		end
		return zbuduj(D, "d_slabszy")
	end
	if (s.wygrane or 0) > 0 then
		if s.stan_gracza then
			return zbuduj(D, C_POZIOMY[kraina] or "c_poziomy", s.poziom)
		end
		return zbuduj(D, C_STRAZNIK[kraina] or "c_straznik")
	end
	return zbuduj(D, "b_potwor")
end

local function miasto(D, s)
	if s.straznik then
		if s.straznik_bagna and s.dzungla then
			return zbuduj(D, "e_dzungla_miasto")
		end
		return zbuduj(D, if s.bagno then "e_bagno_miasto" else "e_brama_miasto")
	end
	if s.ostatni == "przegrana" and not s.trenowal then
		if s.stan_gracza and s.trening_wzmacnia then
			return zbuduj(D, "d_trening_miasto")
		end
		return zbuduj(D, "a_teleport")
	end
	if (s.wygrane or 0) > 0 then
		return zbuduj(D, if s.stan_gracza then "c_poziomy_miasto" else "c_straznik_miasto")
	end
	return zbuduj(D, "a_teleport")
end

local function glowny(D, s)
	if s.wylaczone or not s.klasa or s.ukryte then
		return nil
	end
	local miejsce = s.miejsce or "miasto"
	local kraina = s.kraina
	if kraina == nil and (miejsce == "las" or miejsce == "za_brama") then
		kraina = "las"
	end
	-- pierwsze jajko biomu (swiat/pety_proba): Złota wystarcza na jajko biomu, w którym jest gracz (w mieście: lasu),
	-- a gracz nie kupił jeszcze jajka tego biomu; nie za bramą
	if s.jajko and (s.kupione or 0) == 0 and miejsce ~= "za_brama" then
		if miejsce == "miasto" or kraina == nil then
			return zbuduj(D, "f_jajko_miasto")
		end
		return zbuduj(D, if kraina == "bagno" then "f_jajko_bagno" elseif kraina == "dzungla" then "f_jajko_dzungla"
			else "f_jajko")
	end
	if miejsce == "miasto" or kraina == nil then
		return miasto(D, s)
	end
	if kraina == "dzungla" then
		if s.straznik_dzungli then
			return zbuduj(D, if miejsce == "za_brama" then "e_koniec_dzungla" else "e_brama_pustynia")
		end
		return postep(D, s, "dzungla") -- za bramą Dżungli bez Węża serwer cofa — jak w Bagnie
	end
	if kraina == "bagno" then
		if s.straznik_bagna then
			if miejsce == "za_brama" then
				return zbuduj(D, if s.dzungla then "e_dalej_dzungla" else "e_koniec_bagno")
			end
			return zbuduj(D, if s.dzungla then "e_brama_do_dzungli" else "e_brama_dzungla")
		end
		return postep(D, s, "bagno") -- za bramą Bagna bez Strażnika serwer cofa — jak w Bagnie
	end
	if s.straznik then
		if miejsce == "za_brama" then
			return zbuduj(D, if s.bagno then "e_dalej" else "e_koniec")
		end
		return zbuduj(D, if s.bagno then "e_brama_bagno" else "e_brama")
	end
	return postep(D, s, "las") -- za bramą lasu bez Strażnika serwer cofa — jak w lesie
end

-- kowal na próbę (swiat/kowal_proba, 18.11.2026): zapas do rozbiórki albo Złoto i materiały na ulepszenie — tylko
-- zamiast „zdobywaj poziomy / Strażnik czeka” (c_*), do pierwszego ulepszenia; nigdy nie przykrywa TELEPORT, pierwszej
-- walki, jajka, treningu po przegranej ani bramy
function L.krok(D, s)
	local w = glowny(D, s)
	if w == nil or string.sub(w.id, 1, 2) ~= "c_" or not s.kowal or (s.kowal_ulepszen or 0) > 0 then
		return w
	end
	if not (s.kowal_zapas or s.kowal_ulepsz) then
		return w
	end
	local kid = if s.kowal_zapas then "g_kowal_zapas" else "g_kowal_ulepsz"
	if (s.miejsce or "miasto") ~= "miasto" then
		kid = kid .. "_las"
	end
	return zbuduj(D, kid)
end

function L.miejsce(x, z, prostokat, bramaX)
	if not prostokat then
		return "miasto"
	end
	if not (prostokat.x1 <= x and x <= prostokat.x2 and prostokat.z1 <= z and z <= prostokat.z2) then
		return "miasto"
	end
	if bramaX ~= nil and x > bramaX then
		return "za_brama"
	end
	return "las"
end

function L.wynikWalki(napis)
	if napis == "wygrana" or napis == "przegrana" then
		return napis
	end
	return nil
end

-- przypadki wzorcowe z danych (wyniki policzone w Pythonie) → ok, liczba, lista błędów
function L.sprawdzPrzypadki(D)
	local bledy = {}
	local n = 0
	for _, p in D.przypadki.kroki do
		n += 1
		local w = L.krok(D, p.stan)
		local id = w and w.id
		local tekst = w and w.tekst
		local cel = w and w.cel
		if id ~= p.id or tekst ~= p.tekst or cel ~= p.cel then
			table.insert(bledy, p.opis .. ": " .. tostring(id) .. " ≠ " .. tostring(p.id))
		end
	end
	for _, p in D.przypadki.miejsca do
		n += 1
		local w = L.miejsce(p.x, p.z, p.prostokat, p.brama)
		if w ~= p.wynik then
			table.insert(bledy, string.format("miejsce (%s; %s): %s ≠ %s", tostring(p.x), tostring(p.z), w, p.wynik))
		end
	end
	return #bledy == 0, n, bledy
end

return L
