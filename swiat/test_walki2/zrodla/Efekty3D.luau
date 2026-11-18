--[[
	Efekty3D — efekty 3D walki v2 robione z części Roblox i wbudowanych efektów (ParticleEmitter z domyślną teksturą,
	Fire, Trail, materiał ForceField / Neon). Żadnych uploadów. Wszystko powstaje LOKALNIE u klienta w folderze sceny
	i znika przy sprzątaniu (fx:wyczysc()).

	Czas: efekty, które się ruszają (pociski, rozbłyski, fale, korzenie), dostają krok w CZASIE SCENY (fx:krok(d)),
	więc zwalniają razem ze sceną przy krytyku i przyspieszają przy tempie ×2 / ×4. Cząsteczki (ParticleEmitter, Fire)
	biegną w czasie rzeczywistym — to tylko ozdoba.

	API (fx = Efekty3D.nowe(folder, ustawienia)):
		fx:pocisk(nazwa, od, do, czas, opcje?)   → obiekt; Pocisk.<nazwa> (iskra, strzala, kula_ognia, lod, kwas; Dżungla:
		                                          pylek, jad); opcje.luk = wysokość łuku, opcje.naKoniec = fn(),
		                                          opcje.chybiony = true
		fx:wybuch(nazwa, poz, skala?)            Wybuch.<nazwa> (iskra, ogien, lod, kwas, trucizna, zarodniki, kamien,
		                                          zloto, bariera, blask, cios, krytyk, blok, tarcza; Dżungla: pylek, jad,
		                                          ukaszenie, liscie, kokos, kamuflaz, ruiny)
		fx:fala(poz, kolor, promien)             fala uderzeniowa na ziemi
		fx:pazury(cf, kolor, rozmiar, krzyz?)    trzy świecące ślady pazurów w poprzek celu (krzyz = drugie trzy na krzyż)
		fx:ukaszenie(cf, kolor, rozmiar)         cztery kły zatrzaskujące się na celu (Wąż Stu Lian)
		fx:pyl(poz, kolory, ile, czas, przysp, rozmiar)  jednorazowy obłok drobin (osiadający pyłek, bąble jadu)
		fx:chmura(od, do, czas, kolor)           chmura zarodników płynąca do celu
		fx:korzenie(cfZiemi, promien, kolor, czasWzrostu, czasTrwania)
		fx:smuga(aktor, kolor, czas)             smuga (Trail) za bronią aktora przez czas sceny
		fx:smugaCzesci(czesc, kolor, czas, szer) smuga za dowolną częścią (bańka kwasu z klipu)
		fx:kaluza(poz, promien, kolor, czas)     płaska kałuża kwasu na ziemi przez czas sceny
		fx:wyglad(nazwa, aktor) → ozdoba         Wyglad.<nazwa> — trwały efekt na postaci; ozdoba:puls(), ozdoba:zniszcz()
		                                          (Dżungla: sen, kamuflaz, ruiny)
		fx:lup(zrodlo, cel, lup, natychmiast)    wysypany łup (monety, żetony, klejnot, kryształ)
		fx:krok(d)                               d = krok czasu sceny
		fx:wyczysc()                             niszczy wszystko
		fx.utworzono                             licznik utworzonych instancji (pomiar)
		fx:licznik() → { aktywne, ozdoby, pula, utworzono, koszt }   pomiar: ile efektów żyje i ile instancji kosztował
		                                          każdy rodzaj (koszt["pocisk:pylek"] = najwięcej nowych instancji naraz)
		fx:opisKosztu() → "pocisk:jad=9;…"       to samo jako napis (atrybut OstatniKosztEfektow kontenera)

	Efekty Dżungli (18.11.2026, propozycja): własny wygląd umiejętności potworów Dżungli — podpięty danymi
	(Choreografie.UMIEJETNOSCI_AKTORA), z tych samych klocków i wbudowanych cząsteczek co reszta; nic nie świeci
	światłem (PointLight), wszystko znika z fx:wyczysc(). Spis i liczniki: swiat/dzungla_pas_gra/README.md.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Efekty = {}
Efekty.__index = Efekty

local los = Random.new()
local rad = math.rad

-- rejestry nazw (test bez Studio sprawdza, że każda nazwa z Choreografie ma tu funkcję)
local Pocisk = {}
local Wybuch = {}
local Wyglad = {}

local function hex(h: string): Color3
	return Color3.fromHex(h)
end

local function gladko(x: number): number
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end

------------------------------------------------------------------ podstawy
function Efekty.nowe(folder: Instance, U: any)
	local self = setmetatable({}, Efekty)
	self.folder = folder
	self.U = U
	self.aktywne = {} -- obiekty z krok(d) → false, gdy skończone
	self.ozdoby = {}
	self.utworzono = 0
	self.wolne = {} -- pula iskier
	self.koszt = {} -- "rodzaj:nazwa" → najwięcej nowych instancji przy jednym wywołaniu (pomiar)
	return self
end

-- pomiar kosztu: ile instancji przybyło od `przed` przy efekcie rodzaj:nazwa (iskry z puli liczą się tylko nowe)
function Efekty:zmierz(rodzaj: string, nazwa: string, przed: number)
	local klucz = rodzaj .. ":" .. nazwa
	self.koszt[klucz] = math.max(self.koszt[klucz] or 0, self.utworzono - przed)
end

function Efekty:licznik()
	local ozdoby = 0
	for _, oz in self.ozdoby do
		if not oz.zniszczona then
			ozdoby += 1
		end
	end
	return { aktywne = #self.aktywne, ozdoby = ozdoby, pula = #self.wolne, utworzono = self.utworzono, koszt = self.koszt }
end

function Efekty:opisKosztu(): string
	local klucze = {}
	for k in self.koszt do
		table.insert(klucze, k)
	end
	table.sort(klucze)
	local czesci = {}
	for _, k in klucze do
		table.insert(czesci, k .. "=" .. tostring(self.koszt[k]))
	end
	return table.concat(czesci, ";")
end

function Efekty:nowa(klasa: string, w: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in w do
		o[k] = v
	end
	o.Parent = rodzic or self.folder
	self.utworzono += 1
	return o
end

function Efekty:czesc(w: { [string]: any }): BasePart
	local p = Instance.new(w.Klasa or "Part")
	w.Klasa = nil
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Material = Enum.Material.Neon
	for k, v in w do
		(p :: any)[k] = v
	end
	p.Parent = self.folder
	self.utworzono += 1
	return p
end

function Efekty:dodaj(obj)
	table.insert(self.aktywne, obj)
	return obj
end

function Efekty:krok(d: number)
	for i = #self.aktywne, 1, -1 do
		local o = self.aktywne[i]
		local ok, zyje = pcall(o.krok, o, d)
		if not ok then
			warn("[TestWalki2] Efekt: " .. tostring(zyje))
			zyje = false
		end
		if not zyje then
			table.remove(self.aktywne, i)
			if o.zniszcz then
				pcall(o.zniszcz, o)
			end
		end
	end
	for _, oz in self.ozdoby do
		if oz.krok and not oz.zniszczona then
			pcall(oz.krok, oz, d)
		end
	end
end

function Efekty:wyczysc()
	for _, o in self.aktywne do
		if o.zniszcz then
			pcall(o.zniszcz, o)
		end
	end
	table.clear(self.aktywne)
	for _, oz in self.ozdoby do
		pcall(oz.zniszcz, oz)
	end
	table.clear(self.ozdoby)
	for _, p in self.wolne do
		p:Destroy()
	end
	table.clear(self.wolne)
end

-- Trail między dwoma zaczepami na części (smugi pocisków i broni)
function Efekty:trail(czesc: BasePart, a0: Vector3, a1: Vector3, kolor: Color3, zycie: number, szer: number?)
	local z0 = self:nowa("Attachment", { Position = a0 }, czesc)
	local z1 = self:nowa("Attachment", { Position = a1 }, czesc)
	local t = self:nowa("Trail", {
		Attachment0 = z0, Attachment1 = z1, Lifetime = zycie, Color = ColorSequence.new(kolor),
		Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.15), NumberSequenceKeypoint.new(1, 1) }),
		LightEmission = 0.6, FaceCamera = true, WidthScale = NumberSequence.new(szer or 1, 0.1), MinLength = 0.05,
	}, czesc)
	return t
end

-- emiter cząsteczek z domyślną (wbudowaną) teksturą
function Efekty:emiter(rodzic: Instance, w: { [string]: any }): ParticleEmitter
	local e = Instance.new("ParticleEmitter")
	e.LightEmission = 0.5
	for k, v in w do
		(e :: any)[k] = v
	end
	e.Parent = rodzic
	self.utworzono += 1
	return e
end

------------------------------------------------------------------ iskry i rozbłyski
function Efekty:iskra(): BasePart
	local p = table.remove(self.wolne)
	if not p then
		p = self:czesc({ Name = "Iskra", Size = Vector3.one * 0.4 })
	end
	p.Transparency = 0
	return p
end

-- rozprysk klocków: paleta kolorów, ile, prędkość, grawitacja
function Efekty:iskry(poz: Vector3, paleta: { Color3 }, ile: number, predkosc: number, skala: number?, grawitacja: number?)
	local s = skala or 1
	for _ = 1, ile do
		local p = self:iskra()
		local kier = Vector3.new(los:NextNumber(-1, 1), los:NextNumber(-0.1, 1), los:NextNumber(-1, 1)).Unit
		p.Color = paleta[los:NextInteger(1, #paleta)]
		local stan = {
			p = p, poz = poz, v = kier * predkosc * los:NextNumber(0.5, 1.15), wiek = 0, zycie = los:NextNumber(0.3, 0.55),
			rozmiar = los:NextNumber(0.25, 0.55) * s, g = grawitacja or 34,
			obrot = CFrame.Angles(los:NextNumber(0, 6), los:NextNumber(0, 6), los:NextNumber(0, 6)),
		}
		self:dodaj({
			krok = function(_, d)
				stan.wiek += d
				local u = stan.wiek / stan.zycie
				if u >= 1 then
					return false
				end
				stan.v += Vector3.new(0, -stan.g, 0) * d
				stan.poz += stan.v * d
				stan.p.Size = Vector3.one * math.max(stan.rozmiar * (1 - u * u), 0.05)
				stan.p.CFrame = CFrame.new(stan.poz) * stan.obrot
				return true
			end,
			zniszcz = function()
				stan.p.Transparency = 1
				table.insert(self.wolne, stan.p)
			end,
		})
	end
end

-- rozszerzająca się, gasnąca kula (rozbłysk)
function Efekty:kula(poz: Vector3, kolor: Color3, od: number, do_: number, czas: number, material: Enum.Material?, przezr: number?)
	local p = self:czesc({ Name = "Rozblysk", Shape = Enum.PartType.Ball, Size = Vector3.one * od, Color = kolor,
		Material = material or Enum.Material.Neon, Transparency = przezr or 0.15, CFrame = CFrame.new(poz) })
	local wiek = 0
	local p0 = przezr or 0.15
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local u = wiek / czas
			if u >= 1 then
				return false
			end
			local k = 1 - (1 - u) * (1 - u)
			p.Size = Vector3.one * (od + (do_ - od) * k)
			p.Transparency = p0 + (1 - p0) * u
			return true
		end,
		zniszcz = function()
			p:Destroy()
		end,
	})
end

-- fala uderzeniowa: płaski pierścień rozchodzący się po ziemi
function Efekty:fala(poz: Vector3, kolor: Color3, promien: number)
	local p = self:czesc({ Name = "Fala", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.25, 1, 1), Color = kolor,
		Material = Enum.Material.SmoothPlastic, Transparency = 0.1 })
	local p2 = self:czesc({ Name = "FalaKurz", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.18, 1, 1),
		Color = Color3.fromHex("#F0E2C0"), Material = Enum.Material.SmoothPlastic, Transparency = 0.3 })
	local wiek = 0
	local cf = CFrame.new(poz) * CFrame.Angles(0, 0, rad(90))
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local u = wiek / 0.5
			if u >= 1 then
				return false
			end
			local r = promien * (1 - (1 - u) ^ 3)
			p.Size = Vector3.new(0.25, r * 2, r * 2)
			p.CFrame = cf * CFrame.new(0.1, 0, 0)
			p.Transparency = 0.1 + 0.9 * u
			p2.Size = Vector3.new(0.18, r * 1.6, r * 1.6)
			p2.CFrame = cf * CFrame.new(0.2, 0, 0)
			p2.Transparency = 0.3 + 0.7 * u
			return true
		end,
		zniszcz = function()
			p:Destroy()
			p2:Destroy()
		end,
	})
