-- Skaczący slime z ciemnym obrysem na makiecie lasu (Paweł 28.11: „dodaj mi tutaj jeszcze biegającego slime'a z takim
-- obrysem”). Własny, poglądowy model low poly — nie jest to potwór z gry Karola i nie walczy; skacze tam i z powrotem
-- po leśnej ścieżce makiety. Stoi w kontenerze Workspace/LasLowPolyPodglad (atrybut Wygenerowane), więc znika razem
-- z makietą; jego obrys nazywa się „Kontur”, czyli włącza się tylko blisko kamery, jak pozostałe kontury makiet.
--   W trybie Edit:  python tools/studio_mcp.py luau tools/studio/slime_podglad.luau   → model + skrypt ruchu (na stałe)
--   W trakcie Play: ten sam plik na serwerze (--dm Server) stawia sam model, tylko na tę rozgrywkę.
local RunService = game:GetService("RunService")
local kont = workspace:FindFirstChild("LasLowPolyPodglad")
if not kont or not kont:GetAttribute("Wygenerowane") then
	return "Brak makiety Workspace/LasLowPolyPodglad — najpierw tools/studio/las_lowpoly_podglad.luau"
end
local stary = kont:FindFirstChild("Slime")
if stary then
	stary:Destroy()
end

local function C(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end
local m = Instance.new("Model")
m.Name = "Slime"
local function czesc(nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3, kula: boolean?, przezr: number?): Part
	local p = Instance.new("Part")
	p.Name, p.Size, p.CFrame, p.Color = nazwa, rozmiar, cf, kolor
	p.Material, p.Anchored, p.CanCollide, p.CastShadow = Enum.Material.SmoothPlastic, true, false, true
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Transparency = przezr or 0
	if kula then
		local sm = Instance.new("SpecialMesh")
		sm.MeshType = Enum.MeshType.Sphere
		sm.Parent = p
	end
	p.Parent = m
	return p
end
-- model w układzie własnym: spód na y = 0, przód na −Z
local ZIELEN, JASNY = C(112, 206, 104), C(190, 240, 170)
local cialo = czesc("Ciało", Vector3.new(4.6, 3.4, 4.6), CFrame.new(0, 1.7, 0), ZIELEN, true)
czesc("Spód", Vector3.new(4.9, 1.5, 4.9), CFrame.new(0, 0.75, 0), C(92, 184, 92), true)
czesc("Połysk", Vector3.new(1.3, 0.8, 0.9), CFrame.new(-0.9, 2.75, -1.1) * CFrame.Angles(0, 0, math.rad(25)), JASNY, true, 0.15)
for _, s in ipairs({ -1, 1 }) do
	czesc("Oko", Vector3.new(1.05, 1.25, 0.6), CFrame.new(s * 0.85, 1.95, -2.02), Color3.new(1, 1, 1), true)
	czesc("Źrenica", Vector3.new(0.5, 0.7, 0.4), CFrame.new(s * 0.8, 1.9, -2.3), C(34, 26, 40), true)
end
czesc("Uśmiech", Vector3.new(1, 0.3, 0.3), CFrame.new(0, 1.15, -2.2), C(46, 110, 60))
czesc("Łodyżka", Vector3.new(0.25, 0.9, 0.25), CFrame.new(0, 3.75, 0), C(70, 140, 70))
czesc("Listek", Vector3.new(1.3, 0.2, 0.7), CFrame.new(0.55, 4.25, 0) * CFrame.Angles(0, 0, math.rad(20)), C(96, 180, 84))
czesc("Listek", Vector3.new(1.1, 0.2, 0.6), CFrame.new(-0.45, 4.15, 0) * CFrame.Angles(0, 0, math.rad(-28)), C(110, 196, 92))
m.PrimaryPart = cialo
m.WorldPivot = CFrame.new(0, 0, 0)
local kontur = Instance.new("Highlight")
kontur.Name = "Kontur"
kontur.FillTransparency, kontur.OutlineTransparency = 1, 0
kontur.OutlineColor = C(46, 32, 34)
kontur.DepthMode = Enum.HighlightDepthMode.Occluded
kontur.Parent = m

-- trasa: leśna ścieżka makiety (od bramy w głąb lasu i z powrotem); y = wierzch ścieżki
local bp = workspace:FindFirstChild("Baseplate")
local Y = ((bp and bp:IsA("BasePart")) and (bp.Position.Y + bp.Size.Y / 2) or 0) + 0.75
local TRASA = { Vector3.new(888, Y, -502), Vector3.new(876, Y, -504), Vector3.new(851, Y, -494), Vector3.new(826, Y, -498), Vector3.new(806, Y, -506) }
m:SetAttribute("TrasaY", Y)
m:PivotTo(CFrame.new(TRASA[1]))
m.Parent = kont

local RUCH = [[
-- ruch poglądowego slime'a: skoki po trasie tam i z powrotem (źródło: tools/studio/slime_podglad.luau)
local RunService = game:GetService("RunService")
local m = script.Parent
local cialo = m:WaitForChild("Ciało")
local siatka = cialo:FindFirstChildOfClass("SpecialMesh")
local Y = m:GetAttribute("TrasaY") or 0.75
local TRASA = { Vector3.new(888, Y, -502), Vector3.new(876, Y, -504), Vector3.new(851, Y, -494), Vector3.new(826, Y, -498), Vector3.new(806, Y, -506) }
local SKOK, PAUZA, DLUGOSC, WYS = 0.42, 0.16, 3.4, 2.4
local poz, cel, krok = TRASA[1], 2, 1
local kier = (TRASA[2] - TRASA[1]).Unit
local t, start, koniec = 0, poz, poz
local function nowySkok()
	local doCelu = TRASA[cel] - poz
	if doCelu.Magnitude < 0.6 then
		if cel == #TRASA then krok = -1 elseif cel == 1 then krok = 1 end
		cel += krok
		doCelu = TRASA[cel] - poz
	end
	kier = doCelu.Unit
	start, koniec = poz, poz + kier * math.min(DLUGOSC, doCelu.Magnitude)
	t = 0
end
nowySkok()
local obrot = CFrame.lookAt(Vector3.zero, kier)
RunService.Heartbeat:Connect(function(dt)
	t += dt
	local u = math.clamp(t / SKOK, 0, 1)
	local wys, sy = 0, 1
	if t <= SKOK then
		poz = start:Lerp(koniec, u)
		wys = 4 * WYS * u * (1 - u)
		sy = 1 + 0.22 * math.sin(math.pi * u) -- w locie wyciągnięty
	else
		poz = koniec
		local q = math.clamp((t - SKOK) / PAUZA, 0, 1)
		sy = 1 - 0.28 * math.sin(math.pi * q) -- po lądowaniu przysiad
		if q >= 1 then
			nowySkok()
		end
	end
	obrot = obrot:Lerp(CFrame.lookAt(Vector3.zero, kier), math.min(1, dt * 10))
	m:PivotTo(CFrame.new(poz + Vector3.new(0, wys, 0)) * obrot)
	if siatka then
		local sx = 1 + (1 - sy) * 0.6
		siatka.Scale = Vector3.new(sx, sy, sx)
		siatka.Offset = Vector3.new(0, (sy - 1) * 1.7, 0)
	end
end)
]]
if RunService:IsRunning() then
	-- w trakcie Play nie da się dopisać skryptu ze źródłem ani użyć loadstring: model staje przy bramie bez ruchu.
	-- Ruch w bieżącej rozgrywce: wkleić treść RUCH (z „local m = workspace.LasLowPolyPodglad.Slime”) do execute_luau
	-- na serwerze — tak zrobiono 28.11.
	return "Slime stoi przy bramie makiety (tylko ta rozgrywka, bez ruchu); na stałe z ruchem — uruchom ten plik w trybie Edit"
end
local s = Instance.new("Script")
s.Name = "RuchSlime"
s.Source = RUCH
s.Parent = m
return "Slime dodany do makiety na stałe (model + skrypt RuchSlime)"
