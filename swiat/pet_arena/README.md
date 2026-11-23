# Pet Arena → „Throw & Catch Monsters” — rdzeń, etap 2, v2 (koloseum, fizyka, sterowanie), v3 (łapanie potworów, powód powrotu) — D-118, propozycja

*Throw your pet into the pit, knock out wild monsters and catch them — then fight for the golden throne.* Osobna, samowystarczalna gra we własnym
miejscu Roblox (plik lokalny `PetArena.rbxlx`, kontener `Workspace/PetArenaGra`). Projekt: `B&C/Gra/Pet Arena — projekt
prototypu.md`. Warsztat skopiowany i przerobiony z `swiat/bonk/` (w czasie gry i budowy nic nie jest importowane z BONK;
modele petów, jajek i bossów czytane są z tych samych danych — `swiat/postacie/<id>.py`, `swiat/test_walki2/dane/` —
z których korzystał BONK).

## Co nowego w v3 — „Throw & Catch Monsters” (21.11.2026 noc)

Analiza trendu z 21.11: podobne gry z bitką petów na arenie miały skok i gasły po 4–8 tygodniach, bo nie dawały powodu
do powrotu; rośnie pętla „pokonane potwory dołączają do ciebie”. Dlatego środek ciężkości przesunięty na **rzucaj i łap
potwory**, a walka graczy o tron zostaje jako przyprawa. Tytuł w grze (atrapa, napis nad bramą): **THROW & CATCH
MONSTERS**. Wszystkie liczby w `ustawienia.json` (sekcje `dzikie`, `lapanie`, `odmiany`, `alfa`, `zegar`, `wylegarnia`,
`prezent`, `nowy_potwor`) — to propozycja do strojenia.

**„Wybijesz, to zabierasz” (rdzeń):**
- Dzikie potwory to osobny rodzaj z własną tabelą (`dzikie.tabela`: waga wejścia, Common często, Legendary rzadko).
  Wchodzą **bramą**, dopełniają arenę jak dotąd (razem do 4, limit areny 6). Rzadsze są większe (× 1 / 1,08 / 1,18 / 1,3
  / 1,45) i mają krążek w kolorze rzadkości (Common szary).
- Cios kończący (RING OUT albo KO) peta gracza w dzikiego losuje złapanie z jawną szansą **35 / 22 / 12 / 6 / 3 %**
  (Common → Legendary). Litość: każda nieudana próba danej rzadkości dodaje 3 pkt (najwyżej 90 %), udane złapanie ją
  zeruje. **Pierwsze wybicie dzikiego u nowego gracza to pewne złapanie**; samouczek: „Knock out wild monsters to catch
  them!” zaraz po rzucie.
- Udane złapanie:
  - w świecie pierścień w kolorze rzadkości, a potwór zwija się i leci do loży łowcy;
  - u łowcy krótka scena **CAUGHT!** (wyklucie bez trzęsienia jajka, ok. 3 s, z tabliczką rzadkości i odmiany);
  - potwór trafia do kolekcji jako nowy pet albo gwiazdka.
- Nieudane: **ESCAPED!** i złoto (6 × stopień). Asysty (inni gracze, którzy trafili dzikiego) dostają 8 × stopień.
- **Odmiany** (złapane i wyklute pety):
  - **BIG** 8 %: × 1,25 rozmiaru, +15 % siły;
  - **GOLDEN** 3 %: złoty i lśniący, × 1,5 złota na sekundę;
  - **GIANT** 0,5 %: × 1,6 rozmiaru, +30 % siły.

  Odmianę widzą wszyscy: napis nad petem, rozmiar i wygląd (flagi w migawce) oraz karta w kolekcji. GOLDEN, GIANT i
  złapania od Rare są ogłaszane na serwerze („Player 2 caught a GIANT Forest Troll!”).
- **ALPHA** (z zegara, co 5 minut):
  - rzadki dziki potwór (od Rare) wchodzi bramą z zapowiedzią;
  - jest 1,5 raza większy i ma 3 razy więcej życia;
  - ostatni cios łapie z szansą +20 pkt, a złapana ALPHA ma co najmniej odmianę BIG;
  - łowca dostaje 120 złota, asysty po 30.
- **Jawne szanse**: tablica **CATCH CHANCES** na ścianie przy arenie (złapanie według rzadkości i odmiany) oraz dwa
  wiersze w oknie PETS → INDEX. Jajka zostają jako drugi, pewniejszy sposób (złoto → jajko).

**„Jutro na arenie” (powód powrotu):**
- **Zegar wydarzeń o stałych porach** (czas serwera, UTC):
  - boss o :00 i :30;
  - złoty boss o :15 i :45;
  - ALPHA co 5 minut (:02, :07, …).

  Panel **NEXT: … in mm:ss** jest widoczny od wejścia (lewy dół), a pod nim **NEW MONSTER in N days** (data w
  ustawieniach: 29.11.2026, dzień ósmy). W próbach zegar można przyspieszyć (haczyk `zegar_tempo`).
- **Wylęgarnia w czasie**:
  - kupione jajko trafia do jednego z **2 miejsc** i wylęga się w czasie rzeczywistym, także poza grą;
  - czasy: Forest **2 min**, Swamp **30 min**, Ruin **4 h**; pierwsze jajko jest darmowe i wylęga się od razu;
  - po powrocie gracz widzi „YOUR EGG IS READY!”, a przycisk EGGS pulsuje;
  - w oknie przycisk **HATCH!** albo **SPEED UP** za złoto z gry (pozostałe sekundy × 1,5 / 1 / 0,6 G).
