---
status: propozycja
tags: [gra, mechanika, walka, balans]
źródło: "zlecenie Karola z 14.11 po trzech sesjach głównych; decyzje D-016, D-033 (odrzucona), D-051, D-054, D-055, D-058, D-059, D-060, D-061, D-062; korekty Karola z 14.11 (długość walki, brak kontrowania klas); poprawki po niezależnym przeglądzie"
---
# Walka v2 — silnik, klasy i umiejętności

> [!info] W skrócie
> Nowy silnik walki liczy całą walkę na serwerze i oddaje dziennik zdarzeń do odtworzenia (D-016). **Walka trwa, aż życie jednej strony spadnie do zera** — bez minimalnej liczby wymian, „ostatniego dechu” i ściskania czasu. Zwykły potwór może się ciągnąć, a strażnik paść od jednego ciosu, jeśli tak wypadnie. Są trzy klasy (D-054), sześć statystyk w modelu z D-062, 0–3 sloty umiejętności (D-055), zaklęcia broni (D-051), pet tylko jako mnożnik statystyk (D-059) i pięciu przeciwników lasu z łupem bez jajek (D-058, D-060). Klasy mają **inny styl, ale tę samą siłę** — tabela balansu niżej pokazuje, na ile to się udało (prawie wszędzie w celu; jedno znane odstępstwo przy Leśnym Slimie na poziomach 1–4). Wszystkie liczby są robocze; nic tu nie jest kanonem. Kod Luau silnika działa w Roblox Studio od 14.11.2026 (zgodność z symulacją 496/496), a od 15.11 walkę widać na ekranie w prototypie `Workspace/TestWalki2` — z prawdziwymi ruchami Wojownika i Maga.

## Silnik v3 — zmiany po sesji głównej 16.11 (noc 16/17.11.2026)
> [!warning] Ta sekcja jest nowsza niż reszta notatki
> Niżej opisany jest silnik v2. Tam, gdzie v3 mówi co innego (umiejętności, obrona, statusy, tabele balansu), obowiązuje ta sekcja i dokument `tools/walka/ZMIANY_SESJA_1611.md` (pełne zasady, liczby, tabele, 20 wyborów). Wszystko nadal jest propozycją liczb; zatwierdzone są kierunki z D-073 i D-088–D-091, a wskrzeszenie (D-094) czeka na podpisy.

