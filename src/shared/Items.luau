-- Definicje przedmiotów (ReplicatedStorage.Shared.Items). TYMCZASOWE: tylko przedmiot testowy do sprawdzenia
-- przeciągania w oknie ekwipunku. Docelowy system przedmiotów: B&C/Gra/System RPG.md (do ustalenia).
--
-- slot: do którego slotu ekwipunku pasuje przedmiot (nazwa bez „Slot_”: Helmet, Chest, Gloves, Boots,
--       Amulet, Belt, Ring, Trinket, Weapon) albo "Any" (każdy slot – do testów).
-- category: zakładka plecaka, na której leży przedmiot: Weapons, Armor, Amulets, Others
--           (widoczny w plecaku tylko przy tej zakładce).

local Items = {
	Scrap = {
		name = "Scrap",
		slot = "Trinket",
		category = "Amulets",
		icon = "rbxassetid://119371548847065", -- ItemScrap (assets/processed/ItemScrap.png), podmieniane po uploadzie
	},
}

return Items
