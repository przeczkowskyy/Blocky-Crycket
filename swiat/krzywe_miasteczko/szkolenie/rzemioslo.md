# Rzemiosło budowania w Roblox — ściąga dla budowniczych mapy v2 „Krzywe Miasteczko”

Stan na 13.11.2026. Mapa powstaje wyłącznie z prymitywów (blok, klin, klin narożny, walec, kula), bez siatek, tekstur i bez ruszania usługi `Lighting`.

**Pewność danych:** [D] dokumentacja Roblox · [R] ogłoszenie pracownika Roblox albo artykuł w dziale Roblox Staff · [S] społeczność, orientacyjnie · [Z] mój pomiar ze zrzutów Studio lub z `czesci.json` v1 · [W] wyliczenie z danych [D]. Liczba po literze to numer źródła. Wartości właściwości zapisuję z kropką, jak w Studio.

**Trzy ustalenia, które zmieniają projekt:** (1) słońce w tym miejscu świeci z północnego zachodu, więc fronty budynków głównych mają stać po wschodniej i południowej stronie rynku; (2) materiały z fakturą i blade kolory szarzeją — bazą jest SmoothPlastic i nasycona, ciepła paleta; (3) po ścianie odchylonej od pionu postać wejdzie, więc dolne 10 studs ścian musi być pionowe.

## 1. Skala i ruch postaci

| Fakt | Wartość | Źródło |
|---|---|---|
| 1 stud | 28 cm | [D1] |
| Awatar klasyczny / o proporcjach ludzkich | ok. 5 / 6–6,5 studs wysokości | [D2] |
| Skrajne awatary dopuszczone specyfikacją | od 1,35 × 3,6 × 0,7 do 8,6 × 9,5 × 2,25 studs | [D3] |
| Szerokość klasycznego awatara z rękami | ok. 4 studs | [S20] |
| Chód (`WalkSpeed`) | 16 studs/s | [D4] |
| Skok (`JumpHeight`) | 7,2 studs; w trybie `JumpPower` = 50 z fizyki ok. 6,4 | [D4] [W] |
| Zasięg skoku w poziomie | ok. 8,7 studs (0,54 s lotu × 16 studs/s) | [W] |
| Grawitacja | 196,2 studs/s² | [D5] |
| Maksymalny kąt zbocza | 89° — postać wejdzie prawie wszędzie | [D4] |
| Drabina z części | postać wspina się z prędkością 70% chodu (11,2 studs/s) | [D4] |
| Kolizje postaci | domyślnie tylko tułów i głowa; nogi przechodzą nad niskim progiem | [D4] |
| Próg pokonywany bez skoku | do ok. 2,5 studs (jeden wątek z 2021 r.), zależy od długości nóg | [S20] |
| Auto-skok | przy sterowaniu dotykowym postać sama skacze na przeszkodę | [D4] |
| Kamera | start 12,5 studs za postacią (ekran pionowy: 25), pole widzenia 70°; przeszkoda między kamerą a postacią powoduje najazd | [D6] [R7] |

Awatary graczy nie są jednakowe. Jedną skalę daje ustawienie awatarów „Consistent Gameplay” (ta sama wysokość i jeden kolider) [D2] — to decyzja poza mapą.

**Wymiary do budowania** (wyliczone z tabeli wyżej; komiksowe przerysowanie idzie w górę, nigdy poniżej minimum):

