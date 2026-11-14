--[[
	Klipy — odtwarzanie WŁASNYCH klipów postaci z danych, bez zasobów Animation i bez uploadu.

	Klip to próbki pozy co klatkę (30 kl./s) dla animowanych kości, policzone w Blenderze z tych samych krzywych co
	filmy modeli (swiat/test_walki2/aktorzy.py → dane/<klucz>.json → moduł Moduly/DaneAktorow/<klucz>). Odtwarzacz co
	klatkę wpisuje pozę w Motor6D.Transform stawów modelu (lokalnego klonu u klienta). Działa w trybie Play i w
	opublikowanej grze (nic nie zależy od KeyframeSequenceProvider). Nie działa w trybie Edit: tam silnik fizyki nie
	przelicza stawów, więc części stoją (zrzuty klatek robimy w Play — testy/klatki_aktorow.py).

	Model musi mieć: zakotwiczony korzeń (HumanoidRootPart), części kości jako bezpośrednie dzieci modelu
	(nazwy jak w danych) i w każdej z nich jej Motor6D do rodzica. NIE może mieć Animatora, który grałby swoje ścieżki
	(nadpisałby Transform). Tak buduje szablony budowa/szablon.luau.

	API:
		local Klipy = require(Moduly.Klipy)
		local o = Klipy.nowy(model, dane, opcje?)   -- dane = require(Moduly.DaneAktorow[klucz])
			opcje.reczny = true  → nikt nie woła krok/zastosuj za Ciebie (np. własna oś czasu z zwolnieniem);
			                       domyślnie odtwarzacz liczy się sam co klatkę (RunService.PreSimulation).
		o:graj(nazwa, opcje?) → tor | nil (nil = nie ma takiego klipu)
			opcje.przejscie  s płynnego przejścia od bieżącej pozy (domyślnie 0,15; 0 = od razu)
			opcje.predkosc   mnożnik prędkości tego toru (domyślnie 1)
			opcje.dlugosc    s — dopasuj prędkość tak, by klip trwał tyle (zamiast predkosc)
			opcje.petla      nadpisz zapętlenie z danych (true / false)
			opcje.odCzasu    s — zacznij od tej chwili klipu
			opcje.potem      nazwa klipu, który zagra po końcu (np. "idle"); bez tego zostaje ostatnia klatka
			opcje.przejsciePotem  s przejścia do „potem” (domyślnie jak przejscie)
		o:zatrzymaj(przejscie?)        wszystkie tory wygasają do pozy zerowej (spoczynek klocków)
		o:poza(nazwa, czas)            natychmiastowa poza: klip zatrzymany w chwili czas (do zrzutów klatek)
		o:ustawNakladke(kosc, cf|nil)  dodatkowy obrót/przesunięcie kości PO klipie (ruch proceduralny: garda,
		                               odchylenie głowy) — Transform = klip * nakladka; nil usuwa
		o.tempo                        mnożnik wszystkich torów (×1 / ×2 / ×4 dla gracza; 0 = pauza)
		o:krok(dt) / o:zastosuj()      ręczne liczenie (opcje.reczny) — krok przesuwa czas, zastosuj wpisuje Transform
		o:maKlip(nazwa) → boolean      o:dlugoscKlipu(nazwa) → s | nil      o:biezacy() → tor | nil
		o:zniszcz()                    odłącza od pętli i zeruje stawy (model zostaje)
	tor (wynik graj):
		tor.nazwa, tor.czas (s), tor.dlugosc (s, dla prędkości 1), tor.petla, tor.predkosc, tor.zakonczony
		tor:naKoniec(fn)               fn(tor) raz, gdy klip niezapętlony dobiegnie końca (przy tempie > 0)
		tor:naChwili(s, fn)            fn(tor) raz, gdy czas klipu minie s (np. chwila trafienia z tabeli aktorów)
		tor:ustawCzas(s)
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local RunService = game:GetService("RunService")

local Klipy = {}
Klipy.__index = Klipy
local Tor = {}
Tor.__index = Tor

local ID = CFrame.identity
local DOMYSLNE_PRZEJSCIE = 0.15

------------------------------------------------------------------ dane → CFrame'y (raz na zestaw danych, wspólne dla klonów)
local przeliczone: { [any]: any } = setmetatable({}, { __mode = "k" }) :: any

local function przelicz(dane)
	local gotowe = przeliczone[dane]
	if gotowe then
		return gotowe
	end
	gotowe = {}
	for nazwa, kl in dane.klipy do
		local klatki = table.create(#kl.klatki)
		for f, w in kl.klatki do
			local wiersz = {}
			for j, idx in kl.kosci do
				local o = (j - 1) * 6
				wiersz[idx] = CFrame.new(w[o + 1], w[o + 2], w[o + 3]) * CFrame.fromOrientation(w[o + 4], w[o + 5], w[o + 6])
			end
			klatki[f] = wiersz
		end
		gotowe[nazwa] = {
			nazwa = nazwa, fps = kl.fps, petla = kl.petla, dl = kl.dl, dlugosc = kl.dl / kl.fps, kosci = kl.kosci,
			klatki = klatki,
		}
	end
	przeliczone[dane] = gotowe
	return gotowe
end

------------------------------------------------------------------ wspólna pętla
local aktywne: { [any]: boolean } = {}
local polaczenie: RBXScriptConnection? = nil

local function petla(dt: number)
	for o in aktywne do
		local ok, blad = pcall(function()
			o:krok(dt)
			o:zastosuj()
		end)
		if not ok then
			aktywne[o] = nil
			warn("[TestWalki2] Klipy: błąd odtwarzania — " .. tostring(blad))
		end
	end
end

local function zapnij(o)
	aktywne[o] = true
	if not polaczenie then
		local sygnal = RunService.PreSimulation
		polaczenie = sygnal:Connect(petla)
	end
end

local function odepnij(o)
	aktywne[o] = nil
	if polaczenie and next(aktywne) == nil then
		polaczenie:Disconnect()
		polaczenie = nil
	end
end

------------------------------------------------------------------ odtwarzacz
function Klipy.nowy(model: Model, dane, opcje: any?)
	opcje = opcje or {}
	local self = setmetatable({}, Klipy)
	self.model = model
	self.klipy = przelicz(dane)
	self.stawy = {} -- indeks kości -> Motor6D
	self.nazwyKosci = {} -- nazwa kości -> indeks
	for idx, k in dane.kosci do
		local czesc = model:FindFirstChild(k[1])
		local staw = czesc and czesc:FindFirstChildOfClass("Motor6D")
		if not staw then
			error(string.format("Klipy: model %s nie ma kości %s ze stawem Motor6D", model.Name, tostring(k[1])))
		end
		self.stawy[idx] = staw
		self.nazwyKosci[k[1]] = idx
	end
	self.tory = {} -- najstarszy pierwszy
	self.nakladki = {} -- indeks kości -> CFrame
	self.tempo = 1
	self.reczny = opcje.reczny == true
	if not self.reczny then
		zapnij(self)
	end
	return self
end

function Klipy:maKlip(nazwa: string): boolean
	return self.klipy[nazwa] ~= nil
end

function Klipy:dlugoscKlipu(nazwa: string): number?
	local k = self.klipy[nazwa]
	return k and k.dlugosc
end

function Klipy:biezacy()
	return self.tory[#self.tory]
end

local function nowyTor(klip, opcje)
	local t = setmetatable({}, Tor)
	t.klip = klip
	t.nazwa = klip.nazwa
	t.dlugosc = klip.dlugosc
	t.petla = if opcje.petla ~= nil then opcje.petla == true else klip.petla
	t.predkosc = opcje.predkosc or 1
	if opcje.dlugosc and opcje.dlugosc > 0 and klip.dlugosc > 0 then
		t.predkosc = klip.dlugosc / opcje.dlugosc
	end
	t.czas = math.clamp(opcje.odCzasu or 0, 0, klip.dlugosc)
	t.waga = 0
	t.cel = 1
	t.zmiana = 0 -- zmiana wagi na sekundę
	t.zakonczony = false
	t.chwile = {}
	t.konce = {}
	t.potem = opcje.potem
	t.przejsciePotem = opcje.przejsciePotem
	return t
end

-- przejście: nowy tor rośnie 0 → 1, a wszystkie stare gasną 1 → 0 w tym samym czasie
local function ustawWagi(self, nowy, przejscie: number)
	for _, t in self.tory do
		if t ~= nowy then
			t.cel = 0
			if przejscie <= 0 then
				t.waga = 0
			else
				t.zmiana = math.max(t.waga, 0.001) / przejscie
			end
		end
	end
	if nowy then
		nowy.cel = 1
		if przejscie <= 0 then
			nowy.waga = 1
		else
			nowy.zmiana = 1 / przejscie -- pierwszy klip też wchodzi płynnie: od pozy zerowej (spoczynek klocków)
		end
	end
end

function Klipy:graj(nazwa: string, opcje: any?)
	local klip = self.klipy[nazwa]
	if not klip then
		return nil
	end
	opcje = opcje or {}
	local t = nowyTor(klip, opcje)
	t.wlasciciel = self
	table.insert(self.tory, t)
	ustawWagi(self, t, opcje.przejscie or DOMYSLNE_PRZEJSCIE)
	return t
end

function Klipy:zatrzymaj(przejscie: number?)
	ustawWagi(self, nil, przejscie or DOMYSLNE_PRZEJSCIE)
end

function Klipy:poza(nazwa: string, czas: number)
	table.clear(self.tory)
	local t = self:graj(nazwa, { przejscie = 0, predkosc = 0, odCzasu = czas })
	if t then
		t.waga = 1
	end
	self:zastosuj()
	return t
end

function Klipy:ustawNakladke(kosc: string, cf: CFrame?)
	local idx = self.nazwyKosci[kosc]
	if idx then
		self.nakladki[idx] = cf
	end
end

function Tor:naKoniec(fn)
	table.insert(self.konce, fn)
	return self
end

function Tor:naChwili(s: number, fn)
	table.insert(self.chwile, { s = s, fn = fn, bylo = self.czas > s })
	return self
end

function Tor:ustawCzas(s: number)
	self.czas = math.clamp(s, 0, self.dlugosc)
	for _, c in self.chwile do
		c.bylo = self.czas > c.s
	end
end

local function wywolaj(lista, tor)
	for _, fn in lista do
		task.spawn(fn, tor)
	end
end

function Klipy:krok(dt: number)
	local doUsuniecia = nil
	for i, t in self.tory do
		-- wagi
		if t.waga ~= t.cel then
			if t.cel > t.waga then
				t.waga = math.min(t.cel, t.waga + t.zmiana * dt)
			else
				t.waga = math.max(t.cel, t.waga - t.zmiana * dt)
			end
		end
		if t.cel == 0 and t.waga <= 0 then
			doUsuniecia = doUsuniecia or {}
			table.insert(doUsuniecia, i)
			continue
		end
		-- czas
		local krok = dt * t.predkosc * self.tempo
		if krok ~= 0 then
			local przed = t.czas
			local nowy = przed + krok
			if t.petla then
				local zawinal = t.dlugosc > 0 and nowy >= t.dlugosc
				local koniec = nowy
				if zawinal then
					nowy %= t.dlugosc
				end
				for _, c in t.chwile do -- w pętli chwila wraca w każdym obiegu
					if (c.s > przed and c.s <= koniec) or (zawinal and c.s <= nowy) then
						task.spawn(c.fn, t)
					end
				end
				t.czas = nowy
			else
				t.czas = math.clamp(nowy, 0, t.dlugosc)
				for _, c in t.chwile do
					if not c.bylo and t.czas >= c.s then
						c.bylo = true
						task.spawn(c.fn, t)
					end
				end
				if not t.zakonczony and t.czas >= t.dlugosc then
					t.zakonczony = true
					wywolaj(t.konce, t)
					if t.potem and t.cel > 0 then
						local nastepny = t.potem
						t.potem = nil
						task.defer(function()
							if t.cel > 0 and self.tory[#self.tory] == t then
								self:graj(nastepny, { przejscie = t.przejsciePotem or DOMYSLNE_PRZEJSCIE })
							end
						end)
					end
				end
			end
		end
	end
	if doUsuniecia then
		for j = #doUsuniecia, 1, -1 do
			table.remove(self.tory, doUsuniecia[j])
		end
	end
end

-- poza toru w chwili czas (liniowo między sąsiednimi próbkami)
local function probka(klip, czas: number, petla: boolean)
	local f = czas * klip.fps
	local i0 = math.floor(f)
	local u = f - i0
	local ostatnia = klip.dl
	if i0 >= ostatnia then
		return klip.klatki[ostatnia + 1], nil, 0
	end
	local a = klip.klatki[i0 + 1]
	local b = klip.klatki[i0 + 2]
	if not b then
		b = if petla then klip.klatki[1] else a
	end
	return a, b, u
end

function Klipy:zastosuj()
	local pozy = {} -- indeks -> CFrame
	local wagi = {} -- indeks -> suma wag
	for _, t in self.tory do
		local w = t.waga
		if w > 0 then
			local a, b, u = probka(t.klip, t.czas, t.petla)
			for idx in self.stawy do
				local cf
				local pa = a and a[idx]
				if pa then
					cf = if b and u > 0 then pa:Lerp(b[idx] or pa, u) else pa
				else
					cf = ID
				end
				local s = (wagi[idx] or 0) + w
				local stara = pozy[idx]
				pozy[idx] = if stara then stara:Lerp(cf, w / s) else cf
				wagi[idx] = s
			end
		end
	end
	for idx, staw in self.stawy do
		local cf = pozy[idx] or ID
		local s = wagi[idx] or 0
		if s < 1 then
			cf = ID:Lerp(cf, s)
		end
		local n = self.nakladki[idx]
		if n then
			cf = cf * n
		end
		staw.Transform = cf
	end
end

function Klipy:zniszcz()
	odepnij(self)
	table.clear(self.tory)
	for _, staw in self.stawy do
		if staw.Parent then
			staw.Transform = ID
		end
	end
end

return Klipy
