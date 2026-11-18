--[[
	EfektyTreningu — efekty 3D mini-gier Training Center w języku walki (ModuleScript w Workspace/TreningProba/Moduly).
	Wszystko z części Roblox, lokalnie u klienta, bez wgrywania czegokolwiek.

	Skąd efekty:
		• iskry, rozbłyski, fala uderzeniowa i łuk odbicia — z modułu efektów walki
		  (Workspace/TestWalki2/Moduly/Efekty3D), gdy stoi w miejscu i ma potrzebne funkcje: wtedy mini-gry wyglądają
		  dokładnie jak walka i zmieniają się razem z nią;
		• gdy kontenera walki nie ma, moduł ma inne funkcje albo pierwsze wywołanie zgłosi błąd — własne kopie tych
		  samych efektów z tego pliku (przeniesione z Efekty3D: iskry, kula, fala, parada, tabela wybuchów). Mini-gry
		  działają więc także bez walki; test offline pilnuje, że nazwy wybuchów i funkcji są w obu miejscach te same;
		• konfetti — zawsze własne (walka świętuje radością zwycięzcy, objazdem kamery i łupem, konfetti nie ma):
		  papierowe prostokąty z klocków w barwach walki, wystrzelone salwami z dwóch stron postaci, opadają
		  wirując i gasną.

	Użycie (klient):
		local fx = Efekty.dlaTreningu(folder, D.ui.efekty, wymusWlasne)
		fx:wybuch(nazwa, punkt, skala)   fx:fala(punkt, kolor, promien)   fx:parada(punkt, kierunek, kolor, skala)
		fx:kula(punkt, kolor, od, do_, czas, material, przezr)   fx:iskry(punkt, paleta, ile, predkosc, skala, grawitacja)
		fx:konfetti(ziemia, prawo, ustawienia, wielkie) → liczba kawałków
		fx:krok(dt)   fx:wyczysc()   fx:policz() → liczba utworzonych instancji   fx.zrodlo = "walka" | "wlasne"
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Efekty = {}
Efekty.__index = Efekty

local los = Random.new()
local rad = math.rad

local Wybuch = {}

local function hex(h)
	return Color3.fromHex(h)
end

------------------------------------------------------------------ podstawy (jak Efekty3D)
function Efekty.nowe(folder)
	local self = setmetatable({}, Efekty)
	self.folder = folder
	self.aktywne = {} -- obiekty z krok(d) → false, gdy skończone
	self.utworzono = 0
	self.wolne = {} -- pula iskier
	return self
end

function Efekty:czesc(w)
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Material = Enum.Material.Neon
	for k, v in w do
		p[k] = v
	end
	p.Parent = self.folder
	self.utworzono += 1
	return p
end

function Efekty:dodaj(obj)
	table.insert(self.aktywne, obj)
	return obj
end

function Efekty:krok(d)
	for i = #self.aktywne, 1, -1 do
		local o = self.aktywne[i]
		local ok, zyje = pcall(o.krok, o, d)
		if not ok then
			zyje = false
		end
		if not zyje then
			table.remove(self.aktywne, i)
			if o.zniszcz then
				pcall(o.zniszcz, o)
			end
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
	for _, p in self.wolne do
		p:Destroy()
	end
	table.clear(self.wolne)
end

------------------------------------------------------------------ iskry, rozbłysk, fala, łuk odbicia
function Efekty:iskra()
	local p = table.remove(self.wolne)
	if not p then
		p = self:czesc({ Name = "Iskra", Size = Vector3.one * 0.4 })
	end
	p.Transparency = 0
	return p
end

-- rozprysk klocków: paleta kolorów, ile, prędkość, skala, grawitacja
function Efekty:iskry(poz, paleta, ile, predkosc, skala, grawitacja)
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
function Efekty:kula(poz, kolor, od, do_, czas, material, przezr)
	local p0 = przezr or 0.15
	local p = self:czesc({ Name = "Rozblysk", Shape = Enum.PartType.Ball, Size = Vector3.one * od, Color = kolor,
		Material = material or Enum.Material.Neon, Transparency = p0, CFrame = CFrame.new(poz) })
	local wiek = 0
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
function Efekty:fala(poz, kolor, promien)
	local p = self:czesc({ Name = "Fala", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.25, 1, 1), Color = kolor,
		Material = Enum.Material.SmoothPlastic, Transparency = 0.1 })
	local p2 = self:czesc({ Name = "FalaKurz", Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.18, 1, 1),
		Color = hex("F0E2C0"), Material = Enum.Material.SmoothPlastic, Transparency = 0.3 })
	local wiek = 0
	local cf = CFrame.new(poz) * CFrame.Angles(0, 0, rad(90))
	return self:dodaj({
		krok = function(_, d)
			wiek += d
			local u = wiek / 0.5
			if u >= 1 then
				return false
			end
			local q = 1 - u
			local r = promien * (1 - q * q * q)
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

-- łuk „odbicia” z pięciu świecących klinów w poprzek ciosu, zwrócony w stronę kier; rozchyla się i gaśnie
function Efekty:parada(punkt, kier, kolor, s)
	local poziomo = Vector3.new(kier.X, 0, kier.Z)
	if poziomo.Magnitude < 0.01 then
		poziomo = Vector3.new(0, 0, -1)
	end
	local cf = CFrame.lookAt(punkt, punkt + poziomo.Unit)
	local czesci = {}
	for i = 1, 5 do
		local p = self:czesc({ Name = "Parada", Size = Vector3.new(0.12, 0.9, 0.22) * s, Color = kolor, Transparency = 0.1 })
		table.insert(czesci, { p = p, kat = (i - 3) * 0.42 })
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
				local p = c.p
				p:Destroy()
			end
			blysk:Destroy()
		end,
	})
