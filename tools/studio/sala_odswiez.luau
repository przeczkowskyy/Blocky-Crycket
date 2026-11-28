-- Odświeżenie sali wyboru klasy i rasy w stronę stylu „kreskówka low poly” (Paweł 28.11: „żeby tekstury nie były
-- poglitchowane… ładniejszy, żeby oddawał styl kreskówka poly”; wybór w oknie pytania: „Odświeżyć obecną salę”).
-- Wnętrze i układ zostają. Zmienia tylko to, co da się cofnąć jednym Ctrl+Z:
--   • tekstury nakładane „według materiału” (reguła ogólna z swiat/wybor_klasy/tekstury.json) są spokojniejsze:
--     słoje drewna większe i w połowie wtopione w kolor części (koniec „szumu” na belkach i stropie), kamień i tynk
--     czystsze; reguł szczegółowych (rekwizyty, chorągwie, dywan) nie rusza;
--   • obrys grup sali: ciemny tusz 2E2022, przezroczystość 0,3 — jak na podglądzie miasteczka (było 3A2A20 / 0,5).
-- Te same liczby są zapisane w tekstury.json i w tools/studio/deploy_classselect.py, więc pełne wdrożenie sali da
-- ten sam wynik. Skrypt rozpoznaje teksturę po ID obrazu i po dotychczasowej przezroczystości z reguły ogólnej.
local CHS = game:GetService("ChangeHistoryService")
local sala = workspace:FindFirstChild("WyborKlasy")
if not sala or not sala:GetAttribute("Wygenerowane") then
	return "Brak Workspace/WyborKlasy (Wygenerowane)"
end
-- materiał → { ID obrazu, dotychczasowa przezroczystość, nowe: studs, przezroczystość }
local REGULY = {
	{ id = "124850720793067", bylo = 0.25, studs = 10, przezr = 0.12 }, -- Slate: kamień muru
	{ id = "71241194302925", bylo = 0.2, studs = 9, przezr = 0.55 }, -- Wood: belki
	{ id = "120082727765133", bylo = 0.15, studs = 9, przezr = 0.45 }, -- WoodPlanks: deski
	{ id = "83860363530000", bylo = 0.1, studs = 12, przezr = 0.04 }, -- Plaster: tynk
	{ id = "119327815615605", bylo = 0.25, studs = 4, przezr = 0.4 }, -- Metal: żelazo
}
local rec = CHS:TryBeginRecording("Sala wyboru: spokojniejsze tekstury i ciemny obrys")
local zmienione, obrysy = {}, 0
local n = 0
for _, d in ipairs(sala:GetDescendants()) do
	if d:IsA("Texture") then
		for _, r in ipairs(REGULY) do
			if string.find(d.Texture, r.id, 1, true) and (math.abs(d.Transparency - r.bylo) < 0.011 or math.abs(d.Transparency - r.przezr) < 0.011) then
				d.Transparency = r.przezr
				d.StudsPerTileU, d.StudsPerTileV = r.studs, r.studs
				zmienione[r.id] = (zmienione[r.id] or 0) + 1
				break
			end
		end
		-- duże drewno (belki, więźba, szkielet ścian, deski stropu): słoje w połowie wtopione w kolor części i dwa razy
		-- większe — z kamery wyboru klasy gęsty rysunek słojów na dziesiątkach belek migotał jak szum. Rekwizyty
		-- (beczki, skrzynie, stołki; wszystkie boki poniżej 6 studów) zostają z pełną teksturą.
		local cz = d.Parent
		if cz and cz:IsA("BasePart") and (string.find(d.Texture, "71241194302925", 1, true) or string.find(d.Texture, "120082727765133", 1, true)) then
			if math.max(cz.Size.X, cz.Size.Y, cz.Size.Z) >= 6 and d.Transparency < 0.5 then
				d.Transparency = 0.55
				d.StudsPerTileU, d.StudsPerTileV = math.max(d.StudsPerTileU, 10), math.max(d.StudsPerTileV, 10)
				zmienione["drewno duże"] = (zmienione["drewno duże"] or 0) + 1
			end
		end
		-- jasne szczyty dachu między krokwiami wyglądały jak dziury w stropie: przyciemnione barwą tekstury
		if cz and cz.Name:sub(1, 6) == "Szczyt" and cz.Parent and cz.Parent.Name == "Dach" then
			d.Color3 = Color3.fromRGB(150, 124, 100)
			zmienione["szczyt dachu"] = (zmienione["szczyt dachu"] or 0) + 1
		end
	elseif d:IsA("Highlight") then
		d.OutlineColor = Color3.fromHex("2E2022")
		d.OutlineTransparency = 0.3
		obrysy += 1
	end
	n += 1
	if n % 1500 == 0 then
		task.wait()
	end
end
sala:SetAttribute("KreskaMiekka", nil)
sala:SetAttribute("StylOdswiezony", "2026-11-28")
if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
local out = {}
for id, ile in pairs(zmienione) do
	table.insert(out, id:sub(1, 6) .. "…=" .. ile)
end
return "tekstury zmienione: " .. table.concat(out, ", ") .. "; obrysów: " .. obrysy
