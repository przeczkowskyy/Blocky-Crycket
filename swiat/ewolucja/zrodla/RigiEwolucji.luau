--[[
	RigiEwolucji — rig smoka z danych (Motor6D w modelu zbudowanym przez zbuduj.py) i odtwarzacz klipów po stronie klienta.
	Klipy ustawiają Motor6D.Transform liczbami z KlipyEwolucji (bez Animatora i bez wgranych animacji — działa w opublikowanej
	grze). Dwie warstwy: pętla bazowa (spoczynek / chod / bieg albo nadpisanie: ogien_petla, szybowanie_petla, cokol)
	z przenikaniem i jednorazowa akcja na wierzchu (gryz1–3, splun, ogon_zamach, ryk, trafienie, koziolek, pozarcie, radosc,
	…) z wejściem i wyjściem; po akcji wraca ruch. Zdarzenia klipów (ugryzienie, strzal, ogien_start, …) zwraca krok().
]]
local KL = require(script.Parent:WaitForChild("KlipyEwolucji"))

local R = {}
R.__index = R

local PRZEJSCIE = 0.18
local rad = math.rad

function R.nowy(model: Model, W, skala: number?)
	local self = setmetatable({}, R)
	self.model, self.W = model, W
	self.skala = skala or 1
	self.korzen = model.PrimaryPart
	local kp = model:GetAttribute("KorzenPoz")
	self.korzenOff = (if typeof(kp) == "Vector3" then kp else Vector3.zero) * (skala or 1)
	self.motory = {}
	for i, nazwa in W.stawy do
		local kosc = model:FindFirstChild(nazwa)
		self.motory[i] = kosc and kosc:FindFirstChildOfClass("Motor6D") or false
	end
	self.n = W.n
	self.poza, self.tmp, self.pop = KL.nowaPoza(W.n), KL.nowaPoza(W.n), KL.nowaPoza(W.n)
	local spocz = W.klipy.spoczynek or next(W.klipy) and W.klipy[next(W.klipy)]
	self.loko = { k = spocz, t = math.random() * 2, tempo = 1 }
	self.lokoPop = nil
	self.przejscie = 1
	self.akcja = nil
	self.zd = {}
	self.grane = {}
	return self
end

function R:licz(nazwa: string)
	self.grane[nazwa] = (self.grane[nazwa] or 0) + 1
	if self.wspolne then
		self.wspolne[nazwa] = (self.wspolne[nazwa] or 0) + 1
	end
end

function R:ma(nazwa: string): boolean
	return self.W.klipy[nazwa] ~= nil
end

-- pętla bazowa z przenikaniem; chod ↔ bieg zachowują fazę kroku
function R:petla(nazwa: string, tempo: number?)
	local k = self.W.klipy[nazwa]
	if not k then
		return
	end
	if self.loko.k == k then
		self.loko.tempo = tempo or 1
		return
	end
	local stary = self.loko
	local t = 0
	if stary.k.predkosc and k.predkosc then
		t = (stary.t % stary.k.dl) / stary.k.dl * k.dl
	end
	self.lokoPop = stary
	self.przejscie = 0
	self.loko = { k = k, t = t, tempo = tempo or 1 }
	self:licz(nazwa)
end

function R:petlaNazwa(): string
	return self.loko.k.nazwa
end

-- akcja jednorazowa: od (sekundy startu w klipie), tempo, wejscie / wyjscie (s), slaby (nie przerywa innych akcji)
function R:graj(nazwa: string, o): boolean
	o = o or {}
	local k = self.W.klipy[nazwa]
	if not k then
		return false
	end
	local A = self.akcja
	if o.slaby and A and not A.slaby and A.t < A.k.dl then
		return false
	end
	self.akcja = { k = k, t = o.od or 0, tempo = o.tempo or 1, w = if A then A.w else 0, wejscie = o.wejscie or 0.07,
		wyjscie = o.wyjscie or 0.16, slaby = o.slaby, trzymaj = o.trzymaj, trzymajS = o.trzymajS or 0 }
	self:licz(nazwa)
	return true
end

function R:akcjaNazwa(): string?
	return self.akcja and self.akcja.k.nazwa
end

function R:przerwij(wyjscie: number?)
	if self.akcja then
		self.akcja.t = math.max(self.akcja.t, self.akcja.k.dl)
		self.akcja.trzymaj = false
		self.akcja.trzymajS = 0
		self.akcja.wyjscie = wyjscie or 0.12
	end
end

-- krok animacji: czasy, zdarzenia akcji (lista nazw), poza, zapis do stawów
function R:krok(dt: number)
	local W = self.W
	local zd = self.zd
	table.clear(zd)
	local L = self.loko
	L.t += dt * L.tempo
	KL.probka(W, L.k, L.t, self.poza)
	local P = self.lokoPop
	if P then
		P.t += dt * P.tempo
		self.przejscie = math.min(1, self.przejscie + dt / PRZEJSCIE)
		KL.probka(W, P.k, P.t, self.pop)
		KL.mieszaj(self.pop, self.poza, self.przejscie, W.n)
		self.poza, self.pop = self.pop, self.poza
		if self.przejscie >= 1 then
			self.lokoPop = nil
		end
	end
	local A = self.akcja
	if A then
		local t0 = A.t
		A.t += dt * A.tempo
		KL.zdarzenia(A.k, t0, A.t, zd)
		if A.t >= A.k.dl + A.trzymajS and not A.k.petla and not A.trzymaj then
			A.w -= dt / A.wyjscie
		else
			A.w = math.min(1, A.w + dt / A.wejscie)
		end
		if A.w <= 0 then
			self.akcja = nil
		else
			KL.probka(W, A.k, A.t, self.tmp)
			KL.mieszaj(self.poza, self.tmp, A.w, W.n)
		end
	end
	self:zastosuj()
	return zd
end

function R:zastosuj()
	local p, s = self.poza, self.skala
	for i = 1, self.n do
		local m = self.motory[i]
		if m then
			local b = (i - 1) * 6
			m.Transform = CFrame.new(p[b + 1] * s, p[b + 2] * s, p[b + 3] * s) * CFrame.fromOrientation(rad(p[b + 4] / 10), rad(p[b + 5] / 10), rad(p[b + 6] / 10))
		end
	end
end

-- korzeń w świecie: base = ziemia pod środkiem tułowia z obrotem (przód −Z)
function R:ustaw(base: CFrame)
	if self.korzen then
		self.korzen.CFrame = base * CFrame.new(self.korzenOff)
	end
end

-- poza nieruchoma (cokół trofeum): jedna próbka pętli w chwili t
function R.zamroz(model: Model, W, nazwa: string, t: number?)
	local r = R.nowy(model, W)
	local k = W.klipy[nazwa] or r.loko.k
	r.loko = { k = k, t = t or 0, tempo = 0 }
	r:krok(0)
	return r
end

return R
