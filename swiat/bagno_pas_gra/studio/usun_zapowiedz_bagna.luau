--[[
	Usuwa Workspace/LasPas/ZapowiedzBagna przed budową mapy Bagna (swiat/bagno_pas/README.md: zapowiedź stoi tam, gdzie
	Pomost Przybycia Bagna, i ma niewidzialną ścianę na u 965). Tryb Edit, tylko miejsce gry, tylko kontener z atrybutem
	Wygenerowane, punkt historii przed i po (Ctrl+Z cofa). Niczego nie zapisuje i nie publikuje.

	python -B tools/studio_mcp.py luau swiat/bagno_pas_gra/studio/usun_zapowiedz_bagna.luau

	Uwaga: ZapowiedzBagna jest w swiat/las_pas/czesci.json — ponowna budowa mapy lasu (tools/studio_buduj.py) postawi ją
	znowu; wtedy trzeba to powtórzyć albo dodać przełącznik w swiat/las_pas/generuj.py (zmiana innego pakietu, za zgodą).
]]
if game.PlaceId ~= 129485428021967 then
	return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")"
end
if game:GetService("RunService"):IsRunning() then
	return "STOP: Studio jest w trybie Play — tylko tryb Edit"
end
local las = workspace:FindFirstChild("LasPas")
if not las then
	return "STOP: brak Workspace/LasPas"
end
if las:GetAttribute("Wygenerowane") ~= true then
	return "STOP: Workspace/LasPas bez atrybutu Wygenerowane — nie ruszam"
end
local z = las:FindFirstChild("ZapowiedzBagna")
if not z then
	return "OK: ZapowiedzBagna już nie ma"
end
local n = 0
for _, d in z:GetDescendants() do
	if d:IsA("BasePart") then
		n += 1
	end
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("Bagno: przed usunięciem ZapowiedzBagna")
z:Destroy()
CH:SetWaypoint("Bagno: usunięto ZapowiedzBagna")
return "OK: usunięto LasPas/ZapowiedzBagna (" .. n .. " części)"