- **Dzienny prezent**:
  - przycisk GIFT obok złota pulsuje, gdy prezent czeka;
  - nagrody po kolei: 200 G → 400 G → Forest Egg → 800 G → 1200 G → Swamp Egg → 2000 G, potem od nowa;
  - seria nie przepada (przerwa ją tylko wstrzymuje), a przy odbiorze widać „Tomorrow: …”;
  - powracającemu graczowi okno prezentu otwiera się samo.

**Inne:**
- **Kamera** (przyjęta propozycja z raportu v2): domyślnie cała arena, gdy pet walczy na autopilocie. Za petem tylko
  przy ręcznym sterowaniu; kamera wraca do całości, gdy wraca autopilot. VIEW nadal przełącza widok.
- **Przy tronie najwyżej jedno duże słowo naraz** (KING!, nazwa umiejętności, CRIT!, RING OUT!; reszta pomijana).
- Profil v3: nowe pola `litosc`, `prezent`, `zlapane` i `samouczek.zlap`, wypełnione `odmiany` i `wylegarnia`. Stare
  profile się wczytują, a pierwsze złapanie jest pewne także dla nich.
- Efekty umiejętności bez zmian (zgodnie z priorytetami).

## Co nowego w v2 (21.11.2026 wieczór — po uwagach Karola)

Karol po obejrzeniu demo: arena za mała, pety za małe i bez różnicy wielkości, obszar złota i wygląd słabe, wyklucie bez
emocji, wyrzucanie nieprzekonujące; potem: 10 petów to chaos, gracz ma sterować petem. Zasady rdzenia zostały (rzut w
miejsce, bitka o środek, złoto za bliskość środka, umiejętność na przycisk, odrzut rosnący z ubytkiem życia).

- **Skala:** arena **r 40** (ok. 2,8 × powierzchni etapu 1; najpierw r 48 = 4 ×, ale przy najwyżej 6 petach wyglądała pusto
  i wymagała długich dojść). **Najwyżej 6 petów** na arenie, dzikie dopełniają do 4. Pety **różnej wielkości według
  wagi** (lekki 1 : średni 1,6 : ciężki 2,4 — wysokość 6 / 9,6 / 14,4 st, boss 24 st); promień ciała, zasięg ciosu i
  prędkość rosną z wielkością. Lekkie: Slime, Acornling, Leaf Fox, **Thorn Wolf** (mały — Karol), Wisp, Dragonfly;
  średnie: Croaker, Shroomling; ciężkie: Moss Snail, Forest Troll, Ruin Armadillo, Hut Toad.
- **Fizyka** (dalej liczona na serwerze w 2D, wysokość lotu to dodatkowa współrzędna): masa dzieli odrzut i decyduje o
  przepychaniu (ciężki spycha lekkiego, lekki odbija się od ciężkiego); ślizgający się po ciosie pet, który wpadnie w
  innego, **przekazuje mu pęd** (odbicie sprężyste według mas) i zaliczenie wybicia; krytyk, cios kończący i odrzut ≥ 40
  **wyrzucają w powietrze** (łuk, koziołki, smuga, w locie nie chodzi i nie jest celem, ląduje z odbiciem i kurzem).
  RING OUT: pet przelatuje wielkim łukiem **ponad trybuny poza koloseum** z obrotem, śladem i napisem; kamera pokazuje
  lot, gdy to mój pet albo moje wybicie. Fosy i gejzerów już nie ma.
- **Gracz może sterować petem** (B), ale **domyślna ścieżka nie wymaga drążka** (zmiana priorytetów 21.11): samouczek
  to „rzuć → pet walczy sam → stuknij ABILITY → wyklij darmowe jajko”, efekt po ok. 3–4 s jak dotąd. Po wylądowaniu
  telefon — **drążek pojawia się dopiero pod palcem**, gdy gracz dotknie lewej połowy ekranu (puszczenie chowa go);
  komputer — WASD i strzałki od razu; pad — lewa gałka. Podpowiedź o sterowaniu dopiero po pierwszej umiejętności i
  najwyżej przez 8 s. **Cios automatyczny** (najbliższy w zasięgu); umiejętności kierunkowe (szarża, toczenie,
  stożek ognia, skok) lecą w stronę ruchu albo patrzenia. **Autopilot** po 2,5 s bez dotknięcia sterowania albo po
  otwarciu okna (znacznik AUTO nad petem); dotknięcie drążka od razu oddaje kontrolę. Gdy pet jest na arenie, awatar stoi w
  loży (sterowanie postacią wyłączone); bez peta awatar znów chodzi (mur z lożami, wylęgarnia, mata; niewidzialna
  bariera na krawędzi muru). Serwer liczy wszystko (wejście: wektor długości ≤ 1, własne wiadro tempa 20/s, walidacja),
  a własny pet rusza od razu (przewidywanie u klienta z łagodnym dociąganiem do stanu serwera).
- **Kamera:** bez peta albo przy celowaniu — **cała arena**; gdy pet walczy — kamera płynnie **za petem** ze stałą
  orientacją (góra ekranu = „od kamery”, kierunki drążka stałe), pet ok. 100 pt na telefonie; przy wielkim wybiciu
  krótko za lecącym; przy wejściu bossa bramą — na chwilę cała arena; przycisk **VIEW** (atrapa) przełącza widok
  całości.