| Element | Minimum | Zalecane | Dlaczego |
|---|---|---|---|
| Otwór drzwi | 5 × 8 | 7 × 10, budynek główny 8 × 11 | awatar 6,5 + zapas; dwóch graczy naraz |
| Stopień schodów | — | wysokość 0,5–1, głębokość 1,5–2, szerokość ≥ 6 | 1 stud przejdzie każdy awatar bez skoku |
| Rampa z klina | — | 1:2 (26,6°), najwyżej 1:1 (45°) | technicznie do 89°, ale steruje się źle |
| Uliczka boczna | 8 | 10–12 | dwóch graczy po 4 studs i kamera |
| Ulica główna | 12 | 16–20 | kamera 12,5 studs za plecami nie wpada w ściany |
| Prześwit nad ścieżką | 10 | ≥ 14 albo łuk o głębokości ≤ 6 | niżej kamera najeżdża na postać |
| Rynek dla 16–20 graczy | Ø 50 | Ø 64–72 | 20 graczy × koło Ø 8 = 1005 studs²; ×3 na luz = ok. 3000 studs² (v1: Ø 49) |
| Dojście ze spawnu do drzwi | — | ≤ 80–100 studs | 5–6 s chodu |
| Promień całego huba | — | ≤ 110–130 studs | 7–8 s do najdalszego miejsca |
| Przeszkoda do wskoczenia | — | ≤ 6 | skok 6,4–7,2 |
| Bariera nie do przeskoczenia | 9 | ≥ 10 | wysokości 6,5–9 („prawie się da”) frustrują |
| Rekwizyt z kolizją na ścieżce | — | żaden niższy niż 2,5 | na telefonie auto-skok zamienia chód w podskakiwanie |
| Pochylona ściana | — | dolne 10 studs pionowo albo z przewieszeniem nad ulicą; zwężanie ku górze dopiero wyżej | wg dokumentacji postać wchodzi po zboczu do 89°, więc także po ścianie odchylonej „od siebie” o kilka stopni [D4] |

**Ile pikseli ma stud** [W; pole widzenia 70°, ekran 1080 px wysokości]: z 20 studs 39 px, z 40 studs 19 px, ze 100 studs 7,7 px; na ekranie 720 px o jedną trzecią mniej. Stąd: obrys z klocków 0,4–0,6 studa na budynkach (3–5 px ze 100 studs) i 0,2–0,3 studa na rekwizytach przy ścieżce. Detal cieńszy niż odległość ÷ 250 (0,2 studa z 50 studs, 0,4 ze 100) ma na telefonie mniej niż 2 px — nie budować.

## 2. Wydajność na telefony

Roblox nie podaje limitu części. Dokumentacja każe wybrać urządzenie bazowe i pilnować wywołań rysowania (draw calls), trójkątów i pamięci; jako przykład granicy podaje 1000 wywołań i 1 000 000 trójkątów [D8]. Ostrzejszy budżet pod telefony z 2 GB RAM: **500 wywołań i 500 000 trójkątów w kadrze, pamięć klienta poniżej 1,3 GB, 60 kl./s**, z czego na samą mapę ok. 300 wywołań i 300 000 trójkątów [R9].

| Co | Fakt | Źródło |
|---|---|---|
| Trójkąty prymitywów | blok 12, klin 10, klin narożny 10, walec 96, kula 432 | [S21] |
| Łączenie w jedno wywołanie | części o tym samym kształcie i materiale; kolor, rozmiar i obrót nie przeszkadzają; ok. 512 sztuk na wywołanie (dane z 2018 r.) | [R10] [D11] |
| Co rozbija łączenie | inny materiał, tekstury, naklejki i **przezroczystość — każda taka część to osobne wywołanie** | [R10] [S22] |
| Przezroczystość | wartości pośrednie mają „znaczący koszt”; zalecane tylko 0 albo 1; nakładanie się warstw rysuje piksele wielokrotnie | [D8] [D11] [D12] |
| Cienie | silnik wyłącza je poniżej 4. poziomu jakości grafiki; `CastShadow = false` na drobiazgach pomaga | [D11] [D12] |
| Materiały wbudowane | zużywają dużo mniej pamięci niż własne tekstury | [D8] |
| Kolizje | dekoracje: `CanCollide`, `CanTouch`, `CanQuery` = false; wszystko zakotwiczone | [D11] [D12] |
| Zasięg rysowania | nawet na najniższej jakości co najmniej 500 studs | [D8] |
| StreamingEnabled | domyślnie włączone w nowych miejscach; promień minimalny 64, docelowy 1024 studs; zalecane `Opportunistic` | [D13] |
| Części a siatki | części wbudowane grupują się jak siatki; dom ze 100 części i 12 wywołań po zapieczeniu: 6 instancji i 6 wywołań | [R9] |
| Liczba części w grach | gra uchodząca za wzorzec mobilny: 13,5–14 tys.; rada: poniżej 15–20 tys. | [S22] |

