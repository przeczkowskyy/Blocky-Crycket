# Miasteczko jako ciasny bazar — scena z klocków

Pierwszy blok pasa świata (D-075): ciasny bazar ze sklepami, do których się wchodzi (D-084, D-085), portalem do krain,
przejściem na działkę, zagrodą petów, tablicą z rankingiem i Bramą Leśną na styku z pasem Lasu. Status: **propozycja**
(16/17.11.2026). Projekt, uzasadnienia i wybory do decyzji: [PROJEKT.md](PROJEKT.md).

| Plik | Co to jest |
|---|---|
| `uklad.json` | jedno źródło układu: położenie w świecie, granice, poziomy, budynki, stragany, domy, mury, latarnie, girlandy, ścieżki-kody, cele czasu |
| `generuj.py` | składa scenę → `czesci.json` (format panelu i `tools/studio_buduj.py`) + `znaczniki.json` + raport części |
| `sprawdz.py` | kontrola bez Studio: format, granice, nachodzenie, przejścia, osiągalność, czasy biegu, rozmiary, sprzedawcy, znaczniki |
| `podglad.py`, `rysownik.py` | podglądy w Pillow → `podglad/*.jpg` i `ujecia.json` (te same kamery w świecie Studio) |
| `siatka.py` | siatka chodzenia: przeszkody, promień postaci, najkrótsze drogi i czasy biegu |
| `budynki/*.py` | moduły: karczma, zbrojownia, sklep magiczny, Training Center, zagroda petów, portal do krain, tablica, Brama Leśna |
| `postacie.py` | sprzedawcy (barman, mistrz gier, mag, zbrojmistrz, trener, opiekunka) i pety (pies, slime, smok) |
| `wspolne.py` | skorupa sklepu z wnętrzem, lada, półki, markiza, lampa, girlanda, punkty E, rejestr znaczników |
| `podglad/` | `plan_gora.jpg` (plansza z podpisami, izochronami biegu i skalą) i `u1`–`u5` (całość, uliczka, wnętrze karczmy, plac z portalem i działką, zagroda z tablicą) |
| `tekstury.json` | wygląd w kresce sali wyboru rasy (D-147): kolor i grubość kreski, materiały własne (MaterialVariant) i reguły „co na co” |
| `tekstury.py` | kafelki z arkusza, mapy do barwienia, wgrywanie do Roblox, raport przypisania, pomiar w emulacji telefonu |
| `ujecia_tekstury.json`, `podglad/tekstury_*` | cztery kadry przed/po (plac, uliczka, karczma z bliska, całość z góry) i wyniki pomiaru `tekstury_pomiar.json` |

**Liczby:** 4318 części (po wydłużeniu sali Training Center 26.11.2026; 25.11 po sali i zagrodzie 4312, wcześniej 4410; cel ok. 8000, twardy limit 12 000), 84 grupy. Kontener `Workspace/MiasteczkoBazar`.
Świat = (994 + x; y; −700 + z), bez obrotu: części stoją w pliku już tam, gdzie mają stanąć (X 882…1066,
Z −790…−610), więc przy budowie i zrzutach **nie podaje się `--przesun`**. Wschodni brzeg (X 1066) to początek pasa
Lasu. Bazar stoi na wschodnim końcu płyty Baseplate (PROJEKT.md, wybór 1).

## Polecenia (z głównego folderu repozytorium)

```
python -B swiat/miasteczko_bazar/generuj.py      # → czesci.json, znaczniki.json, raport części
python -B swiat/miasteczko_bazar/sprawdz.py      # kontrola (kod 1 = błąd); --krotko = tylko błędy i ostrzeżenia
python -B swiat/miasteczko_bazar/podglad.py      # → podglad/*.jpg i ujecia.json; --tylko plan,u2; --wyj <folder>
```

Wynik kontroli z 17.11.2026: **0 błędów, 2 ostrzeżenia** (ok. 85 drobnych części wtopionych w grunt do 0,4 st, czyli
w płytę Baseplate — jak w dzisiejszym miasteczku; 31 drobiazgów mniejszych niż 0,5 — oczy, guziki, oczka kostki).