- **Mana zamiast odnowień (D-089):** każda strona, także potwór, ma pasek 0–100; +40 za własny zwykły cios i +1,3 za każdy 1% utraconego życia; pełny pasek odpala następną aktywną umiejętność w rotacji slotów zamiast ciosu. Mana nie jest statystyką i nie zależy od Inteligencji — zmieniają ją przedmioty, drzewko, pasywki w slotach i pasywki broni. Pierwsza umiejętność pada zwykle w 3. akcji.
- **Statystyki:** Zręczność daje też mnożnik krytyka (przydaje się Wojownikowi), Inteligencja to moc umiejętności i odporność na magię. Punkt każdej statystyki pomaga każdej klasie.
- **Obrona (D-073, D-091, odpowiedź Karola na pytanie 46):** blok ma każda klasa (5%), tarcza dodaje Wojownikowi 28,3%; blok zmniejsza obrażenia (przechodzi 25% ciosu). Pancerz ma jawny limit redukcji 75%, a Wojownik ma najlepszy przelicznik.
- **Statusy (D-090):** trucizna w stosach, podpalenie liczone z życia celu, krwawienie z ciosu, spowolnienie (unik i zysk many, bez utraty tury), ogłuszenie (utrata tury), zdarcie Pancerza, wzmocnienie, tarcza z umiejętności −% obrażeń przez 3 tury. Obrażenia w czasie omijają obronę.
- **Sloty (D-088):** trzy sloty z dowolną mieszanką aktywnych i pasywnych, pasywki broni i premie z przedmiotów jako dane. **Wskrzeszenie (propozycja D-094):** legendarna pasywka w slocie, raz na walkę, powrót z 25% życia.
- **Potwory mają klasy** i przechodzą przez ten sam wzór co postać.
- **Wyniki:** pojedynki klas 46–55%; różnica klas przy tym samym potworze do 6,8 pp na ziarnach testu, ale **7,9 pp przy Strażniku na 1. poziomie na innych ziarnach** (granica 7 pp przekroczona — do decyzji). Wskrzeszenie z 25% życia daje 74–76% wygranych z taką samą postacią bez niego, a z dobrymi slotami do 90% — za mocne, do decyzji. Build pod manę używa umiejętności 1,2–1,7 raza częściej, nie 2 razy.
- **Tempo (korekta Karola do D-076):** krzywa doświadczenia 11,71 × L^1,6 daje Las w ok. 30 minut (Strażnik na 11. poziomie, ok. 8 przegranych po drodze) i wejście do ósmego biomu po ok. 10 godzinach na ok. 65. poziomie — model w `tools/walka/tempo.py`, propozycja.
- **Sprawdzone:** testy silnika 73/73, zgodność Pythona z kodem Luau bez Studio 592/592 dzienników (własny mały interpreter `tools/walka/luau_mini.py`), 60/60 złych wejść odrzuconych; niezależna kontrola znalazła i naprawiła cztery ważne błędy (za mocne pasywki many, pasywka trucizny podbijająca każde zaklęcie, słabe testy, ciche przyjmowanie nieznanych pól). Prawdziwy Luau w Roblox Studio i ekran walki — sprawdzone 17.11, punkt niżej.
- **W Studio (17.11.2026, 02:40–04:12):** silnik v3 jest w `Workspace/TestWalki2`, `Workspace/LasPotwory` i `Workspace/LasPasGra`. Zgodność prawdziwego Luau z Pythonem: 592 z 592 dzienników, 60 z 60 złych wejść odrzuconych. Ekran walki pokazuje paski many, znaczki statusów (trucizna do ×3), blok każdej klasy, wskrzeszenie i karteczki pasywek. Pomijanie walk (D-078): przy pierwszym spotkaniu z gatunkiem przycisku nie ma, od drugiej walki jest POMIŃ albo spacja, decyduje serwer; po pominięciu gracz i potwór są wolni od razu (przyjęte na noc, do zmiany). Testy w trybie Play: 44 z 46 i 25 z 27 w prototypie, las-pas 17 punktów w porządku, stary las 5 z 5. **Niesprawdzone:** prawdziwy telefon, pad, dwóch graczy, czas klatki i tempo ×4 przy odsłoniętym ekranie, przegrana i rewanż z pominięciem w lesie. Wyniki i wybory: `swiat/test_walki2/README.md`.

## Co jest zrobione i gdzie

| Co | Gdzie |
|---|---|
| Silnik w Luau (czyste ModuleScripty, nic się nie uruchamia samo) | `src/server/Walka/` → `ServerScriptService.Server.Walka`: `Silnik`, `Statystyki` (sprawdzanie wejścia i przeliczenie statystyk), `Umiejetnosci` (tura, umiejętności, efekty), `Przeciwnicy` (potwory lasu i łup), `Los` (generator), `Dane` (wygenerowane) |
| Format dziennika i jego niezmienniki dla klienta | `src/shared/Walka/Dziennik.luau` → `ReplicatedStorage.Shared.Walka.Dziennik` (`sprawdz(walka)`) |
| Jedno źródło danych (klasy, umiejętności, efekty, przeciwnicy, stałe) | `tools/walka/dane_walki.json` → generator `tools/walka/generuj_dane.py` robi z niego `Dane.luau` |
| Dosłowny port w Pythonie, testy, tabela balansu, wzorce zgodności | `tools/walka/` (instrukcja: `tools/walka/README.md`) |

Poza zakresem tej paczki: odtwarzacz cutscenki i interfejs, skrypt serwera wywołujący silnik, zapis łupu, drzewko jako system, modele 3D.

## Jak przebiega walka

