---
status: propozycja
---
# Stan gracza — jeden właściciel stanu gracza między systemami gry

**Status: propozycja** (zlecenie Karola z 17.11.2026: „Upewnijmy się nad grywalnością już gry”). Nic tu nie jest
kanonem; liczby i zasady z listy „przyjęte, do zmiany” czekają na decyzje ludzi.

Pakiet buduje w Studio kontener `Workspace/StanGracza` (atrybut `Wygenerowane`). Spina prototypy w jedną pętlę:

| Przed pakietem | Z pakietem |
|---|---|
| walka w lesie postacią wzorcową z panelu testowego (dowolna klasa, poziom „auto” = poziom potwora) | bohater z danych gracza: klasa ze startu (atrybut `Class`), poziom (`Level`), sześć statystyk z atrybutów |
| łup tylko na ekranie wyniku | Złoto, XP i Gemy trafiają do atrybutów gracza, HUD Pawła je odlicza po walce |
| `Level` i `XP` nigdy nie rosną | awans: XP ≥ XPMax → poziom w górę, nowe XPMax z krzywej, baner „POZIOM N” |
| statystyki = wartości testowe (130 pkt) niezwiązane z walką | po wyborze klasy 30 pkt według rozkładu klasy, przy awansie +10 według rozkładu |
| trening dopisuje tylko do atrybutu sesyjnego `TreningSila`… | przyrost z Training Center dopisuje się też do `Strength`… i wzmacnia następną walkę |

Atrybuty gracza zostają szyną danych: HUD, okno ekwipunku i drzewko Pawła czytają je jak dawniej — **żaden plik Pawła
nie jest zmieniony**.

## Jak to działa
- **Jeden właściciel stanu:** skrypt `SerwerStanu` w kontenerze. Inne pakiety rozmawiają z nim przez
  `Workspace/StanGracza/Sygnaly` (BindableFunction, tylko serwer), zawsze przez `FindFirstChild` + `pcall`:
  bez kontenera wszystko działa jak przed pakietem.
- **Profil:** jedna tabela na gracza z polem `wersja` (pod przyszły zapis), dziś tylko w pamięci serwera — znika
  przy wyjściu gracza, tak jak atrybuty.
- **Łup po walce:** serwer lasu przyznaje łup przy przyjęciu walki (wynik znany z dziennika), stan gracza trzyma go
  w profilu i wpisuje do atrybutów, gdy HUD znów widać (klient zgłasza `"pokaz"` — koniec ekranu walki) albo
  najpóźniej po czasie walki + 6 s. Zgłoszenie klienta może tylko przyspieszyć pokazanie, nigdy nic nie zmienia.
- **Gold i Gems** są dopisywane do bieżącej wartości atrybutu (drzewko Pawła odejmuje Gems z tego samego atrybutu).
- **Statystyki:** pierwsze wpisanie = rozkład klasy + trening; potem tylko różnica przy zmianie klasy albo poziomu,
  więc to, co dopisze ktoś inny (darmowy „+” w oknie ekwipunku), zostaje.

## Interfejs (`Workspace/StanGracza`)

### Wspólne punkty zaczepienia dla pakietów (18.11.2026: pety D-101, Kowal D-102)
Inne pakiety NIE edytują `stan_gracza` — wpływają na bohatera i trzymają swoje dane gracza przez dwa sygnały
(BindableFunction w `Sygnaly`, tylko serwer, zawsze `FindFirstChild` + `pcall`).

**`Sygnaly/Modyfikatory`** — premie do bohatera walki i do łupu:
- `Invoke("ustaw", gracz, zrodlo, mod)` → `{ ok = true }` albo `{ ok = false, powod }`. `zrodlo` = nazwa pakietu
  („pety”, „kowal”…; litery, cyfry, „_”, do 24 znaków). Każde źródło ma JEDEN wpis na gracza — kolejne `ustaw` go
  zastępuje (zły wpis jest odrzucany, a stary zostaje).
- `Invoke("usun", gracz, zrodlo)` → `{ ok = true, bylo }`.
- `Invoke("czytaj", gracz)` → złożenie wszystkich źródeł: `{ ok = true, statystyki, procent, lup = { zloto,
  doswiadczenie }, bron, pancerz, tarcza, pasywki, zrodla = { nazwy źródeł } }`.
- `mod` — tabela z dowolnymi z pól (inne pole → `nieznane_pole`):

  | Pole | Znaczenie | Granice jednego źródła (`D.modyfikatory`) | Złożenie |
  |---|---|---|---|
  | `statystyki = { Strength = 5, … }` | stałe dodatki do sześciu statystyk (klucze = atrybuty gracza: Strength, Constitution, Intelligence, Dexterity, Luck, Armor) | liczby całkowite −1000…1000 | suma; statystyka 0…9999 |
  | `procent = { Strength = 0.10, … }` | mnożnik końcowej statystyki (pole silnika `pet`, D-059) | 0…1 | suma, najwyżej 3 |
  | `lup = { zloto = 0.05, doswiadczenie = 0.08 }` | ułamki premii do łupu z walki | 0…0,5 | suma, najwyżej 1 |
  | `bron = N`, `pancerz = N` | dodatek do obrażeń broni / pancerza z przedmiotów ze wzoru dla poziomu (dziś broń 12 na 1. poziomie, 48 na 10.) | −1000…1000 | broń ≥ 1, pancerz ≥ 0 |
  | `tarcza = N` | dodatek do szansy bloku (ułamek; wzór: 0,2828) — tylko klasa z tarczą (Wojownik) | −0,5…0,5 | blok 0…0,5 (`blok_maks` silnika) |
  | `pasywki = { "nazwa", … }` | pasywki znane silnikowi — ich modyfikatory idą do pola `premie` opisu postaci (bez zajmowania slotu) | do 6 nazw, nieznana → `nieznana_pasywka` | bez powtórzeń; tylko pasywki klasy gracza (albo wspólne); sumy przycięte do granic silnika |
  | `zaklecie = "podpalenie"` albo `"trucizna"` (18.11.2026) | zaklęcie broni silnika (`bron.zaklecie`): przy ciosie gracza, który nie został zablokowany, podpalenie z szansą 25%, trucizna 30% (+ modyfikator `szansa_zaklecia`) — np. żywioł peta (D-101) | tylko nazwy z `silnik.ZAKLECIA`, inna → `nieznane_zaklecie` | jedno: przy kilku źródłach wygrywa **pierwsze według nazwy źródła** (alfabetycznie: „kowal” przed „pety”); zaklęcie z broni (gdy kiedyś będzie) ma pierwszeństwo |

  Inne powody odmowy: `zly_mod`, `zla_statystyka`, `zle_statystyki`, `zle_procent`, `zly_lup`, `zle_bron`,
  `zle_pancerz`, `zle_tarcza`, `zle_pasywki`, `zle_zrodlo`, `zly_gracz`, `za_duzo_zrodel` (najwyżej 16 źródeł na gracza).
