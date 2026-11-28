-- Naprawa położenia niewidzialnych ścian miasteczka (Paweł 28.11: „odblokujmy wejście do pomieszczenia Game Mastera,
-- bo nie mogę tam teraz wchodzić”). Grupa Workspace/MiasteczkoBazar/Niewidzialne była przesunięta względem generatora
-- Karola o (−17; 0; +21,5) studa — północna ściana stała w poprzek wejść do karczmy, sklepów i sali treningowej
-- (rano 28.11 grupa była jeszcze na miejscu: środek (980; −700)). Skrypt niczego nie projektuje od nowa: przywraca
-- miejsca z swiat/miasteczko_bazar/uklad.json (pole_gry x −95…68, z −36…36; świat = (994 + x; −700 + z)), czyli
-- ściana wschodnia (długość 76) wraca na (1063,5; −700), a pozostałe trzy przesuwają się o ten sam wektor.
-- Uruchomienie w trybie Edit: python tools/studio_mcp.py luau tools/studio/niewidzialne_sciany_napraw.luau
local CHS = game:GetService("ChangeHistoryService")
local mb = workspace:FindFirstChild("MiasteczkoBazar")
local g = mb and mb:FindFirstChild("Niewidzialne")
if not g then
	return "Brak Workspace/MiasteczkoBazar/Niewidzialne"
end
local wsch: BasePart? = nil
local ile = 0
for _, p in ipairs(g:GetChildren()) do
	if p:IsA("BasePart") then
		ile += 1
		if math.abs(p.Size.Z - 76) < 0.1 and math.abs(p.Size.X - 2) < 0.1 then
			wsch = p
		end
	end
end
if not wsch or ile ~= 4 then
	return "Inny układ ścian niż w generatorze (ścian: " .. ile .. ") — nic nie zmieniam"
end
local d = Vector3.new(1063.5, wsch.Position.Y, -700) - wsch.Position
if d.Magnitude < 0.05 then
	return "Ściany są na miejscach z generatora — nic do zrobienia"
end
if d.Magnitude > 60 then
	return string.format("Przesunięcie (%.1f; %.1f; %.1f) jest za duże na zwykłą poprawkę — nic nie zmieniam", d.X, d.Y, d.Z)
end
local rec = CHS:TryBeginRecording("Niewidzialne ściany miasteczka z powrotem na miejsca z generatora")
local out = {}
for _, p in ipairs(g:GetChildren()) do
	if p:IsA("BasePart") then
		p.Position += d
		table.insert(out, string.format("(%.1f; %.1f)", p.Position.X, p.Position.Z))
	end
end
if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return string.format("Przesunięte o (%.1f; %.1f; %.1f); ściany teraz: %s", d.X, d.Y, d.Z, table.concat(out, " "))