**Budżet mapy v2** (propozycja; kolumna v1 policzona z `czesci.json` [Z]):

| Miara | v1 | Cel v2 | Sufit |
|---|---|---|---|
| Części | 2599 | 4500–6000 | 8000 |
| Trójkąty | 65 784 | ≤ 150 000 | 200 000 |
| Różne materiały | 12 | 6–7 | 8 |
| Części przezroczyste | 15 | ≤ 10 | 20 |
| Kule / walce | 24 / 311 | ≤ 100 / ≤ 500 | 150 / 700 |
| Neon | 58 | 80–150 | 200 |
| Części bez cienia | 568 (22%) | ≥ 40% | — |
| Części z kolizją | 890 (34%) | ≤ 40% | 50% |

Na budowlę: główna 250–400 części, zwykła 120–200, stragan z rekwizytami 20–40, drzewo 6–12, latarnia do 8. W v1 las i runo to 1685 części, czyli 65% mapy; w miasteczku ten udział ma spaść poniżej 25%.

Zasady:
1. Okna, woda i dym jako pełne, nieprzezroczyste bryły.
2. `CastShadow = false` dla części mniejszych niż 2 studs (w v1 jest ich 655, czyli 25%) i dla płaskich łat na ziemi. W formacie v2 pliku `czesci.json` ustawia to 16. pole części: 1 = bez kolizji, 2 = bez cienia, 3 = jedno i drugie (`tools/studio_buduj.py`).
3. Płaskie łaty (drogi, bruk, plamy światła) układać warstwami co ≥ 0,05 studa, nigdy w jednej płaszczyźnie — inaczej migoczą; v1 stosuje odstępy 0,03–0,08 [Z].
4. Każda budowla jako osobny `Model`; hub o średnicy ok. 250 studs mieści się w promieniu docelowym streamingu.
5. Siatki dopiero po zgodzie na upload, najpierw dla powtarzalnych rekwizytów (drzewa, beczki, latarnie).
6. Świateł punktowych najwyżej kilka, bez cieni i o małym zasięgu [D11]; latarnie robi Neon.

## 3. Materiały wbudowane w stylu komiksowym

Skali wzoru nie da się zmienić bez własnych tekstur, więc na małych częściach wzór staje się szumem. Oceny wyglądu to wnioski z dokumentacji [D14], wątków społeczności [S23] i zrzutów v1 [Z]. Przed budową warto postawić w Studio próbnik: 13 materiałów × 3 kolory × 2 rozmiary.

