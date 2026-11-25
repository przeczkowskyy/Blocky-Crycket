--[[
	JajkaBiomowSpoczynek — ruch jajek Bagna i Dżungli w spoczynku (swiat/jajka_biomow, Karol 25.11.2026; PROPOZYCJA).
	Na próbę wstawia go swiat/jajka_biomow/wdroz.py jako Script (RunContext = Client) w Workspace/JajkaBiomowPodglad,
	a dane jako ModuleScript Workspace/JajkaBiomowPodglad/Moduly/JajkaBiomowDane (jak pakiety próby Karola, bez src/).
	Docelowo (za zgodą Pawła) LocalScript w src/client i dane w ReplicatedStorage.Shared — skrypt szuka danych
	najpierw w kontenerze, potem w ReplicatedStorage.Shared.

	Co robi u każdego klienta, gdy kamera jest bliżej niż ZASIEG:
	  • Egg buja się wokół korzenia i pęknięcia pulsują (te same liczby co leśne jajo Pawła) — tylko gdy atrybut
	    modelu Wyklucie nie jest true (wtedy jajem steruje scenka wyklucia);
	  • ozdoby grają „ozdobySpoczynek” (wiatr w trzcinach i liściach, bujanie lilii i kwiatów, bąble, puls kryształów);
	  • po zmianie atrybutu Final (scenka zwiększa go w chwili BOOM) ozdoby grają „ozdobyFinal” (trzciny i liście
	    odchylają się od jaja, bąble pękają, kryształy błyskają kolorem żył).
	Wszystko lokalnie (CFrame, Color, Transparency, Size zakotwiczonych części) — serwer nic nie wysyła.
]]
if not game:GetService("RunService"):IsStudio() then
	return -- jak pakiety próby Karola: tylko w Studio, do zdjęcia przy wydaniu
end

local RunService = game:GetService("RunService")

local RS = game:GetService("ReplicatedStorage")

local ZASIEG = 160

local KONTENER = "JajkaBiomowPodglad" -- = D.wspolne.kontener (tu na sztywno, bo dane dopiero szukamy)

local function znajdzDane(): ModuleScript?
	local k = workspace:FindFirstChild(KONTENER)
	local moduly = k and k:FindFirstChild("Moduly")
	local m = moduly and moduly:FindFirstChild("JajkaBiomowDane")
	if not m then
		local wspolny = RS:FindFirstChild("Shared")
		m = wspolny and wspolny:FindFirstChild("JajkaBiomowDane")
	end
	return if m and m:IsA("ModuleScript") then m else nil
end

local modul = znajdzDane()
local doKiedy = os.clock() + 30
while not modul and os.clock() < doKiedy do
	task.wait(0.5)
	modul = znajdzDane()
end
if not modul then
	warn("[JajkaBiomowSpoczynek] brak danych JajkaBiomowDane (Workspace/" .. KONTENER .. "/Moduly ani ReplicatedStorage.Shared)")
	return
end
local D = require(modul)
local W = D.wspolne

local jajka = {}

local function obrot(cf: CFrame, punkt: Vector3, os_: Vector3, kat: number): CFrame
	if os_.Magnitude < 1e-4 or kat == 0 then
		return cf
	end
	return CFrame.new(punkt) * CFrame.fromAxisAngle(os_.Unit, kat) * CFrame.new(-punkt) * cf
end

local function przygotuj(m: Model, dane)
	local korzen = m.PrimaryPart or m:FindFirstChild(W.korzen)
	local jajo = m:FindFirstChild(W.jajo)
	if not (korzen and korzen:IsA("BasePart") and jajo and jajo:IsA("BasePart")) then
		return nil
	end
	local j = { model = m, dane = dane, korzen = korzen, jajo = jajo, domJaja = jajo.CFrame, blaski = {}, ruchy = {},
		stan = {}, final = {}, emisja = true }
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("SurfaceAppearance") then
			table.insert(j.blaski, d)
		end
	end
	local function zapamietaj(nazwa: string)
		local c = m:FindFirstChild(nazwa)
		if not (c and c:IsA("BasePart")) then
			return nil
		end
		if not j.stan[c] then
			j.stan[c] = { dom = c.CFrame, kolor = c.Color, przezr = c.Transparency, rozmiar = c.Size }
		end
		return c
	end
	for _, o in ipairs(dane.ozdobySpoczynek) do
		zapamietaj(o.czesc)
	end
	for _, o in ipairs(dane.ozdobyFinal) do
		zapamietaj(o.czesc)
	end
	m:GetAttributeChangedSignal("Final"):Connect(function()
		local t0 = os.clock()
		for _, o in ipairs(dane.ozdobyFinal) do
			local c = m:FindFirstChild(o.czesc)
			if c and j.stan[c] then
				table.insert(j.final, { czesc = c, o = o, t0 = t0 + (o.t or 0) })
			end
		end
	end)
	return j
end

local function szukaj()
	local k = workspace:FindFirstChild(W.kontener)
	if not k then
		return
	end
	for _, dane in pairs(D.jajka) do
		local m = k:FindFirstChild(dane.model)
		if m and m:IsA("Model") and not jajka[m] then
			local j = przygotuj(m, dane)
			if j then
				jajka[m] = j
			end
		end
	end
end

task.spawn(function()
	workspace:WaitForChild(W.kontener, 120)
	local k = workspace:FindFirstChild(W.kontener)
	if not k then
		return
	end
	szukaj()
	k.ChildAdded:Connect(function()
		task.wait(0.5)
		szukaj()
	end)
end)

