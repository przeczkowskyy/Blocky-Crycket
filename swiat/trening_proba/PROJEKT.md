# Training Center — sześć mini-gier 3D

> **To jest PROPOZYCJA do akceptacji** (17.11.2026, uzupełniona w nocy 17/18.11). Ustalone są tylko punkty
> z zatwierdzonych decyzji wypisanych niżej. Pomysły na mini-gry, nazwy, liczby i układ sceny to propozycja agenta
> Karola. Dwie mini-gry (Siła i Pancerz) stoją w Studio do próby w grze (`README.md`, sprawdzone 17.11). Cztery
> kolejne (Kondycja, Zręczność, Inteligencja, Szczęście) są **zaprogramowane i sprawdzone offline** (testy, lustro
> logiki, podglądy brył w `podglady/`) — czekają na budowę i próbę w Studio. Co zmieniłem względem pierwszego opisu,
> jest w każdej sekcji pod „Zmiany względem projektu”.

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
  ekran błyska, lecą odłamki, kamera lekko drży, a dźwięk trafienia idzie w górę razem z serią. Dźwięki: gdy w miejscu
  jest pakiet `swiat/dzwiek_gra` z wgranym arkuszem efektów, trafienie Siły gra „cios”, Pancerza „blok”, Zręczności
  „unik”, punkt statystyki „awans”, koniec rundy „zwycięstwo”, złota koniczyna „monety”, ukończone zaklęcie „tarcza”
  (tylko zdarzenia, które są w arkuszu). Bez arkusza — pliki wbudowane w klienta Roblox; nic nowego nie wgrywamy.
- **Podpowiedź obrazkowa** (noc 17/18.11): na stanowisku i w czasie odliczania nad panelem startu stoi pasek z ramek:
  co widzisz → co naciskasz → co się dzieje (bez czytania). Przyciski mini-gry pojawiają się dopiero po odliczaniu,
  a naciśnięcia w odliczaniu nic nie robią (wcześniej liczyły się jako pudło „w powietrze”).
- **Waga mini-gry** (D-074): każda gra ma mnożnik jednostek paska (`gry.<id>.waga`), dobrany tak, żeby gracz-model
  zdobywał tyle samo jednostek na minutę w każdej z sześciu gier (test: 0,85–1,18 Siły; dziś 0,96–1,03).
- **Scena**: jedna arena „Training Center” z prostych klocków, w powietrzu z dala od map — 256 × 56 st, sześć stanowisk
  w jednym rzędzie (Kłody, Bieżnia, Rozbijanie, lobby, Blok, Runy, Koniczyny), każda kamera patrzy na północ, więc
  w tle jest tylko murek. Gracz trafia od razu na swoje stanowisko. W budynku Training Center w bazarze jest trener
  z klawiszem E (D-085).

## Sześć mini-gier w skrócie

| Statystyka | Mini-gra | Jedno zdanie | W próbie |
|---|---|---|---|
| Siła | **Rozbijanie** | Miotacz rzuca skrzynki z czterech stron, a gracz rozbija je mieczem strzałką w stronę skrzynki. | grywalna |
| Pancerz | **Blok** | Golem bierze zamach, a gracz blokuje tarczą w chwili uderzenia i nie daje się nabrać na zmyłki. | grywalna |
| Kondycja | **Bieżnia** | Gracz biegnie na taśmie twarzą do kamery i naciska lewą / prawą stopę, gdy ślad dojedzie do linii. | grywalna (Studio 18.11) |
| Zręczność | **Kłody** | Ramię z kłodą obraca się wokół słupa; niską gracz przeskakuje, pod wysoką pada. | grywalna (Studio 18.11) |
| Inteligencja | **Runy** | Kamienie z runami świecą po kolei, a gracz powtarza coraz dłuższą sekwencję. | grywalna (Studio 18.11) |
| Szczęście | **Koniczyny** | Postać z koszykiem nad głową przechodzi między trzema torami: łapie koniczyny, schodzi spod kamieni. | grywalna (Studio 18.11) |

