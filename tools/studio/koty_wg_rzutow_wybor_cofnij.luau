-- Powrót do kotów sprzed podglądu z 26.11: ServerStorage.WyborRas_kopia_przed_rzutami.Race_<Id> wraca do
-- ReplicatedStorage.WyborKlasyModele, a koty według rzutów znikają z wyboru rasy (figury źródłowe zostają
-- w ServerStorage.KotyWgRzutowPodglad).
local CHS = game:GetService("ChangeHistoryService")
local rec = CHS:TryBeginRecording("Wybór rasy: powrót do kotów sprzed rzutów")
local f = game:GetService("ReplicatedStorage"):WaitForChild("WyborKlasyModele")
local kopia = game:GetService("ServerStorage"):FindFirstChild("WyborRas_kopia_przed_rzutami")
if not kopia then
	return "STOP: brak kopii zapasowej ServerStorage.WyborRas_kopia_przed_rzutami"
end
local out = {}
for _, stary in ipairs(kopia:GetChildren()) do
	local nowy = f:FindFirstChild(stary.Name)
	if nowy then
		nowy:Destroy()
	end
	stary.Parent = f
	table.insert(out, stary.Name)
end
kopia:Destroy()
if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return "przywrócono: " .. table.concat(out, ", ")
