--[[
	KlientTeleportu — kliencka połowa „teleportu przez chmury” (Script, RunContext = Client, w kontenerze
	Workspace/TeleportChmury; wymaganie Karola z 16.11.2026, D-075 z doprecyzowaniem). Budowa: swiat/teleport_chmury/zbuduj.py.

	Bez okna mapy i bez HUD. Przebieg (czasy i liczby: krainy.json → Dane):
		A  wejście w chmury   — kamera wznosi się nad gracza przez kłęby chmur, zasłona chmur zamyka obraz;
		B  wyłonienie         — w bieli kamera przeskakuje nad makietę pasa (Makieta), chmury rozchodzą się;
		   wybór              — gracz dotyka / klika krainę na pasie (mysz: najechanie podświetla; klawiatura i pad:
		                        strzałki / krzyżak / gałka przesuwają złotą strzałkę, Enter / A wybiera); zamknięta
		                        kraina jest przyciemniona i z kłódką — dotknięcie nią potrząsa i nic więcej;
		                        rezygnacja: dotknięcie z dala od pasa, Backspace / B na padzie, menu (Esc);
		C  zanurzenie         — kamera nurkuje ku wybranej krainie i znów wchodzi w chmury; w tym czasie serwer
		                        (SerwerTeleportu) sprawdza wybór, wczytuje okolicę celu i przenosi postać;
		D  opadanie           — z bieli kamera opada z góry na gracza w nowym miejscu i oddaje sterowanie.
	Klient niczego nie przenosi sam. Chmury to zwykłe kule z gładkiego plastiku tworzone lokalnie (w Camera), bez
	żadnych wgranych zasobów i bez elementów GUI na ekranie. Wspólnego oświetlenia (serwis oświetlenia) skrypt nie
	dotyka; lokalnie zmienia tylko: kamerę (typ, kąt widzenia, Focus), włączenie podpowiedzi (ProximityPromptService),
	postać (WalkSpeed, JumpPower, JumpHeight = 0, AutoRotate wyłączone; PlayerModule — jeśli miejsce go ma) i — gdy
	sterowanie.ukryj_gui — widoczność ekranów gry. Każda zmiana ma wpis
	w liście sprzątania, który wykonuje się przy KAŻDYM wyjściu: koniec, rezygnacja, błąd, śmierć postaci, usunięcie
	skryptu.

	Uchwyt dla przycisku TELEPORT (HUD Pawła), jedna linijka po stronie klienta:
		local t = workspace:FindFirstChild("TeleportChmury") if t then t.Otworz:Fire() end
	Dopóki sterowanie.sluchaj_hud = true, skrypt sam słucha ReplicatedStorage.HUDButtonPressed z nazwą „Teleport”
	(ten sam sygnał, którego używa EquipmentPanelClient), więc dziś przycisk działa bez zmian w plikach HUD.
	W Studio dodatkowo klawisz testowy (sterowanie.klawisz_testowy, domyślnie T).
	Haczyk testowy: BindableFunction Sygnaly/SterowanieKlienta (polecenia w funkcji sterowanie na końcu pliku).
	Atrybut kontenera „Trwa” (tylko u tego klienta) mówi innym skryptom klienta, że przejście trwa.
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local kontener = script.Parent
local Dane = require(kontener:WaitForChild("Dane"))
local zdalna = kontener:WaitForChild("Zdalne"):WaitForChild("Teleport") :: RemoteFunction
local sygnalTestowy = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieKlienta") :: BindableFunction
local zdarzenieOtworz = kontener:WaitForChild("Otworz") :: BindableEvent
local gracz = Players.LocalPlayer

local PREFIKS = "[TeleportChmury] "
local K = Dane.kamera
local C = Dane.czasy
local CH = Dane.chmury
local M = Dane.makieta
local AKCJA = "TeleportChmuryWybor"

local function kolor(hex: string): Color3
	return Color3.fromHex(hex)
end

------------------------------------------------------------------ makieta (Persistent — przychodzi po dołączeniu)
local makieta: Model? = nil
local makietaPivot = CFrame.identity
type Kraina = { id: string, indeks: number, model: Model, baza: CFrame, x: number, czesci: { any },
	klodka: { BasePart }, napis: TextLabel?, zamknieta: boolean, podniesienie: number, odmowaOd: number?,
	ostatnie: CFrame? }
local krainy: { Kraina } = {}
local krainaPoId: { [string]: Kraina } = {}
local wskaznik: Model? = nil
local wskaznikBaza = CFrame.identity
local pinezka: Model? = nil
local pinezkaBaza = CFrame.identity
local makietaGotowa = false

local function przygotujMakiete(): boolean
	if makietaGotowa then
		return true
	end
	local m = kontener:FindFirstChild("Makieta")
	if not m or not m:IsA("Model") then
		return false
	end
	local wymagane = m:GetAttribute("LiczbaCzesci")
	local jest = 0
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			jest += 1
		end
	end
	if type(wymagane) == "number" and jest < wymagane then
		return false
	end
	makieta = m
	makietaPivot = m:GetPivot()
	local folder = m:FindFirstChild("Krainy")
	for i, dk in Dane.krainy do
		local model = folder and folder:FindFirstChild(dk.id)
		if not model or not model:IsA("Model") then
			warn(PREFIKS .. "w makiecie brak krainy " .. dk.id)
			return false
		end
		local k: Kraina = { id = dk.id, indeks = i, model = model, baza = model:GetPivot(), x = M.srodki_x[i],
			czesci = {}, klodka = {}, napis = nil, zamknieta = not dk.od_poczatku, podniesienie = 0 }
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") then
				if d:GetAttribute("Klodka") then
					table.insert(k.klodka, d)
				elseif typeof(d:GetAttribute("KolorJasny")) == "Color3" then
					table.insert(k.czesci, { czesc = d, jasny = d:GetAttribute("KolorJasny"), neon = d:GetAttribute("Neon") == true })
				end
			elseif d:IsA("TextLabel") and d.Name == "Napis" then
				k.napis = d
			end
		end
		table.insert(krainy, k)
		krainaPoId[k.id] = k
	end
	wskaznik = m:FindFirstChild("Wskaznik") :: Model?
	pinezka = m:FindFirstChild("Pinezka") :: Model?
	if wskaznik then
		wskaznikBaza = makietaPivot:ToObjectSpace(wskaznik:GetPivot())
	end
	if pinezka then
		pinezkaBaza = makietaPivot:ToObjectSpace(pinezka:GetPivot())
	end
	makietaGotowa = true
	return true
end

local function ciemny(c: Color3): Color3
	local h, s, v = c:ToHSV()
	return Color3.fromHSV(h, s * M.przyciemnienie.nasycenie, v * M.przyciemnienie.jasnosc)
end

local function ustawZamkniecie(k: Kraina, zamknieta: boolean)
	k.zamknieta = zamknieta
	for _, w in k.czesci do
		w.czesc.Color = if zamknieta then ciemny(w.jasny) else w.jasny
		if w.neon then
			w.czesc.Material = if zamknieta then Enum.Material.SmoothPlastic else Enum.Material.Neon
		end
	end
	for _, p in k.klodka do
		p.Transparency = if zamknieta then 0 else 1
	end
	if k.napis then
		k.napis.TextColor3 = kolor(if zamknieta then M.napis_kolor_zamkniety else M.napis_kolor)
	end
end

local function przesunPodzespol(model: Model?, baza: CFrame, x: number, dy: number)
	if model then
		model:PivotTo(makietaPivot * CFrame.new(x - M.srodki_x[1], dy, 0) * baza)
	end
end

------------------------------------------------------------------ stan przejścia (do testów i dla innych skryptów)
local trwa = false
local stan: any = { faza = "spoczynek" }
local ostatnie: any = nil
local bladTestowy: string? = nil
local pauzaTestowa: any = nil
local przerwanie: string? = nil
local sprzatanie: { () -> () } = {}
local klatki: { number } = {}
local wyborWynik: any = nil
local kursor = 1
local odmowy = 0
local wPozaWyboru = false

local function poSobie(f: () -> ())
	table.insert(sprzatanie, f)
end

local function posprzataj()
	for i = #sprzatanie, 1, -1 do
		local f = sprzatanie[i]
		sprzatanie[i] = nil
		local ok, e = pcall(f)
		if not ok then
			warn(PREFIKS .. "sprzątanie: " .. tostring(e))
		end
	end
end

local function krok(): number
	local dt = RunService.RenderStepped:Wait()
	table.insert(klatki, dt)
	if przerwanie then
		error("PRZERWANE: " .. przerwanie, 0)
	end
	return dt
end

local function wygladz(a: number): number
	return a * a * (3 - 2 * a)
end
local function przedzial(a: number, od: number, doo: number): number
	return wygladz(math.clamp((a - od) / (doo - od), 0, 1))
end
local function wejscie(a: number): number
	return a * a
end
local function wyjscie(a: number): number
	return 1 - (1 - a) ^ 3
end
local function nurek(a: number): number
	return a * a * a
end

-- animacja jednej fazy: fn(alfa) co klatkę; pauza i błąd testowy tylko z haczyka
local function animuj(faza: string, czas: number, fn: (number) -> ())
	stan.faza = faza
	local t0 = os.clock()
	local pauza = 0
	while true do
		local a = math.clamp((os.clock() - t0 - pauza) / czas, 0, 1)
		if pauzaTestowa and pauzaTestowa.faza == faza and a >= pauzaTestowa.alfa then
			local p0 = os.clock()
			local ta = pauzaTestowa
			a = ta.alfa
			stan.pauza = faza .. " " .. tostring(a)
			while pauzaTestowa == ta do
				fn(a)
				krok()
			end
			if pauzaTestowa and pauzaTestowa.faza == faza and pauzaTestowa.alfa > a then
				-- następna pauza w tej samej fazie: przewijamy czas tak, by dalej liczyć od tej chwili
				pauza += os.clock() - p0
				stan.pauza = nil
				continue
			end
			stan.pauza = nil
			pauza += os.clock() - p0
		end
		if bladTestowy == faza and a >= 0.5 then
			bladTestowy = nil
			error("błąd testowy w fazie " .. faza, 0)
		end
		fn(a)
		if a >= 1 then
			break
		end
		krok()
	end
	stan.czasy[faza] = os.clock() - t0 - pauza
end

------------------------------------------------------------------ chmury (lokalne kule w Camera)
local folderLokalny: Folder? = nil
local zaslona: { { czesc: BasePart, u: number, v: number, g: number, f: number } } = {}
local kolumna: { BasePart } = {}
local losowe = Random.new()

local function lokalny(): Folder
	local kam = workspace.CurrentCamera
	if not folderLokalny or folderLokalny.Parent ~= kam then
		local f = Instance.new("Folder")
		f.Name = "TeleportChmuryLokalne"
		f.Parent = kam
		folderLokalny = f
	end
	return folderLokalny :: Folder
end

local function kula(srednica: number, c: Color3): BasePart
	local p = Instance.new("Part")
	p.Name = "Chmura"
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.new(srednica, srednica, srednica)
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Material = Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Color = c
	p.Transparency = 1
	p.Parent = lokalny()
	return p
end

local TAN_BAZA = math.tan(math.rad(35)) -- zasłona liczona dla kąta 70°; przy innym kącie kule odsuwają się proporcjonalnie

local function zbudujZaslone()
	if #zaslona > 0 then
		return
	end
	local biel, cien = kolor(CH.kolor), kolor(CH.kolor_cienia)
	local g1, g2 = CH.zaslona_glebokosc[1], CH.zaslona_glebokosc[2]
	local n = 0
	local function warstwa(kol: number, wier: number, g: number, przes: number)
		for i = 1, kol do
			for j = 1, wier do
				n += 1
				local u = if kol > 1 then -0.9 + 1.8 * (i - 1) / (kol - 1) else 0
				local v = if wier > 1 then -0.75 + 1.5 * (j - 1) / (wier - 1) else 0
				local r = CH.zaslona_promien * g * TAN_BAZA * losowe:NextNumber(1.0, 1.15)
				local c = kula(2 * r, if n % 3 == 0 then cien else biel)
				table.insert(zaslona, { czesc = c, u = u * przes, v = v * przes, g = g, f = losowe:NextNumber(0, 6.28) })
			end
		end
	end
	warstwa(CH.zaslona_kolumny, CH.zaslona_wiersze, g1, 1)
	warstwa(CH.zaslona_kolumny - 1, CH.zaslona_wiersze - 1, g2, 0.76)
end

-- pokrycie 0 = kule poza kadrem i przezroczyste, 1 = obraz w całości zakryty
local function ustawZaslone(pokrycie: number)
	local kam = workspace.CurrentCamera
	local cf = kam.CFrame
	local vp = kam.ViewportSize
	local aspekt = math.max(vp.X, 1) / math.max(vp.Y, 1)
	local tanV = math.tan(math.rad(kam.FieldOfView / 2))
	local skala = TAN_BAZA / tanV
	local rozrzut = 1 + (1 - pokrycie) * 2.6
	local t = os.clock()
	local przezr = if pokrycie >= 0.97 then 0 else 1 - pokrycie ^ 0.8
	stan.pokrycie = pokrycie
	for _, w in zaslona do
		if pokrycie <= 0.001 then
			w.czesc.Transparency = 1
			continue
		end
		local g = w.g * skala
		local polV = g * tanV
		local polH = polV * aspekt
		local u = w.u + 0.035 * math.sin(t * 1.3 + w.f)
		local v = w.v + 0.035 * math.cos(t * 1.1 + w.f * 1.7)
		w.czesc.Transparency = przezr
		w.czesc.CFrame = cf * CFrame.new(u * polH * rozrzut, v * polV * rozrzut, -g)
	end
end

local function kolumnaChmur(srodek: Vector3)
	for _, p in kolumna do
		p:Destroy()
	end
	table.clear(kolumna)
	local biel, cien = kolor(CH.kolor), kolor(CH.kolor_cienia)
	for i = 1, CH.kolumna_liczba do
		local d = losowe:NextNumber(CH.kolumna_rozmiar[1], CH.kolumna_rozmiar[2])
		local a = losowe:NextNumber(0, math.pi * 2)
		local r = losowe:NextNumber(CH.kolumna_odleglosc[1], CH.kolumna_odleglosc[2])
		local h = CH.kolumna_wysokosc[1] + (CH.kolumna_wysokosc[2] - CH.kolumna_wysokosc[1]) * (i - 1) / math.max(CH.kolumna_liczba - 1, 1)
		local c = kula(d, if i % 4 == 0 then cien else biel)
		c.Transparency = CH.kolumna_przezroczystosc
		c.Position = srodek + Vector3.new(math.cos(a) * r, h, math.sin(a) * r)
		table.insert(kolumna, c)
	end
end

local function usunKolumne()
	for _, p in kolumna do
		p:Destroy()
	end
	table.clear(kolumna)
end

local function zanikKolumny(x: number)
	for _, p in kolumna do
		p.Transparency = CH.kolumna_przezroczystosc + (1 - CH.kolumna_przezroczystosc) * x
	end
end

------------------------------------------------------------------ kamera
local function plaski(v: Vector3): Vector3
	local f = Vector3.new(v.X, 0, v.Z)
	return if f.Magnitude > 1e-3 then f.Unit else Vector3.new(0, 0, -1)
end

local function pozaWidoku(): (CFrame, number)
	local kam = workspace.CurrentCamera
	local vp = kam.ViewportSize
	local aspekt = math.max(vp.X, 1) / math.max(vp.Y, 1)
	local tanH = math.tan(math.rad(K.fov_makiety / 2)) * aspekt
	local d = math.clamp(M.polowa_dlugosci * (1 + K.margines) / tanH, K.min_odleglosc, K.max_odleglosc)
	local nach = math.rad(K.nachylenie_stopnie)
	local cel = Vector3.new(K.cel[1], K.cel[2], K.cel[3])
	local poz = cel + Vector3.new(0, math.sin(nach), math.cos(nach)) * d
	return makietaPivot * CFrame.lookAt(poz, cel), d
end

-- kamera i jej punkt skupienia: Roblox dociąga detale i światła wokół Camera.Focus (jak w ClassSelectClient),
-- więc przy dalekiej makiecie Focus musi być przy makiecie, a przy opadaniu — przy graczu
local function ustaw(cf: CFrame, fokus: Vector3)
	local kam = workspace.CurrentCamera
	kam.CFrame = cf
	kam.Focus = CFrame.new(fokus)
end

local function lokalnaPoza(poz: Vector3, cel: Vector3): CFrame
	return makietaPivot * CFrame.lookAt(poz, cel)
end

-- kamera nie wchodzi w dach, koronę drzewa ani ścianę: promień od głowy gracza do kamery; przy trafieniu kamera
-- staje tuż przed przeszkodą (prawie przezroczyste części, np. niewidzialne ściany, są pomijane)
local function odslon(cf: CFrame, fokus: Vector3, postac: Instance?): CFrame
	local kier = cf.Position - fokus
	if kier.Magnitude < 0.6 then
		return cf
	end
	local pomin: { Instance } = { lokalny() }
	if postac then
		table.insert(pomin, postac)
	end
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	for _ = 1, 6 do
		par.FilterDescendantsInstances = pomin
		local w = workspace:Raycast(fokus, kier, par)
		if not w then
			return cf
		end
		if w.Instance.Transparency >= 0.9 then
			table.insert(pomin, w.Instance)
		else
			return CFrame.new(fokus + kier.Unit * math.max(w.Distance - 1.2, 0.6)) * cf.Rotation
		end
	end
	return cf
end

------------------------------------------------------------------ wybór na makiecie
local podswietlenie: Highlight? = nil
local czasOdmowy = 0

local function krainaZCzesci(p: Instance?): Kraina?
	while p and p ~= makieta do
		local id = p:GetAttribute("Kraina")
		if type(id) == "string" and krainaPoId[id] then
			return krainaPoId[id]
		end
		p = p.Parent
	end
	return nil
end

local function krainaPodPunktem(punkt: Vector2): (Kraina?, boolean)
	local kam = workspace.CurrentCamera
	local promien = kam:ScreenPointToRay(punkt.X, punkt.Y)
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Include
	par.FilterDescendantsInstances = { (makieta :: Model):FindFirstChild("Krainy") :: Instance }
	local w = workspace:Raycast(promien.Origin, promien.Direction * 4000, par)
	if w then
		local k = krainaZCzesci(w.Instance)
		if k then
			return k, true
		end
	end
	-- nie trafił w klocek: najbliższa płytka na ekranie, jeśli dotknięcie jest blisko pasa
	local naj, odl = nil, math.huge
	local krokPx = 0
	local poprzedni: Vector3? = nil
	for _, k in krainy do
		local s = kam:WorldToScreenPoint((makietaPivot * CFrame.new(k.x, 0, 0)).Position)
		if poprzedni then
			krokPx = math.max(krokPx, (Vector2.new(s.X, s.Y) - Vector2.new(poprzedni.X, poprzedni.Y)).Magnitude)
		end
		poprzedni = s
		local d = (Vector2.new(s.X, s.Y) - punkt).Magnitude
		if d < odl then
			naj, odl = k, d
		end
	end
	if naj and odl <= krokPx * 0.75 then
		return naj, false
	end
	return nil, false
end

local function podswietl(k: Kraina?, odmowa: boolean?)
	if not podswietlenie then
		local h = Instance.new("Highlight")
		h.Name = "TeleportChmuryPodswietlenie"
		h.DepthMode = Enum.HighlightDepthMode.Occluded
		h.FillColor = Color3.new(1, 1, 1)
		h.OutlineTransparency = 0
		podswietlenie = h
		poSobie(function()
			h:Destroy()
			podswietlenie = nil
		end)
	end
	local h = podswietlenie :: Highlight
	if not k then
		h.Adornee = nil
		h.Parent = nil
		return
	end
	h.OutlineColor = if odmowa then Color3.fromRGB(230, 57, 43) else Color3.fromRGB(242, 176, 48)
	-- bez wypełnienia przy zwykłym wskazaniu: wypełnienie Highlight bieliło też złotą strzałkę nad płytką
	h.FillColor = if odmowa then Color3.fromRGB(230, 57, 43) else Color3.new(1, 1, 1)
	h.FillTransparency = if odmowa then 0.75 else 1
	h.Adornee = k.model
	h.Parent = k.model
end

local function ustawKursor(i: number)
	kursor = math.clamp(i, 1, #krainy)
	stan.kursor = krainy[kursor].id
	podswietl(krainy[kursor], false)
end

local function odmowa(k: Kraina)
	odmowy += 1
	stan.odmowy = odmowy
	k.odmowaOd = os.clock()
	czasOdmowy = os.clock()
	podswietl(k, true)
end

local function potwierdz(k: Kraina)
	if not wPozaWyboru or wyborWynik then
		return
	end
	ustawKursor(k.indeks)
	if k.zamknieta then
		odmowa(k)
		return
	end
	wyborWynik = { id = k.id }
end

local function rezygnuj(powod: string)
	if wPozaWyboru and not wyborWynik then
		wyborWynik = { rezygnacja = powod }
	end
end

local function naDotyk(punkt: Vector2)
	if not wPozaWyboru then
		return
	end
	local k = krainaPodPunktem(punkt)
	if k then
		potwierdz(k)
	else
		rezygnuj("obok")
	end
end

local ostatniaStrzalka = { x = math.huge, dy = math.huge }

local function aktualizujMakiete(dt: number)
	local t = os.clock()
	for i, k in krainy do
		local cel = if i == kursor then M.podniesienie else 0
		k.podniesienie += (cel - k.podniesienie) * math.min(1, dt * 14)
		if math.abs(cel - k.podniesienie) < 0.02 then
			k.podniesienie = cel
		end
		local drganie = CFrame.identity
		if k.odmowaOd then
			local u = (t - k.odmowaOd) / C.odmowa_s
			if u >= 1 then
				k.odmowaOd = nil
			else
				local sila = (1 - u)
				drganie = CFrame.new(math.sin(u * 46) * 0.9 * sila, 0, 0) * CFrame.Angles(0, 0, math.sin(u * 38) * 0.05 * sila)
			end
		end
		-- PivotTo tylko przy zmianie (płytka stojąca w miejscu nie jest „ruchoma” dla oświetlenia)
		local cf = k.baza * CFrame.new(0, k.podniesienie, 0) * drganie
		if not k.ostatnie or k.odmowaOd or (cf.Position - k.ostatnie.Position).Magnitude > 1e-3 then
			k.ostatnie = cf
			k.model:PivotTo(cf)
		end
	end
	if czasOdmowy > 0 and t - czasOdmowy > C.odmowa_s then
		czasOdmowy = 0
		podswietl(krainy[kursor], false)
	end
	-- strzałka bez stałego kołysania: część przestawiana co klatkę dostaje w Play blade światło (zrzuty 17.11.2026),
	-- więc przesuwamy ją tylko wtedy, gdy zmienia się jej miejsce (zmiana wskazania, podniesienie płytki)
	local k = krainy[kursor]
	if k then
		local dy = math.floor(k.podniesienie * 20 + 0.5) / 20
		if k.x ~= ostatniaStrzalka.x or dy ~= ostatniaStrzalka.dy then
			ostatniaStrzalka.x, ostatniaStrzalka.dy = k.x, dy
			przesunPodzespol(wskaznik, wskaznikBaza, k.x, dy)
		end
	end
end

local function obecnaKraina(pozycja: Vector3): Kraina?
	for _, dk in Dane.krainy do
		for _, o in dk.obszary_xz do
			if pozycja.X >= o[1] and pozycja.X <= o[2] and pozycja.Z >= o[3] and pozycja.Z <= o[4] then
				return krainaPoId[dk.id]
			end
		end
	end
	return nil
end

-- klawiatura i pad: tylko w czasie wyboru (wiązanie z wysokim priorytetem, połyka też skok i ruch)
local ostatniaGalka = 0
local function akcjaWyboru(_: string, st: Enum.UserInputState, wej: InputObject): Enum.ContextActionResult
	local kc = wej.KeyCode
	if kc == Enum.KeyCode.Thumbstick1 then
		if st == Enum.UserInputState.Change and math.abs(wej.Position.X) > 0.6 and os.clock() - ostatniaGalka > C.gamepad_powtorka_s then
			ostatniaGalka = os.clock()
			ustawKursor(kursor + (if wej.Position.X > 0 then 1 else -1))
		end
		return Enum.ContextActionResult.Sink
	end
	if st ~= Enum.UserInputState.Begin then
		return Enum.ContextActionResult.Sink
	end
	if kc == Enum.KeyCode.Left or kc == Enum.KeyCode.A or kc == Enum.KeyCode.DPadLeft then
		ustawKursor(kursor - 1)
	elseif kc == Enum.KeyCode.Right or kc == Enum.KeyCode.D or kc == Enum.KeyCode.DPadRight then
		ustawKursor(kursor + 1)
	elseif kc == Enum.KeyCode.Return or kc == Enum.KeyCode.KeypadEnter or kc == Enum.KeyCode.ButtonA or kc == Enum.KeyCode.Space then
		potwierdz(krainy[kursor])
	elseif kc == Enum.KeyCode.ButtonB or kc == Enum.KeyCode.Backspace or kc == Enum.KeyCode.Escape then
		rezygnuj("klawisz")
	end
	return Enum.ContextActionResult.Sink
end

-- jedna linijka na dole ekranu w fazie wyboru: jak wybrać krainę i jak wrócić (przejście chowa inne ScreenGui
-- na starcie, więc ten tworzymy dopiero teraz i usuwamy zaraz po wyborze — także przy rezygnacji, błędzie i śmierci)
local function pokazPodpowiedzWyboru(): ScreenGui?
	local ekrany = gracz:FindFirstChildOfClass("PlayerGui")
	if not ekrany then
		return nil
	end
	local dotyk = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
	local pad = UserInputService.GamepadEnabled and not dotyk
		and UserInputService:GetLastInputType().Name:find("Gamepad") ~= nil
	local tekst = "Kliknij krainę albo wybierz strzałkami i Enter · Backspace: wróć"
	if dotyk then
		tekst = "Dotknij krainy, żeby tam polecieć · dotknij obok, żeby wrócić"
	elseif pad then
		tekst = "Krzyżak: wybierz krainę · A: leć · B: wróć"
	end
	local g = Instance.new("ScreenGui")
	g.Name = "TeleportChmuryPodpowiedz"
	g.ResetOnSpawn = false
	g.DisplayOrder = 5
	local napis = Instance.new("TextLabel")
	napis.Name = "Podpowiedz"
	napis.AnchorPoint = Vector2.new(0.5, 1)
	napis.Position = UDim2.new(0.5, 0, 1, -24)
	napis.Size = UDim2.fromOffset(0, 40)
	napis.AutomaticSize = Enum.AutomaticSize.X
	napis.BackgroundColor3 = kolor("1D1916")
	napis.BackgroundTransparency = 0.25
	napis.TextColor3 = kolor("FFF6E0")
	napis.Font = Enum.Font.GothamBold
	napis.TextSize = 20
	napis.Text = tekst
	local margines = Instance.new("UIPadding")
	margines.PaddingLeft = UDim.new(0, 18)
	margines.PaddingRight = UDim.new(0, 18)
	margines.Parent = napis
	local rog = Instance.new("UICorner")
	rog.CornerRadius = UDim.new(0.5, 0)
	rog.Parent = napis
	napis.Parent = g
	g.Parent = ekrany
	return g
end

local function wybierzKraine(): any
	wyborWynik = nil
	wPozaWyboru = true
	poSobie(function()
		wPozaWyboru = false
	end)
	ContextActionService:BindActionAtPriority(AKCJA, akcjaWyboru, false, Enum.ContextActionPriority.High.Value + 50,
		Enum.KeyCode.Left, Enum.KeyCode.Right, Enum.KeyCode.A, Enum.KeyCode.D, Enum.KeyCode.W, Enum.KeyCode.S,
		Enum.KeyCode.Up, Enum.KeyCode.Down, Enum.KeyCode.DPadLeft, Enum.KeyCode.DPadRight, Enum.KeyCode.Thumbstick1,
		Enum.KeyCode.Return, Enum.KeyCode.KeypadEnter, Enum.KeyCode.Space, Enum.KeyCode.ButtonA, Enum.KeyCode.ButtonB,
		Enum.KeyCode.Backspace, Enum.KeyCode.Escape)
	poSobie(function()
		ContextActionService:UnbindAction(AKCJA)
	end)
	local dotyk: { [InputObject]: { t: number, p: Vector2 } } = {}
	local polaczenia = {
		UserInputService.InputBegan:Connect(function(wej: InputObject, przetworzone: boolean)
			if przetworzone then
				return
			end
			local typ = wej.UserInputType
			if typ == Enum.UserInputType.Touch or typ == Enum.UserInputType.MouseButton1 then
				dotyk[wej] = { t = os.clock(), p = Vector2.new(wej.Position.X, wej.Position.Y) }
			end
		end),
		UserInputService.InputEnded:Connect(function(wej: InputObject)
			local d = dotyk[wej]
			if not d then
				return
			end
			dotyk[wej] = nil
			local p = Vector2.new(wej.Position.X, wej.Position.Y)
			if os.clock() - d.t <= C.dotyk_max_s and (p - d.p).Magnitude <= C.dotyk_max_px then
				naDotyk(p)
			end
		end),
		UserInputService.InputChanged:Connect(function(wej: InputObject)
			if wej.UserInputType == Enum.UserInputType.MouseMovement and czasOdmowy == 0 then
				local k = krainaPodPunktem(Vector2.new(wej.Position.X, wej.Position.Y))
				if k and k.indeks ~= kursor then
					ustawKursor(k.indeks)
				end
			end
		end),
		GuiService.MenuOpened:Connect(function()
			rezygnuj("menu")
		end),
	}
	poSobie(function()
		for _, p in polaczenia do
			p:Disconnect()
		end
	end)
	stan.faza = "wybor"
	stan.wyborOd = os.clock()
	local podpowiedz = pokazPodpowiedzWyboru()
	poSobie(function()
		if podpowiedz then
			podpowiedz:Destroy()
			podpowiedz = nil
		end
	end)
	local t0 = os.clock()
	while not wyborWynik do
		local dt = krok()
		local cf = pozaWidoku()
		local t = os.clock()
		local kol = math.rad(K.kolysanie_stopnie)
		ustaw(cf * CFrame.Angles(math.sin(t * 0.5) * kol, math.sin(t * 0.37) * kol, 0), makietaPivot.Position)
		aktualizujMakiete(dt)
		ustawZaslone(0)
		if os.clock() - t0 > C.limit_wyboru_s then
			wyborWynik = { rezygnacja = "czas" }
		end
	end
	wPozaWyboru = false
	ContextActionService:UnbindAction(AKCJA)
	if podpowiedz then
		podpowiedz:Destroy()
		podpowiedz = nil
	end
	stan.czasy.wybor = os.clock() - t0
	if wyborWynik.id then
		-- chwila na pokazanie wybranej krainy (podniesiona, ze złotą obwódką i strzałką)
		local tp = os.clock()
		while os.clock() - tp < C.pokaz_wyboru_s do
			local dt = krok()
			ustaw(pozaWidoku(), makietaPivot.Position)
			aktualizujMakiete(dt)
		end
	end
	return wyborWynik
end

------------------------------------------------------------------ jedno przejście
local function wyslij(polecenie: string, id: string?): any
	local ok, w = pcall(function()
		return zdalna:InvokeServer(polecenie, id)
	end)
	if ok and type(w) == "table" then
		return w
	end
	return { ok = false, powod = "brak_odpowiedzi" }
end

local function sterowaniePostaci(): any
	-- bez czekania: w tym miejscu (16.11.2026) PlayerScripts nie ma PlayerModule
	local ps = gracz:FindFirstChildOfClass("PlayerScripts")
	local pm = ps and ps:FindFirstChild("PlayerModule")
	if not pm or not pm:IsA("ModuleScript") then
		return nil
	end
	local ok, s = pcall(function()
		return require(pm :: ModuleScript):GetControls()
	end)
	return if ok then s else nil
end

local function przebieg(zrodlo: string)
	local kam = workspace.CurrentCamera
	local postac = gracz.Character :: Model
	local humanoid = postac:FindFirstChildOfClass("Humanoid") :: Humanoid
	local korzen = postac:FindFirstChild("HumanoidRootPart") :: BasePart
	local t0 = os.clock()
	stan = { faza = "start", zrodlo = zrodlo, czasy = {}, start = t0 }
	przerwanie = nil
	table.clear(klatki)

	-- 1. blokady (każda z wpisem sprzątania)
	local zapis = { typ = kam.CameraType, podmiot = kam.CameraSubject, fov = kam.FieldOfView, cf = kam.CFrame,
		focus = kam.Focus }
	local start = korzen.Position
	local focusOff = zapis.focus.Position - start
	local odleglosc = math.max((zapis.cf.Position - zapis.focus.Position).Magnitude, 0.5)
	local pochylenie = math.asin(math.clamp(zapis.cf.LookVector.Y, -0.99, 0.99))
	local function pozaZa(k: BasePart, kierunek: Vector3): CFrame
		local f = k.Position + focusOff
		local p = plaski(kierunek)
		local patrz = p * math.cos(pochylenie) + Vector3.new(0, math.sin(pochylenie), 0)
		return CFrame.lookAt(f - patrz * odleglosc, f)
	end
	poSobie(function()
		-- kamera wraca za postać (bez skoku) i oddaje się modułowi kamery gracza
		local kk = workspace.CurrentCamera
		local pc = gracz.Character
		local h = pc and pc:FindFirstChildOfClass("Humanoid")
		local r = pc and pc:FindFirstChild("HumanoidRootPart")
		kk.FieldOfView = zapis.fov
		if r and r:IsA("BasePart") then
			local ruszyl = (r.Position - start).Magnitude > 20
			kk.CFrame = pozaZa(r, if ruszyl then r.CFrame.LookVector else zapis.cf.LookVector)
			kk.Focus = CFrame.new(r.Position + focusOff)
		end
		kk.CameraSubject = if h then h else zapis.podmiot
		kk.CameraType = if zapis.typ == Enum.CameraType.Scriptable then Enum.CameraType.Custom else zapis.typ
	end)
	kam.CameraType = Enum.CameraType.Scriptable

	-- postać stoi: lokalnie zero prędkości i skoku, bez obracania (klient symuluje własną postać, więc to wystarcza
	-- i działa też na telefonie i padzie); gdy miejsce ma PlayerModule, dodatkowo wyłączone sterowanie
	local zamroz = { ws = humanoid.WalkSpeed, jp = humanoid.JumpPower, jh = humanoid.JumpHeight, ar = humanoid.AutoRotate }
	humanoid.WalkSpeed = 0
	humanoid.JumpPower = 0
	humanoid.JumpHeight = 0
	humanoid.AutoRotate = false
	stan.sterowanieWylaczone = true
	poSobie(function()
		if humanoid.Parent then
			-- przywracamy tylko to, czego w międzyczasie nie zmienił nikt inny
			if humanoid.WalkSpeed == 0 then
				humanoid.WalkSpeed = zamroz.ws
			end
			if humanoid.JumpPower == 0 then
				humanoid.JumpPower = zamroz.jp
			end
			if humanoid.JumpHeight == 0 then
				humanoid.JumpHeight = zamroz.jh
			end
			humanoid.AutoRotate = zamroz.ar
		end
		stan.sterowanieWylaczone = false
	end)
	local sterowanie = sterowaniePostaci()
	if sterowanie then
		sterowanie:Disable()
		stan.playerModule = true
		poSobie(function()
			sterowanie:Enable()
		end)
	end
	local podpowiedzi = ProximityPromptService.Enabled
	ProximityPromptService.Enabled = false
	poSobie(function()
		ProximityPromptService.Enabled = podpowiedzi
	end)
	if Dane.sterowanie.ukryj_gui then
		local ukryte = {}
		for _, g in gracz:WaitForChild("PlayerGui"):GetChildren() do
			if g:IsA("ScreenGui") and g.Enabled then
				g.Enabled = false
				table.insert(ukryte, g)
			end
		end
		stan.ukryteGui = #ukryte
		poSobie(function()
			for _, g in ukryte do
				if g.Parent then
					g.Enabled = true
				end
			end
		end)
	end
	poSobie(function()
		for _, w in zaslona do
			w.czesc:Destroy()
		end
		table.clear(zaslona)
		usunKolumne()
		if folderLokalny then
			folderLokalny:Destroy()
			folderLokalny = nil
		end
	end)
	poSobie(function()
		-- makieta wraca do spoczynku (podniesienie, drganie, podświetlenie)
		for _, k in krainy do
			k.podniesienie = 0
			k.odmowaOd = nil
			k.model:PivotTo(k.baza)
			k.ostatnie = nil
		end
		ostatniaStrzalka.x, ostatniaStrzalka.dy = math.huge, math.huge
	end)
	local smierc = humanoid.Died:Connect(function()
		przerwanie = "śmierć postaci"
	end)
	local usuniecie = gracz.CharacterRemoving:Connect(function()
		przerwanie = "postać usunięta"
	end)
	poSobie(function()
		smierc:Disconnect()
		usuniecie:Disconnect()
	end)

	-- stan odblokowania od serwera (w tle, w czasie fazy A)
	local stanSerwera: any = nil
	task.spawn(function()
		stanSerwera = wyslij("stan")
	end)
	zbudujZaslone()

	-- A: wejście w chmury — kamera wznosi się pionowo znad swojego miejsca i obraca w dół na gracza
	stan.czasy.blokady = os.clock() - t0
	local C0 = kam.CFrame
	local gora = C0.Position + Vector3.new(0, K.wejscie_wysokosc, 0)
	local C1 = CFrame.lookAt(gora, start, plaski(C0.LookVector))
	local R0, R1 = C0.Rotation, C1.Rotation
	local glowa0 = start + focusOff
	kolumnaChmur(start)
	animuj("A", C.wejscie_s, function(a)
		local pos = C0.Position:Lerp(gora, wejscie(a))
		ustaw(odslon(CFrame.new(pos) * R0:Lerp(R1, przedzial(a, 0.0, 0.75)), glowa0, postac), start)
		ustawZaslone(przedzial(a, 0.45, 0.95))
	end)
	usunKolumne()

	-- przeskok w bieli: makieta z bieżącym stanem odblokowania
	local tb = os.clock()
	while stanSerwera == nil and os.clock() - tb < 1.5 do
		ustaw(C1, start)
		ustawZaslone(1)
		krok()
	end
	local otwarte = {}
	if stanSerwera and stanSerwera.ok and type(stanSerwera.odblokowane) == "table" then
		for _, id in stanSerwera.odblokowane do
			otwarte[id] = true
		end
	else
		for _, dk in Dane.krainy do
			otwarte[dk.id] = dk.od_poczatku
		end
		stan.uwaga = "brak stanu z serwera — makieta wg danych"
	end
	for _, k in krainy do
		ustawZamkniecie(k, not otwarte[k.id])
	end
	local tu = obecnaKraina(start)
	stan.obecna = tu and tu.id or nil
	if pinezka then
		if tu then
			przesunPodzespol(pinezka, pinezkaBaza, tu.x, 0)
		else
			przesunPodzespol(pinezka, pinezkaBaza, M.srodki_x[1], -400) -- poza kadrem (gracz poza krainami)
		end
	end
	ustawKursor(if tu then tu.indeks else 1)
	stan.czasy.przeskok = os.clock() - tb
	kam.FieldOfView = K.fov_makiety
	local Cv, d = pozaWidoku()
	local nach = math.rad(K.nachylenie_stopnie)
	local cel = Vector3.new(K.cel[1], K.cel[2], K.cel[3])
	local pozB = cel + Vector3.new(0, math.sin(nach), math.cos(nach)) * d + Vector3.new(0, K.wylonienie_od[1] * d, K.wylonienie_od[2] * d)
	local CB0 = lokalnaPoza(pozB, cel)
	ustaw(CB0, makietaPivot.Position)
	ustawZaslone(1)
	krok()

	-- B: wyłonienie pasa z chmur
	animuj("B", C.wylonienie_s, function(a)
		ustaw(CB0:Lerp(pozaWidoku(), wyjscie(a)), makietaPivot.Position)
		ustawZaslone(1 - przedzial(a, 0.0, 0.6))
		aktualizujMakiete(0)
	end)
	stan.czasy.doMakiety = os.clock() - t0

	-- wybór
	local wybor = wybierzKraine()
	local tw = os.clock()
	stan.wybor = wybor

	-- C: zanurzenie w chmury (serwer pracuje w tle)
	local odpowiedz: any = nil
	if wybor.id then
		task.spawn(function()
			odpowiedz = wyslij("przenies", wybor.id)
		end)
	end
	local CC0 = kam.CFrame
	local CC1
	if wybor.id then
		local k = krainaPoId[wybor.id]
		CC1 = lokalnaPoza(Vector3.new(k.x + K.nurkowanie[1], K.nurkowanie[2], K.nurkowanie[3]), Vector3.new(k.x, 0, 0))
	else
		local _, dd = pozaWidoku()
		local p = cel + Vector3.new(0, math.sin(nach), math.cos(nach)) * dd + Vector3.new(0, K.odlot[1] * dd, K.odlot[2] * dd)
		CC1 = lokalnaPoza(p, cel)
	end
	animuj("C", C.zanurzenie_s, function(a)
		ustaw(CC0:Lerp(CC1, nurek(a)), makietaPivot.Position)
		ustawZaslone(przedzial(a, 0.4, 0.95))
		aktualizujMakiete(0)
	end)

	-- w bieli: czekamy na serwer (najwyżej limit) i na postać w punkcie przybycia
	local tc = os.clock()
	local function biel()
		ustaw(CC1, makietaPivot.Position)
		ustawZaslone(1)
		krok()
	end
	if wybor.id then
		while odpowiedz == nil and os.clock() - tc < C.limit_serwera_s do
			biel()
		end
		if odpowiedz and odpowiedz.powod == "za_szybko" and type(odpowiedz.zostalo) == "number" and odpowiedz.zostalo <= 5 then
			local tz = os.clock()
			while os.clock() - tz < odpowiedz.zostalo + 0.05 do
				biel()
			end
			odpowiedz = nil
			task.spawn(function()
				odpowiedz = wyslij("przenies", wybor.id)
			end)
			local tr = os.clock()
			while odpowiedz == nil and os.clock() - tr < C.limit_serwera_s do
				biel()
			end
		end
		stan.odpowiedz = odpowiedz and { ok = odpowiedz.ok, powod = odpowiedz.powod, zrodlo = odpowiedz.zrodlo,
			wczytanie = odpowiedz.wczytanie } or { ok = false, powod = "brak_odpowiedzi" }
		if odpowiedz and odpowiedz.ok and typeof(odpowiedz.punkt) == "Vector3" then
			local tp = os.clock()
			while os.clock() - tp < C.limit_przybycia_s and (korzen.Position - odpowiedz.punkt).Magnitude > 8 do
				biel()
			end
		end
	end
	while os.clock() - tc < C.biel_min_s do
		biel()
	end
	stan.czasy.czekanie = os.clock() - tc

	-- D: opadanie z góry na gracza
	kam.FieldOfView = zapis.fov
	for _, k in krainy do
		k.podniesienie = 0
		k.model:PivotTo(k.baza)
		k.ostatnie = nil
	end
	podswietl(nil)
	local przeniesiony = (korzen.Position - start).Magnitude > 20
	local kierunek = if przeniesiony then korzen.CFrame.LookVector else zapis.cf.LookVector
	-- kamera opada pionowo nad swoją końcową pozycją (za plecami gracza), patrząc w dół, a na końcu podnosi wzrok;
	-- odslon() trzyma ją przed dachem albo koroną drzewa, gdy coś wisi między nią a głową gracza
	local H = K.opadanie_wysokosc
	local CDk = pozaZa(korzen, kierunek)
	local RD0 = CFrame.lookAt(CDk.Position + Vector3.new(0, H, 0), korzen.Position, plaski(CDk.LookVector)).Rotation
	kolumnaChmur(korzen.Position)
	ustaw(CFrame.new(CDk.Position + Vector3.new(0, H, 0)) * RD0, korzen.Position)
	ustawZaslone(1)
	animuj("D", C.opadanie_s, function(a)
		local c1 = pozaZa(korzen, kierunek)
		local pos = c1.Position + Vector3.new(0, H * (1 - wyjscie(a)), 0)
		local cf = CFrame.new(pos) * RD0:Lerp(c1.Rotation, przedzial(a, 0.2, 1.0))
		ustaw(odslon(cf, korzen.Position + focusOff, postac), korzen.Position)
		ustawZaslone(1 - przedzial(a, 0.0, 0.45))
		zanikKolumny(przedzial(a, 0.3, 0.85))
	end)
	stan.czasy.poWyborze = os.clock() - tw
	stan.czasy.calosc = os.clock() - t0
	stan.przeniesiony = przeniesiony
end

local function statystykaKlatek(): any
	local n = #klatki
	if n == 0 then
		return { n = 0 }
	end
	local suma, maks = 0, 0
	local kopia = table.clone(klatki)
	for _, dt in kopia do
		suma += dt
		maks = math.max(maks, dt)
	end
	table.sort(kopia)
	local p95 = kopia[math.max(1, math.ceil(n * 0.95))]
	return { n = n, srednia_ms = suma / n * 1000, max_ms = maks * 1000, p95_ms = p95 * 1000,
		fps = n / math.max(suma, 1e-6) }
end

local function mozna(): (boolean, string?)
	if trwa then
		return false, "trwa"
	end
	if not przygotujMakiete() then
		return false, "makieta_niegotowa"
	end
	local postac = gracz.Character
	local humanoid = postac and postac:FindFirstChildOfClass("Humanoid")
	local korzen = postac and postac:FindFirstChild("HumanoidRootPart")
	if not postac or not humanoid or humanoid.Health <= 0 or not korzen then
		return false, "brak_postaci"
	end
	local kam = workspace.CurrentCamera
	if not kam or kam.CameraType ~= Enum.CameraType.Custom or kam.CameraSubject ~= humanoid then
		return false, "kamera_zajeta" -- np. trwa walka albo inna scenka
	end
	return true, nil
end

local function otworz(zrodlo: string): (boolean, string?)
	local ok, powod = mozna()
	if not ok then
		return false, powod
	end
	trwa = true
	kontener:SetAttribute("Trwa", true)
	task.spawn(function()
		local udane, blad = xpcall(przebieg, function(e)
			local s = tostring(e)
			if string.sub(s, 1, 11) == "PRZERWANE: " then
				return s -- zwykłe przerwanie (śmierć, reset, usunięta postać): bez śladu stosu
			end
			return s .. "\n" .. debug.traceback()
		end, zrodlo)
		posprzataj()
		stan.faza = "spoczynek"
		stan.klatki = statystykaKlatek()
		stan.wynik = if udane then (if stan.wybor and stan.wybor.id then "wybrano " .. stan.wybor.id else "rezygnacja") else "błąd"
		if not udane then
			stan.blad = string.sub(tostring(blad), 1, 600)
			if string.sub(tostring(blad), 1, 11) == "PRZERWANE: " then
				print(PREFIKS .. "przejście przerwane (" .. string.sub(tostring(blad), 12) .. ") — posprzątane")
			else
				warn(PREFIKS .. "przejście przerwane: " .. tostring(blad))
			end
		end
		ostatnie = stan
		trwa = false
		kontener:SetAttribute("Trwa", false)
	end)
	return true, nil
end

------------------------------------------------------------------ wyzwalacze
zdarzenieOtworz.Event:Connect(function()
	otworz("otworz")
end)

if Dane.sterowanie.sluchaj_hud then
	task.spawn(function()
		local e = ReplicatedStorage:WaitForChild("HUDButtonPressed", 300)
		if e and e:IsA("BindableEvent") then
			e.Event:Connect(function(nazwa: any)
				if nazwa == Dane.sterowanie.nazwa_przycisku_hud then
					otworz("hud")
				end
			end)
		end
	end)
end

local klawisz: Enum.KeyCode? = nil
pcall(function()
	if type(Dane.sterowanie.klawisz_testowy) == "string" and Dane.sterowanie.klawisz_testowy ~= "" then
		klawisz = (Enum.KeyCode :: any)[Dane.sterowanie.klawisz_testowy]
	end
end)
UserInputService.InputBegan:Connect(function(wej: InputObject, przetworzone: boolean)
	if klawisz and not przetworzone and wej.KeyCode == klawisz and not UserInputService:GetFocusedTextBox() then
		otworz("klawisz")
	end
end)

script.Destroying:Connect(function()
	przerwanie = "skrypt usunięty"
	posprzataj()
end)

-- makieta przychodzi w tle (Persistent); przygotowanie od razu, gdy będzie
task.spawn(function()
	local t0 = os.clock()
	while not przygotujMakiete() and os.clock() - t0 < 120 do
		task.wait(0.5)
	end
	kontener:SetAttribute("KlientGotowy", makietaGotowa)
end)

------------------------------------------------------------------ haczyk testowy
local function kopiaStanu(s: any): any
	if type(s) ~= "table" then
		return s
	end
	local t = {}
	for k, v in s do
		if type(v) == "table" then
			t[k] = kopiaStanu(v)
		elseif typeof(v) == "Vector3" then
			t[k] = { v.X, v.Y, v.Z }
		elseif type(v) == "number" or type(v) == "string" or type(v) == "boolean" then
			t[k] = v
		end
	end
	return t
end

sygnalTestowy.OnInvoke = function(polecenie: any, a: any, b: any): any
	local kam = workspace.CurrentCamera
	if polecenie == "stan" then
		local postac = gracz.Character
		local h = postac and postac:FindFirstChildOfClass("Humanoid")
		local r = postac and postac:FindFirstChild("HumanoidRootPart")
		local lokalne = 0
		if folderLokalny then
			lokalne = #folderLokalny:GetChildren()
		end
		local ukryte = 0
		for _, g in gracz.PlayerGui:GetChildren() do
			if g:IsA("ScreenGui") and not g.Enabled then
				ukryte += 1
			end
		end
		return kopiaStanu({
			trwa = trwa,
			biezacy = stan,
			ostatnie = ostatnie,
			gotowa = makietaGotowa,
			kamera = kam.CameraType.Name,
			podmiotHumanoid = h ~= nil and kam.CameraSubject == h,
			fov = kam.FieldOfView,
			podpowiedzi = ProximityPromptService.Enabled,
			lokalne = lokalne,
			zaslona = #zaslona,
			ukryteGui = ukryte,
			wiazanie = next(ContextActionService:GetBoundActionInfo(AKCJA)) ~= nil,
			sprzatanie = #sprzatanie,
			pozycja = r and (r :: BasePart).Position or nil,
			kameraPoz = kam.CFrame.Position,
			zamkniete = (function()
				local t = {}
				for _, k in krainy do
					if k.zamknieta then
						table.insert(t, k.id)
					end
				end
				return t
			end)(),
		})
	elseif polecenie == "otworz" then
		local ok, powod = otworz("test")
		return { ok = ok, powod = powod }
	elseif polecenie == "wybierz" then
		local k = krainaPoId[a]
		if not k or not wPozaWyboru then
			return { ok = false, powod = "nie_w_wyborze" }
		end
		potwierdz(k)
		return { ok = true, zamknieta = k.zamknieta }
	elseif polecenie == "dotknij" then
		if type(a) ~= "number" or type(b) ~= "number" then
			return { ok = false }
		end
		local k, trafiony = krainaPodPunktem(Vector2.new(a, b))
		naDotyk(Vector2.new(a, b))
		return { ok = true, kraina = k and k.id or nil, trafiony = trafiony }
	elseif polecenie == "ekran" then
		local k = krainaPoId[a]
		if not k then
			return { ok = false }
		end
		local s, widac = kam:WorldToScreenPoint((makietaPivot * CFrame.new(k.x, 2, 0)).Position)
		local v, _ = kam:WorldToViewportPoint((makietaPivot * CFrame.new(k.x, 2, 0)).Position)
		local wstawka = GuiService:GetGuiInset()
		return { ok = true, x = s.X, y = s.Y, vx = v.X, vy = v.Y, widac = widac, vp = { kam.ViewportSize.X, kam.ViewportSize.Y },
			wstawka = { wstawka.X, wstawka.Y } }
	elseif polecenie == "kursor" then
		local k = krainaPoId[a]
		if k and wPozaWyboru then
			ustawKursor(k.indeks)
			return { ok = true }
		end
		return { ok = false }
	elseif polecenie == "rezygnuj" then
		rezygnuj("test")
		return { ok = wPozaWyboru }
	elseif polecenie == "blad" then
		bladTestowy = a
		return { ok = true }
	elseif polecenie == "pauza" then
		pauzaTestowa = if type(a) == "string" then { faza = a, alfa = tonumber(b) or 0.5 } else nil
		return { ok = true }
	elseif polecenie == "wznow" then
		pauzaTestowa = nil
		return { ok = true }
	end
	return { ok = false, powod = "nieznane_polecenie" }
end