- **Styl — jasne koloseum potworów** (decyzja projektanta zamiast lochu, bo grają dzieci): piaskowa arena z pasami
  krawędzi, mur w ciepłym kamieniu z kolorowym pasem, pięć stopni trybun w kolorach sektorów, **kibice z klocków**
  podskakujący sektorami (mocniej przy wielkich chwilach), mur zewnętrzny z blankami i **proporcami**, **paleniska z
  kolorowym ogniem** (migocze), wielka **brama bossa** z kratą, loże graczy na murze (kolor miejsca, chorągiewka),
  wylęgarnia i maty w obrębie stadionu, jasne niebo (13:12).
- **Wzgórze króla zamiast malowanych pierścieni:** trzy okrągłe stopnie (terakota x1 r 18, niebieski marmur x2 r 10,
  złoty szczyt x5 r 4,6 z tronem i słupem światła), małe znaki x1/x2/x5; **tron mieści jednego** — x5 dostaje tylko pet
  najbliżej środka, reszta na szczycie liczy się jak x2; drugi stopień mieści 2–3 pety; poza wzgórzem złota nie ma.
  Pet stoi na wysokości stopnia (tylko w obrazie). **Monety lecą z podłogi do peta** w tempie złota na sekundę; korona
  króla rośnie z nagrodą za głowę (do × 1,7) i ma wielkość dopasowaną do peta (lekki król nie znika pod koroną).
- **Wyklucie (5–6 s, cały ekran):** jajko wskakuje, trzęsie się w trzech fazach (kolor poświaty awansuje aż do
  wylosowanej rzadkości), pęka błyskiem, **80 sztuk konfetti**, wirujące promienie, pet wyskakuje z obrotem i
  odbiciem, tabliczka rzadkości wjeżdża z hukiem, gwiazdki, dźwięki z arkusza; stuknięcie przyspiesza ×3.
- **Umiejętności i stany** (po zmianie priorytetów 21.11 tylko to, co już było zrobione, przeskalowane do nowych
  wielkości — bez nowych efektów w tym etapie): fala — trzy pierścienie, kurz i krater; skok — rosnący cień w miejscu lądowania,
  krater; szarża — smuga i kurz (Ruin Armadillo toczy się); stany nad petem: bryła lodu na zamrożonym, bańka skorupy,
  płomienie na podpalonym, gwiazdki krążące nad ogłuszonym, ikony 💫 ❄ 🔥 🛡; cios — wypad do przodu, błysk i
  spłaszczenie. **Złoty boss** (wydarzenie złote) cały złoty i lśniący (Foil, iskry); boss wchodzi **bramą** z
  zapowiedzią („BOSS IS COMING!”), wstrząsem i wiwatami.
- **Czytelność:** własny pet — żółty krążek i obrys widoczny przez innych, inni gracze — kolor miejsca, dzikie —
  stonowany szary krążek bez obrysu; słowa komiksowe jak w etapie 2 (duże najwyżej 2 naraz).
- **Ekran:** tylko atrapy (docelowe przyciski i okna zrobi Paweł w Figmie) — dodane VIEW i pływający drążek.
- **Pod następny etap (jeszcze nieużywane):** profil ma pola `odmiany` (pet → odmiana → ile, np. rzadka odmiana
  złapanego dzikiego) i `wylegarnia` (jajka wylęgające się w czasie: numer jajka i chwila końca), sprawdzane przy
  wczytaniu i zapisywane; test 2w. Dzikie pety jako osobny rodzaj z własną tabelą — dopiero w tamtym etapie.

## Co nowego (etap 2, 20/21.11.2026)

- **Czytelność:** pety ok. 1,6 × większe (8,8 / 9,6 / 10,5 st; na telefonie 667 × 375 lekki pet ok. 70–78 pt), kamera
  bliżej i niżej (nachylenie 40°, cała arena w pasie 0,12–0,82 wysokości i 0,17–0,83 szerokości — sprawdzane na 4
  ekranach). Ekran w rogach: GOLD i poziom w lewym górnym, EGGS / PETS / TRAIN w prawym górnym, drużyna po lewej,
  ABILITY w prawym dolnym — środek areny odkryty. Napisy „WILD” zastąpione kolorem krążka pod petem (szary — dziki,
  żółty — mój, kolor miejsca — inni gracze, złoty — złoty pet, czerwony — boss); paski życia cienkie nad petem.
- **Słowa komiksowe:** małe i krótkie tylko przy ciosach własnego peta; duże (RING OUT, KO, nazwa własnej
  umiejętności, +złoto, boss) najwyżej 2 naraz, ok. 0,75 s; KING / NEW KING / BOSS jako napis u góry ekranu.
- **Soczystość:** błysk trafienia (białe wypełnienie), podskok i przechył po ciosie, spłaszczenie i odbicie (do 3 petów
  naraz), smuga lotu (rzut, RING OUT, KO, szarża), większy rozbryzg w fosie, krótkie zatrzymanie (0,07 s) i wstrząs
  kamery przy wybiciach własnego peta, króla i bossa; KO — wirujący lot ok. 46 st (pół ekranu).
- **Rzut z ręki:** awatar trzyma w dłoni następnego peta (zmniejszony model), przy rzucie zamach ręką (obrót barku
  doklejony do `Transform`, jak w BONK), pet startuje z dłoni.
- **Odpoczynek 30 s** (było 60). Decyzja projektanta etapu 2 z symulacji: przy 60 s gracz z trzema petami ok. 40 % czasu
  nie ma kogo rzucić. **Karol mówił o ok. minucie** — jedna liczba `odpoczynek_s` w `ustawienia.json`, do sprawdzenia
  graniem.