Każda gra ma jedną czynność i jeden rodzaj wejścia, ale inne odczucie: **rytm** (Bieżnia: równe tempo, bęben),
**reakcja w kierunku** (Siła), **cierpliwość** (Pancerz: zmyłki), **ruch całym ciałem** (Kłody: skok albo padnij
w chwili przejścia kłody), **pamięć** (Runy: bez pośpiechu na pojedynczą runę) i **pozycja** (Koniczyny: gdzie stoi
koszyk, a nie kiedy się naciska). Wszystkie cztery nowe gry przeszły próbę w Studio 18.11 (README, „Część B”).

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
  telefonie zasłaniał prawą strefę — po zrzucie 667 × 375 kamera patrzy bardziej w prawo, a gracz i strefy stoją
  w lewej połowie ekranu (README, „Poprawki po próbach w grze”). Prawdziwego telefonu i dotyku jeszcze nikt nie
  próbował. Trudność dla człowieka do oceny (w próbie rundy grał automat).

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

## 3. Kondycja — „Bieżnia” (grywalna w próbie: offline 17/18.11, Studio 18.11)

- **Pomysł.** Gracz biegnie na bieżni z klocków **twarzą do kamery**, a trener obok bije w bęben. Na taśmie jadą ku
  niemu ślady lewej i prawej stopy (lewy tor po lewej stronie ekranu). Gracz naciska LEWA albo PRAWA, gdy ślad dojedzie
  do białej linii przed jego palcami. Stopy idą zawsze na zmianę. Od trzeciego poziomu trafia się „podbieg”: cztery
  pomarańczowe ślady trochę gęściej.
- **Dlaczego pasuje.** Kondycja to życie i wytrzymałość (D-062). Równy wysiłek przez dłuższą chwilę to bieg. Liczy się
  rytm, a nie najszybsze klikanie, więc mini-gra nie męczy palca i nie nagradza spamu.
- **Sterowanie.** Klawiatura: A / D albo ← / →. Dotyk: dwie duże stopy (96 px) — lewa w lewym dolnym rogu, prawa
  po prawej stronie. Pad: LB / RB, X / B albo krzyżak.
- **Trafienie / pudło / seria.** Trafienie to właściwa stopa w oknie ±0,25 s (na końcu ±0,19 s). Pudło: zła stopa
  („ZŁA STOPA”), za wcześnie, za późno, przepuszczony ślad („POTKNIĘCIE”). Zawsze ta sama stopa nie popłaca: co drugi
  krok to pudło, a seria nie rośnie (test 2k).
- **Trudność.** Krok co 0,8 → 0,7 → 0,62 → 0,56 s (75 → 107 kroków na minutę), bez rozrzutu, bo to rytm. Podbiegi od
  24 s (6–8% kroków zaczyna podbieg, krok ×0,8).
- **Długość rundy.** 45 s, 66–69 kroków. Waga 0,7 (kroków jest więcej niż skrzynek w Sile).
- **Scena 3D.** Taśma 5,6 × 16 st z przesuwanymi pasami (klient), rama w kolorze Kondycji, wałki, poręcze po bokach,
  linia kroku i dwa cele stóp (świecą, gdy ślad jest w oknie), prowadnice torów, tablica z tyłu, trener w dresie
  z gwizdkiem i czerwony bęben (pałka i błysk na każdy krok). Postać biegnie animacją „run” z własnego skryptu
  Animate awatara (bez wgrywania animacji), szybciej przy szybszym tempie.
- **Zmiany względem projektu.** (1) Biegacz stoi twarzą do kamery, a ślady jadą od przodu — na pierwszym podglądzie
  postać za plecami zasłaniała linię i nadjeżdżające ślady. (2) Bez „podwójnych kroków tą samą stopą” — dla dziecka
  to pułapka. (3) Podbiegi dopiero od trzeciego poziomu.
- **Ryzyka.** Na telefonie dźwięk może się spóźniać — rozstrzyga obraz (ślad na linii) i serwer, bęben tylko pomaga.
  Monotonia (do oceny w grze). BALANS_1711: Kondycja daje w walce najwięcej — tę grę łatwo osłabić wagą.

## 4. Zręczność — „Kłody” (grywalna w próbie: offline 17/18.11, Studio 18.11)

- **Pomysł.** Na okrągłym placu stoi słup, a wokół niego obraca się długie ramię z kłodą — raz nisko (przy kostkach),
  raz wysoko (na wysokości głowy). Niską gracz przeskakuje (SKOK), pod wysoką pada (PADNIJ), w chwili gdy kłoda
  dochodzi do jego miejsca. Między dwoma przejściami ramię robi jeden pełny obrót, więc kłodę widać cały czas.
