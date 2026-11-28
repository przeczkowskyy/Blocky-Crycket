-- Kot-Demon i Kot-Człowiek do wyboru rasy (Paweł 25.11: baza kotów bliżej referencji — po przebudowie figur trzeba
-- odświeżyć też kopie w wyborze rasy): figury w stroju podstawowym z Workspace/KotDemonPodglad
-- (tools/studio/kot_demon_studio.py) -> ReplicatedStorage.WyborKlasyModele.Race_Demon / Race_Human, skala 1,4.
-- Podmienia tylko własne kopie kotów (atrybut BronDoGlowy); ludziki Race_<Id>_ludek zostają.
local CHS = game:GetService("ChangeHistoryService")
local rec = CHS:TryBeginRecording("Kot-Demon i Kot-Człowiek w wyborze rasy")
local f = game:GetService("ReplicatedStorage"):WaitForChild("WyborKlasyModele")
local src = workspace:WaitForChild("KotDemonPodglad")
local RASY = {
	Demon = { "Kot-Demon (strój podstawowy)", "kot_demon_podstawowy" },
	Human = { "Kot-Człowiek (strój podstawowy)", "kot_czlowiek_podstawowy" },
}
local out = {}
for id, d in pairs(RASY) do
	local m = src:FindFirstChild(d[1])
	local stary = f:FindFirstChild("Race_" .. id)
	if m and stary and stary:GetAttribute("BronDoGlowy") then
		local c = m:Clone()
		for _, x in ipairs(c:GetDescendants()) do
			if x:IsA("Script") or x:IsA("LocalScript") then x:Destroy() end
		end
		c.Name = "Race_" .. id
		c:ScaleTo(stary:GetAttribute("SkalaWyboru") or 1.4)
		for nazwa, wartosc in pairs(stary:GetAttributes()) do
			c:SetAttribute(nazwa, wartosc)
		end
		stary:Destroy()
		c.Parent = f
		table.insert(out, c.Name)
	else
		table.insert(out, "POMINIETO " .. id .. " (figura: " .. tostring(m ~= nil) .. ", kopia kota: " .. tostring(stary ~= nil and stary:GetAttribute("BronDoGlowy") == true) .. ")")
	end
end
if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end
return table.concat(out, ", ")