end

------------------------------------------------------------------ wybuchy (rozbłysk przy trafieniu) — nazwy i wygląd jak w walce
Wybuch.iskra = function(fx, poz, s)
	fx:kula(poz, hex("C08CFF"), 0.6 * s, 2.6 * s, 0.25)
	fx:iskry(poz, { hex("C08CFF"), hex("FFFFFF"), hex("8A5CFF") }, 7, 11, 0.8 * s)
end
Wybuch.ogien = function(fx, poz, s)
	fx:kula(poz, hex("FFE14A"), 1.0 * s, 4.2 * s, 0.22)
	fx:kula(poz, hex("FF7A1F"), 1.4 * s, 6.0 * s, 0.42, nil, 0.25)
	fx:iskry(poz, { hex("FFD23F"), hex("FF8A1F"), hex("E8364F") }, 14, 16, 1.2 * s)
end
Wybuch.lod = function(fx, poz, s)
	fx:kula(poz, hex("E8FBFF"), 0.8 * s, 3.4 * s, 0.25)
	fx:iskry(poz, { hex("BDF3FF"), hex("FFFFFF"), hex("6FD6FF") }, 12, 13, 1.0 * s, 20)
end
Wybuch.kwas = function(fx, poz, s)
	fx:kula(poz, hex("C8FF7A"), 0.8 * s, 4.6 * s, 0.3, nil, 0.25)
	fx:kula(poz, hex("9BF04A"), 1.2 * s, 6.0 * s, 0.5, Enum.Material.SmoothPlastic, 0.45)
	fx:iskry(poz, { hex("9BF04A"), hex("5FD13A"), hex("DFFF9A") }, 22, 15, 1.25 * s, 36)
end
Wybuch.trucizna = function(fx, poz, s)
	fx:kula(poz, hex("8BEA4E"), 0.5 * s, 2.4 * s, 0.3, nil, 0.35)
	fx:iskry(poz, { hex("8BEA4E"), hex("3E8C2A") }, 6, 8, 0.7 * s)
