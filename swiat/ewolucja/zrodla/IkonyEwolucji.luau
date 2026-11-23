--[[
	IkonyEwolucji — wybór ikony interfejsu (interfejs1), bez API Roblox (próby offline w luau_mini).
	Tabela numerów obrazów: ustawienia.json, klucz „ikony.id” (w grze D.ikony). Numer > 0 → obraz rbxassetid;
	0 albo brak → zastępstwo: mały model 3D (wzorzec z ReplicatedStorage albo model z części: moneta, korona),
	rysunek z ramek (kłódka, romb wariantu) albo krótki napis na kolorowej płytce. Po wpisaniu numerów ikony
	pojawiają się bez zmiany kodu.
]]
local I = {}

-- zastępstwa: { typ, wartość, napis zapasowy }
I.ZASTEPCZE = {
	bite = { "napis", "BITE" },
	dash = { "napis", "DASH" },
	ember_spit = { "napis", "EMBER" },
	fire_breath = { "napis", "BREATH" },
	inferno_breath = { "napis", "INFERNO" },
	tail_sweep = { "napis", "TAIL" },
	wing_glide = { "napis", "GLIDE" },
	roar = { "napis", "ROAR" },
	meteor_dive = { "napis", "METEOR" },
	zablokowane = { "rysunek", "klodka" },
	moneta = { "model", "moneta", "$" },
	korona = { "model", "korona", "TOP" },
	skarb = { "wzorzec", "Rekwizyt_stos_zlota_1", "HOARD" },
	kula_mala = { "wzorzec", "Rekwizyt_kula_mala", "ORB" },
	kula_duza = { "wzorzec", "Rekwizyt_kula_duza", "ORB" },
	kula_wielka = { "wzorzec", "Rekwizyt_kula_wielka", "ORB" },
	wariant_gold = { "rysunek", "romb", "FFC934" },
	wariant_crystal = { "rysunek", "romb", "7FF8FF" },
	wariant_ruby = { "rysunek", "romb", "FF3D6A" },
	wariant_rainbow = { "rysunek", "romb", "FF7AF0" },
	ulepszenie_jaw = { "napis", "JAW" },
	ulepszenie_speed = { "napis", "SPEED" },
	ulepszenie_appetite = { "napis", "EAT" },
	czaszka = { "napis", "SKULL" },
}

-- numer obrazu z tabeli (liczba albo napis z cyframi); 0 / brak / zły wpis → nil
function I.numer(ids, nazwa: string): number?
	local v = ids and ids[nazwa]
	if type(v) == "string" then
		local k = string.find(v, "//", 1, true)
		v = tonumber(if k then string.sub(v, k + 2) else v)
	end
	if type(v) == "number" and v > 0 and v == math.floor(v) then
		return v
	end
	return nil
end

-- opis ikony do narysowania: { typ = "obraz" | "wzorzec" | "model" | "rysunek" | "napis", wartosc, napis, kolor }
-- maWzorzec(nazwa) → bool: czy wzorzec istnieje (bez niego napis zapasowy); napis — nadpisanie tekstu napisu
function I.wybierz(ids, nazwa: string, maWzorzec, napis: string?)
	local n = I.numer(ids, nazwa)
	if n then
		return { typ = "obraz", wartosc = "rbxassetid://" .. tostring(n) }
	end
	local z = I.ZASTEPCZE[nazwa]
	if not z then
		return { typ = "napis", napis = napis or (if string.upper then string.upper(nazwa) else nazwa) }
	end
	local typ = z[1]
	if typ == "napis" then
		return { typ = "napis", napis = napis or z[2] }
	elseif typ == "wzorzec" then
		if maWzorzec and maWzorzec(z[2]) then
			return { typ = "wzorzec", wartosc = z[2] }
		end
		return { typ = "napis", napis = napis or z[3] }
	elseif typ == "rysunek" then
		return { typ = "rysunek", wartosc = z[2], kolor = z[3] }
	end
	return { typ = "model", wartosc = z[2], napis = z[3] }
end

-- ile ikon ma już obraz (raport / próby)
function I.ileObrazow(ids): number
	local n = 0
	for nazwa in I.ZASTEPCZE do
		if I.numer(ids, nazwa) then
			n += 1
		end
	end
	return n
end

return I