end

-- krzyz = true (Zwijogon: cięcie lewą i prawą łapą): drugie trzy ślady w przeciwną stronę, tuż przed pierwszymi
function Efekty:pazury(cf: CFrame, kolor: Color3, rozmiar: number, krzyz: boolean?)
	local przed = self.utworzono
	local czesci = {}
	local katy = if krzyz then { 32, -32 } else { 32 }
	for nr, kat in katy do
		for i = -1, 1 do
			local p = self:czesc({ Name = "Pazur", Size = Vector3.new(0.18, rozmiar, 0.12), Color = kolor,
				CFrame = cf * CFrame.new(i * rozmiar * 0.22, 0, (nr - 1) * -0.08) * CFrame.Angles(0, 0, rad(kat)) })
			table.insert(czesci, p)
		end
	end
	self:zmierz("pazury", if krzyz then "krzyz" else "zwykle", przed)
	local wiek = 0
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local u = wiek / 0.45
			if u >= 1 then
				return false
			end
			for _, p in czesci do
				p.Transparency = u * u
			end
			return true
		end,
		zniszcz = function()
			for _, p in czesci do
				p:Destroy()
			end
		end,
	})
end

--[[ Ukąszenie (Dżungla, Wąż Stu Lian): cztery kły — dwa z góry, dwa z dołu — zatrzaskują się na celu w 0,1 s czasu
	sceny, trzymają i gasną (razem 0,5 s). cf = miejsce na piersi celu (jak przy pazurach). Paszcza stoi zawsze
	przodem do kamery, tuż przed celem od strony kamery — w ujęciu z boku kły ustawione do atakującego było widać
	tylko krawędzią (próba w Studio 18.11.2026). Kieł = klin z kości słoniowej (bez świecenia — świecące kły zlewały
	się w białe słupki): prosta krawędź na zewnątrz, czubek do środka paszczy; górne kły szerzej, dolne między nimi,
	po zatrzaśnięciu zachodzą na siebie. 4 części. ]]
function Efekty:ukaszenie(cf: CFrame, kolor: Color3, rozmiar: number)
	local przed = self.utworzono
	local dl = 0.75 * rozmiar
	local kly = {}
	for _, strona in { -1, 1 } do
		for _, gora in { -1, 1 } do
			local p = self:czesc({ Klasa = "WedgePart", Name = "KielUkaszenia", Size = Vector3.new(0.2, 0.45 * rozmiar, dl), Color = kolor,
				Material = Enum.Material.SmoothPlastic })
			-- klin: czubek to lokalne −Z, trójkąt leży w lokalnej płaszczyźnie YZ → obracamy go w płaszczyznę XY celu
			local vY = Vector3.new(-strona, 0, 0)
			local vZ = Vector3.new(0, gora, 0)
			table.insert(kly, { p = p, strona = strona, gora = gora, obrot = CFrame.fromMatrix(Vector3.zero, vY:Cross(vZ), vY, vZ) })
		end
	end
	self:zmierz("ukaszenie", "kly", przed)
	local wiek = 0
	local function ustaw()
		local zamkniecie = gladko(wiek / 0.1)
		local odl = dl * 0.35 + rozmiar * 0.8 * (1 - zamkniecie)
		local u = wiek / 0.5
		local kam = workspace.CurrentCamera
		local srodek = cf.Position
		local obrot = cf.Rotation
		if kam then
			obrot = kam.CFrame.Rotation
			local doKamery = kam.CFrame.Position - srodek
			if doKamery.Magnitude > 0.01 then
				srodek += doKamery.Unit * math.min(1.5, doKamery.Magnitude * 0.5)
			end
		end
		local baza = CFrame.new(srodek) * obrot
		for _, k in kly do
			-- górne kły na zewnątrz (0,6), dolne w środku (0,2) — zęby mijają się jak w paszczy
			local x = k.strona * rozmiar * (if k.gora > 0 then 0.6 else 0.2)
			k.p.CFrame = baza * CFrame.new(x, k.gora * odl, if k.gora > 0 then 0 else 0.1) * k.obrot
			k.p.Transparency = if u > 0.45 then math.clamp((u - 0.45) / 0.55, 0, 1) else 0
		end
	end
	ustaw()
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			if wiek >= 0.5 then
				return false
			end
			ustaw()
			return true
		end,
		zniszcz = function()
			for _, k in kly do
				k.p:Destroy()
			end
		end,
	})
end

--[[ Jednorazowy obłok drobin (Dżungla: osiadający pyłek, bąble jadu): `ile` cząsteczek naraz z niewidzialnego nośnika;
	nośnik (i z nim drobiny) znika po `czas` s czasu sceny. przysp = przyspieszenie drobin (w dół: osiadają, w górę:
	bąble). 1 część + 1 emiter. ]]
function Efekty:pyl(poz: Vector3, kolory: { Color3 }, ile: number, czas: number, przysp: Vector3, rozmiar: number)
	local nosnik = self:czesc({ Name = "PylNosnik", Size = Vector3.one * 0.3, Transparency = 1, CFrame = CFrame.new(poz) })
	local e = self:emiter(nosnik, { Color = ColorSequence.new(kolory[1], kolory[2] or kolory[1]), Rate = 0,
		Lifetime = NumberRange.new(czas * 0.55, czas * 0.9), Speed = NumberRange.new(1.5, 4), SpreadAngle = Vector2.new(180, 180),
		Acceleration = przysp, Drag = 2, Size = NumberSequence.new(rozmiar, rozmiar * 0.2), LightEmission = 0.4 })
	e:Emit(ile)
	local wiek = 0
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			return wiek < czas
		end,
		zniszcz = function()
			nosnik:Destroy()
		end,
	})
end

------------------------------------------------------------------ wybuchy (rozbłysk przy trafieniu)
Wybuch.iskra = function(fx, poz, s)
	fx:kula(poz, hex("#C08CFF"), 0.6 * s, 2.6 * s, 0.25)
	fx:iskry(poz, { hex("#C08CFF"), hex("#FFFFFF"), hex("#8A5CFF") }, 7, 11, 0.8 * s)
end
Wybuch.ogien = function(fx, poz, s)
	fx:kula(poz, hex("#FFE14A"), 1.0 * s, 4.2 * s, 0.22)
	fx:kula(poz, hex("#FF7A1F"), 1.4 * s, 6.0 * s, 0.42, nil, 0.25)
	fx:iskry(poz, { hex("#FFD23F"), hex("#FF8A1F"), hex("#E8364F") }, 14, 16, 1.2 * s)
end
Wybuch.lod = function(fx, poz, s)
	fx:kula(poz, hex("#E8FBFF"), 0.8 * s, 3.4 * s, 0.25)
	fx:iskry(poz, { hex("#BDF3FF"), hex("#FFFFFF"), hex("#6FD6FF") }, 12, 13, 1.0 * s, 20)
end
Wybuch.kwas = function(fx, poz, s)
	-- rozprysk bańki kwasu (D2: większy) — rozbłysk, krople w górę i na boki
	fx:kula(poz, hex("#C8FF7A"), 0.8 * s, 4.6 * s, 0.3, nil, 0.25)
	fx:kula(poz, hex("#9BF04A"), 1.2 * s, 6.0 * s, 0.5, Enum.Material.SmoothPlastic, 0.45)
	fx:iskry(poz, { hex("#9BF04A"), hex("#5FD13A"), hex("#DFFF9A") }, 22, 15, 1.25 * s, 36)
end
Wybuch.trucizna = function(fx, poz, s)
	fx:kula(poz, hex("#8BEA4E"), 0.5 * s, 2.4 * s, 0.3, nil, 0.35)
	fx:iskry(poz, { hex("#8BEA4E"), hex("#3E8C2A") }, 6, 8, 0.7 * s)
end
Wybuch.zarodniki = function(fx, poz, s)
	fx:kula(poz, hex("#B07CFF"), 1.0 * s, 4.6 * s, 0.55, Enum.Material.SmoothPlastic, 0.45)
	fx:iskry(poz, { hex("#D7B8FF"), hex("#B07CFF"), hex("#8BEA4E") }, 10, 6, 0.8 * s, 4)
end
Wybuch.kamien = function(fx, poz, s)
	fx:kula(poz, hex("#C9CED6"), 1.0 * s, 4.0 * s, 0.35, Enum.Material.SmoothPlastic, 0.4)
	fx:iskry(poz, { hex("#8D949C"), hex("#A9AFB6"), hex("#646B73") }, 12, 10, 1.3 * s, 30)
end
Wybuch.zloto = function(fx, poz, s)
	fx:kula(poz, hex("#FFE14A"), 1.0 * s, 4.5 * s, 0.4, nil, 0.35)
	fx:iskry(poz, { hex("#FFD23F"), hex("#FFF3B0") }, 12, 9, 0.8 * s, 6)
end
Wybuch.bariera = function(fx, poz, s)
	fx:kula(poz, hex("#6FE3FF"), 1.0 * s, 5.0 * s, 0.4, Enum.Material.ForceField, 0.1)
	fx:iskry(poz, { hex("#6FE3FF"), hex("#FFFFFF") }, 10, 9, 0.8 * s, 6)