- Dostępne pasywki (z `src/server/Walka/Dane.luau`, przez `dane.py` z `tools/walka/silnik.py`):
  - umiejętności Wojownika: `bitewny_rytm` (mana +10%, mana na start +15), `furia` (zwykły cios +10,8%), `kolos`
    (życie +4%, cios +2%), `mur_tarczy` (blok +4,2%, pancerz +15,7%), `rozdzieracz` (pancerz wroga −12%);
  - umiejętności Zwiadowcy: `oko_lowcy` (kryt. +0,7%, mnożnik kryt. +2,5%), `przyplyw_adrenaliny` (mana),
    `seria` (zwykły cios +13,4%), `zwinnosc` (unik +7,1%);
  - umiejętności Maga: `kumulowanie_trucizny` (stosy trucizny +4, siła trucizny +42,7%), `magiczny_pocisk` (zwykły
    atak +11,7%), `przeplyw_many` (mana), `skupiona_magia` (moc +2,5%);
  - pasywki broni: Mag — `ciezka_rozdzka`, `jadowity_kostur`, `kostur_many`, `ognista_rozdzka` (podpalenie +2 tury);
    Wojownik — `miecz_runiczny`, `topor_rzeznika`; Zwiadowca — `luk_mysliwego`, `luk_runiczny`, `luk_wiatru`.
  - Niedostępna: `wskrzeszenie` (legendarna, działa tylko ze slotu umiejętności — D-094).
- Wpisy żyją w pamięci serwera (nie w profilu): pakiet odtwarza je ze swoich danych po wejściu gracza.
- **Zgodność wstecz (pety):** dopóki pakiet petów nie zawoła `Modyfikatory` dla źródła `"pety"`, premia z
  `Pety("kup" / "aktywny")` liczy się jako to źródło (zachowanie jak dotąd). Pierwsze `ustaw` albo `usun` dla `"pety"`
  przejmuje źródło — od tej chwili liczy się tylko wpis z `Modyfikatory` (bez podwójnej premii). Komunikat `"premia"`
  do klienta petów niesie tylko część łupu ze źródła petów.

**`Sygnaly/DanePakietu`** — dane pakietu w profilu gracza (pod przyszły zapis razem z resztą profilu):
- `Invoke("czytaj", gracz, pakiet)` → kopia tabeli albo `nil`.
- `Invoke("zapisz", gracz, pakiet, tabela)` → `{ ok = true }` albo `{ ok = false, powod }`; `tabela = nil` usuwa wpis.
- Dane leżą w `profil.pakiety[pakiet]` (profil wersja 3). Tylko liczby skończone, napisy, logiczne i tabele z nich;
  klucze napisy albo liczby całkowite; najwyżej 2000 wartości, 8 poziomów zagłębienia, napis i klucz do 200 bajtów,
  32 pakiety na gracza. Powody: `zly_typ`, `zla_liczba`, `zly_klucz`, `za_dlugi_napis`, `za_gleboko`, `za_duzo`,
  `zly_pakiet`, `za_duzo_pakietow`, `zly_gracz`. Zapis i odczyt robią kopię — zmiana tabeli po `zapisz` niczego nie
  zmienia w profilu.

### Pozostałe obiekty
| Obiekt | Kierunek | Argumenty → wynik |
|---|---|---|
| `Sygnaly/Bohater` (BindableFunction) | las → stan | `Invoke(gracz)` → opis postaci dla `Silnik.symuluj` albo `nil` |
| `Sygnaly/PrzyznajLup` (BindableFunction) | las → stan | `Invoke(gracz, { lup = walka.lup, wynik, czas = walka.czas, zrodlo = "LasPotwory" \| "LasPasGra" \| "BagnoPasGra", gatunek, poziom })` → `{ ok = true }` \| `{ ok = false, powod }` |
| `Sygnaly/SterowanieSerwera` (BindableFunction) | testy | `"stan", gracz?` · `"zgodnosc"` · `"publikuj", gracz?` · `"bohater", gracz?` · `"przyznaj", gracz, lup` |
| `Sygnaly/WydajZloto` (BindableFunction, 17.11) | pakiet → stan | `Invoke(gracz, { ile, zrodlo = kontener z listy D.wydatki.zrodla, cel })` → `{ ok = true, zloto, ile, licznik }` \| `{ ok = false, powod ("za_malo" + brakuje, zloto, ile \| "zla_kwota" \| "zle_zrodlo" \| "zly_cel" \| "zly_gracz") }` — nigdy poniżej zera |
| `Sygnaly/Pety` (BindableFunction, 17.11) | pety → stan | `"kup", gracz, { ile, zrodlo, cel, pet, premia }` (wydatek + kopia peta w jednym wywołaniu) · `"aktywny", gracz, { pet, premia }` \| `{ odstaw = true }` · `"stan", gracz` |
| `Zdalne/ZdarzeniaStanu` (RemoteEvent) | serwer → klient | `"awans", poziom, ile` · `"premia", zloto, doswiadczenie, pet` (dodatek peta w pokazanym łupie — czyta go klient `swiat/pety_proba`) · `"przegrana", kara, doswiadczenie` (kara za przegraną w pokazanym łupie — napis `KlientStanu`) · `"brak_punktow"` („+” bez punktu cofnięty) · `"gemy_straznika", n` (Gemy za pierwsze pokonanie strażnika) |
| | klient → serwer | `"pokaz"` (bez liczb, najwyżej raz na 0,5 s) |
| `Workspace/TreningProba/Sygnaly/PrzyrostStatystyki` | trening → stan | tylko słuchamy (z ponownym podłączeniem po przebudowie) |

