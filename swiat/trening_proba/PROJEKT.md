# Training Center — sześć mini-gier 3D

> **To jest PROPOZYCJA do akceptacji** (17.11.2026). Ustalone są tylko punkty z zatwierdzonych decyzji wypisanych
> niżej. Pomysły na mini-gry, nazwy, liczby i układ sceny to propozycja agenta Karola. Dwie mini-gry (Siła
> i Pancerz) są zrobione do próby w grze (`README.md`), cztery pozostałe istnieją tylko w tym opisie.

## Co już ustalono (decyzje ✅ w `B&C/Produkcja/Rejestr decyzji.md`)

- **D-050 ✅** (Karol i Paweł, 14.11): statystyki rosną w mini-grach 3D w Training Center. Trafienie daje +1,
  a seria trafień daje combo i większy przyrost. Grindu nie ograniczamy. Bez trybu AFK — na razie.
- **D-063 ✅** (16.11): jeden budynek. Okno wyboru przenosi gracza do mini-gry. Mini-gry mają być 3D, interaktywne,
  niezbyt trudne i logicznie związane ze statystyką. Przykład Pawła dla Siły: postać rzuca przedmiotami, a gracz
  rozbija je mieczem, klikając strzałkę w stronę przedmiotu. Training Center jest dostępne od pierwszego poziomu.
- **D-074 ✅** (16.11): Pancerz też ma mini-grę, na próbę, do oceny w grze. Przyrosty mają być takie, żeby nie
  opłacało się nadużywać jednej mini-gry.
- **D-085 ✅** (16.11): mini-gry wybiera się z jednego panelu w jednym miejscu (w miasteczku).
- **D-093 ✅** (16.11): okna 2D i ich skrypty robi Paweł, a 3D Karol. Dlatego wybór mini-gry w tej próbie jest
  **tymczasowy** i tak jest opisany na ekranie.
- **D-062 ✅** (16.11), model statystyk: Siła to obrażenia ciosów, Kondycja to życie, Inteligencja to moc umiejętności
  i odporność na magię, Zręczność to unik, Szczęście to krytyk, a Pancerz to punkty odejmowane od ciosu.
  Na tym opiera się „dlaczego pasuje” przy każdej mini-grze.

## Wspólne zasady (propozycja; liczby „przyjęte, do zmiany” na końcu)

- **Runda** trwa 45 s, a przed nią jest odliczanie 3, 2, 1. Zdarzenia (skrzynki, ciosy, kłody…) układa serwer
  z ziarna losowania. Trudność rośnie w czasie rundy w czterech poziomach: od 0, 12, 24 i 34 s.
- **Trafienie** to właściwa akcja w oknie czasu wokół chwili zdarzenia. **Pudło** to zła akcja, akcja za wcześnie
  albo za późno, przepuszczone zdarzenie albo naciśnięcie, gdy nic nie leci (wtedy seria spada, ale żadne zdarzenie
  się nie rozstrzyga). **Seria** to trafienia z rzędu; od 5, 10 i 20 trafień każde kolejne daje więcej.
  Drugie kliknięcie tuż po trafieniu (do 0,25 s) jest pomijane bez kary.
- **Przyrost.** Domyślnie w próbie działa wzór z `tools/walka/BALANS_1711.md` (część 6; to propozycja innej pracy,
  nie decyzja). Trafienie napełnia pasek statystyki: 4 jednostki, w serii 5 / 6 / 8 (×1,25 / ×1,5 / ×2). Pełny pasek
  daje +1 punkt statystyki. Próg paska to 40 × (1 + W / (0,1 × pula))², gdzie W to punkty już wytrenowane w tej
  statystyce, a pula = 30 + 10 × (poziom − 1). Każda kolejna godzina w tej samej mini-grze daje więc mniej, a świeża
  statystyka znów rośnie szybko — to odpowiedź na D-074. **To zmienia literę D-050** („+1 za trafienie”), więc
  potrzebny jest wybór ludzi (wybór 1). Wariant dosłowny D-050 (+1 / +2 / +3 / +4 za trafienie, bez malejącego zysku)
  to trzy liczby w `ustawienia.json`, bez zmiany kodu.