- Strony działają **na zmianę**; kto zaczyna — rzut 50/50. Tura: (1) tykają efekty strony, (2) spowolniona strona traci turę, inaczej działa (umiejętność albo zwykły cios), (3) jej efekty tracą jedną turę trwania.
- Koniec: życie jednej strony = 0. Długość wynika tylko ze statystyk i losowości. Jedyny bezpiecznik to **techniczny limit 1000 tur** (rozstrzyga procent życia) — na 624 000 walk testowych nie zadziałał ani razu; najdłuższa miała 38 tur.
- **Czas** = wstęp 1,1 s + suma naturalnych czasów zdarzeń (cios 1,1 s, krytyk 1,6 s, unik 1,0 s, umiejętność 1,3–2,1 s, tyknięcie 0,6 s…) + finał 1,9 s. Test sprawdza, że **każde** zdarzenie trwa dokładnie swój czas z danych (także w walkach na ponad 60 tur), a ta sama akcja w 1. i 50. turze daje te same obrażenia — nic nie skraca zdarzeń ani nie podbija ciosów z czasem.
- Ten sam wzór dla gracza, postaci-przeciwnika (Arena, [[Arena (PvP)]]) i potwora; **ranga potwora** (zwykły, rzadki, strażnik) to tylko informacja dla interfejsu i łupu — test sprawdza, że strażnik „przebrany” za zwykłego daje identyczny dziennik.
- **Ziarno losowania** musi być liczbą całkowitą od 0 do 2^31 − 1; inne silnik odrzuca błędem („Walka: …”). Przy większych liczbach Luau i Python liczyłyby inny los, więc serwer, który składa ziarno np. z identyfikatora gracza i licznika, musi je sprowadzić do tego przedziału.

## Wzory (do strojenia)

Statystyka efektywna = punkty × (1 + pasywka z drzewka) × (1 + premia peta), zaokrąglone. Pet nie walczy, tylko mnoży (D-059). „Połowa” = 4 + 2 × poziom (ile punktów daje połowę drogi do limitu).

| Statystyka | Co daje |
|---|---|
| **Siła** | cios = mnożnik klasy × (obrażenia broni + 1 × Siła) — także zwykły atak Maga (magiczny) |
| **Kondycja** | życie = mnożnik klasy × (30 + 15 × poziom + 7 × Kondycja) |
| **Inteligencja** | moc umiejętności = 1 + 1,0 × Int / (Int + połowa) **oraz** odporność na magię = 0,75 × Int (punkty) |
| **Zręczność** | unik = baza klasy + (limit klasy − baza) × Zr / (Zr + połowa) |
| **Szczęście** | krytyk = 5% + 45% × Sz / (Sz + połowa) |
| **Pancerz** | punkty Pancerza + Pancerz z przedmiotów, **odejmowane** od ciosu fizycznego |

- **Obrona punktowa z dolną granicą:** obrażenia = max(25% surowego ciosu, cios − Pancerz) dla fizycznych, a dla magicznych to samo z odpornością na magię. Do tego zawsze co najmniej 1. Magia omija Pancerz.
- **Kolejność rzutu przy ataku:** unik → blok (tylko tarcza, przechodzi 25%) → krytyk (× mnożnik klasy) → zwykłe trafienie. Rozrzut 90–110%.
- **Umiejętności (propozycja mechanizmu):** każda w slocie ma odnowienie N własnych akcji. Na swojej turze postać odlicza sloty i używa **pierwszej gotowej w kolejności slotów zamiast zwykłego ciosu**; pierwszy raz w N-tej akcji. Siła = cios × mnożnik umiejętności × moc. Umiejętności na przeciwnika da się **uniknąć i zablokować** jak zwykły cios, a umiejętność „na siebie” działa zawsze.
- **Efekty** trwają N tur nosiciela: obrażenia w czasie (trucizna, podpalenie, krwawienie) tykają na początku jego tury i omijają obronę; spowolnienie zabiera najbliższą turę; zdarcie pancerza zabiera 50% Pancerza; tarcza pochłania obrażenia, aż się wyczerpie; wzmocnienie dodaje procent do obrażeń. Ten sam efekt się nie kumuluje, tylko odświeża.
- **Zaklęcia broni (D-051):** trucizna (30% szans przy trafieniu) i podpalenie (25%) nakładają obrażenia w czasie, widoczne w dzienniku jako osobne zdarzenia.