Atrybuty gracza, które pisze pakiet: `Level`, `XP`, `XPMax`, `Gold`, `Gems`, `Strength`, `Constitution`,
`Intelligence`, `Dexterity`, `Luck`, `Armor` (Pawła) oraz własne `ShardyEwolucji`, `TokenyKrainy_<kraina>`, `PetAktywny`
i `PetyLiczba` (17.11.2026).

**Pety i wydawanie Złota (17.11.2026, pakiet `swiat/pety_proba`, propozycja):** profil ma wersję 2 z polami
`pety = { kopie, aktywny, premia }` i `wydatki` (licznik wydatków na cel — np. kupione jajka; z niego pakiet petów
liczy cenę). Zakup jajka to JEDNO wywołanie `Pety("kup")`: kwota i źródło sprawdzone, łup czekający na pokazanie
(> `min_s`) wchodzi do Złota, Złoto w dół (za mało = odmowa z brakującą kwotą, bez zmian), kopia peta w górę —
bez przerw między krokami. Premię aktywnego peta (ułamki Złota i doświadczenia, najwyżej `D.pety.premia_maks`)
przysyła pakiet petów; doliczamy ją przy przyjęciu łupu (zaokrąglenie 0,5 w górę). Źródła wydatków: `D.wydatki.zrodla`
(dziś `PetyProba`). Stan petów żyje tutaj, nie w pakiecie petów — Złoto i pety zapiszą się razem.
Atrybuty kontenera do podglądu: `SerwerStanuGotowy`, `ZgodnoscLogikiStanu` („OK 80/80”), `RozkladyZ`,
`TreningPodlaczony`, `LicznikLupow`, `LicznikPokazan`, `LicznikAwansow`, `LicznikBohaterow`, `LicznikTreningu`,
`OstatniLup`, `OstatniePokazanie`, `OstatniBohater`, `LicznikKar`, `OstatniaKara` (kara za przegraną, 17.11.2026).

## Wyłączniki
- **Cały pakiet:** `python -B swiat/stan_gracza/zbuduj.py --usun` — gra wraca do stanu sprzed pakietu (las walczy
  postacią wzorcową z panelu, łupu nie ma).
- **Statystyki klasy:** atrybut kontenera `StatystykiKlasy = false` — zostają wartości testowe z `PlayerStatsDefaults`
  (Paweł); trening dalej dopisuje, bohater walki dalej czyta atrybuty (wtedy jest ok. 4× za mocny).
- **Kara za przegraną (17.11.2026):** `KARA_PROCENT` w `dane.py` (jedna liczba; `0` = wyłączona, potem
  `python -B swiat/stan_gracza/dane.py`) albo atrybut kontenera `KaraPrzegranej`: `false` = wyłączona w czasie gry, liczba
  0..1 = inny ułamek (np. do prób); przechodzi na odbudowany kontener jak `StatystykiKlasy`.
- **Punkty statystyk (18.11.2026):** w `dane.py` dwie liczby: `PUNKTY_DO_ROZDANIA` (5, z D-097) i
  `PUNKTY_SAMO_NA_POZIOM` (5 — wariant b; **0 = czysty wariant D-097**, tylko 5 do rozdania); potem
  `python -B swiat/stan_gracza/dane.py` i `zbuduj.py --skrypty`. Atrybut kontenera `PunktyStatystyk = false` w czasie
  gry — jak przed D-097 (10 samo na poziom, darmowy „+”, bez licznika); przechodzi na odbudowany kontener.
- **Gemy (D-099):** `GEMY_ZA_POZIOM` (10) i `GEMY_ZA_STRAZNIKA` (100) w `dane.py`; 0 wyłącza.
- **„Szczęście początkującego” (18.11.2026):** `SZCZESCIE_POCZATKUJACEGO` w `dane.py` (0,75; 0 = wyłączone) albo atrybut
  kontenera `SzczesciePoczatkujacego = false`.
- **Zapis postępu:** domyślnie wyłączony — rozdział „Zapis postępu”.
- **Tryb testowy lasu:** atrybut kontenera lasu `TestBohater = true` (`Workspace/LasPotwory` albo `Workspace/LasPasGra`)
  — reguła testowa T1 jak dawniej (klasa i poziom z panelu), walki bez łupu. Ustawiają go próby w Play
  (`swiat/las_potwory/testy/proba_play.py`, `kontrola_play.py`, `swiat/las_pas_gra/testy/proba_play.py`,
  `proba_dodatkowa.py`).

**Jak dodać pakiet (jedno miejsce, 18.11.2026):** listy kontenerów, które rozmawiają ze stanem gracza, są na górze
`dane.py`: `PAKIETY_BIOMOW` (walki biomu — łup przez `PrzyznajLup` i kara za przegraną; dziś `LasPotwory`,
`LasPasGra`, `BagnoPasGra` i od razu `DzunglaPasGra`) i `PAKIETY_WYDATKOW` (wydawanie Złota — `PetyProba`,
`KowalProba`). Nowy pakiet: dopisz nazwę jego kontenera, `python -B swiat/stan_gracza/dane.py`, testy, potem
`zbuduj.py --skrypty`. Cele wydatków (`jajko_lesne`, `ulepszenie`, `zakup_przedmiotu`…) listy nie mają — przechodzi każda
nazwa z liter, cyfr i „_”. Test `6b` sam znajduje pakiety `swiat/*_pas_gra` i oblewa, gdy kontener biomu nie jest na
liście (bez wpisu łup dostaje odmowę `zle_zrodlo`). Krainy tokenów (`TokenyKrainy_<kraina>`) też listy nie mają.