## Zagroda „tylko zagrodą” i sala treningowa w Training Center (noc 25/26.11.2026)

Zlecenie z sesji głównej Karola i Pawła 25.11 (zgoda obu na głos; status zmian: **propozycja** do obejrzenia).

**Zagroda petów** (`budynki/zagroda_petow.py`): bez ozdobnego psa, smoka, slime'a (także tego na dachu), budki opiekunki
i psiej budy. Opiekunka Jagoda stoi **przed zagrodą**, na bruku obok prawego słupka bramki (punkt E przed nią, od strony
uliczki), więc nie zasłania petów. Obrys bez zmian (26 × 20). **Osiem miejsc** na pety w kształcie litery U wokół przejścia
od bramki (każde z legowiskiem w innym kolorze), miski przy bramce, koryto przy tylnym płocie, siano w tylnych narożnikach.
Nazwy znaczników i id interakcji `zagroda_petow` bez zmian. Kolejność = kolejność odblokowania (2 → 4 → 6 → 8):

| Znacznik | Świat Studio (X; Y; Z) | | Znacznik | Świat Studio (X; Y; Z) |
|---|---|---|---|---|
| `zagroda_miejsce_1` | 969,835; 0,5; −680,876 | | `zagroda_miejsce_5` | 970,198; 0,5; −670,483 |
| `zagroda_miejsce_2` | 953,844; 0,5; −680,318 | | `zagroda_miejsce_6` | 954,207; 0,5; −669,924 |
| `zagroda_miejsce_3` | 970,016; 0,5; −675,680 | | `zagroda_miejsce_7` | 965,593; 0,5; −670,522 |
| `zagroda_miejsce_4` | 954,026; 0,5; −675,121 | | `zagroda_miejsce_8` | 958,798; 0,5; −670,285 |

Punkt E opiekunki: stoisko (954,632; 0,3; −692,153), podpowiedź (954,172; 4,9; −688,134). Za nim poszły dane pakietów
gry: `swiat/miasteczko_bazar_gra` (`dane.py`, w Studio `zbuduj.py --skrypty`) i NPC Jagody w `swiat/npc_gra` (`dane.py`,
`zbuduj.py`; kotwice bez zmian).

**Training Center rozszerzony „w lewo”** (`budynki/training_center.py`, patrząc z uliczki = na zachód): sala treningowa
24,2 × 16,8 st przy lewym boku budynku, w tym samym stylu (miętowy tynk, różowy okap i kalenica, kreska tuszem, tekstury
z `tekstury.json` przez nazwy części). Lewy bok budynku ma przejście do sali pod podciągiem (nowa opcja `otwarty_bok`
w `wspolne.skorupa`, inne budynki bez zmian). **Kamera:** front sali otwarty na całej szerokości (bez słupów), belka frontu
z kolizją, a dach to szkło (przezroczystość 0,55) na krokwiach — kamera Roblox (Poppercam) przechodzi przez części
przezroczyste ≥ 0,25 i bez kolizji, więc nie wjeżdża w sufit, a stanowiska widać z placyku. Trener, tablica wyboru i punkt
E `training_center` stoją jak stały; stojak z hantlami spod lewej ściany usunięty (zastępuje go stanowisko Siły), manekin
(26.11.2026) przeniesiony z lewego przodu na prawą stronę głównej izby, między trenerem a workiem (7,6; 0,5) — kamera
gracza za plecami na stoisku E trenera stała w jego głowie (próba bazaru B06). Miejsca sześciu stanowisk AFK zapisuje moduł w `znaczniki.json` (blok `trening_afk`, poza listą
`wszystkie`), stąd wpisane do `src/shared/TreningAFKDane.luau` (`D.miejsca`): dwa rzędy po trzy, gracz twarzą do tylnej
ściany; Pancerz w przednim rzędzie twarzą do placyku, żeby NPC z pomidorami (11 st przed graczem) stał na placyku
(układ z 25.11 — od 26.11 rzędy wzdłuż boków sali, zob. niżej).