end
Wybuch.blask = function(fx, poz, s)
	fx:kula(poz, hex("#FFFFFF"), 0.8 * s, 3.4 * s, 0.3, nil, 0.3)
end
Wybuch.cios = function(fx, poz, s)
	fx:iskry(poz, { hex("#FFFFFF"), hex("#FFD23F") }, 8, 12, s)
end
Wybuch.krytyk = function(fx, poz, s)
	fx:kula(poz, hex("#FFF3B0"), 0.6 * s, 3.2 * s, 0.2, nil, 0.2)
	fx:iskry(poz, { hex("#FFD23F"), hex("#FF8A1F"), hex("#FFFFFF") }, 16, 19, 1.35 * s)
end
Wybuch.blok = function(fx, poz, s)
	fx:iskry(poz, { hex("#3FF2D0"), hex("#FFFFFF"), hex("#27B6F2") }, 9, 12, s)
end
Wybuch.tarcza = function(fx, poz, s) -- tarcza pochłonęła cios
	fx:kula(poz, hex("#9FE8FF"), 1.2 * s, 3.0 * s, 0.25, Enum.Material.ForceField, 0.2)
end

-- Dżungla (18.11.2026) — rozbłyski własnych efektów potworów Dżungli
-- usypiający pyłek Gębokwiata: żółty kłąb rozchodzi się na celu, drobiny pyłku osiadają powoli w dół
Wybuch.pylek = function(fx, poz, s)
	fx:kula(poz, hex("#FFE14A"), 1.0 * s, 4.2 * s, 0.55, Enum.Material.SmoothPlastic, 0.45)
	fx:iskry(poz, { hex("#FFE14A"), hex("#FFF3B0"), hex("#F2C230") }, 8, 5, 0.7 * s, 5)
	fx:pyl(poz, { hex("#FFE14A"), hex("#FFF8D0") }, 26, 1.1, Vector3.new(0, -5, 0), 0.45 * s)
end
-- jad Węża Stu Lian: zielony rozprysk, krople na boki i bąble unoszące się z miejsca trafienia
Wybuch.jad = function(fx, poz, s)
	fx:kula(poz, hex("#C8FF7A"), 0.6 * s, 3.0 * s, 0.28, nil, 0.3)
	fx:kula(poz, hex("#5FD13A"), 0.9 * s, 4.2 * s, 0.45, Enum.Material.SmoothPlastic, 0.5)
	fx:iskry(poz, { hex("#8BEA4E"), hex("#5FD13A"), hex("#DFFF9A") }, 12, 11, 0.9 * s, 30)
	fx:pyl(poz, { hex("#B8F55A"), hex("#3E8C2A") }, 14, 0.9, Vector3.new(0, 3, 0), 0.4 * s)
end
-- ukąszenie Węża: krótki rozprysk krwi z kroplą jadu (same iskry z puli)
Wybuch.ukaszenie = function(fx, poz, s)
	fx:iskry(poz, { hex("#FF4A5E"), hex("#9E1020"), hex("#8BEA4E") }, 10, 11, 0.9 * s)
end
-- rozszarpanie Zwijogona: liście sypią się z trafionego (wolno opadają)
Wybuch.liscie = function(fx, poz, s)
	fx:kula(poz, hex("#6FBF3A"), 0.5 * s, 2.4 * s, 0.3, Enum.Material.SmoothPlastic, 0.5)
	fx:iskry(poz, { hex("#6FBF3A"), hex("#3E8C2A"), hex("#C8E86A"), hex("#FF5A3C") }, 10, 9, 0.9 * s, 12)
end
-- kokosy Kokosowego Siłacza: biały błysk miąższu i odłamki łupiny
Wybuch.kokos = function(fx, poz, s)
	fx:kula(poz, hex("#FFF6E0"), 0.6 * s, 2.8 * s, 0.22, nil, 0.2)
	fx:iskry(poz, { hex("#6B4423"), hex("#8A5A34"), hex("#FFF6E0"), hex("#4A2E18") }, 12, 13, 1.1 * s, 34)
end
-- Kamuflaż Zwijogona (Skupienie na siebie): zielony kłąb liści i złote iskry skupienia
Wybuch.kamuflaz = function(fx, poz, s)
	fx:kula(poz, hex("#6FBF3A"), 1.0 * s, 4.4 * s, 0.45, Enum.Material.SmoothPlastic, 0.5)
	fx:iskry(poz, { hex("#6FBF3A"), hex("#3E8C2A"), hex("#C8E86A"), hex("#FFD23F") }, 12, 8, 0.8 * s, 5)
end
-- Kamienna skóra Pancernika Ruin: turkusowy błysk rytów i odpryski starego kamienia
Wybuch.ruiny = function(fx, poz, s)
	fx:kula(poz, hex("#49E0D0"), 1.0 * s, 4.2 * s, 0.35, nil, 0.35)
	fx:kula(poz, hex("#8D949C"), 1.2 * s, 3.6 * s, 0.4, Enum.Material.SmoothPlastic, 0.45)
	fx:iskry(poz, { hex("#8D949C"), hex("#7C8A78"), hex("#49E0D0") }, 12, 10, 1.2 * s, 30)
end

function Efekty:wybuch(nazwa: string, poz: Vector3, skala: number?)
	local f = Wybuch[nazwa] or Wybuch.cios
	local przed = self.utworzono
	f(self, poz, skala or 1)
	self:zmierz("wybuch", if Wybuch[nazwa] then nazwa else "cios", przed)
end

--[[ Parada bez tarczy (v3: blok ma każda klasa i potwór): łuk „odbicia” z pięciu świecących klinów w poprzek ciosu,
	w punkcie przed bronią (albo piersią) broniącego, zwrócony do atakującego; rozchyla się i gaśnie w ok. 0,35 s
	czasu sceny. kier = kierunek od broniącego do atakującego. ]]
function Efekty:parada(punkt: Vector3, kier: Vector3, kolor: Color3, s: number)
	local poziomo = Vector3.new(kier.X, 0, kier.Z)
	if poziomo.Magnitude < 0.01 then
		poziomo = Vector3.new(0, 0, -1)
	end
	local cf = CFrame.lookAt(punkt, punkt + poziomo.Unit)
	local czesci = {}
	for i = 1, 5 do
		local kat = (i - 3) * 0.42
		local p = self:czesc({ Name = "Parada", Size = Vector3.new(0.12, 0.9, 0.22) * s, Color = kolor, Transparency = 0.1 })
		table.insert(czesci, { p = p, kat = kat })
	end
	local blysk = self:czesc({ Name = "ParadaBlysk", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.08, 1.6, 1.6) * s,
		Color = Color3.new(1, 1, 1), Transparency = 0.35 })
	local wiek = 0
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local u = wiek / 0.35
			if u >= 1 then
				return false
			end
			local r = (0.75 + 0.55 * u) * s
			for _, c in czesci do
				c.p.CFrame = cf * CFrame.Angles(0, 0, c.kat) * CFrame.new(0, r, 0) * CFrame.Angles(0, 0, -c.kat * 0.2)
				c.p.Transparency = 0.1 + 0.9 * u * u
			end
			blysk.CFrame = cf * CFrame.Angles(0, rad(90), 0)
			blysk.Size = Vector3.new(0.08, (1.6 + 1.4 * u) * s, (1.6 + 1.4 * u) * s)
			blysk.Transparency = 0.35 + 0.65 * u
			return true
		end,
		zniszcz = function()
			for _, c in czesci do
				c.p:Destroy()
			end
			blysk:Destroy()
		end,
	})
end

--[[ Wskrzeszenie (v3): słup złotego światła z góry na powalonego, krąg na ziemi i iskry unoszące się w górę;
	rośnie w 0,25 s, trzyma się i gaśnie pod koniec zdarzenia (czas = trwanie zdarzenia z dziennika, czas sceny). ]]
function Efekty:wskrzeszenie(cfZiemi: CFrame, szer: number, wys: number, kolor: Color3, czas: number)
	local r = math.max(1.4, szer * 0.6)
	local h = math.max(8, wys * 2.6)
	local slup = self:czesc({ Name = "Swiatlo", Shape = Enum.PartType.Cylinder, Size = Vector3.new(h, r * 2, r * 2), Color = kolor,
		Transparency = 1 })
	local rdzen = self:czesc({ Name = "SwiatloRdzen", Shape = Enum.PartType.Cylinder, Size = Vector3.new(h, r, r),
		Color = Color3.new(1, 1, 1), Transparency = 1 })
	local krag = self:czesc({ Name = "SwiatloKrag", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.12, r * 2.6, r * 2.6),
		Color = kolor, Transparency = 1 })
	local nosnik = self:czesc({ Name = "SwiatloIskry", Size = Vector3.one * 0.3, Transparency = 1, CFrame = cfZiemi })
	local e = self:emiter(nosnik, { Color = ColorSequence.new(kolor, Color3.new(1, 1, 1)), Rate = 40,
		Lifetime = NumberRange.new(0.6, 1.1), Speed = NumberRange.new(3, 6), SpreadAngle = Vector2.new(25, 25),
		Acceleration = Vector3.new(0, 4, 0), Size = NumberSequence.new(0.35, 0), LightEmission = 1 })
	e.EmissionDirection = Enum.NormalId.Top
	local swiatlo = self:nowa("PointLight", { Color = kolor, Range = 14, Brightness = 0, Shadows = false }, nosnik)
	local wiek = 0
	local srodek = cfZiemi * CFrame.new(0, h / 2, 0) * CFrame.Angles(0, 0, rad(90))
	local ziemia = cfZiemi * CFrame.new(0, 0.1, 0) * CFrame.Angles(0, 0, rad(90))
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local u = wiek / math.max(czas, 0.5)
			if u >= 1 then
				return false
			end
			local wej = gladko(u / 0.17)
			local wyj = 1 - gladko((u - 0.75) / 0.25)
			local k = wej * wyj
			slup.CFrame = srodek
			rdzen.CFrame = srodek
			slup.Transparency = 1 - 0.55 * k
			rdzen.Transparency = 1 - 0.75 * k
			krag.CFrame = ziemia * CFrame.Angles(wiek * 2, 0, 0)
			krag.Transparency = 1 - 0.7 * k
			nosnik.CFrame = cfZiemi
			swiatlo.Brightness = 3 * k
			e.Rate = if u < 0.8 then 40 else 0
			return true
		end,
		zniszcz = function()
			slup:Destroy()
			rdzen:Destroy()
			krag:Destroy()
			nosnik:Destroy()
		end,
	})
end

