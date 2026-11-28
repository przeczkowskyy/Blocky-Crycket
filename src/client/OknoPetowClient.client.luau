--!strict
--[[
	OknoPetowClient — okno petów w HUD (Paweł 25.11). GUI: src/gui/OknoPetow.model.json (tools/hud_pety_build_gui.py).

	Otwieranie: przycisk „Pets” w HUD (ReplicatedStorage.HUDButtonPressed). Zamykanie: X, tło, Esc albo znów „Pets”.
	Góra okna: 4 sloty założonych petów (2 otwarte, 2 z kłódką — do odblokowania później). Dół: wszystkie posiadane
	pety (jeden kafelek na gatunek, licznik kopii). Klik w peta na dole zakłada go, klik w założonego zdejmuje.
	EQUIP BEST zakłada najrzadsze, UNEQUIP ALL zdejmuje, DELETE — jeszcze nieczynne (brak usuwania w stanie gracza).
	Podpowiedź przy najechaniu: nazwa, rzadkość, co pet daje graczowi (opis z danych Karola), liczba kopii.
	26.11 (agent Karola, za zgodą Karola): na każdym kafelku widać bez najeżdżania, ile pet daje Rybek na sekundę
	w zagrodzie („+0.04/s” z ikoną Rybki z HUD; zielone — stoi tam teraz). DELETE → SELL: tryb sprzedaży — klik
	zaznacza nadmiar kopii peta (pet założony i pet w zagrodzie zostawiają jedną kopię, z jedną kopią nie da się ich
	zaznaczyć — napis na kafelku), EQUIP BEST → „SELL N FOR X”, pierwszy klik pyta, drugi sprzedaje (serwer petów Karola).

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

------------------------------------------------------------------ dochód na kafelku i sprzedaż (26.11, agent Karola)
local ZIELONY, KREMOWY = Color3.fromRGB(140, 232, 101), Color3.fromRGB(252, 227, 176)
local ikonaRybki: string? = nil -- obrazek Rybki z HUD (GoldIcon) — bez nowych zasobów
local function ikona(): string
	if ikonaRybki == nil or ikonaRybki == "" then
		local hud = player.PlayerGui:FindFirstChild("HUD")
		local i = hud and hud:FindFirstChild("GoldIcon", true)
		ikonaRybki = if i and (i:IsA("ImageLabel") or i:IsA("ImageButton")) then (i :: any).Image else ""
	end
	return ikonaRybki :: string
end

-- napis „+0.04/s” na kafelku: kopia etykiety nazwy (ta sama czcionka, obrys i limit wielkości), nad nazwą
local function dochodKafelka(slot: Instance): (TextLabel, ImageLabel)
	local t = slot:FindFirstChild("Income") :: TextLabel?
	local r = slot:FindFirstChild("IncomeIcon") :: ImageLabel?
	if t and r then
		return t, r
	end
	local nowy = etykieta(slot, "PetName"):Clone()
	nowy.Name = "Income"
	nowy.Text = ""
	nowy.Position = UDim2.fromScale(0.27, 0.5)
	nowy.Size = UDim2.fromScale(0.7, 0.21)
	nowy.TextXAlignment = Enum.TextXAlignment.Left
	nowy.Parent = slot
	local obraz = Instance.new("ImageLabel")
	obraz.Name = "IncomeIcon"
	obraz.BackgroundTransparency = 1
	obraz.Position = UDim2.fromScale(0.05, 0.5)
	obraz.Size = UDim2.fromScale(0.2, 0.21)
	obraz.ScaleType = Enum.ScaleType.Fit
	obraz.ZIndex = nowy.ZIndex
	obraz.Parent = slot
	return nowy, obraz
end

-- zielone kółko z „✓” z dwóch kresek (czcionka gry nie ma tego znaku) w rogu zaznaczonego kafelka
local function znaczekWyboru(slot: Instance): Frame
	local z = slot:FindFirstChild("SellCheck") :: Frame?
	if z then
		return z
	end
	local f = Instance.new("Frame")
	f.Name = "SellCheck"
	f.AnchorPoint = Vector2.new(0.5, 0.5)
	f.Position = UDim2.fromScale(0.22, 0.2)
	f.Size = UDim2.fromScale(0.34, 0.34)
	f.BackgroundColor3 = ZIELONY
	f.ZIndex = 9
	f.Visible = false
	local rog = Instance.new("UICorner")
	rog.CornerRadius = UDim.new(1, 0)
	rog.Parent = f
	local proporcja = Instance.new("UIAspectRatioConstraint")
	proporcja.Parent = f
	local obrys = Instance.new("UIStroke")
	obrys.Color = Color3.fromRGB(43, 33, 24)
	obrys.Thickness = 2
	obrys.Parent = f
	for _, k in ipairs({ { 0.36, 0.58, 0.28, 45 }, { 0.6, 0.48, 0.52, -48 } }) do
		local kreska = Instance.new("Frame")
		kreska.AnchorPoint = Vector2.new(0.5, 0.5)
		kreska.Position = UDim2.fromScale(k[1], k[2])
		kreska.Size = UDim2.fromScale(k[3], 0.14)
		kreska.Rotation = k[4]
		kreska.BackgroundColor3 = Color3.new(1, 1, 1)
		kreska.BorderSizePixel = 0
		kreska.ZIndex = 10
		kreska.Parent = f
	end
	f.Parent = slot
	return f
end

local trybSprzedazy = false
local wybrane: { [string]: number } = {} -- pet → ile kopii sprzedać
local potwierdzenie = 0 -- do kiedy (os.clock) drugi klik w „SELL N FOR X” sprzedaje

-- ile kopii peta można sprzedać: założony (slot 1 / 2) i stojący w zagrodzie zostawiają sobie jedną kopię
local function doSprzedazy(p: any): (number, string?)
	local chroniony = zalozonyW(p.pet) ~= nil or p.wZagrodzie == true
	local n = (p.kopie or 0) - (if chroniony then 1 else 0)
	if n > 0 then
		return n, nil
	end
	return 0, if zalozonyW(p.pet) then "EQUIPPED" else "IN PEN"
end

local function wybraneRazem(): (number, number)
	local sztuk, suma = 0, 0
	for _, p in ipairs(if stan and stan.ok then stan.pety else {}) do
		local n = wybrane[p.pet]
		if n then
			sztuk += n
			suma += n * (p.sprzedaz or 0)
		end
	end
	return sztuk, suma
end

local function rysujStopke()
	local sztuk, suma = wybraneRazem()
	etykieta(panel, "DeleteLabel").Text = if trybSprzedazy then "CANCEL" else "SELL"
	etykieta(panel, "UnequipLabel").Text = if trybSprzedazy then "CLEAR" else "UNEQUIP ALL"
	etykieta(panel, "EquipBestLabel").Text = if not trybSprzedazy then "EQUIP BEST"
		elseif sztuk == 0 then "TAP PETS"
		elseif os.clock() < potwierdzenie then "TAP TO CONFIRM"
		else string.format("SELL %d FOR %d", sztuk, suma)
end

-- napis dochodu (albo, w trybie sprzedaży, dlaczego peta nie da się zaznaczyć) i znaczek wyboru jednego kafelka
local function rysujKafelek(slot: Instance, p: any)
	local t, ik = dochodKafelka(slot)
	local n, powod: string? = 0, nil
	if p then
		n, powod = doSprzedazy(p)
		local juz = wybrane[p.pet]
		wybrane[p.pet] = if juz and n > 0 then math.min(juz, n) else nil -- po sprzedaży / zmianie stanu nie więcej, niż wolno
	end
	local obrazek = if p and not (trybSprzedazy and powod) then ikona() else ""
	t.Text = if not p then "" elseif trybSprzedazy and powod then powod else (p.rybki or "")
	t.TextColor3 = if p and p.wZagrodzie and not (trybSprzedazy and powod) then ZIELONY else KREMOWY
	t.TextTransparency = if p and p.wZagrodzie and not (trybSprzedazy and powod) then 0 else 0.3
	t.Position = if obrazek ~= "" then UDim2.fromScale(0.27, 0.5) else UDim2.fromScale(0.03, 0.5)
	t.Size = if obrazek ~= "" then UDim2.fromScale(0.7, 0.21) else UDim2.fromScale(0.94, 0.21)
	t.TextXAlignment = if obrazek ~= "" then Enum.TextXAlignment.Left else Enum.TextXAlignment.Center
	ik.Image = obrazek
	ik.ImageTransparency = t.TextTransparency
	znaczekWyboru(slot).Visible = trybSprzedazy and p ~= nil and wybrane[p.pet] ~= nil
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
		rysujKafelek(slot, p)
	end
	rysujStopke()
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

------------------------------------------------------------------ sprzedaż: tryb, zaznaczanie, potwierdzenie (26.11)
local function przelaczTryb()
	trybSprzedazy = not trybSprzedazy
	table.clear(wybrane)
	potwierdzenie = 0
	schowajPodpowiedz(nil)
	rysuj()
	msg.Text = if trybSprzedazy then "Tap pets to sell their extra copies" else ""
end

local function przelaczWybor(p: any)
	local n, powod = doSprzedazy(p)
	potwierdzenie = 0
	local tekst: string? = nil
	if wybrane[p.pet] then
		wybrane[p.pet] = nil
	elseif n > 0 then
		wybrane[p.pet] = n
	else
		tekst = if powod == "EQUIPPED" then "Equipped pets stay — only extra copies can be sold"
			else "This pet earns fish in your pen — take it out at the Pet Pen first"
	end
	rysuj()
	if tekst then
		msg.Text = tekst
	end
end

local function sprzedajWybrane()
	local sztuk, suma = wybraneRazem()
	if sztuk == 0 then
		rysuj()
		msg.Text = "Tap pets to sell their extra copies"
		return
	end
	if os.clock() > potwierdzenie then
		potwierdzenie = os.clock() + 5
		rysuj()
		msg.Text = string.format("Sell %d %s for %d fish? Tap again to confirm", sztuk, if sztuk == 1 then "pet" else "pets",
			suma)
		task.delay(5.1, function()
			if os.clock() > potwierdzenie then
				rysujStopke()
			end
		end)
		return
	end
	potwierdzenie = 0
	local lista = {}
	for _, p in ipairs(if stan and stan.ok then stan.pety else {}) do
		if wybrane[p.pet] then
			table.insert(lista, { pet = p.pet, ile = wybrane[p.pet] })
		end
	end
	table.clear(wybrane)
	wyslij("sprzedaj", lista) -- serwer odpowiada stanem z tekstem „Sold N pets for X fish”
end

------------------------------------------------------------------ kliknięcia i najechanie
local dotyk = UIS.TouchEnabled and not UIS.MouseEnabled

for i, slot in ipairs(slotyGory) do
	slot.Activated:Connect(function()
		if trybSprzedazy then
			return -- w trybie sprzedaży sloty u góry nic nie robią (nie zdejmujemy peta przy okazji)
		end
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
		if trybSprzedazy then
			przelaczWybor(p)
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

-- w trybie sprzedaży EQUIP BEST sprzedaje zaznaczone (z potwierdzeniem), UNEQUIP ALL czyści zaznaczenie
local function przycisk(nazwa: string, polecenie: string, wSprzedazy: () -> ())
	(panel:WaitForChild(nazwa) :: ImageButton).Activated:Connect(function()
		if trybSprzedazy then
			wSprzedazy()
		else
			wyslij(polecenie)
		end
	end)
end
przycisk("EquipBestButton", "najlepsze", sprzedajWybrane)
przycisk("UnequipButton", "zdejmij_wszystkie", function()
	table.clear(wybrane)
	potwierdzenie = 0
	rysuj()
end);
(panel:WaitForChild("DeleteButton") :: ImageButton).Activated:Connect(przelaczTryb)

------------------------------------------------------------------ otwieranie i zamykanie
local function zamknij()
	if not otwarte then
		return
	end
	otwarte = false
	gui.Enabled = false
	schowajPodpowiedz(nil)
	trybSprzedazy = false -- okno zawsze otwiera się w zwykłym trybie
	table.clear(wybrane)
	potwierdzenie = 0
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
