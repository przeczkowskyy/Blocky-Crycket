--!strict
-- Dane drzewka umiejętności (ReplicatedStorage.Shared.SkillTreeData) — wspólne dla serwera i klienta.
-- Projekt: B&C/UI/Okno drzewka umiejętności.md (propozycja), zasady: B&C/Gra/Drzewko umiejętności postaci.md
-- (D-055, D-056, D-057: węzły za Gemy/Diamenty). LICZBY SĄ ROBOCZE — do kalkulatora balansu.
--
-- Mapa: każda zakładka ma węzeł startowy (0, 0) i gałęzie rozchodzące się w kierunku `dir`.
-- Węzły gałęzi zajmują po kolei „sloty” wzoru SLOTS (odległość wzdłuż gałęzi, przesunięcie w bok, rodzic),
-- więc mapa się rozwidla, a dane zostają krótką listą. Jednostka pozycji = 1 odstęp siatki (klient: px).
-- Stan gracza: atrybut "SkillTree" (JSON {id = poziom}); premie: atrybuty "ST_<stat>" (suma w %).

local SkillTreeData = {}

export type Node = {
	id: string,
	tab: string,
	branch: string?,
	parent: string?,
	x: number,
	y: number,
	depth: number,
	icon: string,
	name: string,
	stat: string?,
	per: number,
	max: number,
	label: string?,
	desc: string?,
}

-- slot = { wzdłuż gałęzi, w bok, indeks rodzica (0 = węzeł startowy) }
local SLOTS = {
	{ 1.2, 0, 0 },
	{ 2.2, 0.55, 1 },
	{ 2.2, -0.55, 1 },
	{ 3.2, 1.1, 2 },
	{ 3.2, 0, 3 },
	{ 3.2, -1.1, 3 },
	{ 4.2, 0.55, 4 },
	{ 4.2, -0.55, 6 },
	{ 5.2, 0, 7 },
}