local function obwiednia(u: number, czas: number, powrot: number): number
	-- 0 -> 1 w „czas” (łagodnie), potem tłumiona sprężyna do 0 w „powrot”
	if u < 0 then
		return 0
	end
	if u < czas then
		return math.sin(u / czas * math.pi / 2)
	end
	local v = u - czas
	return math.exp(-v * 4 / math.max(powrot, 0.1)) * math.cos(v * 9)
end

RunService.RenderStepped:Connect(function()
	local cam = workspace.CurrentCamera
	local t = os.clock()
	for m, j in pairs(jajka) do
		if not m.Parent then
			jajka[m] = nil
			continue
		end
		if cam and (cam.CFrame.Position - j.korzen.Position).Magnitude > ZASIEG then
			continue
		end
		local s = m:GetScale()
		local sp = W.spoczynek
		-- jajo i pęknięcia (scenka wyklucia ma pierwszeństwo)
		if m:GetAttribute("Wyklucie") ~= true then
			local a = sp.kolysanie
			local rz = math.sin(t * 2 * math.pi / sp.okresZ) * a
			local rx = math.sin(t * 2 * math.pi / sp.okresX + 1) * a * 0.6
			local podstawa = j.korzen.CFrame
			j.jajo.CFrame = podstawa * CFrame.Angles(rx, 0, rz) * podstawa:ToObjectSpace(j.domJaja)
			if j.emisja then
				local puls = sp.blask * (1 - sp.puls + sp.puls * math.sin(t * (2 + sp.blask * 6)))
				local ok = pcall(function()
					for _, sa in ipairs(j.blaski) do
						(sa :: any).EmissiveStrength = puls
					end
				end)
				j.emisja = ok
			end
		end
		-- ozdoby: stan wyjściowy + ruchy spoczynku + reakcje na finał
		local wynik = {}
		for c, st in pairs(j.stan) do
			wynik[c] = { cf = st.dom, kolor = st.kolor, przezr = st.przezr, skala = 1 }
		end
		local wiatr = Vector3.new(j.dane.wiatr.X, 0, j.dane.wiatr.Z)
		local osWiatru = Vector3.yAxis:Cross(wiatr)
		for _, o in ipairs(j.dane.ozdobySpoczynek) do
			local c = m:FindFirstChild(o.czesc)
			local w = c and wynik[c]
			if w then
				local st = j.stan[c]
				local f = math.sin(t * 2 * math.pi / o.okres + (o.faza or 0))
				if o.ruch == "wiatr" then
					local dol = (st.dom * CFrame.new(0, -st.rozmiar.Y / 2, 0)).Position
					w.cf = obrot(w.cf, dol, osWiatru, o.amplituda * (0.6 + 0.4 * f) * f)
				elseif o.ruch == "kolysanie" then
					w.cf = obrot(w.cf, st.dom.Position, Vector3.yAxis, o.amplituda * f)
				elseif o.ruch == "unoszenie" then
					w.cf = w.cf + Vector3.new(0, o.wysokosc * s * f, 0)
				elseif o.ruch == "pulsNeonu" then
					w.przezr = o.przezroczystosc[1] + (o.przezroczystosc[2] - o.przezroczystosc[1]) * (0.5 + 0.5 * f)
				elseif o.ruch == "pulsKoloru" then
					w.kolor = st.kolor:Lerp(Color3.new(1, 1, 1), o.jasniej * (0.5 + 0.5 * f))
				end
			end
		end
		for i = #j.final, 1, -1 do
			local r = j.final[i]
			local o, c = r.o, r.czesc
			local w = wynik[c]
			local u = t - r.t0
			local koniec = false
			if w and u >= 0 then
				local st = j.stan[c]
				if o.ruch == "odchylenie" then
					local od = st.dom.Position - j.korzen.Position
					local os_ = Vector3.yAxis:Cross(Vector3.new(od.X, 0, od.Z))
					local dol = (st.dom * CFrame.new(0, -st.rozmiar.Y / 2, 0)).Position
					w.cf = obrot(w.cf, dol, os_, o.kat * obwiednia(u, o.czas, o.powrotS))
					koniec = u > o.czas + o.powrotS
				elseif o.ruch == "pekniecie" then
					if u < o.czas then
						w.skala = 1 + (o.skala - 1) * u / o.czas
						w.przezr = st.przezr + (1 - st.przezr) * u / o.czas
					elseif u < o.powrotPoS then
						w.przezr = 1
					elseif u < o.powrotPoS + 0.4 then
						w.przezr = 1 - (1 - w.przezr) * (u - o.powrotPoS) / 0.4
					else
						koniec = true
					end
				elseif o.ruch == "blysk" then
					local kolor = m:GetAttribute("KolorRzadkosci") or j.dane.kolorZyl
					local k = if u < o.czas * 0.25 then 1 else math.max(0, 1 - (u - o.czas * 0.25) / (o.czas * 0.75))
					w.kolor = w.kolor:Lerp(kolor, k)
					koniec = u > o.czas
				end
			end
			if koniec or not w then
				table.remove(j.final, i)
			end
		end
		for c, w in pairs(wynik) do
			local st = j.stan[c]
			c.CFrame = w.cf
			if c.Color ~= w.kolor then
				c.Color = w.kolor
			end
			if c.Transparency ~= w.przezr then
				c.Transparency = w.przezr
			end
			local rozmiar = st.rozmiar * w.skala
			if c.Size ~= rozmiar then
				c.Size = rozmiar
			end
		end
	end
end)
