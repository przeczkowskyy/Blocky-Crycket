-- Przymierzalnia zestawów ekwipunku — TYLKO w Roblox Studio (Play). W opublikowanej grze nic nie robi.
-- Instalowana przez `python -B swiat/postacie/roblox_postac.py` jako Workspace/TestPostaci/Przymierzalnia.
-- Przy każdym manekinie z atrybutem `Zestaw` pojawia się podpowiedź „Przymierz” (klawisz E albo dotknięcie).
-- Zestaw zakładany jest na awatar gracza jako zwykłe obiekty Accessory zbudowane z części Roblox (bez zasobów
-- wgrywanych na konto). Ponowne naciśnięcie przy tym samym manekinie zdejmuje zestaw.
-- Do testów ze skryptu: kontener.Przymierz:Fire(gracz, "zestaw_rycerz") albo :Fire(gracz, "") — zdejmij.
-- Dopasowanie liczone dla klockowego awatara R15 w standardowej skali; na innych ciałach części mogą odstawać.
local RunService = game:GetService("RunService")
if not RunService:IsStudio() then
	return
end
local kontener = script.Parent
local Dane = require(kontener:WaitForChild("DaneEkwipunku"))

local function nowaCzesc(c)
	local ks = c[1]
	local p
	if ks == 3 then
		p = Instance.new("WedgePart")
	elseif ks == 4 then
		p = Instance.new("CornerWedgePart")
	else
		p = Instance.new("Part")
		p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
	end
	p.Size = Vector3.new(c[8], c[9], c[10])
	p.Color = Color3.fromHex(c[11])
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	if c[13] ~= "" then
		local sm = Instance.new("SpecialMesh")
		sm.MeshType = Enum.MeshType[c[13]]
		sm.Parent = p
	end
	return p
end

local function noweAkcesorium(zestaw, a)
	local acc = Instance.new("Accessory")
	acc.Name = a.id
	acc:SetAttribute("TestPostaci", true)
	local uchwyt = Instance.new("Part")
	uchwyt.Name = "Handle"
	uchwyt.Size = Vector3.new(0.2, 0.2, 0.2)
	uchwyt.Transparency = 1
	uchwyt.CanCollide = false
	uchwyt.CanTouch = false
	uchwyt.CanQuery = false
	uchwyt.Massless = true
	local zaczep = Instance.new("Attachment")
	zaczep.Name = a.zaczep
	zaczep.Parent = uchwyt
	for i, c in a.czesci do
		local p = nowaCzesc(c)
		p.Name = a.id .. "_" .. i
		local mat = zestaw.materialy[c[12] + 1]
		p.Material = Enum.Material[mat[1]]
		p.Reflectance = mat[2]
		-- Weld z jawnym przesunięciem (C0), a nie WeldConstraint: WeldConstraint zapamiętuje wzajemne położenie
		-- dopiero po wejściu do świata, czyli już PO tym, jak AddAccessory przeniesie uchwyt na awatar —
		-- części zostawały wtedy tam, gdzie powstały (sprawdzone 13.11.2026).
		local przesuniecie = CFrame.new(c[2], c[3], c[4]) * CFrame.fromOrientation(c[5], c[6], c[7])
		p.CFrame = uchwyt.CFrame * przesuniecie
		local w = Instance.new("Weld")
		w.Name = "SpawCzesci"
		w.C0 = przesuniecie
		w.Part0 = uchwyt
		w.Part1 = p
		w.Parent = p
		p.Parent = uchwyt
	end
	uchwyt.Parent = acc
	return acc
end

local function zdejmij(postac)
	local n = 0
	for _, d in postac:GetChildren() do
		if d:IsA("Accessory") and d:GetAttribute("TestPostaci") then
			d:Destroy()
			n += 1
		end
	end
	postac:SetAttribute("ZestawTestowy", nil)
	return n
end

local function przymierz(gracz, idZestawu)
	local postac = gracz and gracz.Character
	local humanoid = postac and postac:FindFirstChildOfClass("Humanoid")
	if not humanoid then
		return
	end
	local poprzedni = postac:GetAttribute("ZestawTestowy")
	zdejmij(postac)
	local zestaw = Dane[idZestawu]
	if not zestaw or poprzedni == idZestawu then
		return -- brak zestawu albo ponowne naciśnięcie = tylko zdjęcie
	end
	local zalozone, bezZaczepu = 0, {}
	for _, a in zestaw.akcesoria do
		if postac:FindFirstChild(a.zaczep, true) then
			humanoid:AddAccessory(noweAkcesorium(zestaw, a))
			zalozone += 1
		else
			table.insert(bezZaczepu, a.id .. " (" .. a.zaczep .. ")")
		end
	end
	postac:SetAttribute("ZestawTestowy", idZestawu)
	postac:SetAttribute("ZestawTestowyCzesci", zalozone)
	if #bezZaczepu > 0 then
		warn("Przymierzalnia: awatar nie ma punktów zaczepienia dla: " .. table.concat(bezZaczepu, ", "))
	end
end

local zdarzenie = Instance.new("BindableEvent")
zdarzenie.Name = "Przymierz"
zdarzenie.Event:Connect(przymierz)
zdarzenie.Parent = kontener

for _, model in kontener:GetChildren() do
	local id = model:IsA("Model") and model:GetAttribute("ZestawId")
	if id and Dane[id] and model.PrimaryPart then
		local pp = Instance.new("ProximityPrompt")
		pp.Name = "PrzymierzZestaw"
		pp.ActionText = "Przymierz"
		pp.ObjectText = model:GetAttribute("Zestaw") or id
		pp.HoldDuration = 0
		pp.MaxActivationDistance = 8 -- manekiny stoją co 9 studów: przy jednym nie łapie się sąsiad
		pp.RequiresLineOfSight = false
		pp.Parent = model.PrimaryPart
		pp.Triggered:Connect(function(gracz)
			przymierz(gracz, id)
		end)
	end
end
