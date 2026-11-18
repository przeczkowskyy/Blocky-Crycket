--[[
	KlientBohatera — „bohater w świecie” (propozycja, swiat/bohater_swiat). Script, RunContext = Client, w kontenerze
	Workspace/BohaterSwiat. Po wyborze klasy gracz chodzi po świecie bohaterem swojej klasy (Rycerz, Zwiadowca,
	Kot-Mag) w stroju, który ma założony — zamiast awatara Roblox.

	Jak to działa (wszystko u tego klienta; nic nie idzie na serwer):
		• Postać Roblox (Humanoid) zostaje: fizyka, sterowanie, kamera, dotyk, podpowiedzi E i wszystko, co czytają inne
		  pakiety (HumanoidRootPart, WalkSpeed, CharacterAdded). Jej części są tylko niewidoczne (Transparency = 1
		  u tego klienta, z zapamiętaniem dawnych wartości).
		• Bohater to osobny, lokalny model z zakotwiczonym korzeniem: co klatkę staje pod postacią (stopy na ziemi:
		  HipHeight + pół wysokości HumanoidRootPart, spód własnych nóg), przodem tam, gdzie postać. Części bez kolizji,
		  dotyku, zapytań i masy; nie są połączone z postacią żadnym spawem, więc nie zmieniają jej ruchu.
		• Model składa moduł przymierzalni Workspace/StrojeProba/Moduly/Ubieranie (ten sam, który ubiera bohatera
		  w walce) z atrybutu gracza StrojProba_<klasa>; brak atrybutu = strój odniesienia, czyli wygląd z walki.
		• Ruch: własne klipy bohatera z danych walki (Workspace/TestWalki2/Moduly/Klipy + DaneAktorow) — spoczynek
		  i chód w tempie prawdziwej prędkości postaci; skok, spadanie, lądowanie i pozy mini-gier to pozy proceduralne
		  nakładane na stawy po klipie (DaneBohatera.klasy[…].pozy). Powyżej prędkości, przy której klip chodu przestaje
		  nadążać, gra proceduralny cykl biegu (LogikaBohatera.bieg): nogi z odwrotnej kinematyki tak, żeby stopa
		  w podporze stała w miejscu, do tego podskok bioder, wymach rąk i pochylenie tułowia.
		• Każdy klient buduje bohaterów WSZYSTKICH graczy z ich atrybutów (Class, StrojProba_…): najbliżsi do
		  D.widocznosc.maks_bohaterow, w promieniu D.widocznosc.promien; dalej — awatar jak dawniej. Dalekim bohaterom
		  animacja liczy się co kilka klatek.
		• Bohater znika razem z awatarem: przejmuje jego LocalTransparencyModifier (walka, mini-gra, widok z pierwszej
		  osoby chowają awatara właśnie tak).
		• Wyłącznik bez przebudowy: atrybut kontenera BohaterWSwiecie = false → awatar jak dawniej, od razu.
		• Bez kontenera TestWalki2 albo StrojeProba bohatera po prostu nie ma (awatar zostaje, bez błędów).

	UMOWA z mini-grami — Sygnaly/RuchBohatera (BindableFunction, u klienta; opis w README):
		Invoke("stan") → nil | { aktywny = true, klasa = "wojownik" | "zwiadowca" | "mag", klip = "…" }
		Invoke("klip", nazwa | nil) → true gdy przyjęte ("bieg", "skok", "padnij", "rece_gora", "radosc"; nil = samo)
		Invoke("przesun", Vector3 | nil) → true gdy przyjęte (przesunięcie bohatera względem postaci)
	Haczyk testowy — Sygnaly/SterowanieKlienta: "stan" | "pomiar", "zeruj"? | "ruch", polecenie, arg |
		"przezroczystosc", liczba | nil | "manekin", model, klasa, napis? | "manekin_usun" | "faza_biegu", 0…1 | nil |
		"nagraj", sekundy | "nagranie".
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local sygnaly = kontener:WaitForChild("Sygnaly")
local sygnalRuchu = sygnaly:WaitForChild("RuchBohatera")

------------------------------------------------------------------ umowa RuchBohatera (najpierw: Invoke bez OnInvoke czeka bez końca)
local D, L = nil, nil
local wym = { licznik = 0 } -- stan umowy lokalnego bohatera: klip, licznik, px/py/pz, ltm
local bohaterowie = {} -- właściciel (Player albo Model manekina) → rekord bohatera
local ostrzezenia = {}

local function ostrzez(tekst)
	if not ostrzezenia[tekst] then
		ostrzezenia[tekst] = true
		warn((if D then D.prefiks else "[BohaterSwiat] ") .. tekst)
	end
end

local function lokalnyBohater()
	local b = bohaterowie[gracz]
	if b ~= nil and b.model ~= nil then
		return b
	end
	return nil
end

local function ruch(polecenie, a)
	if D == nil or L == nil then
		if polecenie == "stan" then
			return nil
		end
		return false
	end
	local b = lokalnyBohater()
	local opis = nil
	if b ~= nil then
		opis = { klasa = b.klasa, tryb = b.tryb }
	end
	if polecenie == "przesun" then
		if typeof(a) == "Vector3" then
			return L.polecenieRuchu(D, wym, opis, "przesun", true, a.X, a.Y, a.Z)
		elseif a ~= nil then
			return false
		end
		return L.polecenieRuchu(D, wym, opis, "przesun", nil)
	elseif polecenie == "przezroczystosc" then
		-- dodatek poza umową: schowaj lokalnego bohatera (0…1) niezależnie od awatara; nil = jak awatar
		if b == nil then
			return false
		end
		wym.ltm = if type(a) == "number" and a == a then math.clamp(a, 0, 1) else nil
		return true
	end
	if polecenie == "klip" and b ~= nil then
		wym.czas = os.clock()
	end
	return L.polecenieRuchu(D, wym, opis, polecenie, a)
end

sygnalRuchu.OnInvoke = function(polecenie, a)
	local ok, wynik = pcall(ruch, polecenie, a)
	if not ok then
		ostrzez("RuchBohatera: " .. tostring(wynik))
		if polecenie == "stan" then
			return nil
		end
		return false
	end
	return wynik
end

------------------------------------------------------------------ dane
local moduly = kontener:WaitForChild("Moduly")
D = require(moduly:WaitForChild("DaneBohatera"))
L = require(moduly:WaitForChild("LogikaBohatera"))
local sterowanie = sygnaly:WaitForChild("SterowanieKlienta")
local R, W, A = D.ruch, D.widocznosc, D.awatar

local folder = kontener:FindFirstChild(D.folder_lokalny)
if folder == nil then
	folder = Instance.new("Folder")
	folder.Name = D.folder_lokalny
	folder.Parent = kontener
end

local NOGI = {}
for _, n in D.kosciNog do
	NOGI[n] = true
end
local EFEKTY = {}
for _, n in A.efekty do
	EFEKTY[n] = true
end

-- pozy z danych → CFrame'y stawów (raz na klasę)
local pozyCF = {}
for klucz, K in D.klasy do
	local t = {}
	for nazwa, wiersze in K.pozy do
		local lista = {}
		for _, w in wiersze do
			table.insert(lista, { w[1], CFrame.new(w[2], w[3], w[4]) * CFrame.fromOrientation(w[5], w[6], w[7]) })
		end
		t[nazwa] = lista
	end
	pozyCF[klucz] = t
end

------------------------------------------------------------------ zależności: klipy z próby walki, strój z przymierzalni
local zal = { klipy = nil, ubieranie = nil, folderDanych = nil, dane = {}, sprawdzono = -math.huge, powod = "nie sprawdzono" }

local function zaleznosci()
	if zal.klipy ~= nil and zal.ubieranie ~= nil then
		return true
	end
	if os.clock() - zal.sprawdzono < W.ponow_zaleznosci_s then
		return false
	end
	zal.sprawdzono = os.clock()
	local tw = workspace:FindFirstChild(D.kontener_walki)
	local sp = workspace:FindFirstChild(D.kontener_strojow)
	local mw = tw and tw:GetAttribute("Wygenerowane") == true and tw:FindFirstChild("Moduly")
	local ms = sp and sp:GetAttribute("Wygenerowane") == true and sp:FindFirstChild("Moduly")
	local mKlipy = mw and mw:FindFirstChild("Klipy")
	local fDane = mw and mw:FindFirstChild("DaneAktorow")
	local mUbieranie = ms and ms:FindFirstChild("Ubieranie")
	if not (mKlipy and fDane and mUbieranie and mKlipy:IsA("ModuleScript") and mUbieranie:IsA("ModuleScript")) then
		zal.powod = "brak " .. (if mKlipy and fDane then D.kontener_strojow .. "/Moduly/Ubieranie" else D.kontener_walki .. "/Moduly (Klipy, DaneAktorow)")
		return false
	end
	local ok1, K = pcall(require, mKlipy)
	local ok2, U = pcall(require, mUbieranie)
	if not (ok1 and type(K) == "table" and type(K.nowy) == "function") then
		zal.powod = "moduł Klipy nie działa"
		return false
	end
	if not (ok2 and type(U) == "table" and type(U.zbuduj) == "function" and type(U.atrybut) == "function" and U.D and U.L) then
		zal.powod = "moduł Ubieranie nie działa"
		return false
	end
	zal.klipy, zal.ubieranie, zal.folderDanych, zal.powod = K, U, fDane, ""
	return true
end

local function daneKlipow(klasa)
	local d = zal.dane[klasa]
	if d == nil then
		local m = zal.folderDanych:FindFirstChild(klasa)
		if m == nil or not m:IsA("ModuleScript") then
			error("brak danych klipów " .. klasa)
		end
		d = require(m)
		if type(d) ~= "table" or type(d.kosci) ~= "table" or type(d.klipy) ~= "table" then
			error("dane klipów " .. klasa .. " są puste")
		end
		zal.dane[klasa] = d
	end
	return d
end

------------------------------------------------------------------ awatar: niewidoczny u tego klienta, dawne wartości zapamiętane
local function schowajJeden(b, o)
	local pam = b.awatar
	if o:IsA("BasePart") or o:IsA("Decal") then
		if pam[o] == nil then
			pam[o] = o.Transparency
		end
		if o.Transparency ~= 1 then
			o.Transparency = 1
		end
	elseif EFEKTY[o.ClassName] then
		if pam[o] == nil then
			pam[o] = o.Enabled
		end
		if o.Enabled then
			o.Enabled = false
		end
	elseif A.ukryj_pole_ochronne and o:IsA("ForceField") then
		if pam[o] == nil then
			pam[o] = o.Visible
		end
		if o.Visible then
			o.Visible = false
		end
	end
end

local function probkaAwatara(b)
	local glowa = b.postac:FindFirstChild("Head")
	if glowa ~= nil and glowa:IsA("BasePart") then
		return glowa
	end
	for _, o in b.postac:GetChildren() do
		if o:IsA("BasePart") and o ~= b.hrp then
			return o
		end
	end
	return nil
end

local function schowajAwatar(b)
	for _, o in b.postac:GetDescendants() do
		schowajJeden(b, o)
	end
	b.probka = probkaAwatara(b)
	if b.polaczenie == nil then
		b.polaczenie = b.postac.DescendantAdded:Connect(function(o)
			if b.model ~= nil then
				schowajJeden(b, o)
			end
		end)
	end
end

local function pokazAwatar(b)
	if b.polaczenie ~= nil then
		b.polaczenie:Disconnect()
		b.polaczenie = nil
	end
	for o, v in b.awatar do
		if o.Parent ~= nil then
			if o:IsA("BasePart") or o:IsA("Decal") then
				o.Transparency = v
			elseif o:IsA("ForceField") then
				o.Visible = v
			else
				o.Enabled = v
			end
		end
	end
	b.awatar = {}
end

------------------------------------------------------------------ budowa bohatera
-- najniższy punkt pudła (y świata)
local function nisko(cf, rozmiar)
	local _, y, _, _, _, _, r10, r11, r12 = cf:GetComponents()
	return y - (math.abs(r10) * rozmiar.X + math.abs(r11) * rozmiar.Y + math.abs(r12) * rozmiar.Z) / 2
end

local function modelWStroju(klasa, napis)
	local U = zal.ubieranie
	local KS = U.D.klasy[klasa]
	if KS == nil then
		error("klasy " .. klasa .. " nie ma w danych przymierzalni")
	end
	-- brak atrybutu stroju = strój odniesienia (wygląd z walki); strój odrzucony przez logikę — też
	local ids = U.L.zNapisu(napis) or KS.odniesienie
	local ok, plan = U.L.plan(U.D, klasa, ids)
	if not ok then
		ok, plan = U.L.plan(U.D, klasa, KS.odniesienie)
		if not ok then
			error("strój odniesienia odrzucony: " .. tostring(plan))
		end
	end
	return U.zbuduj(klasa, plan, nil)
end

-- skraje bryły w układzie modelu: najniższy i najwyższy punkt, przód (najmniejsze Z) i tył (największe Z)
local function obrys(cf, rozmiar)
	local x, y, z = cf.XVector, cf.YVector, cf.ZVector
	local hx, hy, hz = rozmiar.X / 2, rozmiar.Y / 2, rozmiar.Z / 2
	local ey = math.abs(x.Y) * hx + math.abs(y.Y) * hy + math.abs(z.Y) * hz
	local ez = math.abs(x.Z) * hx + math.abs(y.Z) * hy + math.abs(z.Z) * hz
	return cf.Position.Y - ey, cf.Position.Y + ey, cf.Position.Z - ez, cf.Position.Z + ez
end

-- Poły stroju (LogikaBohatera.rodzajPoly): bryły wiszące poniżej bioder na kości bioder; model stoi w początku układu.
-- Ruch poły = obrót jej spawu wokół zawiasu: C0 = a · obrót · b (dzwon szaty: unoszenie przodu wokół tylnego dolnego
-- skraju, skręt wokół osi ciała i podniesienie o tyle, o ile biodra schodzą w biegu). Spoczynek = C0 z budowy (c0).
-- Wynik: lista pół albo nil, gdy nic nie wisi.
local function zbierzPoly(Bg, wiszace)
	local lista, jestDzwon = {}, false
	local dno, tyl = math.huge, -math.huge
	local gory = { przod = -math.huge, tyl = -math.huge }
	local sumy = { przod = 0, tyl = 0 }
	local ile = { przod = 0, tyl = 0 }
	for _, w in wiszace do
		local dol, gora, zp, zt = obrys(w[1].CFrame, w[1].Size)
		local rodzaj = L.rodzajPoly(Bg, dol, zp, zt)
		if rodzaj ~= nil then
			dno = math.min(dno, dol)
			tyl = math.max(tyl, zt)
			if rodzaj == "dzwon" then
				jestDzwon = true
			else
				gory[rodzaj] = math.max(gory[rodzaj], gora)
				sumy[rodzaj] += (zp + zt) / 2
				ile[rodzaj] += 1
			end
			table.insert(lista, { rodzaj = rodzaj, spaw = w[2], c0 = w[2].C0, kosc = w[3].CFrame, srodekY = (dol + gora) / 2 })
		end
	end
	if #lista == 0 then
		return nil
	end
	for _, p in lista do
		local odwr = p.kosc:Inverse()
		if jestDzwon then
			-- szata dookoła: wszystko, co wisi, idzie razem z nią
			p.dzwon = true
			p.waga = L.wagaDzwonu(Bg, p.srodekY, dno)
			p.a = odwr * CFrame.new(0, dno, tyl)
			p.m = CFrame.new(0, -dno, -tyl)
			p.b = p.kosc * p.c0
			p.gora = odwr:VectorToWorldSpace(Vector3.yAxis)
		else
			p.przod = p.rodzaj == "przod"
			p.a = odwr * CFrame.new(0, gory[p.rodzaj], sumy[p.rodzaj] / ile[p.rodzaj])
			p.b = p.a:Inverse() * p.c0
		end
	end
	return lista
end

local function zbuduj(b)
	local t0 = os.clock()
	local K = D.klasy[b.klasa]
	local dane = daneKlipow(b.klasa)
	local model = modelWStroju(b.klasa, b.napis)
	model.Name = "Bohater_" .. b.klasa
	model:SetAttribute("BohaterSwiata", b.klasa)
	local korzen = model:FindFirstChild("HumanoidRootPart")
	if korzen == nil or not korzen:IsA("BasePart") then
		model:Destroy()
		error("model bez korzenia")
	end
	korzen.Anchored = true
	local czesci, nogi, spod = {}, {}, math.huge
	local wiszace = {}
	for _, c in model:GetDescendants() do
		if c:IsA("BasePart") then
			-- nic w bohaterze nie bierze udziału w fizyce ani w zapytaniach (ruch postaci zostaje taki sam)
			c.CanCollide = false
			c.CanTouch = false
			c.CanQuery = false
			c.Massless = true
			if c.Transparency < 1 then
				table.insert(czesci, c)
				local w = c:FindFirstChild("SpawStroju")
				local kosc = w and w:IsA("Weld") and w.Part0
				if kosc and NOGI[kosc.Name] then
					table.insert(nogi, c)
					spod = math.min(spod, nisko(c.CFrame, c.Size)) -- model stoi jeszcze w początku układu
				end
				if kosc and kosc.Name == "LowerTorso" and c ~= kosc and K.bieg.poly then
					table.insert(wiszace, { c, w, kosc })
				end
			end
		end
	end
	local stawy = {}
	for _, d in model:GetChildren() do
		if d:IsA("BasePart") then
			local m = d:FindFirstChildOfClass("Motor6D")
			if m ~= nil then
				stawy[d.Name] = m
			end
		end
	end
	b.cfHrp = CFrame.new(K.hrp[1], K.hrp[2], K.hrp[3])
	model:PivotTo(b.hrp.CFrame * CFrame.new(0, -L.podStopami(b.hum.HipHeight, b.hrp.Size.Y, b.nogiR6), 0))
	model.Parent = folder
	local ok, klipy = pcall(zal.klipy.nowy, model, dane, { reczny = true })
	if not ok then
		model:Destroy()
		error("klipy: " .. tostring(klipy))
	end
	for _, akcja in { "spoczynek", "ruch", "radosc", "upadek" } do
		if not klipy:maKlip(K.klipy[akcja]) then
			klipy:zniszcz()
			model:Destroy()
			error("brak klipu " .. tostring(K.klipy[akcja]))
		end
	end
	b.model, b.korzen, b.klipy, b.stawy, b.czesci, b.nogi = model, korzen, klipy, stawy, czesci, nogi
	b.spod = if spod == math.huge then 0 else spod
	b.pam = L.nowaPamiec()
	b.wagi = {}
	b.wagaChodu = 0
	b.wagaBiegu, b.fazaBiegu, b.vBiegu, b.drogaBiegu = 0, 0, R.bieg_predkosc, 0
	b.vRzecz, b.skret, b.dBiegu, b.katCiala = b.vRzecz or 0, 0, nil, nil
	b.pola, b.polaRuszone = zbierzPoly(K.bieg, wiszace), false
	b.baza, b.tor, b.licznikRuchu = nil, nil, -1
	b.tryb = "idle"
	b.v = 0
	b.ltm = 0
	b.klatka, b.dt, b.okres = 0, 0, 1
	b.budowa_ms = (os.clock() - t0) * 1000
end

local function zniszczModel(b)
	if b.klipy ~= nil then
		pcall(function()
			b.klipy:zniszcz()
		end)
		b.klipy = nil
	end
	if b.model ~= nil then
		b.model:Destroy()
		b.model = nil
	end
end

local function usun(wlasciciel)
	local b = bohaterowie[wlasciciel]
	if b == nil then
		return
	end
	bohaterowie[wlasciciel] = nil
	pokazAwatar(b)
	zniszczModel(b)
end

------------------------------------------------------------------ ruch jednego bohatera
local nagranie = { doKiedy = 0, od = 0, klatki = {} } -- próba: zapis klatek lokalnego bohatera (haczyk "nagraj")

-- staw idzie do pozy bezwzględnej z wagą e (0…1) / dostaje dodatkowy obrót po pozie z klipu
local function ustawStaw(staw, cf, e)
	if staw ~= nil then
		staw.Transform = staw.Transform:Lerp(cf, e)
	end
end

local function dodajStaw(staw, cf)
	if staw ~= nil then
		staw.Transform = staw.Transform * cf
	end
end

local function ustawKlip(b, K, wy)
	local zmiana = b.baza ~= wy.baza
	if b.lokalny and wy.baza == "radosc" and b.licznikRuchu ~= wym.licznik then
		zmiana = true -- każde wywołanie umowy „radosc” gra wiwat od nowa, raz
	end
	if zmiana then
		b.baza = wy.baza
		b.licznikRuchu = wym.licznik
		local opcje = { przejscie = R.przejscie_klipow_s, petla = wy.petla }
		if wy.baza == "ruch" then
			opcje.predkosc = L.tempo(wy.v, K.predkoscChodu, R)
		elseif wy.baza == "radosc" then
			opcje.potem = K.klipy.spoczynek
		end
		b.tor = b.klipy:graj(K.klipy[wy.baza], opcje)
	elseif wy.baza == "ruch" and b.tor ~= nil then
		b.tor.predkosc = L.tempo(wy.v, K.predkoscChodu, R)
	end
end

local function aktualizuj(b, dt)
	local hum, hrp = b.hum, b.hrp
	if hum.Parent == nil or hrp.Parent == nil then
		return
	end
	local K = D.klasy[b.klasa]
	local zyje = hum.Health > 0
	local pr = hrp.AssemblyLinearVelocity
	local Bg = K.bieg
	-- droga postaci po ziemi w tej klatce: z niej prędkość rzeczywista (wygładzona) i krok cyklu biegu. Ruch idzie za
	-- tym, co postać naprawdę przeszła, nie za wciśniętym klawiszem: na przeszkodzie prędkość spada i bieg ustaje.
	local gdzie = hrp.Position
	local bylo = b.pozBiegu
	local drogaKlatki = 0
	if bylo ~= nil then
		local dx, dz = gdzie.X - bylo.X, gdzie.Z - bylo.Z
		drogaKlatki = math.sqrt(dx * dx + dz * dz)
	end
	b.pozBiegu = gdzie
	b.drogaBiegu += drogaKlatki
	b.vRzecz = L.predkosc(b.vRzecz, drogaKlatki, dt, Bg.wygladzanie, Bg.vMaks)
	-- obrót postaci → przechył tułowia w zakręcie
	local _, katCiala = hrp.CFrame:ToOrientation()
	local obrot = 0
	if b.katCiala ~= nil then
		obrot = (katCiala - b.katCiala + math.pi) % (2 * math.pi) - math.pi
	end
	b.katCiala = katCiala
	b.skret = L.skretCiala(b.skret, obrot / math.max(dt, 0.001), dt, Bg.skretCiala)
	local wy = L.krok(b.pam, {
		zyje = zyje,
		stan = hum:GetState().Name,
		naZiemi = hum.FloorMaterial ~= Enum.Material.Air,
		vpoz = math.min(math.sqrt(pr.X * pr.X + pr.Z * pr.Z), b.vRzecz),
		vpion = pr.Y,
		zdalny = b.zdalny,
		wymuszony = if b.lokalny then wym.klip else nil,
	}, R, dt, K.bieg)
	b.tryb = wy.tryb
	b.v = wy.v
	ustawKlip(b, K, wy)
	-- waga biegu: cykl proceduralny wchodzi i wychodzi płynnie (klip chodu ↔ bieg)
	local celBiegu = if wy.bieg then 1 else 0
	local krokBiegu = dt / Bg.czas
	if b.wagaBiegu < celBiegu then
		b.wagaBiegu = math.min(celBiegu, b.wagaBiegu + krokBiegu)
	elseif b.wagaBiegu > celBiegu then
		b.wagaBiegu = math.max(celBiegu, b.wagaBiegu - krokBiegu)
	end
	if wy.bieg then
		b.vBiegu = wy.v
	end
	-- waga chodu: o tyle rig unosi się, gdy klip chodu schodzi stopami pod ziemię
	local celChodu = if wy.baza == "ruch" then 1 else 0
	local krokChodu = dt / R.przejscie_klipow_s
	if b.wagaChodu < celChodu then
		b.wagaChodu = math.min(celChodu, b.wagaChodu + krokChodu)
	elseif b.wagaChodu > celChodu then
		b.wagaChodu = math.max(celChodu, b.wagaChodu - krokChodu)
	end
	-- klip i pozy proceduralne (dalekim bohaterom co kilka klatek)
	b.klatka += 1
	b.dt += dt
	if b.klatka % b.okres == 0 then
		local dta = b.dt
		b.dt = 0
		b.klipy:krok(dta)
		b.klipy:zastosuj()
		local drogaKroku = b.drogaBiegu
		b.drogaBiegu = 0
		if b.wagaBiegu > 0 then
			-- cykl biegu: biodra i nogi bezwzględnie (stopa w podporze stoi w miejscu), reszta ciała jako dodatek do klipu
			local f, d = L.kadencja(Bg, b.vBiegu)
			local s = L.skalaBiegu(Bg, b.vBiegu)
			local wMiejscu = b.lokalny and wym.klip == "bieg"
			if b.dBiegu == nil then
				b.fazaBiegu = d / 2 -- wejście w bieg: lewa stopa pod biodrem (najbliżej pozy stojącej)
			else
				b.fazaBiegu = L.krokBiegu(Bg, b.fazaBiegu, b.dBiegu, f, d, dta, drogaKroku, wMiejscu)
			end
			b.dBiegu = d
			local faza = b.fazaBiegu
			if b.lokalny and wym.fazaBiegu ~= nil then
				faza = wym.fazaBiegu -- próba: zatrzymana faza (arkusz klatek)
			end
			local c = L.bieg(Bg, faza, d, s)
			local e = b.wagaBiegu * b.wagaBiegu * (3 - 2 * b.wagaBiegu)
			local st = b.stawy
			ustawStaw(st.LowerTorso, CFrame.new(0, c.biodraY, 0), e)
			ustawStaw(st.LeftUpperLeg, CFrame.Angles(c.udoL, 0, 0), e)
			ustawStaw(st.LeftLowerLeg, CFrame.Angles(c.lydkaL, 0, 0), e)
			ustawStaw(st.LeftFoot, CFrame.Angles(c.stopaL, 0, 0), e)
			ustawStaw(st.RightUpperLeg, CFrame.Angles(c.udoP, 0, 0), e)
			ustawStaw(st.RightLowerLeg, CFrame.Angles(c.lydkaP, 0, 0), e)
			ustawStaw(st.RightFoot, CFrame.Angles(c.stopaP, 0, 0), e)
			-- ręce, tułów, głowa i dodatki klasy (ogon, kapelusz, kostur): wymach z fazą kroku, skala rośnie z prędkością
			for _, w in Bg.dodatki do
				local rx, ry, rz = L.dodatek(w, faza, s)
				dodajStaw(st[w[1]], CFrame.fromOrientation(rx * e, ry * e, rz * e))
			end
			local sc = Bg.skretCiala
			dodajStaw(st.UpperTorso, CFrame.fromOrientation(0, sc.obrot * b.skret * e, sc.przechyl * b.skret * e))
			-- poły stroju: pasy z przodu i z tyłu idą za udem, dzwon szaty unosi przód i faluje z krokiem
			if b.pola ~= nil then
				b.polaRuszone = true
				local wyzej = math.max(0, -c.biodraY) * e
				for _, p in b.pola do
					if p.dzwon then
						local unies, skret = L.dzwon(Bg, faza, s * e, p.waga)
						p.spaw.C0 = p.a * CFrame.Angles(unies, 0, 0) * p.m * CFrame.Angles(0, skret, 0) * p.b
							+ p.gora * (wyzej * p.waga)
					else
						p.spaw.C0 = p.a * CFrame.Angles((if p.przod then c.polaPrzod else c.polaTyl) * e, 0, 0) * p.b
					end
				end
			end
		else
			b.dBiegu = nil
			if b.polaRuszone then
				b.polaRuszone = false
				for _, p in b.pola do
					p.spaw.C0 = p.c0
				end
			end
		end
		local cele = {}
		if wy.poza ~= nil then
			cele[wy.poza] = 1
		elseif wy.baza == "ruch" then
			cele.pochyl = L.pochylenie(wy.v, R)
		end
		L.krokWag(b.wagi, cele, dta, D.czasyPoz, D.kolejnoscPoz)
		local pozy = pozyCF[b.klasa]
		for _, nazwa in D.kolejnoscPoz do
			local w = b.wagi[nazwa]
			if w ~= nil then
				local e = w * w * (3 - 2 * w)
				for _, p in pozy[nazwa] do
					local s = b.stawy[p[1]]
					if s ~= nil then
						s.Transform = s.Transform:Lerp(p[2], e)
					end
				end
			end
		end
	end
	-- miejsce: pod postacią, stopy na ziemi, przodem jak postać; po śmierci bohater zostaje tam, gdzie padł
	local cf = b.cfOstatni
	if zyje or cf == nil then
		local dol = L.podStopami(hum.HipHeight, hrp.Size.Y, b.nogiR6)
		cf = hrp.CFrame * CFrame.new(0, L.wysokoscRigu(b.spod, K.podniesienieChodu, b.wagaChodu) - dol, 0)
		b.cfOstatni = cf
	end
	if b.lokalny and wym.px ~= nil then
		cf = cf * CFrame.new(wym.px, wym.py, wym.pz)
	end
	-- korzeń staje w miejscu z POPRZEDNIEJ klatki: silnik stosuje Motor6D.Transform dopiero po kroku fizyki, więc poza
	-- stawów widoczna w tej klatce też jest z poprzedniej — razem dają stopę w podporze dokładnie w miejscu (bohater
	-- jest o jedną klatkę za niewidocznym awatarem)
	local teraz = cf
	if R.korzen_klatke_pozniej and b.cfOpozniony ~= nil then
		teraz = b.cfOpozniony
	end
	b.cfOpozniony = cf
	b.korzen.CFrame = teraz * b.cfHrp
	if b.lokalny and nagranie.doKiedy > os.clock() then
		-- próba: klatka po klatce — faza biegu i miejsce stóp w świecie (części kości stóp)
		local _, d = L.kadencja(Bg, b.vBiegu)
		local lewa, prawa = b.model:FindFirstChild("LeftFoot"), b.model:FindFirstChild("RightFoot")
		table.insert(nagranie.klatki, { os.clock() - nagranie.od, b.tryb, b.wagaBiegu, b.fazaBiegu, d, b.v,
			lewa.Position.X, lewa.Position.Y, lewa.Position.Z, prawa.Position.X, prawa.Position.Y, prawa.Position.Z,
			hrp.Position.X, hrp.Position.Y, hrp.Position.Z })
	end
	-- widoczność jak awatar (walka, mini-gra i widok z pierwszej osoby chowają go przez LocalTransparencyModifier)
	local cel = 0
	local probka = b.probka
	if probka ~= nil and probka.Parent ~= nil then
		cel = probka.LocalTransparencyModifier
	end
	if b.lokalny and wym.ltm ~= nil then
		cel = math.max(cel, wym.ltm)
	end
	local wzor = b.czesci[1]
	if wzor ~= nil and (math.abs(b.ltm - cel) > 0.004 or math.abs(wzor.LocalTransparencyModifier - cel) > 0.004) then
		b.ltm = cel
		for _, c in b.czesci do
			c.LocalTransparencyModifier = cel
		end
	end
end

------------------------------------------------------------------ kto ma mieć bohatera (co klatkę; tanie)
local manekiny = {} -- Model (postać testowa) → { klasa, napis }
local bledy = {} -- właściciel → { klucz, doKiedy }
local atrybutyStroju = {} -- klasa → nazwa atrybutu stroju gracza (z modułu przymierzalni)

local function nogiR6(postac, hum)
	if hum.RigType ~= Enum.HumanoidRigType.R6 then
		return 0
	end
	local noga = postac:FindFirstChild("Left Leg")
	return if noga ~= nil and noga:IsA("BasePart") then noga.Size.Y else 2
end

local function uzgodnij()
	local wlaczony = kontener:GetAttribute(D.atrybut_wlacznika) ~= false
	local kandydaci, opisy = {}, {}
	if wlaczony and zaleznosci() then
		local kamera = workspace.CurrentCamera
		local oko = if kamera then kamera.CFrame.Position else nil
		local function dodaj(wlasciciel, postac, klasa, napis, lokalny, zdalny)
			if klasa == nil or postac == nil or postac.Parent == nil then
				return
			end
			local hum = postac:FindFirstChildOfClass("Humanoid")
			local hrp = postac:FindFirstChild("HumanoidRootPart")
			if hum == nil or hrp == nil or not hrp:IsA("BasePart") then
				return
			end
			local odl = 0
			if not lokalny and oko ~= nil then
				odl = (hrp.Position - oko).Magnitude
			end
			local stary = bohaterowie[wlasciciel]
			if not lokalny and not L.widoczny(odl, stary ~= nil, W) then
				return
			end
			opisy[wlasciciel] = { postac = postac, hum = hum, hrp = hrp, klasa = klasa, napis = napis, lokalny = lokalny,
				zdalny = zdalny, odl = odl }
			table.insert(kandydaci, { id = wlasciciel, odl = odl, lokalny = lokalny })
		end
		for _, p in Players:GetPlayers() do
			local klasa = L.klasa(D, p:GetAttribute(D.atrybut_klasy))
			local napis = nil
			if klasa ~= nil then
				local atrybut = atrybutyStroju[klasa]
				if atrybut == nil then
					atrybut = zal.ubieranie.atrybut(klasa)
					atrybutyStroju[klasa] = atrybut
				end
				napis = p:GetAttribute(atrybut)
			end
			dodaj(p, p.Character, klasa, napis, p == gracz, p ~= gracz)
		end
		for m, info in manekiny do
			dodaj(m, m, info.klasa, info.napis, false, false)
		end
	end
	local wybrani = L.wybierz(kandydaci, W.maks_bohaterow)
	for wlasciciel in bohaterowie do
		if not wybrani[wlasciciel] then
			usun(wlasciciel)
		end
	end
	local budowy = 0
	local teraz = os.clock()
	for wlasciciel in wybrani do
		local o = opisy[wlasciciel]
		local stary = bohaterowie[wlasciciel]
		if stary ~= nil and stary.postac == o.postac and stary.klasa == o.klasa and stary.napis == o.napis then
			stary.odl = o.odl
			stary.okres = L.okres(o.odl, W)
		else
			local klucz = o.klasa .. "|" .. L.kluczStroju(o.napis)
			local blad = bledy[wlasciciel]
			local czeka = blad ~= nil and blad.klucz == klucz and teraz < blad.doKiedy
			if budowy < W.budowy_na_klatke and not czeka then
				budowy += 1
				local nowy = { wlasciciel = wlasciciel, postac = o.postac, hum = o.hum, hrp = o.hrp, klasa = o.klasa,
					napis = o.napis, klucz = klucz, lokalny = o.lokalny, zdalny = o.zdalny, odl = o.odl, awatar = {},
					nogiR6 = nogiR6(o.postac, o.hum) }
				local ok, powod = pcall(zbuduj, nowy)
				if ok then
					bledy[wlasciciel] = nil
					nowy.okres = L.okres(o.odl, W)
					if stary ~= nil and stary.postac == o.postac then
						-- zmiana stroju albo klasy: awatar zostaje schowany, podmieniamy tylko model
						nowy.awatar, nowy.polaczenie, nowy.probka = stary.awatar, nil, stary.probka
						if stary.polaczenie ~= nil then
							stary.polaczenie:Disconnect()
						end
						nowy.cfOstatni = stary.cfOstatni
						zniszczModel(stary)
						bohaterowie[wlasciciel] = nowy
					else
						usun(wlasciciel)
						bohaterowie[wlasciciel] = nowy
					end
					schowajAwatar(nowy)
				else
					bledy[wlasciciel] = { klucz = klucz, doKiedy = teraz + W.ponow_po_bledzie_s }
					ostrzez("bohater " .. o.klasa .. " nie powstał (awatar zostaje): " .. tostring(powod))
					if stary ~= nil and stary.postac ~= o.postac then
						usun(wlasciciel)
					end
				end
			elseif stary ~= nil and stary.postac ~= o.postac then
				usun(wlasciciel) -- stara postać zniknęła (odrodzenie), nowy bohater powstanie w następnej klatce
			end
		end
	end
end

------------------------------------------------------------------ pętla
local pomiar = { suma = 0, maks = 0, n = 0, bledy = 0 }
local czasAwatara = 0

local function praca(dt)
	uzgodnij()
	-- umowa bez lokalnego bohatera (wyłącznik, odrodzenie): pozy i przesunięcie nie czekają na następnego
	if lokalnyBohater() == nil then
		if wym.klip ~= nil or wym.px ~= nil then
			L.zerujRuch(wym)
		end
		wym.ltm = nil
		wym.fazaBiegu = nil
	elseif D.kontrakt.wymuszenie_maks_s > 0 and wym.klip ~= nil and os.clock() - (wym.czas or 0) > D.kontrakt.wymuszenie_maks_s then
		L.zerujRuch(wym)
	end
	for _, b in bohaterowie do
		aktualizuj(b, dt)
	end
	czasAwatara += dt
	if czasAwatara >= W.sprawdzaj_awatar_co_s then
		czasAwatara = 0
		for _, b in bohaterowie do
			if b.postac.Parent ~= nil then
				for _, o in b.postac:GetDescendants() do
					schowajJeden(b, o)
				end
				if b.probka == nil or b.probka.Parent == nil then
					b.probka = probkaAwatara(b)
				end
			end
		end
	end
end

local NAZWA_PETLI = "BohaterSwiat"

local function klatka(dt)
	local t0 = os.clock()
	local ok, blad = pcall(praca, dt)
	if not ok then
		pomiar.bledy += 1
		ostrzez("błąd w pętli: " .. tostring(blad))
	end
	local ms = (os.clock() - t0) * 1000
	if pomiar.n >= D.pomiar.okno_klatek then
		pomiar.suma, pomiar.maks, pomiar.n = 0, 0, 0
	end
	pomiar.suma += ms
	pomiar.maks = math.max(pomiar.maks, ms)
	pomiar.n += 1
end

RunService:BindToRenderStep(NAZWA_PETLI, Enum.RenderPriority.Last.Value, klatka)

script.Destroying:Connect(function()
	RunService:UnbindFromRenderStep(NAZWA_PETLI)
	for wlasciciel in bohaterowie do
		usun(wlasciciel)
	end
end)

------------------------------------------------------------------ haczyk testowy
local function stopyNadZiemia(b)
	local dno = math.huge
	for _, c in b.nogi do
		dno = math.min(dno, nisko(c.CFrame, c.Size))
	end
	local wyklucz = { folder }
	for _, p in Players:GetPlayers() do
		if p.Character then
			table.insert(wyklucz, p.Character)
		end
	end
	for m in manekiny do
		table.insert(wyklucz, m)
	end
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	par.FilterDescendantsInstances = wyklucz
	par.RespectCanCollide = true
	local r = workspace:Raycast(b.hrp.Position, Vector3.yAxis * -D.pomiar.promien_w_dol, par)
	if r == nil or dno == math.huge then
		return nil
	end
	return dno - r.Position.Y
end

local function opisBohatera(b)
	local K = D.klasy[b.klasa]
	local ukryte, widoczne, razem = 0, 0, 0
	if b.postac.Parent ~= nil then
		for _, o in b.postac:GetDescendants() do
			if o:IsA("BasePart") or o:IsA("Decal") then
				razem += 1
				if o.Transparency >= 1 then
					ukryte += 1
				else
					widoczne += 1
				end
			end
		end
	end
	local fizyka = 0
	for _, c in b.model:GetDescendants() do
		if c:IsA("BasePart") and (c.CanCollide or c.CanTouch or c.CanQuery or not c.Massless) then
			fizyka += 1
		end
	end
	local wagi = {}
	for n, w in b.wagi do
		wagi[n] = w
	end
	local ziemia = b.korzen.CFrame * b.cfHrp:Inverse()
	local dol = L.podStopami(b.hum.HipHeight, b.hrp.Size.Y, b.nogiR6)
	local podPostacia = b.hrp.CFrame * CFrame.new(0, -dol, 0)
	return {
		aktywny = true,
		klasa = b.klasa,
		klasaGry = K.klasaGry,
		tryb = b.tryb,
		baza = b.baza,
		klip = if b.baza then K.klipy[b.baza] else nil,
		tempo = if b.tor then b.tor.predkosc else nil,
		predkosc = b.v,
		stroj = b.model:GetAttribute("Stroj"),
		strojGracza = b.napis,
		bryly = #b.czesci,
		strojBryly = b.model:GetAttribute("StrojBryly"),
		instancji = #b.model:GetDescendants() + 1,
		spod = b.spod,
		stopyNadZiemia = stopyNadZiemia(b),
		odPostaci = (ziemia.Position - podPostacia.Position).Magnitude,
		zgodnoscPrzodu = ziemia.LookVector:Dot(b.hrp.CFrame.LookVector),
		ltm = b.ltm,
		okres = b.okres,
		odleglosc = b.odl,
		wagi = wagi,
		wagaChodu = b.wagaChodu,
		wagaBiegu = b.wagaBiegu,
		fazaBiegu = b.fazaBiegu,
		budowa_ms = b.budowa_ms,
		awatar = { czesci = razem, ukryte = ukryte, widoczne = widoczne },
		fizyka = { zle = fizyka, zakotwiczony = b.korzen.Anchored },
		ziemia = { ziemia.Position.X, ziemia.Position.Y, ziemia.Position.Z },
		hrp = { b.hrp.Position.X, b.hrp.Position.Y, b.hrp.Position.Z },
	}
end

local function stan()
	local n, wszystkieBryly = 0, 0
	local inni = {}
	for wlasciciel, b in bohaterowie do
		n += 1
		wszystkieBryly += #b.czesci
		if wlasciciel ~= gracz then
			table.insert(inni, { klasa = b.klasa, tryb = b.tryb, okres = b.okres, odleglosc = b.odl, bryly = #b.czesci,
				manekin = manekiny[wlasciciel] ~= nil })
		end
	end
	local nm = 0
	for _ in manekiny do
		nm += 1
	end
	local lokalny = lokalnyBohater()
	return {
		gotowy = true,
		wlaczony = kontener:GetAttribute(D.atrybut_wlacznika) ~= false,
		skrot = D.skrot,
		zaleznosci = zal.klipy ~= nil and zal.ubieranie ~= nil,
		powod = zal.powod,
		bohaterow = n,
		bryl = wszystkieBryly,
		manekinow = nm,
		inni = inni,
		lokalny = if lokalny then opisBohatera(lokalny) else nil,
		klasaGracza = L.klasa(D, gracz:GetAttribute(D.atrybut_klasy)),
		ruch = { klip = wym.klip, licznik = wym.licznik, przesun = if wym.px ~= nil then { wym.px, wym.py, wym.pz } else nil },
		klatka = { srednia_ms = if pomiar.n > 0 then pomiar.suma / pomiar.n else 0, maks_ms = pomiar.maks, n = pomiar.n,
			bledy = pomiar.bledy },
	}
end

sterowanie.OnInvoke = function(polecenie, a, b, c)
	if polecenie == "stan" then
		return stan()
	elseif polecenie == "pomiar" then
		local w = { srednia_ms = if pomiar.n > 0 then pomiar.suma / pomiar.n else 0, maks_ms = pomiar.maks, n = pomiar.n,
			bledy = pomiar.bledy }
		if a == "zeruj" then
			pomiar.suma, pomiar.maks, pomiar.n = 0, 0, 0
		end
		return w
	elseif polecenie == "ruch" then
		return ruch(a, b)
	elseif polecenie == "przezroczystosc" then
		return ruch("przezroczystosc", a)
	elseif polecenie == "manekin" then
		-- postać testowa (Model z Humanoidem i HumanoidRootPart) dostaje bohatera jak cudzy gracz
		if typeof(a) ~= "Instance" or not a:IsA("Model") or type(b) ~= "string" or D.klasy[b] == nil then
			return false
		end
		manekiny[a] = { klasa = b, napis = if type(c) == "string" then c else nil }
		return true
	elseif polecenie == "faza_biegu" then
		-- zatrzymana faza cyklu biegu lokalnego bohatera (0…1) do zrzutów; nil = cykl biegnie sam
		wym.fazaBiegu = if type(a) == "number" and a == a then a - math.floor(a) else nil
		return true
	elseif polecenie == "nagraj" then
		-- zapis klatek lokalnego bohatera przez a sekund (najwyżej 10): { t, tryb, waga biegu, faza, podpór, prędkość,
		-- lewa stopa xyz, prawa stopa xyz, HumanoidRootPart xyz }
		nagranie.klatki = {}
		nagranie.od = os.clock()
		nagranie.doKiedy = os.clock() + math.clamp(if type(a) == "number" and a == a then a else 2, 0, 10)
		return true
	elseif polecenie == "nagranie" then
		return { trwa = nagranie.doKiedy > os.clock(), klatki = nagranie.klatki }
	elseif polecenie == "manekin_usun" then
		for m in manekiny do
			manekiny[m] = nil
		end
		return true
	end
	return nil
end

kontener:SetAttribute("SkrotKlienta", D.skrot)
kontener:SetAttribute("KlientGotowy", true)
