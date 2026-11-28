-- Koty ras według rzutów jako postać gracza w świecie — PODGLĄD u Pawła (26.11), propozycja.
-- Figury z klipami Kota-Maga z Workspace/KotyWgRzutowPodglad (tools/studio/koty_wg_rzutow_studio.py --z-klipami)
-- -> ReplicatedStorage.KotyRasSwiat.Race_<Id> (skala 1, bez skryptów, atrybut WysHRP = wysokość HumanoidRootPart
-- nad stopami). Klient: src/client/KotRasySwiatClient.client.luau. Wyłącznik: atrybut Wlaczone folderu.
-- Kontener z figurami idzie potem do ServerStorage (nie stoi w świecie). Pakiet Karola BohaterSwiat bez zmian.
local CHS = game:GetService("ChangeHistoryService")
local SS = game:GetService("ServerStorage")
local RS = game:GetService("ReplicatedStorage")
local rec = CHS:TryBeginRecording("Koty ras w świecie (podgląd)")
local src = workspace:FindFirstChild("KotyWgRzutowPodglad") or SS:FindFirstChild("KotyWgRzutowPodglad")
if not src then
	return "STOP: brak kontenera KotyWgRzutowPodglad"
end
local f = RS:FindFirstChild("KotyRasSwiat")
if f then
	f:Destroy()
end
f = Instance.new("Folder")
f.Name = "KotyRasSwiat"
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Wlaczone", true)
f:SetAttribute("Zrodlo", "swiat/postacie/koty_wg_rzutow.py + kot_demon.wg_rzutow (Pawel 26.11, podglad)")
local RASY = {
	Human = "Kot-Człowiek (według rzutów)", Demigod = "Kot-Półbóg (według rzutów)", Goblin = "Kot-Goblin (według rzutów)",
	DarkElf = "Kot-Mroczny elf (według rzutów)", Elf = "Kot-Elf (według rzutów)", Orc = "Kot-Ork (według rzutów)",
	Demon = "Kot-Demon (według rzutów)",
}
local out = {}
for id, nazwa in pairs(RASY) do
	local m = src:FindFirstChild(nazwa)
	local hrp = m and m:FindFirstChild("HumanoidRootPart")
	if m and hrp then
		local c = m:Clone()
		local dol = math.huge
		local klipy = 0
		for _, x in ipairs(c:GetDescendants()) do
			if x:IsA("LuaSourceContainer") then
				x:Destroy()
			elseif x:IsA("BasePart") then
				x.CanCollide, x.CanQuery, x.CanTouch, x.Massless, x.CastShadow = false, false, false, true, false
				if x.Transparency < 1 and x.Name ~= "HumanoidRootPart" then
					local cf, s = x.CFrame, x.Size
					local pol = math.abs(cf.XVector.Y) * s.X / 2 + math.abs(cf.YVector.Y) * s.Y / 2 + math.abs(cf.ZVector.Y) * s.Z / 2
					dol = math.min(dol, cf.Position.Y - pol)
				end
			elseif x:IsA("KeyframeSequence") then
				klipy += 1
			end
		end
		c.Name = "Race_" .. id
		c:SetAttribute("WysHRP", c.HumanoidRootPart.Position.Y - dol)
		c:SetAttribute("Wygenerowane", true)
		c.Parent = f
		table.insert(out, string.format("%s (klipy %d, WysHRP %.2f)", c.Name, klipy, c:GetAttribute("WysHRP")))
	else
		table.insert(out, "BRAK " .. id)
	end
end
f.Parent = RS
if src.Parent == workspace then
	src.Parent = SS
end
if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return table.concat(out, ", ")
