-- Decal ID (z Open Cloud) -> Image ID (do ImageLabel/ImageButton).
-- Uruchom w Roblox Studio (Command Bar albo narzedzie MCP do wykonania kodu).
-- Podmien DECAL_ID. Zwraca/printuje imageId albo blad.
local DECAL_ID = 0 -- <- tutaj decalId z tools/roblox_upload.py

local InsertService = game:GetService("InsertService")
local ok, model = pcall(InsertService.LoadAsset, InsertService, DECAL_ID)
if not ok or not model then
	warn("[resolve] LoadAsset nie powiodl sie (moderacja w toku? zly ID? brak uprawnien):", model)
	return nil
end
local decal = model:FindFirstChildWhichIsA("Decal", true)
local imageId = decal and decal.Texture:match("%d+")
model:Destroy()
if imageId then
	print("[resolve] imageId =", imageId)
	return tonumber(imageId)
end
warn("[resolve] w modelu brak Decal – sprawdz ID")
return nil