- **Jajka i kolekcja:** stanowisko jajek na obrzeżu (trzy jajka na cokołach + tablica szans), okno EGGS: FOREST EGG
  360 G, SWAMP EGG 2000 G, RUIN EGG 8000 G, jawne szanse na rzadkość, tylko za złoto z gry; **pierwsze jajko darmowe**
  (drugi krok samouczka: „Hatch your free egg!”, przycisk EGGS pulsuje) — zamiast peta TRIAL z etapu 1. Scena wyklucia
  (jajko trzęsie się, pęka błyskiem w kolorze rzadkości, pet wyskakuje: NEW PET! albo **+1 STAR!**). Kopie dają
  **gwiazdki** (do 5, każda +8 % życia i siły — obrażeń i odrzutu), przy 5 gwiazdkach kopia zwraca 30 % ceny.
  Gwiazdki widać nad petem, na kartach drużyny i w oknach.
- **Okno PETS:** zakładka TEAM — trzy miejsca drużyny (dotknij miejsca, potem peta z kolekcji) i kolekcja z modelami,
  gwiazdkami i znaczkiem IN TEAM; zakładka **INDEX** — Księga: 12 miejsc, nieznane jako czarne sylwetki „???”, licznik
  INDEX n/12. Nowy pet z jajka trafia do drużyny, gdy jest wolne miejsce.
- **Wydarzenia serwera** na zmianę co 150 s (pierwsze po 90 s), z odliczaniem u góry („GOLDEN PET IN 0:30”, „BOSS IN
  0:30”): **GOLDEN PET** (złoty slime ucieka po arenie, każdy cios peta gracza = 6 × stopień złota, wybicie +150) i
  **BOSS** (Strażnik z BONK: MIRE GUARDIAN / VINE SERPENT na zmianę; ląduje z nieba w środku ze wstrząsem; życie 1400 +
  500 na gracza; co 3,2 s fala odrzutu; po 70 s ucieka; pokonany — pula 400 złota dzielona według zadanych obrażeń, co
  najmniej 80 dla każdego, kto trafił; deszcz monet i komunikat). Pasek życia bossa u góry ekranu.
- **Tarcza słabszego:** pet o ≥ 2 stopnie silniejszy zadaje słabszemu 35 % obrażeń i odrzutu (bez bossa i złotego);
  przy słabszym ikona 🛡 nad paskiem.
- **Trener:** doświadczenie za sekundę peta na arenie (1), wybicie (12), udział w bossie (40) i za stanie na macie
  (TRAIN — awatar przechodzi na matę obok swojego miejsca i ćwiczy pajacyki; 0,6 / s); poziom n wymaga 60 × n^1,45;
  każdy poziom +3 % życia i siły wszystkich petów. LV i pasek w lewym górnym rogu, napis LEVEL UP!, poziom i
  najlepszy pet nad głową każdego gracza („LV 3  Hut Toad ★★”).
- **Zapis:** własny magazyn `PetArena_Gracz_v1` (w Studio z przyrostkiem `_Studio`), ochrona prób jak w BONK (znacznik
  `ZapisProbaDo` z `tools/zapis_prob.py` — magazyn nieczytany i niepisany), wczytanie przy wejściu (3 próby), **bez
  udanego wczytania nie zapisujemy**, zapis przy wyjściu, co 60 s i przy zamknięciu serwera. Profil v2: złoto, pety z
  gwiazdkami, drużyna, Księga, doświadczenie, samouczek, wybicia, rzuty, jajka, najdłuższe panowanie; migracja z v1.
  W pliku lokalnym (miejsce nieopublikowane) magazyn bywa niedostępny — gra działa wtedy w pamięci bez błędów.
- **Pokazanie się:** trzy tablice na ścianie dołu (TOP GOLD/S, LONGEST KING, KNOCKOUTS — gracze serwera, co 2 s),
  komunikaty (Epic / Legendary z jajka, zgarnięta nagroda za głowę ≥ 40, pokonany boss), napisy nad graczami.
- **Pad:** lewa gałka — celownik, A rzut, X umiejętność, LB/RB wybór peta, Y okno PETS, w górę EGGS, w dół TRAIN,
  B zamyka okno; w oknach zaznaczenie przycisków (GuiService) i A klika; znaczki przycisków na ekranie, gdy gra pad.
- **Demo wideo** (`testy/demo_wideo.py`, ok. 40 s, 1280 × 720) i plansza klatek — poza repo.

## Co działa (etap 1 — rdzeń, bez zmian w zasadach)

Scena (dół, obrzeże-trybuna, arena r 24 z pasami krawędzi, strefy x5 / x2 / x1 z napisami na podłodze obróconymi do
kamery gracza, fosa z gejzerami, drzewa, światło), kamera stała, rzut w wybrane miejsce (serwer sprawdza cel, limit 8,
jednego peta gracza, odpoczynek, tempo), walka na serwerze w 2D (odrzut = siła × (1 + 2 × ubytek życia) / waga, tarcie,
krytyki, RING OUT do fosy i gejzer, KO), 12 petów z 12 umiejętnościami (9 rodzajów), złoto co sekundę według strefy,
król środka z koroną i nagrodą za głowę, dzikie pety (boty) dopełniające arenę do 5. Szczegóły liczb niżej.

## Sterowanie