## Klasy

| Klasa | Styl | Zwykły cios | Unik (start → limit) | Krytyk | Mnożniki życia / ciosu | Cecha |
|---|---|---|---|---|---|---|
| **Wojownik** | wytrzymałość i blok | fizyczny | 0% → 24,2% | × 2,0 | 0,97 / 1,07 | jedyny nosi **tarczę** (blok to cecha przedmiotu; w tabeli tarcza 28,3%) |
| **Zwiadowca** | unik i krytyk | fizyczny | **25% → 50%** | **× 2,57** | 1,05 / 0,85 | najwyższy unik i najmocniejszy krytyk |
| **Mag** | magia i umiejętności | **magiczny** (omija Pancerz) | 0% → 41,9% | × 2,0 | 1,12 / 1,10 | bije magią; najsilniejsza moc umiejętności, bo stawia na Inteligencję |

Mnożniki i siła umiejętności to wynik strojenia pod równość klas (U10), a nie „charakter” klasy. Wzorcowe rozłożenie punktów (styl): Wojownik 26% Siła, 30% Kondycja, 12% Inteligencja, 8% Zręczność, 10% Szczęście, 14% Pancerz; Zwiadowca 27 / 27 / 10 / 14 / 13 / 9; Mag 24 / 22 / 24 / 10 / 10 / 10. Wszyscy mają tę samą pulę: 30 punktów na 1. poziomie i +10 za każdy kolejny (punkty rozdzielane metodą największych reszt, żeby zaokrąglenie nie zabierało klasie np. Kondycji na jednym poziomie).

## Umiejętności startowe

Kolejność w tabeli = kolejność slotów we wzorcowych postaciach. „Co N” = odnowienie w akcjach.

| Klasa | Umiejętność | Co N | Działanie |
|---|---|---:|---|
| Wojownik | **Potężne cięcie** | 3 | cios za ok. 200% (206%; przykład Pawła z sesji) |
| Wojownik | **Miażdżący cios** | 4 | 135% + zdarcie pancerza (−50% na 3 tury) + 14% szans na spowolnienie (przykład Karola) |
| Wojownik | **Kamienna skóra** | 5 | tarcza pochłaniająca na siebie (59% ciosu × moc, na 3 tury) |
| Zwiadowca | **Uderzenie z góry** | 3 | 165% i +27 pp szansy na krytyk (przykład Karola) |
| Zwiadowca | **Zatruta strzała** | 4 | 131% + trucizna (3 tyknięcia) |
| Zwiadowca | **Skupienie** | 5 | wzmocnienie +46% obrażeń na 3 tury |
| Mag | **Kula ognia** | 3 | 169% magiczne + podpalenie (2 tyknięcia) |
| Mag | **Lodowy pocisk** | 4 | 148% magiczne + 55% szans na spowolnienie |
| Mag | **Bariera** | 5 | tarcza pochłaniająca na siebie (42% ciosu × moc, na 3 tury) |

## Przeciwnicy lasu

Własne projekty (żadnych postaci z cudzych gier). Wartości na 5. poziomie; każdy rośnie z poziomem. Wszystkie bloki potworów = 0, bo blok to tarcza gracza.

