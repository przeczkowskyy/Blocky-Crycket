--[[
	InterfejsWalki2 — interfejs walki v2, tworzony w czasie działania w PlayerGui (nic w StarterGui). Wzór: v1
	(swiat/test_walki_roblox/zrodla/InterfejsWalki.luau) — ten sam komiksowy styl, kadr 16:9 z czarnymi pasami,
	paski życia z „duchem”, komiksowe napisy nad postaciami, baner, „POMIŃ”, panel wyniku z odliczaniem.

	Nowe w v2:
		• tabliczki z nazwą, poziomem i rangą przeciwnika, portret z pikseli dla każdego aktora;
		• pod paskiem ikony aktywnych efektów z licznikiem tur (i zapasem tarczy);
		• licznik tury pod „VS”, wstęga z nazwą użytej umiejętności;
		• przyciski tempa ×1 / ×2 / ×4 (wybór gracza, D-068) obok „POMIŃ” — duże, czytelne na telefonie;
		• panel wyniku z łupem z dziennika: Złoto, doświadczenie, tokeny krainy, Gem, Shard Ewolucji.

	Użycie: local ui = InterfejsWalki2.nowy(playerGui, Ustawienia) … ui:zniszcz()
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")
local ContextActionService = game:GetService("ContextActionService")

local Interfejs = {}
-- spacja (albo B na padzie) zamyka kartę wyniku; priorytet nad „POMIŃ” odtwarzacza (10001), który w tej fazie nic nie robi
local AKCJA_ZAMKNIJ_WYNIK = "TestWalki2ZamknijWynik"
local ZAMKNIJ_WYNIK_PO = 0.6 -- s od pokazania karty: podwójna spacja po POMIŃ nie zamknie jej, zanim gracz zobaczy łup
-- podpis kafla tokenów z krainy walki (walka.lup.kraina z danych przeciwnika); nieznana kraina → „TOKENY”
local NAPISY_TOKENOW = { las = "TOKENY LASU", bagno = "TOKENY BAGNA" }
Interfejs.__index = Interfejs

local PROPORCJE = 16 / 9
local WYS_ODNIESIENIA = 720
local kontener = script.Parent.Parent -- Workspace/TestWalki2

--[[ Emulacja ekranu telefonu (tylko testy): atrybut kontenera EmulacjaEkranu = Vector2 (rozmiar ekranu w punktach,
	np. 844 × 390 — telefon w poziomie). Interfejs układa się wtedy w prostokącie o tych proporcjach na środku okna
	(pomniejszonym, gdy okno Studio jest mniejsze), a kamera kadruje tak, jak na tym ekranie. Zrzut tego prostokąta
	pokazuje układ jak na telefonie; wielkość napisów w punktach = piksele ÷ skalaEmulacji. ]]
function Interfejs.ekran(): (number, number, number, number, number)
	local okno = workspace.CurrentCamera.ViewportSize
	local em = kontener:GetAttribute("EmulacjaEkranu")
	if typeof(em) == "Vector2" and em.X > 0 and em.Y > 0 then
		local f = math.min(1, okno.X / em.X, okno.Y / em.Y)
		local sz, wys = em.X * f, em.Y * f
		return (okno.X - sz) / 2, (okno.Y - wys) / 2, sz, wys, f
	end
	return 0, 0, okno.X, okno.Y, 1
end
local NAGLOWKI = Enum.Font.LuckiestGuy
local KOMIKS = Enum.Font.Bangers

------------------------------------------------------------------ ikony z pikseli (8 × 8)
local IKONY = {
	wojownik = {
		paleta = { S = "#C9D2DE", s = "#8E99AB", R = "#E0413A", D = "#20242B", B = "#2F6FE0", O = "#8FF6FF" },
		mapa = { "..RRR...", ".SSSSSR.", "SSSSSSSR", "SDODDODS", "SSSsSSSS", "sSSsSSSs", ".sSSSSs.", "..BBBB.." },
	},
	zwiadowca = {
		paleta = { G = "#1F5A36", g = "#2A7A48", D = "#17121F", W = "#FFFFFF", C = "#F2C9A0" },
		mapa = { "...Gg...", "..GGGg..", ".GGGGGG.", "GGDDDDGG", "GDWDDWDG", "GGCCCCGG", ".GCCCCG.", "..gggg.." },
	},
	mag = {
		paleta = { P = "#7B4DFF", Y = "#FFD23F", O = "#FF9A2E", K = "#17121F", W = "#FFFFFF" },
		mapa = { "...PP...", "..PYPP..", ".PPPPPP.", "PPPPPPPP", ".OOOOOO.", ".OKOOKO.", ".OOWWOO.", "..OOOO.." },
	},
	-- Leśny Slime: kostka galarety z kiełkiem, duże oczy z błyskiem, rumieńce (swiat/postacie/lesny_slime.py)
	lesny_slime = {
		paleta = { G = "#7EDB57", g = "#5CB842", K = "#17121F", W = "#FAFFF0", R = "#FF8DA1", L = "#A6E34F" },
		mapa = { "...LL...", "GGGGGGGG", "GGGGGGGG", "GKWGGKWG", "GKKGGKKG", "RGGGGGGR", "GGGKKGGG", "gggggggg" },
	},
	cierniowy_wilk = {
		paleta = { D = "#4A4252", A = "#FFB52E", B = "#17121F", W = "#FFFFFF", G = "#4CB443" },
		mapa = { "D......D", "DD.GG.DD", "DDDDDDDD", "DADDDDAD", "DDDDDDDD", ".DDBBDD.", "..DWWD..", "...DD..." },
	},
	muchomornik = {
		paleta = { R = "#E5482F", W = "#FFFFFF", C = "#F2EBDC", K = "#17121F", G = "#4E9E3C" },
		mapa = { "..RRRR..", ".RWRRWR.", "RRRRRRRR", "RWRRRWRR", "..CCCC..", "..KCCK..", "..CGGC..", "...GG..." },
	},
	lesny_troll = {
		paleta = { g = "#4E9E3C", B = "#86704F", Y = "#FFE14A", K = "#17121F", T = "#FFFFFF" },
		mapa = { "..gggg..", ".BBBBBB.", "BBBBBBBB", "BBYBBYBB", "BBBBBBBB", "BTBBBBTB", "BBKKKKBB", ".BBBBBB." },
	},
	-- Strażnik Gaju: kamienna głowa, korona z gałęzi, zielone oczy, broda z korzonków (swiat/postacie/straznik_gaju.py)
	straznik_lasu = {
		paleta = { M = "#7DAE3C", B = "#8E5B32", S = "#858074", s = "#57524C", G = "#36EE4E", K = "#2B2428" },
		mapa = { "M.B..B.M", ".BMBBMB.", "SSSSSSSS", "SsGSSGsS", "SSSSSSSS", "SSsKKsSS", "SBSBBSBS", ".B.BB.B." },
	},
	-- przeciwnicy Bagna (17.11.2026, swiat/bagno_pas_gra; modele swiat/postacie/<klucz>.py)
	-- Rechotek: oliwkowa ropucha, pomarańczowe oczy na czubku, czarna linia ust, żółty brzuch
	rechotek = {
		paleta = { G = "#7E8C3E", g = "#4F5E2A", O = "#F2932E", K = "#17121F", Y = "#E8D27A" },
		mapa = { ".OO..OO.", "OKOGGOKO", "GGGGGGGG", "GgGGGGgG", "KKKKKKKK", "GYYYYYYG", "GYYYYYYG", ".gggggg." },
	},
	-- Bulgotnik: zielona bańka-głowa z oczami, błotny kopczyk, ognik na kiju
	bulgotnik = {
		paleta = { B = "#9FD89A", b = "#6FB86A", K = "#17121F", M = "#5B4A34", m = "#3E3122", Y = "#C8E05A" },
		mapa = { "..bbbb.Y", ".bBBBBbY", ".bKBBKbM", ".bBBBBbM", "..bbbb.M", ".MMMMMMM", "MMmMMmMM", ".mm..mm." },
	},
	-- Kłodokłap: kłoda z mchem, bursztynowe oczy, paszcza z kołkami-zębami, korzenie
	klodoklap = {
		paleta = { L = "#6B4F33", l = "#4A3624", A = "#A9B48E", W = "#F2E6C8", K = "#17121F", Y = "#FFB52E" },
		mapa = { "AAAAAAAA", "LLYLLYLL", "LLLLLLLL", "LWLWWLWL", "KKKKKKKK", "LWLWWLWL", "lLLLLLLl", "l.l..l.l" },
	},
	-- Ropucha z Chatką: chatka z kominem i świecącym okienkiem na grzbiecie ropuchy
	ropucha_z_chatka = {
		paleta = { D = "#9C7A4A", R = "#5E7A3A", S = "#8D949C", W = "#E6E6E6", Y = "#FFD27A", G = "#5E6B2E",
			O = "#F2932E", K = "#17121F" },
		mapa = { ".....SW.", "..RRRS..", ".RRRRRR.", "..DYDD..", "GGDDDDGG", "GOGGGGOG", "GKKKKKKG", ".GG..GG." },
	},
	-- Strażnik Topieli: przewrócona łódka jak kapelusz, zielone oczy, latarnia w piersi, broda z mchu
	straznik_topieli = {
		paleta = { T = "#2EB8A6", B = "#7A5A36", M = "#5B4A34", G = "#C8E05A", E = "#36EE4E", A = "#A9B48E" },
		mapa = { ".BBBBBB.", "BTTTTTTB", ".MMMMMM.", "MEMMMMEM", "MMMMMMMM", "MAAGGAAM", "MAAGGAAM", ".A.AA.A." },
	},
	-- efekty
	trucizna = {
		paleta = { G = "#8BEA4E", g = "#3E8C2A", L = "#E8FFD0" },
		mapa = { "...GG...", "..GGGG..", ".GGLGGG.", ".GLGGGG.", "GGGGGGGG", "GGGGGGgG", ".GGGGgG.", "..gggg.." },
	},
	ogien = {
		paleta = { R = "#E8364F", O = "#FF8A1F", Y = "#FFD23F", W = "#FFF3B0" },
		mapa = { "...R....", "..RR..R.", "..ROR.RR", ".RROORRR", "RROYYORR", "ROYYYYOR", "ROYWWYOR", ".RRRRRR." },
	},
	kropla = {
		paleta = { R = "#FF2E45", r = "#9E1020", L = "#FFC0C8" },
		mapa = { "...RR...", "..RRRR..", ".RRLRRR.", ".RLRRRR.", "RRRRRRRR", "RRRRRRrR", ".RRRRrR.", "..rrrr.." },
	},
	gwiazdki = {
		paleta = { Y = "#FFE14A", B = "#7FD8FF", W = "#FFFFFF" },
		mapa = { "...Y....", "..YYY...", "YYYYYYY.", ".YYWYY..", ".YY.YY..", "Y.....B.", "....BBB.", ".....B.." },
	},
	-- v3: spowolnienie (płatek śniegu — inne niż gwiazdki ogłuszenia), wskrzeszenie (złote pióro), mana (kryształ)
	sniezynka = {
		paleta = { B = "#7FD8FF", W = "#FFFFFF", b = "#2E9BD6" },
		mapa = { "...W....", ".B.W.B..", "..BWB...", "WWWBWWW.", "..BWB...", ".B.W.B..", "...W....", "..b.b..." },
	},
	feniks = {
		paleta = { Y = "#FFD23F", O = "#FF8A1F", W = "#FFF3B0", R = "#E8364F" },
		mapa = { ".....WY.", "....WYY.", "...WYYO.", "..WYYO..", ".WYYOR..", ".YYOR...", "YOR.....", "R......." },
	},
	mana = {
		paleta = { B = "#4FA8FF", b = "#1F5FD0", W = "#E6F4FF", D = "#14306E" },
		mapa = { "...DD...", "..DWBD..", ".DWBBbD.", "DWBBBBbD", "DBBBBBbD", ".DBBBbD.", "..DBbD..", "...DD..." },
	},
	-- zapowiedź pasywki broni (v3)
	bron = {
		paleta = { S = "#DDE3EA", s = "#8E99AB", B = "#8A5A0A", Y = "#FFD23F" },
		mapa = { ".......S", "......Ss", ".....Ss.", "....Ss..", "Y..Ss...", ".YBs....", "..BY....", ".B..Y..." },
	},
	pancerz = {
		paleta = { S = "#B9BEC4", s = "#8D949C", K = "#17121F", O = "#D9A066" },
		mapa = { "SSSSSSSS", "SSSKSSSs", "SSSSKSSs", "SSSKSSSs", ".SSSKSs.", ".SSKSSs.", "..SSSs..", "...OO..." },
	},
	kamien = {
		paleta = { S = "#A9AFB6", s = "#646B73", W = "#E3E7EC" },
		mapa = { "SSSSSSSS", "SWWSSSSs", "SWSSSSSs", "SSSSSSSs", ".SSSSSs.", ".SSSSss.", "..SSss..", "...ss..." },
	},
	banka = {
		paleta = { B = "#6FE3FF", b = "#27B6F2", W = "#FFFFFF" },
		mapa = { "..bbbb..", ".bBBBBb.", "bBWWBBBb", "bBWBBBBb", "bBBBBBBb", "bBBBBBBb", ".bBBBBb.", "..bbbb.." },
	},
	oko = {
		paleta = { Y = "#FFD23F", y = "#E79A12", K = "#17121F", W = "#FFFFFF" },
		mapa = { "........", "..YYYY..", ".YWWWWY.", "YWWKKWWY", "YWKKKKWY", ".YWWWWY.", "..YYYY..", "........" },
	},
	-- przycisk dźwięku: głośnik i głośnik z czerwonym krzyżykiem (wyciszone)
	glosnik = {
		paleta = { W = "#FFFFFF", Y = "#FFD23F" },
		mapa = { "....W...", "...WW.Y.", "WWWWW..Y", "WWWWW..Y", "WWWWW..Y", "WWWWW..Y", "...WW.Y.", "....W..." },
	},
	cisza = {
		paleta = { W = "#C9CED6", R = "#E8364F" },
		mapa = { "....W...", "...WW...", "WWWWWR.R", "WWWWW.R.", "WWWWWR.R", "WWWWW...", "...WW...", "....W..." },
	},
	-- łup
	moneta = {
		paleta = { Y = "#FFD23F", O = "#E79A12", W = "#FFF3B0", D = "#8A5A0A" },
		mapa = { "..DDDD..", ".DYYYYD.", "DYWYYYOD", "DYWYOYOD", "DYYYOYOD", "DYYYYYOD", ".DOOOOD.", "..DDDD.." },
	},
	gwiazda = {
		paleta = { P = "#7B4DFF", p = "#B79BFF", D = "#2B1A66" },
		mapa = { "...DD...", "..DpPD..", "DDDpPDDD", "DpppPPPD", ".DpPPPD.", ".DpPPPD.", "DpPDDPPD", "DDD..DDD" },
	},
	zeton = {
		paleta = { G = "#52D273", D = "#1F5A36", L = "#A8F07A" },
		mapa = { "..DDDD..", ".DGGGGD.", "DGGLLGGD", "DGLLLLGD", "DGGLLGGD", "DGGGLGGD", ".DGGGGD.", "..DDDD.." },
	},
	gem = {
		paleta = { P = "#C04DFF", p = "#F0C8FF", D = "#5A1A8A" },
		mapa = { "........", ".DDDDDD.", "DppPPPPD", "DpPPPPPD", ".DPPPPD.", "..DPPD..", "...DD...", "........" },
	},
	shard = {
		paleta = { C = "#49D6F2", c = "#E8FBFF", D = "#1A5A7A" },
		mapa = { "...DD...", "..DcCD..", "..DcCD..", ".DcCCCD.", ".DcCCCD.", ".DCCCCD.", "..DCCD..", "...DD..." },
	},
}
Interfejs.IKONY = IKONY

------------------------------------------------------------------ pomocnicze
-- wielkie litery z polskimi znakami: string.upper zmienia tylko ASCII („Strażnik Gaju” → „STRAżNIK GAJU”,
-- zauważone w Studio 17.11.2026); nazwy z Dane są w UTF-8
local POLSKIE_WIELKIE = { { "ą", "Ą" }, { "ć", "Ć" }, { "ę", "Ę" }, { "ł", "Ł" }, { "ń", "Ń" }, { "ó", "Ó" },
	{ "ś", "Ś" }, { "ź", "Ź" }, { "ż", "Ż" } }
local function wielkie(tekst: string): string
	local t = string.upper(tekst)
	for _, para in POLSKIE_WIELKIE do
		t = string.gsub(t, para[1], para[2])
	end
	return t
end
Interfejs.wielkie = wielkie

local function gladko(x: number): number
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end

function Interfejs:_nowy(klasa: string, wlasciwosci: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in wlasciwosci do
		o[k] = v
	end
	o.Parent = rodzic
	self.utworzono += 1
	return o
end

function Interfejs:_obrys(obiekt: GuiObject, px: number, kolor: Color3?): UIStroke
	local jestTekstem = obiekt:IsA("TextLabel") or obiekt:IsA("TextButton")
	local s = self:_nowy("UIStroke", {
		Color = kolor or self.K.tusz,
		Thickness = px,
		LineJoinMode = Enum.LineJoinMode.Round,
		ApplyStrokeMode = if jestTekstem then Enum.ApplyStrokeMode.Contextual else Enum.ApplyStrokeMode.Border,
	}, obiekt)
	self.obrysy[s] = px
	s.Thickness = math.max(1, px * self.skalaObrysu)
	return s
end

function Interfejs:_rog(obiekt: GuiObject, ulamek: number)
	return self:_nowy("UICorner", { CornerRadius = UDim.new(ulamek, 0) }, obiekt)
end

function Interfejs:_ikona(rodzic: GuiObject, nazwa: string, margines: number?)
	local def = IKONY[nazwa] or IKONY.oko
	local m = margines or 0.12
	local pole = self:_nowy("Frame", {
		Name = "Ikona", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromScale(1 - 2 * m, 1 - 2 * m), ZIndex = rodzic.ZIndex + 1,
	}, rodzic)
	self:_nowy("UIAspectRatioConstraint", { AspectRatio = 1 }, pole)
	for y, wiersz in def.mapa do
		local x = 1
		while x <= 8 do
			local znak = string.sub(wiersz, x, x)
			local koniec = x
			while koniec < 8 and string.sub(wiersz, koniec + 1, koniec + 1) == znak do
				koniec += 1
			end
			if znak ~= "." then
				self:_nowy("Frame", {
					BackgroundColor3 = Color3.fromHex(def.paleta[znak] or "#FF00FF"), BorderSizePixel = 0,
					Position = UDim2.fromScale((x - 1) / 8, (y - 1) / 8), Size = UDim2.fromScale((koniec - x + 1) / 8 + 0.004, 1 / 8 + 0.004),
					ZIndex = pole.ZIndex,
				}, pole)
			end
			x = koniec + 1
		end
	end
	return pole
end

function Interfejs:_ramka(rodzic: Instance, wlasciwosci: { [string]: any }, obrysPx: number, rog: number, cien: boolean?)
	local c: Frame? = nil
	if cien then
		c = self:_nowy("Frame", {
			Name = (wlasciwosci.Name or "Ramka") .. "Cien", BackgroundColor3 = self.K.tusz, BackgroundTransparency = 0.25,
			BorderSizePixel = 0, AnchorPoint = wlasciwosci.AnchorPoint or Vector2.zero,
			Position = (wlasciwosci.Position or UDim2.new()) + UDim2.fromScale(0.006, 0.014), Size = wlasciwosci.Size,
			Rotation = wlasciwosci.Rotation or 0, ZIndex = (wlasciwosci.ZIndex or 1) - 1,
		}, rodzic)
		self:_rog(c, rog)
	end
	local f = self:_nowy("Frame", wlasciwosci, rodzic)
	f.BorderSizePixel = 0
	self:_rog(f, rog)
	self:_obrys(f, obrysPx)
	-- cień jest rodzeństwem ramki, więc sam nie znika z nią: ukryta karteczka pasywki zostawiała ciemny pas na
	-- ekranie walki (Studio 17.11.2026, zrzuty v3_*) — cień idzie za Visible ramki
	local cienRamki = c
	if cienRamki then
		cienRamki.Visible = f.Visible
		f:GetPropertyChangedSignal("Visible"):Connect(function()
			cienRamki.Visible = f.Visible
		end)
	end
	return f
end

function Interfejs:_tekst(rodzic: Instance, wlasciwosci: { [string]: any }, obrysPx: number?)
	local t = self:_nowy("TextLabel", wlasciwosci, rodzic)
	t.BackgroundTransparency = 1
	t.TextScaled = true
	if obrysPx and obrysPx > 0 then
		self:_obrys(t, obrysPx)
	end
	return t
end

------------------------------------------------------------------ budowa
function Interfejs.nowy(playerGui: Instance, Ustawienia: any)
	local self = setmetatable({}, Interfejs)
	self.U = Ustawienia
	self.K = Ustawienia.KOLORY
	self.utworzono = 0
	self.obrysy = {} :: { [UIStroke]: number }
	self.skalaObrysu = 1
	self.napisy = {}
	self.kolejkaNapisow = {}
	self.ostatnieWejscie = {}
	self.trybNapisow = {}
	self.skalaStosu = {}
	self.kotwice = {}
	self.zegarNapisow = 0
	self.skalaZycia = 1
	self.statNapisow = { maksNaraz = 0, nakladania = 0, naCelu = 0, naInnym = 0, naGlowie = 0, pokazane = 0 }
	self.polaczenia = {} :: { RBXScriptConnection }
	self.paski = {}
	self.wspolczynnikPasa = 1
	self.zniszczony = false

	local gui = self:_nowy("ScreenGui", {
		Name = "TestWalki2Cutscenka", IgnoreGuiInset = true, ResetOnSpawn = false, DisplayOrder = 101, -- nad ekranem ładowania gry (100), który zostaje włączony i łapie kliknięcia
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, nil)
	self.gui = gui
	self.pasGorny = self:_nowy("Frame", { Name = "PasGorny", BackgroundColor3 = Color3.new(0, 0, 0), BorderSizePixel = 0, ZIndex = 1 }, gui)
	self.pasDolny = self:_nowy("Frame", { Name = "PasDolny", BackgroundColor3 = Color3.new(0, 0, 0), BorderSizePixel = 0, ZIndex = 1 }, gui)
	self.warstwaNapisow = self:_nowy("Frame", { Name = "Napisy", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), ZIndex = 5 }, gui)
	self.kadr = self:_nowy("Frame", { Name = "Kadr", BackgroundTransparency = 1, ZIndex = 10 }, gui)
	self.zaslona = self:_nowy("Frame", {
		Name = "Zaslona", BackgroundColor3 = Color3.new(0, 0, 0), BackgroundTransparency = 1, BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1), ZIndex = 100, Active = false,
	}, gui)

	self:_zbudujTabliczke("gracz")
	self:_zbudujTabliczke("wrog")
	self:_zbudujVS()
	self:_zbudujBaner()
	self:_zbudujUmiejetnosc()
	self:_zbudujPomin()
	self:_zbudujTempo()
	self:_zbudujDzwiek()
	self:_zbudujWynik()
	self:_zbudujPasywki()

	self.zegar = self:_tekst(self.kadr, {
		Name = "Zegar", Visible = false, AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0.02, 0.83),
		Size = UDim2.fromScale(0.5, 0.04), Font = Enum.Font.Code, TextColor3 = Color3.new(1, 1, 1),
		TextXAlignment = Enum.TextXAlignment.Left, Text = "", ZIndex = 50,
	}, 2)

	local kamera = workspace.CurrentCamera
	table.insert(self.polaczenia, kamera:GetPropertyChangedSignal("ViewportSize"):Connect(function()
		self:_przelicz()
	end))
	table.insert(self.polaczenia, kontener:GetAttributeChangedSignal("EmulacjaEkranu"):Connect(function()
		self:_przelicz()
	end))
	self:_przelicz()
	gui.Parent = playerGui
	return self
end

function Interfejs:_przelicz()
	local oknoWys = workspace.CurrentCamera.ViewportSize.Y
	local ox, oy, sz, wys, f = Interfejs.ekran()
	if sz <= 0 or wys <= 0 then
		return
	end
	self.skalaEmulacji = f
	local kadrWys = wys
	if sz / wys < PROPORCJE then
		kadrWys = sz / PROPORCJE
	end
	local pas = (wys - kadrWys) / 2
	-- pionowy kąt kamery dotyczy całego okna: kadr (na środku okna) ma mieć kąt ujęcia
	self.wspolczynnikPasa = kadrWys / oknoWys
	self.kadrPx = { x = ox, y = oy + pas, sz = sz, wys = kadrWys }
	self.kadr.Position = UDim2.fromOffset(ox, oy + pas)
	self.kadr.Size = UDim2.fromOffset(sz, kadrWys)
	self.pasGorny.Position = UDim2.fromOffset(ox, oy)
	self.pasGorny.Size = UDim2.fromOffset(sz, math.ceil(pas))
	self.pasDolny.Position = UDim2.fromOffset(ox, oy + math.floor(pas + kadrWys))
	self.pasDolny.Size = UDim2.fromOffset(sz, math.ceil(pas) + 1)
	self.pasGorny.Visible = pas > 0.5
	self.pasDolny.Visible = pas > 0.5
	local zajete = 0
	if pas < 1 then
		local ok, wstawka = pcall(function()
			return GuiService.TopbarInset
		end)
		if ok and wstawka then
			zajete = wstawka.Height * f
		end
	end
	self.gornyMargines = math.max(0.045, (zajete + 4) / kadrWys)
	for strona, p in self.paski do
		p.tabliczka.Position = UDim2.fromScale(if strona == "gracz" then 0.025 else 0.975, self.gornyMargines)
	end
	-- zapowiedzi pasywek: pod ikonami efektów (tabliczka 0,15 + efekty do 1,68 tabliczki)
	for strona, z in self.pasywki or {} do
		z.ramka.Position = UDim2.fromScale(if strona == "gracz" then 0.025 else 0.975, self.gornyMargines + 0.27)
	end
	if self.vs then
		self.vs.Position = UDim2.fromScale(0.5, self.gornyMargines + 0.065)
		self.tura.Position = UDim2.fromScale(0.5, self.gornyMargines + 0.12)
	end
	-- wstęga z nazwą umiejętności: pod licznikiem tury; gdy pasek Roblox u góry (telefon, okno bez pasów) spycha
	-- tabliczki w dół, wstęga idzie na dół ekranu między przyciski tempa a POMIŃ — inaczej zasłaniała paski życia
	if self.umiejetnosc then
		-- v3: tabliczki są wyższe (pasek many) — wstęga niżej (0,30), żeby nie wchodziła na rangę i ikony efektów
		self.wstegaNaDole = self.gornyMargines > 0.08
		self.umiejetnosc.Position = UDim2.fromScale(0.5, if self.wstegaNaDole then 0.905 else 0.3)
		self.umiejetnosc.Size = UDim2.fromScale(if self.wstegaNaDole then 0.34 else 0.4, if self.wstegaNaDole then 0.08 else 0.07)
	end
	-- napisy nad postaciami nie wchodzą na tabliczki ani na wstęgę
	self.gornaGranicaNapisow = math.max(0.35, self.gornyMargines + 0.29)
	self.skalaObrysu = kadrWys / WYS_ODNIESIENIA
	for obrys, px in self.obrysy do
		if obrys.Parent then
			obrys.Thickness = math.max(1, px * self.skalaObrysu)
		else
			self.obrysy[obrys] = nil
		end
	end
end

local RANGI = {
	zwykly = { "ZWYKŁY", "#8D93A6" },
	rzadki = { "RZADKI", "#2F6FE0" },
	straznik = { "STRAŻNIK", "#E8364F" },
	gracz = { "GRACZ", "#52D273" },
	pojedynek = { "POJEDYNEK", "#52D273" },
}

function Interfejs:_zbudujTabliczke(strona: string)
	local K = self.K
	local lewa = strona == "gracz"
	local ax = if lewa then 0 else 1
	-- v3: tabliczka wyższa (0,15 kadru) — pod paskiem życia pasek many (0,85–1,04 tabliczki), niżej ikony efektów
	local t = self:_nowy("Frame", {
		Name = if lewa then "TabliczkaGracza" else "TabliczkaWroga", BackgroundTransparency = 1,
		AnchorPoint = Vector2.new(ax, 0), Position = UDim2.fromScale(if lewa then 0.025 else 0.975, 0.045),
		Size = UDim2.fromScale(0.4, 0.15), Rotation = if lewa then -1.5 else 1.5, ZIndex = 10,
	}, self.kadr)
	local portret = self:_ramka(t, {
		Name = "Portret", AnchorPoint = Vector2.new(ax, 0.5), Position = UDim2.fromScale(ax, 0.5), Size = UDim2.fromScale(1.02, 1.02),
		SizeConstraint = Enum.SizeConstraint.RelativeYY, BackgroundColor3 = if lewa then K.niebieski else K.czerwony,
		Rotation = if lewa then -4 else 4, ZIndex = 14,
	}, 4, 0.16, false)
	local nazwa = self:_tekst(t, {
		-- v3: wyższa tabliczka = większy portret (0,215 szerokości tabliczki + obrót i obrys); nazwa zaczyna się za nim,
		-- inaczej portret zasłaniał ostatni znak poziomu przeciwnika („POZ. 10” czytało się jak „POZ. 1”)
		Name = "Nazwa", AnchorPoint = Vector2.new(ax, 0), Position = UDim2.fromScale(if lewa then 0.24 else 0.76, -0.02),
		Size = UDim2.fromScale(0.78, 0.4), Font = NAGLOWKI, TextColor3 = K.bialy,
		TextXAlignment = if lewa then Enum.TextXAlignment.Left else Enum.TextXAlignment.Right, Text = "", ZIndex = 13,
	}, 3.5)
	local ranga = self:_ramka(t, {
		-- pod paskiem many, od strony środka ekranu (ikony efektów rosną od zewnętrznej krawędzi)
		Name = "Ranga", AnchorPoint = Vector2.new(1 - ax, 0), Position = UDim2.fromScale(if lewa then 0.86 else 0.14, 1.12),
		Size = UDim2.fromScale(0.2, 0.32), BackgroundColor3 = K.szary, Rotation = if lewa then 3 else -3, ZIndex = 13,
	}, 3, 0.2, false)
	local rangaNapis = self:_tekst(ranga, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.86, 0.72),
		Font = KOMIKS, TextColor3 = K.bialy, Text = "", ZIndex = 14,
	}, 2)
	local pasek = self:_ramka(t, {
		Name = "Pasek", AnchorPoint = Vector2.new(ax, 1), Position = UDim2.fromScale(if lewa then 0.14 else 0.86, 0.82),
		Size = UDim2.fromScale(0.86, 0.42), BackgroundColor3 = K.ciemny, ZIndex = 11,
	}, 4, 0.28, false)
	local wnetrze = self:_nowy("Frame", {
		Name = "Wnetrze", BackgroundTransparency = 1, Position = UDim2.fromScale(if lewa then 0.05 else 0.012, 0.12),
		Size = UDim2.fromScale(0.938, 0.76), ZIndex = 11,
	}, pasek)
	local duch = self:_nowy("Frame", {
		Name = "Duch", BackgroundColor3 = K.bialy, BorderSizePixel = 0, AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(ax, 0), Size = UDim2.fromScale(1, 1), ZIndex = 11,
	}, wnetrze)
	self:_rog(duch, 0.3)
	local wypelnienie = self:_nowy("Frame", {
		Name = "Wypelnienie", BackgroundColor3 = K.bialy, BorderSizePixel = 0, AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(ax, 0), Size = UDim2.fromScale(1, 1), ZIndex = 12,
	}, wnetrze)
	self:_rog(wypelnienie, 0.3)
	self:_nowy("UIGradient", {
		Rotation = 90,
		Color = if lewa then ColorSequence.new(Color3.fromHex("#6BFFE3"), Color3.fromHex("#17B8D9"))
			else ColorSequence.new(Color3.fromHex("#FF9AA5"), Color3.fromHex("#E8364F")),
	}, wypelnienie)
	local polysk = self:_nowy("Frame", {
		Name = "Polysk", BackgroundColor3 = K.bialy, BackgroundTransparency = 0.55, BorderSizePixel = 0,
		Position = UDim2.fromScale(0.02, 0.1), Size = UDim2.fromScale(0.96, 0.26), ZIndex = 12,
	}, wypelnienie)
	self:_rog(polysk, 0.5)
	-- blask paska życia przy wskrzeszeniu (v3): złota nakładka, gaśnie sama
	local blaskZycia = self:_nowy("Frame", {
		Name = "BlaskZycia", BackgroundColor3 = Color3.fromHex("#FFE58A"), BackgroundTransparency = 1, BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1), ZIndex = 13,
	}, wnetrze)
	self:_rog(blaskZycia, 0.3)
	local liczba = self:_tekst(pasek, {
		Name = "Liczba", Position = UDim2.fromScale(0.05, 0.08), Size = UDim2.fromScale(0.9, 0.84), Font = KOMIKS,
		TextColor3 = K.bialy, Text = "", ZIndex = 14,
	}, 2.5)
	--[[ Pasek many (v3, D-089): wartości WYŁĄCZNIE z dziennika (mana_gracz / mana_wrog po zdarzeniu). Kreska progu =
		koszt następnej umiejętności tej strony z dziennika (gdy mniejszy niż pełny pasek). Gotowa (mana ≥ próg): pasek
		świeci i pulsuje kryształ na jego końcu; przy użyciu umiejętności błysk i spadek o koszt. Bez napisu (pasek
		ma ok. 11 punktów wysokości na telefonie — tekst byłby za mały). ]]
	local mana = self:_ramka(t, {
		Name = "Mana", AnchorPoint = Vector2.new(ax, 0), Position = UDim2.fromScale(if lewa then 0.14 else 0.86, 0.85),
		Size = UDim2.fromScale(0.86, 0.19), BackgroundColor3 = K.ciemny, ZIndex = 11,
	}, 3, 0.4, false)
	local manaWnetrze = self:_nowy("Frame", {
		Name = "Wnetrze", BackgroundTransparency = 1, Position = UDim2.fromScale(if lewa then 0.05 else 0.012, 0.16),
		Size = UDim2.fromScale(0.938, 0.68), ZIndex = 11,
	}, mana)
	local manaWyp = self:_nowy("Frame", {
		Name = "Wypelnienie", BackgroundColor3 = K.bialy, BorderSizePixel = 0, AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(ax, 0), Size = UDim2.fromScale(0, 1), ZIndex = 12, Visible = false,
	}, manaWnetrze)
	self:_rog(manaWyp, 0.5)
	local manaGradient = self:_nowy("UIGradient", {
		Rotation = 90, Color = ColorSequence.new(Color3.fromHex("#8FD0FF"), Color3.fromHex("#2F6FE0")),
	}, manaWyp)
	local manaBlysk = self:_nowy("Frame", {
		Name = "Blysk", BackgroundColor3 = K.bialy, BackgroundTransparency = 1, BorderSizePixel = 0, Size = UDim2.fromScale(1, 1), ZIndex = 13,
	}, manaWnetrze)
	self:_rog(manaBlysk, 0.5)
	local manaProg = self:_nowy("Frame", {
		Name = "Prog", BackgroundColor3 = K.zolty, BorderSizePixel = 0, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(1, 0.5), Size = UDim2.new(0, 3, 1.5, 0), ZIndex = 14, Visible = false,
	}, manaWnetrze)
	local manaKrysztal = self:_nowy("Frame", {
		Name = "Krysztal", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(if lewa then 1.02 else -0.02, 0.5), Size = UDim2.fromScale(1.9, 1.9),
		SizeConstraint = Enum.SizeConstraint.RelativeYY, ZIndex = 15, Visible = false,
	}, mana)
	self:_ikona(manaKrysztal, "mana", 0)
	local krysztalSkala = self:_nowy("UIScale", { Scale = 1 }, manaKrysztal)
	-- rząd ikon efektów pod tabliczką (pod paskiem many)
	local efekty = self:_nowy("Frame", {
		Name = "Efekty", BackgroundTransparency = 1, AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(if lewa then 0.14 else 0.86, 1.12), Size = UDim2.fromScale(0.86, 0.56), ZIndex = 12,
	}, t)
	self:_nowy("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = if lewa then Enum.HorizontalAlignment.Left else Enum.HorizontalAlignment.Right,
		Padding = UDim.new(0.015, 0), SortOrder = Enum.SortOrder.LayoutOrder,
	}, efekty)

	-- legenda gotowa (wskrzeszenie w slocie): złote pióro w rogu portretu; po wskrzeszeniu szare
	local legenda = self:_nowy("Frame", {
		Name = "Legenda", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(if lewa then 0.92 else 0.08, 0.9), Size = UDim2.fromScale(0.42, 0.42), ZIndex = 16, Visible = false,
	}, portret)
	self:_ikona(legenda, "feniks", 0)

	self.paski[strona] = {
		tabliczka = t, nazwa = nazwa, wypelnienie = wypelnienie, duch = duch, liczba = liczba, portret = portret,
		ranga = ranga, rangaNapis = rangaNapis, efekty = efekty, podpisEfektow = "", blaskZycia = blaskZycia,
		maks = 1, cel = 1, pokazane = 1, duchPokazany = 1, duchCzeka = 0, wstrzas = 0, obrotBazowy = t.Rotation,
		blaskZyciaCzas = 0, legenda = legenda,
		mana = {
			ramka = mana, wyp = manaWyp, gradient = manaGradient, blysk = manaBlysk, prog = manaProg, krysztal = manaKrysztal,
			krysztalSkala = krysztalSkala, maks = 100, wartosc = 0, pokazane = 0, cel = 0, progWartosc = 100, gotowa = false,
			blyskCzas = 0, wiek = 0, spowolniona = false,
		},
	}