| Materiał | Jak czyta się w płaskim świetle | Werdykt | Gdzie |
|---|---|---|---|
| SmoothPlastic | czysta plama koloru; traci ok. 20% nasycenia [Z] | **baza, 70–80% powierzchni** | ściany, dachy, liście, bruk z klocków, obrysy |
| Plastic | drobny szum, przybrudzony SmoothPlastic | nie używać | — |
| WoodPlanks | równe szczeliny desek działają jak kreska tuszem | dobry | drzwi, podesty, beczki, skrzynie, mosty |
| Wood | spokojne słoje, widoczne dopiero z bliska; w ciemnych brązach czyta się dobrze [Z] | dobry | pnie, belki, bramy |
| Cobblestone | z bliska fotograficzna faktura kamieni i niebieski odblask nieba [Z] | ostrożnie, ≤ 10% | cokoły, studnia; bruk rynku lepiej z klocków SmoothPlastic w 2–3 tonach |
| Brick | regularna siatka cegieł | akcent, ≤ 10% | kominy, fragment muru |
| Slate | plamista faktura widoczna jeszcze ze 140 studs; dach traci ok. 28% nasycenia [Z] | nie na dachy | skały, głazy |
| Grass | szum źdźbeł, nasycenie −38% już z bliska [Z] | tylko grunt | trawniki; w v1 miały go liście (1045 części) — w v2 liście ze SmoothPlastic |
| Sand | delikatne ziarno | neutralny | ścieżki, plaża |
| Fabric | drobny splot | neutralny | markizy, flagi |
| Metal | odbija niebo i horyzont, kolor własny słabnie | unikać | zamiast niego ciemny SmoothPlastic i jasny klocek „błysk” |
| Neon | świeci własnym kolorem, ignoruje cień; na niskiej jakości znika poświata, kolor zostaje [R15] | **akcent światła, ≤ 2–3% powierzchni** | okna, latarnie, portal, szyldy |
| Glass | wymaga przezroczystości; załamanie światła nie działa na telefonach [D14] | nie używać | okno z Neonu albo z jasnego SmoothPlastic z ukośnym białym „blikiem” |

Materiał Ground, z którego v1 ma ścieżki, traci 54% nasycenia [Z] — ścieżki robić ze SmoothPlastic albo sprawdzić Sand. Osiem materiałów dodanych w 2024 r. (m.in. ClayRoofTiles, RoofShingles, Plaster, CeramicTiles) ma regularny wzór — sprawdzić na próbniku, zanim trafią na dachy [R16]. Próbnik pokaże też, czy miejsce używa materiałów sprzed 2022 r., czy nowych.

## 4. Kolor i światło przy domyślnym oświetleniu miejsca

**Pomiary z czterech zrzutów Studio v1** [Z] — ten sam kolor w palecie i na ekranie (odcień, nasycenie, jasność):

| Element i materiał | Paleta | Na ekranie | Zmiana |
|---|---|---|---|
| Złota obwódka, SmoothPlastic, z bliska | `F5B82E` (42°, 81%, 96%) | `E4D04F` (52°, 65%, 89%) | nasycenie −20%, odcień +10° |
| Trawa, Grass, z bliska | `5FB548` (107°, 60%, 71%) | `6EAF74` (126°, 37%, 69%) | nasycenie −38%, odcień +19° |
| Ścieżka, Ground, z bliska | `B58A5A` (32°, 50%, 71%) | `928271` (31°, 23%, 57%) | nasycenie −54%, jasność −20% |
| Bruk, Cobblestone, z bliska | `9AA0A8` (214°, 8%, 66%) | `8B98B2`–`BAC6D7` | niebieszczeje: nasycenie 8% → 13–22% |
| Dach w słońcu, Slate, ze 140 studs | `C9472F` (9°, 77%, 79%) | `D1685E` (5°, 55%, 82%) | nasycenie −28% |
| Tynk w słońcu, ze 140 studs | `F2E2B6` (44°, 25%, 95%) | `D3D2C2` (56°, 8%, 83%) | kremowy ton znika: nasycenie 25% → 8% |
| Tynk w cieniu, z 220 studs | `F2E2B6` | `899690` (152°, 9%, 59%) | ok. 70% jasności ściany w słońcu |
| Dach oglądany pod słońce, z 220 studs | `C9472F` | `934C54` (353°, 48%, 58%) | nasycenie −38%, jasność −27% |
| Cień rzucony na trawę | — | `1D4D43` (168°, 62%, 30%) | 43–52% jasności trawy w słońcu, odcień morski |
| Neon blady (latarnia) | `FFD76A` (44°, 58%, 100%) | `FBFDA5` (61°, 35%, 99%) | blednie; okno `FFD98A` wypala się do bieli |
| Neon nasycony (ogień) | `FFD23F` (46°, 75%, 100%) | `FEE413` (53°, 93%, 100%) | zostaje jaskrawy |
| Niebo i płyta | — | zenit `1E71D1`, nisko `83C0DC`, horyzont `C6D5DC`, baseplate `7E90A4` | błękit u góry, szarość przy horyzoncie i na płycie |