## Przyjęte, do zmiany (robocze — do decyzji ludzi)
1. **Krzywa doświadczenia** 11,71 × L^1,6 (z `tools/walka/tempo.py`; las ok. 30 min) zamiast stałego `XPMax = 100`.
2. **Przyrost co poziom (D-097 ✅ zatwierdzona 17.11: „5 punktów do rozdania za poziom”; wdrożenie 18.11.2026):** za każdy poziom
   **5 punktów do rozdania** przez gracza (atrybut `PunktyDoRozdania`, „+” w oknie ekwipunku) **+ 5 rozdzielanych samo**
   rozkładem klasy (stały przyrost z D-057; suma 10 jak dotąd, więc balans potworów zostaje). Złoto nie kupuje
   statystyk. „+” Pawła (`StatPoints`, jego pliki nietknięte) dodaje punkt za darmo — **rozwiązanie tymczasowe:** serwer
   stanu pilnuje zmian sześciu atrybutów, których sam nie zrobił: z punktem w puli zmiana zostaje, a punkt schodzi;
   bez punktu albo spadek — zmiana cofnięta, gracz widzi „Brak punktów — zdobądź poziom”. Mały licznik „Punkty do
   rozdania: N” na dole ekranu (własne GUI, tylko gdy N > 0). Wyłącznik: atrybut kontenera `PunktyStatystyk = false`
   (jak przed D-097). Liczby z `punkty_statystyk.py` (las do Strażnika Gaju, Bagno do Strażnika Topieli, 40 graczy
   na klasę; profil klas z `ClassData`, czyli dzisiejsza gra):

   | Wariant | Gracz rozdaje | Las: min / przegrane / Gaj za 1. razem | Bagno: min / przegrane / Topiel za 1. razem |
   |---|---|---|---|
   | dziś: 10 samo | — | 32 / 12 / 22% | 57 / 26 / 17% |
   | a: tylko 5 do rozdania | jak klasa | 61 / 34 / 2% | 126 / 93 / 3% |
   | a | wszystko w jedną (główną) | 111 / 66 / 0% | 174 / 126 / 2% (78 z 120 nie kończy) |
   | **b: 5 samo + 5 do rozdania (wybrany)** | **jak klasa** | **31 / 12 / 29%** | **57 / 26 / 13%** |
   | b | po równo | 28 / 10 / 32% | 50 / 22 / 13% |
   | b | wszystko w główną | 43 / 19 / 7% | 99 / 53 / 4% |
   | b | wszystko w nieswoją | 31 / 13 / 26% | 66 / 33 / 6% |
   | c: 10 do rozdania | jak klasa | 31 / 12 / 22% | 54 / 26 / 14% |
   | c | wszystko w główną | 90 / 47 / 1% | 172 / 114 / 0% (76 nie kończy) |

   **Odstępstwo od D-097, przyjęte roboczo dla balansu:** D-097 mówi tylko o 5 punktach do rozdania za poziom.
   Wdrożony wariant b dokłada 5 rozdzielanych samo, bo czysty wariant (a) to połowa dzisiejszych punktów na poziom:
   las wydłuża się z ok. 31 do ok. 61 min (przegranych 12 → 34, Strażnik Gaju za pierwszym razem 29% → 2%), Bagno
   z 57 do 126 min — a potwory były strojone pod 10 punktów na poziom. Czysty wariant (a) wymaga osłabienia potworów
   w danych silnika (`tools/walka/dane_walki.json`), czego tu nie robię. Przełącznik dla ludzi: `PUNKTY_SAMO_NA_POZIOM`
   w `dane.py` (5 → 0 = czysty wariant D-097).
   Dlaczego b: tylko 5 do rozdania (a) to połowa dzisiejszych punktów — las trwa dwa razy dłużej. 10 do rozdania (c)
   daje dziecku, które kliknie wszystko w jedno, las 3× dłuższy, a Bagno prawie nie do przejścia. Przy b najgorszy
   wybór kosztuje w lesie ok. +11 min, a rozkład samo rozdzielany trzyma postać przy życiu. Z profilem wzorcowym
   wychodzi to samo (b: 27,5 min, 8 przegranych; najgorszy wybór 38 min). Ciekawostka: „po równo” wygrywa częściej
   niż rozkład klasy — oba profile klas nie są najlepszym rozdaniem dla silnika (wątek do pytania 56).
   **Tempo treningu (pytanie 50):** Karol wybrał wzór z paskiem (odpowiedź a). Wariant b nie zmienia sumy punktów na
   poziom, więc pula odniesienia w `swiat/trening_proba/ustawienia.json` (`pula_baza` 30, `pula_na_poziom` 10) zostaje,
   a wzór (4/5/6/8 jednostek za trafienie przy seriach 5/10/20, próg paska 40, połowa udziału 0,1) też — tego pakietu
   nie zmieniam.
   **Potwory pod profil z ClassData (sprawdzone, nie zmienione):** pierwsza walka (1. poziom, Leśny Slime poz. 1) to
   dziś 73–79% przy celu ok. 85% — slime ma już najniższy poziom, a siły potworów nie da się zmienić bez zmiany silnika.
   Strażnik Gaju za pierwszym razem 29% (cel 35–40%): obniżenie jego poziomu z 10 na 9 dałoby 54–64% na 11. poziomie
   gracza, czyli za dużo — poziomy są za grube. Dane potworów zostają; możliwy ruch po stronie bohatera (do decyzji):
   pula startowa 30 → 33 daje pierwszą walkę 79–84%. Strażnik Topieli zostaje trudny (13% za pierwszym razem).
2b. **Pierwsza walka praktycznie pewna (18.11.2026, „szczęście początkującego”):** dopóki gracz nie ma żadnej wygranej,
   jego sześć statystyk w walce ×1,75. Działa przez wewnętrzne źródło `szczescie_poczatkujacego` w `Modyfikatory`
   (pole silnika `pet`), bez napisu dla gracza. Znika po pierwszej wygranej; przegrana go nie zdejmuje.
   - Pierwsza walka z potworem 1. poziomu przy profilu klas z `ClassData`: Wojownik 79% → 99,6%, Zwiadowca 76% → 98%,
     Mag 73% → 96%.
   - Uwaga: po D-096 slime'y pierwszej przegrody mają poziomy 1–3 rozdane po miejscach. Ze slime'em 2. poziomu ta sama
     premia daje 73–88% (bez niej 26–34%).
3. **Sloty umiejętności** 1 / 2 / 3 od poziomów 1 / 5 / 10 (jak dziś w walce). D-055 i D-088 mówią: sloty z drzewka,
   na start 0.
   **Gemy bez płacenia (D-099 ✅ 17.11; wdrożenie 18.11.2026, liczby „do zmiany”):** +10 Gemów za każdy awans i +100 za
   pierwsze pokonanie strażnika każdego biomu (raz na gatunek strażnika — profil `straznicy`; napis po walce). Nie
   wdrożone (opis i liczby w `tools/walka/REBIRTH_1711.md`, część 1): +1 Gem za każde 10 wygranych i kopalnia
   w Twierdzy (D-049). Przy tych liczbach gracz ma ok. 200 Gemów na końcu lasu, czyli wszystkie trzy sloty
   umiejętności z drzewka (25 / 70 / 125), a po 10 godzinach ok. ćwierć drzewka gracza. Rebirth (D-100) odrzucony.
