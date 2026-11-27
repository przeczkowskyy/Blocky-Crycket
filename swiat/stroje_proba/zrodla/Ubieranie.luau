--[[
	Ubieranie — składa bohatera z GOŁEGO CIAŁA i założonych PRZEDMIOTÓW (próba D-071, swiat/stroje_proba).
	Wspólne dla walki (Workspace/TestWalki2/Moduly/Aktorzy woła U.dlaAktora przy każdym nowym aktorze, więc tak samo
	próba walki i walki w lesie, które grają odtwarzaczem próby) i dla podglądu w przymierzalni (KlientStrojow).

	Jak przedmiot trafia na postać (PROJEKT.md): szkielet = kopia szablonu walki (HumanoidRootPart, części kości,
	Motor6D, zaczepy, punkty Punkt_*) bez jego brył; potem bryły z DaneStrojow, każda przyspawana (Weld z C0) do
	części SWOJEJ kości w tym samym miejscu co w szablonie walki. Klipy (moduł Klipy, Motor6D.Transform) ruszają
	kośćmi, a bryły idą za nimi — w każdym klipie, także w upadku (kapelusz i broń kota na kościach HatPivot /
	StaffPivot). Powłoka (zakrywa) chowa gołe bryły swojej kości, hełm i kaptur (ukrywa) — włosy.

	Źródło prawdy o stroju: SERWER (SerwerStrojow) — atrybut gracza D.atrybut .. klasa = „id,id,…” (pusty napis =
	goły, brak atrybutu = dawny szablon walki). Klient tylko czyta.

	API:
		U.D, U.L                                dane i logika (DaneStrojow, LogikaStrojow)
		U.atrybut(klasa) → nazwa atrybutu gracza
		U.strojGracza(gracz, klasa) → { id… } | nil
		U.zbuduj(klasa, plan, wzor?) → Model     plan z L.plan; wzor = szablon walki (bez niego własny szkielet z danych,
		                                          bez punktów Punkt_* — tylko podgląd bez próby walki)
		U.dlaAktora(klasa, wzor, stroj?) → Model | nil
			stroj: tabela id (np. podgląd), false = zawsze dawny szablon, nil = strój lokalnego gracza z atrybutu;
			nil wynik = brak klasy w danych albo brak stroju → wołający bierze dawny szablon. Strój odrzucony przez
			logikę = error (Aktorzy łapie go w pcall i też bierze dawny szablon).
	Model dostaje atrybuty Stroj („id,id,…”) i StrojBryly (liczba brył stroju z ciałem).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Players = game:GetService("Players")

local moduly = script.Parent
local D = require(moduly:WaitForChild("DaneStrojow"))
local L = require(moduly:WaitForChild("LogikaStrojow"))

local U = {}
U.D = D
U.L = L

function U.atrybut(klasa)
	return D.atrybut .. klasa
end

function U.strojGracza(gracz, klasa)
	if gracz == nil or type(klasa) ~= "string" or D.klasy[klasa] == nil then
		return nil
	end
	return L.zNapisu(gracz:GetAttribute(U.atrybut(klasa)))
end

local function bezFizyki(p)
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
end

-- bryła z danych (układ środka części kości) przyspawana do części kości
local function nowaCzesc(c, kosc, rodzic)
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
	p.Name = c[2]
	p.Size = Vector3.new(c[9], c[10], c[11])
	local lok = CFrame.new(c[3], c[4], c[5]) * CFrame.fromOrientation(c[6], c[7], c[8])
	p.CFrame = kosc.CFrame * lok
	p.Color = Color3.fromHex(c[12])
	local m = D.materialy[c[13]]
	p.Material = Enum.Material[m[1]]
	p.Reflectance = m[2]
	p.Anchored = false
	bezFizyki(p)
	if c[14] ~= "" then
		local sm = Instance.new("SpecialMesh")
		sm.MeshType = Enum.MeshType[c[14]]
		sm.Parent = p
	end
	-- Weld z jawnym C0 (nie WeldConstraint): położenie względem kości nie zależy od pozy, w której kość jest teraz
	local w = Instance.new("Weld")
	w.Name = "SpawStroju"
	w.Part0 = kosc
	w.Part1 = p
	w.C0 = lok
	w.Parent = p
	p.Parent = rodzic
	return p
end

-- własny szkielet z danych (gdy nie ma szablonu walki): jak swiat/test_walki2/budowa/szablon.luau, bez brył i punktów
local function szkielet(K)
	local model = Instance.new("Model")
	model.Name = K.klucz
	local hrpPos = Vector3.new(K.hrp[1], K.hrp[2], K.hrp[3])
	local hrp = Instance.new("Part")
	hrp.Name = "HumanoidRootPart"
	hrp.Size = Vector3.new(1, 1, 1)
	hrp.Transparency = 1
	hrp.Anchored = true
	hrp.CastShadow = false
	bezFizyki(hrp)
	hrp.CFrame = CFrame.new(hrpPos)
	hrp.PivotOffset = CFrame.new(-hrpPos)
	hrp.Parent = model
	model.PrimaryPart = hrp
	local kosci = {}
	for i, k in K.kosci do
		local p = Instance.new("Part")
		p.Name = k[1]
		p.Size = Vector3.new(k[9], k[10], k[11])
		p.Transparency = 1
		p.CastShadow = false
		bezFizyki(p)
		p.CFrame = CFrame.new(k[6], k[7], k[8])
		p.Parent = model
		kosci[i] = p
	end
	for i, k in K.kosci do
		local rodzic, srodekRodzica = hrp, hrpPos
		if k[2] ~= 0 then
			local kr = K.kosci[k[2]]
			rodzic, srodekRodzica = kosci[k[2]], Vector3.new(kr[6], kr[7], kr[8])
		end
		local staw = Vector3.new(k[3], k[4], k[5])
		local m = Instance.new("Motor6D")
		m.Name = k[12]
		m.C0 = CFrame.new(staw - srodekRodzica)
		m.C1 = CFrame.new(staw - Vector3.new(k[6], k[7], k[8]))
		m.Part0 = rodzic
		m.Part1 = kosci[i]
		m.Parent = kosci[i]
	end
	for _, z in K.zaczepy do
		local a = Instance.new("Attachment")
		a.Name = z[1]
		a.CFrame = CFrame.new(z[3], z[4], z[5]) * CFrame.fromOrientation(z[6], z[7], z[8])
		a.Parent = kosci[z[2]]
	end
	return model
end

function U.zbuduj(klasa, plan, wzor)
	local K = D.klasy[klasa]
	if K == nil then
		error("Ubieranie: nieznana klasa " .. tostring(klasa))
	end
	local model = if wzor then wzor:Clone() else szkielet(K)
	local kosci = {}
	for _, k in K.kosci do
		local p = model:FindFirstChild(k[1])
		if not p or not p:IsA("BasePart") then
			model:Destroy()
			error("Ubieranie: szkielet " .. klasa .. " nie ma kości " .. k[1])
		end
		kosci[k[1]] = p
	end
	-- bryły szablonu precz (grupy akcesoriów i bryły na kościach); szkielet, stawy, zaczepy i punkty zostają
	for _, d in model:GetChildren() do
		if d:IsA("Model") then
			d:Destroy()
		end
	end
	for _, p in kosci do
		for _, c in p:GetChildren() do
			if c:IsA("BasePart") then
				c:Destroy()
			end
		end
	end
	local grupy = {}
	local function grupa(nazwa)
		local g = grupy[nazwa]
		if not g then
			g = Instance.new("Model")
			g.Name = nazwa
			g.Parent = model
			grupy[nazwa] = g
		end
		return g
	end
	local n = 0
	for _, g in K.golas do
		if not plan.zakryte[g.kosc] then
			local kosc = kosci[g.kosc]
			for _, c in g.czesci do
				nowaCzesc(c, kosc, kosc)
				n += 1
			end
		end
	end
	for _, a in K.akcesoria do
		if not (a.znacznik and plan.ukryte[a.znacznik]) then
			local r = grupa(a.id)
			for _, c in a.czesci do
				nowaCzesc(c, kosci[a.kosc], r)
				n += 1
			end
		end
	end
	for _, id in plan.przedmioty do
		for _, s in D.przedmioty[id].segmenty do
			local kosc = kosci[s.kosc]
			local r = if s.grupa then grupa(s.grupa) else kosc
			for _, c in s.czesci do
				nowaCzesc(c, kosc, r)
				n += 1
			end
		end
	end
	-- 27.11.2026 (UI broni): broń puli Lv 1–10 nie ma brył — na postać idzie kopia uchwytu akcesorium z
	-- ReplicatedStorage/BronieKlas: jej zaczep (RightGripAttachment / LeftGripAttachment) na zaczepie dłoni postaci,
	-- u kota (Kot-Mag) na zaczepie z korektą chwytu (ekwipunek.json: kot = zaczep, pos, rot — jak przy przebudowie)
	local bronie = game:GetService("ReplicatedStorage"):FindFirstChild("BronieKlas")
	local nBroni = 0 -- osobno od StrojBryly (bryły z danych = lustro Pythona zloz())
	for _, id in plan.przedmioty do
		local a = D.przedmioty[id].akcesorium
		local wzorBroni = a and bronie and bronie:FindFirstChild(a.nazwa)
		local uchwyt = wzorBroni and wzorBroni:FindFirstChild("Handle")
		local zaczepBroni = uchwyt and uchwyt:FindFirstChild(a.zaczep)
		if not (zaczepBroni and zaczepBroni:IsA("Attachment")) then
			continue
		end
		local naKocie = K.cialo == "kot" and a.kot ~= nil
		local cel = model:FindFirstChild(if naKocie then a.kot.zaczep else a.zaczep, true)
		if not (cel and cel:IsA("Attachment") and cel.Parent and cel.Parent:IsA("BasePart")) then
			continue
		end
		local korekta = CFrame.new()
		if naKocie then
			-- korekta liczona w układzie biblioteki postaci (przód +Z), a akcesorium wgrane z obrotem Y180 (atrybut
			-- ObrotImportu): ta sama korekta w układzie Roblox = sprzężenie obrotem 180° wokół Y — pos (−x, y, −z),
			-- kąty (−rx, ry, −rz); sprawdzone 27.11: Kostur Ucznia stoi jak kostur Kota-Maga (od ziemi nad głowę)
			local p, r = a.kot.pos, a.kot.rot
			korekta = CFrame.new(-p[1], p[2], -p[3])
				* CFrame.fromOrientation(math.rad(-r[1]), math.rad(r[2]), math.rad(-r[3]))
		end
		local h = uchwyt:Clone()
		h.Name = a.nazwa
		h.Anchored = false
		bezFizyki(h)
		local c0 = cel.CFrame * korekta * zaczepBroni.CFrame:Inverse()
		h.CFrame = cel.Parent.CFrame * c0
		local w = Instance.new("Weld")
		w.Name = "SpawStroju"
		w.Part0 = cel.Parent
		w.Part1 = h
		w.C0 = c0
		w.Parent = h
		h.Parent = grupa("Bron_" .. a.nazwa)
		nBroni += 1
	end
	model:SetAttribute("Stroj", L.naNapis(plan.przedmioty))
	model:SetAttribute("StrojBryly", n)
	model:SetAttribute("StrojBronie", nBroni)
	return model
end

function U.dlaAktora(klasa, wzor, stroj)
	if type(klasa) ~= "string" or D.klasy[klasa] == nil or stroj == false then
		return nil
	end
	local ids = stroj
	if ids == nil then
		ids = U.strojGracza(Players.LocalPlayer, klasa)
		if ids == nil then
			return nil
		end
	end
	local ok, plan = L.plan(D, klasa, ids)
	if not ok then
		error("strój " .. klasa .. " odrzucony: " .. tostring(plan))
	end
	return U.zbuduj(klasa, plan, wzor)
end

return U
