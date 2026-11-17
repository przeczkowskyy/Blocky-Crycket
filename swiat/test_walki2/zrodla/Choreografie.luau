--[[
	Choreografie — DANE odtwarzacza walki v2: co odtwarzacz robi z każdym typem zdarzenia dziennika, jak wygląda każda
	umiejętność i każdy efekt. Sam kod choreografii jest w OdtwarzaczWalki2 (Choreo.<styl>, Obsluga.<nazwa>) i
	Efekty3D (Wyglad.<wyglad>, Pocisk.<pocisk>, Wybuch.<wybuch>).

	Test bez Studio (testy/test_odtwarzacza.py) czyta ten plik i pilnuje, że:
	  • każdy typ zdarzenia z Dziennik.TYPY ma wpis w ZDARZENIA, a każda obsługa istnieje w odtwarzaczu,
	  • każda umiejętność z tools/walka/dane_walki.json ma wpis w UMIEJETNOSCI ze znanym stylem (i odwrotnie),
	  • każdy efekt z danych ma wpis w EFEKTY ze znanym wyglądem,
	  • pociski i wybuchy wskazane w tabelach istnieją w Efekty3D.
	Nowa umiejętność bez wpisu NIE zostanie więc po cichu bez animacji. Gdyby mimo to w grze trafiło się coś bez wpisu,
	odtwarzacz gra styl zastępczy (ZASTEPCZY) i liczy to w atrybucie OstatnieBrakiChoreografii.

	Pola wpisu umiejętności:
	  styl     "wrecz" (doskok i cios), "skok" (wyskok i cios z góry), "pocisk" (coś leci od aktor:punkt("Pocisk") do
	           piersi celu), "chmura" (chmura płynie i otula cel), "korzenie" (korzenie wyrastają spod celu),
	           "w_klipie" (efekt jest w klipie aktora — bańka i kałuża Leśnego Slime'a, korzenie Strażnika Gaju: atakujący
	           stoi, a kości efektu sięgają do celu, patrz Klipy „wydluz”; punkt = punkt efektu w modelu (opis; rozbłysk
	           `wybuch` stoi tam, gdzie efekt ląduje: zasięg klipu + wydłużenie), celPrzod = efekt trafia w przód celu,
	           puszcza = ile sekund klipu po trafieniu efekt trzyma cel — bez odrzutu),
	           "na_siebie" (aura wokół rzucającego; efekt pokazuje zdarzenie efekt_nalozony)
	  pocisk   rodzaj pocisku (Efekty3D: Pocisk.<nazwa>); predkosc w studach na sekundę, luk = wysokość łuku lotu
	  wybuch   rozbłysk przy trafieniu (Efekty3D: Wybuch.<nazwa>)
	  smuga    kolor smugi za bronią w czasie ciosu;  fala = kolor fali uderzeniowej na ziemi;  pazury = kolor śladów
	  aura     błysk przy rzuceniu umiejętności na siebie (Efekty3D: Wybuch.<nazwa>)
	  kamera   ujęcie umiejętności (patrz Kamera w OdtwarzaczWalki2); stronaKamery = -1 → kamera od strony lasu
	  zamach   (ujęcie boczne) studs ponad głowę atakującego, na które sięga broń w zamachu z wyskokiem — kadr liczony
	           z tą wysokością (Miażdżący cios)
	           (np. Zwiadowca przy strzale stoi bokiem, piersią od kamery planu ogólnego)
	  wstrzas  siła drżenia kamery przy trafieniu
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Ch = {}

-- typ zdarzenia dziennika → obsługa w odtwarzaczu (Obsluga.<nazwa>)
Ch.ZDARZENIA = {
	cios = "atak",
	krytyk = "atak",
	blok = "atak",
	unik = "atak",
	umiejetnosc = "umiejetnosc",
	efekt_tick = "tykniecie",
	efekt_nalozony = "nalozenie",
	efekt_koniec = "koniec",
	utrata_tury = "utrata",
	wskrzeszenie = "wskrzeszenie", -- v3 (propozycja D-094): powalony wstaje z częścią życia, raz na walkę
}
-- zdarzenie nieznane odtwarzaczowi (nowszy silnik): ostrzeżenie w konsoli, paski i mana z dziennika, bez animacji
Ch.NIEZNANE = "nieznane"

-- style choreografii (Choreo.<styl> w odtwarzaczu)
Ch.STYLE = { "wrecz", "skok", "pocisk", "chmura", "korzenie", "w_klipie", "na_siebie" }

-- zwykły cios aktora: klucz aktora → wpis jak u umiejętności; brak wpisu = ZWYKLY_CIOS
Ch.ZWYKLY_CIOS = { styl = "wrecz", smuga = false }
Ch.ATAK = {
	mag = { styl = "pocisk", pocisk = "iskra", wybuch = "iskra", predkosc = 20 }, -- zwykły atak Maga jest magiczny: mały pocisk z kostura
}

-- umiejętność bez wpisu (gdyby się trafiła): magiczna → pocisk, inna → cios wręcz
Ch.ZASTEPCZY = {
	magiczne = { styl = "pocisk", pocisk = "iskra", wybuch = "iskra" },
	fizyczne = { styl = "wrecz", smuga = "#FFFFFF" },
	sam = { styl = "na_siebie", aura = "blask" },
}

Ch.UMIEJETNOSCI = {
	-- Wojownik
	ciecie = { styl = "wrecz", smuga = "#FFFFFF", wstrzas = 0.35, kamera = "zaBroniacym" },
	-- 17.11.2026: kamera z boku (jak przy uderzeniu z góry) zamiast zza Wojownika — tam stał za blisko i zamach ucinał mu
	-- głowę; zamach = ile studów nad głową sięga miecz z wyskokiem z klipu (9,2 studa nad ziemią przy wzroście 5,7)
	miazdzacy_cios = { styl = "wrecz", smuga = "#FFC94A", fala = "#B08A58", wstrzas = 0.55, kamera = "boczny", zamach = 3.5 },
	kamienna_skora = { styl = "na_siebie", aura = "kamien" },
	-- Zwiadowca
	uderzenie_z_gory = { styl = "skok", smuga = "#FFFFFF", fala = "#B08A58", wysokosc = 4.5, wstrzas = 0.45 },
	-- prędkości pocisków (studs/s) od 15.11 niższe: lot 0,45–0,7 s (odtwarzacz i tak pilnuje tych granic)
	zatruta_strzala = { styl = "pocisk", pocisk = "strzala", wybuch = "trucizna", predkosc = 16, stronaKamery = -1 },
	skupienie = { styl = "na_siebie", aura = "zloto" },
	-- Mag
	kula_ognia = { styl = "pocisk", pocisk = "kula_ognia", wybuch = "ogien", predkosc = 15, wstrzas = 0.45 },
	lodowy_pocisk = { styl = "pocisk", pocisk = "lod", wybuch = "lod", predkosc = 17, wstrzas = 0.3 },
	bariera = { styl = "na_siebie", aura = "bariera" },
	-- potwory lasu
	-- bańka i kałuża z klipu modelu; lot = bańka leci od kl. 21 (0,7 s klipu) do trafienia, odtwarzacz gra ten odcinek
	-- wolniej (ok. 0,55 s sceny) ze smugą za kością Kula; kaluza = dysk kwasu na ziemi do końca kałuży w klipie (kl. 65)
	-- (wpis w jednym wierszu: test bez Studio czyta tę tabelę wierszami)
	kwasny_plusk = { styl = "w_klipie", punkt = "Plusk", wybuch = "kwas", celPrzod = true, wstrzas = 0.3, kamera = "boczny", skalaWybuchu = 1.25, lot = { od = 0.7, czas = 0.55, kosc = "Kula", kolor = "#C8FF5A", szer = 0.4 }, kaluza = { koniec = 2.167, promien = 2.1, kolor = "#8EE83C" } },
	rozszarpanie = { styl = "wrecz", pazury = "#FF3B4F", wstrzas = 0.4, kamera = "zaBroniacym" },
	chmura_zarodnikow = { styl = "chmura", kolor = "#B07CFF", wybuch = "zarodniki" },
	ogluszajace_uderzenie = { styl = "wrecz", fala = "#8B6A43", wstrzas = 0.7, kamera = "zaBroniacym" },
	uscisk_korzeni = { styl = "w_klipie", punkt = "Korzenie", puszcza = 0.53, wstrzas = 0.4, kamera = "boczny" }, -- korzenie z klipu: zaciśnięte kl. 50–66
}

--[[ Efekty na postaci: widoczne od efekt_nalozony do efekt_koniec (albo końca walki).
	wyglad  Efekty3D: Wyglad.<nazwa> (trwała ozdoba na postaci)
	kolor   kolor napisu tyknięcia i ikony
	ikona   ikona z pikseli w interfejsie (InterfejsWalki2)
	napis   napis przy nałożeniu = nazwa efektu z danych silnika wielkimi literami i „!” (test tego pilnuje — napis
	        nie może mówić czego innego niż dziennik)
	znaczek co pokazuje znaczek w lewym górnym rogu ikony (v3): "stosy" = „×N” (trucizna w stosach, gdy N > 1),
	        "procent" = „−N%” (tarcza procentowa: wartosc przy nałożeniu); bez pola — tylko licznik tur
	Statusy v3 mają różny charakter (ZMIANY_SESJA_1611.md): spowolnienie NIE zabiera tury (lód, płatek śniegu),
	ogłuszenie zabiera najbliższą turę (gwiazdki nad głową, napis „TRACI TURĘ!” przy utrata_tury), tarcza z
	umiejętności zmniejsza trafienia o procent przez 3 tury (bez „zapasu” pochłaniania). ]]
Ch.EFEKTY = {
	trucizna = { wyglad = "babelki", kolor = "#8BEA4E", ikona = "trucizna", napis = "TRUCIZNA!", znaczek = "stosy" },
	podpalenie = { wyglad = "ogien", kolor = "#FF9A2E", ikona = "ogien", napis = "PODPALENIE!" },
	krwawienie = { wyglad = "krople", kolor = "#FF4A5E", ikona = "kropla", napis = "KRWAWIENIE!" },
	spowolnienie = { wyglad = "lod", kolor = "#7FD8FF", ikona = "sniezynka", napis = "SPOWOLNIENIE!" },
	ogluszenie = { wyglad = "gwiazdki", kolor = "#FFE14A", ikona = "gwiazdki", napis = "OGŁUSZENIE!" },
	zdarcie_pancerza = { wyglad = "odlamki", kolor = "#D9A066", ikona = "pancerz", napis = "ZDARTY PANCERZ!" },
	kamienna_skora = { wyglad = "kamienie", kolor = "#C9CED6", ikona = "kamien", napis = "KAMIENNA SKÓRA!", znaczek = "procent" },
	bariera = { wyglad = "banka", kolor = "#6FE3FF", ikona = "banka", napis = "BARIERA!", znaczek = "procent" },
	skupienie = { wyglad = "blask", kolor = "#FFD23F", ikona = "oko", napis = "SKUPIENIE!" },
}
-- efekt bez wpisu (gdyby się trafił)
Ch.EFEKT_ZASTEPCZY = { wyglad = "blask", kolor = "#FFFFFF", ikona = "oko", napis = "EFEKT!" }

-- ten sam efekt nakładają różne umiejętności: wygląd na postaci zależy od tej, która go nałożyła
-- (efekt → umiejętność → Wyglad.<nazwa>). Test pilnuje, że KAŻDA umiejętność, która nakłada ogłuszenie albo
-- spowolnienie, ma tu wpis (lód przy lodowym pocisku, pnącza przy uścisku korzeni, gwiazdki przy ogłuszającym
-- uderzeniu trolla i Miażdżącym ciosie).
Ch.WYGLAD_OD_UMIEJETNOSCI = {
	spowolnienie = { lodowy_pocisk = "lod" },
	ogluszenie = { uscisk_korzeni = "pnacza", ogluszajace_uderzenie = "gwiazdki", miazdzacy_cios = "gwiazdki" },
}
-- efekty, przy których odtwarzacz pulsuje ozdobą w chwili utrata_tury (tylko ogłuszenie zabiera turę)
Ch.TRACI_TURE = { ogluszenie = true }

--[[ Blok (v3: każda klasa i każdy potwór). Aktor z klipem bloku (Wojownik z tarczą) gra klip i iskry przy punkcie
	Tarcza; reszta — parada proceduralna: odchylenie i krok w tył, łuk „odbicia” przed bronią (punkt Bron) albo
	przed piersią, iskry. Napis „BLOK −N%” (N z walka.czesc_przez_blok) i mniejsza liczba = część, która przeszła. ]]
Ch.BLOK = {
	kolor = "#7CF3FF", -- łuk parady i napis
	odchylenie = 14, -- stopnie
	cofniecie = 0.7, -- studs
}

--[[ Etykiety premii w zapowiedzi pasywek na starcie walki (tekst UI; liczby zawsze z danych silnika):
	klucz modyfikatora → { tekst, jednostka } — jednostka "%" (ułamek → procent), "pp" (punkty procentowe),
	"pkt" (punkty), "tury", "stosy", "x" (dodatek do mnożnika). Test pilnuje, że każdy modyfikator z danych ma tu
	etykietę (nowy modyfikator silnika bez etykiety = błąd testu). ]]
Ch.MODYFIKATORY = {
	kolejnosc = {
		"zycie", "cios", "cios_zwykly", "moc", "pancerz", "odpornosc", "unik", "blok", "krytyk", "mnoznik_krytyka",
		"zysk_many", "koszt_many", "mana_startowa", "pancerz_wroga", "szansa_zaklecia", "stosy_trucizny",
		"sila_trucizny", "trwanie_podpalenia",
	},
	zycie = { tekst = "życia", jednostka = "%" },
	cios = { tekst = "obrażeń", jednostka = "%" },
	cios_zwykly = { tekst = "zwykłego ciosu", jednostka = "%" },
	moc = { tekst = "mocy umiejętności", jednostka = "%" },
	pancerz = { tekst = "Pancerza", jednostka = "%" },
	odpornosc = { tekst = "odporności na magię", jednostka = "%" },
	unik = { tekst = "uniku", jednostka = "pp" },
	blok = { tekst = "bloku", jednostka = "pp" },
	krytyk = { tekst = "szansy krytyka", jednostka = "pp" },
	mnoznik_krytyka = { tekst = "do mnożnika krytyka", jednostka = "x" },
	zysk_many = { tekst = "zysku many", jednostka = "%" },
	koszt_many = { tekst = "zniżki kosztu many", jednostka = "%" },
	mana_startowa = { tekst = "many na start", jednostka = "pkt" },
	pancerz_wroga = { tekst = "Pancerza wroga", jednostka = "%" },
	szansa_zaklecia = { tekst = "szansy zaklęcia", jednostka = "pp" },
	stosy_trucizny = { tekst = "trucizny (limit)", jednostka = "stosy" },
	sila_trucizny = { tekst = "siły trucizny", jednostka = "%" },
	trwanie_podpalenia = { tekst = "podpalenia", jednostka = "tury" },
}

-- wskrzeszenie (v3): ile trwa każda faza sceny (ułamek trwania zdarzenia z dziennika — czas jest z silnika)
Ch.WSKRZESZENIE = { swiatlo = 0.0, wstaje = 0.22, zycie = 0.38, napis = 0.3, kolor = "#FFE58A" }

-- moment trafienia w zdarzeniu (część jego trwania) i zwolnienie
Ch.TRAFIENIE = { cios = 0.5, blok = 0.5, unik = 0.5, krytyk = 0.5, umiejetnosc = 0.56 }
Ch.ZWOLNIENIE = {
	krytyk = { przed = 0.28, po = 0.42, tempo = 0.22 }, -- krytyk: scena zwalnia wokół trafienia (jak w v1)
	nokaut = { przed = 0.12, po = 0.55, tempo = 0.4 }, -- cios kończący walkę
	powalenie = { przed = 0.12, po = 0.45, tempo = 0.45 }, -- cios, po którym strona wstaje (wskrzeszenie, v3)
	-- atak z lotem (pocisk, chmura, bańka z klipu): zwolnienie zaczyna się dopiero w chwili dolotu (przegląd 15.11 —
	-- przy 0,28 s „przed” pocisk dolatywał 1,1–1,3 s i wyglądał, jakby stał przed celem); rampa = wejście w zwolnienie
	lot = { przed = 0, rampa = 0.03 },
}

-- kolory obrażeń (fizyczne i magiczne muszą się różnić) — liczby nad postaciami
Ch.KOLOR_OBRAZEN = { fizyczne = "#FFFFFF", magiczne = "#C08CFF" }

return Ch
