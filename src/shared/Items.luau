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
	-- bronie startowe (Paweł 18.11): gracz dostaje broń swojej klasy do slotu broni po wyborze klasy
	-- (ClassData.Classes[].weapon). Ikony: górny rząd arkusza assets/raw/BronieStartowe_arkusz.jpg; modele 3D:
	-- swiat/postacie/bronie_startowe.py (na ekranie wyboru rasy figura trzyma broń klasy). Bez statystyk (propozycja).
	StarterClub = {
		name = "Stone Club",
		slot = "Weapon",
		category = "Weapons",
		icon = "rbxassetid://73877053632813", -- WeaponClub (Wojownik)
	},
	StarterStaff = {
		name = "Curly Staff",
		slot = "Weapon",
		category = "Weapons",
		icon = "rbxassetid://128671874530213", -- WeaponStaff (Mag)
	},
	StarterSlingshot = {
		name = "Slingshot",
		slot = "Weapon",
		category = "Weapons",
		icon = "rbxassetid://90364220695668", -- WeaponSlingshot (Zwiadowca)
	},
}

return Items
