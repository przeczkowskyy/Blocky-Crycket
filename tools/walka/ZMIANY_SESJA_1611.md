# Silnik walki v3 — zmiany po sesji głównej 16.11.2026

> **Status: propozycja (liczby robocze), nie kanon.** Zrobione na zlecenie z sesji 16.11 (Karol i Paweł): silnik v2
> zostaje bazą, a zmienia się to, co ustalili — mana zamiast odnowień, Zręczność i Inteligencja przydatne każdej klasie,
> blok i unik każdej klasy, limit Pancerza, statusy z charakterem, tarcza procentowa, sloty z pełną dowolnością,
> pasywki (w slotach i broni), klasy potworów, tempo. Wszystkie liczby są w `tools/walka/dane_walki.json` (nic na
> sztywno w kodzie) i dobrał je automat strojący na symulacjach — można je zaokrąglać, ale wtedy trzeba przeliczyć
> tabele (`python -B tools/walka/balans.py`). Kanoniczne decyzje (D-062 Pancerz punktowy, D-055 sloty, D-059 pet,
> D-060 bez jajek, D-058 Shard ze strażnika) są zachowane. Dokument dla zespołu z v2:
> `B&C/Gra/Walka v2 — silnik, klasy i umiejętności.md` (tej notatki nie zmieniałem — sejf prowadzi inny agent).
>
> **Po niezależnej kontroli (16/17.11)** część liczb i twierdzeń niżej jest poprawiona (pasywki many, Kumulowanie
> trucizny, nieznane pola wejścia, nowe testy). Co znaleziono, co naprawiono i co zostało ludziom — sekcja
> „Niezależna kontrola (16/17.11)” przed tabelami balansu.

## W skrócie

- **Mana zamiast odnowień:** każda strona (także potwór) ma pasek 0–100; +40 za własny zwykły cios, +1,3 za każdy
  1% utraconego życia; gdy starczy na następną aktywną umiejętność w rotacji slotów (koszt 100), używa jej zamiast
  ciosu. Mana nie jest statystyką — zmieniają ją przedmioty, drzewko, pasywki w slotach i pasywki broni.
  Pierwsza umiejętność: mediana w **3. akcji**; build pod manę używa umiejętności **1,2–1,6× częściej** (od 1. akcji; cel ok. 2× nie jest osiągnięty — kontrola 16/17.11).
- **Statystyki każdej klasie:** Zręczność daje też mnożnik krytyka (z nasyceniem, więcej klasom o niskim limicie
  uniku), Inteligencja = moc umiejętności i odporność na magię (nie mana). Punkt każdej statystyki podnosi wygrane
  każdej klasy; najsłabsza statystyka jest warta 35–63% najmocniejszej. Nabijanie jednej statystyki przegrywa z wzorcową; z potworami Mag z 60% w Kondycji jest równy rozkładowi wzorcowemu (tabela h — dawne „zawsze przegrywa” było za mocne).
- **Obrona:** Pancerz punktowy (D-062) z jawnym limitem 75% (zawsze przechodzi ≥ 25% ciosu); przelicznik Pancerza
  Wojownika 1,6 (inni 1,2–1,25). Blok ma każda klasa (5%), tarcza dodaje Wojownikowi 28,3%; **blok zmniejsza
  obrażenia** (przechodzi 25%, decyzja Karola z 16.11). Unik jak w v2.
- **Statusy z charakterem:** trucizna w stosach (do 5, +4 z pasywki), podpalenie od życia celu, krwawienie od ciosu,
  spowolnienie (unik i mana, bez utraty tury), ogłuszenie (utrata tury), zdarcie Pancerza, tarcza −% na 3 tury,
  wzmocnienie. Obrażenia w czasie omijają obronę, unik, blok i tarczę.
- **Sloty z dowolnością** (aktywne / pasywne / mieszanka), pasywki broni, premie z przedmiotów — jako dane.
  **Wskrzeszenie** (propozycja D-094): legendarna pasywka w slocie, raz na walkę powrót z 25% życia.
- **Potwory mają klasy** (Slime i Wilk — Zwiadowca, Muchomornik — Mag, Troll — Wojownik, Strażnik — klasa strażnika)
  i przechodzą przez ten sam wzór co postać.
- **Równość:** różnica klas przy tym samym potworze najwyżej 6,8 pp (63 z 65 zestawień ≤ 5 pp), pojedynki klas
  45,9–54,5%; na ziarnach kontrolnych 8,0 pp przy Strażniku na 1. poziomie i pojedynki do 55,3% (kontrola 16/17.11,
  ziarna 200001–203000: 7,9 pp przy Strażniku na 1. poziomie — **twarda granica 7 pp przekroczona**, test przechodzi tylko
  na ziarnach 1–2000). Buildy z wzorcową swojej klasy **46,7–53,6%** (po kontroli) — ale wyraźnego „swojego” i „nie
  swojego” potwora w lesie mają tylko 3–4 z 18 (niżej).
- **Tempo:** krzywa doświadczenia **11,71 × L^1,6** daje las w **ok. 30 min** (mediana 29,7; 10–90% graczy 22–39 min),
  ok. 8 przegranych po drodze, Strażnik na 11. poziomie; 7 biomów w 600 min → **8. biom na ok. 65. poziomie**.
- **Luau:** dosłowny port; zgodność sprawdzona bez Studio — złożony kod do Studio wykonany w nowym interpreterze
  `tools/walka/luau_mini.py`: **592/592 identycznych dzienników** i 52/52 złych wejść odrzuconych (po kontroli 16/17.11: 60/60). W Studio jeszcze
  nie uruchomiony.

## Zasady tak, jak zostały zrobione

### Co zostało z v2

Walka trwa, aż życie jednej strony spadnie do zera (bez minimalnej liczby tur, ostatniego dechu i ściskania czasu);
pełny determinizm z ziarna (generator Park–Miller, stała kolejność rzutów); ten sam wzór dla gracza, postaci-przeciwnika
i potwora; dziennik zdarzeń z naturalnymi czasami (czas całości = wstęp + suma czasów zdarzeń + finał); walidacja wejścia
z czytelnym błędem „Walka: …”; techniczny limit 1000 tur; łup bez jajek, Shard Ewolucji tylko ze strażnika; Pancerz
punktowy (D-062); zwykły atak Maga bije Siłą (magia to tylko rodzaj obrażeń). Tura strony: (1) tyknięcia jej efektów,
(2) ogłuszona traci turę, inaczej akcja, (3) jej efekty tracą jedną turę. Kolejność rzutu przy ataku: unik → blok →
krytyk → trafienie.

### Mana (zamiast odnowień)

| Co | Jak |
|---|---|
| Pasek | każda strona (gracz, potwór, postać na Arenie) ma pasek **0–100**, start 0 (+ „mana na starcie” z modyfikatorów) |
| Zysk | **+M** za każdy własny zwykły cios (także chybiony); **+K × procent utraconego maks. życia**, gdy strona dostaje obrażenia (także z trucizny); oba × (1 + zysk many), spowolnienie obniża zysk |
| Użycie | na swojej turze strona patrzy na **następną aktywną umiejętność w rotacji slotów**: gdy mana ≥ jej koszt, używa jej zamiast zwykłego ciosu i płaci koszt; inaczej zwykły cios. Rotacja: aktywne w kolejności slotów, potem od początku; pasywne nie biorą udziału |
| Koszt | `koszt_many` umiejętności (dziś 100 = pełny pasek) × (1 − zniżka); zniżka najwyżej 60% |
| Modyfikatory | zysk many, zniżka kosztu, mana na starcie — z przedmiotów (amulet, pierścień, zbroja), węzłów drzewka, pasywek w slotach i pasywek broni. **Mana nie jest statystyką** (nie ma okna, nie trenuje się jej; Inteligencja jej nie zmienia) — w oknie statystyk wystarczy osobna linia „Mana: +X% zysku, −Y% kosztu” |
| Kto | każda klasa i każdy potwór (potwory też mają umiejętności z many) |

### Statystyki

| Statystyka | Co daje (wzór; liczby w danych) |
|---|---|
| **Siła** | cios = mnożnik klasy × (obrażenia broni + 0,75 × Siła) — także zwykły atak Maga (magiczny) |
| **Kondycja** | życie = mnożnik klasy × (66 + 40 × poziom + 11,5 × Kondycja) |
| **Inteligencja** | moc umiejętności = 1 + 1,8 × Int / (Int + połowa) **i** odporność na magię = przelicznik klasy × 1,0 × Int (punkty). Nie daje many |
| **Zręczność** | unik = start klasy + (limit klasy − start) × Zr / (Zr + połowa) **i** (nowe) mnożnik krytyka + premia klasy × Zr / (Zr + połowa) — premia jest większa u klas z niskim limitem uniku, więc punkt Zręczności jest wart podobnie u każdej klasy |
| **Szczęście** | szansa krytyka = 5% + 60% × Sz / (Sz + połowa) |
| **Pancerz** | Pancerz = przelicznik klasy × (1,4 × Pancerz + Pancerz z przedmiotów), odejmowany od ciosu fizycznego |

„Połowa” = 4 + 2 × poziom (tyle punktów daje połowę drogi do limitu krzywej). Krzywe z nasyceniem są takie same na
każdym poziomie (pula rośnie liniowo, połowa też), więc proporcje nie psują się na wysokich poziomach — patrz (i).

### Obrona: Pancerz, odporność, blok, unik

- **Pancerz nigdy nie zeruje ciosu:** obrażenia = max(25% surowego ciosu, cios − Pancerz) — jawny limit redukcji 75%
  (`limit_redukcji`). To samo dla magii z odpornością. Do tego zawsze co najmniej 1.
- **Wojownik korzysta z Pancerza lepiej:** przelicznik Pancerza 1,6 (Zwiadowca 1,2, Mag 1,25) — przy tych samych
  punktach i przedmiotach ma o ok. 28–33% więcej Pancerza i szybciej dochodzi do limitu. Ma też przelicznik
  odporności na magię 2,2 (inni 1,0): bez tego Mag, którego magia omija Pancerz, kontrował Wojownika (patrz wybór 6).
- **Blok ma każda klasa** (D-062): 5% z klasy, **tarcza Wojownika dodaje 28,3%** (razem ok. 33%). **Blok zmniejsza
  otrzymane obrażenia** (Karol, 16.11, odpowiedź na pytanie 46): przechodzi 25% ciosu (`czesc_przez_blok`; warianty
  50% i — tylko dla porównania — 0% w tabeli f). Blok działa na zwykły cios i na umiejętność (zablokowana umiejętność
  nie nakłada efektów); obrażeń w czasie nie da się zablokować.
- **Unik** jak w v2 (Zwiadowca 25% → 50%, Wojownik i Mag od 0% do swojego limitu), razem najwyżej 60%.

### Statusy — każdy ma inny charakter

| Efekt | Typ | Trwa (tury nosiciela) | Siła | Stosy | Uwagi |
|---|---|---:|---|---:|---|
| Trucizna | obrazenia_w_czasie | 4 | 12% ciosu atakującego × moc na stos | 5 | tyka na początku tury nosiciela; omija Pancerz, odporność i tarczę; bez uniku i bloku; modyfikatory: stosy_trucizny, sila_trucizny |
| Podpalenie | obrazenia_w_czasie | 2 | 5,3% maks. życia celu × moc (najwyżej 60% ciosu atakującego) | 1 | tyka na początku tury nosiciela; omija Pancerz, odporność i tarczę; bez uniku i bloku; modyfikatory: trwanie_podpalenia |
| Krwawienie | obrazenia_w_czasie | 3 | 25% trafienia, które je nałożyło | 1 | tyka na początku tury nosiciela; omija Pancerz, odporność i tarczę; bez uniku i bloku |
| Spowolnienie | spowolnienie | 2 | unik −56%, zysk many −50% | 1 | nie zabiera tury |
| Ogłuszenie | ogluszenie | 1 | — | 1 | zabiera najbliższą turę |
| Zdarty pancerz | zdarcie | 3 | Pancerz −50% | 1 |  |
| Kamienna skóra | oslona | 3 | trafienia −42% × moc (najwyżej 75%) | 1 | tarcza z umiejętności; nie działa na obrażenia w czasie |
| Bariera | oslona | 3 | trafienia −36% × moc (najwyżej 75%) | 1 | tarcza z umiejętności; nie działa na obrażenia w czasie |
| Skupienie | wzmocnienie | 3 | obrażenia +46% × moc | 1 |  |

- **Trucizna** (Paweł: build „kumulowanie trucizny”): każde nałożenie dokłada stos (do limitu), tyka długo, siła od
  ciosu atakującego. Pasywka „Kumulowanie trucizny” podnosi limit stosów i siłę, „Jadowity kostur” siłę i szansę zaklęcia.
- **Podpalenie:** bez stosów, krótko, procent maks. życia celu (z limitem względem ciosu atakującego) — mocne na
  grubych celach (troll, strażnik), słabe na małych. „Ognista różdżka” wydłuża je o 2 tury (przykład z sesji).
- **Krwawienie:** procent trafienia, które je nałożyło — im mocniejszy cios (krytyk), tym mocniej krwawi.
- **Spowolnienie** (Lodowy pocisk): nie zabiera tury, tylko obniża unik i zysk many. **Ogłuszenie** (Ogłuszające
  uderzenie trolla, Uścisk korzeni strażnika, czasem Miażdżący cios): zabiera najbliższą turę.
- **Trucizna i podpalenie** (i krwawienie) są nieblokowalne, nie do uniknięcia i omijają odporność na magię, Pancerz
  i tarczę (potwierdzone na sesji).
- Ten sam efekt odświeża się (czas i siła); trucizna przy tym dokłada stos.

### Tarcza z umiejętności

Kamienna skóra (Wojownik) i Bariera (Mag): rzucenie kosztuje turę (jak w v2), tarcza trwa **3 tury** nosiciela
i **zmniejsza trafienia o procent** (× moc umiejętności, najwyżej 75%) — zamiast puli pochłaniania. W dzienniku
`pochloniete` = ile tarcza zatrzymała (do napisu „TARCZA −n”).

### Sloty, pasywki, pasywki broni, premie

- **Trzy sloty z pełną dowolnością:** 3 aktywne, 3 pasywne albo dowolna mieszanka (liczba slotów to wejście — odkrywa
  je drzewko, D-055). W slocie może być umiejętność aktywna klasy (`umiejetnosci`) albo pasywna klasy (`pasywne`).
- **Pasywka** = stałe modyfikatory na całą walkę (np. Kolos: więcej życia i obrażeń; Rozdzieracz: na starcie zdziera
  część Pancerza przeciwnika na całą walkę — przykład Karola mówił o 20%, po strojeniu 12%). Bez zdarzeń w dzienniku.
- **Pasywka broni** (`bron.pasywka`) — tak samo, z wadą (np. Ciężka różdżka: mocny zwykły atak, wolniejsza mana —
  przykład z sesji; Ognista różdżka: podpalenie +2 tury).
