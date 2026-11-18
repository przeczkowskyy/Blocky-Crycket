--[[
	KomiksTreningu — komiksowe napisy mini-gier Training Center w stylu napisów walki (ModuleScript w
	Workspace/TreningProba/Moduly). Wzór: swiat/test_walki2/zrodla/InterfejsWalki2.luau (STYLE, _pokazNapis,
	_aktualizujNapisy) — moduł walki rysuje napisy tylko wewnątrz swojego ekranu walki (kadr, stosy przy aktorach),
	więc styl jest tu przeniesiony, a liczby stylu są w danych (ui.komiks) i porównuje je z walką test offline.

	Napis = pole (Frame, obrócone) ze skalą wejścia (od 0,2 przez 1,08 do 1 w 0,2 s), cień (ten sam tekst tuszem,
	przesunięty), tekst w kolorze stylu z obrysem tuszem i — przy dużych słowach („POW!”, „SERIA 10!”, „+1 Siła!”) —
	gwiazda z dwóch obróconych kwadratów, która się kręci. Pod koniec życia napis gaśnie.

	Czcionka: Bangers (wbudowana), gdy ma wszystkie litery napisu — ASCII i litery z ui.komiks.znaki (polskie znaki
	sprawdzone w pliku czcionki klienta Roblox); napis z inną literą dostaje czcionkę okien, żeby żadna litera nie
	była rysowana czcionką zastępczą (jak ę, ż, ś w FredokaOne). Licznik self.zastepcze mówi, ile takich było.

	Użycie (klient): local k = Komiks.nowy(warstwa, D.ui, czcionkaOkien)
		k:napis(tekst, styl, x, y, opcje)   -- x, y: środek w pikselach warstwy; opcje: kolor, obrot, gwiazda, zycie,
		                                    -- skala, obszar { x0, y0, x1, y1 }, przeszkody { prostokąt… }
		k:krok(dt)   k:usun(napis)   k:wyczysc()   k:ile()
	Czyste funkcje (bez instancji, sprawdzane offline): Komiks.rozmiar, Komiks.miejsce.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local TextService = game:GetService("TextService")

local Komiks = {}
Komiks.__index = Komiks

local function ogranicz(v, a, b)
	if v < a then
		return a
	elseif v > b then
		return b
	end
	return v
end

------------------------------------------------------------------ czysty rachunek
--[[ Rozmiar NARYSOWANEGO napisu (piksele bazowe): prostokąt tekstu po obrocie, gwiazda w każdym obrocie (kwadrat
	o boku „bok” wysokości kręci się → przekątna), obrys i cień, powiększenie w animacji wejścia — jak w walce. ]]
function Komiks.rozmiar(KX, szer, wys, obrot, gwiazda)
	local a = math.rad(math.abs(obrot))
	local w = szer * math.cos(a) + wys * math.sin(a)
	local h = szer * math.sin(a) + wys * math.cos(a)
	if gwiazda then
		local s = KX.gwiazda.bok * wys * math.sqrt(2)
		w, h = math.max(w, s), math.max(h, s)
	end
	local m = 2 * (KX.obrys_px + 1)
	return (w + m) * KX.nadmiar, (h + m) * KX.nadmiar
end

--[[ Środek napisu o rozmiarze w × h jak najbliżej (x, y): w obszarze { x0, y0, x1, y1 } z marginesem m i poza
	przeszkodami (prostokąty { x0, y0, x1, y1 } — panel rundy, przyciski). Z przeszkody napis schodzi najkrótszą
	drogą, która zostaje w obszarze. ]]
function Komiks.miejsce(x, y, w, h, obszar, przeszkody, m)
	if obszar == nil then
		return x, y
	end
	local function wObszar(px, py)
		local x0, x1 = obszar[1] + m + w / 2, obszar[3] - m - w / 2
		local y0, y1 = obszar[2] + m + h / 2, obszar[4] - m - h / 2
		if x0 > x1 then
			px = (obszar[1] + obszar[3]) / 2
		else
			px = ogranicz(px, x0, x1)
		end
		if y0 > y1 then
			py = (obszar[2] + obszar[4]) / 2
		else
			py = ogranicz(py, y0, y1)
		end
		return px, py
	end
	x, y = wObszar(x, y)
	if przeszkody == nil then
		return x, y
	end
	for _ = 1, 4 do
		local ruszono = false
		for _, r in przeszkody do
			local wLewo = (x + w / 2 + m) - r[1]
			local wPrawo = r[3] - (x - w / 2 - m)
			local wGore = (y + h / 2 + m) - r[2]
			local wDol = r[4] - (y - h / 2 - m)
			if wLewo > 0 and wPrawo > 0 and wGore > 0 and wDol > 0 then
				local najlepszy, nx, ny = math.huge, x, y
				for _, k in { { -wLewo, 0 }, { wPrawo, 0 }, { 0, -wGore }, { 0, wDol } } do
					local cx, cy = x + k[1], y + k[2]
					local zx, zy = wObszar(cx, cy)
					if math.abs(zx - cx) < 0.5 and math.abs(zy - cy) < 0.5 then
						local koszt = math.abs(k[1]) + math.abs(k[2])
						if koszt < najlepszy then
							najlepszy, nx, ny = koszt, cx, cy
						end
					end
				end
				if najlepszy < math.huge then
					x, y = nx, ny
					ruszono = true
				end
			end
		end
		if not ruszono then
			return x, y
		end
	end
	return x, y
end

------------------------------------------------------------------ napisy
function Komiks.nowy(warstwa, U, czcionkaOkien)
	local self = setmetatable({}, Komiks)
	self.warstwa = warstwa
	self.KX = U.komiks
	self.czcionkaOkien = czcionkaOkien
	self.czcionka = Font.fromEnum(Enum.Font[self.KX.czcionka])
	self.znaki = {}
	for _, kod in utf8.codes(self.KX.znaki) do
		self.znaki[kod] = true
	end
	self.los = Random.new()
	self.napisy = {}
	self.szerokosci = {}
	self.kierunek = 1 -- napisy obracają się na zmianę w lewo i w prawo
	self.pokazane = 0
	self.zastepcze = 0 -- ile napisów dostało czcionkę okien (litera spoza czcionki komiksowej)
	return self
end

-- czy czcionka komiksowa ma każdą literę napisu (drukowalne ASCII: od spacji do tyldy)
local ASCII_OD, ASCII_DO = string.byte(" "), string.byte("~")
function Komiks:pokrywa(tekst)
	for _, kod in utf8.codes(tekst) do
		if not ((kod >= ASCII_OD and kod <= ASCII_DO) or self.znaki[kod]) then
			return false
		end
	end
	return true
end

function Komiks:czcionkaDla(tekst)
	if self:pokrywa(tekst) then
		return self.czcionka, true
	end
	return self.czcionkaOkien, false
end

-- szerokość napisu jako wielokrotność jego wysokości: prawdziwa szerokość tekstu w czcionce komiksowej (z pamięcią),
-- a gdy pomiar zawiedzie — szacunek z liczby liter
function Komiks:szerokosc(tekst, komiksowa)
	local klucz = (if komiksowa then "k:" else "o:") .. tekst
	local w = self.szerokosci[klucz]
	if w then
		return w
	end
	local n = utf8.len(tekst) or #tekst
	w = n * (if komiksowa then self.KX.szerokosc_znaku else 0.62)
	if komiksowa then
		local wys = self.KX.rozmiary_px.wielki
		local ok, v = pcall(function()
			return TextService:GetTextSize(tekst, wys, Enum.Font[self.KX.czcionka], Vector2.new(math.huge, math.huge))
		end)
		if ok and v and v.X > 0 then
			w = v.X / wys
		end
	end
	self.szerokosci[klucz] = w
	return w
end

local function obrys(rodzic, grubosc, kolor, tekstowy)
	local s = Instance.new("UIStroke")
	s.Color = kolor
	s.Thickness = math.max(1, grubosc)
	s.LineJoinMode = Enum.LineJoinMode.Round
	s.ApplyStrokeMode = if tekstowy then Enum.ApplyStrokeMode.Contextual else Enum.ApplyStrokeMode.Border
	s.Parent = rodzic
	return s
end

function Komiks:napis(tekst, styl, x, y, opcje)
	local KX = self.KX
	local def = KX.style[styl] or KX.style.trafienie
	opcje = opcje or {}
	local skala = opcje.skala or 1
	local czcionka, komiksowa = self:czcionkaDla(tekst)
	if not komiksowa then
		self.zastepcze += 1
	end
	local wys = KX.rozmiary_px[def.rozmiar]
	local szer = wys * math.max(1.2, self:szerokosc(tekst, komiksowa) * 1.12)
	local gwiazda = def.gwiazda == true
	if opcje.gwiazda ~= nil then
		gwiazda = opcje.gwiazda
	end
	-- długi napis obraca się mniej: obrócony prostokąt długiego napisu byłby wysoki jak dwa napisy (jak w walce)
	local maksObrot = math.min(KX.obrot_max, math.deg(math.asin(ogranicz(0.3 * wys / szer, 0, 1))))
	local obrot = opcje.obrot
	if obrot == nil then
		self.kierunek = -self.kierunek
		obrot = self.kierunek * self.los:NextNumber(0.45, 1) * KX.obrot_max
	end
	obrot = ogranicz(obrot, -maksObrot, maksObrot)
	local w2, h2 = Komiks.rozmiar(KX, szer, wys, obrot, gwiazda)
	x, y = Komiks.miejsce(x, y, w2 * skala, h2 * skala, opcje.obszar, opcje.przeszkody, KX.margines_px)

	local tusz = Color3.fromHex(KX.kolory.tusz)
	local kolor = opcje.kolor or def.kolor
	kolor = Color3.fromHex(KX.kolory[kolor] or kolor)
	local pole = Instance.new("Frame")
	pole.Name = "Napis_" .. styl
	pole.BackgroundTransparency = 1
	pole.AnchorPoint = Vector2.new(0.5, 0.5)
	pole.Position = UDim2.fromOffset(x, y)
	pole.Size = UDim2.fromOffset(szer, wys)
	pole.Rotation = obrot
	pole.ZIndex = 20
	local sk = Instance.new("UIScale")
	sk.Scale = KX.wejscie_od * skala
	sk.Parent = pole
	local obrysy = {}
	local kwadraty = {}
	if gwiazda then
		for i, h in KX.gwiazda.kolory do
			local g = Instance.new("Frame")
			g.Name = "Gwiazda" .. i
			g.AnchorPoint = Vector2.new(0.5, 0.5)
			g.Position = UDim2.fromScale(0.5, 0.5)
			g.Size = UDim2.fromScale(KX.gwiazda.bok, KX.gwiazda.bok)
			g.SizeConstraint = Enum.SizeConstraint.RelativeYY
			g.BackgroundColor3 = Color3.fromHex(h)
			g.BorderSizePixel = 0
			g.Rotation = KX.gwiazda.obrot[i] or 0
			g.ZIndex = 20
			table.insert(obrysy, obrys(g, KX.gwiazda.obrys_px * skala, tusz, false))
			g.Parent = pole
			kwadraty[i] = g
		end
	end
	-- Litery mają rozmiar stylu (bez TextScaled: ono kończy się na 100 px, a skala okna powiększa napis dalej);
	-- obrys i cień rosną z rozmiarem liter — przy małych słowach pełny obrys zlewał litery w plamę (próba 18.11.2026)
	local udzial = wys / KX.rozmiary_px.wielki
	local function etykieta(nazwa, barwa, grubosc, dx, dy, z)
		local l = Instance.new("TextLabel")
		l.Name = nazwa
		l.BackgroundTransparency = 1
		l.AnchorPoint = Vector2.new(0.5, 0.5)
		l.Position = UDim2.new(0.5, dx, 0.5, dy)
		l.Size = UDim2.fromScale(1, 1)
		l.FontFace = czcionka
		l.TextScaled = false
		l.TextWrapped = false
		l.TextSize = math.min(wys, KX.rozmiar_max)
		l.Text = tekst
		l.TextColor3 = barwa
		l.ZIndex = z
		table.insert(obrysy, obrys(l, math.max(1.5, grubosc * udzial) * skala, tusz, true))
		l.Parent = pole
		return l
	end
	local cien = etykieta("Cien", tusz, KX.obrys_px + 1, KX.cien_px[1] * udzial, KX.cien_px[2] * udzial, 21)
	local napis = etykieta("Tekst", kolor, KX.obrys_px, 0, 0, 22)
	pole.Parent = self.warstwa

	local n = {
		pole = pole, sk = sk, cien = cien, tekst = napis, gwiazda = kwadraty, obrysy = obrysy, wiek = 0,
		zycie = def.zycie_s * (opcje.zycie or 1), skala = skala, styl = styl, napis = tekst, x = x, y = y,
		komiksowa = komiksowa,
	}
	table.insert(self.napisy, n)
	self.pokazane += 1
	while #self.napisy > KX.naraz do
		local stary = table.remove(self.napisy, 1)
		local obj = stary.pole
		obj:Destroy()
	end
	return n
end

-- wiek, skala wejścia, obrót gwiazdy, zanik; skończone napisy znikają
function Komiks:krok(dt)
	local KX = self.KX
	local w = KX.wejscie_s
	for i = #self.napisy, 1, -1 do
		local n = self.napisy[i]
		n.wiek += dt
		if n.wiek >= n.zycie then
			table.remove(self.napisy, i)
			local obj = n.pole
			obj:Destroy()
		else
			local s = 1
			if n.wiek < w then
				s = KX.wejscie_od + (KX.nadmiar - KX.wejscie_od) * (n.wiek / w)
			elseif n.wiek < 2 * w then
				s = KX.nadmiar - (KX.nadmiar - 1) * ((n.wiek - w) / w)
			end
			n.sk.Scale = s * n.skala
			local zanik = ogranicz((n.wiek / n.zycie - KX.zanik_od) / (1 - KX.zanik_od), 0, 1)
			if zanik > 0 or n.zanikal then
				n.zanikal = true
				n.tekst.TextTransparency = zanik
				n.cien.TextTransparency = zanik
				for _, o in n.obrysy do
					o.Transparency = zanik
				end
				for _, g in n.gwiazda do
					g.BackgroundTransparency = zanik
				end
			end
			for j, g in n.gwiazda do
				g.Rotation += dt * (KX.gwiazda.predkosc[j] or 0)
			end
		end
	end
end

-- zdejmuje napis przed czasem (nowe duże słowo zastępuje poprzednie w tym samym miejscu)
function Komiks:usun(n)
	local i = table.find(self.napisy, n)
	if i then
		table.remove(self.napisy, i)
		local obj = n.pole
		obj:Destroy()
	end
end

function Komiks:wyczysc()
	for _, n in self.napisy do
		local obj = n.pole
		obj:Destroy()
	end
	table.clear(self.napisy)
end

function Komiks:ile()
	return #self.napisy
end

return Komiks
