--[[
	OknoSklepu — TYMCZASOWE okno sklepu zbrojmistrza (próba D-106; docelowe okno 2D zrobi druga osoba — to ma być proste
	i łatwe do podmiany). Osobny ScreenGui „SklepProbaOkno” (HUD-u ani innych okien nie dotyka), napis „PRÓBA”
	w nagłówku. Okno niczego nie liczy: pokazuje ofertę od serwera, teksty bierze z LogikaSklepu i woła `opcje`.

		local o = Okno.nowe(playerGui, D, L, { naKup = fn(id), naZaloz = fn(id), naZamknij = fn(), emulacja = Vector2? })
		o:pokaz(widok)      -- widok = { oferta, zloto, poziom, klasa } z serwera
		o:nieczynny(tekst)  o:komunikat(tekst, blad?)  o:zniszcz()
	Układ (L.uklad z rozmiaru ekranu): nagłówek (tytuł, poziom, Złoto, X) · zakładki stopni (startowy / leśny /
	bagienny / Dżungli, kolor stopnia) · przewijana lista przedmiotów stopnia (kolorowe pole stopnia zamiast ikony,
	nazwa, slot i statystyki, wymagany poziom i cena, stan, przycisk „Kup” albo „Załóż”) · pasek komunikatu.
	Nazwy do prób: Okno/Naglowek/Zamknij, Okno/Zakladki/Zakladka_<stopien>, Okno/Lista/Wiersz_<id>/Przycisk.
	Telefon: opcja emulacja = Vector2 (np. 667, 375) — okno liczy się jak na takim ekranie (tylko do zrzutów).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Okno = {}
Okno.__index = Okno

local function kolor(D, nazwa)
	return Color3.fromHex(D.ui.kolory[nazwa])
end

function Okno:_tekst(rodzic, nazwa, tekst, poz, rozm, kol, wyrownanie)
	local t = Instance.new("TextLabel")
	t.Name = nazwa
	t.BackgroundTransparency = 1
	t.Position = poz
	t.Size = rozm
	t.Text = tekst
	t.TextColor3 = kolor(self.D, kol or "tekst")
	t.TextXAlignment = wyrownanie or Enum.TextXAlignment.Left
	t.TextTruncate = Enum.TextTruncate.AtEnd
	t.TextSize = self.u.tekst
	t.Font = Enum.Font[self.D.ui.czcionka]
	t.Parent = rodzic
	return t
end

function Okno:_przycisk(rodzic, nazwa, tekst, poz, rozm, kol, aktywny, fn)
	local b = Instance.new("TextButton")
	b.Name = nazwa
	b.AutoButtonColor = aktywny
	b.Active = aktywny
	b.BackgroundColor3 = if type(kol) == "string" then kolor(self.D, if aktywny then kol else "przycisk_wylaczony") else kol
	b.TextColor3 = kolor(self.D, if aktywny then "tekst" else "tekst_szary")
	b.Position = poz
	b.Size = rozm
	b.Text = tekst
	b.TextTruncate = Enum.TextTruncate.AtEnd
	b.TextSize = self.u.tekst
	b.Font = Enum.Font[self.D.ui.czcionka]
	local r = Instance.new("UICorner")
	r.CornerRadius = UDim.new(0, 8)
	r.Parent = b
	b.Activated:Connect(function()
		if aktywny then
			fn()
		end
	end)
	b.Parent = rodzic
	return b
end

function Okno.nowe(playerGui, D, L, opcje)
	local self = setmetatable({}, Okno)
	self.D, self.L, self.opcje = D, L, opcje
	self.zakladka = nil
	self.widok = nil
	self.tekstKomunikatu, self.bladKomunikatu = "", false
	local gui = Instance.new("ScreenGui")
	gui.Name = "SklepProbaOkno"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = D.ui.kolejnosc_wyswietlania
	local ekran = Instance.new("Frame")
	ekran.Name = "Ekran"
	ekran.BackgroundTransparency = 1
	local skala = Instance.new("UIScale")
	skala.Parent = ekran
	ekran.Parent = gui
	self.gui, self.ekran, self.skala = gui, ekran, skala
	self.emulacja = opcje.emulacja
	self.u = L.uklad(D, 667, 375)
	gui.Parent = playerGui
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(function()
		self:rysuj()
	end)
	self:rysuj()
	return self
end

-- ekran (albo emulowany telefon) → układ z LogikaSklepu
function Okno:_ekran()
	local pelny = self.gui.AbsoluteSize
	local W, H = pelny.X, pelny.Y
	if W < 1 or H < 1 then
		return false
	end
	if typeof(self.emulacja) == "Vector2" and self.emulacja.X > 0 and self.emulacja.Y > 0 then
		W, H = self.emulacja.X, self.emulacja.Y
		self.skala.Scale = math.min(pelny.X / W, pelny.Y / H)
		self.ekran.AnchorPoint = Vector2.new(0.5, 0.5)
		self.ekran.Position = UDim2.fromScale(0.5, 0.5)
		self.ekran.Size = UDim2.fromOffset(W, H)
	else
		self.skala.Scale = 1
		self.ekran.AnchorPoint = Vector2.zero
		self.ekran.Position = UDim2.fromScale(0, 0)
		self.ekran.Size = UDim2.fromScale(1, 1)
	end
	self.u = self.L.uklad(self.D, W, H)
	return true
end

function Okno:rysuj()
	local D, L, op = self.D, self.L, self.opcje
	local T = D.teksty
	if not self:_ekran() then
		return
	end
	local u = self.u
	local stare = self.ekran:FindFirstChild("Okno")
	if stare then
		stare:Destroy()
	end
	local okno = Instance.new("Frame")
	okno.Name = "Okno"
	okno.BackgroundColor3 = kolor(D, "tlo")
	okno.BackgroundTransparency = 0.04
	okno.Position = UDim2.fromOffset(u.x, u.y)
	okno.Size = UDim2.fromOffset(u.szer, u.wys)
	local rog = Instance.new("UICorner")
	rog.CornerRadius = UDim.new(0, 10)
	rog.Parent = okno
	local obrys = Instance.new("UIStroke")
	obrys.Color = kolor(D, "ramka")
	obrys.Thickness = 3
	obrys.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	obrys.Parent = okno
	self.okno = okno

	-- nagłówek: PRÓBA, poziom, Złoto, zamknij
	local widok = self.widok
	local n = L.naglowek(D, if widok then widok.zloto else 0, if widok then widok.poziom else 1)
	local nag = Instance.new("Frame")
	nag.Name = "Naglowek"
	nag.BackgroundTransparency = 1
	nag.Position = UDim2.fromOffset(8, 0)
	nag.Size = UDim2.fromOffset(u.szer - 16, u.naglowek)
	nag.Parent = okno
	local reszta = u.szer - 16 - u.zamknij
	self:_tekst(nag, "Tytul", n.tytul, UDim2.fromOffset(0, 0), UDim2.fromOffset(reszta * 0.46, u.naglowek), "ramka")
	self:_tekst(nag, "Poziom", if widok then n.poziom else "", UDim2.fromOffset(reszta * 0.46, 0),
		UDim2.fromOffset(reszta * 0.24, u.naglowek), "tekst")
	self:_tekst(nag, "Zloto", if widok then n.zloto else "", UDim2.fromOffset(reszta * 0.7, 0),
		UDim2.fromOffset(reszta * 0.3 - 6, u.naglowek), "zloto")
	self:_przycisk(nag, "Zamknij", T.zamknij, UDim2.fromOffset(reszta, 2), UDim2.fromOffset(u.zamknij, u.naglowek - 4),
		"przycisk", true, function()
			op.naZamknij()
		end)

	-- zakładki stopni (kolor stopnia; wybrana jaśniejsza)
	local grupy = L.grupy(D, if widok then widok.oferta else {})
	if self.zakladka == nil and widok then
		self.zakladka = L.pierwszaZakladka(D, widok.oferta)
	end
	local zak = Instance.new("Frame")
	zak.Name = "Zakladki"
	zak.BackgroundTransparency = 1
	zak.Position = UDim2.fromOffset(8, u.naglowek)
	zak.Size = UDim2.fromOffset(u.szer - 16, u.zakladka)
	zak.Parent = okno
	local szerZak = (u.szer - 16) / math.max(1, #grupy)
	local wybrana = nil
	for i, g in grupy do
		local czyWybrana = g.id == self.zakladka
		if czyWybrana then
			wybrana = g
		end
		local napis = if g.doKupienia > 0 then string.format("%s (%d)", g.nazwa, g.doKupienia) else g.nazwa
		local b = self:_przycisk(zak, "Zakladka_" .. g.id, napis, UDim2.fromOffset((i - 1) * szerZak + 2, 2),
			UDim2.fromOffset(szerZak - 4, u.zakladka - 4), Color3.fromHex(g.kolor), true, function()
				self.zakladka = g.id
				self:rysuj()
			end)
		b.BackgroundTransparency = if czyWybrana then 0 else 0.55
		b.TextColor3 = kolor(D, "tekst")
	end

	-- lista przedmiotów wybranego stopnia (przewijana)
	local lista = Instance.new("ScrollingFrame")
	lista.Name = "Lista"
	lista.BackgroundTransparency = 1
	lista.BorderSizePixel = 0
	lista.Position = UDim2.fromOffset(8, u.naglowek + u.zakladka)
	lista.Size = UDim2.fromOffset(u.szer - 16, u.lista)
	lista.ScrollBarThickness = 6
	lista.ScrollingDirection = Enum.ScrollingDirection.Y
	local wiersze = if wybrana then wybrana.wiersze else {}
	lista.CanvasSize = UDim2.fromOffset(0, #wiersze * u.wiersz)
	lista.Parent = okno
	local szerWiersza = u.szer - 16 - 8
	local pole = u.wiersz - 10
	local tekstX = pole + 10
	local tekstSzer = szerWiersza - tekstX - u.przyciskSzer - 8
	for i, o in wiersze do
		local w = L.wiersz(D, o)
		local f = Instance.new("Frame")
		f.Name = "Wiersz_" .. o.id
		f.BackgroundColor3 = kolor(D, if o.stan == "zalozone" then "wybrany" else "pasek")
		f.BackgroundTransparency = 0.25
		f.BorderSizePixel = 0
		f.Position = UDim2.fromOffset(0, (i - 1) * u.wiersz + 1)
		f.Size = UDim2.fromOffset(szerWiersza, u.wiersz - 2)
		f:SetAttribute("Stan", o.stan)
		local rw = Instance.new("UICorner")
		rw.CornerRadius = UDim.new(0, 6)
		rw.Parent = f
		local znak = Instance.new("Frame")
		znak.Name = "Stopien"
		znak.BackgroundColor3 = Color3.fromHex(wybrana.kolor)
		znak.BorderSizePixel = 0
		znak.Position = UDim2.fromOffset(4, 4)
		znak.Size = UDim2.fromOffset(pole, pole)
		local rz = Instance.new("UICorner")
		rz.CornerRadius = UDim.new(0, 6)
		rz.Parent = znak
		znak.Parent = f
		local pol = (u.wiersz - 2) / 2
		self:_tekst(f, "Nazwa", w.nazwa, UDim2.fromOffset(tekstX, 0), UDim2.fromOffset(tekstSzer * 0.5, pol), "tekst")
		self:_tekst(f, "Wymaga", w.wymaga, UDim2.fromOffset(tekstX + tekstSzer * 0.5, 0),
			UDim2.fromOffset(tekstSzer * 0.5, pol), if o.stan == "za_niski_poziom" then "blad" else "zloto",
			Enum.TextXAlignment.Right)
		self:_tekst(f, "Opis", w.opis, UDim2.fromOffset(tekstX, pol), UDim2.fromOffset(tekstSzer * 0.68, pol), "tekst_szary")
		self:_tekst(f, "StanTekst", w.stan, UDim2.fromOffset(tekstX + tekstSzer * 0.68, pol),
			UDim2.fromOffset(tekstSzer * 0.32, pol), if w.aktywny or o.stan == "zalozone" then "ok" else "blad",
			Enum.TextXAlignment.Right)
		if w.przycisk ~= "" then
			self:_przycisk(f, "Przycisk", w.przycisk, UDim2.fromOffset(szerWiersza - u.przyciskSzer - 2, 1),
				UDim2.fromOffset(u.przyciskSzer, u.przycisk), if w.akcja == "zaloz" then "zaloz" else "przycisk", w.aktywny,
				function()
					if w.akcja == "kup" then
						op.naKup(o.id)
					elseif w.akcja == "zaloz" then
						op.naZaloz(o.id)
					end
				end)
		end
		f.Parent = lista
	end
	if widok and #wiersze == 0 then
		self:_tekst(lista, "Pusto", T.pusto, UDim2.fromOffset(4, 0), UDim2.fromOffset(szerWiersza, u.wiersz), "tekst_szary")
	end

	-- pasek komunikatu (odmowy i potwierdzenia pełnymi zdaniami)
	local kom = self:_tekst(okno, "Komunikat", self.tekstKomunikatu, UDim2.fromOffset(12, u.wys - u.komunikat),
		UDim2.fromOffset(u.szer - 24, u.komunikat), if self.bladKomunikatu then "blad" else "ok")
	kom.TextXAlignment = Enum.TextXAlignment.Center
	okno.Parent = self.ekran
	self.rozmiarTekstu = u.tekst
	self.liczbaWierszy = #wiersze
end

function Okno:pokaz(widok)
	self.widok = widok
	self:rysuj()
end

function Okno:komunikat(tekst, blad)
	self.tekstKomunikatu, self.bladKomunikatu = tekst, blad == true
	self:rysuj()
end

function Okno:nieczynny(tekst)
	self.widok = nil
	self:komunikat(tekst, true)
end

function Okno:zniszcz()
	self.gui:Destroy()
end

return Okno