| Przeciwnik | Ranga | Charakter (5. poziom) | Umiejętność | Wygląd (do modelu) |
|---|---|---|---|---|
| **Leśny Slime** | zwykły | 509 życia, słabe ciosy (57) | Kwaśny plusk: 92% magiczne, zdziera pancerz | Półprzezroczysty, mchowozielony sześcian galarety z liściem i małym grzybkiem zatopionymi w środku; podskakuje i zostawia lepkie ślady. |
| **Cierniowy Wilk** | zwykły | 282 życia, 23% uniku, krytyk × 2,1 | Rozszarpanie: 127% + krwawienie | Chudy, kanciasty wilk o futrze z ciemnej sierści przetykanej kolcami jeżyny, z bursztynowymi świecącymi oczami i ogonem jak zarośla. |
| **Muchomornik** | zwykły | 329 życia, bije laską (62) | Chmura zarodników: 74% magiczne + trucizna | Niski grzybowy ludek z czerwonym kapeluszem w białe kropki, bródką z mchu i krzywą laską z korzenia, z której sypią się świecące zarodniki. |
| **Leśny Troll** | rzadki, ciężki | 597 życia, gruby Pancerz (15) | Ogłuszające uderzenie: 166% + 60% szans na spowolnienie | Ogromny, przygarbiony troll o skórze jak kora, z poduchami mchu i grzybami na plecach; wlecze maczugę z wyrwanego pnia z korzeniami. |
| **Strażnik Gaju** | strażnik biomu | 772 życia, Pancerz 15 | Uścisk korzeni: 140% magiczne + spowolnienie (jedyna, własna) | Wysoki kolos z kamienia i splecionego drewna, z koroną z gałęzi, korzeniami zamiast stóp i świecącym zielonym kryształem w piersi. |

Pancerz i odporność na magię każdego potwora są strojone osobno (odporność to ok. 0,1–0,6 Pancerza), żeby Mag (magia omija Pancerz) nie był ani silniejszy, ani słabszy od klas fizycznych przy żadnym potworze. Trudność: średnia postać tego samego poziomu wygrywa ok. 80–87% walk ze zwykłymi, ok. 50–57% z trollem i ok. 30–39% ze strażnikiem; na poziomach 1–4 (jeden slot) rozrzut jest większy: 65–91%, 37–66% i 18–46%.

Łup za wygraną: Złoto i doświadczenie (skalowane poziomem, z rozrzutem), tokeny krainy (D-058), rzadko 1 Gem (1–15%), **Shard Ewolucji tylko ze strażnika** i z szansą 10% (D-058). Za przegraną tylko 20% doświadczenia. **Jajek w łupie nie ma** — nie ma nawet takiego pola (D-060). Arena: nagrody poza silnikiem.

## Tabela balansu

**Wniosek: klasy są równe w pojedynkach i prawie równe z potworami — na 13 poziomach (1–10, 12, 15, 20) różnica klas przy tym samym potworze mieści się w 7 pp wszędzie poza Leśnym Slimem na poziomach 1 i 4 (7,4–7,5 pp; na ziarnach kontrolnych do 8,6 pp, a Strażnik na 3. poziomie 7,6 pp), a cel ≤ 5 pp spełnia 53 z 65 zestawień.**

Pełna tabela: `python -B tools/walka/balans.py` (2000 walk na każdą parę, te same ziarna dla każdej klasy; wymiana = tura jednej strony). Kontrola na innych ziarnach: `--start 50001`. Sloty we wzorcowych postaciach: 1 (poziomy 1–4), 2 (5–9), 3 (od 10).

Największa różnica procentu wygranych między klasami (pp) — ziarna testu 1–2000 / ziarna kontrolne 50001–52000:

| Przeciwnik | Poziomy 1–4 (1 slot) | Poziomy 5–9 (2 sloty) | Poziomy 10–20 (3 sloty) |
|---|---:|---:|---:|
| Leśny Slime | **7,5 / 8,6** | 4,7 / 4,5 | 5,4 / 5,5 |
| Cierniowy Wilk | 6,2 / 6,4 | 4,7 / 3,3 | 6,9 / 6,7 |
| Muchomornik | 4,3 / 3,5 | 2,4 / 1,8 | 3,6 / 5,3 |
| Leśny Troll (rzadki) | 4,5 / 6,9 | 5,1 / 2,6 | 2,5 / 4,6 |
| Strażnik Gaju | 4,9 / 7,6 | 2,7 / 5,1 | 2,9 / 4,9 |

