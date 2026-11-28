-- Porządki w lobby (Paweł 28.11): poglądowe figury kotów znikają z miasteczka, leśne jajo staje w gnieździe
-- (inkubatorze) w lesie.
--   • Workspace/KotRasyPodglad, KotDemonPodglad, KotKlasyPodglad (własne kontenery Pawła, źródła figur) -> ServerStorage;
--     wybór rasy i klasy korzysta z kopii w ReplicatedStorage.WyborKlasyModele, więc nic się w nim nie zmienia.
--     Powrót: przenieść kontener z ServerStorage z powrotem do Workspace.
--   • Workspace/JajkoKorowePodglad/„Jajko korowe”: z miasteczka (955; 0,2; −695) na dno gniazda
--     Workspace/LasPas/Punkty/StanowiskoJajka, przodem do miejsca przybycia do lasu. Gniazda Karola nie zmieniamy.
-- Kontener Karola Workspace/TestPostaci i zwierzęta w zagrodzie zostają nietknięte.
local CHS = game:GetService("ChangeHistoryService")
local SS = game:GetService("ServerStorage")
local rec = CHS:TryBeginRecording("Porządki w lobby: figury kotów i leśne jajo")
local out = {}

for _, nazwa in ipairs({ "KotRasyPodglad", "KotDemonPodglad", "KotKlasyPodglad" }) do
	local k = workspace:FindFirstChild(nazwa)
	if k and k:GetAttribute("Wygenerowane") then
		local stary = SS:FindFirstChild(nazwa)
		if stary then
			stary:Destroy()
		end
		k.Parent = SS
		table.insert(out, nazwa .. " -> ServerStorage")
	elseif k then
		table.insert(out, nazwa .. ": bez atrybutu Wygenerowane — nie ruszam")
	end
end

local kont = workspace:FindFirstChild("JajkoKorowePodglad")
local jajko = kont and kont:FindFirstChild("Jajko korowe")
local las = workspace:FindFirstChild("LasPas")
local punkty = las and las:FindFirstChild("Punkty")
local gniazdo = punkty and punkty:FindFirstChild("StanowiskoJajka")
local dno = gniazdo and gniazdo:FindFirstChild("Gniazdo dno")
if jajko and jajko:IsA("Model") and dno and dno:IsA("BasePart") then
	local cf, rozmiar = jajko:GetBoundingBox()
	local pivot = jajko:GetPivot()
	local spod = cf.Position.Y - rozmiar.Y / 2
	-- wierzch dna gniazda (część może leżeć bokiem: bierzemy jej zasięg w pionie)
	local d = dno.CFrame
	local pol = math.abs(d.XVector.Y) * dno.Size.X / 2 + math.abs(d.YVector.Y) * dno.Size.Y / 2 + math.abs(d.ZVector.Y) * dno.Size.Z / 2
	local wierzch = dno.Position.Y + pol
	local cel = Vector3.new(dno.Position.X, wierzch + (pivot.Position.Y - spod), dno.Position.Z)
	-- przodem do miejsca przybycia do lasu (LasPasGra: przybycie 1114; 3,6; −700)
	local doGracza = Vector3.new(1114 - cel.X, 0, -700 - cel.Z)
	if doGracza.Magnitude < 1 then
		doGracza = Vector3.new(0, 0, -1)
	end
	jajko:PivotTo(CFrame.lookAt(cel, cel + doGracza.Unit))
	table.insert(out, string.format("Jajko korowe -> gniazdo w lesie (%.1f; %.1f; %.1f)", cel.X, cel.Y, cel.Z))
else
	table.insert(out, "Jajko: brak modelu albo gniazda LasPas/Punkty/StanowiskoJajka/Gniazdo dno — nie przeniesione")
end

if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return table.concat(out, "; ")
