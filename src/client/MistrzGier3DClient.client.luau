--!nonstrict
--[[
	MistrzGier3DClient — plansza mistrza gier jako model 3D na jego stole (Paweł 25.11: „na stole rzeczywista plansza
	z polami, po E kamera przenosi się na planszę, w tle widać mistrza gier, gracz rzeczywiście rzuca kostkami”).

	Paweł 26.11: model planszy i kostka przeniesione z jego artefaktu „Treasure Loop” (rysunek izometryczny 2D →
	części Robloxa): rama ze złotymi okuciami, pętla 36 pól (START + 3 złote narożniki + 4 × 8 pól), łąka ze stawem
	i mostem, las, świątynia, wyspa z portalem i złotą skrzynią, pionek kot-czarodziej, drewniana kostka na tacy.
	Wymiary z artefaktu: 1 kratka = U studów; piksele rysunku → kratki przez PX (poziomo) i PZ (pionowo).
	Nakładka 2D (tytuł, ROLL, LEAVE, cena, wstęga, gwiazda nagrody) bez zmian.

	Zasady i nagrody liczy serwer: src/server/MistrzGier.server.luau (ReplicatedStorage.MistrzGier: "stan" | "rzut").
	Pola serwera 1..36 = pola pętli (1 = START), pole 37 = powrót na START (gwiazda, nowa plansza).

	Plansza powstaje LOKALNIE u gracza przy starcie (nic nie zapisuje się w Studio ani u innych graczy): stoi na blacie
	stołu w karczmie bazaru (Workspace/MiasteczkoBazar/Karczma/„Stół blat”); taca na kostkę stoi obok na lokalnym
	stoliku w kolorach stołu. Ozdobna plansza, pionki i kostka z mapy Karola są u gracza ukrywane (tylko
	przezroczystość po stronie klienta) — pliki i obiekty Karola bez zmian.

	Sterowanie: E „Zagraj” przy mistrzu (ReplicatedStorage.OknoMiejsca "mistrz_gier") → kamera nad stół; ROLL albo
	spacja = rzut; LEAVE, Esc albo odejście = powrót kamery.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")
local PPS = game:GetService("ProximityPromptService")

local player = Players.LocalPlayer
local F = RS:WaitForChild("MistrzGier") :: RemoteFunction

------------------------------------------------------------ wymiary z artefaktu
local U = 0.33 -- studów na kratkę planszy
local L, C, NS, M = 11, 1.5, 8, 0.7 -- bok pętli, narożnik, pól na bok, margines ramy (kratki)
local PX, PZ = 1 / 56.57, 1 / 47.2 -- piksel rysunku → kratki: poziomo i pionowo
local RAMA, TH = 46 * PZ, 10 * PZ -- grubość ramy i wysokość pola
local CT = 0.05 -- grubość wierzchu pola
local NOZKI, EPS = 0.1, 0.003 -- studów: nóżki ramy, odstęp płaskich warstw
local OBROT_PODPISU = 0 -- stopnie: wspólna poprawka obrotu płaskich podpisów pól (patrz „Podpis”)
local ZT = 7 * EPS / U -- poziom trawy (kratki)
local LICZBA_POL = 4 * (NS + 1)

local function hex(s: string): Color3
	return Color3.fromHex(s)
end
local INK = hex("#1d1522")
local FONT = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
local FONT_PLANSZY = Font.fromEnum(Enum.Font.FredokaOne)
local IKONY = {
	rybki = "rbxassetid://76704302626777",
	gwiazda = "rbxassetid://76704302626777",
	skarb = "rbxassetid://76704302626777",
	diamenty = "rbxassetid://130974323293639",
	przedmiot = "rbxassetid://71553702739963",
}
local POZIOMY = { -- kolory pól wg numeru planszy (artefakt: x1, x2, x4, x8)
	{ top = hex("#e6e0d2"), side = hex("#b7af9e"), dark = hex("#8f8778") },
	{ top = hex("#a5e0f7"), side = hex("#5eaed6"), dark = hex("#3c86ad") },
	{ top = hex("#d6b6fa"), side = hex("#9d73d6"), dark = hex("#7650ad") },
	{ top = hex("#ffb9cc"), side = hex("#e3748f"), dark = hex("#b84f6b") },
}
local KOLOR_START = { top = hex("#63d65c"), side = hex("#34a53f"), dark = hex("#237a30") }
local KOLOR_ZLOTE = { top = hex("#ffd84d"), side = hex("#eaa41c"), dark = hex("#b97a0e") }
local OZDOBY_KAROLA = { ["Plansza"] = true, ["Plansza pole"] = true, ["Pionek"] = true, ["Kostka"] = true, ["Kostka oczko"] = true }

local function bindable(name: string): BindableEvent
	local e = RS:FindFirstChild(name)
	if not e then
		e = Instance.new("BindableEvent")
		e.Name = name
		e.Parent = RS
	end
	return e :: BindableEvent
end
local okna = bindable("OknoMiejsca")

------------------------------------------------------------ układ stołu
local karczma = workspace:WaitForChild("MiasteczkoBazar", 120)
karczma = karczma and karczma:WaitForChild("Karczma", 60)
local blat = karczma and karczma:WaitForChild("Stół blat", 60)
if not (karczma and blat and blat:IsA("BasePart")) then
	warn("[MistrzGier3D] brak stołu mistrza gier (MiasteczkoBazar/Karczma/Stół blat) — zostaje płaskie okno")
	return
end

local srodekBlatu = blat.Position
local gora = srodekBlatu.Y + math.min(blat.Size.X, blat.Size.Y, blat.Size.Z) / 2
-- kierunek „do mistrza”: od punktu E gracza przez stół (bez punktu: −Z jak na mapie z 25.11)
local przod = Vector3.new(0, 0, -1)
do
	local gra = workspace:FindFirstChild("MiasteczkoBazarGra")
	local inter = karczma:FindFirstChild("_Interakcja")
	local punkt = inter and inter:FindFirstChild("Punkt E mistrz_gier")
	if not punkt and gra then
		local p = gra:FindFirstChild("Punkty")
		punkt = p and p:FindFirstChild("E mistrz_gier")
	end
	local mistrz = karczma:FindFirstChild("MistrzGier")
	if mistrz and mistrz:IsA("Model") then
		local d = mistrz:GetPivot().Position - srodekBlatu
		d = Vector3.new(d.X, 0, d.Z)
		if d.Magnitude > 0.5 then
			przod = d.Unit
		end
	elseif punkt and punkt:IsA("BasePart") then
		local d = srodekBlatu - punkt.Position
		d = Vector3.new(d.X, 0, d.Z)
		if d.Magnitude > 0.5 then
			przod = d.Unit
		end
	end
end
local UP = Vector3.yAxis
local prawo = przod:Cross(UP).Unit
local baza = Vector3.new(srodekBlatu.X, gora, srodekBlatu.Z)

local function miejsce(x: number, y: number, z: number): Vector3
	return baza + prawo * x + UP * y + przod * z
end

-- plansza stoi rombem jak na rysunku: START przy graczu, daleki narożnik pod mistrzem
local vx = (prawo - przod).Unit -- kierunek +gx kratek
local vz = (-prawo - przod).Unit -- kierunek +gy kratek
local B = CFrame.fromMatrix(baza + UP * (NOZKI + RAMA * U), vx, UP, vz) -- Y = 0 to wierzch ramy
local SPR = CFrame.Angles(0, math.pi / 4, 0) -- układ „rysunku”: X w prawo gracza, Z do gracza

local function G(gx: number, gy: number, z: number?): CFrame
	return B * CFrame.new((gx - L / 2) * U, (z or 0) * U, (gy - L / 2) * U)
end
local function S(gx: number, gy: number, z: number?): CFrame
	return G(gx, gy, z) * SPR
end

-- ozdoby z mapy Karola: tylko u tego gracza i tylko przezroczystość (plansza 3 × 3, pionki, kostka)
for _, p in ipairs(karczma:GetChildren()) do
	if p:IsA("BasePart") and OZDOBY_KAROLA[p.Name] and (p.Position - baza).Magnitude < 5 then
		p.Transparency = 1
		p.CanCollide = false
	end
end

------------------------------------------------------------ cegiełki modelu
local model = Instance.new("Model")
model.Name = "MistrzGierPlansza3D"

local function grupa(nazwa: string, obrys: boolean?, rodzic: Instance?): Model
	local g = Instance.new("Model")
	g.Name = nazwa
	g.Parent = rodzic or model
	if obrys then -- czarny kontur jak tusz na rysunku
		local h = Instance.new("Highlight")
		h.FillTransparency = 1
		h.OutlineColor = INK
		h.OutlineTransparency = 0
		h.DepthMode = Enum.HighlightDepthMode.Occluded
		h.Parent = g
	end
	return g
end

local function nowa(klasa: string, rodzic: Instance, nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3): any
	local p = Instance.new(klasa) :: any
	p.Name = nazwa
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
	p.Size = Vector3.new(math.max(rozmiar.X, 0.001), math.max(rozmiar.Y, 0.001), math.max(rozmiar.Z, 0.001))
	p.CFrame, p.Color, p.Material = cf, kolor, Enum.Material.SmoothPlastic
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Parent = rodzic
	return p
end

local function blok(rodzic: Instance, nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3): Part
	return nowa("Part", rodzic, nazwa, rozmiar, cf, kolor)
end

-- walec stojący: oś = Y układu cf
local function walec(rodzic: Instance, nazwa: string, promien: number, wysokosc: number, cf: CFrame, kolor: Color3): Part
	local p = nowa("Part", rodzic, nazwa, Vector3.new(wysokosc, promien * 2, promien * 2), cf * CFrame.Angles(0, 0, math.pi / 2), kolor)
	p.Shape = Enum.PartType.Cylinder
	return p
end

local function kula(rodzic: Instance, nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3): Part
	local p = nowa("Part", rodzic, nazwa, rozmiar, cf, kolor)
	local m = Instance.new("SpecialMesh")
	m.MeshType = Enum.MeshType.Sphere
	m.Parent = p
	return p
end

-- układ w połowie odcinka a–b z osią X wzdłuż odcinka
local function osX(a: Vector3, b: Vector3): CFrame
	local x = (b - a).Unit
	local pom = if math.abs(x.Y) > 0.99 then Vector3.xAxis else Vector3.yAxis
	local z = x:Cross(pom).Unit
	return CFrame.fromMatrix((a + b) / 2, x, z:Cross(x), z)
end

local function pret(rodzic: Instance, nazwa: string, a: Vector3, b: Vector3, promien: number, kolor: Color3): Part
	local p = nowa("Part", rodzic, nazwa, Vector3.new((b - a).Magnitude, promien * 2, promien * 2), osX(a, b), kolor)
	p.Shape = Enum.PartType.Cylinder
	return p
end

-- belka a–b: szer wzdłuż wskazanego kierunku, grub prostopadle
local function belka(rodzic: Instance, nazwa: string, a: Vector3, b: Vector3, szer: number, grub: number, wskaz: Vector3, kolor: Color3): Part
	local x = (b - a).Unit
	local z = (wskaz - x * wskaz:Dot(x)).Unit
	return nowa("Part", rodzic, nazwa, Vector3.new((b - a).Magnitude, grub, szer), CFrame.fromMatrix((a + b) / 2, x, z:Cross(x), z), kolor)
end

-- trójkąt prostokątny: kąt prosty w r, przyprostokątne r–p i r–q (WedgePart: pion przy +Z, skos do −Z)
local function klin(rodzic: Instance, nazwa: string, r: Vector3, p: Vector3, q: Vector3, grub: number, kolor: Color3): WedgePart
	local y = (p - r).Unit
	local z = (r - q).Unit
	return nowa("WedgePart", rodzic, nazwa, Vector3.new(grub, (p - r).Magnitude, (q - r).Magnitude),
		CFrame.fromMatrix((p + q) / 2, y:Cross(z), y, z), kolor)
end

-- dowolny trójkąt = dwa kliny wzdłuż wysokości opuszczonej na najdłuższy bok
local function trojkat(rodzic: Instance, nazwa: string, a: Vector3, b: Vector3, c: Vector3, grub: number, kolor: Color3)
	local ab, bc, ca = (b - a).Magnitude, (c - b).Magnitude, (a - c).Magnitude
	if bc > ab and bc >= ca then
		a, b, c = b, c, a
	elseif ca > ab and ca > bc then
		a, b, c = c, a, b
	end
	local t = (c - a):Dot(b - a) / (b - a):Dot(b - a)
	local h = a + (b - a) * t
	if (c - h).Magnitude < 1e-4 then
		return
	end
	if (a - h).Magnitude > 1e-4 then
		klin(rodzic, nazwa, h, c, a, grub, kolor)
	end
	if (b - h).Magnitude > 1e-4 then
		klin(rodzic, nazwa, h, c, b, grub, kolor)
	end
end

-- płaska płyta na planszy: prostokąt kratek, wierzch na wysokości `wierzch` studów nad ramą
local function plyta(rodzic: Instance, nazwa: string, x0: number, y0: number, x1: number, y1: number, wierzch: number, kolor: Color3): Part
	return blok(rodzic, nazwa, Vector3.new((x1 - x0) * U, 0.02, (y1 - y0) * U),
		G((x0 + x1) / 2, (y0 + y1) / 2, 0) * CFrame.new(0, wierzch - 0.01, 0), kolor)
end

local function krazek(rodzic: Instance, nazwa: string, gx: number, gy: number, r: number, wierzch: number, kolor: Color3): Part
	return walec(rodzic, nazwa, r * U, 0.012, G(gx, gy, 0) * CFrame.new(0, wierzch - 0.006, 0), kolor)
end

-- pudło z rysunku (bqBox): środek, półwymiary, dół i wysokość w kratkach; wierzch może mieć własny kolor
local function pudlo(rodzic: Instance, nazwa: string, gx: number, gy: number, ax: number, ay: number, z0: number, h: number, bok: Color3, wierzch: Color3?)
	local ct = if wierzch then math.min(h * 0.35, 0.05) else 0
	blok(rodzic, nazwa, Vector3.new(2 * ax, h - ct, 2 * ay) * U, G(gx, gy, z0 + (h - ct) / 2), bok)
	if wierzch then
		blok(rodzic, nazwa .. " wierzch", Vector3.new(2 * ax, ct, 2 * ay) * U, G(gx, gy, z0 + h - ct / 2), wierzch)
	end
end

-- przelicznik pikseli rysunku w układzie o (X w prawo, Y w górę, Z do gracza), skala s
local function px(o: CFrame, s: number)
	local kx, ky = PX * U * s, PZ * U * s
	return function(x: number, y: number, z: number?): Vector3
		return o * Vector3.new(x * kx, y * ky, (z or 0) * kx)
	end, kx, ky
end

local function powierzchnia(p: BasePart, pps: number): SurfaceGui
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Top -- na wierzchu: prawo napisu = −Z części, góra napisu = −X części
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = pps
	sg.LightInfluence = 0 -- wierzchy pól i łąka w czystych kolorach z rysunku, niezależnie od światła karczmy
	sg.Parent = p
	return sg
end

local cienie = grupa("Cienie")
local function cien(o: CFrame, promien: number)
	local p = walec(cienie, "Cień", promien, 0.006, o * CFrame.new(0, 0.004, 0), Color3.fromRGB(20, 60, 20))
	p.Transparency = 0.72
end

------------------------------------------------------------ rośliny i rekwizyty (duszki z rysunku)
local function drzewo(g: Instance, o: CFrame, s: number)
	local v, kx = px(o, s)
	cien(o, 16 * kx)
	pret(g, "Pień", v(0, 0, 0), v(0, 26, 0), 4 * kx, hex("#8a5424"))
	for _, c in ipairs({ { 0, 38, 0, 17 }, { -13, 27, 0, 12.5 }, { 13, 27, 0, 12.5 }, { 0, 24, 7, 12 }, { 0, 29, -8, 12.5 } }) do
		kula(g, "Korona", Vector3.one * (2 * c[4] * kx), CFrame.new(v(c[1], c[2], c[3])), hex("#2f9440"))
	end
	for _, c in ipairs({ { -1.5, 40.5, 5, 13.8 }, { -14.5, 29.5, 4, 9.3 }, { 11.5, 29.5, 4, 9.3 } }) do
		kula(g, "Korona jasna", Vector3.one * (2 * c[4] * kx), CFrame.new(v(c[1], c[2], c[3])), hex("#55c44e"))
	end
end

local function grzyb(g: Instance, o: CFrame, s: number)
	local v, kx, ky = px(o, s)
	cien(o, 7 * kx)
	pret(g, "Trzon", v(0, 0, 0), v(0, 9, 0), 2.6 * kx, hex("#fff1d6"))
	kula(g, "Kapelusz", Vector3.new(16 * kx, 12 * ky, 16 * kx), CFrame.new(v(0, 11.5, 0)), hex("#e8362f"))
	for _, d in ipairs({ { -3, 12.5, 6.8 }, { 3.2, 11, 7 }, { 0.6, 15.6, 5 } }) do
		kula(g, "Kropka", Vector3.one * (3 * kx), CFrame.new(v(d[1], d[2], d[3])), Color3.new(1, 1, 1))
	end
end

-- liść: z punktu (bx, by) pod kątem ang (jak canvas: ujemny = w górę), mir = strona, odchyl = wychylenie do gracza
local function lisc(g: Instance, v: any, kx: number, bx: number, by: number, mir: number, ang: number, len: number, w: number, kolor: Color3, odchyl: number?)
	local a = v(bx, by, 0)
	local b = v(bx + mir * math.cos(ang) * len, by - math.sin(ang) * len, odchyl or 0)
	kula(g, "Liść", Vector3.new((b - a).Magnitude, w * kx * 0.9, w * kx * 0.35), osX(a, b), kolor)
end

local function palma(g: Instance, o: CFrame, s: number, lean: number)
	local v, kx = px(o, s)
	cien(o, 14 * kx)
	local tx, ty, mx, my = lean * 9, 56, lean * -7, 30
	local function pien(t: number): Vector3
		local u = 1 - t
		return v(2 * u * t * mx + t * t * tx, 2 * u * t * my + t * t * ty, 0)
	end
	for k = 0, 4 do
		pret(g, "Pień", pien(k / 5), pien((k + 1) / 5 + 0.02), 3.4 * kx, hex("#b07a3c"))
		if k > 0 then
			pret(g, "Pierścień", pien(k / 5 - 0.012), pien(k / 5 + 0.012), 3.7 * kx, hex("#7a4f22"))
		end
	end
	local C1, C2 = hex("#2f9440"), hex("#46b84c")
	for _, mir in ipairs({ 1, -1 }) do
		lisc(g, v, kx, tx, ty, mir, -1.3, 24, 9, C1)
		lisc(g, v, kx, tx, ty, mir, -0.6, 32, 10, C2)
		lisc(g, v, kx, tx, ty, mir, 0.25, 30, 9, C1)
		lisc(g, v, kx, tx, ty, mir * 0.35, -0.2, 26, 9, C2, mir * 22)
	end
	kula(g, "Kokos", Vector3.one * (6.4 * kx), CFrame.new(v(tx - 3, ty - 3, 2)), hex("#7a4a22"))
	kula(g, "Kokos", Vector3.one * (6 * kx), CFrame.new(v(tx + 3.5, ty - 4, 2)), hex("#8a5424"))
end

local function paproc(g: Instance, o: CFrame, s: number)
	local v, kx = px(o, s)
	cien(o, 10 * kx)
	lisc(g, v, kx, 0, 0, 1, -1.45, 16, 5, hex("#2f9440"))
	for _, mir in ipairs({ 1, -1 }) do
		lisc(g, v, kx, 0, 0, mir, -0.85, 17, 5.5, hex("#46b84c"), mir * 3)
		lisc(g, v, kx, 0, 0, mir, -0.3, 15, 5, hex("#3aa544"), mir * -3)
	end
	lisc(g, v, kx, 0, 0, 0.2, -0.7, 15, 5, hex("#46b84c"), 11)
end

local function skala(g: Instance, o: CFrame, s: number)
	local v, kx, ky = px(o, s)
	cien(o, 12 * kx)
	blok(g, "Skała", Vector3.new(18 * kx, 11 * ky, 13 * kx), CFrame.new(v(-1, 5, 0)) * o.Rotation * CFrame.Angles(0.1, 0.5, 0.16), hex("#bdb6a6"))
	blok(g, "Skała", Vector3.new(9 * kx, 9 * ky, 10 * kx), CFrame.new(v(6, 4, 1)) * o.Rotation * CFrame.Angles(-0.1, -0.3, -0.25), hex("#9a9383"))
end

local function trzcina(g: Instance, o: CFrame, s: number)
	local v, kx, ky = px(o, s)
	for k = 0, 2 do
		local bx, tx, ty = k * 4 - 4, k * 6 - 6, 17 + (k % 2) * 6
		pret(g, "Łodyga", v(bx, 0, 0), v(tx, ty, 0), 1.1 * kx, hex("#4c9a3f"))
		kula(g, "Pałka", Vector3.new(4.6 * kx, 9.2 * ky, 4.6 * kx), CFrame.new(v(tx, ty + 3, 0)), hex("#7a4a22"))
	end
end

local function skrzynia(g: Instance, o: CFrame, s: number, zlota: boolean)
	local v, kx, ky = px(o, s)
	local korpus = if zlota then hex("#f2b02a") else hex("#a85a22")
	local wieko = if zlota then hex("#ffc83a") else hex("#c06a28")
	local okucie = if zlota then hex("#b8651f") else hex("#ffcf3a")
	local listwa = if zlota then hex("#ffe27a") else hex("#ffcf3a")
	local function box(nazwa: string, x0: number, x1: number, y0: number, y1: number, z0: number, z1: number, kolor: Color3)
		blok(g, nazwa, Vector3.new((x1 - x0) * kx, (y1 - y0) * ky, (z1 - z0) * kx),
			o.Rotation + v((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), kolor)
	end
	box("Skrzynia", -26, 26, 0, 24, -20, 20, korpus)
	pret(g, "Wieko", v(-28, 26, 0), v(28, 26, 0), 20 * kx, wieko)
	for _, x in ipairs({ -20, 13 }) do
		box("Okucie", x, x + 7, 0, 24.3, -20.6, 20.6, okucie)
		pret(g, "Okucie wieka", v(x, 26, 0), v(x + 7, 26, 0), 20.7 * kx, okucie)
	end
	box("Listwa", -28.5, 28.5, 23, 29, -21.2, 21.2, listwa)
	box("Zamek", -5.5, 5.5, 19, 31, 21, 23, hex("#fff0a8"))
	box("Dziurka", -1.5, 1.5, 23, 28, 23, 23.6, INK)
end

-- portal: kamienny łuk ze świecącym wnętrzem; zwraca światło do pulsowania
local function portal(g: Instance, o: CFrame, s: number): PointLight
	local v, kx, ky = px(o, s)
	local K = hex("#cbc5b6")
	cien(o, 34 * kx)
	local function box(nazwa: string, x0: number, x1: number, y0: number, y1: number, z0: number, z1: number, kolor: Color3): Part
		return blok(g, nazwa, Vector3.new((x1 - x0) * kx, (y1 - y0) * ky, (z1 - z0) * kx),
			o.Rotation + v((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), kolor)
	end
	box("Filar", -29, -17, 0, 52, -5, 5, K)
	box("Filar", 17, 29, 0, 52, -5, 5, K)
	for _, y in ipairs({ 18, 38 }) do
		box("Fuga", -29.5, -16.5, y, y + 1.3, -5.4, 5.4, hex("#7d7767"))
		box("Fuga", 16.5, 29.5, y, y + 1.3, -5.4, 5.4, hex("#7d7767"))
	end
	local function luk(kat: number): Vector3
		return v(23 * math.cos(kat), 52 + 23 * math.sin(kat) * kx / ky, 0)
	end
	local n = 8
	for i = 0, n - 1 do
		local p = belka(g, "Łuk", luk(i * math.pi / n), luk((i + 1) * math.pi / n), 10 * kx, 12 * kx, o.ZVector, K)
		p.Size = Vector3.new(p.Size.X * 1.3, p.Size.Y, p.Size.Z)
	end
	local blask = box("Blask", -17, 17, 0, 52, -1, 1, hex("#e9ff9a"))
	blask.Material = Enum.Material.Neon
	local szczyt = pret(g, "Blask", v(0, 52, -1), v(0, 52, 1), 17 * kx, hex("#f6ffc4"))
	szczyt.Material = Enum.Material.Neon
	kula(g, "Krzak", Vector3.new(12 * kx, 6 * ky, 8 * kx), CFrame.new(v(-22, 1.5, 5)), hex("#55c44e"))
	kula(g, "Krzak", Vector3.new(10 * kx, 5.2 * ky, 7 * kx), CFrame.new(v(24, 2, 5)), hex("#55c44e"))
	local sw = Instance.new("PointLight")
	sw.Color, sw.Range, sw.Brightness, sw.Shadows = Color3.fromRGB(233, 255, 154), 2.4, 1.1, false
	sw.Parent = blask
	return sw
end

------------------------------------------------------------ rama planszy
do
	local g = grupa("Rama", true)
	local a0, a1 = -M, L + M
	local sr, pol = (a0 + a1) / 2, (a1 - a0) / 2
	for _, n in ipairs({ { a0 + 0.7, a0 + 0.7 }, { a1 - 0.7, a0 + 0.7 }, { a1 - 0.7, a1 - 0.7 }, { a0 + 0.7, a1 - 0.7 } }) do
		walec(g, "Nóżka", 0.45 * U, NOZKI + 0.02, G(n[1], n[2], -RAMA) * CFrame.new(0, -NOZKI / 2 + 0.01, 0), hex("#c98a12"))
	end
	local zD, zG = 7 * PZ, 9 * PZ
	pudlo(g, "Listwa dolna", sr, sr, pol + 0.04, pol + 0.04, -RAMA, zD, hex("#f2b632"))
	pudlo(g, "Bok", sr, sr, pol, pol, -RAMA + zD, RAMA - zD - zG, hex("#a05c2b"))
	for _, zp in ipairs({ 20, 31 }) do
		pudlo(g, "Rowek", sr, sr, pol + 0.012, pol + 0.012, -zp * PZ - 0.02, 0.04, hex("#7a431d"))
	end
	pudlo(g, "Listwa górna", sr, sr, pol + 0.04, pol + 0.04, -zG, zG, hex("#ffd24a"))

	-- wierzch: drewno, złote narożniki, ciemne dno pod polami
	plyta(g, "Drewno obrys", a0 + 0.27, a0 + 0.27, a1 - 0.27, a1 - 0.27, 1 * EPS, INK)
	plyta(g, "Drewno", a0 + 0.3, a0 + 0.3, a1 - 0.3, a1 - 0.3, 2 * EPS, hex("#b56d30"))
	plyta(g, "Dno obrys", -0.13, -0.13, L + 0.13, L + 0.13, 4 * EPS, INK)
	plyta(g, "Dno", -0.1, -0.1, L + 0.1, L + 0.1, 5 * EPS, hex("#6b4020"))

	local ZLOTO = hex("#ffd84d")
	local stopnie = { { 84 * PX, 0, 0.3 }, { 56 * PX, 0.3, 0.62 }, { 26 * PX, 0.62, 1 } }
	for _, r in ipairs({ { a0, a0, 1, 1 }, { a1, a0, -1, 1 }, { a1, a1, -1, -1 }, { a0, a1, 1, -1 } }) do
		local cx, cy, ix, iy = r[1], r[2], r[3], r[4]
		-- okucia na bokach ramy: trzy schodki zwężające się ku dołowi
		for _, st in ipairs(stopnie) do
			local w = st[1]
			local half = (w + 0.07) / 2
			pudlo(g, "Okucie", cx + ix * (w - 0.07) / 2, cy + iy * (w - 0.07) / 2, half, half, -RAMA * st[3], RAMA * (st[3] - st[2]), ZLOTO)
		end
		-- ozdobne guzy na obu ścianach przy narożniku
		for _, sciana in ipairs({ 1, 2 }) do
			local wzdluz = if sciana == 1 then Vector3.new(ix * 26 * PX, 0, 0) else Vector3.new(0, 0, iy * 26 * PX)
			local normalna = if sciana == 1 then Vector3.new(0, 0, -iy) else Vector3.new(-ix, 0, 0)
			local srodek = G(cx, cy, -RAMA * 0.36) * CFrame.new((wzdluz + normalna * 0.07) * U)
			local n = (B.Rotation * normalna)
			for _, k in ipairs({ { 8, 0.03, "#a8690c" }, { 5.6, 0.05, "#ffd84d" }, { 2.4, 0.07, "#a8690c" } }) do
				pret(g, "Guz", srodek.Position, srodek.Position + n * (k[2] * U), k[1] * PX * U, hex(k[3]))
			end
		end
		-- złoty narożnik na wierzchu (latawiec z rysunku = kwadrat + dwa trójkąty) i nit
		local h = 3 * EPS - 0.006
		local function pkt(dx: number, dy: number): Vector3
			return (G(cx + ix * dx, cy + iy * dy, 0) * CFrame.new(0, h, 0)).Position
		end
		blok(g, "Narożnik", Vector3.new(0.44 * U, 0.012, 0.44 * U), CFrame.new(pkt(0.22, 0.22)) * B.Rotation, hex("#ffe27a"))
		klin(g, "Narożnik", pkt(0.44, 0), pkt(1.3, 0), pkt(0.44, 0.44), 0.012, hex("#ffe27a"))
		klin(g, "Narożnik", pkt(0, 0.44), pkt(0, 1.3), pkt(0.44, 0.44), 0.012, hex("#ffe27a"))
		krazek(g, "Nit", cx + ix * 0.3, cy + iy * 0.3, 0.09, 4 * EPS, hex("#c98a12"))
	end
end

------------------------------------------------------------ łąka, staw, sceneria
local swiatloPortalu: PointLight
local srodekPortalu: CFrame
local srodekSkrzyni: Vector3
do
	local g = grupa("Łąka")
	local t0, t1 = C + 0.04, L - C - 0.04
	plyta(g, "Trawa obrys", C + 0.005, C + 0.005, L - C - 0.005, L - C - 0.005, 6 * EPS, INK)
	local trawa = plyta(g, "Trawa", t0, t0, t1, t1, 7 * EPS, hex("#62c24c"))
	local sg = powierzchnia(trawa, 160)
	local pole = Instance.new("Frame")
	pole.BackgroundColor3, pole.BorderSizePixel, pole.Size, pole.ClipsDescendants = hex("#62c24c"), 0, UDim2.fromScale(1, 1), true
	pole.Parent = sg
	local function naTrawie(gx: number, gy: number): UDim2
		return UDim2.fromScale(1 - (gy - t0) / (t1 - t0), (gx - t0) / (t1 - t0))
	end
	for _, p in ipairs({ { 3.0, 8.0, 2.0, "#4dab41" }, { 3.0, 3.2, 1.7, "#58b84a" }, { 8.2, 3.2, 2.1, "#80cf4b" }, { 8.0, 8.0, 2.2, "#4f9f6a" }, { 5.5, 5.5, 2.5, "#7ed65a" } }) do
		local f = Instance.new("Frame")
		f.AnchorPoint, f.BorderSizePixel = Vector2.new(0.5, 0.5), 0
		f.Position, f.Size = naTrawie(p[1], p[2]), UDim2.fromScale(2 * p[3] / (t1 - t0), 2 * p[3] / (t1 - t0))
		f.BackgroundColor3 = hex(p[4])
		local c = Instance.new("UICorner")
		c.CornerRadius = UDim.new(0.5, 0)
		c.Parent = f
		f.Parent = pole
	end
	-- kępki trawy: ten sam generator co w artefakcie (ziarno 7)
	local seed = 7
	local function rnd(): number
		seed = (seed * 16807) % 2147483647
		return (seed - 1) / 2147483646
	end
	for _ = 1, 110 do
		local gx = C + 0.3 + rnd() * (L - 2 * C - 0.6)
		local gy = C + 0.3 + rnd() * (L - 2 * C - 0.6)
		for _, kat in ipairs({ 17, 73 }) do
			local f = Instance.new("Frame")
			f.AnchorPoint, f.BorderSizePixel = Vector2.new(0.5, 1), 0
			f.Position, f.Size, f.Rotation = naTrawie(gx, gy), UDim2.fromOffset(2, 6), kat
			f.BackgroundColor3 = hex("#3f9a3a")
			f.Parent = pole
		end
	end

	-- staw
	for _, s in ipairs({ { 8.0, 8.0, 1.15 }, { 7.3, 8.55, 0.62 } }) do
		krazek(g, "Staw obrys", s[1], s[2], s[3] + 0.07, 8 * EPS, INK)
		krazek(g, "Staw", s[1], s[2], s[3], 9 * EPS, hex("#2f8f86"))
		krazek(g, "Staw woda", s[1], s[2], s[3] - 0.13, 10 * EPS, hex("#74cfc9"))
	end
	krazek(g, "Staw blask", 7.8, 7.75, 0.6, 11 * EPS, hex("#a4e6df"))
	for _, f in ipairs({ { 22, 2, 9 }, { 10, 9, 12 } }) do -- fale: dwa łuki pod środkiem
		local o = S(8.35, 8.35, 0) * CFrame.new(0, 12 * EPS, 0)
		local function pkt(x: number, y: number): Vector3
			return o * Vector3.new(x * PX * U, 0, y / 31.1 * U)
		end
		for _, strona in ipairs({ -1, 1 }) do
			local p = belka(g, "Fala", pkt(strona * f[1], f[2]), pkt(0, (f[2] + f[3]) / 2 + 1.5), 0.012, 0.004, UP:Cross(prawo), Color3.new(1, 1, 1))
			p.Transparency = 0.25
		end
	end
	for _, l in ipairs({ { 7.55, 7.55, true }, { 8.55, 8.5, true }, { 7.3, 8.65, false }, { 8.6, 7.5, false }, { 7.95, 8.75, false } }) do
		krazek(g, "Lilia obrys", l[1], l[2], 0.185, 13 * EPS, INK)
		krazek(g, "Lilia", l[1], l[2], 0.16, 14 * EPS, hex("#43b04c"))
		if l[3] then
			local v, kx, ky = px(S(l[1], l[2], 0) * CFrame.new(0, 14 * EPS, 0), 1)
			kula(g, "Kwiat", Vector3.new(8 * kx, 5.5 * ky, 8 * kx), CFrame.new(v(-1, 2.6, 0)), hex("#ff9ec4"))
			kula(g, "Kwiat środek", Vector3.one * (2.8 * kx), CFrame.new(v(-1, 5, 0)), hex("#ffe14d"))
		end
	end

	-- sceneria: lista z artefaktu (rodzaj, gx, gy, skala, pochylenie palmy)
	local LISTA = {
		{ "tree", 2.6, 7.0, 1.05, 0 }, { "tree", 3.2, 8.5, 1.1, 0 }, { "tree", 2.5, 8.7, 0.85, 0 }, { "tree", 2.9, 6.1, 0.9, 0 }, { "tree", 3.8, 7.4, 0.8, 0 },
		{ "mush", 3.1, 7.7, 1.1, 0 }, { "mush", 3.9, 8.9, 1, 0 }, { "mush", 2.45, 7.9, 0.9, 0 }, { "mush", 4.2, 8.1, 1.1, 0 }, { "mush", 2.9, 9.15, 0.9, 0 },
		{ "tree", 2.9, 3.0, 0.95, 0 }, { "tree", 3.8, 2.6, 0.78, 0 }, { "tree", 2.6, 4.1, 0.85, 0 }, { "mush", 3.4, 3.5, 1, 0 }, { "rock", 4.6, 2.5, 0.9, 0 },
		{ "fern", 3.0, 4.9, 1, 0 }, { "fern", 5.4, 2.6, 0.9, 0 }, { "mush", 5.9, 2.9, 0.9, 0 },
		{ "palm", 6.5, 2.75, 0.95, -1 }, { "palm", 8.95, 4.8, 1.05, 1 }, { "fern", 7.2, 3.3, 1, 0 }, { "fern", 8.1, 4.75, 1.1, 0 }, { "fern", 9.15, 4.0, 1, 0 },
		{ "rock", 9.0, 6.0, 1, 0 }, { "fern", 9.1, 5.4, 1, 0 }, { "mush", 8.2, 6.3, 1, 0 },
		{ "reed", 6.85, 8.95, 1, 0 }, { "reed", 9.1, 7.3, 1, 0 }, { "reed", 8.95, 8.95, 0.9, 0 }, { "rock", 6.55, 9.2, 0.9, 0 },
		{ "tree", 5.1, 8.9, 0.9, 0 }, { "mush", 5.9, 9.1, 1, 0 }, { "fern", 4.6, 9.2, 0.9, 0 },
	}
	table.sort(LISTA, function(a, b)
		return a[2] + a[3] < b[2] + b[3]
	end)
	local sceneria = {}
	for i = 1, 4 do -- cztery grupy na zmianę: sąsiednie rośliny mają osobne kontury
		sceneria[i] = grupa("Sceneria" .. i, true)
	end
	local function duszek(gs: Instance, rodzaj: string, o: CFrame, s: number, extra: number)
		if rodzaj == "tree" then
			drzewo(gs, o, s)
		elseif rodzaj == "mush" then
			grzyb(gs, o, s)
		elseif rodzaj == "palm" then
			palma(gs, o, s, extra)
		elseif rodzaj == "fern" then
			paproc(gs, o, s)
		elseif rodzaj == "rock" then
			skala(gs, o, s)
		elseif rodzaj == "reed" then
			trzcina(gs, o, s)
		end
	end
	for i, d in ipairs(LISTA) do
		duszek(sceneria[(i - 1) % 4 + 1], d[1], S(d[2], d[3], ZT), d[4], d[5])
	end

	-- świątynia w dżungli
	do
		local gs = grupa("Świątynia", true)
		local gx, gy = 8.3, 3.2
		local T1, T2 = hex("#d8d0bc"), hex("#b0a892")
		local sc = krazek(cienie, "Cień", gx + 0.1, gy + 0.1, 1.0, 7 * EPS + 0.003, Color3.fromRGB(20, 60, 20))
		sc.Transparency = 0.75
		pudlo(gs, "Stopień 1", gx, gy, 0.8, 0.8, ZT, 13 * PZ, T2, T1)
		pudlo(gs, "Stopień 2", gx, gy, 0.56, 0.56, ZT + 13 * PZ, 13 * PZ, T2, T1)
		pudlo(gs, "Wieża", gx, gy, 0.34, 0.34, ZT + 26 * PZ, 18 * PZ, T2, T1)
		pudlo(gs, "Daszek", gx, gy, 0.42, 0.42, ZT + 44 * PZ, 5 * PZ, hex("#bdb59f"), hex("#e6dfcc"))
		pudlo(gs, "Fuga", gx, gy, 0.806, 0.806, ZT + 6 * PZ, 0.03, hex("#857d6a"))
		pudlo(gs, "Fuga", gx, gy, 0.566, 0.566, ZT + 19 * PZ, 0.03, hex("#857d6a"))
		pudlo(gs, "Wejście", gx, gy + 0.33, 0.13, 0.02, ZT + 26 * PZ, 12 * PZ, hex("#3a2f3f"))
		for _, m in ipairs({ { -0.45, 0.62, 0.16, 13 }, { 0.6, -0.3, 0.14, 13 }, { -0.3, 0.42, 0.11, 26 } }) do
			kula(gs, "Mech", Vector3.new(2 * m[3], 0.09, 2 * m[3]) * U, G(gx + m[1], gy + m[2], ZT + m[4] * PZ + 0.02), hex("#6ccf52"))
		end
		pret(gs, "Pnącze", G(gx - 0.55, gy + 0.81, ZT + 13 * PZ).Position, G(gx - 0.58, gy + 0.81, ZT + 5 * PZ).Position, 1.1 * PX * U, hex("#46b84c"))
		pret(gs, "Pnącze", G(gx + 0.81, gy + 0.3, ZT + 13 * PZ).Position, G(gx + 0.81, gy + 0.33, ZT + 7 * PZ).Position, 1.1 * PX * U, hex("#46b84c"))
	end

	-- wyspa skarbów: kamienna podstawa, trawa, schody, portal, złota skrzynia
	do
		local gs = grupa("Wyspa", true)
		local Z = ZT + 22 * PZ
		pudlo(gs, "Kamień", 5.5, 5.5, 1.5, 1.5, ZT, 16 * PZ, hex("#aaa494"), hex("#d5cfc0"))
		pudlo(gs, "Trawa wyspy", 5.5, 5.5, 1.38, 1.38, ZT + 16 * PZ, 6 * PZ, hex("#43a33f"), hex("#6fd155"))
		local jasna = walec(gs, "Trawa jasna", 0.95 * U, 0.01, G(5.3, 5.3, Z) * CFrame.new(0, 0.001, 0), hex("#84dd62"))
		jasna.Parent = cienie -- bez konturu
		local SCH1, SCH2 = hex("#b4ae9e"), hex("#e0dacb")
		pudlo(gs, "Schody", 5.5, 7.24, 0.42, 0.22, ZT, 8 * PZ, SCH1, SCH2)
		pudlo(gs, "Schody", 5.5, 7.1, 0.42, 0.1, ZT + 8 * PZ, 8 * PZ, SCH1, SCH2)
		pudlo(gs, "Schody", 7.24, 5.5, 0.22, 0.42, ZT, 8 * PZ, SCH1, SCH2)
		pudlo(gs, "Schody", 7.1, 5.5, 0.1, 0.42, ZT + 8 * PZ, 8 * PZ, SCH1, SCH2)
		local gp = grupa("Portal", true)
		srodekPortalu = S(5.0, 5.0, Z)
		swiatloPortalu = portal(gp, srodekPortalu, 1)
		local gsk = grupa("Skrzynia skarbów", true)
		local oSkrzyni = S(5.95, 5.95, Z) * CFrame.new(0, 0, 4 / 31.1 * U)
		cien(S(5.95, 5.95, Z), 30 * PX * U)
		skrzynia(gsk, oSkrzyni, 0.92, true)
		srodekSkrzyni = oSkrzyni * Vector3.new(17 * PX * U, 40 * PZ * U, 0)
		duszek(sceneria[1], "tree", S(4.4, 5.6, Z), 0.8, 0)
		duszek(sceneria[2], "tree", S(5.6, 4.4, Z), 0.8, 0)
		duszek(sceneria[3], "tree", S(4.5, 6.55, Z), 0.72, 0)
		duszek(sceneria[4], "tree", S(6.55, 4.5, Z), 0.72, 0)
		duszek(sceneria[1], "mush", S(5.05, 6.4, Z), 1, 0)
		duszek(sceneria[2], "mush", S(6.4, 5.05, Z), 1, 0)
		duszek(sceneria[3], "mush", S(6.55, 6.2, Z), 0.9, 0)
	end

	-- most nad stawem
	do
		local gs = grupa("Most", true)
		local n, x0, x1, y, hw = 7, 6.72, 9.28, 8.0, 0.3
		local function arch(t: number): number
			return ZT + (4 + math.sin(math.pi * t) * 11) * PZ
		end
		for i = 0, n - 1 do
			local t0b, t1b = i / n, (i + 1) / n
			local a = G(x0 + (x1 - x0) * (t0b + 0.012), y, arch(t0b)).Position
			local b = G(x0 + (x1 - x0) * (t1b - 0.012), y, arch(t1b)).Position
			belka(gs, "Deska", a, b, 2 * hw * U, 4 * PZ * U, vz, if i % 2 == 1 then hex("#c98a45") else hex("#b97a38"))
		end
		for _, strona in ipairs({ -1, 1 }) do
			local yy = y + strona * hw
			for _, t in ipairs({ 0, 0.5, 1 }) do
				local xx = x0 + (x1 - x0) * t
				pret(gs, "Słupek", G(xx, yy, arch(t) - 2 * PZ).Position, G(xx, yy, arch(t) + 15 * PZ).Position, 1.8 * PX * U, hex("#b9793a"))
			end
			for k = 0, 9 do
				local ta, tb = k / 10, (k + 1) / 10
				pret(gs, "Poręcz", G(x0 + (x1 - x0) * ta, yy, arch(ta) + 13 * PZ).Position,
					G(x0 + (x1 - x0) * tb, yy, arch(tb) + 13 * PZ).Position, 1.3 * PX * U, hex("#d99a55"))
			end
		end
	end
end

------------------------------------------------------------ pola pętli
local grupaPol = grupa("Pola", true)
local pola = {}
local aktywne = {} -- pola w trakcie animacji
local KARTA_W, KARTA_H = 46 * PX * U, 34 * PZ * U
local DO_GRACZA = -przod

local function dodajPole(gx: number, gy: number, typ: string)
	local i = #pola + 1
	local rozmiar = if typ == "norm" then 1 else C
	local h = rozmiar / 2 - 0.07
	local kol = if typ == "start" then KOLOR_START elseif typ == "gold" then KOLOR_ZLOTE else POZIOMY[1]
	local m = Instance.new("Model")
	m.Name = string.format("Pole%02d", i)
	m.Parent = grupaPol
	local baza0 = G(gx, gy, 0)
	local cialo = blok(m, "Bok", Vector3.new(2 * h, TH - CT, 2 * h) * U, baza0 * CFrame.new(0, (TH - CT) / 2 * U, 0), kol.side)
	blok(m, "Obrys", Vector3.new(2 * h + 0.04, 0.035, 2 * h + 0.04) * U, baza0 * CFrame.new(0, (TH - CT - 0.0175) * U, 0), INK)
	local czapka = blok(m, "Góra", Vector3.new(2 * h, CT, 2 * h) * U, baza0 * CFrame.new(0, (TH - CT / 2) * U, 0), kol.top)

	-- wierzch: wewnętrzna ramka i biały połysk na dwóch dalszych krawędziach
	local sg = powierzchnia(czapka, 320)
	local tlo = Instance.new("Frame")
	tlo.Size, tlo.BorderSizePixel, tlo.BackgroundColor3 = UDim2.fromScale(1, 1), 0, kol.top
	tlo.Parent = sg
	local ramka = Instance.new("Frame")
	ramka.AnchorPoint, ramka.Position, ramka.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.5, 0.5), UDim2.fromScale(0.76, 0.76)
	ramka.BackgroundColor3, ramka.BackgroundTransparency, ramka.BorderSizePixel = Color3.new(1, 1, 1), 1, 0
	local obrys = Instance.new("UIStroke")
	obrys.Thickness, obrys.Color = 1.5, kol.dark
	obrys.Parent = ramka
	ramka.Parent = sg
	for _, k in ipairs({ { 0.12, 0.12, 0.76, 0 }, { 0.88, 0.12, 0, 0.76 } }) do
		local f = Instance.new("Frame")
		f.BorderSizePixel, f.BackgroundColor3, f.BackgroundTransparency = 0, Color3.new(1, 1, 1), 0.35
		f.Position = UDim2.fromScale(k[1], k[2])
		f.Size = if k[3] > 0 then UDim2.new(k[3], 0, 0, 2) else UDim2.new(0, 2, k[4], 0)
		f.AnchorPoint = if k[3] > 0 then Vector2.zero else Vector2.new(1, 0)
		f.Parent = sg
	end

	local t = {
		i = i, gx = gx, gy = gy, typ = typ, model = m, baza = baza0, bok = 2 * h * U,
		cialo = cialo, czapka = czapka, tlo = tlo, obrys = obrys, ramka = ramka, gorne = {},
		lift = 0, liftT = 0, dip = 0, spin = -1, czeka = 0, obrocone = true, pop = 0,
		nowa = nil, poziom = 1,
	}

	local szczyt = TH * U
	if typ == "start" then
		-- strzałka kierunku i napis START namalowane na polu (1 piksel rysunku = 1/40 kratki)
		local k = U / 40
		local function pkt(x: number, y: number, wys: number): Vector3
			return baza0 * Vector3.new(x * k, szczyt + wys, y * k)
		end
		for _, w in ipairs({ { 1.25, 0.002, "#1f6b2a" }, { 1, 0.006, "#d6ffb8" } }) do
			local s, wys, kolor = w[1], w[2], hex(w[3])
			local function p(x: number, y: number): Vector3
				return pkt(-4 + (x + 4) * s, -9 + (y + 9) * s, wys)
			end
			trojkat(m, "Strzałka", p(-22, -9), p(-8, -19), p(-8, 1), 0.006, kolor)
			blok(m, "Strzałka", Vector3.new(22 * k * s, 0.006, 8 * k * s), CFrame.new(p(3, -9)) * B.Rotation, kolor)
		end
		local napis = Instance.new("TextLabel")
		napis.BackgroundTransparency = 1
		napis.AnchorPoint, napis.Position, napis.Size, napis.Rotation = Vector2.new(0.5, 0.5), UDim2.fromScale(0.26, 0.5), UDim2.fromScale(0.8, 0.26), 90
		napis.FontFace, napis.TextScaled, napis.TextColor3, napis.Text = FONT_PLANSZY, true, Color3.new(1, 1, 1), "START"
		local st = Instance.new("UIStroke")
		st.Thickness, st.Color = 3, hex("#1f6b2a")
		st.Parent = napis
		napis.Parent = sg
	else
		if typ == "gold" then
			skrzynia(m, S(gx - 0.3, gy - 0.3, TH) * CFrame.new(0, 0, 7 / 31.1 * U), 0.62, true)
		end
		-- Paweł 28.11: ikona i wartość leżą PŁASKO na polu (wcześniej karta unosiła się nad polem). Plansza stoi
		-- rombem, więc podpis jest obrócony o 45° — czyta się poziomo od strony gracza i z kamery z góry. Na polu
		-- złotym podpis leży w bliższym rogu, przed skrzynią.
		local bb = Instance.new("Frame")
		bb.Name = "Podpis"
		-- Paweł 28.11 (trzecia uwaga): kamera idzie za pionkiem, więc podpis leży zgodnie z kierunkiem marszu po
		-- swoim boku pętli (0°, 90°, 180°, 270°) — z kamery za pionkiem pola przed nim czyta się prosto.
		local bokPetli = if i == 1 then 3 else ((i - 2) // (NS + 1)) % 4
		bb.BackgroundTransparency, bb.AnchorPoint, bb.Rotation = 1, Vector2.new(0.5, 0.5), 90 * bokPetli + OBROT_PODPISU
		bb.Position = if typ == "gold" then UDim2.fromScale(0.33, 0.67) else UDim2.fromScale(0.5, 0.5)
		bb.Size = if typ == "gold" then UDim2.fromScale(0.5, 0.26) else UDim2.fromScale(0.7, 0.7)
		local skalaPodpisu = Instance.new("UIScale")
		skalaPodpisu.Parent = bb
		local ikona
		if typ ~= "gold" then
			ikona = Instance.new("ImageLabel")
			ikona.BackgroundTransparency = 1
			ikona.Position, ikona.Size = UDim2.fromScale(0.2, 0.02), UDim2.fromScale(0.6, 0.54)
			ikona.ScaleType = Enum.ScaleType.Fit
			ikona.Parent = bb
		end
		local napis = Instance.new("TextLabel")
		napis.BackgroundTransparency = 1
		napis.Position, napis.Size = UDim2.fromScale(0, if typ == "gold" then 0 else 0.54), UDim2.fromScale(1, if typ == "gold" then 1 else 0.46)
		napis.FontFace, napis.TextScaled, napis.TextColor3, napis.Text = FONT_PLANSZY, true, Color3.new(1, 1, 1), ""
		local st = Instance.new("UIStroke")
		st.Thickness, st.Color = 2.5, INK
		st.Parent = napis
		napis.Parent = bb
		bb.Parent = sg
		t.karta, t.ikona, t.napis, t.skalaPodpisu = bb, ikona, napis, skalaPodpisu
	end

	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") and d ~= cialo then
			table.insert(t.gorne, { p = d, rel = baza0:ToObjectSpace(d.CFrame) })
		end
	end
	pola[i] = t
end

for side = 0, 3 do
	if side == 0 then
		dodajPole(L - C / 2, L - C / 2, "start")
	elseif side == 1 then
		dodajPole(C / 2, L - C / 2, "gold")
	elseif side == 2 then
		dodajPole(C / 2, C / 2, "gold")
	else
		dodajPole(L - C / 2, C / 2, "gold")
	end
	for k = 1, NS do
		local d = k - 0.5
		if side == 0 then
			dodajPole(L - C - d, L - C / 2, "norm")
		elseif side == 1 then
			dodajPole(C / 2, L - C - d, "norm")
		elseif side == 2 then
			dodajPole(C + d, C / 2, "norm")
		else
			dodajPole(L - C / 2, C + d, "norm")
		end
	end
end

local function ustawPole(t: any)
	local ang, zf = 0, 0
	if t.spin >= 0 then
		local s = math.min(1, t.spin)
		ang = s * s * (3 - 2 * s) * math.pi
		zf = math.sin(math.pi * s) * 30 * PZ
	end
	local lift = (t.lift - t.dip * 3) * PZ
	local root = t.baza * CFrame.new(0, zf * U, 0) * CFrame.Angles(0, -ang, 0)
	local hb = math.max(0.02, TH - CT + lift)
	t.cialo.Size = Vector3.new(t.bok, hb * U, t.bok)
	t.cialo.CFrame = root * CFrame.new(0, hb / 2 * U, 0)
	local wierzch = root * CFrame.new(0, lift * U, 0)
	for _, c in ipairs(t.gorne) do
		c.p.CFrame = wierzch * c.rel
	end
	if t.karta then -- podpis leży na polu i obraca się razem z nim; „pop” przy zmianie wartości
		local pk = math.sin(math.pi * math.clamp(t.pop, 0, 1))
		t.skalaPodpisu.Scale = 1 + 0.3 * pk
		t.napis.TextColor3 = if pk > 0.02 then hex("#fff27a") else Color3.new(1, 1, 1)
	end
end

-- wysokość wierzchu pola nad jego podstawą (studia), z uniesieniem
local function wierzchPola(t: any): number
	return (TH + (t.lift - t.dip * 3) * PZ) * U
end

local function stoi(t: any): Vector3 -- gdzie staje pionek (bez uniesienia)
	local d = if t.typ == "gold" then 0.26 else 0
	return G(t.gx + d, t.gy + d, TH).Position
end

local function ustawNagrode(t: any, n: any, plansza: number)
	if t.typ == "norm" then
		local kol = POZIOMY[math.clamp(plansza, 1, #POZIOMY)]
		t.cialo.Color, t.czapka.Color, t.tlo.BackgroundColor3, t.obrys.Color = kol.side, kol.top, kol.top, kol.dark
	end
	if not (t.napis and n) then
		return
	end
	if n.typ == "przedmiot" then
		t.napis.Text = "ITEM"
	else
		t.napis.Text = "+" .. tostring(n.ile)
	end
	if t.ikona then
		t.ikona.Image = IKONY[n.typ] or ""
	end
end

------------------------------------------------------------ pionek: kot-czarodziej na złotej podstawce
local pionekG = grupa("Pionek", true)
local pionekCzesci = {}
local pionekKotwica: Part
do
	local v, kx, ky = px(CFrame.new(), 0.9)
	local POM = hex("#f58a1f")
	pionekKotwica = walec(pionekG, "Podstawka", 23 * kx, 7 * ky, CFrame.new(v(0, 3.5, 0)), hex("#e09a1b"))
	walec(pionekG, "Podstawka wierzch", 22.4 * kx, 0.01, CFrame.new(v(0, 7, 0)), hex("#ffd84d"))
	walec(pionekG, "Podstawka krąg", 17.5 * kx, 0.01, CFrame.new(v(0, 7, 0)) * CFrame.new(0, 0.004, 0), hex("#ffe98a"))
	local function c(x: number, y: number, z: number?): Vector3
		return v(x, 7.5 + y, z)
	end
	kula(pionekG, "Tułów", Vector3.new(31 * kx, 30 * ky, 25 * kx), CFrame.new(c(0, 14, 0)), POM)
	kula(pionekG, "Brzuch", Vector3.new(13 * kx, 17 * ky, 8 * kx), CFrame.new(c(0, 11.5, 9.5)), hex("#ffb04a"))
	for _, s in ipairs({ -1, 1 }) do
		kula(pionekG, "Łapa", Vector3.new(9.2 * kx, 6.8 * ky, 9 * kx), CFrame.new(c(s * 5.8, 2.8, 10)), hex("#ffa23a"))
		kula(pionekG, "Oko", Vector3.new(3.8 * kx, 5.6 * ky, 2.2 * kx), CFrame.new(c(s * 5.5, 35.5, 12.5)), INK)
		kula(pionekG, "Błysk oka", Vector3.new(1.4 * kx, 1.8 * ky, 1 * kx), CFrame.new(c(s * 5.5 - 0.6, 36.9, 13.4)), Color3.new(1, 1, 1))
		kula(pionekG, "Policzek", Vector3.new(4.6 * kx, 2.9 * ky, 1.6 * kx), CFrame.new(c(s * 9.6, 31.5, 9.9)), hex("#ff8f7a"))
		trojkat(pionekG, "Ucho", c(s * 15, 42, 0), c(s * 15.5, 56, 0), c(s * 5, 47, 0), 4 * kx, POM)
		trojkat(pionekG, "Ucho środek", c(s * 13.5, 45, 1.6), c(s * 14, 52, 1.6), c(s * 8.5, 47, 1.6), 2 * kx, hex("#ffb3a6"))
	end
	-- ogon: krzywa z rysunku (9,3) → (25,1) → (22,15), za tułowiem
	local function ogon(t: number): Vector3
		local u = 1 - t
		return c(u * u * 9 + 2 * u * t * 25 + t * t * 22, u * u * 3 + 2 * u * t * 1 + t * t * 15, -6)
	end
	for k = 0, 4 do
		pret(pionekG, "Ogon", ogon(k / 5), ogon((k + 1) / 5), 2.6 * kx, POM)
		kula(pionekG, "Ogon", Vector3.one * (5.2 * kx), CFrame.new(ogon((k + 1) / 5)), POM)
	end
	kula(pionekG, "Głowa", Vector3.new(30 * kx, 25 * ky, 25 * kx), CFrame.new(c(0, 36, 1)), hex("#f79a2d"))
	kula(pionekG, "Nos", Vector3.new(3.2 * kx, 2.2 * ky, 2.2 * kx), CFrame.new(c(0, 31.6, 13.2)), hex("#ff8fa3"))
	-- kapelusz czarodzieja: rondo, złota wstążka, stożek z zagiętym czubkiem
	walec(pionekG, "Rondo", 20 * kx, 2.4 * ky, CFrame.new(c(0, 45.5, 1)), hex("#6f37b8"))
	walec(pionekG, "Wstążka", 12 * kx, 2.6 * ky, CFrame.new(c(0, 47.8, 1)), hex("#ffd84d"))
	for _, s in ipairs({ { 0, 49, 0, 55, 10.5 }, { 0, 55, 0.5, 61, 8 }, { 0.5, 61, 1.6, 66.5, 5.6 }, { 1.6, 66.5, 4.5, 71, 3.6 }, { 4.5, 70.5, 9.5, 72.5, 2.3 } }) do
		pret(pionekG, "Kapelusz", c(s[1], s[2], 1), c(s[3], s[4], 1), s[5] * kx, hex("#8d4fd8"))
	end
	kula(pionekG, "Czubek", Vector3.one * (4.6 * kx), CFrame.new(c(9.8, 72.6, 1)), hex("#8d4fd8"))
	for _, d in ipairs(pionekG:GetDescendants()) do
		if d:IsA("BasePart") then
			local cf = d.CFrame
			table.insert(pionekCzesci, {
				p = d, rel = cf, rozmiar = d.Size,
				pion = Vector3.new(math.abs(cf.XVector.Y), math.abs(cf.YVector.Y), math.abs(cf.ZVector.Y)),
			})
		end
	end
end
local cienPionka = walec(cienie, "Cień pionka", 21 * PX * U * 0.9, 0.004, CFrame.new(), INK)
cienPionka.Transparency = 0.72

-- kierunki marszu po bokach pętli: 0 = −gx, 1 = −gy, 2 = +gx, 3 = +gy
local KIERUNKI = { [0] = -vx, [1] = -vz, [2] = vx, [3] = vz }
local function obrotKierunku(k: number): CFrame
	return CFrame.lookAt(Vector3.zero, -KIERUNKI[k % 4])
end
local pionek = { poz = stoi(pola[1]), obrot = obrotKierunku(3), sx = 1, sy = 1, pole = 1, skok = 0 }

-- Kotwica licznika pól (Paweł 28.11: „znacznik zaraz nad pionkiem”): osobna, niewidoczna część bez obrotu, trzymana
-- nad czubkiem figurki. Wcześniej dymek był zaczepiony do podstawki, a ta jest walcem obróconym o 90° — przesunięcie
-- BillboardGui liczy się w osiach zaczepu, więc „w górę” wychodziło w bok i licznik stał obok pionka.
local kotwicaDymka = Instance.new("Part")
kotwicaDymka.Name = "Kotwica dymka"
kotwicaDymka.Size, kotwicaDymka.Transparency = Vector3.new(0.05, 0.05, 0.05), 1
kotwicaDymka.Anchored, kotwicaDymka.CanCollide, kotwicaDymka.CanQuery, kotwicaDymka.CastShadow = true, false, false, false
kotwicaDymka.Parent = model
local wysPionka = 0 -- od stóp do czubka kapelusza, w osiach świata
for _, c in ipairs(pionekCzesci) do
	local s = c.rozmiar
	wysPionka = math.max(wysPionka, c.rel.Y + (c.pion.X * s.X + c.pion.Y * s.Y + c.pion.Z * s.Z) / 2)
end

local function odswiezPionek()
	local t = pola[pionek.pole]
	local unies = if pionek.skok > 0 then 0 else (t.lift - t.dip * 3) * PZ * U
	local cf = CFrame.new(pionek.poz + UP * unies) * pionek.obrot
	local sx, sy = pionek.sx, pionek.sy
	local skaluj = math.abs(sy - 1) > 0.004
	for _, c in ipairs(pionekCzesci) do
		local r = c.rel
		if skaluj or c.skalowane then
			local wsp = Vector3.new(sx, sx, sx) + c.pion * (sy - sx)
			c.p.Size = c.rozmiar * wsp
			c.skalowane = skaluj
		end
		c.p.CFrame = cf * (r.Rotation + Vector3.new(r.X * sx, r.Y * sy, r.Z * sx))
	end
	kotwicaDymka.CFrame = CFrame.new(pionek.poz + UP * (unies + wysPionka * sy))
	local k = math.max(0.3, 1 - pionek.skok / (140 * PZ * U))
	cienPionka.Size = Vector3.new(0.004, 42 * PX * U * 0.9 * k, 42 * PX * U * 0.9 * k)
	cienPionka.CFrame = CFrame.new(pionek.poz + UP * (unies - pionek.skok + 0.004)) * CFrame.Angles(0, 0, math.pi / 2)
end

------------------------------------------------------------ taca, stolik i kostka
local T -- układ tacy: środek wierzchu, osie jak plansza
local kostka: Part
local cienKostki: Part
local KOSTKA = 62 * PX * U
local kostkaSpoczynek: Vector3
do
	T = CFrame.fromMatrix(miejsce(3.5, NOZKI + RAMA * U, 2.0), vx, UP, vz)
	local g = grupa("Taca", true)
	local pol, gr = 1.95, 20 * PZ
	local function warstwa(nazwa: string, skala: number, wierzch: number, kolor: Color3): Part
		return blok(g, nazwa, Vector3.new(2 * pol * skala * U, 0.02, 2 * pol * skala * U), T * CFrame.new(0, wierzch - 0.01, 0), kolor)
	end
	blok(g, "Taca", Vector3.new(2 * pol, gr - 0.1, 2 * pol) * U, T * CFrame.new(0, -(gr + 0.1) / 2 * U, 0), hex("#a05c2b"))
	blok(g, "Taca złoto", Vector3.new(2 * pol + 0.06, 0.1, 2 * pol + 0.06) * U, T * CFrame.new(0, -0.05 * U, 0), hex("#ffd24a"))
	warstwa("Obrys", 0.895, 1 * EPS, INK)
	warstwa("Drewno", 0.88, 2 * EPS, hex("#b56d30"))
	warstwa("Obrys", 0.775, 3 * EPS, INK)
	warstwa("Sukno", 0.76, 4 * EPS, hex("#6f48b5"))
	local kr = pol * 0.69 * U
	blok(g, "Lamówka", Vector3.new(0.03 * U, 0.02, 2 * kr), T * CFrame.new(-kr, 5 * EPS - 0.01, 0), hex("#8d68d4"))
	blok(g, "Lamówka", Vector3.new(2 * kr, 0.02, 0.03 * U), T * CFrame.new(0, 5 * EPS - 0.01, -kr), hex("#8d68d4"))
	for _, s in ipairs({ { -72, 6, 6 }, { 66, -12, 5 }, { 14, 44, 5 }, { -20, -40, 4 } }) do -- gwiazdki na suknie
		local o = T * SPR * CFrame.new(s[1] * PX * U, 5 * EPS - 0.01, s[2] / 31.1 * U)
		for _, kat in ipairs({ 0, math.pi / 2 }) do
			blok(g, "Gwiazdka", Vector3.new(2 * s[3] * PX * U, 0.02, 0.6 * s[3] * PX * U), o * CFrame.Angles(0, kat, 0), hex("#8d68d4"))
		end
	end

	-- stolik pod tacę: kolory i materiał ze stołu mistrza
	local st = grupa("Stolik kostki")
	local noga = karczma:FindFirstChild("Stół noga")
	local kolorNogi = if noga and noga:IsA("BasePart") then noga.Color else blat.Color
	local spodTacy = T.Position - UP * (gr * U)
	local podloga = baza.Y - 2.95 -- gdy promień nie trafi w posadzkę
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	par.FilterDescendantsInstances = { model, player.Character }
	local traf = workspace:Raycast(spodTacy, -UP * 8, par)
	if traf then
		podloga = traf.Position.Y
	end
	local wys = spodTacy.Y - podloga
	local function stolikCzesc(nazwa: string, r: number, od: number, doo: number, kolor: Color3, wzor: BasePart)
		local p = walec(st, nazwa, r, doo - od, CFrame.new(spodTacy.X, podloga + (od + doo) / 2, spodTacy.Z), kolor)
		p.Material = wzor.Material
	end
	stolikCzesc("Blat", 1.05, wys - 0.22, wys, blat.Color, blat)
	stolikCzesc("Noga", 0.2, 0.14, wys - 0.22, kolorNogi, if noga and noga:IsA("BasePart") then noga else blat)
	stolikCzesc("Stopa", 0.6, 0, 0.14, kolorNogi, if noga and noga:IsA("BasePart") then noga else blat)

	-- kostka: złota z drewnianymi ściankami; układ jak w artefakcie (góra 1, dół 6, +Z 2, −Z 5, +X 3, −X 4)
	local gk = grupa("Kostka", true)
	kostkaSpoczynek = T * Vector3.new(-0.18 * U, 4 * EPS + KOSTKA / 2, -0.18 * U)
	kostka = blok(gk, "Kostka", Vector3.one * KOSTKA, CFrame.new(kostkaSpoczynek), hex("#ffd45a"))
	local OCZKA = {
		[1] = { { 0, 0 } },
		[2] = { { -1, -1 }, { 1, 1 } },
		[3] = { { -1, -1 }, { 0, 0 }, { 1, 1 } },
		[4] = { { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } },
		[5] = { { -1, -1 }, { 1, -1 }, { 0, 0 }, { -1, 1 }, { 1, 1 } },
		[6] = { { -1, -1 }, { -1, 0 }, { -1, 1 }, { 1, -1 }, { 1, 0 }, { 1, 1 } },
	}
	local SCIANY = { [1] = Enum.NormalId.Top, [6] = Enum.NormalId.Bottom, [2] = Enum.NormalId.Back, [5] = Enum.NormalId.Front,
		[3] = Enum.NormalId.Right, [4] = Enum.NormalId.Left }
	for wartosc, sciana in pairs(SCIANY) do
		local sg = Instance.new("SurfaceGui")
		sg.Face = sciana
		sg.CanvasSize = Vector2.new(100, 100)
		sg.LightInfluence = 1
		local drewno = Instance.new("Frame")
		drewno.AnchorPoint, drewno.Position, drewno.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.5, 0.5), UDim2.fromScale(0.74, 0.74)
		drewno.BackgroundColor3, drewno.BorderSizePixel = hex("#eeb068"), 0
		local st2 = Instance.new("UIStroke")
		st2.Thickness, st2.Color = 2, hex("#7a4315")
		st2.Parent = drewno
		drewno.Parent = sg
		for _, o in ipairs(OCZKA[wartosc]) do
			local f = Instance.new("Frame")
			f.AnchorPoint = Vector2.new(0.5, 0.5)
			f.Position, f.Size = UDim2.fromScale(0.5 + o[1] * 0.22, 0.5 + o[2] * 0.22), UDim2.fromScale(0.15, 0.15)
			f.BackgroundColor3, f.BorderSizePixel = hex("#2a1a14"), 0
			local c = Instance.new("UICorner")
			c.CornerRadius = UDim.new(0.5, 0)
			c.Parent = f
			f.Parent = sg
		end
		sg.Parent = kostka
	end
	cienKostki = walec(cienie, "Cień kostki", 31 * 1.3 * PX * U, 0.004, T * CFrame.new(-0.18 * U, 4 * EPS + 0.003, -0.18 * U), INK)
	cienKostki.Transparency = 0.7
end
local KOSTKA0 = B.Rotation * CFrame.Angles(0, math.pi / 2, 0) -- osie kostki z artefaktu: x = −gy, z = +gx
local OBROT_WYNIKU: { [number]: CFrame } = {
	[1] = CFrame.new(), [6] = CFrame.Angles(math.pi, 0, 0), [2] = CFrame.Angles(-math.pi / 2, 0, 0),
	[5] = CFrame.Angles(math.pi / 2, 0, 0), [3] = CFrame.Angles(0, 0, math.pi / 2), [4] = CFrame.Angles(0, 0, -math.pi / 2),
}
kostka.CFrame = CFrame.new(kostkaSpoczynek) * KOSTKA0 * OBROT_WYNIKU[5]

------------------------------------------------------------ światło, iskry, mgiełka, gwiazdki
local GRAFIKA = {
	tytul = "rbxassetid://113072079774411", roll = "rbxassetid://122880810258615", leave = "rbxassetid://73797764327522",
	cena = "rbxassetid://108268009960610", wstega = "rbxassetid://121251992074776", gwiazda = "rbxassetid://138613041337013",
}

local function niewidoczna(nazwa: string, poz: Vector3): Part
	local p = blok(cienie, nazwa, Vector3.one * 0.05, CFrame.new(poz), Color3.new(1, 1, 1))
	p.Transparency = 1
	return p
end

do -- lampa nad stołem: karczma nie ma własnych świateł, a plansza ma być czytelna
	local lampa = niewidoczna("Lampa", miejsce(0.5, 3.2, -1.0))
	local sw = Instance.new("PointLight")
	sw.Range, sw.Brightness, sw.Shadows = 12, 2.6, false
	sw.Color = Color3.fromRGB(255, 244, 224)
	sw.Parent = lampa
end

local zrodloIskier = niewidoczna("Iskry", baza)
local iskryE = Instance.new("ParticleEmitter")
iskryE.Texture = GRAFIKA.gwiazda
iskryE.Color = ColorSequence.new(hex("#ffe14d"), hex("#fff7c2"))
iskryE.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.11), NumberSequenceKeypoint.new(1, 0.02) })
iskryE.Lifetime = NumberRange.new(0.6, 1)
iskryE.Speed = NumberRange.new(50 * PX * U, 160 * PX * U)
iskryE.SpreadAngle = Vector2.new(180, 180)
iskryE.Acceleration = Vector3.new(0, -170 * PZ * U, 0)
iskryE.Rotation, iskryE.RotSpeed = NumberRange.new(0, 360), NumberRange.new(-120, 120)
iskryE.Rate, iskryE.LightEmission, iskryE.LightInfluence = 0, 0.4, 0
iskryE.Parent = zrodloIskier
local zrodloKurzu = niewidoczna("Kurz", baza)
local kurzE = Instance.new("ParticleEmitter")
kurzE.Texture = "rbxasset://textures/particles/smoke_main.dds"
kurzE.Color = ColorSequence.new(hex("#e8d6b0"))
kurzE.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.05), NumberSequenceKeypoint.new(1, 0.11) })
kurzE.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1) })
kurzE.Lifetime = NumberRange.new(0.3, 0.4)
kurzE.Speed = NumberRange.new(30 * PX * U, 70 * PX * U)
kurzE.SpreadAngle = Vector2.new(80, 80)
kurzE.Rate, kurzE.LightInfluence = 0, 1
kurzE.Parent = zrodloKurzu