**Dlaczego scena wygląda szaro i płasko:**
1. Słońce świeci z północnego zachodu, z wysokości ok. 45–60°. Cienie padają na południowy wschód i mają 0,6–1,0 wysokości obiektu. Zrzut poglądowy v1 był robiony pod słońce: fasada karczmy (zwrócona na +Z) i wszystkie widoczne ściany stały w cieniu. Ta sama mapa oglądana od północy wygląda żywo [Z].
2. Światło wypełniające jest niebieskawe (w szablonie Studio otoczenie to 70, 70, 70 [D17]): kolory przesuwają się o 10–30° ku błękitowi i tracą nasycenie — SmoothPlastic ok. 20%, materiały z fakturą 28–54%. Kremowy tynk robi się jasnoszary.
3. Z daleka dochodzi mgła, a w kadrach z góry dużą część obrazu zajmują szara płyta i blady horyzont. Z poziomu gracza niebo jest nasycone, błękitne.
4. Sąsiednie plamy mają zbliżoną jasność (zielenie lasu), a liście z materiału Grass — widoczny szum.
5. Domyślny styl „Soft” jest z założenia płaski [D17], a poniżej 4. poziomu jakości cieni nie ma wcale [D11] — bryłę musi budować sam kolor.

**Technologie oświetlenia** [R18] [D19]: od 23.07.2025 zamiast `Technology` są `LightingStyle` i `PrioritizeLightingQuality`. „Soft” z priorytetem jakości to dawny ShadowMap (ostre cienie słońca, płaskie cieniowanie). „Soft” bez priorytetu to dawny Voxel (światło w kostkach 4 studs, rozmyte cienie). „Realistic” to dawny Future (połysk, cienie od lamp, najdroższy). Mapa ma się bronić w najgorszym przypadku: „Soft”, bez cieni.

**Przeciwdziałanie samą geometrią i kolorem:**
1. **Ustawienie względem słońca.** Oświetlone są ściany zwrócone na −X i −Z. Budynek patrzący na środek rynku ma front w słońcu, gdy stoi po stronie wschodniej lub południowej (x + z > 0). Tam stawiać budynki główne i najwyższe — ich cień pada poza rynek. Po stronie północnej i zachodniej budynki do 20 studs wysokości (cień 12–20 studs) i z najjaśniejszymi ścianami. Spawn obrócić tak, żeby gracz na starcie patrzył na oświetlony front, czyli na wschód lub południe. Ulice biegnące z północnego zachodu na południowy wschód mają słońce na bruku; poprzeczne są całe w cieniu, gdy budynki są wyższe niż 1–1,7 szerokości ulicy.
2. **Trzy walory na budynek:** cokół jasność 30–45%; ściana jasność 90–100%, nasycenie 30–45%; dach nasycenie 75–90%, jasność 75–90%. Jasna ściana w cieniu (na ekranie ok. 57%) nadal jest jaśniejsza od cokołu.
3. **Kontrast sąsiadów:** różnica jasności ≥ 25 punktów albo odcienia ≥ 60°; trzy tony zieleni różniące się o ≥ 12 punktów.
4. **Zapas na błękit i szarość:** kolory o 15–20 punktów bardziej nasycone niż docelowe; kremowa ściana np. `FFE3A3` (nasycenie 36%), bo przy 25% wychodzi jasnoszara; żółcie i zielenie przesunąć o 10–20° w ciepłą stronę (złoto ok. 35°, zieleń 85–95°).
5. **Sylwetka na tle nieba:** dachy ciepłe (czerwień, pomarańcz, żółć, fiolet). Niebieski dach z palety v1 (`3F7FBF`: 210°, 67%, 75%) ma prawie kolor nieba (`4497D8`: 206°, 69%, 85%) — tylko z ciemną krawędzią.
6. **Obrys z klocków:** ciemny brąz `2A2420` na narożnikach, wokół okien i drzwi, na krawędziach dachu; grubości z rozdz. 1.
7. **Okap i udawany cień:** okap zacienia ścianę na wysokość ok. 1,5–3 swojego wysięgu — w v1 piętro karczmy od słonecznej strony jest prawie całe w cieniu okapu (jasność 58% wobec 83% parteru). Pod dużym dachem dawać więc najjaśniejszy kolor i Neon. Na wypadek wyłączonych cieni dodać pas 0,5–1 studa pod okapem i przy ziemi, o 25–35% ciemniejszy od ściany.
8. **Neon jako światło:** 3–8 elementów na budynek, nasycenie ≥ 70% (ciepłe okna raczej `FFB030` niż `FFD98A`). Neon nie oświetla otoczenia, więc pod latarnią dać jasną, ciepłą plamę: walec Ø 8–12, grubość 0,1, bez kolizji i cienia.
9. **Kurtyna na szarą płytę:** pierścień wzgórz, murów lub drzew o wysokości ≥ 16 studs (lepiej schodkowo 24–40) w promieniu 120–140 studs; w v1 szary pas płyty widać między pniami za bramą.