- **Premie** (`premie`) — modyfikatory z przedmiotów i węzłów drzewka, które sumuje serwer (zamknięta lista kluczy
  z granicami w danych; złe klucze i wartości silnik odrzuca błędem „Walka: …”).
- Modyfikatory sumują się w stałej kolejności (premie → pasywka broni → pasywki w slotach) i są przycinane do granic.

### Wskrzeszenie — propozycja D-094 (nie kanon)

Karol przyjął ją słownie w oknie Balans panelu; czeka na jego podpis i potwierdzenie Pawła. Zrobione tak:

| Co | Jak |
|---|---|
| Czym jest | **legendarna umiejętność pasywna** `wskrzeszenie` w danych (`pasywne`, `legendarna: true`, `klasa: ""` — każda klasa); zajmuje jeden z trzech slotów |
| Czym nie jest | nie jest modyfikatorem, więc **nie da jej pasywka broni ani premia z przedmiotów czy drzewka** (silnik odrzuca `premie.wskrzeszenie` i broń z taką pasywką błędem „Walka: …”); dwa razy w slotach — też błąd |
| Działanie | raz na walkę strata życia, która zbiłaby je do zera, kończy się **powrotem z 25% maks. życia** (`wskrzeszenie: 0.25` w danych); **bez losowania** |
| Co ją wyzwala | **każda** śmiertelna strata życia: cios, umiejętność i — decyzja tej paczki — także **śmiertelne tyknięcie trucizny, podpalenia albo krwawienia** (inaczej zatruty gracz ginąłby z nieużytą legendą; do decyzji, wybór 16) |
| Po powrocie | efekty na postaci trwają dalej (trucizna tyka), mana zostaje; atak, który „zabił”, nakłada swoje efekty (np. truciznę z zaklęcia), bo cel znowu żyje |
| Dziennik | nowe zdarzenie **`wskrzeszenie`** zaraz po zdarzeniu, które zbiło życie do zera: `kto = cel =` wskrzeszona strona, `wartosc` = życie po powrocie, `hp_*` już po powrocie, czas 1,5 s (`stale.czasy.wskrzeszenie`). `Dziennik.sprawdz` pilnuje: tylko zaraz po nokaucie, najwyżej raz na stronę, życie 1..maks |
| Zastępuje | dawny pomysł węzła „Jeszcze stoję” (1 HP) |

Ile jest warte w symulacji: część „Wyniki” (akapit „Wskrzeszenie”) i tabela (k); wybory 16 i 17.

### Potwory mają klasy

Potwór jest opisany jak postać: klasa, punkty sześciu statystyk, broń, Pancerz z przedmiotów (pary baza / na poziom),
modyfikatory (charakter: np. Slime ma więcej życia i słabsze ciosy) i umiejętności — i przechodzi przez ten sam wzór
(`bojowe`), te same ataki, obronę i manę. Leśny Slime i Cierniowy Wilk to klasa Zwiadowca (25% uniku na start),
Muchomornik — Mag (bije magią), Leśny Troll — Wojownik, Strażnik Gaju — klasa tylko dla potworów „Strażnik biomu”.

| Potwór | Ranga | Klasa | 5. poziom: życie / cios / Pancerz / odporność / unik / blok | Modyfikatory | Umiejętność |
|---|---|---|---|---|---|
| Leśny Slime | zwykły | Zwiadowca | 423 / 43,8 / 20,6 / 0,7 / 31,6% / 5% | życie -35%, obrażenia +40%, Pancerz -15%, odporność -90% | Kwaśny plusk |
| Cierniowy Wilk | zwykły | Zwiadowca | 246 / 42 / 17,7 / 2,4 / 36,5% / 5% | Pancerz -15%, odporność -20%, życie -50%, obrażenia +5% | Rozszarpanie |
| Muchomornik | zwykły | Mag | 360 / 48,3 / 18,5 / 6,3 / 11% / 5% | Pancerz -5%, odporność -65%, życie -28%, obrażenia +8% | Chmura zarodników |
| Leśny Troll | rzadki | Wojownik | 583 / 59,4 / 38,7 / 14,1 / 5,4% / 5% | życie +6%, Pancerz -5%, odporność +60%, obrażenia +29% | Ogłuszające uderzenie |
| Strażnik Gaju | strażnik | Strażnik biomu | 933 / 48,9 / 33,3 / 7 / 3,9% / 5% | życie +53%, Pancerz +5%, odporność -30%, obrażenia +11% | Uścisk korzeni |

### Liczby (z `dane_walki.json`)

| Stała | Wartość |
|---|---:|
| pasek many (`mana_maks`) | 100 |
| mana za własny zwykły cios (także chybiony) (`mana_za_cios`) | 40 |
| mana za 1% utraconego maks. życia (`mana_za_obrazenia`) | 1,3 |
| premia do zysku many za każdą aktywną ponad pierwszą (`mana_premia_za_aktywna`) | 0,2 |
| obrona zatrzymuje najwyżej tyle ciosu (`limit_redukcji`) | 0,75 |
| część ciosu przez blok (`czesc_przez_blok`) | 0,25 |
| blok najwyżej (`blok_maks`) | 0,5 |
| unik najwyżej (`unik_maks`) | 0,6 |
| krytyk bez Szczęścia (`krytyk_baza`) | 0,05 |
| krytyk z samego Szczęścia najwyżej (`krytyk_limit`) | 0,65 |
| krytyk razem najwyżej (`krytyk_maks`) | 0,75 |
| moc umiejętności z Inteligencji: +najwyżej (`moc_maks`) | 1,8 |
| odporność na magię za punkt Int. (`odpornosc_za_inteligencje`) | 1 |
| cios za punkt Siły (`sila_za_punkt`) | 0,75 |
| Pancerz za punkt Pancerza (`pancerz_za_punkt`) | 1,4 |
| życie: baza (`zycie_baza`) | 66 |
| życie: za poziom (`zycie_na_poziom`) | 40 |
| życie: za punkt Kondycji (`zycie_za_kondycje`) | 11,5 |

| Klasa | Zwykły cios | Mnożnik życia / ciosu | Przelicznik Pancerza / odporności | Unik (start → limit) | Krytyk × (bez Zr → z Zr) | Blok klasy | Tarcza |
|---|---|---|---|---|---|---:|---|
| Wojownik | fizyczne | 0,95 / 1,071 | 1,6 / 2,2 | 0% → 24,2% | 2 → 4 | 5% | +28,3% z tarczy wzorcowej |
| Zwiadowca | fizyczne | 1,152 / 0,934 | 1,2 / 1 | 25% → 50% | 2,57 → 3,37 | 5% | — |
| Mag | magiczne | 1,112 / 1,1 | 1,25 / 1 | 0% → 41,9% | 2 → 3,6 | 5% | — |
| Strażnik biomu (tylko potwory) | fizyczne | 1 / 1 | 1,2 / 1 | 0% → 15% | 1,9 → 2,4 | 5% | — |

| Umiejętność | Klasa | Koszt many | Działanie |
|---|---|---:|---|
| Potężne cięcie | wojownik | 100 | 206% ciosu × moc, fizyczne |
| Miażdżący cios | wojownik | 100 | 141,2% ciosu × moc, fizyczne + Zdarty pancerz, Ogłuszenie (15%) |
| Kamienna skóra | wojownik | 100 | na siebie + Kamienna skóra |
| Uderzenie z góry | zwiadowca | 100 | 152,7% ciosu × moc, fizyczne, krytyk +27,1 pp |
| Zatruta strzała | zwiadowca | 100 | 150% ciosu × moc, fizyczne + Trucizna |
| Skupienie | zwiadowca | 100 | na siebie + Skupienie |
| Kula ognia | mag | 100 | 169% ciosu × moc, magiczne + Podpalenie |
| Lodowy pocisk | mag | 100 | 135,6% ciosu × moc, magiczne + Spowolnienie |
| Bariera | mag | 100 | na siebie + Bariera |
| Kwaśny plusk | potwor | 100 | 120% ciosu × moc, magiczne + Zdarty pancerz |
| Rozszarpanie | potwor | 100 | 140% ciosu × moc, fizyczne + Krwawienie |
| Chmura zarodników | potwor | 100 | 100% ciosu × moc, magiczne + Trucizna |
| Ogłuszające uderzenie | potwor | 100 | 166% ciosu × moc, fizyczne + Ogłuszenie (60%) |
| Uścisk korzeni | potwor | 100 | 140% ciosu × moc, magiczne + Ogłuszenie |

| Pasywka (slot) | Klasa | Działanie |
|---|---|---|
| Kolos | wojownik | życie +4%, obrażenia +2% |
| Mur tarczy | wojownik | blok +4 pp, Pancerz +16% |
| Rozdzieracz | wojownik | Pancerz przeciwnika -12% na całą walkę |
| Furia | wojownik | zwykły cios +11% |
| Zwinność | zwiadowca | unik +7 pp |
| Oko łowcy | zwiadowca | krytyk +1 pp, mnożnik krytyka +0,03 |
| Przypływ adrenaliny | zwiadowca | zysk many +10%, mana na starcie +15 (kontrola 16/17.11: było +35% i +35 — za mocne, patrz niżej) |
| Seria | zwiadowca | zwykły cios +13% |
| Kumulowanie trucizny | mag | limit stosów trucizny +4, siła trucizny +43% (kontrola 16/17.11: bez dawnego „szansa zaklęcia +14 pp” — podnosiło też szansę zaklęcia OGNIA) |
| Przepływ many | mag | zysk many +10%, mana na starcie +15 (kontrola 16/17.11: było +35% i +35) |
| Skupiona magia | mag | moc umiejętności +2% |
| Magiczny pocisk | mag | zwykły cios +12% |
| Bitewny rytm | wojownik | zysk many +10%, mana na starcie +15 (kontrola 16/17.11: było +30% i +35) |
| Wskrzeszenie (legendarna, propozycja D-094) | każda | raz na walkę śmiertelna strata życia → powrót z 25% maks. życia |

| Pasywka broni | Klasa | Działanie |
|---|---|---|
| Ognista różdżka | mag | podpalenie (tury) +2 |
| Ciężka różdżka | mag | zwykły cios +16%, zysk many -30% |
| Jadowity kostur | mag | szansa zaklęcia +28 pp, siła trucizny +28%, zwykły cios -10% |
| Kostur many | mag | zysk many +25%, zwykły cios -10% |
| Topór rzeźnika | wojownik | zwykły cios +15%, zysk many -30% |
| Miecz runiczny | wojownik | zysk many +25%, zwykły cios -10% |
| Łuk wiatru | zwiadowca | unik +5 pp, zwykły cios -8% |
| Łuk myśliwego | zwiadowca | zwykły cios +18%, zysk many -30% |
| Łuk runiczny | zwiadowca | zysk many +25%, zwykły cios -10% |

## Wyniki strojenia (C) — najważniejsze liczby

Wszystko na wzorcowych postaciach (`tools/walka/wzorcowe.py`, te same co w v2 i w prototypie Studio), potwór tego
samego poziomu, te same ziarna dla porównywanych stron. Pełne tabele niżej (wynik `python -B tools/walka/balans.py`).

| Co | Cel | Wynik (ziarna testu 1–2000) | Kontrola (ziarna 50001–52000) |
|---|---|---|---|
| Różnica klas przy tym samym potworze (13 poziomów × 5 potworów) | ≤ 5 pp, granica 7 | najwyżej **6,8 pp** (Strażnik, 1. poziom); **63 z 65** zestawień ≤ 5 pp | najwyżej **8,0 pp** (Strażnik, 1. poziom; Strażnik na poz. 1–6: 4–8 pp); 58 z 65 ≤ 5 pp. Kontrola 16/17.11 (ziarna 200001–203000, 3000 walk): **7,9 pp** (Strażnik, 1. poz.: 37,4 / 29,5 / 30,5), 60 z 65 ≤ 5 pp, 1 ponad 7 |
| Pojedynki klasa na klasę (oba miejsca) | 45–55% | **45,9–54,5%** | 46,5–55,3%; kontrola 16/17.11: 46,4–54,9% |
| Trudność (średnio klasy) | zwykłe ok. 85%, troll ok. 55%, strażnik ok. 36% | zwykłe 82–91%, troll 47–58%, strażnik 29–38% | — |
| Pierwsza umiejętność (mediana) | 3.–4. własna akcja | **3. akcja** | — |
| Użycia umiejętności na walkę (wzorcowa) | 2–3 | zwykły potwór 1,4–2,1 (Mag mniej — krótsze walki), Slime 2,1–3,3, troll 2,0–3,6, strażnik 2,6–4,8 | — |
| Build pod manę: użycia | ok. 2× | **1,2–1,6×** wzorcowej (kontrola 16/17.11: przy trollu i strażniku na 10. poz. 1,2×), pierwsza umiejętność w 1. akcji (limit paska — wybór 2) | — |
| Buildy z wzorcową swojej klasy | 45–55% | **46,7–53,6%** (po kontroli 16/17.11; przedtem 48,2–54,6%) | — |
| Najlepszy DARMOWY zestaw slotów z wzorcową (przeszukanie wszystkich, tabela l) | nie może wyraźnie dominować | po kontroli 16/17.11 **≤ 60%** (Mag: Kula ognia + Przepływ many + Magiczny pocisk 59,9%); przed poprawką pasywek many **63–67%** | świeże ziarna 300001+: 60,4% (ten sam zestaw) |
| Build ma potwora wyraźnie lepszego i gorszego (≥ 3 pp) | każdy | **tylko 3–4 z 18** (Pancerz i blok Wojownika na 5. i 10. poz., mana Maga na 5.; unik Zwiadowcy na 5. na granicy, −3,0 pp) — patrz „Czego nie udało się zrobić” | — |
| Każda statystyka coś daje każdej klasie | wszystkie > 0 | wszystkie > 0; najsłabsza / najmocniejsza **0,35–0,63** (v2: ok. 0,3–0,5) | — |
| Nabijanie jednej statystyki (60% puli) | nie może się opłacać | gorzej niż rozkład wzorcowy: −8 do −40 pp z potworami, 2–45% z wzorcową — **z wyjątkiem Maga i Kondycji** (już w tabeli h: 70,4% / 69,7%) | kontrola 16/17.11 (ziarna 160001+): Mag 60% Kondycji ±0 pp z potworami / 49,7% z wzorcową, **45% Kondycji +3,2 pp / 53,2%** (5. poz.), +1,9 pp / 52,2% (10. poz.); reszta 45–60% zawsze gorzej |
| Pancerz | nigdy nie zeruje, Wojownik lepiej | limit 75%; ten sam Pancerz z punktów: Wojownik 66% redukcji ciosu trolla, Zwiadowca 38%, Mag 43% | — |
| Wysokie poziomy (30–100) | rozsądnie | różnica klas 4,8–5,5 pp, pojedynki 48–53%, walki stale ok. 12 tur / 23 s (zwykły) i 27 tur / 45 s (strażnik), krzywe nasycone w tym samym miejscu | — |