end

function Interfejs:_zbudujVS()
	local K = self.K
	local vs = self:_nowy("Frame", {
		Name = "VS", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.11),
		Size = UDim2.fromScale(0.095, 0.095), SizeConstraint = Enum.SizeConstraint.RelativeYY, ZIndex = 15,
	}, self.kadr)
	self:_ramka(vs, {
		Name = "Romb", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(0.78, 0.78),
		BackgroundColor3 = K.zolty, Rotation = 45, ZIndex = 15,
	}, 4, 0.14, false)
	self:_tekst(vs, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.9, 0.62),
		Font = NAGLOWKI, Text = "VS", TextColor3 = K.czerwony, Rotation = -6, ZIndex = 16,
	}, 3)
	self.vs = vs
	self.tura = self:_tekst(self.kadr, {
		Name = "Tura", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.18), Size = UDim2.fromScale(0.12, 0.04),
		Font = NAGLOWKI, Text = "", TextColor3 = K.bialy, ZIndex = 15,
	}, 3)
end

function Interfejs:_zbudujBaner()
	local K = self.K
	local baner = self:_nowy("Frame", {
		Name = "Baner", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.31),
		Size = UDim2.fromScale(0.74, 0.2), Rotation = -3, Visible = false, ZIndex = 30,
	}, self.kadr)
	self.banerSkala = self:_nowy("UIScale", { Scale = 1 }, baner)
	self.banerWstega = self:_ramka(baner, {
		Name = "Wstega", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.55), Size = UDim2.fromScale(1.3, 0.62),
		BackgroundColor3 = K.czerwony, ZIndex = 30,
	}, 5, 0.08, true)
	self.banerCien = self:_tekst(baner, {
		Name = "Cien", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.506, 0.535), Size = UDim2.fromScale(0.96, 0.9),
		Font = NAGLOWKI, Text = "", TextColor3 = K.tusz, ZIndex = 31,
	}, 7)
	self.banerNapis = self:_tekst(baner, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(0.96, 0.9),
		Font = NAGLOWKI, Text = "", TextColor3 = K.zolty, ZIndex = 32,
	}, 6)
	self.baner = baner