local function iskry(poz: Vector3, ile: number)
	zrodloIskier.CFrame = CFrame.new(poz)
	iskryE:Emit(ile)
end
local function kurz(poz: Vector3, ile: number)
	zrodloKurzu.CFrame = CFrame.new(poz)
	kurzE:Emit(ile)
end

local function gwiazdka(): (Part, BillboardGui)
	local p = niewidoczna("Gwiazdka", baza)
	local bb = Instance.new("BillboardGui")
	bb.Adornee, bb.LightInfluence, bb.MaxDistance = p, 0, 45
	bb.Size = UDim2.fromScale(0.1, 0.1)
	local im = Instance.new("ImageLabel")
	im.BackgroundTransparency, im.Size, im.Image = 1, UDim2.fromScale(1, 1), GRAFIKA.gwiazda
	im.ImageColor3 = hex("#fffbd0")
	im.Parent = bb
	bb.Parent = p
	return p, bb
end
local gwiazdkiPortalu = {}
for i = 1, 4 do
	local p, bb = gwiazdka()
	gwiazdkiPortalu[i] = { p = p, bb = bb }
end
local blyskSkrzyni = { gwiazdka() }
blyskSkrzyni[1].CFrame = CFrame.new(srodekSkrzyni)
local mgielki = {}
for i = 1, 3 do
	local p = kula(cienie, "Mgiełka", Vector3.new((92 - i * 12) * PX * U, 0.02, 30 * PX * U), S(8, 8, ZT), Color3.new(1, 1, 1))
	p.Transparency = 0.8
	mgielki[i] = p