**Blok (tabela f):** przy 25% (dziś) różnica klas 3,5–4,5 pp, pojedynki 46,8–53,5%, tarcza daje Wojownikowi
+18–19 pp wygranych; przy 50% — 5,8–7,4 pp i 43,7–55,1% (tarcza +15,5–16,5 pp); przy 0% (blok zatrzymuje wszystko,
tylko porównanie) — 9,7–10,1 pp i 45,5–56,2%, tarcza +21–23 pp: Wojownik za mocny bez przestrojenia.

**Sloty (tabela g, 10. poziom):** 3 aktywne ≈ 70–71% z potworami; 2 aktywne + pasywka 69–75%; 1 aktywna + 2 pasywne
72–76% (z wzorcową 53–56%); **3 pasywne 37–48%** (bez aktywnych pasek many się marnuje). Przy jednym pasku many
2. i 3. aktywna są warte mało, więc zwykłe pasywki musiały zostać słabe (Kolos +4% życia i +2% obrażeń) — wybór 3.

**Wskrzeszenie (tabela k, propozycja D-094):** legenda za 25% życia daje **+15–17 pp** wygranych z potworami i **74–76%** w pojedynku z wzorcową (5. i 10. poziom; zwykła pasywka w tym samym slocie: −1…+4 pp, 48–54%). Szacunek z okna Balans („25% ≈ +10–15 pp, tyle co slot”) jest więc trochę za niski, a „100% ≈ +35–45 pp” — za wysoki: przy 100% wychodzi **+28–30 pp** (wygrane z potworami nasycają się, z wzorcową 94–96%). Uczciwa wymiana „slot za wskrzeszenie” (tyle, co zwykła pasywka) wypada przy **1 HP–5% życia** (+3…+9 pp). Na poziomach 1–4 wskrzeszenie zabiera jedyny slot z umiejętnością i jest wyraźnie gorsze.

## Tempo (D) — propozycja liczb, nie kanon

`python -B tools/walka/tempo.py` (200 symulowanych graczy na klasę, prawdziwy silnik, walki w tempie ×1).

Krzywa doświadczenia: **na poziom L → L+1 potrzeba 11,71 × L^1,6** (zaokrąglone). Tempo odtwarzania ×1,0, odrodzenie gracza 15,0 s, rozdanie punktów 8,0 s, farmienie po przegranej z bramą: 3 walk, trening: brak.

| Poziom | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 15 | 20 | 30 | 50 | 70 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Doświadczenie do następnego | 12 | 35 | 68 | 108 | 154 | 206 | 263 | 326 | 394 | 466 | 892 | 1413 | 2704 | 6122 | 10489 |

Przegrody lasu (propozycja): Leśny Slime poz. 1–3, 8 s między walkami; Muchomornik poz. 3–5, 10 s między walkami; Cierniowy Wilk poz. 5–8, 10 s między walkami; Leśny Troll poz. 9–9 (brama), 25 s między walkami; Strażnik Gaju poz. 10–10 (brama), 40 s między walkami.

### Las: czas do pokonania Strażnika Gaju (200 graczy na klasę)

| Klasa | Mediana | 10%–90% graczy | Przegrane po drodze (mediana / 90%) | Bez żadnej przegranej | Poziom przy Strażniku | Walk | Prób bram (troll + strażnik) | Czas samych walk | Trening |
|---|---:|---|---|---:|---:|---:|---:|---:|---|
| Wojownik | 29,9 min | 23,4–38,1 min | 8 / 12 | 0,0% | 11 | 45 | 6 | 57% | — |
| Zwiadowca | 30,9 min | 24,2–39,3 min | 8 / 12 | 0,0% | 11 | 46 | 7 | 57% | — |
| Mag | 27,5 min | 21,9–36,0 min | 8 / 13 | 0,0% | 11 | 46 | 6 | 53% | — |

Wszystkie klasy razem: mediana **29,7 min**, poziom przy Strażniku **11**.

**Z treningiem** (`--trening 6`: Training Center 6 punktów na minutę, malejący zysk, 2 minuty po każdej przegranej
z bramą): ta sama mediana (ok. 30 min), ale mniej walk (39 zamiast 45) i mniej prób bram (4 zamiast 6–7), a Strażnik pada na 10. zamiast 11. poziomie — trening zastępuje farmienie, więc jest powód trenować.

| Klasa | Mediana | 10%–90% graczy | Przegrane po drodze (mediana / 90%) | Bez żadnej przegranej | Poziom przy Strażniku | Walk | Prób bram (troll + strażnik) | Czas samych walk | Trening |
|---|---:|---|---|---:|---:|---:|---:|---:|---|
| Wojownik | 29,6 min | 23,6–36,8 min | 7 / 11 | 0,0% | 10 | 39 | 4 | 49% | 4,0 min, 18 pkt |
| Zwiadowca | 30,8 min | 23,9–36,7 min | 7 / 11 | 0,0% | 10 | 39 | 4 | 49% | 4,0 min, 18 pkt |
| Mag | 28,3 min | 22,9–34,9 min | 7 / 11 | 0,0% | 10 | 39 | 4 | 44% | 4,0 min, 18 pkt |

### Model biomów 1–7: plan rosnący (propozycja), razem 600 min

| Biom | Minuty | Poziom na wejściu | Poziom na końcu | Poziomów | Walk (ok.) |
|---|---:|---:|---:|---:|---:|
| Las | 30 | 1 | 11 | 10 | 56 |
| Bagno | 45 | 11 | 19 | 8 | 83 |
| Dżungla | 60 | 19 | 26 | 7 | 110 |
| Pustynia | 75 | 26 | 34 | 8 | 137 |
| Góry z tundrą | 95 | 34 | 43 | 9 | 173 |
| Lodowiec | 125 | 43 | 53 | 10 | 229 |
| Wulkaniczny | 170 | 53 | 65 | 12 | 311 |

Do 8. biomu (Kryształowy) gracz dochodzi na poziomie **65**.

### Model biomów 1–7: plan równy, razem 600 min

| Biom | Minuty | Poziom na wejściu | Poziom na końcu | Poziomów | Walk (ok.) |
|---|---:|---:|---:|---:|---:|
| Las | 86 | 1 | 20 | 19 | 158 |
| Bagno | 86 | 20 | 30 | 10 | 157 |
| Dżungla | 86 | 30 | 39 | 9 | 156 |
| Pustynia | 86 | 39 | 46 | 7 | 157 |
| Góry z tundrą | 86 | 46 | 53 | 7 | 157 |
| Lodowiec | 86 | 53 | 59 | 6 | 157 |
| Wulkaniczny | 86 | 59 | 65 | 6 | 157 |

Do 8. biomu (Kryształowy) gracz dochodzi na poziomie **65**.

Silnik na wysokich poziomach zachowuje się rozsądnie (tabela i): pula punktów i „połowa” krzywych rosną liniowo
z poziomem, więc unik, krytyk i moc umiejętności stoją w tym samym miejscu (np. Zwiadowca 35% uniku, Mag moc 1,98
od 30. do 100. poziomu), a walka trwa tyle samo tur i sekund. Życie i ciosy rosną liniowo (na 100. poziomie kilka
tysięcy życia — bez problemu dla liczb). Trudność dalszych biomów trzeba będzie ustawić ich potworami.

## Wybory do decyzji

Każdy da się zmienić w danych (`dane_walki.json`) albo w kilku liniach kodu; „Dziś” = tak, jak jest zrobione.

1. **Ile obrażeń zabiera blok**
   - Karol (16.11, pytanie 46): blok zmniejsza otrzymane obrażenia, tarcza daje Wojownikowi większą szansę — zrobione.
   - Dziś: przez blok przechodzi 25% ciosu (`czesc_przez_blok` = 0,25). Tabela (f): wariant 50% i — tylko dla porównania — 0%.
2. **Tempo many: ile za cios i za obrażenia**
   - Dziś: 40 za cios, 1,3 za 1% utraconego życia, koszt 100; pierwsza umiejętność w 3. akcji (mediana).
   - Szybciej = umiejętność co 2 akcje i mniej zwykłych ciosów; wolniej = jak dawne odnowienia.
3. **Czy kolejna aktywna w slocie przyspiesza manę**
   - Problem: przy jednym pasku 2. i 3. aktywna dają głównie różnorodność; bez premii były warte mniej niż pusty slot.
   - Dziś: +20% zysku many za każdą aktywną ponad pierwszą — wtedy 2. i 3. aktywna są warte ok. 0, więc zwykłe pasywki (Kolos, Oko łowcy, Skupiona magia) musiały zostać słabe, a „3 pasywne” jest słabe (tabela g).
   - Opcja: większa premia (np. +50%) i mocniejsze pasywki — wymaga przestrojenia potworów; albo „mocny cios”, gdy pasek pełny, a w slotach nie ma aktywnej.
4. **Rotacja umiejętności: ściśle po slotach czy „mądrze”**
   - Dziś: ściśle w kolejności slotów (przewidywalne, łatwe do pokazania).
   - Opcja: pomijać tarczę albo wzmocnienie, które jeszcze trwa, i debuff, który już wisi na wrogu.
5. **Pasywki: stałe na walkę czy tylko „na starcie”**
   - Dziś: stałe modyfikatory na całą walkę (Kolos, Rozdzieracz), bez zdarzeń w dzienniku.
   - Opcja: efekt na starcie na N tur (np. Kolos +50% przez 3 tury, jak w przykładzie Pawła) — nowe zdarzenia dla odtwarzacza.
6. **Odporność Wojownika na magię (przelicznik 2,2)**
   - Bez niej Mag (magia omija Pancerz) wygrywał z Wojownikiem ok. 58%.
   - Opcja: zostawić; albo słabsze umiejętności Maga i niższa moc z Inteligencji (wtedy Int mniej warta wszystkim).
7. **Przeliczniki Pancerza klas**
   - Dziś: Wojownik 1,6, Zwiadowca 1,2, Mag 1,25 — Wojownik ma wyraźnie więcej Pancerza z tych samych punktów i przedmiotów.
   - Wyższy przelicznik Wojownika wymaga obcięcia jego życia, inaczej wygrywa ze Zwiadowcą.
8. **Ile Zręczności idzie w mnożnik krytyka**
   - Dziś: Wojownik do +2,0, Mag do +1,6, Zwiadowca do +0,8 (Zwiadowca ma większy limit uniku).
   - Opcja: jedna premia dla wszystkich (prościej, ale Zręczność mniej warta Wojownikowi).
9. **Trucizna: limit stosów i czy Inteligencja ją wzmacnia**
   - Dziś: do 5 stosów (+4 z pasywki Kumulowanie trucizny), 4 tury; z zaklęcia broni bez mocy (Int nie pomaga), z umiejętności × moc.
   - Opcja: zaklęcie też × moc (Mag trucizny mocniejszy, Int warta więcej).
10. **Podpalenie od życia celu z limitem**
    - Dziś: 5,3% maks. życia celu × moc, najwyżej 60% ciosu atakującego (inaczej Kula ognia kasowała grubego Wojownika na niskich poziomach).
    - Opcja: bez limitu (build podpalenia rozbija bossów) albo mniejszy procent.
11. **Tarcza a obrażenia w czasie**
    - Dziś: tarcza procentowa nie działa na truciznę, podpalenie i krwawienie.
    - Opcja: tarcza zmniejsza wszystko — trucizna słabnie wobec Maga z Barierą.
12. **Leśny Slime jako „zwiadowca” (25% uniku)**
    - Dziś: tak, jak na sesji (Slime i Wilk typu zwiadowcy); Slime ma więcej życia i słabsze ciosy.
    - Opcja: Slime jako wojownik (gruby, blokuje) — bardziej pasuje do galarety.
13. **Koszt buildów w modelu**
    - Model: build pod manę oddaje 20–26% puli (przedmioty many zamiast przedmiotów ze statystykami), build trucizny 10%.
    - Do ustalenia przy projekcie przedmiotów: co dokładnie dają amulet, pierścień i zbroja (szybsza mana jest warta bardzo dużo).
14. **Przegrody lasu, troll i krzywa doświadczenia**
    - Propozycja liczb w części „Tempo”; w pakiecie `swiat/las_potwory` trolla dziś nie ma — w modelu stoi przed strażnikiem.
15. **Plan 600 minut: rosnący czy równy**
    - Policzone oba: 30/45/60/75/95/125/170 min i po ok. 86 min na biom.
16. **Wskrzeszenie (D-094): czy wyzwala je trucizna i podpalenie**
    - Dziś: tak — każda śmiertelna strata życia (także tyknięcie), raz na walkę.
    - Opcja: tylko cios i umiejętność (prostsze w odbiorze, słabsze przeciw truciźnie).
17. **Wskrzeszenie (D-094): z ilu procent życia**
    - Dziś: 25% (jak w propozycji). Symulacja: +15–17 pp z potworami, 74–76% z wzorcową (zwykła pasywka: −1…+4 pp) — to moc „legendy”.
    - Uczciwa wymiana „slot za wskrzeszenie”: 1 HP–5% życia (+3…+9 pp); 25% zostawić, jeśli legenda ma być wyraźnie mocniejsza od slotu.

### Sprawy sporne z sesji (pkt 12 zlecenia) — nie zrobione, tylko pytania

18. **Czwarty slot umiejętności za Robuxy** — slot (pasywka albo 2./3. aktywna) jest dziś wart kilka pp; płatny slot to przewaga za pieniądze.
19. **Runy przeciw truciźnie** — odporność na obrażenia w czasie (nowy modyfikator) osłabiłaby build trucizny.
20. **Płatna rasa z lepszymi statystykami** — sprzeczne z równymi klasami; możliwa tylko kosmetyka.

## Dziennik v3 — co musi umieć odtwarzacz (`swiat/test_walki2`, `swiat/las_potwory`)

Plików budowanych do Studio **nie zmieniałem**. Silnik przyjmuje to samo wejście co v2 (nowe pola są opcjonalne),
więc serwer prototypu (`SerwerWalki2`, `Wzorcowe.luau`) i serwer lasu (`SerwerPotworow`) liczą walki bez zmian;
kopia silnika i `Dziennik` trafiają do Studio przy każdej budowie (`zbuduj.py`). Odtwarzacz sprawdza dziennik
`Dziennik.sprawdz` — po przebudowie dostanie wersję 3 razem z nowym silnikiem.

