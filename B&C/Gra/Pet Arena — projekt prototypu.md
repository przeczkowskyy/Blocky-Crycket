---
status: propozycja
tags: [gra, pet-arena, prototyp, rdzeń]
źródło: "D-118 — polecenie Karola z 20.11.2026 na czacie po sesji głównej; pomysł Karola z sesji 20.11; projekt agenta"
---
# Pet Arena — projekt prototypu

> [!info] W skrócie
> **Wrzucasz swojego peta do dołu-areny, trzymasz złoty środek i wybijasz innych.** Pet walczy sam, ale to gracz decyduje, gdzie go wrzucić i kiedy odpalić umiejętność. Złoto leci co sekundę — tym więcej, im bliżej środka. Za złoto jajka i lepsze pety. Osobna, samowystarczalna gra w pakiecie `swiat/pet_arena/`, we własnym miejscu Roblox. Wszystkie liczby to propozycja do pomiaru. Karta i krytyka: [[Pet Arena]].

## Gra w jednym zdaniu
*Throw your pet into the pit, hold the golden center, knock the others out.*

## Scena
Okrągły **dół**; gracze stoją dookoła na obrzeżu (trybuna) i patrzą w dół. W dole okrągła **platforma-arena** otoczona fosą. Na platformie trzy strefy: **złoty środek**, pierścień środkowy, pierścień zewnętrzny. Za plecami graczy stanowiska: jajka, mata treningowa, tablice. Styl jak nasze mapy z klocków, komiksowe efekty.

## Pętla
1. **THROW — gdzie.** Gracz wskazuje miejsce na arenie (telefon: stuknięcie w arenę, komputer: klik, pad: celownik i przycisk) — pet leci łukiem z jego ręki i tam ląduje. Bez kolejki, w dowolnej chwili; jeden pet gracza naraz, na arenie najwyżej 8 petów (gdy pełna — krótki napis, miejsce zwalnia się co chwilę).
2. **Pet walczy sam:** idzie do środka i bije najbliższego w zasięgu. Cios to obrażenia i odrzut.
3. **ABILITY — kiedy.** Pasek umiejętności ładuje się z czasem i od ciosów; gracz odpala ją jednym przyciskiem w wybranym momencie (budowanie napięcia: czekać, aż trzech stanie obok, aż rywal podejdzie do krawędzi).
4. **Złoto na sekundę:** zewnętrzny pierścień ×1, środkowy ×2, złoty środek ×5 (mieści 1–2 pety) — razy stopień peta. Im dłużej pet się utrzyma i im bliżej środka, tym więcej złota. Liczba „+G/s” nad petem i u gracza.
5. **Odrzut jak w bijatykach platformowych:** im mniej życia, tym dalej pet leci po ciosie; lekki leci dalej, ciężki bliżej, ale łatwiej go trafić. Trochę losowości: krytyki i mocniejsze wybicia — przyprawa, nie loteria.
6. **Koniec peta:** **RING OUT** (wypchnięty za krawędź wpada do fosy, gejzer wystrzeliwuje go komicznie w niebo i pet wraca do właściciela) albo **KO** (życie 0 — gwiazdki i odlot). Bez kary: ten pet odpoczywa ok. minuty, w tym czasie można wrzucić innego — stąd sens posiadania kilku.
7. **Nagroda za głowę:** pet w złotym środku nosi koronę i rosnącą nagrodę; kto go wybije, zgarnia ją. Środek zawsze ściąga ataki — silny nie stoi tam bezkarnie.
8. **Dzikie pety** (boty) dopełniają arenę do 4–5, żeby zawsze była walka, także gdy gracz jest sam.
9. **Wydarzenia serwera:** co ok. 3 minuty **BOSS** (wielki, zajmuje środek; wypchnięcie go to deszcz złota dla wszystkich, którzy trafili) i **GOLDEN PET** (złoty pet: każdy cios to monety), z zapowiedzią i odliczaniem.

## Rozwój
- **Jajka** przy arenie: trzy stopnie, stała cena, jawne szanse, tylko za złoto z gry (D-086, D-015, D-105). Pety w pięciu rzadkościach; rzadkość daje stopień (tier).
- **Drużyna:** do 3 petów „w ręce” (wybór przyciskami), reszta w kolekcji; **Księga petów** z sylwetkami.
- **Trener:** poziom gracza rośnie od czasu petów na arenie, wybić i treningu AFK na macie obok areny; daje procent życia i siły **wszystkim** petom — postęp nie przepada przy zmianie peta (pomysł Karola).
- **Pokazanie się:** pet i jego rzadkość widoczne dla wszystkich, korona króla środka, komunikaty (legendarny pet, wybicie króla, boss), tablice: złoto na sekundę, najdłużej w środku, wybicia.