| Co | Telefon | Komputer | Pad |
|---|---|---|---|
| Rzut | stuknięcie w arenę | klik (podgląd celu pod myszą) | gałka — celownik, A |
| Ruch peta (v2, nieobowiązkowy — bez niego autopilot) | przytrzymanie lewej połowy ekranu (drążek pod palcem) | WASD / strzałki | lewa gałka |
| Widok całości (v2) | VIEW | VIEW | — |
| Umiejętność | ABILITY | spacja / Q | X |
| Wybór peta | karta po lewej | 1 / 2 / 3 | LB / RB |
| Jajka (wylęgarnia: HATCH! / SPEED UP) / Pety / Trening | EGGS / PETS / TRAIN | E / P / T | w górę / Y / w dół |
| Dzienny prezent (v3) | GIFT (obok złota) | GIFT | — |
| Zamknij okno | X | X | B |

## Liczby (propozycja do strojenia — wszystkie w `ustawienia.json`)

| Co | Wartość |
|---|---|
| Arena / wzgórze (v2) | r 40; tron r 4,6 (×5, jeden pet), stopień r 10 (×2), stopień r 18 (×1), podłoga bez złota |
| Klasy wagi (v2: lekki / średni / ciężki) | rozmiar 1 / 1,6 / 2,4; wysokość 6 / 9,6 / 14,4 st; masa 1 / 1,8 / 3; życie 100 / 130 / 170; cios 4,5 / 6 / 8; odrzut 13 / 18 / 26; prędkość 11 / 13 / 15; promień ciała 2 / 3,2 / 4,8 (do 1,25 × przy szerokich modelach) |
| Stopień (rzadkość 1–5) | życie +20 %, cios +15 %, odrzut +6 % na stopień |
| Gwiazdki / trener | +8 % życia i siły na gwiazdkę (do 5); +3 % na poziom trenera |
| Złoto na minutę (pet stopnia 1) | środek **300**, ×2 **120**, ×1 **60**; Rare (stopień 3): 900 / 360 / 180 |
| Premie | wybicie 15 × stopień (dziki 10 × stopień); nagroda za głowę 10 + 3/s; złoty pet 6 × stopień za cios, 150 za wybicie; boss pula 400 (min. 80) |
| Jajka | 360 / 2000 / 8000 G; szanse (C/U/R/E/L): 58/30/11/1/0 · 20/42/30/7,5/0,5 · 0/28/42/25/5 % |
| Odpoczynek / arena / tempo | 30 s / najwyżej **6 petów**, dzikie do 4 / akcje: wiadro 3/s (zapas 4), ruch: 20/s (zapas 10), autopilot po 2,5 s |
| Łapanie (v3) | szansa 35 / 22 / 12 / 6 / 3 % (Common → Legendary), litość +3 pkt za nieudaną próbę (najwyżej 90 %), pierwsze wybicie dzikiego — pewne; ucieczka 6 × stopień G, asysta 8 × stopień G |
| Odmiany (v3) | BIG 8 % (× 1,25 rozmiaru, +15 % siły) · GOLDEN 3 % (× 1,5 złota/s) · GIANT 0,5 % (× 1,6, +30 % siły) |
| Dzikie i ALPHA (v3) | rozmiar według rzadkości × 1 / 1,08 / 1,18 / 1,3 / 1,45; ALPHA od Rare, × 1,5 rozmiaru, × 3 życia, +20 pkt szansy, co najmniej BIG, 120 G (asysta 30) |
| Zegar (v3, UTC) | boss :00 i :30, złoty boss :15 i :45, ALPHA co 5 min (:02, :07, …) |
| Wylęgarnia (v3) | 2 miejsca; 2 min / 30 min / 4 h; przyspieszenie 1,5 / 1 / 0,6 G za sekundę |
| Prezent (v3) | 200 G, 400 G, Forest Egg, 800 G, 1200 G, Swamp Egg, 2000 G (w kółko; seria nie przepada) |
| Lot (v2) | odrzut = siła × (1 + 1,6 × ubytek życia) / masa; od 40 st/s (i przy krytyku lub ciosie kończącym) w powietrze: vy = 0,55 × v (najwyżej 45), grawitacja 70, odbicie przy lądowaniu; zderzenie: odbicie sprężyste 0,6 |

**Tempo jajek** (`tempo.py`, 2000 przebiegów, samotny gracz, model przybliżony): pierwsze jajko darmowe od razu,
pierwsze kupione — mediana **1,5 min** (pomaga złoty pet w 1,5 min), pierwszy Rare — mediana **6,8 min** (65 % graczy
do 10 min), pierwszy Epic — **29 % do 30 min** (mediana później; model nie liczy gwiazdek ani trenera — do strojenia po
graniu). Symulacja walki (logika, v2, 5 petów, 60 s): pet żyje średnio ok. 15 s, pierwsze wybicie na arenie po ok. 9 s
(9 RING OUT i 3 KO na 12 wybić); gracz z
Common-ami zarabia ok. 150–190 G/min (odpoczynek 30 s: czekanie bez peta 2–30 s na 4 min zamiast ok. 95 s przy 60 s).

## Jak zbudować i zagrać

```
python -B swiat/pet_arena/dane.py                    # po zmianie ustawień: zrodla/DanePetArena.luau
python -B swiat/pet_arena/testy/test_pet_arena.py    # testy bez Studio (--tabela: symulacja walki)
python -B swiat/pet_arena/tempo.py                   # rachunek tempa jajek (Monte Carlo)
python -B swiat/pet_arena/zbuduj.py --sucho          # plan i kontrola Luau bez Studio
python -B swiat/pet_arena/zbuduj.py                  # budowa w otwartym miejscu PetArena (ok. 3 s; --studio <id>)
python -B swiat/pet_arena/zbuduj.py --skrypty        # po zmianie samego kodu
python -B swiat/pet_arena/zbuduj.py --stan | --usun | --wlacz on|off
python -B swiat/pet_arena/testy/proba_play.py <folder poza repo> [--studio <id>]   # próba w Play (P00–P40)
python -B swiat/pet_arena/testy/demo_wideo.py <plik.mp4 poza repo>                  # film demo ok. 40 s + plansza
```