end

-- wstęga z nazwą użytej umiejętności (pod licznikiem tury)
function Interfejs:_zbudujUmiejetnosc()
	local K = self.K
	local u = self:_nowy("Frame", {
		Name = "Umiejetnosc", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.272),
		Size = UDim2.fromScale(0.44, 0.07), Rotation = -2, Visible = false, ZIndex = 28,
	}, self.kadr)
	self.umSkala = self:_nowy("UIScale", { Scale = 1 }, u)
	self.umWstega = self:_ramka(u, {
		Name = "Wstega", Size = UDim2.fromScale(1, 1), BackgroundColor3 = K.niebieski, ZIndex = 28,
	}, 4, 0.18, true)
	self.umNapis = self:_tekst(u, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.92, 0.78),
		Font = NAGLOWKI, Text = "", TextColor3 = K.bialy, ZIndex = 29,
	}, 4)
	self.umiejetnosc = u
end

function Interfejs:_przycisk(rodzic: Instance, nazwa: string, tekst: string, kolor: Color3, wlasciwosci: { [string]: any })
	local K = self.K
	local uchwyt = self:_nowy("Frame", {
		Name = nazwa, BackgroundTransparency = 1, AnchorPoint = wlasciwosci.AnchorPoint, Position = wlasciwosci.Position,
		Size = wlasciwosci.Size, Rotation = wlasciwosci.Rotation or 0, ZIndex = wlasciwosci.ZIndex,
	}, rodzic)
	local skala = self:_nowy("UIScale", { Scale = 1 }, uchwyt)
	local cien = self:_nowy("Frame", {
		Name = "Cien", BackgroundColor3 = K.tusz, BorderSizePixel = 0, Position = UDim2.fromScale(0.025, 0.12),
		Size = UDim2.fromScale(1, 1), ZIndex = wlasciwosci.ZIndex,
	}, uchwyt)
	self:_rog(cien, 0.26)
	local p = self:_nowy("TextButton", {
		Name = "Przycisk", AutoButtonColor = false, BackgroundColor3 = kolor, BorderSizePixel = 0, Size = UDim2.fromScale(1, 1),
		Text = "", ZIndex = wlasciwosci.ZIndex + 1,
	}, uchwyt)
	self:_rog(p, 0.26)
	self:_obrys(p, 4)
	self:_nowy("UIGradient", { Rotation = 90, Color = ColorSequence.new(Color3.new(1, 1, 1), Color3.new(0.82, 0.82, 0.82)) }, p)
	self:_tekst(p, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.86, 0.66),
		Font = NAGLOWKI, Text = tekst, TextColor3 = K.bialy, ZIndex = wlasciwosci.ZIndex + 2,
	}, 3.5)
	local szybko = TweenInfo.new(0.1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	local nad = false
	local function do_(v: number)
		TweenService:Create(skala, szybko, { Scale = v }):Play()
	end
	table.insert(self.polaczenia, p.MouseEnter:Connect(function()
		nad = true
		do_(1.07)
	end))
	table.insert(self.polaczenia, p.MouseLeave:Connect(function()
		nad = false
		do_(1)
	end))
	table.insert(self.polaczenia, p.MouseButton1Down:Connect(function()
		do_(0.93)
	end))
	table.insert(self.polaczenia, p.MouseButton1Up:Connect(function()
		do_(if nad then 1.07 else 1)
	end))
	return uchwyt, p
end

function Interfejs:_zbudujPomin()
	local uchwyt, p = self:_przycisk(self.kadr, "Pomin", "POMIŃ  »", self.K.zolty, {
		AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(0.975, 0.955), Size = UDim2.fromScale(0.19, 0.115),
		Rotation = -2, ZIndex = 40,
	})
	p.Napis.TextColor3 = self.K.tusz
	local obrysNapisu = p.Napis:FindFirstChildOfClass("UIStroke")
	if obrysNapisu then
		self.obrysy[obrysNapisu] = nil
		obrysNapisu:Destroy()
	end
	uchwyt.Visible = false
	self.pomin = uchwyt
	self.pominPrzycisk = p
	-- informacja w miejscu przycisku, gdy pomijać nie wolno (D-078) — nie przycisk, dwa wiersze ok. 16 pkt na telefonie
	local info = self:_tekst(self.kadr, {
		Name = "PominInfo", AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(0.975, 0.955), Size = UDim2.fromScale(0.21, 0.1),
		Font = KOMIKS, Text = "", TextColor3 = self.K.zolty, TextWrapped = true, Rotation = -2, ZIndex = 40, Visible = false,
	}, 2.5)
	self.pominInfo = info
	self.pominInfoCzas = 0
end

-- przyciski tempa: ×1 / ×2 / ×4 (lewy dolny róg; duże, do kciuka na telefonie)
function Interfejs:_zbudujTempo()
	local K = self.K
	local pas = self:_nowy("Frame", {
		Name = "Tempo", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0.025, 0.955),
		Size = UDim2.fromScale(0.3, 0.115), Visible = false, ZIndex = 40,
	}, self.kadr)
	self.tempoPrzyciski = {}
	for i, t in { 1, 2, 4 } do
		local uchwyt, p = self:_przycisk(pas, "Tempo" .. t, "×" .. t, K.szary, {
			AnchorPoint = Vector2.new(0, 0), Position = UDim2.fromScale((i - 1) * 0.34, 0), Size = UDim2.fromScale(0.3, 1),
			Rotation = ({ -2, 1, -1 })[i], ZIndex = 40,
		})
		self.tempoPrzyciski[t] = { uchwyt = uchwyt, przycisk = p }
	end
	self.tempoPas = pas
