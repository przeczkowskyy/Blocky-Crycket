--[[
	LogikaNpc — czysta logika postaci niezależnych (D-109; swiat/npc_gra). Bez instancji i bez usług Roblox poza
	strażnikiem: te same funkcje ma lustro w Pythonie (swiat/npc_gra/logika_npc.py), a test bez Studio wykonuje ten
	plik interpreterem i porównuje wyniki. Używa tylko math.floor / abs / min / max.

		L.tryb(odl, obecny, Z)            → "brak" | "uspiony" | "daleko" | "blisko"   (odl = nil: gracza nie ma)
		L.co_ile(tryb)                    → co ile klatek liczyć pozę (0 = wcale)
		L.nowy_stan(los, C)               → stan zachowania jednego NPC
		L.krok(stan, odl, dt, los, D, n)  → nil | "powitanie" | "gest" | "spoczynek"   (zmienia stan)
		L.wymus(stan, rola, n)            → true/false: klip „powitanie” / „gest” / „spoczynek” na polecenie
		L.wzrok(kat, pochyl, poziom, W)   → skręt tułowia, skręt głowy, pochylenie głowy (radiany)
		L.wygladz(a, cel, dt, tempo)      → a bliżej celu
		L.klatka(t, fps, n, petla)        → i0, i1, a   (numery klatek od 0 i udział drugiej)
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local function ogranicz(x, a, b)
	return math.max(a, math.min(b, x))
end

-- Stopień szczegółów jednego NPC z odległości gracza. Histereza: budowa ≤ Z.budowa, usunięcie > Z.usuniecie,
-- ruch ≤ Z.animacja, uśpienie > Z.uspienie; „blisko” (≤ Z.blisko) zmienia tylko częstość liczenia pozy.
function L.tryb(odl, obecny, Z)
	if odl == nil then
		return if obecny == "brak" then "brak" else "uspiony"
	end
	if obecny == "brak" then
		if odl > Z.budowa then
			return "brak"
		end
	elseif odl > Z.usuniecie then
		return "brak"
	end
	local rusza = obecny == "daleko" or obecny == "blisko"
	if rusza then
		if odl > Z.uspienie then
			return "uspiony"
		end
	elseif odl > Z.animacja then
		return "uspiony"
	end
	return if odl <= Z.blisko then "blisko" else "daleko"
end

function L.co_ile(tryb)
	if tryb == "blisko" then
		return 1
	elseif tryb == "daleko" then
		return 2
	end
	return 0
end

function L.nowy_stan(los, C)
	return {
		klip = "spoczynek",
		zostalo = 0,
		do_gestu = C.gest_min_s + los * (C.gest_max_s - C.gest_min_s),
		powitany = false,
		od_powitania = C.powitanie_odstep_s,
	}
end

-- Jeden krok zachowania. odl = odległość gracza (nil: brak gracza), los = liczba 0…1 na następny odstęp gestu,
-- n = wpis NPC z danych (dlugosci klipów w sekundach).
function L.krok(stan, odl, dt, los, D, n)
	local Z, C = D.zasiegi, D.czasy
	stan.od_powitania = math.min(stan.od_powitania + dt, C.powitanie_odstep_s)
	if stan.klip ~= "spoczynek" then
		stan.zostalo -= dt
		if stan.zostalo <= 0 then
			stan.klip = "spoczynek"
			stan.zostalo = 0
			return "spoczynek"
		end
		return nil
	end
	if odl == nil then
		return nil
	end
	if odl > Z.pozegnanie then
		stan.powitany = false
	elseif odl <= Z.powitanie and not stan.powitany then
		stan.powitany = true
		if stan.od_powitania >= C.powitanie_odstep_s then
			stan.od_powitania = 0
			stan.klip = "powitanie"
			stan.zostalo = n.dlugosci.powitanie
			return "powitanie"
		end
	end
	if odl <= Z.gest then
		stan.do_gestu -= dt
		if stan.do_gestu <= 0 then
			stan.do_gestu = C.gest_min_s + los * (C.gest_max_s - C.gest_min_s)
			stan.klip = "gest"
			stan.zostalo = n.dlugosci.gest
			return "gest"
		end
	end
	return nil
end

-- Klip na polecenie (mini-gra, próba): „gest” i „powitanie” grają raz i wracają do spoczynku.
function L.wymus(stan, rola, n)
	if rola == "spoczynek" then
		stan.klip = "spoczynek"
		stan.zostalo = 0
		return true
	elseif rola == "gest" or rola == "powitanie" then
		stan.klip = rola
		stan.zostalo = n.dlugosci[rola]
		return true
	end
	return false
end

-- kat = kąt gracza w poziomie względem przodu NPC (radiany, + = w lewo NPC), pochyl = kąt w pionie do głowy gracza,
-- poziom = odległość w poziomie. Gracz za plecami albo za daleko → patrzy przed siebie.
function L.wzrok(kat, pochyl, poziom, W)
	if poziom > W.zasieg or poziom < 0.05 or math.abs(kat) > W.za_plecami then
		return 0, 0, 0
	end
	local tulow = ogranicz(kat * W.tulow_udzial, -W.tulow_maks, W.tulow_maks)
	local glowa = ogranicz(kat - tulow, -W.glowa_maks, W.glowa_maks)
	return tulow, glowa, ogranicz(pochyl, -W.pochyl_maks, W.pochyl_maks)
end

function L.wygladz(a, cel, dt, tempo)
	return a + (cel - a) * math.min(1, tempo * dt)
end

-- Miejsce w klipie o n klatkach (co 1/fps s): numery klatek od 0 i udział drugiej; klip bez pętli staje na końcu.
function L.klatka(t, fps, n, petla)
	local ost = n - 1
	if ost <= 0 then
		return 0, 0, 0
	end
	local f = t * fps
	if petla then
		f = f - math.floor(f / ost) * ost
	elseif f >= ost then
		return ost, ost, 0
	end
	if f < 0 then
		f = 0
	end
	local i0 = math.floor(f)
	return i0, math.min(i0 + 1, ost), f - i0
end

return L
