--[[
	Los — wspólne narzędzia silnika walki v2: własny generator liczb, zaokrąglanie, premia z malejącym przyrostem
	i sprawdzanie liczb. Czysty moduł: nie dotyka świata gry, zegara ani Random.

	Generator Park–Miller (minstd) liczy wyłącznie na liczbach całkowitych mniejszych niż 2^53, więc daje identyczne
	wyniki na każdej platformie — w Luau i w porcie w Pythonie (tools/walka/silnik.py, sekcja Los.luau).
]]

local Los = {}

local MODUL = 2147483647
-- 2^31: dozwolone ziarna to liczby całkowite 0 .. 2^31 − 1 (Silnik.symuluj odrzuca resztę)
Los.ZIARNO_GRANICA = 2147483648

function Los.nowyLos(ziarno: number): () -> number
	local stan = math.floor(math.abs(ziarno)) % MODUL
	if stan == 0 then
		stan = 20261113
	end
	local function los(): number
		stan = (stan * 48271) % MODUL
		return (stan - 1) / (MODUL - 1) -- liczba z przedziału [0, 1)
	end
	for _ = 1, 8 do
		los() -- rozgrzewka: sąsiednie ziarna dają na początku podobne liczby
	end
	return los
end

function Los.zaokraglij(x: number): number
	return math.floor(x + 0.5)
end

-- rośnie od 0 do 1 coraz wolniej; przy x == polowa daje 0,5 — każdy punkt coś daje, ale nic nie przekracza limitu
function Los.premia(x: number, polowa: number): number
	return x / (x + polowa)
end

function Los.blad(tekst: string)
	error("Walka: " .. tekst, 0)
end

-- skończona liczba (nie NaN, nie nieskończoność)
function Los.liczba(v: any): boolean
	return type(v) == "number" and v == v and v ~= math.huge and v ~= -math.huge
end

function Los.calkowita(v: any): boolean
	return Los.liczba(v) and math.floor(v) == v
end

return Los