end

-- przycisk wyciszenia (obok POMIŃ, od strony środka; wstęga umiejętności na dole telefonu kończy się przed nim)
function Interfejs:_zbudujDzwiek()
	local uchwyt, p = self:_przycisk(self.kadr, "Dzwiek", "", self.K.niebieski, {
		AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(0.772, 0.955), Size = UDim2.fromScale(0.068, 0.115),
		Rotation = 2, ZIndex = 40,
	})
	uchwyt.Visible = false
	self.dzwiek = uchwyt
	self.dzwiekPrzycisk = p
	self:ustawDzwiek(false)
end

function Interfejs:ustawDzwiek(wyciszone: boolean)
	local p = self.dzwiekPrzycisk
	local stara = p:FindFirstChild("Ikona")
	if stara then
		stara:Destroy()
	end
	local ikona = self:_ikona(p, if wyciszone then "cisza" else "glosnik", 0.2)
	ikona.ZIndex = p.ZIndex + 2
	for _, d in ikona:GetDescendants() do
		if d:IsA("GuiObject") then
			d.ZIndex = p.ZIndex + 2
		end
	end
	p.BackgroundColor3 = if wyciszone then self.K.szary else self.K.niebieski
	p:SetAttribute("Wyciszone", wyciszone)
end

function Interfejs:pokazDzwiek(wyciszone: boolean, naZmiane: () -> ())
	self.dzwiek.Visible = true
	if self.polaczenieDzwieku then
		self.polaczenieDzwieku:Disconnect()
	end
	self.polaczenieDzwieku = self.dzwiekPrzycisk.Activated:Connect(naZmiane)
	self:ustawDzwiek(wyciszone)
end

function Interfejs:ukryjDzwiek()
	self.dzwiek.Visible = false
end

--[[ Zapowiedzi pasywek (v3): krótka karteczka pod tabliczką strony na starcie walki — „PASYWKA: KOLOS” i premie
	z danych silnika („+4% życia · +2% obrażeń”), po kolei, każda ok. 1,2 s. Pasywki działają w liczbach (bez
	zdarzeń w dzienniku), więc to jedyny ślad, skąd premia. Na telefonie: tytuł ok. 15 pkt, premie ok. 13 pkt. ]]
local ZRODLA_PASYWEK = {
	slot = { "PASYWKA", "gwiazda", "#7B4DFF" },
	bron = { "BROŃ", "bron", "#8A5A0A" },
	legenda = { "LEGENDA", "feniks", "#E79A12" },
}
function Interfejs:_zbudujPasywki()
	local K = self.K
	self.pasywki = {}
	for _, strona in { "gracz", "wrog" } do
		local lewa = strona == "gracz"
		local ax = if lewa then 0 else 1
		local ramka = self:_ramka(self.kadr, {
			Name = if lewa then "PasywkaGracza" else "PasywkaWroga", AnchorPoint = Vector2.new(ax, 0),
			Position = UDim2.fromScale(if lewa then 0.025 else 0.975, 0.315), Size = UDim2.fromScale(0.44, 0.088),
			BackgroundColor3 = K.krem, Rotation = if lewa then -1 else 1, ZIndex = 26, Visible = false,
		}, 3, 0.18, true)
		local skala = self:_nowy("UIScale", { Scale = 1 }, ramka)
		local poleIkony = self:_nowy("Frame", {
			Name = "PoleIkony", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.fromScale(0.015, 0.5),
			Size = UDim2.fromScale(0.78, 0.78), SizeConstraint = Enum.SizeConstraint.RelativeYY, ZIndex = 27,
		}, ramka)
		local tytul = self:_tekst(ramka, {
			Name = "Tytul", Position = UDim2.fromScale(0.15, 0.06), Size = UDim2.fromScale(0.83, 0.46), Font = NAGLOWKI,
			Text = "", TextColor3 = K.tusz, TextXAlignment = Enum.TextXAlignment.Left, ZIndex = 27,
		}, 0)
		local linia = self:_tekst(ramka, {
			Name = "Linia", Position = UDim2.fromScale(0.15, 0.54), Size = UDim2.fromScale(0.83, 0.4), Font = KOMIKS,
			Text = "", TextColor3 = K.ciemny, TextXAlignment = Enum.TextXAlignment.Left, ZIndex = 27,
		}, 0)
		self.pasywki[strona] = { ramka = ramka, skala = skala, poleIkony = poleIkony, tytul = tytul, linia = linia,
			kolejka = {}, czas = 0, pokazane = {} }
	end
end

-- opisy: { { nazwa, linia, zrodlo = "slot" | "bron", legendarna } } (PlanWalki.opisPasywki); czas = s na jedną
function Interfejs:zapowiedzPasywki(strona: string, opisy, czas: number?)
	local z = self.pasywki and self.pasywki[strona]
	if not z then
		return
	end
	z.kolejka = table.clone(opisy or {})
	z.czasNaJedna = czas or 1.25
	z.czas = 0
	z.pokazane = {}
	z.ramka.Visible = false
end

function Interfejs:ukryjPasywki()
	for _, z in self.pasywki or {} do
		table.clear(z.kolejka)
		z.ramka.Visible = false
		z.czas = 0
	end
end

function Interfejs:_pokazPasywke(z, opis)
	local zr = ZRODLA_PASYWEK[if opis.legendarna then "legenda" else opis.zrodlo] or ZRODLA_PASYWEK.slot
	local stara = z.poleIkony:FindFirstChild("Ikona")
	if stara then
		stara:Destroy()
	end
	self:_ikona(z.poleIkony, zr[2], 0)
	z.tytul.Text = zr[1] .. ": " .. wielkie(opis.nazwa)
	z.tytul.TextColor3 = Color3.fromHex(zr[3])
	z.linia.Text = opis.linia
	z.ramka.Visible = true
	z.ramka:SetAttribute("Pasywka", opis.nazwa)
	z.skala.Scale = 0.5
	TweenService:Create(z.skala, TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	table.insert(z.pokazane, opis.nazwa)
end

function Interfejs:_aktualizujPasywki(dt: number)
	for _, z in self.pasywki or {} do
		if z.ramka.Visible or #z.kolejka > 0 then
			z.czas -= dt
			if z.czas <= 0 then
				if #z.kolejka > 0 then
					self:_pokazPasywke(z, table.remove(z.kolejka, 1))
					z.czas = z.czasNaJedna or 1.25
				else
					z.ramka.Visible = false
				end
			end
		end
	end
end

-- D-078: przy pierwszej walce z gatunkiem nie ma przycisku POMIŃ — w jego miejscu krótka informacja (start walki
-- i próba pominięcia spacją); czas w sekundach rzeczywistych
function Interfejs:pokazInfoPominiecia(tekst: string, czas: number)
	self.pominInfo.Text = tekst
	self.pominInfo.Visible = true
	self.pominInfoCzas = czas
end

function Interfejs:ukryjInfoPominiecia()
	self.pominInfo.Visible = false
	self.pominInfoCzas = 0
end

function Interfejs:_zbudujWynik()
	local K = self.K
	local uchwyt = self:_nowy("Frame", {
		Name = "Wynik", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.66, 0.58),
		Size = UDim2.fromScale(0.56, 0.64), Rotation = -1.2, Visible = false, ZIndex = 60,
	}, self.kadr)
	self.wynikSkala = self:_nowy("UIScale", { Scale = 1 }, uchwyt)
	local karta = self:_ramka(uchwyt, { Name = "Karta", Size = UDim2.fromScale(1, 1), BackgroundColor3 = K.krem, ZIndex = 61 }, 5, 0.06, true)
	local wstega = self:_ramka(uchwyt, {
		Name = "Wstega", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, -0.09), Size = UDim2.fromScale(1.06, 0.25),
		BackgroundColor3 = K.pomarancz, Rotation = 1.6, ZIndex = 63,
	}, 5, 0.14, true)
	local tytulCien = self:_tekst(wstega, {
		Name = "TytulCien", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.505, 0.56), Size = UDim2.fromScale(0.9, 0.78),
		Font = NAGLOWKI, Text = "", TextColor3 = K.tusz, ZIndex = 64,
	}, 6)
	local tytul = self:_tekst(wstega, {
		Name = "Tytul", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.9, 0.78),
		Font = NAGLOWKI, Text = "", TextColor3 = K.zolty, ZIndex = 65,
	}, 5)
	local podtytul = self:_tekst(karta, {
		Name = "Podtytul", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.2), Size = UDim2.fromScale(0.92, 0.085),
		Font = KOMIKS, Text = "", TextColor3 = K.ciemny, ZIndex = 62,
	}, 0)
	local kafle = {}
	local opisy = { { "moneta", "ZŁOTO" }, { "gwiazda", "DOŚWIADCZ." }, { "zeton", "TOKENY LASU" }, { "gem", "GEM" }, { "shard", "SHARD EWOL." } }
	for i, opis in opisy do
		local kafel = self:_ramka(karta, {
			Name = "Kafel" .. i, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.11 + (i - 1) * 0.195, 0.315),
			Size = UDim2.fromScale(0.175, 0.37), BackgroundColor3 = K.bialy, Rotation = ({ -2.5, 1.5, -1.5, 2, -1 })[i], ZIndex = 62,
		}, 4, 0.1, true)
		local skala = self:_nowy("UIScale", { Scale = 1 }, kafel)
		local poleIkony = self:_nowy("Frame", {
			Name = "PoleIkony", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.05),
			Size = UDim2.fromScale(0.62, 0.42), ZIndex = 62,
		}, kafel)
		self:_ikona(poleIkony, opis[1], 0)
		local wartosc = self:_tekst(kafel, {
			Name = "Wartosc", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.48), Size = UDim2.fromScale(0.92, 0.3),
			Font = KOMIKS, Text = "", TextColor3 = K.tusz, ZIndex = 63,
		}, 0)
		local podpis = self:_tekst(kafel, {
			Name = "Podpis", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.79), Size = UDim2.fromScale(0.94, 0.16),
			Font = KOMIKS, Text = opis[2], TextColor3 = K.szary, ZIndex = 63,
		}, 0)
		kafle[i] = { ramka = kafel, skala = skala, wartosc = wartosc, podpis = podpis, ikona = poleIkony }
	end
	local _, jeszczePrzycisk = self:_przycisk(karta, "JeszczeRaz", "JESZCZE RAZ", K.zielony, {
		AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.fromScale(0.29, 0.95), Size = UDim2.fromScale(0.42, 0.18), Rotation = -1.5, ZIndex = 66,
	})
	local _, zamknijPrzycisk = self:_przycisk(karta, "Zamknij", "ZAMKNIJ", K.czerwony, {
		AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.fromScale(0.75, 0.95), Size = UDim2.fromScale(0.34, 0.18), Rotation = 1.5, ZIndex = 66,
	})
	local stopka = self:_tekst(uchwyt, {
		Name = "Stopka", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 1.03), Size = UDim2.fromScale(0.98, 0.05),
		Font = Enum.Font.GothamBold, Text = "", TextColor3 = K.bialy, ZIndex = 62,
	}, 2)
	self.wynik = {
		uchwyt = uchwyt, wstega = wstega, tytul = tytul, tytulCien = tytulCien, podtytul = podtytul, kafle = kafle,
		jeszcze = jeszczePrzycisk, zamknij = zamknijPrzycisk, stopka = stopka, liczniki = {},
	}