------------------------------------------------------------------ pociski
-- wspólny lot: część „glowa” (i doczepione) leci od → do w czasie sceny, po łuku (luk), obrócona wzdłuż lotu
local function lot(fx, czesci: { { BasePart | CFrame } }, od: Vector3, do_: Vector3, czas: number, opcje)
	local wiek = 0
	local luk = opcje.luk or 0
	local poprz = od
	local chybiony = opcje.chybiony
	local cel = do_
	if chybiony then
		-- pocisk mija cel (unik): leci dalej za plecy celu i gaśnie
		cel = do_ + (do_ - od).Unit * 6 + Vector3.new(0, 1.2, 0)
	elseif opcje.grot and opcje.grot > 0 then
		--[[ do_ = punkt na powierzchni celu, który ma trafić PRZÓD pocisku (grot strzały): środek pocisku kończy lot
			o grot studs przed nim wzdłuż stycznej łuku w chwili dolotu (styczna = (cel − od) − (0, 4·łuk, 0)), więc
			przy stromym strzale w kryształ Strażnika grot nie kończy ok. 1,2 studa pod punktem trafienia. ]]
		for _ = 1, 4 do
			local styczna = (cel - od) - Vector3.new(0, 4 * luk, 0)
			if styczna.Magnitude < 1e-3 then
				break
			end
			cel = do_ - styczna.Unit * opcje.grot
		end
	end
	local obr = opcje.obrot or 0
	local function ustaw(u: number)
		local p = od:Lerp(cel, u) + Vector3.new(0, luk * 4 * u * (1 - u), 0)
		local kier = p - poprz
		local cf
		if kier.Magnitude > 1e-3 then
			cf = CFrame.lookAt(p, p + kier)
		else
			cf = CFrame.lookAt(p, cel)
		end
		obr += opcje.wirowanie or 0
		cf *= CFrame.Angles(0, 0, obr)
		for _, c in czesci do
			(c[1] :: BasePart).CFrame = cf * (c[2] :: CFrame)
		end
		poprz = p
	end
	ustaw(0)
	-- światło pocisku gaśnie przy dolocie (przegląd 15.11: zielone światło strzały barwiło cały cel na blado)
	local swiatlo = opcje.swiatlo
	local jasnosc = swiatlo and swiatlo.Brightness or 0
	-- opcje.zostaw = s: pocisk zostaje wbity w cel (strzała) i jedzie za nim (opcje.przyczep() = CFrame celu)
	local wbity = nil
	return fx:dodaj({
		krok = function(_, d)
			wiek += d
			if wbity then
				local cf = opcje.przyczep and opcje.przyczep()
				local u2 = (wiek - czas) / opcje.zostaw
				for i, c in czesci do
					local p = c[1] :: BasePart
					if cf then
						p.CFrame = cf * wbity[i]
					end
					if u2 > 0.7 then
						p.LocalTransparencyModifier = math.clamp((u2 - 0.7) / 0.3, 0, 1)
					end
				end
				return u2 < 1
			end
			local u = math.min(wiek / math.max(czas, 0.01), 1)
			ustaw(if chybiony then u * 1.25 else u)
			if swiatlo then
				swiatlo.Brightness = jasnosc * (1 - gladko((u - 0.55) / 0.35))
			end
			if u >= 1 then
				if opcje.naKoniec then
					task.spawn(opcje.naKoniec)
				end
				if opcje.zostaw and not chybiony then
					local cf = opcje.przyczep and opcje.przyczep()
					wbity = {}
					for i, c in czesci do
						local p = c[1] :: BasePart
						wbity[i] = if cf then cf:ToObjectSpace(p.CFrame) else CFrame.identity
						for _, t in p:GetChildren() do
							if t:IsA("Trail") or t:IsA("Light") then
								t.Enabled = false
							end
						end
					end
					return true
				end
				return false
			end
			return true
		end,
		zniszcz = function()
			for _, c in czesci do
				(c[1] :: BasePart):Destroy()
			end
		end,
	})
end

Pocisk.iskra = function(fx, od, do_, czas, opcje)
	local g = fx:czesc({ Name = "PociskIskra", Shape = Enum.PartType.Ball, Size = Vector3.one * 0.75, Color = hex("#E2CCFF") })
	local o = fx:czesc({ Name = "PociskIskraPoswiata", Shape = Enum.PartType.Ball, Size = Vector3.one * 1.25, Color = hex("#9B5CFF"), Transparency = 0.45 })
	fx:trail(g, Vector3.new(0, 0.3, 0), Vector3.new(0, -0.3, 0), hex("#B07CFF"), 0.22)
	fx:nowa("PointLight", { Color = hex("#B07CFF"), Range = 8, Brightness = 2 }, g)
	return lot(fx, { { g, CFrame.identity }, { o, CFrame.identity } }, od, do_, czas, opcje)
end
-- strzała (poprawka D2): większa i czytelna jako strzała z daleka — jasne drzewce, świecący zielony grot (trucizna),
-- dwie czerwone lotki na krzyż, zielona smuga i poświata; leci 0,45–0,7 s lekkim łukiem
Pocisk.strzala = function(fx, od, do_, czas, opcje)
	local drzewce = fx:czesc({ Name = "Strzala", Size = Vector3.new(0.22, 0.22, 3.2), Color = hex("#E0B07A"), Material = Enum.Material.SmoothPlastic })
	local grot = fx:czesc({ Klasa = "WedgePart", Name = "StrzalaGrot", Size = Vector3.new(0.12, 0.55, 0.85), Color = hex("#8BEA4E") })
	local grot2 = fx:czesc({ Klasa = "WedgePart", Name = "StrzalaGrot", Size = Vector3.new(0.12, 0.55, 0.85), Color = hex("#8BEA4E") })
	local lotka = fx:czesc({ Name = "StrzalaLotka", Size = Vector3.new(0.75, 0.07, 0.7), Color = hex("#E8364F"), Material = Enum.Material.SmoothPlastic })
	local lotka2 = fx:czesc({ Name = "StrzalaLotka", Size = Vector3.new(0.07, 0.75, 0.7), Color = hex("#E8364F"), Material = Enum.Material.SmoothPlastic })
	fx:trail(drzewce, Vector3.new(0, 0.28, 1.4), Vector3.new(0, -0.28, 1.4), hex("#8BEA4E"), 0.4, 1.4)
	-- słabe światło o małym zasięgu, gaśnie przy dolocie (wcześniej Range 7 / Brightness 2,5 barwiło cały cel na zielono)
	opcje.swiatlo = fx:nowa("PointLight", { Color = hex("#8BEA4E"), Range = 3, Brightness = 1.2 }, grot)
	if opcje.luk == nil then
		opcje.luk = 0.7
	end
	-- dwa kliny (pełna ściana z tyłu, ostrze z przodu, −Z) tworzą grot w kształcie rombu
	return lot(fx, { { drzewce, CFrame.identity },
		{ grot, CFrame.new(0, 0.27, -1.9) },
		{ grot2, CFrame.new(0, -0.27, -1.9) * CFrame.Angles(0, 0, math.pi) },
		{ lotka, CFrame.new(0, 0, 1.3) }, { lotka2, CFrame.new(0, 0, 1.3) } }, od, do_, czas, opcje)
end
Pocisk.kula_ognia = function(fx, od, do_, czas, opcje)
	local g = fx:czesc({ Name = "KulaOgnia", Shape = Enum.PartType.Ball, Size = Vector3.one * 1.2, Color = hex("#FFE14A") })
	local o = fx:czesc({ Name = "KulaOgniaPlomien", Shape = Enum.PartType.Ball, Size = Vector3.one * 1.9, Color = hex("#FF7A1F"), Transparency = 0.35 })
	fx:nowa("Fire", { Size = 4, Heat = 0, Color = hex("#FF8A1F"), SecondaryColor = hex("#FFE14A") }, o)
	fx:nowa("PointLight", { Color = hex("#FF9A2E"), Range = 14, Brightness = 3 }, g)
	fx:trail(o, Vector3.new(0, 0.7, 0), Vector3.new(0, -0.7, 0), hex("#FF8A1F"), 0.3)
	opcje.wirowanie = 0.4
	return lot(fx, { { g, CFrame.identity }, { o, CFrame.identity } }, od, do_, czas, opcje)
end
Pocisk.lod = function(fx, od, do_, czas, opcje)
	local g = fx:czesc({ Name = "Lod", Size = Vector3.new(0.55, 0.55, 2.0), Color = hex("#BDF3FF"), Material = Enum.Material.Glass, Transparency = 0.15 })
	local r = fx:czesc({ Name = "LodRdzen", Size = Vector3.new(0.28, 0.28, 1.6), Color = hex("#FFFFFF") })
	fx:trail(g, Vector3.new(0.25, 0, 0.8), Vector3.new(-0.25, 0, 0.8), hex("#9FE8FF"), 0.28)
	fx:nowa("PointLight", { Color = hex("#9FE8FF"), Range = 8, Brightness = 2 }, r)
	opcje.wirowanie = 0.25
	return lot(fx, { { g, CFrame.Angles(0, 0, rad(45)) }, { r, CFrame.identity } }, od, do_, czas, opcje)
end
Pocisk.kwas = function(fx, od, do_, czas, opcje)
	local g = fx:czesc({ Name = "Kwas", Shape = Enum.PartType.Ball, Size = Vector3.one * 1.1, Color = hex("#9BF04A"), Transparency = 0.2 })
	local k = fx:czesc({ Name = "KwasKropla", Shape = Enum.PartType.Ball, Size = Vector3.one * 0.55, Color = hex("#DFFF9A") })
	fx:trail(g, Vector3.new(0, 0.4, 0), Vector3.new(0, -0.4, 0), hex("#7BE04A"), 0.25)
	return lot(fx, { { g, CFrame.identity }, { k, CFrame.new(0.2, 0.25, 0.3) } }, od, do_, czas, opcje)
end

-- Dżungla — usypiający pyłek Gębokwiata: żółta chmura pyłku (jasny środek i trzy kłęby krążące wokół osi lotu) płynie
-- łukiem do celu i sypie drobinami; bez światła i smugi. 4 części + 1 emiter.
Pocisk.pylek = function(fx, od, do_, czas, opcje)
	local g = fx:czesc({ Name = "Pylek", Shape = Enum.PartType.Ball, Size = Vector3.one * 1.2, Color = hex("#FFE98A"), Transparency = 0.1 })
	local ust = { { g, CFrame.identity } }
	for i = 1, 3 do
		local kat = (i - 1) / 3 * math.pi * 2
		local p = fx:czesc({ Name = "PylekKlab", Shape = Enum.PartType.Ball, Size = Vector3.one * (2.2 - i * 0.3),
			Color = hex(if i == 2 then "#FFF3B0" else "#F2C230"), Material = Enum.Material.SmoothPlastic, Transparency = 0.4 })
		table.insert(ust, { p, CFrame.new(math.cos(kat) * 0.8, math.sin(kat) * 0.8, 0.5 * (i - 1)) })
	end
	fx:emiter(g, { Color = ColorSequence.new(hex("#FFE14A"), hex("#FFF8D0")), Rate = 60, Lifetime = NumberRange.new(0.4, 0.8),
		Speed = NumberRange.new(0.5, 2), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, -3, 0),
		Size = NumberSequence.new(0.6, 0.05), LightEmission = 0.4 })
	if opcje.luk == nil then
		opcje.luk = 0.9
	end
	opcje.wirowanie = 0.12
	return lot(fx, ust, od, do_, czas, opcje)