end

model.Parent = workspace
odswiezPionek()

------------------------------------------------------------ nakładka 2D
-- Grafika z jednej generacji (Higgsfield 25.11, tools/mistrz_gier_ui.py; ID w assets/manifest.json: MistrzTytul,
-- MistrzRoll, MistrzLeave, MistrzCena, MistrzWstega, MistrzGwiazda). Układ jak na makiecie zaakceptowanej przez Pawła:
-- położenie i szerokość w ułamkach ekranu, wysokość z proporcji obrazka.
local KREM, BIALY, ZLOTY, CIEMNY = Color3.fromRGB(252, 227, 176), Color3.new(1, 1, 1), Color3.fromRGB(255, 214, 90), Color3.fromRGB(74, 46, 26)

local gui = Instance.new("ScreenGui")
gui.Name = "MistrzGier3D"
gui.ResetOnSpawn, gui.IgnoreGuiInset, gui.Enabled, gui.DisplayOrder = false, true, false, 26

local function obraz(klasa: string, nazwa: string, obrazek: string, x: number, y: number, szer: number, proporcje: number): any
	local o = Instance.new(klasa) :: any
	o.Name = nazwa
	o.BackgroundTransparency = 1
	o.Image, o.ScaleType = obrazek, Enum.ScaleType.Stretch
	o.Position, o.Size = UDim2.fromScale(x, y), UDim2.fromScale(szer, 1)
	if klasa == "ImageButton" then
		o.AutoButtonColor = false
	end
	local ar = Instance.new("UIAspectRatioConstraint")
	ar.AspectRatio, ar.AspectType, ar.DominantAxis = proporcje, Enum.AspectType.ScaleWithParentSize, Enum.DominantAxis.Width
	ar.Parent = o
	o.Parent = gui
	return o
