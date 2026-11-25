--!strict
--[[
	OknoPetowClient — okno petów w HUD (Paweł 25.11). GUI: src/gui/OknoPetow.model.json (tools/hud_pety_build_gui.py).

	Otwieranie: przycisk „Pets” w HUD (ReplicatedStorage.HUDButtonPressed). Zamykanie: X, tło, Esc albo znów „Pets”.
	Góra okna: 4 sloty założonych petów (2 otwarte, 2 z kłódką — do odblokowania później). Dół: wszystkie posiadane
	pety (jeden kafelek na gatunek, licznik kopii). Klik w peta na dole zakłada go, klik w założonego zdejmuje.
	EQUIP BEST zakłada najrzadsze, UNEQUIP ALL zdejmuje, DELETE — jeszcze nieczynne (brak usuwania w stanie gracza).
	Podpowiedź przy najechaniu: nazwa, rzadkość, co pet daje graczowi (opis z danych Karola), liczba kopii.

	Dane i polecenia: ReplicatedStorage.OknoPetow (src/server/OknoPetow.server.luau). Podobizny 3D budują moduły Karola
	(PetyProba/Moduly: RigPetow.zbuduj + Rig_<pet>) — działają tylko w Studio; bez nich kafelek ma samą nazwę.
]]
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UIS = game:GetService("UserInputService")

if not RunService:IsStudio() then
	return
end

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("OknoPetow") :: ScreenGui
local panel = gui:WaitForChild("Panel") :: Frame
local tooltip = gui:WaitForChild("Tooltip") :: ImageLabel
local F = RS:WaitForChild("OknoPetow") :: RemoteFunction

local SLOTOW_PLECAKA = 24
local stan: any = nil
local otwarte = false
local pokazane: { [Instance]: string } = {} -- co jest narysowane w którym widoku (żeby nie budować modeli od nowa)

local function etykieta(rodzic: Instance, nazwa: string): TextLabel
	return rodzic:WaitForChild(nazwa) :: TextLabel
end

local msg = etykieta(panel, "Message")
local licznik = etykieta(panel, "EquippedCount")
local moje = etykieta(panel, "OwnedLabel")

local PL = { ["ą"] = "Ą", ["ć"] = "Ć", ["ę"] = "Ę", ["ł"] = "Ł", ["ń"] = "Ń", ["ó"] = "Ó", ["ś"] = "Ś", ["ź"] = "Ź", ["ż"] = "Ż" }
local function wielkie(t: string): string
	local w = string.upper(t)
	for m, d in pairs(PL) do
		w = string.gsub(w, m, d)
	end
	return w
end

------------------------------------------------------------------ podobizna peta w ramce
local function pokazPeta(v: ViewportFrame, petId: string?)
	if pokazane[v] == (petId or "") then
		return
	end
	pokazane[v] = petId or ""
	for _, x in ipairs(v:GetChildren()) do
		x:Destroy()
	end
	if not petId then
		return
	end
	local k = workspace:FindFirstChild("PetyProba")
	local mod = k and k:FindFirstChild("Moduly")
	local rig = mod and mod:FindFirstChild("RigPetow")
	local dane = mod and mod:FindFirstChild("Rig_" .. petId, true)
	if not (rig and rig:IsA("ModuleScript") and dane and dane:IsA("ModuleScript")) then
		return
	end
	local ok, model = pcall(function()
		local R = require(rig) :: any
		return (R.zbuduj(require(dane), 1, "Podglad " .. petId))
	end)
	if not ok or typeof(model) ~= "Instance" then
		return
	end
	local m = model :: Model
	m.Parent = v
	local cf, rozmiar = m:GetBoundingBox()
	local przod, bok = m:GetPivot().LookVector, m:GetPivot().RightVector
	local cam = Instance.new("Camera")
	cam.FieldOfView = 30
	local odl = math.max(rozmiar.X, rozmiar.Y, rozmiar.Z) * 2.3
	cam.CFrame = CFrame.lookAt(cf.Position + (przod * 0.9 + bok * 0.45).Unit * odl + Vector3.new(0, rozmiar.Y * 0.2, 0), cf.Position)
	cam.Parent = v
	v.CurrentCamera = cam
end

local function wiersz(petId: string?): any
	if not (stan and stan.ok and petId) then
		return nil
	end
	for _, p in ipairs(stan.pety) do
		if p.pet == petId then
			return p
		end
	end
	return nil
end

