--[[
	LogikaWskazowek — czysta logika wskazówek celu (ModuleScript Moduly/LogikaWskazowek w Workspace/WskazowkiGry).
	Lustro w Pythonie: swiat/wskazowki_gry/logika_wskazowek.py (ten sam opis stanu i te same przypadki wzorcowe —
	sprawdzPrzypadki porównuje z wynikami Pythona zapisanymi w DaneWskazowek.przypadki).

	L.krok(D, s) → nil | { id, tekst, cel }   — który krok pokazać (s: klasa, ukryte, wylaczone, miejsce, wygrane,
	                                             przegrane, ostatni, trenowal, straznik, stan_gracza, trening_wzmacnia,
	                                             poziom, bagno)
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

function L.krok(D, s)
	if s.wylaczone or not s.klasa or s.ukryte then
		return nil
	end
	local miejsce = s.miejsce or "miasto"
	local wLesie = miejsce == "las"
	if s.straznik then
		if miejsce == "za_brama" then
			return zbuduj(D, if s.bagno then "e_dalej" else "e_koniec")
		end
		return zbuduj(D, if wLesie then "e_brama" else "e_brama_miasto")
	end
	if miejsce == "za_brama" then
		miejsce = "las" -- bez Strażnika za bramę się nie wejdzie (serwer cofa) — jak w lesie
		wLesie = true
	end
	if s.ostatni == "przegrana" and not s.trenowal then
		if s.stan_gracza and s.trening_wzmacnia then
			return zbuduj(D, if wLesie then "d_trening" else "d_trening_miasto")
		end
		return zbuduj(D, if wLesie then "d_slabszy" else "a_teleport")
	end
	if (s.wygrane or 0) > 0 then
		if s.stan_gracza then
			if wLesie then
				return zbuduj(D, "c_poziomy", s.poziom)
			end
			return zbuduj(D, "c_poziomy_miasto")
		end
		return zbuduj(D, if wLesie then "c_straznik" else "c_straznik_miasto")
	end
	return zbuduj(D, if wLesie then "b_potwor" else "a_teleport")
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
