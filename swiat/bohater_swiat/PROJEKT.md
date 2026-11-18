# Bohater w świecie — projekt

> **Status: propozycja (prototyp w Studio), nie kanon i nie kod gry.** Zlecenie Karola z 18.11.2026: „Popraw modele —
> żeby w grze można było się już nimi ruszać”. Wszystkie liczby są „przyjęte, do zmiany” (`ustawienia.json`).
> Stan wdrożenia i wyniki prób: `README.md`.

## 1. Co ma się stać

Dziś gracz chodzi po świecie awatarem Roblox, a bohatera swojej klasy (Rycerz, Zwiadowca, Kot-Mag — modele z klocków
z własnymi klipami i strojem D-071) widzi tylko w walce. Po tej zmianie od wyboru klasy gracz **chodzi bohaterem**:
po bazarze, pasie lasu, Bagnie, Dżungli i starym miasteczku, w tym, co ma założone, z ruchem (spoczynek, chód, skok,
spadanie, lądowanie), i tak samo widzą go inni gracze.

## 2. Wybory i powody

### 2.1. Postać Roblox zostaje, bohater jest „skórą”

Postać z `Humanoid` zostaje w całości: fizyka, sterowanie, kamera, dotyk na telefonie, podpowiedzi E i wszystko, co
czytają inne pakiety (`HumanoidRootPart`, `WalkSpeed`, `CharacterAdded`, teleporty, pety, walki). Bohater to osobny
model, który co klatkę staje pod postacią. Powód: zamiana postaci na własny rig oznaczałaby przepisanie ruchu,
kamery i każdego pakietu, który przestawia postać — a tu nie zmienia się nic poza tym, co widać.

- **Bez połączenia z postacią.** Korzeń bohatera jest zakotwiczony, a jego części nie mają kolizji, dotyku, zapytań
  ani masy. Nie ma żadnego spawu między bohaterem a postacią, więc masa i ruch postaci są takie same jak bez niego
  (próba B03 porównuje masę, `HipHeight`, `WalkSpeed` i skok). Odrzucone: przyspawanie rigu do `HumanoidRootPart` —
  mniej kodu, ale części bohatera weszłyby do bryły fizycznej postaci.
- **Awatar chowany przez `Transparency = 1` u klienta**, z zapamiętaniem dawnych wartości (wracają po wyłączeniu).
  Odrzucone: `LocalTransparencyModifier` — tę właściwość awatara piszą już walka (chowa wszystkie postacie), mini-gra
  i kamera Robloxa przy zbliżeniu, a próby walki sprawdzają ją po odrodzeniu („własna postać widoczna”, wartość 0).
  Dzięki temu te pakiety i ich próby działają bez zmian.
- **Bohater znika razem z awatarem.** Co klatkę przejmuje `LocalTransparencyModifier` głowy awatara. Skutki bez
  jednej linijki w cudzym kodzie: w walce bohater świata jest schowany (walka chowa postacie graczy), po walce wraca;
  w widoku z pierwszej osoby znika (kamera chowa awatara), więc nie zasłania ekranu.

### 2.2. Model i strój: to samo co w walce

Model składa moduł przymierzalni `Workspace/StrojeProba/Moduly/Ubieranie` — ten sam, który ubiera bohatera w walce —
z atrybutu gracza `StrojProba_<klasa>` (pisze go serwer przymierzalni; kowal zakłada nowe przedmioty tą samą drogą).
Brak atrybutu = strój odniesienia, czyli dokładnie wygląd z walki. Bohater w świecie i w walce nosi więc to samo.

Szkielet powstaje z danych przymierzalni (`Ubieranie.zbuduj(klasa, plan, nil)`), nie z klona szablonu walki. Powód:
miejsce ma streaming, a szablony aktorów stoją przy arenie walki — z bazaru albo lasu zwykle nie są wczytane.
Dane szkieletu to moduł (jest u klienta zawsze), a generator przymierzalni pilnuje, że kości i strój odniesienia są
co do bryły takie jak w szablonie walki.

### 2.3. Ruch: własne klipy + pozy proceduralne

- **Spoczynek i chód** to klipy bohatera z danych walki (`TestWalki2/Moduly/DaneAktorow/<klasa>`), grane odtwarzaczem
  `TestWalki2/Moduly/Klipy` w trybie ręcznym (krok liczy pętla tego pakietu). Żadnych zasobów Animation, żadnego
  uploadu.
- **Tempo chodu** = prędkość pozioma postaci ÷ prędkość naturalna klipu (2 × zakres ruchu stopy ÷ okres), w granicach
  `tempo_min`–`tempo_max`. Prędkości naturalne: Rycerz 3,06 st/s, Zwiadowca 7,11, Kot-Mag 1,16. Klipy chodu
  Rycerza i kota to marsz w miejscu z walki: powyżej tempa 1,8 klip przestaje nadążać i stopy ślizgałyby się po ziemi.