-- węzeł gałęzi: { ikona, NAZWA, statystyka (atrybut ST_<stat>), % za poziom, maks. poziom, [opis] }
local TABS = {
	{
		id = "Player",
		root = { icon = "NodeRootPlayer", name = "WARRIOR" },
		branches = {
			{
				id = "Stats", title = "STATS", dir = { -1, 0 }, side = { 0, -1 },
				nodes = {
					{ "NodeStatStr", "STRENGTH I", "Strength", 2, 5 },
					{ "NodeStatConst", "CONSTITUTION I", "Constitution", 2, 5 },
					{ "NodeStatArmor", "ARMOR I", "Armor", 2, 5 },
					{ "NodeStatStr", "STRENGTH II", "Strength", 3, 5 },
					{ "NodeStatLuck", "LUCK I", "Luck", 2, 5 },
					{ "NodeStatDex", "DEXTERITY I", "Dexterity", 2, 5 },
					{ "NodeStatConst", "CONSTITUTION II", "Constitution", 3, 5 },
					{ "NodeStatInt", "INTELLIGENCE I", "Intelligence", 2, 5 },
					{ "NodeStatAll", "ALL STATS", "AllStats", 1, 5 },
				},
			},
			{
				id = "Income", title = "INCOME", dir = { 1, 0 }, side = { 0, -1 },
				nodes = {
					{ "NodeIncGold", "GOLD I", "Gold", 3, 5 },
					{ "NodeIncExp", "EXP I", "Exp", 3, 5 },
					{ "NodeIncChest", "LOOT", "Loot", 2, 5 },
					{ "NodeIncExp", "EXP II", "Exp", 4, 5 },
					{ "NodeIncPouch", "QUEST GOLD", "QuestGold", 3, 5 },
					{ "NodeIncGems", "GEMS", "Gems", 1, 5 }, -- premia do Diamentów: pytanie otwarte #45
					{ "NodeIncGold", "GOLD II", "Gold", 4, 5 },
					{ "NodeIncOffline", "OFFLINE GOLD", "Offline", 5, 5 },
				},
			},
			{
				id = "Skills", title = "SKILLS", dir = { 0, 1 }, side = { 1, 0 },
				nodes = {
					{ "NodeSkillSlot", "SKILL SLOT I", "SkillSlots", 1, 1, "Unlocks a combat skill slot" },
					{ "NodeSkillPowerSlash", "POWER SLASH", "PowerSlash", 10, 5, "Power Slash damage" },
					{ "NodeSkillShieldBlock", "SHIELD BLOCK", "ShieldBlock", 2, 5, "Shield block chance" },
					{ "NodeSkillCrushingBlow", "CRUSHING BLOW", "CrushingBlow", 10, 5, "Crushing Blow damage" },
					{ "NodeSkillSlot", "SKILL SLOT II", "SkillSlots", 1, 1, "Unlocks a combat skill slot" },
					{ "NodeSkillStoneSkin", "STONE SKIN", "StoneSkin", 10, 5, "Stone Skin shield strength" },
					{ "NodeSkillWarCry", "WAR CRY", "WarCry", 5, 5, "War Cry damage boost" },
					{ "NodeSkillSlot", "SKILL SLOT III", "SkillSlots", 1, 1, "Unlocks a combat skill slot" },
				},
			},
		},
	},
	{
		id = "Fortress",
		root = { icon = "NodeRootFortress", name = "FORTRESS" },
		branches = {
			{
				id = "Training", title = "TRAINING CENTER", dir = { -1, 0 }, side = { 0, -1 },
				nodes = {
					{ "NodeFortTrainDummy", "TRAINING I", "FortTraining", 3, 5, "Stats gained in the Training Center" },
					{ "NodeFortTrainWeights", "HEAVY LIFTING", "FortTrainStr", 4, 5, "Strength gained in training" },
					{ "NodeFortTrainSwords", "SPARRING", "FortTrainDex", 4, 5, "Dexterity gained in training" },
					{ "NodeFortTrainTarget", "FOCUS", "FortTrainLuck", 4, 5, "Luck gained in training" },
					{ "NodeFortTrainAnvil", "FORGED BODY", "FortTrainArmor", 4, 5, "Armor gained in training" },
					{ "NodeFortTrainGain", "TRAINING II", "FortTraining", 5, 5, "Stats gained in the Training Center" },
				},
			},
			{
				id = "Income", title = "INCOME", dir = { 1, 0 }, side = { 0, -1 },
				nodes = {
					{ "NodeFortIncOre", "MINING", "FortOre", 4, 5, "Ore mined" },
					{ "NodeFortIncWood", "LUMBER", "FortWood", 4, 5, "Wood chopped" },
					{ "NodeFortIncStone", "QUARRY", "FortStone", 4, 5, "Stone quarried" },
					{ "NodeFortIncCrystal", "CRYSTALS", "FortCrystal", 3, 5, "Magic crystals found" },
					{ "NodeFortIncCart", "BIG CARTS", "FortAllRes", 2, 5, "All resources" },
					{ "NodeFortIncTimed", "RUSH HOUR", "FortTimed", 5, 5, "Timed bonus rewards" },
				},
			},
			{
				id = "Timer", title = "TIMER", dir = { 0, 1 }, side = { 1, 0 },
				nodes = {
					{ "NodeFortTimeHourglass", "QUICK BUILD", "FortBuildTime", 3, 5, "Shorter building time" },
					{ "NodeFortTimeHammer", "BUILDERS", "FortBuildTime", 3, 5, "Shorter building time" },
					{ "NodeFortTimeStopwatch", "FAST UPGRADES", "FortUpgradeTime", 4, 5, "Shorter upgrade time" },
					{ "NodeFortTimeScaffold", "SCAFFOLDING", "FortBuildTime", 4, 5, "Shorter building time" },
					{ "NodeFortTimeCrane", "CRANE", "FortUpgradeTime", 5, 5, "Shorter upgrade time" },
					{ "NodeFortTimeGears", "CLOCKWORK", "FortAllTime", 3, 5, "All Fortress timers" },
				},
			},
		},
	},
	{
		id = "Pets",
		root = { icon = "NodeRootPets", name = "PETS" },
		branches = {
			{
				id = "PetStats", title = "PET STATS", dir = { 0, -1 }, side = { 1, 0 },
				nodes = {
					{ "NodePetStatAtk", "PET ATTACK", "PetAttack", 3, 5 },
					{ "NodePetStatHp", "PET HEALTH", "PetHealth", 3, 5 },
					{ "NodePetStatDef", "PET DEFENSE", "PetDefense", 3, 5 },
					{ "NodePetStatDex", "PET DEXTERITY", "PetDexterity", 3, 5 }, -- Paweł 15.11: zamiast PET SPEED
					{ "NodePetStatLuck", "PET LUCK", "PetLuck", 3, 5 },
					{ "NodePetStatInt", "PET INTELLIGENCE", "PetIntelligence", 3, 5 }, -- Paweł 15.11: zamiast PET POWER
				},
			},
			{
				id = "Eggs", title = "EGGS", dir = { 1, 0 }, side = { 0, 1 },
				nodes = {
					{ "NodePetEggFast", "FAST HATCH", "EggSpeed", 5, 5, "Faster egg hatching" },
					{ "NodePetEggMulti", "MULTI HATCH", "EggMulti", 1, 2, "+1 egg opened at once" },
					{ "NodePetEggTimer", "QUICK EGGS", "EggSpeed", 5, 5, "Faster egg hatching" },
					{ "NodePetEggCrack", "INSTANT HATCH", "EggInstant", 2, 5, "Chance to hatch instantly" },
					{ "NodePetEggIncubator", "INCUBATOR", "EggSpeed", 6, 5, "Faster egg hatching" },
					{ "NodePetEggBasket", "EGG BASKET", "EggStorage", 1, 3, "+1 egg storage slot" },
				},
			},
			{
				id = "Luck", title = "LUCK", dir = { 0, 1 }, side = { -1, 0 },
				nodes = {
					{ "NodePetLuckClover", "LUCKY EGGS", "EggLuck", 2, 5, "Better egg odds" },
					{ "NodePetLuckGolden", "GOLDEN CHANCE", "EggGolden", 1, 5, "Golden pet chance" },
					{ "NodePetLuckDice", "LUCKY ROLL", "EggLuck", 2, 5, "Better egg odds" },
					{ "NodePetLuckRainbow", "RAINBOW CHANCE", "EggRainbow", 1, 5, "Rainbow pet chance" },
					{ "NodePetLuckStar", "SHOOTING STAR", "EggLuck", 3, 5, "Better egg odds" },
					{ "NodePetLuckCrown", "LEGENDARY", "EggLegendary", 1, 5, "Legendary pet chance" },
				},
			},
			{
				id = "Capacity", title = "CAPACITY", dir = { -1, 0 }, side = { 0, -1 },
				nodes = {
					{ "NodePetCapSlots", "PET SLOT", "PetSlots", 1, 3, "+1 pet equipped at once" },
					{ "NodePetCapBackpack", "PET BAG", "PetStorage", 5, 5, "+5 pet storage" },
					{ "NodePetCapCollar", "LOYALTY", "PetAll", 1, 5 },
					{ "NodePetCapBed", "COZY BED", "PetStorage", 5, 5, "+5 pet storage" },
					{ "NodePetCapCrates", "CRATES", "PetStorage", 10, 3, "+10 pet storage" },
					{ "NodePetCapHouse", "PET HOUSE", "PetSlots", 1, 2, "+1 pet equipped at once" },
				},
			},
		},
	},
}

