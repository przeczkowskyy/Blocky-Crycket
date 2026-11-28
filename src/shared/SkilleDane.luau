-- WYGENEROWANE przez tools/skille_dane.py z danych walki Karola (tools/walka/dane_walki.json) — nie edytuj ręcznie.
-- Podpowiedź umiejętności w oknie ekwipunku: stat węzła drzewka (SkillTreeData) -> opis działania w walce.
return {
	PowerSlash = { walka = "ciecie", rodzaj = "ACTIVE", mana = 100, cel = "enemy", opis = { "Damage: 206% of a hit (physical)" } },
	CrushingBlow = { walka = "miazdzacy_cios", rodzaj = "ACTIVE", mana = 100, cel = "enemy", opis = { "Damage: 141.2% of a hit (physical)", "Armor break for 3 turns", "15% chance: Stun for 1 turns" } },
	StoneSkin = { walka = "kamienna_skora", rodzaj = "ACTIVE", mana = 100, cel = "self", opis = { "Stone Skin shield for 3 turns" } },
	ShieldBlock = { walka = "mur_tarczy", rodzaj = "PASSIVE", mana = 0, cel = "self", opis = { "Block chance +4.2%", "Armor +15.7%" } },
	WarCry = { walka = "furia", rodzaj = "PASSIVE", mana = 0, cel = "self", opis = { "Basic attack damage +10.8%" } },
}