| Co nowego | Gdzie w dzienniku | Co odtwarzacz musi zrobić |
|---|---|---|
| wersja dziennika **3** | `walka.wersja` | nic (Dziennik.luau przychodzi z silnikiem) |
| **mana obu stron** | każde zdarzenie: `mana_gracz`, `mana_wrog` (po zdarzeniu, liczby całkowite 0–100); strony: `mana` (na starcie), `mana_maks` | paski many pod paskami życia (w HUD gry pasek Many już jest — D-048); pełny pasek = zapowiedź umiejętności |
| **koszt umiejętności** | `wartosc` przy zdarzeniu z umiejętnością (`umiejetnosc`, `unik` i `blok` z polem `umiejetnosc`) | spadek paska many o koszt w chwili użycia |
| **stosy** | `stosy` przy `efekt_nalozony` i `efekt_tick` (trucizna 1–9 z pasywką Kumulowanie trucizny, reszta 1) | licznik stosów na ikonie trucizny („TRUCIZNA ×3”); `wartosc` przy nałożeniu = obrażenia tyknięcia ze wszystkimi stosami |
| **nowy efekt `ogluszenie`** (utrata tury) | `efekt_nalozony` / `utrata_tury` / `efekt_koniec` z `efekt = "ogluszenie"` | wpis w `Choreografie.EFEKTY` (wygląd, ikona, napis „OGŁUSZENIE!”), wygląd zależny od umiejętności (gwiazdki: troll, Miażdżący cios; pnącza: Uścisk korzeni — przenieść z `WYGLAD_SPOWOLNIENIA`); `Obsluga.utrata` pulsuje dziś ozdobę `…:spowolnienie` — ma pulsować `…:ogluszenie` |
| **spowolnienie bez utraty tury** | `efekt = "spowolnienie"` trwa 2 tury, bez `utrata_tury` | zostaje wygląd lodu (Lodowy pocisk); napis „TRACI TURĘ!” już się przy nim nie pojawi |
| **tarcza procentowa** | `kamienna_skora`, `bariera`: typ `oslona`, `wartosc` przy nałożeniu = procent (np. 40 = −40%), trwa 3 tury; `pochloniete` przy trafieniu = ile zatrzymała | nie pokazywać „zapasu” tarczy (typ nie jest już `tarcza`, więc odtwarzacz sam go nie liczy); „TARCZA −n” działa jak dziś; „TARCZA PĘKŁA!” już się nie zdarzy — tarcza kończy się `efekt_koniec` po 3 turach |
| **blok u każdej klasy i potwora** | `typ = "blok"` także u Maga, Zwiadowcy i potworów | dziś: napis „BLOK!” i iskry przy piersi (klip bloku ma tylko Wojownik) — potrzebne klipy albo choreografia bloku dla pozostałych aktorów |
| **blok zmniejsza obrażenia** (Karol, 16.11: odpowiedź na pytanie 46) | `walka.czesc_przez_blok` (dziś 0,25 = blok zabiera 75%); wariant „blok zatrzymuje wszystko” (0) zostaje tylko w tabeli porównania | „BLOK!” i mniejsza liczba — jak dziś |
| **podpalenie dłuższe** | `tury` przy nałożeniu (np. 4 z Ognistą różdżką) | licznik tur na ikonie (już działa) |
| **pierwsza akcja może być umiejętnością** | mana na starcie (modyfikator) | nic nowego — zwykła obsługa umiejętności |
| **Muchomornik bije magią** | zwykły cios Muchomornika ma `rodzaj = "magiczne"` (klasa Mag) | fioletowe liczby (już działa); ewentualnie pocisk zamiast uderzenia laską |
| pasywki w slotach i broni | brak zdarzeń (działają w liczbach) | opcjonalnie ikony pasywek przy portrecie |
| **nowe zdarzenie `wskrzeszenie`** (propozycja D-094) | zaraz po zdarzeniu, które zbiło życie strony do zera: `kto = cel`, `wartosc` = życie po powrocie, `hp_*` po powrocie, `trwa` 1,5 s | wpis w `Choreografie.ZDARZENIA` i `Obsluga` (np. upadek → powstanie, poświata, napis „WSKRZESZENIE!”); pasek życia z 0 do `wartosc`; walka trwa dalej mimo życia 0 w poprzednim zdarzeniu |

Typów zdarzeń jest 10: dziewięć z v2 i nowe `wskrzeszenie`. Pole `pochloniete` zostało (inne znaczenie: zatrzymane przez tarczę
procentową), żeby kod czytający je dalej działał.

**Doprecyzowanie po kontroli 16/17.11** — kolejności zdarzeń, które odtwarzacz musi przyjąć (wszystkie występują
w prawdziwych dziennikach i przechodzą `Dziennik.sprawdz`):

| Sytuacja | Kolejność w dzienniku | Co odtwarzacz musi zrobić |
|---|---|---|
| śmiertelne tyknięcie i wskrzeszenie | `efekt_tick` (hp 0) → `wskrzeszenie` → dalsze `efekt_tick` tej samej tury → akcja tej strony | nie kończyć walki po `hp = 0`, jeśli następne zdarzenie to `wskrzeszenie`; tura trwa dalej |
| cios, który „zabił”, a cel wstał | `cios`/`krytyk`/`umiejetnosc` (hp 0) → `wskrzeszenie` → `efekt_nalozony` z tego samego ataku (zaklęcie broni, efekt umiejętności) | efekt pojawia się na postaci PO powstaniu |
| zablokowana albo uniknięta umiejętność | `blok` / `unik` z polem `umiejetnosc` i `wartosc` = koszt; pasek many spada | animacja umiejętności + blok/unik; **bez** `efekt_nalozony` (zablokowana umiejętność nie nakłada efektów) |
| ogłuszenie | `efekt_nalozony` (ogluszenie) w turze atakującego → w następnej turze celu: tyknięcia, `utrata_tury`, `efekt_koniec` | ogłuszenie zabiera dokładnie jedną turę; dwie straty tury z rzędu zdarzają się tylko przy skrajnych premiach (najdłuższa seria w próbie: 2) |
| tarcza z umiejętności | `umiejetnosc` (kto = cel) → `efekt_nalozony` (oslona) → osłania przed dokładnie 3 kolejnymi akcjami przeciwnika → `efekt_koniec` na końcu 3. tury nosiciela po rzuceniu | „TARCZA −n” przy każdym trafieniu z `pochloniete` > 0 |
| tyknięcia | na początku tury nosiciela, przed jego akcją; `rodzaj` trucizny i krwawienia = `fizyczne`, podpalenia = `magiczne` | tyknięć nie da się uniknąć ani zablokować — bez napisów „UNIK”/„BLOK” |

Silnik odrzuca też (od kontroli) **nieznane pola wejścia** — serwer (`SerwerWalki2`, `SerwerPotworow`) może podawać tylko
pola z listy `POLA_POSTACI` / `POLA_BRONI` / `POLA_TARCZY` / `POLA_PRZECIWNIKA` (`Statystyki.luau`); `Wzorcowe.luau`
prototypu spełnia to już dziś.

## Testy (polecenia i wyniki)

_Stan przed niezależną kontrolą; wyniki po kontroli: „Testy po kontroli” w sekcji „Niezależna kontrola (16/17.11)”._

| Polecenie | Wynik |
|---|---|
| `python -B -m unittest discover -s tools/walka -p "test_*.py"` | **68/68 OK** (ok. 4,5 min); duża próba 2000 ziaren × 13 poziomów × 3 klasy × 8 przeciwników |
| `python -B tools/walka/zgodnosc_studio.py --offline` | **592/592 identycznych dzienników**, niezmienniki OK, powtarzalność OK, **52/52** złych wejść odrzuconych błędem „Walka: …” |
| `python -B tools/walka/zgodnosc_studio.py --sucho` | złożony kod 106 842 znaków, 592 przypadki, 52 złe wejścia |
| `python -B swiat/las_potwory/sprawdz_luau.py` (pakiet lasu) i reguły 1–2 na plikach silnika | OK (5 plików pakietu); reguły 1–2 (bloki, nawiasy) na 7 plikach silnika: 0 błędów |
| `python -B swiat/test_walki2/testy/test_odtwarzacza.py` | **5/9** — 4 błędy pokrycia, słuszne: brak wyglądu efektu `ogluszenie`, brak obsługi zdarzenia `wskrzeszenie`, zmieniony zbiór umiejętności ze spowolnieniem, a test dzienników zatrzymuje się na pierwszym nieznanym efekcie. Poza pokryciem port odtwarzacza w teście przechodzi wszystkie 2700 dzienników (9/9 typów, 14/14 umiejętności), po jednej poprawce testu — patrz niżej |
| `python -B swiat/test_walki2/testy/test_aktorow.py` | **15/15 OK** |
| `python -B swiat/las_potwory/testy/test_styku.py` | **15/15 OK** |
| `python -B swiat/las_potwory/testy/test_logiki.py` | **17/17 OK** |

Co pilnują nowe testy silnika (`tools/walka/test_walki.py`, poza niezmiennikami z v2): wyrocznia many i rotacji
(odtwarza każdy dziennik z reguł zapisanych w teście: zysk za cios i za obrażenia, spowolnienie, koszt, „zwykły cios
mimo pełnej many” to błąd) na 200 ziarnach każdej pary dużej próby i na wszystkich buildach; wyrocznia statusów
(tyknięcie = ogłoszona siła × stosy, stosy +1 do limitu, ogłuszenie zabiera dokładnie jedną turę, spowolnienie żadnej,
tarcza zatrzymuje tylko, gdy trwa) — obie wyrocznie mają test, że wykrywają zepsute dzienniki; pierwsza umiejętność
w 3.–4. akcji i 1,5–3,5 użycia na walkę ze zwykłym potworem; build pod manę ≥ 1,25× częściej; 3 pasywne = zero
użyć; trucizna z pasywką przekracza limit stosów z danych i nigdy limitu z pasywką; podpalenie od życia celu; krwawienie od ciosu, który je nałożył; obrażenia
w czasie bez Pancerza, odporności i tarczy; tarcza procentowa −X% przez 3 tury; Pancerz z limitem 75% i lepszym
przelicznikiem Wojownika; blok każdej klasy, tarcza tylko Wojownika, wariant 25% i 0%; Zręczność daje mnożnik
krytyka każdej klasie; mana nie jest statystyką i Inteligencja jej nie zmienia; pasywki w slotach i broni (Ognista
różdżka +2 tury, Rozdzieracz); potwór = ten sam wzór co postać (ta sama klasa i punkty → te same wartości); buildy
45–55% z wzorcową swojej klasy (potwór lepszy / gorszy o ≥ 3 pp — tylko tam, gdzie to dziś prawda, `BUILDY_ROZNE`); każda statystyka coś daje każdej klasie; dokładnie te same
dzienniki Luau (interpreter) i Pythona na wszystkich wzorcach; wskrzeszenie (D-094): najwyżej raz na walkę, tylko
zaraz po zbiciu życia do zera, także po śmiertelnym tyknięciu, dokładnie 25% życia, tylko ze slotu (premia i broń
odrzucone), deterministyczne, a `Dziennik.sprawdz` odrzuca drugie wskrzeszenie, wskrzeszenie bez nokautu i złe życie.

**Zmiana w teście prototypu** (`swiat/test_walki2/testy/test_odtwarzacza.py`, funkcja `odtworz` — port księgowości
odtwarzacza): sprawdzenie „tarcza pochłonęła więcej, niż odtwarzacz miał w zapasie” przyjmuje teraz też tarczę
procentową (typ `oslona`, bez zapasu) — w v3 `pochloniete` to to, co zatrzymała tarcza procentowa. To konieczne
i bezpieczne: prawdziwy odtwarzacz (`Sesja:pochlon`) przy braku zapasu niczego nie odejmuje, a napis „TARCZA −n”
dalej ma sens. Testów pokrycia nie osłabiałem — pokazują, czego odtwarzaczowi brakuje.

## Czego nie udało się zrobić (wprost)

- **Buildy nie mają w lesie wyraźnego „swojego” i „nie swojego” potwora.** Wszystkie 9 buildów jest równych
  wzorcowej swojej klasy (**48,2–54,6%**), ale warunek „potwór, na którego wyraźnie lepszy (≥ 3 pp) i na którego
  wyraźnie gorszy” spełniają tylko: **Wojownik pod Pancerz i blok** (5. i 10. poziom: Wilk i Troll +6…+10, Strażnik
  −7…−14) i **Mag pod manę** na 5. poziomie. Build trucizny i build uniku na 10. poziomie są prawie płaskie (±1–3 pp).
  Powód: potwory lasu po wyrównaniu klas są do siebie podobne (żaden nie jest skrajnie opancerzony, skrajnie zwinny
  albo skrajnie magiczny). Test pilnuje warunku tylko dla tych trzech (`BUILDY_ROZNE` w `test_walki.py`, jawnie
  opisane). Do zrobienia: potwory o ostrzejszych cechach w kolejnych biomach albo buildy o mocniejszym charakterze.
- **Build pod manę nie używa umiejętności 2× częściej**, tylko 1,3–1,6× (pasek kończy się na 100, więc umiejętność
  pada najwyżej co drugą akcję). Szybsza mana jest za to warta tak dużo, że build płaci za nią 20–26% puli punktów.
- **„3 pasywne” są słabe** (37–48% z potworami), a zwykłe pasywki (Kolos, Oko łowcy, Skupiona magia) musiały zostać
  słabe, bo przy jednym pasku 2. i 3. aktywna umiejętność są warte mało — wybór 3.
- **Ziarna kontrolne:** różnica klas przy Strażniku Gaju na poziomach 1–6 dochodzi do 6–8 pp (Wojownik lepszy; na
  ziarnach testu 6,8 pp na 1. poziomie), pojedynki do 55,3%. Na poziomie, na którym gracz spotyka strażnika (ok. 10–11),
  różnica to ok. 4 pp.
- **Prototyp w Studio** nie umie dziennika v3 (ogłuszenie, wskrzeszenie, paski many, stosy, blok innych klas) —
  plików budowanych do Studio nie wolno było zmieniać; lista wyżej. Jego testy pokrycia nie przechodzą (4 błędy,
  słusznie).
- **Luau nie był uruchomiony w Roblox Studio** — tylko w interpreterze offline.
- Rejestracji pracy w panelu (`praca.py start`) nie robiłem — zakaz zmian w `panel/` i danych lokalnych panelu.

## Co niesprawdzone

- **Luau nie był uruchomiony w Roblox Studio** (praca offline). Sprawdzone: (1) `zgodnosc_studio.py --offline` —
  dokładnie ten sam złożony kod, który poszedłby do Studio, wykonany w interpreterze `tools/walka/luau_mini.py`:
  **592/592 identycznych dzienników**, niezmienniki OK, powtarzalność OK, **52/52** złych wejść odrzuconych błędem „Walka: …”; (2) bilans bloków i nawiasów dwoma narzędziami (`test_walki.py`, `swiat/las_potwory/sprawdz_luau.py`).
  Interpreter to podzbiór Luau napisany w Pythonie — nie sprawdza kompilatora Luau, typów ani zachowania Studio.
  **Przed użyciem w grze:** `python -B tools/walka/zgodnosc_studio.py --studio <id>` (tryb Edit, tylko odczyt).
- **Prototyp w Studio (`swiat/test_walki2`) nie umie jeszcze dziennika v3**: brak wyglądu ogłuszenia, pasków many,
  stosów, klipów bloku dla Maga, Zwiadowcy i potworów (lista wyżej). Testy pokrycia prototypu to wykazują
  (`test_odtwarzacza.py`: 3 błędy pokrycia — patrz „Testy”). Pakiet `swiat/las_potwory` liczy walki tym samym
  silnikiem i jego testy przechodzą, ale odtwarza je odtwarzacz prototypu — ten sam brak.