end
Wybuch.zarodniki = function(fx, poz, s)
	fx:kula(poz, hex("B07CFF"), 1.0 * s, 4.6 * s, 0.55, Enum.Material.SmoothPlastic, 0.45)
	fx:iskry(poz, { hex("D7B8FF"), hex("B07CFF"), hex("8BEA4E") }, 10, 6, 0.8 * s, 4)
end
Wybuch.kamien = function(fx, poz, s)
	fx:kula(poz, hex("C9CED6"), 1.0 * s, 4.0 * s, 0.35, Enum.Material.SmoothPlastic, 0.4)
	fx:iskry(poz, { hex("8D949C"), hex("A9AFB6"), hex("646B73") }, 12, 10, 1.3 * s, 30)
end
Wybuch.zloto = function(fx, poz, s)
	fx:kula(poz, hex("FFE14A"), 1.0 * s, 4.5 * s, 0.4, nil, 0.35)
	fx:iskry(poz, { hex("FFD23F"), hex("FFF3B0") }, 12, 9, 0.8 * s, 6)
end
Wybuch.bariera = function(fx, poz, s)
	fx:kula(poz, hex("6FE3FF"), 1.0 * s, 5.0 * s, 0.4, Enum.Material.ForceField, 0.1)
	fx:iskry(poz, { hex("6FE3FF"), hex("FFFFFF") }, 10, 9, 0.8 * s, 6)
end
Wybuch.blask = function(fx, poz, s)
	fx:kula(poz, hex("FFFFFF"), 0.8 * s, 3.4 * s, 0.3, nil, 0.3)
end
Wybuch.cios = function(fx, poz, s)
	fx:iskry(poz, { hex("FFFFFF"), hex("FFD23F") }, 8, 12, s)
end
Wybuch.krytyk = function(fx, poz, s)
	fx:kula(poz, hex("FFF3B0"), 0.6 * s, 3.2 * s, 0.2, nil, 0.2)
	fx:iskry(poz, { hex("FFD23F"), hex("FF8A1F"), hex("FFFFFF") }, 16, 19, 1.35 * s)
end
Wybuch.blok = function(fx, poz, s)
	fx:iskry(poz, { hex("3FF2D0"), hex("FFFFFF"), hex("27B6F2") }, 9, 12, s)
end
Wybuch.tarcza = function(fx, poz, s)
	fx:kula(poz, hex("9FE8FF"), 1.2 * s, 3.0 * s, 0.25, Enum.Material.ForceField, 0.2)
end

function Efekty:wybuch(nazwa, poz, skala)
	local f = Wybuch[nazwa] or Wybuch.cios
	f(self, poz, skala or 1)
end

------------------------------------------------------------------ konfetti (własne — w walce go nie ma)
--[[ Papierowe konfetti przy świętowaniu po rundzie. ziemia = punkt pod postacią, prawo = wektor „w prawo” kamery
	(poziomy): salwy lecą na zmianę z lewej i z prawej strony postaci w górę i do środka, potem kawałki opadają
	powoli (opór powietrza), kołyszą się na boki, wirują i gasną. K = D.ui.efekty.konfetti (przy prędkości 30,
	grawitacji 9 i oporze 2,2 kawałki dolatują ok. 7 st nad ziemię i opadają ok. 4 st/s); wielkie = runda bez
	pudła (więcej kawałków i salw). Zwraca liczbę kawałków. ]]
