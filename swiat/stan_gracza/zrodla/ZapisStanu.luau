--[[
	ZapisStanu — zapis postępu gracza między sesjami (ModuleScript w Workspace/StanGracza/Moduly; używa go tylko
	SerwerStanu). 18.11.2026, propozycja: DOMYŚLNIE WYŁĄCZONY (D.zapis.wlaczony = false; atrybut kontenera
	D.zapis.atrybut = true włącza). Zasady: skill projektu roblox-data.

	Rekord w DataStore pod kluczem D.zapis.klucz .. UserId (identyfikator gracza jako stały kawałek klucza — usuwanie
	danych na żądanie):
		{ profil = LogikaStanu.profilDoZapisu(…) | nil, sesja = { serwer = żeton serwera, czas = os.time() } | nil,
		  zapisano = os.time() }
	Wszystko przez UpdateAsync (odczyt-zmiana-zapis w jednym kroku; bez osobnego odczytu i jego 4-sekundowej pamięci podręcznej).
	Przekształcenia nie czekają i nie zmieniają niczego poza zwracanym rekordem (mogą zostać wywołane kilka razy).

	Blokada sesji: wczytanie bierze rekord tylko, gdy nie ma sesji, sesja jest tego serwera albo przeterminowana
	(starsza niż D.zapis.blokada_s — serwer padł). Świeża cudza sesja: czekamy D.zapis.czekaj_blokada_s i próbujemy
	jeszcze D.zapis.proby_blokady razy (stary serwer zwykle właśnie zapisuje wyjście gracza); potem „zajety” — gracz gra
	w pamięci BEZ zapisu (nie przejmujemy cudzej świeżej sesji — to cofnęłoby jej postęp). Każdy zapis odświeża czas
	sesji; zapis, który zastanie cudzą sesję, NIE pisze („utracona_blokada”) i ten serwer przestaje zapisywać gracza.

	Błędy: każde wywołanie w pcall; błąd usługi → ponowienie po D.zapis.odstep_s × 2^(n−1) (+ rozrzut), najwyżej
	D.zapis.proby razy. Studio bez dostępu do usług danych (StudioAccessToApisNotAllowed) → zapis wyłącza się do końca
	sesji serwera, gra działa w pamięci. Zły / za duży / przyszły profil przy wczytaniu → odmowa bez zmiany rekordu
	(gracz dostaje świeży profil w pamięci i nie jest zapisywany, więc stary rekord zostaje nietknięty).

	Z.nowy(D, L, srodowisko) → obiekt { wczytaj, zapisz, wylaczony, powod }
		srodowisko = { magazyn (DataStore albo atrapa), zeton, teraz() → s (os.time), opoznij(s, fn), log(tekst),
		               budzet() → liczba albo nil, los() → 0..1 }
		wczytaj(userId, gotowe(stan, profil?, powod)) — stan: "ok" | "nowy" | "zajety" | "zepsuty" | "blad" |
		                                               "brak_dostepu" | "wylaczony"
		zapisz(userId, profil | nil, zwolnij, gotowe(ok, powod)) — profil nil: tylko zwolnienie / odświeżenie sesji
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Z = {}

local function brakDostepu(blad: any): boolean
	local t = tostring(blad)
	return string.find(t, "StudioAccessToApisNotAllowed", 1, true) ~= nil
		or string.find(t, "API Services", 1, true) ~= nil
end

function Z.nowy(D, L, S)
	local o = { wylaczony = false, powod = nil }
	local G = D.zapis

	local function klucz(userId: number): string
		return G.klucz .. tostring(userId)
	end

	local function odstep(n: number): number
		return G.odstep_s * 2 ^ (n - 1) + (if S.los then S.los() * 0.25 else 0)
	end

	local function wylacz(powod: string)
		if not o.wylaczony then
			o.wylaczony = true
			o.powod = powod
			S.log("zapis wyłączony do końca sesji serwera: " .. powod .. " — gra działa w pamięci")
		end
	end

	-- wywołanie UpdateAsync z bramką budżetu zapytań; → ok, wynik
	local function aktualizuj(k: string, przeksztalc)
		return pcall(function()
			return S.magazyn:UpdateAsync(k, przeksztalc)
		end)
	end

	function o.wczytaj(userId: number, gotowe)
		local k = klucz(userId)
		local function proba(n: number, blokada: number)
			if o.wylaczony then
				gotowe("wylaczony", nil, o.powod)
				return
			end
			local budzet = if S.budzet then S.budzet() else nil -- nil: nie wiadomo — idziemy
			if budzet ~= nil and budzet < G.budzet_min and n <= G.proby then
				S.opoznij(1, function()
					proba(n + 1, blokada)
				end)
				return
			end
			local wynik, profil, powod = nil, nil, nil
			local teraz = S.teraz()
			local ok, blad = aktualizuj(k, function(stary)
				wynik, profil, powod = nil, nil, nil
				if stary ~= nil and type(stary) ~= "table" then
					wynik, powod = "zepsuty", "zly_rekord"
					return nil
				end
				local rekord = stary or {}
				local sesja = rekord.sesja
				if type(sesja) == "table" and sesja.serwer ~= S.zeton and type(sesja.czas) == "number"
					and teraz - sesja.czas < G.blokada_s then
					wynik, powod = "zajety", "swieza_sesja"
					return nil
				end
				if rekord.profil == nil then
					wynik = "nowy"
				else
					local m, pm = L.migrujProfil(D, rekord.profil)
					if m == nil then
						wynik, powod = "zepsuty", pm
						return nil
					end
					local c, pc = L.czystyProfil(D, m)
					if c == nil then
						wynik, powod = "zepsuty", pc
						return nil
					end
					wynik, profil = "ok", c
				end
				-- bierzemy sesję; profil zostaje taki, jak był (zapisze go dopiero zapis — bez zapisu częściowego)
				return { profil = rekord.profil, sesja = { serwer = S.zeton, czas = teraz }, zapisano = rekord.zapisano }
			end)
			if not ok then
				if brakDostepu(blad) then
					wylacz("brak dostępu do usług danych (Studio: ustawienia gry)")
					gotowe("brak_dostepu", nil, tostring(blad))
					return
				end
				if n < G.proby then
					S.opoznij(odstep(n), function()
						proba(n + 1, blokada)
					end)
				else
					S.log(string.format("wczytanie %s nie powiodło się po %d próbach: %s", k, n, tostring(blad)))
					gotowe("blad", nil, tostring(blad))
				end
				return
			end
			if wynik == "zajety" then
				if blokada < G.proby_blokady then
					S.opoznij(G.czekaj_blokada_s, function()
						proba(n, blokada + 1)
					end)
				else
					S.log(k .. ": profil używa inny serwer (świeża sesja) — gracz gra bez zapisu")
					gotowe("zajety", nil, powod)
				end
				return
			end
			if wynik == "zepsuty" then
				S.log(k .. ": zapisany profil odrzucony (" .. tostring(powod) .. ") — świeży profil w pamięci, rekord nietknięty")
				gotowe("zepsuty", nil, powod)
				return
			end
			gotowe(wynik, profil, nil)
		end
		proba(1, 0)
	end

	function o.zapisz(userId: number, profil, zwolnij: boolean, gotowe)
		local k = klucz(userId)
		if profil ~= nil then
			local c, pc = L.czystyProfil(D, profil)
			if c == nil then
				S.log(k .. ": profil do zapisu odrzucony (" .. tostring(pc) .. ") — nic nie zapisano")
				gotowe(false, pc)
				return
			end
			profil = c
		end
		local function proba(n: number)
			if o.wylaczony then
				gotowe(false, "wylaczony")
				return
			end
			local budzet = if S.budzet then S.budzet() else nil -- nil: nie wiadomo — idziemy
			if budzet ~= nil and budzet < G.budzet_min and n <= G.proby then
				S.opoznij(1, function()
					proba(n + 1)
				end)
				return
			end
			local powod = nil
			local teraz = S.teraz()
			local ok, wynik = aktualizuj(k, function(stary)
				powod = nil
				if stary ~= nil and type(stary) ~= "table" then
					powod = "zly_rekord"
					return nil
				end
				local rekord = stary or {}
				local sesja = rekord.sesja
				if type(sesja) == "table" and sesja.serwer ~= S.zeton then
					powod = "utracona_blokada"
					return nil
				end
				if type(rekord.profil) == "table" and type(rekord.profil.wersja) == "number"
					and rekord.profil.wersja > D.wersja_profilu then
					powod = "przyszla_wersja"
					return nil
				end
				return { profil = if profil ~= nil then profil else rekord.profil,
					sesja = if zwolnij then nil else { serwer = S.zeton, czas = teraz }, zapisano = teraz }
			end)
			if not ok then
				if brakDostepu(wynik) then
					wylacz("brak dostępu do usług danych (Studio: ustawienia gry)")
					gotowe(false, "brak_dostepu")
					return
				end
				if n < G.proby then
					S.opoznij(odstep(n), function()
						proba(n + 1)
					end)
				else
					S.log(string.format("zapis %s nie powiódł się po %d próbach: %s", k, n, tostring(wynik)))
					gotowe(false, "blad")
				end
				return
			end
			if wynik == nil then
				S.log(k .. ": zapis odmówiony (" .. tostring(powod) .. ")")
				gotowe(false, powod or "odmowa")
				return
			end
			gotowe(true, nil)
		end
		proba(1)
	end

	return o
end

return Z