4. **Przegrana (realizacja zatwierdzonej D-098 ✅ 17.11; liczby dalej „do zmiany”):** bez łupu, 20% doświadczenia
   (tak liczy silnik) i **kara: 5% posiadanego Złota (w dół do całych), najwyżej tyle, ile daje wygrana ze zwykłym
   potworem na poziomie przeciwnika** (łup Cierniowego Wilka z silnika: 22 + 9 × (poziom − 1)), nigdy poniżej zera.
   Bez kary czasowej, Gemy zostają. Tylko walki lasu-pasa, starego lasu i Bagna (`D.kara.zrodla`); tablica próby
   i tryb testowy `TestBohater` łupu nie wysyłają, więc kary tam nie ma. Złoto znika przy pokazaniu łupu (koniec
   ekranu walki), a gracz widzi napis „Przegrana: −N Złota, +M doświadczenia” (na dole ekranu, tuż nad napisem
   premii peta; bez Złota — sam XP). Profil bez zmian (wersja 2). Liczby z `kara_przegranej.py` (gracze z ekonomii
   jajek, jajko 300 w lesie i 750 w Bagnie, kupują od razu):

   | Wariant (las do Strażnika; profil wzorcowy, 8 przegranych na 45 walk) | Kara za przegraną (mediana / maks.) | Razem w lesie | 1. jajko później o | Tuż przed zakupem | Oszczędzający: razem / maks. jednej |
   |---|---|---|---|---|---|
   | 2% | 2 / 5 | 16 | 0 min | 5 Złota | 158 / 71 |
   | **5%, najwyżej 1 wygrana (wybrany)** | **6 / 14** | **46** | **0 min (90%: 0,6)** | **13 Złota = 0,2 walki** | **366 / 103** |
   | 5% bez limitu | 6 / 14 | 46 | 0 min (90%: 0,6) | 13 Złota | 380 / 155 |
   | 10% (z limitem albo bez) | 12 / 29 | 94 | 0 min (90%: 0,7) | 26 Złota | 470–698 / 103–271 |
   | stała ½ wygranej zwykłego potwora | 38 / 51 | 255 | 0,5 min (90%: 1,3) | 42 Złota | 278 / 51 |

   Bagno (60 min, 19 przegranych na 78 walk): przy 5% z limitem kara 18 / 37 za przegraną, razem 346, jajko Bagna
   bez przesunięcia (90%: 1,4 min), oszczędzający traci najwyżej 157 naraz (bez limitu — 615). Z profilem klas
   z `ClassData` Pawła (pytanie 56: 12 przegranych w lesie, 26 w Bagnie) razem 65 w lesie i 460 w Bagnie.
   Dlaczego ten wariant: kara rośnie z tym, co gracz ma (biedny nowy gracz prawie nic nie traci, stała kwota zabiera
   mu za to prawie całe jajko), a limit „jednej wygranej” znaczy, że jedna walka odrabia każdą przegraną. Obejście
   przez wydanie Złota przed trudną walką (jajko, później przedmioty) jest w porządku — to wydawanie, o które chodzi
   w ekonomii, a nie zysk. **Doświadczenie 20% zostaje**: w lesie celowa przegrana ze Strażnikiem daje 104 XP/min
   wobec 136 z wygranych; w Bagnie odwrotnie (190 wobec 161 XP/min), ale każda przegrana kosztuje Złoto, a wygrana je
   daje. Gdyby chcieć to domknąć (propozycja, nie wdrożona): XP za przegraną najwyżej tyle, co za wygraną ze zwykłym
   potworem tego poziomu.
5. **Tablica próby walki (`TestWalki2`) bez nagród** — to piaskownica (dowolna klasa i poziom 1/5/10).
6. **Broń i pancerz z przedmiotów** ze wzoru dla poziomu; ekwipunek z okna Pawła (dziś tylko po stronie klienta)
   i drzewko (`ST_*`) do walki nie wchodzą.
7. **Przed wyborem klasy** statystyki to rozkład Wojownika; zmiana klasy w trakcie gry (ChooseClass na to pozwala)
   przelicza rozkład, trening i „+” zostają.
8. **Gemy z łupu** dopisują się do testowych 1000 z `PlayerStatsDefaults`.
9. **Rozkłady klas** czytane z `ReplicatedStorage.Shared.ClassData` (paski ekranu wyboru Pawła). Od 17.11.2026
   (commit Pawła `bf5c933`) są inne niż wzorcowe — pytanie 56 czeka na ludzi; do decyzji gra czyta ClassData, serwer
   ostrzega o różnicy, a testy pilnują tylko warunków każdego profilu (trzy klasy, sześć liczb, suma 100, pula bez
   zgubionego punktu) i liczą oczekiwane statystyki z aktualnego ClassData. Porównanie w lesie:
   `python -B swiat/stan_gracza/porownaj_profile.py` — z profilem Pawła każda klasa przegrywa częściej (11–13 zamiast 8
   przegranych do Strażnika, las dłuższy o 3–5 min), a różnice między klasami rosną (na trollu 13 pp zamiast 4).
10. **Baner „POZIOM N”** to tymczasowe GUI pakietu; docelowe pop-upy projektuje Paweł (D-093).
11. **Bez zapisu:** profil w pamięci serwera; po wyjściu z gry wszystko znika (jak dziś). Miejsce na zapis: profil
    (`L.nowyProfil`, pole `wersja`), `swiat/las_pas_gra/zrodla/PamiecGracza.luau`.
12. **Pety (17.11.2026):** premia peta do łupu poza silnikiem walki (D-059 mówi o mnożniku statystyk — następny krok),
    pierwszy kupiony pet od razu aktywny, jedna kwota wydatku najwyżej 1 000 000 Złota.

## Zapis postępu (status: propozycja, DOMYŚLNIE WYŁĄCZONY — 18.11.2026)
Kod zapisu jest gotowy i przetestowany offline. Włączenie to jedna decyzja ludzi. Zasady: skill projektu
`roblox-data` (DataStore, blokada sesji, `UpdateAsync`, migracja, cykl życia zapisu).