Zagrać: otworzyć plik miejsca `PetArena.rbxlx` w Studio, **Play** (F5) — gracz staje w swojej loży nad areną z petem w dłoni,
stuka / klika w arenę; pet walczy sam, a cios kończący w dzikiego potwora losuje złapanie (pierwsze pewne). Sterowanie petem jest dodatkiem (przytrzymanie lewej połowy ekranu, WASD / strzałki, lewa gałka pada). Budowa odmawia w miejscu obecnej gry B&C, działa tylko w trybie Edit i we własnym kontenerze.

## Publikacja jako prywatna wersja testowa — kroki dla ludzi (decyzja ludzi, agent nie publikuje)

1. W Studio: **File → New** (puste miejsce, Baseplate) i zapis jako osobne doświadczenie (**File → Publish to Roblox As…
   → Create new experience**, nazwa robocza „Pet Arena”, prywatne).
2. W terminalu: `python -B swiat/pet_arena/zbuduj.py --publikacja --studio <id tego okna>` (skrypty bez strażnika
   Studio, wszystko inne jak w pliku lokalnym), potem w Studio **File → Publish to Roblox**.
3. Na stronie doświadczenia (Creator Hub): **Access → Private**, dodać testera (Paweł / znajomi), włączyć **Enable
   Studio Access to API Services** tylko jeśli chcemy zapis w wersji testowej (bez tego gra działa w pamięci).
4. Ikona i miniatury: na wzór `swiat/bonk/grafika/` (osobne zlecenie). Po teście — wrażenia do `B&C/Wytwórnia/Lekcje z prototypów.md`.

## Struktura

| Plik | Co |
|---|---|
| `ustawienia.json` | jedyne źródło liczb (v3 także: dzikie, łapanie, odmiany, alfa, zegar, wylęgarnia, prezent, nowy potwór): scena, strefy, kamera, walka, rzut, złoto, nagroda, umiejętność, odpoczynek, boty, gracz, gwiazdki, jajka, tarcza, trener, wydarzenia, boss, złoty pet, zapis, tablice, pokazanie, klasy wagi, rzadkości, 12 petów, teksty, dźwięki |
| `dane.py` | generator `zrodla/DanePetArena.luau`, wzorców (12 petów, 3 jajka, 2 bossowie) i części sceny (965, v2 koloseum: arena i wzgórze króla, mur z blankami, 5 stopni trybun, kibice w 8 sektorach, proporce, paleniska z ogniem, brama bossa, loże graczy, maty, cokoły jajek); rzut kamery na ekran (test kadru) |
| `tempo.py` | rachunek tempa jajek (pierwsze jajko, pierwszy Rare, pierwszy Epic) |
| `zbuduj.py` | budowa w Studio: kontener, moduły i skrypty, sygnały, scena, wzorce, stanowisko jajek, tablice wyników, napisy stref, SpawnLocation, Lighting; `--skrypty`, `--stan`, `--usun`, `--wlacz`, `--publikacja` |
| `zrodla/LogikaPetArena.luau` | czyste rachunki (też w testach bez Studio): walka, umiejętności, król, złoto, boty, tarcza, boss, złoty pet, jajka, kolekcja i gwiazdki, trener, profil v2, zapis z podanym magazynem, tablice |
| `zrodla/SerwerPetArena.server.luau` | serwer: gracze, rzuty, umiejętności, jajka, drużyna, trening, wydarzenia, nagrody, zapis, tablice, komunikaty, migawki, haczyki prób |
| `zrodla/KlientPetArena.client.luau` | klient: widoki petów i bossa, loty, RING OUT / KO, korona, napisy, słowa, soczystość, ręce awatarów, kamera, wejście (dotyk, mysz, klawiatura, pad), haczyki prób |
| `zrodla/InterfejsPetArena.luau`, `zrodla/OknaPetArena.luau`, `zrodla/EfektyPetArena.luau` | ekran (rogi), okna (EGGS, PETS / INDEX, wyklucie), efekty w świecie |
| `testy/test_pet_arena.py`, `testy/proba_play.py`, `testy/demo_wideo.py` | testy bez Studio, próba w Play, film demo |
| `klatki/` | zrzuty z próby („Player 1”, bez nazwy konta i listy graczy) |

W Studio (`Workspace/PetArenaGra`, atrybut `Wygenerowane`): `Scena/{Arena, Wzgorze, Mur, MurZewn, Trybuny, Kibice1–8,
Proporce, Paleniska, Ogien1–7, Brama, Loze, Maty, Jajka}`, `Stanowisko/Jajko1–3`, `Tablice/{Tablica1–4, TytulGry}` (4 — CATCH CHANCES; tytuł nad bramą), `Wzorce/{Pet_<id>, Jajko_<model>, Boss_<model>}`
(w grze serwer przenosi je do `ReplicatedStorage/PetArenaWzorce`), `Start` (SpawnLocation), `Moduly/*`, `SerwerPetArena`,
`KlientPetArena`, `Sygnaly/{Akcja, Zdarzenia, Stan, SterowanieSerwera, SterowanieKlienta}`. Atrybuty kontenera:
`PetArenaWlaczony`, `Skrot`, w grze `SerwerGotowy`, `WzorceGotowe`, `ZapisStan`, `ZapisMagazyn`, `PA_WydTyp`, `PA_WydT`.

