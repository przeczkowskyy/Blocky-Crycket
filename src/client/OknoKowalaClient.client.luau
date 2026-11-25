--!strict
--[[
	OknoKowalaClient — nowe okno kowala (Paweł 24.11: grafika z jednej generacji, „żeby było klikane i coś robiło”).
	Grafika: src/gui/OknoKowala (tools/okna_build_gui.py). Logika jest Karola (swiat/kowal_proba, D-102):
	Workspace/KowalProba/Zdalne/Kuznia (RemoteFunction) — "widok" | "ulepsz", id | "rozbierz", id; serwer liczy
	wszystko (koszt, materiały, Złoto/Rybki, odległość), klient tylko pokazuje i wysyła akcję.

	Otwieranie: E przy kowalu (KowalProba/Kuznia/E/Podpowiedz) — jego tymczasowe okno „KUŹNIA · PRÓBA” zamykamy jego
	haczykiem Sygnaly/SterowanieKlienta "zamknij" (jak przy sklepie). Bez zmian w plikach Karola.
	Lewa strona: przedmioty klasy (posiadane jasne, nieposiadane przygaszone; „+N” poziom, „xN” zapas do rozbiórki).
	Środek: przedmiot przed / po ulepszeniu, statystyki na pergaminie, kółka (poziom, materiały, zapas), cena,
	przyciski ULEPSZ (młotek) i ROZBIERZ (kowadło). Okno otwiera się od razu, bez wjazdu.

	Zakładki nad górną siatką (Paweł 25.11, prośba Karola o panel na składniki): ITEMS — przedmioty jak dotąd;
	INGREDIENTS — składniki kuźni w tych samych 12 polach. Serwer Karola zna dziś jeden składnik (materiały
	z rozbiórki, „widok.materialy”); lista SKLADNIKI niżej jest gotowa na kolejne, gdy pojawią się w „widoku”.
]]

local Players = game:GetService("Players")
local UIS = game:GetService("UserInputService")
local TS = game:GetService("TweenService")

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("OknoKowala") :: ScreenGui
local panel = gui:WaitForChild("Panel") :: Frame

local stats = panel:WaitForChild("Stats") :: TextLabel
local priceL = panel:WaitForChild("Price") :: TextLabel
local msg = panel:WaitForChild("Message") :: TextLabel
local matL = panel:WaitForChild("Materials") :: TextLabel
local before = panel:WaitForChild("Before") :: Frame
local after = panel:WaitForChild("After") :: Frame
local c1 = panel:WaitForChild("Circle1") :: TextLabel
local c2 = panel:WaitForChild("Circle2") :: TextLabel
local c3 = panel:WaitForChild("Circle3") :: TextLabel
local upBtn = panel:WaitForChild("UpgradeButton") :: GuiButton
local scrapBtn = panel:WaitForChild("ScrapButton") :: GuiButton
local upLbl = panel:WaitForChild("UpgradeLabel") :: TextLabel
local scrapLbl = panel:WaitForChild("ScrapLabel") :: TextLabel

local SLOTOW = 21
local GORNYCH = 12 -- pola górnej siatki: przedmioty 1–12 albo składniki (zakładki)
local tabItems = panel:WaitForChild("TabItems") :: TextButton
local tabIngr = panel:WaitForChild("TabIngredients") :: TextButton
local zakladka = "items" -- "items" | "ingredients"
local wybranySkladnik: number? = nil
local IKONA_ZLOMU = "rbxassetid://119371548847065" -- ItemScrap (assets/manifest.json)
local widok: any = nil
local wybrany: string? = nil
local otwarte, czeka = false, false
local miejsceOtwarcia: Vector3? = nil

local function kowalProba(): Instance?
	return workspace:FindFirstChild("KowalProba")
end

local function kuznia(): RemoteFunction?
	local k = kowalProba()
	local z = k and k:FindFirstChild("Zdalne")
	local f = z and z:FindFirstChild("Kuznia")
	return if f and f:IsA("RemoteFunction") then f else nil
end

-- teksty serwera Karola mówią o Złocie; waluta to Rybki (D-146)
local function rybki(s: string?): string
	if type(s) ~= "string" then
		return ""
	end
	s = s:gsub("Złota", "Rybek"):gsub("Złoto", "Rybki"):gsub("złota", "rybek"):gsub("złoto", "rybki")
	return s
end

local function krotka(nazwa: string): string
	-- w małym slocie mieści się ok. 2 słowa
	local slowa = {}
	for w in nazwa:gmatch("%S+") do
		table.insert(slowa, w)
		if #slowa == 2 then
			break
		end
	end
	return table.concat(slowa, " ")
end

local function liczba(s: any): string
	if type(s) ~= "string" then
		return ""
	end
	return s:match("%d+") or ""
end

local function wiersz(id: string?): any
	if not widok or not id then
		return nil
	end
	for _, w in ipairs(widok.wiersze) do
		if w.id == id then
			return w
		end
	end
	return nil
end