**Jak działa.** `Moduly/ZapisStanu` + `SerwerStanu`:
- **Wczytanie przy wejściu, zanim cokolwiek wpisze atrybuty:**
  - `UpdateAsync` na kluczu `player_<UserId>`; identyfikator w kluczu ułatwia usuwanie danych na żądanie.
  - W tym samym kroku serwer bierze sesję (blokadę).
  - Do końca wczytania atrybut gracza `StanGraczaWczytany = false`. W tym czasie odmawiają: łup, wydatki, pety,
    `Modyfikatory`, `DanePakietu` i bohater walki.
  - **Pakiety (pety, Kowal…) mają czekać, aż `StanGraczaWczytany ~= false`.**
  - Potem serwer wpisuje atrybuty z profilu: poziom, doświadczenie, Złoto, Gemy, shardy, tokeny, klasę i zapisane
    atrybuty. Statystyki liczy od nowa: rozkład klasy dla poziomu + trening + rozdane punkty.
- **Zapis:**
  - co ok. 2 min (120 s + rozrzut do 30 s);
  - przy wyjściu gracza (wcześniej łup z zakończonej walki trafia do profilu);
  - przy zamknięciu serwera (`BindToClose`, najwyżej 25 s).
  - Jeden zapis gracza naraz: następny czeka w kolejce, a dane są brane w chwili wywołania.
- **Blokada sesji** jest w rekordzie (`sesja = { serwer, czas }`):
  - Świeża cudza sesja (młodsza niż 600 s): 6 prób co 5 s, bo stary serwer zwykle właśnie zapisuje wyjście gracza.
    Potem gracz gra **bez zapisu** — cudzej sesji nie przejmujemy.
  - Sesja starsza niż 600 s (serwer padł) jest przejmowana.
  - Każdy zapis odświeża czas sesji.
  - Zapis, który zastanie cudzą sesję, nie pisze, a ten serwer przestaje zapisywać gracza.
- **Błędy:**
  - Każde wywołanie jest w `pcall`.
  - Najwyżej 4 próby, z odstępem 1, 2 i 4 s (+ rozrzut).
  - Przed wywołaniem serwer sprawdza budżet zapytań.
  - Nieudane wczytanie NIE kończy się pustym profilem nadpisującym rekord. Gracz gra w pamięci bez zapisu, a w dzienniku
    serwera pojawia się wpis `[StanGracza] zapis: …`.
- **Sprawdzanie i migracja:**
  - `LogikaStanu.migrujProfil` obsługuje wersje 1–4. Uzupełnia brakujące pola wzorem i niczego nie nadpisuje. Profil
    sprzed wersji 4 nie dostaje punktów za dawne poziomy.
  - `czystyProfil` przepuszcza tylko wartości, które da się zapisać. Sprawdza typy i zakresy pól oraz rozmiar: najwyżej
    70 000 wartości i ok. 3 MB.
  - Zepsuty, za duży albo przyszły profil: gracz dostaje świeży profil w pamięci i gra bez zapisu, a rekord zostaje
    nietknięty.
  - Za duży profil przy zapisie: nic się nie zapisuje, bez zapisu częściowego.
- **Studio bez dostępu do usług danych** (to ustawienie gry, którego nie zmieniamy):
  - Pierwsze wywołanie to wykrywa i zapis wyłącza się do końca sesji serwera.
  - Gra działa w pamięci, a w dzienniku jest jeden wpis.
  - Atrybuty kontenera: `ZapisAktywny`, `ZapisStan` oraz liczniki `LicznikWczytan`, `LicznikZapisow`,
    `LicznikBledowZapisu`, `LicznikBezZapisu`.
- **Magazyn:** `BC_StanGracza_v1`, a w Studio `BC_StanGracza_v1_Studio`, więc zapisy ze Studio nie trafiają do gry.

**Co obejmuje (profil wersja 4):**
- Z profilu: poziom, doświadczenie, Złoto, Gemy, shardy, tokeny krain, klasa (atrybut `Class`), trening
  (`wytrenowane`), punkty do rozdania (pula, rozdane, poziom), walki (wygrane, przegrane), awanse, pety (kopie,
  aktywny, premia), wydatki (np. kupione jajka), pokonani strażnicy (Gemy za pierwsze pokonanie) i `pakiety` (dane innych
  pakietów, np. Kowala, przez `Sygnaly/DanePakietu`).
- Atrybuty gracza o przedrostkach:
  - `WidzialPrzelot…` i `PokonalStraznika…` — przeloty i brama każdego biomu; z bramy wynika też odblokowanie krainy
    w teleporcie;
  - `StrojProba_…` — strój z przymierzalni.
- `PamiecGracza` lasu-pasa (ta sama kopia kodu w Bagnie i Dżungli) przy aktywnym zapisie czyta stan z tych atrybutów.
  Przy wyłączonym zapisie działa dokładnie jak dawniej.

**Czego NIE obejmuje i dlaczego:**
- **Drzewko umiejętności Pawła** (atrybut `SkillTree` z zakupami w JSON oraz `ST_*`): to jego plik, a JSON może
  przekroczyć limit napisu w profilu. **Bez tego przy włączonym zapisie Gemy wydane na drzewko przepadną razem
  z drzewkiem.** Drzewko musi trafić do zapisu przed włączeniem (lista niżej).
- **Przedmioty z okna ekwipunku:** dziś istnieją tylko po stronie klienta.
- **Pasek treningu** (malejący zysk w `swiat/trening_proba`) i własne dane innych pakietów, dopóki nie użyją `DanePakietu`.
- **Stan sprzed nagłego padu serwera bez `BindToClose`:** łup walki, który jeszcze nie trafił do profilu, i zmiany od
  ostatniego zapisu (najwyżej ok. 2,5 min).
- **Modyfikatory** z `Sygnaly/Modyfikatory`: z założenia żyją w pamięci serwera. Pakiety odtwarzają je ze swoich
  danych po wejściu gracza.

**Jak włączyć:**
1. W `dane.py` ustaw `ZAPIS_WLACZONY = True` (dla wszystkich) albo w trybie Edit ustaw atrybut kontenera
   `StanGracza.ZapisPostepu = true` (przechodzi na odbudowany kontener). Atrybut działa przy starcie serwera, nie w trakcie
   gry.