- **Dlaczego pasuje.** Zręczność to unik (D-062): zejść z linii ciosu we właściwej chwili.
- **Sterowanie.** Klawiatura: spacja, W albo ↑ = SKOK; S albo ↓ = PADNIJ. Dotyk: SKOK nad PADNIJ (po 80 px) po prawej.
  Pad: A = skok, B = padnij.
- **Trafienie / pudło / seria.** Trafienie to właściwy unik w oknie ±0,32 s (na końcu ±0,26 s) wokół chwili, w której
  trzeba nacisnąć; kłoda dochodzi do postaci 0,15 s później (skok trwa 0,6 s). Pudło: odwrotny unik („ODWROTNIE!”),
  za wcześnie, za późno, brak uniku — kłoda trąca postać („BUM!”, postać się odchyla, kamera drży, bez obrażeń).
- **Trudność.** Obrót co 1,7 → 1,5 → 1,32 → 1,18 s. Pierwszy poziom: tylko niskie kłody (sam skok). Od trzeciego:
  12–15% „zmian” — kłoda najpierw ustawia się na złej wysokości i przeskakuje na właściwą w połowie obrotu (właściwą
  widać na ok. 0,5 s przed przejściem). Zwykle wysokość ustala się w drugiej ćwiartce obrotu (ok. 0,8 s przed).
- **Długość rundy.** 45 s, 30–32 kłody. Waga 1,2.
- **Scena 3D.** Plac z piasku (śr. 22 st), słup ze złotą kulą, ramię z kłodą i trzema żółtymi pasami (obraca je
  i podnosi klient — Model `Ramie`), żółty podest gracza (świeci, gdy kłoda jest w oknie), szyld za placem, drwal
  w kraciastej koszuli z siekierą — z boku, poza zasięgiem ramienia. Kamera z ukosa z przodu, nisko (4,4 st): dobrze
  widać, czy kłoda jest przy kostkach, czy przy głowie.
- **Postać.** Skok i padnij pokazuje przesunięcie stawu biodra tylko u tego gracza (Motor6D: `C0`; nowe stawy awatara
  — AnimationConstraint, jak w tym miejscu 18.11: `CFrame` jego `Attachment0`): skok — uniesienie po łuku 2,7 st, padnij — w dół i pochylenie, uderzenie — odchylenie w tył. Bez wgrywania
  animacji, działa dla R6 i R15; po rundzie, zejściu i resecie staw wraca (próba T16 i T20).
- **Zmiany względem projektu.** Jedno ramię (bez „dwóch kłód jedna po drugiej”); zmiana wysokości tylko jako rzadka
  zmyłka od trzeciego poziomu; pierwszy poziom wyłącznie skoki.
- **Ryzyka.** Czy przesunięcie biodra wygląda dobrze na różnych awatarach (do obejrzenia w Studio). Czy kąt kamery
  wystarcza do oceny wysokości (podgląd: tak). Kłoda nie ma kolizji — gracz nie może się o nią zahaczyć.

## 5. Inteligencja — „Runy” (grywalna w próbie: offline 17/18.11, Studio 18.11)

- **Pomysł.** Cztery kamienie w krzyżu na kamiennej ścianie (góra, lewo, prawo, dół — jak strzałki), każdy z innym
  znakiem i kolorem: niebieski pierścień, czerwony kwadrat, zielony romb, żółty krzyż. Kamienie świecą po kolei (każdy
  ma swoją nutę), a gracz powtarza sekwencję. Każda poprawna runa to trafienie; po całej sekwencji „ZAKLĘCIE!” i runa
  więcej.
- **Dlaczego pasuje.** Inteligencja to moc umiejętności i odporność na magię (D-062). Zapamiętanie i odtworzenie
  zaklęcia to praca głowy, nie ręki.
- **Sterowanie.** Klawiatura: strzałki albo W / A / S / D (kamienie w krzyżu jak strzałki). Dotyk: krzyż czterech
  kamieni-przycisków (60 px) w kolorach i kształtach z kamieni. Pad: Y / X / B / A albo krzyżak.
