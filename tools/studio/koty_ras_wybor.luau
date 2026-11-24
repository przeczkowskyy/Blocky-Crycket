-- Koty ras do wyboru rasy (Paweł 24.11, D-145): kopie figur w stroju podstawowym z Workspace/KotRasyPodglad
-- (tools/studio/koty_ras_studio.py) -> ReplicatedStorage.WyborKlasyModele.Race_<Id>, skala 1,4 jak Race_Demon
-- i Race_Human. Dawne ludziki zostają jako Race_<Id>_ludek (powrót: zmienić nazwy z powrotem).
local CHS = game:GetService("ChangeHistoryService")
local rec = CHS:TryBeginRecording("Koty ras w wyborze rasy")
local f = game:GetService("ReplicatedStorage"):WaitForChild("WyborKlasyModele")
local src = workspace:WaitForChild("KotRasyPodglad")
local RASY = {
	Elf = { "Kot-Elf (strój podstawowy)", "kot_elf_podstawowy" },
	DarkElf = { "Kot-Mroczny elf (strój podstawowy)", "kot_mroczny_elf_podstawowy" },
	Orc = { "Kot-Ork (strój podstawowy)", "kot_ork_podstawowy" },
	Goblin = { "Kot-Goblin (strój podstawowy)", "kot_goblin_podstawowy" },
	Demigod = { "Kot-Półbóg (strój podstawowy)", "kot_polbog_podstawowy" },
}
local out = {}
for id, d in pairs(RASY) do
	local m = src:FindFirstChild(d[1])
	if m then
		local nazwa = id
		local stary = f:FindFirstChild("Race_" .. id)
		if stary and not stary:GetAttribute("BronDoGlowy") then
			nazwa = stary:GetAttribute("Nazwa") or id
			local l = f:FindFirstChild("Race_" .. id .. "_ludek")
			if l then l:Destroy() end
			stary.Name = "Race_" .. id .. "_ludek"
		elseif stary then
			nazwa = stary:GetAttribute("Nazwa") or id
			stary:Destroy()
		end
		local c = m:Clone()
		for _, x in ipairs(c:GetDescendants()) do
			if x:IsA("Script") or x:IsA("LocalScript") then x:Destroy() end
		end
		c.Name = "Race_" .. id
		c:ScaleTo(1.4)
		c:SetAttribute("SkalaWyboru", 1.4)
		c:SetAttribute("BronDoGlowy", true)
		c:SetAttribute("Wygenerowane", true)
		c:SetAttribute("Nazwa", nazwa)
		c:SetAttribute("Postac", d[2])
		c:SetAttribute("Zrodlo", "swiat/postacie/koty_ras.py (Pawel 24.11, koty ras)")
		c.Parent = f
		table.insert(out, c.Name)
	else
		table.insert(out, "BRAK " .. d[1])
	end
end
if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end
return table.concat(out, ", ")