end
-- Dżungla — jad Węża Stu Lian: zielona struga (duża kropla z jasnym środkiem i dwie mniejsze za nią), szeroka smuga
-- i kapiące krople; bez światła. 4 części + smuga (Trail i 2 zaczepy) + 1 emiter.
Pocisk.jad = function(fx, od, do_, czas, opcje)
	local g = fx:czesc({ Name = "Jad", Shape = Enum.PartType.Ball, Size = Vector3.one * 1.35, Color = hex("#8BEA4E"), Transparency = 0.1 })
	local r = fx:czesc({ Name = "JadSrodek", Shape = Enum.PartType.Ball, Size = Vector3.one * 0.7, Color = hex("#E4FF9A") })
	local k1 = fx:czesc({ Name = "JadKropla", Shape = Enum.PartType.Ball, Size = Vector3.one * 0.95, Color = hex("#5FD13A"), Transparency = 0.15 })
	local k2 = fx:czesc({ Name = "JadKropla", Shape = Enum.PartType.Ball, Size = Vector3.one * 0.6, Color = hex("#3E8C2A"), Transparency = 0.15 })
	fx:trail(g, Vector3.new(0, 0.6, 0), Vector3.new(0, -0.6, 0), hex("#7BE04A"), 0.35, 1.2)
	fx:emiter(g, { Color = ColorSequence.new(hex("#8BEA4E"), hex("#3E8C2A")), Rate = 30, Lifetime = NumberRange.new(0.3, 0.5),
		Speed = NumberRange.new(0.5, 1.5), SpreadAngle = Vector2.new(40, 40), Acceleration = Vector3.new(0, -22, 0),
		Size = NumberSequence.new(0.3, 0.08), LightEmission = 0.6 })
	if opcje.luk == nil then
		opcje.luk = 0.9
	end
	-- przód lotu to −Z: krople za główną kroplą są na +Z
	return lot(fx, { { g, CFrame.identity }, { r, CFrame.new(0, 0.05, -0.2) }, { k1, CFrame.new(0, 0, 1.0) },
		{ k2, CFrame.new(0, 0.05, 1.8) } }, od, do_, czas, opcje)
end

function Efekty:pocisk(nazwa: string, od: Vector3, do_: Vector3, czas: number, opcje: any?)
	local f = Pocisk[nazwa] or Pocisk.iskra
	local przed = self.utworzono
	local obiekt = f(self, od, do_, czas, opcje or {})
	self:zmierz("pocisk", if Pocisk[nazwa] then nazwa else "iskra", przed)
	return obiekt
end

------------------------------------------------------------------ chmura i korzenie
function Efekty:chmura(od: Vector3, do_: Vector3, czas: number, kolor: Color3)
	local kule = {}
	for i = 1, 6 do
		local p = self:czesc({ Name = "Chmura", Shape = Enum.PartType.Ball, Size = Vector3.one * 0.8, Color = kolor,
			Material = Enum.Material.SmoothPlastic, Transparency = 0.35 })
		kule[i] = { p = p, kat = los:NextNumber(0, 6.28), r = los:NextNumber(0.4, 1.2), y = los:NextNumber(-0.4, 0.6),
			s = los:NextNumber(1.6, 2.6), opoz = (i - 1) * 0.04 }
	end
	local nosnik = self:czesc({ Name = "ChmuraNosnik", Size = Vector3.one * 0.2, Transparency = 1 })
	self:emiter(nosnik, { Color = ColorSequence.new(kolor, hex("#8BEA4E")), Rate = 40, Lifetime = NumberRange.new(0.5, 0.9),
		Speed = NumberRange.new(1, 3), SpreadAngle = Vector2.new(180, 180), Size = NumberSequence.new(0.5, 0.1) })
	local wiek = 0
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local u = math.min(wiek / czas, 1)
			local srodek = od:Lerp(do_, gladko(u)) + Vector3.new(0, math.sin(u * math.pi) * 1.2, 0)
			nosnik.CFrame = CFrame.new(srodek)
			for _, k in kule do
				local uu = math.clamp((wiek - k.opoz) / czas, 0, 1)
				local rozm = k.s * (0.5 + uu * 0.8)
				k.p.Size = Vector3.one * rozm
				k.kat += d * 3
				k.p.CFrame = CFrame.new(srodek + Vector3.new(math.cos(k.kat) * k.r * (1 + uu), k.y, math.sin(k.kat) * k.r * (1 + uu)))
				k.p.Transparency = 0.35 + 0.4 * math.max(0, (wiek - czas) / 0.4)
			end
			return wiek < czas + 0.4
		end,
		zniszcz = function()
			for _, k in kule do
				k.p:Destroy()
			end
			nosnik:Destroy()
		end,
	})
end

-- korzenie wyrastają z ziemi wokół celu (kliny), trzymają, potem chowają się
function Efekty:korzenie(cfZiemi: CFrame, promien: number, kolor: Color3, czasWzrostu: number, czasTrwania: number, wysokosc: number)
	local pedy = {}
	local n = 7
	for i = 1, n do
		local kat = (i - 1) / n * math.pi * 2 + los:NextNumber(-0.2, 0.2)
		local dl = wysokosc * los:NextNumber(0.55, 0.9)
		local p = self:czesc({ Klasa = "WedgePart", Name = "Korzen", Size = Vector3.new(0.7, dl, 1.0), Color = kolor,
			Material = Enum.Material.Wood })
		local liscie = self:czesc({ Name = "KorzenLisc", Size = Vector3.new(0.6, 0.15, 0.6), Color = hex("#56B84A"),
			Material = Enum.Material.SmoothPlastic })
		pedy[i] = { p = p, l = liscie, kat = kat, dl = dl, r = promien * los:NextNumber(0.85, 1.1),
			nachyl = rad(los:NextNumber(18, 30)) }
	end
	local blask = self:czesc({ Name = "KorzenieBlask", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.12, promien * 2.4, promien * 2.4),
		Color = hex("#7CFF9B"), Transparency = 0.5, CFrame = cfZiemi * CFrame.new(0, 0.08, 0) * CFrame.Angles(0, 0, rad(90)) })
	local wiek = 0
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local wzrost
			if wiek < czasWzrostu then
				wzrost = gladko(wiek / czasWzrostu)
			elseif wiek < czasTrwania then
				wzrost = 1
			else
				wzrost = 1 - gladko((wiek - czasTrwania) / 0.35)
			end
			for _, pd in pedy do
				local h = math.max(pd.dl * wzrost, 0.05)
				local baza = cfZiemi * CFrame.Angles(0, pd.kat, 0) * CFrame.new(0, 0, pd.r)
				-- klin pochylony do środka (oplata cel)
				local cf = baza * CFrame.Angles(-pd.nachyl * wzrost, 0, 0) * CFrame.new(0, h / 2 - 0.2, 0)
				pd.p.Size = Vector3.new(0.7, h, 1.0)
				pd.p.CFrame = cf * CFrame.Angles(0, math.pi, 0)
				pd.l.CFrame = cf * CFrame.new(0, h / 2, 0.1)
				pd.l.Transparency = if wzrost > 0.6 then 0 else 1
			end
			blask.Transparency = 0.5 + 0.5 * (1 - wzrost)
			return wiek < czasTrwania + 0.35
		end,
		zniszcz = function()
			for _, pd in pedy do
				pd.p:Destroy()
				pd.l:Destroy()
			end
			blask:Destroy()
		end,
	})
end

------------------------------------------------------------------ smuga za bronią (Trail na kości z bronią)
function Efekty:smuga(aktor, kolor: Color3, czas: number)
	local punkt = aktor.model:FindFirstChild("Punkt_Bron", true)
	if not punkt or not punkt:IsA("Attachment") or not punkt.Parent or not punkt.Parent:IsA("BasePart") then
		return
	end
	local czesc = punkt.Parent :: BasePart
	-- drugi zaczep: na tej samej kości, bliżej środka części (wzdłuż broni)
	local p0 = punkt.Position
	local kier = if p0.Magnitude > 1e-3 then p0.Unit else Vector3.new(0, 1, 0)
	local p1 = p0 - kier * math.min(1.6, p0.Magnitude * 0.6)
	local t = self:trail(czesc, p0, p1, kolor, 0.2, 1)
	local wiek = 0
	self:dodaj({
		krok = function(_, d)
			wiek += d
			if wiek > czas then
				t.Enabled = false
			end
			return wiek < czas + 0.3
		end,
		zniszcz = function()
			if t.Attachment0 then
				t.Attachment0:Destroy()
			end
			if t.Attachment1 then
				t.Attachment1:Destroy()
			end
			t:Destroy()
		end,
	})
end