- **Serwer decyduje.** Klient zgłasza tylko naciśnięcie. Serwer sprawdza czas, kierunek i tempo zgłoszeń i dopiero
  wtedy dopisuje przyrost do atrybutu sesyjnego gracza (bez zapisu). Ogłasza go też sygnałem dla przyszłego modułu
  statystyk. Spam nie daje nic: bot wciskający losowo 20 razy na sekundę zdobywa w teście 0 jednostek.
- **Sterowanie na stanowisku**: kamera stoi, postać się nie rusza (klawisze ruchu są pochłonięte), a sterowanie
  dotykowe Robloxa jest wyłączone. Klawiatura, dotyk (przyciski co najmniej 44 px, tekst co najmniej 12 pt przy
  667 × 375) i pad. Po wyjściu wszystko wraca.
- **Frajda z trafienia**: licznik serii „podskakuje”, pojawia się krótki napis („TRAFIONE!”, „SERIA 10!”, „+1 Siła!”),
  ekran błyska, lecą odłamki, kamera lekko drży, a dźwięk trafienia idzie w górę razem z serią. Dźwięki pochodzą
  wyłącznie z plików wbudowanych w klienta Roblox; nic nie wgrywamy.
- **Scena**: jedna arena „Training Center” z prostych klocków, w powietrzu z dala od map. Stanowiska stoją obok
  siebie, a gracz trafia od razu na swoje. W budynku Training Center w bazarze jest trener z klawiszem E (D-085).

## Sześć mini-gier w skrócie

| Statystyka | Mini-gra | Jedno zdanie | W próbie |
|---|---|---|---|
| Siła | **Rozbijanie** | Miotacz rzuca skrzynki z czterech stron, a gracz rozbija je mieczem strzałką w stronę skrzynki. | grywalna |
| Pancerz | **Blok** | Golem bierze zamach, a gracz blokuje tarczą w chwili uderzenia i nie daje się nabrać na zmyłki. | grywalna |
| Kondycja | **Bieżnia** | Gracz biegnie w rytmie, naciskając lewą i prawą stopę równo z bębnem trenera. | w projekcie |
| Zręczność | **Kłody** | Kręcąca się kłoda nadlatuje nisko albo wysoko, a gracz przeskakuje albo pada w ostatniej chwili. | w projekcie |
| Inteligencja | **Runy** | Kamienie z runami świecą po kolei, a gracz powtarza coraz dłuższą sekwencję. | w projekcie |
| Szczęście | **Koniczyny** | Z drzewa lecą koniczyny i kamyki, a gracz koszykiem łapie koniczyny i omija kamyki. | w projekcie |

---

## 1. Siła — „Rozbijanie” (grywalna w próbie)

- **Pomysł.** Naprzeciw gracza stoi miotacz przy stosie skrzynek i rzuca skrzynki, dzbany i beczułki łukiem w jedną
  z czterech stref wokół gracza: górę, lewo, prawo albo dół. Gdy przedmiot dolatuje do świecącego kółka, gracz
  naciska strzałkę w tę stronę, a miecz rozbija przedmiot na kawałki. Im dłuższa seria, tym szybciej rośnie pasek Siły.
- **Dlaczego pasuje.** Siła to obrażenia zwykłych ciosów (D-062). Rozbijanie mieczem twardych rzeczy jest wprost
  „siłą ciosu” i to jest przykład Pawła z D-063.
- **Sterowanie.** Klawiatura: strzałki albo W / A / S / D. Dotyk: krzyż czterech przycisków ze strzałkami (56 px),
  po prawej stronie, obok kolumny HUD. Pad: Y / X / B / A (układ jak strefy: góra, lewo, prawo, dół) albo krzyżak.
