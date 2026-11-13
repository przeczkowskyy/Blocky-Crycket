-- Kontrola kolizji mapy „Krzywe Miasteczko” w Roblox Studio (tryb Edit, TYLKO ODCZYT — same promienie, nic nie zmienia).
-- Uruchomienie z folderu repozytorium:  python tools/studio_mcp.py luau swiat/krzywe_miasteczko/kontrola_kolizji.luau
-- Sprawdza: (1) czy pod nogami jest podłoże z kolizją (siatka co 6 studów w obrębie muru), (2) czy budynki zatrzymują
-- gracza (16 promieni dookoła każdego budynku na wysokości 4 studów), (3) czy są przeszkody „prawie do przeskoczenia”
-- na ulicach (wysokość 6,5–9 studów) — tylko liczba, do ręcznego obejrzenia.
local korzen = workspace:FindFirstChild("KrzyweMiasteczko")
if not korzen then
	return "Brak Workspace/KrzyweMiasteczko"
end
local SRODEK = Vector3.new(0, 0, -700)
local PROMIEN = 112 -- wnętrze muru

local tylkoMapa = RaycastParams.new()
tylkoMapa.FilterType = Enum.RaycastFilterType.Include
tylkoMapa.FilterDescendantsInstances = { korzen }
tylkoMapa.RespectCanCollide = true

local wynik = {}
local function linia(t)
	table.insert(wynik, t)
end

-- (1) podłoże
local punkty, dziury, wysokie = 0, {}, 0
local grupy = {}
for x = -PROMIEN, PROMIEN, 6 do
	for z = -PROMIEN, PROMIEN, 6 do
		if x * x + z * z <= PROMIEN * PROMIEN then
			punkty += 1
			local r = workspace:Raycast(SRODEK + Vector3.new(x, 300, z), Vector3.new(0, -600, 0), tylkoMapa)
			if not r then
				if #dziury < 12 then
					table.insert(dziury, string.format("(%d; %d)", x, z))
				end
			else
				local g = r.Instance.Parent and r.Instance.Parent.Name or "?"
				grupy[g] = (grupy[g] or 0) + 1
				if r.Position.Y > 1.5 then
					wysokie += 1
				end
			end
		end
	end
end
local opis = {}
for g, n in grupy do
	table.insert(opis, g .. " " .. n)
end
table.sort(opis)
linia(string.format("PODŁOŻE: %d punktów siatki w murze, bez podłoża z kolizją: %d %s; trafienia powyżej 1,5 studa (dachy, rekwizyty z kolizją): %d",
	punkty, punkty - (function() local s = 0 for _, n in grupy do s += n end return s end)(), table.concat(dziury, " "), wysokie))
linia("  na co pada promień (grupa → liczba): " .. table.concat(opis, ", "))

-- (2) budynki: bryła wielkości postaci (2,5 × 4 × 2,5; od 0,6 do 4,6 studa nad ziemią) pchana z 16 stron ku środkowi
-- budynku. „Zatrzymana” = natrafiła na coś z kolizją, zanim doszła na 3 study od środka. Bramy i otwarte stragany
-- mają z natury przejścia — liczba mówi, z ilu stron da się wejść w obrys.
local function zbadaj(m, etykieta)
	local cf, rozmiar = m:GetBoundingBox()
	local r = math.sqrt(rozmiar.X * rozmiar.X + rozmiar.Z * rozmiar.Z) / 2 + 8
	local zatrzymane, zKolizja, wszystkie = 0, 0, 0
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			wszystkie += 1
			if d.CanCollide then
				zKolizja += 1
			end
		end
	end
	local przejscia = {}
	for k = 0, 15 do
		local kat = k / 16 * math.pi * 2
		local start = Vector3.new(cf.Position.X + math.cos(kat) * r, 2.6, cf.Position.Z + math.sin(kat) * r)
		local kier = Vector3.new(cf.Position.X, 2.6, cf.Position.Z) - start
		local traf = workspace:Blockcast(CFrame.new(start), Vector3.new(2.5, 4, 2.5), kier.Unit * (r - 3), tylkoMapa)
		if traf then
			zatrzymane += 1
		else
			table.insert(przejscia, tostring(math.floor(math.deg(kat))) .. "°")
		end
	end
	linia(string.format("  %-14s części %3d, z kolizją %3d; zatrzymana z %2d/16 stron%s", etykieta, wszystkie, zKolizja, zatrzymane,
		#przejscia > 0 and (" — wchodzi się od: " .. table.concat(przejscia, " ")) or ""))
end
linia("BUDYNKI:")
for _, nazwa in { "Karczma", "Zbrojownia", "SklepMagiczny", "Wylegarnia", "Stajnia", "BramaLochow", "BramaTwierdzy", "BramaMiejska",
	"Arena", "Gildia", "KoloFortuny", "StudniaPomnik" } do
	local m = korzen:FindFirstChild(nazwa)
	if m then
		zbadaj(m, nazwa)
	else
		linia("  " .. nazwa .. ": brak")
	end
end
local domy = korzen:FindFirstChild("DomyTla")
if domy then
	for _, m in domy:GetChildren() do
		if m:IsA("Model") then
			zbadaj(m, m.Name)
		end
	end
end

-- (3) przeszkody 6,5–9 studów na ulicach i rynku (z grup rekwizytów)
local prawie = 0
for _, nazwa in { "Rekwizyty", "Stragany", "Rynek", "Ulice" } do
	local g = korzen:FindFirstChild(nazwa)
	if g then
		for _, d in g:GetDescendants() do
			if d:IsA("BasePart") and d.CanCollide then
				local gora = d.Position.Y + d.Size.Y / 2
				if gora >= 6.5 and gora <= 9 and d.Size.X * d.Size.Z > 4 then
					prawie += 1
				end
			end
		end
	end
end
linia("PRZESZKODY 6,5–9 studów z kolizją w rekwizytach, straganach, rynku i ulicach: " .. prawie)
return table.concat(wynik, "\n")
