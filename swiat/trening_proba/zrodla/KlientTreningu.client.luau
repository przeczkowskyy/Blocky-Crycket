--[[
	KlientTreningu — kliencka połowa próby Training Center (Script, RunContext = Client, w kontenerze
	Workspace/TreningProba). Własny ScreenGui „TreningProba” tworzony tym skryptem (HUD-u i plików src/ nie rusza).

	Co robi:
		1. TYMCZASOWY wybór mini-gry (sześć kafelków) — docelowe okno 2D robi Paweł (D-093). Otwiera go: E przy trenerze
		   w bazarze (zdarzenie ReplicatedStorage.OknoMiejsca z id "training_center"), E przy własnej tablicy wejścia
		   i przy tablicy w arenie (serwer → "wybor"), przycisk INNA GRA.
		   Gdy okno Pawła będzie gotowe: atrybut kontenera WyborTymczasowy = false (ten wybór się nie otwiera),
		   a okno Pawła wywołuje u klienta:  workspace.TreningProba.Sygnaly.WybierzGre:Invoke("sila")
		2. Stanowisko: kamera stała (Scriptable), klawisze ruchu pochłonięte (ContextActionService, wysoki priorytet),
		   dotykowe sterowanie Robloxa wyłączone na czas stanowiska, inne ekrany (HUD) schowane; po wyjściu wszystko wraca.
		   Przed rundą i w czasie odliczania — podpowiedź obrazkowa (co widzisz → co naciskasz → co się dzieje).
		3. Runda: naciśnięcie → natychmiastowy efekt z lokalnej kopii logiki (LogikaTreningu) i zgłoszenie do serwera;
		   licznik serii i przyrost poprawia werdykt serwera ("wynik"). Efekty: licznik serii z „podskokiem”, krótki
		   napis, błysk ekranu, odłamki, wstrząs kamery, dźwięki: odcinki arkusza efektów z Workspace/DzwiekGra (pakiet
		   swiat/dzwiek_gra, gdy arkusz jest wgrany), inaczej pliki wbudowane w klienta (rbxasset://sounds/).
		4. Sześć mini-gier (każda ma własne stanowisko, kamerę, przyciski dotykowe i rysowanie w GRY[gra]):
		   Siła „Rozbijanie” — strzałka w stronę skrzynki przy kółku; Pancerz „Blok” — BLOK, gdy pierścień dojdzie do
		   kółka (fioletowy = zmyłka); Kondycja „Bieżnia” — biegacz na taśmie, ślady stóp jadą do linii, lewa / prawa
		   w rytmie bębna; Zręczność „Kłody” — ramię z kłodą obraca się wokół słupa, niska: SKOK, wysoka: PADNIJ (postać
		   skacze i pada — przesunięcie stawu biodra tylko u siebie); Inteligencja „Runy” — kamienie świecą po kolei,
		   gracz powtarza; Szczęście „Koniczyny” — postać z koszykiem nad głową przechodzi między trzema torami.
		5. Wygląd jak w walce (18.11.2026, polecenie Karola: „pod takimi kątami i w takich samych efektach POW / PAF,
		   konfetti jak walki”):
		   • kamera stanowiska nisko, pod wąskim kątem widzenia, z ukosa (rachunek: Moduly/KameraTreningu) — dojazd
		     w odliczaniu, w rundzie stoi (krótkie zawężenie kąta i drżenie przy trafieniu), po rundzie zbliżenie na
		     postać, która obraca się do kamery i się cieszy;
		   • komiksowe napisy (Moduly/KomiksTreningu: Bangers, obrys tuszem, obrót, gwiazda za dużymi słowami) przy
		     miejscu trafienia, duże słowa („SERIA 10!”, „+1 Siła!”) w miejscu stanowiska z danych;
		   • efekty 3D trafień w języku walki (Moduly/EfektyTreningu: z modułu efektów walki, gdy stoi w miejscu, inaczej
		     własne) i papierowe konfetti przy podsumowaniu, gdy runda dała punkt statystyki (większe bez pudła);
		   • postać: gdy w miejscu działa bohater klasy (BindableFunction Workspace/BohaterSwiat/Sygnaly/RuchBohatera),
		     bieg, skok, padnij, ręce w górę i radość idą przez ten haczyk; bez niego — stawy i animacje awatara.
	Haczyk testowy: Sygnaly/SterowanieKlienta ("stan" | "wybor" | "okno" | "graj", gra | "start" | "nacisnij", w |
	"autograj", celnosc, blokujZmylki | "zaplanuj", lista | "spam", n, w | "surowe", w, dt | "wyjdz" | "inna" | "zamknij"
	| "przerwij" | "dlugie_napisy", k | "napis", tekst, styl | "konfetti", wielkie).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneTreningu"))
local L = require(moduly:WaitForChild("LogikaTreningu"))
local Kam = require(moduly:WaitForChild("KameraTreningu"))
local Efekty = require(moduly:WaitForChild("EfektyTreningu"))
local Komiks = require(moduly:WaitForChild("KomiksTreningu"))
local zdalne: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaTreningu")
local sygnaly = kontener:WaitForChild("Sygnaly")
local sterowanie: BindableFunction = sygnaly:WaitForChild("SterowanieKlienta")
local wybierzF: BindableFunction = sygnaly:WaitForChild("WybierzGre")
local ekrany = gracz:WaitForChild("PlayerGui")

local U = D.ui
local T = D.teksty
local KOL = U.kolory
local PX = U.tekst_px
local KA = U.kamera -- ruch kamery (jak w walce)
local KX = U.komiks -- komiksowe napisy
local EF = U.efekty -- efekty 3D trafień i konfetti
local BH = U.bohater -- haczyk bohatera klasy
-- czcionka z pełnymi polskimi znakami (FredokaOne rysuje ę, ż, ś, ć, ź zastępczą, mniejszą czcionką)
local CZCIONKA = Font.new(Font.fromEnum(Enum.Font[U.czcionka]).Family, Enum.FontWeight[U.waga_czcionki])
-- nagłówek karty podsumowania: czcionka nagłówków walki (ma polskie znaki — sprawdzone jak czcionka napisów)
local CZCIONKA_NAGLOWKA = Font.fromEnum(Enum.Font[KX.czcionka_naglowka])

local function kolor(h)
	return Color3.fromHex(h)
end

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

local function teraz()
	return workspace:GetServerTimeNow()
end

local function sciezka(korzen, tekst)
	local o = korzen
	for i, n in string.split(tekst, "/") do
		if o == nil then
			return nil
		end
		if not (i == 1 and n == "Workspace") then
			o = o:FindFirstChild(n)
		end
	end
	return o
end

local losowe = Random.new()

local KOLOR_GRY = {}
for _, st in D.statystyki do
	KOLOR_GRY[st.id] = st.kolor
end
local TRAFIENIA = {
	sila = T.trafienia, pancerz = T.trafienia_blok, kondycja = T.trafienia_rytm, zrecznosc = T.trafienia_unik,
	inteligencja = T.trafienia_runy, szczescie = T.trafienia_lapanie,
}
local PODBIEG = "F28C28"

------------------------------------------------------------------ stan
local stan = {
	ekran = "brak", -- brak | stanowisko | runda | podsumowanie
	wybor = false, -- tymczasowy wybór na ekranie
	zrodlo = nil,
	gra = nil, -- id gry na stanowisku
	runda = nil, -- dane rundy z serwera { id, gra, t0, dlugosc, plan }
	R = nil, -- lokalna kopia rundy (natychmiastowe efekty)
	lokalne = {}, -- nr → true / false (werdykt pokazany)
	wyniki = {}, -- ostatnie werdykty serwera (haczyk)
	rozbieznosci = 0, -- werdykt serwera ≠ lokalny
	odliczanie = nil,
	przedStartem = false, -- odliczanie trwa (podpowiedź obrazkowa na ekranie)
	wstrzas = nil,
	miecz = nil, -- { t, k }
	tarcza = nil, -- { t }
	ostatnieOdliczanie = nil,
	podsumowanie = nil,
	tor = 2, -- Koniczyny: tor koszyka (1..3)
	ruchToru = nil, -- { od, ["do"], t }
	unik = nil, -- Kłody: { rodzaj, t } — skok, padnij, uderzenie
	krok = {}, -- Bieżnia: stopa → chwila naciśnięcia (błysk celu)
	beben = 0, -- Bieżnia: numer ostatniego uderzenia bębna
	runyNacisk = {}, -- Runy: runa → { t, zle }
	pokazGrany = nil, -- Runy: "pokazy:i" ostatnio zagranej nuty pokazu
	pokazNapis = nil, -- Runy: numer pokazu, przy którym był napis PATRZ / TWOJA KOLEJ
	final = nil, -- po rundzie: { korzen, fx, cfOd, cfDo, t, obrot } — zbliżenie na postać, obrót do kamery
	liczenie = nil, -- karta podsumowania: { t, a } — liczby rosną od zera
	konfetti = 0, -- ile kawałków konfetti poszło przy ostatnim podsumowaniu (haczyk)
	radosc = nil, -- postać się cieszy: chwila startu (podskoki awatara bez animacji)
}

------------------------------------------------------------------ ekran: pomocnicze (rozmiary tylko z D.ui)
local gui = Instance.new("ScreenGui")
gui.Name = "TreningProba"
gui.ResetOnSpawn = false
gui.DisplayOrder = U.kolejnosc_wyswietlania
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
gui.Enabled = false
-- obszar GUI omija pasek Robloxa i wycięcia ekranu telefonu (bezpieczny obszar); układ liczy się od jego rozmiaru
gui.ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets
gui.Parent = ekrany

-- korzeń wszystkich paneli: cały ekran, a przy atrybucie kontenera EmulacjaEkranu (Vector2, punkty telefonu) —
-- prostokąt telefonu na środku okna, powiększony UIScale (zrzuty „jak na telefonie”, wzór: swiat/test_walki2)
local korzen = Instance.new("Frame")
korzen.Name = "Ekran"
korzen.BackgroundTransparency = 1
korzen.Size = UDim2.fromScale(1, 1)
korzen.Parent = gui
local skalaKorzenia = Instance.new("UIScale")
skalaKorzenia.Parent = korzen

-- warstwa komiksowa: napisy przy miejscu trafienia i pierścienie Pancerza. Osobny ScreenGui na cały ekran
-- (IgnoreGuiInset), bo jego współrzędne to piksele widoku kamery (Camera:WorldToViewportPoint) — jak w ekranie walki;
-- stoi pod oknami mini-gry (niższy DisplayOrder), więc napis nigdy nie przykrywa przycisku ani panelu rundy
local guiKomiks = Instance.new("ScreenGui")
guiKomiks.Name = "TreningProbaKomiks"
guiKomiks.ResetOnSpawn = false
guiKomiks.IgnoreGuiInset = true
guiKomiks.DisplayOrder = U.kolejnosc_wyswietlania - 1
guiKomiks.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
guiKomiks.Enabled = false
guiKomiks.Parent = ekrany
local warstwa = Instance.new("Frame")
warstwa.Name = "Napisy"
warstwa.BackgroundTransparency = 1
warstwa.Size = UDim2.fromScale(1, 1)
warstwa.Active = false
warstwa.Parent = guiKomiks
local komiks = Komiks.nowy(warstwa, U, CZCIONKA)

local skale = {}
local przyciski = {} -- { obiekt, szer, wys } (bazowo)
local napisy = {} -- { obiekt, rozmiar } (bazowo)

local function zaokraglij(o, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, r)
	c.Parent = o
	return c
end

local function obrysuj(o, grubosc, h)
	local s = Instance.new("UIStroke")
	s.Thickness = grubosc
	s.Color = kolor(h or KOL.tusz)
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = o
	return s
end

-- obrys liter (napisy w stylu walki: tytuł karty podsumowania, przyrost)
local function obrysTekstu(l, grubosc, h)
	local s = Instance.new("UIStroke")
	s.Thickness = grubosc
	s.Color = kolor(h or KOL.tusz)
	s.LineJoinMode = Enum.LineJoinMode.Round
	s.Parent = l
	return s
end

local function panel(nazwa, szer, wys, pozycja, kotwica, tlo)
	local f = Instance.new("Frame")
	f.Name = nazwa
	f.Size = UDim2.fromOffset(szer, wys)
	f.Position = pozycja
	f.AnchorPoint = kotwica
	if tlo == "" then
		f.BackgroundTransparency = 1
	else
		f.BackgroundColor3 = kolor(tlo or KOL.krem)
	end
	f.BorderSizePixel = 0
	f.Visible = false
	local s = Instance.new("UIScale")
	s.Parent = f
	table.insert(skale, s)
	f.Parent = korzen
	return f
end

local function napis(rodzic, nazwa, tekst, rozmiar, x, y, szer, wys, h, wyrownaj)
	local l = Instance.new("TextLabel")
	l.Name = nazwa
	l.BackgroundTransparency = 1
	l.Position = UDim2.fromOffset(x, y)
	l.Size = UDim2.fromOffset(szer, wys)
	l.FontFace = CZCIONKA
	l.TextSize = PX[rozmiar]
	l.TextColor3 = kolor(h or KOL.tusz)
	l.TextXAlignment = wyrownaj or Enum.TextXAlignment.Center
	l.TextWrapped = true
	l.Text = tekst
	l.Parent = rodzic
	table.insert(napisy, { obiekt = l, rozmiar = PX[rozmiar] })
	return l
end

local function przycisk(rodzic, nazwa, tekst, x, y, szer, wys, tlo, akcja, rozmiar)
	local b = Instance.new("TextButton")
	b.Name = nazwa
	b.Position = UDim2.fromOffset(x, y)
	b.Size = UDim2.fromOffset(szer, wys)
	b.BackgroundColor3 = kolor(tlo)
	b.AutoButtonColor = true
	b.FontFace = CZCIONKA
	b.TextSize = PX[rozmiar or "sredni"]
	b.TextColor3 = kolor(KOL.krem)
	b.Text = tekst
	b.Parent = rodzic
	zaokraglij(b, 10)
	obrysuj(b, 2)
	table.insert(przyciski, { obiekt = b, szer = szer, wys = wys })
	table.insert(napisy, { obiekt = b, rozmiar = PX[rozmiar or "sredni"] })
	if akcja then
		b.Activated:Connect(akcja)
	end
	return b
end

local KATY = { gora = 0, prawo = 90, dol = 180, lewo = 270 }

-- strzałka z dwóch kresek (bez obrazków): ^ obrócone o kąt kierunku; y = środek w pionie (ułamek), skala grubości
local function strzalka(rodzic, kierunek, y, kolorKresek, skala)
	local a = math.rad(KATY[kierunek])
	local k = skala or 1
	for i, dx in { -4.5 * k, 4.5 * k } do
		local f = Instance.new("Frame")
		f.Name = "Kreska" .. i
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		f.Size = UDim2.fromOffset(5 * k, 17 * k)
		f.Position = UDim2.new(0.5, dx * math.cos(a), y or 0.4, dx * math.sin(a))
		f.Rotation = (if i == 1 then 45 else -45) + KATY[kierunek]
		f.BackgroundColor3 = kolor(kolorKresek or KOL.krem)
		f.BorderSizePixel = 0
		zaokraglij(f, 3)
		f.Parent = rodzic
	end
end

------------------------------------------------------------------ ikony z ramek (bez obrazków): runy, stopa, kłoda, koniczyna…
local function ramka(rodzic, nazwa, x, y, w, h, h_kolor, przezr)
	local f = Instance.new("Frame")
	f.Name = nazwa
	f.AnchorPoint = Vector2.new(0.5, 0.5)
	f.Position = UDim2.fromOffset(x, y)
	f.Size = UDim2.fromOffset(w, h)
	f.BackgroundColor3 = kolor(h_kolor or KOL.krem)
	f.BackgroundTransparency = przezr or 0
	f.BorderSizePixel = 0
	f.Parent = rodzic
	return f
end

-- znak runy (kształt różny dla każdej runy, nie tylko kolor): pierścień, kwadrat, romb, krzyż
local function glifRuny(rodzic, k, x, y, r, h_kolor)
	if k == "gora" then
		local f = ramka(rodzic, "Znak", x, y, r, r, h_kolor, 1)
		zaokraglij(f, 999)
		obrysuj(f, math.max(3, r * 0.16), h_kolor)
	elseif k == "lewo" then
		local f = ramka(rodzic, "Znak", x, y, r * 0.86, r * 0.86, h_kolor, 1)
		obrysuj(f, math.max(3, r * 0.16), h_kolor)
	elseif k == "prawo" then
		local f = ramka(rodzic, "Znak", x, y, r * 0.7, r * 0.7, h_kolor, 1)
		f.Rotation = 45
		obrysuj(f, math.max(3, r * 0.16), h_kolor)
	else
		ramka(rodzic, "Znak1", x, y, r, r * 0.24, h_kolor)
		ramka(rodzic, "Znak2", x, y, r * 0.24, r, h_kolor)
	end
end

local function ikonaStopy(rodzic, x, y, r, h_kolor)
	local s = ramka(rodzic, "Stopa", x, y + r * 0.12, r * 0.5, r * 0.78, h_kolor)
	zaokraglij(s, 999)
	for i, dx in { -0.17, 0, 0.17 } do
		local p = ramka(rodzic, "Palec" .. i, x + dx * r, y - r * 0.42, r * 0.15, r * 0.15, h_kolor)
		zaokraglij(p, 999)
	end
end

local function ikonaKoniczyny(rodzic, x, y, r, h_kolor)
	for i, d in { { -0.2, -0.12 }, { 0.2, -0.12 }, { 0, 0.2 } } do
		local l = ramka(rodzic, "Listek" .. i, x + d[1] * r, y + d[2] * r, r * 0.42, r * 0.42, h_kolor)
		zaokraglij(l, 999)
	end
end

------------------------------------------------------------------ ekran: panele
local ui = {}

-- panel rundy — zwarty (poprawka po zrzutach telefonu 18.11.2026: dawny 268 × 92 zajmował ok. 40% szerokości
-- telefonu i zasłaniał koronę drzewa Koniczyn): czas · seria · mnożnik w jednym wierszu, pod nim pasek statystyki.
-- Położenie (prawy górny róg) i przyciski gry ustawia odswiezSkale z L.ukladUI — ten sam układ sprawdza test telefonu.
ui.status = panel("Status", U.status_px[1], U.status_px[2], UDim2.fromOffset(0, 8), Vector2.zero)
zaokraglij(ui.status, 12)
obrysuj(ui.status, 3)
ui.czas = napis(ui.status, "Czas", "", "sredni", 8, 4, 50, 24, KOL.tusz, Enum.TextXAlignment.Left)
ui.seria = napis(ui.status, "Seria", "SERIA 0", "sredni", 58, 4, 96, 24, KOL.tusz, Enum.TextXAlignment.Center)
ui.mnoznik = napis(ui.status, "Mnoznik", "", "maly", 152, 6, 50, 20, KOL.zloto, Enum.TextXAlignment.Right)
ui.pasek = Instance.new("Frame")
ui.pasek.Name = "Pasek"
ui.pasek.Position = UDim2.fromOffset(8, 34)
ui.pasek.Size = UDim2.fromOffset(U.status_px[1] - 16, 9)
ui.pasek.BackgroundColor3 = kolor(KOL.szary)
ui.pasek.BorderSizePixel = 0
zaokraglij(ui.pasek, 3)
ui.pasek.Parent = ui.status
ui.wypelnienie = Instance.new("Frame")
ui.wypelnienie.Name = "Wypelnienie"
ui.wypelnienie.Size = UDim2.fromScale(0, 1)
ui.wypelnienie.BackgroundColor3 = kolor(KOL.zloto)
ui.wypelnienie.BorderSizePixel = 0
zaokraglij(ui.wypelnienie, 3)
ui.wypelnienie.Parent = ui.pasek
local skalaSerii = Instance.new("UIScale")
skalaSerii.Parent = ui.seria

ui.przerwij = panel("Przerwij", U.przycisk_maly_px, U.przycisk_maly_px, UDim2.fromOffset(0, 8), Vector2.zero, "")

-- sterowanie dotykowe: przy krawędziach ekranu na dole (na stanowisku HUD jest schowany, więc prawa kolumna jest wolna);
-- położenie z L.ukladUI (odswiezSkale), tu tylko rozmiary bazowe
local b = U.przycisk_px
local g = U.odstep_px
local START_POZ = UDim2.fromOffset(0, 0)
ui.krzyz = panel("SterowanieSila", 3 * b + 2 * g, 3 * b + 2 * g, START_POZ, Vector2.zero, "")
ui.blok = panel("SterowaniePancerz", U.blok_px, U.blok_px, START_POZ, Vector2.zero, "")
ui.stopaL = panel("SterowanieKondycjaL", U.stopa_px, U.stopa_px, START_POZ, Vector2.zero, "")
ui.stopaP = panel("SterowanieKondycjaP", U.stopa_px, U.stopa_px, START_POZ, Vector2.zero, "")
ui.unik = panel("SterowanieZrecznosc", U.unik_px, 2 * U.unik_px + 2 * g, START_POZ, Vector2.zero, "")
local r_ = U.runa_px
ui.runy = panel("SterowanieInteligencja", 3 * r_ + 2 * g, 3 * r_ + 2 * g, START_POZ, Vector2.zero, "")
ui.torL = panel("SterowanieSzczescieL", U.tor_px, U.tor_px, START_POZ, Vector2.zero, "")
ui.torP = panel("SterowanieSzczescieP", U.tor_px, U.tor_px, START_POZ, Vector2.zero, "")
-- Runy: postęp sekwencji (kropki) w lewym górnym rogu
ui.postep = panel("PostepRun", U.postep_px[1], U.postep_px[2], UDim2.fromOffset(8, 8), Vector2.zero)
-- panel w układzie (L.ukladUI) → ramka klienta
ui.wUkladzie = {
	status = ui.status, przerwij = ui.przerwij, krzyz = ui.krzyz, blok = ui.blok, stopaL = ui.stopaL,
	stopaP = ui.stopaP, unik = ui.unik, runy = ui.runy, postep = ui.postep, torL = ui.torL, torP = ui.torP,
}
zaokraglij(ui.postep, 10)
obrysuj(ui.postep, 2)
ui.kropki = {}
for i = 1, D.gry.inteligencja and D.gry.inteligencja.maks_dlugosc or 8 do
	local k = ramka(ui.postep, "Kropka" .. i, 16 + (i - 1) * 26, 15, 18, 18, KOL.szary)
	zaokraglij(k, 999)
	ui.kropki[i] = k
end

ui.panele = {
	sila = { ui.krzyz }, pancerz = { ui.blok }, kondycja = { ui.stopaL, ui.stopaP }, zrecznosc = { ui.unik },
	inteligencja = { ui.runy, ui.postep }, szczescie = { ui.torL, ui.torP },
}

-- panel startu (dół środka) i podpowiedź obrazkowa nad nim
ui.start = panel("Start", 400, 132, UDim2.new(0.5, 0, 1, -8), Vector2.new(0.5, 1))
zaokraglij(ui.start, 12)
obrysuj(ui.start, 3)
ui.opis = napis(ui.start, "Opis", "", "maly", 10, 4, 380, 40, KOL.tusz)
ui.podp = napis(ui.start, "Podpowiedz", T.start_podpowiedz, "maly", 10, 46, 380, 20, KOL.szary)
ui.obrazek = panel("Obrazek", U.obrazek_px[1], U.obrazek_px[2], UDim2.new(0.5, 0, 1, -156), Vector2.new(0.5, 1))
zaokraglij(ui.obrazek, 12)
obrysuj(ui.obrazek, 3)

-- podsumowanie rundy — karta w stylu wyniku walki: przy prawej krawędzi (lewa część ekranu zostaje dla postaci
-- w zbliżeniu po rundzie), lekko przekrzywiona, z pomarańczową wstęgą tytułu; liczby rosną od zera (stan.liczenie)
ui.koniec = panel("Podsumowanie", 400, 244, UDim2.new(1, -KX.karta.margines_px, 0.5, 0), Vector2.new(1, 0.5))
zaokraglij(ui.koniec, 14)
obrysuj(ui.koniec, 4)
ui.koniec.Rotation = KX.karta.obrot
ui.wstega = Instance.new("Frame")
ui.wstega.Name = "Wstega"
ui.wstega.Position = UDim2.fromOffset(-8, -12)
ui.wstega.Size = UDim2.fromOffset(416, 50)
ui.wstega.BackgroundColor3 = kolor(KX.kolory[KX.karta.wstega])
ui.wstega.BorderSizePixel = 0
ui.wstega.Rotation = KX.karta.wstega_obrot
zaokraglij(ui.wstega, 12)
obrysuj(ui.wstega, 4)
ui.wstega.Parent = ui.koniec
ui.kTytul = napis(ui.wstega, "Tytul", T.koniec, "duzy", 0, 6, 416, 38, KX.kolory[KX.karta.tytul])
ui.kTytul.FontFace = CZCIONKA_NAGLOWKA
obrysTekstu(ui.kTytul, 3)
-- wiersze nad przyrostem wyżej, przyrost niżej: kreski liter „Ś”, „Ć” w czcionce komiksowej wchodziły na wiersz serii
-- (próba w Studio 18.11.2026)
ui.k1 = napis(ui.koniec, "Trafienia", "", "sredni", 10, 46, 380, 24, KOL.tusz)
ui.k2 = napis(ui.koniec, "Seria", "", "sredni", 10, 70, 380, 24, KOL.tusz)
ui.k3 = napis(ui.koniec, "Przyrost", "", "seria", 10, 100, 380, 44, KX.kolory.zielony)
obrysTekstu(ui.k3, 3)
ui.k4 = napis(ui.koniec, "Sesja", "", "maly", 10, 142, 380, 32, KOL.szary)
local skalaKarty = ui.koniec:FindFirstChildOfClass("UIScale")

-- komunikat (odmowa)
ui.toast = panel("Komunikat", 380, 44, UDim2.new(0.5, 0, 0.3, 0), Vector2.new(0.5, 0.5))
zaokraglij(ui.toast, 10)
obrysuj(ui.toast, 2)
ui.toastTekst = napis(ui.toast, "Tekst", "", "sredni", 8, 4, 364, 36, KOL.tusz)

-- błysk ekranu (napisy odliczania i trafień rysuje warstwa komiksowa — napisKomiks niżej)
ui.blysk = Instance.new("Frame")
ui.blysk.Name = "Blysk"
ui.blysk.Size = UDim2.fromScale(1, 1)
ui.blysk.BackgroundColor3 = Color3.new(1, 1, 1)
ui.blysk.BackgroundTransparency = 1
ui.blysk.BorderSizePixel = 0
ui.blysk.Active = false
ui.blysk.Parent = gui

-- pierścienie Pancerza (cel stały + dwa zbiegające się) — w warstwie komiksowej, w miejscu, w które uderzy pięść
-- (rzut punktu ciosu na ekran co klatkę): wskazówka czasu jest tam, gdzie gracz patrzy na cios
ui.pierscienie = Instance.new("Frame")
ui.pierscienie.Name = "Pierscienie"
ui.pierscienie.AnchorPoint = Vector2.new(0.5, 0.5)
ui.pierscienie.Size = UDim2.fromOffset(64, 64)
ui.pierscienie.BackgroundTransparency = 1
ui.pierscienie.Visible = false
ui.pierscienie.Parent = warstwa
local skalaPierscieni = Instance.new("UIScale")
skalaPierscieni.Parent = ui.pierscienie
local celPierscienia = Instance.new("Frame")
celPierscienia.Name = "Cel"
celPierscienia.Size = UDim2.fromScale(1, 1)
celPierscienia.BackgroundTransparency = 1
zaokraglij(celPierscienia, 32)
obrysuj(celPierscienia, 4, KOL.krem)
celPierscienia.Parent = ui.pierscienie
local pierscienie = {}
for i = 1, 2 do
	local p = Instance.new("Frame")
	p.Name = "Pierscien" .. i
	p.AnchorPoint = Vector2.new(0.5, 0.5)
	p.Position = UDim2.fromScale(0.5, 0.5)
	p.Size = UDim2.fromScale(1, 1)
	p.BackgroundTransparency = 1
	p.Visible = false
	zaokraglij(p, 999)
	local s = obrysuj(p, 5, KOL.cios)
	p.Parent = ui.pierscienie
	pierscienie[i] = { ramka = p, obrys = s }
end

------------------------------------------------------------------ dźwięki: arkusz efektów (DzwiekGra) albo pliki wbudowane
local function graj(nazwa, szybkosc)
	local d = D.dzwieki[nazwa]
	if not d then
		return
	end
	local dzwiek = Instance.new("Sound")
	dzwiek.SoundId = "rbxasset://sounds/" .. d.plik
	dzwiek.Volume = d.glosnosc
	dzwiek.PlaybackSpeed = szybkosc or d.szybkosc
	dzwiek.Parent = gui
	dzwiek:Play()
	task.delay(d.maks or 2.5, function()
		dzwiek:Stop()
		dzwiek:Destroy()
	end)
end

local function melodia(nuty)
	for i, n in nuty do
		task.delay((i - 1) * D.dzwieki.odstep_melodii_s, function()
			graj("nuta", n)
		end)
	end
end

-- katalog arkusza efektów z pakietu swiat/dzwiek_gra (czytany raz; brak katalogu albo identyfikator 0 → false i dźwięk
-- wbudowany). Tylko zdarzenia zapisane w D.dzwieki_katalog (sprawdza je dane.py z ustawień pakietu dźwięku).
local DK = D.dzwieki_katalog
local katalog = nil -- false = sprawdzone, brak
local grajaceZArkusza = 0
local function arkusz()
	if katalog ~= nil then
		return katalog
	end
	katalog = false
	local k = workspace:FindFirstChild(DK.kontener)
	local m = k and k:FindFirstChild("Moduly")
	m = m and m:FindFirstChild(DK.modul)
	if not m or not m:IsA("ModuleScript") then
		return katalog
	end
	local ok, kat = pcall(require, m)
	if not ok or type(kat) ~= "table" or type(kat.arkusz) ~= "table" or type(kat.zdarzenia) ~= "table"
		or type(kat.efekty) ~= "table" then
		return katalog
	end
	local id = k:GetAttribute("TestArkuszId")
	if id == nil then
		id = kat.arkusz.id
	end
	local adres = nil
	if type(id) == "number" and id > 0 then
		adres = "rbxassetid://" .. tostring(math.floor(id))
	elseif type(id) == "string" and string.sub(id, 1, 18) == "rbxasset://sounds/" then
		adres = id
	end
	if adres then
		katalog = { kat = kat, adres = adres }
	end
	return katalog
end

local function grajZdarzenie(zdarzenie)
	if zdarzenie == nil or grajaceZArkusza >= DK.naraz then
		return false
	end
	local ark = arkusz()
	local zd = ark and ark.kat.zdarzenia[zdarzenie]
	local e = zd and ark.kat.efekty[zd.efekt]
	if not e or type(e.poczatek) ~= "number" or type(e.koniec) ~= "number" then
		return false
	end
	-- uderzenie: od chwili tuż przed atakiem efektu (szczyt od razu, efekt ma być natychmiast po naciśnięciu)
	local od = e.poczatek + (if zd.uderzenie then math.max(0, (e.atak or 0) - 0.03) else 0)
	local dzwiek = Instance.new("Sound")
	dzwiek.SoundId = ark.adres
	dzwiek.Volume = (e.glosnosc or 1) * (ark.kat.arkusz.glosnosc or 1)
	pcall(function()
		dzwiek.PlaybackRegionsEnabled = true
		dzwiek.PlaybackRegion = NumberRange.new(od, e.koniec)
	end)
	dzwiek.TimePosition = od
	dzwiek.Parent = gui
	dzwiek:Play()
	grajaceZArkusza += 1
	task.delay(e.koniec - od + 0.05, function()
		grajaceZArkusza -= 1
		dzwiek:Stop()
		dzwiek:Destroy()
	end)
	return true
end

------------------------------------------------------------------ efekty ekranu
local function pokazWidocznosc()
	-- panel rundy znika na podsumowaniu (jego miejsce zajmuje wstęga karty; czas i seria są już nieaktualne)
	ui.status.Visible = stan.gra ~= nil and stan.ekran ~= "podsumowanie"
	ui.start.Visible = stan.ekran == "stanowisko" and not stan.wybor
	ui.koniec.Visible = stan.ekran == "podsumowanie" and not stan.wybor
	-- przyciski mini-gry dopiero po odliczaniu (w czasie odliczania na ich miejscu jest podpowiedź obrazkowa)
	for gra, lista in ui.panele do
		for _, p in lista do
			p.Visible = stan.ekran == "runda" and stan.gra == gra and not stan.przedStartem
		end
	end
	ui.pierscienie.Visible = stan.ekran == "runda" and stan.gra == "pancerz" and not stan.przedStartem
	ui.przerwij.Visible = stan.ekran == "runda"
	ui.obrazek.Visible = stan.gra ~= nil and not stan.wybor
		and (stan.ekran == "stanowisko" or (stan.ekran == "runda" and stan.przedStartem))
	if ui.wybor then
		ui.wybor.Visible = stan.wybor
	end
	gui.Enabled = stan.gra ~= nil or stan.wybor or ui.toast.Visible
	guiKomiks.Enabled = stan.gra ~= nil
end

local licznikToastu = 0
local function komunikat(tekst)
	licznikToastu += 1
	local moj = licznikToastu
	ui.toastTekst.Text = tekst
	ui.toast.Visible = true
	pokazWidocznosc()
	task.delay(2.6, function()
		if moj == licznikToastu then
			ui.toast.Visible = false
			pokazWidocznosc()
		end
	end)
end

------------------------------------------------------------------ komiksowe napisy (styl walki)
-- obszar napisów w pikselach warstwy komiksowej (= piksele widoku kamery): prostokąt korzenia okien — ekran pod paskiem
-- Robloxa i między wycięciami telefonu albo emulowany telefon; skala = skala interfejsu. Ustawia odswiezSkale.
local uklad = { skala = 1, obszar = nil }

-- prostokąt panelu okien w pikselach warstwy komiksowej (położenia okien liczą się od końca paska Robloxa)
local function prostokatPanelu(p)
	local wstawka = GuiService:GetGuiInset()
	local a, r = p.AbsolutePosition, p.AbsoluteSize
	return { a.X + wstawka.X, a.Y + wstawka.Y, a.X + wstawka.X + r.X, a.Y + wstawka.Y + r.Y }
end

-- panele, na które napis nie może wejść: panel rundy, przerwanie, przyciski gry, podpowiedź, start, karta podsumowania
local function przeszkodyNapisow()
	local lista = {}
	local function dodaj(p)
		if p and p.Visible then
			table.insert(lista, prostokatPanelu(p))
		end
	end
	for _, p in { ui.status, ui.przerwij, ui.obrazek, ui.start, ui.koniec, ui.wybor } do
		dodaj(p)
	end
	for _, p in (stan.gra and ui.panele[stan.gra]) or {} do
		dodaj(p)
	end
	return lista
end

local function punktEkranu(p)
	local v = workspace.CurrentCamera:WorldToViewportPoint(p)
	return v.X, v.Y, v.Z > 0
end

--[[ Komiksowy napis. punkt = miejsce w świecie (Vector3), przy którym ma wyskoczyć — rzut na ekran w chwili pokazania
	(w rundzie kamera stoi); nil = miejsce dużych napisów stanowiska (D.swiat[gra].napis, ułamki obszaru). opcje: kolor
	(nazwa z ui.komiks.kolory), przesun (Vector2 — piksele bazowe od punktu), ekran (Vector2 — gotowe miejsce
	w pikselach warstwy), gwiazda, obrot. Napis nie wychodzi poza obszar okien i schodzi z paneli. ]]
local function napisKomiks(tekst, styl, punkt, opcje)
	local o = uklad.obszar
	if o == nil then
		return nil
	end
	opcje = opcje or {}
	local n = (stan.gra and D.swiat[stan.gra].napis) or { 0.5, 0.3 }
	local x, y = o[1] + (o[3] - o[1]) * n[1], o[2] + (o[4] - o[2]) * n[2]
	if opcje.ekran then
		x, y = opcje.ekran.X, opcje.ekran.Y -- gotowe miejsce na ekranie (napis nad postacią w zbliżeniu po rundzie)
	elseif punkt then
		local px, py, widac = punktEkranu(punkt)
		if widac then
			x, y = px, py
			if opcje.przesun then
				x += opcje.przesun.X * uklad.skala
				y += opcje.przesun.Y * uklad.skala
			end
		end
	end
	-- w miejscu dużych napisów stoi jedno słowo naraz: nowe zastępuje poprzednie („+1 Pancerz!” i zaraz „SERIA 10!”
	-- nakładały się na siebie — próba w Studio 18.11.2026)
	local wMiejscu = not opcje.ekran and not punkt
	if wMiejscu and stan.duzyNapis then
		komiks:usun(stan.duzyNapis)
		stan.duzyNapis = nil
	end
	local wpis = komiks:napis(tekst, styl, x, y, {
		kolor = opcje.kolor, gwiazda = opcje.gwiazda, obrot = opcje.obrot, zycie = stan.dlugieNapisy,
		skala = uklad.skala, obszar = o, przeszkody = przeszkodyNapisow(),
	})
	if wMiejscu then
		stan.duzyNapis = wpis
	end
	return wpis
end

local function blysk(przezr, h)
	ui.blysk.BackgroundColor3 = kolor(h or "FFFFFF")
	ui.blysk.BackgroundTransparency = przezr
	TweenService:Create(ui.blysk, TweenInfo.new(0.18), { BackgroundTransparency = 1 }):Play()
end

local function podskokSerii()
	skalaSerii.Scale = 1.3
	TweenService:Create(skalaSerii, TweenInfo.new(0.18, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

------------------------------------------------------------------ kamera stanowiska (ujęcia jak w walce; rachunek: KameraTreningu)
-- uj: "stanowisko" (przed rundą) | "odliczanie" (dojazd) | "gra" (stoi) | "final" (zbliżenie na postać po rundzie)
local kam = {
	uj = "stanowisko", start = 0, od = nil, przejscie = 0, przejscieStart = 0, ostatnie = nil,
	wstrzasSila = 0, wstrzasWiek = 0, zawezenia = {}, przed = nil,
}

local function ujecie(nazwa, przejscie)
	if kam.uj == nazwa then
		return
	end
	-- płynne przejście od ostatniego kadru (albo cięcie, gdy przejscie = 0)
	kam.od = if przejscie and przejscie > 0 then kam.ostatnie else nil
	kam.przejscie = przejscie or 0
	kam.przejscieStart = os.clock()
	kam.uj = nazwa
	kam.start = os.clock()
end

-- drżenie kamery: gaśnie wykładniczo; nowe nie jest słabsze od tego, co jeszcze nie zgasło (jak w walce)
local function wstrzas(sila)
	kam.wstrzasSila = math.max(Kam.wstrzas(D, kam.wstrzasSila, kam.wstrzasWiek), sila)
	kam.wstrzasWiek = 0
end

-- krótkie zawężenie kąta widzenia („wciśnięcie” kadru) po trafieniu: "uderzenie" | "mocne" | "seria"
local function zawezenie(rodzaj)
	kam.zawezenia[rodzaj] = os.clock()
end

------------------------------------------------------------------ lokalne obiekty 3D (tylko u tego gracza)
local efekty = Instance.new("Folder")
efekty.Name = "TreningProbaEfekty"
efekty.Parent = workspace.CurrentCamera

-- efekty trafień w języku walki i konfetti (Moduly/EfektyTreningu). Zestaw powstaje przy wejściu na stanowisko —
-- wtedy sprawdzamy, czy w miejscu stoi moduł efektów walki (jest → iskry, rozbłyski, fale i łuk odbicia z niego,
-- nie ma → własne); atrybut kontenera EfektyWlasne = true wymusza własne (próba w Studio). Znika przy zejściu.
local fx = nil
local function efektyStanowiska()
	if fx == nil then
		fx = Efekty.dlaTreningu(efekty, EF, kontener:GetAttribute("EfektyWlasne") == true)
	end
	return fx
end

local function sprzatnijEfekty()
	if fx then
		fx:wyczysc()
		fx = nil
	end
	komiks:wyczysc()
	stan.duzyNapis = nil
end

local function wybuch(nazwa, punkt, skala)
	if fx and punkt then
		fx:wybuch(nazwa, punkt, (skala or 1) * EF.skala)
	end
end

local function fala(punkt, h, promien)
	if fx and punkt then
		fx:fala(punkt, kolor(h), promien)
	end
end

local function czesc(nazwa, rozmiar, h, material, ksztalt)
	local obj = Instance.new("Part")
	obj.Name = nazwa
	obj.Anchored = true
	obj.CanCollide = false
	obj.CanQuery = false
	obj.CanTouch = false
	obj.Size = rozmiar
	obj.Color = kolor(h)
	obj.Material = material or Enum.Material.SmoothPlastic
	if ksztalt then
		obj.Shape = ksztalt
	end
	obj.TopSurface = Enum.SurfaceType.Smooth
	obj.BottomSurface = Enum.SurfaceType.Smooth
	return obj
end

local function odlamki(pozycja, h, n, rozrzut)
	for _ = 1, n do
		local obj = czesc("Odlamek", Vector3.new(0.45, 0.45, 0.45), h)
		obj.CFrame = CFrame.new(pozycja) * CFrame.Angles(losowe:NextNumber(0, 6), losowe:NextNumber(0, 6), 0)
		obj.Parent = efekty
		local kier = Vector3.new(losowe:NextNumber(-1, 1), losowe:NextNumber(0.2, 1.2), losowe:NextNumber(-1, 1)).Unit
		TweenService:Create(obj, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			CFrame = CFrame.new(pozycja + kier * (rozrzut or 3)) * CFrame.Angles(losowe:NextNumber(0, 6), 2, 1),
			Transparency = 1, Size = Vector3.new(0.15, 0.15, 0.15),
		}):Play()
		task.delay(0.5, function()
			obj:Destroy()
		end)
	end
end

local function obrysModelu(rodzic)
	local h = Instance.new("Highlight")
	h.FillTransparency = 1
	h.OutlineColor = kolor(KOL.tusz)
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Parent = rodzic
end

-- model z części: { nazwa, rozmiar, kolor, przesunięcie, materiał?, kształt? } — pierwsza część to PrimaryPart
local function modelZCzesci(nazwa, lista)
	local model = Instance.new("Model")
	model.Name = nazwa
	for i, c in lista do
		local obj = czesc(c[1], c[2], c[3], c[5], c[6])
		obj.CFrame = CFrame.new(c[4] or Vector3.zero)
		obj.Parent = model
		if i == 1 then
			model.PrimaryPart = obj
		end
	end
	model.Parent = efekty
	return model
end

-- miecz (Siła), tarcza (Pancerz), koszyk (Szczęście): modele przesuwane PivotTo
local modelGracza = nil
local smugaMiecza = nil -- Trail na ostrzu (smuga ciosu jak za bronią w walce), włączana na czas machnięcia
local function zbudujMiecz()
	local model = modelZCzesci("Miecz", {
		{ "Rekojesc", Vector3.new(0.35, 1.1, 0.35), "6B4A2F" },
		{ "Jelec", Vector3.new(1.4, 0.3, 0.45), KOL.zloto, Vector3.new(0, 0.7, 0) },
		{ "Ostrze", Vector3.new(0.25, 3.6, 0.7), "D8DEE9", Vector3.new(0, 2.65, 0), Enum.Material.Metal },
	})
	obrysModelu(model)
	local ostrze = model:FindFirstChild("Ostrze")
	if ostrze then
		-- smuga tylko za końcową częścią ostrza i mocno przezroczysta: pełna szerokość ostrza dawała przy machnięciu
		-- biały wachlarz, który na chwilę zasłaniał strefę (próba w Studio 18.11.2026)
		local a0 = Instance.new("Attachment")
		a0.Position = Vector3.new(0, 0.5, 0)
		a0.Parent = ostrze
		local a1 = Instance.new("Attachment")
		a1.Position = Vector3.new(0, 1.8, 0)
		a1.Parent = ostrze
		local slad = Instance.new("Trail")
		slad.Name = "Smuga"
		slad.Attachment0 = a0
		slad.Attachment1 = a1
		slad.Lifetime = 0.14
		slad.Color = ColorSequence.new(kolor(KX.kolory.bialy), kolor(KX.kolory.zolty))
		slad.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.5), NumberSequenceKeypoint.new(1, 1) })
		slad.LightEmission = 0.6
		slad.FaceCamera = true
		slad.MinLength = 0.05
		slad.Enabled = false
		slad.Parent = ostrze
		smugaMiecza = slad
	end
	return model
end

local function zbudujTarcze()
	local model = modelZCzesci("Tarcza", {
		{ "Plyta", Vector3.new(2.6, 2.9, 0.35), KOLOR_GRY.pancerz },
		{ "Rama", Vector3.new(2.95, 3.25, 0.25), KOL.zloto, Vector3.new(0, 0, -0.12) },
		{ "Guz", Vector3.new(0.9, 0.9, 0.9), KOL.zloto, Vector3.new(0, 0, -0.25), nil, Enum.PartType.Ball },
	})
	obrysModelu(model)
	return model
end

local function zbudujKoszyk()
	local model = modelZCzesci("Koszyk", {
		{ "Dno", Vector3.new(2.6, 0.2, 2.0), KOL.drewno, Vector3.new(0, -0.5, 0), Enum.Material.WoodPlanks },
		{ "ScianaL", Vector3.new(0.15, 1.0, 2.0), "A86B3C", Vector3.new(-1.25, 0, 0), Enum.Material.WoodPlanks },
		{ "ScianaP", Vector3.new(0.15, 1.0, 2.0), "A86B3C", Vector3.new(1.25, 0, 0), Enum.Material.WoodPlanks },
		{ "ScianaT", Vector3.new(2.6, 1.0, 0.15), "A86B3C", Vector3.new(0, 0, -0.95), Enum.Material.WoodPlanks },
		{ "ScianaF", Vector3.new(2.6, 1.0, 0.15), "A86B3C", Vector3.new(0, 0, 0.95), Enum.Material.WoodPlanks },
	})
	obrysModelu(model)
	return model
end

------------------------------------------------------------------ części areny animowane lokalnie (zmiany widzi tylko ten gracz)
local arena = {}
local function zapamietaj(o)
	return { obj = o, cf = o.CFrame, kolor = o.Color, przezr = o.Transparency, material = o.Material }
end

local function zapamietajArene()
	local function z(nazwa)
		local o = sciezka(kontener, nazwa)
		if o and o:IsA("BasePart") then
			return zapamietaj(o)
		end
		return nil
	end
	local function dzieci(nazwa, przedrostek)
		local wynik = {}
		local f = sciezka(kontener, nazwa)
		if f then
			for _, c in f:GetChildren() do
				if c:IsA("BasePart") and (przedrostek == nil or string.sub(c.Name, 1, #przedrostek) == przedrostek) then
					wynik[c.Name] = zapamietaj(c)
				end
			end
		end
		return wynik
	end
	arena.ramie = z(D.nazwy.miotacz_ramie)
	arena.piesc = z(D.nazwy.golem_piesc)
	arena.oczy = {}
	for _, n in D.nazwy.golem_oczy do
		table.insert(arena.oczy, z(n))
	end
	arena.strefy = dzieci(D.nazwy.strefy)
	arena.pasy = dzieci(D.nazwy.tasma_pasy, "Pas")
	arena.cele = dzieci(D.nazwy.cele_stop)
	arena.beben = z(D.nazwy.beben)
	arena.palka = z(D.nazwy.palka)
	arena.podestKlody = z(D.nazwy.podest_klody)
	local m = sciezka(kontener, D.nazwy.ramie_klody)
	arena.klody = if m and m:IsA("Model") then { obj = m, cf = m:GetPivot() } else nil
	arena.runy = {}
	local f = sciezka(kontener, D.nazwy.runy)
	if f then
		for _, k in (D.gry.inteligencja and D.gry.inteligencja.runy or {}) do
			local rm = f:FindFirstChild(k)
			if rm then
				local w = { znaki = {} }
				for _, c in rm:GetChildren() do
					if c:IsA("BasePart") and string.sub(c.Name, 1, 4) == "Znak" then
						table.insert(w.znaki, zapamietaj(c))
					elseif c:IsA("BasePart") and c.Name == "Kamien" then
						w.kamien = zapamietaj(c)
					end
				end
				arena.runy[k] = w
			end
		end
	end
	arena.kula = z(D.nazwy.kula_maga)
	arena.tory = dzieci(D.nazwy.tory)
end

local function przywrocCzesc(w)
	if w and w.obj.Parent then
		w.obj.CFrame = w.cf
		w.obj.Color = w.kolor
		w.obj.Transparency = w.przezr
		w.obj.Material = w.material
	end
end

local function przywrocArene()
	for _, w in { arena.ramie, arena.piesc, arena.beben, arena.palka, arena.kula, arena.podestKlody } do
		przywrocCzesc(w)
	end
	for _, lista in { arena.oczy or {}, arena.strefy or {}, arena.pasy or {}, arena.cele or {}, arena.tory or {} } do
		for _, w in lista do
			przywrocCzesc(w)
		end
	end
	for _, w in arena.runy or {} do
		przywrocCzesc(w.kamien)
		for _, z in w.znaki do
			przywrocCzesc(z)
		end
	end
	if arena.klody and arena.klody.obj.Parent then
		arena.klody.obj:PivotTo(arena.klody.cf)
	end
end

local function swiec(w, h, przezr, neon)
	if w and w.obj.Parent then
		w.obj.Color = kolor(h)
		w.obj.Transparency = przezr or w.przezr
		w.obj.Material = if neon then Enum.Material.Neon else w.material
	end
end

------------------------------------------------------------------ bohater klasy (haczyk innego pakietu) albo awatar
--[[ Gdy w miejscu działa bohater klasy, awatar gracza jest schowany, a zamiast niego widać model bohatera. Jego ruchy
	na stanowisku idą przez BindableFunction u klienta (ścieżka w Workspace z D.ui.bohater.sciezka):
		Invoke("stan")                    → nil (brak aktywnego bohatera) albo { aktywny = true, klasa = …, klip = bieżący
		                                    tryb ruchu, wymuszony = nazwa wymuszonego klipu albo brak }
		Invoke("klip", nazwa | nil)       wymusza pozę / klip: bieg, skok, padnij, rece_gora, radosc (wiwat raz, potem
		                                    spoczynek — każde wywołanie gra go od nowa); nil = ruch samoczynny;
		                                    → true / false (false: nieznana nazwa albo brak bohatera)
		Invoke("przesun", Vector3 | nil)  przesunięcie bohatera względem postaci (X w prawo, Y w górę, −Z do przodu),
		                                    od razu, bez wygładzania (podskok rysujemy klatka po klatce); nil = bez.
		                                    Poza „padnij” sama opuszcza biodra — przy niej bez przesunięcia w dół
	Każde wywołanie jest osłonięte: obiektu może nie być, funkcja może nie mieć obsługi (Invoke czekałby bez końca,
	więc wołamy w osobnym wątku i liczy się tylko odpowiedź dana od razu) albo zgłosić błąd — wtedy zostaje awatar.
	Awatar chowa pakiet bohatera (przez Transparency), a bohater przejmuje LocalTransparencyModifier awatara — więc
	półprzezroczystość postaci w Sile działa bez zmian także na bohaterze. ]]
local hak = {
	niedostepnyDo = 0, zawieszony = false, aktywny = false, sprawdzono = -math.huge, klip = nil, odrzucony = nil,
	przesuniety = false, wywolania = 0,
}

local function wolajBohatera(polecenie, arg)
	if hak.zawieszony or os.clock() < hak.niedostepnyDo then
		return nil, false
	end
	-- ścieżka z danych; atrybut kontenera HaczykBohatera (napis) podmienia ją na czas próby w Studio
	local gdzie = kontener:GetAttribute("HaczykBohatera")
	local f = sciezka(workspace, if type(gdzie) == "string" and gdzie ~= "" then gdzie else BH.sciezka)
	if not f or not f:IsA("BindableFunction") then
		hak.niedostepnyDo = os.clock() + BH.ponow_po_s
		return nil, false
	end
	local wynik, gotowe, blad = nil, false, false
	task.spawn(function()
		local ok, w = pcall(f.Invoke, f, polecenie, arg)
		if ok then
			wynik = w
		else
			blad = true
		end
		gotowe = true
	end)
	hak.wywolania += 1
	if not gotowe then
		-- brak obsługi po drugiej stronie (Invoke czeka): nie pytamy więcej do następnego wejścia na stanowisko
		hak.zawieszony = true
		return nil, false
	end
	if blad then
		hak.niedostepnyDo = os.clock() + BH.ponow_po_s
		return nil, false
	end
	return wynik, true
end

-- czy lokalny gracz ma aktywnego bohatera klasy (odpowiedź pamiętana przez odswiez_s)
local function bohaterAktywny()
	local c = os.clock()
	if c - hak.sprawdzono < BH.odswiez_s then
		return hak.aktywny
	end
	hak.sprawdzono = c
	local w, ok = wolajBohatera("stan", nil)
	local aktywny = ok and type(w) == "table" and w.aktywny == true
	if not aktywny then
		hak.klip = nil
		hak.przesuniety = false
	elseif hak.klip ~= nil then
		-- czy nasz wymuszony klip dalej obowiązuje (bohater zeruje go przy odrodzeniu postaci): pole „wymuszony”,
		-- a gdyby go nie było — nazwa bieżącego klipu
		local wymuszony = w.wymuszony
		if wymuszony == nil then
			wymuszony = w.klip
		end
		if wymuszony ~= hak.klip then
			hak.klip = nil -- następne żądanie pójdzie jeszcze raz
		end
	end
	hak.odrzucony = nil
	hak.aktywny = aktywny
	return aktywny
end

-- wymuszony klip bohatera (nil = sam). Haczyk odpowiada true / false (false: nieznana nazwa albo brak bohatera) —
-- odrzuconej nazwy nie powtarzamy co klatkę, tylko po następnym odświeżeniu stanu
local function klipBohatera(nazwa)
	if hak.klip == nazwa or (nazwa ~= nil and hak.odrzucony == nazwa) then
		return
	end
	local w, ok = wolajBohatera("klip", nazwa)
	if ok and w ~= false then
		hak.klip = nazwa
	elseif ok then
		hak.odrzucony = nazwa
	end
end

local function przesunBohatera(v)
	if v == nil and not hak.przesuniety then
		return
	end
	local _, ok = wolajBohatera("przesun", v)
	if ok then
		hak.przesuniety = v ~= nil
	end
end

-- bohater wraca do zwykłego zachowania (koniec rundy, zejście ze stanowiska)
local function spokojBohatera()
	if hak.aktywny or hak.klip ~= nil or hak.przesuniety then
		klipBohatera(nil)
		przesunBohatera(nil)
	end
end

------------------------------------------------------------------ postać gracza (tylko u siebie: nic nie idzie na serwer)
local przezroczystoscTeraz = 0
local function przezroczystoscPostaci(v)
	local postac = gracz.Character
	if not postac or (v == przezroczystoscTeraz) then
		return
	end
	-- (przy aktywnym bohaterze klasy awatar jest niewidoczny przez Transparency, a bohater przejmuje ten
	-- LocalTransparencyModifier — półprzezroczystość działa więc na to, co gracz widzi)
	przezroczystoscTeraz = v
	for _, d in postac:GetDescendants() do
		if d:IsA("BasePart") or d:IsA("Decal") then
			d.LocalTransparencyModifier = v
		end
	end
end

-- staw biodra (Motor6D z Part0 = HumanoidRootPart; R15 i R6): skok / padnij / uderzenie kłody i barki (koszyk nad
-- głową) — przesunięcie C0 tylko w tym kliencie; oryginalne C0 wraca przy końcu rundy, zejściu i odrodzeniu
-- Dwa rodzaje stawów awatara: Motor6D (pozycja stawu = C0) i AnimationConstraint z nowych awatarów Robloxa (próba
-- 18.11.2026: w tym miejscu awatar R15 ma 15 AnimationConstraint i 0 Motor6D — pozycja stawu = CFrame jego Attachment0)
local stawy = {} -- obiekt (Motor6D albo Attachment0) → poza oryginalna
local znaneStawy = {} -- nazwa ("" = biodro) → obiekt albo false (szukane raz na postać)
local function poza(o)
	if o:IsA("Motor6D") then
		return o.C0
	end
	return o.CFrame
end

local function ustawPoze(o, cf)
	if o:IsA("Motor6D") then
		o.C0 = cf
	else
		o.CFrame = cf
	end
end

local function staw(nazwa)
	local postac = gracz.Character
	local klucz = nazwa or ""
	local j = znaneStawy[klucz]
	if j and j.Parent and postac and j:IsDescendantOf(postac) then
		return j
	end
	if j == false then
		return nil
	end
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp then
		return nil
	end
	znaneStawy[klucz] = false
	for _, d in postac:GetDescendants() do
		local cel = nil
		if d:IsA("Motor6D") and ((nazwa == nil and d.Part0 == hrp) or d.Name == nazwa) then
			cel = d
		elseif d:IsA("AnimationConstraint") and d.Attachment0
			and ((nazwa == nil and d.Attachment0.Parent == hrp) or d.Name == nazwa) then
			cel = d.Attachment0
		end
		if cel then
			if stawy[cel] == nil then
				stawy[cel] = poza(cel)
			end
			znaneStawy[klucz] = cel
			return cel
		end
	end
	return nil
end

local function ustawStaw(nazwa, cf)
	local j = staw(nazwa)
	if j then
		ustawPoze(j, cf * stawy[j])
	end
end

local function ustawStawLokalnie(nazwa, cf)
	local j = staw(nazwa)
	if j then
		ustawPoze(j, stawy[j] * cf)
	end
end

local function przywrocStawy()
	for j, c0 in stawy do
		if j.Parent then
			ustawPoze(j, c0)
		end
	end
	table.clear(stawy)
	table.clear(znaneStawy)
end

-- animacja z domyślnego skryptu Animate postaci (bez wgrywania animacji): "run" — bieg na taśmie, "cheer" — radość
local function animacjaAwatara(nazwa)
	local postac = gracz.Character
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	local animator = hum and hum:FindFirstChildOfClass("Animator")
	local a = postac and postac:FindFirstChild("Animate")
	local grupa = a and a:FindFirstChild(nazwa)
	local anim = grupa and grupa:FindFirstChildOfClass("Animation")
	if not animator or not anim then
		return nil
	end
	local ok, tr = pcall(function()
		return animator:LoadAnimation(anim)
	end)
	if ok and tr then
		tr.Priority = Enum.AnimationPriority.Action
		tr.Looped = true
		return tr
	end
	return nil
end

-- bieg na taśmie: bohater klasy — klip biegu przez haczyk; awatar — animacja biegu z Animate (brak — tylko podskakuje)
local bieg = nil -- ścieżka animacji biegu awatara
local function zatrzymajBieg()
	if bieg then
		pcall(function()
			bieg:Stop(0.2)
		end)
		bieg = nil
	end
end

local function zacznijBieg(predkosc)
	if bohaterAktywny() then
		zatrzymajBieg()
		klipBohatera(BH.klipy.bieg)
		return
	end
	if bieg then
		pcall(function()
			bieg:AdjustSpeed(predkosc)
		end)
		return
	end
	local tr = animacjaAwatara("run")
	if tr then
		tr:Play(0.15, 1, predkosc)
		bieg = tr
	end
end

-- radość po rundzie z punktem statystyki: bohater klasy — klip radości; awatar — animacja „cheer” z Animate, a gdy
-- jej nie ma — ręce w górę i podskoki (stawy tylko u siebie, w wyglad())
local radosc = nil -- ścieżka animacji radości awatara
local function zatrzymajRadosc()
	if radosc then
		pcall(function()
			radosc:Stop(0.2)
		end)
		radosc = nil
	end
	stan.radosc = nil
end

local function zacznijRadosc()
	zatrzymajRadosc()
	stan.radosc = os.clock()
	if bohaterAktywny() then
		stan.radoscBohatera = os.clock()
		klipBohatera(BH.klipy.radosc)
		return "bohater"
	end
	local tr = animacjaAwatara("cheer")
	if tr then
		tr:Play(0.15, 1, 1)
		radosc = tr
		return "animacja"
	end
	return "stawy"
end

-- Koniczyny: postać przechodzi między torami (PivotTo w kliencie, który i tak steruje fizyką swojej postaci)
local function punktToru(k)
	local G = D.gry.szczescie
	return v3(D.swiat.szczescie.tory[G.tory[k]])
end

local function ustawTor(k, odRazu)
	stan.tor = k
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp then
		return
	end
	local cel = punktToru(k)
	cel = Vector3.new(cel.X, hrp.Position.Y, cel.Z)
	if odRazu then
		stan.ruchToru = nil
		postac:PivotTo(CFrame.new(cel) * hrp.CFrame.Rotation)
		hrp.AssemblyLinearVelocity = Vector3.zero
	else
		stan.ruchToru = { od = hrp.Position, ["do"] = cel, t = os.clock() }
	end
end

------------------------------------------------------------------ wizualizacja zdarzeń rundy
local wizualne = {} -- nr → { obj, … }

local function usunWizualne()
	for _, v in wizualne do
		if v.obj then
			local obj = v.obj
			v.obj = nil
			obj:Destroy()
		end
		if v.cien then
			local obj = v.cien
			v.cien = nil
			obj:Destroy()
		end
	end
	wizualne = {}
end

-- Lecące cele Siły to owoce (D-108: „przecinanie owoców w lesie”) — SAM WYGLĄD: tor lotu, strefy, okna czasu i werdykty
-- liczy ta sama logika co dotąd. Owoc = kula w barwie skórki + dodatki (ogonek, listek, pasek), które jadą za nią;
-- przy trafieniu rozpada się na dwie połówki w barwie miąższu i cząstki skórki.
local OWOCE = {
	{ nazwa = "Dynia", sr = 1.7, skorka = "F08A24", miazsz = "FFC25A" },
	{ nazwa = "Jablko", sr = 1.5, skorka = "E5392B", miazsz = "FFF1C9" },
	{ nazwa = "Arbuz", sr = 1.9, skorka = "2E8B3D", miazsz = "FF5A6E" },
	{ nazwa = "Gruszka", sr = 1.4, skorka = "C9D64A", miazsz = "FFF6C9" },
}
local function nowyPrzedmiot(nr)
	local o = OWOCE[nr % #OWOCE + 1]
	local obj = czesc(o.nazwa, Vector3.one * o.sr, o.skorka, nil, Enum.PartType.Ball)
	local dodatki = {}
	local function dodatek(nazwa, rozmiar, h, przes, ksztalt)
		local d = czesc(nazwa, rozmiar, h, nil, ksztalt)
		d.Parent = obj
		table.insert(dodatki, { d, przes })
	end
	local r = o.sr / 2
	if o.nazwa == "Dynia" then
		dodatek("Ogonek", Vector3.new(0.32, 0.45, 0.32), "3F8F35", CFrame.new(0, r + 0.12, 0))
	elseif o.nazwa == "Jablko" then
		dodatek("Ogonek", Vector3.new(0.14, 0.4, 0.14), "6B4A2F", CFrame.new(0, r + 0.12, 0))
		dodatek("Listek", Vector3.new(0.55, 0.1, 0.3), "3F8F35", CFrame.new(0.3, r + 0.2, 0) * CFrame.Angles(0, 0, math.rad(-20)))
	elseif o.nazwa == "Arbuz" then
		dodatek("Pasek", Vector3.new(0.5, o.sr + 0.04, o.sr + 0.04), "7CCB5A", CFrame.new(), Enum.PartType.Cylinder)
	else
		dodatek("Czubek", Vector3.one * 0.95, o.skorka, CFrame.new(0, r + 0.2, 0), Enum.PartType.Ball)
		dodatek("Ogonek", Vector3.new(0.14, 0.4, 0.14), "6B4A2F", CFrame.new(0, r + 0.85, 0))
	end
	obrysModelu(obj)
	obj.Parent = efekty
	return obj, dodatki, o
end

local function polowkiOwocu(pozycja, o)
	odlamki(pozycja, o.skorka, 5, 3.5)
	odlamki(pozycja, o.miazsz, 4, 3.0)
	for _, znak in { -1, 1 } do
		local obj = czesc("Polowka", Vector3.one * o.sr * 0.62, o.miazsz, nil, Enum.PartType.Ball)
		obj.CFrame = CFrame.new(pozycja + Vector3.new(znak * 0.4, 0, 0))
		obj.Parent = efekty
		TweenService:Create(obj, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			CFrame = CFrame.new(pozycja + Vector3.new(znak * 2.6, 1.2, 0)) * CFrame.Angles(znak * 2, 1, 0),
			Transparency = 1,
		}):Play()
		task.delay(0.55, function()
			obj:Destroy()
		end)
	end
end

-- Gest trenera NPC (pakiet swiat/npc_gra, gdy stoi w miejscu): w chwili ruchu ręki figury z klocków wołamy krótki klip
-- „akcja” postaci (rzut miotacza trwa u nas 0,41 s, uderzenie pałką trenera Bieżni 0,28 s),
-- która ją zastępuje. Osłonięte i w osobnym wątku — bez pakietu NPC nic się nie zmienia; dopóki poprzednie wywołanie nie
-- wróciło (funkcja bez obsługi czekałaby bez końca), kolejnych nie wysyłamy, więc wisieć może najwyżej jeden wątek.
local gestWToku = false
local function gestTrenera(klucz)
	if gestWToku then
		return
	end
	local npc = workspace:FindFirstChild("NpcGra")
	local s = npc and npc:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild("Polecenie")
	if not (f and f:IsA("BindableFunction")) then
		return
	end
	gestWToku = true
	task.spawn(function()
		pcall(function()
			f:Invoke("graj", klucz, "akcja")
		end)
		gestWToku = false
	end)
end

local function machnij(w, kat, wznies, opusc)
	if not w or not w.obj.Parent then
		return
	end
	local bark = w.cf * CFrame.new(0, w.obj.Size.Y / 2 - 0.1, 0)
	local gora = bark * CFrame.Angles(kat, 0, 0) * CFrame.new(0, -(w.obj.Size.Y / 2 - 0.1), 0)
	TweenService:Create(w.obj, TweenInfo.new(wznies), { CFrame = gora }):Play()
	task.delay(wznies + 0.04, function()
		TweenService:Create(w.obj, TweenInfo.new(opusc), { CFrame = w.cf }):Play()
	end)
end

local function bezier(a, H, C, Z)
	local q = 1 - a
	return H * (q * q) + C * (2 * q * a) + Z * (a * a)
end

local function tekstTrafienia(seria, lista)
	local i = math.min(#lista, 1 + math.floor(seria / 5))
	return lista[i]
end

-- mnożnik serii dla następnego trafienia (jednostki paska względem trafienia bez serii)
local function mnoznikSerii(seria)
	return L.przyrost(D, seria + 1) / L.przyrost(D, 1)
end

local function odswiezStatus()
	local R = stan.R
	local seria = if R then R.seria else 0
	local suma = if R then R.suma else 0
	ui.seria.Text = string.format("SERIA %d", seria)
	ui.mnoznik.Text = string.format("×%.2f", mnoznikSerii(seria))
	stan.sumaRundy = suma -- punkty w rundzie: napis „+1 Siła!” w chwili zdobycia i podsumowanie (zwarty panel ich nie ma)
	local pasek, prog = 0, 1
	if R then
		pasek, prog = R.pasek, L.prog(D, R.W, R.pula)
	end
	ui.wypelnienie.Size = UDim2.fromScale(math.clamp(pasek / math.max(prog, 1e-6), 0, 1), 1)
end

local function rzadPoziomu(G, t, Rd)
	return G.poziomy[L.poziom(G, t - Rd.t0)]
end

-- punkt na ziemi pod postacią gracza (fale, konfetti) i jej pierś (napisy, wybuch przy oberwaniu)
local function stopyPostaci()
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if hrp then
		return hrp.Position - Vector3.new(0, KA.final.korzen_nad_ziemia, 0)
	end
	return if stan.gra then v3(D.swiat[stan.gra].podest) else nil
end

local function piersPostaci()
	local p = stopyPostaci()
	return if p then p + Vector3.new(0, 3.4, 0) else nil
end

--[[ Mini-gry: rysowanie stanowisk w czasie rundy. Każda gra może mieć:
	akcja(wartosc)      — ruch po naciśnięciu (miecz, tarcza, skok…)
	miejsce(w) → Vector3 — gdzie w świecie padł werdykt: tam idzie wybuch w języku walki i (domyślnie) słowo
	napis(w) → Vector3, Vector2 — inne miejsce słowa i przesunięcie w pikselach bazowych (żeby nie zasłaniało pola gry)
	efekt(w, m)         — dodatki tej gry (odłamki skrzynki, łuk odbicia, czerwony błysk przy oberwaniu…)
	klatka(t, Rd, W)    — rysowanie co klatkę ]]
local GRY = {}

-- Siła „Rozbijanie”: miotacz rzuca skrzynki łukiem do czterech stref; strefa w oknie świeci
GRY.sila = {
	akcja = function(wartosc)
		if KATY[wartosc] ~= nil then
			stan.miecz = { t = os.clock(), k = wartosc }
			graj("swist")
		end
	end,
	miejsce = function(w)
		local v = w.nr and wizualne[w.nr]
		if v and v.obj then
			return v.obj.Position
		end
		local strefa = w.wartosc and D.swiat.sila.strefy[w.wartosc]
		return if strefa then v3(strefa) else nil
	end,
	napis = function(_)
		return nil, Vector2.new(0, -34)
	end,
	efekt = function(w)
		if w.trafienie then
			local v = wizualne[w.nr]
			if v and v.obj then
				if v.owoc then
					polowkiOwocu(v.obj.Position, v.owoc)
				else
					odlamki(v.obj.Position, v.obj.Color:ToHex(), 9, 3.5)
				end
				local obj = v.obj
				v.obj = nil
				obj:Destroy()
			end
			wstrzas(0.12)
		end
	end,
	klatka = function(t, Rd, W)
		if modelGracza then
			local spoczynek = CFrame.new(v3(W.miecz)) * CFrame.Angles(math.rad(25), 0, math.rad(-20))
			local cf = spoczynek
			local macha = false
			if stan.miecz then
				local dt = os.clock() - stan.miecz.t
				if dt < 0.34 then
					macha = true
					local piers = v3(W.podest) + Vector3.new(0.8, 3.4, -0.4)
					local cios = CFrame.lookAt(piers, v3(W.strefy[stan.miecz.k])) * CFrame.Angles(-math.pi / 2, 0, 0)
					local f = if dt < 0.09 then dt / 0.09 else 1 - (dt - 0.09) / 0.25
					cf = spoczynek:Lerp(cios, math.clamp(f, 0, 1))
				end
			end
			if smugaMiecza and smugaMiecza.Parent then
				smugaMiecza.Enabled = macha
			end
			modelGracza:PivotTo(cf)
		end
		if not Rd then
			return
		end
		local G = D.gry.sila
		local swieca = {}
		for _, e in Rd.plan do
			local ti = Rd.t0 + e.t
			local start = ti - G.lot_s
			local v = wizualne[e.nr]
			if v == nil and t >= start and t < ti + 0.5 then
				local obj, dodatki, owoc = nowyPrzedmiot(e.nr)
				v = { obj = obj, dodatki = dodatki, owoc = owoc, k = e.wartosc }
				wizualne[e.nr] = v
				machnij(arena.ramie, -2.4, 0.12, 0.25)
				gestTrenera("trening_sila")
			end
			if v and v.obj then
				local a = (t - start) / G.lot_s
				local H, Z = v3(W.reka), v3(W.strefy[v.k])
				local C = (H + Z) / 2 + v3(W.luki[v.k])
				local p = if a <= 1 then bezier(math.max(0, a), H, C, Z) else Z + (Z - C) * (2 * (a - 1))
				v.obj.CFrame = CFrame.new(p) * CFrame.Angles(a * 5, a * 3, 0)
				for _, d in v.dodatki or {} do
					d[1].CFrame = v.obj.CFrame * d[2]
				end
				if a > 1.8 then
					local obj = v.obj
					v.obj = nil
					obj:Destroy()
				end
			end
			if stan.lokalne[e.nr] == nil and math.abs(t - ti) <= e.okno then
				swieca[e.wartosc] = true
			end
		end
		for k, w in arena.strefy or {} do
			if swieca[k] then
				swiec(w, KOL.zloto, 0.2)
			else
				przywrocCzesc(w)
			end
		end
	end,
}

-- Pancerz „Blok”: golem bierze zamach, pierścienie zbiegają się do kółka; fioletowy = zmyłka
GRY.pancerz = {
	akcja = function()
		stan.tarcza = { t = os.clock() }
	end,
	miejsce = function(_)
		return v3(D.swiat.pancerz.piesc_cel)
	end,
	napis = function(_)
		return nil, Vector2.new(-36, -52)
	end,
	efekt = function(w, m)
		local W = D.swiat.pancerz
		if w.trafienie and w.powod ~= "przetrwana_zmylka" then
			-- cios przyjęty na tarczę: łuk odbicia zwrócony do golema (jak parada w walce)
			if fx then
				fx:parada(v3(W.tarcza_blok), v3(W.golem) - v3(W.podest), kolor(KX.kolory.blok), 1.6)
			end
			wstrzas(0.25)
		elseif w.powod == "przepuszczone" then
			graj("oberwanie")
			blysk(0.75, KOL.zle)
			wstrzas(0.5)
			wybuch(EF.oberwanie, m, 1.3)
		end
	end,
	klatka = function(t, Rd, W)
		-- pierścienie czasu stoją na ekranie tam, gdzie pięść trafi w tarczę
		local rx, ry = punktEkranu(v3(W.piesc_cel))
		ui.pierscienie.Position = UDim2.fromOffset(rx, ry)
		if modelGracza then
			local spoczynek = CFrame.lookAt(v3(W.tarcza), v3(W.tarcza) + Vector3.new(0, 0, -1))
			local blok = CFrame.lookAt(v3(W.tarcza_blok), v3(W.tarcza_blok) + Vector3.new(0, 0, -1))
			local f = 0
			if stan.tarcza then
				local dt = os.clock() - stan.tarcza.t
				f = if dt < 0.06 then dt / 0.06 elseif dt < 0.24 then 1 else 1 - (dt - 0.24) / 0.2
			end
			modelGracza:PivotTo(spoczynek:Lerp(blok, math.clamp(f, 0, 1)))
		end
		if not Rd then
			return
		end
		local G = D.gry.pancerz
		local spoczynek, zamach, cel = v3(W.piesc_spoczynek), v3(W.piesc_zamach), v3(W.piesc_cel)
		local poz = spoczynek
		local oczy = nil
		local wolne = 1
		for _, p in pierscienie do
			p.ramka.Visible = false
		end
		for _, e in Rd.plan do
			local ti = Rd.t0 + e.t
			local od = ti - G.zamach_s
			if t >= od and t < ti + 0.25 then
				local f = (t - od) / (G.zamach_s - 0.12)
				if t < ti - 0.12 then
					poz = spoczynek:Lerp(zamach, math.clamp(f, 0, 1))
				elseif e.wartosc == "cios" and t < ti then
					poz = zamach:Lerp(cel, (t - (ti - 0.12)) / 0.12)
				elseif e.wartosc == "cios" then
					poz = cel:Lerp(spoczynek, math.clamp((t - ti) / 0.25, 0, 1))
				else
					poz = zamach:Lerp(spoczynek, math.clamp((t - (ti - 0.12)) / 0.37, 0, 1))
				end
				oczy = if e.wartosc == "zmylka" then KOL.zmylka else KOL.cios
			end
			if t >= od and t < ti + 0.1 and wolne <= #pierscienie and stan.lokalne[e.nr] == nil then
				local p = pierscienie[wolne]
				wolne += 1
				local s = 1 + 1.6 * math.clamp((ti - t) / G.zamach_s, 0, 1)
				p.ramka.Size = UDim2.fromScale(s, s)
				p.obrys.Color = kolor(if e.wartosc == "zmylka" then KOL.zmylka else KOL.cios)
				p.ramka.Visible = true
			end
		end
		if arena.piesc then
			arena.piesc.obj.CFrame = CFrame.new(poz)
		end
		for _, w in arena.oczy do
			if w then
				w.obj.Color = if oczy then kolor(oczy) else w.kolor
			end
		end
	end,
}

-- Kondycja „Bieżnia”: ślady stóp jadą na taśmie do linii przed palcami biegacza; lewa / prawa równo z bębnem
local function nowySlad(e)
	local h = if e.podbieg then PODBIEG else KOLOR_GRY.kondycja
	local model = modelZCzesci("Slad", {
		{ "Stopa", Vector3.new(0.95, 0.08, 1.45), h, Vector3.zero },
		{ "Palce", Vector3.new(0.8, 0.08, 0.38), h, Vector3.new(0, 0, 0.98) },
	})
	return model
end

GRY.kondycja = {
	akcja = function(wartosc)
		stan.krok[wartosc] = os.clock()
	end,
	-- stopa na śladzie: wybuch i fala na celu tej stopy; słowo obok taśmy po stronie stopy (nie zasłania śladów)
	miejsce = function(w)
		local p = D.swiat.kondycja.stopy[w.wartosc or w.akcja]
		return if p then v3(p) + Vector3.new(0, 0.2, 0) else nil
	end,
	napis = function(w)
		local lewa = (w.wartosc or w.akcja) == D.gry.kondycja.kierunki[1]
		return nil, Vector2.new(if lewa then -96 else 96, -8)
	end,
	efekt = function(w, m)
		local v = wizualne[w.nr]
		if v and v.obj then
			for _, c in v.obj:GetChildren() do
				if c:IsA("BasePart") then
					c.Color = kolor(if w.trafienie then KOL.zloto else KOL.zle)
					c.Material = if w.trafienie then Enum.Material.Neon else Enum.Material.SmoothPlastic
				end
			end
		end
		if w.trafienie then
			graj("krok")
			fala(m, KOL.zloto, EF.fala_promien * 0.7)
		elseif w.powod == "przepuszczone" then
			wstrzas(0.15)
		end
	end,
	klatka = function(t, Rd, W)
		local G = D.gry.kondycja
		local v = W.slad_predkosc
		local ts, tr = v3(W.tasma_srodek), v3(W.tasma_rozmiar)
		local z0 = ts.Z - tr.Z / 2
		local przesuw = if Rd and t > Rd.t0 then v * (t - Rd.t0) else 0
		for _, w in arena.pasy or {} do
			if w.obj.Parent then
				local z = z0 + ((w.cf.Position.Z - przesuw - z0) % tr.Z)
				w.obj.CFrame = CFrame.new(w.cf.Position.X, w.cf.Position.Y, z) * w.cf.Rotation
			end
		end
		if not Rd then
			return
		end
		local swieca = {}
		local beben = 0
		for i, e in Rd.plan do
			local ti = Rd.t0 + e.t
			local z = W.linia[3] + v * (ti - t)
			local vw = wizualne[e.nr]
			if vw == nil and t >= ti - W.slady_s and z > W.linia[3] - 2.6 then
				vw = { obj = nowySlad(e) }
				wizualne[e.nr] = vw
			end
			if vw and vw.obj then
				local p = W.stopy[e.wartosc]
				vw.obj:PivotTo(CFrame.new(p[1], p[2] + 0.05, z))
				if z < W.linia[3] - 2.6 then
					local model = vw.obj
					vw.obj = nil
					model:Destroy()
				end
			end
			if stan.lokalne[e.nr] == nil and math.abs(t - ti) <= e.okno then
				swieca[e.wartosc] = true
			end
			if t >= ti then
				beben = i
			end
		end
		for k, w in arena.cele or {} do
			local nacisk = stan.krok[k] and os.clock() - stan.krok[k] < 0.15
			if nacisk then
				swiec(w, KOL.krem, 0.05, true)
			elseif swieca[k] then
				swiec(w, KOL.zloto, 0.15, true)
			else
				przywrocCzesc(w)
			end
		end
		-- bęben trenera na każdy krok (dźwięk i ruch pałki) — rytm słychać, ale ocenia tylko obraz i serwer
		if beben > stan.beben then
			stan.beben = beben
			graj("beben")
			machnij(arena.palka, -1.3, 0.06, 0.18)
			gestTrenera("trening_kondycja")
			if arena.beben then
				swiec(arena.beben, KOL.zloto, 0, true)
				task.delay(0.1, function()
					przywrocCzesc(arena.beben)
				end)
			end
		end
		if t >= Rd.t0 then
			local p = rzadPoziomu(G, t, Rd)
			zacznijBieg(0.62 / p.odstep_s)
		end
	end,
}

-- Zręczność „Kłody”: ramię z kłodą obraca się wokół słupa; jeden pełny obrót między przejściami przez miejsce gracza
-- (w chwili t zdarzenia + wyprzedzenie_s kłoda jest przy postaci); wysokość ustala się w drugiej ćwiartce obrotu
local function katKlody(t, Rd, W)
	local G = D.gry.zrecznosc
	local wy = G.wyprzedzenie_s
	local plan = Rd.plan
	local s = W.obrot
	local function kat(faza, pol)
		return math.rad(90 - s * (if pol then 180 else 360) * (1 - faza))
	end
	if #plan == 0 or t < Rd.t0 then
		return kat(0, true), 1, 0
	end
	local poprz = Rd.t0
	for i, e in plan do
		local ta = Rd.t0 + e.t + wy
		if t < ta then
			local faza = (t - poprz) / math.max(0.05, ta - poprz)
			return kat(faza, i == 1), i, faza
		end
		poprz = ta
	end
	local faza = math.clamp((t - poprz) / 0.8, 0, 1)
	return math.rad(90 - s * 180 * faza), #plan + 1, faza
end

local function wysokoscKlody(Rd, W, i, faza)
	local H = W.wysokosci
	local plan = Rd.plan
	local e = plan[i]
	local poprz = if i > 1 and plan[i - 1] then H[plan[i - 1].wartosc] else H.nisko
	if not e then
		return poprz
	end
	local cel = H[e.wartosc]
	local inna = if e.wartosc == "nisko" then H.wysoko else H.nisko
	local function przejscie(a, b2, od, koniec)
		local f = math.clamp((faza - od) / (koniec - od), 0, 1)
		f = f * f * (3 - 2 * f)
		return a + (b2 - a) * f
	end
	if e.zmiana then
		if faza < 0.45 then
			return przejscie(poprz, inna, 0.25, 0.4)
		end
		return przejscie(inna, cel, 0.45, 0.55)
	end
	return przejscie(poprz, cel, 0.25, 0.4)
end

GRY.zrecznosc = {
	akcja = function(wartosc)
		stan.unik = { rodzaj = wartosc, t = os.clock() }
		if wartosc == "skok" then
			graj("skok")
		end
	end,
	-- unik udany: fala kurzu spod stóp; słowo nad głową postaci (kłoda przechodzi niżej)
	miejsce = function(_)
		local p = stopyPostaci()
		return if p then p + Vector3.new(0, 0.15, 0) else nil
	end,
	napis = function(_)
		local p = stopyPostaci()
		if p then
			-- obok głowy, nie na niej: w skoku postać jest wyżej i słowo zasłaniało głowę; po prawej, bo po lewej stoi
			-- duże słowo stanowiska („+1 Zręczność!”) — próba w Studio 18.11.2026
			return p + Vector3.new(0, 7.2, 0), Vector2.new(124, 0)
		end
		return nil, nil
	end,
	efekt = function(w, m)
		if w.trafienie then
			fala(m, KOL.krem, EF.fala_promien)
		elseif w.powod == "przepuszczone" then
			stan.unik = { rodzaj = "uderzenie", t = os.clock() }
			graj("upadek")
			blysk(0.75, KOL.zle)
			wstrzas(0.4)
			wybuch(EF.oberwanie, piersPostaci(), 1.3)
		end
	end,
	klatka = function(t, Rd, W)
		-- postać: skok (uniesienie po łuku), padnij (niżej i pochylona), uderzenie (odchylenie do tyłu).
		-- Bohater klasy: klip skoku / padnięcia i przesunięcie widoku przez haczyk; awatar: staw biodra u siebie
		local u = stan.unik
		if u then
			local dt = os.clock() - u.t
			local bohater = bohaterAktywny()
			if u.rodzaj == "skok" and dt < 0.6 then
				local luk = math.sin(math.pi * dt / 0.6)
				if bohater then
					klipBohatera(BH.klipy.skok)
					przesunBohatera(Vector3.new(0, BH.skok_wys * luk, 0))
				else
					ustawStaw(nil, CFrame.new(0, 2.7 * luk, 0))
				end
			elseif u.rodzaj == "padnij" and dt < 0.75 then
				local f = math.clamp(math.min(dt / 0.1, (0.75 - dt) / 0.15), 0, 1)
				if bohater then
					-- poza „padnij” sama opuszcza biodra bohatera ze stopami na ziemi — bez przesunięcia w dół
					-- (inaczej wszedłby pod ziemię); przesunięcie zostaje tylko na skok
					klipBohatera(BH.klipy.padnij)
					przesunBohatera(nil)
				else
					ustawStaw(nil, CFrame.new(0, -1.7 * f, 0) * CFrame.Angles(-1.2 * f, 0, 0))
				end
			elseif u.rodzaj == "uderzenie" and dt < 0.45 then
				local f = math.sin(math.pi * dt / 0.45)
				if bohater then
					klipBohatera(nil)
					przesunBohatera(Vector3.new(0, 0, 0.7 * f)) -- odrzut od kłody (postać stoi twarzą do słupa)
				else
					ustawStaw(nil, CFrame.Angles(0.45 * f, 0, 0))
				end
			else
				stan.unik = nil
				if bohater then
					klipBohatera(nil)
					przesunBohatera(nil)
				else
					ustawStaw(nil, CFrame.new())
				end
			end
		end
		if not arena.klody or not arena.klody.obj.Parent then
			return
		end
		local sl = v3(W.slup)
		local kat, i, faza = 0, 1, 0
		local h = W.wysokosci.nisko
		if Rd then
			kat, i, faza = katKlody(t, Rd, W)
			h = wysokoscKlody(Rd, W, i, faza)
		else
			kat = math.rad(270)
		end
		local a = math.pi - kat
		local obrot = CFrame.new(sl) * CFrame.Angles(0, a, 0) * CFrame.new(-sl)
		arena.klody.obj:PivotTo(CFrame.new(0, h - W.wysokosci.nisko, 0) * obrot * arena.klody.cf)
		-- podest gracza świeci, gdy kłoda jest w oknie (jak strefy Siły)
		local w = false
		if Rd then
			for _, e in Rd.plan do
				if stan.lokalne[e.nr] == nil and math.abs(t - (Rd.t0 + e.t)) <= e.okno then
					w = true
				end
			end
		end
		if w then
			swiec(arena.podestKlody, KOL.zloto, 0, true)
		else
			przywrocCzesc(arena.podestKlody)
		end
	end,
}

-- Inteligencja „Runy”: pokaz (kamienie świecą po kolei, nuta każdej runy), potem gracz powtarza; kropki postępu
local function nutaRuny(k)
	local G = D.gry.inteligencja
	local i = table.find(G.runy, k) or 1
	graj("nuta", D.dzwieki.runy_nuty[i])
end

GRY.inteligencja = {
	akcja = function(wartosc, w)
		stan.runyNacisk[wartosc] = { t = os.clock(), zle = w ~= nil and w.przyjete and not w.trafienie }
		nutaRuny(wartosc)
	end,
	-- runa wpisana: iskry przy naciśniętym kamieniu; słowo na tym kamieniu (gracz już go nacisnął)
	miejsce = function(w)
		local p = D.swiat.inteligencja.kamienie[w.akcja or w.wartosc]
		return if p then v3(p) + Vector3.new(0, 0, 0.9) else nil
	end,
	efekt = function(w)
		if w.trafienie and w.zaklecie then
			for k, rw in arena.runy do
				if rw.kamien then
					odlamki(rw.kamien.obj.Position + Vector3.new(0, 0, 0.8), KOL["runa_" .. k], 5, 2.5)
				end
			end
			-- całe zaklęcie: rozbłysk bariery na środku ściany z runami
			local W = D.swiat.inteligencja
			wybuch(EF.zaklecie, v3(W.sciana) + Vector3.new(0, 0, 1.2), 1.4)
			if not grajZdarzenie(DK.zaklecie) then
				melodia(D.dzwieki.melodia_koniec)
			end
		elseif not w.trafienie then
			for k in arena.runy do
				stan.runyNacisk[k] = { t = os.clock(), zle = true }
			end
			wstrzas(0.12)
		end
	end,
	klatka = function(t, Rd, W)
		local R = stan.R
		local swieca = {}
		if Rd and R and R.pokazOd and not R.koniec then
			local r = t - Rd.t0
			local G = D.gry.inteligencja
			if r >= R.pokazOd and r < R.pokazDo + 0.05 then
				local idx = math.floor((r - R.pokazOd) / R.krok) + 1
				if idx <= R.dl and (r - R.pokazOd) - (idx - 1) * R.krok < R.swieci then
					local e = Rd.plan[R.offset + idx]
					if e then
						swieca[e.wartosc] = "pokaz"
						local klucz = string.format("%d:%d", R.pokazy, idx)
						if stan.pokazGrany ~= klucz then
							stan.pokazGrany = klucz
							nutaRuny(e.wartosc)
						end
					end
				end
				if stan.pokazNapis ~= R.pokazy and t >= Rd.t0 then
					stan.pokazNapis = R.pokazy
					napisKomiks(T.patrz, "info", nil)
				end
				if arena.kula then
					swiec(arena.kula, "FFFFFF", 0, true)
				end
			elseif r >= R.pokazDo then
				if stan.pokazNapis ~= -R.pokazy and R.poz == 0 then
					stan.pokazNapis = -R.pokazy
					napisKomiks(T.twoja_kolej, "info", nil, { kolor = "krytyk" })
				end
				przywrocCzesc(arena.kula)
			end
			-- kropki: ile run w tej sekwencji i ile już wpisano (w pokazie: ile pokazano)
			local pokazane = if r < R.pokazDo then math.clamp(math.floor((r - R.pokazOd) / R.krok) + 1, 0, R.dl) else R.poz
			for i, k in ui.kropki do
				k.Visible = i <= R.dl
				k.BackgroundColor3 = kolor(if i <= pokazane then (if r < R.pokazDo then KOL.krem else KOL.zloto) else KOL.szary)
			end
			ui.postep.BackgroundColor3 = kolor(if r < R.pokazDo then KOL.tusz else KOL.krem)
		end
		for k, n in stan.runyNacisk do
			if os.clock() - n.t < 0.28 then
				swieca[k] = if n.zle then "zle" else "nacisk"
			end
		end
		for k, rw in arena.runy do
			local s = swieca[k]
			for _, z in rw.znaki do
				if s == "zle" then
					swiec(z, KOL.zle, 0, true)
				elseif s then
					swiec(z, KOL["runa_" .. k], 0, true)
				else
					przywrocCzesc(z)
				end
			end
			if s == "pokaz" or s == "nacisk" then
				swiec(rw.kamien, "C9CED6", nil, false)
			else
				przywrocCzesc(rw.kamien)
			end
		end
	end,
}

-- Szczęście „Koniczyny”: koniczyny i kamienie spadają z korony drzewa na trzy tory; koszyk nad głową łapie w chwili
-- upadku (werdykt lokalny od razu, serwer po zapasie); cień na torze pokazuje, gdzie spadnie
local function nowyObiekt(e)
	local lista
	if e.wartosc == "kamien" then
		lista = { { "Kamien", Vector3.new(1.3, 1.3, 1.3), KOL.kamien, Vector3.zero, Enum.Material.Slate, Enum.PartType.Ball } }
	else
		local h = if e.wartosc == "zlota" then KOL.zloto else KOL.koniczyna
		local m = if e.wartosc == "zlota" then Enum.Material.Neon else Enum.Material.SmoothPlastic
		lista = { { "Lodyzka", Vector3.new(0.18, 0.9, 0.18), "2E7D32", Vector3.new(0, -0.55, 0) } }
		local listki = { { -0.36, 0.18 }, { 0.36, 0.18 }, { 0, -0.18 } }
		if e.wartosc == "zlota" then
			listki = { { -0.36, 0.18 }, { 0.36, 0.18 }, { -0.2, -0.24 }, { 0.2, -0.24 } }
		end
		for i, d in listki do
			table.insert(lista, { "Listek" .. i, Vector3.new(0.72, 0.72, 0.72), h, Vector3.new(d[1], d[2] + 0.1, 0), m, Enum.PartType.Ball })
		end
	end
	local model = modelZCzesci("Spada", lista)
	obrysModelu(model)
	return model
end

GRY.szczescie = {
	-- koniczyna w koszyku (albo kamień): wybuch tam, gdzie rzecz spadła; słowo na piersi postaci (nie na torach)
	miejsce = function(w)
		local v = w.nr and wizualne[w.nr]
		if v and v.obj then
			return v.obj:GetPivot().Position
		end
		local p = stopyPostaci()
		return if p then p + (v3(D.swiat.szczescie.koszyk) - v3(D.swiat.szczescie.podest)) else nil
	end,
	napis = function(w)
		if w.trafienie or w.powod == "kamien" then
			return piersPostaci(), nil
		end
		return nil, Vector2.new(0, -30) -- koniczyna spadła obok: słowo nad miejscem upadku
	end,
	efekt = function(w, m)
		local v = wizualne[w.nr]
		if w.trafienie then
			graj("lap")
			if w.powod == "zlota" then
				if not grajZdarzenie(DK.zlota) then
					melodia(D.dzwieki.melodia_koniec)
				end
				if v and v.obj then
					odlamki(v.obj:GetPivot().Position, KOL.zloto, 8, 2.5)
				end
			end
		elseif w.powod == "kamien" then
			graj("kamien")
			blysk(0.75, KOL.zle)
			wstrzas(0.3)
			wybuch(EF.kamien, m, 1.1)
		end
	end,
	klatka = function(t, Rd, W)
		local G = D.gry.szczescie
		local postac = gracz.Character
		local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
		-- przejście postaci na tor (0,14 s)
		if stan.ruchToru and hrp then
			local f = math.clamp((os.clock() - stan.ruchToru.t) / 0.14, 0, 1)
			local p = stan.ruchToru.od:Lerp(stan.ruchToru["do"], f)
			postac:PivotTo(CFrame.new(p) * hrp.CFrame.Rotation)
			if f >= 1 then
				stan.ruchToru = nil
			end
		end
		local kosz = v3(W.koszyk) - v3(W.podest)
		local baza = if hrp then Vector3.new(hrp.Position.X, W.podest[2], hrp.Position.Z) else v3(W.podest)
		local kp = baza + kosz
		if modelGracza then
			modelGracza:PivotTo(CFrame.new(kp))
		end
		-- tor pod koszykiem jaśniejszy
		for n, w in arena.tory or {} do
			if G.tory[stan.tor] == n then
				swiec(w, KOL.zloto, 0.35, false)
			else
				przywrocCzesc(w)
			end
		end
		if not Rd or not stan.R then
			return
		end
		local y0 = W.podest[2] + W.spad_y
		local yb = kp.Y
		for _, e in Rd.plan do
			local ti = Rd.t0 + e.t
			local start = ti - G.lot_s
			local vw = wizualne[e.nr]
			if vw == nil and t >= start and t < ti + 0.6 then
				local k, zt = L.toryZdarzenia(D, stan.R, e)
				local cien = czesc("Cien", Vector3.new(0.06, 1.2, 1.2), "2F3B22", nil, Enum.PartType.Cylinder)
				cien.Transparency = 0.45
				cien.Parent = efekty
				vw = { obj = nowyObiekt(e), cien = cien, k = k, z = zt }
				wizualne[e.nr] = vw
			end
			if vw and vw.obj then
				local a = (t - start) / G.lot_s
				local xk, xz = punktToru(vw.k), punktToru(vw.z)
				local x = xz:Lerp(xk, math.clamp(a / 0.5, 0, 1))
				local werdykt = stan.lokalne[e.nr]
				local y
				if a <= 1 then
					y = y0 - (y0 - yb) * a * a
				elseif werdykt == true then
					y = yb
				else
					y = math.max(W.podest[2] + 0.6, yb - 9 * (a - 1))
				end
				vw.obj:PivotTo(CFrame.new(x.X, y, kp.Z) * CFrame.Angles(0, 0, if e.wartosc == "kamien" then a * 4 else math.sin(a * 9) * 0.3))
				if vw.cien then
					local s = 0.6 + 1.2 * math.clamp(a, 0, 1)
					vw.cien.Size = Vector3.new(0.06, s, s)
					vw.cien.CFrame = CFrame.new(xk.X, W.podest[2] + 0.18, kp.Z) * CFrame.Angles(0, 0, math.rad(90))
					if a > 1 then
						local obj = vw.cien
						vw.cien = nil
						obj:Destroy()
					end
				end
				if a > 1.35 then
					local model = vw.obj
					vw.obj = nil
					model:Destroy()
				end
			end
		end
	end,
}

------------------------------------------------------------------ werdykt (lokalny albo z serwera) → efekty; każde zdarzenie pokazane raz
local function efekt(w)
	if w.nr ~= nil and stan.lokalne[w.nr] ~= nil then
		return
	end
	if w.nr ~= nil then
		stan.lokalne[w.nr] = w.trafienie
	end
	local gra = stan.gra
	local h = gra and GRY[gra]
	-- miejsce werdyktu w świecie (wybuch) i miejsce słowa (domyślnie to samo, z przesunięciem gry)
	local m = if h and h.miejsce then h.miejsce(w) else nil
	local gdzie, przesun = m, nil
	if h and h.napis then
		local p2, d2 = h.napis(w)
		gdzie = p2 or m
		przesun = d2
	end
	if w.trafienie then
		if not grajZdarzenie(gra and DK.trafienie[gra]) then
			graj("trafienie")
		end
		if gra ~= "inteligencja" then
			local nuty = D.dzwieki.skale_nuty
			graj("nuta", nuty[math.min(#nuty, math.max(1, w.seria))])
		end
		blysk(0.82)
		podskokSerii()
		local prog = false
		for _, p in D.przyrost.progi_serii do
			if w.seria == p then
				prog = true
			end
		end
		local st = gra and L.statystyka(D, gra)
		local punkt = (w.przyrost or 0) > 0 and st ~= nil
		local zmylka = w.powod == "przetrwana_zmylka"
		local zlota = w.powod == "zlota"
		local zaklecie = w.zaklecie == true
		-- „mocne” trafienie (jak krytyk w walce): co któreś w serii, próg serii, punkt statystyki, złota koniczyna, całe
		-- zaklęcie — większy wybuch, gwiazda za słowem, mocniejsze zawężenie kadru
		local mocne = not zmylka and (punkt or prog or zlota or zaklecie or (w.seria > 0 and w.seria % KX.mocne_co == 0))
		if not zmylka then
			wybuch(if mocne then EF.mocne else (EF.trafienie[gra] or "cios"), m, if mocne then EF.skala_mocne else 1)
		end
		zawezenie(if mocne then "mocne" else "uderzenie")
		-- duże słowo w miejscu napisów stanowiska: punkt statystyki, potem próg serii, potem całe zaklęcie (jedno naraz)
		local duze = nil
		if punkt then
			-- pasek treningu pełny: punkt statystyki (to widzi gracz jako nagrodę)
			if not grajZdarzenie(DK.punkt) then
				graj("seria")
				melodia(D.dzwieki.melodia_koniec)
			end
			duze = "punkt"
			napisKomiks(string.format(T.punkt, w.przyrost, st.nazwa), "punkt", nil)
		elseif prog then
			graj("seria")
			duze = "seria"
			napisKomiks(string.format(T.seria, w.seria), "seria", nil)
		elseif zaklecie then
			duze = "zaklecie"
			napisKomiks(T.zaklecie, "zloto", nil)
		end
		if duze == "punkt" or duze == "seria" then
			-- akcent serii: mocniejsze zawężenie kadru, drżenie i złota fala wokół postaci
			zawezenie("seria")
			wstrzas(0.2)
			fala(stopyPostaci(), KOL.zloto, EF.fala_serii)
		end
		-- słowo przy miejscu trafienia (komiksowe „PAF!”, „BLOK!”, „HOP!”…)
		local tekst = tekstTrafienia(w.seria, TRAFIENIA[gra] or T.trafienia)
		local styl = if mocne then "mocne" else "trafienie"
		local barwa = if mocne then nil else KX.kolor_trafienia[gra]
		if zmylka then
			tekst = T.zmylka_ok
		elseif zlota then
			tekst, styl = T.zlota, "zloto"
		elseif zaklecie then
			tekst, styl = T.zaklecie, "zloto"
		end
		if duze ~= "zaklecie" then
			napisKomiks(tekst, styl, gdzie, { kolor = barwa, przesun = przesun })
		end
	else
		graj("pudlo")
		local wlasne = gra and T.pudla_gier[gra]
		napisKomiks((wlasne and wlasne[w.powod]) or T.pudlo[w.powod] or T.pudlo.przepuszczone, "pudlo", gdzie, { przesun = przesun })
	end
	if h and h.efekt then
		h.efekt(w, m)
	end
	odswiezStatus()
end

------------------------------------------------------------------ naciśnięcia
local function nacisnij(wartosc)
	if stan.ekran ~= "runda" or stan.R == nil or stan.runda == nil then
		return "brak_rundy"
	end
	if teraz() < stan.runda.t0 then
		return "odliczanie" -- w czasie odliczania naciśnięcia nic nie robią (bez kary za niecierpliwość)
	end
	local G = D.gry[stan.gra]
	if G.typ == "lapanie" and (wartosc == "w_lewo" or wartosc == "w_prawo") then
		local nowy = math.clamp(stan.tor + (if wartosc == "w_lewo" then -1 else 1), 1, #G.tory)
		if nowy == stan.tor then
			return "brzeg"
		end
		wartosc = G.tory[nowy]
	end
	local h = GRY[stan.gra]
	if h.akcja and G.typ ~= "sekwencja" then
		h.akcja(wartosc)
	end
	local t = teraz()
	local w = L.zgloszenie(D, stan.R, wartosc, t, t)
	if not w.przyjete then
		return w.powod
	end
	zdalne:FireServer("akcja", stan.runda.id, wartosc, t)
	if G.typ == "sekwencja" then
		h.akcja(wartosc, w)
	end
	if w.ruch then
		ustawTor(w.tor, false)
	else
		efekt(w)
	end
	return w.powod
end

------------------------------------------------------------------ przyciski sterowania
for k, poz in { gora = { 1, 0 }, lewo = { 0, 1 }, prawo = { 2, 1 }, dol = { 1, 2 } } do
	local s = D.sterowanie[k]
	local p = przycisk(ui.krzyz, "Przycisk_" .. k, "", poz[1] * (b + g), poz[2] * (b + g), b, b, KOLOR_GRY.sila, function()
		nacisnij(k)
	end)
	strzalka(p, k)
	napis(p, "Klawisz", s.skrot, "maly", 0, b - 20, b, 18, KOL.krem)
end
do
	local s = D.sterowanie.blok
	local p = przycisk(ui.blok, "Przycisk_blok", "", 0, 0, U.blok_px, U.blok_px, KOLOR_GRY.pancerz, function()
		nacisnij("blok")
	end)
	p:FindFirstChildOfClass("UICorner").CornerRadius = UDim.new(0.5, 0) -- okrągły
	napis(p, "Napis", s.napis, "duzy", 0, U.blok_px * 0.22, U.blok_px, 32, KOL.krem)
	napis(p, "Klawisz", s.skrot, "maly", 0, U.blok_px * 0.6, U.blok_px, 18, KOL.krem)
end
-- Kondycja: dwie duże stopy pod kciukami
for _, w in { { ui.stopaL, "lewa" }, { ui.stopaP, "prawa" } } do
	local s = D.sterowanie[w[2]]
	local p = przycisk(w[1], "Przycisk_" .. w[2], "", 0, 0, U.stopa_px, U.stopa_px, KOLOR_GRY.kondycja, function()
		nacisnij(w[2])
	end)
	ikonaStopy(p, U.stopa_px / 2, U.stopa_px * 0.4, U.stopa_px * 0.5, KOL.krem)
	napis(p, "Klawisz", s.napis .. " · " .. s.skrot, "maly", 0, U.stopa_px - 22, U.stopa_px, 18, KOL.krem)
end
-- Zręczność: SKOK nad PADNIJ
for i, k in { "skok", "padnij" } do
	local s = D.sterowanie[k]
	local p = przycisk(ui.unik, "Przycisk_" .. k, "", 0, (i - 1) * (U.unik_px + 2 * g), U.unik_px, U.unik_px,
		KOLOR_GRY.zrecznosc, function()
			nacisnij(k)
		end)
	strzalka(p, if k == "skok" then "gora" else "dol", 0.3, KOL.tusz)
	napis(p, "Napis", s.napis, "maly", 0, U.unik_px * 0.48, U.unik_px, 18, KOL.tusz)
	napis(p, "Klawisz", s.skrot, "maly", 0, U.unik_px - 20, U.unik_px, 18, KOL.tusz)
end
-- Inteligencja: cztery runy w krzyżu (kolor i kształt jak na kamieniach)
for k, poz in { gora = { 1, 0 }, lewo = { 0, 1 }, prawo = { 2, 1 }, dol = { 1, 2 } } do
	local p = przycisk(ui.runy, "Przycisk_" .. k, "", poz[1] * (r_ + g), poz[2] * (r_ + g), U.runa_px, U.runa_px,
		KOL["runa_" .. k], function()
		nacisnij(k)
	end)
	glifRuny(p, k, r_ / 2, r_ / 2, r_ * 0.55, KOL.krem)
end
-- Szczęście: w lewo / w prawo (o jeden tor)
for _, w in { { ui.torL, "w_lewo", "lewo" }, { ui.torP, "w_prawo", "prawo" } } do
	local s = D.sterowanie[w[2]]
	local p = przycisk(w[1], "Przycisk_" .. w[2], "", 0, 0, U.tor_px, U.tor_px, KOLOR_GRY.szczescie, function()
		nacisnij(w[2])
	end)
	strzalka(p, w[3], 0.38, KOL.krem, 1.4)
	napis(p, "Klawisz", s.skrot, "maly", 0, U.tor_px - 22, U.tor_px, 18, KOL.krem)
end

local function wyslijStart()
	if stan.ekran == "stanowisko" or stan.ekran == "podsumowanie" then
		if not grajZdarzenie(DK.przycisk) then
			graj("przycisk")
		end
		zdalne:FireServer("start")
	end
end

local function wyslijWyjdz()
	graj("przycisk")
	zdalne:FireServer("wyjdz")
end

local function przerwij()
	if stan.ekran == "runda" then
		zdalne:FireServer("przerwij")
	end
end

przycisk(ui.przerwij, "Przycisk_przerwij", "X", 0, 0, U.przycisk_maly_px, U.przycisk_maly_px, KOL.zle, przerwij)

------------------------------------------------------------------ podpowiedź obrazkowa (co widzisz → co naciskasz → co się dzieje)
local function strzalkaPodpowiedzi(P, x)
	local f = ramka(P, "Dalej" .. x, x, 42, 26, 26, KOL.krem, 1)
	strzalka(f, "prawo", 0.5, KOL.szary, 0.9)
end

local function klawiszIkona(P, x, y, w, h_kolor, tekst, kierunek)
	local f = ramka(P, "Klawisz" .. x .. "_" .. y, x, y, w, w, h_kolor)
	zaokraglij(f, 8)
	obrysuj(f, 2)
	if kierunek then
		strzalka(f, kierunek, 0.4, KOL.krem, 0.8)
	end
	if tekst then
		napis(f, "Tekst", tekst, "maly", 0, w - 18, w, 16, KOL.krem)
	end
	return f
end

local function gwiazda(P, x, y, r)
	for i, kat in { 0, 45 } do
		local f = ramka(P, "Gwiazda" .. i, x, y, r, r, KOL.zloto)
		f.Rotation = kat
		obrysuj(f, 2)
	end
end

local function zbudujObrazek(gra, P)
	local kol = KOLOR_GRY[gra]
	if gra == "sila" then
		local s = ramka(P, "Owoc", 46, 34, 28, 28, OWOCE[1].skorka)
		zaokraglij(s, 999)
		obrysuj(s, 2)
		local z = ramka(P, "Strefa", 92, 52, 30, 30, KOL.krem, 1)
		zaokraglij(z, 999)
		obrysuj(z, 4, KOL.zloto)
		strzalkaPodpowiedzi(P, 140)
		klawiszIkona(P, 200, 42, 52, kol, "D", "prawo")
		strzalkaPodpowiedzi(P, 262)
		gwiazda(P, 330, 42, 34)
	elseif gra == "pancerz" then
		local duzy = ramka(P, "Pierscien", 70, 42, 62, 62, KOL.krem, 1)
		zaokraglij(duzy, 999)
		obrysuj(duzy, 4, KOL.cios)
		local maly = ramka(P, "Kolko", 70, 42, 30, 30, KOL.krem, 1)
		zaokraglij(maly, 999)
		obrysuj(maly, 4, KOL.krem)
		strzalkaPodpowiedzi(P, 140)
		local p = klawiszIkona(P, 200, 42, 56, kol, nil, nil)
		p:FindFirstChildOfClass("UICorner").CornerRadius = UDim.new(0.5, 0)
		napis(p, "Blok", D.sterowanie.blok.napis, "maly", 0, 18, 56, 18, KOL.krem)
		strzalkaPodpowiedzi(P, 262)
		local t = ramka(P, "Tarcza", 330, 42, 40, 46, kol)
		zaokraglij(t, 10)
		obrysuj(t, 3, KOL.zloto)
	elseif gra == "kondycja" then
		local tasma = ramka(P, "Tasma", 70, 42, 70, 72, "2E2A33")
		zaokraglij(tasma, 6)
		ramka(tasma, "Linia", 35, 18, 66, 4, KOL.krem)
		ikonaStopy(tasma, 18, 22, 22, KOL.zloto)
		ikonaStopy(tasma, 52, 52, 22, kol)
		strzalkaPodpowiedzi(P, 140)
		klawiszIkona(P, 178, 42, 40, kol, D.sterowanie.lewa.skrot, nil)
		klawiszIkona(P, 222, 42, 40, kol, D.sterowanie.prawa.skrot, nil)
		strzalkaPodpowiedzi(P, 262)
		ikonaStopy(P, 315, 42, 40, kol)
		ikonaStopy(P, 345, 50, 40, kol)
	elseif gra == "zrecznosc" then
		for i, w in { { "nisko", 62, "gora", D.sterowanie.skok.skrot }, { "wysoko", 228, "dol", D.sterowanie.padnij.skrot } } do
			local ramkaK = ramka(P, "Scena" .. i, w[2], 42, 56, 64, "D8C08A")
			zaokraglij(ramkaK, 6)
			local postac = ramka(ramkaK, "Postac", 28, 36, 14, 40, "8FA6C8")
			zaokraglij(postac, 4)
			local kl = ramka(ramkaK, "Kloda", 28, if w[1] == "nisko" then 54 else 16, 52, 12, KOL.drewno)
			zaokraglij(kl, 6)
			obrysuj(kl, 2)
			klawiszIkona(P, w[2] + 66, 42, 48, kol, w[4], w[3])
		end
		strzalkaPodpowiedzi(P, 170)
	elseif gra == "inteligencja" then
		local oko = ramka(P, "Oko", 46, 42, 50, 30, KOL.krem)
		zaokraglij(oko, 999)
		obrysuj(oko, 3)
		local zrenica = ramka(oko, "Zrenica", 25, 15, 16, 16, KOL.tusz)
		zaokraglij(zrenica, 999)
		local kam = ramka(P, "Kamien", 100, 42, 40, 40, "8A8F99")
		zaokraglij(kam, 6)
		glifRuny(kam, "prawo", 20, 20, 26, KOL.runa_prawo)
		strzalkaPodpowiedzi(P, 150)
		local p = klawiszIkona(P, 210, 42, 52, KOL.runa_prawo, nil, nil)
		glifRuny(p, "prawo", 26, 26, 28, KOL.krem)
		strzalkaPodpowiedzi(P, 270)
		gwiazda(P, 330, 42, 34)
	elseif gra == "szczescie" then
		for i, w in { { "koniczyna", 52, true }, { "kamien", 150, false } } do
			local kosz = ramka(P, "Koszyk" .. i, w[2], 58, 44, 18, KOL.drewno)
			zaokraglij(kosz, 4)
			if w[1] == "koniczyna" then
				ikonaKoniczyny(P, w[2], 30, 30, KOL.koniczyna)
			else
				local k = ramka(P, "Kamien" .. i, w[2], 30, 24, 24, KOL.kamien)
				zaokraglij(k, 999)
				obrysuj(k, 2)
			end
			local znak = ramka(P, "Znak" .. i, w[2] + 30, 22, 22, 22, if w[3] then KOL.dobrze else KOL.zle)
			zaokraglij(znak, 999)
			napis(znak, "T", if w[3] then "+" else "−", "maly", 0, 1, 22, 20, KOL.krem)
		end
		strzalkaPodpowiedzi(P, 214)
		klawiszIkona(P, 274, 42, 46, kol, D.sterowanie.w_lewo.skrot, "lewo")
		klawiszIkona(P, 330, 42, 46, kol, D.sterowanie.w_prawo.skrot, "prawo")
	end
end

-- sześć obrazków budowanych raz (ramki w ui.obrazek), na stanowisku widać tylko obrazek tej gry
ui.obrazki = {}
for _, st in D.statystyki do
	local P = Instance.new("Frame")
	P.Name = "Obrazek_" .. st.id
	P.Size = UDim2.fromScale(1, 1)
	P.BackgroundTransparency = 1
	P.Visible = false
	P.Parent = ui.obrazek
	zbudujObrazek(st.id, P)
	ui.obrazki[st.id] = P
end

local function obrazek(gra)
	for id, P in ui.obrazki do
		P.Visible = id == gra
	end
end

------------------------------------------------------------------ tymczasowy wybór mini-gry
local function pokazWybor(zrodlo)
	if stan.ekran == "runda" then
		komunikat(T.odmowa.trwa_runda)
		return false
	end
	stan.wybor = true
	stan.zrodlo = zrodlo
	pokazWidocznosc()
	return true
end

local function ukryjWybor()
	stan.wybor = false
	pokazWidocznosc()
end

local function wybierz(gra)
	if stan.ekran == "runda" then
		komunikat(T.odmowa.trwa_runda)
		return "trwa_runda"
	end
	graj("przycisk")
	zdalne:FireServer("wejdz", gra)
	return "wyslano"
end

do
	local W = panel("Wybor", 478, 304, UDim2.new(0.5, 0, 0.5, 0), Vector2.new(0.5, 0.5))
	ui.wybor = W
	zaokraglij(W, 14)
	obrysuj(W, 3)
	napis(W, "Tytul", T.tytul_wyboru, "sredni", 12, 6, 400, 26, KOL.tusz, Enum.TextXAlignment.Left)
	napis(W, "Tymczasowy", T.tymczasowy, "maly", 12, 32, 400, 36, KOL.zmylka, Enum.TextXAlignment.Left)
	przycisk(W, "Zamknij", "X", 478 - 12 - U.przycisk_maly_px, 8, U.przycisk_maly_px, U.przycisk_maly_px, KOL.zle, ukryjWybor)
	for i, st in D.statystyki do
		local kol, rz = (i - 1) % 3, math.floor((i - 1) / 3)
		local k = Instance.new("Frame")
		k.Name = "Kafelek_" .. st.id
		k.Position = UDim2.fromOffset(12 + kol * 154, 72 + rz * 114)
		k.Size = UDim2.fromOffset(146, 106)
		k.BackgroundColor3 = Color3.new(1, 1, 1)
		k.BorderSizePixel = 0
		zaokraglij(k, 10)
		obrysuj(k, 2, st.kolor)
		k.Parent = W
		local pasek = Instance.new("Frame")
		pasek.Name = "Pasek"
		pasek.Size = UDim2.new(1, 0, 0, 6)
		pasek.BackgroundColor3 = kolor(st.kolor)
		pasek.BorderSizePixel = 0
		pasek.Parent = k
		napis(k, "Nazwa", st.nazwa, "sredni", 4, 8, 138, 22, KOL.tusz)
		napis(k, "Gra", st.gra, "maly", 4, 30, 138, 18, KOL.szary)
		if st.stan == "grywalna" then
			przycisk(k, "Graj", T.graj, 13, 50, 120, U.przycisk_maly_px, KOL.dobrze, function()
				wybierz(st.id)
			end)
		else
			napis(k, "WProjekcie", T.w_projekcie, "maly", 4, 62, 138, 20, KOL.szary)
			k.BackgroundTransparency = 0.35
		end
	end
end

-- przyciski panelu startu i podsumowania (po utworzeniu wyboru)
przycisk(ui.start, "InnaGra", T.inna_gra, 10, 72, 116, U.przycisk_maly_px, KOL.szary, function()
	pokazWybor("stanowisko")
end)
przycisk(ui.start, "Start", D.sterowanie.start.napis, 138, 70, 124, U.przycisk_px, KOL.dobrze, wyslijStart, "duzy")
przycisk(ui.start, "Wyjdz", T.wyjdz, 274, 72, 116, U.przycisk_maly_px, KOL.zle, wyslijWyjdz)
przycisk(ui.koniec, "JeszczeRaz", T.jeszcze_raz, 10, 176, 150, U.przycisk_maly_px, KOL.dobrze, wyslijStart)
przycisk(ui.koniec, "InnaGra", T.inna_gra, 172, 176, 112, U.przycisk_maly_px, KOL.szary, function()
	pokazWybor("podsumowanie")
end)
przycisk(ui.koniec, "Wyjdz", T.wyjdz, 296, 176, 94, U.przycisk_maly_px, KOL.zle, wyslijWyjdz)

-- wybór i komunikat nad wszystkim (ZIndexBehavior.Sibling: później dodany = wyżej)
ui.wybor.Parent = nil
ui.wybor.Parent = korzen
ui.toast.Parent = nil
ui.toast.Parent = korzen

------------------------------------------------------------------ skala UI (baza 667 × 375; min. 44 px przycisku, 12 pt tekstu)
local function odswiezSkale()
	local cam = workspace.CurrentCamera
	local w, h = cam.ViewportSize.X, cam.ViewportSize.Y
	local em = kontener:GetAttribute("EmulacjaEkranu")
	-- obszar okien w pikselach widoku kamery (dla warstwy komiksowej i kadru zbliżenia): ScreenGui omija pasek Robloxa
	-- i wycięcia ekranu, a położenia okien liczą się od końca paska — stąd wstawka
	local wstawka = GuiService:GetGuiInset()
	local ox, oy = gui.AbsolutePosition.X + wstawka.X, gui.AbsolutePosition.Y + wstawka.Y
	local osz, owy = gui.AbsoluteSize.X, gui.AbsoluteSize.Y
	if osz < 1 or owy < 1 then
		-- ekran okien jeszcze niezmierzony (pierwsza klatka): cały widok pod paskiem Robloxa
		ox, oy = wstawka.X, wstawka.Y
		osz, owy = math.max(1, w - wstawka.X), math.max(1, h - wstawka.Y)
	end
	uklad.wsp = 1
	if typeof(em) == "Vector2" and em.X > 0 and em.Y > 0 then
		-- ekran telefonu em (punkty) bez paska Robloxa, wpisany w obszar okna pod paskiem
		local wys = em.Y - U.pasek_gorny_pt
		local k = math.min(osz / em.X, owy / wys)
		korzen.AnchorPoint = Vector2.new(0.5, 0.5)
		korzen.Position = UDim2.fromScale(0.5, 0.5)
		korzen.Size = UDim2.fromOffset(em.X, wys)
		skalaKorzenia.Scale = k
		-- kadr 3D jak na tym telefonie: jego ekran jest środkową częścią okna, więc kamera okna dostaje szerszy kąt
		-- (Kam.katOkna) — w prostokącie telefonu widać wtedy to samo, co na telefonie
		uklad.wsp = math.max(1, h / (em.Y * k))
		ox, oy = ox + (osz - em.X * k) / 2, oy + (owy - wys * k) / 2
		osz, owy = em.X * k, wys * k
		w, h = em.X, em.Y
	else
		korzen.AnchorPoint = Vector2.zero
		korzen.Position = UDim2.fromScale(0, 0)
		korzen.Size = UDim2.fromScale(1, 1)
		skalaKorzenia.Scale = 1
	end
	local s = L.skalaUI(D, w, h)
	for _, sk in skale do
		sk.Scale = s
	end
	local ks = skalaKorzenia.Scale
	skalaPierscieni.Scale = s * ks
	uklad.skala = s * ks
	uklad.s = s
	uklad.obszar = { ox, oy, ox + osz, oy + owy }
	-- przesunięcia (Position) nie skalują się z UIScale: podpowiedź obrazkowa nad panelem startu, a panel rundy,
	-- przycisk przerwania i przyciski gry — z L.ukladUI (obszar GUI po pasku Robloxa i wycięciach ekranu).
	-- W odliczaniu panel startu jest schowany, więc podpowiedź schodzi na dół: środek ekranu zostaje dla dojazdu kamery
	if stan.ekran == "runda" and stan.przedStartem then
		ui.obrazek.Position = UDim2.new(0.5, 0, 1, -8)
	else
		ui.obrazek.Position = UDim2.new(0.5, 0, 1, -8 - (ui.start.Size.Y.Offset + 8) * s)
	end
	local gw, gh = osz / ks, owy / ks
	-- zbliżenie po rundzie: postać stoi w środku wolnego pasa na lewo od karty podsumowania (ułamek szerokości widoku)
	local kartaLewa = gw - KX.karta.margines_px - ui.koniec.Size.X.Offset * s
	uklad.fx = (ox + kartaLewa * ks * KA.final.postac_w_wolnym) / cam.ViewportSize.X
	uklad.aspekt = cam.ViewportSize.X / cam.ViewportSize.Y * uklad.wsp
	for nazwa, r in L.ukladUI(D, stan.gra or "sila", gw, gh, s) do
		local p = ui.wUkladzie[nazwa]
		if p then
			p.AnchorPoint = Vector2.zero
			p.Position = UDim2.fromOffset(r[1], r[2])
		end
	end
	-- przyciski gier, których nie ma w układzie bieżącej gry, i tak są schowane; ustawiamy wszystkie raz na grę
	for _, gra in { "sila", "pancerz", "kondycja", "zrecznosc", "inteligencja", "szczescie" } do
		if gra ~= stan.gra then
			for nazwa, r in L.ukladUI(D, gra, gw, gh, s) do
				local p = ui.wUkladzie[nazwa]
				if p and nazwa ~= "status" and nazwa ~= "przerwij" then
					p.Position = UDim2.fromOffset(r[1], r[2])
				end
			end
		end
	end
end
odswiezSkale()
workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(odswiezSkale)
gui:GetPropertyChangedSignal("AbsoluteSize"):Connect(odswiezSkale) -- obszar okien (pasek, wycięcia) znany albo zmieniony
kontener:GetAttributeChangedSignal("EmulacjaEkranu"):Connect(odswiezSkale)

------------------------------------------------------------------ klawisze, kamera, dotyk
local AKCJA = "TreningProbaKlawisze"
local mapaGry, mapaStart, mapaWyjdz = {}, {}, {}
local dotykPrzed = nil

local function obsluzKlawisz(_, stanWejscia, wejscie)
	if stanWejscia ~= Enum.UserInputState.Begin then
		return Enum.ContextActionResult.Sink
	end
	local kod = wejscie.KeyCode.Name
	if stan.wybor then
		return Enum.ContextActionResult.Sink
	end
	if stan.ekran == "runda" then
		local a = mapaGry[kod]
		if a then
			nacisnij(a)
		end
	elseif stan.ekran == "stanowisko" or stan.ekran == "podsumowanie" then
		if mapaStart[kod] then
			wyslijStart()
		elseif mapaWyjdz[kod] then
			wyslijWyjdz()
		end
	end
	return Enum.ContextActionResult.Sink
end

local function odepnij()
	ContextActionService:UnbindAction(AKCJA)
end

local function przypnij(gra)
	odepnij()
	mapaGry, mapaStart, mapaWyjdz = {}, {}, {}
	local wszystkie, byly = {}, {}
	local function dodaj(n)
		if not byly[n] and Enum.KeyCode[n] then
			byly[n] = true
			table.insert(wszystkie, Enum.KeyCode[n])
		end
	end
	local G = D.gry[gra]
	for _, a in (G.przyciski or G.akcje) do
		local s = D.sterowanie[a]
		for _, n in s.klawisze do
			mapaGry[n] = a
			dodaj(n)
		end
		for _, n in s.pad do
			mapaGry[n] = a
			dodaj(n)
		end
	end
	for _, lista in { { D.sterowanie.start, mapaStart }, { D.sterowanie.wyjdz, mapaWyjdz } } do
		for _, n in lista[1].klawisze do
			lista[2][n] = true
			dodaj(n)
		end
		for _, n in lista[1].pad do
			lista[2][n] = true
			dodaj(n)
		end
	end
	for _, n in D.sterowanie.blokuj_ruch do
		dodaj(n)
	end
	ContextActionService:BindActionAtPriority(AKCJA, obsluzKlawisz, false, Enum.ContextActionPriority.High.Value + 50, table.unpack(wszystkie))
end

local function kameraNaStanowisko(gra)
	local cam = workspace.CurrentCamera
	if kam.przed == nil then
		kam.przed = { kat = cam.FieldOfView } -- kąt widzenia gracza sprzed stanowiska (oddajemy przy zejściu)
	end
	cam.CameraType = Enum.CameraType.Scriptable
	kam.uj = "stanowisko"
	kam.od = nil
	kam.start = os.clock()
	kam.wstrzasSila = 0
	table.clear(kam.zawezenia)
	local u = Kam.stanowisko(D, gra, 0)
	kam.ostatnie = u
	cam.CFrame = CFrame.lookAt(v3(u.oko), v3(u.cel))
	cam.FieldOfView = math.clamp(Kam.katOkna(u.kat, uklad.wsp or 1), 5, 120)
end

local function kameraPrzywroc()
	local cam = workspace.CurrentCamera
	cam.CameraType = Enum.CameraType.Custom
	if kam.przed then
		cam.FieldOfView = kam.przed.kat
		kam.przed = nil
	end
	local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
	if hum then
		cam.CameraSubject = hum
	end
end

-- kamera co klatkę: ujęcie z rachunku KameraTreningu, płynne przejście od poprzedniego kadru, zawężenie kąta po
-- trafieniu (tylko w ujęciu gry) i drżenie; t = czas serwera (odliczanie), dt = czas klatki
local function kameraKlatka(t, dt, gra)
	local cam = workspace.CurrentCamera
	if stan.ekran == "brak" or cam.CameraType ~= Enum.CameraType.Scriptable then
		return
	end
	local c = os.clock()
	local u
	if kam.uj == "odliczanie" and stan.runda then
		u = Kam.odliczanie(D, gra, stan.runda.t0 - t)
	elseif kam.uj == "final" and stan.final then
		u = Kam.final(D, gra, stan.final.korzen, uklad.fx or 0.25, uklad.aspekt or 1.78, c - kam.start)
	elseif kam.uj == "gra" then
		u = Kam.gra(D, gra)
	else
		u = Kam.stanowisko(D, gra, c - kam.start)
	end
	if kam.od then
		local f = (c - kam.przejscieStart) / kam.przejscie
		if f >= 1 then
			kam.od = nil
		else
			u = Kam.przejscie(kam.od, u, f)
		end
	end
	kam.ostatnie = u
	local kat = u.kat
	if kam.uj == "gra" then
		local z = 0
		for rodzaj, od in kam.zawezenia do
			z = math.max(z, Kam.zawezenie(D, rodzaj, c - od))
		end
		kat -= z
	end
	local drzenie = Vector3.zero
	if kam.wstrzasSila > 0 then
		kam.wstrzasWiek += dt
		local amp = Kam.wstrzas(D, kam.wstrzasSila, kam.wstrzasWiek)
		if amp <= 0 then
			kam.wstrzasSila = 0
		else
			drzenie = Vector3.new(losowe:NextNumber(-1, 1), losowe:NextNumber(-1, 1), losowe:NextNumber(-1, 1)) * amp
		end
	end
	cam.CFrame = CFrame.lookAt(v3(u.oko) + drzenie, v3(u.cel) + drzenie * 0.35)
	cam.FieldOfView = math.clamp(Kam.katOkna(kat, uklad.wsp or 1), 5, 120)
end

-- miecz i tarcza wiszą w stałym miejscu stanowiska — w zbliżeniu po rundzie (postać obraca się do kamery) są
-- schowane, wracają z kolejną rundą; koszyk Koniczyn idzie za postacią, więc zostaje
local function pokazModelGracza(widac)
	if modelGracza and stan.gra ~= "szczescie" then
		modelGracza.Parent = if widac then efekty else nil
	end
end

local function usunModelGracza()
	if modelGracza then
		local model = modelGracza
		modelGracza = nil
		model:Destroy()
	end
end

-- po rundzie (i przy zejściu): postać bez przesunięć stawów, bez biegu i radości, koszyk na środku; bohater klasy
-- wraca do własnych klipów
local function spokojPostaci()
	stan.unik = nil
	stan.ruchToru = nil
	zatrzymajBieg()
	zatrzymajRadosc()
	przywrocStawy()
	spokojBohatera()
end

-- postać twarzą w stronę gry (po zbliżeniu patrzyła w kamerę) — przed kolejną rundą na tym samym stanowisku
local function postacDoGry(gra)
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp then
		return
	end
	local W = D.swiat[gra]
	local kier = Vector3.new(W.patrz[1] - W.podest[1], 0, W.patrz[3] - W.podest[3])
	if kier.Magnitude < 0.1 then
		return
	end
	postac:PivotTo(CFrame.lookAt(hrp.Position, hrp.Position + kier.Unit))
	hrp.AssemblyLinearVelocity = Vector3.zero
	hrp.AssemblyAngularVelocity = Vector3.zero
end

--[[ Koniec rundy jak finał walki: kamera robi zbliżenie na postać (karta podsumowania stoi po prawej), postać obraca
	się do kamery; gdy runda dała punkt statystyki — postać się cieszy i leci konfetti (większe po rundzie bez pudła,
	wtedy też napis „BEZ PUDŁA!”). a = podsumowanie z serwera. ]]
local function zacznijFinal(a)
	local gra = stan.gra
	local W = D.swiat[gra]
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local korzen = if hrp then hrp.Position else v3(W.podest) + Vector3.new(0, KA.final.korzen_nad_ziemia, 0)
	local kier = Kam.kierunekFinalu(D, gra, 0)
	local F = { korzen = { korzen.X, korzen.Y, korzen.Z }, t = os.clock(), obrot = false, postac = postac }
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	-- obrót tylko żywej postaci (runda przerwana resetem postaci też kończy się podsumowaniem)
	if hrp and hum and hum.Health > 0 then
		F.cfOd = hrp.CFrame
		F.cfDo = CFrame.lookAt(hrp.Position, hrp.Position + Vector3.new(kier[1], 0, kier[3]))
		F.obrot = true
	end
	stan.final = F
	pokazModelGracza(false)
	-- słowa z rundy nie zostają pod kartą podsumowania (na telefonie karta zajmuje ponad połowę ekranu)
	komiks:wyczysc()
	stan.duzyNapis = nil
	ujecie("final", KA.final.przejscie_s)
	stan.konfetti = 0
	if (a.suma or 0) <= 0 or not F.obrot then
		return -- bez punktu statystyki (albo bez żywej postaci) nie ma świętowania
	end
	local idealna = not a.przerwana and (a.trafienia or 0) > 0 and (a.pudla or 0) + (a.puste or 0) == 0
	zacznijRadosc()
	-- konfetti, gdy kamera jest już w drodze do postaci: salwy z lewej i z prawej strony względem kamery zbliżenia
	task.delay(KA.final.przejscie_s * 0.5, function()
		if stan.final ~= F or stan.ekran ~= "podsumowanie" or not fx then
			return
		end
		local ziemia = Vector3.new(korzen.X, korzen.Y - KA.final.korzen_nad_ziemia, korzen.Z)
		stan.konfetti = fx:konfetti(ziemia, Vector3.new(kier[3], 0, -kier[1]), EF.konfetti, idealna)
		wybuch("zloto", ziemia + Vector3.new(0, 5.5, 0), 1.2)
		if idealna and uklad.obszar then
			local o = uklad.obszar
			local x = (uklad.fx or 0.25) * workspace.CurrentCamera.ViewportSize.X
			napisKomiks(T.bez_pudla, "seria", nil, { ekran = Vector2.new(x, o[2] + (o[4] - o[2]) * 0.17) })
		end
	end)
end

------------------------------------------------------------------ inne ekrany schowane na stanowisku (jak w walce)
-- HUD gry i ekrany innych pakietów znikają, gdy gracz stoi na stanowisku (kamera stała, runda, podsumowanie), i wracają
-- przy zejściu — także po resecie postaci (CharacterAdded → zejdzZeStanowiska). Chowamy tylko to, co było włączone, i
-- przywracamy tylko to, co sami schowaliśmy; ekran włączony w tym czasie przez inny skrypt też chowamy (i oddajemy).
local POMIJANE_EKRANY = { TouchGui = true, Freecam = true, LoadingScreen = true, ProximityPrompts = true }
local schowaneEkrany = nil -- { [ScreenGui]: true } albo nil, gdy nic nie jest schowane
local polaczeniaEkranow = {}

local function schowajInneEkrany()
	if schowaneEkrany then
		return
	end
	schowaneEkrany = {}
	local function sprawdz(e)
		if schowaneEkrany and e:IsA("ScreenGui") and e ~= gui and e ~= guiKomiks and not POMIJANE_EKRANY[e.Name]
			and e.Enabled then
			schowaneEkrany[e] = true
			e.Enabled = false
		end
	end
	local function pilnuj(e)
		if e:IsA("ScreenGui") and e ~= gui and e ~= guiKomiks then
			sprawdz(e)
			table.insert(polaczeniaEkranow, e:GetPropertyChangedSignal("Enabled"):Connect(function()
				sprawdz(e)
			end))
		end
	end
	for _, e in ekrany:GetChildren() do
		pilnuj(e)
	end
	table.insert(polaczeniaEkranow, ekrany.ChildAdded:Connect(pilnuj))
end

local function przywrocInneEkrany()
	for _, p in polaczeniaEkranow do
		p:Disconnect()
	end
	table.clear(polaczeniaEkranow)
	local byly = schowaneEkrany
	schowaneEkrany = nil
	if byly then
		for e in byly do
			if e.Parent then
				e.Enabled = true
			end
		end
	end
end

local function wejdzNaStanowisko(gra)
	usunWizualne()
	usunModelGracza()
	spokojPostaci()
	przywrocArene()
	if not arena.piesc or not arena.ramie or not arena.klody then
		zapamietajArene() -- arena jest Persistent, ale gdyby nie była jeszcze wczytana przy starcie skryptu
	end
	stan.gra = gra
	stan.runda = nil
	stan.R = nil
	stan.lokalne = {}
	stan.wybor = false
	stan.przedStartem = false
	stan.final = nil
	stan.liczenie = nil
	stan.ekran = "stanowisko"
	-- nowe stanowisko: efekty od zera (i ponowne sprawdzenie modułu walki), haczyk bohatera pytany od nowa
	sprzatnijEfekty()
	efektyStanowiska()
	hak.zawieszony = false
	hak.sprawdzono = -math.huge
	schowajInneEkrany()
	przypnij(gra)
	if dotykPrzed == nil then
		dotykPrzed = GuiService.TouchControlsEnabled
	end
	GuiService.TouchControlsEnabled = false
	odswiezSkale()
	kameraNaStanowisko(gra)
	if gra == "sila" then
		modelGracza = zbudujMiecz()
	elseif gra == "pancerz" then
		modelGracza = zbudujTarcze()
	elseif gra == "szczescie" then
		modelGracza = zbudujKoszyk()
		stan.tor = table.find(D.gry.szczescie.tory, D.gry.szczescie.start_tor) or 2
	end
	ui.opis.Text = T["sterowanie_" .. gra] or ""
	obrazek(gra)
	odswiezSkale()
	odswiezStatus()
	ui.czas.Text = string.format("%d:%02d", math.floor(D.runda.dlugosc_s / 60), D.runda.dlugosc_s % 60)
	pokazWidocznosc()
end

local function zejdzZeStanowiska()
	odepnij()
	usunWizualne()
	usunModelGracza()
	spokojPostaci()
	przywrocArene()
	sprzatnijEfekty()
	if dotykPrzed ~= nil then
		GuiService.TouchControlsEnabled = dotykPrzed
		dotykPrzed = nil
	end
	kameraPrzywroc()
	przywrocInneEkrany()
	stan.gra = nil
	stan.runda = nil
	stan.R = nil
	stan.final = nil
	stan.liczenie = nil
	stan.ekran = "brak"
	stan.wybor = false
	stan.przedStartem = false
	pokazWidocznosc()
end

------------------------------------------------------------------ klatka: odliczanie, rysowanie mini-gry, kamera
-- postać półprzezroczysta u siebie tylko w Sile: tam kamera stoi za plecami i postać jest pośrodku czterech stref.
-- W Pancerzu i Runach kamera w stylu walki patrzy z boku — postać nie zasłania pola gry (test 5f) i zostaje pełna
local PRZEZROCZYSTE = { sila = true }

local function wyglad(t, dt)
	local gra = stan.gra
	local W = gra and D.swiat[gra]
	przezroczystoscPostaci(if W and stan.ekran == "runda" and PRZEZROCZYSTE[gra] then U.przezroczystosc_postaci else 0)
	if not W then
		return
	end
	local Rd = if stan.ekran == "runda" then stan.runda else nil
	local bohater = bohaterAktywny()
	-- Koniczyny: koszyk nad głową przez cały pobyt na stanowisku — bohater klasy: klip „ręce w górę”, awatar: barki
	if gra == "szczescie" then
		if bohater then
			if stan.radosc == nil then
				klipBohatera(BH.klipy.rece)
			end
		else
			ustawStawLokalnie("RightShoulder", CFrame.Angles(math.pi, 0, 0))
			ustawStawLokalnie("LeftShoulder", CFrame.Angles(math.pi, 0, 0))
		end
	end
	-- radość bohatera klasy: jego wiwat gra raz, więc póki trwa podsumowanie, zamawiamy go od nowa co radosc_co_s
	if stan.radosc and bohater and os.clock() - (stan.radoscBohatera or 0) > BH.radosc_co_s then
		stan.radoscBohatera = os.clock()
		hak.klip = nil
		klipBohatera(BH.klipy.radosc)
	end
	-- radość awatara, gdy nie ma animacji „cheer”: ręce w górę i podskoki (stawy tylko u siebie)
	if stan.radosc and radosc == nil and not bohater then
		ustawStawLokalnie("RightShoulder", CFrame.Angles(math.pi, 0, 0))
		ustawStawLokalnie("LeftShoulder", CFrame.Angles(math.pi, 0, 0))
		ustawStaw(nil, CFrame.new(0, 0.9 * math.abs(math.sin((os.clock() - stan.radosc) * 5)), 0))
	end
	local h = GRY[gra]
	if h and h.klatka then
		h.klatka(t, Rd, W)
	end
	-- po rundzie: postać obraca się twarzą do kamery zbliżenia (jak zwycięzca w finale walki)
	local F = stan.final
	if F and F.obrot then
		local postac = gracz.Character
		local hrp = postac and postac == F.postac and postac:FindFirstChild("HumanoidRootPart")
		local f = math.clamp((os.clock() - F.t) / KA.final.obrot_postaci_s, 0, 1)
		if hrp then
			postac:PivotTo(F.cfOd:Lerp(F.cfDo, Kam.gladko(f)))
			hrp.AssemblyLinearVelocity = Vector3.zero
			hrp.AssemblyAngularVelocity = Vector3.zero
		end
		if f >= 1 or not hrp then
			F.obrot = false
		end
	end
	if fx then
		fx:krok(dt)
	end
	komiks:krok(dt)
	kameraKlatka(t, dt, gra)
	-- karta podsumowania: liczby rosną od zera (jak łup na karcie wyniku walki)
	local Lz = stan.liczenie
	if Lz then
		local f = Kam.gladko((os.clock() - Lz.t) / KX.karta.liczenie_s)
		local a = Lz.a
		ui.k1.Text = string.format("Trafienia %d · pudła %d · celność %d%%", math.floor((a.trafienia or 0) * f + 0.5),
			math.floor(((a.pudla or 0) + (a.puste or 0)) * f + 0.5), math.floor((a.celnosc or 0) * f + 0.5))
		ui.k3.Text = string.format("%s +%d", Lz.nazwa, math.floor((a.suma or 0) * f + 0.5))
		if f >= 1 then
			stan.liczenie = nil
		end
	end
	if not Rd then
		return
	end
	-- odliczanie i czas
	local przed = t < Rd.t0
	if przed ~= stan.przedStartem then
		stan.przedStartem = przed
		if not przed then
			ujecie("gra", 0) -- dojazd skończył się przed startem: kamera stoi w ujęciu gry
		end
		odswiezSkale()
		pokazWidocznosc()
	end
	-- liczby odliczania i „START!” na środku ekranu (ui.komiks.licznik_miejsce): w odliczaniu nic się nie rozgrywa
	local o = uklad.obszar
	local srodek = if o then Vector2.new(o[1] + (o[3] - o[1]) * KX.licznik_miejsce[1], o[2] + (o[4] - o[2]) * KX.licznik_miejsce[2])
		else nil
	if przed then
		local n = math.ceil(Rd.t0 - t)
		if n ~= stan.ostatnieOdliczanie then
			stan.ostatnieOdliczanie = n
			napisKomiks(tostring(n), "licznik", nil, { ekran = srodek })
			graj("nuta", 1)
		end
	elseif stan.ostatnieOdliczanie ~= 0 then
		stan.ostatnieOdliczanie = 0
		napisKomiks(D.sterowanie.start.napis .. "!", "start", nil, { ekran = srodek })
		graj("nuta", 2)
	end
	local zostalo = math.max(0, Rd.t0 + Rd.dlugosc - math.max(t, Rd.t0))
	ui.czas.Text = string.format("%d:%02d", math.floor(zostalo / 60), math.floor(zostalo % 60))
	-- zdarzenia, których nie odbito (lokalnie, z tym samym zapasem co serwer; Koniczyny — od razu przy upadku)
	if stan.R and not stan.R.koniec then
		local zapas = if D.gry[gra].typ == "lapanie" then 0 else nil
		for _, w in L.przeterminowane(D, stan.R, t, zapas) do
			efekt(w)
		end
	end
end
RunService.RenderStepped:Connect(function(dt)
	wyglad(teraz(), dt)
end)

------------------------------------------------------------------ wiadomości z serwera
local function zapiszWynik(w)
	table.insert(stan.wyniki, w)
	while #stan.wyniki > 16 do
		table.remove(stan.wyniki, 1)
	end
end

zdalne.OnClientEvent:Connect(function(rodzaj, a, b2)
	if rodzaj == "wybor" then
		pokazWybor(a)
	elseif rodzaj == "odmowa" then
		komunikat(b2 or tostring(a))
	elseif rodzaj == "przybycie" then
		wejdzNaStanowisko(a)
	elseif rodzaj == "runda" then
		if stan.gra ~= a.gra then
			wejdzNaStanowisko(a.gra)
		end
		usunWizualne()
		spokojPostaci()
		przywrocArene()
		if stan.final then
			postacDoGry(a.gra) -- po zbliżeniu postać patrzyła w kamerę
		end
		pokazModelGracza(true)
		stan.final = nil
		stan.liczenie = nil
		stan.runda = a
		stan.R = L.nowaRunda(D, a.gra, a.id, a.t0, a.plan, { pasek = a.pasek, W = a.W, pula = a.pula })
		stan.lokalne = {}
		stan.ostatnieOdliczanie = nil
		stan.beben = 0
		stan.krok = {}
		stan.runyNacisk = {}
		stan.pokazGrany = nil
		stan.pokazNapis = nil
		stan.wybor = false
		stan.przedStartem = true
		stan.ekran = "runda"
		if D.gry[a.gra].typ == "lapanie" then
			ustawTor(table.find(D.gry[a.gra].tory, D.gry[a.gra].start_tor) or 2, true)
		end
		-- odliczanie: kamera przechodzi do ujęcia „start” i dojeżdża do kamery gry (jak wjazd kamery przed walką)
		table.clear(kam.zawezenia)
		ujecie("odliczanie", 0.35)
		odswiezSkale()
		odswiezStatus()
		pokazWidocznosc()
	elseif rodzaj == "wynik" then
		zapiszWynik(a)
		local R = stan.R
		if R and stan.runda and stan.runda.id == a.id then
			if a.nr ~= nil and stan.lokalne[a.nr] ~= nil and stan.lokalne[a.nr] ~= a.trafienie then
				stan.rozbieznosci += 1
			end
			local G = D.gry[R.gra]
			if G.typ == "sekwencja" then
				-- stan sekwencji z serwera (gdyby lokalna kopia się rozjechała, np. odrzucony spam)
				if type(a.pokazOd) == "number" then
					R.dl, R.poz, R.offset, R.pokazOd, R.pokazDo = a.dl, a.poz, a.offset, a.pokazOd, a.pokazDo
					R.pokazy, R.ostatnia = a.pokazy, a.ostatnia
					L.tempoPokazu(D, R)
				end
			elseif a.nr ~= nil and R.rozstrzygniete[a.nr] == nil then
				R.rozstrzygniete[a.nr] = if a.trafienie then "T" else "P"
				if a.tor ~= nil and R.tory and R.tory[a.nr] == nil then
					R.tory[a.nr] = { a.tor, a.tor }
				end
			end
			R.seria = a.seria
			R.suma = a.suma
			if type(a.pasek) == "number" then
				R.pasek = a.pasek
				R.W = (stan.runda.W or 0) + a.suma
			end
			if a.nr ~= nil and stan.lokalne[a.nr] == nil then
				efekt(a)
			end
			odswiezStatus()
		end
	elseif rodzaj == "koniec" then
		stan.podsumowanie = a
		if stan.R then
			stan.R.koniec = true
			stan.R.seria = 0
		end
		usunWizualne()
		spokojPostaci()
		przywrocArene()
		local st = L.statystyka(D, a.gra)
		ui.kTytul.Text = if a.przerwana then T.przerwana else T.koniec
		-- liczone z rozstrzygniętych prób (trafienia + pudła + naciśnięcia w powietrze), nie ze wszystkich zdarzeń
		-- planu — po przerwaniu rundy „2 z 43 (15%)” było sprzeczne (raport przejścia gry 17.11.2026, M8)
		ui.k1.Text = string.format("Trafienia %d · pudła %d · celność %d%%", a.trafienia or 0, (a.pudla or 0) + (a.puste or 0),
			a.celnosc or 0)
		if a.najdluzszaSekwencja ~= nil then
			ui.k2.Text = string.format(T.najdluzsze_zaklecie, a.najdluzszaSekwencja)
		elseif a.zlapane ~= nil then
			ui.k2.Text = string.format(T.zlapane, a.zlapane)
		else
			ui.k2.Text = string.format("Najdłuższa seria %d", a.najdluzsza)
		end
		ui.k3.Text = string.format("%s +%d", st.nazwa, a.suma)
		ui.k3.FontFace = komiks:czcionkaDla(ui.k3.Text)
		ui.k3.TextColor3 = kolor(if (a.suma or 0) > 0 then KX.kolory.zielony else KOL.szary)
		ui.k4.Text = string.format("Do następnego punktu: %d/%d · %s łącznie: +%d", math.floor(a.pasek or 0),
			math.ceil(a.prog or 0), st.nazwa, a.sesja or 0)
		stan.ekran = "podsumowanie"
		stan.przedStartem = false
		-- karta wyskakuje jak karta wyniku walki, liczby rosną od zera; kamera robi zbliżenie na postać
		stan.liczenie = { t = os.clock(), a = a, nazwa = st.nazwa }
		odswiezSkale()
		skalaKarty.Scale = (uklad.s or 1) * KX.karta.wejscie_od
		TweenService:Create(skalaKarty, TweenInfo.new(KX.karta.wejscie_s, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
			{ Scale = uklad.s or 1 }):Play()
		zacznijFinal(a)
		if (a.trafienia or 0) == 0 or not grajZdarzenie(DK.koniec) then
			melodia(D.dzwieki.melodia_koniec)
		end
		odswiezStatus()
		pokazWidocznosc()
	elseif rodzaj == "wyjscie" then
		zejdzZeStanowiska()
	end
end)

gracz.CharacterAdded:Connect(function()
	table.clear(stawy) -- nowa postać ma własne stawy (stare zniknęły razem z postacią)
	table.clear(znaneStawy)
	bieg = nil
	radosc = nil
	stan.radosc = nil
	przezroczystoscTeraz = 0
	if stan.gra then
		zejdzZeStanowiska()
	end
end)

------------------------------------------------------------------ E przy trenerze w bazarze: zdarzenie OknoMiejsca
-- BindableEvent w ReplicatedStorage (tworzy go pierwszy, kto potrzebuje — bazar albo ten skrypt); słuchamy każdego
-- o tej nazwie, gdyby dwa skrypty utworzyły go naraz. Atrybut "training_center" = true wyłącza dymek bazaru
-- „Trener: mini-gry w budowie”, póki działa ten tymczasowy wybór.
local zdarzeniaOkien = {}
local function tymczasowyWlaczony()
	return kontener:GetAttribute("WyborTymczasowy") ~= false
end

local function podepnijOkna(okna)
	if zdarzeniaOkien[okna] or okna.Name ~= D.zdarzenie_okien or not okna:IsA("BindableEvent") then
		return
	end
	zdarzeniaOkien[okna] = true
	okna.Event:Connect(function(id)
		if id == D.id_miejsca_bazaru and tymczasowyWlaczony() then
			pokazWybor("bazar")
		end
	end)
	if tymczasowyWlaczony() then
		okna:SetAttribute(D.id_miejsca_bazaru, true)
	end
end
for _, c in ReplicatedStorage:GetChildren() do
	podepnijOkna(c)
end
ReplicatedStorage.ChildAdded:Connect(podepnijOkna)
if not ReplicatedStorage:FindFirstChild(D.zdarzenie_okien) then
	local nowe = Instance.new("BindableEvent")
	nowe.Name = D.zdarzenie_okien
	nowe.Parent = ReplicatedStorage
end

-- uchwyt dla docelowego okna Pawła (klient): workspace.TreningProba.Sygnaly.WybierzGre:Invoke("sila")
wybierzF.OnInvoke = function(gra)
	return wybierz(gra)
end

------------------------------------------------------------------ haczyk testowy
-- autogra: naciśnięcia tą samą drogą co klawisz; gry czasowe — w zaplanowanych chwilach; Runy i Koniczyny — pętla, która
-- patrzy na stan rundy jak gracz (powtarza pokazane runy, idzie pod koniczynę, schodzi spod kamienia)
local function autograj(celnosc, blokujZmylki)
	local Rd = stan.runda
	if not Rd or stan.ekran ~= "runda" then
		return 0
	end
	local G = D.gry[stan.gra]
	if G.typ == "sekwencja" then
		task.spawn(function()
			local ostatnio = 0
			while stan.runda == Rd and stan.R and not stan.R.koniec do
				local R = stan.R
				local r = teraz() - Rd.t0
				if r >= R.pokazDo + 0.15 and R.poz < R.dl and os.clock() - ostatnio > 0.32 then
					local e = Rd.plan[R.offset + R.poz + 1]
					if e then
						local w = e.wartosc
						if losowe:NextNumber() > (celnosc or 1) then
							w = G.runy[(table.find(G.runy, w) % #G.runy) + 1]
						end
						ostatnio = os.clock()
						nacisnij(w)
					end
				end
				task.wait(0.05)
			end
		end)
		return -1
	elseif G.typ == "lapanie" then
		task.spawn(function()
			local ostatnio = 0
			while stan.runda == Rd and stan.R and not stan.R.koniec do
				local R = stan.R
				local t = teraz()
				local cel = nil
				for _, e in Rd.plan do
					local ti = Rd.t0 + e.t
					if R.rozstrzygniete[e.nr] == nil and t >= ti - G.lot_s + 0.05 and t < ti then
						local k = L.toryZdarzenia(D, R, e)
						if e.wartosc ~= "kamien" then
							if losowe:NextNumber() <= (celnosc or 1) then
								cel = k
							end
							break
						elseif k == stan.tor and ti - t < 0.6 then
							cel = if stan.tor == 1 then 2 else stan.tor - 1
							break
						end
					end
				end
				-- nie wchodzi na tor, na który za chwilę spadnie kamień (jak gracz, który widzi jego cień)
				local nastepny = if cel and cel < stan.tor then stan.tor - 1 else stan.tor + 1
				local kamienTuz = false
				for _, e in Rd.plan do
					local w = R.tory[e.nr]
					local dt = Rd.t0 + e.t - t
					if e.wartosc == "kamien" and R.rozstrzygniete[e.nr] == nil and w and w[1] == nastepny and dt >= 0 and dt < 0.3 then
						kamienTuz = true
					end
				end
				if cel and cel ~= stan.tor and os.clock() - ostatnio > 0.2 and not kamienTuz then
					ostatnio = os.clock()
					nacisnij(if cel < stan.tor then "w_lewo" else "w_prawo")
				end
				task.wait(0.05)
			end
		end)
		return -1
	end
	local n = 0
	for _, e in Rd.plan do
		local akcja = if G.typ == "blok" then "blok" else L.odpowiedz(G, e.wartosc)
		if losowe:NextNumber() < (celnosc or 1) and (e.wartosc ~= "zmylka" or blokujZmylki) then
			n += 1
			task.delay(math.max(0, Rd.t0 + e.t - teraz()), function()
				if stan.runda == Rd then
					nacisnij(akcja)
				end
			end)
		end
	end
	return n
end

local function widoczny(o)
	if not gui.Enabled then
		return false
	end
	while o and o ~= gui do
		if o:IsA("GuiObject") and not o.Visible then
			return false
		end
		o = o.Parent
	end
	return o == gui
end

local function stanTestowy()
	local cam = workspace.CurrentCamera
	local minBaza, minTekst, minEkran = math.huge, math.huge, math.huge
	for _, p in przyciski do
		minBaza = math.min(minBaza, p.szer, p.wys)
		if widoczny(p.obiekt) then
			minEkran = math.min(minEkran, p.obiekt.AbsoluteSize.X, p.obiekt.AbsoluteSize.Y)
		end
	end
	for _, n in napisy do
		minTekst = math.min(minTekst, n.rozmiar)
	end
	for _, px in KX.rozmiary_px do
		minTekst = math.min(minTekst, px) -- napisy komiksowe też liczą się do najmniejszego tekstu
	end
	local kafelki, grywalne = 0, 0
	for _, k in ui.wybor:GetChildren() do
		if string.sub(k.Name, 1, 8) == "Kafelek_" then
			kafelki += 1
			if k:FindFirstChild("Graj") then
				grywalne += 1
			end
		end
	end
	local R = stan.R
	local zmienioneStawy = 0
	for j, c0 in stawy do
		if j.Parent and poza(j) ~= c0 then
			zmienioneStawy += 1
		end
	end
	local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
	return {
		ekran = stan.ekran, wybor = stan.wybor, zrodlo = stan.zrodlo, gra = stan.gra, guiWlaczone = gui.Enabled,
		schowaneEkrany = (function()
			local n = 0
			for _ in schowaneEkrany or {} do
				n += 1
			end
			return n
		end)(),
		runda = if stan.runda then { id = stan.runda.id, gra = stan.runda.gra, n = #stan.runda.plan, t0 = stan.runda.t0 } else nil,
		lokalnie = if R then {
			trafienia = R.trafienia, pudla = R.pudla, puste = R.puste, spam = R.spam, seria = R.seria, suma = R.suma,
			dl = R.dl, poz = R.poz, pokazOd = R.pokazOd, pokazDo = R.pokazDo, pokazy = R.pokazy,
		} else nil,
		wyniki = stan.wyniki, rozbieznosci = stan.rozbieznosci, podsumowanie = stan.podsumowanie,
		ui = {
			skala = L.skalaUI(D, cam.ViewportSize.X, cam.ViewportSize.Y), ekranPx = { cam.ViewportSize.X, cam.ViewportSize.Y },
			przyciskBazaMin = minBaza, tekstBazaMin = minTekst, przyciskNaEkranieMin = if minEkran < math.huge then minEkran else nil,
			przycisk667 = minBaza * L.skalaUI(D, 667, 375), tekst667 = minTekst * L.skalaUI(D, 667, 375),
			przycisk568 = minBaza * L.skalaUI(D, 568, 320), tekst568 = minTekst * L.skalaUI(D, 568, 320),
			obrazek = ui.obrazek.Visible,
			obrazekElementy = if stan.gra and ui.obrazki[stan.gra] then #ui.obrazki[stan.gra]:GetDescendants() else 0,
		},
		kamera = cam.CameraType.Name, dotyk = GuiService.TouchControlsEnabled,
		kafelki = kafelki, grywalne = grywalne, zdarzeniaOkien = (function()
			local n = 0
			for _ in zdarzeniaOkien do
				n += 1
			end
			return n
		end)(),
		tor = stan.tor, unik = stan.unik and stan.unik.rodzaj,
		-- ruch postaci: stawy awatara albo bohater klasy przez haczyk (przesunięcie / klip biegu)
		stawyZmienione = zmienioneStawy + (if hak.przesuniety then 1 else 0),
		stawyAwatara = zmienioneStawy, -- same stawy awatara (przy aktywnym bohaterze mają zostać nietknięte)
		radoscStawami = stan.radosc ~= nil and radosc == nil and not hak.aktywny, -- radość bez animacji: ręce i podskoki
		bieg = bieg ~= nil or hak.klip == BH.klipy.bieg,
		arkusz = arkusz() ~= false, pozycja = if hrp then { hrp.Position.X, hrp.Position.Y, hrp.Position.Z } else nil,
		przezroczystosc = przezroczystoscTeraz,
		-- wygląd jak w walce: ujęcie i kąt kamery, napisy komiksowe, efekty 3D, konfetti, bohater klasy
		kameraUjecie = kam.uj, kameraKat = cam.FieldOfView,
		kameraOko = { cam.CFrame.Position.X, cam.CFrame.Position.Y, cam.CFrame.Position.Z },
		kameraPatrzy = { cam.CFrame.LookVector.X, cam.CFrame.LookVector.Y, cam.CFrame.LookVector.Z },
		wspEmulacji = uklad.wsp, obszar = uklad.obszar, ulamekPostaci = uklad.fx,
		komiks = {
			naEkranie = komiks:ile(), pokazane = komiks.pokazane, zastepcze = komiks.zastepcze,
			czcionka = KX.czcionka, warstwa = guiKomiks.Enabled,
			ostatnie = (function()
				local lista = {}
				for _, n in komiks.napisy do
					table.insert(lista, { tekst = n.napis, styl = n.styl, x = n.x, y = n.y, komiksowa = n.komiksowa })
				end
				return lista
			end)(),
		},
		efekty = if fx then { zrodlo = fx.zrodlo, utworzono = fx:policz(), bledy = fx.bledy } else nil,
		czesciEfektow = #efekty:GetChildren(),
		konfetti = stan.konfetti, radosc = stan.radosc ~= nil, radoscAnimacja = radosc ~= nil,
		final = stan.final ~= nil, obrotPostaci = if hrp then { hrp.CFrame.LookVector.X, hrp.CFrame.LookVector.Z } else nil,
		bohater = { aktywny = hak.aktywny, klip = hak.klip, przesuniety = hak.przesuniety, wywolania = hak.wywolania,
			zawieszony = hak.zawieszony },
		pierscienie = { ui.pierscienie.Visible, ui.pierscienie.AbsolutePosition.X, ui.pierscienie.AbsolutePosition.Y },
		karta = { ui.koniec.AbsolutePosition.X, ui.koniec.AbsolutePosition.Y, ui.koniec.AbsoluteSize.X, ui.koniec.AbsoluteSize.Y },
	}
end

sterowanie.OnInvoke = function(polecenie, a, b3)
	if polecenie == "stan" then
		return stanTestowy()
	elseif polecenie == "wybor" then
		return pokazWybor(a or "test")
	elseif polecenie == "okno" then
		for okna in zdarzeniaOkien do
			okna:Fire(D.id_miejsca_bazaru, { nazwa = "Trener", postac = "Trener", akcja = "okno" })
		end
		return true
	elseif polecenie == "graj" then
		return wybierz(a)
	elseif polecenie == "start" then
		wyslijStart()
		return true
	elseif polecenie == "nacisnij" then
		return nacisnij(a)
	elseif polecenie == "autograj" then
		return autograj(a, b3)
	elseif polecenie == "zaplanuj" then
		-- a = { { nr = 2, w = "lewo", dt = 0 }, … }: naciśnięcia w chwili t0 + t zdarzenia nr + dt (ta sama droga co klawisz)
		local Rd = stan.runda
		if not Rd then
			return 0
		end
		local n = 0
		for _, p in a do
			local e = Rd.plan[p.nr]
			if e and e.t then
				n += 1
				task.delay(math.max(0, Rd.t0 + e.t + (p.dt or 0) - teraz()), function()
					if stan.runda == Rd then
						nacisnij(p.w)
					end
				end)
			end
		end
		return n
	elseif polecenie == "spam" then
		local id = stan.runda and stan.runda.id or 0
		for _ = 1, a or 1 do
			zdalne:FireServer("akcja", id, b3, teraz())
		end
		return a
	elseif polecenie == "surowe" then
		if stan.runda then
			zdalne:FireServer("akcja", stan.runda.id, a, teraz() + (b3 or 0))
		end
		return true
	elseif polecenie == "wyjdz" then
		wyslijWyjdz()
		return true
	elseif polecenie == "inna" then
		return pokazWybor("stanowisko")
	elseif polecenie == "dlugie_napisy" then
		stan.dlugieNapisy = a -- mnożnik życia napisów komiksowych (zrzuty); nil = zwykle
		return true
	elseif polecenie == "napis" then
		-- napis komiksowy w miejscu dużych napisów stanowiska (zrzuty i pomiar czcionki): a = tekst, b3 = styl
		local n = napisKomiks(tostring(a), b3 or "seria", nil)
		return n ~= nil and { komiksowa = n.komiksowa, x = n.x, y = n.y } or nil
	elseif polecenie == "konfetti" then
		-- konfetti przy postaci (zrzuty): a = true → wielkie
		local p0 = stopyPostaci()
		if not fx or not p0 then
			return 0
		end
		stan.konfetti = fx:konfetti(p0, workspace.CurrentCamera.CFrame.RightVector, EF.konfetti, a == true)
		return stan.konfetti
	elseif polecenie == "zamknij" then
		ukryjWybor()
		return true
	elseif polecenie == "przerwij" then
		przerwij()
		return true
	end
	return nil
end

zapamietajArene()
pokazWidocznosc()
kontener:SetAttribute("KlientTreninguGotowy", true)