## Uczciwość (propozycja agenta, wzór: ±2 stadia w Ant Evolution)
Jedna arena na start. **Tarcza słabszego:** pet o co najmniej 2 stopnie silniejszy zadaje słabszemu ok. 35% obrażeń i odrzutu (ikona tarczy). Silny pet zarabia więcej złota na sekundę, ale nie wymiata nowych graczy. Docelowo osobne areny albo serwery według stopnia — po pomiarze.

## Pety na start (propozycja, z istniejących modeli)
Waga: lekki 0,7 / średni 1,0 / ciężki 1,5 (dzieli odrzut). Stopień = rzadkość 1–5.

| Pet | Model | Rzadkość | Waga | Umiejętność |
|---|---|---|---|---|
| Slime | `lesny_slime` | Common | lekki | Bounce — odbija się rykoszetem między trzema najbliższymi |
| Acornling | `zoledziak` | Common | lekki | Headbutt — krótka szarża z mocnym wybiciem |
| Croaker | `rechotek` | Common | średni | Tongue — przyciąga wroga i przerzuca go za siebie |
| Shroomling | `muchomornik` | Uncommon | lekki | Spore Cloud — ogłusza wszystkich wokół na 1,5 s |
| Moss Snail | `mchowy_slimak` | Uncommon | ciężki | Shell — 3 s nie do ruszenia, ciosy odbijają napastników |
| Leaf Fox | `lisciolis` | Uncommon | lekki | Dash — przelot przez arenę po linii |
| Thorn Wolf | `cierniowy_wilk` | Rare | średni | Pounce — skok na króla środka |
| Wisp | `ognik` | Rare | lekki | Burn — podpala w stożku (obrażenia w czasie) |
| Dragonfly | `wazeczka` | Rare | lekki | Freeze — zamraża najbliższego na 2 s |
| Forest Troll | `lesny_troll` | Epic | ciężki | Ground Slam — fala odrzutu wokół |
| Ruin Armadillo | `pancernik_ruin` | Epic | ciężki | Roll — toczy się jak kula do kręgli przez całą arenę |
| Hut Toad | `ropucha_z_chatka` | Legendary | ciężki | Sky Dive — wskakuje na ścianę dołu i spada na arenę z wielką falą |

Bossowie: trzej Strażnicy z BONK (Grove Guardian, Mire Guardian, Vine Serpent).

## Pierwsza minuta
Gracz pojawia się na obrzeżu z dwoma petami startowymi; strzałka „Tap the arena to throw!”. Po 5 s jego pet już walczy, po 30–60 s pierwsze wybicie, w ciągu ok. 2 minut stać go na pierwsze jajko (pierwsze jajko może być darmowe jako krok samouczka). Cele do strojenia: pierwszy rzadki pet do 10 minut, pierwszy epicki ok. 30 minut.

## Czego nie ma w pierwszej wersji
Robuxów, handlu, krain, pałek, czatu głosowego. Koty i kot-policjant z pomysłu Pawła ([[Super Kitty Brawlers]]) — do rozważenia po teście rdzenia.

## Technika
- Pakiet `swiat/pet_arena/` na wzór `swiat/bonk/` (samowystarczalny: scena, wzorce petów, interfejs, dźwięki, zapis; nie importuje z BONK — kopiuje i przerabia). Własne miejsce Roblox (plik lokalny), kontener `Workspace/PetArenaGra`.
- **Walkę liczy serwer w 2D** (pozycje, prędkości, odrzut z tarciem, krawędź) w stałym kroku, bez fizyki Roblox; klienci rysują modele z wygładzaniem, loty i efekty — tanio na telefonie i odporne na oszustwa. Od klienta tylko: „rzuć tu” i „umiejętność”.
- Liczby w `ustawienia.json` → generator danych → moduł Luau; testy logiki bez Studio i próba w Play; interfejs po angielsku (D-045); telefon, komputer, pad.
- Z BONK przechodzą: wzorce potworów i petów, jajka i wyklucie, Księga, efekty komiksowe i lot, zapis z ochroną prób, narzędzia budowy i prób, ikona i miniatury jako wzór.

