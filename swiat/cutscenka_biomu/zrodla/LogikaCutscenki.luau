--[[
	LogikaCutscenki — czysta logika cutscenki biomu (ModuleScript w Workspace/CutscenkaBiomu/Moduly; czytają go
	SerwerCutscenki i KlientCutscenki). Bez instancji, zegara i Random: tylko liczby, napisy, wartości logiczne i tabele.
	Lustro w Pythonie: swiat/cutscenka_biomu/logika_cutscenki.py (te same funkcje i wzory); test bez Studio
	(testy/test_cutscenki.py) wykonuje ten plik w interpreterze tools/walka/luau_mini.py i porównuje wywołanie po
	wywołaniu. Zmieniasz wzór tutaj — zmień go tam.

	API:
		wProstokacie(x, z, r) → bool
		biomPunktu(biomy, x, y, z) → nr biomu (1…) albo 0        (prostokąt wejścia biomu, y powyżej yMin)
		krzywa(tab, n, krok, t) → x, y, z      (jednostajny Catmull-Rom po płaskiej tablicy próbek co `krok` s)
		widocznosc(t, od, pelnaOd, pelnaDo, doKiedy) → 0…1       (napis: wejście, pełny, zejście)
		wstrzas(t, od, czas, sila) → amplituda                   (gaśnie do zera w `czas` s od `od`)
		uklad(w, h, lewo, gora, prawo, dol, k) → prostokąty napisów i przycisku w pikselach ekranu w × h
		nowyStan() → stan       krok(stan, wejscie, teraz, stale) → { akcja, … }
		sprawdzPrzypadki() → (ok, n, bledy)

	Automat jednego gracza (krok): fazy brak → uspokaja → pyta → laduje → trwa → brak.
		wejscie = { cel = id biomu, w którym gracz stoi i którego cutscenki nie widział (albo nil), wymus = id biomu do
		odtworzenia na życzenie (albo nil), postac (ta sama żywa postać), odpowiedz = nil | "gotowe" | "odmowa",
		strumienie (ile próśb o mapę jeszcze trwa), czas (długość cutscenki biomu), koniec, pominieta,
		przerwij = nil | "reset" | "postac" }
		akcje: "blokuj_walke", "pytaj" (klient: czy może i przygotuj się), "widzial" (pamięć na tak), "zakotwicz",
		"laduj" (wczytanie mapy wzdłuż trasy), "start", "podtrzymaj" (mapa przed kamerą), "przerwij" (klient sprząta),
		"poddaj" (klient milczał probMaks razy — pamięć na tak, żeby nie pytać w kółko), "odblokuj" (zawsze przy wyjściu).
		Pamięć „widział” ustawiamy dopiero, gdy klient przyjął cutscenkę; odmowa (walka, chmury, mini-gra) niczego
		nie zapisuje i serwer pyta ponownie po ponowPoOdmowie s.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

------------------------------------------------------------------ miejsca
function L.wProstokacie(x: number, z: number, r): boolean
	return x >= r.x1 and x <= r.x2 and z >= r.z1 and z <= r.z2
end

function L.biomPunktu(biomy, x: number, y: number, z: number): number
	for i, b in biomy do
		if y > b.yMin and L.wProstokacie(x, z, b.prostokat) then
			return i
		end
	end
	return 0
end

------------------------------------------------------------------ krzywa trasy
local function catmull(p0: number, p1: number, p2: number, p3: number, f: number): number
	return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f)
end

function L.krzywa(tab, n: number, krok: number, t: number): (number, number, number)
	local q = t / krok
	if q <= 0 then
		return tab[1], tab[2], tab[3]
	end
	if q >= n - 1 then
		return tab[3 * n - 2], tab[3 * n - 1], tab[3 * n]
	end
	local i = math.floor(q)
	local f = q - i
	local a = 3 * math.max(i - 1, 0)
	local b = 3 * i
	local c = 3 * (i + 1)
	local d = 3 * math.min(i + 2, n - 1)
	return catmull(tab[a + 1], tab[b + 1], tab[c + 1], tab[d + 1], f), catmull(tab[a + 2], tab[b + 2], tab[c + 2], tab[d + 2], f),
		catmull(tab[a + 3], tab[b + 3], tab[c + 3], tab[d + 3], f)
end

------------------------------------------------------------------ oprawa
function L.widocznosc(t: number, od: number, pelnaOd: number, pelnaDo: number, doKiedy: number): number
	if t <= od or t >= doKiedy then
		return 0
	end
	if t < pelnaOd then
		return (t - od) / (pelnaOd - od)
	end
	if t <= pelnaDo then
		return 1
	end
	return (doKiedy - t) / (doKiedy - pelnaDo)
end

function L.wstrzas(t: number, od: number, czas: number, sila: number): number
	if t < od or t >= od + czas or czas <= 0 then
		return 0
	end
	local f = 1 - (t - od) / czas
	return sila * f * f
end

local function ogranicz(x: number, a: number, b: number): number
	return math.min(b, math.max(a, x))
end

-- Prostokąty w pikselach ekranu w × h; lewo / gora / prawo / dol = bezpieczne marginesy urządzenia (wcięcie, pasek).
function L.uklad(w: number, h: number, lewo: number, gora: number, prawo: number, dol: number, k)
	local m = k.margines
	local pas = math.floor(h * k.pasy + 0.5)
	local pw = ogranicz(w * k.pomin.szer, k.pomin.minSzer, k.pomin.maksSzer)
	local ph = ogranicz(h * k.pomin.wys, k.pomin.minWys, k.pomin.maksWys)
	local pomin = { x = w - prawo - m - pw, y = h - dol - m - ph, w = pw, h = ph, tekst = math.max(k.pomin.tekstMin, math.floor(ph * k.pomin.tekst)) }
	local szer = w - lewo - prawo - 2 * m
	local tn = ogranicz(h * k.nazwa.wys, k.nazwa.min, k.nazwa.maks)
	local nazwa = { x = lewo + m, y = math.floor(h * k.nazwa.y - tn / 2), w = szer, h = tn, tekst = math.floor(tn * 0.9) }
	local td = ogranicz(h * k.nadtytul.wys, k.nadtytul.min, k.nadtytul.maks)
	local nadtytul = { x = lewo + m, y = nazwa.y - td - 4, w = szer, h = td, tekst = math.floor(td) }
	local tp = ogranicz(h * k.podpis.wys, k.podpis.min, k.podpis.maks)
	local wolne = pomin.x - m - (lewo + m)
	local podpis = { x = lewo + m, y = math.min(h - pas, pomin.y) - tp - 8, w = wolne, h = tp, tekst = math.floor(tp) }
	local ts = ogranicz(h * k.straznik.wys, k.straznik.min, k.straznik.maks)
	local straznik = { x = lewo + m, y = math.min(h - pas, h - dol - m) - ts - 6, w = wolne, h = ts, tekst = math.floor(ts * 0.9) }
	return { pas = pas, pomin = pomin, nazwa = nazwa, nadtytul = nadtytul, podpis = podpis, straznik = straznik }
end

------------------------------------------------------------------ automat
function L.nowyStan()
	return { faza = "brak", id = 0, biom = "", wymuszony = false, od = 0, doKiedy = 0, nastepny = 0, wolnyOd = 0, proby = 0, wynik = "" }
end

local function zakoncz(s, akcje, wynik: string)
	table.insert(akcje, "odblokuj")
	s.faza = "brak"
	s.wynik = wynik
end

function L.krok(s, w, teraz: number, k)
	local akcje = {}
	local f = s.faza
	if f == "brak" then
		local biom = w.cel
		if w.wymus ~= nil then
			biom = w.wymus
		end
		if w.postac and biom ~= nil and (w.wymus ~= nil or teraz >= s.wolnyOd) then
			s.id += 1
			s.biom = biom
			s.wymuszony = w.wymus ~= nil
			s.faza = "uspokaja"
			s.od = teraz
			s.wynik = ""
		end
		return akcje
	end
	local przerwij = w.przerwij
	if przerwij == nil and not w.postac then
		przerwij = "postac"
	end
	if przerwij ~= nil then
		if f ~= "uspokaja" then
			table.insert(akcje, "przerwij")
		end
		zakoncz(s, akcje, przerwij)
		if przerwij == "reset" then
			s.wolnyOd = teraz
		end
		return akcje
	end
	if f == "uspokaja" then
		if teraz - s.od >= k.uspokojenie then
			if not s.wymuszony and w.cel ~= s.biom then
				s.faza = "brak"
				s.wynik = "wyszedl"
			else
				s.faza = "pyta"
				s.od = teraz
				table.insert(akcje, "blokuj_walke")
				table.insert(akcje, "pytaj")
			end
		end
	elseif f == "pyta" then
		if w.odpowiedz == "gotowe" then
			s.faza = "laduje"
			s.od = teraz
			s.proby = 0
			table.insert(akcje, "widzial")
			table.insert(akcje, "zakotwicz")
			table.insert(akcje, "laduj")
		elseif w.odpowiedz == "odmowa" then
			zakoncz(s, akcje, "odmowa")
			s.wolnyOd = teraz + k.ponowPoOdmowie
		elseif teraz - s.od >= k.odpowiedz then
			s.proby += 1
			table.insert(akcje, "przerwij")
			if s.proby >= k.probMaks then
				table.insert(akcje, "poddaj")
				s.proby = 0
			end
			zakoncz(s, akcje, "cisza")
			s.wolnyOd = teraz + k.ponowPoCiszy
		end
	elseif f == "laduje" then
		if w.strumienie <= 0 or teraz - s.od >= k.ladowanie then
			s.faza = "trwa"
			s.od = teraz
			s.doKiedy = teraz + w.czas + k.zapas
			s.nastepny = teraz + k.strumienCo
			table.insert(akcje, "start")
		end
	elseif f == "trwa" then
		if w.koniec then
			zakoncz(s, akcje, if w.pominieta then "pominieta" else "koniec")
		elseif teraz >= s.doKiedy then
			table.insert(akcje, "przerwij")
			zakoncz(s, akcje, "czas")
		elseif teraz >= s.nastepny then
			s.nastepny = teraz + k.strumienCo
			table.insert(akcje, "podtrzymaj")
		end
	end
	return akcje
end

------------------------------------------------------------------ przypadki wzorcowe (te same co PRZYPADKI w logika_cutscenki.py)
local R = { x1 = 0, x2 = 10, z1 = -5, z2 = 5 }
local BIOMY = { { yMin = -30, prostokat = R }, { yMin = -30, prostokat = { x1 = 12, x2 = 20, z1 = -5, z2 = 5 } } }
local TAB = { 0, 0, 0, 10, 0, 0, 20, 10, 0, 20, 10, 0 }

local function pierwsza(a, _b, _c)
	return a
end
local function druga(_a, b, _c)
	return b
end

local PRZYPADKI = {
	{ "wProstokacie(5,0)", function() return L.wProstokacie(5, 0, R) end, true },
	{ "wProstokacie(11,0)", function() return L.wProstokacie(11, 0, R) end, false },
	{ "biomPunktu(5,0,0)", function() return L.biomPunktu(BIOMY, 5, 0, 0) end, 1 },
	{ "biomPunktu(15,0,0)", function() return L.biomPunktu(BIOMY, 15, 0, 0) end, 2 },
	{ "biomPunktu(11,0,0)", function() return L.biomPunktu(BIOMY, 11, 0, 0) end, 0 },
	{ "biomPunktu(5,-40,0)", function() return L.biomPunktu(BIOMY, 5, -40, 0) end, 0 },
	{ "krzywa(0).x", function() return pierwsza(L.krzywa(TAB, 4, 1, 0)) end, 0 },
	{ "krzywa(1).x", function() return pierwsza(L.krzywa(TAB, 4, 1, 1)) end, 10 },
	{ "krzywa(0.5).x", function() return pierwsza(L.krzywa(TAB, 4, 1, 0.5)) end, 4.375 },
	{ "krzywa(1.5).y", function() return druga(L.krzywa(TAB, 4, 1, 1.5)) end, 5 },
	{ "krzywa(9).y", function() return druga(L.krzywa(TAB, 4, 1, 9)) end, 10 },
	{ "krzywa(krok 0.5, t 0.5).x", function() return pierwsza(L.krzywa(TAB, 4, 0.5, 0.5)) end, 10 },
	{ "widocznosc(przed)", function() return L.widocznosc(0, 0.1, 0.4, 1.5, 1.9) end, 0 },
	{ "widocznosc(wejscie)", function() return L.widocznosc(0.25, 0.1, 0.4, 1.5, 1.9) end, 0.5 },
	{ "widocznosc(pelna)", function() return L.widocznosc(1, 0.1, 0.4, 1.5, 1.9) end, 1 },
	{ "widocznosc(zejscie)", function() return L.widocznosc(1.7, 0.1, 0.4, 1.5, 1.9) end, 0.5 },
	{ "widocznosc(po)", function() return L.widocznosc(2, 0.1, 0.4, 1.5, 1.9) end, 0 },
	{ "wstrzas(przed)", function() return L.wstrzas(1, 2, 1, 0.4) end, 0 },
	{ "wstrzas(start)", function() return L.wstrzas(2, 2, 1, 0.4) end, 0.4 },
	{ "wstrzas(polowa)", function() return L.wstrzas(2.5, 2, 1, 0.4) end, 0.1 },
	{ "wstrzas(po)", function() return L.wstrzas(3, 2, 1, 0.4) end, 0 },
}

function L.opisyPrzypadkow()
	local opisy = {}
	for i, p in PRZYPADKI do
		opisy[i] = p[1]
	end
	return opisy
end

function L.sprawdzPrzypadki()
	local bledy = {}
	for _, p in PRZYPADKI do
		local wynik = p[2]()
		local zgodne = wynik == p[3]
		if type(wynik) == "number" and type(p[3]) == "number" then
			zgodne = math.abs(wynik - p[3]) < 1e-9
		end
		if not zgodne then
			table.insert(bledy, p[1] .. ": " .. tostring(wynik) .. " zamiast " .. tostring(p[3]))
		end
	end
	return #bledy == 0, #PRZYPADKI, bledy
end

return L
