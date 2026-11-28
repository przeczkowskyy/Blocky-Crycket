--[[
	KlientKowala — klient kowala na próbę (D-102; swiat/kowal_proba). Script, RunContext = Client, w kontenerze
	Workspace/KowalProba. Niczego nie decyduje: pokazuje okno z widokiem od serwera, wysyła tylko nazwę akcji i id
	przedmiotu (Zdalne/Kuznia), gra klipy kowala z klocków (lokalnie, Motor6D.Transform) i pokazuje napisy o łupie.

	E przy kowalu (ProximityPrompt „Podpowiedz” na części Kuznia/E; włącza go serwer w Play) → okno (od 26.11.2026 tylko,
	gdy w PlayerGui nie ma okna kowala Pawła „OknoKowala” — ono zastępuje to okno próbne); X albo odejście dalej
	niż D.kuznia.zasiegOkna od punktu E → zamknięcie. Kowal: klip D.kowal.klip w pętli, po udanym ulepszeniu raz
	D.kowal.klipRadosci. Atrybut kontenera EmulacjaEkranu = Vector2 (np. 667, 375) — okno jak na telefonie (zrzuty).
	Sygnaly/SterowanieKlienta (BindableFunction, haczyk prób): "otworz" · "zamknij" · "stan" → { otwarte, wiersze,
	wybrany, rozmiarTekstu, klip } · "kliknij", nazwa ("Ulepsz" | "Rozbierz" | "Przedmiot_<id>" | "Zamknij").
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneKowala"))
local Okno = require(moduly:WaitForChild("OknoKowala"))
local Rig = require(moduly:WaitForChild("RigKowala"))
local daneRigu = require(moduly:WaitForChild(D.kowal.rig))
local kuzniaF = kontener:WaitForChild("Zdalne"):WaitForChild("Kuznia")
local zdarzenia = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaKowala")
local T = D.teksty

local stan = { okno = nil, uchwyt = nil, czeka = false }

------------------------------------------------------------------ kowal z klocków (klipy lokalnie)
local function podlaczKowala()
	local kuznia = kontener:WaitForChild("Kuznia", 30)
	local model = kuznia and kuznia:WaitForChild("Kowal", 30)
	if not model then
		warn(D.prefiks .. "brak modelu kowala w kuźni")
		return
	end
	-- kości dochodzą strumieniowaniem: czekamy na korzeń i wszystkie kości z danych
	for _ = 1, 60 do
		local u = Rig.uchwyt(model, daneRigu)
		if u then
			stan.uchwyt = u
			Rig.graj(u, D.kowal.klip)
			kontener:SetAttribute("KowalAnimowany", true)
			return
		end
		task.wait(0.5)
	end
	warn(D.prefiks .. "rig kowala niekompletny — kowal stoi bez ruchu")
end
task.spawn(podlaczKowala)

RunService.Heartbeat:Connect(function(dt)
	if stan.uchwyt then
		Rig.krok(stan.uchwyt, dt)
	end
end)

------------------------------------------------------------------ napis o łupie (także bez okna)
local napis = nil
local nrNapisu = 0
local function pokazNapis(tekst)
	if not napis then
		local g = Instance.new("ScreenGui")
		g.Name = "KowalProbaKomunikat"
		g.ResetOnSpawn = false
		g.IgnoreGuiInset = true
		g.DisplayOrder = D.ui.kolejnosc_wyswietlania
		local t = Instance.new("TextLabel")
		t.Name = "Napis"
		t.AnchorPoint = Vector2.new(0.5, 0.5)
		t.Position = UDim2.fromScale(0.5, D.ui.komunikat_y)
		t.Size = UDim2.fromScale(0.5, 0.05)
		t.BackgroundColor3 = Color3.fromHex(D.ui.kolory.tlo)
		t.BackgroundTransparency = 0.2
		t.TextColor3 = Color3.fromHex(D.ui.kolory.zloto)
		t.Font = Enum.Font[D.ui.czcionka]
		t.TextScaled = true
		local o = Instance.new("UITextSizeConstraint")
		o.MaxTextSize = D.ui.tekst_maks
		o.MinTextSize = D.ui.tekst_min
		o.Parent = t
		local r = Instance.new("UICorner")
		r.CornerRadius = UDim.new(0, 8)
		r.Parent = t
		t.Parent = g
		g.Parent = gracz:WaitForChild("PlayerGui")
		napis = t
	end
	napis.Text = tekst
	napis.Visible = true
	nrNapisu += 1
	local nr = nrNapisu
	kontener:SetAttribute("OstatniNapis", tekst)
	task.delay(4, function()
		if nr == nrNapisu and napis then
			napis.Visible = false
		end
	end)
end

------------------------------------------------------------------ okno
local function zamknij()
	if stan.okno then
		stan.okno:zniszcz()
		stan.okno = nil
	end
	kontener:SetAttribute("OknoOtwarte", false)
end

local function odpowiedz(r)
	if type(r) ~= "table" then
		return
	end
	if stan.okno and type(r.widok) == "table" then
		stan.okno:pokaz(r.widok)
	end
	if stan.okno and type(r.tekst) == "string" then
		stan.okno:komunikat(r.tekst, r.ok ~= true)
	end
end

local function prosba(akcja, id)
	if stan.czeka then
		return
	end
	stan.czeka = true
	local ok, r = pcall(function()
		return kuzniaF:InvokeServer(akcja, id)
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
	stan.okno = Okno.nowe(gracz:WaitForChild("PlayerGui"), D, {
		emulacja = kontener:GetAttribute("EmulacjaEkranu"),
		naUlepsz = function(id)
			prosba("ulepsz", id)
		end,
		naRozbierz = function(id)
			prosba("rozbierz", id)
		end,
		naZamknij = zamknij,
	})
	stan.okno:pokaz({ tytul = T.tytul, materialy = "", zloto = "", bohater = "", uwaga = "", wiersze = {} })
	kontener:SetAttribute("OknoOtwarte", true)
	prosba("widok")
end

local function podlaczPodpowiedz()
	local kuznia = kontener:WaitForChild("Kuznia", 30)
	local e = kuznia and kuznia:WaitForChild("E", 30)
	local pp = e and e:WaitForChild("Podpowiedz", 30)
	if not pp then
		warn(D.prefiks .. "brak podpowiedzi E kowala")
		return
	end
	pp.Triggered:Connect(function()
		-- okno kowala Pawła (ScreenGui „OknoKowala”, src/client/OknoKowalaClient, 24.11.2026) otwiera się na to samo E
		-- i zastępuje to okno próbne: wtedy na E nie otwieramy swojego (bez dwóch okien naraz i bez mignięcia).
		-- Haczyk prób "otworz" działa dalej; atrybut kontenera OknoZastapione mówi próbom, czyje okno stoi.
		local pg = gracz:FindFirstChild("PlayerGui")
		local cudze = pg and pg:FindFirstChild("OknoKowala")
		if cudze and cudze:IsA("ScreenGui") then
			kontener:SetAttribute("OknoZastapione", cudze.Name)
			return
		end
		kontener:SetAttribute("OknoZastapione", nil)
		otworz()
	end)
end
task.spawn(podlaczPodpowiedz)

-- zamknięcie po odejściu od kowala
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
		local e = D.kuznia.e
		local dx, dz = hrp.Position.X - e[1], hrp.Position.Z - e[3]
		if dx * dx + dz * dz > D.kuznia.zasiegOkna * D.kuznia.zasiegOkna then
			zamknij()
		end
	end
end)

zdarzenia.OnClientEvent:Connect(function(polecenie, a, b)
	if polecenie == "lup" and type(a) == "string" then
		pokazNapis(string.format(if b == true then T.lup_nowy else T.lup_zapas, a))
	elseif polecenie == "ulepszono" then
		if stan.uchwyt then
			Rig.graj(stan.uchwyt, D.kowal.klipRadosci, 1, D.kowal.klip)
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
		return { ok = true, otwarte = o ~= nil, wiersze = o and o.widok and #o.widok.wiersze or 0,
			wybrany = o and o.wybrany, rozmiarTekstu = o and o.rozmiarTekstu,
			klip = stan.uchwyt and stan.uchwyt.klip, napis = napis and napis.Visible and napis.Text or nil }
	elseif polecenie == "kliknij" and type(a) == "string" and stan.okno then
		local o = stan.okno.okno
		for _, d in o:GetDescendants() do
			if d:IsA("TextButton") and d.Name == a and d.Active then
				if a == "Ulepsz" then
					prosba("ulepsz", stan.okno.wybrany)
				elseif a == "Rozbierz" then
					prosba("rozbierz", stan.okno.wybrany)
				elseif a == "Zamknij" then
					zamknij()
				else
					stan.okno.wybrany = string.sub(a, #"Przedmiot_" + 1)
					stan.okno:pokaz(stan.okno.widok)
				end
				return { ok = true }
			end
		end
		return { ok = false, powod = "brak_przycisku" }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end
kontener:SetAttribute("KlientKowalaGotowy", true)
