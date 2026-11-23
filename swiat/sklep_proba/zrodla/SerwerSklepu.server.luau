--[[
	SerwerSklepu — cienki serwer sklepu zbrojmistrza na próbę (D-106; swiat/sklep_proba). Script, RunContext = Server,
	w kontenerze Workspace/SklepProba. Poza Studio usuwa cały kontener (w opublikowanej grze próby nie ma).

	Sklep niczego nie trzyma i o niczym nie decyduje: właścicielem przedmiotów gracza jest kowal (swiat/kowal_proba),
	a Złota — StanGracza. Każde zapytanie klienta po sprawdzeniu (typy, limit, odległość) idzie do wejścia kowala
	KowalProba/Sygnaly/Sklep: "oferta" | "kup", id | "zaloz", id — to kowal sprawdza klasę, poziom, posiadanie i Złoto,
	płaci przez WydajZloto, zapisuje przedmiot, zakłada go według reguły i przelicza Modyfikatory.
	Bez kowala albo bez stanu gracza okno dostaje napis „Sklep nieczynny (próba)” — bez błędów w konsoli.

	Zdalne/Sklep (RemoteFunction): InvokeServer(akcja, id?) → { ok, powod?, tekst?, widok? }
		"oferta"      widok = { oferta, zloto, poziom, klasa } (wiersze liczy kowal; klient tylko pokazuje)
		"kup", id     kupno za Złoto (gracz przy zbrojmistrzu) → tekst + odświeżony widok
		"zaloz", id   założenie posiadanego przedmiotu (gracz przy zbrojmistrzu) → tekst + odświeżony widok
	Klient wysyła tylko nazwę akcji i id z oferty; serwer sprawdza typy, długość, limit jednego zapytania na D.limit s
	i odległość od stoiska zbrojmistrza (D.miejsce.zasieg + zapasSerwera).
	Sygnaly/SterowanieSerwera (BindableFunction, haczyk testowy): "stan" → { ok, kowal } · "zgodnosc".
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneSklepu"))
local L = require(moduly:WaitForChild("LogikaSklepu"))
local sklepF = kontener:WaitForChild("Zdalne"):WaitForChild("Sklep")
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera")
local T = D.teksty

local ostatnie = {}
local liczniki = { LicznikKupna = 0, LicznikZalozen = 0, LicznikOdmow = 0 }
local AKCJE = { oferta = true, kup = true, zaloz = true }

local function dolicz(nazwa)
	liczniki[nazwa] += 1
	kontener:SetAttribute(nazwa, liczniki[nazwa])
end

------------------------------------------------------------------ styk z kowalem (FindFirstChild + pcall)
local function wejscieKowala()
	local k = workspace:FindFirstChild(D.kowal.kontener)
	local s = k and k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild(D.kowal.sygnal)
	if f and f:IsA("BindableFunction") then
		return f
	end
	return nil
end

local function kowal(polecenie, gracz, id)
	local f = wejscieKowala()
	if not f then
		return nil
	end
	local ok, w = pcall(function()
		return f:Invoke(polecenie, gracz, id)
	end)
	if not ok or type(w) ~= "table" then
		return nil
	end
	return w
end

local function przyZbrojmistrzu(gracz)
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp then
		return false
	end
	local p = hrp.Position
	local e = D.miejsce.punkt
	local dx, dz = p.X - e[1], p.Z - e[3]
	local r = D.miejsce.zasieg + D.miejsce.zapasSerwera
	return dx * dx + dz * dz <= r * r
end

local function widok(gracz)
	local r = kowal("oferta", gracz, nil)
	if r == nil or r.ok ~= true or type(r.oferta) ~= "table" then
		return nil
	end
	return { oferta = r.oferta, zloto = r.zloto, poziom = r.poziom, klasa = r.klasa }
end

local function odmowa(gracz, powod, zWidokiem)
	dolicz("LicznikOdmow")
	local w = { ok = false, powod = powod, tekst = L.komunikat(D, "kup", { ok = false, powod = powod }) }
	if zWidokiem then
		w.widok = widok(gracz)
	end
	return w
end

local function wykonaj(gracz, akcja, id)
	if type(akcja) ~= "string" or not AKCJE[akcja] then
		return { ok = false, powod = "zla_akcja", tekst = T.blad }
	end
	if id ~= nil and (type(id) ~= "string" or #id > 64) then
		return { ok = false, powod = "zly_argument", tekst = T.blad }
	end
	if akcja == "oferta" then
		local w = widok(gracz)
		if w == nil then
			return { ok = false, powod = "nieczynny", tekst = T.nieczynny }
		end
		return { ok = true, widok = w }
	end
	if type(id) ~= "string" then
		return odmowa(gracz, "nieznany_przedmiot", true)
	end
	if not przyZbrojmistrzu(gracz) then
		return odmowa(gracz, "daleko", true)
	end
	local r = kowal(akcja, gracz, id)
	if r == nil or r.powod == "brak_stanu" or r.powod == "zly_gracz" then
		dolicz("LicznikOdmow")
		return { ok = false, powod = "nieczynny", tekst = T.nieczynny }
	end
	if r.ok == true then
		dolicz(if akcja == "kup" then "LicznikKupna" else "LicznikZalozen")
	else
		dolicz("LicznikOdmow")
	end
	return { ok = r.ok == true, powod = r.powod, brakuje = r.brakuje, zalozony = r.zalozony == true,
		tekst = L.komunikat(D, akcja, r), widok = widok(gracz) }
end

sklepF.OnServerInvoke = function(gracz, akcja, id)
	local t = os.clock()
	if ostatnie[gracz] and t - ostatnie[gracz] < D.limit then
		dolicz("LicznikOdmow")
		return { ok = false, powod = "za_szybko", tekst = T.za_szybko }
	end
	ostatnie[gracz] = t
	local ok, w = pcall(wykonaj, gracz, akcja, id)
	if not ok then
		warn(D.prefiks .. "błąd sklepu: " .. tostring(w))
		return { ok = false, powod = "blad", tekst = T.blad }
	end
	return w
end

Players.PlayerRemoving:Connect(function(gracz)
	ostatnie[gracz] = nil
end)

-- kowal pojawia się albo znika (przebudowa): atrybut dla prób i dla okna
local function pilnuj()
	kontener:SetAttribute("KowalPodlaczony", wejscieKowala() ~= nil)
	task.delay(D.kowal.coIleS, pilnuj)
end
pilnuj()

sterowanie.OnInvoke = function(polecenie)
	if polecenie == "zgodnosc" then
		local ok, n, zle = L.sprawdzPrzypadki(D)
		return { ok = ok, n = n, zle = zle }
	elseif polecenie == "stan" then
		return { ok = true, kowal = wejscieKowala() ~= nil, kupna = liczniki.LicznikKupna, odmowy = liczniki.LicznikOdmow }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end

local okZ, nZ, zleZ = L.sprawdzPrzypadki(D)
kontener:SetAttribute("ZgodnoscLogikiSklepu", if okZ then string.format("OK %d/%d", nZ, nZ)
	else "BŁĄD " .. table.concat(zleZ, ", "))
kontener:SetAttribute("SkrotSerwera", D.skrot)
kontener:SetAttribute("SerwerSklepuGotowy", true)