- **Trafienie / pudło / seria.** Trafienie to właściwy kierunek w oknie ±0,30 s (na ostatnim poziomie ±0,19 s)
  wokół chwili dolotu. Pudło to zły kierunek, za wcześnie, za późno, przepuszczona skrzynka (przelatuje za plecy)
  albo machnięcie, gdy nic nie leci. Seria to trafienia z rzędu.
- **Trudność.** Rośnie co 11–12 s. Poziom 1 to rzut co 1,25 s z trzech stron (lewo, góra, prawo). Poziom 2 dokłada
  dół i rzut co 1,05 s, a potem co 0,9 s i 0,78 s, z coraz węższym oknem. Odstęp ma ±15% rozrzutu i zawsze jest
  dłuższy niż dwa okna, więc każde naciśnięcie wskazuje jedno zdarzenie.
- **Długość rundy.** 45 s, czyli ok. 45 rzutów (43–47).
- **Scena 3D.** Podest gracza, cztery przezroczyste kółka stref, miotacz z klocków (pomarańczowa kamizelka, fartuch,
  zielona opaska), stos skrzynek i szyld. Skrzynki, miecz i odłamki widzi tylko ten gracz.
- **Ryzyka.** D-050 mówi o kierunkach „góra / prawo / dół”, a próba ma cztery (wybór 2). Krzyż przycisków na
  telefonie może zasłaniać prawą strefę — do sprawdzenia na emulatorze. Kamera zza prawego ramienia jest dobrana
  na oko, nie na zrzucie.

## 2. Pancerz — „Blok” (grywalna w próbie, D-074: na próbę)

- **Pomysł.** Przed graczem stoi kamienny golem treningowy z czerwoną rękawicą. Bierze zamach i uderza w tarczę
  gracza, a pierścień na ekranie zbiega się do kółka dokładnie w chwili uderzenia. Gracz naciska BLOK właśnie
  wtedy. Fioletowy pierścień i fioletowe oczy golema oznaczają zmyłkę: golem cofa rękę, a zablokowanie to pudło.
- **Dlaczego pasuje.** Pancerz to punkty odejmowane od ciosu (D-062). Mini-gra uczy „przyjąć cios na pancerz”:
  właściwy moment i spokój, a nie szybkie klikanie. Zmyłki odróżniają ją od Siły.
- **Sterowanie.** Klawiatura: spacja, F albo strzałka w górę / W. Dotyk: jeden okrągły przycisk BLOK (96 px).
  Pad: A, R1 albo R2.
- **Trafienie / pudło / seria.** Trafienie to blok w oknie ±0,30 s (na końcu ±0,19 s) przy prawdziwym ciosie.
  Przeczekana zmyłka też liczy się jako trafienie. Pudło to blok za wcześnie albo za późno, cios bez bloku (kamera
  drży, czerwony błysk, bez obrażeń) i zablokowana zmyłka („ZMYŁKA!”). Seria działa jak w Sile.
- **Trudność.** Cios co 1,3 → 1,1 → 0,95 → 0,82 s. Zmyłek nie ma na początku, potem jest ich 15%, 20% i 25%.
  Okno się zwęża. Zamach trwa zawsze 1,0 s.
- **Długość rundy.** 45 s, czyli ok. 43 ciosy i zmyłki. Jednostek paska na minutę jest tyle samo co w Sile
  (test 2h: stosunek 0,85–1,18).
- **Scena 3D.** Podest, golem z klocków (szary, z pasem, niebieskimi oczami i czerwoną rękawicą, którą rusza klient),
  szyld. Tarczę widzi tylko ten gracz.
- **Ryzyka.** Paweł chciał najpierw Pancerz tylko z ekwipunku (D-063) i zgodził się na próbę — ocena po zagraniu.
  Wskazówka koloru przy zmyłce może być za łatwa albo za trudna dla daltonistów (wybór 3). Obie mini-gry
  opierają się na wyczuciu czasu, więc trzeba sprawdzić, czy nie są dla graczy „tym samym”.

## 3. Kondycja — „Bieżnia” (w projekcie)