-- smuga za dowolną częścią (np. kością bańki kwasu z klipu slime'a) przez czas sceny
function Efekty:smugaCzesci(czesc: BasePart, kolor: Color3, czas: number, szer: number?)
	local s = szer or 0.4
	local t = self:trail(czesc, Vector3.new(0, s, 0), Vector3.new(0, -s, 0), kolor, 0.35, 1.3)
	t.LightEmission = 0.8
	-- poświata wokół (mała bańka z klipu z daleka ginie): świecąca kula idzie za częścią do końca lotu
	local aura = self:czesc({ Name = "SmugaPoswiata", Shape = Enum.PartType.Ball, Size = Vector3.one * (s * 3), Color = kolor,
		Transparency = 0.45, CFrame = czesc.CFrame })
	local wiek = 0
	self:dodaj({
		krok = function(_, d)
			wiek += d
			if wiek > czas then
				t.Enabled = false
				aura.Transparency = 1
			else
				aura.CFrame = CFrame.new(czesc.Position)
			end
			return wiek < czas + 0.4
		end,
		zniszcz = function()
			aura:Destroy()
			if t.Attachment0 then
				t.Attachment0:Destroy()
			end
			if t.Attachment1 then
				t.Attachment1:Destroy()
			end
			t:Destroy()
		end,
	})
end

--[[ Kałuża kwasu na ziemi (poprawka D2): płaski świecący dysk z jaśniejszym środkiem i bąblami — rośnie w 0,15 s,
	stoi `czas` sekund sceny (tyle, ile kałuża w klipie modelu), na końcu kurczy się i blednie. ]]
function Efekty:kaluza(poz: Vector3, promien: number, kolor: Color3, czas: number)
	local cf = CFrame.new(poz + Vector3.new(0, 0.05, 0)) * CFrame.Angles(0, 0, rad(90))
	local dysk = self:czesc({ Name = "KaluzaKwasu", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.1, 0.1, 0.1),
		Color = kolor, Material = Enum.Material.SmoothPlastic, Transparency = 0.1, CFrame = cf })
	local srodek = self:czesc({ Name = "KaluzaKwasuSrodek", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.1, 0.1, 0.1),
		Color = hex("#E4FF9A"), Material = Enum.Material.Neon, Transparency = 0.35, CFrame = cf * CFrame.new(0.03, 0, 0) })
	local plamy = {}
	for i = 1, 4 do
		local kat = (i - 1) / 4 * math.pi * 2 + los:NextNumber(-0.4, 0.4)
		local p = self:czesc({ Name = "KaluzaKwasuPlama", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.1, 0.1, 0.1),
			Color = kolor, Material = Enum.Material.SmoothPlastic, Transparency = 0.15 })
		plamy[i] = { p = p, off = Vector3.new(math.cos(kat), 0, math.sin(kat)) * promien * los:NextNumber(0.8, 1.05),
			r = promien * los:NextNumber(0.28, 0.42) }
	end
	local nosnik = self:czesc({ Name = "KaluzaKwasuBable", Size = Vector3.new(promien * 1.4, 0.1, promien * 1.4),
		Transparency = 1, CFrame = CFrame.new(poz + Vector3.new(0, 0.1, 0)) })
	local e = self:emiter(nosnik, { Color = ColorSequence.new(hex("#DFFF9A"), kolor), Rate = 14,
		Lifetime = NumberRange.new(0.3, 0.6), Speed = NumberRange.new(0.6, 1.4), SpreadAngle = Vector2.new(15, 15),
		EmissionDirection = Enum.NormalId.Top, Size = NumberSequence.new(0.25, 0.05), LightEmission = 0.7,
		Shape = Enum.ParticleEmitterShape.Box })
	local wiek = 0
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local rosnie = gladko(wiek / 0.15)
			local znika = if wiek > czas then gladko((wiek - czas) / 0.3) else 0
			local r = promien * rosnie * (1 - 0.35 * znika)
			dysk.Size = Vector3.new(0.1, r * 2, r * 2)
			dysk.CFrame = cf
			dysk.Transparency = 0.1 + 0.9 * znika
			srodek.Size = Vector3.new(0.11, r * 1.1, r * 1.1)
			srodek.Transparency = 0.35 + 0.65 * znika
			for _, pl in plamy do
				local rr = pl.r * rosnie * (1 - 0.35 * znika)
				pl.p.Size = Vector3.new(0.09, rr * 2, rr * 2)
				pl.p.CFrame = CFrame.new(poz + pl.off * rosnie + Vector3.new(0, 0.045, 0)) * CFrame.Angles(0, 0, rad(90))
				pl.p.Transparency = 0.15 + 0.85 * znika
			end
			e.Enabled = znika < 0.5
			return wiek < czas + 0.3
		end,
		zniszcz = function()
			dysk:Destroy()
			srodek:Destroy()
			for _, pl in plamy do
				pl.p:Destroy()
			end
			nosnik:Destroy()
		end,
	})
end

------------------------------------------------------------------ trwałe ozdoby efektów na postaci (Wyglad.<nazwa>)
-- nośnik: niewidzialna część, która co klatkę idzie za piersią (albo stopami / głową) aktora
local function ozdoba(fx, aktor, gdzie: string)
	local o = { aktor = aktor, czesci = {}, zniszczona = false, wiek = 0, pulsy = 0 }
	o.nosnik = fx:czesc({ Name = "OzdobaNosnik", Size = Vector3.one * 0.3, Transparency = 1 })
	function o:pozycja(): CFrame
		local a = self.aktor
		if gdzie == "glowa" then
			return a:cfZiemi() * CFrame.new(0, a.wpis.wysokosc + 0.3, 0)
		elseif gdzie == "stopy" then
			return a:cfZiemi() * CFrame.new(0, 0.1, 0)
		end
		return a:punkt("Piers") or (a:cfZiemi() * CFrame.new(0, a.wpis.wysokosc * 0.55, 0))
	end
	function o:zniszcz()
		if self.zniszczona then
			return
		end
		self.zniszczona = true
		for _, c in self.czesci do
			c:Destroy()
		end
		self.nosnik:Destroy()
	end
	function o:puls()
		self.pulsy = 0.35
	end
	return o
end

local function zarejestruj(fx, o)
	o.nosnik.CFrame = o:pozycja()
	table.insert(fx.ozdoby, o)
	return o
end

Wyglad.babelki = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local h = aktor.wpis.wysokosc
	local e = fx:emiter(o.nosnik, { Color = ColorSequence.new(hex("#8BEA4E"), hex("#3E8C2A")), Rate = 14,
		Lifetime = NumberRange.new(0.6, 1.1), Speed = NumberRange.new(1.5, 3), SpreadAngle = Vector2.new(35, 35),
		Acceleration = Vector3.new(0, 2, 0), Size = NumberSequence.new(0.35 * math.max(1, h / 6), 0.05), LightEmission = 0.8 })
	function o:krok(d)
		self.nosnik.CFrame = self:pozycja()
		if self.pulsy > 0 then
			self.pulsy -= d
			e.Rate = 45
		else
			e.Rate = 14
		end
	end
	return zarejestruj(fx, o)
end
Wyglad.ogien = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local h = aktor.wpis.wysokosc
	local ogien = fx:nowa("Fire", { Size = math.clamp(h * 0.55, 2.5, 7), Heat = 6, Color = hex("#FF7A1F"), SecondaryColor = hex("#FFE14A") }, o.nosnik)
	function o:krok(d)
		self.nosnik.CFrame = self:pozycja()
		if self.pulsy > 0 then
			self.pulsy -= d
			ogien.Size = math.clamp(h * 0.9, 4, 10)
		else
			ogien.Size = math.clamp(h * 0.55, 2.5, 7)
		end
	end
	return zarejestruj(fx, o)
end
Wyglad.krople = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local e = fx:emiter(o.nosnik, { Color = ColorSequence.new(hex("#FF2E45"), hex("#9E1020")), Rate = 9,
		Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(1, 3), SpreadAngle = Vector2.new(60, 60),
		Acceleration = Vector3.new(0, -25, 0), Size = NumberSequence.new(0.3, 0.12), LightEmission = 0.2 })
	function o:krok(d)
		self.nosnik.CFrame = self:pozycja()
		if self.pulsy > 0 then
			self.pulsy -= d
			e.Rate = 40
		else
			e.Rate = 9
		end
	end
	return zarejestruj(fx, o)
end
Wyglad.gwiazdki = function(fx, aktor)
	local o = ozdoba(fx, aktor, "glowa")
	local s = math.clamp(aktor.wpis.wysokosc / 6, 0.7, 1.8)
	local gw = {}
	for i = 1, 3 do
		local p = fx:czesc({ Name = "Gwiazdka", Size = Vector3.new(0.5, 0.5, 0.18) * s, Color = hex("#FFE14A") })
		local p2 = fx:czesc({ Name = "Gwiazdka", Size = Vector3.new(0.5, 0.5, 0.18) * s, Color = hex("#FFE14A") })
		table.insert(o.czesci, p)
		table.insert(o.czesci, p2)
		gw[i] = { p, p2 }
	end
	function o:krok(d)
		self.wiek += d
		local cf = self:pozycja()
		self.nosnik.CFrame = cf
		for i, g in gw do
			local kat = self.wiek * 4 + i * 2.09
			local c = cf * CFrame.new(math.cos(kat) * 1.1 * s, math.sin(self.wiek * 6 + i) * 0.15, math.sin(kat) * 1.1 * s)
			g[1].CFrame = c * CFrame.Angles(0, self.wiek * 3, 0)
			g[2].CFrame = c * CFrame.Angles(0, self.wiek * 3, rad(45))
		end
	end
	return zarejestruj(fx, o)
end
-- spowolnienie od lodowego pocisku: lodowe kryształy przy nogach, szron unoszący się z ciała, lód pod stopami
Wyglad.lod = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local w = aktor.wpis
	local h = w.wysokosc
	local r = math.max(w.szerokosc, w.glebokosc) * 0.42 + 0.4
	local s = math.clamp(h / 6, 0.7, 1.8)
	local krysztaly = {}
	for i = 1, 5 do
		local p = fx:czesc({ Klasa = "WedgePart", Name = "Krysztal", Size = Vector3.new(0.35, 1.3, 0.6) * s * los:NextNumber(0.8, 1.2),
			Color = hex(if i % 2 == 0 then "#CFF6FF" else "#9FE8FF"), Material = Enum.Material.Glass, Transparency = 0.25 })
		table.insert(o.czesci, p)
		krysztaly[i] = { p = p, kat = (i - 1) / 5 * 6.283 + los:NextNumber(-0.3, 0.3), pochyl = los:NextNumber(0.2, 0.5) }
	end
	local lod = fx:czesc({ Name = "LodStopy", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.3, r * 2, r * 2), Color = hex("#9FE8FF"),
		Material = Enum.Material.Glass, Transparency = 0.35 })
	table.insert(o.czesci, lod)
	local e = fx:emiter(o.nosnik, { Color = ColorSequence.new(hex("#FFFFFF"), hex("#9FE8FF")), Rate = 8,
		Lifetime = NumberRange.new(0.7, 1.2), Speed = NumberRange.new(0.5, 1.5), SpreadAngle = Vector2.new(180, 180),
		Acceleration = Vector3.new(0, 1.5, 0), Size = NumberSequence.new(0.25 * s, 0), LightEmission = 0.6 })
	function o:krok(d)
		self.nosnik.CFrame = self:pozycja()
		local stopy = self.aktor:cfZiemi()
		lod.CFrame = stopy * CFrame.new(0, 0.15, 0) * CFrame.Angles(0, 0, rad(90))
		for _, k in krysztaly do
			k.p.CFrame = stopy * CFrame.Angles(0, k.kat, 0) * CFrame.new(0, k.p.Size.Y * 0.4, -r) * CFrame.Angles(-k.pochyl, 0, 0)
		end
		if self.pulsy > 0 then
			self.pulsy -= d
			e.Rate = 35
		else
			e.Rate = 8
		end
	end
	return zarejestruj(fx, o)
end

