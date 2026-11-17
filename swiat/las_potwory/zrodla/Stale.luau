--[[
	Stale — wspólne stałe pakietu „potwory w ruchu” (serwer i klient czytają je z jednego miejsca).
	Liczby zasad (odstęp, smycz, blokada domu, prędkości) są w DanePotworow (z potwory.json), nie tutaj.

	Drugi kontener (16.11.2026): ten sam kod potworów działa też w Workspace/LasPasGra (las-pas, swiat/las_pas_gra).
	Kontener może nadpisać wybrane stałe atrybutem „Stale_<NAZWA>” ustawionym przy budowie — patrz koniec pliku.
	Stary las (Workspace/LasPotwory) takich atrybutów nie ma, więc u niego wszystko zostaje jak niżej.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local S = {}
S.WERSJA = "las_potwory etap A (2026-11-15)"
S.NAZWA_KONTENERA = "LasPotwory"
S.NAZWA_BIOMU = "BiomLas"
S.NAZWA_PROTOTYPU = "TestWalki2"
S.NAZWA_SZABLONOW = "LasPotworySzablony"         -- ReplicatedStorage
S.SZABLONY = { "lesny_slime", "cierniowy_wilk", "muchomornik", "straznik_lasu" }
S.PREFIKS = "[LasPotwory] "
S.GADATLIWY = false           -- true: serwer drukuje każde odrodzenie i wejście na pętlę

------------------------------------------------------------------ serwer
S.OKRES_RUCHU = 0.25          -- s (4 Hz)
S.OKRES_ODRADZANIA = 1.0      -- s
S.ODSTEP_PROSB = 1.0          -- s, jak SerwerWalki2
S.ZAPAS_SESJI = 0.4           -- s, jak SerwerWalki2
S.ZAPAS_ZAJETOSCI = 1.0       -- s ponad walka.czas
S.ZASIEG_E = 8                -- studs w poziomie od punktu bazowego + promień gatunku
S.ZAPAS_E_SERWER = 6          -- studs zapasu po stronie serwera (opóźnienie, ruch 4 Hz)
S.MAKS_ROZNICA_WYSOKOSCI = 6
S.PRZEDPOLE = 6               -- studs od węzła w stronę domu
S.PROG_POZYCJI = 0.05         -- studs: mniejszej zmiany nie zapisujemy
S.PROG_KIERUNKU = math.rad(2)
S.KLASY = { "wojownik", "zwiadowca", "mag" }
S.POZIOMY_BOHATERA = { "auto", "1", "5", "10" }
S.ARENA_PROTOTYPU = Vector3.new(0, 1, 250)  -- = Ustawienia.scena().Position w swiat/test_walki2
-- wdrożenie 15.11: miejsce ma StreamOutBehavior = Opportunistic, więc arena prototypu wypadała u klienta zaraz po
-- prośbie (postać stoi 2000+ studów dalej) i walka szła na gołej płycie. Serwer ponawia prośbę co sekundę przez
-- walka.czas + tyle sekund (wejście, wynik, okno łupu).
S.PODTRZYMANIE_ARENY = 45     -- s ponad walka.czas
S.PODTRZYMANIE_CO = 1.0       -- s między prośbami o arenę

------------------------------------------------------------------ klient
S.PROMIEN_WIDOKU = 120
S.PROMIEN_USUNIECIA = 135
S.MAKS_WIDOKOW = 12           -- budujemy i animujemy najwyżej tylu najbliższych
S.MAKS_WIDOKOW_TWARDO = 14
S.BUDZET_CZESCI = 4000        -- suma brył wszystkich widoków (telefon: zacząć od 1500, rozdz. 10)
S.BUDOWA_CO = 0.1             -- s między kolejnymi klonami
S.WYBOR_CO = 0.5              -- s między przeliczeniami listy widoków
S.PODPOWIEDZ_CO = 0.1
S.SKOK_WYGLADZANIA = 20
S.OBROT_NA_S = 8              -- rad/s
S.CZERWONA_OD = 3             -- poziomów ponad poziom bohatera
S.TABLICZKA_ZASIEG = 80
S.BANER_S = 5
-- wdrożenie 15.11 (pomiar w Studio, rozdz. 9.3): dalsze widoki przestawiamy i animujemy rzadziej, z sumą dt
S.KLATKA_PELNA_RANGA = 3      -- tylu najbliższych kamerze widoków zawsze co klatkę
S.KLATKA_PELNA_DO = 25        -- studs od kamery: bliżej zawsze co klatkę
S.KLATKA_POLOWA_DO = 70       -- do tej odległości co KLATKA_CO_DALEJ klatek, dalej co KLATKA_CO_DALEKO
S.KLATKA_CO_DALEJ = 2
S.KLATKA_CO_DALEKO = 3

------------------------------------------------------------------ kolory (jak Ustawienia.KOLORY prototypu)
local function hex(h: string): Color3
	return Color3.fromHex(h)
end
S.KOLORY = {
	tusz = hex("#17121F"), bialy = hex("#FFFFFF"), krem = hex("#FFF3D1"), zolty = hex("#FFD23F"),
	czerwony = hex("#E8364F"), zielony = hex("#52D273"), fiolet = hex("#7B4DFF"), szary = hex("#8D93A6"),
}
S.KOLOR_BURSZTYNOWY = hex("#F2B030")

------------------------------------------------------------------ drugi kontener (16.11.2026, swiat/las_pas_gra)
S.GUI_BOHATERA = "LasPotworyBohater"   -- ScreenGui panelu bohatera (dwa kontenery = dwie nazwy)
S.GUI_BANERA = "LasPotworyBaner"       -- ScreenGui banera po Strażniku
S.PANEL_Y = 8                          -- px od góry: przycisk panelu bohatera (drugi kontener stawia go niżej)
S.PANEL_PREFIKS = ""                   -- przed napisem „Bohater: …” (drugi kontener: skąd jest panel)
S.SYGNAL_WYNIKU = "WynikWalki"         -- opcjonalny BindableEvent w Sygnaly: serwer strzela nim po przyjęciu walki
S.ATRYBUT_BLOKADY = "BlokadaWalki"     -- atrybut gracza (ustawia inny skrypt serwera, np. przelot kamery): bez walk
-- jeden komplet na ekranie (17.11.2026): gdy w miejscu stoją dwa kontenery potworów (stary las i las-pas), panel
-- bohatera każdego z nich widać tylko w jego lesie (prostokąt płyty biomu z DanePotworow + zapas), więc nigdy dwa naraz
S.PANEL_TYLKO_W_LESIE = true
S.PANEL_ZAPAS = 40                     -- studs wokół płyty biomu, w których panel jeszcze widać
S.PODPIS_STRAZNIKA = "Wróci za 2 min"  -- podpis banera po Strażniku; inny skrypt kontenera może go podmienić lokalnym
                                       -- atrybutem kontenera PodpisBaneraStraznika (las-pas: „brama otwarta”) — jeden baner

------------------------------------------------------------------ nadpisania z atrybutów kontenera
-- Atrybut kontenera „Stale_<NAZWA>” (ustawia zbuduj.py drugiego kontenera) zastępuje istniejącą stałą tego samego
-- typu: napis, liczbę albo wartość logiczną; listę napisów (np. SZABLONY) podaje się jako napis z przecinkami.
-- Inne typy i nieznane nazwy są pomijane z ostrzeżeniem. Bez atrybutów (stary las) nic się nie zmienia.
local kontenerStalych = script.Parent and script.Parent.Parent
if kontenerStalych then
	for nazwa, stara in S do
		local nowa = kontenerStalych:GetAttribute("Stale_" .. nazwa)
		if nowa ~= nil then
			if type(stara) == "table" and type(stara[1]) == "string" and type(nowa) == "string" then
				local lista = {}
				for _, kawalek in string.split(nowa, ",") do
					local x = string.match(kawalek, "^%s*(.-)%s*$")
					if x and x ~= "" then
						table.insert(lista, x)
					end
				end
				S[nazwa] = lista
			elseif type(stara) == type(nowa) and type(stara) ~= "table" then
				S[nazwa] = nowa
			else
				warn("[Stale] atrybut Stale_" .. nazwa .. " ma typ " .. type(nowa) .. ", a stała " .. type(stara) .. " — pomijam")
			end
		end
	end
end

return S