**Kolizje sali z mapą i wybór** (sala stoi w kącie pn.-zach. placyku studni): niebieski dom placyku `dom_placyk_pn`
zastąpiony salą (wpis w `uklad.json` zostaje z polem `pominiety`, żeby pozostałe domy miały te same losowania), łącznik
„Training Center | dom placyku” usunięty (łączył z tym domem i stałby przed salą), drzewo z kąta placyku (−92; −29,5)
usunięte, latarnia z (−71,3; −16,4) przesunięta o 4,1 st na (−75,3; −15,5) — stała na linii frontu sali, za plecami
stanowiska Siły (słup z kolizją wciągałby kamerę). Front sali cofnięty o 3,2 st względem frontu budynku, więc ławka
placyku zostaje. Mur w rogu placyku (x −95,5) dotyka ściany sali cokołem (0,2 st), dom zachodni nie nachodzi.

Kontrola: `sprawdz.py` **0 błędów, 2 ostrzeżenia** (te same co wcześniej), 4312 części (było 4410). Testy
`swiat/miasteczko_bazar_gra`: 36/38, dwa niezaliczenia sprzed tej pracy (`test_1d…`, `test_5e…`; 26.11.2026
zaktualizowane do HUD i okien Pawła — 38/38). Zrzuty przed/po:
`podglad/noc2511_*.jpg` (zagroda, Training Center z zewnątrz i w środku, sześć stanowisk w trakcie treningu — Kot-Mag
i Wojownik).

## Sala Training Center: dwa rzędy po trzy z przejściem pośrodku (26.11.2026)

Prośba Pawła przekazana przez Karola: „poprawiłbym domek treningowy wydłużając go lekko, żeby te stanowiska AFK ze
środka przenieść za pozostałe, żeby były 2 rzędy po 3 i przestrzeń po środku”. Status: **propozycja** do obejrzenia.
**Odczytanie (interpretacja agenta):** rzędy biegną wzdłuż lewego i prawego boku sali, od otwartego frontu do tylnej
ściany, a pośrodku zostaje wolne przejście od placyku do tylnej ściany; dwa stanowiska ze środka sali (Kondycja,
Zręczność) stoją teraz na końcu rzędów.

- **Sala dłuższa o 3,2 st do tyłu** (głębokość 16,8 → 20,0; tył z −10,0 na −13,2 modułu). Dalej się nie da bez ruszania
  innych rzeczy: 0,9 st za tylną ścianą jest okap domu z kulis (kalenica sali kończy się 0,1 st przed nim), a tuż za
  salą biegnie niewidzialna ściana pola gry (wnętrze sali zostaje przed nią). Front, szerokość, ławka i latarnia placyku
  bez zmian. Za tylną ścianą budynku prawy bok sali to nowa ściana w linii lewej ściany budynku; tylna ściana, szkło
  dachu, okap i kalenica sięgają do niej. Przejście z budynku do sali zaczyna się jak dotąd przy tylnej ścianie
  budynku. Trzy okna w lewej ścianie (nad stanowiskami zwróconymi do niej), trzy lampy nad przejściem, krokwie i szkło
  wydłużone; hantla-szyld nad frontem bez zmian. Bruk omija nowy obrys (`OBRYSY_DODATKOWE`).
- **Stanowiska** (`STANOWISKA` w `budynki/training_center.py` → `znaczniki.json`, blok `trening_afk` →
  `src/shared/TreningAFKDane.luau`, `D.miejsca`; świat = środek maty na posadzce):

| Stanowisko | Rząd, miejsce | Moduł x; z | Obrót (świat) | Gracz patrzy | Świat Studio (X; Y; Z) |
|---|---|---|---|---|---|
| Pancerz | lewy, przód | −31,5; 3,0 | 183 | na placyk (NPC z pomidorami 11 st przed graczem, na placyku) | 904,200; 0,5; −719,356 |
| Szczęście | lewy, środek | −29,5; −3,2 | 93 | na lewą ścianę (stolik pod ścianą) | 905,873; 0,5; −725,652 |
| Zręczność | lewy, tył | −29,5; −8,8 | 93 | na lewą ścianę (bieżnia pod ścianą) | 905,580; 0,5; −731,244 |
| Siła | prawy, przód | −13,5; 3,0 | 3 | na tylną ścianę | 922,176; 0,5; −720,298 |
| Inteligencja | prawy, środek | −13,5; −2,75 | 3 | na tylną ścianę | 921,875; 0,5; −726,040 |
| Kondycja | prawy, tył | −13,5; −8,5 | 3 | na tylną ścianę (leży na ławce) | 921,574; 0,5; −731,782 |

  Szczęście i Zręczność stoją bokiem (twarzą do lewej ściany), bo przodem do tyłu nie zmieściłyby się jedno za drugim
  (stolik kości sięga 3,9 st przed gracza, a 3 st za graczem jest punkt zejścia ze stanowiska); tabliczki z nazwą stoją
  wtedy przy przejściu i czyta się je z przejścia. Odstępy policzone z rekwizytów w `src/server/TreningAFK.server.luau`.