-- spowolnienie od uścisku korzeni: pnącza owinięte wokół nóg (kołyszą się) i liście
Wyglad.pnacza = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local w = aktor.wpis
	local h = w.wysokosc
	local r = math.max(w.szerokosc, w.glebokosc) * 0.4 + 0.25
	local s = math.clamp(h / 6, 0.7, 1.8)
	local pnacza = {}
	for i = 1, 6 do
		local lisc = i % 2 == 0
		local p = fx:czesc({ Klasa = if lisc then "WedgePart" else "Part", Name = if lisc then "Lisc" else "Pnacze",
			Size = if lisc then Vector3.new(0.12, 0.45, 0.7) * s else Vector3.new(0.3, 0.3, r * 1.6) * Vector3.new(s, s, 1),
			Color = hex(if lisc then "#6FBF3A" else "#5A3A22"), Material = Enum.Material.SmoothPlastic })
		table.insert(o.czesci, p)
		pnacza[i] = { p = p, kat = (i - 1) / 6 * 6.283, y = (0.15 + 0.12 * ((i - 1) % 3)) * math.min(h, 6), lisc = lisc }
	end
	function o:krok(d)
		self.wiek += d
		self.nosnik.CFrame = self:pozycja()
		local stopy = self.aktor:cfZiemi()
		local p = 0
		if self.pulsy > 0 then
			self.pulsy -= d
			p = self.pulsy
		end
		for _, k in pnacza do
			local kat = k.kat + math.sin(self.wiek * 2 + k.kat) * 0.12
			local promien = r * (1 - p * 0.3) + (if k.lisc then 0.15 else 0)
			k.p.CFrame = stopy * CFrame.Angles(0, kat, 0) * CFrame.new(promien, k.y, 0) * CFrame.Angles(0, 0, rad(if k.lisc then 30 else 12))
		end
	end
	return zarejestruj(fx, o)
end

Wyglad.odlamki = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local e = fx:emiter(o.nosnik, { Color = ColorSequence.new(hex("#B9BEC4"), hex("#8A5A34")), Rate = 7,
		Lifetime = NumberRange.new(0.6, 1.0), Speed = NumberRange.new(2, 4), SpreadAngle = Vector2.new(70, 70),
		Acceleration = Vector3.new(0, -20, 0), Size = NumberSequence.new(0.35, 0.2), LightEmission = 0, Rotation = NumberRange.new(0, 360),
		RotSpeed = NumberRange.new(-200, 200) })
	local s = math.clamp(aktor.wpis.wysokosc / 6, 0.7, 1.8)
	-- pęknięta tarczka krąży nad głową: znak „pancerz zdarty”
	local a = fx:czesc({ Klasa = "WedgePart", Name = "Pekniecie", Size = Vector3.new(0.12, 0.8, 0.45) * s, Color = hex("#D9A066"), Material = Enum.Material.SmoothPlastic })
	local b = fx:czesc({ Klasa = "WedgePart", Name = "Pekniecie", Size = Vector3.new(0.12, 0.8, 0.45) * s, Color = hex("#B9BEC4"), Material = Enum.Material.SmoothPlastic })
	table.insert(o.czesci, a)
	table.insert(o.czesci, b)
	function o:krok(d)
		self.wiek += d
		self.nosnik.CFrame = self:pozycja()
		local glowa = self.aktor:cfZiemi() * CFrame.new(0, self.aktor.wpis.wysokosc + 0.7 * s, 0) * CFrame.Angles(0, self.wiek * 1.5, 0)
		local rozchyl = 0.12 + 0.08 * math.sin(self.wiek * 5)
		a.CFrame = glowa * CFrame.new(-0.25 * s - rozchyl, 0, 0) * CFrame.Angles(0, math.pi / 2, 0)
		b.CFrame = glowa * CFrame.new(0.25 * s + rozchyl, 0, 0) * CFrame.Angles(0, -math.pi / 2, 0)
		if self.pulsy > 0 then
			self.pulsy -= d
			e.Rate = 30
		else
			e.Rate = 7
		end
	end
	return zarejestruj(fx, o)
end
Wyglad.kamienie = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local h = aktor.wpis.wysokosc
	local r = math.max(aktor.wpis.szerokosc, aktor.wpis.glebokosc, h * 0.6) * 0.55 + 0.6
	local kamienie = {}
	for i = 1, 6 do
		local s = los:NextNumber(0.5, 0.85) * math.clamp(h / 6, 0.8, 1.8)
		local p = fx:czesc({ Name = "Kamien", Size = Vector3.new(s * 1.2, s, s), Color = hex(if i % 2 == 0 then "#A9AFB6" else "#8D949C"),
			Material = Enum.Material.Slate })
		table.insert(o.czesci, p)
		kamienie[i] = { p = p, kat = (i - 1) / 6 * 6.283, y = (i % 3 - 1) * h * 0.22 }
	end
	local skorupa = fx:czesc({ Name = "KamiennaPowloka", Shape = Enum.PartType.Ball, Size = Vector3.one * r * 2, Color = hex("#C9CED6"),
		Material = Enum.Material.ForceField, Transparency = 0.2 })
	table.insert(o.czesci, skorupa)
	function o:krok(d)
		self.wiek += d
		local cf = self:pozycja()
		self.nosnik.CFrame = cf
		local srodek = self.aktor:cfZiemi() * CFrame.new(0, h * 0.5, 0)
		skorupa.CFrame = srodek
		local p = 0
		if self.pulsy > 0 then
			self.pulsy -= d
			p = self.pulsy
		end
		skorupa.Size = Vector3.one * (r * 2 * (1 + p * 0.3))
		for _, k in kamienie do
			local kat = k.kat + self.wiek * 1.6
			k.p.CFrame = srodek * CFrame.new(math.cos(kat) * r * 0.95, k.y, math.sin(kat) * r * 0.95) * CFrame.Angles(kat, kat * 0.7, 0)
		end
	end
	return zarejestruj(fx, o)
end
Wyglad.banka = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local h = aktor.wpis.wysokosc
	local r = math.max(aktor.wpis.szerokosc, aktor.wpis.glebokosc, h) * 0.58 + 0.5
	local b = fx:czesc({ Name = "Banka", Shape = Enum.PartType.Ball, Size = Vector3.one * r * 2, Color = hex("#6FE3FF"),
		Material = Enum.Material.ForceField, Transparency = 0 })
	table.insert(o.czesci, b)
	function o:krok(d)
		self.wiek += d
		self.nosnik.CFrame = self:pozycja()
		local p = 0
		if self.pulsy > 0 then
			self.pulsy -= d
			p = self.pulsy
		end
		b.Size = Vector3.one * r * 2 * (1 + 0.03 * math.sin(self.wiek * 4) + p * 0.35)
		b.CFrame = self.aktor:cfZiemi() * CFrame.new(0, h * 0.5, 0)
	end
	return zarejestruj(fx, o)
end
Wyglad.blask = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local r = math.max(aktor.wpis.szerokosc, aktor.wpis.glebokosc) * 0.5 + 0.6
	local krag = fx:czesc({ Name = "BlaskKrag", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.12, r * 2, r * 2), Color = hex("#FFD23F"),
		Transparency = 0.2 })
	local wew = fx:czesc({ Name = "BlaskKragW", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.14, r * 1.6, r * 1.6), Color = hex("#5A3A22"),
		Material = Enum.Material.SmoothPlastic, Transparency = 0.3 })
	table.insert(o.czesci, krag)
	table.insert(o.czesci, wew)
	fx:emiter(o.nosnik, { Color = ColorSequence.new(hex("#FFE14A"), hex("#FFFFFF")), Rate = 10, Lifetime = NumberRange.new(0.6, 1.0),
		Speed = NumberRange.new(1, 2), SpreadAngle = Vector2.new(180, 180), Size = NumberSequence.new(0.3, 0), LightEmission = 1 })
	function o:krok(d)
		self.wiek += d
		self.nosnik.CFrame = self:pozycja()
		local stopy = self.aktor:cfZiemi() * CFrame.new(0, 0.12, 0) * CFrame.Angles(0, self.wiek, rad(90))
		krag.CFrame = stopy
		wew.CFrame = stopy * CFrame.new(0.01, 0, 0)
		krag.Transparency = 0.2 + 0.25 * (0.5 + 0.5 * math.sin(self.wiek * 5))
	end
	return zarejestruj(fx, o)
end

------------------------------------------------------------------ Dżungla (18.11.2026): ozdoby własnych efektów
--[[ Spowolnienie od usypiającego pyłku Gębokwiata: trzy klockowe „Z” wypływają znad głowy, rosną i gasną (zawsze
	przodem do kamery), a żółty pyłek osiada wokół głowy. Litery mają kolor statusu (jak ikona i napis
	„SPOWOLNIENIE!”), pyłek — kolor pocisku. Puls (tyknięcie): litery płyną szybciej. 9 części + nośnik + 1 emiter. ]]
Wyglad.sen = function(fx, aktor)
	local o = ozdoba(fx, aktor, "glowa")
	local s = math.clamp(aktor.wpis.wysokosc / 6, 0.7, 1.8)
	local litery = {}
	for i = 1, 3 do
		local belki = {}
		for j = 1, 3 do
			local p = fx:czesc({ Name = "SenZ", Size = Vector3.new(0.6, 0.14, 0.12) * s, Color = hex("#9FE8FF"), Transparency = 1 })
			table.insert(o.czesci, p)
			belki[j] = p
		end
		litery[i] = { belki = belki, faza = (i - 1) / 3 }
	end
	local e = fx:emiter(o.nosnik, { Color = ColorSequence.new(hex("#FFE14A"), hex("#FFF8D0")), Rate = 9,
		Lifetime = NumberRange.new(0.8, 1.3), Speed = NumberRange.new(0.5, 1.5), SpreadAngle = Vector2.new(180, 180),
		Acceleration = Vector3.new(0, -4, 0), Size = NumberSequence.new(0.3 * s, 0), LightEmission = 0.4 })
	local bieg = 0
	function o:krok(d)
		self.wiek += d
		local cf = self:pozycja()
		self.nosnik.CFrame = cf
		local szybkosc = 0.55
		if self.pulsy > 0 then
			self.pulsy -= d
			szybkosc = 1.6
			e.Rate = 30
		else
			e.Rate = 9
		end
		bieg += d * szybkosc
		local kam = workspace.CurrentCamera
		local obrot = if kam then kam.CFrame.Rotation else CFrame.identity
		for _, l in litery do
			local u = (bieg + l.faza) % 1
			local k = (0.55 + 0.75 * u) * s
			-- litera odpływa w górę i w prawo (w kadrze), rośnie; pojawia się w pierwszych 15% drogi, gaśnie od 70%
			local srodek = CFrame.new(cf.Position + Vector3.new(0, (0.3 + 1.9 * u) * s, 0)) * obrot * CFrame.new((0.5 + 1.0 * u) * s, 0, 0)
			local widac = math.min(1, u / 0.15) * (1 - gladko((u - 0.7) / 0.3))
			local b = l.belki
			b[1].Size = Vector3.new(0.6, 0.14, 0.12) * k
			b[1].CFrame = srodek * CFrame.new(0, 0.28 * k, 0)
			b[2].Size = Vector3.new(0.6, 0.14, 0.12) * k
			b[2].CFrame = srodek * CFrame.new(0, -0.28 * k, 0)
			b[3].Size = Vector3.new(0.8, 0.14, 0.12) * k
			b[3].CFrame = srodek * CFrame.Angles(0, 0, rad(43))
			for _, p in b do
				p.Transparency = 1 - widac
			end
		end
	end
	return zarejestruj(fx, o)