- Balans liczony na **wzorcowych** postaciach i buildach z `tools/walka/wzorcowe.py`. Koszt buildów (−10% puli za
  przedmioty z premią) to założenie modelu, a nie zasada; prawdziwe przedmioty i drzewko mogą to zmienić.
- **Model tempa** to model: prosta polityka gracza, czasy dojścia i odrodzenia to parametry, a biomy 2–7 liczone są
  na potworach lasu przeskalowanych do poziomu gracza (zastępczo). Prawdziwe potwory dalszych biomów i ich trudność
  trzeba będzie stroić osobno. Nie sprawdzono czasu na prawdziwym telefonie ani odbioru przez człowieka.
- Wysokie poziomy (30–100) sprawdzone tylko na potworach lasu przeskalowanych do tych poziomów i na pojedynkach klas.
- Liczby dobrał automat strojący (stąd np. 1,172) — zaokrąglenie wymaga przeliczenia tabel.

## Niezależna kontrola (16/17.11)

Drugi agent, który nie pisał silnika, szukał błędów tak, jakby chciał wykazać, że praca jest zła: przeczytał oba porty
linia po linii (Python ↔ Luau), uruchomił 25 celowo zepsutych wersji silnika (testy mutacyjne w kopii poza repo),
próby brzegowe, przeszukanie ok. 4,5 tys. zestawów (sloty × pasywka broni × zaklęcie, poziomy 5 i 10) i tabele na
**innych ziarnach** niż testy (1–2000) i raport (50001–52000): 110001+, 160001+, 200001–203000, 300001+, 600001+,
700001+, 800001+, 900001+. Liczby niżej to wyniki tych przebiegów (pojedynek z wzorcową = średnio z obu miejsc).

### Znalezione błędy i co z nimi zrobiono

| # | Waga | Co było źle | Minimalny przykład | Co zrobione |
|---:|---|---|---|---|
| 1 | **ważny** (balans) | pasywki many w slocie (Bitewny rytm, Przypływ adrenaliny, Przepływ many: +30–35% zysku many i +35 many na start) były za mocne jak na DARMOWY wybór slotu; tabela (g) sprawdzała tylko 6 wybranych zestawów, a build pod manę płacił za te pasywki 20–26% puli, więc nikt tego nie widział | 10. poz., ziarna 300001–301000 (1000 walk z każdej strony): Mag [Kula ognia, Bariera, Przepływ many] **66,5%** z wzorcową, Wojownik [Potężne cięcie, Mur tarczy, Bitewny rytm] **64,8%**, Zwiadowca [Uderzenie z góry, Zwinność, Przypływ adrenaliny] **63,5%**; 5. poz. Mag [Kula ognia, Przepływ many] **63,0%** | dane: **+10% zysku i +15 many na start** (wszystkie trzy). Model buildu pod manę (`wzorcowe.py`): tyle many co przedtem, ale z przedmiotów (PREMIE_MANY: zysk 0,35 → 0,60, start 50 → 70), KOSZT_MANY Wojownika 0,22 → 0,225. Nowy test `TestZestawySlotow` (przeszukanie wszystkich zestawów, próg 63%; na starych danych pada: 66,8%) i część (l) w `balans.py`. Po poprawce najlepszy darmowy zestaw: tabela (l) |
| 2 | **ważny** (balans) | Kumulowanie trucizny dawało +14 pp szansy KAŻDEGO zaklęcia broni — także ognia; z Barierą na początku rotacji (dłuższa walka) i zaklęciem łamało równowagę nawet przy koszcie 10% puli za zaklęcie, jak w modelu | 10. poz., ziarna 800001+ (800 walk): Mag [Bariera, Kula ognia, Kumulowanie trucizny] + Jadowity kostur + zaklęcie trucizny, pula −10% → **65,3%**; to samo z Ognistą różdżką i zaklęciem OGNIA → **64,6%** | dane: Kumulowanie trucizny **bez szansy zaklęcia** (limit stosów +4 i siła +43% zostają). Ten sam zestaw: 57,7%; build trucizny z modelu 46,7–50,0% (tabela e) |
| 3 | **ważny** (testy) | 6 z 25 celowo zepsutych reguł przechodziło WSZYSTKIE testy | blok zeruje cios (zostaje dolna granica 1); tarcza krócej albo dłużej o turę; krytyk przed blokiem (kolejność z v2); zablokowana umiejętność nakłada efekty; tarcza bez limitu z danych | nowe testy: `test_blok_zmniejsza_obrazenia_do_czesci_ciosu_a_nie_zeruje`, `test_kolejnosc_rzutu_unik_blok_krytyk`, limit tarczy w `test_tarcza_procentowa_trzy_tury`; wyrocznia `sprawdz_przebieg_efektow` sprawdza teraz czas KAŻDEGO efektu w turach nosiciela (także tarczy, spowolnienia, zdarcia), czas ogłoszony = czas z danych i to, że efekt na przeciwnika pada tylko po trafieniu. Teraz **25/25** mutacji wykrytych |
| 4 | **ważny** (walidacja) | nieznane pola wejścia przechodziły po cichu — postać walczyła bez przedmiotów albo slotów i nikt by tego nie zauważył | `{"premia": {"cios": 0.5}}` (zamiast `premie`), `bron.pasywki`, `tarcza.pancerz`, `{"potwor": …, "premie": …}`, `"mana": 100` w postaci — wszystkie dawały zwykłą walkę bez błędu | zamknięte listy pól w obu portach (`sprawdz_klucze` / `Statystyki.sprawdzKlucze`, `POLA_POSTACI`, `POLA_BRONI`, `POLA_TARCZY`, `POLA_PRZECIWNIKA`); 8 nowych złych wejść w `wzorce.py` (także NaN w premii, umiejętności jako liczba, nazwa jako liczba) — **60/60** odrzuconych w obu portach; test, że listy są takie same w Pythonie i Luau |
| 5 | drobny (zgodność Python ↔ Luau) | bezpiecznik porównywał hp × życie na dokładnych liczbach całkowitych Pythona, a Luau na double — przy życiu rzędu 10⁸–10⁹ (osiągalne z dozwolonymi wejściami) znak porównania mógł być inny | życie 1000000007 / 1000000009, hp po walce 999999951 / 999999953: dokładnie 999999951 × 1000000009 < 999999953 × 1000000007 (o 112), w double oba iloczyny równe → Luau „wygrana”, Python „przegrana” | `float()` w `silnik.py` i `dziennik.py`; test na tym przykładzie (Python i `Dziennik.luau` w interpreterze dają to samo) |
| 6 | drobny (test) | test „iteracja tylko po listach” przepuszczał też SŁOWNIKI (`Dane.umiejetnosci`, `p.statystyki` pasowały do wzorca) | — | dokładna lista dozwolonych źródeł pętli |
| 7 | drobny (dokument) | nieścisłości | „nabijanie zawsze przegrywa” — a tabela (h) miała Maga z 60% Kondycji 70,4% / 69,7%; „1,3–1,6×” — tabela (d) miała 1,19× (Wojownik, troll); „3 błędy pokrycia” obok „4 błędów”; README „części a–j” (jest a–k); nagłówek `Dane.luau` „silnika walki v2” | poprawione w tym pliku, README i `generuj_dane.py` |

### Co sprawdziłem i jest dobrze

- **Porty linia po linii** (miejsca nowych reguł: mana, rotacja, blok, tarcza, statusy, wskrzeszenie, modyfikatory):
  te same wzory w tej samej kolejności działań (ta sama kolejność mnożeń i sumowania liczb zmiennoprzecinkowych),
  `math.floor(x + 0.5)` w obu, rotacja `nastepna` 0-indeksowana w Pythonie i 1-indeksowana w Luau daje te same sloty,
  suma modyfikatorów po LIŚCIE z danych, iteracja w regułach walki tylko po listach (pętle po słownikach są wyłącznie
  w walidacji). Interpreter: 592/592 identycznych dzienników po wszystkich poprawkach.
- **Reguły brzegowe** (próby poza testami): walka zawsze kończy się nokautem dokładnie jednej strony (remis w jednej
  turze niemożliwy: tyknięcia ranią tylko nosiciela, akcja tylko cel); 15 360 walk wzorcowych i buildów na poziomach
  1/3/10/30 z każdym przeciwnikiem bez błędu dziennika i bez bezpiecznika, 6912 walk z rozszerzoną wyrocznią efektów; bezpiecznik działa (1000 tur w lustrze z ogromnym życiem i Pancerzem — wejście
  dozwolone, wynik poprawny); mana zawsze 0..100 (pilnują tego `Dziennik.sprawdz` i wyrocznia); 0 aktywnych = zero
  użyć, pasek się marnuje; ogłuszenie nigdy w pętli — najdłuższa seria straconych tur: 1 przy potworach (Strażnik
  zabiera 13% tur Wojownikowi i Zwiadowcy, 17–18% Magowi), 2 przy skrajnych premiach (zysk many +300%, koszt −60%,
  pełna mana na start, Miażdżący cios — gracz musi przecież atakować, żeby ładować manę); stosy trucizny nigdy ponad
  limit z danych + modyfikator; podpalenie strażnika ograniczone 60% ciosu atakującego; wskrzeszenie raz na walkę,
  także po śmiertelnym tyknięciu, z tarczą działa normalnie; kolejność rzutów nie zależy od strony (pasywki nie
  dokładają rzutów).
- **Testy `swiat/`:** `swiat/las_potwory/testy/test_styku.py` 15/15 OK, `test_logiki.py` 17/17 OK,
  `swiat/test_walki2/testy/test_aktorow.py` 15/15 OK, `test_odtwarzacza.py` **5/9** — 4 błędy to WYŁĄCZNIE pokrycie
  nowego dziennika w odtwarzaczu: brak wyglądu efektu `ogluszenie` (2 testy: lista efektów i test dzienników, który
  zatrzymuje się na pierwszym nieznanym efekcie), brak obsługi zdarzenia `wskrzeszenie`, a `WYGLAD_SPOWOLNIENIA` ma
  jeszcze Uścisk korzeni, Miażdżący cios i Ogłuszające uderzenie (dziś ogłuszają, nie spowalniają). Sprawdzone osobno:
  port księgowości odtwarzacza z testu (`odtworz`) przechodzi wszystkie 2700 dzienników testu bez błędu (9 typów
  zdarzeń, 14/14 umiejętności). **Uwaga dla następnego etapu:** ta księgowość nie zna `wskrzeszenie` — pasek życia
  nie wraca z 0 (w próbie testu wskrzeszenia nie ma, bo postacie wzorcowe go nie mają).

### Balans na innych ziarnach (po poprawkach)

- **Różnica klas przy tym samym potworze** (ziarna 200001–203000, 3000 walk na komórkę): najwyżej **7,9 pp —
  Strażnik Gaju na 1. poziomie** (Wojownik 37,4 / Zwiadowca 29,5 / Mag 30,5), dalej Strażnik na 3. i 4. poziomie
  6,3 i 6,2 pp; 60 z 65 zestawień ≤ 5 pp. **Twarda granica 7 pp jest przekroczona** (na ziarnach kontrolnych raportu
  też: 8,0); test przechodzi, bo na ziarnach 1–2000 wyszło 6,8. Przyczyna: na 1.–4. poziomie (jeden slot) Wojownik
  blokuje tarczą 33% Uścisków korzeni (zablokowany = bez ogłuszenia), Zwiadowca ich unika, a Mag traci najwięcej tur.
  Poprawka danymi zmieniłaby Strażnika i przeliczenie wszystkich tabel i tempa — zostawione ludziom (niżej).
- **Pojedynki klas:** 46,4–54,9% — w celu.
- **Najlepszy DARMOWY zestaw slotów** (tabela l, ziarna 300001+; przeszukanie wszystkich zestawów bez broni,
  zaklęcia i premii): 5. poz. 54,9–56,2%; 10. poz. Wojownik 58,3%, Zwiadowca 56,8%, **Mag 59,9%** [Kula ognia,
  Przepływ many, Magiczny pocisk] (na 1500 walk z innych ziaren 60,4%; 15. poz. 60,6%). To już nie pasywka many
  (z +5% zysku wychodzi to samo), tylko zasada: **jedna najlepsza aktywna + pasywki bije trzy aktywne**, bo rotacja
  rozcieńcza najlepszą umiejętność słabszymi (wybór 3), oraz **kolejność**: te same trzy aktywne co wzorcowa, tylko
  z tarczą na początku rotacji — Wojownik (Kamienna skóra pierwsza) 57,4%, Zwiadowca (Skupienie pierwsze) 53,6%, Mag
  (Bariera pierwsza) 48,3% (wybór 4). Granica 60% bez zapasu.
- **Z zaklęciem broni** (model: zaklęcie kosztuje 10% puli): najlepsze zestawy 59,9–63,1% (Mag [Bariera, Kula ognia,
  Magiczny pocisk] + Ognista różdżka + zaklęcie ognia 63,1%; Wojownik [Potężne cięcie, Kolos, Mur tarczy] + Miecz
  runiczny + zaklęcie ognia 62,8%). Samo zaklęcie bez kosztu: 52–59,5% (Wojownik z zaklęciem ognia 59,5%), z kosztem
  42,5–50%. Ognista różdżka nie ma wady (+2 tury podpalenia, przykład z sesji): z wzorcową 54,8%.
- **Najsilniejszy znaleziony zestaw w ogóle** (po poprawkach, ziarna 310001+, 1000 walk z każdej strony): Mag 10. poz.
  [Bariera, Kula ognia, Wskrzeszenie] + Ognista różdżka + zaklęcie ognia (bez kosztu) — **89,8%** z wzorcową;
  Zwiadowca [Uderzenie z góry, Zwinność, Wskrzeszenie] + Łuk wiatru + ogień 86,2%; Wojownik [Kamienna skóra, Potężne
  cięcie, Wskrzeszenie] + Miecz runiczny + ogień 85,4% (przed poprawką pasywek many najmocniejszy Wojownik miał 89,1%).
  Samo wskrzeszenie zamiast 3. aktywnej: Wojownik **74,8%** z wzorcową, +14,8 pp z potworami — tyle, co w tabeli (k).
- **Buildy z modelu** (tabela e): 46,7–53,6% z wzorcową; pod manę używa umiejętności **1,2–1,7× częściej na walkę**,
  ale **1,6–2,0× częściej na akcję** (walki buildu są krótsze) — cel „ok. 2×” jest spełniony tylko w tym drugim sensie.
- **Nabijanie jednej statystyki** (ziarna 160001+, 45% i 60% puli): zawsze gorzej niż rozkład wzorcowy — **oprócz
  Maga i Kondycji**: 45% Kondycji +3,2 pp z potworami i 53,2% z wzorcową (5. poz.), +1,9 pp / 52,2% (10. poz.);
  60% Kondycji ±0 pp / 49,7%. Rozkład wzorcowy Maga (22% Kondycji) nie jest najlepszy; Kondycja jest dla Maga
  najcenniejszą statystyką (tabela c).

