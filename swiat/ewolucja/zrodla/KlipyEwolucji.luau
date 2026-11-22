--[[
	KlipyEwolucji — próbkowanie klipów smoka z danych `swiat/ewolucja/modele/dane/<id>_klipy.json` (format /2), bez Roblox
	(same liczby: działa w grze i w testach bez Studio). Poza = płaska tablica 6 × liczba stawów: px, py, pz (study),
	rx, ry, rz (dziesiąte stopnia, do CFrame.fromOrientation). Interpolujemy LICZBY, nie CFrame (ogon_zamach i koziolek
	przechodzą przez 360°); między różnymi klipami kąty mieszamy najkrótszą drogą.
]]
local K = {}

-- zestaw klipów z odkodowanego JSON: czasy w sekundach, przesunięcia jako zbiór
function K.przygotuj(J)
	local W = { stawy = J.stawy, n = #J.stawy, fps = J.fps, krok = J.krok, klipy = {} }
	for nazwa, c in J.klipy do
		local przes = {}
		for _, i in c.przes or {} do
			przes[i] = true
		end
		local zd = {}
		for z, kl in c.zdarzenia or {} do
			zd[z] = kl / J.fps
		end
		W.klipy[nazwa] = { nazwa = nazwa, dl = c.dl / J.fps, petla = c.petla == true, zdarzenia = zd, predkosc = c.predkosc, stawy = c.stawy,
			przes = przes, probki = c.probki }
	end
	return W
end

function K.nowaPoza(n: number)
	local p = {}
	for i = 1, n * 6 do
		p[i] = 0
	end
	return p
end

function K.zeruj(p, n: number)
	for i = 1, n * 6 do
		p[i] = 0
	end
end

-- czas klipu: pętla modulo długość, jednorazowy przycięty do [0, dl]
function K.czas(k, t: number): number
	if k.petla then
		return t % k.dl
	end
	return math.clamp(t, 0, k.dl)
end

-- próbka klipu k w czasie t → poza (stawy spoza klipu = 0, czyli poza C0)
function K.probka(W, k, t: number, poza)
	K.zeruj(poza, W.n)
	t = K.czas(k, t)
	local f = t * W.fps / W.krok
	local a = math.floor(f)
	local u = f - a
	local np = #k.probki
	local A = k.probki[math.min(a + 1, np)]
	local B = k.probki[math.min(a + 2, np)]
	local o = 0
	for _, i in k.stawy do
		local b = (i - 1) * 6
		if k.przes[i] then
			poza[b + 1] = (A[o + 1] + (B[o + 1] - A[o + 1]) * u) / 1000
			poza[b + 2] = (A[o + 2] + (B[o + 2] - A[o + 2]) * u) / 1000
			poza[b + 3] = (A[o + 3] + (B[o + 3] - A[o + 3]) * u) / 1000
			o += 3
		end
		poza[b + 4] = A[o + 1] + (B[o + 1] - A[o + 1]) * u
		poza[b + 5] = A[o + 2] + (B[o + 2] - A[o + 2]) * u
		poza[b + 6] = A[o + 3] + (B[o + 3] - A[o + 3]) * u
		o += 3
	end
	return poza
end

-- a ← a + (b − a) × w; kąty najkrótszą drogą (przejście między klipami bez obrotu wstecz o 360°)
function K.mieszaj(a, b, w: number, n: number)
	if w <= 0 then
		return a
	end
	for j = 0, n - 1 do
		local o = j * 6
		a[o + 1] += (b[o + 1] - a[o + 1]) * w
		a[o + 2] += (b[o + 2] - a[o + 2]) * w
		a[o + 3] += (b[o + 3] - a[o + 3]) * w
		for q = 4, 6 do
			local d = (b[o + q] - a[o + q]) % 3600
			if d > 1800 then
				d -= 3600
			end
			a[o + q] += d * w
		end
	end
	return a
end

-- zdarzenia klipu przekroczone między t0 (wyłącznie) a t1 (włącznie); dla pętli z przejściem przez koniec
function K.zdarzenia(k, t0: number, t1: number, wynik)
	if t1 <= t0 then
		return wynik
	end
	for nazwa, tz in k.zdarzenia do
		if k.petla and k.dl > 0 then
			local c0, c1 = math.floor(t0 / k.dl), math.floor(t1 / k.dl)
			for c = c0, c1 do
				local tt = c * k.dl + tz
				if tt > t0 and tt <= t1 then
					table.insert(wynik, nazwa)
				end
			end
		elseif tz > t0 and tz <= t1 then
			table.insert(wynik, nazwa)
		end
	end
	return wynik
end

-- tempo chodu / biegu dopasowane do prędkości (stopy bez poślizgu): v / (predkosc × skala), w granicach [mn, mx]
function K.tempo(k, v: number, skala: number, mn: number, mx: number): number
	if not k.predkosc or k.predkosc <= 0 then
		return 1
	end
	return math.clamp(v / (k.predkosc * skala), mn, mx)
end

-- czas zdarzenia w klipie (sekundy) albo zapas
function K.czasZdarzenia(W, klip: string, zdarzenie: string, zapas: number?): number?
	local k = W.klipy[klip]
	return (k and k.zdarzenia[zdarzenie]) or zapas
end

return K