end

------------------------------------------------------------------ sterowanie z odtwarzacza
-- strony: walka.strony; aktorzy: { gracz = klucz aktora, wrog = klucz aktora }
function Interfejs:ustawStrony(strony, aktorzy)
	for strona, dane in strony do
		local p = self.paski[strona]
		if p then
			p.nazwa.Text = wielkie(dane.nazwa) .. "  •  POZ. " .. tostring(dane.poziom)
			p.maks = math.max(1, dane.zycie)
			p.hp = dane.zycie
			p.cel, p.pokazane, p.duchPokazany, p.duchCzeka, p.wstrzas = 1, 1, 1, 0, 0
			p.liczba.Text = tostring(dane.zycie) .. " / " .. tostring(dane.zycie)
			p.wypelnienie.Size = UDim2.fromScale(1, 1)
			p.wypelnienie.Visible = true
			p.duch.Size = UDim2.fromScale(1, 1)
			p.tabliczka.Rotation = p.obrotBazowy
			p.blaskZycia.BackgroundTransparency = 1
			p.blaskZyciaCzas = 0
			p.legenda.Visible = false
			local m = p.mana
			m.maks = math.max(1, tonumber(dane.mana_maks) or 100)
			m.blyskCzas, m.wiek, m.spowolniona, m.gotowa = 0, 0, false, false
			self:ustawMane(strona, tonumber(dane.mana) or 0, { natychmiast = true })
			local ikona = p.portret:FindFirstChild("Ikona")
			if ikona then
				ikona:Destroy()
			end
			self:_ikona(p.portret, aktorzy[strona] or "oko", 0.13)
			-- przeciwnik-postać (pojedynek z lustrem, v3) ma w dzienniku rangę „gracz” — na tabliczce „POJEDYNEK”
			local r = if strona == "wrog" and dane.rodzaj == "postac" then RANGI.pojedynek else (RANGI[dane.ranga] or RANGI.zwykly)
			p.ranga.Visible = strona == "wrog"
			p.rangaNapis.Text = r[1]
			p.ranga.BackgroundColor3 = Color3.fromHex(r[2])
			self:ustawEfekty(strona, {})
		end
	end
	self:ustawTure(0)
end

function Interfejs:ustawZycie(strona: string, hp: number, natychmiast: boolean?)
	local p = self.paski[strona]
	if not p then
		return
	end
	if p.hp == hp and not natychmiast then
		return
	end
	p.hp = hp
	p.cel = math.clamp(hp / p.maks, 0, 1)
	p.liczba.Text = tostring(hp) .. " / " .. tostring(p.maks)
	if natychmiast then
		p.pokazane, p.duchPokazany, p.duchCzeka, p.wstrzas = p.cel, p.cel, 0, 0
		p.wypelnienie.Size = UDim2.fromScale(math.max(p.cel, 0.001), 1)
		p.wypelnienie.Visible = p.cel > 0.004
	else
		p.duchCzeka = 0.28
		p.wstrzas = 1
	end
end

-- złoty blask paska życia (wskrzeszenie): pasek rośnie z 0 do życia po powrocie i świeci ok. 1 s
function Interfejs:blaskZycia(strona: string)
	local p = self.paski[strona]
	if p then
		p.blaskZyciaCzas = 1
		p.wstrzas = 0.6
	end
end

-- legenda (wskrzeszenie w slocie): widoczna = jest; zuzyta = szara (już użyta w tej walce)
function Interfejs:ustawLegende(strona: string, widoczna: boolean, zuzyta: boolean?)
	local p = self.paski[strona]
	if not p then
		return
	end
	p.legenda.Visible = widoczna
	for _, d in p.legenda:GetDescendants() do
		if d:IsA("Frame") and d.Name ~= "Ikona" then
			d.BackgroundTransparency = if zuzyta then 0.7 else 0
		end
	end
	p.legenda:SetAttribute("Zuzyta", zuzyta == true)
end

--[[ Pasek many: wartosc z dziennika; opcje = { gotowa, prog, uzycie, natychmiast, spowolniona }.
	gotowa → świeci i pulsuje kryształ; uzycie → biały błysk (pasek „dobija” i zapala się) i spadek o koszt;
	prog < maks → żółta kreska w miejscu kosztu następnej umiejętności; spowolniona → lodowy, szarawy kolor
	(spowolnienie obcina zysk many — widać to w liczbach z dziennika). Wartość do testów: Interfejs:mana(strona). ]]
local KOLOR_MANY = ColorSequence.new(Color3.fromHex("#8FD0FF"), Color3.fromHex("#2F6FE0"))
local KOLOR_MANY_GOTOWEJ = ColorSequence.new(Color3.fromHex("#E6F4FF"), Color3.fromHex("#4FA8FF"))
local KOLOR_MANY_SPOWOLNIONEJ = ColorSequence.new(Color3.fromHex("#D3E6EE"), Color3.fromHex("#7C9AAE"))
function Interfejs:ustawMane(strona: string, wartosc: number, opcje: any?)
	local p = self.paski[strona]
	if not p then
		return
	end
	local o = opcje or {}
	local m = p.mana
	m.wartosc = math.max(0, wartosc)
	m.cel = math.clamp(m.wartosc / m.maks, 0, 1)
	if o.prog ~= nil then
		m.progWartosc = o.prog
	end
	if o.gotowa ~= nil then
		m.gotowa = o.gotowa == true
	end
	if o.spowolniona ~= nil then
		m.spowolniona = o.spowolniona == true
	end
	if o.uzycie then
		m.blyskCzas = 0.45
	end
	if o.natychmiast then
		m.pokazane = m.cel
	end
	local progUlamek = math.clamp((m.progWartosc or m.maks) / m.maks, 0, 1)
	m.prog.Visible = progUlamek < 0.995
	m.prog.Position = UDim2.fromScale(if strona == "gracz" then progUlamek else 1 - progUlamek, 0.5)
	m.gradient.Color = if m.spowolniona then KOLOR_MANY_SPOWOLNIONEJ elseif m.gotowa then KOLOR_MANY_GOTOWEJ else KOLOR_MANY
	m.krysztal.Visible = m.gotowa
	m.ramka:SetAttribute("Wartosc", m.wartosc)
	m.ramka:SetAttribute("Gotowa", m.gotowa)
	self:_rysujMane(m)
end

function Interfejs:_rysujMane(m)
	m.wyp.Size = UDim2.fromScale(math.max(m.pokazane, 0.001), 1)
	m.wyp.Visible = m.pokazane > 0.004
end

function Interfejs:mana(strona: string): number?
	local p = self.paski[strona]
	return p and p.mana.wartosc
end

-- lista: { { id, ikona, kolor, tury, znaczek? } } — znaczek = tekst w lewym górnym rogu („×3”, „−42%”);
-- przebudowa tylko przy zmianie
function Interfejs:ustawEfekty(strona: string, lista)
	local p = self.paski[strona]
	if not p then
		return
	end
	local podpis = {}
	for _, e in lista do
		table.insert(podpis, e.id .. ":" .. tostring(e.tury) .. ":" .. tostring(e.znaczek or ""))
	end
	local s = table.concat(podpis, ",")
	if s == p.podpisEfektow then
		return
	end
	p.podpisEfektow = s
	for _, d in p.efekty:GetChildren() do
		if d:IsA("Frame") then
			d:Destroy()
		end
	end
	for i, e in lista do
		local f = self:_ramka(p.efekty, {
			Name = "Efekt_" .. e.id, Size = UDim2.fromScale(1, 1), SizeConstraint = Enum.SizeConstraint.RelativeYY,
			BackgroundColor3 = self.K.ciemny, LayoutOrder = i, ZIndex = 12,
		}, 3, 0.2, false)
		self:_ikona(f, e.ikona, 0.14)
		local licznik = self:_ramka(f, {
			-- licznik tur: na telefonie (390 punktów wysokości) cyfra ma ok. 14 punktów (testy/telefon.py)
			Name = "Licznik", AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(1.16, 1.16), Size = UDim2.fromScale(0.62, 0.62),
			BackgroundColor3 = Color3.fromHex(e.kolor), ZIndex = 15,
		}, 2, 0.5, false)
		self:_tekst(licznik, {
			Name = "Tury", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.88, 0.88),
			Font = NAGLOWKI, Text = tostring(e.tury), TextColor3 = self.K.tusz, ZIndex = 16,
		}, 0)
		f:SetAttribute("Tury", e.tury)
		f:SetAttribute("Znaczek", e.znaczek or "")
		if e.znaczek and e.znaczek ~= "" then
			-- stosy trucizny („×3”) albo procent tarczy („−42%”): pigułka w lewym górnym rogu (ok. 14 pkt na telefonie)
			local z = self:_ramka(f, {
				Name = "Znaczek", AnchorPoint = Vector2.new(0, 0), Position = UDim2.fromScale(-0.22, -0.08), Size = UDim2.fromScale(1.3, 0.52),
				BackgroundColor3 = self.K.tusz, ZIndex = 15,
			}, 2, 0.5, false)
			self:_tekst(z, {
				Name = "Tekst", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.9, 0.86),
				Font = NAGLOWKI, Text = e.znaczek, TextColor3 = Color3.fromHex(e.kolor), ZIndex = 16,
			}, 0)
		end
	end
end

function Interfejs:ustawTure(n: number)
	self.tura.Text = if n > 0 then ("TURA " .. tostring(n)) else ""
end