### Miejsca, w których prawdziwy Luau może dać inny wynik niż interpreter `luau_mini.py`

Interpreter liczy na tych samych liczbach double w tej samej kolejności, więc **wyniki walk** (podpisy dzienników)
są wiarygodne. Może natomiast ukryć:
1. **Kolejność iteracji po słownikach** — `luau_mini` iteruje część słownikową w kolejności wstawiania, Luau
   w nieokreślonej. W silniku dotyczy to tylko walidacji (`sprawdzPremie`, `sprawdzModyfikatory`, `sprawdzKlucze`,
   pętle po `st` i `um`, `Dziennik.sprawdz` po łupie): przy KILKU złych polach naraz Luau może zgłosić inne pole niż
   Python (inny tekst błędu, ten sam prefiks „Walka: ”). Na wynik walki nie wpływa (pilnuje test pętli).
2. **`#` tabeli z dziurami** — interpreter liczy pierwszą granicę, Luau może zwrócić inną; walidacja odrzuca taką
   listę przy każdej z możliwych granic (sprawdzone na `{[1]=…, [3]=…}`).
3. **`tostring` liczby niecałkowitej** — interpreter `%.14g` (jak Lua 5.1), Luau najkrótszy zapis (np. 0.1+0.2 →
   0.30000000000000004) — tylko w tekstach błędów (`Dziennik.sprawdz`: „oczekiwano t”).
4. **`string.format("%d", x)` z niecałkowitym x** — interpreter rzuca błąd; w podpisie wszystkie pola są całkowite.
5. **Iteracja po tabeli zmienianej w pętli** — interpreter bierze klucze na starcie pętli, Luau iteruje „na żywo”;
   silnik nie zmienia iterowanych tabel (`koniecTury` buduje nową listę).
6. **Kompilator i typy** — interpreter nie kompiluje Luau: nie sprawdza limitów (200 zmiennych lokalnych, 255
   upvalue, stałych), adnotacji typów (pomija je), trybu `--!strict`; przyjmuje też `continue` jako słowo kluczowe.
7. **Środowisko Studio** — `HttpService:JSONDecode/JSONEncode` i `task.wait()` w trybie Edit są podstawione;
   w Studio mogą się zachować inaczej (np. limit czasu `execute_luau`).
8. **Arytmetyka na napisach** — Luau zamienia napis na liczbę („10” + 1 = 11), interpreter rzuca błąd; silnik
   sprawdza typ (`Los.liczba`) przed każdym działaniem na wejściu, więc różnicy nie widać.
9. **Liczby powyżej 2^53** — poza bezpiecznikiem (poprawione, pkt 5) największe wartości przy skrajnych dozwolonych
   wejściach to ok. 10¹¹ (obrażenia umiejętności), więc są dokładne w obu portach.

### Ocena testów (przed kontrolą)

- **Mocne:** wyrocznie many i statusów są niezależne od kodu silnika i wykrywają zepsute dzienniki; `Dziennik.sprawdz`
  pilnuje życia, many, czasu i wskrzeszenia; 19 z 25 mutacji złapanych od razu.
- **Słabe:** (a) próg buildu pod manę „≥ 1,25×” poluzowany pod wynik (cel 2×); (b) `BUILDY_ROZNE` — wyjątek wpisany
  na sztywno, warunek „swój / nie swój potwór” sprawdzany tylko dla 3 z 18 buildów (opisane uczciwie); (c) koszty
  buildów w `wzorcowe.py` (KOSZT_MANY 20–26% puli) są dobrane tak, żeby test 45–55% przechodził — test buildu pod
  manę nie może więc wykryć zbyt mocnych przedmiotów many; (d) równość klas sprawdzana na jednych ziarnach 1–2000,
  przy wyniku 6,8 pp tuż pod granicą 7 — na innych ziarnach 7,9 i 8,0; (e) wyrocznia many korzysta z wartości
  bojowych liczonych przez silnik (`wartosci_postaci`), więc nie wykryje błędu we wzorze `zysk_many`; (f) tabela (g)
  i testy slotów nie przeszukiwały zestawów (stąd błąd 1); (g) brak testów: blok jako część ciosu, kolejność rzutu,
  czas tarczy, efekty po bloku, limit tarczy (stąd błąd 3).
- **Po kontroli** testów jest 73 (było 68); wszystkie przechodzą — wynik w tabeli „Testy po kontroli”. Jeden stary
  test zmieniony: `test_trucizna_kumuluje_stosy_do_limitu` żądał, żeby w 100 walkach trucizna przekroczyła 5 stosów —
  po poprawce danych to rzadkie (punkt 10 niżej), więc limit stosów sprawdza teraz wprost (kolejne nałożenia: 1, 2, …,
  9, 9, 9 z pasywką i 1…5, 5 bez niej) plus „nigdy ponad limit” na 300 walkach.

### Co zostaje ludziom (do decyzji — liczby, nie rozstrzygałem)

1. **Strażnik na 1.–4. poziomie łamie twardą granicę 7 pp** (7,9 pp na świeżych ziarnach). Opcje: granica liczy się
   tylko od poziomu, na którym gracz spotyka strażnika (brama na ok. 10. poz.: tam 3,5–4 pp); albo przestroić
   Strażnika (np. Uścisk korzeni mniej zależny od bloku) i przeliczyć wszystko.
2. **Wskrzeszenie 25% (D-094) = 74–76% z wzorcową**, z zaklęciem i dobrymi slotami do 89–90%. To decyzja właścicieli
   (legenda ma być mocna); uczciwa wymiana „slot za slot” wypada przy 1 HP–5% życia (tabela k).
3. **Jedna aktywna + pasywki i kolejność rotacji** (wybory 3 i 4): najlepszy darmowy zestaw ok. 60% z wzorcową
   (Mag: Kula ognia + 2 pasywki), tarcza na początku rotacji: Wojownik +7 pp, Zwiadowca +4 pp, Mag −2 pp. Opcje: większa premia za kolejne aktywne
   (`mana_premia_za_aktywna`), „mądra” rotacja albo słabsze pasywki — każda wymaga przeliczenia tabel.
4. **Koszt zaklęcia broni i pasywek broni** (wybór 13): zaklęcie bez kosztu +5…+10 pp (Wojownik z ogniem 59,5%);
   Ognista różdżka bez wady (54,8%). Z kosztem 10% puli najlepsze zestawy z zaklęciem 60–63%.
5. **Pasywki many po osłabieniu (+10%, +15 na start)** — wartości moje, do zatwierdzenia albo zmiany (warunek: żaden
   darmowy zestaw nie bije wzorcowej wyraźnie; test `TestZestawySlotow` ma próg 63%).
6. **Build pod manę: 2×** — na akcję jest ok. 1,6–2,0×, na walkę 1,2–1,7× (walki krótsze). Czy „2×” liczyć na akcję?
7. **Łączna redukcja obrażeń** — Pancerz (najwyżej 75%) × blok (przechodzi 25%) × tarcza (najwyżej 75%) daje
   najwyżej ok. 98,4% redukcji jednego trafienia (zawsze ≥ 1). Wymaganie „Pancerz nigdy nie zeruje” jest spełnione,
   ale czy taka suma jest w porządku?
8. **Granice premii z przedmiotów** w danych są szerokie (np. obrażenia +300%, zysk many +300%, zdarcie 90% Pancerza
   wroga) — silnik ich nie ogranicza bardziej; trzeba je trzymać w projekcie przedmiotów.
9. **Mag i Kondycja** — rozkład wzorcowy Maga ma za mało Kondycji (45% Kondycji wygrywa 53% z wzorcową).
10. **Kumulowanie trucizny — czy ma być „kumulowanie”?** Po zabraniu pasywce szansy zaklęcia (błąd 2) build trucizny
    ma 58% szansy zaklęcia przy zwykłym trafieniu (umiejętności zaklęcia nie wyzwalają), a trucizna trwa 4 tury: ponad 5 stosów zdarza się w ok. 0,5% walk ze
    strażnikiem (mediana 2 stosy), więc +4 do limitu prawie nie działa — pasywka działa głównie przez +43% siły.
    Opcja: osobny modyfikator szansy tylko dla trucizny (zmiana kodu w obu portach) albo dłuższa trucizna tylko
    z tej pasywki — każda wymaga sprawdzenia, czy zestaw z Barierą na początku nie wraca powyżej 60%.

### Czego NIE sprawdziłem (wprost)

- **Prawdziwego Luau w Roblox Studio** — praca offline (zakaz Studio); sprawdzenie tylko interpreterem i statycznie.
  Przed użyciem w grze: `python -B tools/walka/zgodnosc_studio.py --studio <id>`.
- Kodu odtwarzacza i plików budowanych do Studio (`swiat/test_walki2`, `swiat/las_potwory`) — poza uruchomieniem
  ich testów; zakres zapisu tego nie obejmował.
- Modelu tempa (`tempo.py`) poza przeczytaniem: model biomów 2–7 jest z definicji zgodny z planem 600 min (liczy,
  na jakim poziomie gracz kończy zaplanowany czas) — „10 godzin do 8. biomu” jest więc założeniem, nie wynikiem.
  Las ~30 min nie zależy od zmienionych pasywek (gracz modelu to postać wzorcowa bez pasywek).
- Przeszukania buildów na poziomach 15–100 z zaklęciami i wskrzeszeniem (tylko zestawy slotów do 15. poz.), rozkładów
  punktów razem z zestawami slotów (osobno: rozkłady 45/60% jednej statystyki) i premii z przedmiotów innych niż
  w modelu (premie mają szerokie granice, punkt 8).

### Testy po kontroli

| Polecenie | Wynik |
|---|---|
| `python -B -m unittest discover -s tools/walka -p "test_*.py"` | **73/73 OK** (ok. 4,8 min; było 68 testów) |
| `python -B tools/walka/zgodnosc_studio.py --offline` | 592/592 identycznych dzienników, niezmienniki OK, powtarzalność OK, **60/60** złych wejść odrzuconych |
| `python -B tools/walka/zgodnosc_studio.py --sucho` | złożony kod 109 252 znaki, 592 przypadki, 60 złych wejść |
| `python -B swiat/las_potwory/sprawdz_luau.py` | 5 plików pakietu lasu: OK |
| `python -B swiat/las_potwory/sprawdz_luau.py <7 plików silnika>` | reguły 1–2 (bloki, nawiasy): 0 błędów (także w teście `test_bilans_blokow_drugim_narzedziem`); reguła 3 („strażnik Studio” na początku) zgłasza 7 plików — nie dotyczy modułów silnika (czyste ModuleScript, bez kodu uruchamianego przy wczytaniu) |
| `swiat/las_potwory/testy/test_styku.py`, `test_logiki.py` | 15/15 OK, 17/17 OK |
| `swiat/test_walki2/testy/test_aktorow.py`, `test_odtwarzacza.py` | 15/15 OK; 5/9 (4 błędy pokrycia nowego dziennika — wyżej). Uwaga: w trakcie kontroli inny agent przerabiał `swiat/test_walki2/zrodla` (odtwarzacz v3); przy ponownym uruchomieniu na końcu `test_odtwarzacza.py` nie wczytuje się („brak tabeli Ch.WYGLAD_SPOWOLNIENIA w Choreografie.luau”) — to stan jego niedokończonej pracy, nie tej paczki |
| testy mutacyjne (25 zepsutych reguł, kopia poza repo) | przed kontrolą 19/25 wykrytych, po kontroli **25/25** |

Zmienione pliki: `tools/walka/{dane_walki.json, silnik.py, dziennik.py, wzorcowe.py, wzorce.py, wzorce.json,
balans.py, generuj_dane.py, test_walki.py, zgodnosc_studio.py, README.md, ZMIANY_SESJA_1611.md}`,
`src/server/Walka/{Dane.luau, Statystyki.luau, Przeciwnicy.luau}`. Bez zmian: reguły walki w `Umiejetnosci.luau`
i `Silnik.luau` (nie znalazłem w nich błędu), `luau_mini.py`, `tempo.py`, `Dziennik.luau`.

## Tabele balansu — pełny wynik

`python -B tools/walka/balans.py` (2000 ziaren na parę; części c–k: 1000). Kontrola na innych ziarnach: `--start 50001` (wynik w tabeli na górze).

**Wniosek (a, b):** największa różnica klas przy tym samym potworze 6,8 pp (Strażnik Gaju, poziom 1; cel ≤ 5, granica 7); w celu 63 z 65 zestawień. Pojedynki klasa na klasę 45,9%–54,5% (cel 45–55%).

Każda komórka: 2000 walk na tych samych ziarnach 1–2000. Pula punktów: 30 na 1. poziomie + 10 za każdy kolejny. Sloty umiejętności: 1 (poziom 1–4), 2 (5–9), 3 (od 10). Tura = ruch jednej strony.

### (a) Różnica klas przy tym samym potworze — wszystkie poziomy

Komórka: największa różnica procentu wygranych między klasami (pp), w nawiasie Wojownik / Zwiadowca / Mag.

| Poziom | Leśny Slime | Cierniowy Wilk | Muchomornik | Leśny Troll | Strażnik Gaju |
|---:|---|---|---|---|---|
| 1 | 2,4 (85 / 83 / 86) | 3,5 (89 / 86 / 87) | 1,4 (90 / 90 / 91) | 3,7 (51 / 51 / 47) | 6,8 (37 / 30 / 31) |
| 2 | 2,4 (83 / 83 / 85) | 3,2 (87 / 84 / 85) | 1,7 (89 / 90 / 90) | 4,0 (51 / 51 / 47) | 4,9 (34 / 29 / 31) |
| 3 | 2,0 (83 / 83 / 85) | 3,7 (91 / 87 / 87) | 2,5 (86 / 88 / 89) | 1,9 (52 / 52 / 50) | 4,1 (36 / 32 / 32) |
| 4 | 2,5 (83 / 82 / 85) | 3,9 (88 / 84 / 85) | 2,1 (86 / 87 / 88) | 0,4 (53 / 53 / 53) | 5,4 (35 / 30 / 31) |
| 5 | 0,7 (84 / 84 / 84) | 4,0 (89 / 87 / 85) | 1,7 (89 / 90 / 90) | 3,4 (58 / 56 / 54) | 2,5 (33 / 30 / 32) |
| 6 | 0,6 (84 / 84 / 84) | 3,5 (89 / 89 / 86) | 1,2 (88 / 90 / 89) | 4,2 (56 / 54 / 52) | 3,8 (35 / 32 / 34) |
| 7 | 1,7 (87 / 87 / 85) | 3,7 (89 / 88 / 86) | 1,5 (88 / 88 / 89) | 3,0 (55 / 54 / 52) | 3,1 (36 / 33 / 36) |
| 8 | 1,8 (86 / 87 / 85) | 3,0 (87 / 87 / 84) | 1,5 (88 / 88 / 89) | 2,8 (58 / 56 / 55) | 3,2 (37 / 34 / 36) |
| 9 | 2,0 (87 / 88 / 86) | 3,6 (89 / 88 / 85) | 2,2 (87 / 88 / 89) | 2,2 (55 / 55 / 53) | 2,6 (35 / 33 / 35) |
| 10 | 2,9 (88 / 85 / 86) | 2,9 (88 / 86 / 85) | 3,2 (86 / 87 / 90) | 4,0 (57 / 54 / 53) | 3,5 (36 / 38 / 35) |
| 12 | 3,0 (88 / 84 / 86) | 2,3 (87 / 86 / 85) | 3,5 (86 / 86 / 89) | 3,2 (58 / 55 / 56) | 2,7 (36 / 38 / 35) |
| 15 | 2,2 (87 / 85 / 86) | 2,8 (88 / 86 / 85) | 3,7 (85 / 86 / 89) | 3,2 (57 / 54 / 56) | 2,7 (36 / 38 / 35) |
| 20 | 3,1 (87 / 84 / 86) | 3,3 (89 / 87 / 86) | 2,8 (87 / 87 / 90) | 3,3 (56 / 53 / 55) | 2,8 (37 / 38 / 35) |

