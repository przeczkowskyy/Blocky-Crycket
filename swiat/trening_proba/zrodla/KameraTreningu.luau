--[[
	KameraTreningu — czysty rachunek kamery stanowisk Training Center w stylu ekranu walki (ModuleScript w
	Workspace/TreningProba/Moduly). Bez instancji Roblox: punkt to tablica { x, y, z }, kąt widzenia w stopniach
	(pionowy, jak Camera.FieldOfView), ujęcie to { oko = punkt, cel = punkt, kat = liczba }. Klient zamienia ujęcie
	na CFrame.lookAt i FieldOfView co klatkę.

	Lustro w Pythonie: swiat/trening_proba/kamera_treningu.py — ten sam rachunek rysuje podglądy (podglad.py) i jest
	sprawdzany w testach offline (pole gry na czterech ekranach, zbliżenie na postać po rundzie).

	Ujęcia (wzór: swiat/test_walki2/zrodla/OdtwarzaczWalki2.luau — wąski kąt widzenia, niski kadr, dojazdy):
		K.stanowisko(D, gra, czas)                 przed rundą: kamera gry z lekkim kołysaniem wokół celu
		K.odliczanie(D, gra, doStartu)             dojazd z ujęcia „start” do kamery gry; kończy się przed startem
		K.gra(D, gra)                              runda: kamera stoi (pole gry czytelne — test 5e)
		K.final(D, gra, korzen, fx, aspekt, czas)  po rundzie: zbliżenie na postać; fx = ułamek szerokości ekranu,
		                                           w którym ma stać postać (reszta jest dla karty podsumowania)
	Dodatki: K.przejscie(a, b, u) — płynne przejście między ujęciami; K.zawezenie(D, rodzaj, wiek) — o ile stopni
	zawęzić kąt po trafieniu („uderzenie”, „mocne”, „seria”); K.wstrzas(D, sila, wiek) — amplituda drżenia;
	K.katOkna(kat, wsp) — kąt dla okna, w którym ekran telefonu jest tylko środkową częścią (emulacja w testach).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local K = {}

function K.gladko(x)
	if x <= 0 then
		return 0
	elseif x >= 1 then
		return 1
	end
	return x * x * (3 - 2 * x)
end

-- szybki początek, łagodny koniec (dojazd kamery)
function K.wyjscie(x)
	if x <= 0 then
		return 0
	elseif x >= 1 then
		return 1
	end
	local q = 1 - x
	return 1 - q * q * q
end

local function mieszaj(a, b, u)
	return { a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, a[3] + (b[3] - a[3]) * u }
end

function K.gra(D, gra)
	local W = D.swiat[gra]
	return { oko = W.oko, cel = W.cel, kat = W.kat }
end

function K.przejscie(a, b, u)
	local g = K.gladko(u)
	return { oko = mieszaj(a.oko, b.oko, g), cel = mieszaj(a.cel, b.cel, g), kat = a.kat + (b.kat - a.kat) * g }
end

-- przed rundą: oko kołysze się po łuku wokół pionowej osi przez cel (kadr „żyje”, ale nic się nie rozgrywa)
function K.stanowisko(D, gra, czas)
	local W = D.swiat[gra]
	local kol = D.ui.kamera.kolysanie
	local a = math.rad(kol.stopnie) * math.sin(2 * math.pi * czas / kol.okres_s)
	local dx, dz = W.oko[1] - W.cel[1], W.oko[3] - W.cel[3]
	local c, s = math.cos(a), math.sin(a)
	return { oko = { W.cel[1] + dx * c + dz * s, W.oko[2], W.cel[3] - dx * s + dz * c }, cel = W.cel, kat = W.kat }
end

-- odliczanie: doStartu = sekundy do początku rundy; dojazd kończy się odliczanie_koniec_s przed startem i od tej
-- chwili kamera stoi dokładnie w ujęciu gry (zanim pojawi się pierwsze zdarzenie)
function K.odliczanie(D, gra, doStartu)
	local W = D.swiat[gra]
	local koniec = D.ui.kamera.odliczanie_koniec_s
	local u = 1 - (doStartu - koniec) / (D.runda.odliczanie_s - koniec)
	return K.przejscie(W.start, K.gra(D, gra), u)
end

-- kierunek poziomy od postaci do kamery zbliżenia w chwili czas (azymut: 0 = +Z, dodatni w stronę +X)
function K.kierunekFinalu(D, gra, czas)
	local F = D.swiat[gra].final
	local O = D.ui.kamera.final
	local znak = if F.azymut < 0 then -1 else 1
	local dryf = math.min(O.dryf_max, O.dryf_stopnie_s * math.max(0, czas))
	local az = math.rad(F.azymut - znak * dryf)
	return { math.sin(az), 0, math.cos(az) }
end

--[[ Zbliżenie na postać po rundzie. korzen = środek HumanoidRootPart postaci; kamera stoi nisko przed postacią
	(postać obraca się do niej — klient), dojeżdża o „dojazd” w dojazd_s i powoli objeżdża (dryf). Postać ma stać
	w ułamku fx szerokości ekranu (0 = lewy brzeg), więc cel kamery jest przesunięty w prawo o kąt, którego tangens
	to (1 − 2·fx) · tg(kat / 2) · aspekt (aspekt = szerokość / wysokość widoku). ]]
function K.final(D, gra, korzen, fx, aspekt, czas)
	local F = D.swiat[gra].final
	local O = D.ui.kamera.final
	local gx, gy, gz = korzen[1], korzen[2] - O.korzen_nad_ziemia, korzen[3]
	local kier = K.kierunekFinalu(D, gra, czas)
	local d = F.dystans * (1 + O.dojazd * (1 - K.wyjscie(czas / O.dojazd_s)))
	local oko = { gx + kier[1] * d, gy + F.wysokosc, gz + kier[3] * d }
	local c0 = { gx, gy + F.cel_wysokosc, gz }
	local vx, vy, vz = c0[1] - oko[1], c0[2] - oko[2], c0[3] - oko[3]
	local d0 = math.sqrt(vx * vx + vy * vy + vz * vz)
	local h = math.sqrt(vx * vx + vz * vz)
	-- wektor „w prawo” kamery patrzącej na postać: kierunek × góra = (−vz, 0, vx) / h
	local rx, rz = -vz / h, vx / h
	local t = (1 - 2 * fx) * math.tan(math.rad(F.kat) / 2) * aspekt
	return { oko = oko, cel = { c0[1] + rx * d0 * t, c0[2], c0[3] + rz * d0 * t }, kat = F.kat }
end

-- o ile stopni zawęzić kąt widzenia po trafieniu: od razu pełne zawężenie, potem powrót (kwadratowo) w czas_s
function K.zawezenie(D, rodzaj, wiek)
	local p = D.ui.kamera[rodzaj]
	if p == nil or wiek < 0 or wiek >= p.czas_s then
		return 0
	end
	local u = 1 - wiek / p.czas_s
	return p.kat * u * u
end

-- amplituda drżenia kamery (w studach): gaśnie wykładniczo jak w walce; poniżej progu = 0
function K.wstrzas(D, sila, wiek)
	local amp = sila * math.exp(-wiek * D.ui.kamera.wstrzas_zanik)
	if amp < 0.004 then
		return 0
	end
	return amp
end

-- kąt widzenia okna, w którym ekran o kącie kat zajmuje środkową część wysokości (wsp = wysokość okna / wysokość
-- ekranu ≥ 1; emulacja telefonu w testach — w grze wsp = 1 i kąt zostaje)
function K.katOkna(kat, wsp)
	return math.deg(2 * math.atan(math.tan(math.rad(kat) / 2) * wsp))
end

return K