- **Nowy cykl biegu (18.11.2026, w plikach, jeszcze nie w Studio)** zastępuje opis nóg, kadencji i reszty ciała
  z punktu niżej; progi biegu, korzeń o klatkę później i umowa zostają.
  - *Tempo:* czas podporu = krok ÷ prędkość; czas lotu jednego kroku = (1 ÷ (2 × `kadencja_pelna`) − krok ÷ 16) ×
    prędkość ÷ 16, najmniej 30% tej wartości. Podpór jest zawsze krótszy niż pół cyklu. Przy 16 st/s: Rycerz 2,20
    cyklu/s (podpór 17%, lot 0,150 s), Zwiadowca 2,50 (17%, 0,132 s), kot 3,40 (13%, 0,108 s).
  - *Faza:* w podporze przesuwa się o podpór × droga ÷ krok — stopa cofa się względem bioder dokładnie o drogę
    postaci przy każdej prędkości; w locie idzie zegarem. Gdy udział podporu się zmienia (inna prędkość), faza jest
    przeliczana tak, żeby stopa została w tym samym ułamku podporu. Prędkość = droga ÷ czas klatki, wygładzona
    (0,1 s), i nie większa niż prędkość z fizyki: na przeszkodzie spada do zera i bieg ustaje.
  - *Nogi:* krok Rycerza 0,8, Zwiadowcy 0,7, kota 1,1 długości nogi; biodra w skrajach podporu na wysokości, przy
    której noga ma 0,99 długości (krótszy krok = prostsze kolano: w połowie podporu 59° / 51° zamiast 79°),
    w podporze uginają się, w locie wznoszą (1,6 × ugięcie × lot ÷ podpór). Wymach: pięta wcześnie w górę, wybieg
    w tył po odbiciu, cofnięcie stopy przed postawieniem; stopa w podporze płasko (miara B19 bez zmian).
  - *Dodatki* (`bieg.dodatki`): kąt kości = stałe + skala × wymach × cos(2π × (harmoniczna × faza − przesunięcie)),
    dokładane do pozy z klipu — ręce, tułów (pochył, skręt, kołysanie), głowa (wyrównanie), u kota ogon, kapelusz,
    uszy i kostur. Pochył tułowia w biegu jest teraz dodatkiem; poza `pochyl` została dla chodu (przy 16 st/s
    zastępowała całą pozę tułowia i kasowała jego skręt).
  - *Poły:* bryły przyspawane do kości bioder, których spód jest poniżej stawu biodra — klient rozpoznaje je przy
    budowie po geometrii (każdy strój), rusza spawem (`Weld.C0`), w spoczynku przywraca. Pasy z przodu / z tyłu:
    0,9 × kąt uda, które je wypycha. Dzwon (bryła obejmuje przód i tył): uniesienie przodu wokół tylnego dolnego
    skraju 7° ± 3° dwa razy na cykl, skręt ±6°, niższe bryły mocniej i z opóźnieniem, plus podniesienie o zejście bioder.
  - *Zakręt:* prędkość obrotu postaci → przechył tułowia do 7° i obrót do 5° (pełne przy 5 rad/s, wygładzone 0,15 s).