## 5. Limity

| Limit | Wartość | Źródło |
|---|---|---|
| Rozmiar części | 0,001–2048 studs na oś; poniżej 0,05 fizyka liczy jak 0,05 | [D12] |
| Liczba Highlightów | 255 jednocześnie (od 10.11.2025, wcześniej 31); nadmiarowe są po cichu pomijane; wyłączony nadal zajmuje miejsce | [D24] [R25] |
| Koszt Highlightu | pierwszy widoczny: do 1 ms GPU na telefonie; każdy podświetlony obiekt rysowany osobno; dodanie lub usunięcie przebudowuje geometrię | [D24] [R25] |
| Światło w trybie voxel | kostka 4 × 4 × 4 studs — mniejsze obiekty nie rzucają sensownego cienia | [D19] |

Wnioski dla stylu:
- Highlight obrysowuje tylko sylwetkę całej grupy i nie ma właściwości grubości — gruby kontur i linie wewnętrzne robi geometria (rozdz. 4, pkt 6).
- Opcja `--obrysy` w `tools/studio_buduj.py` ma w opisie limit 31; aktualny to 255. Na telefonie koszt rośnie jednak z powierzchnią ekranu zajętą przez podświetlone obiekty [D24], a każdy z nich jest rysowany osobno [R25]. Zacząć od 8–12 brył przy rynku i porównać liczbę wywołań rysowania z obrysami i bez.

## 6. Propozycja oświetlenia „komiks dzienny” — do decyzji zespołu, nie stosować bez zgody

Wartości startowe do strojenia na oko. Kierunek słońca zostaje, żeby nie unieważnić ustawienia budynków. `LightingStyle` zmienia się tylko ręcznie w Studio [R18]. Podgląd bez ruszania wspólnego `Lighting`: efekty wstawione do własnej kamery widzi tylko jedna osoba [D26].

