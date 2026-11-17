--!strict
-- Klasy postaci i scena wyboru klasy (ReplicatedStorage.Shared.ClassData) — wspólne dla serwera i klienta.
-- Klasy: D-054 (Wojownik, Zwiadowca, Mag). Paski statystyk na ekranie wyboru = profil klasy wg Pawła (17.11.2026):
-- Wojownik STR/CON/ARMOR, Zwiadowca DEX + LUCK, Mag INT + LUCK (pasek pełny przy BAR_FULL). To opis klasy na
-- ekranie, nie liczby silnika walki (B&C/Gra/Walka v2 — silnik, klasy i umiejętności.md).
-- Scena 3D: swiat/wybor_klasy/generuj.py (kontener Workspace/WyborKlasy). Projekt: B&C/UI/Selektor bohatera.md.

local ClassData = {}

export type Class = {
	id: string,
	name: string,
	subtitle: string,
	emblem: string, -- nazwa grafiki w Shared.ClassSelectIcons
	model: string, -- nazwa modelu w ReplicatedStorage.WyborKlasyModele
	stats: { number }, -- STR, CON, INT, DEX, LUCK, ARMOR (pasek pełny przy BAR_FULL)
	color: { Color3 }, -- kolor klasy: góra i dół gradientu pasków, nazwa klasy (Paweł 17.11)
}

ClassData.Classes = {
	{ id = "Warrior", name = "WARRIOR", subtitle = "SHIELD & SWORD", emblem = "CsEmblemWarrior", model = "Warrior",
		stats = { 27, 29, 7, 10, 10, 26 }, color = { Color3.fromRGB(120, 196, 255), Color3.fromRGB(38, 110, 230) } },
	{ id = "Scout", name = "SCOUT", subtitle = "BOW & DAGGER", emblem = "CsEmblemScout", model = "Scout",
		stats = { 17, 21, 10, 29, 23, 12 }, color = { Color3.fromRGB(150, 240, 110), Color3.fromRGB(44, 168, 64) } },
	{ id = "Mage", name = "MAGE", subtitle = "STAFF & SPELLS", emblem = "CsEmblemMage", model = "Mage",
		stats = { 8, 13, 29, 12, 22, 6 }, color = { Color3.fromRGB(214, 150, 255), Color3.fromRGB(128, 58, 214) } },
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