function Efekty:konfetti(ziemia, prawo, K, wielkie)
	local tryb = if wielkie then K.wielkie else K.zwykle
	local kolory = {}
	for _, h in K.kolory do
		table.insert(kolory, hex(h))
	end
	local bok = Vector3.new(prawo.X, 0, prawo.Z)
	if bok.Magnitude < 0.01 then
		bok = Vector3.new(1, 0, 0)
	end
	bok = bok.Unit
	local wglab = Vector3.new(-bok.Z, 0, bok.X)
	local r = K.rozmiar
	local kawalki = {}
	for i = 1, tryb.ile do
		local salwa = (i - 1) % tryb.salwy
		local strona = if salwa % 2 == 0 then -1 else 1
		local p = self:czesc({ Name = "Konfetti", Size = Vector3.new(r[1], r[2], r[3]) * los:NextNumber(0.8, 1.35),
			Color = kolory[los:NextInteger(1, #kolory)], Material = Enum.Material.SmoothPlastic, Transparency = 1 })
		local start = ziemia + bok * (strona * K.rozrzut * los:NextNumber(0.7, 1.0)) + wglab * los:NextNumber(-1.5, 1.5)
			+ Vector3.new(0, 0.3, 0)
		local kier = Vector3.new(0, 1, 0) + bok * (-strona * los:NextNumber(0.05, 0.55)) + wglab * los:NextNumber(-0.3, 0.3)
		table.insert(kawalki, {
			p = p, poz = start, v = kier.Unit * K.predkosc * los:NextNumber(0.6, 1.0),
			wiek = -(salwa * K.odstep_salw_s + los:NextNumber(0, 0.12)), faza = los:NextNumber(0, 6),
			os = Vector3.new(los:NextNumber(-1, 1), los:NextNumber(-1, 1), los:NextNumber(-1, 1)),
			wir = los:NextNumber(4, 11), lezy = false,
		})
	end
	local podloga = ziemia.Y + 0.06
	local zycie = K.zycie_s
	self:dodaj({
		krok = function(_, d)
			local zywe = false
			for _, k in kawalki do
				k.wiek += d
				if k.wiek < zycie then
					zywe = true
				end
				if k.wiek >= 0 and k.wiek < zycie then
					if not k.lezy then
						-- grawitacja i opór powietrza: szybki wystrzał, potem powolne opadanie z kołysaniem
						k.v += Vector3.new(0, -K.grawitacja, 0) * d
						k.v *= math.max(0, 1 - K.opor * d)
						k.poz += k.v * d + bok * (math.sin(k.faza + k.wiek * 5) * 1.1 * d)
						if k.poz.Y <= podloga and k.v.Y < 0 then
							k.poz = Vector3.new(k.poz.X, podloga, k.poz.Z)
							k.lezy = true
						end
					end
					local kat = if k.lezy then 0 else k.wiek * k.wir
					k.p.CFrame = CFrame.new(k.poz) * CFrame.Angles(k.os.X * kat, k.os.Y * kat + k.faza, k.os.Z * kat)
					local u = k.wiek / zycie
					k.p.Transparency = math.clamp((u - 0.75) / 0.25, 0, 1)
				elseif k.wiek >= zycie then
					k.p.Transparency = 1
				end
			end
			return zywe
		end,
		zniszcz = function()
			for _, k in kawalki do
				local p = k.p
				p:Destroy()
			end
		end,
	})
	return #kawalki
end

-- nazwy (testy offline: te same wybuchy i funkcje co w module walki)
Efekty.WYBUCHY = Wybuch
Efekty.WSPOLNE = { "wybuch", "fala", "parada", "kula", "iskry", "krok", "wyczysc" }

------------------------------------------------------------------ zestaw dla mini-gier: efekty walki albo własne
local Zestaw = {}
Zestaw.__index = Zestaw

-- moduł efektów walki z jej kontenera (tylko odczyt, bez czekania): nil, gdy go nie ma albo nie pasuje
local function modulWalki(U)
	local k = workspace:FindFirstChild(U.kontener_walki)
	local m = k and k:FindFirstChild("Moduly")
	local e = m and m:FindFirstChild(U.modul_walki)
	if not e or not e:IsA("ModuleScript") then
		return nil, nil
	end
	local ok, E = pcall(require, e)
	if not ok or type(E) ~= "table" or type(E.nowe) ~= "function" or type(E.WYBUCHY) ~= "table" then
		return nil, nil
	end
	for _, n in Efekty.WSPOLNE do
		if type(E[n]) ~= "function" then
			return nil, nil
		end
	end
	for nazwa in Wybuch do
		if type(E.WYBUCHY[nazwa]) ~= "function" then
			return nil, nil
		end
	end
	-- ustawienia walki (gdyby jej efekty z nich korzystały); brak → nil, jak w testach walki
	local ust = nil
	local mu = m:FindFirstChild("Ustawienia")
	if mu and mu:IsA("ModuleScript") then
		local ok2, w = pcall(require, mu)
		if ok2 and type(w) == "table" then
			ust = w
		end
	end
	return E, ust
end

function Efekty.dlaTreningu(folder, U, wymusWlasne)
	local z = setmetatable({}, Zestaw)
	z.wlasne = Efekty.nowe(folder)
	z.walka = nil
	z.zrodlo = "wlasne"
	z.bledy = 0
	if not wymusWlasne then
		local E, ust = modulWalki(U)
		if E then
			local ok, fx = pcall(E.nowe, folder, ust)
			if ok and type(fx) == "table" then
				z.walka = fx
				z.zrodlo = "walka"
			end
		end
	end
	return z
end

-- efekt z modułu walki; pierwszy błąd przełącza na własne efekty do końca pobytu na stanowisku
function Zestaw:_zWalki(nazwa, a, b, c, d, e, f, g)
	local w = self.walka
	if not w then
		return false
	end
	local ok = pcall(w[nazwa], w, a, b, c, d, e, f, g)
	if ok then
		return true
	end
	self.walka = nil
	self.zrodlo = "wlasne"
	self.bledy += 1
	pcall(w.wyczysc, w)
	return false
end

function Zestaw:wybuch(nazwa, poz, skala)
	if not self:_zWalki("wybuch", nazwa, poz, skala) then
		self.wlasne:wybuch(nazwa, poz, skala)
	end
end

function Zestaw:fala(poz, kolor, promien)
	if not self:_zWalki("fala", poz, kolor, promien) then
		self.wlasne:fala(poz, kolor, promien)
	end
end

function Zestaw:parada(punkt, kier, kolor, s)
	if not self:_zWalki("parada", punkt, kier, kolor, s) then
		self.wlasne:parada(punkt, kier, kolor, s)
	end
end

function Zestaw:kula(poz, kolor, od, do_, czas, material, przezr)
	if not self:_zWalki("kula", poz, kolor, od, do_, czas, material, przezr) then
		self.wlasne:kula(poz, kolor, od, do_, czas, material, przezr)
	end
end

function Zestaw:iskry(poz, paleta, ile, predkosc, skala, grawitacja)
	if not self:_zWalki("iskry", poz, paleta, ile, predkosc, skala, grawitacja) then
		self.wlasne:iskry(poz, paleta, ile, predkosc, skala, grawitacja)
	end
end

function Zestaw:konfetti(ziemia, prawo, K, wielkie)
	return self.wlasne:konfetti(ziemia, prawo, K, wielkie)
end

function Zestaw:krok(d)
	local w = self.walka
	if w then
		local ok = pcall(w.krok, w, d)
		if not ok then
			self.walka = nil
			self.zrodlo = "wlasne"
			self.bledy += 1
			pcall(w.wyczysc, w)
		end
	end
	self.wlasne:krok(d)
end

function Zestaw:wyczysc()
	local w = self.walka
	if w then
		pcall(w.wyczysc, w)
	end
	self.wlasne:wyczysc()
end

function Zestaw:policz()
	local n = self.wlasne.utworzono
	local w = self.walka
	if w and type(w.utworzono) == "number" then
		n += w.utworzono
	end
	return n
end

return Efekty
