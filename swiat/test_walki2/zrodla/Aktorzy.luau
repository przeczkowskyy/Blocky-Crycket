--[[
	Aktorzy — lokalne klony aktorów walki v2 (klasy gracza i przeciwnicy) z własnymi klipami i obrysem.

	Szablony stoją w Workspace/TestWalki2/Aktorzy/<klucz> (galeria na północ od podestu; buduje je zbuduj.py
	z dane/<klucz>.json). Klient klonuje szablon LOKALNIE (inni gracze go nie widzą), ustawia w scenie i gra klipy
	z danych (moduł Klipy). Tabela aktorów (Moduly/TabelaAktorow) powstaje z swiat/test_walki2/aktorzy.py.

	API (klucz = id klasy albo przeciwnika z silnika: wojownik, zwiadowca, mag, lesny_slime, cierniowy_wilk,
	muchomornik, lesny_troll, straznik_lasu):
		Aktorzy.kolejnosc                 lista kluczy w kolejności tabeli
		Aktorzy.wpis(klucz)               wiersz tabeli (pola opisane w aktorzy.py; wymiary w studach)
		Aktorzy.klip(klucz, akcja)        nazwa klipu dla akcji albo id umiejętności; nil = brak klipu (ruch proceduralny)
		Aktorzy.nowy(klucz, cfZiemi, opcje?) → aktor
			cfZiemi: CFrame punktu na ziemi pod aktorem, LookVector = przód (np. Ustawienia.miejsce("gracz"))
			opcje.rodzic  gdzie wstawić klon (domyślnie kontener; walka: własny folder sceny)
			opcje.obrys   "brak" | "highlight" | "skorupa" (domyślnie Ustawienia.OBRYS)
			opcje.reczny  true → Klipy liczone ręcznie (aktor.klipy:krok(dt) i :zastosuj())
			opcje.bezSpoczynku  true → nie włączaj od razu klipu spoczynku
	aktor:
		aktor.klucz, aktor.wpis, aktor.model, aktor.hrp, aktor.klipy (odtwarzacz z modułu Klipy),
		aktor.liczbaCzesci (widoczne bryły, bez skorupy), aktor.liczbaInstancji
		aktor:graj(akcja, opcjeKlipu?) → tor | nil   akcja = AKCJE z tabeli albo id umiejętności; nil = brak klipu.
			opcjeKlipu jak Klipy:graj, plus opcjeKlipu.naTrafieniu = fn(tor) — wołane w chwili trafienia z tabeli
			(wpis.chwile[klip]); gdy dla klipu nie ma chwili, w połowie klipu
		aktor:spoczynek(przejscie?)        zapętlony klip spoczynku
		aktor:maKlip(akcja) → nazwa | nil   aktor:chwila(akcja) → s | nil (chwila trafienia przy prędkości 1)
		aktor:ustaw(cfZiemi)               przestaw całego aktora (ruch proceduralny: doskok, odrzut, upadek całego ciała)
		aktor:cfZiemi() → CFrame
		aktor:punkt(nazwa) → CFrame | nil   świat: "Bron", "Pocisk", "Piers" (+ "Tarcza" u Wojownika), "Pasek" (nad głową)
		aktor:obrys(tryb)                  zmień obrys w trakcie
		aktor:przezroczystosc(x)           LocalTransparencyModifier wszystkich brył (0 = widać, 1 = schowany)
		aktor:zniszcz()
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local moduly = script.Parent
local kontener = moduly.Parent
local Ustawienia = require(moduly:WaitForChild("Ustawienia"))
local Klipy = require(moduly:WaitForChild("Klipy"))
local Tabela = require(moduly:WaitForChild("TabelaAktorow"))
local folderDanych = moduly:WaitForChild("DaneAktorow")

local Aktorzy = {}
Aktorzy.kolejnosc = Tabela.kolejnosc
Aktorzy.AKCJE = Tabela.akcje
local Aktor = {}
Aktor.__index = Aktor

local daneKlipow: { [string]: any } = {}

function Aktorzy.wpis(klucz: string)
	return Tabela.aktorzy[klucz]
end

function Aktorzy.klip(klucz: string, akcja: string): string?
	local w = Tabela.aktorzy[klucz]
	if not w then
		return nil
	end
	local k = w.klipy[akcja]
	if k == nil then
		k = w.umiejetnosci[akcja]
	end
	return if type(k) == "string" then k else nil
end

local function dane(klucz: string)
	local d = daneKlipow[klucz]
	if not d then
		local modul = folderDanych:WaitForChild(klucz, 5)
		if not modul then
			error("Aktorzy: brak danych klipów aktora " .. klucz)
		end
		d = require(modul)
		daneKlipow[klucz] = d
	end
	return d
end

local function szablon(klucz: string): Model
	local folder = kontener:WaitForChild("Aktorzy", 5)
	local m = folder and folder:WaitForChild(klucz, 5)
	if not m then
		error("Aktorzy: brak szablonu aktora " .. klucz .. " w " .. kontener:GetFullName() .. ".Aktorzy")
	end
	return m :: Model
end

------------------------------------------------------------------ obrys
--[[ Skorupa („odwrócona powłoka”): czarna kopia bryły powiększona o OBRYS_GRUBOSC z każdej strony, z siatką
	o UJEMNEJ skali — wtedy silnik rysuje jej tylne ściany, więc z bryły wystaje tylko czarny brzeg sylwetki.
	Sprawdzone 14.11.2026 w Studio: ujemna skala działa TYLKO dla siatki z pliku (MeshType.FileMesh); dla typów
	wbudowanych (Brick, Wedge, Sphere…) skala bierze moduł i kopia zasłania bryłę w całości. Bez uploadu mamy jedną
	pewną siatkę-klocek wbudowaną w klienta: rbxasset://fonts/leftarm.mesh (ręka R6, 1 × 2 × 1 studa, lekko
	zaokrąglone krawędzie). Dlatego skorupę dostają tylko bryły-klocki; kliny, walce i kule zostają bez obrysu
	(prostopadłościan wokół klina zasłoniłby jego skos czarnym trójkątem). ]]
local SIATKA_KLOCKA = "rbxasset://fonts/leftarm.mesh"
local ROZMIAR_SIATKI = Vector3.new(1, 2, 1)

local function klocek(c: BasePart): boolean
	if c:IsA("WedgePart") or c:IsA("CornerWedgePart") or not c:IsA("Part") then
		return false
	end
	local sm = c:FindFirstChildOfClass("SpecialMesh")
	if sm then
		return sm.MeshType == Enum.MeshType.Brick
	end
	return (c :: Part).Shape == Enum.PartType.Block
end

-- bryły widoczne (bez korzenia, kości i dodatków obrysu)
local function bryly(model: Model): { BasePart }
	local wynik = {}
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and d.Transparency < 1 and d.Name ~= "HumanoidRootPart" and d:GetAttribute("Obrys") == nil
			and d:GetAttribute("Punkt") == nil then
			table.insert(wynik, d)
		end
	end
	return wynik
end

function Aktorzy.obrys(model: Model, tryb: string?)
	tryb = tryb or Ustawienia.OBRYS
	local stary = model:FindFirstChild("ObrysHighlight")
	if stary then
		stary:Destroy()
	end
	local staraSkorupa = model:FindFirstChild("ObrysSkorupa")
	if staraSkorupa then
		staraSkorupa:Destroy()
	end
	if tryb == "highlight" then
		local h = Instance.new("Highlight")
		h.Name = "ObrysHighlight"
		h.FillTransparency = 1
		h.OutlineColor = Ustawienia.KOLORY.tusz
		h.OutlineTransparency = 0
		h.DepthMode = Enum.HighlightDepthMode.Occluded
		h.Adornee = model
		h.Parent = model
		return 1
	elseif tryb == "skorupa" then
		local g = Ustawienia.OBRYS_GRUBOSC
		local folder = Instance.new("Folder")
		folder.Name = "ObrysSkorupa"
		local n = 0
		for _, c in bryly(model) do
			local r = c.Size
			-- bryły skóry (galareta slime'a) zgniata siatka co klatkę, a skorupa jest sztywną kopią rozmiaru spoczynku —
			-- przy przysiadzie i w kałuży wystawałaby czarną ramą, więc skóra nie dostaje skorupy (D8)
			if math.min(r.X, r.Y, r.Z) < Ustawienia.OBRYS_MIN or not klocek(c) or c:GetAttribute("Skora") then
				continue
			end
			local s = Instance.new("Part")
			s.Name = "Skorupa"
			s:SetAttribute("Obrys", true)
			s.Size = r + Vector3.one * (2 * g)
			s.CFrame = c.CFrame
			s.Color = Ustawienia.KOLORY.tusz
			s.Material = Enum.Material.SmoothPlastic
			s.CastShadow = false
			s.CanCollide = false
			s.CanTouch = false
			s.CanQuery = false
			s.Massless = true
			s.Anchored = false
			s.TopSurface = Enum.SurfaceType.Smooth
			s.BottomSurface = Enum.SurfaceType.Smooth
			local sm = Instance.new("SpecialMesh")
			sm.MeshType = Enum.MeshType.FileMesh
			sm.MeshId = SIATKA_KLOCKA
			sm.Scale = -(s.Size / ROZMIAR_SIATKI) -- ujemna skala odwraca ściany: widać tylko tylne ściany = obrys
			sm.Parent = s
			local w = Instance.new("Weld")
			w.Part0 = c
			w.Part1 = s
			w.C0 = CFrame.identity
			w.Parent = s
			s.Parent = folder
			n += 1
		end
		folder.Parent = model
		return n
	end
	return 0
end

------------------------------------------------------------------ aktor
function Aktorzy.nowy(klucz: string, cfZiemi: CFrame, opcje: any?)
	opcje = opcje or {}
	local wpis = Tabela.aktorzy[klucz]
	if not wpis then
		error("Aktorzy: nieznany aktor " .. tostring(klucz))
	end
	local d = dane(klucz)
	local model = szablon(klucz):Clone()
	model.Name = klucz .. "_lokalny"
	model:SetAttribute("Lokalny", true)
	local hrp = model:FindFirstChild("HumanoidRootPart") :: BasePart
	hrp.Anchored = true
	model:PivotTo(cfZiemi)
	local self = setmetatable({}, Aktor)
	self.klucz = klucz
	self.wpis = wpis
	self.model = model
	self.hrp = hrp
	self.przesuniecieKorzenia = CFrame.new(wpis.hrp[1], wpis.hrp[2], wpis.hrp[3])
	self.liczbaCzesci = #bryly(model)
	Aktorzy.obrys(model, opcje.obrys)
	if Ustawienia.POKAZ_PUNKTOW then
		for _, a in model:GetDescendants() do
			if a:IsA("Attachment") and a.Name:sub(1, 6) == "Punkt_" then
				local k = Instance.new("Part")
				k.Name = a.Name .. "_znacznik"
				k:SetAttribute("Punkt", true)
				k.Shape = Enum.PartType.Ball
				k.Size = Vector3.one * 0.35
				k.Material = Enum.Material.Neon
				k.Color = Color3.fromRGB(255, 40, 200)
				k.CanCollide, k.CanTouch, k.CanQuery, k.Massless, k.CastShadow = false, false, false, true, false
				k.CFrame = a.WorldCFrame
				local w = Instance.new("Weld")
				w.Part0 = a.Parent :: BasePart
				w.Part1 = k
				w.C0 = a.CFrame
				w.Parent = k
				k.Parent = model
			end
		end
	end
	model.Parent = opcje.rodzic or kontener
	self.liczbaInstancji = #model:GetDescendants() + 1
	self.klipy = Klipy.nowy(model, d, { reczny = opcje.reczny })
	if not opcje.bezSpoczynku then
		self:spoczynek(0)
	end
	return self
end

function Aktor:maKlip(akcja: string): string?
	return Aktorzy.klip(self.klucz, akcja)
end

function Aktor:chwila(akcja: string): number?
	local k = self:maKlip(akcja)
	return k and self.wpis.chwile[k] or nil
end

function Aktor:graj(akcja: string, opcje: any?)
	local nazwa = self:maKlip(akcja)
	if not nazwa then
		return nil
	end
	opcje = opcje or {}
	if akcja == "spoczynek" and opcje.petla == nil then
		opcje.petla = true
	end
	local tor = self.klipy:graj(nazwa, opcje)
	if tor and opcje.naTrafieniu then
		local s = self.wpis.chwile[nazwa]
		if s == nil or s <= 0 then
			s = tor.dlugosc * 0.5
		end
		tor:naChwili(s, opcje.naTrafieniu)
	end
	return tor
end

function Aktor:spoczynek(przejscie: number?)
	return self:graj("spoczynek", { przejscie = przejscie or Ustawienia.PRZEJSCIE_KLIPOW, petla = true })
end

function Aktor:ustaw(cfZiemi: CFrame)
	self.hrp.CFrame = cfZiemi * self.przesuniecieKorzenia
end

function Aktor:cfZiemi(): CFrame
	return self.hrp.CFrame * self.przesuniecieKorzenia:Inverse()
end

function Aktor:punkt(nazwa: string): CFrame?
	if nazwa == "Pasek" then
		return self:cfZiemi() * CFrame.new(0, self.wpis.pasek, 0)
	end
	local a = self.model:FindFirstChild("Punkt_" .. nazwa, true)
	return if a and a:IsA("Attachment") then a.WorldCFrame else nil
end

function Aktor:obrys(tryb: string)
	return Aktorzy.obrys(self.model, tryb)
end

function Aktor:przezroczystosc(x: number)
	for _, d in self.model:GetDescendants() do
		if d:IsA("BasePart") then
			d.LocalTransparencyModifier = x
		end
	end
end

function Aktor:zniszcz()
	if self.klipy then
		self.klipy:zniszcz()
	end
	self.model:Destroy()
end

return Aktorzy