local function przycisk(b: GuiButton, l: TextLabel, wlaczony: boolean)
	b.Active = wlaczony
	l.TextTransparency = if wlaczony then 0 else 0.55
end

-- składniki kuźni z „widoku” serwera; kolejne dojdą tu, gdy serwer Karola zacznie je podawać
local function skladniki(): { { nazwa: string, ile: string, ikona: string, opis: string } }
	if not widok then
		return {}
	end
	return {
		{
			nazwa = "Scrap", ile = liczba(widok.materialy), ikona = IKONA_ZLOMU,
			opis = "Scrap\nUsed for every upgrade.\nGet it by scrapping spare items (SCRAP button).",
		},
	}
end

local function rysujZakladki()
	for b, aktywna in pairs({ [tabItems] = zakladka == "items", [tabIngr] = zakladka == "ingredients" }) do
		b.BackgroundColor3 = if aktywna then Color3.fromRGB(242, 179, 61) else Color3.fromRGB(107, 66, 38)
		b.TextColor3 = if aktywna then Color3.new(1, 1, 1) else Color3.fromRGB(252, 227, 176)
	end
end

local function rysujSrodek()
	if zakladka == "ingredients" then
		local s = wybranySkladnik and skladniki()[wybranySkladnik]
		for _, f in ipairs({ before, after }) do
			(f:FindFirstChild("ItemName") :: TextLabel).Text = "";
			(f:FindFirstChild("Lvl") :: TextLabel).Text = ""
		end
		stats.Text = if s then s.opis .. "\nYou have: " .. s.ile else "Pick an ingredient on the left"
		priceL.Text, c1.Text, c3.Text = "", "", ""
		przycisk(upBtn, upLbl, false)
		przycisk(scrapBtn, scrapLbl, false)
		return
	end
	local w = wiersz(wybrany)
	if not w then
		for _, f in ipairs({ before, after }) do
			(f:FindFirstChild("ItemName") :: TextLabel).Text = "";
			(f:FindFirstChild("Lvl") :: TextLabel).Text = ""
		end
		stats.Text = "Pick an item on the left"
		priceL.Text, c1.Text, c3.Text = "", "", ""
		przycisk(upBtn, upLbl, false)
		przycisk(scrapBtn, scrapLbl, false)
		return
	end;
	(before:FindFirstChild("ItemName") :: TextLabel).Text = krotka(w.nazwa);
	(before:FindFirstChild("Lvl") :: TextLabel).Text = if w.posiadany then "+" .. w.poziom else "—";
	(after:FindFirstChild("ItemName") :: TextLabel).Text = krotka(w.nazwa);
	(after:FindFirstChild("Lvl") :: TextLabel).Text = if w.posiadany and w.nastepny ~= "" and w.koszt ~= "" then "+" .. (w.poziom + 1) else ""
	local linie = { w.nazwa .. (if w.zalozony then " (equipped)" else ""), rybki(w.staty) }
	if w.nastepny ~= "" then
		table.insert(linie, rybki(w.nastepny))
	end
	if w.powod ~= "" then
		table.insert(linie, rybki(w.powod))
	end
	if w.rozbiorka ~= "" then
		table.insert(linie, rybki(w.rozbiorka))
	end
	stats.Text = table.concat(linie, "\n")
	priceL.Text = rybki(w.koszt)
	c1.Text = if w.posiadany then "+" .. w.poziom else "-"
	c3.Text = if w.posiadany then "x" .. w.zapas else "-"
	przycisk(upBtn, upLbl, w.ulepsz == true)
	przycisk(scrapBtn, scrapLbl, w.rozbierz == true)
end

local function rysuj()
	if not widok then
		return
	end
	matL.Text = rybki(widok.zloto or "")
	c2.Text = liczba(widok.materialy)
	for i = 1, SLOTOW do
		local s = panel:FindFirstChild(string.format("Item%02d", i)) :: ImageButton
		local w = widok.wiersze[i]
		s.Visible = w ~= nil and (i > GORNYCH or zakladka == "items")
		if w then
			(s:FindFirstChild("ItemName") :: TextLabel).Text = krotka(w.nazwa);
			(s:FindFirstChild("ItemName") :: TextLabel).TextTransparency = if w.posiadany then 0 else 0.5;
			(s:FindFirstChild("Lvl") :: TextLabel).Text = if w.posiadany then "+" .. w.poziom else "";
			(s:FindFirstChild("Spare") :: TextLabel).Text = if w.posiadany and w.zapas > 0 then "x" .. w.zapas else "";
			(s:FindFirstChild("Select") :: Frame).Visible = w.id == wybrany and zakladka == "items"
		end
	end
	local lista = skladniki()
	for i = 1, GORNYCH do
		local s = panel:FindFirstChild(string.format("Ingredient%02d", i)) :: ImageButton
		local d = lista[i]
		s.Visible = zakladka == "ingredients" and d ~= nil
		if d then
			(s:FindFirstChild("Icon") :: ImageLabel).Image = d.ikona;
			(s:FindFirstChild("ItemName") :: TextLabel).Text = d.nazwa;
			(s:FindFirstChild("Count") :: TextLabel).Text = "x" .. d.ile;
			(s:FindFirstChild("Select") :: Frame).Visible = wybranySkladnik == i
		end
	end
	rysujZakladki()
	rysujSrodek()