| Obiekt | Właściwość | Propozycja | Zakres prób | Po co |
|---|---|---|---|---|
| Lighting | LightingStyle | Soft | — | płaskie, rysunkowe cieniowanie; tańsze |
| | PrioritizeLightingQuality | true | — | ostre cienie słońca |
| | Brightness | 2.5 | 2–3 | wyraźny podział na światło i cień |
| | OutdoorAmbient | 145, 140, 170 | ±20 | cień jaśniejszy i fioletowy zamiast ciemnomorskiego |
| | Ambient | 95, 90, 115 | ±20 | podcienia nie czernieją |
| | ColorShift_Top | 255, 236, 196 | — | ciepłe światło kontra chłodny cień |
| | EnvironmentDiffuseScale | 0.4 | 0.3–0.6 | mniej niebieskiego wypełnienia z nieba |
| | EnvironmentSpecularScale | 0.1 | 0–0.2 | bez odbić nieba na plastiku i bruku |
| | ExposureCompensation | 0.15 | 0–0.3 | jaśniej bez wypalania (zakres −5…5, +1 = dwa razy jaśniej) |
| | ShadowSoftness | 0.1 | 0–0.2 | twarda, komiksowa krawędź cienia |
| | ClockTime, GeographicLatitude | bez zmian | — | zachować kierunek słońca |
| Atmosphere | Density | 0.25 | 0.2–0.3 | mniej mgły zjadającej nasycenie |
| | Offset | 0.3 | 0.2–0.4 | wyraźna sylwetka na tle nieba |
| | Color | 190, 220, 255 | — | horyzont błękitny zamiast szarego |
| | Decay | 255, 225, 180 | — | ciepły horyzont; działa przy Haze i Glare > 0 |
| | Haze / Glare | 1 / 0.2 | 0–1.5 / 0–0.3 | lekka poświata przy słońcu |
| ColorCorrection | Saturation | 0.25 | 0.15–0.35 | odzyskanie utraconych 20–38% nasycenia |
| | Contrast | 0.12 | 0.05–0.2 | mocniejszy podział walorów |
| | TintColor | 255, 248, 235 | — | ciepły ton całości |
| Bloom | Intensity / Size / Threshold | 0.4 / 24 / 1.0 | próg 0.95–1.5 | świecą tylko Neony, nie jasny tynk |
| Clouds (w Terrain) | Cover / Density / Color | 0.5 / 0.2 / biały | — | kłębiaste, rysunkowe chmury na pustym niebie |

## 7. Do potwierdzenia w Studio (same odczyty)

- Ustawienia miejsca i kierunek słońca: `print(game.Lighting:GetSunDirection(), game.Lighting.ClockTime, game.Lighting.OutdoorAmbient)` oraz lista dzieci `Lighting`. Kierunek słońca odczytałem z cieni na zrzutach (zgodny na trzech ujęciach), bez dostępu do Studio.
- Próg wejścia bez skoku i szerokość drzwi: przejść awatarem klasycznym i wysokim.
- Próbnik materiałów oraz liczba wywołań rysowania z rynku (statystyki renderowania, Shift+F2).
- Tryb skoku w `StarterPlayer` (`CharacterUseJumpPower`) i maksymalne oddalenie kamery.
- Do decyzji zespołu, poza mapą: obniżenie `CharacterMaxSlopeAngle` z 89° do 60–70°, żeby krzywe ściany nie były drogą na dachy.
- Limit zapytań wyszukiwarki wyczerpał się w trakcie pracy: nie porównałem społecznościowych zestawów ustawień „cartoon” (tabela z rozdz. 6 wynika z dokumentacji i pomiarów), a wątek o wymiarach drzwi [S20] znam tylko ze streszczenia wyszukiwarki (strona zwróciła błąd 403).

## Źródła (dostęp 13.11.2026)

