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
	           "na_siebie" (aura wokół rzucającego; efekt pokazuje zdarzenie efekt_nalozony)
	  pocisk   rodzaj pocisku (Efekty3D: Pocisk.<nazwa>); predkosc w studach na sekundę, luk = wysokość łuku lotu
	  wybuch   rozbłysk przy trafieniu (Efekty3D: Wybuch.<nazwa>)
	  smuga    kolor smugi za bronią w czasie ciosu;  fala = kolor fali uderzeniowej na ziemi;  pazury = kolor śladów
	  aura     błysk przy rzuceniu umiejętności na siebie (Efekty3D: Wybuch.<nazwa>)
	  kamera   ujęcie umiejętności (patrz Kamera w OdtwarzaczWalki2); stronaKamery = -1 → kamera od strony lasu
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
}

-- style choreografii (Choreo.<styl> w odtwarzaczu)
Ch.STYLE = { "wrecz", "skok", "pocisk", "chmura", "korzenie", "na_siebie" }

-- zwykły cios aktora: klucz aktora → wpis jak u umiejętności; brak wpisu = ZWYKLY_CIOS
Ch.ZWYKLY_CIOS = { styl = "wrecz", smuga = false }
Ch.ATAK = {
	mag = { styl = "pocisk", pocisk = "iskra", wybuch = "iskra" }, -- zwykły atak Maga jest magiczny: mały pocisk z kostura
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
	miazdzacy_cios = { styl = "wrecz", smuga = "#FFC94A", fala = "#B08A58", wstrzas = 0.55, kamera = "zaAtakujacym" },
	kamienna_skora = { styl = "na_siebie", aura = "kamien" },
	-- Zwiadowca
	uderzenie_z_gory = { styl = "skok", smuga = "#FFFFFF", fala = "#B08A58", wysokosc = 4.5, wstrzas = 0.45 },
	zatruta_strzala = { styl = "pocisk", pocisk = "strzala", wybuch = "trucizna", predkosc = 42, stronaKamery = -1 },
	skupienie = { styl = "na_siebie", aura = "zloto" },
	-- Mag
	kula_ognia = { styl = "pocisk", pocisk = "kula_ognia", wybuch = "ogien", predkosc = 26, wstrzas = 0.45 },
	lodowy_pocisk = { styl = "pocisk", pocisk = "lod", wybuch = "lod", predkosc = 34, wstrzas = 0.3 },
	bariera = { styl = "na_siebie", aura = "bariera" },
	-- potwory lasu
	kwasny_plusk = { styl = "pocisk", pocisk = "kwas", wybuch = "kwas", predkosc = 20, luk = 3.5, kamera = "boczny" }, -- szeroki slime zasłaniał kadr zza pleców
	rozszarpanie = { styl = "wrecz", pazury = "#FF3B4F", wstrzas = 0.4, kamera = "zaBroniacym" },
	chmura_zarodnikow = { styl = "chmura", kolor = "#B07CFF", wybuch = "zarodniki" },
	ogluszajace_uderzenie = { styl = "wrecz", fala = "#8B6A43", wstrzas = 0.7, kamera = "zaBroniacym" },
	uscisk_korzeni = { styl = "korzenie", kolor = "#5A3A22", wstrzas = 0.4, kamera = "boczny" },
}

--[[ Efekty na postaci: widoczne od efekt_nalozony do efekt_koniec (albo końca walki).
	wyglad  Efekty3D: Wyglad.<nazwa> (trwała ozdoba na postaci)
	kolor   kolor napisu tyknięcia i ikony
	ikona   ikona z pikseli w interfejsie (InterfejsWalki2)
	napis   napis przy nałożeniu = nazwa efektu z danych silnika wielkimi literami i „!” (test tego pilnuje — napis
	        nie może mówić czego innego niż dziennik) ]]
Ch.EFEKTY = {
	trucizna = { wyglad = "babelki", kolor = "#8BEA4E", ikona = "trucizna", napis = "TRUCIZNA!" },
	podpalenie = { wyglad = "ogien", kolor = "#FF9A2E", ikona = "ogien", napis = "PODPALENIE!" },
	krwawienie = { wyglad = "krople", kolor = "#FF4A5E", ikona = "kropla", napis = "KRWAWIENIE!" },
	spowolnienie = { wyglad = "gwiazdki", kolor = "#7FD8FF", ikona = "gwiazdki", napis = "SPOWOLNIENIE!" },
	zdarcie_pancerza = { wyglad = "odlamki", kolor = "#D9A066", ikona = "pancerz", napis = "ZDARTY PANCERZ!" },
	kamienna_skora = { wyglad = "kamienie", kolor = "#C9CED6", ikona = "kamien", napis = "KAMIENNA SKÓRA!" },
	bariera = { wyglad = "banka", kolor = "#6FE3FF", ikona = "banka", napis = "BARIERA!" },
	skupienie = { wyglad = "blask", kolor = "#FFD23F", ikona = "oko", napis = "SKUPIENIE!" },
}
-- efekt bez wpisu (gdyby się trafił)
Ch.EFEKT_ZASTEPCZY = { wyglad = "blask", kolor = "#FFFFFF", ikona = "oko", napis = "EFEKT!" }

-- spowolnienie nakładają różne umiejętności: wygląd na postaci zależy od tej, która je nałożyła
-- (umiejętność → Wyglad.<nazwa>; test pilnuje, że każda umiejętność ze spowolnieniem ma tu wpis)
Ch.WYGLAD_SPOWOLNIENIA = {
	lodowy_pocisk = "lod",
	uscisk_korzeni = "pnacza",
	ogluszajace_uderzenie = "gwiazdki",
	miazdzacy_cios = "gwiazdki",
}

-- moment trafienia w zdarzeniu (część jego trwania) i zwolnienie
Ch.TRAFIENIE = { cios = 0.5, blok = 0.5, unik = 0.5, krytyk = 0.5, umiejetnosc = 0.56 }
Ch.ZWOLNIENIE = {
	krytyk = { przed = 0.28, po = 0.42, tempo = 0.22 }, -- krytyk: scena zwalnia wokół trafienia (jak w v1)
	nokaut = { przed = 0.12, po = 0.55, tempo = 0.4 }, -- cios kończący walkę
}

-- kolory obrażeń (fizyczne i magiczne muszą się różnić) — liczby nad postaciami
Ch.KOLOR_OBRAZEN = { fizyczne = "#FFFFFF", magiczne = "#C08CFF" }

return Ch
