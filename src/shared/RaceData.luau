--!strict
-- Rasy postaci (ReplicatedStorage.Shared.RaceData) — wspólne dla serwera i klienta.
-- D-079 (zatwierdzona przez Karola i Pawła 16.11): po wyborze klasy gracz wybiera jedną z sześciu ras.
-- Półbóg (D-080) to rasa premium: widoczna, ale zablokowana do czasu zakupów (serwer jej nie przyjmie).
-- Ekran wyboru rasy jest w tej samej sali co wybór klasy (ClassSelectClient, Paweł 17.11).
-- PLACEHOLDER: pasywne cechy ras (np. demon: więcej Życia i Siły, mniej Inteligencji) nie są jeszcze liczone —
-- czekają na logikę i balans (D-069: żadna para rasa–klasa nie może być obowiązkowa).
-- Ikony: ReplicatedStorage.Shared.RaceIcons (tools/raceselect_assets.py). Projekt: B&C/UI/Selektor bohatera.md.

local RaceData = {}

export type Race = {
	id: string,
	name: string, -- napis na ekranie (po angielsku, jak reszta UI)
	icon: string, -- nazwa grafiki w Shared.RaceIcons
	color: Color3, -- kolor rasy: napis i podświetlenie przycisku
	skin: Color3, -- kolor skóry na modelu-zastępcy, dopóki nie ma modeli ras (D-079)
	trait: string, -- krótki opis cechy pasywnej (PROPOZYCJA, bez liczb)
	premium: boolean?, -- rasa za Robuxy (D-080) — na razie zablokowana, zakupów jeszcze nie ma
}

RaceData.Races = {
	{ id = "Human", name = "HUMAN", icon = "RaceHuman", color = Color3.fromRGB(110, 190, 255),
		skin = Color3.fromRGB(255, 204, 160), trait = "BALANCED IN EVERYTHING" },
	{ id = "Demon", name = "DEMON", icon = "RaceDemon", color = Color3.fromRGB(255, 92, 80),
		skin = Color3.fromRGB(200, 52, 48), trait = "MORE HEALTH & STRENGTH" },
	{ id = "DarkElf", name = "DARK ELF", icon = "RaceDarkElf", color = Color3.fromRGB(196, 140, 255),
		skin = Color3.fromRGB(150, 138, 178), trait = "MORE DEXTERITY & LUCK" },
	{ id = "Elf", name = "ELF", icon = "RaceElf", color = Color3.fromRGB(120, 230, 140),
		skin = Color3.fromRGB(255, 222, 190), trait = "MORE INTELLIGENCE" },
	{ id = "Orc", name = "ORC", icon = "RaceOrc", color = Color3.fromRGB(170, 200, 90),
		skin = Color3.fromRGB(122, 156, 74), trait = "MORE STRENGTH & ARMOR" },
	{ id = "Goblin", name = "GOBLIN", icon = "RaceGoblin", color = Color3.fromRGB(255, 170, 60),
		skin = Color3.fromRGB(176, 206, 70), trait = "MORE LUCK & GOLD" },
	{ id = "Demigod", name = "DEMIGOD", icon = "RaceDemigod", color = Color3.fromRGB(255, 214, 90),
		skin = Color3.fromRGB(240, 196, 110), trait = "PREMIUM RACE — COMING SOON", premium = true },
} :: { Race }

function RaceData.byId(id: string): Race?
	for _, r in ipairs(RaceData.Races) do
		if r.id == id then
			return r
		end
	end
	return nil
end

return RaceData