- **Pomysł.** Gracz stoi na bieżni z klocków, a trener obok bije w bęben. Na taśmie podjeżdżają ślady lewej i prawej
  stopy. Gracz naciska lewą albo prawą stopę, gdy ślad dojedzie do linii. Co jakiś czas trafia się „podbieg”, czyli
  kilka szybszych kroków pod rząd.
- **Dlaczego pasuje.** Kondycja to życie i wytrzymałość (D-062). Równy wysiłek przez dłuższą chwilę to bieg.
  Liczy się rytm, a nie najszybsze klikanie, więc mini-gra nie męczy palca i nie nagradza spamu.
- **Sterowanie.** Klawiatura: A / D albo ← / →. Dotyk: dwa duże przyciski stóp, jeden pod lewym, drugi pod prawym
  kciukiem. Pad: LB / RB albo X / B.
- **Trafienie / pudło / seria.** Trafienie to właściwa stopa w oknie rytmu. Pudło to zła stopa, krok poza rytmem albo
  przegapiony ślad. Seria to kroki w rytmie z rzędu.
- **Trudność.** Tempo rośnie od ok. 90 do 150 kroków na minutę. Dochodzą podbiegi i podwójne kroki tą samą stopą.
- **Długość rundy.** 45 s.
- **Scena 3D.** Bieżnia z klocków (pasy taśmy przesuwane przez klienta), trener z bębnem, płytki śladów.
- **Ryzyka.** Na telefonie dźwięk może się opóźniać względem obrazu — potrzebna kalibracja albo szersze okno.
  Gra może być monotonna. BALANS_1711 wylicza, że Kondycja daje w walce najwięcej każdej klasie, więc jej mini-gra
  nie może być najłatwiejsza.

## 4. Zręczność — „Kłody” (w projekcie)

- **Pomysł.** Na okrągłym placu kręci się kłoda na długim ramieniu, raz nisko (przy kostkach), raz wysoko (na wysokości
  głowy). Gracz przeskakuje niską i pada pod wysoką w ostatniej chwili. Na wyższych poziomach przychodzą dwie kłody
  jedna po drugiej, a czasem kłoda zmienia wysokość w połowie obrotu.
- **Dlaczego pasuje.** Zręczność to unik (D-062): chodzi o to, żeby zejść z linii ciosu we właściwej chwili.
- **Sterowanie.** Klawiatura: spacja albo W to skok, S albo ↓ to padnij. Dotyk: przyciski SKOK i PADNIJ.
  Pad: A to skok, B to padnij.
- **Trafienie / pudło / seria.** Trafienie to właściwy unik w oknie przejścia kłody. Pudło to zły unik, unik za
  wcześnie (gracz już „opadł”) albo trącenie kłodą (bez obrażeń). Seria działa jak wyżej.
- **Trudność.** Szybszy obrót, kłody na zmianę i zmiana wysokości jako zmyłka.
- **Długość rundy.** 45 s.
- **Scena 3D.** Okrągły plac, słup z obracanym ramieniem i kłodą (animacja u klienta), trener-drwal.
- **Ryzyka.** Postać musi pokazać „padnij” bez wgrywania animacji (np. niższa poza kamery albo bryła tarczy) — do
  sprawdzenia. Z kamery stojącej z tyłu trudniej ocenić wysokość kłody, więc lepszy może być widok z boku.

## 5. Inteligencja — „Runy” (w projekcie)

- **Pomysł.** Cztery kamienie z runami (każdy ma inny kolor i kształt) stoją w krzyżu i świecą po kolei. Gracz
  powtarza sekwencję. Każda poprawna runa to trafienie, a po każdej całej sekwencji dochodzi jedna runa więcej.
- **Dlaczego pasuje.** Inteligencja to moc umiejętności i odporność na magię (D-062). Zapamiętanie i odtworzenie
  zaklęcia to praca głowy, nie ręki.
- **Sterowanie.** Klawiatura: strzałki albo W / A / S / D (kamienie w krzyżu jak przyciski) albo 1–4. Dotyk: cztery
  kamienie-przyciski. Pad: Y / X / B / A.
