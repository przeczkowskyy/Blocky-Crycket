--[[
	DaneBohatera — WYGENEROWANE przez swiat/bohater_swiat/dane.py (nie edytuj ręcznie), skrót 9d0ead2c5a44.
	Źródła: ustawienia.json, swiat/test_walki2 (aktorzy.py, dane/<klasa>.json — tylko odczyt),
	swiat/stroje_proba/dane.py (atrybut stroju, liczby brył).
	Poza = lista { kość, x, y, z, rx, ry, rz } — Motor6D.Transform stawu tej kości:
	       CFrame.new(x, y, z) * CFrame.fromOrientation(rx, ry, rz) (radiany).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local D = {}
D.wersja = 1
D.kontener = "BohaterSwiat"
D.prefiks = "[BohaterSwiat] "
D.atrybut_wlacznika = "BohaterWSwiecie"
D.atrybut_klasy = "Class"
D.atrybut_stroju = "StrojProba_"
D.klasy_gracza = { Warrior = "wojownik", Scout = "zwiadowca", Mage = "mag" }
D.kontener_walki = "TestWalki2"
D.kontener_strojow = "StrojeProba"
D.folder_lokalny = "BohaterowieLokalni"
D.ruch = {
	prog_ruchu_start = 0.75,
	prog_ruchu_stop = 0.35,
	tempo_min = 0.6,
	tempo_max = 1.8,
	przejscie_klipow_s = 0.18,
	bieg_predkosc = 16,
	prog_wznoszenia = 1,
	prog_ponownego_wznoszenia = 12,
	min_czas_w_powietrzu_s = 0.1,
	min_czas_na_ziemi_s = 0.06,
	czas_ladowania_s = 0.18,
	prog_pionu_zdalny = 8,
	korzen_klatke_pozniej = true,
	pochylenie_od = 6,
	pochylenie_do = 16,
}
D.widocznosc = {
	promien = 260,
	histereza = 1.15,
	maks_bohaterow = 12,
	promien_pelnej_animacji = 90,
	okres_daleko = 3,
	budowy_na_klatke = 1,
	ponow_po_bledzie_s = 5,
	ponow_zaleznosci_s = 2,
	sprawdzaj_awatar_co_s = 0.5,
}
D.awatar = { ukryj_pole_ochronne = true, efekty = { "ParticleEmitter", "Trail", "Beam", "Fire", "Smoke", "Sparkles" } }
D.kontrakt = { sygnal = "RuchBohatera", klipy = { "bieg", "skok", "padnij", "rece_gora", "radosc" }, przesun_maks = 30, wymuszenie_maks_s = 0 }
D.pomiar = { okno_klatek = 600, promien_w_dol = 40 }
D.limity = { maks_czesci_bohatera = 220 }
D.kosciNog = { "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg", "RightFoot" }
D.kolejnoscPoz = { "skok", "spadanie", "ladowanie", "padnij", "rece_gora", "pochyl" }
D.czasyPoz = { skok = 0.1, spadanie = 0.16, ladowanie = 0.07, padnij = 0.12, rece_gora = 0.12, pochyl = 0.2 }
D.kolejnoscKlas = { "wojownik", "zwiadowca", "mag" }
D.skrot = "9d0ead2c5a44"
D.klasy = {}
D.klasy["wojownik"] = {
	klucz = "wojownik",
	nazwa = "Wojownik",
	klasaGry = "Warrior",
	klipy = { spoczynek = "idle", ruch = "chod", radosc = "wiwat", upadek = "upadek" },
	dlugosci = { spoczynek = 2, ruch = 0.8, radosc = 1.2, upadek = 2 },
	predkoscChodu = 3.055,
	podniesienieChodu = 0.064,
	wysokosc = 5.71,
	hrp = { 0, 1.9, 0 },
	czesci = { golas = 74, odniesienie = 127 },
	spod = { golas = 0, odniesienie = 0 },
	bieg = {
		udo = 0.8,
		lydka = 0.75,
		kostka = 0.35,
		biodro = 1.9,
		noga = 1.55,
		krok = 1.24,
		biodraPodpor = 1.4037,
		ugiecie = 0.0542,
		wzlotMaks = 0.2712,
		wzlotRazy = 1.6,
		unoszenie = 0.465,
		skosUnoszenia = 0.5,
		wybieg = 0.124,
		lot = 0.14977,
		lotMin = 0.3,
		vPelna = 16,
		vMin = 1,
		podporMin = 0.06,
		skalaMin = 0.5,
		skalaMaks = 1.15,
		vOd = 6.159,
		vDo = 5.499,
		czas = 0.25,
		stopaWymach = -0.38397,
		skosStopy = 0.8,
		wygladzanie = 0.1,
		vMaks = 64,
		poly = true,
		polaProg = 0.05,
		polaSrodek = 0.05,
		polaUdo = 0.9,
		dzwonUnies = 0.12217,
		dzwonFala = 0.05236,
		dzwonSkret = 0.10472,
		dzwonZwloka = 0.18,
		skretCiala = { przechyl = 0.12217, obrot = 0.08727, pelny = 5, wygladzanie = 0.15 },
		dodatki = {
			{ "LeftUpperArm", 0, 0, 0, -0.12217, 0, 0, 1, 0 },
			{ "RightUpperArm", 0, 0, 0, 0.27925, 0, 0, 1, 0 },
			{ "LeftLowerArm", 0.10472, 0, 0, 0.05236, 0, 0, 1, 0.5 },
			{ "RightLowerArm", 0.13963, 0, 0, 0.10472, 0, 0, 1, 0 },
			{ "UpperTorso", -0.15708, 0, 0, 0, 0.06981, 0.04363, 1, 0 },
			{ "Head", 0.08727, 0, 0, 0, -0.05236, -0.03491, 1, 0 },
		},
	},
	przysiady = { skok = 0, spadanie = 0, ladowanie = 0.2094, padnij = 0.8874, rece_gora = 0, pochyl = 0 },
}
D.klasy["wojownik"].pozy = {}
D.klasy["wojownik"].pozy["skok"] = {
	{ "UpperTorso", 0, 0, 0, -0.10472, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -0.95993 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 0.95993 },
	{ "LeftLowerArm", 0, 0, 0, 0.43633, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 0.43633, 0, 0 },
	{ "LeftUpperLeg", 0, 0, 0, 0.73304, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -1.309, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 0.20944, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -0.66323, 0, 0 },
}
D.klasy["wojownik"].pozy["spadanie"] = {
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -1.8326 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 1.8326 },
	{ "LeftUpperLeg", 0, 0, 0, 0.10472, 0, -0.17453 },
	{ "RightUpperLeg", 0, 0, 0, -0.17453, 0, 0.17453 },
	{ "LeftLowerLeg", 0, 0, 0, -0.31416, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -0.48869, 0, 0 },
}
D.klasy["wojownik"].pozy["ladowanie"] = {
	{ "LowerTorso", 0, -0.2094, 0, 0, 0, 0 },
	{ "UpperTorso", 0, 0, 0, -0.20944, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -0.43633 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 0.43633 },
	{ "LeftUpperLeg", 0, 0, 0, 0.55851, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -1.0472, 0, 0 },
	{ "LeftFoot", 0, 0, 0, 0.48869, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 0.55851, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -1.0472, 0, 0 },
	{ "RightFoot", 0, 0, 0, 0.48869, 0, 0 },
}
D.klasy["wojownik"].pozy["padnij"] = {
	{ "LowerTorso", 0, -0.8874, 0, 0, 0, 0 },
	{ "UpperTorso", 0, 0, 0, -0.66323, 0, 0 },
	{ "Head", 0, 0, 0, 0.38397, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0.95993, 0, 0 },
	{ "LeftLowerArm", 0, 0, 0, 1.0472, 0, 0 },
	{ "RightUpperArm", 0, 0, 0, 0.95993, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 1.0472, 0, 0 },
	{ "LeftUpperLeg", 0, 0, 0, 1.43117, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -2.30383, 0, 0 },
	{ "LeftFoot", 0, 0, 0, 0.87266, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 1.43117, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -2.30383, 0, 0 },
	{ "RightFoot", 0, 0, 0, 0.87266, 0, 0 },
}
D.klasy["wojownik"].pozy["rece_gora"] = {
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -2.87979 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 2.87979 },
	{ "LeftLowerArm", 0, 0, 0, 0, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 0, 0, 0 },
}
D.klasy["wojownik"].pozy["pochyl"] = {
	{ "UpperTorso", 0, 0, 0, -0.15708, 0, 0 },
}
D.klasy["zwiadowca"] = {
	klucz = "zwiadowca",
	nazwa = "Zwiadowca",
	klasaGry = "Scout",
	klipy = { spoczynek = "idle", ruch = "ruch", radosc = "wiwat", upadek = "upadek" },
	dlugosci = { spoczynek = 2, ruch = 0.667, radosc = 1.6, upadek = 2 },
	predkoscChodu = 7.107,
	podniesienieChodu = 0,
	wysokosc = 5.947,
	hrp = { 0, 1.9, 0 },
	czesci = { golas = 109, odniesienie = 182 },
	spod = { golas = 0, odniesienie = 0 },
	bieg = {
		udo = 0.8,
		lydka = 0.75,
		kostka = 0.35,
		biodro = 1.9,
		noga = 1.55,
		krok = 1.085,
		biodraPodpor = 1.4354,
		ugiecie = 0.0387,
		wzlotMaks = 0.1938,
		wzlotRazy = 1.6,
		unoszenie = 0.62,
		skosUnoszenia = 0.5,
		wybieg = 0.1085,
		lot = 0.13219,
		lotMin = 0.3,
		vPelna = 16,
		vMin = 1,
		podporMin = 0.06,
		skalaMin = 0.5,
		skalaMaks = 1.15,
		vOd = 14.329,
		vDo = 12.793,
		czas = 0.25,
		stopaWymach = -0.48869,
		skosStopy = 0.8,
		wygladzanie = 0.1,
		vMaks = 64,
		poly = true,
		polaProg = 0.05,
		polaSrodek = 0.05,
		polaUdo = 0.9,
		dzwonUnies = 0.12217,
		dzwonFala = 0.05236,
		dzwonSkret = 0.10472,
		dzwonZwloka = 0.18,
		skretCiala = { przechyl = 0.12217, obrot = 0.08727, pelny = 5, wygladzanie = 0.15 },
		dodatki = {
			{ "LeftUpperArm", 0, 0, 0, -0.41888, 0, 0, 1, 0 },
			{ "RightUpperArm", 0, 0, 0, 0.59341, 0, 0, 1, 0 },
			{ "LeftLowerArm", 0.34907, 0, 0, 0.24435, 0, 0, 1, 0.5 },
			{ "RightLowerArm", 0.34907, 0, 0, 0.24435, 0, 0, 1, 0 },
			{ "UpperTorso", -0.19199, 0, 0, 0, 0.12217, 0.03491, 1, 0 },
			{ "Head", 0.10472, 0, 0, 0, -0.10472, -0.02618, 1, 0 },
		},
	},
	przysiady = { skok = 0, spadanie = 0, ladowanie = 0.2094, padnij = 0.9274, rece_gora = 0, pochyl = 0 },
}
D.klasy["zwiadowca"].pozy = {}
D.klasy["zwiadowca"].pozy["skok"] = {
	{ "UpperTorso", 0, 0, 0, -0.10472, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -0.95993 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 0.95993 },
	{ "LeftLowerArm", 0, 0, 0, 0.43633, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 0.43633, 0, 0 },
	{ "LeftUpperLeg", 0, 0, 0, 0.73304, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -1.309, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 0.20944, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -0.66323, 0, 0 },
}
D.klasy["zwiadowca"].pozy["spadanie"] = {
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -1.8326 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 1.8326 },
	{ "LeftUpperLeg", 0, 0, 0, 0.10472, 0, -0.17453 },
	{ "RightUpperLeg", 0, 0, 0, -0.17453, 0, 0.17453 },
	{ "LeftLowerLeg", 0, 0, 0, -0.31416, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -0.48869, 0, 0 },
}
D.klasy["zwiadowca"].pozy["ladowanie"] = {
	{ "LowerTorso", 0, -0.2094, 0, 0, 0, 0 },
	{ "UpperTorso", 0, 0, 0, -0.20944, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -0.43633 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 0.43633 },
	{ "LeftUpperLeg", 0, 0, 0, 0.55851, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -1.0472, 0, 0 },
	{ "LeftFoot", 0, 0, 0, 0.48869, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 0.55851, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -1.0472, 0, 0 },
	{ "RightFoot", 0, 0, 0, 0.48869, 0, 0 },
}
D.klasy["zwiadowca"].pozy["padnij"] = {
	{ "LowerTorso", 0, -0.9274, 0, 0, 0, 0 },
	{ "UpperTorso", 0, 0, 0, -0.66323, 0, 0 },
	{ "Head", 0, 0, 0, 0.38397, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0.95993, 0, 0 },
	{ "LeftLowerArm", 0, 0, 0, 1.0472, 0, 0 },
	{ "RightUpperArm", 0, 0, 0, 0.95993, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 1.0472, 0, 0 },
	{ "LeftUpperLeg", 0, 0, 0, 1.43117, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -2.30383, 0, 0 },
	{ "LeftFoot", 0, 0, 0, 0.87266, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 1.43117, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -2.30383, 0, 0 },
	{ "RightFoot", 0, 0, 0, 0.87266, 0, 0 },
}
D.klasy["zwiadowca"].pozy["rece_gora"] = {
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -2.87979 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 2.87979 },
	{ "LeftLowerArm", 0, 0, 0, 0, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 0, 0, 0 },
}
D.klasy["zwiadowca"].pozy["pochyl"] = {
	{ "UpperTorso", 0, 0, 0, -0.15708, 0, 0 },
}
D.klasy["mag"] = {
	klucz = "mag",
	nazwa = "Mag",
	klasaGry = "Mage",
	klipy = { spoczynek = "idle", ruch = "chod", radosc = "wiwat", upadek = "upadek" },
	dlugosci = { spoczynek = 2, ruch = 0.667, radosc = 1, upadek = 2 },
	predkoscChodu = 1.164,
	podniesienieChodu = 0.221,
	wysokosc = 5.164,
	hrp = { 0, 0.75, 0 },
	czesci = { golas = 107, odniesienie = 166 },
	spod = { golas = 0, odniesienie = 0 },
	bieg = {
		udo = 0.3,
		lydka = 0.27,
		kostka = 0.18,
		biodro = 0.75,
		noga = 0.57,
		krok = 0.627,
		biodraPodpor = 0.4692,
		ugiecie = 0.0228,
		wzlotMaks = 0.114,
		wzlotRazy = 1.6,
		unoszenie = 0.228,
		skosUnoszenia = 0.5,
		wybieg = 0.0627,
		lot = 0.10787,
		lotMin = 0.3,
		vPelna = 16,
		vMin = 1,
		podporMin = 0.06,
		skalaMin = 0.5,
		skalaMaks = 1.15,
		vOd = 2.346,
		vDo = 2.095,
		czas = 0.25,
		stopaWymach = -0.17453,
		skosStopy = 0.8,
		wygladzanie = 0.1,
		vMaks = 64,
		poly = true,
		polaProg = 0.05,
		polaSrodek = 0.05,
		polaUdo = 0.9,
		dzwonUnies = 0.12217,
		dzwonFala = 0.05236,
		dzwonSkret = 0.10472,
		dzwonZwloka = 0.18,
		skretCiala = { przechyl = 0.12217, obrot = 0.08727, pelny = 5, wygladzanie = 0.15 },
		dodatki = {
			{ "LeftUpperArm", 0, 0, 0, -0.38397, 0, 0, 1, 0 },
			{ "RightUpperArm", 0, 0, 0, 0.15708, 0, 0, 1, 0 },
			{ "LeftLowerArm", 0.17453, 0, 0, 0.13963, 0, 0, 1, 0.5 },
			{ "RightLowerArm", 0.69813, 0, 0, 0, 0, 0, 1, 0 },
			{ "UpperTorso", -0.10472, 0, 0, 0, 0.10472, 0.05236, 1, 0 },
			{ "Head", 0.05236, 0, 0, 0, -0.06981, -0.03491, 1, 0 },
			{ "StaffPivot", -0.69813, 0, 0, -0.15708, 0, 0, 1, 0 },
			{ "Tail", -0.43633, 0, 0, 0, 0.24435, 0, 1, 0.1 },
			{ "TailTip", 0.24435, 0, 0, 0, 0, 0.17453, 1, 0.3 },
			{ "TailTip", 0, 0, 0, 0.08727, 0, 0, 2, 0.2 },
			{ "HatPivot", 0.08727, 0, 0, 0.06981, 0, 0, 2, 0.15 },
			{ "LeftEar", 0.10472, 0, 0, 0.08727, 0, 0, 2, 0.1 },
			{ "RightEar", 0.10472, 0, 0, 0.08727, 0, 0, 2, 0.1 },
		},
	},
	przysiady = { skok = 0, spadanie = 0, ladowanie = 0.0772, padnij = 0.3547, rece_gora = 0, pochyl = 0 },
}
D.klasy["mag"].pozy = {}
D.klasy["mag"].pozy["skok"] = {
	{ "UpperTorso", 0, 0, 0, -0.10472, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -0.95993 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 0.95993 },
	{ "LeftLowerArm", 0, 0, 0, 0.43633, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 0.43633, 0, 0 },
	{ "LeftUpperLeg", 0, 0, 0, 0.73304, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -1.309, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 0.20944, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -0.66323, 0, 0 },
}
D.klasy["mag"].pozy["spadanie"] = {
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -1.8326 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 1.8326 },
	{ "LeftUpperLeg", 0, 0, 0, 0.10472, 0, -0.17453 },
	{ "RightUpperLeg", 0, 0, 0, -0.17453, 0, 0.17453 },
	{ "LeftLowerLeg", 0, 0, 0, -0.31416, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -0.48869, 0, 0 },
}
D.klasy["mag"].pozy["ladowanie"] = {
	{ "LowerTorso", 0, -0.0772, 0, 0, 0, 0 },
	{ "UpperTorso", 0, 0, 0, -0.20944, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -0.43633 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 0.43633 },
	{ "LeftUpperLeg", 0, 0, 0, 0.55851, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -1.0472, 0, 0 },
	{ "LeftFoot", 0, 0, 0, 0.48869, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 0.55851, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -1.0472, 0, 0 },
	{ "RightFoot", 0, 0, 0, 0.48869, 0, 0 },
}
D.klasy["mag"].pozy["padnij"] = {
	{ "LowerTorso", 0, -0.3547, 0, 0, 0, 0 },
	{ "UpperTorso", 0, 0, 0, -0.66323, 0, 0 },
	{ "Head", 0, 0, 0, 0.38397, 0, 0 },
	{ "LeftUpperArm", 0, 0, 0, 0.95993, 0, 0 },
	{ "LeftLowerArm", 0, 0, 0, 1.0472, 0, 0 },
	{ "RightUpperArm", 0, 0, 0, 0.95993, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 1.0472, 0, 0 },
	{ "LeftUpperLeg", 0, 0, 0, 1.43117, 0, 0 },
	{ "LeftLowerLeg", 0, 0, 0, -2.30383, 0, 0 },
	{ "LeftFoot", 0, 0, 0, 0.87266, 0, 0 },
	{ "RightUpperLeg", 0, 0, 0, 1.43117, 0, 0 },
	{ "RightLowerLeg", 0, 0, 0, -2.30383, 0, 0 },
	{ "RightFoot", 0, 0, 0, 0.87266, 0, 0 },
}
D.klasy["mag"].pozy["rece_gora"] = {
	{ "LeftUpperArm", 0, 0, 0, 0, 0, -2.87979 },
	{ "RightUpperArm", 0, 0, 0, 0, 0, 2.87979 },
	{ "LeftLowerArm", 0, 0, 0, 0, 0, 0 },
	{ "RightLowerArm", 0, 0, 0, 0, 0, 0 },
}
D.klasy["mag"].pozy["pochyl"] = {
	{ "UpperTorso", 0, 0, 0, -0.15708, 0, 0 },
}
return D
