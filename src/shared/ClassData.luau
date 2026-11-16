--!strict
-- Klasy postaci i scena wyboru klasy (ReplicatedStorage.Shared.ClassData) — wspólne dla serwera i klienta.
-- Klasy: D-054 (Wojownik, Zwiadowca, Mag). Paski statystyk = wzorcowe rozłożenie punktów z
-- B&C/Gra/Walka v2 — silnik, klasy i umiejętności.md (procent puli; pasek pełny przy 30).
-- Scena 3D: swiat/wybor_klasy/generuj.py (kontener Workspace/WyborKlasy). Projekt: B&C/UI/Selektor bohatera.md.

local ClassData = {}

export type Class = {
	id: string,
	name: string,
	subtitle: string,
	emblem: string, -- nazwa grafiki w Shared.ClassSelectIcons
	model: string, -- nazwa modelu w ReplicatedStorage.WyborKlasyModele
	stats: { number }, -- STR, CON, INT, DEX, LUCK, ARMOR (procent puli)
}

ClassData.Classes = {
	{ id = "Warrior", name = "WARRIOR", subtitle = "SHIELD & SWORD", emblem = "CsEmblemWarrior", model = "Warrior",
		stats = { 26, 30, 12, 8, 10, 14 } },
	{ id = "Scout", name = "SCOUT", subtitle = "BOW & DAGGER", emblem = "CsEmblemScout", model = "Scout",
		stats = { 27, 27, 10, 14, 13, 9 } },
	{ id = "Mage", name = "MAGE", subtitle = "STAFF & SPELLS", emblem = "CsEmblemMage", model = "Mage",
		stats = { 24, 22, 24, 10, 10, 10 } },
} :: { Class }

ClassData.BAR_FULL = 30

function ClassData.byId(id: string): Class?
	for _, c in ipairs(ClassData.Classes) do
		if c.id == id then
			return c
		end
	end
	return nil
end

-- scena (układ świata Studio; musi zgadzać się z swiat/wybor_klasy/generuj.py: PRZESUNIECIE, GORA_PODESTU, ujęcie a_gracz)
ClassData.Scene = {
	center = Vector3.new(0, 400 + 2.15, 4000), -- środek blatu podestu
	ringRadius = 5.3, -- koło postaci
	sideTurn = 0.3, -- boczni bohaterowie obróceni ku środkowi (ułamek kąta na kole)
	camPos = Vector3.new(0, 407.5, 4021),
	camLook = Vector3.new(0, 405.5, 3997),
	fov = 50,
	parallax = 0.55, -- o ile studów kamera odsuwa się za myszką (głębia sali); 0 = wyłączone
	-- nastrój sali: noc rozświetlona ogniem. Ustawiany tylko u gracza i tylko na czas ekranu (po PLAY wraca światło miejsca)
	mood = {
		ambient = Color3.fromRGB(62, 54, 88),
		envDiffuse = 0,
		envSpecular = 0,
		tint = Color3.fromRGB(255, 244, 232),
		contrast = 0.1,
		saturation = 0.12,
		exposure = -0.3, -- korekta ekspozycji na czas ekranu (ujemna = ciemniej); Paweł 16.11: „zmniejszmy naświetlenie”
		bloomIntensity = 0.15,
		bloomSize = 24,
		bloomThreshold = 1.6,
	},
}

return ClassData
