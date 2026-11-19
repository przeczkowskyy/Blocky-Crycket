--[[
	KlientSklepu — klient sklepu zbrojmistrza na próbę (D-106; swiat/sklep_proba). Script, RunContext = Client,
	w kontenerze Workspace/SklepProba. Niczego nie decyduje: pokazuje ofertę od serwera i wysyła tylko nazwę akcji
	i id przedmiotu (Zdalne/Sklep).

	Okno otwiera ISTNIEJĄCA podpowiedź E bazaru przy zbrojmistrzu: klient bazaru po E odpala u klienta zdarzenie
	ReplicatedStorage.<D.miejsce.zdarzenie> (BindableEvent „OknoMiejsca”) z id miejsca — tu słuchamy id D.miejsce.id.
	Pakietu bazaru nie zmieniamy; jego dymek „w budowie” wyłącza przewidziany do tego atrybut zdarzenia
	(zdarzenie:SetAttribute(id, true) — haczyk opisany w README bazaru). X albo odejście dalej niż D.miejsce.zasiegOkna
	od stoiska → zamknięcie. Atrybut kontenera EmulacjaEkranu = Vector2 (np. 667, 375) — okno jak na telefonie.
	Sygnaly/SterowanieKlienta (BindableFunction, haczyk prób): "otworz" · "zamknij" · "stan" → { otwarte, wiersze,
	zakladka, rozmiarTekstu, komunikat } · "zakladka", id stopnia · "kliknij", id przedmiotu (przycisk wiersza).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneSklepu"))
local L = require(moduly:WaitForChild("LogikaSklepu"))
local Okno = require(moduly:WaitForChild("OknoSklepu"))
local sklepF = kontener:WaitForChild("Zdalne"):WaitForChild("Sklep")
local T = D.teksty

local stan = { okno = nil, czeka = false }

local function zamknij()
	if stan.okno then
		stan.okno:zniszcz()
		stan.okno = nil
	end
	kontener:SetAttribute("OknoOtwarte", false)
end

local function odpowiedz(r)
	local o = stan.okno
	if not o then
		return
	end
	if type(r) ~= "table" then
		o:nieczynny(T.nieczynny)
		return
	end
	if type(r.widok) == "table" then
		o:pokaz(r.widok)
	elseif r.powod == "nieczynny" then
		o:nieczynny(T.nieczynny)
		return
	end
	if type(r.tekst) == "string" then
		o:komunikat(r.tekst, r.ok ~= true)
	end
end

local function prosba(akcja, id)
	if stan.czeka then
		return
	end
	stan.czeka = true
	local ok, r = pcall(function()
		return sklepF:InvokeServer(akcja, id)
	end)
	stan.czeka = false
	if not ok then
		if stan.okno then
			stan.okno:komunikat(T.blad, true)
		end
		return
	end
	odpowiedz(r)
end

local function otworz()
	if stan.okno then
		return
	end
	stan.okno = Okno.nowe(gracz:WaitForChild("PlayerGui"), D, L, {
		emulacja = kontener:GetAttribute("EmulacjaEkranu"),
		naKup = function(id)
			prosba("kup", id)
		end,
		naZaloz = function(id)
			prosba("zaloz", id)
		end,
		naZamknij = zamknij,
	})
	kontener:SetAttribute("OknoOtwarte", true)
	prosba("oferta")
end

-- zdarzenie okien bazaru: tworzy je pierwszy, kto go potrzebuje (ten sam wzór co w kliencie bazaru)
local function zdarzenieOkien()
	local z = ReplicatedStorage:FindFirstChild(D.miejsce.zdarzenie)
	if z == nil then
		z = Instance.new("BindableEvent")
		z.Name = D.miejsce.zdarzenie
		z.Parent = ReplicatedStorage
	end
	return z
end

local zdarzenie = zdarzenieOkien()
if zdarzenie:IsA("BindableEvent") then
	zdarzenie:SetAttribute(D.miejsce.id, true) -- to miejsce ma już okno: bazar nie pokazuje dymku „w budowie”
	zdarzenie.Event:Connect(function(id)
		if id == D.miejsce.id then
			otworz()
		end
	end)
	kontener:SetAttribute("PodpietePodE", true)
else
	warn(D.prefiks .. "zdarzenie okien bazaru ma inny typ — okno sklepu otworzy tylko haczyk prób")
end

-- zamknięcie po odejściu od zbrojmistrza
local odliczanie = 0
RunService.Heartbeat:Connect(function(dt)
	if not stan.okno then
		return
	end
	odliczanie += dt
	if odliczanie < 0.25 then
		return
	end
	odliczanie = 0
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if hrp then
		local e = D.miejsce.punkt
		local dx, dz = hrp.Position.X - e[1], hrp.Position.Z - e[3]
		if dx * dx + dz * dz > D.miejsce.zasiegOkna * D.miejsce.zasiegOkna then
			zamknij()
		end
	end
end)

------------------------------------------------------------------ haczyk prób (Play w Studio)
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieKlienta")
sterowanie.OnInvoke = function(polecenie, a)
	if polecenie == "otworz" then
		otworz()
		return { ok = true }
	elseif polecenie == "zamknij" then
		zamknij()
		return { ok = true }
	elseif polecenie == "stan" then
		local o = stan.okno
		return { ok = true, otwarte = o ~= nil, wiersze = o and o.liczbaWierszy or 0, zakladka = o and o.zakladka,
			rozmiarTekstu = o and o.rozmiarTekstu, komunikat = o and o.tekstKomunikatu or nil }
	elseif polecenie == "zakladka" and type(a) == "string" and stan.okno then
		stan.okno.zakladka = a
		stan.okno:rysuj()
		return { ok = true }
	elseif polecenie == "kliknij" and type(a) == "string" and stan.okno then
		local wiersz = stan.okno.okno:FindFirstChild("Lista") and stan.okno.okno.Lista:FindFirstChild("Wiersz_" .. a)
		local b = wiersz and wiersz:FindFirstChild("Przycisk")
		if not b or not b.Active then
			return { ok = false, powod = "brak_przycisku" }
		end
		local akcja = if wiersz:GetAttribute("Stan") == "kup" then "kup" else "zaloz"
		if akcja == "kup" then
			prosba("kup", a)
		else
			prosba("zaloz", a)
		end
		return { ok = true }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end
kontener:SetAttribute("KlientSklepuGotowy", true)
