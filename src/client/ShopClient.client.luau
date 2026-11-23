--[[
	ShopClient — okno sklepu (ScreenGui „Shop”, src/gui/Shop.model.json, generator tools/shop_build_gui.py).
	Dwa wyglądy w jednym oknie: sklep z bronią (Blocky za ladą) i sklep magiczny (Crycket za ladą).
	Projekt: B&C/UI/Sklepy i bronie startowe — prompty.md (propozycja).

	LEWA STRONA = kopia okna ekwipunku (Paweł 23.11: „żeby to EQ jakby się kopiowało po prostu do tych sklepów”):
	te same przedmioty w tych samych slotach i na tych samych miejscach plecaka, poziom i pasek doświadczenia,
	znaczek klasy w portrecie. Stan bierzemy ze wspólnego modułu EkwipunekStan (ten sam co EquipmentPanelClient),
	więc każda zmiana w EQ od razu widać w sklepie i odwrotnie. Zakładki WEAPONS / ARMOR / AMULETS / OTHERS
	przełączają stronę plecaka (sklep pokazuje sloty 1–15 strony, czyli trzy górne rzędy plecaka z EQ).

	PRAWA STRONA = towar zbrojmistrza z serwera sklepu Karola (swiat/sklep_proba, D-106): RemoteFunction
	Workspace/SklepProba/Zdalne/Sklep — "oferta" → widok { oferta, zloto, poziom, klasa }, "kup", id, "zaloz", id.
	O cenie, poziomie, klasie i Złocie decyduje serwer (kowal); klient wysyła tylko akcję i id. Sześć slotów
	pokazuje po sześć pozycji, przycisk odświeżenia przechodzi do następnych. Kliknięcie slotu → karta przedmiotu
	z przyciskiem BUY (albo EQUIP dla posiadanego). Przedmioty posiadane trafiają też do EQ (EkwipunekStan.zKowala).
	Sklep magiczny nie ma jeszcze towaru (serwer obsługuje tylko zbrojownię) — tabliczka „COMING SOON”.

	Okno tymczasowe Karola (SklepProba/KlientSklepu) też słucha E przy zbrojowni i chowało to okno (stąd 23.11
	„nie działa”). Bez zmian w jego plikach: wyłączamy u siebie jego chowanie (atrybut ChowajOknoShop = false,
	tylko po stronie klienta — tak przewidział jego README) i zamykamy jego okno jego haczykiem
	Sygnaly/SterowanieKlienta "zamknij".

	Otwieranie: E przy sprzedawcy (OknoMiejsca z pakietu bazaru: zbrojownia, sklep_magiczny) albo kliknięcie /
	dotknięcie sprzedawcy z bliska. Zamyka X, Esc, kliknięcie obok albo odejście od miejsca otwarcia.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
local TS = game:GetService("TweenService")
local RunService = game:GetService("RunService")

local Stan = require(script.Parent:WaitForChild("EkwipunekStan"))

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("Shop")
local panel = gui:WaitForChild("Panel")
local backdrop = gui:WaitForChild("Backdrop")
local panelScale = panel:WaitForChild("UIScale")
local card = panel:WaitForChild("Card")
local plate = panel:WaitForChild("Plate")

local QUICK = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local ZASIEG_KLIKU = 22 -- studów: sprzedawcę klika się z bliska (jak E)
local ZASIEG_OKNA = 26 -- studów od miejsca otwarcia: dalej okno się zamyka (u Karola 20 od stoiska)
local SLOTY_PLECAKA = 15
local ZAKLADKI = { "Weapons", "Armor", "Amulets", "Others" }
local KOLOR_ZAKLADKI = Color3.fromRGB(255, 255, 255)
local KOLOR_ZAKLADKI_NIE = Color3.fromRGB(150, 150, 150)
local NAZWY_STOPNI = { start = "STARTER", las = "FOREST", bagno = "SWAMP", dzungla = "JUNGLE" }

local SKLEPY = {
	zbrojownia = { art = "ArtBron", tytul = "WEAPON SHOP", model = "Zbrojmistrz", budynek = "Zbrojownia", towar = true },
	sklep_magiczny = { art = "ArtMagia", tytul = "MAGIC SHOP", model = "Mag", budynek = "SklepMagiczny", towar = false },
}

local function bindable(name: string): BindableEvent
	local e = RS:FindFirstChild(name)
	if not e then
		e = Instance.new("BindableEvent")
		e.Name = name
		e.Parent = RS
	end
	return e :: BindableEvent
end

-- okno zgłasza się pakietowi bazaru: przy E nie pokaże dymku „sklep w budowie”
local okna = bindable("OknoMiejsca")
okna:SetAttribute("zbrojownia", true)
okna:SetAttribute("sklep_magiczny", true)

------------------------------------------------------------ serwer sklepu Karola (SklepProba)
local function sklepProba(): Instance?
	return workspace:FindFirstChild("SklepProba")
end

local function zdalneSklepu(): RemoteFunction?
	local k = sklepProba()
	local z = k and k:FindFirstChild("Zdalne")
	local f = z and z:FindFirstChild("Sklep")
	return if f and f:IsA("RemoteFunction") then f else nil
end

-- jego klient nie chowa już naszego okna (atrybut ustawiony tylko u nas, na kopii kontenera po stronie klienta)
task.spawn(function()
	local k = workspace:WaitForChild("SklepProba", 30)
	if k then
		k:SetAttribute("ChowajOknoShop", false)
	end
end)

local function zamknijOknoKarola()
	local k = sklepProba()
	local s = k and k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild("SterowanieKlienta")
	if f and f:IsA("BindableFunction") then
		pcall(function()
			(f :: BindableFunction):Invoke("zamknij")
		end)
	end
end

------------------------------------------------------------ stan okna
local otwarte: string? = nil
local zamykanie = false
local miejsceOtwarcia: Vector3? = nil
local zakladka = "Weapons"
local oferta: { any } = {}
local strona = 0 -- która szóstka towaru jest na ladzie
local wybrany: any = nil -- wiersz oferty na karcie
local czeka = false
local zloto: number? = nil

------------------------------------------------------------ tabliczka: Złoto albo komunikat
local komunikatDo = 0
local function rysujTabliczke()
	if os.clock() < komunikatDo then
		return
	end
	local s = otwarte and SKLEPY[otwarte]
	if s and not s.towar then
		plate.Text = "COMING SOON"
	elseif zloto then
		plate.Text = tostring(zloto) .. " GOLD"
	else
		plate.Text = "NEW GOODS"
	end
	plate.TextColor3 = Color3.fromRGB(252, 227, 176)
end

local function komunikat(tekst: string, blad: boolean)
	plate.Text = tekst
	plate.TextColor3 = if blad then Color3.fromRGB(255, 120, 100) else Color3.fromRGB(140, 232, 101)
	komunikatDo = os.clock() + 2.6
	task.delay(2.7, rysujTabliczke)
end

------------------------------------------------------------ lewa strona: kopia EQ
local equipFolder = panel:WaitForChild("EquipSlots")
local bagFolder = panel:WaitForChild("BackpackGrid")

local function rysujEkwipunek()
	for _, s in ipairs(equipFolder:GetChildren()) do
		if s:IsA("GuiButton") then
			local id = Stan.equip[s.Name]
			Stan.rysujIkone(s:WaitForChild("Icon"), id)
			local cover = s:FindFirstChild("Cover")
			if cover then
				cover.Visible = id ~= nil
			end
		end
	end
	local page = Stan.bag[zakladka]
	for i = 1, SLOTY_PLECAKA do
		local s = bagFolder:FindFirstChild(string.format("BagSlot%02d", i))
		if s then
			Stan.rysujIkone(s:WaitForChild("Icon"), page[i])
		end
	end
	for _, nazwa in ipairs(ZAKLADKI) do
		local t = panel.Tabs:FindFirstChild("Tab" .. nazwa)
		if t then
			t.TextColor3 = if nazwa == zakladka then KOLOR_ZAKLADKI else KOLOR_ZAKLADKI_NIE
		end
	end
end
Stan.Zmiana.Event:Connect(function()
	if gui.Enabled then
		rysujEkwipunek()
	end
end)

local fill = panel:WaitForChild("ExpBar"):WaitForChild("Fill")
local function rysujPoziom()
	panel.Level.Text = "LV " .. tostring(player:GetAttribute("Level") or 1)
	local xp = player:GetAttribute("XP") or 0
	local maxXp = math.max(player:GetAttribute("XPMax") or 100, 1)
	fill.Size = UDim2.fromScale(math.clamp(xp / maxXp, 0, 1), 1)
	local ok, ClassData = pcall(function()
		return require(RS:WaitForChild("Shared"):WaitForChild("ClassData"))
	end)
	local ok2, Icons = pcall(function()
		return require(RS:WaitForChild("Shared"):WaitForChild("ClassSelectIcons"))
	end)
	local c = ok and ok2 and ClassData.byId(player:GetAttribute("Class") or "")
	panel.ClassEmblem.Image = c and Icons[c.emblem] or ""
end
-- portret rasy w ramce bohatera (Paweł 23.11); emblemat klasy tylko wtedy, gdy portretu nie ma
pcall(function()
	-- ramka z portretem rasy w miejscu starej ramki bohatera (wymazanej z grafiki sklepu w tools/sklep_okno.py)
	panel.ExpBar.BackgroundTransparency = 1
	for _, d in ipairs(panel.ExpBar:GetDescendants()) do
		if d:IsA("UICorner") then
			d.CornerRadius = UDim.new(0.25, 0) -- jak w EQ: końce lekko zaokrąglone
		end
	end
	local c0 = panel.ExpBar:FindFirstChildOfClass("UICorner")
	if c0 then
		c0.CornerRadius = UDim.new(0.25, 0) -- jak w EQ: końce lekko zaokrąglone
	end
	local granica = panel.Level:FindFirstChildOfClass("UITextSizeConstraint")
	if granica then
		granica.MaxTextSize = 60 -- napis skaluje się do wysokości paska jak w EQ
	end
	require(RS:WaitForChild("Shared"):WaitForChild("RacePortraitUI")).attach({
		rodzic = panel,
		prostokat = { 0.1908, 0.1959, 0.1629, 0.2419 }, -- px 916–1698 × 702–1569 z 4800 × 3584
		zindex = 2,
		nad = { panel.ExpBar, panel.Level, panel.ClassEmblem },
		-- pasek i „LV” w torze ramki WYBRANEJ rasy — wymiary z Figmy (Shared.RacePortraits.Tor), jak w EQ
		pasek = {
			{ obj = panel.ExpBar, ramka = { 0.1908, 0.1959, 0.1629, 0.2419 } },
			{ obj = panel.Level, ramka = { 0.1908, 0.1959, 0.1629, 0.2419 }, wnetrze = { 0.03, 0.2, 0.94, 0.75 } },
		},
		zastepstwo = panel.ClassEmblem,
	})
end)
for _, a in ipairs({ "Level", "XP", "XPMax", "Class" }) do
	player:GetAttributeChangedSignal(a):Connect(function()
		if gui.Enabled then
			rysujPoziom()
		end
	end)
end

------------------------------------------------------------ prawa strona: towar
local KOLEJNOSC_STANU = { kup = 1, za_drogie = 2, za_niski_poziom = 3, masz = 4, zalozone = 5 }

local function towarNaLadzie(): { any }
	local s = otwarte and SKLEPY[otwarte]
	if not (s and s.towar) then
		return {}
	end
	local lista = {}
	for _, w in ipairs(oferta) do
		if type(w) == "table" and type(w.id) == "string" and (w.cena or 0) > 0 then
			table.insert(lista, w)
		end
	end
	table.sort(lista, function(a, b)
		local ka, kb = KOLEJNOSC_STANU[a.stan] or 9, KOLEJNOSC_STANU[b.stan] or 9
		if ka ~= kb then
			return ka < kb
		end
		if (a.nrStopnia or 0) ~= (b.nrStopnia or 0) then
			return (a.nrStopnia or 0) < (b.nrStopnia or 0)
		end
		return (a.cena or 0) < (b.cena or 0)
	end)
	return lista
end

local function definicjaTowaru(w: any)
	local okIk, Ikony = pcall(function()
		return require(RS:WaitForChild("Shared"):WaitForChild("IkonyPrzedmiotow"))
	end)
	return {
		name = tostring(w.nazwa or w.id),
		slot = w.slot,
		category = Stan.kategoriaSlotu(w.slot or ""),
		icon = (okIk and Ikony[w.id]) or "",
		kolor = Stan.KOLORY_STOPNI[w.stopien or ""] or Stan.KOLORY_STOPNI.start,
		poziom = tonumber(w.ulepszenie) or 0,
	}
end

local naLadzie: { any } = {}
local function rysujTowar()
	local lista = towarNaLadzie()
	local stron = math.max(1, math.ceil(#lista / 6))
	strona = strona % stron
	naLadzie = {}
	for i = 1, 6 do
		local slot = panel:FindFirstChild("ShopSlot" .. i)
		if not slot then
			continue
		end
		local w = lista[strona * 6 + i]
		naLadzie[i] = w
		local icon = slot:WaitForChild("Icon")
		if w then
			-- ten sam rysunek co w EQ (ikona albo kafelek stopnia z nazwą)
			Stan.rysujDefinicje(icon, definicjaTowaru(w) :: any)
			slot.Price.Text = if w.stan == "masz" or w.stan == "zalozone" then "" else tostring(w.cena) .. " G"
			slot.Price.TextColor3 = if w.stan == "za_drogie" then Color3.fromRGB(255, 120, 100) else Color3.fromRGB(255, 214, 90)
			slot.Lock.Text = if w.stan == "za_niski_poziom" then "LV " .. tostring(w.poziom) else ""
			slot.Owned.Text = if w.stan == "zalozone" then "EQUIPPED" elseif w.stan == "masz" then "OWNED" else ""
			icon.ImageTransparency = if w.stan == "za_niski_poziom" then 0.5 else 0
		else
			Stan.rysujIkone(icon, nil)
			slot.Price.Text = ""
			slot.Lock.Text = ""
			slot.Owned.Text = ""
		end
	end
end

------------------------------------------------------------ karta przedmiotu
local function pokazKarte(w: any, zLewej: boolean)
	wybrany = w
	card.ItemName.Text = tostring(w.nazwa or w.name or "?")
	card.Tier.Text = NAZWY_STOPNI[w.stopien or ""] or ""
	card.Tier.TextColor3 = Stan.KOLORY_STOPNI[w.stopien or ""] or Color3.new(1, 1, 1)
	card.Stats.Text = tostring(w.staty or "")
	if (w.ulepszenie or w.poziomUlepszenia or 0) > 0 then
		card.Stats.Text = card.Stats.Text .. "  (+" .. tostring(w.ulepszenie or w.poziomUlepszenia) .. ")"
	end
	card.Req.Text = if w.poziom then "REQUIRES LV " .. tostring(w.poziom) else ""
	card.Req.TextColor3 = if w.stan == "za_niski_poziom" then Color3.fromRGB(255, 120, 100) else Color3.new(1, 1, 1)
	card.Price.Text = if w.cena and w.cena > 0 and w.stan ~= "masz" and w.stan ~= "zalozone" then tostring(w.cena) .. " GOLD" else ""
	card.Price.TextColor3 = if w.stan == "za_drogie" then Color3.fromRGB(255, 120, 100) else Color3.fromRGB(255, 214, 90)
	local b = card.BuyButton
	if zLewej or w.stan == "zalozone" then
		b.Visible = false
	else
		b.Visible = true
		local kup = w.stan ~= "masz"
		b.Text = if kup then "BUY" else "EQUIP"
		local mozna = w.stan == "kup" or w.stan == "masz"
		b.BackgroundColor3 = if not mozna
			then Color3.fromRGB(90, 96, 112)
			elseif kup then Color3.fromRGB(63, 155, 85)
			else Color3.fromRGB(62, 123, 224)
	end
	card.Visible = true
end

local function schowajKarte()
	wybrany = nil
	card.Visible = false
end

------------------------------------------------------------ rozmowa z serwerem
local function przyjmij(r: any)
	if type(r) ~= "table" then
		komunikat("SHOP CLOSED", true)
		return
	end
	local widok = r.widok
	if type(widok) == "table" and type(widok.oferta) == "table" then
		oferta = widok.oferta
		zloto = tonumber(widok.zloto)
		Stan.zKowala(oferta)
	end
	if type(r.tekst) == "string" and r.tekst ~= "" then
		komunikat(r.tekst, r.ok ~= true)
	else
		rysujTabliczke()
	end
	if gui.Enabled then
		rysujTowar()
		if wybrany then
			-- odśwież kartę wybranego (stan po kupnie)
			for _, w in ipairs(oferta) do
				if type(w) == "table" and w.id == wybrany.id then
					pokazKarte(w, false)
					break
				end
			end
		end
	end
end

local function prosba(akcja: string, id: string?)
	local f = zdalneSklepu()
	if not f then
		if akcja ~= "oferta" then
			komunikat("SHOP CLOSED", true)
		end
		return
	end
	if czeka then
		return
	end
	czeka = true
	local ok, r = pcall(function()
		return (f :: RemoteFunction):InvokeServer(akcja, id)
	end)
	czeka = false
	if ok then
		przyjmij(r)
	elseif akcja ~= "oferta" then
		komunikat("TRY AGAIN", true)
	end
end

------------------------------------------------------------ otwieranie i zamykanie
local function open(id: string)
	local s = SKLEPY[id]
	if not s then
		return
	end
	otwarte = id
	zamykanie = false
	strona = 0
	schowajKarte()
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	miejsceOtwarcia = root and root.Position or nil
	for _, k in pairs(SKLEPY) do
		panel[k.art].Visible = k == s
	end
	panel.TitleRight.Text = s.tytul
	rysujPoziom()
	rysujEkwipunek()
	rysujTowar()
	rysujTabliczke()
	gui.Enabled = true
	backdrop.BackgroundTransparency = 1
	TS:Create(backdrop, TweenInfo.new(0.2), { BackgroundTransparency = 0.45 }):Play()
	panelScale.Scale = 0.8
	TS:Create(panelScale, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	if s.towar then
		-- tymczasowe okno Karola otwiera się na to samo E: zamykamy je (kolejność słuchaczy jest nieustalona)
		task.spawn(function()
			for _ = 1, 4 do
				zamknijOknoKarola()
				task.wait(0.1)
			end
		end)
		task.spawn(prosba, "oferta")
	end
end

local function close()
	if zamykanie or not gui.Enabled then
		return
	end
	zamykanie = true
	otwarte = nil
	schowajKarte()
	TS:Create(backdrop, TweenInfo.new(0.15), { BackgroundTransparency = 1 }):Play()
	local t = TS:Create(panelScale, TweenInfo.new(0.15, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.85 })
	t.Completed:Connect(function()
		if zamykanie then
			gui.Enabled = false
		end
	end)
	t:Play()
end

okna.Event:Connect(function(id)
	if typeof(id) == "string" and SKLEPY[id] then
		open(id)
	end
end)

------------------------------------------------------------ przyciski
-- przyciski wypalone w grafice: cień przy najechaniu / wciśnięciu
local function hitButton(btn: GuiButton, onClick: () -> ())
	local shade = Instance.new("Frame")
	shade.Name = "Shade"
	shade.Size = UDim2.fromScale(1, 1)
	shade.BackgroundColor3 = Color3.new(0, 0, 0)
	shade.BackgroundTransparency = 1
	shade.BorderSizePixel = 0
	shade.ZIndex = btn.ZIndex + 5
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0.2, 0)
	c.Parent = shade
	shade.Parent = btn
	btn.MouseEnter:Connect(function()
		TS:Create(shade, QUICK, { BackgroundTransparency = 0.85 }):Play()
	end)
	btn.MouseLeave:Connect(function()
		TS:Create(shade, QUICK, { BackgroundTransparency = 1 }):Play()
	end)
	btn.MouseButton1Down:Connect(function()
		TS:Create(shade, QUICK, { BackgroundTransparency = 0.7 }):Play()
	end)
	btn.Activated:Connect(function()
		TS:Create(shade, QUICK, { BackgroundTransparency = 1 }):Play()
		onClick()
	end)
end

hitButton(panel:WaitForChild("CloseButton"), close)
hitButton(panel:WaitForChild("RerollButton"), function()
	strona += 1
	schowajKarte()
	rysujTowar()
end)
for i = 1, 6 do
	local s = panel:FindFirstChild("ShopSlot" .. i)
	if s then
		hitButton(s, function()
			local w = naLadzie[i]
			if w then
				pokazKarte(w, false)
			else
				schowajKarte()
			end
		end)
	end
end
card.BuyButton.Activated:Connect(function()
	local w = wybrany
	if not w then
		return
	end
	if w.stan == "kup" then
		prosba("kup", w.id)
	elseif w.stan == "masz" then
		prosba("zaloz", w.id)
	elseif w.stan == "za_drogie" then
		komunikat("NOT ENOUGH GOLD", true)
	elseif w.stan == "za_niski_poziom" then
		komunikat("NEED LV " .. tostring(w.poziom), true)
	end
end)
card.CloseCard.Activated:Connect(schowajKarte)

-- lewa strona: zakładki i podgląd przedmiotu (bez przeciągania — przekłada się w oknie ekwipunku)
for _, nazwa in ipairs(ZAKLADKI) do
	local t = panel.Tabs:FindFirstChild("Tab" .. nazwa)
	if t then
		t.Activated:Connect(function()
			zakladka = nazwa
			rysujEkwipunek()
		end)
	end
end
local function podgladPrzedmiotu(id: string?)
	local d = Stan.definicja(id)
	if not d then
		schowajKarte()
		return
	end
	pokazKarte({ nazwa = d.name, stopien = d.stopien, poziomUlepszenia = d.poziom, staty = "" }, true)
end
for _, s in ipairs(equipFolder:GetChildren()) do
	if s:IsA("GuiButton") then
		hitButton(s, function()
			podgladPrzedmiotu(Stan.equip[s.Name])
		end)
	end
end
for i = 1, SLOTY_PLECAKA do
	local s = bagFolder:FindFirstChild(string.format("BagSlot%02d", i))
	if s then
		hitButton(s, function()
			podgladPrzedmiotu(Stan.bag[zakladka][i])
		end)
	end
end

backdrop.Activated:Connect(close)
UIS.InputBegan:Connect(function(input, processed)
	if not processed and gui.Enabled and input.KeyCode == Enum.KeyCode.Escape then
		close()
	end
end)

-- odejście od miejsca otwarcia zamyka okno
local licznik = 0
RunService.Heartbeat:Connect(function(dt)
	if not (gui.Enabled and otwarte and miejsceOtwarcia) then
		return
	end
	licznik += dt
	if licznik < 0.25 then
		return
	end
	licznik = 0
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if root and (root.Position - miejsceOtwarcia).Magnitude > ZASIEG_OKNA then
		close()
	end
end)

-- przedmioty kupione wcześniej (zapis kowala) pojawiają się w EQ od wejścia do gry, nie dopiero po otwarciu sklepu
task.spawn(function()
	while not player:GetAttribute("Class") do
		player:GetAttributeChangedSignal("Class"):Wait()
	end
	local k = workspace:WaitForChild("SklepProba", 30)
	if k and k:WaitForChild("Zdalne", 10) then
		task.wait(2)
		prosba("oferta")
	end
end)

------------------------------------------------------------ kliknięcie na sprzedawcę
local function sklepZModelu(inst: Instance?): string?
	local bazar = workspace:FindFirstChild("MiasteczkoBazar")
	if not (inst and bazar) then
		return nil
	end
	for id, s in pairs(SKLEPY) do
		local b = bazar:FindFirstChild(s.budynek)
		local m = b and b:FindFirstChild(s.model)
		if m and inst:IsDescendantOf(m) then
			return id
		end
	end
	return nil
end

local function kliknij(pos: Vector2)
	if gui.Enabled then
		return
	end
	local cam = workspace.CurrentCamera
	local ray = cam:ScreenPointToRay(pos.X, pos.Y) -- pozycja z InputObject jest bez paska u góry
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { player.Character }
	local hitR = workspace:Raycast(ray.Origin, ray.Direction * 200, params)
	local id = hitR and sklepZModelu(hitR.Instance)
	if not id then
		return
	end
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if root and (root.Position - hitR.Position).Magnitude <= ZASIEG_KLIKU then
		open(id)
	end
end

UIS.InputEnded:Connect(function(input, processed)
	if processed then
		return
	end
	local t = input.UserInputType
	if t == Enum.UserInputType.MouseButton1 or t == Enum.UserInputType.Touch then
		kliknij(Vector2.new(input.Position.X, input.Position.Y))
	end
end)