- **Przejście:** x modułu −26,1 … −17,9 — **8,2 st** wolne od placyku do tylnej ściany (sprawdzone na częściach
  stanowisk zbudowanych w Play, nic w nim nie stoi).
- **Znaczniki:** w `znaczniki.json` zmienił się tylko blok `trening_afk` i liczby części (Training Center 254 → 267,
  bruk 294 → 287); punkty E, kotwice NPC, miejsca petów i strefy bez zmian, więc pakiety gry nie wymagały przebudowy.
- **Podpowiedź E** (uwaga do decyzji — skrypt serwera jest Pawła): Roblox pokazuje tę podpowiedź „E”, która jest najbliżej
  środka ekranu, a podpowiedzi stanowisk mają zasięg 10 st. Gdy gracz podchodzi do Siły albo Inteligencji **od frontu**
  (kamera za plecami, patrzy w głąb rzędu), wygrywa podpowiedź następnego stanowiska w rzędzie (Inteligencji, Kondycji).
  Podchodząc **z przejścia** (naturalna droga w tym układzie) wszystkie sześć startuje dobrze — sprawdzone w Play.
  W dawnym układzie (3 × 2) to samo działo się przy Zręczności i Sile. Naprawa po stronie serwera: mniejszy zasięg
  podpowiedzi (`MaxActivationDistance` ok. 4,5 zamiast 10) albo wybór najbliższej maty — do decyzji Pawła.

Kontrola: `sprawdz.py` **0 błędów, 2 ostrzeżenia** (te same co przed zmianą), 4318 części, czas biegu do Training
Center bez zmian (4,3 s). Testy `swiat/miasteczko_bazar_gra/testy/test_bazaru.py` 38/38. W Studio przebudowany
kontener (4318 części) i wdrożone `TreningAFKDane` + `TreningAFKClient` (`tools/studio/deploy_gui.py`). Próba w Play
(przez `SesjaPlay`, znacznik próby): każde z sześciu stanowisk startuje E z przejścia, postać stoi (leży) na macie
i patrzy w kierunek stanowiska, rekwizyty stanowisk się nie nachodzą, NPC Pancerza dotyka tylko bruku.

**Czytanie (Inteligencja, `src/client/TreningAFKClient.client.luau`, 26.11):** książka była mała (0,98 × 0,67 st)
i siedziała w mankietach rękawów Kota-Maga (nachodziła na nie do 0,18 st), a u wojownika obracająca się kartka
wchodziła w tułów i głowę (do 0,48 st). Teraz książka jest większa (skala z wysokości tułowia: kot 0,85, wojownik
i zwiadowca 1,08), trzymana nisko przed klatką, pochylona 50° stronami ku twarzy, łapy na dolnych rogach od strony
stron, głowa lekko pochylona; przewracana kartka ma 3/4 szerokości strony i „zwija się” w połowie obrotu. Pomiar
w Play (19 próbek na postać, z przewracaniem kartek): Kot-Mag — książka dotyka tylko łapek (0,10 st), nic nie wchodzi
w głowę, wąsy, szatę ani rękawy; wojownik i zwiadowca — tylko dłonie (0,20 st); awatar bez bohatera (szkielet bez
Motor6D, poza zapasowa) — nic, ale ręce awatara (stawy AnimationConstraint) w trakcie treningu w ogóle się nie
ruszają: skrypt ustawia Transform, a ramię zostaje w pozie spoczynkowej — tak samo na stanowisku Siły, więc to
ograniczenie wszystkich stanowisk przy awatarze, nie zmiany z 26.11. Z kamery dokładnie za plecami kota książkę zasłania jego głowa (głowa ma 2,2 st
szerokości z wąsami); z boku i z przejścia (skąd gracz podchodzi) książkę widać.