Procent wygranych Wojownik / Zwiadowca / Mag z potworem tego samego poziomu (ziarna testu):

| Przeciwnik | Poziom 1 | Poziom 4 | Poziom 5 | Poziom 10 | Tury na 5. poziomie: najkrótsza–mediana–najdłuższa | Średni czas (5. poziom) |
|---|---|---|---|---|---|---:|
| Leśny Slime | 91 / 84 / 88 | 72 / 68 / 65 | 82 / 80 / 82 | 83 / 78 / 83 | 7–11–22 | 20 s |
| Cierniowy Wilk | 89 / 83 / 82 | 81 / 76 / 77 | 86 / 83 / 83 | 87 / 80 / 81 | 5–8–23 | 16 s |
| Muchomornik | 83 / 80 / 81 | 76 / 75 / 73 | 86 / 84 / 85 | 85 / 81 / 84 | 3–8–18 | 15 s |
| Leśny Troll (rzadki) | 66 / 63 / 64 | 41 / 38 / 37 | 57 / 55 / 57 | 56 / 56 / 57 | 5–13–27 | 23 s |
| Strażnik Gaju | 46 / 42 / 45 | 22 / 21 / 18 | 36 / 36 / 39 | 38 / 37 / 36 | 5–16–32 | 29 s |

**Klasa na klasę** (ziarna testu, wszystkie 13 poziomów): Wojownik–Zwiadowca 49,3–52,9%, Wojownik–Mag 45,5–51,2%, Zwiadowca–Mag 48,9–54,5%. Żadna klasa nie kontruje innej. Na ziarnach kontrolnych wszystko w 45–55% poza Wojownik–Mag na **2. poziomie: 43,7–44,6%** (Mag lekko silniejszy tylko na tym jednym poziomie).

**Długość walki wynika ze statystyk i losu:** ze zwykłym potworem od 3 do 26 tur (7,3–40,2 s), ze strażnikiem od 5 do 38 tur (10,0–53,0 s). Najdłuższe walki ze zwykłymi potworami są dłuższe niż typowa walka ze strażnikiem, a najkrótsza walka ze strażnikiem krótsza niż typowa walka ze zwykłym. Przy równym poziomie strażnik nie pada w 1–2 tury (ma kilkanaście razy więcej życia niż jeden cios), ale żadna reguła tego nie blokuje: postać wyraźnie silniejsza (np. 10. poziom z dużą Siłą na strażnika 2. poziomu) kładzie go jednym ciosem, a pierwszy cios walki może zabić.

**Każda statystyka coś daje** (+14 punktów na 5. poziomie, średnio z potworami i klasami): Kondycja +20–25 pp, Siła +15–18, Pancerz +13–16, Inteligencja +7–10, Szczęście +6–7, Zręczność +6–10 pp. Nic nie jest bezużyteczne, ale punkt Zręczności i Szczęścia jest dziś wart 2–3 razy mniej niż punkt Siły czy Kondycji — patrz wybór 5.

**Wojownik z tarczą i wysoką Zręcznością (pytanie 40) nie jest za mocny:** przesunięcie 15% puli z Siły i Kondycji do Zręczności daje mu unik 12,9% (limit klasy 24,2%) i obniża wygrane z potworami z 70% do 51%, a z klasami z 50% do 36%. Tarcza plus unik się nie „sumują w przewagę”, bo limit uniku Wojownika jest niski, a Zręczność jest dziś tańsza w działaniu niż Siła i Kondycja.

**Dlaczego Slime na poziomach 1–4 odstaje:** przy jednym slocie Wojownik (blok tarczą wobec wielu słabych ciosów) znosi tę długą walkę najlepiej, a Mag na 3.–4. poziomie najgorzej. Te same liczby Slime’a obowiązują przy 2 i 3 slotach, gdzie różnica jest już mała, więc strojenie samego Slime’a nie usunęło jej do końca. Test pilnuje tu 8 pp zamiast 7 (jawny wyjątek w `tools/walka/test_walki.py`); zniknie albo zmaleje, gdy zapadnie decyzja o slotach na starcie (wybór 5 i „Co niesprawdzone”).

