--!nonstrict
-- Zaczepy akcesoriów z swiat/postacie/przedmioty.json (wygenerowane przez swiat/postacie/zestawienie.py — nie edytuj).
-- Status: propozycja; NIE sprawdzone w Studio. Uruchamia człowiek, po imporcie modeli (upload robi właściciel).
--
-- Jak użyć (Studio, pasek Command Bar albo Script w ServerScriptService na czas pracy):
--   1. Zaimportuj część (np. przedmioty/zr_helm.glb albo .fbx) przez Import 3D.
--   2. Włóż MeshPart do obiektu Accessory i nazwij go "Handle"; nazwij Accessory tak jak id części (np. zr_helm).
--   3. Zaznacz Accessory (albo folder z wieloma) i uruchom ten skrypt. ZRODLO = "glb" albo "fbx" (skąd import).
--   4. Skrypt dodaje do Handle Attachment o nazwie zaczepu (np. HatAttachment) z pozycją i obrotem z tabeli.
-- Gdy model po imporcie FBX jest obrócony tyłem, użyj ZRODLO = "glb" albo popraw obrót ręcznie.
local ZRODLO = "glb"

-- id = {zaczep, glb = {x, y, z, rx, ry, rz}, fbx = {x, y, z, rx, ry, rz}}
local DANE = {
	rekrut_czapka = {zaczep = "HatAttachment", glb = {-0, 0.223, -0.032, 0, 0, 0}, fbx = {0, 0.223, 0.032, 0, 180, 0}},
	rekrut_przeszywanica = {zaczep = "BodyFrontAttachment", glb = {-0, 0.14, 0.462, 0, 0, 0}, fbx = {0, 0.14, -0.462, 0, 180, 0}},
	rekrut_rekaw_l = {zaczep = "LeftShoulderAttachment", glb = {-0.065, 0.42, -0, 0, 0, 0}, fbx = {0.065, 0.42, 0, 0, 180, 0}},
	rekrut_rekaw_p = {zaczep = "RightShoulderAttachment", glb = {0.065, 0.42, -0, 0, 0, 0}, fbx = {-0.065, 0.42, 0, 0, 180, 0}},
	rekrut_rekawica_l = {zaczep = "LeftGripAttachment", glb = {-0.12, -0.069, 0.238, 0, 0, 0}, fbx = {0.12, -0.069, -0.238, 0, 180, 0}},
	rekrut_rekawica_p = {zaczep = "RightGripAttachment", glb = {0.12, -0.069, 0.238, 0, 0, 0}, fbx = {-0.12, -0.069, -0.238, 0, 180, 0}},
	rekrut_but_l = {zaczep = "LeftFootAttachment", glb = {-0.057, -0.573, -0.235, 0, 0, 0}, fbx = {0.057, -0.573, 0.235, 0, 180, 0}},
	rekrut_but_p = {zaczep = "RightFootAttachment", glb = {0.057, -0.573, -0.235, 0, 0, 0}, fbx = {-0.057, -0.573, 0.235, 0, 180, 0}},
	rekrut_pas = {zaczep = "WaistCenterAttachment", glb = {-0, 0.26, -0.243, 0, 0, 0}, fbx = {0, 0.26, 0.243, 0, 180, 0}},
	rekrut_miecz = {zaczep = "RightGripAttachment", glb = {-0, -1.22, -0, 0, 0, 0}, fbx = {0, -1.22, 0, 0, 180, 0}},
	rekrut_amulet = {zaczep = "NeckAttachment", glb = {-0, 0.21, -0, 0, 0, 0}, fbx = {0, 0.21, 0, 0, 180, 0}},
	rekrut_pierscien = {zaczep = "RightGripAttachment", glb = {-0, -0.071, -0, 0, 0, 0}, fbx = {0, -0.071, 0, 0, 180, 0}},
	rekrut_podkowa = {zaczep = "WaistCenterAttachment", glb = {-0, -0.016, -0.007, 0, 0, 0}, fbx = {0, -0.016, 0.007, 0, 180, 0}},
	zr_helm = {zaczep = "HatAttachment", glb = {-0, -0.18, 0.19, 0, 0, 0}, fbx = {0, -0.18, -0.19, 0, 180, 0}},
	zr_napiersnik = {zaczep = "NeckAttachment", glb = {-0, 1.035, -0, 0, 0, 0}, fbx = {0, 1.035, 0, 0, 180, 0}},
	zr_naramiennik_l = {zaczep = "LeftShoulderAttachment", glb = {-0.059, 0.08, -0, 0, 0, 0}, fbx = {0.059, 0.08, 0, 0, 180, 0}},
	zr_naramiennik_p = {zaczep = "RightShoulderAttachment", glb = {0.059, 0.08, -0, 0, 0, 0}, fbx = {-0.059, 0.08, 0, 0, 180, 0}},
	zr_pola = {zaczep = "WaistFrontAttachment", glb = {-0, 0.646, -0.251, 0, 0, 0}, fbx = {0, 0.646, 0.251, 0, 180, 0}},
	zr_rekawica_l = {zaczep = "LeftGripAttachment", glb = {-0.14, -0.02, 0.216, 0, 0, 0}, fbx = {0.14, -0.02, -0.216, 0, 180, 0}},
	zr_rekawica_p = {zaczep = "RightGripAttachment", glb = {0.14, -0.02, 0.216, 0, 0, 0}, fbx = {-0.14, -0.02, -0.216, 0, 180, 0}},
	zr_but_l = {zaczep = "LeftFootAttachment", glb = {-0.12, -0.552, 0.13, 0, 0, 0}, fbx = {0.12, -0.552, -0.13, 0, 180, 0}},
	zr_but_p = {zaczep = "RightFootAttachment", glb = {0.12, -0.552, 0.13, 0, 0, 0}, fbx = {-0.12, -0.552, -0.13, 0, 180, 0}},
	zr_pas = {zaczep = "WaistCenterAttachment", glb = {-0, -0, -0.052, 0, 0, 0}, fbx = {0, -0, 0.052, 0, 180, 0}},
	zr_miecz = {zaczep = "RightGripAttachment", glb = {-0, -1.68, -0, 0, 0, 0}, fbx = {0, -1.68, 0, 0, 180, 0}},
	zr_tarcza = {zaczep = "LeftGripAttachment", glb = {-0.741, -0, 0.32, 0, 0, 0}, fbx = {0.741, -0, -0.32, 0, 180, 0}},
	zr_amulet = {zaczep = "NeckAttachment", glb = {-0, 0.634, -0.05, 0, 0, 0}, fbx = {0, 0.634, 0.05, 0, 180, 0}},
	zr_sygnet = {zaczep = "LeftGripAttachment", glb = {-0, -0.077, -0.025, 0, 0, 0}, fbx = {0, -0.077, 0.025, 0, 180, 0}},
	zr_ostroga = {zaczep = "WaistCenterAttachment", glb = {1.067, 0.42, -0, 0, 0, 0}, fbx = {-1.067, 0.42, 0, 0, 180, 0}},
	mag_kapelusz = {zaczep = "HatAttachment", glb = {-0, -0.672, -0, 0, 0, 0}, fbx = {0, -0.672, 0, 0, 180, 0}},
	mag_szata = {zaczep = "BodyFrontAttachment", glb = {-0, -0.261, 0.623, 0, 0, 0}, fbx = {0, -0.261, -0.623, 0, 180, 0}},
	mag_szata_dol = {zaczep = "WaistCenterAttachment", glb = {-0, 0.115, -0, 0, 0, 0}, fbx = {0, 0.115, 0, 0, 180, 0}},
	mag_rekaw_l = {zaczep = "LeftShoulderAttachment", glb = {-0.269, 0.693, -0, 0, 0, 0}, fbx = {0.269, 0.693, 0, 0, 180, 0}},
	mag_rekaw_p = {zaczep = "RightShoulderAttachment", glb = {0.269, 0.693, -0, 0, 0, 0}, fbx = {-0.269, 0.693, 0, 0, 180, 0}},
	mag_rekawica_l = {zaczep = "LeftGripAttachment", glb = {-0.15, -0.01, 0.17, 0, 0, 0}, fbx = {0.15, -0.01, -0.17, 0, 180, 0}},
	mag_rekawica_p = {zaczep = "RightGripAttachment", glb = {0.15, -0.01, 0.17, 0, 0, 0}, fbx = {-0.15, -0.01, -0.17, 0, 180, 0}},
	mag_cizma_l = {zaczep = "LeftFootAttachment", glb = {-0.1, -0.575, -0.322, 0, 0, 0}, fbx = {0.1, -0.575, 0.322, 0, 180, 0}},
	mag_cizma_p = {zaczep = "RightFootAttachment", glb = {0.1, -0.575, -0.322, 0, 0, 0}, fbx = {-0.1, -0.575, 0.322, 0, 180, 0}},
	mag_pas = {zaczep = "WaistCenterAttachment", glb = {-0, 0.125, -0.165, 0, 0, 0}, fbx = {0, 0.125, 0.165, 0, 180, 0}},
	mag_kostur = {zaczep = "RightGripAttachment", glb = {-0, -1.055, -0, 0, 0, 0}, fbx = {0, -1.055, 0, 0, 180, 0}},
	mag_ksiega = {zaczep = "LeftGripAttachment", glb = {-0.07, -0.81, -0.13, 0, 0, 0}, fbx = {0.07, -0.81, 0.13, 0, 180, 0}},
	mag_amulet = {zaczep = "NeckAttachment", glb = {-0, 0.49, -0.219, 0, 0, 0}, fbx = {0, 0.49, 0.219, 0, 180, 0}},
	mag_pierscien = {zaczep = "RightGripAttachment", glb = {-0, -0.62, 0.069, 0, 0, 0}, fbx = {0, -0.62, -0.069, 0, 180, 0}},
	mag_klepsydra = {zaczep = "WaistCenterAttachment", glb = {-0.3, 0.406, -0.7, 0, 0, 0}, fbx = {0.3, 0.406, 0.7, 0, 180, 0}},
	palka_gwozdz = {zaczep = "RightGripAttachment", glb = {0.241, -0.984, -0.121, 0, 0, 0}, fbx = {-0.241, -0.984, 0.121, 0, 180, 0}},
	patelnia = {zaczep = "RightGripAttachment", glb = {0.02, -1.065, -0.095, 0, 0, 0}, fbx = {-0.02, -1.065, 0.095, 0, 180, 0}},
	mlot_bojowy = {zaczep = "RightGripAttachment", glb = {-0.156, -1.165, -0, 0, 0, 0}, fbx = {0.156, -1.165, 0, 0, 180, 0}},
	topor_dwureczny = {zaczep = "RightGripAttachment", glb = {0.209, -1.167, -0, 0, 0, 0}, fbx = {-0.209, -1.167, 0, 0, 180, 0}},
	wlocznia_choragiew = {zaczep = "RightGripAttachment", glb = {0.79, -1.905, -0, 0, 0, 0}, fbx = {-0.79, -1.905, 0, 0, 180, 0}},
	miecz_plomienisty = {zaczep = "RightGripAttachment", glb = {-0, -1.62, -0, 0, 0, 0}, fbx = {0, -1.62, 0, 0, 180, 0}},
	kostur_lodu = {zaczep = "RightGripAttachment", glb = {0.006, -1.7, -0.021, 0, 0, 0}, fbx = {-0.006, -1.7, 0.021, 0, 180, 0}},
	chochla_mistrza = {zaczep = "RightGripAttachment", glb = {-0, -1.509, -0.044, 0, 0, 0}, fbx = {0, -1.509, 0.044, 0, 180, 0}},
	rycerz_helm_glowa = {zaczep = "EkwHeadAttachment", glb = {-0, -0.18, -0, 0, 0, 0}, fbx = {0, -0.18, 0, 0, 180, 0}},
	rycerz_zbroja_tulow = {zaczep = "EkwUpperTorsoAttachment", glb = {-0, -0.04, -0.022, 0, 0, 0}, fbx = {0, -0.04, 0.022, 0, 180, 0}},
	rycerz_zbroja_ramie_l = {zaczep = "EkwLeftUpperArmAttachment", glb = {-0.125, -0.06, -0, 0, 0, 0}, fbx = {0.125, -0.06, 0, 0, 180, 0}},
	rycerz_zbroja_przedramie_l = {zaczep = "EkwLeftLowerArmAttachment", glb = {-0.03, -0.04, 0.028, 0, 0, 0}, fbx = {0.03, -0.04, -0.028, 0, 180, 0}},
	rycerz_zbroja_ramie_p = {zaczep = "EkwRightUpperArmAttachment", glb = {0.125, -0.06, -0, 0, 0, 0}, fbx = {-0.125, -0.06, 0, 0, 180, 0}},
	rycerz_zbroja_przedramie_p = {zaczep = "EkwRightLowerArmAttachment", glb = {0.03, -0.04, 0.028, 0, 0, 0}, fbx = {-0.03, -0.04, -0.028, 0, 180, 0}},
	rycerz_zbroja_biodra = {zaczep = "EkwLowerTorsoAttachment", glb = {-0, 0.765, -0, 0, 0, 0}, fbx = {0, 0.765, 0, 0, 180, 0}},
	rycerz_nogawice_biodra = {zaczep = "EkwLowerTorsoAttachment", glb = {-0, -0, -0, 0, 0, 0}, fbx = {0, -0, 0, 0, 180, 0}},
	rycerz_nogawice_udo_l = {zaczep = "EkwLeftUpperLegAttachment", glb = {-0, -0, -0.03, 0, 0, 0}, fbx = {0, -0, 0.03, 0, 180, 0}},
	rycerz_nogawice_udo_p = {zaczep = "EkwRightUpperLegAttachment", glb = {-0, -0, -0.03, 0, 0, 0}, fbx = {0, -0, 0.03, 0, 180, 0}},
	rycerz_pas_biodra = {zaczep = "EkwLowerTorsoAttachment", glb = {-0, -0, -0.65, 0, 0, 0}, fbx = {0, -0, 0.65, 0, 180, 0}},
	rycerz_rekawice_dlon_l = {zaczep = "EkwLeftHandAttachment", glb = {-0, -0.06, -0, 0, 0, 0}, fbx = {0, -0.06, 0, 0, 180, 0}},
	rycerz_rekawice_dlon_p = {zaczep = "EkwRightHandAttachment", glb = {-0, -0.06, -0, 0, 0, 0}, fbx = {0, -0.06, 0, 0, 180, 0}},
	rycerz_buty_golen_l = {zaczep = "EkwLeftLowerLegAttachment", glb = {-0, -0.05, -0.08, 0, 0, 0}, fbx = {0, -0.05, 0.08, 0, 180, 0}},
	rycerz_buty_stopa_l = {zaczep = "EkwLeftFootAttachment", glb = {-0, -0, -0.03, 0, 0, 0}, fbx = {0, -0, 0.03, 0, 180, 0}},
	rycerz_buty_golen_p = {zaczep = "EkwRightLowerLegAttachment", glb = {-0, -0.05, -0.08, 0, 0, 0}, fbx = {0, -0.05, 0.08, 0, 180, 0}},
	rycerz_buty_stopa_p = {zaczep = "EkwRightFootAttachment", glb = {-0, -0, -0.03, 0, 0, 0}, fbx = {0, -0, 0.03, 0, 180, 0}},
	rycerz_miecz = {zaczep = "RightGripAttachment", glb = {-0, -1.659, -0, 0, 0, 0}, fbx = {0, -1.659, 0, 0, 180, 0}},
	rycerz_tarcza = {zaczep = "LeftGripAttachment", glb = {-0.746, -0, 0.3, 0, 0, 0}, fbx = {0.746, -0, -0.3, 0, 180, 0}},
	kot_mag_kapelusz = {zaczep = "HatAttachment", glb = {-0, -0.878, -0, 0, 0, 0}, fbx = {0, -0.878, 0, 0, 180, 0}},
	kot_mag_szata_tulow = {zaczep = "EkwUpperTorsoAttachment", glb = {-0, -0.06, 0.045, 0, 0, 0}, fbx = {0, -0.06, -0.045, 0, 180, 0}},
	kot_mag_szata_ramie_l = {zaczep = "EkwLeftUpperArmAttachment", glb = {-0, -0, -0, 0, 0, 0}, fbx = {0, -0, 0, 0, 180, 0}},
	kot_mag_szata_przedramie_l = {zaczep = "EkwLeftLowerArmAttachment", glb = {-0, 0.068, -0, 0, 0, 0}, fbx = {0, 0.068, 0, 0, 180, 0}},
	kot_mag_szata_ramie_p = {zaczep = "EkwRightUpperArmAttachment", glb = {-0, -0, -0, 0, 0, 0}, fbx = {0, -0, 0, 0, 180, 0}},
	kot_mag_szata_przedramie_p = {zaczep = "EkwRightLowerArmAttachment", glb = {-0, 0.068, -0, 0, 0, 0}, fbx = {0, 0.068, 0, 0, 180, 0}},
	kot_mag_szata_biodra = {zaczep = "EkwLowerTorsoAttachment", glb = {-0, 0.37, 0.291, 0, 0, 0}, fbx = {0, 0.37, -0.291, 0, 180, 0}},
	kot_mag_pas_biodra = {zaczep = "EkwLowerTorsoAttachment", glb = {-0, -0.005, -0.025, 0, 0, 0}, fbx = {0, -0.005, 0.025, 0, 180, 0}},
	kot_mag_kostur = {zaczep = "RightGripAttachment", glb = {-0, -0.835, -0, 0, 0, 0}, fbx = {0, -0.835, 0, 0, 180, 0}},
	zwiadowca_kaptur_glowa = {zaczep = "EkwHeadAttachment", glb = {-0, -0.216, 0.45, 0, 0, 0}, fbx = {0, -0.216, -0.45, 0, 180, 0}},
	zwiadowca_kaptur_tulow = {zaczep = "EkwUpperTorsoAttachment", glb = {-0, 0.049, 0.013, 0, 0, 0}, fbx = {0, 0.049, -0.013, 0, 180, 0}},
	zwiadowca_kurtka_tulow = {zaczep = "EkwUpperTorsoAttachment", glb = {-0, -0.09, -0.05, 0, 0, 0}, fbx = {0, -0.09, 0.05, 0, 180, 0}},
	zwiadowca_kurtka_ramie_l = {zaczep = "EkwLeftUpperArmAttachment", glb = {-0.048, -0.034, -0, 0, 0, 0}, fbx = {0.048, -0.034, 0, 0, 180, 0}},
	zwiadowca_kurtka_przedramie_l = {zaczep = "EkwLeftLowerArmAttachment", glb = {-0.005, -0, -0, 0, 0, 0}, fbx = {0.005, -0, 0, 0, 180, 0}},
	zwiadowca_kurtka_ramie_p = {zaczep = "EkwRightUpperArmAttachment", glb = {0.048, -0.034, -0, 0, 0, 0}, fbx = {-0.048, -0.034, 0, 0, 180, 0}},
	zwiadowca_kurtka_przedramie_p = {zaczep = "EkwRightLowerArmAttachment", glb = {0.005, -0, -0, 0, 0, 0}, fbx = {-0.005, -0, 0, 0, 180, 0}},
	zwiadowca_kurtka_udo_l = {zaczep = "EkwLeftUpperLegAttachment", glb = {-0, -0.089, -0, 0, 0, 0}, fbx = {0, -0.089, 0, 0, 180, 0}},
	zwiadowca_kurtka_udo_p = {zaczep = "EkwRightUpperLegAttachment", glb = {-0, -0.089, -0, 0, 0, 0}, fbx = {0, -0.089, 0, 0, 180, 0}},
	zwiadowca_spodnie_biodra = {zaczep = "EkwLowerTorsoAttachment", glb = {-0, -0, -0, 0, 0, 0}, fbx = {0, -0, 0, 0, 180, 0}},
	zwiadowca_spodnie_udo_l = {zaczep = "EkwLeftUpperLegAttachment", glb = {-0, -0, -0, 0, 0, 0}, fbx = {0, -0, 0, 0, 180, 0}},
	zwiadowca_spodnie_udo_p = {zaczep = "EkwRightUpperLegAttachment", glb = {-0, -0, -0, 0, 0, 0}, fbx = {0, -0, 0, 0, 180, 0}},
	zwiadowca_pas_biodra = {zaczep = "EkwLowerTorsoAttachment", glb = {-0, 0.075, 0.095, 0, 0, 0}, fbx = {0, 0.075, -0.095, 0, 180, 0}},
	zwiadowca_rekawice_dlon_l = {zaczep = "EkwLeftHandAttachment", glb = {-0, -0.005, -0, 0, 0, 0}, fbx = {0, -0.005, 0, 0, 180, 0}},
	zwiadowca_rekawice_dlon_p = {zaczep = "EkwRightHandAttachment", glb = {-0, -0.005, -0, 0, 0, 0}, fbx = {0, -0.005, 0, 0, 180, 0}},
	zwiadowca_buty_golen_l = {zaczep = "EkwLeftLowerLegAttachment", glb = {-0, -0, -0, 0, 0, 0}, fbx = {0, -0, 0, 0, 180, 0}},
	zwiadowca_buty_stopa_l = {zaczep = "EkwLeftFootAttachment", glb = {-0, -0, -0.035, 0, 0, 0}, fbx = {0, -0, 0.035, 0, 180, 0}},
	zwiadowca_buty_golen_p = {zaczep = "EkwRightLowerLegAttachment", glb = {-0, -0, -0, 0, 0, 0}, fbx = {0, -0, 0, 0, 180, 0}},
	zwiadowca_buty_stopa_p = {zaczep = "EkwRightFootAttachment", glb = {-0, -0, -0.035, 0, 0, 0}, fbx = {0, -0, 0.035, 0, 180, 0}},
	zwiadowca_luk_tulow = {zaczep = "EkwUpperTorsoAttachment", glb = {0.465, -0.373, 0.258, 0, 0, 0}, fbx = {-0.465, -0.373, -0.258, 0, 180, 0}},
	zwiadowca_luk = {zaczep = "LeftGripAttachment", glb = {-0, -0, 0.177, 0, 0, 0}, fbx = {0, -0, -0.177, 0, 180, 0}},
	zwiadowca_sztylet = {zaczep = "RightGripAttachment", glb = {-0, -0.54, -0.015, 0, 0, 0}, fbx = {0, -0.54, 0.015, 0, 180, 0}},
	karczmarz_chochla = {zaczep = "RightGripAttachment", glb = {0.46, -0.68, -0, 0, 0, 0}, fbx = {-0.46, -0.68, 0, 0, 180, 0}},
}

local Selection = game:GetService("Selection")

local function ustaw(akcesorium: Instance)
	local d = DANE[akcesorium.Name]
	local handle = akcesorium:FindFirstChild("Handle")
	if not d or not handle or not handle:IsA("BasePart") then
		return
	end
	local v = d[ZRODLO]
	local att = handle:FindFirstChild(d.zaczep) or Instance.new("Attachment")
	att.Name = d.zaczep
	att.Position = Vector3.new(v[1], v[2], v[3])
	att.Orientation = Vector3.new(v[4], v[5], v[6])
	att.Parent = handle
	print("Zaczep", d.zaczep, "->", akcesorium:GetFullName())
end

for _, obiekt in Selection:Get() do
	if obiekt:IsA("Accessory") then
		ustaw(obiekt)
	end
	for _, dziecko in obiekt:GetDescendants() do
		if dziecko:IsA("Accessory") then
			ustaw(dziecko)
		end
	end
end