Zrzuty: `podglad/sala2611_tc_z_placyku_{przed,po}.jpg` (przed = zrzut z raportu nocnego), `sala2611_tc_przejscie_po.jpg`
(dla porównania przed: `noc2511_tc_wnetrze_po.jpg`), `sala2611_tc_z_gory_po.jpg`, `sala2611_afk_<stanowisko>.jpg`
(sześć stanowisk w trakcie treningu, kamera gracza), `sala2611_czytanie_kot_przed.jpg`,
`sala2611_czytanie_kot_{przod,bok}_po.jpg`, `sala2611_czytanie_kot_kamera_gracza_{przed,po}.jpg`,
`sala2611_czytanie_wojownik_po.jpg`.

## Tekstury i kreska w stylu sali wyboru rasy (D-147, 25.11.2026)

Karol (D-147): miasto „w kresce” panelu wyboru rasy — tekstury na budynkach zamiast gładkich kolorów i jednolita kreska,
bez przebudowy miasta. Status: **propozycja**.

- **Tekstury bez nowych instancji.** Zamiast obiektu `Texture` na każdej ścianie (sala ma ich ok. 4800; tu byłoby ok.
  20 000) części dostają materiał własny: 25 obiektów `MaterialVariant` (`BC_Bazar_<nazwa>`, baza SmoothPlastic) w jednym
  folderze `MaterialService/BC_MiasteczkoBazar` (atrybut `Wygenerowane`). W `Workspace/MiasteczkoBazar` liczba instancji
  się nie zmienia (4511). Teksturę ma 2186 z 4410 części — wszystkie duże powierzchnie; gładkie zostają szyby, kryształy,
  Neon, postacie i pety, chmury, dym, ścieżki-kody, kwiaty i drobne symbole, a także sama kreska.
- **Paleta miasta zostaje.** W Roblox kolor części mnoży mapę koloru materiału, więc kafelki z paczki (fioletowy kamień,
  beżowy tynk) przerabiamy na „mapy do barwienia”: każdy kafelek dzielimy przez jego typową barwę, płaska powierzchnia
  wychodzi prawie biała (`jasnosc` 0,96–0,98), a kreska, cegły, słoje i dachówki zostają jako ciemniejszy rysunek.
  Zielony dom zostaje zielony, kremowa karczma kremowa — tylko z rysunkiem tynku i cegieł jak w sali.
- **Skąd tekstury.** 11 z paczki sali (CsTex v2: tynk, kamień, kamienie kominka, cegła, belka, deski, skrzynia, beczka,
  żelazo, złoto) i 14 z nowego arkusza miasteczka `TownTex01`–`16` (Higgsfield, Nano Banana 2.1, 4k, referencje: arkusz
  v2 sali i key-art; ta sama cienka brązowa kreska): trawa, płyta bruku, dachówka, łupek, strzecha, płótno, liście,
  igliwie, woda, ziemia, skała, kora, mech, gładki tynk, piasek (kocie łby — w zapasie). Mapy: `assets/processed/
  TownTextures/TownMap_<nazwa>.png`, 512 × 512 (na telefon wystarczy; 4 × mniej pamięci niż 1024), ID w
  `assets/manifest.json`.
- **Kreska.** To ciemne części „tusz” z generatora (narożniki, ramy okien i drzwi, ranty dachów, wieńce, szprosy —
  1178 części). Kolor i grubość są w jednej linii `"kreska"` w `tekstury.json`: dziś `4A3426` (ciepły brąz jak w sali)
  i grubość 1,0 (geometria z generatora). Wariant czarny i grubszy: `{"kolor": "1D1916", "grubosc": 1.4}` (gotowy wpis
  `kreska_wariant_czarny`; sprawdzony `sprawdz.py`: 0 błędów). Postacie i pety mają własną, czarną kreskę twarzy.
  Bez obrysów `Highlight`: silnik rysuje naraz najwyżej 31, w miejscu jest już 19 (sala, postacie), a na telefonie
  każdy to dodatkowe przejście renderu.