- **Bieg — cykl proceduralny, wersja pierwsza (stoi w Studio)** (bez klipu, bez zmian w modułach postaci i danych walki). Gra, gdy prędkość pozioma
  przekroczy `tempo_max` × chód naturalny × 1,12 (Rycerz 6,2 st/s, Zwiadowca 14,3, kot 2,3), wraca do chodu poniżej
  `tempo_max` × chód naturalny; przejście chód ↔ bieg trwa 0,2 s (waga cyklu rośnie płynnie, klip chodu gaśnie do
  spoczynku). Przy zwykłej prędkości postaci (16 st/s) wszyscy trzej biegną.
  - *Nogi:* kostka każdej nogi idzie po torze względem bioder — w podporze stoi na ziemi i cofa się ze stałą
    prędkością od +krok/2 do −krok/2, w wymachu wraca łukiem do przodu (uniesienie 0,32 długości nogi). Kąty uda,
    łydki i stopy liczy z tego toru odwrotna kinematyka dwóch kości (kolano do przodu), więc stopa jest dokładnie tam,
    gdzie tor.
  - *Krok z długości nóg:* krok = 1,0 × (udo + łydka) — Rycerz i Zwiadowca 1,55 st, kot 0,57 st; biodra w podporze
    na wysokości 0,82 długości nogi nad kostką (lekko ugięte kolana).
  - *Kadencja* = prędkość × podpór ÷ krok (podpór docelowo 32% cyklu), najwyżej 2,5 cyklu/s × √(1,55 ÷ długość nogi):
    Rycerz i Zwiadowca 2,5, kot 4,12. Powyżej tej granicy skraca się podpór (dłuższy lot): przy 16 st/s Rycerz
    i Zwiadowca stoją na stopie 24% cyklu, kot 15%.
  - *Stopa w podporze stoi w miejscu:* stopa cofa się względem bioder z prędkością krok × kadencja ÷ podpór, a to
    jest dokładnie prędkość postaci. Cykl przesuwa się **drogą postaci, nie zegarem** (czas klatki = droga ÷
    prędkość), więc nierówne klatki nie rozjeżdżają stopy z ziemią; bieg w miejscu (klip umowy) idzie zegarem.
    Silnik stosuje pozę stawów (`Motor6D.Transform`) dopiero po kroku fizyki, czyli klatkę później niż położenie
    ustawione wprost — dlatego korzeń bohatera też staje w miejscu z poprzedniej klatki (`ruch.korzen_klatke_pozniej`);
    bohater jest o jedną klatkę za niewidocznym awatarem. Bez tego stopa „pływała” do 0,27 st na podpór.
    Tolerancja zmierzona: bez Studio (kinematyka w przód na rigu, 60 kl./s) przesunięcie poniżej 0,005 st; w grze
    (próba B19, prawdziwy bieg 16 st/s, klatka po klatce) 0,000 st u wszystkich trzech klas.
  - *Stopa w wymachu* pochyla się czubkiem w dół o 22°; u kota (długa stopa na krótkiej nodze) generator zmniejsza
    kąt do 8°, żeby czubek nie wchodził w ziemię.
  - *Reszta ciała:* biodra podskakują dwa razy na cykl (±0,05 długości nogi, najniżej w połowie podporu), ręce
    wymachują przeciwnie do nóg jako dodatek do pozy ze spoczynku (broń i tarcza zostają w dłoniach; kąty na klasę
    w `ustawienia.json`), tułów pochyla się do przodu (poza `pochyl`, waga rośnie z prędkością 6→16 st/s) i lekko
    skręca.
  - Klip umowy `"bieg"` (mini-gry) to ten sam cykl w miejscu, przy 16 st/s.
- **Skok, spadanie, lądowanie** nie mają klipów: to pozy proceduralne nakładane na stawy po klipie
  (`Transform = klip:Lerp(poza, waga)`, waga dochodzi liniowo w czasie z danych). Lot zaczyna się od razu przy stanie
  `Jumping` albo po 0,1 s w powietrzu (zejście ze schodka nie jest skokiem), po locie 0,18 s lądowania. Kto już
  spada, wraca do pozy skoku dopiero przy wznoszeniu szybszym niż 12 st/s (odbicie przy lądowaniu to nie skok).
- **Stopy na ziemi.** Punkt pod postacią = środek `HumanoidRootPart` − (`HipHeight` + pół jego wysokości; w R6 także
  wysokość nóg). Rig staje tam swoim początkiem (ziemia rigu), z poprawką o spód własnych nóg zmierzony po budowie
  i o „podniesienie chodu” (klip chodu kota schodzi stopami 0,22 st pod ziemię, Rycerza 0,06 — o tyle rig unosi się,
  gdy gra chód). W pozach z przysiadem (lądowanie, padnij) generator dolicza opuszczenie bioder kinematyką w przód,
  tak żeby najniższa bryła nóg stała na ziemi.
- **Śmierć:** klip `upadek` w miejscu, gdzie postać padła; po odrodzeniu bohater powstaje przy nowej postaci.

### 2.4. Inni gracze

Każdy klient buduje bohaterów wszystkich graczy sam, z atrybutów gracza, które już się replikują (`Class`,
`StrojProba_<klasa>`) — tak jak walki i pety, bez nowych zdarzeń sieciowych. Granice: najwyżej
`maks_bohaterow` (12) najbliższych kamerze w promieniu `promien` (260 st, z histerezą 1,15); dalej widać awatara jak
dawniej. Bohaterom dalej niż 90 st animacja liczy się co 3. klatkę (miejsce — co klatkę). Budowa: jeden bohater na
klatkę. U cudzej postaci stan podłoża nie jest pewny, więc lot poznajemy po stanie albo po prędkości pionowej > 8 st/s.

Klipy wymuszone umową (mini-gra) widzi tylko gracz, który gra — tak samo jak dzisiejsze ruchy awatara w mini-grze.

### 2.5. Wyłącznik i brak zależności

