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

-- drugi biom (17.11.2026): SerwerPasa podaje klucze swojego biomu (DanePasa.biom), np. widzialPrzelotBagna;
-- każdy kontener ma własną kopię modułu, więc klucze lasu i Bagna się nie mieszają
function Pamiec.klucze(lista: { string })
	for _, k in lista do
		if type(k) == "string" and k ~= "" then
			KLUCZE[k] = true
		end
	end
end
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
	if w ~= nil and w[klucz] == true then
		return true
	end
	-- 18.11.2026, zapis postępu (swiat/stan_gracza, domyślnie wyłączony): gdy działa, stan z poprzedniej sesji wraca
	-- jako atrybut gracza o nazwie klucza z wielkiej litery (WidzialPrzelotLasu, PokonalStraznikaBagna…); przy
	-- wyłączonym zapisie bez zmian — tylko pamięć serwera
	local stan = workspace:FindFirstChild("StanGracza")
	if stan ~= nil and stan:GetAttribute("ZapisAktywny") == true then
		return gracz:GetAttribute(string.upper(string.sub(klucz, 1, 1)) .. string.sub(klucz, 2)) == true
	end
	return false
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
	local wynik = {}
	for k in KLUCZE do
		wynik[k] = w[k] == true
	end
	return wynik
end

return Pamiec