- **Każda przebudowa zachowuje wygląd.** `generuj.py` dopisuje do `czesci.json` blok „tekstury” (definicje materiałów
  i numer materiału każdej części), a `tools/studio_buduj.py` tworzy z niego folder w MaterialService i ustawia
  `Material` + `MaterialVariant` w tej samej paczce, w której buduje części.
- **Uprawnienia.** Mapy są wgrane na konto osoby zalogowanej w Studio (Karol), a gra należy do innego konta — dlatego
  `tekstury.py wgraj` nadaje też grze (universe) prawo „Use” do obrazów (Open Cloud, asset-permissions); bez tego
  obrazy mogą się nie wczytać w grze.
- **Uwaga przy wgrywaniu:** Studio, które poprosi o mapę w pierwszych minutach po wgraniu, potrafi zapamiętać błąd do
  końca sesji (ściana robi się szarozielona, bez rysunku). Wtedy wystarczy przebudować kontener jeszcze raz po kilku
  minutach (25.11 tak było: po drugiej budowie wszystkie 25 map w porządku, także u klienta w trybie Play).

**Pomiar 25.11.2026** (`tekstury.py pomiar`, emulacja Samsung Galaxy A06 800 × 360, te same 4 kadry, wyniki
`podglad/tekstury_pomiar.json`): instancje kontenera bez zmian — 4511 (4410 części), do MaterialService doszło 26
(folder i 25 wariantów). Przy oknie Studio na wierzchu: klatka 16,7 ms (p95 17,4–18,0 ms, 60 kl./s) w każdym kadrze,
render CPU 3,3–4,0 ms, GPU 0,5–0,8 ms, drawcalle 19–68 — w próbie A/B na przemian z wariantami i bez nich (folder
odpięty) liczby są takie same. Przed zmianą okno Studio było w tle (limit Studia 15 kl./s = 66,7 ms), więc „przed”
porównujemy w renderze: CPU 4,7–6,6 ms, drawcalle 29–31; po zmianie w szerokim kadrze z góry drawcalli jest więcej
(31 → 68, osobne partie na materiał), co i tak jest daleko poniżej budżetu telefonu. Mapy 512 px: 25 × ok. 270 KB.
Zrzuty: `podglad/tekstury_{plac,uliczka,budynek,calosc}_{przed,po}.jpg`. Gra w trybie Play: serwer i klient bazaru
gotowe (zgodność logiki 71/71, 13 podpowiedzi), u klienta 25 wariantów i 2186 części z materiałem.

**Słabsze miejsca:** kilka kafelków sali (kamień muru, kamienie kominka, cegła, deski) nie jest idealnie bez szwów —
co 5–7 st widać lekkie przesunięcie rzędów, tak samo jak w sali; mapa wody ma po zszyciu delikatne pasy (woda to tylko
fontanna, koryto i beczka); igliwie z arkusza to małe choinki, nie igły; narożniki budynków (1,3 st) zostają grubsze
niż kreska w sali — cieńsze wymagałyby zmiany modułów budynków, nie tylko parametru.

```
python -B swiat/miasteczko_bazar/tekstury.py kafle      # arkusz assets/raw/TownTextures/v1.png → TownTex01–16
python -B swiat/miasteczko_bazar/tekstury.py mapy --podglad   # mapy do barwienia + plansza _mapy_barwione.jpg
python -B swiat/miasteczko_bazar/tekstury.py wgraj      # mapy bez ID → Roblox przez Studio + imageId + prawo Use dla gry
python -B swiat/miasteczko_bazar/tekstury.py raport --gladkie 40   # co dostaje który materiał, czego nie ma
python -B swiat/miasteczko_bazar/generuj.py && python -B tools/studio_buduj.py swiat/miasteczko_bazar/czesci.json
python -B tools/studio_zrzuty.py swiat/miasteczko_bazar/ujecia_tekstury.json --wyj <folder>
python -B swiat/miasteczko_bazar/tekstury.py pomiar --etykieta po [--ab]   # emulacja telefonu (Galaxy A06)
```