local function obwodka(slot: Instance, kolor: string?)
	local r = slot:FindFirstChild("Rim") :: Frame?
	local st = r and r:FindFirstChildWhichIsA("UIStroke")
	if r and st then
		r.Visible = kolor ~= nil
		if kolor then
			st.Color = Color3.fromHex(kolor)
		end
	end
end

------------------------------------------------------------------ podpowiedź
local podpowiedzDla: Instance? = nil
local function waluta(t: string): string
	-- waluta gry to rybki (D-146) — opisy z danych Karola mówią jeszcze „Złoto”
	return (string.gsub(string.gsub(t, "Złota", "Rybek"), "Złoto", "Rybki"))
end

local function pokazPodpowiedz(slot: Instance, tytul: string, podtytul: string, kolor: string, opis: string, dol: string)
	podpowiedzDla = slot
	etykieta(tooltip, "PetName").Text = tytul
	local rz = etykieta(tooltip, "Rarity")
	rz.Text = podtytul
	rz.TextColor3 = Color3.fromHex(kolor)
	etykieta(tooltip, "Skill").Text = opis
	etykieta(tooltip, "Copies").Text = dol
	tooltip.Visible = true
end

local function schowajPodpowiedz(slot: Instance?)
	if slot == nil or podpowiedzDla == slot then
		podpowiedzDla = nil
		tooltip.Visible = false
	end
end

local function podpowiedzPeta(slot: Instance, p: any, zalozonyW: number?)
	local dol = string.format("Owned: x%d", p.kopie)
	if zalozonyW == 1 then
		dol ..= "  ·  EQUIPPED"
	elseif zalozonyW == 2 then
		dol ..= "  ·  EQUIPPED (slot 2: bonus soon)"
	end
	pokazPodpowiedz(slot, p.nazwa, wielkie(p.rzadkoscNazwa or ""), p.kolor or "FFFFFF", waluta(p.skill or ""), dol)
end

RunService.RenderStepped:Connect(function()
	if not tooltip.Visible then
		return
	end
	local m = UIS:GetMouseLocation()
	local ekran = gui.AbsoluteSize
	local r = tooltip.AbsoluteSize
	local x = math.clamp(m.X + 18, 4, math.max(4, ekran.X - r.X - 4))
	local y = math.clamp(m.Y + 18, 4, math.max(4, ekran.Y - r.Y - 4))
	tooltip.Position = UDim2.fromOffset(x, y)
end)

------------------------------------------------------------------ rysowanie
local slotyGory: { ImageButton } = {}
local slotyDolu: { ImageButton } = {}
for i = 1, 4 do
	slotyGory[i] = panel:WaitForChild("Equipped" .. i) :: ImageButton
end
for i = 1, SLOTOW_PLECAKA do
	slotyDolu[i] = panel:WaitForChild(string.format("Pet%02d", i)) :: ImageButton
end

local function zalozonyW(petId: string): number?
	if stan and stan.ok then
		if stan.pierwszy == petId then
			return 1
		elseif stan.drugi == petId then
			return 2
		end
	end
	return nil
end

local function rysuj()
	local s = stan
	local ok = s ~= nil and s.ok
	local zal = { if ok then s.pierwszy else nil, if ok then s.drugi else nil }
	local ile = 0
	for i = 1, 4 do
		local slot = slotyGory[i]
		local petId: string? = if i <= 2 then zal[i] else nil
		local p = wiersz(petId)
		pokazPeta(slot:WaitForChild("View") :: ViewportFrame, if p then petId else nil)
		etykieta(slot, "PetName").Text = if p then p.nazwa else ""
		obwodka(slot, if p then p.kolor else nil)
		if p then
			ile += 1
		end
	end
	local otwartych = if ok then s.sloty else 2
	licznik.Text = string.format("%d/%d", ile, otwartych)
	moje.Text = if ok then string.format("MY PETS  %d", s.razem) else "MY PETS"
	for i = 1, SLOTOW_PLECAKA do
		local slot = slotyDolu[i]
		local p = if ok then s.pety[i] else nil
		pokazPeta(slot:WaitForChild("View") :: ViewportFrame, if p then p.pet else nil)
		etykieta(slot, "Count").Text = if p and p.kopie > 1 then "x" .. p.kopie else ""
		etykieta(slot, "PetName").Text = if p then p.nazwa else ""
		local w = if p then zalozonyW(p.pet) else nil
		etykieta(slot, "Mark").Text = if w then "E" else ""
		obwodka(slot, if p then p.kolor else nil)
	end
	if s and type(s.tekst) == "string" then
		msg.Text = s.tekst
		local znacznik = s
		task.delay(3.5, function()
			if stan == znacznik then
				msg.Text = ""
			end
		end)
	elseif ok then
		msg.Text = if #s.pety == 0 then "No pets yet - hatch an egg!" else ""
	end