function Interfejs:pokazUmiejetnosc(tekst: string, strona: string)
	local K = self.K
	self.umNapis.Text = wielkie(tekst)
	self.umWstega.BackgroundColor3 = if strona == "gracz" then K.niebieski else K.czerwony
	self.umiejetnosc.Rotation = if strona == "gracz" then -2 else 2
	self.umiejetnosc.Visible = true
	self.umSkala.Scale = 0.4
	TweenService:Create(self.umSkala, TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

function Interfejs:ukryjUmiejetnosc()
	self.umiejetnosc.Visible = false
end

--[[ Komiksowe napisy przy postaciach (styl: zadane, otrzymane, magiczne, blok, unik, krytyk, krytykLiczba, efekt —
	kolor z argumentu, tyk, info).

	Kolejka i stos (poprawka D3 z 15.11, po przeglądzie przebudowane): przy jednej postaci (klucz = strona) widać
	NAJWYŻEJ 3 napisy naraz; kolejne czekają w kolejce i wchodzą co najmniej co ODSTEP_NAPISOW sekund (liczby obrażeń
	mają pierwszeństwo — gdy czekają dłużej niż 0,3 s, najstarszy inny napis gaśnie wcześniej). Napisy jednej postaci
	stoją w stosie w kolejności wejścia (nowy na końcu, nikt się nie przesuwa); miejsce w stosie liczy się z
	NARYSOWANEGO rozmiaru (obrót, gwiazda „KRYTYK!” w każdym obrocie, obrys, powiększenie przy wejściu) i zwalnia się
	dopiero, gdy napis całkiem zgaśnie — wtedy dalsze napisy dojeżdżają płynnie, ale nigdy nie wchodzą na poprzedni.
	Miejsce całego stosu wybiera ocena kandydatów (`_miejsceStosu`): nad postacią, obok niej, pod nią, a przy dużym
	celu także na sylwetce przy zewnętrznym brzegu — nigdy na własnej małej postaci, na głowie dużej, na tabliczkach,
	przyciskach i wstędze; drugi stos omija pierwszy. Wiek napisu liczy się w czasie podanym przez odtwarzacz (w testach
	poklatkowych — w czasie sceny przeliczonym na ×1, więc arkusze i filmy pokazują to samo co gra). ]]
local MAKS_NAPISOW = 3
local ODSTEP_NAPISOW = 0.12
local NADMIAR_WEJSCIA = 1.08 -- największe powiększenie napisu w animacji wejścia (miejsce w stosie liczone z nim)
local LICZBY = { zadane = true, otrzymane = true, magiczne = true, krytykLiczba = true, tyk = true }
local STYLE = {
	zadane = { kolor = "#FFFFFF", rozmiar = 0.12, zycie = 0.95 },
	otrzymane = { kolor = "#FF8A9A", rozmiar = 0.11, zycie = 0.95 },
	magiczne = { kolor = "#C08CFF", rozmiar = 0.12, zycie = 0.95 },
	blok = { kolor = "#7CF3FF", rozmiar = 0.1, zycie = 1.0 },
	unik = { kolor = "#B8FF8A", rozmiar = 0.1, zycie = 1.0 },
	krytyk = { kolor = "#FFE14A", rozmiar = 0.115, zycie = 1.25, gwiazda = true },
	krytykLiczba = { kolor = "#FFE14A", rozmiar = 0.165, zycie = 1.25 },
	wskrzeszenie = { kolor = "#FFE58A", rozmiar = 0.13, zycie = 1.5, gwiazda = true }, -- v3: „WSKRZESZENIE!”
	efekt = { kolor = "#FFFFFF", rozmiar = 0.08, zycie = 1.0 },
	tyk = { kolor = "#FFFFFF", rozmiar = 0.09, zycie = 0.8 },
	info = { kolor = "#E3E7EC", rozmiar = 0.06, zycie = 0.9 },
}
Interfejs.LICZBY = LICZBY

--[[ Rozmiar napisu w stosie (ułamki wysokości kadru): prostokąt po obrocie napisu, gwiazda „KRYTYK!” w każdym
	obrocie (kwadrat 1,15 wysokości kręci się → przekątna 1,63), obrys i cień tekstu, powiększenie w animacji
	wejścia. Przegląd 15.11: stos liczony z samych prostokątów tekstu — gwiazda i wejście nachodziły na sąsiadów. ]]
local function rozmiarNapisu(szer: number, wys: number, obrot: number, gwiazda: boolean): (number, number)
	local a = math.rad(math.abs(obrot))
	local w = szer * math.cos(a) + wys * math.sin(a)
	local h = szer * math.sin(a) + wys * math.cos(a)
	if gwiazda then
		local s = 1.15 * wys * math.sqrt(2)
		w, h = math.max(w, s), math.max(h, s)
	end
	return (w + 0.014) * NADMIAR_WEJSCIA, (h + 0.014) * NADMIAR_WEJSCIA
end

-- szerokość tekstu w czcionce napisów jako ułamek jego wysokości (z pamięcią: te same napisy wracają co walkę)
local TextService = game:GetService("TextService")
local szerokosci = {}
local function szerokoscTekstu(tekst: string): number
	local w = szerokosci[tekst]
	if w then
		return w
	end
	local ok, v = pcall(function()
		return TextService:GetTextSize(tekst, 100, KOMIKS, Vector2.new(10000, 10000))
	end)
	w = if ok and v then v.X / 100 else 0.6 * (utf8.len(tekst) or #tekst)
	szerokosci[tekst] = w
	return w
end

-- napis do kolejki; klucz = postać, przy której stoi ("gracz" / "wrog"); przesuniecie zostaje dla zgodności (stos
-- układa się sam)
function Interfejs:napis(punkt: Vector3, tekst: string, styl: string, _przesuniecie: Vector2?, obrot: number?, kolor: Color3?, klucz: string?)
	local def = STYLE[styl] or STYLE.zadane
	self.licznikNapisow = (self.licznikNapisow or 0) + 1
	local wys = def.rozmiar
	-- szerokość z prawdziwej szerokości tekstu w tej czcionce (Bangers ma ok. 0,37 wysokości na znak; wcześniej
	-- 0,6 na znak — stos rezerwował o 60% za szerokie miejsce i długie napisy efektów nie mieściły się obok celu)
	local naWys = szerokoscTekstu(tekst)
	local szer = def.rozmiar * math.max(1.2, naWys * 1.12)
	-- długi napis obraca się mniej: obrócony prostokąt „ZDARTY PANCERZ!” byłby wysoki jak dwa napisy
	local maksObrot = math.min(8, math.deg(math.asin(math.clamp(0.3 * wys / szer, 0, 1))))
	local o = math.clamp(obrot or 0, -maksObrot, maksObrot)
	local lw, lh = rozmiarNapisu(szer, wys, o, def.gwiazda == true)
	table.insert(self.kolejkaNapisow, {
		punkt = punkt, tekst = tekst, styl = styl, def = def, obrot = o, kolor = kolor, klucz = klucz or "?",
		prio = if LICZBY[styl] then 3 elseif styl == "krytyk" or styl == "blok" or styl == "unik" or styl == "wskrzeszenie" then 2 else 1,
		nr = self.licznikNapisow, czeka = 0, zycie = def.zycie * (self.skalaZycia or 1), wys = wys, szer = szer,
		lw = lw, lh = lh,
	})
	self:_wpuscNapisy()
end

-- z kolejki na ekran: najwyżej MAKS_NAPISOW przy postaci, kolejne co ODSTEP_NAPISOW; liczby najpierw
function Interfejs:_wpuscNapisy()
	local kolejka = self.kolejkaNapisow
	if #kolejka == 0 then
		return
	end
	local ile = {}
	for _, n in self.napisy do
		ile[n.klucz] = (ile[n.klucz] or 0) + 1
	end
	local i = 1
	while i <= #kolejka do
		local n = kolejka[i]
		local k = n.klucz
		local ostatnio = self.ostatnieWejscie[k]
		local wolno = (ile[k] or 0) < MAKS_NAPISOW and (ostatnio == nil or self.zegarNapisow - ostatnio >= ODSTEP_NAPISOW - 1e-6)
		if wolno then
			-- najważniejszy czekający przy tej postaci (liczba przed resztą, potem kolejność)
			local najlepszy = i
			for j = i + 1, #kolejka do
				local m = kolejka[j]
				if m.klucz == k and m.prio > kolejka[najlepszy].prio then
					najlepszy = j
				end
			end
			local wybrany = table.remove(kolejka, najlepszy)
			self:_pokazNapis(wybrany)
			ile[k] = (ile[k] or 0) + 1
			self.ostatnieWejscie[k] = self.zegarNapisow
		else
			i += 1
		end
	end
end

function Interfejs:_pokazNapis(n)
	local def = n.def
	local styl = n.styl
	local K = self.K
	local tekst = n.tekst
	local pole = self:_nowy("Frame", {
		Name = "Napis_" .. styl, BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Size = UDim2.fromOffset(100, 100), Rotation = n.obrot, ZIndex = 20, Visible = false,
	}, self.warstwaNapisow)
	local skala = self:_nowy("UIScale", { Scale = 0.2 }, pole)
	local gwiazda = {}
	if def.gwiazda then
		for i = 1, 2 do
			local g = self:_nowy("Frame", {
				Name = "Gwiazda" .. i, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
				Size = UDim2.fromScale(1.15, 1.15), SizeConstraint = Enum.SizeConstraint.RelativeYY,
				BackgroundColor3 = if i == 1 then K.pomarancz else K.czerwony, BorderSizePixel = 0, Rotation = (i - 1) * 45 + 12, ZIndex = 20,
			}, pole)
			self:_obrys(g, 4)
			gwiazda[i] = g
		end
	end
	local cien = self:_tekst(pole, {
		Name = "Cien", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 3, 0.5, 4), Size = UDim2.fromScale(1, 1),
		Font = KOMIKS, Text = tekst, TextColor3 = K.tusz, ZIndex = 21,
	}, if styl == "info" then 3 else 5)
	local napis = self:_tekst(pole, {
		Name = "Tekst", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(1, 1),
		Font = KOMIKS, Text = tekst, TextColor3 = n.kolor or Color3.fromHex(def.kolor), ZIndex = 22,
	}, if styl == "info" then 3 else 4.5)
	n.pole, n.skala, n.cien, n.napis, n.gwiazda, n.wiek = pole, skala, cien, napis, gwiazda, 0
	self.licznikWejsc = (self.licznikWejsc or 0) + 1
	n.wejscie = self.licznikWejsc
	table.insert(self.napisy, n)
	self.statNapisow.pokazane += 1
end

--[[ Miejsce stosu napisów jednej postaci (przegląd 15.11: stos nad postacią albo obok niej i wyjątek „duży cel”
	przykrywały głowę Strażnika, małego wilka i siebie nawzajem). Kandydaci: nad postacią, obok (dalej / bliżej
	przeciwnika), pod nią, a przy dużym celu także na jego sylwetce przy zewnętrznym brzegu — każdy w kilku miejscach.
	Ocena kandydata (mniej = lepiej):
	  • twarde (bardzo drogie): poza kadrem, na tabliczkach, przyciskach i wstędze, na drugim stosie, na własnej
	    postaci, gdy jest mała (< 40% wysokości kadru), na głowie postaci (prostokąt górnej części), na małym przeciwniku;
	  • miękkie: odległość od postaci, nachodzenie na dużego przeciwnika i na własną sylwetkę dużego celu, zmiana
	    miejsca względem poprzedniej klatki (stos nie skacze), „pod” i „na” trochę gorsze od „nad” i „obok”.
	Wynik: prostokąt stosu, kierunek wzrostu (−1 w górę od postaci, +1 w dół) i klucz miejsca. ]]
local function pole2(a, b): number
	local w = math.min(a.x1, b.x1) - math.max(a.x0, b.x0)
	local h = math.min(a.y1, b.y1) - math.max(a.y0, b.y0)
	if w <= 0 or h <= 0 then
		return 0
	end
	return w * h
end
Interfejs.wspolnePole = pole2

function Interfejs:_zakazane()
	local kadr = self.kadrPx
	local wynik = {}
	local function dodaj(x0, y0, x1, y1)
		table.insert(wynik, { x0 = kadr.x + kadr.sz * x0, y0 = kadr.y + kadr.wys * y0, x1 = kadr.x + kadr.sz * x1, y1 = kadr.y + kadr.wys * y1 })
	end
	local g = (self.gornyMargines or 0.045) - 0.045
	if self.paski.gracz and self.paski.gracz.tabliczka.Visible then
		-- v3: tabliczka 0,15 z paskiem many, ikony efektów do ok. 0,30 kadru
		dodaj(0, 0, 0.43, 0.305 + g) -- tabliczka gracza z maną, rangą i ikonami efektów
		dodaj(0.57, 0, 1, 0.305 + g) -- tabliczka przeciwnika
		dodaj(0.43, 0, 0.57, 0.225 + g) -- VS i licznik tury
	end
	if self.umiejetnosc and self.umiejetnosc.Visible then
		if self.wstegaNaDole then
			dodaj(0.31, 0.85, 0.69, 1)
		else
			dodaj(0.28, 0.255 + g, 0.72, 0.345 + g)
		end
	end
	for strona, z in self.pasywki or {} do
		if z.ramka.Visible then
			if strona == "gracz" then
				dodaj(0, 0.3 + g, 0.48, 0.415 + g)
			else
				dodaj(0.52, 0.3 + g, 1, 0.415 + g)
			end
		end
	end
	if self.baner and self.baner.Visible then
		dodaj(0.08, 0.2, 0.92, 0.44)
	end
	dodaj(0, 0.835, 1, 1) -- przyciski tempa, dźwięku i POMIŃ
	return wynik
end

function Interfejs:_miejsceStosu(klucz: string, W: number, Hs: number, R, O, przeszkody, poprzedni: string?)
	local kadr = self.kadrPx
	local kw = kadr.wys
	local odstep = math.max(4, kw * 0.014)
	local L, P = kadr.x + 4, kadr.x + kadr.sz - 4
	local T, B = kadr.y + kw * 0.04, kadr.y + kw * 0.98
	local Rh = R.y1 - R.y0
	local duzy = Rh >= kw * 0.4
	local cx, cy = (R.x0 + R.x1) / 2, (R.y0 + R.y1) / 2
	local dalej = "lewo"
	if O and (O.x0 + O.x1) / 2 < cx then
		dalej = "prawo"
	end
	local G = R.glowa
	local OG = O and O.glowa
	local oMaly = O and (O.y1 - O.y0) < kw * 0.4
	local najlepszy, najKoszt, najKlucz, najKier = nil, math.huge, nil, -1
	local poprzKoszt, poprzProst, poprzKier = nil, nil, nil
	local function ocen(nazwa: string, x: number, y: number, kier: number, kara: number)
		x = math.clamp(x, L, math.max(L, P - W))
		y = math.clamp(y, T, math.max(T, B - Hs))
		local p = { x0 = x, y0 = y, x1 = x + W, y1 = y + Hs }
		local pp = W * Hs
		local twarde = 0
		for _, z in przeszkody do
			twarde += pole2(p, z) / pp * (z.waga or 1000)
		end
		if not duzy then
			twarde += pole2(p, R) / pp * 100
		elseif G then
			twarde += pole2(p, G) / math.max(1, (G.x1 - G.x0) * (G.y1 - G.y0)) * 100
		end
		local miekkie = 0
		if O then
			if oMaly then
				twarde += pole2(p, O) / pp * 30
			else
				miekkie += pole2(p, O) / pp * 2
				if OG then
					twarde += pole2(p, OG) / math.max(1, (OG.x1 - OG.x0) * (OG.y1 - OG.y0)) * 30
				end
			end
		end
		if duzy then
			miekkie += pole2(p, R) / pp * 1.2
		end
		-- odległość stosu od postaci (0 = przylega)
		local dx = math.max(R.x0 - p.x1, 0, p.x0 - R.x1)
		local dy = math.max(R.y0 - p.y1, 0, p.y0 - R.y1)
		miekkie += math.sqrt(dx * dx + dy * dy) / kw * 2.5
		miekkie += kara
		local koszt = twarde + miekkie
		if nazwa == poprzedni then
			poprzKoszt, poprzProst, poprzKier = koszt, p, kier
		end
		if koszt < najKoszt then
			najlepszy, najKoszt, najKlucz, najKier = p, koszt, nazwa, kier
		end
	end
	local xs = { cx - W / 2, R.x0, R.x1 - W, cx - W, cx }
	for i, x in xs do
		ocen("nad" .. i, x, R.y0 - odstep - Hs, -1, 0)
		ocen("pod" .. i, x, R.y1 + odstep, 1, 0.12)
	end
	local ys = { R.y0 + Rh * 0.08, cy - Hs / 2, R.y1 - Hs, R.y0 - Hs * 0.5 }
	for i, y in ys do
		ocen("prawo" .. i, R.x1 + odstep, y, 1, if dalej == "prawo" then 0 else 0.06)
		ocen("lewo" .. i, R.x0 - odstep - W, y, 1, if dalej == "lewo" then 0 else 0.06)
	end
	if duzy then
		local yG = if G then G.y1 + odstep else R.y0 + Rh * 0.3
		for i, y in { yG, cy - Hs / 2, R.y1 - Hs - Rh * 0.08 } do
			local x = if dalej == "prawo" then R.x1 - W - Rh * 0.02 else R.x0 + Rh * 0.02
			ocen("na" .. i, x, y, 1, 0.3)
		end
	end
	-- stabilność: zostań na poprzednim miejscu, gdy jest prawie tak dobre (bez twardych kar)
	if poprzKoszt and poprzKoszt < 1 and poprzKoszt <= najKoszt + 0.25 then
		return poprzProst, poprzKier, poprzedni, poprzKoszt
	end
	return najlepszy, najKier, najKlucz, najKoszt
end

-- kotwice napisów: prostokąty postaci na ekranie (piksele) — ustawia odtwarzacz co klatkę
function Interfejs:ustawKotwice(kotwice)
	self.kotwice = kotwice
end

function Interfejs:pokazBaner(tekst: string, kolorNapisu: Color3, kolorWstegi: Color3, wysokosc: number?)
	self.baner.Position = UDim2.fromScale(0.5, wysokosc or 0.31)
	self.banerNapis.Text = tekst
	self.banerCien.Text = tekst
	self.banerNapis.TextColor3 = kolorNapisu
	self.banerWstega.BackgroundColor3 = kolorWstegi
	self.baner.Visible = true
	self.banerSkala.Scale = 0.3
	TweenService:Create(self.banerSkala, TweenInfo.new(0.28, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

function Interfejs:ukryjBaner(natychmiast: boolean?)
	if not self.baner.Visible then
		return
	end
	if natychmiast then
		self.baner.Visible = false
		return
	end
	local tw = TweenService:Create(self.banerSkala, TweenInfo.new(0.16, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.01 })
	tw.Completed:Once(function()
		if not self.zniszczony and self.banerSkala.Scale < 0.05 then
			self.baner.Visible = false
		end
	end)
	tw:Play()
end

function Interfejs:pokazPomin(funkcja: () -> ())
	self.pomin.Visible = true
	if self.polaczeniePomin then
		self.polaczeniePomin:Disconnect()
	end
	self.polaczeniePomin = self.pominPrzycisk.Activated:Connect(funkcja)
end

function Interfejs:ukryjPomin()
	self.pomin.Visible = false
end

-- przyciski tempa: aktywne = 1 | 2 | 4; naZmiane(t)
function Interfejs:pokazTempo(aktywne: number, naZmiane: (number) -> ())
	self.tempoPas.Visible = true
	self.polaczeniaTempa = self.polaczeniaTempa or {}
	for _, c in self.polaczeniaTempa do
		c:Disconnect()
	end
	table.clear(self.polaczeniaTempa)
	for t, pr in self.tempoPrzyciski do
		table.insert(self.polaczeniaTempa, pr.przycisk.Activated:Connect(function()
			naZmiane(t)
		end))
	end
	self:ustawTempo(aktywne)
end

function Interfejs:ustawTempo(aktywne: number)
	for t, pr in self.tempoPrzyciski do
		local wl = t == aktywne
		pr.przycisk.BackgroundColor3 = if wl then self.K.zolty else self.K.szary
		local n = pr.przycisk:FindFirstChild("Napis")
		if n then
			n.TextColor3 = if wl then self.K.tusz else self.K.bialy
		end
		pr.przycisk:SetAttribute("Aktywny", wl)
	end
end

function Interfejs:ukryjTempo()
	self.tempoPas.Visible = false
end

-- odmiana liczebnika: 1 tura, 2–4 tury (ale 12–14 tur), 5+ tur; 22 tury, 25 tur
function Interfejs.liczebnik(n: number, jeden: string, kilka: string, wiele: string): string
	local forma
	if n == 1 then
		forma = jeden
	elseif n % 10 >= 2 and n % 10 <= 4 and (n % 100 < 12 or n % 100 > 14) then
		forma = kilka
	else
		forma = wiele
	end
	return tostring(n) .. " " .. forma
end

-- „w 1 turze”, „w 3 turach”
function Interfejs.wTurach(n: number): string
	return if n == 1 then "w 1 turze" else ("w " .. tostring(n) .. " turach")
end

function Interfejs:pokazWynik(walka, naJeszczeRaz: () -> (), naZamknij: () -> ())
	local K = self.K
	local w = self.wynik
	local wygrana = walka.wynik == "wygrana"
	local tytul = if wygrana then "ZWYCIĘSTWO!" else "PORAŻKA!"
	w.tytul.Text = tytul
	w.tytulCien.Text = tytul
	w.tytul.TextColor3 = if wygrana then K.zolty else K.bialy
	w.wstega.BackgroundColor3 = if wygrana then K.pomarancz else K.fiolet
	local wrog = walka.strony.wrog
	w.podtytul.Text = if wygrana
		then string.format("%s (poz. %d) pokonany %s", wrog.nazwa, wrog.poziom, Interfejs.wTurach(walka.tury))
		else string.format("%s (poz. %d) był silniejszy — %s", wrog.nazwa, wrog.poziom, Interfejs.liczebnik(walka.tury, "tura", "tury", "tur"))
	local lup = walka.lup
	local wartosci = { lup.zloto, lup.doswiadczenie, lup.tokeny_krainy, lup.gemy, lup.shard_ewolucji }
	local kafelTokenow = w.kafle[3]
	if kafelTokenow and kafelTokenow.podpis then
		kafelTokenow.podpis.Text = NAPISY_TOKENOW[tostring(lup.kraina or "")] or "TOKENY"
	end
	w.liczniki = {}
	for i, kafel in w.kafle do
		local v = wartosci[i] or 0
		local jest = v > 0
		kafel.ramka.BackgroundColor3 = if jest then (if i >= 4 then Color3.fromHex("#FFF6C9") else K.bialy) else Color3.fromHex("#D9D3C4")
		kafel.wartosc.TextColor3 = if jest then K.tusz else K.szary
		kafel.wartosc.Text = if jest then "+0" else "—"
		kafel.ramka:SetAttribute("Wartosc", v)
		for _, piksel in kafel.ikona:GetDescendants() do
			if piksel:IsA("Frame") and piksel.Name ~= "Ikona" then
				piksel.BackgroundTransparency = if jest then 0 else 0.65
			end
		end
		if jest then
			table.insert(w.liczniki, { etykieta = kafel.wartosc, cel = v, start = 0.25 + (i - 1) * 0.14, trwa = if v > 5 then 0.45 else 0.2 })
		end
		kafel.skala.Scale = 0.01
		task.delay(0.12 + (i - 1) * 0.08, function()
			if not self.zniszczony then
				TweenService:Create(kafel.skala, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
			end
		end)
	end
	w.czasPokazania = 0
	w.blokadaPokazana = nil
	-- JESZCZE RAZ widoczne na starcie; odtwarzacz chowa je zaraz potem w walkach w lesie (opcja bezPowtorki). Stopka
	-- (ziarno, liczba zdarzeń) to napis dla twórców: widać ją tylko w trybie próby z JESZCZE RAZ (aktualizuj).
	local ramkaJeszcze = w.jeszcze.Parent
	if ramkaJeszcze and ramkaJeszcze:IsA("GuiObject") then
		ramkaJeszcze.Visible = true
	end
	w.stopka.Visible = false
	w.pokazanoO = os.clock()
	w.naZamknij = naZamknij
	ContextActionService:BindActionAtPriority(AKCJA_ZAMKNIJ_WYNIK, function(_, stanWejscia)
		if stanWejscia == Enum.UserInputState.Begin and w.uchwyt.Visible and w.naZamknij
			and os.clock() - (w.pokazanoO or 0) >= ZAMKNIJ_WYNIK_PO then
			local f = w.naZamknij
			w.naZamknij = nil
			f()
		end
		return Enum.ContextActionResult.Sink
	end, false, 10002, Enum.KeyCode.Space, Enum.KeyCode.ButtonB)
	w.stopka.Text = string.format("dziennik policzył serwer  •  ziarno %s  •  %s  •  %s  •  %.1f s",
		tostring(walka.ziarno), Interfejs.liczebnik(walka.tury, "tura", "tury", "tur"),
		Interfejs.liczebnik(#walka.dziennik, "zdarzenie", "zdarzenia", "zdarzeń"), walka.czas)
	if w.polJeszcze then
		w.polJeszcze:Disconnect()
	end
	if w.polZamknij then
		w.polZamknij:Disconnect()
	end
	w.polJeszcze = w.jeszcze.Activated:Connect(naJeszczeRaz)
	w.polZamknij = w.zamknij.Activated:Connect(naZamknij)
	w.uchwyt.Position = UDim2.fromScale(if wygrana then 0.66 else 0.34, 0.58)
	w.uchwyt.Visible = true
	self.wynikSkala.Scale = 0.55
	TweenService:Create(self.wynikSkala, TweenInfo.new(0.32, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

function Interfejs:ustawBlokadeJeszczeRaz(zostalo: number)
	local w = self.wynik
	local sekundy = if zostalo > 0 then math.ceil(zostalo) else 0
	if w.blokadaPokazana == sekundy then
		return
	end
	w.blokadaPokazana = sekundy
	local napis = w.jeszcze:FindFirstChild("Napis")
	w.jeszcze.BackgroundColor3 = if sekundy > 0 then self.K.szary else self.K.zielony
	if napis then
		napis.Text = if sekundy > 0 then string.format("ZA %d s", sekundy) else "JESZCZE RAZ"
	end
	w.jeszcze:SetAttribute("Zablokowany", sekundy > 0)
end

function Interfejs:ukryjWynik()
	self.wynik.uchwyt.Visible = false
	self.wynik.liczniki = {}
	self.wynik.naZamknij = nil
	ContextActionService:UnbindAction(AKCJA_ZAMKNIJ_WYNIK)
end

function Interfejs:ustawZaslone(krycie: number)
	self.zaslona.BackgroundTransparency = 1 - math.clamp(krycie, 0, 1)
end

function Interfejs:ustawZegar(tekst: string?)
	self.zegar.Visible = tekst ~= nil
	if tekst then
		self.zegar.Text = tekst
	end
end

function Interfejs:pokazPaski(widoczne: boolean)
	for _, p in self.paski do
		p.tabliczka.Visible = widoczne
	end
	self.vs.Visible = widoczne
	self.tura.Visible = widoczne
end

function Interfejs:usunNapisy()
	for _, n in self.napisy do
		n.pole:Destroy()
	end
	table.clear(self.napisy)
	table.clear(self.kolejkaNapisow)
	table.clear(self.ostatnieWejscie)
	table.clear(self.trybNapisow)
	table.clear(self.skalaStosu)
end

-- statystyki napisów do testów (zerowane na początku walki)
function Interfejs:zerujStatystykiNapisow()
	self.statNapisow = { maksNaraz = 0, nakladania = 0, naCelu = 0, naInnym = 0, naGlowie = 0, pokazane = 0 }
end

-- napisy: kolejka, wiek, stos przy kotwicy, zanik; dtNapisow = czas napisów (domyślnie dt)
function Interfejs:_aktualizujNapisy(dtNapisow: number, kamera: Camera)
	self.zegarNapisow += dtNapisow
	-- liczby czekające w kolejce dłużej niż 0,3 s: najstarszy inny napis przy tej postaci gaśnie wcześniej
	for _, q in self.kolejkaNapisow do
		q.czeka += dtNapisow
		if q.czeka > 0.3 then
			local ofiara = nil
			for _, n in self.napisy do
				if n.klucz == q.klucz and n.wiek < n.zycie * 0.74 and (n.prio < q.prio or q.czeka > 0.6)
					and (ofiara == nil or n.nr < ofiara.nr) then
					ofiara = n
				end
			end
			if ofiara then
				ofiara.wiek = ofiara.zycie * 0.74
			end
		end
	end
	-- wiek i koniec życia (miejsce w stosie zwalnia się dopiero, gdy napis całkiem zgaśnie)
	for i = #self.napisy, 1, -1 do
		local n = self.napisy[i]
		n.wiek += dtNapisow
		if n.wiek >= n.zycie then
			n.pole:Destroy()
			table.remove(self.napisy, i)
		end
	end
	self:_wpuscNapisy()
	if #self.napisy == 0 then
		self.prostokatyNapisow = {}
		return
	end
	local kadr = self.kadrPx
	local kw = kadr.wys
	local odstep = math.max(4, kw * 0.014)
	-- grupy przy postaciach, w kolejności wejścia (nowy napis idzie na koniec stosu — nikt się nie przesuwa)
	local grupy = {}
	for _, n in self.napisy do
		grupy[n.klucz] = grupy[n.klucz] or {}
		table.insert(grupy[n.klucz], n)
	end
	local kolejnosc = {}
	for klucz, lista in grupy do
		table.sort(lista, function(a, b)
			return a.wejscie < b.wejscie
		end)
		local prio = 0
		for _, n in lista do
			prio = math.max(prio, n.prio)
		end
		table.insert(kolejnosc, { klucz = klucz, lista = lista, prio = prio })
		self.statNapisow.maksNaraz = math.max(self.statNapisow.maksNaraz, #lista)
	end
	-- najpierw stos z liczbą obrażeń (cel), drugi omija pierwszy
	table.sort(kolejnosc, function(a, b)
		if a.prio ~= b.prio then
			return a.prio > b.prio
		end
		return a.klucz < b.klucz
	end)
	local przeszkody = self:_zakazane()
	local stosy = {}
	for _, g in kolejnosc do
		local klucz, lista = g.klucz, g.lista
		local R = self.kotwice[klucz]
		if not R then
			-- bez kotwicy (np. stary klucz): mały prostokąt w punkcie napisu
			local e = kamera:WorldToViewportPoint(lista[1].punkt)
			R = { x0 = e.X - 10, y0 = e.Y - 10, x1 = e.X + 10, y1 = e.Y + 10, widac = e.Z > 0 }
		end
		local O = nil
		for k2, r2 in self.kotwice do
			if k2 ~= klucz then
				O = r2
			end
		end
		-- przesunięcia napisów wzdłuż stosu (od strony postaci): po zgaśnięciu napisu dalsze dojeżdżają płynnie, ale
		-- nigdy nie wchodzą na poprzedni (pchnięcie w pętli); stos zajmuje tyle, ile sięga ostatni (także w dojeździe)
		local wygladz = 1 - math.exp(-dtNapisow * 14)
		local skala = 1
		local function przesuniecia(odNowa: boolean): (number, number)
			local W, zajete = 0, 0
			for _, n in lista do
				local h = n.lh * kw * skala
				W = math.max(W, n.lw * kw * skala)
				if n.przes == nil or odNowa then
					n.przes = zajete
				else
					n.przes += (zajete - n.przes) * wygladz
					n.przes = math.max(n.przes, zajete) -- nie bliżej postaci, niż pozwala poprzedni napis
				end
				zajete = n.przes + h + odstep
			end
			return W, zajete - odstep
		end
		local stare = {}
		for i, n in lista do
			stare[i] = n.przes
		end
		--[[ Gdy stos nigdzie się nie mieści bez twardej kary (mały cel w rogu kadru, obok tabliczki i przyciski —
			przegląd 15.11: „KRYTYK!” lądował na małym slimie przy ×4), napisy tej postaci maleją: 0,85, potem 0,7
			(na telefonie 844 × 390 najmniejszy napis efektu to wtedy ok. 22 punkty). ]]
		local W, Hs, prost, kier, miejsce
		for _, sk in { 1, 0.85, 0.7 } do
			skala = sk
			for i, n in lista do
				n.przes = stare[i]
			end
			W, Hs = przesuniecia(false)
			local koszt
			prost, kier, miejsce, koszt = self:_miejsceStosu(klucz, W, Hs, R, O, przeszkody, self.trybNapisow[klucz])
			if koszt < 1 then
				break
			end
		end
		local innaSkala = skala ~= (self.skalaStosu[klucz] or 1)
		self.skalaStosu[klucz] = skala
		if miejsce ~= self.trybNapisow[klucz] or innaSkala then
			-- nowe miejsce stosu: napisy od razu na swoich miejscach (bez przejazdu przez postać)
			for i, n in lista do
				n.przes = stare[i]
			end
			W, Hs = przesuniecia(true)
			prost = { x0 = prost.x0, y0 = if kier < 0 then prost.y1 - Hs else prost.y0, x1 = prost.x1,
				y1 = if kier < 0 then prost.y1 else prost.y0 + Hs }
		end
		self.trybNapisow[klucz] = miejsce
		table.insert(przeszkody, { x0 = prost.x0 - 3, y0 = prost.y0 - 3, x1 = prost.x1 + 3, y1 = prost.y1 + 3, waga = 500 })
		stosy[klucz] = { lista = lista, prost = prost, kier = kier, R = R, skala = skala }
	end
	-- pozycje, skala i zanik; prostokąty NARYSOWANE (z animacją wejścia, obrotem i gwiazdą) do pomiaru
	local prostokaty = {}
	for _, s in stosy do
		local p = s.prost
		for _, n in s.lista do
			local h = n.lh * kw * s.skala
			local cx = (p.x0 + p.x1) / 2
			local cy = if s.kier < 0 then p.y1 - n.przes - h / 2 else p.y0 + n.przes + h / 2
			n.x, n.y = cx, cy
			local wysPx = n.wys * kw * s.skala
			local szerPx = n.szer * kw * s.skala
			n.pole.Visible = s.R.widac ~= false
			n.pole.Position = UDim2.fromOffset(cx, cy)
			n.pole.Size = UDim2.fromOffset(szerPx, wysPx)
			local sk
			if n.wiek < 0.1 then
				sk = 0.2 + (NADMIAR_WEJSCIA - 0.2) * (n.wiek / 0.1)
			elseif n.wiek < 0.2 then
				sk = NADMIAR_WEJSCIA - (NADMIAR_WEJSCIA - 1) * ((n.wiek - 0.1) / 0.1)
			else
				sk = 1
			end
			n.skala.Scale = sk
			local zanik = math.clamp((n.wiek / n.zycie - 0.74) / 0.26, 0, 1)
			if zanik > 0 or n.zanikal then
				n.zanikal = true
				n.napis.TextTransparency = zanik
				n.cien.TextTransparency = zanik
				for _, d in n.pole:GetDescendants() do
					if d:IsA("UIStroke") then
						d.Transparency = zanik
					elseif d:IsA("Frame") then
						d.BackgroundTransparency = zanik
					end
				end
			end
			local obrotGwiazdy = nil
			for j, g in n.gwiazda do
				g.Rotation += dtNapisow * (if j == 1 then 40 else -55)
				obrotGwiazdy = g.Rotation
			end
			-- prostokąt narysowany: tekst po obrocie (+ obrys i cień), gwiazda w bieżącym obrocie, skala wejścia
			local a = math.rad(math.abs(n.obrot))
			local w = szerPx * math.cos(a) + wysPx * math.sin(a)
			local hh = szerPx * math.sin(a) + wysPx * math.cos(a)
			if #n.gwiazda > 0 then
				local bok = 1.15 * wysPx
				local maks = 0
				for _, g in n.gwiazda do
					local r = math.rad(g.Rotation + n.obrot)
					maks = math.max(maks, bok * (math.abs(math.cos(r)) + math.abs(math.sin(r))))
				end
				w, hh = math.max(w, maks), math.max(hh, maks)
			end
			local m = 0.007 * kw
			w, hh = (w + 2 * m) * sk, (hh + 2 * m) * sk
			local _ = obrotGwiazdy
			table.insert(prostokaty, { n = n, x0 = cx - w / 2, y0 = cy - hh / 2, x1 = cx + w / 2, y1 = cy + hh / 2, R = s.R,
				widoczny = (s.R.widac ~= false) and zanik < 0.9 })
		end
	end
	-- pomiar (D3): nakładanie się narysowanych napisów (także w wejściu i wygaszaniu), napis na małym celu (każdy,
	-- nie tylko liczba), ułamek głowy dużego celu przykryty napisami
	local zle = false
	for i = 1, #prostokaty do
		local a = prostokaty[i]
		if a.widoczny then
			for j = i + 1, #prostokaty do
				local b = prostokaty[j]
				if b.widoczny and pole2(a, { x0 = b.x0 + 2, y0 = b.y0 + 2, x1 = b.x1 - 2, y1 = b.y1 - 2 }) > 0 then
					zle = true
				end
			end
		end
	end
	if zle then
		self.statNapisow.nakladania += 1
	end
	local naCelu, naInnym = false, false
	local glowy = {}
	for _, p in prostokaty do
		if p.widoczny then
			for k, R in self.kotwice do
				local maly = R.y1 - R.y0 < kw * 0.4
				if maly and pole2(p, { x0 = R.x0 + 3, y0 = R.y0 + 3, x1 = R.x1 - 3, y1 = R.y1 - 3 }) > 0 then
					if k == p.n.klucz then
						naCelu = true
					else
						naInnym = true
					end
				end
				if R.glowa and not maly then
					glowy[k] = (glowy[k] or 0) + pole2(p, R.glowa)
				end
			end
		end
	end
	if naCelu then
		self.statNapisow.naCelu += 1
	end
	if naInnym then
		self.statNapisow.naInnym = (self.statNapisow.naInnym or 0) + 1
	end
	for k, pole in glowy do
		local G = self.kotwice[k].glowa
		local u = pole / math.max(1, (G.x1 - G.x0) * (G.y1 - G.y0))
		self.statNapisow.naGlowie = math.max(self.statNapisow.naGlowie or 0, u)
	end
	self.prostokatyNapisow = prostokaty
end

function Interfejs:aktualizuj(dt: number, kamera: Camera, dtNapisow: number?)
	for _, p in self.paski do
		if p.pokazane ~= p.cel then
			p.pokazane += (p.cel - p.pokazane) * math.min(1, dt * 14)
			if math.abs(p.pokazane - p.cel) < 0.002 then
				p.pokazane = p.cel
			end
			p.wypelnienie.Size = UDim2.fromScale(math.max(p.pokazane, 0.001), 1)
			p.wypelnienie.Visible = p.pokazane > 0.004
		end
		if p.duchCzeka > 0 then
			p.duchCzeka -= dt
		elseif p.duchPokazany ~= p.cel then
			p.duchPokazany += (p.cel - p.duchPokazany) * math.min(1, dt * 7)
			if math.abs(p.duchPokazany - p.cel) < 0.002 then
				p.duchPokazany = p.cel
			end
		end
		p.duch.Size = UDim2.fromScale(math.max(p.duchPokazany, 0.001), 1)
		p.duch.Visible = p.duchPokazany > p.pokazane + 0.003
		if p.wstrzas > 0 then
			p.wstrzas = math.max(0, p.wstrzas - dt * 5)
			p.tabliczka.Rotation = p.obrotBazowy + math.sin(p.wstrzas * 40) * 2.2 * p.wstrzas
		end
		-- wskrzeszenie: złoty blask paska życia gaśnie w ok. 1 s
		if p.blaskZyciaCzas > 0 then
			p.blaskZyciaCzas = math.max(0, p.blaskZyciaCzas - dt)
			p.blaskZycia.BackgroundTransparency = 1 - 0.75 * p.blaskZyciaCzas
		end
		-- mana: płynny ruch do wartości z dziennika, błysk przy użyciu, puls kryształu przy gotowej
		local m = p.mana
		m.wiek += dt
		if m.pokazane ~= m.cel then
			local szybkosc = if m.cel < m.pokazane then 9 else 6
			m.pokazane += (m.cel - m.pokazane) * math.min(1, dt * szybkosc)
			if math.abs(m.pokazane - m.cel) < 0.002 then
				m.pokazane = m.cel
			end
			self:_rysujMane(m)
		end
		if m.blyskCzas > 0 then
			m.blyskCzas = math.max(0, m.blyskCzas - dt)
			m.blysk.BackgroundTransparency = 1 - math.min(1, m.blyskCzas / 0.45) * 0.85
		elseif m.blysk.BackgroundTransparency < 1 then
			m.blysk.BackgroundTransparency = 1
		end
		if m.gotowa then
			m.krysztalSkala.Scale = 1 + 0.18 * (0.5 + 0.5 * math.sin(m.wiek * 9))
			m.blysk.BackgroundTransparency = math.min(m.blysk.BackgroundTransparency, 0.82 - 0.12 * math.sin(m.wiek * 9))
		end
	end
	self:_aktualizujPasywki(dt)
	if self.pominInfoCzas > 0 then
		self.pominInfoCzas -= dt
		if self.pominInfoCzas <= 0 then
			self.pominInfo.Visible = false
		end
	end
	if #self.napisy > 0 or #self.kolejkaNapisow > 0 then
		self:_aktualizujNapisy(if dtNapisow ~= nil then dtNapisow else dt, kamera)
	end
	local w = self.wynik
	if w.uchwyt.Visible then
		local ramkaJeszcze = w.jeszcze.Parent
		local proba = ramkaJeszcze ~= nil and ramkaJeszcze:IsA("GuiObject") and ramkaJeszcze.Visible
		if w.stopka.Visible ~= proba then
			w.stopka.Visible = proba
		end
	end
	if w.uchwyt.Visible and #w.liczniki > 0 then
		w.czasPokazania += dt
		for i = #w.liczniki, 1, -1 do
			local l = w.liczniki[i]
			local u = (w.czasPokazania - l.start) / l.trwa
			if u >= 1 then
				l.etykieta.Text = "+" .. tostring(l.cel)
				table.remove(w.liczniki, i)
			elseif u > 0 then
				l.etykieta.Text = "+" .. tostring(math.floor(l.cel * gladko(u) + 0.5))
			end
		end
	end
end

-- liczba obrażeń pokazywana na pasku (do testu zgodności z dziennikiem)
function Interfejs:zycie(strona: string): number?
	local p = self.paski[strona]
	return p and p.hp
end

function Interfejs:zniszcz()
	if self.zniszczony then
		return
	end
	self.zniszczony = true
	for _, p in self.polaczenia do
		p:Disconnect()
	end
	if self.polaczeniePomin then
		self.polaczeniePomin:Disconnect()
	end
	if self.polaczenieDzwieku then
		self.polaczenieDzwieku:Disconnect()
	end
	for _, c in self.polaczeniaTempa or {} do
		c:Disconnect()
	end
	if self.wynik.polJeszcze then
		self.wynik.polJeszcze:Disconnect()
	end
	if self.wynik.polZamknij then
		self.wynik.polZamknij:Disconnect()
	end
	self.wynik.naZamknij = nil
	ContextActionService:UnbindAction(AKCJA_ZAMKNIJ_WYNIK)
	self.gui:Destroy()
end

return Interfejs
