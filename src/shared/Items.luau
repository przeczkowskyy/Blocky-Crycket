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
	-- bronie Maga i Zwiadowcy z puli Lv 1–10 (Karol 27.11, D-167; nazwy z puli — propozycja): kupuje się je
	-- u zbrojmistrza (kowal Karola, katalog swiat/postacie/bronie_klas_sklep.json — tam cena, poziom i statystyki,
	-- LICZBY ROBOCZE), id = id przedmiotu kowala = model w ReplicatedStorage.BronieKlas. Tu tylko ikona do okien
	-- (EkwipunekStan.definicja bierze Shared.Items przed przedmiotami kowala). Ikony: swiat/postacie/ikony_broni.json.
	mag_rozdzka_z_patyka = { name = "Różdżka z Patyka", slot = "Weapon", category = "Weapons", icon = "rbxassetid://84907332708348" },
	mag_kostur_z_miotly = { name = "Kostur z Miotły", slot = "Weapon", category = "Weapons", icon = "rbxassetid://73948961084878" },
	mag_walek_czarodziejski = { name = "Wałek Czarodziejski", slot = "Weapon", category = "Weapons", icon = "rbxassetid://76821207350979" },
	mag_rozdzka_ze_swieczki = { name = "Różdżka ze Świeczki", slot = "Weapon", category = "Weapons", icon = "rbxassetid://120086401556569" },
	mag_kostur_ucznia = { name = "Kostur Ucznia", slot = "Weapon", category = "Weapons", icon = "rbxassetid://81130849751144" },
	zwiad_proca_z_galezi = { name = "Proca z Gałęzi", slot = "Weapon", category = "Weapons", icon = "rbxassetid://88443827869989" },
	zwiad_luk_z_wieszaka = { name = "Łuk z Wieszaka", slot = "Weapon", category = "Weapons", icon = "rbxassetid://95890663840529" },
	zwiad_noz_do_masla = { name = "Nóż do Masła", slot = "Weapon", category = "Weapons", icon = "rbxassetid://78117130092048" },
	zwiad_sztylet_z_szyszki = { name = "Sztylet z Szyszki", slot = "Weapon", category = "Weapons", icon = "rbxassetid://82943053367365" },
	zwiad_luk_tropiciela = { name = "Łuk Tropiciela", slot = "Weapon", category = "Weapons", icon = "rbxassetid://110256058556217" },
}

return Items