## Miary testu (granie we dwóch i z dziećmi znajomych)
Czy po 10 minutach dalej wrzucają; czy mówią o tym, którego peta i gdzie wrzucić; czy czekają z umiejętnością na moment; ile razy się śmieją przy wybiciach; czy pytają „co wypadnie z jajka”.

## Kierunek po analizie trendu (21.11) — propozycja agenta z upoważnienia Karola
Karol 21.11: gracz ma sterować petem zamiast tylko oglądać; 10 petów to za dużo („potwory stoją na potworach”); „przyspieszamy tempo, żeby wstrzelić się w trend”; decyzję o kształcie zostawił agentowi. Analiza: [[Pet Arena — ocena wobec trendu 2026-11-21]].
- **Sterowanie z autopilotem:** po rzucie gracz kieruje petem (drążek, WASD, gałka), cios jest automatyczny, umiejętność na przycisk; gdy gracz puści sterowanie, pet walczy sam. Domyślna ścieżka nowego gracza nie wymaga drążka (rzuć → pet walczy → stuknij ABILITY).
- **6 petów na arenie**, duża arena, ciała się przepychają; **na złotym szczycie mieści się jeden pet** (tron) — czytelna walka o tron zamiast tłoku.
- **Zwrot 1 — „Wybijesz, to zabierasz”:** dzikie potwory na arenie to zdobycz: wybicie daje szansę na złapanie potwora albo jego jajko; rzadkie odmiany różnią się rozmiarem i kolorem; złapanie ogłaszane na serwerze. Trafia w najszybciej rosnącą pętlę z petami i daje niewiadomą przy każdym wybiciu.
- **Zwrot 2 — „Jutro na arenie”:** wydarzenia o stałych porach (złoty pet co pełną godzinę, boss wieczorem), jajka wylęgające się także, gdy gracza nie ma, zapowiedziany nowy pet na dzień ósmy.
- **Zwrot 3 — „Rzuć z kumplem”** (pierwsza aktualizacja): premia za znajomego na arenie, drużyny.
- **Okno czasowe:** prywatny test z ludźmi spoza zespołu do ok. 28.11, publiczny test (pierwsi gracze to osoby 16+) najpóźniej ok. 5.12; po ok. 15.12 będziemy spóźnieni. Jeśli w prywatnym teście ludzie przestają rzucać po kilku minutach — nie publikować, wracamy do karty.
- **Wstrzymane do grania ludzi spoza zespołu:** widowiskowe efekty umiejętności i dalsze dopieszczanie wyglądu (rdzeń, skala i wyklucie zostają w przebudowie).
- **Tytuł roboczy: „Throw & Catch Monsters”** (zgoda Karola 21.11 na rekomendację agenta; drugi kandydat: „Throw Pets, Take the Throne”).
- **Środek ciężkości gry (propozycja agenta po zgodzie Karola „jestem otwarty na zmiany koncepcji”):** z „bitki graczy na arenie” na **„rzucaj i łap potwory”** — dzikie potwory do złapania są stałą treścią areny, kolekcja jest celem, a walka graczy o tron jest przyprawą i sposobem pokazania się. To ta sama budowa, ale bliżej tego, co dziś rośnie (pety zdobywane w walce), i z powodem powrotu.
- **Pułap nakładów i warunek wyjścia (odpowiedź na „jeśli wiemy, że nie wyjdzie, nie ma co testować”):** do decyzji idą jeszcze tylko: dokończenie przebudowy, jeden etap ze zwrotami i prywatny test w tym tygodniu. Bez reklamy, bez publicznego startu i bez dalszego połysku przed wynikiem. **Kończymy z tą grą**, jeśli w prywatnym teście ludzie przestają rzucać po kilku minutach albo następnego dnia sami nie wracają; wtedy zasoby (rzut, pety, łapanie, wyklucie) idą do następnego pomysłu z lejka.