- **Trafienie / pudło / seria.** Trafienie to właściwa runa. Pudło to zła runa: sekwencja zaczyna się od nowa,
  o dwie runy krótsza. Seria to poprawne runy z rzędu.
- **Trudność.** Dłuższe sekwencje i szybszy pokaz, a wyżej „lustro”, czyli powtórzenie w odwrotnej kolejności.
- **Długość rundy.** 45 s, bez okna czasu na pojedynczą runę (jest tylko limit całej rundy).
- **Scena 3D.** Krąg czterech kamieni z neonowymi runami i mag-trener.
- **Ryzyka.** Runa wymaga więcej czasu niż skrzynka, więc trzeba wyrównać jednostki paska na minutę (D-074).
  Same kolory nie wystarczą daltonistom, stąd kształty run.

## 6. Szczęście — „Koniczyny” (w projekcie)

- **Pomysł.** Z drzewa z klocków spadają na trzech torach koniczyny i szare kamyki. Gracz przesuwa koszyk w lewo
  i w prawo, łapie koniczyny i omija kamyki. Rzadka złota czterolistna koniczyna daje podwójne jednostki paska.
  Jest widoczna od początku spadania i nie ma w niej nic losowego dla gracza.
- **Dlaczego pasuje.** Szczęście to krytyk (D-062), czyli „trafić w dobry moment”. Motywem jest szczęście
  (koniczyna), ale wynik zależy od ręki, a nie od losowania — żadnej losowej nagrody i nic za walutę (zasady bez
  hazardu z `Retencja i monetyzacja`).
- **Sterowanie.** Klawiatura: ← / → albo A / D. Dotyk: dwa przyciski albo przeciągnięcie palcem. Pad: lewa gałka
  albo krzyżak.
- **Trafienie / pudło / seria.** Trafienie to złapana koniczyna. Pudło to złapany kamyk albo koniczyna, która spadła
  na ziemię. Seria to złapane koniczyny z rzędu.
- **Trudność.** Szybsze spadanie, więcej kamyków i wiatr, który przesuwa koniczynę na sąsiedni tor.
- **Długość rundy.** 45 s.
- **Scena 3D.** Drzewo z klocków, trzy tory, koszyk przed graczem i trener-ogrodnik.
- **Ryzyka.** Tory przypominają Kłody i Bieżnię, więc trzeba zadbać o inny rytm. Złota koniczyna nie może wyglądać
  na „losowanie nagrody” (ważne przy płatnych przedmiotach losowych, D-052 i D-086). Nazwa do decyzji (wybór 8).

---

## Wybory dla ludzi

**1. Przyrost: pasek z malejącym zyskiem czy dosłownie D-050?**
- Pasek (dziś w próbie, liczby z BALANS_1711): ok. 10 trafień na pierwszy punkt świeżej statystyki, potem coraz
  wolniej. Jedna mini-gra się nie opłaca, ale u nisko poziomowych runda potrafi dać 0 punktów.
- D-050 dosłownie: +1 / +2 / +3 / +4 za trafienie, bez hamulca. Ok. 70 punktów na rundę, czyli wielokrotnie
  więcej, niż daje walka (BALANS_1711, część 6).
- Szczegóły: wariant to trzy liczby w `ustawienia.json` (`za_trafienie`, `prog_paska`, `malejacy_zysk`). W (punkty
  wytrenowane) żyje dziś tylko w sesji, więc ponowne wejście do gry zeruje hamulec — docelowo musi trafić do profilu.

**2. Siła: cztery kierunki czy trzy z D-050?**
- Cztery (dziś): lewo, góra, prawo, dół; pierwszy poziom tylko trzy.
- Trzy z D-050: góra, prawo, dół — prościej, ale bez lewej strony.

**3. Pancerz: zmyłka z kolorem czy bez?**
- Fioletowy pierścień i fioletowe oczy (dziś) — czytelne, niezbyt trudne.
- Bez koloru, tylko ruch golema — trudniej, bardziej „pancernie”.

