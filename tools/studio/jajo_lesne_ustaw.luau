-- Leśne jajo z artefaktu Pawła („Leśne jajo 3D”, model wgrany 24.11 jako zasób 92671202213818, wstawiony do
-- Workspace/JajkoKorowePodglad jako JajoLesneImport) -> gotowy model „Jajko korowe” w miejscu starego jaja z klocków.
-- Naprawia to, co gubi importer: kolory materiałów bez tekstury (kryształy, odłamki, grzybki — z pliku GLB, liniowe ->
-- sRGB), skalę (1 m = 1 stud; jajo ×1,5), zakotwiczenie; dokłada świecenie pęknięć (SurfaceAppearance: maska blasku
-- z egg_emissive.png) i niewidzialny korzeń (PrimaryPart) z przodem tam, gdzie patrzyła kamera artefaktu (+Z pliku).
-- Kawałki skorupy są w spoczynku niewidoczne (pokazuje je klient przy wykluciu). Uruchom raz po insert_asset.
local CHS = game:GetService("ChangeHistoryService")
local rec = CHS:TryBeginRecording("Leśne jajo z artefaktu")
local k = workspace.JajkoKorowePodglad
local imp = k:FindFirstChild("JajoLesneImport")
assert(imp, "brak JajoLesneImport")
local SKALA = 1.5
local KOLOR_TEKSTURY = "rbxassetid://129739236064351" -- obraz utworzony przez importer z egg_basecolor.png
local BLASK = "rbxassetid://70749662306023" -- JajoLesneBlask (egg_emissive.png)
local KOLORY = { -- nazwa siatki -> kolor sRGB, materiał
	Crystals = { Color3.fromRGB(88, 219, 201), Enum.Material.Neon },
	Shards = { Color3.fromRGB(88, 219, 201), Enum.Material.Neon },
	MushroomStems = { Color3.fromRGB(192, 225, 231), Enum.Material.SmoothPlastic },
	MushroomCaps = { Color3.fromRGB(42, 144, 209), Enum.Material.SmoothPlastic },
	MushroomSpots = { Color3.fromRGB(187, 242, 255), Enum.Material.Neon },
	RockBed = { Color3.new(1, 1, 1), Enum.Material.SmoothPlastic }, -- kolory wierzchołków
}

-- stare jajo: miejsce i kierunek
-- miejsce: w miasteczku obok zagrody petów (Paweł 24.11: stare miejsce 983, -652 leżało za niewidzialną ścianą
-- miasteczka, nie dało się tam dojść); przód w stronę uliczki (-Z)
local stare = k:FindFirstChild("Jajko korowe")
local miejsce = Vector3.new(955, 0.2, -695)
local przod = Vector3.new(0, 0, -1)

local m = Instance.new("Model")
m.Name = "Jajko korowe nowe"
local dol, sx, sz, n = math.huge, 0, 0, 0
local czesci = {}
for _, d in ipairs(imp:GetDescendants()) do
	if d:IsA("MeshPart") then
		table.insert(czesci, d)
	end
end
for _, d in ipairs(czesci) do
	d.Anchored = true
	d.CanCollide = false
	d.CanTouch = false
	d.CanQuery = false
	d.CastShadow = d.Name == "Egg" or d.Name == "RockBed"
	local kol = KOLORY[d.Name]
	if kol then
		d.Color, d.Material = kol[1], kol[2]
	else
		-- jajo i kawałki skorupy: tekstura + świecące pęknięcia
		d.Color = Color3.new(1, 1, 1)
		d.Material = Enum.Material.SmoothPlastic
		d.TextureID = ""
		local sa = Instance.new("SurfaceAppearance")
		sa.ColorMap = KOLOR_TEKSTURY
		local sx2: any = sa
		pcall(function()
			sx2.EmissiveMaskContent = Content.fromUri(BLASK)
			sx2.EmissiveStrength = 1
			sx2.EmissiveTint = Color3.fromRGB(83, 232, 154)
		end)
		sa.Parent = d
		if d.Name ~= "Egg" then
			d.Transparency = 1
		end
	end
	dol = math.min(dol, d.Position.Y - d.Size.Y / 2)
	if d.Name == "Egg" then
		sx, sz, n = d.Position.X, d.Position.Z, 1
	end
	d.Parent = m
end
assert(n == 1, "brak siatki Egg")
local korzen = Instance.new("Part")
korzen.Name = "Korzen"
korzen.Size = Vector3.new(0.4, 0.4, 0.4)
korzen.Transparency = 1
korzen.Anchored, korzen.CanCollide, korzen.CanTouch, korzen.CanQuery = true, false, false, false
-- przód modelu = +Z pliku (stamtąd patrzy kamera artefaktu); po imporcie +Z pliku = +Z świata (sprawdzone na
-- położeniu ShellTopRight (+X) i Crystals)
korzen.CFrame = CFrame.lookAt(Vector3.new(sx, dol, sz), Vector3.new(sx, dol, sz + 1))
korzen.Parent = m
m.PrimaryPart = korzen
m.Parent = k
m:ScaleTo(SKALA)
m:PivotTo(CFrame.lookAt(miejsce, miejsce + przod))
m:SetAttribute("Wygenerowane", true)
m:SetAttribute("Zrodlo", "artefakt Pawła „Leśne jajo 3D” (24.11), zasób 92671202213818")
m:SetAttribute("Zajety", true)
imp:Destroy()
if stare then
	stare:Destroy()
end
m.Name = "Jajko korowe"
-- punkt podpowiedzi E nad nowym jajem
local punkt = k:FindFirstChild("PunktJajka")
if punkt and punkt:IsA("BasePart") then
	punkt.CFrame = CFrame.new(miejsce + Vector3.new(0, 2, 0))
end
local cf, rozmiar = m:GetBoundingBox()
if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
local sa = m.Egg:FindFirstChildWhichIsA("SurfaceAppearance")
local sa2: any = sa
local okE, blask = pcall(function()
	return tostring(sa2.EmissiveMaskContent)
end)
return string.format("ok: %d części, rozmiar %.1f × %.1f × %.1f, pivot %s, blask: %s", #czesci, rozmiar.X, rozmiar.Y, rozmiar.Z,
	tostring(m:GetPivot().Position), okE and blask or "brak")
