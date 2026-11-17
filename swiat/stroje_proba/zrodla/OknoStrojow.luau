--[[
	OknoStrojow — TYMCZASOWE okno przymierzalni (próba D-071). Docelowe okno ekwipunku 2D robi Paweł (D-093); to jest
	tylko narzędzie próby: osobny ScreenGui „StrojeProbaOkno” (HUD-u ani okna ekwipunku nie dotyka), w pasie między
	kolumnami przycisków HUD (D.ui.okno_x) i pod panelem gracza (D.ui.okno_y), napis „PRÓBA” w nagłówku.

	Okno niczego nie decyduje: woła funkcje z `opcje` (klient pyta serwer), a pokazuje stan, który dostanie:
		local o = Okno.nowe(playerGui, D, {
			naKlase = fn(klasa), naWybor = fn(slot, id | nil), naZestaw = fn(nazwa), naDawny = fn(),
			naRuch = fn(krok), naZagraj = fn(), naWszystkie = fn(), naZamknij = fn(), emulacja = Vector2? })
		o:pokaz({ klasa, oferta = L.oferta(...), stroj = { id… } | nil, ruch = "napis" })
		o:komunikat(tekst, blad?)          o:zniszcz()
	Nazwy przycisków (do prób): Okno/Naglowek/Zakladka_<klasa>, Okno/Naglowek/Zamknij, Okno/Slot_<slot>/Poprzedni |
	Nastepny | Nazwa, Okno/Zestawy/Zestaw_<id>, Okno/Zestawy/Dawny, Okno/Ruch/Poprzedni | Nazwa | Nastepny | Zagraj |
	Wszystkie. Telefon: atrybut kontenera EmulacjaEkranu = Vector2 (np. 667, 375) — okno liczy się jak na takim
	ekranie i jest powiększone UIScale (tylko do zrzutów).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = require(script.Parent:WaitForChild("LogikaStrojow"))

local Okno = {}
Okno.__index = Okno

local WIERSZE_MAKS = 10

local function kolor(D, nazwa)
	return Color3.fromHex(D.ui.kolory[nazwa])
end

local function etykieta(rodzic, nazwa, tekst, x, w)
	local t = Instance.new("TextLabel")
	t.Name = nazwa
	t.BackgroundTransparency = 1
	t.Position = UDim2.fromScale(x, 0)
	t.Size = UDim2.fromScale(w, 1)
	t.Text = tekst
	t.TextWrapped = false
	t.TextTruncate = Enum.TextTruncate.AtEnd
	t.Parent = rodzic
	return t
end

function Okno:_przycisk(rodzic, nazwa, tekst, x, w, wybrany, fn)
	local b = Instance.new("TextButton")
	b.Name = nazwa
	b.AutoButtonColor = true
	b.BackgroundColor3 = if wybrany then kolor(self.D, "przycisk_wybrany") else kolor(self.D, "przycisk")
	b.TextColor3 = if wybrany then kolor(self.D, "tekst_ciemny") else kolor(self.D, "tekst")
	b.Position = UDim2.new(x, 2, 0.08, 0)
	b.Size = UDim2.new(w, -4, 0.84, 0)
	b.Text = tekst
	b.TextTruncate = Enum.TextTruncate.AtEnd
	local r = Instance.new("UICorner")
	r.CornerRadius = UDim.new(0.25, 0)
	r.Parent = b
	b.Activated:Connect(fn)
	b.Parent = rodzic
	table.insert(self.teksty, b)
	return b
end

function Okno.nowe(playerGui, D, opcje)
	local self = setmetatable({}, Okno)
	self.D = D
	self.opcje = opcje
	self.teksty = {}
	local gui = Instance.new("ScreenGui")
	gui.Name = "StrojeProbaOkno"
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
	self.wiersze = 1
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
		local s = math.min(pelny.X / W, pelny.Y / H)
		self.skala.Scale = s
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
	local wiersz = math.min(H * (oy[2] - oy[1]), D.ui.okno_maks_px[2]) / WIERSZE_MAKS
	local srodekX = W * (ox[1] + ox[2]) / 2
	self.okno.Position = UDim2.fromOffset(srodekX, H * oy[2])
	self.okno.Size = UDim2.fromOffset(szer, wiersz * self.wiersze + 6)
	local px = math.clamp(math.floor(wiersz * 0.62), D.ui.tekst_min, D.ui.tekst_maks)
	self.rozmiarTekstu = px
	local czcionka = Enum.Font[D.ui.czcionka]
	for _, t in self.teksty do
		if t.Parent then
			t.TextSize = px
			t.Font = czcionka
		end
	end
	self.toast.Position = UDim2.fromOffset(srodekX, H * oy[2] - wiersz * self.wiersze - 12)
	self.toast.Size = UDim2.fromOffset(szer, wiersz)
	self.toast.TextSize = px
	self.toast.Font = czcionka
	self.wysokoscWiersza = wiersz
end

function Okno:_wiersz(nazwa, nr)
	local f = Instance.new("Frame")
	f.Name = nazwa
	f.BackgroundTransparency = 1
	f.Position = UDim2.new(0, 6, (nr - 1) / self.wiersze, 3)
	f.Size = UDim2.new(1, -12, 1 / self.wiersze, 0)
	f.Parent = self.okno
	return f
end

-- id założony w slocie okna (strój nil = dawny szablon = strój odniesienia)
local function wSlocie(D, klasa, stroj, slot)
	local lista = stroj or D.klasy[klasa].odniesienie
	for _, id in lista do
		if L.wybieralny(D, klasa, id) and L.slotOkna(D, id) == slot then
			return id
		end
	end
	return nil
end

function Okno:pokaz(stan)
	local D, op = self.D, self.opcje
	for _, d in self.okno:GetChildren() do
		if d:IsA("Frame") then
			d:Destroy()
		end
	end
	table.clear(self.teksty)
	self.stan = stan
	self.wiersze = 3 + #stan.oferta
	local T = D.teksty
	-- nagłówek: PRÓBA, zakładki klas, zamknij
	local n = self:_wiersz("Naglowek", 1)
	local proba = etykieta(n, "Proba", "PRÓBA", 0, 0.16)
	proba.TextColor3 = kolor(D, "ramka")
	table.insert(self.teksty, proba)
	local szer = 0.74 / #D.kolejnoscKlas
	for i, k in D.kolejnoscKlas do
		self:_przycisk(n, "Zakladka_" .. k, D.klasy[k].nazwa, 0.16 + (i - 1) * szer, szer, k == stan.klasa, function()
			op.naKlase(k)
		end)
	end
	self:_przycisk(n, "Zamknij", T.zamknij, 0.9, 0.1, false, function()
		op.naZamknij()
	end)
	-- sloty: nazwa, poprzedni, przedmiot, następny (opcje: nic + przedmioty slotu)
	for i, s in stan.oferta do
		local w = self:_wiersz("Slot_" .. s.slot, 1 + i)
		local nazwa = etykieta(w, "Slot", s.nazwa, 0, 0.26)
		nazwa.TextColor3 = kolor(D, "ramka")
		nazwa.TextXAlignment = Enum.TextXAlignment.Left
		table.insert(self.teksty, nazwa)
		local opcjeSlotu = { false }
		for _, id in s.przedmioty do
			table.insert(opcjeSlotu, id)
		end
		local teraz = wSlocie(D, stan.klasa, stan.stroj, s.slot)
		local poz = 1
		for j, id in opcjeSlotu do
			if id == teraz then
				poz = j
			end
		end
		local function wybierz(krok)
			local nowa = opcjeSlotu[((poz - 1 + krok) % #opcjeSlotu) + 1]
			op.naWybor(s.slot, if nowa == false then nil else nowa)
		end
		self:_przycisk(w, "Poprzedni", "<", 0.26, 0.11, false, function()
			wybierz(-1)
		end)
		local t = etykieta(w, "Nazwa", if teraz then D.przedmioty[teraz].nazwa else T.brak, 0.37, 0.52)
		t.TextColor3 = kolor(D, "tekst")
		table.insert(self.teksty, t)
		self:_przycisk(w, "Nastepny", ">", 0.89, 0.11, false, function()
			wybierz(1)
		end)
	end
	-- zestawy i dawny wygląd
	local z = self:_wiersz("Zestawy", 2 + #stan.oferta)
	local ile = #D.zestawyOkna + 1
	for i, id in D.zestawyOkna do
		local nazwa = T["zestaw_" .. id]
		for _, x in D.klasy[stan.klasa].zestawy do
			if x.id == id and nazwa == nil then
				nazwa = x.nazwa
			end
		end
		nazwa = nazwa or id
		self:_przycisk(z, "Zestaw_" .. id, nazwa, (i - 1) / ile, 1 / ile, false, function()
			op.naZestaw(id)
		end)
	end
	self:_przycisk(z, "Dawny", T.dawny, (ile - 1) / ile, 1 / ile, stan.stroj == nil, function()
		op.naDawny()
	end)
	-- ruch podglądu: poprzedni, nazwa, następny, zagraj, wszystkie
	local r = self:_wiersz("Ruch", 3 + #stan.oferta)
	self:_przycisk(r, "Poprzedni", "<", 0, 0.1, false, function()
		op.naRuch(-1)
	end)
	local rn = etykieta(r, "Nazwa", T.ruch .. ": " .. (stan.ruch or "?"), 0.1, 0.4)
	rn.TextColor3 = kolor(D, "tekst")
	table.insert(self.teksty, rn)
	self:_przycisk(r, "Nastepny", ">", 0.5, 0.1, false, function()
		op.naRuch(1)
	end)
	self:_przycisk(r, "Zagraj", T.zagraj, 0.6, 0.15, false, function()
		op.naZagraj()
	end)
	self:_przycisk(r, "Wszystkie", T.wszystkie, 0.75, 0.25, false, function()
		op.naWszystkie()
	end)
	self:uloz()
end

function Okno:komunikat(tekst, blad)
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
