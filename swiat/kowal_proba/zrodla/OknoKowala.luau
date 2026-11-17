--[[
	OknoKowala — TYMCZASOWE okno kuźni (próba D-102; docelowe okno 2D — pytanie 57). Osobny ScreenGui „KowalProbaOkno”
	(HUD-u ani okna ekwipunku nie dotyka), w pasie między kolumnami przycisków HUD (D.ui.okno_x) i pod panelem gracza
	(D.ui.okno_y), napis „PRÓBA” w nagłówku. Okno niczego nie liczy: pokazuje widok z serwera (L.widok) i woła `opcje`.

		local o = Okno.nowe(playerGui, D, { naUlepsz = fn(id), naRozbierz = fn(id), naZamknij = fn(), emulacja = Vector2? })
		o:pokaz(widok)          o:komunikat(tekst, blad?)          o:zniszcz()
	Układ (D.ui.wiersze wierszy): nagłówek (tytuł, materiały, Złoto, X) · lista przedmiotów klasy po lewej (wybrany
	podświetlony) i szczegóły wybranego po prawej (statystyki, ulepszenie, koszt albo powód, „Ulepsz”, „Rozbierz zapas”)
	· stopka (bohater: broń / pancerz / blok; uwaga bez tarczy). Nazwy do prób: Okno/Naglowek/Zamknij,
	Okno/Lista/Przedmiot_<id>, Okno/Szczegoly/Ulepsz, Okno/Szczegoly/Rozbierz. Telefon: atrybut kontenera
	EmulacjaEkranu = Vector2 (np. 667, 375) — okno liczy się jak na takim ekranie (tylko do zrzutów).
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
	t.Parent = rodzic
	table.insert(self.teksty, t)
	return t
end

function Okno:_przycisk(rodzic, nazwa, tekst, poz, rozm, kol, aktywny, fn)
	local b = Instance.new("TextButton")
	b.Name = nazwa
	b.AutoButtonColor = aktywny
	b.Active = aktywny
	b.BackgroundColor3 = kolor(self.D, if aktywny then kol else "przycisk_wylaczony")
	b.TextColor3 = kolor(self.D, if aktywny then "tekst" else "tekst_szary")
	b.Position = poz
	b.Size = rozm
	b.Text = tekst
	b.TextTruncate = Enum.TextTruncate.AtEnd
	local r = Instance.new("UICorner")
	r.CornerRadius = UDim.new(0.25, 0)
	r.Parent = b
	b.Activated:Connect(function()
		if aktywny then
			fn()
		end
	end)
	b.Parent = rodzic
	table.insert(self.teksty, b)
	return b
end

function Okno.nowe(playerGui, D, opcje)
	local self = setmetatable({}, Okno)
	self.D = D
	self.opcje = opcje
	self.teksty = {}
	self.wybrany = nil
	local gui = Instance.new("ScreenGui")
	gui.Name = "KowalProbaOkno"
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
	local okno = Instance.new("Frame")
	okno.Name = "Okno"
	okno.AnchorPoint = Vector2.new(0.5, 1)
	okno.BackgroundColor3 = kolor(D, "tlo")
	okno.BackgroundTransparency = 0.06
	local rog = Instance.new("UICorner")
	rog.CornerRadius = UDim.new(0, 10)
	rog.Parent = okno
	local obrys = Instance.new("UIStroke")
	obrys.Color = kolor(D, "ramka")
	obrys.Thickness = 3
	obrys.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	obrys.Parent = okno
	okno.Parent = ekran
	local toast = Instance.new("TextLabel")
	toast.Name = "Komunikat"
	toast.AnchorPoint = Vector2.new(0.5, 1)
	toast.BackgroundColor3 = kolor(D, "tlo")
	toast.BackgroundTransparency = 0.15
	toast.TextColor3 = kolor(D, "ok")
	toast.Visible = false
	toast.TextTruncate = Enum.TextTruncate.AtEnd
	local rt = Instance.new("UICorner")
	rt.CornerRadius = UDim.new(0, 8)
	rt.Parent = toast
	toast.Parent = ekran
	self.gui, self.ekran, self.skala, self.okno, self.toast = gui, ekran, skala, okno, toast
	self.emulacja = opcje.emulacja
	gui.Parent = playerGui
	gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(function()
		self:uloz()
	end)
	self:uloz()
	return self
end

-- rozmiar okna i tekstu z ekranu (albo emulowanego telefonu), w pikselach ekranu przed UIScale
function Okno:uloz()
	local D = self.D
	local pelny = self.gui.AbsoluteSize
	if pelny.X < 1 or pelny.Y < 1 then
		return
	end
	local W, H = pelny.X, pelny.Y
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
	local ox, oy = D.ui.okno_x, D.ui.okno_y
	local szer = math.min(W * (ox[2] - ox[1]), D.ui.okno_maks_px[1])
	local wys = math.min(H * (oy[2] - oy[1]), D.ui.okno_maks_px[2])
	local wiersz = wys / D.ui.wiersze
	local srodekX = W * (ox[1] + ox[2]) / 2
	self.okno.Position = UDim2.fromOffset(srodekX, H * oy[2])
	self.okno.Size = UDim2.fromOffset(szer, wys)
	local px = math.clamp(math.floor(wiersz * 0.62), D.ui.tekst_min, D.ui.tekst_maks)
	local czcionka = Enum.Font[D.ui.czcionka]
	for _, t in self.teksty do
		if t.Parent then
			t.TextSize = px
			t.Font = czcionka
		end
	end
	self.toast.Position = UDim2.fromOffset(srodekX, H * oy[2] - wys - 8)
	self.toast.Size = UDim2.fromOffset(szer, wiersz)
	self.toast.TextSize = px
	self.toast.Font = czcionka
	self.rozmiarTekstu = px
	self.wysokoscWiersza = wiersz
end

local function wiersze(n, od, ile)
	-- pozycja i wysokość pasa wierszy `od`..`od + ile − 1` z `n`
	return (od - 1) / n, ile / n
end

function Okno:pokaz(widok)
	local D, op = self.D, self.opcje
	local T = D.teksty
	for _, d in self.okno:GetChildren() do
		if d:IsA("Frame") then
			d:Destroy()
		end
	end
	table.clear(self.teksty)
	self.widok = widok
	local n = D.ui.wiersze
	-- wybrany przedmiot: ten sam co wcześniej, jeśli nadal jest na liście; inaczej pierwszy
	local wybrany = nil
	for _, w in widok.wiersze do
		if w.id == self.wybrany then
			wybrany = w
		end
	end
	wybrany = wybrany or widok.wiersze[1]
	self.wybrany = wybrany and wybrany.id

	local function pas(nazwa, od, ile, x, w)
		local y, h = wiersze(n, od, ile)
		local f = Instance.new("Frame")
		f.Name = nazwa
		f.BackgroundTransparency = 1
		f.Position = UDim2.new(x, 6, y, 3)
		f.Size = UDim2.new(w, -12, h, -2)
		f.Parent = self.okno
		return f
	end

	-- nagłówek: PRÓBA, materiały, Złoto, zamknij
	local nag = pas("Naglowek", 1, 1, 0, 1)
	self:_tekst(nag, "Tytul", widok.tytul, UDim2.fromScale(0, 0), UDim2.fromScale(0.36, 1), "ramka")
	self:_tekst(nag, "Materialy", widok.materialy, UDim2.fromScale(0.36, 0), UDim2.fromScale(0.27, 1), "material")
	self:_tekst(nag, "Zloto", widok.zloto, UDim2.fromScale(0.63, 0), UDim2.fromScale(0.25, 1), "zloto")
	self:_przycisk(nag, "Zamknij", T.zamknij, UDim2.new(0.9, 2, 0.06, 0), UDim2.new(0.1, -2, 0.88, 0), "przycisk", true,
		function()
			op.naZamknij()
		end)

	-- lista przedmiotów klasy (wiersze 2..n−1)
	local ileListy = n - 2
	local lista = pas("Lista", 2, ileListy, 0, 0.44)
	for i, w in widok.wiersze do
		if i > ileListy then
			break
		end
		local napis = w.nazwa
		if w.posiadany then
			napis = string.format("%s %s", w.nazwa, string.format(T.poziom, w.poziom))
			if w.zapas > 0 then
				napis = napis .. " · " .. string.format(T.zapas, w.zapas)
			end
		end
		local b = self:_przycisk(lista, "Przedmiot_" .. w.id, napis, UDim2.new(0, 0, (i - 1) / ileListy, 1),
			UDim2.new(1, 0, 1 / ileListy, -2), if w.id == self.wybrany then "wybrany" else "pasek", true, function()
				self.wybrany = w.id
				self:pokaz(self.widok)
			end)
		b.TextXAlignment = Enum.TextXAlignment.Left
		if not w.posiadany then
			b.TextColor3 = kolor(D, "tekst_szary")
		end
		local pad = Instance.new("UIPadding")
		pad.PaddingLeft = UDim.new(0, 6)
		pad.Parent = b
	end

	-- szczegóły wybranego
	local sz = pas("Szczegoly", 2, ileListy, 0.44, 0.56)
	if wybrany then
		local h = 1 / ileListy
		local function linia(nr, nazwa, tekst, kol)
			return self:_tekst(sz, nazwa, tekst, UDim2.fromScale(0, (nr - 1) * h), UDim2.fromScale(1, h), kol)
		end
		linia(1, "Nazwa", wybrany.nazwa, "ramka")
		local stanTekst = wybrany.slot
		if wybrany.posiadany then
			stanTekst = string.format("%s · %s · %s", wybrany.slot, string.format(T.poziom, wybrany.poziom),
				if wybrany.zalozony then T.zalozony else T.zdjety)
		end
		linia(2, "Slot", stanTekst, "tekst_szary")
		linia(3, "Staty", wybrany.staty, if wybrany.posiadany then "tekst" else "tekst_szary")
		if wybrany.posiadany then
			linia(4, "Nastepny", wybrany.nastepny, "ok")
			linia(5, "Koszt", if wybrany.powod ~= "" then wybrany.powod else wybrany.koszt,
				if wybrany.powod ~= "" then "blad" else "zloto")
			local yP = (ileListy - 1) * h
			self:_przycisk(sz, "Ulepsz", T.ulepsz, UDim2.new(0, 0, yP, 1), UDim2.new(0.48, 0, h, -2), "przycisk",
				wybrany.ulepsz, function()
					op.naUlepsz(wybrany.id)
				end)
			self:_przycisk(sz, "Rozbierz", if wybrany.rozbierz then T.rozbierz .. " (" .. wybrany.rozbiorka .. ")"
				else T.rozbierz, UDim2.new(0.52, 0, yP, 1), UDim2.new(0.48, 0, h, -2), "rozbierz", wybrany.rozbierz,
				function()
					op.naRozbierz(wybrany.id)
				end)
		end
	end

	-- stopka: bohater i uwaga
	local st = pas("Stopka", n, 1, 0, 1)
	local dol = widok.bohater
	if widok.uwaga ~= "" then
		dol = if dol ~= "" then dol .. " · " .. widok.uwaga else widok.uwaga
	end
	self:_tekst(st, "Bohater", dol, UDim2.fromScale(0, 0), UDim2.fromScale(1, 1),
		if widok.uwaga ~= "" then "blad" else "tekst")
	self:uloz()
end

function Okno:komunikat(tekst, blad)
	if type(tekst) ~= "string" or tekst == "" then
		return
	end
	self.toast.Text = tekst
	self.toast.TextColor3 = if blad then kolor(self.D, "blad") else kolor(self.D, "ok")
	self.toast.Visible = true
	local nr = (self.nrKomunikatu or 0) + 1
	self.nrKomunikatu = nr
	task.delay(3, function()
		if self.nrKomunikatu == nr and self.toast.Parent then
			self.toast.Visible = false
		end
	end)
end

function Okno:zniszcz()
	if self.gui then
		self.gui:Destroy()
		self.gui = nil
	end
end

return Okno