- **Trafienie / pudło / seria.** Trafienie to właściwa runa. Pudło to zła runa („OJ! JESZCZE RAZ”): sekwencja wraca
  o dwie runy krótsza (najmniej 2), **z tym samym początkiem**. Naciśnięcia w czasie pokazu są pomijane bez kary,
  podwójne stuknięcie tej samej runy (do 0,25 s) też. Po 6 s bez naciśnięcia ten sam pokaz wraca od początku.
  Seria to poprawne runy z rzędu.
- **Trudność.** Sekwencja 3 → 8 run (po każdym zaklęciu +1), potem nowe zaklęcie od 3. Pokaz coraz szybszy:
  runa świeci 0,6 → 0,52 → 0,45 → 0,4 s. W liście run ta sama runa nie stoi dwa razy z rzędu.
- **Długość rundy.** 45 s, bez limitu na pojedynczą runę. Gracz-model (reakcja 0,55 s, runa co 0,42 s) trafia ok. 26
  run na rundę → waga 1,35.
- **Scena 3D.** Kamienna ściana z łukiem i szyldem, cztery kamienie ze znakami (Neon i jaśniejszy kamień w czasie
  świecenia, czerwone przy błędzie), mag w fioletowej szacie z laską, której kula świeci w czasie pokazu. Kropki
  postępu w lewym górnym rogu (ile run w sekwencji, ile już wpisano). Napisy „PATRZ!” i „TWOJA KOLEJ!”. Postać
  gracza stoi z boku, półprzezroczysta (nie zasłania kamieni).
- **Zmiany względem projektu.** (1) Bez „lustra” (powtarzania od końca) — wymaga czytania i myli dzieci; trudność daje
  szybszy pokaz i dłuższe sekwencje. (2) Po błędzie ten sam początek (łatwiej się pozbierać). (3) Ponowny pokaz po
  bezczynności.
- **Ryzyka.** Zgadywanie 1 z 4 zawsze coś daje: bot losujący runy zdobywa ok. 16–18% tego, co gracz mylący co dziesiątą
  runę (w pozostałych grach bot ma 0). Stanie bez ruchu daje 0. Kolory nie wystarczą daltonistom — stąd kształty.

## 6. Szczęście — „Koniczyny” (grywalna w próbie: offline 17/18.11, Studio 18.11)

- **Pomysł.** Z korony drzewa spadają na trzy tory koniczyny i szare kamienie. Postać trzyma koszyk **nad głową**
  i przechodzi między torami: łapie koniczyny, schodzi spod kamieni. Rzadka złota czterolistna koniczyna (7%) daje
  podwójne jednostki paska — jest złota od początku spadania, nic w niej nie jest losowane dla gracza.
- **Dlaczego pasuje.** Szczęście to krytyk (D-062), czyli „być we właściwym miejscu we właściwej chwili”. Motywem jest
  koniczyna, ale wynik zależy od ręki, nie od losowania — żadnej losowej nagrody i nic za walutę.
- **Sterowanie.** Klawiatura: A / D albo ← / → (o jeden tor). Dotyk: ◀ w lewym dolnym rogu, ▶ po prawej (88 px).
  Pad: krzyżak, X / B, LB / RB.
- **Trafienie / pudło / seria.** Trafienie to koniczyna złapana: koszyk na jej torze w chwili upadku **i przez 0,2 s
  wcześniej**. Pudło: koniczyna spadła obok („SPADŁA”), koszyk wsunięty w ostatniej chwili („ZA PÓŹNO”), kamień do
  koszyka („AUĆ! KAMIEŃ”). Kamień obok koszyka nie jest werdyktem (seria zostaje). Ruch koszyka sam w sobie nie jest
  ani trafieniem, ani pudłem.
- **Gdzie spada.** Tor liczy serwer (i tak samo klient) z miejsca koszyka w chwili, gdy rzecz zaczyna spadać:
  koniczyna — na jeden z dwóch pozostałych torów, a gdy się da, nie na tor kamienia, który jeszcze leci; kamień —
  w koszyk. Stanie w miejscu daje więc 0 (test: 40 rund, 0 jednostek) i nie ma trybu AFK (D-050). Cień na torze
  pokazuje, gdzie spadnie.
- **Trudność.** Upadek co 1,4 → 1,2 → 1,05 → 0,95 s, lot 1,7 s. Kamieni nie ma na pierwszym poziomie, potem 22–28%.
  Od trzeciego poziomu wiatr: 20–25% koniczyn zaczyna o tor obok i w pierwszej połowie lotu dryfuje na swój.
