-- Koci Rycerz i Koci Zwiadowca do selektora klas (Paweł 24.11, D-145): kopie figur z Workspace/KotKlasyPodglad
-- (tools/studio/kot_klasy_studio.py) -> ReplicatedStorage.WyborKlasyModele.Warrior / Scout. Dawne ludziki zostają
-- jako Warrior_ludek / Scout_ludek (powrót: zmienić nazwy z powrotem). Broń w łapce daje ClassSelectClient.holdWeapon
-- (atrybut BronDoGlowy -> Weapon_<klasa>_Kot). Skala 1 — jak Kot-Mag (Mage) obok na kole.
local CHS = game:GetService("ChangeHistoryService")
local rec = CHS:TryBeginRecording("Koty klas w selektorze")
local f = game:GetService("ReplicatedStorage"):WaitForChild("WyborKlasyModele")
local src = workspace:WaitForChild("KotKlasyPodglad")
local out = {}
for klasa, nazwa in pairs({ Warrior = "Koci Rycerz", Scout = "Koci Zwiadowca" }) do
	local m = src:FindFirstChild(nazwa)
	if m then
		local stary = f:FindFirstChild(klasa)
		if stary and not stary:GetAttribute("BronDoGlowy") then
			local l = f:FindFirstChild(klasa .. "_ludek")
			if l then l:Destroy() end
			stary.Name = klasa .. "_ludek"
		elseif stary then
			stary:Destroy()
		end
		local c = m:Clone()
		for _, d in ipairs(c:GetDescendants()) do
			if d:IsA("Script") or d:IsA("LocalScript") then d:Destroy() end
		end
		c.Name = klasa
		c:SetAttribute("BronDoGlowy", true)
		c:SetAttribute("Wygenerowane", true)
		c:SetAttribute("Postac", if klasa == "Warrior" then "kot_rycerz" else "kot_zwiadowca")
		c:SetAttribute("Zrodlo", "swiat/postacie/kot_klasy.py (Pawel 24.11, koty klas)")
		c.Parent = f
		table.insert(out, klasa .. " <- " .. nazwa)
	end
end
if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end
return table.concat(out, ", ")