**4. Runda: 45 s czy inaczej?**
- 45 s z odliczaniem (dziś).
- Krócej (30 s) na telefon albo „do pierwszego pudła” jako osobny tryb.

**5. HUD w czasie mini-gry**
- Zostaje (dziś); przyciski mini-gry leżą nad nim, krzyż jest na lewo od prawej kolumny HUD.
- Chowany na czas stanowiska — to okno 2D, więc decyzja i wykonanie należą do Pawła (D-093).

**6. Tymczasowa tablica wejścia przy spawnie**
- Zostaje na czas prób, potem do usunięcia (wejście tylko od trenera, D-085).
- Usunąć od razu po etapie B.

**7. Kolejne mini-gry: w jakiej kolejności budować?**
- Propozycja: Kondycja (największy pożytek w walce), potem Zręczność, Inteligencja i Szczęście.

**8. Nazwy mini-gier**
- Rozbijanie, Blok, Bieżnia, Kłody, Runy, Koniczyny — robocze, do zmiany.

**9. Sala czy budynek**
- Osobna sala w powietrzu (dziś) — miejsce na sześć stanowisk i stała kamera.
- Wnętrze budynku Training Center w bazarze — ciasno, kamera zderzy się ze ścianami.

## Ustawienia „przyjęte, do zmiany” (wszystkie w `ustawienia.json`)

| Co | Wartość | Skąd |
|---|---|---|
| Długość rundy, odliczanie, pierwsze zdarzenie | 45 s, 3 s, 1,0 s | przyjęte |
| Poziomy trudności (od) | 0 / 12 / 24 / 34 s | przyjęte |
| Siła: odstęp, okno, kierunki | 1,25 / 1,05 / 0,9 / 0,78 s; ±0,30 / 0,26 / 0,22 / 0,19 s; 3 / 4 / 4 / 4 | przyjęte |
| Siła: lot skrzynki | 1,1 s | przyjęte |
| Pancerz: odstęp, okno, zmyłki | 1,3 / 1,1 / 0,95 / 0,82 s; ±0,30 / 0,26 / 0,22 / 0,19 s; 0 / 15 / 20 / 25% | przyjęte |
| Pancerz: zamach | 1,0 s | przyjęte |
| Rozrzut odstępu | ±15% | przyjęte |
| Progi serii | 5 / 10 / 20 trafień | BALANS_1711 (te same co w D-050 „seria daje więcej”) |
| Pasek: jednostki za trafienie | 4 / 5 / 6 / 8 | BALANS_1711 |
| Pasek: próg | 40 × (1 + W / (0,1 × pula))² | BALANS_1711 |
| Pula z poziomu | 30 + 10 × (poziom − 1); poziom z atrybutu `Level` (dziś placeholder) | BALANS_1711 |
| Ulepszone centrum (D-050) | mnożnik 1 (bez ulepszeń w próbie) | przyjęte |
| Ochrona: kubełek zgłoszeń | 4 na start, +4 na sekundę | przyjęte |
| Ochrona: wiadomości od klienta | 12 na start, +12 na sekundę | przyjęte |
| Ochrona: czas klienta | od −0,35 s do +0,05 s względem serwera, inaczej czas serwera | przyjęte |
| Ochrona: przypisanie i dubel | 0,6 s; 0,25 s | przyjęte |
| Odstęp wejść / startów / E | 2 s / 1 s / 0,4 s | przyjęte |
| Zasięg wejścia od trenera i tablicy | 16 st | przyjęte |
| Telefon: przyciski | 56 px (strzałki), 52 px (pozostałe), 96 px (BLOK); skala 0,85–1,6 od 667 × 375 | przyjęte (wymóg 44 px, 12 pt) |
| Teksty | 15 / 18 / 26 / 40 / 56 px | przyjęte |
| Kamera stanowiska | oko 3,2 / 6,6 / 11,5 st od podestu (zza prawego ramienia), cel 8 st przed graczem | przyjęte, na oko |
| Arena | środek (3000; 300; 3000), 96 × 56 st | przyjęte (z dala od pasa krain, starego lasu i sal testowych) |