## Stan budowy
- [x] 2026-11-20 (wieczór) — **etap 1, rdzeń:** dół-arena z trybuną, rzut w wybrane miejsce, walka liczona na serwerze w 2D, odrzut rosnący z ubytkiem życia, RING OUT i KO, strefy złota, nagroda za głowę, 12 petów z umiejętnościami, dzikie pety, drużyna z odpoczynkiem. Próba w Studio 17/17.
- [x] 2026-11-20 (noc) — **etap 2:** większe pety i odkryty środek ekranu, „czucie” ciosu, odpoczynek 30 s, jajka w trzech stopniach (pierwsze darmowe), gwiazdki za kopie, drużyna i Księga, boss i złoty pet z odliczaniem, tarcza słabszego, trener i mata AFK, tablice, zapis, pad, demo wideo. Próba w Studio 28/28, testy 28 OK, 60 klatek na sekundę przy 8 petach. Szczegóły: `swiat/pet_arena/README.md`.
- [x] 2026-11-21 — **przebudowa v2** po uwagach Karola: arena o promieniu 40 i najwyżej 6 petów, wielkość według wagi, zderzenia z przekazaniem pędu i wybicia ponad trybuny, wzgórze króla z tronem dla jednego, jasne koloseum, sterowanie petem z autopilotem (domyślnie bez drążka), nowe wyklucie, złoty boss. Próba w Studio 34/34, testy 33 OK.
- [x] 2026-11-21 — **prywatna wersja testowa** „Throw & Catch Monsters” (placeId 93704244631419, universe 10778282381; konto Karola, prywatna, wszystkie urządzenia; Paweł zaproszony jako tester). Wejście: aplikacja Roblox → https://www.roblox.com/games/93704244631419
- [ ] etap v3 — „Wybijesz, to zabierasz” i „Jutro na arenie” (w budowie w nocy 21/22.11), potem aktualizacja wersji testowej.
- [ ] granie ludzi spoza zespołu do ok. 28.11 i decyzja według warunku wyjścia.

## Do strojenia po graniu
- **Odpoczynek peta: 30 s** (Karol mówił o ok. minucie; przy 60 s gracz przez ok. 40% czasu nie miał kogo rzucić — jedna liczba w ustawieniach).
- Tłok w środku przy 7–8 petach (mniej petów naraz albo większa arena).
- Ceny jajek: pierwszy rzadki pet ok. 7 min (cel do 10), pierwszy epicki za wolno (ok. 29% graczy w 30 min).
- Złoto z wydarzeń dla samotnego gracza (cała pula bossa trafia do jednej osoby).
- Braki: muzyka, zamach rzutu widoczny dla innych graczy, prawdziwy magazyn zapisu (wymaga publikacji), próba na prawdziwym telefonie i padzie, ikona i miniatury.

## Uwagi Karola po pierwszym podglądzie (sesja 21.11) — propozycje
Karol jest z pierwszego podglądu „bardzo niezadowolony”. Nic z tej listy nie jest zatwierdzone; zapis: [[Sesja główna 2026-11-21 — zapis ustaleń]].
- **Arena** ok. 4 razy większa (miejsce na ok. 10 petów, gra taktyczna) i zamknięta; strefa zbierania złota do poprawy — D-119. Agent: sprawdzić dwie wielkości, bo przy całej arenie w kadrze pety wyjdą mniejsze, a wybicia rzadsze.
- **Wielkość petów** wyraźnie różna: duży pet duży, mały mały — D-120.
- **Wybicia:** krytyczny cios wyrzuca peta w powietrze jak w BONK, lepsze wypychanie, więcej statusów, boss cały złoty; ataki do dopracowania później — D-121.
- **Jajka i wyklucie:** jajka gładsze i podobne do jajek, konfetti i ozdobniki, efektowne umiejętności — D-122.
- **Interfejs** robi Paweł (Higgsfield, Figma); w grze na razie zaślepki — D-123.
- **Styl sceny** (loch czy jaskrawe kolory) — bez wyboru, pytanie 78 w [[Pytania otwarte]].

## Do ustalenia
- Styl sceny: loch czy jaskrawa, zamknięta arena (pytanie 78).
- Nazwa gry (robocza „Pet Arena”).
- Czas odpoczynku peta (ok. minuty) i liczba petów na arenie (8) — po graniu.
- Publikacja jako prywatna wersja testowa — decyzja ludzi.

## Powiązane
- [[Pet Arena]] · [[00 Wytwórnia pomysłów]] · [[Mózg — zasady hitu Roblox]] · [[Lekcje z prototypów]] · [[BONK — projekt prototypu]] · [[Rejestr decyzji]]
