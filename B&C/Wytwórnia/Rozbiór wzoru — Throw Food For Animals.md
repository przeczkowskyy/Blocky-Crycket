---
status: propozycja
tags: [wytwórnia, badania, rozbiór]
źródło: "badanie agenta 2026-11-22 (strona gry, poradniki, napisy filmów, trackery, DevForum); fakty z linkami, wnioski oznaczone"
---
# Rozbiór wzoru — Throw Food For Animals

> [!info] W skrócie
> Jak dokładnie działa gra, w którą Karol „mógłby grać cały czas”: rzut, odsłona w kilku krokach (mnożnik szczęścia, stopień, rozmiar, kolor mutacji, zakryta nazwa), 19 krain odblokowywanych odległością rzutu, mutacje i rozmiary, sobotnie wydarzenia, liczby. **Nie kopiujemy tej gry** (Karol, 22.11) — to wzór zasad.
Oznaczenia: **[F]** fakt ze źródła (link przy zdaniu), **[W]** wniosek własny, **[?]** nie da się ustalić ze źródeł — podane najlepsze przybliżenie.

Główne źródło do scenki: napisy automatyczne z filmu „STARTING OVER with INFINITE LUCKY THROWS in Throw Food For Animals” ([YouTube PT7_XeaBh78](https://www.youtube.com/watch?v=PT7_XeaBh78)), w którym gracz zaczyna od zera (z płatnym szczęściem x100) i komentuje każdy rzut. Cytaty z napisów podaję po angielsku ze znacznikiem czasu filmu. Film jest zmontowany, więc jego czasy nie są czasem gry.

---

## 0. Karta gry — liczby

| Co | Wartość | Źródło |
|---|---|---|
| Twórca | grupa **Goofy Chupacabra** (id 670988975) | [F] [Roblox API](https://games.roblox.com/v1/games?universeIds=10766972131) |
| Utworzona | 18.09.2026; ostatnia aktualizacja 21.11.2026 | [F] tamże |
| Rozmiar serwera | **5 graczy** | [F] tamże (`maxPlayers: 5`) |
| Gracze teraz | ok. **329–331 tys.** (rano 22.11) | [F] tamże, [omni-search](https://apis.roblox.com/search-api/omni-search?searchQuery=for%20animals&sessionId=abc123&pageType=all) |
| Szczyt | **2,4–2,5 mln** naraz, 21.11.2026 (dzień wydarzenia/aktualizacji) | [F] [RoWatcher](https://rowatcher.com/games/10766972131/throw-food-for-animals/dying), [RoTrends](https://www.rotrends.com/game/10766972131/Throw-Food-For-Animals) |
| Średnio | 7 dni: ok. 285 tys.; 14 dni: 272 tys.; 30 dni: 173 tys. | [F] RoTrends, RoWatcher |
| Odwiedziny | ok. 399 mln; ulubione 380 tys. | [F] Roblox API |
| Ocena | 94,1% (209 601 👍 / 13 051 👎) | [F] [votes API](https://games.roblox.com/v1/games/votes?universeIds=10766972131) |
| Średnia sesja | **17,7 min** (−9% tydzień do tygodnia) | [F] RoTrends |
| Ranking | #1 Top Trending od 26.10; #3 Top Playing Now od 29.10; **#5 Top Earning** | [F] RoTrends |
| Monetyzacja | 2 przepustki + 15 produktów deweloperskich | [F] RoTrends, [game-passes API](https://apis.roblox.com/game-passes/v1/universes/10766972131/game-passes?passView=Full&pageSize=100) |

**Przebieg wzrostu [F]:** wydana 18.09, przez ponad miesiąc mała (zmiana 30-dniowa +101 024%, czyli startowała z kilkuset graczy — RoWatcher); pierwsze listy Up-and-Coming 25–26.10, czyli **równo z Halloween Update (25.10)** ([Bloxodes](https://bloxodes.com/wiki/throw-food-for-animals), RoTrends). Starszy odczyt RoWatcher z wyszukiwarki: szczyt 54 tys. 28.10 — dalej rosła tygodniowymi skokami.
**[W]** Gra nie „wystrzeliła” w dniu wydania — dojrzewała ponad 5 tygodni, a przełom dał pierwszy duży update sezonowy. Szczyt 2,5 mln przy średniej ok. 285 tys. pokazuje, że wydarzenie w sobotę daje 8–9× ruch zwykłego dnia.

---

## 1. Pierwsze 60 sekund nowego gracza

- [F] Start z darmową **marchewką** (Carrot). Rzut marchewką przyciąga np. żabę albo królika ([Bloxodes wiki](https://bloxodes.com/wiki/throw-food-for-animals), [games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/)).
- [F] Kolejność z poradnika: rzut (celuj w 20 na mierniku) → zwierzę idzie do zagrody → kup lepsze jedzenie → powiększ bazę; **drążek do podciągania odblokowuje się po samouczku** ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/), [Bloxodes poradnik](https://bloxodes.com/articles/throw-food-for-animals-beginners-guide)).
- [F] Pierwsze zwierzęta zarabiają $1–3/s (ślimak $1/s, żaba $2/s, królik $3/s) ([game.guide](https://www.game.guide/throw-food-for-animals/catch-calculator)). Pierwszy drążek Wooden Bar kosztuje **$1**, Steel Bar **$50** ([Axeetech](https://axeetech.com/?p=120541)) — poradnik każe kupić Steel Bar przed następnym jedzeniem ([Bloxodes](https://bloxodes.com/articles/throw-food-for-animals-beginners-guide)).
- [F] W filmie gra **sama podpowiada następny krok**: „It's telling me to do something. Buy new food” (1:04), „it's telling me I could go buy something” (1:26) ([film](https://www.youtube.com/watch?v=PT7_XeaBh78)).
- [F] Układ bazy: sklep z jedzeniem (biało-niebieski budynek) na lewo od wejścia do bazy, przycisk powiększenia bazy na prawo od wejścia, stoisko sprzedaży (czerwono-białe) na prawo od miejsca rzutu, menu zwierząt po prawej stronie ekranu, Indeks po lewej ([Ofzen and Computing](https://www.ofzenandcomputing.com/throw-food-for-animals-beginner-guide/)).
- **[W] Przybliżony przebieg minuty:** 0–10 s: pojawienie się przy pasie rzutu, strzałka; 10–25 s: pierwszy rzut i pierwsza scenka; 25–40 s: zwierzę w zagrodzie, licznik $/s rusza; 40–60 s: kupno drążka za $1 i pierwsze podciągnięcia, poziom w górę. Dokładnych sekund samouczka żadne źródło nie podaje **[?]**.

---

## 2. Pętla krok po kroku

### 2.1 Rzut
- [F] Przytrzymaj i puść; **miernik 0–20**; im bliżej 20, tym dalej. **PERFECT** dodaje ok. +18–20 do mocy rzutu, **GREAT** ok. +15–18 ([Bloxodes — szczęście](https://bloxodes.com/articles/throw-food-for-animals-luck-guide), [Axeetech](https://axeetech.com/?p=120541)).
- [F] Odległość = **Throw Power** (z podciągania) + bonus z miernika. **Jedzenie nie dodaje odległości** ([Bloxodes wiki](https://bloxodes.com/wiki/throw-food-for-animals)). Każdy poziom = **+5 studów** ([Axeetech](https://axeetech.com/?p=120541)).
- [F] Celowania w bok nie ma — jest jeden pas („track”, „lane”), rzut leci wzdłuż niego przez kolejne krainy („we're going to need to get all the way down this track”, 1:43, [film](https://www.youtube.com/watch?v=PT7_XeaBh78)).
- [F] Przed rzutem przycisk **Details** pokazuje szanse mutacji przy obecnym ustawieniu ([games.gg — mutacje](https://games.gg/roblox/guides/roblox-throw-food-for-animals-mutations-sizes-guide/)).

### 2.2 Lot — szczęście rośnie w powietrzu
- [F] **Szczęście narasta, gdy jedzenie leci wzdłuż pasa**; liczy się wartość w miejscu lądowania ([Bloxodes — szczęście](https://bloxodes.com/articles/throw-food-for-animals-luck-guide), [Sportskeeda w wynikach wyszukiwania](https://www.sportskeeda.com/roblox-news/how-get-luck-throw-food-for-animals)). Według jednego poradnika od ok. 2,5× w Forest do ponad 20× w Taiga; w filmie: „this gives us 8.28x multi” po wejściu do Desert (3:53).
- [F] Lepsze jedzenie „daje więcej szczęścia w locie” ([Bloxodes](https://bloxodes.com/articles/throw-food-for-animals-luck-guide)).
- [F] Gracz widzi przekraczanie granic krain: „We're into the jungle just by like one little inch. We just crossed the line” (6:15).

### 2.3 Lądowanie i losowanie
- [F] Każda kraina dzieli się na **trzy części**: przednia — zwierzęta do rangi 4, środkowa — do rangi 6, tylna — każda ranga; najlepsze zwierzę wymaga lądowania w tylnej trzeciej (w trzech krainach dopiero od 90% głębokości) ([game.guide](https://www.game.guide/throw-food-for-animals/catch-calculator)).
- [F] **Jedzenie ustala, w którą rangę rzut „celuje”**, miejsce lądowania obcina rangi powyżej swojego sufitu ([game.guide](https://www.game.guide/throw-food-for-animals/catch-calculator)).
- [F] **Ochrona przed powtórką:** ostatnio złapane zwierzę jest **200× mniej prawdopodobne**, przedostatnie 2,5× mniej ([game.guide](https://www.game.guide/throw-food-for-animals/catch-calculator)).
- [W] Gra pilnuje, żeby kolejne rzuty prawie zawsze dawały *inne* zwierzę. To ważne dla emocji „co teraz przyjdzie”.

### 2.4 Scenka podejścia — co da się ustalić
Pełnego opisu klatka po klatce nie ma w żadnym poradniku. Poniżej to, co mówi film z napisami, plus poradniki. **[?] Czas trwania nie jest nigdzie podany.**

| Etap | Co widać / słychać | Źródło |
|---|---|---|
| 1. Lot | kamera leci za jedzeniem wzdłuż pasa; w dalekich krainach „the camera's going so fast” (27:08) | [F] [film](https://www.youtube.com/watch?v=PT7_XeaBh78) |
| 2. Licznik szczęścia | **narastający napis stopnia szczęścia i licznik „1 in X”**: „1 in 65. No, it's going up higher… impossible luck… One in 158,730” (0:20); kolejne stopnie: „Lucky. Super lucky. Insane. Legendary. Godly” (1:43, 5:17, 15:36), najwyższy „Impossible” | [F] film; napisy „LUCKY!” i „SUPER LUCKY!” na karcie wyniku — [Bloxodes](https://bloxodes.com/articles/throw-food-for-animals-luck-guide) |
| 3. Odsunięcie kamery = rozmiar | **kamera odjeżdża tym dalej, im większe zwierzę**: „Camera's panned out pretty big right now… it's pulling back. Yo, that thing is tall… as tall as the map” → Titanic (3:53–4:15); „the camera's panning back big. That's a good sign” (29:05); „pull back camera. Hey, that is tiny” (20:05) | [F] film |
| 4. Linia oczu | gracz ocenia wielkość po wysokości oczu: „the eye line is as high as the top of the wall, so this should be a good one” (15:36); „Oh, the eye line is high” (11:43) | [F] film |
| 5. Kolor poświaty = mutacja | „If it's like pink… It's looking pink… No, it's emerald” (13:57); jedzenie po płatnym rzucie robi się tęczowe („rainbow carrot”, 0:20) | [F] film; wygląd mutacji: złota — błyszczy, Diamond — kryształowy, Emerald — zielony, Ruby — czerwony, Rainbow — wielobarwny ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-mutations-sizes-guide/)) |
| 6. Nazwa jako puste litery | **imię zwierzęcia pokazane jako liczba liter do zgadywania**: „five letters. Somebody guess what that is” (2:27); „Five, six letters… Jackal” (4:38); „Three-letter word. Dog. I'm going for dog. That ain't a dog… Yak” (9:55); „that is a lot of letters. How are you supposed to guess that?” (23:46) | [F] film |
| 7. Dojście do jedzenia | zwierzę idzie zjeść: „Come for my watermelon”, „Eat the toast” (1:26, 4:38); zwierzę zwabione do jedzenia ([Sportskeeda w wynikach](https://www.sportskeeda.com/roblox-news/how-get-luck-throw-food-for-animals)) | [F] |
| 8. Odsłona | nazwa + rozmiar + mutacja + dochód: „Hey, dingo. Titanic. 19.1 million” (4:15); „Rainbow mantis shrimp… 5.36 billion” (8:03) | [F] film |
| 9. Powrót | zwierzę idzie za graczem do bazy; przy pełnej: „your plot is full” → „Equip best”; „Bro's just standing at the door” (13:14) | [F] film |

**Sprawdzenie uwag właściciela studia:**
1. *„Kamera pokazuje nadchodzącego stwora, rozmiar sugeruje rzadkość”* — **potwierdzone częściowo [F]:** kamera odsuwa się proporcjonalnie do rozmiaru, a gracze czytają wielkość z linii oczu. Ale rozmiar to **osobna oś** (Big…Infinite), nie rzadkość gatunku — gatunek wynika z krainy, jedzenia i rangi. [W] Dla gracza to i tak „duży = dobry”, bo rozmiar mnoży dochód.
2. *„Otoczka w kolorze — złota, platynowa, rubinowa, tęczowa”* — **potwierdzone [F]:** mutacje to w kolejności **Gold → Diamond → Emerald → Ruby → Rainbow**; „platynowa” to najpewniej Diamond (kryształowy, jasny). Kolor widać przed odsłoną („It's looking pink… No, it's emerald”).
3. *„Do końca nie wiadomo, jaki to stwór”* — **potwierdzone [F]:** nazwa jest zakryta jako puste litery i gracze zgadują ją na głos aż do odsłony.
4. Dźwięk: w napisach są tylko oznaczenia „[music]” w chwilach licznika szczęścia **[?]** — rodzaju dźwięku nie da się ustalić bez obejrzenia.

### 2.5 Baza, dochód, wydatki
- [F] Tylko zwierzęta postawione w bazie zarabiają co sekundę; **zarabiają też offline** ([Bloxodes poradnik](https://bloxodes.com/articles/throw-food-for-animals-beginners-guide)).
- [F] Każde powiększenie bazy = **+2 miejsca** (koszt nie podany) ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/)); w filmie 12 miejsc po pierwszym powiększeniu, potem 14, później 20; „200T to upgrade my plot” (9:31) ([film](https://www.youtube.com/watch?v=PT7_XeaBh78)).
- [F] **Sprzedaż = 20 × dochód na sekundę** ([Axeetech](https://axeetech.com/?p=120541)); przycisk **Equip Best** ([Bloxodes wiki](https://bloxodes.com/wiki/throw-food-for-animals)).
- [F] Pieniądze idą na: jedzenie, drążki, powiększenie bazy; **ukończenie krainy w Indeksie daje gotówkę** (kwota nieznana) ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/)).
- [F] Przykładowe tempo z filmu (z płatnym szczęściem): badger 1k/s (1:04), 17k/s w Savannie (2:27), 23 mln/s łącznie po ok. 5 min filmu (5:38), 11,8 mld/s (8:03). Dochód rośnie mniej więcej o rząd wielkości na krainę.

---

## 3. Ulepszenia bohatera

- [F] **Jedna statystyka: Throw Power.** Szybkości ani innych cech poradniki nie opisują ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/)). U kopii analogicznie: wyciskanie na ławce (Shoot Arrows), bieżnie (Carry Food) — [Roblox API](https://games.roblox.com/v1/games?universeIds=10774784939,10774803726,10773616048,10775182046).
- [F] Trening: drążek robi **powtórzenie co 0,5 s** (120/min), także AFK; co 4–6 s wyskakuje **bonus do kliknięcia** = dodatkowe powtórzenie; zwykłe kliknięte zdarzenia chwilowo podwajają tempo ([Axeetech](https://axeetech.com/?p=120541), [Ofzen](https://www.ofzenandcomputing.com/throw-food-for-animals-beginner-guide/)).
- [F] **46 drążków**, każdy daje 2× XP poprzedniego: Wooden 1 XP/$1, Steel 2/$50, Gold 4/$2K, Cyan 8/$12K, Violet 16/$100K, Ruby 32/$600K, Amber 64/$6M, Chrome 128/$38M … Frost 8,2K/$4,2T … Reactor Core 35,2T ([Axeetech](https://axeetech.com/?p=120541)). Wooden Bar daje ok. 1 poziom na minutę do Savanny.
- [F] W filmie poziom maksymalny: „capped out. It won't go any further… level of 2284” (31:30) ([film](https://www.youtube.com/watch?v=PT7_XeaBh78)).
- [F] **Odrodzenia (rebirth) — brak w źródłach**; żaden poradnik go nie opisuje ([wyszukiwanie: games.gg, roonby, rosenberryrooms](https://games.gg/roblox/guides/roblox-throw-food-for-animals-mutations-sizes-guide/)). [W] Gra jest liniowa: pas ma koniec.

### Krainy (odblokowanie = tylko odległość rzutu)
[F] Tabela z [Axeetech](https://axeetech.com/?p=120541) (odległość / poziom dla rzutu PERFECT): Forest 5 st./1 · Savanna 173/28 · Desert 341/62 · Jungle 509/96 · Ocean 677/129 · Mountains 845/163 · Taiga 1K/201 · Winter 1,3K/244 · Prehistoric Forest 1,5K/292 · Deep Waters 1,8K/345 · Hell 2K/403 · Ancient Ruins 2,4K/470 · Mythical Paradise 2,8K/547 · Shadow Realm 3,2K/643 · Harvest Fields 4,1K/811 · Phantom Harbor 5,2K/1K · Nuclear Wasteland 6,2K/1,2K. Później doszły **Cursed Carnival i Eclipse Kingdom** — razem **19 krain** ([Bloxodes wiki](https://bloxodes.com/wiki/throw-food-for-animals)).

- [F] Liczba krain rosła: **15** (31.10, [games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/)) → **17** (ok. 11.11, [Beebom](https://beebom.com/all-animals-in-throw-food-for-animals/)) → **19** (po 8.11, Bloxodes). Wydarzenia „NEW MAP + ADMIN ABUSE” 31.10 i 7.11 ([Bloxodes wiki](https://bloxodes.com/wiki/throw-food-for-animals)) — **[W] nowa kraina co tydzień, w sobotę**.
- [F] **Następną krainę widać na pasie przed sobą:** „the next zone, which is just past the mountains. It's looking green” (9:55); „Yo, what's the next zone? I don't know, but we need to get there” (4:38) ([film](https://www.youtube.com/watch?v=PT7_XeaBh78)).
- [F] Indeks ma filtr „Limited” z **sylwetkami** zwierząt z wydarzenia ([Nerdschalk](https://nerdschalk.com/admin-abuse-dreamland-throw-food-for-animals/)). **[?]** Czy zwykłe niezłapane zwierzęta też są sylwetkami — nie znalazłem potwierdzenia (najpewniej tak, bo to wzór Indeksu w grach Roblox).
- [F] Przykładowe tempo z płatnym szczęściem (czas filmu, zmontowany): Savanna 2:27, Desert 3:53, Jungle 6:15, Ocean 7:23, Winter 12:49 („We only just started this game like 15 minutes ago”), koniec pasa po „one hour later” ([film](https://www.youtube.com/watch?v=PT7_XeaBh78)). Bez płatności poradnik ostrzega, że można utknąć w Forest „na tydzień” ([Ofzen](https://www.ofzenandcomputing.com/throw-food-for-animals-beginner-guide/)) — **[W]** to raczej przesada autora; realnie Savanna (poz. 28) w kilkanaście–kilkadziesiąt minut.

### Jedzenie
[F] 38–50 rodzajów w 16 poziomach (liczba rośnie z aktualizacjami): Carrot darmo, Apple $30, Banana $150, Toast $4K, Orange $20K, Pear $200K, Cheese $1M, Bread Loaf $12M, Watermelon $60M, Croissant $650M, Chocolate $3,2B, Mushroom $30B, Bacon $150B … Shank $6,8T, Steak $1,5Qa, Royal Steak $50Qa, Uranium Cake $9Qad ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/), [Axeetech](https://axeetech.com/?p=120541), [Bloxodes](https://bloxodes.com/wiki/throw-food-for-animals)). Kupione jedzenie trzeba **wyposażyć** (EQUIP) ([Bloxodes](https://bloxodes.com/articles/throw-food-for-animals-beginners-guide)).

---

## 4. Zwierzęta, mutacje, rozmiary

- [F] 128–148 zwierząt (liczba rośnie), rzadkości od Common do Sovereign ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/), [Bloxodes](https://bloxodes.com/wiki/throw-food-for-animals)); najlepiej zarabiający: Waste Harvester (410Dd/s) ([wyniki wyszukiwania — roonby/eldorado](https://www.eldorado.gg/blog/roblox-en/all-animals-in-throw-food-for-animals-index/)).
- [F] **Mutacje** (szansa zwykły rzut / płatny Lucky Throw / mnożnik dochodu i sprzedaży) ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-mutations-sizes-guide/)):
  Gold 13% / 9,5% / ×1,5 · Diamond 4% / 25% / ×3 · Emerald 2% / 29% / ×5 · Ruby 1% / 23% / ×10 · Rainbow 0,5% / 14% / ×20 · **brak mutacji 79,5%** ([theclick.gg w wynikach](https://www.theclick.gg/?p=112120)).
- [F] **Rozmiary** (zwykły / Lucky / mnożnik): Big 15% / 21% / ×1,5 · Large 3,5% / 42% / ×2,25 · Huge 0,97% / 22% / ×3,38 · Colossal 0,31% / 8,49% / ×5,06 · Gigantic 0,12% / 3,6% / ×7,59 · Titanic 0,05% / 1,48% / ×11,39 · Monstrous 0,02% / 0,6% / ×17,09 · Cosmic 0,008% / 0,24% / ×25,63 · Infinite 0,005% / 0,16% / ×38+ ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-mutations-sizes-guide/)). Każdy rozmiar ×1,5 poprzedniego.
- [F] Jedna mutacja + jeden rozmiar na zwierzę; łączą się **addytywnie** ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-mutations-sizes-guide/), [progameguides w wynikach](https://progameguides.com/roblox/throw-food-for-animals-mutations-sizes-chances-multipliers/)).
- [W] **Kluczowa liczba tempa:** ok. **20% rzutów ma kolorową poświatę** i ok. **20% ma jakiś rozmiar** — co drugi–trzeci rzut ma „coś specjalnego”. Niespodzianka jest częsta na niskim szczeblu i bardzo rzadka na wysokim (Infinite 1 na 20 000).
- [F] Wydarzenie Dreamland: **„Infusion”** — Dream Potion na zwierzę = +20% dochodu ([Nerdschalk](https://nerdschalk.com/admin-abuse-dreamland-throw-food-for-animals/)). W wersji 1 brak maszyn nakładających mutacje na posiadane zwierzęta i brak pogody ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-mutations-sizes-guide/)).
- **[?] Co widzą inni gracze** — źródła milczą. [W] Przy 5 graczach na serwerze i osobnych bazach inni widzą zapewne twoją bazę i zwierzęta w niej.

---

## 5. Głębia i „co dalej”

### Wydarzenia [F] ([Bloxodes wiki](https://bloxodes.com/wiki/throw-food-for-animals), czas pacyficzny)
| Wydarzenie | Kiedy | Czas |
|---|---|---|
| Halloween Update | 25.10–1.11 | tydzień |
| NEW MAP + ADMIN ABUSE | sob. 31.10 | 1 h |
| New Map + Admin Abuse | sob. 7.11 | 30 min |
| DREAMLAND EVENT | sob. 14.11 | 1 h |
| THANKSGIVING EVENT | sob. 21.11 – niedz. 22.11 | ok. 27 h |
| WINTER IS COMING | sob. 28.11 (zapowiedziane) | ok. 27 h |

- [F] **Admin abuse:** globalne „8x Luck” i „8x Training”; baner „BEN STARTED ADMIN LUCK IN EVERY SERVER!” z odliczaniem „5:00 left” ([Nerdschalk](https://nerdschalk.com/admin-abuse-dreamland-throw-food-for-animals/)).
- [F] **Dreamland:** co 30 min „habitat shift” — pięć krain zmienia się w Dreamland z 24–25 limitowanymi zwierzętami; minigra Wake Dragons z wagonika kolejki (rzucanie w śpiące smoki, 250 = Big Lucid Ironhide Rhino); nagrody za kolekcję: 12 → Super Lucky Throw ×2, 16 → ×3, 20 → Dream Potion ×4 ([Nerdschalk](https://nerdschalk.com/admin-abuse-dreamland-throw-food-for-animals/), [Beebom/wyniki](https://www.ofzenandcomputing.com/throw-food-for-animals-dreamland-event-guide/)).
- [F] **Zapowiedź w grze:** „There's a special event that has finally popped up. When the habitat shifts, catch these animals… there is an event in 11 minutes” (9:10); gracz czeka na start (12:29 „before this event starts in 3 minutes”) ([film](https://www.youtube.com/watch?v=PT7_XeaBh78)).
- [F] Szczyt 2,5 mln padł **w dzień wydarzenia 21.11** (RoWatcher). [W] Sobotnie wydarzenie z ograniczonym czasem to główny silnik powrotów; stały rytm „sobota = nowa mapa + admin” uczy graczy, kiedy wracać.

### Co trzyma [W, na podstawie faktów wyżej]
- **Po 10 min:** nowa kraina co kilka minut, każda z nową pulą zwierząt; zgadywanie nazwy po literach; częste poświaty.
- **Po godzinie:** pogoń za rozmiarami Colossal+ i mutacjami Ruby/Rainbow; Indeks krain z nagrodą; „następna kraina już widać na pasie”.
- **Następnego dnia:** dochód offline + trening AFK (gracze zostawiają awatara na drążku na noc — [Ofzen](https://www.ofzenandcomputing.com/throw-food-for-animals-beginner-guide/)); sobotnie wydarzenie i nowa mapa.
- Kody: **brak systemu kodów** (31.10) ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-beginners-guide/)). Pogody brak ([games.gg](https://games.gg/roblox/guides/roblox-throw-food-for-animals-mutations-sizes-guide/)).

---

## 6. Inni gracze
- [F] Serwer **5 osób** (Roblox API). [F] **Server Luck** kupiony za Robuxy podnosi szczęście **wszystkim na serwerze** na 15 min ([Bloxodes](https://bloxodes.com/articles/throw-food-for-animals-luck-guide)). Admin abuse działa na wszystkie serwery.
- **[?]** Handel, kradzież, pomaganie — nie znalazłem żadnej wzmianki; najpewniej brak. U kopii Throw Food For Baddies: **+15% dochodu za każdego przyjaciela** na serwerze ([Roblox API](https://games.roblox.com/v1/games?universeIds=10774784939,10774803726,10773616048,10775182046)).
- [W] Inni gracze są tu prawie nieważni — to gra solo obok siebie. Jedyny „społeczny” mechanizm to płatne szczęście dla serwera (ktoś płaci, wszyscy zyskują — to zachęca do bycia na serwerze z wydającym).

## 7. Monetyzacja
- [F] Przepustki: **x2 Cash 99 R$**, **x2 Training Power 149 R$** ([game-passes API](https://apis.roblox.com/game-passes/v1/universes/10766972131/game-passes?passView=Full&pageSize=100)).
- [F] 15 produktów deweloperskich (RoTrends), w tym: **Server Luck 2×/4×/8×/16× za 19/39/79/159 R$** na 15 min ([Bloxodes](https://bloxodes.com/articles/throw-food-for-animals-luck-guide)); **Lucky Throw** (płatny rzut z ×100 szczęścia, jedzenie robi się tęczowe; w filmie „For 450 Robux, we get a 60” — **[?]** brzmi jak pakiet 60 rzutów za 450 R$, nie potwierdzone), **Super Lucky Throw** ([Bloxodes](https://bloxodes.com/articles/throw-food-for-animals-luck-guide), [film](https://www.youtube.com/watch?v=PT7_XeaBh78)); jajka: Halloween Egg 80 R$ (3 za 200), Rainbow Egg 99 R$ (3 za 249) ([Axeetech](https://axeetech.com/?p=120541)).
- **[?]** Co jest najczęściej kupowane — nie jest publiczne. [W] Konstrukcja wskazuje na Lucky Throw: zmienia rozkład szans drastycznie (Large z 3,5% na 42%), a film „STARTING OVER with INFINITE LUCKY THROWS” to popularny format na YouTube.

## 8. Na co narzekają gracze
Reddit jest niedostępny dla moich narzędzi, a na DevForum nie ma wątków o tej grze. Poniżej **sygnały**, nie zebrane skargi:
- [F] **Koniec treści:** w filmie gracz z płatnym szczęściem dochodzi do końca pasa i limitu poziomu 2284 (31:30) — „Even with a times two, it does nothing” ([film](https://www.youtube.com/watch?v=PT7_XeaBh78)).
- [F] **Słabe zwierzęta wydarzenia:** „these dreamland pets, they ain't going to give us much… I'm wasting my throws” (13:57–14:16) (tamże).
- [F] **Długi grind na początku bez płacenia:** „gracze potrafią utknąć w Forest na tydzień” ([Ofzen](https://www.ofzenandcomputing.com/throw-food-for-animals-beginner-guide/)); średnia sesja spada (−9% tydzień do tygodnia, [RoTrends](https://www.rotrends.com/game/10766972131/Throw-Food-For-Animals)).
- [F] **Oszustwa:** w sieci są filmy ze skryptami „Instant Take Auto Farm Infinite Animal Dupe” ([YouTube](https://www.youtube.com/watch?v=PI-lu9A4bjw)).
- [W] **Brak sprawczości:** czynność gracza to jedno kliknięcie w miernik; reszta to losowanie i czekanie na drążku. Płatne szczęście przebija wszystko, co gracz może zrobić sam.
- [W] **Brak drugiego gracza:** 5 osób, nic wspólnego do zrobienia.
- [W] Ocena 94% mówi, że to nie są skargi, które odpychają masowo — to raczej miejsca, gdzie można dać więcej.

## Powiązane
- [[00 Wytwórnia pomysłów]] · [[Rozbiór wzoru — Throw Food For Animals]] · [[Kopie pętli rzutu — listopad 2026]] · [[Zasady pętli z odsłonięciem]] · [[Mózg — zasady hitu Roblox]] · [[Lekcje z prototypów]]