end

local function napis(rodzic: Instance, tekst: string, x: number, y: number, w: number, h: number, kolor: Color3, maks: number, obrys: number): TextLabel
	local l = Instance.new("TextLabel")
	l.Name = "Label"
	l.BackgroundTransparency = 1
	l.Position, l.Size = UDim2.fromScale(x, y), UDim2.fromScale(w, h)
	l.FontFace, l.TextScaled, l.TextColor3, l.Text = FONT, true, kolor, tekst
	local lim = Instance.new("UITextSizeConstraint")
	lim.MaxTextSize, lim.MinTextSize = maks, 6
	lim.Parent = l
	if obrys > 0 then
		local st = Instance.new("UIStroke")
		st.Thickness, st.Color = obrys, Color3.fromRGB(26, 20, 16)
		st.Parent = l
	end
	l.Parent = rodzic
	return l
end

local function sprezyna(b: GuiButton)
	local sc = Instance.new("UIScale")
	sc.Parent = b
	b.MouseButton1Down:Connect(function()
		TS:Create(sc, TweenInfo.new(0.08), { Scale = 0.94 }):Play()
	end)
	local function pusc()
		TS:Create(sc, TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	end
	b.MouseButton1Up:Connect(pusc)
	b.MouseLeave:Connect(pusc)
end

local tytulRama = obraz("ImageLabel", "Title", GRAFIKA.tytul, 0.018, 0.03, 0.30, 3.2)
local tytul = napis(tytulRama, "GAME MASTER", 0.08, 0.24, 0.84, 0.52, KREM, 40, 3)
local leaveBtn = obraz("ImageButton", "LeaveButton", GRAFIKA.leave, 0.845, 0.125, 0.135, 2.2756) :: ImageButton
napis(leaveBtn, "LEAVE", 0.36, 0.2, 0.56, 0.6, BIALY, 30, 3)
local cenaRama = obraz("ImageLabel", "Price", GRAFIKA.cena, 0.765, 0.545, 0.215, 3.1347)
local cenaIkona = Instance.new("ImageLabel")
cenaIkona.Name = "Icon"
cenaIkona.BackgroundTransparency = 1
cenaIkona.Position, cenaIkona.Size = UDim2.fromScale(0.07, 0.2), UDim2.fromScale(0.19, 0.6)
cenaIkona.ScaleType, cenaIkona.Image = Enum.ScaleType.Fit, IKONY.rybki
cenaIkona.Parent = cenaRama
local cenaL = napis(cenaRama, "FREE ROLL", 0.3, 0.2, 0.64, 0.6, ZLOTY, 30, 3)
local rollBtn = obraz("ImageButton", "RollButton", GRAFIKA.roll, 0.755, 0.675, 0.225, 2.2522) :: ImageButton
local rollNapis = napis(rollBtn, "ROLL", 0.38, 0.14, 0.56, 0.72, BIALY, 64, 4)
local wstega = obraz("ImageLabel", "Message", GRAFIKA.wstega, 0.02, 0.80, 0.33, 5.0443)
wstega.Visible = false
local msg = napis(wstega, "", 0.14, 0.1, 0.72, 0.58, CIEMNY, 24, 0)
msg.TextWrapped = true
sprezyna(rollBtn)
sprezyna(leaveBtn)
gui.Parent = player:WaitForChild("PlayerGui")

-- wstęga widać tylko wtedy, gdy jest co powiedzieć
local function komunikat(t: string)
	msg.Text = t
	wstega.Visible = t ~= ""
end

-- dymek nad pionkiem z artefaktu: ile skoków zostało
local dymek = Instance.new("BillboardGui")
dymek.Name = "Dymek"
dymek.Adornee, dymek.LightInfluence, dymek.Enabled = kotwicaDymka, 0, false
-- Paweł 28.11: licznik pól stoi zaraz nad czubkiem pionka (kotwica bez obrotu, patrz kotwicaDymka) i jest lekko
-- mniejszy (0,36 × 0,42 studa; wcześniej 0,46 × 0,54). SizeOffset stawia dół dymka w punkcie kotwicy.
dymek.Size = UDim2.fromScale(0.36, 0.42)
dymek.SizeOffset, dymek.AlwaysOnTop = Vector2.new(0, 0.5), true
local dymekSkala = Instance.new("UIScale")
dymekSkala.Parent = dymek
local dymekOgon = Instance.new("Frame")
dymekOgon.AnchorPoint, dymekOgon.Position, dymekOgon.Size, dymekOgon.Rotation = Vector2.new(0.5, 0.5), UDim2.fromScale(0.5, 0.72), UDim2.fromScale(0.36, 0.3), 45
dymekOgon.BackgroundColor3, dymekOgon.BorderSizePixel = hex("#ffe14d"), 0
local dymekOgonObrys = Instance.new("UIStroke")
dymekOgonObrys.Thickness, dymekOgonObrys.Color = 2, INK
dymekOgonObrys.Parent = dymekOgon
dymekOgon.Parent = dymek
local dymekKolo = Instance.new("Frame")
dymekKolo.AnchorPoint, dymekKolo.Position, dymekKolo.Size = Vector2.new(0.5, 0), UDim2.fromScale(0.5, 0.02), UDim2.fromScale(0.84, 0.72)
dymekKolo.BackgroundColor3, dymekKolo.BorderSizePixel = hex("#ffe14d"), 0
local dymekRog = Instance.new("UICorner")
dymekRog.CornerRadius = UDim.new(0.5, 0)
dymekRog.Parent = dymekKolo
local dymekObrys = Instance.new("UIStroke")
dymekObrys.Thickness, dymekObrys.Color = 2, INK
dymekObrys.Parent = dymekKolo
local dymekLiczba = Instance.new("TextLabel")
dymekLiczba.BackgroundTransparency = 1
dymekLiczba.Position, dymekLiczba.Size = UDim2.fromScale(0.12, 0.1), UDim2.fromScale(0.76, 0.8)
dymekLiczba.FontFace, dymekLiczba.TextScaled, dymekLiczba.TextColor3 = FONT_PLANSZY, true, INK
dymekLiczba.Parent = dymekKolo
dymekKolo.Parent = dymek
dymek.Parent = gui

local function pokazDymek(n: number?)
	if not n then
		dymek.Enabled = false
		return
	end
	local kolor = if n == 0 then hex("#8ff08a") else hex("#ffe14d")
	dymekKolo.BackgroundColor3, dymekOgon.BackgroundColor3 = kolor, kolor
	dymekLiczba.Text = tostring(n)
	dymek.Enabled = true
	dymekSkala.Scale = 1.45
	TS:Create(dymekSkala, TweenInfo.new(0.22, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

------------------------------------------------------------ stan i rysowanie
local stan: any = nil
local otwarte, toczy = false, false
local miejsceOtwarcia: Vector3? = nil
local podniesione: any = nil

local function indeksPola(pole: number): number
	return (pole - 1) % LICZBA_POL + 1
end

local function rysuj()
	if not stan then
		return
	end
	for i = 2, LICZBA_POL do
		ustawNagrode(pola[i], stan.nagrody[i], stan.plansza)
	end
	if not toczy then
		local idx = indeksPola(math.clamp(stan.pole, 1, stan.pol))
		pionek.pole, pionek.poz, pionek.skok = idx, stoi(pola[idx]), 0
		pionek.obrot = obrotKierunku(if idx == 1 then 3 else (idx - 2) // (NS + 1))
		odswiezPionek()
	end
	tytul.Text = "GAME MASTER  ·  BOARD " .. tostring(stan.plansza)
end

local function rysujCene()
	if not stan then
		return
	end
	if stan.darmowyZa <= 0 then
		cenaL.Text = "FREE ROLL"
	else
		cenaL.Text = string.format("%d  ·  %d:%02d", stan.cena, stan.darmowyZa // 60, stan.darmowyZa % 60)
	end
end

local function odswiez()
	local ok, w = pcall(function()
		return F:InvokeServer("stan")
	end)
	if ok and type(w) == "table" and w.ok then
		stan = w
		rysuj()
		rysujCene()
	end
end

------------------------------------------------------------ animacje
local function czekaj(czas: number, krok: (u: number) -> ())
	local t0 = os.clock()
	while true do
		local u = math.clamp((os.clock() - t0) / czas, 0, 1)
		krok(u)
		if u >= 1 then
			break
		end
		RunService.RenderStepped:Wait()
	end
end

-- rzut jak w artefakcie: lot z prawej, trzy odbicia (80, 30, 9 px), obrót gaśnie do wyniku
local ODBICIA, SZCZYTY = { 0.38, 0.66, 0.84, 0.94 }, { 0, 80, 30, 9 }
local function rzutKostka(wynik: number)
	local a, b, y = 9 + math.random() * 5, 7 + math.random() * 5, 3 + math.random() * 3
	czekaj(1.45, function(u)
		local e = 1 - (1 - u) ^ 3
		local h = 0
		if u < ODBICIA[1] then
			local q = u / ODBICIA[1]
			h = 230 * (1 - q * q)
		else
			for k = 2, 4 do
				if u >= ODBICIA[k - 1] and u < ODBICIA[k] then
					local pp = (u - ODBICIA[k - 1]) / (ODBICIA[k] - ODBICIA[k - 1])
					h = 4 * SZCZYTY[k] * pp * (1 - pp)
				end
			end
		end
		local rem = if u >= 0.94 then 0 else (1 - u / 0.94) ^ 2.2
		local ziemia = kostkaSpoczynek + prawo * (250 * PX * U * 0.75 * (1 - e)) + przod * (50 / 31.1 * U * (1 - e))
		kostka.CFrame = CFrame.new(ziemia + UP * (h * PZ * U)) * KOSTKA0 * CFrame.Angles(0, y * rem, 0) * CFrame.Angles(a * rem, 0, 0)
			* CFrame.Angles(0, 0, b * rem) * OBROT_WYNIKU[wynik]
		local sh = math.max(0.35, 1 - h / 380)
		local sr = 31 * 2.6 * PX * U * sh
		cienKostki.Size = Vector3.new(0.004, sr, sr)
		cienKostki.CFrame = CFrame.new(ziemia - UP * (KOSTKA / 2 - 0.003)) * CFrame.Angles(0, 0, math.pi / 2)
		cienKostki.Transparency = 1 - 0.3 * sh
	end)
end

local SKOK_CZAS, SKOK_WYS = 0.36, 36 * PZ * U
local function skok(z: number, na: number)
	local zostalo = na - z
	for i = z + 1, na do
		local idx = indeksPola(i)
		local t = pola[idx]
		local a, b = pionek.poz, stoi(t)
		local zObrotu, naObrot = pionek.obrot, obrotKierunku((i - 2) // (NS + 1))
		pionek.pole = idx
		czekaj(SKOK_CZAS, function(u)
			pionek.poz = a:Lerp(b, u) + UP * (4 * SKOK_WYS * u * (1 - u))
			pionek.skok = 4 * SKOK_WYS * u * (1 - u)
			pionek.obrot = zObrotu:Lerp(naObrot, math.min(1, u / 0.55))
			pionek.sy = 1 + 0.14 * math.sin(math.pi * u)
			pionek.sx = 1 + (1 - pionek.sy) * 0.6
			odswiezPionek()
		end)
		pionek.poz, pionek.skok = b, 0
		t.dip = 1
		aktywne[t] = true
		kurz(b, 5)
		zostalo -= 1
		pokazDymek(zostalo)
		-- przysiad po lądowaniu
		czekaj(if i == na then 0.2 else 0.07, function(u)
			local q = 1 - u * (if i == na then 1 else 0.38)
			pionek.sy = 1 - 0.3 * q * math.cos((1 - q) * 4.2)
			pionek.sx = 1 + (1 - pionek.sy) * 0.6
			odswiezPionek()
		end)
	end
	pionek.sx, pionek.sy = 1, 1
	odswiezPionek()
end

-- nowa plansza = wszystkie pola kręcą się i awansują (artefakt: „tiles spin and upgrade”)
local function ulepszPola(nowy: any)
	for i = 2, LICZBA_POL do
		local t = pola[i]
		t.czeka = 0.25 + (i - 2) * 0.045
		t.nowa = { n = nowy.nagrody[i], plansza = nowy.plansza }
		aktywne[t] = true
	end
	task.wait(0.25 + (LICZBA_POL - 2) * 0.045 + 0.95)
end

local function pokazNagrode(t: any, tekst: string, typ: string?)
	-- Paweł 28.11: nagroda nie wyskakuje już nad pionkiem (z kamery za pionkiem była za duża i nie mieściła się
	-- w ekranie), tylko jako mniejsza plakietka z boku — pod tabliczką GAME MASTER.
	local _ = t
	local bb = Instance.new("Frame")
	bb.Name = "Reward"
	bb.BackgroundTransparency = 1
	bb.AnchorPoint, bb.Position, bb.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.105, 0.43), UDim2.fromScale(0.125, 1)
	local proporcje = Instance.new("UIAspectRatioConstraint")
	proporcje.AspectRatio, proporcje.AspectType, proporcje.DominantAxis = 1, Enum.AspectType.ScaleWithParentSize, Enum.DominantAxis.Width
	proporcje.Parent = bb
	local skala = Instance.new("UIScale")
	skala.Scale = 0.5
	skala.Parent = bb
	TS:Create(skala, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	local gw = Instance.new("ImageLabel")
	gw.BackgroundTransparency = 1
	gw.Size = UDim2.fromScale(1, 1)
	gw.Image, gw.ScaleType = GRAFIKA.gwiazda, Enum.ScaleType.Fit
	gw.Parent = bb
	local tl = Instance.new("TextLabel")
	tl.BackgroundTransparency = 1
	tl.Position, tl.Size = UDim2.fromScale(0.2, 0.3), UDim2.fromScale(0.6, 0.3)
	tl.FontFace, tl.TextScaled, tl.TextColor3, tl.Text = FONT, true, Color3.new(1, 1, 1), tekst
	local st = Instance.new("UIStroke")
	st.Thickness, st.Color = 3, Color3.fromRGB(26, 20, 16)
	st.Parent = tl
	tl.Parent = bb
	local ik = Instance.new("ImageLabel")
	ik.BackgroundTransparency = 1
	ik.Position, ik.Size = UDim2.fromScale(0.39, 0.58), UDim2.fromScale(0.22, 0.2)
	ik.ScaleType, ik.Image = Enum.ScaleType.Fit, IKONY[typ or "rybki"] or ""
	ik.Parent = bb
	bb.Parent = gui
	local zanik = TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In, 0, false, 1.0)
	TS:Create(bb, TweenInfo.new(1.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Position = UDim2.fromScale(0.105, 0.39) }):Play()
	TS:Create(gw, zanik, { ImageTransparency = 1 }):Play()
	TS:Create(tl, zanik, { TextTransparency = 1 }):Play()
	TS:Create(st, zanik, { Transparency = 1 }):Play()
	TS:Create(ik, zanik, { ImageTransparency = 1 }):Play()
	task.delay(1.6, function()
		bb:Destroy()
	end)
end

-- agent Karola, 27.11 (Karol: „zmień kamerę przy rzucie kości, żeby była bardziej z lotu, z góry, a nie z boku — żeby
-- było widać, co jest rzucane”): widokStolu() Pawła (25.11: cała plansza i mistrz w kadrze) zostaje, gdy gracz nie rzuca;
-- na czas rzutu kamera przechodzi prawie pionowo nad stół — w kadrze cała plansza i taca z kostką, górna ścianka kostki
-- czytelna — i po nagrodzie wraca do widoku Pawła
--
-- Paweł 28.11 (trzecia uwaga) zastępuje to: kamera stoi ZA PIONKIEM i idzie za nim po planszy („żeby gracz miał
-- odczucie, jak się porusza po tej planszy”); przy rzucie kamera się nie zmienia, tylko pojawia się okienko z podglądem
-- kostki na tacy, a gdy wypadnie liczba — znika. Cel Karola (widać, co jest rzucane) zostaje spełniony okienkiem.
local FOV_PIONKA = 62
local KAM_TYL, KAM_GORA, KAM_PRZOD = 4.4 * U, 4.6 * U, 3.2 * U -- za pionkiem, nad planszą, punkt patrzenia przed pionkiem
local kamOko: Vector3? = nil
local kamCel: Vector3? = nil
local function celKamery(): (Vector3, Vector3)
	-- kierunek NASTĘPNEGO kroku z pola, na którym stoi (albo na które skacze) pionek: na narożniku i na START kamera
	-- patrzy już wzdłuż kolejnego boku pętli, a nie tam, skąd pionek przyszedł (test 28.11: przy START patrzyła za stół)
	local d = KIERUNKI[((pionek.pole - 1) // (NS + 1)) % 4]
	local p = pionek.poz - UP * pionek.skok -- bez podskoku: kamera nie skacze razem z pionkiem
	return p - d * KAM_TYL + UP * KAM_GORA, p + d * KAM_PRZOD + UP * (0.4 * U)
end
local function kameraZaPionkiem(dt: number)
	local oko0, cel0 = kamOko, kamCel
	if not oko0 or not cel0 then
		return
	end
	local oko, cel = celKamery()
	local a = 1 - math.exp(-dt * 5)
	local noweOko, nowyCel = oko0:Lerp(oko, a), cel0:Lerp(cel, a)
	kamOko, kamCel = noweOko, nowyCel
	local k = workspace.CurrentCamera
	if k.CameraType ~= Enum.CameraType.Scriptable then
		k.CameraType = Enum.CameraType.Scriptable
	end
	k.CFrame = CFrame.lookAt(noweOko, nowyCel)
	k.FieldOfView += (FOV_PIONKA - k.FieldOfView) * a
end

-- Test 28.11: gdy pionek idzie dalszymi bokami planszy, kamera za nim wypada za ścianą karczmy albo za mistrzem gier
-- i cały kadr zasłania ściana. Dlatego wszystko, co stoi między kamerą a pionkiem i planszą, znika — tylko u tego
-- gracza i tylko na czas gry przy stole (LocalTransparencyModifier; części mapy Karola nie są zmieniane). Jeśli zasłania
-- choć jedna część mistrza gier, znika cała jego figura, żeby nie zostawały pojedyncze klocki w powietrzu.
local zasloniete: { [BasePart]: boolean } = {}
local zaslonaZa = 0
local function odslonKadr(dt: number)
	for p in pairs(zasloniete) do -- co klatkę, bo silnik potrafi wyzerować modyfikator
		p.LocalTransparencyModifier = 1
	end
	zaslonaZa -= dt
	if zaslonaZa > 0 or not kamOko then
		return
	end
	zaslonaZa = 0.15
	local k = workspace.CurrentCamera
	local stopy = pionek.poz - UP * pionek.skok
	local punkty = { stopy + UP * 0.1, stopy + UP * 0.6, kamCel or stopy, miejsce(0, 0.2, 0) }
	local pomin: { Instance } = { model }
	if player.Character then
		table.insert(pomin, player.Character)
	end
	local teraz: { [BasePart]: boolean } = {}
	local mistrz = karczma:FindFirstChild("MistrzGier")
	local calyMistrz = false
	for _, p in ipairs(k:GetPartsObscuringTarget(punkty, pomin)) do
		if p:IsA("BasePart") and p.Transparency < 1 then
			teraz[p] = true
			if mistrz and p:IsDescendantOf(mistrz) then
				calyMistrz = true
			end
		end
	end
	if calyMistrz and mistrz then
		for _, p in ipairs(mistrz:GetDescendants()) do
			if p:IsA("BasePart") and p.Transparency < 1 then
				teraz[p] = true
			end
		end
	end
	for p in pairs(zasloniete) do
		if not teraz[p] then
			p.LocalTransparencyModifier = 0
		end
	end
	for p in pairs(teraz) do
		p.LocalTransparencyModifier = 1
	end
	zasloniete = teraz
end
local function przywrocZasloniete()
	for p in pairs(zasloniete) do
		p.LocalTransparencyModifier = 0
	end
	zasloniete = {}
end

-- okienko kostki: ViewportFrame z kopią tacy i kostki; kopia co klatkę przyjmuje położenie prawdziwej kostki.
-- Ścianki prawdziwej kostki to SurfaceGui (nie rysują się w ViewportFrame), więc kopia ma oczka z części.
local oknoKostki = Instance.new("Frame")
oknoKostki.Name = "DiceWindow"
oknoKostki.Visible = false
oknoKostki.AnchorPoint, oknoKostki.Position, oknoKostki.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.8725, 0.395), UDim2.fromScale(0.17, 1) -- między LEAVE a tabliczką ceny
oknoKostki.BackgroundColor3, oknoKostki.BorderSizePixel = hex("#b56d30"), 0
local oknoSkala = Instance.new("UIScale")
oknoSkala.Parent = oknoKostki
local kostkaOkna = Instance.new("Model")
local cienOkna: Part
do
	local ar = Instance.new("UIAspectRatioConstraint")
	ar.AspectRatio, ar.AspectType, ar.DominantAxis = 1.25, Enum.AspectType.ScaleWithParentSize, Enum.DominantAxis.Width
	ar.Parent = oknoKostki
	local rog = Instance.new("UICorner")
	rog.CornerRadius = UDim.new(0.1, 0)
	rog.Parent = oknoKostki
	local obrys = Instance.new("UIStroke")
	obrys.Thickness, obrys.Color = 3, Color3.fromRGB(26, 20, 16)
	obrys.Parent = oknoKostki
	local vf = Instance.new("ViewportFrame")
	vf.Name = "Dice"
	vf.AnchorPoint, vf.Position, vf.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.5, 0.5), UDim2.fromScale(0.94, 0.9)
	vf.BackgroundColor3, vf.BorderSizePixel = hex("#4a2e1a"), 0
	vf.Ambient, vf.LightColor, vf.LightDirection = Color3.fromRGB(190, 190, 200), Color3.new(1, 1, 1), Vector3.new(-0.5, -1, -0.4)
	local rog2 = Instance.new("UICorner")
	rog2.CornerRadius = UDim.new(0.08, 0)
	rog2.Parent = vf
	local obrys2 = Instance.new("UIStroke")
	obrys2.Thickness, obrys2.Color = 2, Color3.fromRGB(26, 20, 16)
	obrys2.Parent = vf
	local kam = Instance.new("Camera")
	-- Paweł 28.11: kadr ma obejmować dokładnie miejsce rzutu, bez pustych pól. Kamera okienka patrzy wzdłuż boku
	-- tacy (taca stoi rombem, więc w okienku wychodzi prosto, jako kwadrat) i z góry pod kątem ok. 60° — taca
	-- wypełnia okienko, a kostka ma ok. jednej czwartej jego wysokości.
	kam.FieldOfView = 40
	local srodekTacy = T.Position
	kam.CFrame = CFrame.lookAt(srodekTacy + UP * 1.75 + vx * 1.0, srodekTacy + UP * 0.16)
	kam.Parent = vf
	vf.CurrentCamera = kam
	local tacaWzor = model:FindFirstChild("Taca")
	if tacaWzor then
		tacaWzor:Clone().Parent = vf
	end
	local function czesc(nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3, walcowata: boolean?): Part
		local p = Instance.new("Part")
		p.Name, p.Size, p.CFrame, p.Color = nazwa, rozmiar, cf, kolor
		p.Material, p.Anchored, p.CanCollide, p.CastShadow = Enum.Material.SmoothPlastic, true, false, false
		p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
		if walcowata then
			p.Shape = Enum.PartType.Cylinder
		end
		p.Parent = kostkaOkna
		return p
	end
	local rdzen = czesc("Kostka", Vector3.one * KOSTKA, CFrame.new(), kostka.Color)
	kostkaOkna.PrimaryPart = rdzen
	local X, Y, Z = Vector3.xAxis, Vector3.yAxis, Vector3.zAxis
	-- układ jak na prawdziwej kostce: góra 1, dół 6, +Z 2, −Z 5, +X 3, −X 4
	local SCIANKI = { [1] = { Y, X, Z }, [6] = { -Y, X, Z }, [2] = { Z, X, Y }, [5] = { -Z, X, Y }, [3] = { X, Z, Y }, [4] = { -X, Z, Y } }
	local UKLAD = {
		[1] = { { 0, 0 } }, [2] = { { -1, -1 }, { 1, 1 } }, [3] = { { -1, -1 }, { 0, 0 }, { 1, 1 } },
		[4] = { { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } }, [5] = { { -1, -1 }, { 1, -1 }, { 0, 0 }, { -1, 1 }, { 1, 1 } },
		[6] = { { -1, -1 }, { -1, 0 }, { -1, 1 }, { 1, -1 }, { 1, 0 }, { 1, 1 } },
	}
	for wartosc, s in pairs(SCIANKI) do
		local n, a, b = s[1], s[2], s[3]
		local function plytka(nazwa: string, bok: number, wysun: number, kolor: Color3)
			czesc(nazwa, Vector3.new(bok * KOSTKA, bok * KOSTKA, 0.004), CFrame.fromMatrix(n * (KOSTKA / 2 + wysun), a, b, a:Cross(b)), kolor)
		end
		plytka("Obrys ścianki", 0.8, 0.001, hex("#7a4315"))
		plytka("Ścianka", 0.72, 0.003, hex("#eeb068"))
		for _, o in ipairs(UKLAD[wartosc]) do
			local srodek = n * (KOSTKA / 2 + 0.006) + a * (o[1] * 0.22 * KOSTKA) + b * (o[2] * 0.22 * KOSTKA)
			czesc("Oczko", Vector3.new(0.005, 0.16 * KOSTKA, 0.16 * KOSTKA), CFrame.fromMatrix(srodek, n, a, n:Cross(a)), hex("#2a1a14"), true)
		end
	end
	kostkaOkna.Name = "Kostka okna"
	kostkaOkna:PivotTo(kostka.CFrame)
	kostkaOkna.Parent = vf
	cienOkna = cienKostki:Clone()
	cienOkna.Parent = vf
	vf.Parent = oknoKostki
	oknoKostki.Parent = gui
end
local oknoKostkiNr = 0
local function pokazOknoKostki(pokaz: boolean)
	oknoKostkiNr += 1
	local moj = oknoKostkiNr
	if pokaz then
		oknoKostki.Visible = true
		oknoSkala.Scale = 0.6
		TS:Create(oknoSkala, TweenInfo.new(0.22, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	elseif oknoKostki.Visible then
		TS:Create(oknoSkala, TweenInfo.new(0.16, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.6 }):Play()
		task.delay(0.16, function()
			if oknoKostkiNr == moj then
				oknoKostki.Visible = false
			end
		end)
	end
end
local function odswiezOknoKostki()
	if oknoKostki.Visible then
		kostkaOkna:PivotTo(kostka.CFrame)
		cienOkna.Size, cienOkna.CFrame, cienOkna.Transparency = cienKostki.Size, cienKostki.CFrame, cienKostki.Transparency
	end
end

local function rzuc()
	if toczy or not stan or not otwarte then
		return
	end
	toczy = true
	pokazOknoKostki(true) -- Paweł 28.11: okienko z kostką zamiast zmiany kamery
	komunikat("")
	rollBtn.ImageColor3 = Color3.fromRGB(150, 150, 150)
	rollNapis.TextTransparency = 0.4
	if podniesione then
		podniesione.liftT = 0
		aktywne[podniesione] = true
		podniesione = nil
	end
	pokazDymek(nil)
	local ok, w = pcall(function()
		return F:InvokeServer("rzut", stan.darmowyZa > 0)
	end)
	if not ok or type(w) ~= "table" or not w.ok then
		komunikat(if ok and type(w) == "table" and w.tekst then w.tekst else "…")
		pokazOknoKostki(false)
	else
		rzutKostka(w.kostka)
		iskry(kostka.Position, 10)
		pokazDymek(w.na - w.z)
		task.wait(0.5) -- chwila na odczytanie wyniku w okienku
		pokazOknoKostki(false)
		skok(w.z, w.na)
		local t = pola[indeksPola(w.na)]
		t.liftT = 16
		aktywne[t] = true
		podniesione = t
		iskry(stoi(t) + UP * (8 * PZ * U), 14)
		task.wait(0.55)
		pokazDymek(nil)
		if w.nowaPlansza then
			pokazNagrode(t, "STAR! +" .. w.nagroda, "rybki")
			komunikat(string.format("Board %d done! New, better board.", w.planszaRzutu))
			ulepszPola(w)
		elseif w.typ == "przedmiot" then
			pokazNagrode(t, "ITEM!", "przedmiot")
			task.wait(0.35)
		else
			pokazNagrode(t, "+" .. w.nagroda, w.typ)
			task.wait(0.35)
		end
		if not w.wyplacono and w.nagroda > 0 then
			komunikat("Reward not paid — player state (Karol) not running")
		end
		stan = w
		rysuj()
		rysujCene()
	end
	rollBtn.ImageColor3 = Color3.new(1, 1, 1)
	rollNapis.TextTransparency = 0
	toczy = false
end

-- pola w ruchu, połysk złotych narożników, portal, gwiazdki i mgiełka nad stawem
local czas = 0
RunService.RenderStepped:Connect(function(dt)
	dt = math.min(dt, 0.05)
	kameraZaPionkiem(dt)
	odslonKadr(dt)
	odswiezOknoKostki()
	if (workspace.CurrentCamera.CFrame.Position - baza).Magnitude > 60 then
		return
	end
	czas += dt
	local ruszycPionek = false
	for t in pairs(aktywne) do
		t.lift += (t.liftT - t.lift) * math.min(1, dt * 9)
		if t.pop > 0 then
			t.pop = math.max(0, t.pop - dt * 2.8)
		end
		if t.dip > 0 then
			t.dip = math.max(0, t.dip - dt * 7)
		end
		if t.czeka > 0 then
			t.czeka -= dt
			if t.czeka <= 0 then
				t.czeka, t.spin, t.obrocone = 0, 0, false
			end
		end
		if t.spin >= 0 then
			t.spin += dt / 0.9
			if t.spin >= 0.5 and not t.obrocone then
				t.obrocone = true
				if t.nowa then
					ustawNagrode(t, t.nowa.n, t.nowa.plansza)
					t.nowa = nil
				end
				t.pop = 1
				if t.i % 3 == 0 then
					iskry(t.baza.Position + UP * ((TH + 30 * PZ) * U), 6)
				end
			end
			if t.spin >= 1 then
				t.spin = -1
			end
		end
		ustawPole(t)
		if t.i == pionek.pole then
			ruszycPionek = true
		end
		if math.abs(t.liftT - t.lift) < 0.02 and t.pop <= 0 and t.dip <= 0 and t.czeka <= 0 and t.spin < 0 then
			t.lift = t.liftT
			ustawPole(t)
			aktywne[t] = nil
		end
	end
	if ruszycPionek and pionek.skok <= 0 then
		odswiezPionek()
	end
	for _, t in ipairs(pola) do
		if t.typ == "gold" then
			t.ramka.BackgroundTransparency = 1 - (0.2 + 0.14 * math.sin(czas * 3 + t.i))
		end
	end
	swiatloPortalu.Brightness = 1.1 + 0.4 * math.sin(czas * 2.2)
	local kx, ky = PX * U, PZ * U
	for i, g in ipairs(gwiazdkiPortalu) do
		local a = czas * 0.9 + (i - 1) * math.pi / 2
		g.p.CFrame = CFrame.new(srodekPortalu * Vector3.new(math.cos(a) * 36 * kx, (42 - math.sin(a * 1.3) * 28) * ky, 6 * kx))
		local r = math.max(1.5, 3.5 + 2 * math.sin(czas * 3 + (i - 1) * 2)) * 3.2 * kx
		g.bb.Size = UDim2.fromScale(r, r)
	end
	local tw = math.sin(math.pi * ((czas * 0.8) % 1)) * 22 * kx
	blyskSkrzyni[2].Size = UDim2.fromScale(tw, tw)
	for i, p in ipairs(mgielki) do
		local j = i - 1
		p.CFrame = S(8, 8, ZT) * CFrame.new(math.sin(czas * 0.35 + j * 2.1) * 46 * kx, 8 * ky, (-6 + math.cos(czas * 0.28 + j * 1.7) * 12) / 31.1 * U)
	end
end)

------------------------------------------------------------ kamera i tryb gry
local kamera = workspace.CurrentCamera
local poprzedniFov = 70
local hudBylo: boolean? = nil

-- gracz nie chodzi w trybie stołu: moduł sterowania Robloxa, a gdy gra go nie ma — prędkość postaci 0
local predkosc: number? = nil
local function sterowanie(wlacz: boolean)
	local ps = player:FindFirstChild("PlayerScripts")
	local pm = ps and ps:FindFirstChild("PlayerModule")
	if pm and pm:IsA("ModuleScript") then
		pcall(function()
			local c = (require(pm) :: any):GetControls()
			if wlacz then
				c:Enable()
			else
				c:Disable()
			end
		end)
		return
	end
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if not hum then
		return
	end
	if wlacz then
		if predkosc then
			hum.WalkSpeed = predkosc
			predkosc = nil
		end
	elseif not predkosc then
		predkosc = hum.WalkSpeed
		hum.WalkSpeed = 0
	end
end

-- Paweł 25.11 po teście: w kadrze cała plansza ORAZ mistrz gier (z głową), nic ich nie zasłania; postać gracza jest
-- u niego niewidoczna na czas gry przy stole. 26.11: kamera przesunięta w prawo — plansza po lewej jak w artefakcie,
-- taca z kostką po prawej nad plakietką ceny (ustawienie policzone dla 16:9, sprawdzone dla 4:3 i 19,5:9).
local FOV_STOLU = 65
local function widokStolu(): CFrame
	-- Paweł 28.11: kamera na planszę rzutowana z góry przez cały czas (wcześniej: z boku, z mistrzem w kadrze —
	-- ustawienie z 25–26.11: oko miejsce(1.2, 3.4, -5.2), nachylenie 25°). Ten sam kadr co przy rzucie (widokRzutu
	-- agenta Karola): cała plansza i taca z kostką, góra kadru = strona mistrza.
	-- Paweł 28.11 (druga uwaga): nie całkiem z góry, tylko lekko pod kątem od przodu (od strony gracza), tak żeby
	-- w kadrze była cała plansza i taca z kostką, a płaskie podpisy pól dalej były czytelne. Kąt ok. 58° w dół.
	-- Widok rzutu agenta Karola (prawie pionowy, na czas rzutu) zostaje bez zmian.
	-- Pomiar w Play 28.11 (1366 × 670): przy pierwszym ustawieniu plansza z tacą zajmowała tylko ok. 40% szerokości
	-- ekranu, więc kamera podeszła o 12% bliżej (ten sam kąt) i celuje trochę w prawo, żeby kadr był między tytułem
	-- a prawą kolumną przycisków (cena, RZUĆ).
	local srodek = miejsce(1.2, 0, -0.05) -- między środkiem planszy a tacą z kostką; pomiar: całość x 280–976, y ok. 122–641
	return CFrame.lookAt(srodek + UP * 4.9 - przod * 3.1, srodek)
end

-- Od trzeciej uwagi Pawła z 28.11 kamera idzie za pionkiem (kameraZaPionkiem); widokStolu i FOV_STOLU zostają
-- nieużywane na wypadek przełącznika „widok całej planszy”.
local _ = { widokStolu, FOV_STOLU }

local ukrywanie: RBXScriptConnection? = nil
local function przezroczystoscPostaci(wartosc: number)
	local char = player.Character
	if not char then
		return
	end
	for _, d in ipairs(char:GetDescendants()) do
		if d:IsA("BasePart") or d:IsA("Decal") or d:IsA("Texture") then
			d.LocalTransparencyModifier = wartosc
		end
	end
end
local function ukryjPostac(ukryj: boolean)
	if ukrywanie then
		ukrywanie:Disconnect()
		ukrywanie = nil
	end
	if ukryj then
		-- co klatkę: obejmuje też części dołożone w trakcie (np. założony przedmiot)
		ukrywanie = RunService.RenderStepped:Connect(function()
			przezroczystoscPostaci(1)
		end)
	else
		przezroczystoscPostaci(0)
	end
end

local function otworz()
	local wybor = player.PlayerGui:FindFirstChild("ClassSelect")
	if otwarte or (wybor and wybor:IsA("ScreenGui") and wybor.Enabled) then
		return -- ekran wyboru rasy ma własną kamerę
	end
	otwarte = true
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	miejsceOtwarcia = root and root.Position or nil
	komunikat("")
	kamera = workspace.CurrentCamera
	poprzedniFov = kamera.FieldOfView
	kamera.CameraType = Enum.CameraType.Scriptable
	-- kamera dolatuje z miejsca, w którym była, za pionek (wygładzanie w kameraZaPionkiem)
	kamOko, kamCel = kamera.CFrame.Position, kamera.CFrame.Position + kamera.CFrame.LookVector * 4
	sterowanie(false)
	ukryjPostac(true)
	local hud = player.PlayerGui:FindFirstChild("HUD")
	if hud and hud:IsA("ScreenGui") then
		hudBylo = hud.Enabled
		hud.Enabled = false
	end
	PPS.Enabled = false -- podpowiedzi E nie zasłaniają stołu
	gui.Enabled = true
	odswiez()
end

local function zamknij()
	if not otwarte then
		return
	end
	otwarte = false
	kamOko, kamCel = nil, nil
	przywrocZasloniete()
	oknoKostkiNr += 1
	oknoKostki.Visible = false
	gui.Enabled = false
	PPS.Enabled = true
	kamera.CameraType = Enum.CameraType.Custom
	kamera.FieldOfView = poprzedniFov
	sterowanie(true)
	ukryjPostac(false)
	local hud = player.PlayerGui:FindFirstChild("HUD")
	if hud and hud:IsA("ScreenGui") and hudBylo ~= nil then
		hud.Enabled = hudBylo
	end
end

okna:SetAttribute("mistrz_gier", true) -- dymek „w budowie” bazaru wyłączony
okna:SetAttribute("mistrz_gier_3d", true) -- płaskie okno ustępuje
okna.Event:Connect(function(id)
	if id == "mistrz_gier" then
		otworz()
	end
end)
rollBtn.Activated:Connect(rzuc)
leaveBtn.Activated:Connect(zamknij)
UIS.InputBegan:Connect(function(input, processed)
	if not otwarte then
		return
	end
	if input.KeyCode == Enum.KeyCode.Escape then
		zamknij()
	elseif not processed and input.KeyCode == Enum.KeyCode.Space then
		rzuc()
	end
end)
player.CharacterAdded:Connect(zamknij)

-- plansza od razu pokazuje stan gracza (widać ją także bez wejścia w grę); licznik darmowego rzutu
task.spawn(function()
	task.wait(3)
	odswiez()
	while true do
		task.wait(1)
		if otwarte and stan then
			if stan.darmowyZa > 0 then
				stan.darmowyZa -= 1
				rysujCene()
			end
			local char = player.Character
			local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
			if root and miejsceOtwarcia and (root.Position - miejsceOtwarcia).Magnitude > 14 then
				zamknij()
			end
		end
	end
end)