- **Długość rundy.** 45 s, 37–39 rzeczy. Waga 1,3.
- **Scena 3D.** Trawnik z trzema jasnymi polami torów (pole pod koszykiem świeci), drzewo z pniem z tyłu i koroną
  z gałęzią nad torami, szyld z boku, ogrodnik w fartuchu, kapeluszu i z konewką. Koszyk z klocków i spadające rzeczy
  widzi tylko ten gracz. Postać przechodzi między torami w 0,14 s (klient przesuwa swoją postać), ręce podniesione
  (staw barku, tylko u siebie, R15).
- **Zmiany względem projektu.** (1) Tor koniczyny zależy od miejsca koszyka (stanie w miejscu = 0) — inaczej gracz
  stojący na środku łapałby co trzecią bez ruchu. (2) Koszyk nad głową — przed postacią zasłaniało go ciało (podgląd).
  (3) Wymóg 0,2 s pod koniczyną — bez niego bot machający koszykiem łapał co trzecią (38% zysku gracza); teraz 11%.
  (4) Postać chodzi z koszykiem, a nie sam koszyk.
- **Ryzyka.** „ZA PÓŹNO” przy wsunięciu w ostatniej chwili może być dla dziecka niezrozumiałe (0,2 s to ok. 1/8 lotu —
  do oceny w grze, liczba w ustawieniach). Złota koniczyna nie może wyglądać na losowanie nagrody (D-052, D-086).

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
- Chowany na czas stanowiska (dziś, od poprawek po przejściu gry 17.11) i oddawany przy zejściu.
- Zostawiony — wtedy przyciski gier trzeba ułożyć wokół kolumny HUD (decyzja o oknach 2D należy do Pawła, D-093).

**6. Tymczasowa tablica wejścia przy spawnie**
- Zostaje na czas prób, potem do usunięcia (wejście tylko od trenera, D-085).
- Usunąć od razu po etapie B.

**7. Kolejne mini-gry: w jakiej kolejności budować?**
- Rozstrzygnięte w nocy 17/18.11: wszystkie cztery naraz (polecenie Karola), w kodzie i offline; do próby w Studio.

**8. Nazwy mini-gier**
- Rozbijanie, Blok, Bieżnia, Kłody, Runy, Koniczyny — robocze, do zmiany.

**9. Sala czy budynek**
- Osobna sala w powietrzu (dziś) — miejsce na sześć stanowisk i stała kamera.
- Wnętrze budynku Training Center w bazarze — ciasno, kamera zderzy się ze ścianami.

**10. Runy: bez „lustra”?**
- Bez (dziś): trudność z długości sekwencji i tempa pokazu — dziecko nie musi czytać.
- Z lustrem na ostatnim poziomie (powtarzanie od końca) — trudniej, potrzebny napis.

**11. Koniczyny: wymóg 0,2 s pod koniczyną**
- Zostaje (dziś): koszyk wsunięty w ostatniej chwili to „ZA PÓŹNO”; bot machający koszykiem ma 11% zysku gracza.
- Bez wymogu: łapie każde wsunięcie, ale miotanie koszykiem łapie co trzecią koniczynę (38% zysku gracza).

**12. Bieżnia: biegacz twarzą do kamery**
- Tak (dziś): widać twarz i bieg, ślady jadą od przodu i nic ich nie zasłania.
- Za plecami (pierwszy pomysł): bardziej „jak bieg”, ale ciało zasłania linię kroku (podgląd).