## Walka na ekranie — prototyp w Studio (15.11.2026)
Dziennik z silnika odtwarza prototyp `Workspace/TestWalki2` (źródła i instrukcja: `swiat/test_walki2/README.md`; tylko w Roblox Studio, obok starego prototypu `Workspace/TestWalki`). Przy tablicy gracz wybiera klasę, przeciwnika i poziom; serwer liczy walkę, klient odtwarza **cały** dziennik zdarzenie po zdarzeniu (D-068): ciosy, krytyki, bloki, uniki, umiejętności z lecącymi pociskami, efekty na postaci z licznikiem tur, łup. Tempo ×1/×2/×4 i „pomiń” to wybór gracza. Aktorzy to nasze modele z części Roblox z własnymi klipami granymi z danych — bez wgrywania czegokolwiek. Sprawdzone: ekran zgadza się ze stanem silnika zdarzenie po zdarzeniu (5 walk, 93 zdarzenia), kopia silnika w Studio zgodna z symulacją (45/45). Nie sprawdzono: prawdziwego telefonu, dźwięku, odbioru przez człowieka w normalnym tempie. Raport: „Walka v2 na ekranie — prototyp w Studio” w panelu.

### Prawdziwe ruchy bohaterów w prototypie (15.11.2026)
- **Co się zmieniło:** Wojownik (model Rycerza) i Mag (model Kota-Maga) grają w walce własne klipy walki z modułów postaci, przyjęte wcześniej przez właściciela, zamiast szkiców prototypu. Szkice tych dwóch postaci są usunięte; szkic został tylko u Zwiadowcy (klip „skupienie”).
- **Tarcza z modelu (D-071):** Wojownik walczy w stroju „bojowy” z tarczą modułu w lewej dłoni — jedna tarcza, dawna tarcza prototypu usunięta. Silnik daje bloki tylko dlatego, że postać wzorcowa Wojownika nosi tarczę; bez tarczy aktor ma być w stroju „pełny”, a silnik nie może dawać bloków. Przy bloku iskry pojawiają się przy tarczy w chwili ciosu.
- **Mag:** kapelusz i kostur siedzą na kościach modelu; po porażce spadają jak w module. Pociski (kula ognia, lodowy pocisk, zwykły atak) wylatują z kryształu kostura.
- **Poprawki odtwarzacza:** Miażdżący cios — Wojownik na czas doskoku obraca się o ok. 21° w lewo, żeby klinga z jego klipu spadła na cel (bez obrotu mijała wąskiego wilka). Unik — klip uniku sam odskakuje w bok, odtwarzacz dodaje tylko krok 0,9 studa w tył.
- **Testy (na końcowym kodzie):** offline 9/9 (2700 walk) i 15/15 testów aktorów; w Studio kopia silnika zgodna z Pythonem 45/45, klipy 24/24, walka 112/112, poprawki 29/29, dopieszczenie 38/38, telefon: żaden napis poniżej 12 pt. Filmy: `swiat/test_walki2/klatki/film_wojownik_cierniowy_wilk_5.mp4`, `film_mag_lesny_slime_5.mp4`.
- **Słabe strony:** przy krytyku błysk trafienia pojawia się chwilę po tym, jak klinga minie głowę niskiego celu (klip kończy cios przy ziemi); w ujęciu Miażdżącego ciosu zza pleców Wojownik zasłania połowę kadru, a przy zamachu głowa wychodzi poza kadr; unik Wojownika przed Trollem — maczuga przez 1–2 klatki przechodzi przez jego przód; Bariera unosi Maga o 0,19 studa (ruch klipu). Ocena człowieka w normalnym tempie jeszcze nie zapadła.

## Wybory do decyzji

Zrobione tak, jak w pierwszej opcji — każdą da się zmienić w danych albo w kilku liniach kodu.