### (a) Klasa przeciw potworom lasu — szczegóły

**Poziom 1** (potwór tego samego poziomu)

| Przeciwnik | Ranga | Wojownik | Zwiadowca | Mag | Różnica | Tury: najkrótsza–mediana–najdłuższa | Średni czas | Umiejętności na walkę |
|---|---|---:|---:|---:|---:|---|---:|---:|
| Leśny Slime | zwykły | 85,2% | 83,5% | 85,8% | 2,4 pp | 5–14–43 | 24,2 s | 2,2 |
| Cierniowy Wilk | zwykły | 89,0% | 85,5% | 86,7% | 3,5 pp | 3–10–38 | 19,0 s | 1,5 |
| Muchomornik | zwykły | 89,8% | 89,8% | 91,2% | 1,4 pp | 5–11–30 | 19,1 s | 1,5 |
| Leśny Troll | rzadki | 50,6% | 51,0% | 47,2% | 3,7 pp | 5–15–41 | 26,2 s | 2,0 |
| Strażnik Gaju | strażnik | 36,9% | 30,1% | 31,4% | 6,8 pp | 9–23–50 | 37,6 s | 2,8 |

**Poziom 5** (potwór tego samego poziomu)

| Przeciwnik | Ranga | Wojownik | Zwiadowca | Mag | Różnica | Tury: najkrótsza–mediana–najdłuższa | Średni czas | Umiejętności na walkę |
|---|---|---:|---:|---:|---:|---|---:|---:|
| Leśny Slime | zwykły | 83,7% | 84,3% | 83,7% | 0,7 pp | 4–16–43 | 25,3 s | 2,6 |
| Cierniowy Wilk | zwykły | 88,8% | 87,5% | 84,8% | 4,0 pp | 4–10–42 | 19,3 s | 1,8 |
| Muchomornik | zwykły | 88,5% | 90,0% | 90,2% | 1,7 pp | 4–11–29 | 19,5 s | 1,7 |
| Leśny Troll | rzadki | 57,6% | 55,7% | 54,2% | 3,4 pp | 5–17–40 | 28,7 s | 2,6 |
| Strażnik Gaju | strażnik | 32,9% | 30,4% | 32,5% | 2,5 pp | 9–23–50 | 39,8 s | 3,4 |

**Poziom 10** (potwór tego samego poziomu)

| Przeciwnik | Ranga | Wojownik | Zwiadowca | Mag | Różnica | Tury: najkrótsza–mediana–najdłuższa | Średni czas | Umiejętności na walkę |
|---|---|---:|---:|---:|---:|---|---:|---:|
| Leśny Slime | zwykły | 87,8% | 84,9% | 86,5% | 2,9 pp | 4–19–49 | 27,8 s | 2,9 |
| Cierniowy Wilk | zwykły | 87,8% | 85,7% | 85,0% | 2,9 pp | 4–10–44 | 20,1 s | 1,9 |
| Muchomornik | zwykły | 86,5% | 86,8% | 89,7% | 3,2 pp | 4–10–30 | 20,4 s | 1,9 |
| Leśny Troll | rzadki | 57,1% | 53,8% | 53,1% | 4,0 pp | 5–20–49 | 31,6 s | 3,1 |
| Strażnik Gaju | strażnik | 36,3% | 38,1% | 34,6% | 3,5 pp | 9–27–65 | 44,4 s | 4,0 |

### (b) Klasa na klasę — wszystkie poziomy

Komórka: wynik pierwszej klasy jako gracza / jako przeciwnika (100% − wynik drugiej) — cel 45–55%.

| Poziom | Wojownik – Zwiadowca | Wojownik – Mag | Zwiadowca – Mag | Lustro (ta sama klasa) |
|---:|---:|---:|---:|---|
| 1 | 52,9% / 53,0% | 49,4% / 51,6% | 48,5% / 48,1% | 48,8% / 50,2% / 50,6% |
| 2 | 52,0% / 52,4% | 46,1% / 46,8% | 50,5% / 49,5% | 48,9% / 49,4% / 50,4% |
| 3 | 53,4% / 52,8% | 49,0% / 49,2% | 50,8% / 50,6% | 49,5% / 49,7% / 50,5% |
| 4 | 54,5% / 52,4% | 48,6% / 48,2% | 49,6% / 49,0% | 49,7% / 50,1% / 50,1% |
| 5 | 48,5% / 51,0% | 49,0% / 49,5% | 51,9% / 54,1% | 49,6% / 47,6% / 49,8% |
| 6 | 48,8% / 50,0% | 49,8% / 51,2% | 51,0% / 53,5% | 50,5% / 47,2% / 49,9% |
| 7 | 49,0% / 50,7% | 49,1% / 49,2% | 51,1% / 52,9% | 50,1% / 47,9% / 50,0% |
| 8 | 48,5% / 50,8% | 49,6% / 50,7% | 51,1% / 53,0% | 50,1% / 47,1% / 49,8% |
| 9 | 48,8% / 50,7% | 49,7% / 50,1% | 50,9% / 53,0% | 50,1% / 47,4% / 49,9% |
| 10 | 50,5% / 50,6% | 49,8% / 50,0% | 51,7% / 52,1% | 49,4% / 48,9% / 49,5% |
| 12 | 50,4% / 50,3% | 50,1% / 49,4% | 51,7% / 52,2% | 49,2% / 48,7% / 49,5% |
| 15 | 50,1% / 50,7% | 50,2% / 50,0% | 52,0% / 52,5% | 49,2% / 48,6% / 49,8% |
| 20 | 50,5% / 50,5% | 50,2% / 49,7% | 51,5% / 52,4% | 49,1% / 49,0% / 49,5% |


### (c) Ile daje PUNKT statystyki każdej klasie

Zmiana średniego procentu wygranych (pięć potworów i trzy klasy, 1000 walk na parę) po dodaniu 20% puli w jedną statystykę, podzielona przez liczbę dodanych punktów (pp na punkt).

| Poziom | Klasa | Siła | Kondycja | Inteligencja | Zręczność | Szczęście | Pancerz | Najsłabsza / najmocniejsza |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5 | Wojownik | +1,1 | +1,2 | +1,1 | +0,8 | +0,8 | +0,7 | 0,63 |
| 5 | Zwiadowca | +1,1 | +1,2 | +1,0 | +0,5 | +0,7 | +0,7 | 0,43 |
| 5 | Mag | +0,9 | +1,3 | +0,5 | +0,8 | +0,6 | +0,8 | 0,35 |
| 10 | Wojownik | +0,6 | +0,7 | +0,6 | +0,4 | +0,5 | +0,4 | 0,63 |
| 10 | Zwiadowca | +0,5 | +0,7 | +0,5 | +0,3 | +0,4 | +0,4 | 0,46 |
| 10 | Mag | +0,6 | +0,8 | +0,3 | +0,5 | +0,4 | +0,5 | 0,38 |

### (d) Ile razy w walce pada umiejętność

_Przeliczone po kontroli 16/17.11 (nowe pasywki many i trucizny, model buildu pod manę)._

Średnia liczba użyć umiejętności gracza na walkę i mediana numeru własnej akcji z pierwszym użyciem (postać wzorcowa i build pod manę, 1000 walk na parę).

| Poziom | Klasa | Postać | Leśny Slime | Cierniowy Wilk | Muchomornik | Leśny Troll | Strażnik Gaju | Lustro | Pierwsze użycie (akcja) |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 5 | Wojownik | wzorcowa | 2,8 | 1,9 | 1,9 | 2,9 | 3,8 | 3,0 | 3,0 |
| 5 | Wojownik | pod manę | 4,1 | 2,9 | 2,9 | 3,9 | 5,4 | 4,4 | 1,0 |
| 5 | Zwiadowca | wzorcowa | 2,9 | 1,9 | 1,9 | 2,8 | 3,7 | 3,2 | 3,0 |
| 5 | Zwiadowca | pod manę | 4,3 | 3,0 | 3,0 | 4,2 | 5,3 | 4,9 | 1,0 |
| 5 | Mag | wzorcowa | 2,1 | 1,4 | 1,4 | 2,0 | 2,6 | 1,8 | 3,0 |
| 5 | Mag | pod manę | 3,0 | 2,3 | 2,1 | 2,9 | 3,4 | 2,5 | 1,0 |
| 10 | Wojownik | wzorcowa | 3,3 | 2,1 | 2,1 | 3,6 | 4,8 | 4,3 | 3,0 |
| 10 | Wojownik | pod manę | 4,5 | 3,1 | 3,1 | 4,4 | 5,9 | 5,4 | 1,0 |
| 10 | Zwiadowca | wzorcowa | 3,1 | 2,1 | 2,1 | 3,2 | 4,0 | 3,5 | 3,0 |
| 10 | Zwiadowca | pod manę | 4,6 | 3,2 | 3,2 | 4,5 | 5,8 | 5,3 | 1,0 |
| 10 | Mag | wzorcowa | 2,3 | 1,6 | 1,6 | 2,4 | 3,2 | 2,1 | 3,0 |
| 10 | Mag | pod manę | 3,4 | 2,4 | 2,6 | 3,3 | 4,3 | 3,1 | 1,0 |

### (e) Buildy: z postacią wzorcową swojej klasy i z potworami

_Przeliczone po kontroli 16/17.11 (nowe pasywki many i trucizny, model buildu pod manę)._

Pojedynek z wzorcową: wynik buildu średnio z obu miejsc (cel 45–55%). Potwory: różnica procentu wygranych buildu i postaci wzorcowej tej klasy przy tym samym potworze (pp; 1000 walk).

| Poziom | Klasa | Build | Z wzorcową | Leśny Slime | Cierniowy Wilk | Muchomornik | Leśny Troll | Strażnik Gaju |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 5 | Wojownik | pod manę | 53,6% | -2,2 | +0,5 | +1,4 | -3,7 | +2,6 |
| 5 | Wojownik | pod zwykłe ataki | 48,9% | -0,5 | +2,3 | -4,7 | -2,8 | -2,5 |
| 5 | Wojownik | pod Pancerz i blok | 50,9% | -0,9 | +5,5 | -4,5 | +9,8 | -7,2 |
| 5 | Zwiadowca | pod manę | 50,4% | -4,2 | +0,1 | +0,5 | +2,2 | +2,5 |
| 5 | Zwiadowca | pod zwykłe ataki | 51,3% | +0,0 | +0,7 | +0,2 | -6,4 | -2,5 |
| 5 | Zwiadowca | pod unik | 50,1% | -3,0 | -0,4 | +0,3 | +2,5 | +5,9 |
| 5 | Mag | pod manę | 53,1% | -0,9 | +2,2 | +3,8 | +4,4 | -4,5 |
| 5 | Mag | pod zwykłe ataki | 49,6% | +2,7 | +3,7 | +0,6 | +3,0 | -1,0 |
| 5 | Mag | pod truciznę | 46,7% | -0,3 | -0,8 | -1,8 | -2,5 | -4,9 |
| 10 | Wojownik | pod manę | 47,6% | -5,3 | -3,9 | -0,8 | -5,4 | -5,5 |
| 10 | Wojownik | pod zwykłe ataki | 50,1% | -2,4 | +2,1 | -3,6 | -1,3 | -3,2 |
| 10 | Wojownik | pod Pancerz i blok | 48,7% | +1,9 | +7,7 | -2,0 | +2,6 | -14,1 |
| 10 | Zwiadowca | pod manę | 51,7% | -1,8 | -1,2 | +2,5 | -3,7 | -7,7 |
| 10 | Zwiadowca | pod zwykłe ataki | 51,4% | +0,2 | +2,2 | +0,9 | -3,5 | -8,8 |
| 10 | Zwiadowca | pod unik | 52,3% | -0,7 | -1,7 | -2,8 | +0,6 | -0,5 |
| 10 | Mag | pod manę | 48,5% | -3,4 | +0,0 | +0,3 | -2,2 | -4,1 |
| 10 | Mag | pod zwykłe ataki | 53,5% | +3,6 | +3,0 | +0,9 | +5,5 | +0,8 |
| 10 | Mag | pod truciznę | 48,1% | -2,2 | -1,8 | -1,3 | -3,5 | -0,3 |
| 15 | Wojownik | pod manę | 47,5% | -5,7 | -2,6 | +0,0 | -4,9 | -3,6 |
| 15 | Wojownik | pod zwykłe ataki | 50,0% | -2,3 | +2,4 | -3,9 | -2,9 | -4,0 |
| 15 | Wojownik | pod Pancerz i blok | 48,7% | +0,7 | +8,2 | -1,9 | +3,2 | -13,6 |
| 15 | Zwiadowca | pod manę | 50,5% | -4,4 | -1,5 | +2,1 | -2,4 | -7,6 |
| 15 | Zwiadowca | pod zwykłe ataki | 52,5% | -0,8 | +2,7 | +1,0 | -2,2 | -6,8 |
| 15 | Zwiadowca | pod unik | 52,4% | -1,3 | -1,9 | -3,0 | +1,0 | +1,7 |
| 15 | Mag | pod manę | 48,6% | -3,2 | +0,0 | +1,0 | -1,6 | -5,3 |
| 15 | Mag | pod zwykłe ataki | 53,3% | +3,6 | +3,1 | +1,0 | +6,3 | +0,3 |
| 15 | Mag | pod truciznę | 50,0% | -1,7 | -1,7 | -0,7 | -3,3 | -2,0 |

### (f) Blok zmniejsza obrażenia: przechodzi 25% (dziś), 50% albo 0% (blok zatrzymuje cały cios — tylko porównanie)