## Budowa w Studio (następny etap — w tym etapie Studio nie było używane)

Studio to wspólne miejsce Team Create: najpierw zgłoś pracę, buduj tylko we własnym kontenerze, Lighting bez zmian,
niczego nie publikuj.

```
python panel/narzedzia/praca.py start --id bazar-studio --tytul "Bazar w Studio" --koniec +45m ^
    --obszar studio:MiasteczkoBazar --obszar swiat/miasteczko_bazar --stop-przy-kolizji
python tools/studio_buduj.py swiat/miasteczko_bazar/czesci.json --sucho   # tylko pokaże kontener i liczbę części
python tools/studio_buduj.py swiat/miasteczko_bazar/czesci.json           # Workspace/MiasteczkoBazar (ok. 30 paczek po 150)
python tools/studio_zrzuty.py swiat/miasteczko_bazar/ujecia.json --wyj <folder>   # te same kadry co podglad/, bez --przesun
python tools/studio_buduj.py swiat/miasteczko_bazar/czesci.json --usun    # usuwa tylko własny kontener (atrybut Wygenerowane)
python panel/narzedzia/praca.py koniec --id bazar-studio
```

Po budowie: migawka i raport na panelu (skill `.claude/skills/panel/SKILL.md`), porównanie zrzutów ze Studio
z `podglad/`.

## Następny etap — lista

1. **Budowa i zrzuty** jak wyżej; obejrzeć kadry `u1`–`u5` i `plan_gora` ze Studio, poprawić kolory frontów rzędu
   północnego (stoją w cieniu) i ewentualne migotanie.
2. **Miejsce startu:** `SpawnLocation` na znaczniku `start` (część „Punkt startu” w grupie `Start`, patrzy na +x —
   `tools/studio_buduj.py` tworzy tylko części). Co z dzisiejszym spawnem — decyzja człowieka.
3. **Podpowiedzi E i uchwyt dla okien Pawła:** `ProximityPrompt` w każdej części „Podpowiedź E <id>”
   (`znaczniki.json` → `sklepy`, `training_center`, `zagroda`, `tablica`); `MaxActivationDistance` 10 (sprawdzone:
   podpowiedź jest bliżej), `RequiresLineOfSight` do sprawdzenia przy ladach. Uchwyt: jedno zdarzenie po stronie
   klienta z identyfikatorem sklepu (`karczma`, `mistrz_gier`, `sklep_magiczny`, `zbrojownia`, `training_center`,
   `zagroda_petow`, opcjonalnie `tablica`), na które okna 2D Pawła się podpinają — nazwę i miejsce ustala Paweł (D-093:
   okna i ich skrypty są po jego stronie).
4. **Portal do krain:** E (albo wejście w wir — znacznik `portal_krain_wir`) → przejście przez chmury i wybór krainy
   (D-075); na razie cel: Las — Polana Przybycia (u 14 w planie pasa). Punkt przybycia „miasteczko” w planie Lasu
   (dziś przy Bramie Miejskiej starego miasteczka) zmienić na start bazaru.
5. **Brama Leśna:** E → Las (albo przejście pieszo — wybór 2 w PROJEKT.md, wymaga bramy w ścianie zamykającej Lasu).
6. **Brama Twierdzy:** E → działka gracza, gdy Twierdza powstanie.
7. **Wrota lochów:** blokada osobna dla gracza — klient chowa `BramaLochow/Blokada` po odblokowaniu (cutscenka, D-042).
8. **Zagroda petów:** osiem miejsc `miejsce_peta` na odstawione pety (od 25.11.2026; wcześniej sześć); okno zagrody — Paweł.
9. **Tablica:** SurfaceGui na powierzchni ze znacznika `tablica_ranking` (środek, normalna, 6,4 × 4,8).
10. **Pomiar:** chodzenie w Play (progi, schodki portalu, kamera we wnętrzach), telefon (części, streaming — bazar to
    hub, rozważyć `Persistent`), czytelność sprzedawców i szyldów.