- [D1] Jednostki — https://create.roblox.com/docs/physics/units
- [D2] Ustawienia awatarów — https://create.roblox.com/docs/studio/avatar-settings
- [D3] Specyfikacja postaci — https://create.roblox.com/docs/art/characters/specifications
- [D4] Humanoid, StarterPlayer — https://create.roblox.com/docs/reference/engine/classes/Humanoid · https://create.roblox.com/docs/reference/engine/classes/StarterPlayer
- [D5] Workspace — https://create.roblox.com/docs/reference/engine/classes/Workspace
- [D6] Camera, Player — https://create.roblox.com/docs/reference/engine/classes/Camera · https://create.roblox.com/docs/reference/engine/classes/Player
- [R7] Archiwalny skrypt kamery Roblox — https://raw.githubusercontent.com/Roblox/Core-Scripts/master/PlayerScripts/StarterPlayerScripts/CameraScript/RootCamera.lua
- [D8] Projektowanie pod wydajność — https://create.roblox.com/docs/performance-optimization/design
- [R9] Artykuł gościnny w dziale Roblox Staff, 20.08.2024 — https://devforum.roblox.com/t/real-world-building-and-scripting-optimization-for-roblox/3127146
- [R10] Instancjonowanie części, 29.05.2018 — https://devforum.roblox.com/t/part-instancing-pre-release-announcement/130333
- [D11] Poprawa wydajności — https://create.roblox.com/docs/performance-optimization/improve
- [D12] BasePart — https://create.roblox.com/docs/reference/engine/classes/BasePart
- [D13] Streaming instancji — https://create.roblox.com/docs/workspace/streaming
- [D14] Materiały, MaterialService — https://create.roblox.com/docs/parts/materials · https://create.roblox.com/docs/reference/engine/classes/MaterialService
- [R15] Ulepszony Neon, 16.08.2017 — https://devforum.roblox.com/t/introducing-improved-neon/48861
- [R16] Osiem nowych materiałów, 06.05.2024 — https://devforum.roblox.com/t/introducing-8-new-base-materials-studio-beta/2959559
- [D17] Samouczki oświetlenia — https://create.roblox.com/docs/tutorials/curriculums/core/building/customize-global-lighting · https://create.roblox.com/docs/tutorials/use-case-tutorials/lighting/enhance-outdoor-environments
- [R18] Unified Lighting, 21.01.2025, pełne wdrożenie 23.07.2025 — https://devforum.roblox.com/t/let-there-be-unified-light-unified-lighting-is-fully-live/3401512
- [D19] Lighting — https://create.roblox.com/docs/reference/engine/classes/Lighting · https://create.roblox.com/docs/environment/lighting
- [S20] Próg bez skoku, 11.2021; wymiary drzwi — https://devforum.roblox.com/t/how-to-change-the-maximum-height-that-an-object-can-be-so-that-a-humanoid-can-still-walk-over-it/1544732 · https://devforum.roblox.com/t/what-should-be-the-ideal-door-size/2200910
- [S21] Geometria prymitywów, 20.06.2024 — https://devforum.roblox.com/t/basepart-shapes-have-unnecessary-additional-geometry/3030984
- [S22] Liczby części i optymalizacja, 2021–2025 — https://devforum.roblox.com/t/how-many-parts-is-too-many-when-is-geometry-optimization-overkill/1116692 · https://devforum.roblox.com/t/whats-a-good-maximum-part-count-for-low-end-devices/1930430 · https://devforum.roblox.com/t/checklist-for-building-optimization/3232350 · https://devforum.roblox.com/t/optimization-for-roblox-environments/3844846
- [S23] Materiały w stylu rysunkowym, 2020–2025 — https://devforum.roblox.com/t/plastic-or-smoothplastic-materials-performance/3830065 · https://devforum.roblox.com/t/how-to-make-the-best-cartoony-feel/680546 · https://devforum.roblox.com/t/stylized-low-poly/3780170
- [D24] Highlight — https://create.roblox.com/docs/reference/engine/classes/Highlight · https://create.roblox.com/docs/effects/highlighting
- [R25] Więcej Highlightów, 10.11.2025 — https://devforum.roblox.com/t/lights-camera-more-highlights/4061534
- [D26] Atmosfera, efekty, chmury — https://create.roblox.com/docs/environment/atmosphere · https://create.roblox.com/docs/environment/post-processing-effects · https://create.roblox.com/docs/environment/clouds · https://create.roblox.com/docs/reference/engine/classes/BloomEffect · https://create.roblox.com/docs/reference/engine/classes/ColorCorrectionEffect
- [Z] Pliki lokalne: zrzuty Studio `noc/studio/test_zrzut.png` i `panel/dane/podglad/20261113-001753-2562/zrzut_1–3.jpg`, `swiat/demo_lesna_baza/czesci.json`, `swiat/demo_lesna_baza/generuj.py`, `tools/studio_buduj.py`