end

local function zapytaj(akcja: string, id: string?): any
	local f = kuznia()
	if not f then
		msg.Text = "Smithy is closed (no KowalProba)"
		return nil
	end
	local ok, w = pcall(function()
		return f:InvokeServer(akcja, id)
	end)
	if not ok or type(w) ~= "table" then
		msg.Text = "…"
		return nil
	end
	if w.widok then
		widok = w.widok
	end
	if w.tekst then
		msg.Text = rybki(w.tekst)
	end
	return w
end

local function blysk(f: GuiObject)
	local sc = f:FindFirstChildWhichIsA("UIScale") or Instance.new("UIScale")
	sc.Parent = f
	sc.Scale = 1.25
	TS:Create(sc, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

local function akcja(nazwa: string)
	if czeka or not wybrany then
		return
	end
	czeka = true
	local w = zapytaj(nazwa, wybrany)
	if w and w.ok then
		blysk(if nazwa == "ulepsz" then after else c2)
	end
	rysuj()
	czeka = false
end

local function otworz()
	if otwarte then
		return
	end
	otwarte = true
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	miejsceOtwarcia = root and root.Position or nil
	msg.Text = ""
	zakladka = "items" -- okno zawsze zaczyna od przedmiotów
	gui.Enabled = true
	-- jego tymczasowe okno otwiera się na to samo E — zamykamy je (kolejność słuchaczy nieustalona)
	task.spawn(function()
		for _ = 1, 3 do
			task.wait(0.05)
			local k = kowalProba()
			local s = k and k:FindFirstChild("Sygnaly")
			local f = s and s:FindFirstChild("SterowanieKlienta")
			if f and f:IsA("BindableFunction") then
				pcall(function()
					f:Invoke("zamknij")
				end)
			end
		end
	end)
	-- jego okno pyta serwer w tej samej chwili, a serwer ma limit jednego zapytania na D.limit s — ponawiamy
	local w = zapytaj("widok")
	for _ = 1, 4 do
		if w and w.powod ~= "za_szybko" then
			break
		end
		task.wait(0.6)
		w = zapytaj("widok")
	end
	if w and w.ok then
		msg.Text = ""
	end
	if w and widok and not wiersz(wybrany) then
		wybrany = if widok.wiersze[1] then widok.wiersze[1].id else nil
	end
	rysuj()
end

local function zamknij()
	if not otwarte then
		return
	end
	otwarte = false
	gui.Enabled = false
end

for i = 1, SLOTOW do
	local s = panel:WaitForChild(string.format("Item%02d", i)) :: ImageButton
	s.Activated:Connect(function()
		local w = widok and widok.wiersze[i]
		if w then
			wybrany = w.id
			rysuj()
		end
	end)
end
for i = 1, GORNYCH do
	local s = panel:WaitForChild(string.format("Ingredient%02d", i)) :: ImageButton
	s.Activated:Connect(function()
		if skladniki()[i] then
			wybranySkladnik = i
			rysuj()
		end
	end)
end
local function ustawZakladke(nazwa: string)
	if zakladka ~= nazwa then
		zakladka = nazwa
		if nazwa == "ingredients" and not wybranySkladnik and skladniki()[1] then
			wybranySkladnik = 1
		end
		rysuj()
	end
end
tabItems.Activated:Connect(function()
	ustawZakladke("items")
end)
tabIngr.Activated:Connect(function()
	ustawZakladke("ingredients")
end)
upBtn.Activated:Connect(function()
	akcja("ulepsz")
end)
scrapBtn.Activated:Connect(function()
	akcja("rozbierz")
end);
(panel:WaitForChild("CloseButton") :: GuiButton).Activated:Connect(zamknij);
(gui:WaitForChild("Backdrop") :: GuiButton).Activated:Connect(zamknij)
UIS.InputBegan:Connect(function(input)
	if otwarte and input.KeyCode == Enum.KeyCode.Escape then
		zamknij()
	end
end)

-- E przy kowalu (podpowiedź włącza serwer Karola w Play)
task.spawn(function()
	local k = workspace:WaitForChild("KowalProba", 60)
	local e = k and k:WaitForChild("Kuznia", 30)
	e = e and e:WaitForChild("E", 30)
	local pp = e and e:WaitForChild("Podpowiedz", 30)
	if pp and pp:IsA("ProximityPrompt") then
		pp.Triggered:Connect(otworz)
	end
end)

task.spawn(function()
	while true do
		task.wait(0.5)
		if otwarte then
			local char = player.Character
			local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
			if root and miejsceOtwarcia and (root.Position - miejsceOtwarcia).Magnitude > 14 then
				zamknij()
			end
		end
	end
end)
