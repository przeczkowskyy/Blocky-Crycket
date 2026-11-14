--[[
	Budowa SZABLONU jednego aktora (tryb Edit, przez zbuduj.py → execute_luau; __DANE__ wstawia zbuduj.py
	z dane/<klucz>.json). Tworzy WYŁĄCZNIE Workspace/TestWalki2/Aktorzy/<klucz> i jego cokół w galerii.

	Model: zakotwiczony HumanoidRootPart (PrimaryPart, punkt obrotu = ziemia pod aktorem), niewidzialna część na kość
	(bezpośrednie dziecko modelu), Motor6D do rodzica w stawie, bryły przyspawane do kości (WeldConstraint),
	Attachmenty modelu i punkty „Punkt_<nazwa>” (Bron, Pocisk, Piers…). Bez AnimationController/Animator — klipy gra
	moduł Klipy, wpisując Motor6D.Transform w lokalnym klonie.
]]
local D = __DANE__
local kontener = workspace:FindFirstChild("TestWalki2")
if not kontener or kontener:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera Workspace/TestWalki2 z atrybutem Wygenerowane"
end
local folder = kontener:FindFirstChild("Aktorzy")
local galeria = kontener:FindFirstChild("Galeria")
if not folder or not galeria then
	return "STOP: brak folderów Aktorzy / Galeria w kontenerze"
end
for _, f in { folder, galeria } do
	local stary = f:FindFirstChild(D.klucz)
	if stary then
		stary:Destroy()
	end
end

local baza = CFrame.lookAt(Vector3.new(D.poz[1], D.poz[2], D.poz[3]), Vector3.new(D.poz[1] + D.patrz[1], D.poz[2], D.poz[3] + D.patrz[2]))

local model = Instance.new("Model")
model.Name = D.klucz
model:SetAttribute("Aktor", D.klucz)
model:SetAttribute("Nazwa", D.nazwa)
model:SetAttribute("Wygenerowane", true)
if D.zastepczy ~= "" then
	model:SetAttribute("Zastepczy", D.zastepczy)
end

local function bezFizyki(p: BasePart)
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
end

local hrpPos = Vector3.new(D.hrp[1], D.hrp[2], D.hrp[3])
local hrp = Instance.new("Part")
hrp.Name = "HumanoidRootPart"
hrp.Size = Vector3.new(1, 1, 1)
hrp.Transparency = 1
hrp.Anchored = true
hrp.CastShadow = false
bezFizyki(hrp)
hrp.CFrame = baza * CFrame.new(hrpPos)
hrp.PivotOffset = CFrame.new(-hrpPos)
hrp.Parent = model
model.PrimaryPart = hrp

local kosci = {}
for i, k in D.kosci do
	local p = Instance.new("Part")
	p.Name = k[1]
	p.Size = Vector3.new(k[9], k[10], k[11])
	p.Transparency = 1
	p.Anchored = false
	p.CastShadow = false
	bezFizyki(p)
	p.CFrame = baza * CFrame.new(k[6], k[7], k[8])
	p.Parent = model
	kosci[i] = p
end
for i, k in D.kosci do
	local rodzic, srodekRodzica
	if k[2] == 0 then
		rodzic, srodekRodzica = hrp, hrpPos
	else
		local kr = D.kosci[k[2]]
		rodzic, srodekRodzica = kosci[k[2]], Vector3.new(kr[6], kr[7], kr[8])
	end
	local staw = Vector3.new(k[3], k[4], k[5])
	local m = Instance.new("Motor6D")
	m.Name = k[12]
	m.C0 = CFrame.new(staw - srodekRodzica)
	m.C1 = CFrame.new(staw - Vector3.new(k[6], k[7], k[8]))
	m.Part0 = rodzic
	m.Part1 = kosci[i]
	m.Parent = kosci[i]
end

local grupy = {}
for i, nazwa in D.grupy do
	if i > 1 then
		local g = Instance.new("Model")
		g.Name = nazwa
		g.Parent = model
		grupy[i] = g
	end
