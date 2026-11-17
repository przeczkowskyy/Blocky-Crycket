--[[
	SerwerStrojow — serwerowa połowa przymierzalni (próba D-071, swiat/stroje_proba). Script, RunContext = Server,
	w kontenerze Workspace/StrojeProba. Poza Studio usuwa cały kontener (w opublikowanej grze próby nie ma).

	Źródło prawdy o stroju: atrybuty GRACZA ustawiane wyłącznie tutaj — D.atrybut .. klasa (np. „StrojProba_wojownik”)
	= „id,id,…” w kolejności danych (pusty napis = goły bohater, brak atrybutu = dawny szablon walki). Atrybuty gracza
	widzi jego klient (podgląd, walka), zostają po odrodzeniu, giną z końcem sesji (bez zapisu — to próba).

	Zdalne/ZmienStroj (RemoteFunction): InvokeServer(akcja, klasa, arg) → { ok, powod?, klasa, stroj? }
		"zaloz", klasa, id        przedmiot z katalogu do jego slotu okna (to, co tam było, zdjęte)
		"zdejmij", klasa, slot    pusty slot okna
		"zestaw", klasa, nazwa    zestaw z danych (golas, komplet, zestawy modułu bohatera)
		"dawny", klasa            atrybut usunięty → walka znowu z dawnym szablonem
		"stan", klasa             tylko odczyt
	Klient wysyła tylko napisy z zamkniętych list; serwer sprawdza typy, długość, klasę i każdą regułę stroju
	(LogikaStrojow) i dopiero wtedy ustawia atrybut. Limit: jedno wywołanie na D.limit s na gracza.
	Sygnaly/SterowanieSerwera (BindableFunction, haczyk testowy): Invoke("ustaw", gracz, klasa, napis|nil) — ten sam
	przegląd co zdalna; Invoke("czytaj", gracz, klasa).
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneStrojow"))
local L = require(moduly:WaitForChild("LogikaStrojow"))
local zmien = kontener:WaitForChild("Zdalne"):WaitForChild("ZmienStroj")
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera")

local AKCJE = { zaloz = true, zdejmij = true, zestaw = true, dawny = true, stan = true }
local ostatnie = {}
local odrzucone = 0

local function odniesienie(klasa)
	local ids = {}
	for _, id in D.klasy[klasa].odniesienie do
		table.insert(ids, id)
	end
	return ids
end

-- 18.11.2026 (swiat/kowal_proba, D-102): gdy działa kowal na próbę (kontener Workspace/KowalProba i atrybut gracza
-- KowalDostepne = „id,id,…” — pisze go tylko serwer kowala), gracz zakłada wyłącznie przedmioty, które ma (części
-- zbroi idą z całością), a „Dawny wygląd” jest niedostępny. Bez kowala → nil: przymierzalnia działa jak dawniej.
local function dostepne(gracz)
	local v = gracz:GetAttribute("KowalDostepne")
	if not workspace:FindFirstChild("KowalProba") or type(v) ~= "string" then
		return nil
	end
	local zb = {}
	for _, id in L.zNapisu(v) or {} do
		zb[id] = true
	end
	for id, P in D.przedmioty do
		if P.czescOd ~= nil and zb[P.czescOd] then
			zb[id] = true
		end
	end
	return zb
end

local function tylkoDostepne(ids, zb)
	if zb == nil then
		return ids
	end
	local w = {}
	for _, id in ids do
		if zb[id] then
			table.insert(w, id)
		end
	end
	return w
end

local function wykonaj(gracz, akcja, klasa, arg)
	if type(akcja) ~= "string" or not AKCJE[akcja] then
		return { ok = false, powod = "zla_akcja" }
	end
	if type(klasa) ~= "string" or D.klasy[klasa] == nil then
		return { ok = false, powod = "zla_klasa" }
	end
	if arg ~= nil and (type(arg) ~= "string" or #arg > 64) then
		return { ok = false, powod = "zly_argument" }
	end
	local nazwa = D.atrybut .. klasa
	local teraz = gracz:GetAttribute(nazwa)
	if akcja == "stan" then
		return { ok = true, klasa = klasa, stroj = teraz }
	end
	local zb = dostepne(gracz)
	if akcja == "dawny" then
		if zb then
			return { ok = false, powod = "dawny_niedostepny", klasa = klasa, stroj = teraz }
		end
		gracz:SetAttribute(nazwa, nil)
		return { ok = true, klasa = klasa }
	end
	if akcja == "zaloz" and zb and not zb[arg] then
		return { ok = false, powod = "nie_masz", klasa = klasa, stroj = teraz }
	end
	-- bez atrybutu postać wygląda jak szablon walki = strój odniesienia, więc od niego zaczynamy zmianę
	local obecny = tylkoDostepne(L.zNapisu(teraz) or odniesienie(klasa), zb)
	local ok, wynik
	if akcja == "zaloz" then
		ok, wynik = L.zaloz(D, klasa, obecny, arg)
	elseif akcja == "zdejmij" then
		ok, wynik = L.zdejmij(D, klasa, obecny, arg)
	else
		ok, wynik = L.zestaw(D, klasa, arg)
		if ok and zb then
			ok, wynik = L.normalizuj(D, klasa, tylkoDostepne(wynik, zb))
		end
	end
	if not ok then
		return { ok = false, powod = wynik, klasa = klasa, stroj = teraz }
	end
	local napis = L.naNapis(wynik)
	gracz:SetAttribute(nazwa, napis)
	return { ok = true, klasa = klasa, stroj = napis }
end

zmien.OnServerInvoke = function(gracz, akcja, klasa, arg)
	local t = os.clock()
	if ostatnie[gracz] and t - ostatnie[gracz] < D.limit then
		odrzucone += 1
		kontener:SetAttribute("OdrzuconeZaSzybko", odrzucone)
		return { ok = false, powod = "za_szybko" }
	end
	ostatnie[gracz] = t
	local ok, w = pcall(wykonaj, gracz, akcja, klasa, arg)
	if not ok then
		warn("[StrojeProba] błąd zmiany stroju: " .. tostring(w))
		return { ok = false, powod = "blad" }
	end
	return w
end

Players.PlayerRemoving:Connect(function(gracz)
	ostatnie[gracz] = nil
end)

sterowanie.OnInvoke = function(polecenie, gracz, klasa, napis)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or type(klasa) ~= "string" or D.klasy[klasa] == nil then
		return { ok = false, powod = "zle_argumenty" }
	end
	local nazwa = D.atrybut .. klasa
	if polecenie == "czytaj" then
		return { ok = true, stroj = gracz:GetAttribute(nazwa) }
	elseif polecenie == "ustaw" then
		if napis == nil then
			gracz:SetAttribute(nazwa, nil)
			return { ok = true }
		end
		local ok, wynik = L.normalizuj(D, klasa, L.zNapisu(napis) or {})
		if not ok then
			return { ok = false, powod = wynik }
		end
		gracz:SetAttribute(nazwa, L.naNapis(wynik))
		return { ok = true, stroj = L.naNapis(wynik) }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end

-- podpowiedź E przy stojaku: zbudowana wyłączona (Edit), włączona w Play (tylko w Studio)
local podpowiedzi = 0
for _, d in kontener:GetDescendants() do
	if d:IsA("ProximityPrompt") and d:GetAttribute("Akcja") == "przymierzalnia" then
		d.Enabled = true
		podpowiedzi += 1
	end
end
kontener:SetAttribute("PodpowiedziWlaczone", podpowiedzi)
kontener:SetAttribute("SkrotSerwera", D.skrot)
kontener:SetAttribute("SerwerGotowy", true)
