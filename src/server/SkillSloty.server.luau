--!strict
--[[
	SkillSloty (serwer) — sloty umiejętności w oknie ekwipunku (Paweł 26.11, zakładka SKILLS).

	Ile slotów jest otwartych: węzły SKILL SLOT I–III w drzewku (stat "SkillSlots", atrybut gracza "SkillTree" —
	src/server/SkillTree.server.luau). Jakie umiejętności gracz ma: węzły gałęzi „Skills” drzewka (poza SkillSlots)
	z poziomem > 0. Wybór gracza: atrybut "SkillLoadout" (JSON: [nodeId|"" , …]) — czyta go klient, a docelowo silnik
	walki. Zapis między sesjami: jeszcze nie (stan gracza Karola nie zna tego pola — pytanie w sejfie).

	Zdalne: ReplicatedStorage.SkillSloty (RemoteFunction)
	  "stan"                   → { ok, slotow, wszystkich = 3, umiejetnosci = { { id, nazwa, ikona } }, wybrane = { id|"" ×3 } }
	  "wybierz", slot, nodeId? → jak "stan" (+ tekst przy odmowie); nodeId = nil albo "" czyści slot
]]
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")

local Data = require(RS:WaitForChild("Shared"):WaitForChild("SkillTreeData")) :: any
local WSZYSTKICH = 3
local LIMIT = 0.2

local F = RS:FindFirstChild("SkillSloty") :: RemoteFunction?
if not F then
	local f = Instance.new("RemoteFunction")
	f.Name = "SkillSloty"
	f.Parent = RS
	F = f
end
local ostatnie: { [Player]: number } = {}

local function poziomy(gracz: Player): { [string]: number }
	local ok, t = pcall(HttpService.JSONDecode, HttpService, gracz:GetAttribute("SkillTree") or "{}")
	return if ok and type(t) == "table" then t else {}
end

local function wybrane(gracz: Player): { string }
	local ok, t = pcall(HttpService.JSONDecode, HttpService, gracz:GetAttribute("SkillLoadout") or "[]")
	local w = {}
	for i = 1, WSZYSTKICH do
		w[i] = if ok and type(t) == "table" and type(t[i]) == "string" then t[i] else ""
	end
	return w
end

local function stan(gracz: Player, tekst: string?): any
	local lv = poziomy(gracz)
	local slotow, lista, mam = 0, {}, {}
	for id, n in pairs(lv) do
		local node = Data.Nodes[id]
		if node and type(n) == "number" and n > 0 then
			if node.stat == "SkillSlots" then
				slotow += n * (node.per or 1)
			elseif node.branch == "Skills" then
				table.insert(lista, { id = id, nazwa = node.name, ikona = node.icon, poziom = n })
				mam[id] = true
			end
		end
	end
	table.sort(lista, function(a, b)
		return a.nazwa < b.nazwa
	end)
	slotow = math.clamp(slotow, 0, WSZYSTKICH)
	-- porządek: wybór z zamkniętych slotów albo nieposiadanych umiejętności znika
	local w = wybrane(gracz)
	local zmiana = false
	for i = 1, WSZYSTKICH do
		if w[i] ~= "" and (i > slotow or not mam[w[i]]) then
			w[i] = ""
			zmiana = true
		end
	end
	if zmiana then
		gracz:SetAttribute("SkillLoadout", HttpService:JSONEncode(w))
	end
	return { ok = true, slotow = slotow, wszystkich = WSZYSTKICH, umiejetnosci = lista, wybrane = w, tekst = tekst }
end

local function wybierz(gracz: Player, slot: any, id: any): any
	local s = stan(gracz)
	if type(slot) ~= "number" or slot ~= math.floor(slot) or slot < 1 or slot > WSZYSTKICH then
		return stan(gracz, "Unknown slot")
	end
	if slot > s.slotow then
		return stan(gracz, "Unlock this slot in the skill tree")
	end
	local w = s.wybrane
	if id == nil or id == "" then
		w[slot] = ""
	else
		if type(id) ~= "string" or #id > 64 then
			return stan(gracz, "Unknown skill")
		end
		local mam = false
		for _, u in ipairs(s.umiejetnosci) do
			mam = mam or u.id == id
		end
		if not mam then
			return stan(gracz, "Unlock this skill in the skill tree")
		end
		-- ta sama umiejętność w innym slocie -> zamiana miejscami
		for i = 1, WSZYSTKICH do
			if w[i] == id then
				w[i] = w[slot]
			end
		end
		w[slot] = id
	end
	gracz:SetAttribute("SkillLoadout", HttpService:JSONEncode(w))
	return stan(gracz)
end

(F :: RemoteFunction).OnServerInvoke = function(gracz: Player, polecenie: any, a: any, b: any): any
	local t = os.clock()
	if t - (ostatnie[gracz] or 0) < LIMIT then
		return stan(gracz, "Slow down")
	end
	ostatnie[gracz] = t
	if polecenie == "stan" then
		return stan(gracz)
	elseif polecenie == "wybierz" then
		return wybierz(gracz, a, b)
	end
	return { ok = false, tekst = "Unknown command" }
end

Players.PlayerRemoving:Connect(function(g)
	ostatnie[g] = nil
end)