| Wariant | Poziom | Największa różnica klas (potwory) | Pojedynki klas (najniżej–najwyżej) | Wojownik: wygrane z potworami z tarczą / bez | Ile daje tarcza |
|---|---:|---:|---|---|---:|
| 25,0% przechodzi | 5 | 4,5 pp | 46,8%–53,5% | 69,9% / 51,6% | +18,3 pp |
| 25,0% przechodzi | 10 | 3,5 pp | 49,0%–52,6% | 70,9% / 51,5% | +19,4 pp |
| 50,0% przechodzi | 5 | 7,4 pp | 43,7%–55,1% | 67,2% / 51,7% | +15,5 pp |
| 50,0% przechodzi | 10 | 5,8 pp | 45,5%–52,6% | 67,7% / 51,3% | +16,5 pp |
| 0,0% przechodzi | 5 | 9,7 pp | 47,0%–53,9% | 73,0% / 51,6% | +21,4 pp |
| 0,0% przechodzi | 10 | 10,1 pp | 45,5%–56,2% | 74,1% / 51,5% | +22,7 pp |

### (g) Sloty: aktywne, pasywne i mieszanki

_Przeliczone po kontroli 16/17.11 (nowe pasywki many i trucizny, model buildu pod manę)._

Średni procent wygranych z pięcioma potworami i z wzorcową postacią tej klasy (1000 walk na parę).

| Poziom | Klasa | Sloty | Aktywne / pasywne | Śr. z potworami | Z wzorcową | Umiejętności na walkę |
|---:|---|---|---|---:|---:|---:|
| 10 | Wojownik | Potężne cięcie, Miażdżący cios, Kamienna skóra | 3 / 0 | 70,9% | 49,9% | 3,2 |
| 10 | Wojownik | Potężne cięcie, Miażdżący cios, Kolos | 2 / 1 | 74,8% | 52,7% | 2,7 |
| 10 | Wojownik | Potężne cięcie, Kolos, Rozdzieracz | 1 / 2 | 75,2% | 53,4% | 2,3 |
| 10 | Wojownik | Kolos, Rozdzieracz, Furia | 0 / 3 | 44,4% | 10,6% | 0,0 |
| 10 | Wojownik | Potężne cięcie | 1 / 0 | 70,4% | 46,0% | 2,3 |
| 10 | Wojownik | Kolos | 0 / 1 | 34,2% | 3,0% | 0,0 |
| 10 | Zwiadowca | Uderzenie z góry, Zatruta strzała, Skupienie | 3 / 0 | 69,7% | 47,9% | 2,9 |
| 10 | Zwiadowca | Uderzenie z góry, Skupienie, Oko łowcy | 2 / 1 | 68,7% | 55,2% | 2,7 |
| 10 | Zwiadowca | Uderzenie z góry, Oko łowcy, Zwinność | 1 / 2 | 75,4% | 56,1% | 2,4 |
| 10 | Zwiadowca | Oko łowcy, Zwinność, Seria | 0 / 3 | 48,3% | 23,7% | 0,0 |
| 10 | Zwiadowca | Uderzenie z góry | 1 / 0 | 68,2% | 46,6% | 2,4 |
| 10 | Zwiadowca | Oko łowcy | 0 / 1 | 33,1% | 8,4% | 0,0 |
| 10 | Mag | Kula ognia, Lodowy pocisk, Bariera | 3 / 0 | 69,7% | 50,6% | 2,2 |
| 10 | Mag | Kula ognia, Lodowy pocisk, Skupiona magia | 2 / 1 | 70,4% | 50,9% | 2,0 |
| 10 | Mag | Kula ognia, Skupiona magia, Magiczny pocisk | 1 / 2 | 72,4% | 55,9% | 1,6 |
| 10 | Mag | Skupiona magia, Magiczny pocisk, Przepływ many | 0 / 3 | 37,3% | 7,4% | 0,0 |
| 10 | Mag | Kula ognia | 1 / 0 | 69,6% | 52,5% | 1,7 |
| 10 | Mag | Skupiona magia | 0 / 1 | 30,8% | 2,0% | 0,0 |
| 15 | Wojownik | Potężne cięcie, Miażdżący cios, Kamienna skóra | 3 / 0 | 70,8% | 49,3% | 3,2 |
| 15 | Wojownik | Potężne cięcie, Miażdżący cios, Kolos | 2 / 1 | 74,8% | 52,8% | 2,7 |
| 15 | Wojownik | Potężne cięcie, Kolos, Rozdzieracz | 1 / 2 | 75,2% | 53,4% | 2,3 |
| 15 | Wojownik | Kolos, Rozdzieracz, Furia | 0 / 3 | 43,9% | 10,7% | 0,0 |
| 15 | Wojownik | Potężne cięcie | 1 / 0 | 70,6% | 46,1% | 2,3 |
| 15 | Wojownik | Kolos | 0 / 1 | 33,4% | 2,9% | 0,0 |
| 15 | Zwiadowca | Uderzenie z góry, Zatruta strzała, Skupienie | 3 / 0 | 69,6% | 47,8% | 2,9 |
| 15 | Zwiadowca | Uderzenie z góry, Skupienie, Oko łowcy | 2 / 1 | 68,8% | 54,9% | 2,7 |
| 15 | Zwiadowca | Uderzenie z góry, Oko łowcy, Zwinność | 1 / 2 | 75,7% | 55,7% | 2,5 |
| 15 | Zwiadowca | Oko łowcy, Zwinność, Seria | 0 / 3 | 48,0% | 23,7% | 0,0 |
| 15 | Zwiadowca | Uderzenie z góry | 1 / 0 | 68,5% | 47,3% | 2,4 |
| 15 | Zwiadowca | Oko łowcy | 0 / 1 | 32,6% | 9,1% | 0,0 |
| 15 | Mag | Kula ognia, Lodowy pocisk, Bariera | 3 / 0 | 70,4% | 51,0% | 2,2 |
| 15 | Mag | Kula ognia, Lodowy pocisk, Skupiona magia | 2 / 1 | 71,0% | 50,8% | 2,0 |
| 15 | Mag | Kula ognia, Skupiona magia, Magiczny pocisk | 1 / 2 | 73,0% | 55,0% | 1,6 |
| 15 | Mag | Skupiona magia, Magiczny pocisk, Przepływ many | 0 / 3 | 37,3% | 7,2% | 0,0 |
| 15 | Mag | Kula ognia | 1 / 0 | 70,1% | 51,7% | 1,7 |
| 15 | Mag | Skupiona magia | 0 / 1 | 30,5% | 1,8% | 0,0 |

### (h) Nabijanie jednej statystyki

Postać, która wkłada 60% puli w jedną statystykę (reszta jak w rozkładzie klasy, przeskalowana), kontra rozkład wzorcowy: średni procent wygranych z potworami i z wzorcową postacią (1000 walk).

| Klasa | Wzorcowy rozkład | 60% Siła | 60% Kondycja | 60% Inteligencja | 60% Zręczność | 60% Szczęście | 60% Pancerz |
|---|---:|---:|---:|---:|---:|---:|---:|
| Wojownik | 69,9% / 47,8% | 60,0% / 38,6% | 60,0% / 31,1% | 51,5% / 15,6% | 30,3% / 12,5% | 35,7% / 12,4% | 36,3% / 24,4% |
| Zwiadowca | 69,1% / 49,4% | 59,3% / 41,6% | 61,4% / 36,4% | 47,7% / 19,4% | 33,2% / 10,8% | 38,1% / 14,7% | 34,4% / 21,2% |
| Mag | 69,7% / 49,4% | 61,3% / 44,9% | 70,4% / 45,6% | 47,7% / 36,8% | 44,0% / 21,0% | 38,3% / 12,3% | 42,4% / 2,2% |

W komórce: średnio z potworami / z wzorcową postacią tej klasy (poziom 5).

### (i) Wysokie poziomy

Te same potwory lasu przeskalowane do wysokiego poziomu (zastępczo za potwory dalszych biomów — sprawdzamy wzory, nie trudność biomu) i pojedynki klas; 1000 walk na parę.

| Poziom | Największa różnica klas | Pojedynki klas | Tury: zwykły / strażnik (mediana) | Czas walki: zwykły / strażnik | Umiejętności na walkę | Unik / krytyk / moc (Zwiadowca, Mag) |
|---:|---:|---|---|---|---:|---|
| 30 | 4,8 pp | 48,3%–52,6% | 12 / 27 | 23,0 s / 45,1 s | 2,8 | 35,3% / 28,8% / 1,60; 14,0% / 25,0% / 1,98 |
| 50 | 4,9 pp | 48,3%–52,8% | 12 / 27 | 23,0 s / 45,1 s | 2,8 | 35,3% / 28,7% / 1,60; 14,0% / 25,0% / 1,98 |
| 75 | 5,5 pp | 48,4%–52,9% | 12 / 27 | 23,1 s / 45,2 s | 2,8 | 35,3% / 28,6% / 1,60; 14,0% / 25,0% / 1,98 |
| 100 | 5,5 pp | 48,4%–53,0% | 12 / 27 | 23,1 s / 45,2 s | 2,8 | 35,3% / 28,7% / 1,60; 14,0% / 25,0% / 1,98 |

### (j) Pancerz: limit redukcji i przelicznik klasy

Obrona nigdy nie zatrzymuje więcej niż 75,0% surowego ciosu (przechodzi zawsze co najmniej 25,0%). Pancerz każdej klasy na poziomie 5 przy tej samej puli i tych samych przedmiotach, i ile zostaje z ciosu Leśnego Trolla tego poziomu (bez krytyka, rozrzut 100%):

| Klasa | Przelicznik Pancerza | Pancerz (punkty) | Cios trolla | Po Pancerzu | Redukcja | +30 punktów Pancerza: redukcja |
|---|---:|---:|---:|---:|---:|---:|
| Wojownik | 1,60 | 39,2 | 59,4 | 20,2 | 66,0% | 75,0% |
| Zwiadowca | 1,20 | 22,7 | 59,4 | 36,7 | 38,2% | 75,0% |
| Mag | 1,25 | 25,4 | 59,4 | 34,0 | 42,7% | 75,0% |

### (k) Wskrzeszenie (propozycja D-094) zamiast zwykłej umiejętności w slocie

Postać wzorcowa z wskrzeszeniem w ostatnim slocie (zamiast ostatniej aktywnej; na 1.–4. poziomie jedyny slot) i dla porównania z pasywką Kolos / Oko łowcy / Skupiona magia w tym slocie. Komórka: pojedynek z wzorcową (oba miejsca) / zmiana średnich wygranych z potworami względem wzorcowej (pp; 1000 walk).

| Poziom | Klasa | Zwykła pasywka w slocie | Wskrzeszenie: 1 HP | Wskrzeszenie 5,0% życia | Wskrzeszenie 10,0% życia | Wskrzeszenie 25,0% życia | Wskrzeszenie 50,0% życia | Wskrzeszenie 100,0% życia |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 3 | Wojownik | 4,3% / -36,1 | 4,4% / -36,4 | 6,6% / -32,9 | 7,4% / -30,3 | 10,7% / -23,4 | 19,0% / -14,4 | 38,5% / -0,6 |
| 3 | Zwiadowca | 10,1% / -35,0 | 12,9% / -32,9 | 15,6% / -30,7 | 17,8% / -27,6 | 24,8% / -20,5 | 35,0% / -11,5 | 61,9% / +1,5 |
| 3 | Mag | 3,2% / -37,8 | 4,1% / -33,4 | 4,1% / -30,8 | 6,5% / -27,5 | 12,9% / -20,4 | 21,7% / -10,2 | 47,8% / +6,3 |
| 5 | Wojownik | 52,8% / +2,2 | 53,8% / +2,9 | 61,1% / +6,4 | 64,6% / +9,7 | 73,6% / +15,7 | 84,5% / +22,6 | 94,9% / +28,5 |
| 5 | Zwiadowca | 48,5% / -0,8 | 51,0% / +3,3 | 59,0% / +5,3 | 64,0% / +8,8 | 73,5% / +14,6 | 81,2% / +22,1 | 94,7% / +29,0 |
| 5 | Mag | 49,4% / -0,3 | 54,4% / +4,3 | 54,6% / +5,7 | 63,8% / +10,7 | 73,5% / +16,5 | 85,1% / +23,7 | 96,0% / +29,2 |
| 10 | Wojownik | 54,3% / +3,9 | 56,5% / +3,5 | 63,3% / +8,6 | 66,8% / +11,1 | 76,2% / +16,2 | 85,0% / +23,3 | 95,5% / +28,3 |
| 10 | Zwiadowca | 53,3% / +1,0 | 59,2% / +5,2 | 65,5% / +7,4 | 68,9% / +11,3 | 75,7% / +16,7 | 84,5% / +23,1 | 93,8% / +28,7 |
| 10 | Mag | 51,8% / +0,7 | 57,5% / +5,2 | 58,5% / +7,5 | 66,0% / +11,2 | 76,0% / +17,0 | 85,5% / +24,3 | 96,0% / +29,5 |

### (l) Przeszukanie wszystkich zestawów slotów (bez broni z pasywką, zaklęcia i premii)

Każdy zestaw 1–3 slotów klasy (aktywne w każdej kolejności, pasywne, bez wskrzeszenia) w pojedynku z wzorcową tej klasy (oba miejsca): sito 200 walk z każdej strony, trzy najlepsze potwierdzone na 1000 innych ziarnach. Wybór slotów jest darmowy, więc żaden zestaw nie powinien wyraźnie bić wzorcowej (kontrola 16/17.11: przed osłabieniem pasywek many najlepsze miały 63–67%).

| Poziom | Klasa | 1. zestaw | 2. zestaw | 3. zestaw |
|---:|---|---|---|---|
| 5 | Wojownik | Potężne cięcie, Mur tarczy: 56,2% | Potężne cięcie, Kolos: 53,7% | Potężne cięcie, Bitewny rytm: 53,2% |
| 5 | Zwiadowca | Uderzenie z góry, Zwinność: 55,4% | Skupienie, Uderzenie z góry: 54,4% | Zatruta strzała, Zwinność: 48,8% |
| 5 | Mag | Kula ognia, Przepływ many: 54,9% | Kula ognia, Magiczny pocisk: 51,9% | Lodowy pocisk, Kula ognia: 49,9% |
| 10 | Wojownik | Potężne cięcie, Mur tarczy, Bitewny rytm: 58,3% | Potężne cięcie, Kolos, Bitewny rytm: 55,5% | Potężne cięcie, Kamienna skóra, Mur tarczy: 52,5% |
| 10 | Zwiadowca | Skupienie, Uderzenie z góry, Zwinność: 56,8% | Uderzenie z góry, Zatruta strzała, Zwinność: 56,7% | Zatruta strzała, Uderzenie z góry, Zwinność: 55,3% |
| 10 | Mag | Kula ognia, Przepływ many, Magiczny pocisk: 59,9% | Bariera, Kula ognia, Magiczny pocisk: 58,3% | Kula ognia, Przepływ many, Skupiona magia: 57,9% |

_Część (l) dopisana przy kontroli 16/17.11; policzone: `python -B tools/walka/balans.py --procesy 1 --ziaren 2000 --czesci d,e,g,l`._