11. **Sejf:** wpis w `B&C/Technika/Klocki — Blender i Roblox.md`, `Zadania.md` i `Dziennik zmian.md` (w tym etapie
    zakres zapisu był ograniczony do tego folderu).

## Poprawki po pierwszej próbie w grze (17.11.2026, w nocy)

Mapa stoi w Studio (`Workspace/MiasteczkoBazar`, 4410 części) razem z pakietem gry `swiat/miasteczko_bazar_gra`
(podpowiedzi E, przejścia, tablica). Wyniki prób w trybie Play i zrzuty z gry: `swiat/miasteczko_bazar_gra/README.md`
i `swiat/miasteczko_bazar_gra/klatki/`. Zmiany w tym folderze:

- **Postacie — własne projekty** (`postacie.py`): karczmarz nie jest już wąsaczem w czerwieni i bieli (za bardzo
  przypominał znaną postać z cudzych gier) — teraz łysy, z krótką rudą brodą i bakami BEZ wąsów, czerwona opaska
  karczmy zawiązana z tyłu (bez czapki z daszkiem), złoty kolczyk, zielona koszula, skórzany fartuch na szelkach,
  ręcznik na ramieniu, w prawej dłoni kufel z pianą. Przegląd pozostałych: **mistrz gier** miał cylinder, monokl,
  podkręcony wąsik i muszkę (razem — maskotka znanej gry planszowej) → miękki beret w kolorze koła fortuny ze złotą
  kostką, okrągłe okulary (same oprawki), bródka bez wąsów; **trener** — czerwona opaska z białą koszulką była blisko
  znanego wojownika z bijatyk, a czerwoną opaskę ma już karczmarz → niebieska opaska na pot. Mag (fioletowa szata,
  spiczasty kapelusz z gwiazdką), zbrojmistrz (hełm z nosalem, ruda broda, skórzany fartuch, młot) i opiekunka
  (słomkowy kapelusz, rude warkocze, ogrodniczki) to ogólne typy fantasy/wiejskie — bez zmian.
- **Kamera we wnętrzach:** kamera gracza w Roblox (Poppercam) zatrzymuje się tylko na częściach **z kolizją**. Przy
  obróconej kamerze przy mistrzu gier wchodziła między tylną ścianę karczmy a tablicę zleceń (cały ekran zasłaniał tył
  deski), w sklepie magicznym — między ścianę a księgi na półce, a słupek ramy drzwi karczmy zasłaniał postać, gdy
  kamera stała za drzwiami. Teraz z kolizją: rama i deska tablicy zleceń (`budynki/karczma.py`), księgi i kryształy
  dolnej półki maga (`budynki/sklep_magiczny.py`, nad głową gracza) i rama otworu drzwi każdego sklepu
  (`wspolne.py`; wystaje 0,1 st w otwór — przejście bez zmian, `sprawdz.py` 0 błędów).
- Kontrola po zmianach: **0 błędów, 2 ostrzeżenia** (jak wcześniej). Styk z płytą Baseplate sprawdzony skryptem na
  `czesci.json`: żadna płaska część nie ma górnej ściany w płaszczyźnie gruntu (0,1) ani płyty (0,0) — nie ma czego
  migotać; 85 części wtopionych głębiej niż 0,05 jest pod gruntem i niewidocznych.
- Zrzut `klatki/u3_wnetrze.jpg` (ujęcie u3, tryb Edit) zrobiony ponownie z nowym karczmarzem i mistrzem gier.

## Czego nie sprawdzono

- Wyglądu w Roblox Studio — podglądy to rysunek z klocków (bez faktur, cieni rzucanych i świecenia Neonu).
- ~~Kolizji, kamery we wnętrzach i chodzenia postacią w trybie Play~~ — sprawdzone 17.11.2026 (wyżej i w README pakietu gry).
- Telefonu: wydajności, czytelności, streamingu.
- Rozmiaru płyty Baseplate (założone ±1024, jak w planie Lasu).
- Podglądy z Lasem za Bramą Leśną doklejają do rysunku początek `swiat/las_pas/czesci.json` (inny etap, praca w toku) —
  te części nie należą do bazaru i nie ma ich w `czesci.json`.