end

--[[ Skupienie Zwijogona („Kamuflaż”): sześć liści krąży wokół ciała w dwóch pierścieniach (wtapia się w gąszcz), pod
	stopami złota obręcz w kolorze statusu. Puls: liście przyspieszają. 7 części + nośnik. ]]
Wyglad.kamuflaz = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local w = aktor.wpis
	local h = w.wysokosc
	local r = math.max(w.szerokosc, w.glebokosc) * 0.5 + 0.5
	local s = math.clamp(h / 6, 0.7, 1.8)
	local liscie = {}
	for i = 1, 6 do
		local p = fx:czesc({ Klasa = "WedgePart", Name = "LiscKamuflazu", Size = Vector3.new(0.14, 0.75, 1.35) * s,
			Color = hex(if i % 3 == 0 then "#E6F58A" elseif i % 2 == 0 then "#9BD94A" else "#C8E86A"),
			Material = Enum.Material.SmoothPlastic })
		table.insert(o.czesci, p)
		liscie[i] = { p = p, kat = (i - 1) / 6 * 6.283, y = (0.28 + 0.42 * ((i - 1) % 2)) * h }
	end
	local krag = fx:czesc({ Name = "KamuflazKrag", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.1, r * 2, r * 2),
		Color = hex("#FFD23F"), Transparency = 0.25 })
	table.insert(o.czesci, krag)
	local obieg = 0
	function o:krok(d)
		self.wiek += d
		self.nosnik.CFrame = self:pozycja()
		local stopy = self.aktor:cfZiemi()
		local tempo = 1.8
		if self.pulsy > 0 then
			self.pulsy -= d
			tempo = 6
		end
		obieg += d * tempo
		krag.CFrame = stopy * CFrame.new(0, 0.1, 0) * CFrame.Angles(0, 0, rad(90))
		krag.Transparency = 0.3 + 0.15 * math.sin(self.wiek * 4)
		for _, l in liscie do
			local kat = l.kat + obieg
			l.p.CFrame = stopy * CFrame.Angles(0, kat, 0) * CFrame.new(r, l.y + math.sin(self.wiek * 3 + l.kat) * 0.2, 0)
				* CFrame.Angles(rad(25), rad(90), 0)
		end
	end
	return zarejestruj(fx, o)
end

--[[ Kamienna skóra Pancernika Ruin: cztery płyty starego kamienia krążą wolno wokół ciała, na każdej świeci
	turkusowy ryt (jak szczeliny modelu); turkusowa powłoka jak przy kamiennej skórze bohatera. Puls (cios w tarczę):
	powłoka rośnie. 9 części + nośnik. ]]
Wyglad.ruiny = function(fx, aktor)
	local o = ozdoba(fx, aktor, "piers")
	local h = aktor.wpis.wysokosc
	local r = math.max(aktor.wpis.szerokosc, aktor.wpis.glebokosc, h * 0.6) * 0.55 + 0.6
	local s = math.clamp(h / 6, 0.8, 1.8)
	local plyty = {}
	for i = 1, 4 do
		local p = fx:czesc({ Name = "PlytaRuin", Size = Vector3.new(1.5, 1.9, 0.35) * s,
			Color = hex(if i % 2 == 0 then "#8D949C" else "#7C8A78"), Material = Enum.Material.Slate })
		local ryt = fx:czesc({ Name = "PlytaRuinRyt", Size = Vector3.new(0.16, 1.3, 0.1) * s, Color = hex("#49E0D0") })
		table.insert(o.czesci, p)
		table.insert(o.czesci, ryt)
		plyty[i] = { p = p, ryt = ryt, kat = (i - 1) / 4 * 6.283, y = (if i % 2 == 0 then 0.12 else -0.12) * h }
	end
	local powloka = fx:czesc({ Name = "PowlokaRuin", Shape = Enum.PartType.Ball, Size = Vector3.one * r * 2, Color = hex("#49E0D0"),
		Material = Enum.Material.ForceField, Transparency = 0.2 })
	table.insert(o.czesci, powloka)
	function o:krok(d)
		self.wiek += d
		self.nosnik.CFrame = self:pozycja()
		local srodek = self.aktor:cfZiemi() * CFrame.new(0, h * 0.5, 0)
		local p = 0
		if self.pulsy > 0 then
			self.pulsy -= d
			p = self.pulsy
		end
		powloka.CFrame = srodek
		powloka.Size = Vector3.one * (r * 2 * (1 + p * 0.3))
		for _, pl in plyty do
			local cf = srodek * CFrame.Angles(0, pl.kat + self.wiek * 0.9, 0) * CFrame.new(0, pl.y, -r * 0.95)
			pl.p.CFrame = cf
			pl.ryt.CFrame = cf * CFrame.new(0, 0, -0.2 * s)
		end
	end
	return zarejestruj(fx, o)
end

function Efekty:wyglad(nazwa: string, aktor)
	local f = Wyglad[nazwa] or Wyglad.blask
	local przed = self.utworzono
	local o = f(self, aktor)
	self:zmierz("wyglad", if Wyglad[nazwa] then nazwa else "blask", przed)
	return o
end

------------------------------------------------------------------ łup wysypany z pokonanego
function Efekty:lup(zrodlo: Vector3, cel: Vector3, lup, natychmiast: boolean, podloga: number)
	local przedmioty = {}
	local function dodaj(czesci, celP: Vector3, wys: number, opoz: number, trwa: number, wiruje: boolean, kolysze: boolean)
		table.insert(przedmioty, { czesci = czesci, start = zrodlo, cel = celP, wys = wys, opoz = opoz, trwa = trwa,
			wiek = if natychmiast then 99 else 0, wiruje = wiruje, kolysze = kolysze, obrot = CFrame.Angles(0, los:NextNumber(0, 6), 0) })
	end
	local function rozsyp(r1: number, r2: number): Vector3
		local kat = los:NextNumber(0, math.pi * 2)
		local r = los:NextNumber(r1, r2)
		local p = cel + Vector3.new(math.cos(kat) * r, 0, math.sin(kat) * r)
		return Vector3.new(p.X, podloga, p.Z)
	end
	local monet = math.clamp(math.floor((lup.zloto or 0) / 12), if (lup.zloto or 0) > 0 then 4 else 0, 12)
	for i = 1, monet do
		local m = self:czesc({ Name = "Moneta", Size = Vector3.new(0.85, 0.24, 0.85), Color = if i % 3 == 0 then hex("#FFE98A") else hex("#FFD23F"),
			Material = Enum.Material.SmoothPlastic })
		dodaj({ { m, CFrame.new(0, 0.12, 0) } }, rozsyp(1.0, 3.4), los:NextNumber(2.6, 4.6), (i - 1) * 0.035, los:NextNumber(0.5, 0.7), true, false)
	end
	for i = 1, (lup.tokeny_krainy or 0) do
		local t = self:czesc({ Name = "Zeton", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.25, 1.0, 1.0), Color = hex("#52D273"),
			Material = Enum.Material.SmoothPlastic })
		local l = self:czesc({ Name = "ZetonLisc", Size = Vector3.new(0.3, 0.12, 0.55), Color = hex("#1F5A36"), Material = Enum.Material.SmoothPlastic })
		dodaj({ { t, CFrame.new(0, 0.13, 0) * CFrame.Angles(0, 0, rad(90)) }, { l, CFrame.new(0, 0.27, 0) * CFrame.Angles(0, rad(30), 0) } },
			rozsyp(1.5, 3.0), 4.0, 0.2 + i * 0.06, 0.65, true, false)
	end
	if (lup.gemy or 0) > 0 then
		local g = self:czesc({ Name = "Gem", Size = Vector3.new(0.9, 0.9, 0.9), Color = hex("#C04DFF"), Material = Enum.Material.Glass, Transparency = 0.1 })
		local g2 = self:czesc({ Name = "GemSrodek", Size = Vector3.new(0.5, 0.5, 0.5), Color = hex("#F0C8FF") })
		dodaj({ { g, CFrame.new(0, 0.9, 0) * CFrame.Angles(rad(45), 0, rad(45)) }, { g2, CFrame.new(0, 0.9, 0) * CFrame.Angles(rad(45), 0, rad(45)) } },
			rozsyp(0.6, 1.6), 5.0, 0.3, 0.75, false, true)
	end
	if (lup.shard_ewolucji or 0) > 0 then
		local s = self:czesc({ Name = "Shard", Size = Vector3.new(0.6, 1.8, 0.6), Color = hex("#49D6F2"), Material = Enum.Material.Glass, Transparency = 0.05 })
		local s2 = self:czesc({ Name = "ShardRdzen", Size = Vector3.new(0.3, 1.3, 0.3), Color = hex("#E8FBFF") })
		self:nowa("PointLight", { Color = hex("#49D6F2"), Range = 10, Brightness = 2 }, s2)
		dodaj({ { s, CFrame.new(0, 1.2, 0) * CFrame.Angles(0, 0, rad(12)) }, { s2, CFrame.new(0, 1.2, 0) * CFrame.Angles(0, 0, rad(12)) } },
			rozsyp(0.5, 1.4), 5.5, 0.4, 0.8, false, true)
	end
	local wiek = 0
	self:dodaj({
		krok = function(_, d)
			wiek += d
			for _, l in przedmioty do
				l.wiek += d
				local u = math.clamp((l.wiek - l.opoz) / l.trwa, 0, 1)
				local cf
				if u < 1 then
					local poz = l.start:Lerp(l.cel, u) + Vector3.new(0, l.wys * 4 * u * (1 - u), 0)
					cf = CFrame.new(poz) * (if l.wiruje then CFrame.Angles(u * 9, u * 5, 0) else CFrame.Angles(0, u * 6, math.sin(u * 9) * 0.5))
				else
					local kol = if l.kolysze then CFrame.Angles(0, (l.wiek - l.opoz) * 1.5, 0) * CFrame.new(0, math.sin((l.wiek - l.opoz) * 3) * 0.12, 0) else CFrame.identity
					cf = CFrame.new(l.cel) * l.obrot * kol
				end
				local widac = l.wiek >= l.opoz
				for _, c in l.czesci do
					(c[1] :: BasePart).CFrame = cf * c[2]
					;(c[1] :: BasePart).Transparency = if widac then (if c[1].Name == "Gem" then 0.1 else 0) else 1
				end
			end
			return true
		end,
		zniszcz = function()
			for _, l in przedmioty do
				for _, c in l.czesci do
					(c[1] :: BasePart):Destroy()
				end
			end
		end,
	})
	return #przedmioty
end

-- nazwy (dla testu i dla odtwarzacza: czy styl ma wygląd)
Efekty.POCISKI = Pocisk
Efekty.WYBUCHY = Wybuch
Efekty.WYGLADY = Wyglad

return Efekty