- Atrybut kontenera `BohaterWSwiecie` (domyślnie `true`). `false` → bohaterowie znikają, awatary wracają — od razu,
  bez przebudowy (klient czyta atrybut co klatkę). Ustawiony w Edit przechodzi na odbudowany kontener.
- Bez `Workspace/TestWalki2` albo `Workspace/StrojeProba` bohatera nie ma, awatar zostaje, konsola jest czysta
  (klient sprawdza zależności co 2 s). Błąd budowy jednego bohatera = jedno ostrzeżenie i ponowienie po 5 s.
- Poza Studio serwer usuwa kontener, klient nic nie robi (jak inne próby).

## 3. Liczby

| Klasa | Bryły: goły / w stroju odniesienia | Instancji (ok.) | Chód naturalny | Podniesienie chodu | Przysiad: lądowanie / padnij |
|---|---|---|---|---|---|
| Wojownik (Rycerz) | 74 / 127 | 199 / 306 | 3,06 st/s | 0,064 st | 0,21 / 0,89 st |
| Zwiadowca | 109 / 182 | 269 / 416 | 7,11 st/s | 0 | 0,21 / 0,93 st |
| Mag (Kot-Mag) | 107 / 166 | 278 / 406 | 1,16 st/s | 0,221 st | 0,08 / 0,35 st |

| Klasa | Noga (udo + łydka) | Krok biegu | Bieg od / chód poniżej | Przy 16 st/s: kadencja, podpór, droga na cykl |
|---|---|---|---|---|
| Wojownik (Rycerz) | 1,55 st | 1,24 st (było 1,55) | 6,2 / 5,5 st/s | 2,20 cyklu/s, 17% cyklu, 7,3 st (było 2,5, 24%, 6,4 st) |
| Zwiadowca | 1,55 st | 1,08 st (było 1,55) | 14,3 / 12,8 st/s | 2,50 cyklu/s, 17% cyklu, 6,4 st (było 2,5, 24%, 6,4 st) |
| Mag (Kot-Mag) | 0,57 st | 0,63 st (było 0,57) | 2,3 / 2,1 st/s | 3,40 cyklu/s, 13% cyklu, 4,7 st (było 4,12, 15%, 3,9 st) |

Limit kontrolny w testach: 220 brył na bohatera w najcięższym stroju. Przy 12 bohaterach to do ok. 2,2 tys. brył
bez kolizji u jednego klienta. Zmierzone w Studio na komputerze (próba B17): pętla pakietu 0,05 ms na klatkę
z jednym bohaterem i 0,41 ms z dwunastoma (1861 brył), 60 kl./s bez bohatera, z jednym i z dwunastoma.

## 4. Umowa z mini-grami

`Workspace/BohaterSwiat/Sygnaly/RuchBohatera` — opis i przykłady w `README.md`. Stan umowy trzyma klient; czysta
logika (`LogikaBohatera.polecenieRuchu`) ma lustro w Pythonie i test, który wykonuje plik Luau interpreterem.
Po odrodzeniu postaci i po wyłączeniu bohatera wymuszony klip i przesunięcie są zerowane.

## 5. Sprawy do decyzji ludzi

1. **Bieg jest proceduralny** (pkt 2.3): stopy nie ślizgają się, ale to ruch policzony wzorem, bez ręki animatora.
   Do oceny w grze: kadencja (kot stawia teraz 6,8 kroku na sekundę zamiast 8), długość kroku, wymach rąk z bronią,
   ruch pół stroju i szaty kota (nowe, policzone bez Studio — podglądy w `podglady/`). Liczby są
   w `ustawienia.json` → `bieg`. Inne wyjście na później: ręczny klip biegu w modułach postaci.
2. **Skok bez własnego klipu** — poza proceduralna. Czy ma powstać klip skoku?
3. **Telefon.** 127–182 brył na bohatera; ilu bohaterów naraz i z jakiej odległości (dziś 12 i 260 st).
4. **Widok z pierwszej osoby:** bohater znika (jak awatar). Czy blokować zbliżenie kamery do pierwszej osoby?
5. **Daleko poza zasięgiem** widać awatara Roblox zamiast bohatera. Inne wyjście: nie pokazywać nikogo.
6. **Rozmiar postaci.** Bryła kolizji i wysokość kamery zostają z awatara gracza; kot jest niższy, miecz i tarcza
   Rycerza wystają poza bryłę kolizji i przechodzą przez ściany.
7. **Pozy mini-gier u innych graczy** — dziś lokalne. Replikacja wymagałaby zdarzenia sieciowego z kontrolą serwera.
8. **Awatar gracza** (ubrania, akcesoria Roblox) nie jest już widoczny w świecie po wyborze klasy — to zmiana
   projektowa, do potwierdzenia przez Karola i Pawła.