end

local wToku = false
local function wyslij(polecenie: string, a: any?)
	if wToku then
		return
	end
	wToku = true
	local ok, w = pcall(function()
		return F:InvokeServer(polecenie, a)
	end)
	wToku = false
	if ok and type(w) == "table" then
		stan = w
		rysuj()
	end
end

------------------------------------------------------------------ kliknięcia i najechanie
local dotyk = UIS.TouchEnabled and not UIS.MouseEnabled

for i, slot in ipairs(slotyGory) do
	slot.Activated:Connect(function()
		if i > 2 then
			msg.Text = "This slot unlocks later in the game"
			return
		end
		if stan and stan.ok and ((i == 1 and stan.pierwszy) or (i == 2 and stan.drugi)) then
			schowajPodpowiedz(nil)
			wyslij("zdejmij", i)
		end
	end)
	slot.MouseEnter:Connect(function()
		if i > 2 then
			pokazPodpowiedz(slot, "LOCKED SLOT", "UNLOCKS LATER", "FFC23D", "Keep playing to unlock more pet slots.", "")
			return
		end
		local id = if stan and stan.ok then (if i == 1 then stan.pierwszy else stan.drugi) else nil
		local p = wiersz(id)
		if p then
			podpowiedzPeta(slot, p, i)
		else
			pokazPodpowiedz(slot, "EMPTY SLOT", "", "FFFFFF", "Click a pet below to equip it here.", "")
		end
	end)
	slot.MouseLeave:Connect(function()
		schowajPodpowiedz(slot)
	end)
end

for i, slot in ipairs(slotyDolu) do
	slot.Activated:Connect(function()
		local p = if stan and stan.ok then stan.pety[i] else nil
		if not p then
			return
		end
		local w = zalozonyW(p.pet)
		if w then
			wyslij("zdejmij", w)
		else
			wyslij("zaloz", p.pet)
		end
		if dotyk then
			local np = if stan and stan.ok then stan.pety[i] else nil
			if np then
				podpowiedzPeta(slot, np, zalozonyW(np.pet))
				task.delay(2.5, function()
					schowajPodpowiedz(slot)
				end)
			end
		end
	end)
	slot.MouseEnter:Connect(function()
		local p = if stan and stan.ok then stan.pety[i] else nil
		if p then
			podpowiedzPeta(slot, p, zalozonyW(p.pet))
		end
	end)
	slot.MouseLeave:Connect(function()
		schowajPodpowiedz(slot)
	end)
end

local function przycisk(nazwa: string, polecenie: string)
	(panel:WaitForChild(nazwa) :: ImageButton).Activated:Connect(function()
		wyslij(polecenie)
	end)
end
przycisk("EquipBestButton", "najlepsze")
przycisk("UnequipButton", "zdejmij_wszystkie")
przycisk("DeleteButton", "usun")

------------------------------------------------------------------ otwieranie i zamykanie
local function zamknij()
	if not otwarte then
		return
	end
	otwarte = false
	gui.Enabled = false
	schowajPodpowiedz(nil)
end

local function otworz()
	if otwarte then
		return
	end
	otwarte = true
	msg.Text = ""
	gui.Enabled = true
	rysuj()
	task.spawn(wyslij, "stan")
end

(panel:WaitForChild("CloseButton") :: ImageButton).Activated:Connect(zamknij);
(gui:WaitForChild("Backdrop") :: TextButton).Activated:Connect(zamknij)
UIS.InputBegan:Connect(function(wejscie, przetworzone)
	if otwarte and not przetworzone and wejscie.KeyCode == Enum.KeyCode.Escape then
		zamknij()
	end
end)

local hud = RS:WaitForChild("HUDButtonPressed", 120)
if hud and hud:IsA("BindableEvent") then
	hud.Event:Connect(function(nazwa)
		if nazwa == "Pets" then
			if otwarte then
				zamknij()
			else
				otworz()
			end
		elseif otwarte then
			zamknij() -- inny przycisk HUD otwiera swoje okno
		end
	end)
end