**Sieć:** od klienta tylko `Sygnaly/Akcja (rodzaj, a, b, c)`: `"rzut", nr, x, z` · `"umiejetnosc"` · `"wybierz", nr` ·
`"jajko", nr` (v3: kupione → wylęgarnia) · `"wykluj", miejsce` · `"przyspiesz", miejsce` · `"prezent"` · `"druzyna", { id, … }` · `"trening", bool` · `"ruch", x, z` (v2: kierunek długości ≤ 1 albo nil =
autopilot; osobne wiadro 20/s) — serwer sprawdza typ rodzaju i argumentów, wiadro tempa,
cel, limit areny, jednego peta gracza, odpoczynek, złoto (darmowe tylko pierwsze jajko), przerwę między jajkami,
posiadanie petów w drużynie. Do klientów: `Sygnaly/Stan` (UnreliableRemoteEvent, bufor 14 + 28 bajtów na peta co
0,066 s: id, pet / boss, właściciel, faza, flagi stanów, x, z, życie, pasek, złoto/s, kierunek, gwiazdki, tarcza / boss /
złoty, v2: wysokość y; v3 w tym samym bajcie flag: BIG 8, GIANT 16, GOLDEN 32, ALPHA 64) i `Sygnaly/Zdarzenia` (`rzut`, `ladowanie`, `cios`, `umiejetnosc`, `ladowanie_skoku`, `odbicie`, `odbicie_slime`,
`ringout`, `ko`, `zderzenie`, `upadek`, v3: `zlapanie`, `ucieczka`, `alfa`, `do_wylegarni`, `prezent`, `krol`, `krol_stracil`, `zloto`, `zloto_cios`, `boss`, `boss_fala`, `boss_uciekl`, `zloty`,
`zloty_uciekl`, `wyklucie`, `poziom`, `ogloszenie`, `odmowa`). Stan gracza w atrybutach `PA_*` (tylko serwer): `PA_Slot`,
`PA_Nazwa`, `PA_Zloto`, `PA_GS`, `PA_Pet`, `PA_Rzucil`, `PA_Wybicia`, `PA_Druzyna` („id:gwiazdki,…”), `PA_Odpoczynek`,
`PA_Kolekcja`, `PA_Ksiega`, `PA_Wybrany`, `PA_NaArenie`, `PA_Poziom`, `PA_Xp`, `PA_XpPotrzeba`, `PA_Samouczek`,
`PA_Trening`, `PA_Najlepszy`, `PA_ProfilGotowy`.

## Próby w Studio

`python -B swiat/pet_arena/testy/proba_play.py <folder poza repo>` — **41/41 OK** (21.11.2026 ok. 20:30, v3, miejsce w
chmurze „Throw & Catch Monsters”, okno Studio zmaksymalizowane przy nocnym zaciemnieniu). Pierwszy przebieg v3: 39/41 —
P02 (małe okno Studio 761 × 635: arena wychodziła poza kadr w poziomie → kamera całości cofa się na wąskich ekranach) i
P13 (pulsujący EGGS nachodził na PETS → mniejszy puls). Testy bez Studio: **41 OK**:
- etapy 1–2 i v2: dane, kadr kamery na 4 ekranach, logika, zapis z atrapą magazynu, sterowanie, zderzenia, lot, tron;
- v3: dzicy z tabeli i rozmiar według rzadkości, pewne pierwsze złapanie i litość, odmiany, asysty, zegar wydarzeń,
  wylęgarnia z atrapą zegara, dzienny prezent, profil v3 przez zapis.

| Punkt | Wynik |
|---|---|
| P00–P04 | budowa zgodna (965 części, 17 wzorców); „Player 1”, zapis w próbie wyłączony; cała arena w kadrze (okno i telefon); dźwięki 28/28; pierwszy rzut **4,0 s** od wejścia; odrzut 14 → 30 przy 25 % życia |
| P05–P12, P14 | RING OUT z kamerą lotu, KO, złoto 5 / 2 / 1 G/s, król i nagroda, umiejętności, dzikie pety, limit 6 (ARENA FULL!); **6 petów na emulacji telefonu: 16,7 ms (60 kl./s)** |
| P17–P27 (etap 2) | jajka (darmowe od razu, kupione → wylęgarnia), gwiazdki, drużyna i INDEX, boss (zapowiedź w panelu NEXT), złoty boss, tarcza, trener, zapis w pamięci, pad, tablet, tablice |
| P28–P33 (v2) | wielkość według wagi (dzicy dodatkowo według rzadkości: troll 18,7 st), zderzenia i lot, kamera (bez peta i na autopilocie cała arena, przy sterowaniu za petem — pet 103 pt), wzgórze (37 monet w 6 s), sterowanie, opóźnienie 2 × 60 ms |
| P34 panel NEXT i zegar | „NEXT: BOSS in 1:02” i „NEW MONSTER in 8 days” od wejścia; przyspieszony zegar sam odpala wydarzenie |
| P35 rzuć → wybij → złap | podpowiedź „Knock out wild monsters to catch them!”, wybity Leaf Fox — **pewne pierwsze złapanie**, scena CAUGHT!, pet w kolekcji |
| P36 ucieczka | ESCAPED!, +19 złota, litość Common 1 |
| P37 odmiana GIANT | ogłoszenie na serwerze; złapany troll GIANT na arenie: 23 st (× 1,6), napis „GIANT” nad petem |
| P38 ALPHA | zapowiedź „ALPHA MONSTER!”, ALPHA Thorn Wolf 10,6 st (× 1,18 × 1,5), ostatni cios — złapany |
| P39 wylęgarnia | Swamp Egg do wylęgarni, po 30 min (atrapa zegara) „YOUR EGG IS READY!” i HATCH!, przyspieszenie za 1800 G |
| P40 prezent | okno DAILY GIFT, +200 G, „Tomorrow: +400 G”, następnego dnia seria 2 |
| P13 telefon 667 × 375 | wszystko w ekranie bez nakładania (z panelem NEXT i GIFT), najmniejszy przycisk 46 pt; cała arena na autopilocie, za petem przy sterowaniu (pet 80–140 pt), drążek tylko pod palcem |
| P15, P16 | konsola bez błędów pakietu; Studio w Edit |

