--!strict
-- Migawka świata gry dla podglądu 3D panelu (panel/bc/podglad.py). TYLKO CZYTA DataModel — niczego nie tworzy,
-- nie zmienia i nie usuwa.
--
-- Szablon: Python podstawia znaczniki przed wysłaniem do Studio (execute_luau, DataModel "Edit"):
--   "__KORZEN__"  literał tekstowy ze ścieżką korzenia, np. "Workspace/DemoLesnaBaza" (domyślnie Workspace)
--   __OD__        ile pasujących części pominąć (strona zaczyna się od tej pozycji, liczone od 0)
--   __ILE__       najwięcej części na stronę (800)
--   __LIMIT__     najwięcej znaków odpowiedzi na wiersze (Studio ucina wynik execute_luau na ~100 000 znaków)
-- Bez podstawienia skrypt działa sam (Workspace, pierwsza strona) — można go odpalić `tools/studio_mcp.py luau`.
--
-- Zwraca JSON: {wersja, razem, od, nastepny?, korzen, miejsce:{placeId, nazwa}, grupy:[…], materialy:[…],
--   czesci:[[ksztalt, grupa, x,y,z, rx,ry,rz, sx,sy,sz, "RRGGBB", material, przezroczystosc, "Nazwa"], …]}
-- `grupa` i `material` to indeksy w listach TEJ strony (Python skleja strony). `nastepny` = od której pozycji
-- pobrać kolejną stronę (brak = to była ostatnia). Kolejność = kolejność GetDescendants (stabilna, dopóki nikt
-- nie zmienia świata między stronami).
-- Błąd (np. brak korzenia) = {blad:"…"}.

local HttpService = game:GetService("HttpService")

local KORZEN: string = "__KORZEN__"
local OD: number = tonumber("__OD__") or 0
local ILE: number = tonumber("__ILE__") or 800
local LIMIT: number = tonumber("__LIMIT__") or 90000
if KORZEN == "__KORZ" .. "EN__" or KORZEN == "" then
	KORZEN = "Workspace"
end

local GLEBOKOSC_GRUPY = 3 -- tyle poziomów poniżej usługi (Workspace) trafia do ścieżki grupy
local CO_ILE_PRZERWA = 4000 -- task.wait() co tyle potomków, żeby nie zamrozić Studio

-- --------------------------------------------------------------------------- korzeń
local function znajdzKorzen(sciezka: string): Instance?
	local seg = string.split(sciezka, "/")
	local obj: Instance? = nil
	local pierwszy = seg[1] or ""
	if pierwszy == "" or string.lower(pierwszy) == "workspace" then
		obj = workspace
	else
		obj = game:FindFirstChild(pierwszy)
	end
	for i = 2, #seg do
		if obj == nil then
			return nil
		end
		if seg[i] ~= "" then
			obj = (obj :: Instance):FindFirstChild(seg[i])
		end
	end
	return obj
end

local korzen = znajdzKorzen(KORZEN)
if korzen == nil then
	return HttpService:JSONEncode({ blad = "Nie ma takiego miejsca w świecie gry: " .. KORZEN })
end

-- --------------------------------------------------------------------------- kształty
local function enumPartType(nazwa: string): EnumItem?
	local ok, wartosc = pcall(function()
		return (Enum.PartType :: any)[nazwa]
	end)
	return if ok then wartosc else nil
end
local PT_KULA = enumPartType("Ball")
local PT_WALEC = enumPartType("Cylinder")
local PT_KLIN = enumPartType("Wedge")
local PT_NAROZNY = enumPartType("CornerWedge")

local function ksztalt(d: BasePart): number
	local klasa = d.ClassName
	if klasa == "Part" then
		local s = (d :: Part).Shape
		if s == PT_KULA then
			return 1
		elseif s == PT_WALEC then
			return 2
		elseif PT_KLIN and s == PT_KLIN then
			return 3
		elseif PT_NAROZNY and s == PT_NAROZNY then
			return 4
		end
		return 0
	elseif klasa == "WedgePart" then
		return 3
	elseif klasa == "CornerWedgePart" then
		return 4
	elseif klasa == "MeshPart" then
		return 5
	elseif klasa == "TrussPart" then
		return 7
	elseif d:IsA("PartOperation") then
		return 6
	end
	return 0 -- SpawnLocation, Seat, VehicleSeat i inne = blok
end

-- --------------------------------------------------------------------------- grupy (ścieżki Model/Folder)
local pamiecGrup: { [Instance]: string } = {}