2. W Studio włącz w ustawieniach gry: Security → „Enable Studio Access to API Services”. Robią to ludzie, nie agent.
3. Wartości startowe nowego gracza są w `D.zapis.start` (dziś 0 Gemów i 0 Złota).
   - Testowe 1000 Gemów z `PlayerStatsDefaults` nie utrwalą się po cichu: dla nowego gracza serwer stanu nadpisuje je
     wartościami startowymi.
   - Do decyzji: ile Gemów na start (D-099).

**Jak sprawdzić:**
- **Offline:** `python -B swiat/stan_gracza/testy/test_zapisu.py` — 11 scenariuszy na atrapie DataStore.
- **W Studio** (gdy ludzie włączą dostęp do usług danych):
  1. Play.
  2. Zagraj: walka, awans, „+”, jajko, przymierzalnia, Strażnik.
  3. Stop (zapisuje `BindToClose`).
  4. Play jeszcze raz: stan wraca, `ZapisStan` = „włączony”, `LicznikWczytan` = 1.
  5. Blokada: dwa okna Studio (Team Create, ten sam gracz). Drugie okno gra bez zapisu (`StanGraczaZapis` =
     „bez_zapisu”).
- **Na testowym serwerze dziś się nie da:** kontener `StanGracza` działa tylko w Studio. Strażnik `IsStudio` na początku
  skryptów usuwa go poza Studio, jak w pozostałych prototypach. Przeniesienie do gry to osobna decyzja.

**Do włączenia potrzebne po stronie Pawła (co, w którym pliku, po co):**
1. **`src/client/ClassSelectClient`:** czekać na `StanGraczaWczytany ~= false`, zanim pokaże wybór klasy, i nie
   pokazywać go, gdy `Class` wróci z zapisu. Inaczej powracający gracz zobaczy ekran klasy i może ją zmienić (wyścig
   z wczytaniem).
2. **`src/server/ClassSelect.server.luau`:** przyjmować `ChooseClass` tylko wtedy, gdy `Class` jest pusty (D-081: klasę
   wybiera się raz). Dziś klasę można zmienić w każdej chwili, a po włączeniu zapisu zmiana byłaby trwała.
3. **`src/server/SkillTree.server.luau`:** zakupy drzewka (`SkillTree`) zapisywać przez `Sygnaly/DanePakietu` (np. pakiet
   `drzewko`) po `StanGraczaWczytany`, a `ST_*` przeliczać po wczytaniu i przy każdej zmianie (dziś tylko przy starcie
   i przy zakupie). Bez tego zapis gubi drzewko, a wydane na nie Gemy są już odjęte.
4. **`src/server/PlayerStatsDefaults.server.luau`:** wartości testowe (1000 Gemów, statystyki 20/16/18/12/7/57) usunąć
   albo zostawić tylko w Studio. Stan gracza i tak je nadpisze, ale jedno źródło wartości startowych jest czytelniejsze.
5. **(później) `src/server/StatPoints.server.luau`:** „+” powinien sam zdejmować `PunktyDoRozdania`, zamiast dodawać
   punkt za darmo (dziś cofamy go po naszej stronie).
6. **(później) Okno ekwipunku:** przedmioty po stronie serwera — dopiero wtedy da się je zapisać.

**Decyzje ludzi:**
- czy i kiedy włączyć zapis;
- dostęp Studio do usług danych;
- Gemy i Złoto na start;
- czy zapis drzewka (punkt 3) jest warunkiem włączenia — rekomendacja: tak;
- przeniesienie pakietu ze Studio do gry (test na serwerze).

## Co zgłosić Pawłowi
- Jego atrybuty `Level`, `XP`, `XPMax`, `Gold`, `Gems` i sześć statystyk pisze teraz serwer pakietu (XPMax z krzywej,
  statystyki 30 pkt według klasy zamiast 20/16/18/12/7/57). Jego pliki są nietknięte; `PlayerStatsDefaults` dalej
  ustawia tylko brakujące wartości.
- Darmowy „+” (`StatPoints`): od 18.11.2026 serwer stanu zdejmuje za niego punkt z `PunktyDoRozdania`, a bez punktu
  cofa zmianę (rozwiązanie tymczasowe, jego plików nie zmieniamy). Docelowo „+” powinien zapytać stan gracza wprost
  (np. sygnał po stronie serwera) i nie dodawać punktu, gdy puli brak; okno może pokazywać atrybut `PunktyDoRozdania`.
- `ClassData.stats` steruje teraz balansem walki, nie tylko paskami ekranu wyboru.
- `ChooseClass` przyjmuje zmianę klasy w każdej chwili, a D-081 mówi o wyborze tylko przy pierwszym wejściu.
- Drzewko: premie `ST_*` nadal nic nie zmieniają w walce; gałąź gracza ma korzeń „WARRIOR” dla każdej klasy.
- Pod przyszły zapis: `ClassSelectClient` sprawdza `Class` raz, od razu na starcie (wczytanie profilu będzie
  asynchroniczne), a `SkillTree` liczy `ST_*` tylko przy starcie i przy zakupie.
- Tokeny krainy (`TokenyKrainy_<kraina>`) i Shardy Ewolucji (`ShardyEwolucji`) są w atrybutach, ale HUD ich nie pokazuje.