1. **Czym bije zwykły atak Maga.** (a) Siłą, jak u wszystkich — magia to tylko rodzaj obrażeń (zrobione; każda statystyka coś daje każdej klasie); (b) Inteligencją, jak w klasycznych RPG — ale wtedy Siła jest dla Maga bezużyteczna, a Inteligencja liczy się podwójnie.
2. **Jak działają umiejętności w walce automatycznej.** (a) odnowienie co N akcji, pierwsza gotowa w kolejności slotów zamiast zwykłego ciosu (zrobione); (b) losowa szansa na użycie w każdej turze; (c) jedna umiejętność na walkę (zdanie Pawła z sesji).
3. **Unik i blok wobec umiejętności i obrażeń w czasie.** (a) umiejętność na przeciwnika da się uniknąć i zablokować, a trucizna i podpalenie omijają obronę (zrobione — bez tego Zwiadowca i Wojownik tracili swoją obronę wobec potworów z umiejętnościami); (b) umiejętność zawsze trafia.
4. **Dolna granica obrony.** (a) zawsze przechodzi 25% surowego ciosu i co najmniej 1 (zrobione); (b) 10% albo 50%; (c) stała liczba zamiast procentu.
5. **Ile slotów na starcie i ile wart jest punkt statystyki.** Każdy nowy slot to skok siły o ok. 10–15 pp wygranych, a przy jednym slocie klasy różnią się najbardziej (Slime wyżej). (a) zostawić 1 slot od 1. poziomu, 2 od 5., 3 od 10. (tak liczy tabela); (b) dawać sloty częściej albo od razu wszystkie trzy, a różnicować tylko siłą umiejętności z drzewka — mniejsze skoki i łatwiejszy balans. Osobno: punkt Siły i Kondycji daje dziś 2–3 razy więcej niż punkt Zręczności i Szczęścia — zostawić (limity uniku i krytyka) albo wyrównać krzywe.

## Co niesprawdzone

- **Kod Luau sprawdzony w Studio 14.11.2026 (ok. 21:10):** `python -B tools/walka/zgodnosc_studio.py --studio <id>` (tryb Edit, tylko odczyt) dał powtarzalność OK, niezmienniki OK na 496 walkach, **496/496 dzienników identycznych z Pythonem** i 38/38 złych wejść odrzuconych czytelnym błędem „Walka: …” (w tym ziarno 1e20, ułamkowe i ujemne oraz umiejętności podane jako tabela zamiast listy). Po każdej zmianie silnika albo danych trzeba to powtórzyć. Nie sprawdzono jeszcze silnika wołanego przez prawdziwy skrypt serwera w trybie Play — takiego skryptu jeszcze nie ma.
- Balans liczony na **wzorcowych** postaciach (`tools/walka/wzorcowe.py`): równa pula punktów, ta sama broń i pancerz z przedmiotów, sloty 1/2/3 na poziomach 1/5/10. Prawdziwi gracze rozłożą punkty inaczej; drzewko, pety i zaklęcia nie były w tabeli. Liczby w danych dobrał automat strojący (stąd np. 0,2707) — można je zaokrąglić, ale wtedy trzeba przeliczyć tabelę.
- **Bez umiejętności postać jest dziś dużo słabsza**, bo potwory skalibrowano pod sloty z założenia. Jeśli na starcie gracz ma 0 slotów (D-055), potwory pierwszych poziomów trzeba osłabić.
- Odbioru przez człowieka (czy walka 15–30 s przy każdym potworze nie męczy) nikt nie sprawdzał — to sprawa odtwarzacza i przycisków „×2” / „pomiń”.

## Powiązane
[[System RPG]] · [[Drzewko umiejętności postaci]] · [[Pety]] · [[Arena (PvP)]] · [[Rejestr decyzji]] · [[Pytania otwarte]] · [[Sesja główna 2026-11-14 — zapis ustaleń]] · [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] · [[Sesja główna 2026-11-14 (3) — zapis ustaleń]]
