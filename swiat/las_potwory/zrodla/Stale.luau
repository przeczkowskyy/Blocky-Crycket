--[[
	Stale — wspólne stałe pakietu „potwory w ruchu” (serwer i klient czytają je z jednego miejsca).
	Liczby zasad (odstęp, smycz, blokada domu, prędkości) są w DanePotworow (z potwory.json), nie tutaj.
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

return S