local function sciezkaGrupy(czesc: Instance): string
	local rodzic = czesc.Parent
	if rodzic and pamiecGrup[rodzic] then
		return pamiecGrup[rodzic]
	end
	-- najbliższy przodek Model albo Folder (Workspace też jest Modelem, więc część wprost w nim ma grupę "Workspace")
	local a: Instance? = rodzic
	while a and a ~= game and not (a:IsA("Model") or a:IsA("Folder")) do
		a = a.Parent
	end
	if a == nil or a == game then
		a = czesc -- brak Modelu/Folderu w drodze do usługi: grupą jest sama usługa
		while a and a.Parent and a.Parent ~= game do
			a = a.Parent
		end
	end
	local nazwy = {}
	local x: Instance? = a
	while x and x ~= game do
		table.insert(nazwy, 1, x.Name)
		x = x.Parent
	end
	local wynik = table.concat(nazwy, "/", 1, math.min(#nazwy, 1 + GLEBOKOSC_GRUPY))
	if rodzic then
		pamiecGrup[rodzic] = wynik
	end
	return wynik
end

-- --------------------------------------------------------------------------- pomocnicze
local function r3(v: number): number
	return math.round(v * 1000) / 1000
end
local function r4(v: number): number
	return math.round(v * 10000) / 10000
end
local function krotkaNazwa(n: string): string
	local dl = utf8.len(n)
	if dl == nil then
		return string.sub(n, 1, 40) -- niepoprawny UTF-8: tniemy po bajtach
	end
	if dl <= 40 then
		return n
	end
	return string.sub(n, 1, (utf8.offset(n, 41) or 41) - 1)
end

-- --------------------------------------------------------------------------- przejście
local lista = korzen:GetDescendants()
if korzen:IsA("BasePart") then
	table.insert(lista, 1, korzen)
end
local grupy: { string } = {}
local indeksGrup: { [string]: number } = {}
local materialy: { string } = {}
local indeksMat: { [string]: number } = {}
local wiersze: { string } = {}
local znaki = 0
local razem = 0
local nastepny: number? = nil

for i, d in lista do
	if i % CO_ILE_PRZERWA == 0 then
		task.wait()
	end
	if d:IsA("BasePart") and not d:IsA("Terrain") then
		local czesc = d :: BasePart
		if czesc.Transparency < 0.98 and not czesc:FindFirstAncestorOfClass("Camera") then
			razem += 1
			if razem > OD and nastepny == nil then
				local sciezka = sciezkaGrupy(czesc)
				local gi = indeksGrup[sciezka]
				local nowaGrupa = gi == nil
				if nowaGrupa then
					gi = #grupy
				end
				local mat = czesc.Material.Name
				local mi = indeksMat[mat]
				local nowyMat = mi == nil
				if nowyMat then
					mi = #materialy
				end
				local p = czesc.Position
				local s = czesc.Size
				local rx, ry, rz = czesc.CFrame:ToOrientation()
				local wiersz = HttpService:JSONEncode({
					ksztalt(czesc), gi,
					r3(p.X), r3(p.Y), r3(p.Z),
					r4(rx), r4(ry), r4(rz),
					r3(s.X), r3(s.Y), r3(s.Z),
					string.upper(czesc.Color:ToHex()), mi,
					math.round(czesc.Transparency * 100) / 100,
					krotkaNazwa(czesc.Name),
				})
				local koszt = #wiersz + 1 + (if nowaGrupa then #sciezka + 3 else 0) + (if nowyMat then #mat + 3 else 0)
				if #wiersze >= ILE or (znaki + koszt > LIMIT and #wiersze > 0) then
					nastepny = razem - 1 -- ta część zaczyna następną stronę
				else
					if nowaGrupa then
						table.insert(grupy, sciezka)
						indeksGrup[sciezka] = gi :: number
					end
					if nowyMat then
						table.insert(materialy, mat)
						indeksMat[mat] = mi :: number
					end
					table.insert(wiersze, wiersz)
					znaki += koszt
				end
			end
		end
	end
end

local naglowek = HttpService:JSONEncode({
	wersja = 1,
	razem = razem,
	od = OD,
	nastepny = nastepny,
	korzen = korzen:GetFullName(),
	miejsce = { placeId = game.PlaceId, nazwa = game.Name },
	grupy = grupy,
	materialy = materialy,
})
-- dopinamy gotowe wiersze bez ponownego kodowania całości
return string.sub(naglowek, 1, -2) .. ',"czesci":[' .. table.concat(wiersze, ",") .. "]}"