end
local n = 0
for _, c in D.czesci do
	local ks = c[2]
	local p
	if ks == 3 then
		p = Instance.new("WedgePart")
	elseif ks == 4 then
		p = Instance.new("CornerWedgePart")
	else
		p = Instance.new("Part")
		p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
	end
	p.Name = c[3]
	p.Size = Vector3.new(c[10], c[11], c[12])
	p.CFrame = baza * CFrame.new(c[4], c[5], c[6]) * CFrame.fromOrientation(c[7], c[8], c[9])
	p.Color = Color3.fromHex(c[13])
	local mat = D.materialy[c[14] + 1]
	p.Material = Enum.Material[mat[1]]
	p.Reflectance = mat[2]
	p.Anchored = false
	bezFizyki(p)
	if c[16] ~= "" then
		local sm = Instance.new("SpecialMesh")
		sm.MeshType = Enum.MeshType[c[16]]
		sm.Parent = p
	end
	local kosc = kosci[c[1]]
	local w = Instance.new("WeldConstraint")
	w.Part0 = kosc
	w.Part1 = p
	w.Parent = p
	p.Parent = if c[15] == 0 then kosc else grupy[c[15] + 1]
	n += 1
end
for _, z in D.zaczepy do
	local a = Instance.new("Attachment")
	a.Name = z[1]
	a.CFrame = CFrame.new(z[3], z[4], z[5]) * CFrame.fromOrientation(z[6], z[7], z[8])
	a.Parent = kosci[z[2]]
end
for _, pk in D.punkty do
	local a = Instance.new("Attachment")
	a.Name = "Punkt_" .. pk[1]
	a.Position = Vector3.new(pk[3], pk[4], pk[5])
	a.Parent = kosci[pk[2]]
end
model.Parent = folder

------------------------------------------------------------------ cokół i tabliczka w galerii
local cokol = Instance.new("Model")
cokol.Name = D.klucz
local function blok(nazwa, rozmiar, cf, kolor, material)
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored = true
	p.Size = rozmiar
	p.CFrame = cf
	p.Color = Color3.fromHex(kolor)
	p.Material = material
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanTouch = false
	p.Parent = cokol
	return p
end
local podstawa = baza * CFrame.new(0, -0.25, 0)
blok("Cokol", Vector3.new(D.szer + 1.2, 0.5, D.glab + 1.2), podstawa, "6C727A", Enum.Material.Slate)
local tab = blok("Tabliczka", Vector3.new(math.max(3.2, D.szer * 0.8), 1.1, 0.2), baza * CFrame.new(0, 0.55, -(D.przod + 0.8)) * CFrame.Angles(math.rad(-20), 0, 0), "F7F2E6", Enum.Material.SmoothPlastic)
tab.CanCollide = false
local sg = Instance.new("SurfaceGui")
sg.Face = Enum.NormalId.Front
sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
sg.PixelsPerStud = 50
sg.Parent = tab
local function napis(tekst, y, h, kolor, czcionka)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position = UDim2.fromScale(0.03, y)
	t.Size = UDim2.fromScale(0.94, h)
	t.Text = tekst
	t.TextScaled = true
	t.Font = czcionka
	t.TextColor3 = Color3.fromHex(kolor)
	t.Parent = sg
end
napis(D.nazwa, 0.04, 0.55, "17121F", Enum.Font.LuckiestGuy)
napis(if D.zastepczy ~= "" then "model zastępczy" else (D.rola == "klasa" and "klasa gracza" or "przeciwnik"), 0.6, 0.34,
	if D.zastepczy ~= "" then "D9483B" else "2F6FE0", Enum.Font.Bangers)
cokol.Parent = galeria

return string.format("%s: %d brył, %d kości, %d punktów; stoi w (%.1f; %.1f; %.1f)", D.klucz, n, #D.kosci, #D.punkty,
	baza.X, baza.Y, baza.Z)
