--[[
	PamiecGracza — co serwer pamięta o graczu w lesie-pasie (ModuleScript; używa go tylko SerwerPasa).

	Na razie TYLKO w pamięci serwera (tabela według UserId): przeżywa respawn i ponowne wejście na ten sam serwer,
	ginie przy restarcie serwera i przy zatrzymaniu Play. Klucze:
		widzialPrzelotLasu    — przelot kamery przy pierwszym wejściu już był (D-077)
		pokonalStraznikaLasu  — gracz pokonał Strażnika Gaju: brama do Bagna jest dla niego otwarta

	MIEJSCE NA ZAPIS (później, gdy powstanie zapis postaci — skill roblox-data, ProfileStore / DataStore):
		• wczytaj(gracz) — dziś nic nie robi; tu wczytać oba klucze z profilu gracza (PlayerAdded, przed pierwszym
		  odczytem; do tego czasu czytaj() zwraca false, więc przelot i brama zachowują się jak dla nowego gracza);
		• po ustaw() — dziś tylko pamięć; tu oznaczyć profil do zapisu (zapis robi system profili, nie ten moduł);
		• zapomnijGracza(gracz) przy PlayerRemoving zostawia dane (ponowne wejście na ten sam serwer pamięta stan).
	Reszta pakietu woła tylko czytaj / ustaw, więc zamiana pamięci na zapis nie zmienia SerwerPasa.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Pamiec = {}

local KLUCZE = { widzialPrzelotLasu = true, pokonalStraznikaLasu = true }
local dane: { [number]: { [string]: boolean } } = {}

local function wpis(gracz: Player)
	local w = dane[gracz.UserId]
	if not w then
		w = {}
		dane[gracz.UserId] = w
	end
	return w
end

-- miejsce na wczytanie z zapisu (dziś nic)
function Pamiec.wczytaj(_gracz: Player)
	return true
end

function Pamiec.czytaj(gracz: Player, klucz: string): boolean
	if not KLUCZE[klucz] then
		error("PamiecGracza: nieznany klucz " .. tostring(klucz))
	end
	local w = dane[gracz.UserId]
	return w ~= nil and w[klucz] == true
end

function Pamiec.ustaw(gracz: Player, klucz: string, wartosc: boolean)
	if not KLUCZE[klucz] then
		error("PamiecGracza: nieznany klucz " .. tostring(klucz))
	end
	wpis(gracz)[klucz] = if wartosc then true else nil
	-- miejsce na zapis: tu oznaczyć profil gracza do zapisu
end

-- tylko do testów (uchwyt SterowaniePasa): kopia wpisu gracza
function Pamiec.opis(gracz: Player)
	local w = dane[gracz.UserId] or {}
	return { widzialPrzelotLasu = w.widzialPrzelotLasu == true, pokonalStraznikaLasu = w.pokonalStraznikaLasu == true }
end

return Pamiec