**13. Kłody: skok i padnij przesunięciem biodra**
- Tak (dziś): bez wgrywania animacji, działa na każdym awatarze, widać tylko u siebie.
- Własne animacje skoku i padnięcia — ładniej i widać u innych graczy, ale trzeba je zrobić i wgrać.

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
| Kamera stanowiska | oko 3,2 / 6,6 / 11,5 st od podestu (zza prawego ramienia), cel 6,0 (Siła) / 5,5 (Pancerz) st w prawo i 8 st przed graczem — gracz w lewej połowie ekranu, prawa wolna na przyciski | przyjęte, poprawione po zrzutach 17.11 |
| Strefy Siły | góra (0; 6,6; −1,6), lewo / prawo (∓3,4; 3,4; −1,6), dół (0; 0,9; −3,2) st od podestu | przyjęte, „dół” odsunięty po zrzutach |
| Postać w rundzie | półprzezroczysta u siebie (0,55), żeby strefa „dół” była widoczna | przyjęte po zrzutach |
| Czcionka okien i szyldów | Nunito ExtraBold (pełne polskie znaki; FredokaOne ich nie ma) | przyjęte po zrzutach |
| Arena | środek (3000; 300; 3000), 256 × 56 st (od nocy 17/18.11; było 96 × 56) | przyjęte (z dala od pasa krain, starego lasu i sal testowych) |
| Stanowiska (x od środka areny) | Kłody −104, Bieżnia −64, Siła −24, lobby 0, Pancerz +24, Runy +64, Koniczyny +104; podest z = +8 | przyjęte, noc 17/18.11 |
| Waga (mnożnik jednostek paska) | Siła 1, Pancerz 1, Bieżnia 0,7, Kłody 1,2, Runy 1,35, Koniczyny 1,3 — gracz-model: 0,96–1,03 Siły na minutę | dobrane symulacją (test 2h) |
| Bieżnia: krok, okno, podbiegi | 0,8 / 0,7 / 0,62 / 0,56 s; ±0,25 / 0,23 / 0,21 / 0,19 s; 0 / 0 / 6 / 8% (4 kroki ×0,8) | przyjęte |
| Bieżnia: ślady | widać 1,8 s przed linią, 4 st/s; stopy ±1,2 st od środka taśmy, linia 1,8 st przed biegaczem | przyjęte po podglądach |
| Kłody: obrót, okno, wysokości, zmiany | 1,7 / 1,5 / 1,32 / 1,18 s; ±0,32 / 0,30 / 0,28 / 0,26 s; 1 / 2 / 2 / 2; 0 / 0 / 12 / 15% | przyjęte |
| Kłody: geometria | ramię 9,6 st, kłoda śr. 1,3 st, nisko 1,0 / wysoko 4,8 st; gracz 7 st od słupa; kłoda przy graczu 0,15 s po chwili naciśnięcia | przyjęte |
| Runy: długość, kara, przerwy | 3 → 8 (+1 po zaklęciu), −2 po błędzie (min. 2); przerwa 0,8 s, po błędzie 1,3 s, ponowny pokaz po 6 s | przyjęte |
| Runy: tempo pokazu | świeci 0,6 / 0,52 / 0,45 / 0,4 s, przerwa 0,22 / 0,2 / 0,17 / 0,15 s | przyjęte |
| Koniczyny: upadki, kamienie, wiatr, złote | 1,4 / 1,2 / 1,05 / 0,95 s; 0 / 22 / 25 / 28%; 0 / 0 / 20 / 25%; 7% (×2) | przyjęte |
| Koniczyny: lot, pierwsza, pod koniczyną | 1,7 s; pierwszy upadek 2,4 s po starcie; koszyk na torze 0,2 s przed upadkiem | przyjęte (0,2 s — po teście bota) |
| Kubełek Run i Koniczyn | 6 na start, +6 na sekundę (szybkie wpisywanie i przejścia) | przyjęte |
| Przyciski nowych gier | stopy 96 px, SKOK / PADNIJ 80 px, runy 60 px, ◀ ▶ 88 px; podpowiedź obrazkowa 400 × 80 | przyjęte (wymóg 44 px, 12 pt) |
| Panel rundy i przyciski (18.11, po zrzutach telefonu) | panel 210 × 52 w prawym górnym rogu, „X” obok; przyciski gier przy krawędziach ekranu na dole; obszar GUI w bezpiecznym obszarze telefonu | przyjęte (test 5e: 6 gier × 4 ekrany) |
| Kamery Bieżni i Koniczyn (18.11) | Bieżnia oko (0; 8,4; 14,5), cel (0; 1,4; −0,5); Koniczyny oko (0; 9,4; 17,5), cel (0; 8,1; −6) | przyjęte po teście 5e |
| Dźwięki z arkusza (swiat/dzwiek_gra) | trafienie Siły „cios”, Pancerza „blok”, Zręczności „unik”; punkt „awans”; koniec „zwyciestwo”; złota „monety”; zaklęcie „tarcza”; START „przycisk”; najwyżej 4 naraz | przyjęte; bez arkusza — dźwięki wbudowane |
