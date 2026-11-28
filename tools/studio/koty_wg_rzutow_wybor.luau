-- Koty ras według rzutów Pawła z 26.11 -> wybór rasy (PODGLĄD, propozycja): figury z Workspace/KotyWgRzutowPodglad
-- (tools/studio/koty_wg_rzutow_studio.py) -> ReplicatedStorage.WyborKlasyModele.Race_<Id>, skala i atrybuty jak
-- dotychczasowa kopia kota. Podmienia tylko własne kopie kotów (atrybut BronDoGlowy); ludziki Race_<Id>_ludek zostają.
-- Dotychczasowe koty trafiają do ServerStorage.WyborRas_kopia_przed_rzutami (powrót: koty_wg_rzutow_wybor_cofnij.luau).
-- Po skopiowaniu kontener z figurami idzie do ServerStorage (nie stoi w świecie gry).
local CHS = game:GetService("ChangeHistoryService")
local SS = game:GetService("ServerStorage")
local rec = CHS:TryBeginRecording("Koty według rzutów w wyborze rasy")
local f = game:GetService("ReplicatedStorage"):WaitForChild("WyborKlasyModele")
local src = workspace:FindFirstChild("KotyWgRzutowPodglad") or SS:FindFirstChild("KotyWgRzutowPodglad")
if not src then
	return "STOP: brak kontenera KotyWgRzutowPodglad"
end
local kopia = SS:FindFirstChild("WyborRas_kopia_przed_rzutami")
if not kopia then
	kopia = Instance.new("Folder")
	kopia.Name = "WyborRas_kopia_przed_rzutami"
	kopia:SetAttribute("Wygenerowane", true)
	kopia.Parent = SS
end
local RASY = {
	Human = { "Kot-Człowiek (według rzutów)", "kot_czlowiek_wg_rzutow" },
	Demigod = { "Kot-Półbóg (według rzutów)", "kot_polbog_wg_rzutow" },
	Goblin = { "Kot-Goblin (według rzutów)", "kot_goblin_wg_rzutow" },
	DarkElf = { "Kot-Mroczny elf (według rzutów)", "kot_mroczny_elf_wg_rzutow" },
	Elf = { "Kot-Elf (według rzutów)", "kot_elf_wg_rzutow" },
	Orc = { "Kot-Ork (według rzutów)", "kot_ork_wg_rzutow" },
	Demon = { "Kot-Demon (według rzutów)", "kot_demon_wg_rzutow" },
}
local out = {}
for id, d in pairs(RASY) do
	local m = src:FindFirstChild(d[1])
	local stary = f:FindFirstChild("Race_" .. id)
	if m and stary and stary:GetAttribute("BronDoGlowy") then
		local c = m:Clone()
		for _, x in ipairs(c:GetDescendants()) do
			if x:IsA("Script") or x:IsA("LocalScript") then
				x:Destroy()
			end
		end
		c.Name = "Race_" .. id
		c:ScaleTo(stary:GetAttribute("SkalaWyboru") or 1.4)
		for nazwa, wartosc in pairs(stary:GetAttributes()) do
			c:SetAttribute(nazwa, wartosc)
		end
		c:SetAttribute("Postac", d[2])
		c:SetAttribute("Zrodlo", "swiat/postacie/koty_wg_rzutow.py (Pawel 26.11, koty wedlug rzutow — podglad)")
		if stary:GetAttribute("Postac") ~= d[2] and not kopia:FindFirstChild(stary.Name) then
			stary.Parent = kopia -- pierwsza podmiana: dotychczasowy kot do kopii zapasowej
		else
			stary:Destroy()
		end
		c.Parent = f
		table.insert(out, c.Name)
	else
		table.insert(out, "POMINIETO " .. id)
	end
end
if src.Parent == workspace then
	src.Parent = SS
end
if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return table.concat(out, ", ")