-- czytelne nazwy statystyk do opisu „+2% Strength”
local LABELS = {
	Strength = "Strength", Constitution = "Constitution", Armor = "Armor", Dexterity = "Dexterity",
	Luck = "Luck", Intelligence = "Intelligence", AllStats = "all stats", Gold = "Gold", Exp = "EXP",
	Loot = "loot drops", QuestGold = "quest Gold", Gems = "Gems", Offline = "offline Gold",
	PetAttack = "pet attack", PetHealth = "pet health", PetDefense = "pet defense", PetSpeed = "pet speed",
	PetLuck = "pet luck", PetAll = "all pet stats", PetDexterity = "pet dexterity", PetIntelligence = "pet intelligence",
}

SkillTreeData.ROOT_COST = 10 -- Diamenty za węzeł startowy zakładki (polecenie Pawła: „niewielka ilość”)
SkillTreeData.Tabs = {} :: { { id: string, title: string } }
SkillTreeData.Branches = {} :: { [string]: { { id: string, title: string, x: number, y: number } } }
SkillTreeData.Nodes = {} :: { [string]: Node }
SkillTreeData.Order = {} :: { [string]: { string } } -- id węzłów w kolejności rysowania, per zakładka

for _, tab in ipairs(TABS) do
	table.insert(SkillTreeData.Tabs, { id = tab.id, title = string.upper(tab.id) })
	local order = {}
	local rootId = tab.id .. "_Root"
	SkillTreeData.Nodes[rootId] = {
		id = rootId, tab = tab.id, branch = nil, parent = nil, x = 0, y = 0, depth = 0,
		icon = tab.root.icon, name = tab.root.name, stat = nil, per = 0, max = 1,
		desc = "Unlocks the " .. string.upper(tab.id) .. " tree",
	}
	table.insert(order, rootId)
	SkillTreeData.Branches[tab.id] = {}
	for _, br in ipairs(tab.branches) do
		local d, s = br.dir, br.side
		-- nazwa gałęzi: nad pierwszym węzłem (gałąź pozioma) albo obok niego (pionowa) — pod węzłem są nazwa i cena
		local horizontal = d[2] == 0
		table.insert(SkillTreeData.Branches[tab.id], {
			id = br.id, title = br.title,
			x = horizontal and d[1] * 1.2 or -0.75, y = horizontal and -0.6 or d[2] * 1.2,
		})
		for i, n in ipairs(br.nodes) do
			local slot = SLOTS[i]
			assert(slot, "za dużo węzłów w gałęzi " .. br.id)
			local id = string.format("%s_%s_%d", tab.id, br.id, i)
			local stat = n[3]
			SkillTreeData.Nodes[id] = {
				id = id, tab = tab.id, branch = br.id,
				parent = slot[3] == 0 and rootId or string.format("%s_%s_%d", tab.id, br.id, slot[3]),
				x = d[1] * slot[1] + s[1] * slot[2], y = d[2] * slot[1] + s[2] * slot[2],
				depth = math.floor(slot[1]),
				icon = n[1], name = n[2], stat = stat, per = n[4], max = n[5],
				label = LABELS[stat], desc = n[6],
			}
			table.insert(order, id)
		end
	end
	SkillTreeData.Order[tab.id] = order
end

-- cena kolejnego poziomu (poziom = obecny + 1) w Diamentach
function SkillTreeData.cost(node: Node, nextLevel: number): number
	if node.depth == 0 then
		return SkillTreeData.ROOT_COST
	end
	return (10 + 5 * node.depth) * nextLevel
end

-- opis efektu: „+2% Strength per level” / opis specjalny
local COUNTS = { SkillSlots = true, PetSlots = true, EggMulti = true, EggStorage = true, PetStorage = true }

function SkillTreeData.describe(node: Node, level: number): string
	if node.depth == 0 or (node.stat and COUNTS[node.stat]) then
		return node.desc or "" -- odblokowanie / liczby sztuk: opis mówi wszystko
	end
	local s = if node.desc
		then string.format("%s: +%d%% per level", node.desc, node.per)
		else string.format("+%d%% %s per level", node.per, node.label or node.stat or "")
	if level > 0 then
		s ..= string.format("  ·  now +%d%%", node.per * level)
	end
	return s
end

-- dostępny = rodzic kupiony (węzeł startowy zawsze dostępny)
function SkillTreeData.isAvailable(node: Node, levels: { [string]: number }): boolean
	return node.parent == nil or (levels[node.parent] or 0) >= 1
end

return SkillTreeData