## Sprawdzanie
Bez Studio (wszystko pojedynczo, bez wielu procesów):
```
python -B swiat/stan_gracza/dane.py --sprawdz          # DaneStanu.luau aktualny
python -B swiat/stan_gracza/testy/test_stanu.py        # 56 testów, w tym SerwerStanu i KlientStanu w luau_mini
python -B swiat/stan_gracza/testy/test_zapisu.py       # 11 scenariuszy zapisu postępu na atrapie DataStore
python -B swiat/stan_gracza/sprawdz_luau_stanu.py      # kontrola statyczna Luau
python -B swiat/stan_gracza/zbuduj.py --sucho          # plan budowy
python -B swiat/stan_gracza/symulacja_lasu.py          # szanse w przegrodach lasu-pasa i czas do Strażnika
python -B swiat/stan_gracza/kara_przegranej.py         # warianty kary za przegraną (las, Bagno; --profil pawla)
python -B swiat/stan_gracza/porownaj_profile.py        # profil klas Pawła vs wzorcowy (pytanie 56)
python -B swiat/stan_gracza/punkty_statystyk.py       # punkty do rozdania: warianty × sposób rozdania × profil (D-097)
```
W Studio (część B): `zbuduj.py` buduje kontener; potem wymiana skryptów obu lasów
(`python -B swiat/las_potwory/zbuduj.py --skrypty`, `python -B swiat/las_pas_gra/zbuduj.py --skrypty`) i próba w Play:
```
python -B swiat/stan_gracza/testy/proba_play.py <folder wyników poza repo>   # S00–S15, zrzuty → klatki/
python -B swiat/stan_gracza/testy/proba_play.py --sprawdz                    # bez Studio: parsuje kawałki Luau próby
```
Próba sprawdza: trzy klasy w walce na poziomie gracza, łup dopiero po walce i HUD = atrybuty, baner awansu,
przegraną (+20% XP, kara Złota i napis — S06, S13; dopisane 17.11, jeszcze nieuruchomione), trening Siły → Strength → opis bohatera, tryb testowy `TestBohater`, brak sygnału i usunięcie
kontenera (las działa jak dawniej), konsolę, `script_grep` po innych piszących Gold / XP / DataStore / leaderstats,
oraz pomiar poprawki M6 lasu (15 podejść prawdziwym E z dawną kotwicą i 15 z nową; dymek przy blokadzie po walce).
Wyniki mogą zawierać nazwę konta, dlatego folder wyników musi być poza repozytorium; zrzuty są bez listy graczy i czatu.
`--tylko-m6` powtarza sam pomiar M6 (gracz staje 4,5 studa od potwora i wciska E po 1,5 s, jak człowiek).

Wynik w Studio 17.11.2026 (13:50–14:15): S00–S12 OK; M6 — walka ruszyła w 5 z 15 prób z dawną podpowiedzią i w 13 z 15
po poprawce (histereza zasięgu 7 przy zapasie serwera 10; obie nieudane dały dymek „Podejdź bliżej potwora…”).

Zatrzymanie potworów przy graczu (runda 3, 17.11.2026, propozycja): `--tylko-m6 --m6-zatrzymanie` mierzy „przed” bez
zatrzymań (`TestBezZatrzyman` na `LasPasGra`) i „po” z nimi, zapisuje stan celu przy E (Stan, przesunięcie, odchylenie
kierunku od gracza) i robi zrzuty `swiat/las_potwory/klatki/stop_*.jpg` (kamera z boku pary); `--reakcja <s>` zmienia
czas do E. Wynik: przy 1,5 s 15/15 przed i 15/15 po; przy 3 s 7/15 przed i 15/15 po — przy E stało 3 z 15 potworów
przed i 15 z 15 po, wszystkie 15 zwrócone do gracza, średnie przesunięcie 12,9 → 0,5 studa.

Noc 17/18.11.2026 (Studio): po pełnej przebudowie `StanGracza` próba `--bez-m6` S00–S14 OK (S00 „?” jak zawsze;
S06 400 → 380 Złota, S13 napis „Przegrana: −20 Złota, +34 doświadczenia”, S14 punkty 10 → „+” 9 → 0 → kolejny „+”
cofnięty z napisem). Przejście prawdziwymi kliknięciami (awans o 2 poziomy → licznik „Punkty do rozdania: 10” →
EQUIPMENT w HUD → „+” przy Szczęściu 10 razy → 11. „+” cofnięty, napis „Brak punktów — zdobądź poziom”; Gemy
1000 → 1020 za dwa awanse): zrzuty `klatki/pkt_1…5`. Serwer `StatPoints` Pawła nie nadpisuje cofnięcia.
Uwaga z tej nocy: `luau_mini` widzi lokalne funkcje zdefiniowane niżej w pliku, a Luau w Studio nie — tak padło
`dopisz()` w `przyznajPunkty` (awans bez punktów i bez banera); test `7f` pilnuje teraz kolejności definicji.

## Liczby z symulacji (17.11.2026, propozycja)
Bohater na prawdziwym poziomie, bez treningu: pierwsza przegroda (Leśny Slime poz. 1) na poziomie 1 to 84–88% wygranych.
Przejście lasu-pasa do wygranej ze Strażnikiem: mediana ok. 27 min przy walkach ×1 (Mag 25, Wojownik i Zwiadowca 28),
ok. 19 min przy ×2. Gracz dochodzi do Strażnika na 10. poziomie i wygrywa z nim na 11., zwykle za drugim razem,
z ok. 8 przegranymi po drodze. Cel planu rosnącego z `tools/walka/tempo.py`: ok. 30 min na Las. Pełne tabele:
`python -B swiat/stan_gracza/symulacja_lasu.py --md <plik>`.

## Pliki
- `dane.py` → `zrodla/DaneStanu.luau` (wygenerowany; liczby z `tools/walka/wzorcowe.py`, `tempo.py`,
  `src/server/Walka/Statystyki.luau`), `logika_stanu.py` (lustro `zrodla/LogikaStanu.luau`).
- `zrodla/SerwerStanu.server.luau`, `zrodla/KlientStanu.client.luau`, `zrodla/LogikaStanu.luau`, `zrodla/ZapisStanu.luau`
  (zapis postępu, domyślnie wyłączony), `testy/test_zapisu.py`.
- `zbuduj.py`, `sprawdz_luau_stanu.py`, `symulacja_lasu.py`, `kara_przegranej.py` (warianty kary; gracze z
  `swiat/pety_proba/ekonomia_jajek.py`, tylko uruchamiany), `porownaj_profile.py` (pytanie 56), `punkty_statystyk.py` (D-097), `testy/test_stanu.py`,
  `testy/atrapa_roblox.py`.
- Zmiany w innych pakietach (małe, w osobnych funkcjach): `swiat/las_potwory/zrodla/Stale.luau` (stałe stanu gracza),
  `SerwerPotworow.server.luau` (`sygnalStanu`, `bohaterZeStanu`, `nagrodaZaWalke` + dwa wywołania w kontroli 7
  i po przyjęciu walki), `KlientPotworow.client.luau` (`trybTestowyBohatera`, `poziomGracza`,
  `zsynchronizujBohatera`, napis panelu). Las-pas używa tych samych źródeł.