Zrzuty (`klatki/`, „Player 1”, bez nazwy konta i listy graczy): `pa_wejscie`, `pa_rzut`, `pa_wybicie_lot`, `pa_ko`,
`pa_krol`, `pa_umiejetnosc_troll`, `pa_umiejetnosc_toad`, `pa_arena`, `pa_szesc_petow`, `pa_wyklucie`, `pa_okno_pety`,
`pa_ksiega`, `pa_boss`, `pa_boss_nagroda`, `pa_zloty`, `pa_trening`, `pa_kamera_pet`, `pa_wzgorze`, `pa_telefon`;
v3: `pa_zlapanie` (CAUGHT!), `pa_odmiana` (GIANT), `pa_alfa`, `pa_wylegarnia`, `pa_prezent`.
Film demo v3 (33 s, 1280 × 720) i plansza klatek leżą poza repo (`testy/demo_wideo.py`). Sceny: dzikie wchodzą bramą i
rzut, wybicie i CAUGHT! (Croaker), CAUGHT! GIANT · EPIC Forest Troll, olbrzymi troll na tronie z napisem tytułu nad
bramą, panel NEXT i ALPHA, jajko w wylęgarni (29:58 → HATCH!) i wyklucie BIG · RARE Dragonfly.

## Ograniczenia i znane problemy

- v3: szanse, odmiany i czasy wylęgarni to propozycja bez pomiaru — rachunek tempa (`tempo.py`) nie liczy jeszcze łapania.
  Złapane potwory dają kopie (gwiazdki) szybciej niż jajka; do strojenia po graniu.
- v3: zegar wydarzeń jest wspólny dla wszystkich serwerów (UTC), więc nie zależy od liczby graczy. ALPHA co 5 minut może
  być za często przy pustym serwerze.
- v3: wylęgarnia i prezent liczą czas z `os.time()` serwera. Zapis w pliku lokalnym w Play działa w pamięci (znacznik
  próby), więc „poza grą” sprawdzone tylko atrapą zegara (`czas_plus`) i testem logiki.
- v3: ALPHA może na chwilę przekroczyć limit 6 petów (wchodzi zawsze).
- Okno Studio było małe (761 × 635 — panele). Kamera całości cofa się teraz na wąskich ekranach (tablet 4:3, okno),
  a do filmu i ostatniej próby okno Studio było zmaksymalizowane (potem przywrócone).

- v2 zmieniła wygląd, skalę i sterowanie, ale **zasady walki** (siły, życie, umiejętności) są tylko przestrojone do nowej
  skali (symulacja: pet żyje średnio ok. 15 s) — Karol: system walki dopracujemy później.
- Przewidywanie ruchu własnego peta: przy sztucznym opóźnieniu 2 × 60 ms (narzędzie Studio `settings().Network`, potem
  przywrócone do 0) pet rusza u gracza od razu, serwer dociąga go łagodnie; przy ciosach i lotach widok idzie za
  serwerem (bez przewidywania), więc odrzut może pojawić się z opóźnieniem sieci.
- Fala bossa osłabiona (siła 32), żeby lekkie pety nie wylatywały za każdym tupnięciem.
- Zapis sprawdzony testem z atrapą magazynu; w pliku lokalnym w Play działa w pamięci (znacznik próby).
- Tempo jajek to model (`tempo.py`), nie pomiar.
- Ekran to atrapy (docelowe przyciski i okna — Paweł, Figma); napisy nad petami i graczami są na warstwie 2D.
- Kibice i ogień animowane 20 razy na sekundę jednym `BulkMoveTo` (tanio); brak muzyki.
- W chwili umiejętności przy królu bywa naraz kilka słów (KING!, nazwa umiejętności, CRIT!, POW!) — przy bitce na
  szczycie jest tłoczno; do przycięcia razem z docelowym UI.
- Kamera za petem trzyma peta na ok. 100 pt (telefon) — na dużym monitorze pet zajmuje ok. 1/3 wysokości ekranu, a
  sąsiadów dalej niż ok. 15 st widać dopiero w widoku VIEW.

## Co dalej (propozycja)

Granie ludzi (Karol rano): czy po 10 min dalej wrzucają, czy czekają z umiejętnością, ile razy się śmieją, czy pytają
„co wypadnie z jajka”. Potem: strojenie odpoczynku i cen, osobne areny albo serwery według stopnia, codzienna nagroda,
nowy pet co tydzień, wydarzenie o stałej godzinie, ikona i miniatury, prywatna publikacja.
