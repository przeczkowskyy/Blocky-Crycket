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
- **Profil:** jedna tabela na gracza z polem `wersja`; od 19.11.2026 zapisywana między sesjami (D-110, rozdział
  „Zapis postępu”).
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
| `Sygnaly/Pety` (BindableFunction, 17.11) | pety → stan | `"kup", gracz, { ile, zrodlo, cel, pet, premia }` (wydatek + kopia peta w jednym wywołaniu) · `"aktywny", gracz, { pet, premia }` \| `{ odstaw = true }` · `"stan", gracz` · `"przychod", gracz, { ile, zrodlo, cel }` → `{ ok, zloto, ile }` (25.11.2026: Rybki spoza walki — zagroda petów; źródło z listy `PAKIETY_PRZYCHODOW`, kwota 1…`D.przychody.kwota_maks`, dopisane do `Gold` jak łup, bez premii z modyfikatorów i bez licznika walk) · `"sprzedaj", gracz, { pety = { [id] = n }, ile, zrodlo, cel }` → `{ ok, zloto, ile, kopie }` (26.11.2026: sprzedaż petów — kopie zabrane i Rybki dopisane jednym wywołaniem; za mało kopii → `nie_masz`, ostatnia kopia peta za graczem → `aktywny`, nic nie zmienione; źródło i kwota jak przy `przychod`) |
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
- **Punkty statystyk od 27.11.2026 (D-165 — decyzja Karola, czeka na Pawła; zmienia D-140):** `PUNKTY_DO_ROZDANIA` = 0, `PUNKTY_SAMO_NA_POZIOM` = 10 — za poziom 10 punktów rozdzielanych samo, licznik „Punkty do rozdania” znika (stara niewydana pula wraca jako punkty rozdzielane samo). Serwer wystawia atrybuty `Wytrenowane<Atrybut>` dla limitu treningu AFK (`src/shared/TreningAFKDane.luau`). Opis niżej to stan z 18.11. Raport: `swiat/przejscie_gry/BALANS_2711.md`.
- **Punkty statystyk (18.11.2026):** w `dane.py` dwie liczby: `PUNKTY_DO_ROZDANIA` (5, z D-097) i
  `PUNKTY_SAMO_NA_POZIOM` (5 — wariant b; **0 = czysty wariant D-097**, tylko 5 do rozdania); potem
  `python -B swiat/stan_gracza/dane.py` i `zbuduj.py --skrypty`. Atrybut kontenera `PunktyStatystyk = false` w czasie
  gry — jak przed D-097 (10 samo na poziom, darmowy „+”, bez licznika); przechodzi na odbudowany kontener.
- **Gemy (D-099):** `GEMY_ZA_POZIOM` (10) i `GEMY_ZA_STRAZNIKA` (100) w `dane.py`; 0 wyłącza.
- **„Szczęście początkującego” (18.11.2026):** `SZCZESCIE_POCZATKUJACEGO` w `dane.py` (1,75, czyli ×2,75; 0 = wyłączone) albo atrybut
  kontenera `SzczesciePoczatkujacego = false`.
- **Zapis postępu:** włączony od 19.11.2026 (D-110); atrybut kontenera `ZapisPostepu = false` wyłącza, kasowanie własnego
  zapisu `zbuduj.py --kasuj-zapis --tak` — rozdział „Zapis postępu”.
- **Tryb testowy lasu:** atrybut kontenera lasu `TestBohater = true` (`Workspace/LasPotwory` albo `Workspace/LasPasGra`)
  — reguła testowa T1 jak dawniej (klasa i poziom z panelu), walki bez łupu. Ustawiają go próby w Play
  (`swiat/las_potwory/testy/proba_play.py`, `kontrola_play.py`, `swiat/las_pas_gra/testy/proba_play.py`,
  `proba_dodatkowa.py`).

**Jak dodać pakiet (jedno miejsce, 18.11.2026):** listy kontenerów, które rozmawiają ze stanem gracza, są na górze
`dane.py`: `PAKIETY_BIOMOW` (walki biomu — łup przez `PrzyznajLup` i kara za przegraną; dziś `LasPotwory`,
`LasPasGra`, `BagnoPasGra` i od razu `DzunglaPasGra`) i `PAKIETY_WYDATKOW` (wydawanie Złota — `PetyProba`,
`KowalProba`, od 27.11.2026 `TreningAFK` — sklep trenera w skrypcie Pawła: ulepszenia stanowisk i wzmacniacze, cele
`trening_ulepszenie` / `trening_wzmacniacz`, dane w profilu przez `DanePakietu`, pakiet `TreningAFK`), od 25.11.2026 też `PAKIETY_PRZYCHODOW` (dopisywanie Złota / Rybek poza walką przez `Pety("przychod")` — `PetyProba`, zagroda petów). Nowy pakiet: dopisz nazwę jego kontenera, `python -B swiat/stan_gracza/dane.py`, testy, potem
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
   jego sześć statystyk w walce ×2,75 (`SZCZESCIE_POCZATKUJACEGO = 1.75`). Działa przez wewnętrzne źródło
   `szczescie_poczatkujacego` w `Modyfikatory` (pole silnika `pet`), bez napisu dla gracza. Znika po pierwszej wygranej;
   przegrana go nie zdejmuje.
   - Po D-096 w pierwszej zagrodzie chodzą slime'y 1.–3. poziomu rozdane po miejscach, a gracz podchodzi do najbliższego
     (w próbach dymnych pierwsza walka przegrana 2 razy na 7 przy ×1,75).
   - ×2,75 to najmniejszy mnożnik, przy którym każda klasa wygrywa ze slime'em 3. poziomu w co najmniej 95% walk.

   Szansa pierwszej walki: rozkłady wzorcowe, bohater 1. poziomu bez przedmiotów z łupu i bez peta, 700 walk na
   komórkę (×2,6 i ×2,75 — 1000 walk); kolejno Wojownik / Zwiadowca / Mag:

   | Mnożnik | Slime 1. poziomu | Slime 2. poziomu | Slime 3. poziomu |
   |---|---|---|---|
   | bez premii | 86 / 84 / 85% | 36 / 35 / 43% | 8 / 6 / 15% |
   | ×1,75 (było) | 100 / 99 / 99% | 92 / 89 / 88% | 72 / 61 / 58% |
   | ×2,5 | 100 / 100 / 100% | 99 / 99 / 99% | 94 / 94 / 91% |
   | ×2,6 | — | — | 94 / 94 / 93% |
   | **×2,75 (wybrany)** | **100%** | **99–100%** | **96 / 96 / 95%** |
   | ×3 | 100% | 100% | 98 / 98 / 98% |
   | ×4 | 100% | 100% | 100% |

   - Przy profilu z `ClassData` (tryb `classdata`) ×2,75 daje: slime 1. poziomu 100%, 2. poziomu 95–99%, 3. poziomu
     79–94% (Mag najsłabszy).
   - **Czy da się to nadużyć** (gracz bez wygranej idzie od razu na mocniejszego potwora; wygrane Wojownik / Zwiadowca
     / Mag i poziom po jednej wygranej, normalnie po pierwszej walce jest 2. poziom):

     | Przeciwnik | Wygrane | Poziom po jednej wygranej |
     |---|---|---|
     | Muchomornik 3. poziomu | 98–99% | 2. |
     | Muchomornik 5. poziomu | 74–81% | 2. |
     | Wilk 6. poziomu | 53–61% | 2. |
     | Wilk 8. poziomu | 28–41% | 3. |
     | Troll | 2–4% | 4. |
     | Strażnik Gaju | 0% | — |

   - Wniosek: najwięcej da się zyskać 1–2 poziomy jedną walką, po kilku przegranych i dojściu przez pół lasu — mniej,
     niż gracz zdobywa w tym czasie zwykłą grą. Nadużycie nie jest realne, więc premii nie ograniczam do poziomu
     potwora. Byłoby to też trudne: sygnał `Bohater` nie dostaje dziś przeciwnika, a zmiana dotknęłaby wspólnego kodu
     lasu-pasa.
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
   ekranu walki), a gracz widzi napis „Przegrana: −N Rybek, +M doświadczenia” (od 26.11.2026 Rybki, D-146, z odmianą
   „−1 Rybka / −3 Rybki / −5 Rybek”; formy w `D.kara.formy_rybki`) (na dole ekranu, tuż nad napisem
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
9. **Rozkłady klas (18.11.2026: robocza decyzja Karola z pytania 56 — odpowiedź „b”, czeka na potwierdzenie Pawła):**
   walka i punkty statystyk według rozkładów **wzorcowych** (`tools/walka/wzorcowe.py`). Profil z
   `src/shared/ClassData.luau` (Paweł, plik nietknięty) zostaje tylko na karcie wyboru klasy.
   - Ustawienie: `ROZKLADY_KLAS = "wzorcowe"` w `dane.py` albo `"classdata"`, czyli zachowanie sprzed 18.11 (punkty
     według ClassData).
   - Atrybut kontenera `RozkladyKlas` (`"wzorcowe"` / `"classdata"`) przełącza w Studio bez przebudowy. Przechodzi na
     odbudowany kontener. Przy przełączeniu w czasie gry trening, rozdane punkty i „+” zostają.
   - `RozkladyZ` mówi, skąd są rozkłady, np. „wzorcowe (tools/walka); karta klasy pokazuje profil ClassData — inny dla:
     …”. Ostrzeżenie „(balans!)” pojawia się tylko w trybie `classdata`.
   - Testy liczą oczekiwania z wybranego trybu. Cała paczka scenariuszy w drugim trybie:
     `STAN_ROZKLADY=classdata python -B swiat/stan_gracza/testy/test_stanu.py`.

   Las po D-096, punkty 5 + 5, rozdane jak klasa (150 graczy na klasę):

   | Klasa | Tryb | 1. walka (bez / ze szczęściem) | Strażnik Gaju za 1. razem | Las | Przegrane |
   |---|---|---|---|---|---|
   | Wojownik | wzorcowe | 85% / 100% | ok. 33–39% | 27,5 min | 7–8 |
   | Wojownik | classdata | 79% / 99% | ok. 24–26% | 32–33 min | 10–11 |
   | Zwiadowca | wzorcowe | 84% / 100% | ok. 34–39% | 28 min | 8–9 |
   | Zwiadowca | classdata | 76% / 98% | ok. 33–35% | 30–31 min | 11–12 |
   | Mag | wzorcowe | 84% / 99% | ok. 36–37% | 25 min | 7–8 |
   | Mag | classdata | 75% / 94–95% | ok. 24–29% | 29 min | 12–13 |

   Szczęście początkującego: od 18.11 (noc) ×2,75 — ze względu na slime'y 2. i 3. poziomu w pierwszej zagrodzie
   (punkt 2b). Kolumna „1. walka” w tabeli wyżej liczy slime'a 1. poziomu przy dawnym ×1,75.
10. **Baner „POZIOM N”** to tymczasowe GUI pakietu; docelowe pop-upy projektuje Paweł (D-093).
11. **Bez zapisu:** profil w pamięci serwera; po wyjściu z gry wszystko znika (jak dziś). Miejsce na zapis: profil
    (`L.nowyProfil`, pole `wersja`), `swiat/las_pas_gra/zrodla/PamiecGracza.luau`.
12. **Pety (17.11.2026):** premia peta do łupu poza silnikiem walki (D-059 mówi o mnożniku statystyk — następny krok),
    pierwszy kupiony pet od razu aktywny, jedna kwota wydatku najwyżej 1 000 000 Złota.

## Zapis postępu (WŁĄCZONY 19.11.2026 decyzją D-110 — podpis Karola, czeka na potwierdzenie Pawła)
Kod zapisu powstał 18.11.2026 i był sprawdzony na atrapie; 19.11.2026 jest włączony domyślnie (`ZAPIS_WLACZONY = True`
w `dane.py`). Działa tylko w Studio (prototypy gry żyją w Studio) i pisze do magazynu Studio `BC_StanGracza_v1_Studio`,
nie do magazynu opublikowanej gry. Zasady: skill projektu `roblox-data` (DataStore, blokada sesji, `UpdateAsync`,
migracja, cykl życia zapisu).

**Stan na 19.11.2026 — skrót dla człowieka:**
- Wchodzisz do gry (Play) → wraca poziom, doświadczenie, Złoto, Gemy, punkty, klasa, przedmioty (także ze sklepu)
  z ulepszeniami i strojem, pety, trening, pokonani Strażnicy i otwarte bramy, obejrzane przeloty. Zapis co ok. 2 min,
  przy wyjściu i przy Stop.
- **Zacząć od zera:** w trybie Edit `python -B swiat/stan_gracza/zbuduj.py --kasuj-zapis` (podgląd: co jest zapisane),
  potem `python -B swiat/stan_gracza/zbuduj.py --kasuj-zapis --tak` (kasuje zapis gracza zalogowanego w Studio, tylko
  w magazynie Studio; przy świeżej sesji — gra trwa — odmawia). Następne Play zaczyna nowego gracza. Rekord przez 30 dni
  da się odzyskać z wersji magazynu.
- **Wyłączyć:** atrybut kontenera `StanGracza.ZapisPostepu = false` w trybie Edit (działa od następnego Play, przechodzi
  na odbudowany kontener) albo `ZAPIS_WLACZONY = False` w `dane.py` + `dane.py` + `zbuduj.py --skrypty`.
- **Próby gry (agenci) zaczynają od świeżego gracza i nie dotykają zapisu człowieka** (niżej: „Próby gry a zapis”).
- Nie zapisuje się jeszcze: drzewko umiejętności i przedmioty z okna ekwipunku (pliki Pawła — lista niżej),
  `PoznaneGatunki` (POMIŃ przy znanym gatunku walki). Wybór klasy pokaże się powracającemu graczowi jeszcze raz (Paweł).

**Jak sprawdzić, że zapis działa (Studio, tryb Edit — robi człowiek):**
1. Pierwsze wejście: Play. Na kontenerze `Workspace/StanGracza` (podczas gry, widok Server) `ZapisStan` = „włączony”,
   a u gracza `StanGraczaZapis` = „aktywny”. Pierwszy raz zaczynasz od nowego gracza (poziom 1, 0 Złota, 0 Gemów).
2. Zagraj chwilę: walka, kupno u zbrojmistrza, jajko, mini-gra. Zapamiętaj poziom i Złoto z HUD.
3. Stop. Odczekaj kilka sekund (zapis wyjścia kończy się po powrocie Studio do Edit).
4. Podgląd bez gry: `python -B swiat/stan_gracza/zbuduj.py --kasuj-zapis` — pokazuje zapisany poziom, Złoto, Gemy i klasę.
5. Play jeszcze raz: HUD ma ten sam poziom i Złoto, przedmioty i pet wracają. Ekran wyboru klasy jeszcze się pokaże
   (poprawka po stronie Pawła) — wybierz tę samą klasę, bo inna zostałaby zapisana. Od zera: Stop, potem
   `zbuduj.py --kasuj-zapis --tak`.

**Wynik próby w Studio 19.11.2026 (14:32–14:34, `testy/proba_zapisu.py`, magazyn próby): Z00–Z08 OK.**
- Z00: zwykła próba gry — „wyłączony (próba gry)”, bez wczytywania. Z01: nowy gracz w magazynie próby, wczytanie ok. 1 s.
- Z02: klasa Wojownik, łup → poziom 6, „+” ×2 (Szczęście), kupno w sklepie przedmiotu stopnia leśnego („Pas Leśnika
  z Sakiewką”, 100 Złota, od razu założony), ulepszenie u kowala do poziomu 1, przymierzalnia (zdjęta broń), jajko leśne
  (pet aktywny), mini-gra Siły (autogra: 4 punkty), Strażnik Gaju (+100 Gemów, brama), przelot lasu.
- Z03–Z04: po Stop i ponownym Play wróciło wszystko co do wartości: poziom 6, XP 33/206, Złoto 3501, Gemy 150, klasa
  Warrior, punkty do rozdania 23 (rozdane 2 w Szczęście), statystyki, pet aktywny i 1 kopia, kupione jajka i licznik
  wydatków, przedmioty kowala z ulepszeniem i 49 materiałami, strój, trening (4 punkty Siły i pasek 80,25), Strażnik i
  brama, przelot; czas wczytania 0,9–1,6 s. Kupiony pas po powrocie: posiadany, „założone” w sklepie, w stroju i na
  bohaterze walki u klienta (Z04b).
- Z05: 2 błędy usługi przy zapisie wyjścia — ponowienie się udało (Złoto 3512 w rekordzie).
- Z06: usługa pada cały czas — po ok. 7 s „bez_zapisu”, gra w pamięci (łup dochodzi), rekord po Stop identyczny.
- Z07: rekord próby skasowany, znaczniki zdjęte. Z08: bez błędów skryptów w konsoli.
- Prawdziwy zapis człowieka: podgląd `--kasuj-zapis` rozpoznaje gracza zalogowanego w Studio i pokazuje „brak zapisu”
  przed próbami i po nich (19.11, przed pierwszym wejściem człowieka); nic nie skasowane ani nadpisane.
- Regresja 19.11 (14:35–15:08, `regresja_calosci.py` „proba dymna, stan gracza, kowal, pety, trening, sklep, stroje,
  cutscenka, zapis”): każda próba z wierszem `ZapisStan = wyłączony (próba gry)` w dzienniku (próba zapisu: 1× ten,
  3× „włączony (magazyn próby)”); bez błędów poza próbą dymną: D02 (kamera po przelocie została „Scriptable”) i zależne
  od niego D12, D05 — powtórka 15:09 14 z 14, więc jednorazowe. Po regresji znaczników nie ma.

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
  - Atrybuty kontenera: `ZapisAktywny`, `ZapisStan`, `ZapisMagazyn` (nazwa magazynu, 19.11) oraz liczniki
    `LicznikWczytan`, `LicznikZapisow`, `LicznikBledowZapisu`, `LicznikBezZapisu`. Atrybuty gracza: `StanGraczaWczytany`,
    `StanGraczaZapis` („aktywny” / „bez_zapisu”), `StanGraczaWczytanieMs` (czas wczytania, 19.11).
- **Magazyn:** `BC_StanGracza_v1`, a w Studio `BC_StanGracza_v1_Studio`, więc zapisy ze Studio nie trafiają do gry.

**Próby gry a zapis (19.11.2026, D-110).** Każda próba w Play (`proba_play.py` wszystkich pakietów, `SesjaPlay`,
`swiat/przejscie_gry/regresja_calosci.py`) włącza Play przez `tools/studio_mcp.py`, a ten każde `start_stop_play`
przepuszcza przez `tools/zapis_prob.py`:
- przed Play (tryb Edit) stawia na kontenerze znacznik `ZapisProbaDo` = `os.time()` + 900 s (`D.zapis.proba`);
- serwer stanu czyta znacznik tylko przy starcie: przy znaczniku **nie otwiera magazynu** — gracz jest świeży i w pamięci,
  dokładnie jak przed D-110 (`ZapisStan` = „wyłączony (próba gry)”); zaraz po Play `zapis_prob` odczytuje `ZapisStan`
  z serwera i wypisuje go do dziennika próby (`[zapis_prob] Play ze znacznikiem próby: ZapisStan = …`);
- po Stop znacznik jest zdejmowany. Gdy próba padnie przed Stop, znacznik sam wygasa po kwadransie (do tego czasu Play
  człowieka też idzie bez zapisu — nic nie ginie, tylko nie wczytuje się postęp);
- kontener jest, a znacznika nie da się ustawić → Play nie startuje (próba kończy się błędem, zapis nietknięty);
- jedyny wyjątek: próba zapisu (`testy/proba_zapisu.py`) dokłada `ZapisProbaMagazyn = true` → serwer pracuje na osobnym
  magazynie `BC_StanGracza_v1_Studio_Proba` (tylko tam działa atrapa błędów usługi `ZapisProbaBledy`). Ten znacznik bez
  `ZapisProbaDo` nic nie znaczy.
- Agent, który włącza Play narzędziem MCP sesji (z pominięciem `tools/studio_mcp.py`), stawia znacznik ręcznie:
  `python -B tools/zapis_prob.py start`, a po Stop `python -B tools/zapis_prob.py koniec` (`stan` — podgląd).
- Uwaga Team Create: znacznik jest atrybutem miejsca, więc w czasie próby (do 15 min) Play drugiej osoby też idzie bez
  zapisu. Ctrl+Z tuż po próbie może przywrócić świeży znacznik (punktów historii nie stawiamy) — wygasa sam.
Dowód bez Studio: `test_zapisu.py` z12–z14 (próba nawet nie otwiera magazynu, prawdziwy rekord nietknięty; znacznik
z `tools/zapis_prob.py` przeniesiony z „Edit” do serwera; kolejność wywołań MCP).

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

**Pakiety → co trafia do zapisu (spis 19.11.2026):**

| Pakiet | Co się zapisuje (i gdzie w profilu) | Domknięte 19.11.2026 |
|---|---|---|
| stan gracza | poziom, XP, Złoto, Gemy, shardy, tokeny krain, klasa (`idKlasy`), rasa (`idRasy`, od 27.11.2026), punkty do rozdania (pula, rozdane), walki, awanse, wytrenowane punkty statystyk | 27.11.2026 (Karol: „Tak, zapisuj rasę”): atrybut `Race` (rasy z `src/shared/RaceData.luau` → `D.rasy_gracza`) wraca razem z `Class`, rasa ustawiana tuż przed klasą — ekran wyboru Pawła sam się pomija, a kot rasy stoi od razu. Pole nieobowiązkowe, bez zmiany wersji profilu: profil sprzed 27.11 (bez `idRasy`) = gracz bez rasy, ekran ras jak dotąd; rasa spoza listy nie trafia do zapisu, a profil z taką rasą odrzuca `czystyProfil` („zla_rasa”). Test `test_zapisu.py` z2b; Play 27.11 na magazynie próby: wybór rasy → Stop → Play 2: `Race` i `Class` z zapisu, ekranu wyboru brak, kot od pierwszej sekundy |
| kowal + sklep (`swiat/kowal_proba`, `swiat/sklep_proba`) | posiadane przedmioty (także kupione w sklepie) z poziomem ulepszenia, zapasy, materiały — `pakiety.kowal`; założone = strój z przymierzalni | kowal czekał na `StanGraczaWczytany` tylko teoretycznie: brał gracza za nowego w trakcie wczytywania i pierwsza zmiana nadpisywała zapisane przedmioty. Teraz odkłada stan do końca wczytania i wtedy czyta profil |
| przymierzalnia (`swiat/stroje_proba`) | atrybuty `StrojProba_<klasa>` | — |
| pety (`swiat/pety_proba`) | kopie, aktywny pet, premia, kupione jajka (`pety`, `wydatki`) | skill aktywnego peta (Modyfikatory) i ceny jajek ustawiały się w trakcie wczytywania (odmowa) — teraz po wczytaniu |
| mini-gry (`swiat/trening_proba`) | wytrenowane punkty (`wytrenowane`) oraz punkty mini-gier `Trening…` i pasek malejącego zysku — `pakiety.trening` | pasek i punkty sesji ginęły przy wyjściu (malejący zysk wracał do zera) — teraz przez `DanePakietu`, odczyt po wczytaniu, zapis przy nowym punkcie i po rundzie |
| biomy (las-pas, Bagno, Dżungla) | `PokonalStraznika…` (brama, odblokowanie krainy w teleporcie), `WidzialPrzelot…`, pokonani strażnicy (`straznicy`, Gemy za pierwsze pokonanie) | — |
| cutscenka biomu | `WidzialPrzelot…` (ten sam atrybut co biom) | — |
| poza listą | `PoznaneGatunki` (pamięć walk TestWalki2: POMIŃ przy znanym gatunku) — nie zapisuje się; wybór klasy i drzewko — pliki Pawła (niżej) | — |

**Czego NIE obejmuje i dlaczego:**
- **Drzewko umiejętności Pawła** (atrybut `SkillTree` z zakupami w JSON oraz `ST_*`): to jego plik, a JSON może
  przekroczyć limit napisu w profilu. **Bez tego przy włączonym zapisie Gemy wydane na drzewko przepadną razem
  z drzewkiem.** Do czasu zmiany po stronie Pawła drzewko się nie zapisuje (D-110).
- **Przedmioty z okna ekwipunku:** dziś istnieją tylko po stronie klienta.
- **`PoznaneGatunki`** (TestWalki2) i własne dane innych pakietów, dopóki nie użyją `DanePakietu`.
- **Stan sprzed nagłego padu serwera bez `BindToClose`:** łup walki, który jeszcze nie trafił do profilu, i zmiany od
  ostatniego zapisu (najwyżej ok. 2,5 min).
- **Modyfikatory** z `Sygnaly/Modyfikatory`: z założenia żyją w pamięci serwera. Pakiety odtwarzają je ze swoich
  danych po wczytaniu profilu (kowal, pety — 19.11.2026).

**Jak włączyć / wyłączyć:**
1. Włączony od 19.11.2026: `ZAPIS_WLACZONY = True` w `dane.py`. Wyłączyć: `False` (dla wszystkich) albo w trybie Edit
   atrybut kontenera `StanGracza.ZapisPostepu = false` (przechodzi na odbudowany kontener). Atrybut działa przy starcie
   serwera, nie w trakcie gry.
2. Studio ma dostęp do usług danych gry (Security → „Enable Studio Access to API Services”; ustawiają ludzie).
3. Wartości startowe nowego gracza są w `D.zapis.start` (dziś 0 Gemów i 0 Złota).
   - Testowe 1000 Gemów z `PlayerStatsDefaults` nie utrwalą się po cichu: dla nowego gracza serwer stanu nadpisuje je
     wartościami startowymi.
   - Do decyzji: ile Gemów na start (D-099).
4. Pakiety, które trzymają dane w profilu, czekają na `StanGraczaWczytany ~= false` i po zmianie na `true` czytają profil
   jeszcze raz (kowal, pety, trening — wzór dla nowych pakietów).

**Jak sprawdzić:**
- **Offline:** `python -B swiat/stan_gracza/testy/test_zapisu.py` — 14 scenariuszy na atrapie DataStore (z12–z14: próby
  gry i magazyn próby).
- **W Studio, na magazynie próby:** `python -B swiat/stan_gracza/testy/proba_zapisu.py <folder poza repo>` — Z00–Z08
  (zwykła próba bez zapisu; nowy gracz; gra: klasa, łup i awans, „+”, sklep, ulepszenie, przymierzalnia, pet, mini-gra,
  Strażnik, przelot; Stop; Play: stan wrócił co do wartości, czas wczytania; błąd przy zapisie wyjścia; usługa padająca
  cały czas — gra w pamięci, rekord nietknięty; sprzątanie; konsola). Jest też w `regresja_calosci.py` („zapis”).
- **Ręcznie w Studio:** Play → zagraj → Stop → Play: stan wraca, `ZapisStan` = „włączony”, `LicznikWczytan` = 1.
  Blokada: dwa okna Studio (Team Create, ten sam gracz) — drugie gra bez zapisu (`StanGraczaZapis` = „bez_zapisu”).
- **Na testowym serwerze dziś się nie da:** kontener `StanGracza` działa tylko w Studio. Strażnik `IsStudio` na początku
  skryptów usuwa go poza Studio, jak w pozostałych prototypach. Przeniesienie do gry to osobna decyzja.

*19.11.2026: zapis jest włączony bez tych zmian (D-110). Do czasu ich wdrożenia powracający gracz może zobaczyć ekran
klasy i ją zmienić, a drzewko umiejętności się nie zapisuje. Lista bez zmian:*

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
- ~~czy i kiedy włączyć zapis~~ — włączony 19.11.2026 (D-110, podpis Karola; czeka na Pawła);
- ~~dostęp Studio do usług danych~~ — włączony (19.11.2026);
- Gemy i Złoto na start;
- czy zapis drzewka (punkt 3) jest warunkiem włączenia — D-110: nie; do zmiany Pawła drzewko się nie zapisuje;
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
python -B swiat/stan_gracza/testy/test_zapisu.py       # 14 scenariuszy zapisu postępu na atrapie DataStore
python -B swiat/stan_gracza/testy/proba_zapisu.py --sprawdz   # bez Studio: kawałki Luau próby zapisu
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
  (zapis postępu, włączony 19.11.2026), `testy/test_zapisu.py`, `testy/proba_zapisu.py` (próba w Studio na magazynie
  próby); znacznik prób gry: `tools/zapis_prob.py` (woła go `tools/studio_mcp.py` przy każdym `start_stop_play`).
- `zbuduj.py`, `sprawdz_luau_stanu.py`, `symulacja_lasu.py`, `kara_przegranej.py` (warianty kary; gracze z
  `swiat/pety_proba/ekonomia_jajek.py`, tylko uruchamiany), `porownaj_profile.py` (pytanie 56), `punkty_statystyk.py` (D-097), `testy/test_stanu.py`,
  `testy/atrapa_roblox.py`.
- Zmiany w innych pakietach (małe, w osobnych funkcjach): `swiat/las_potwory/zrodla/Stale.luau` (stałe stanu gracza),
  `SerwerPotworow.server.luau` (`sygnalStanu`, `bohaterZeStanu`, `nagrodaZaWalke` + dwa wywołania w kontroli 7
  i po przyjęciu walki), `KlientPotworow.client.luau` (`trybTestowyBohatera`, `poziomGracza`,
  `zsynchronizujBohatera`, napis panelu). Las-pas używa tych samych źródeł.

## Łup po szybko pominiętej walce — od razu (19.11.2026, D-107)

*Mała zmiana przy decyzji D-107 (walka bez przestojów; podpis Karola, czeka na potwierdzenie Pawła). Wdrożona w Studio
19.11.2026 (`zbuduj.py --skrypty`).*

Łup walki pokazuje się graczowi (atrybuty Gold, XP…), gdy klient zgłosi koniec ekranu walki („pokaz”), ale tylko łupy
starsze niż `publikacja.min_s` (1,5 s) — żeby spóźnione zgłoszenie nie pokazało łupu następnej walki w jej trakcie.
Pominięta walka kończy się u klienta w ok. 0,5 s (pomiar w Play 19.11), więc zgłoszenie przychodzi, zanim łup
„dojrzeje” — według kodu gracz widziałby wtedy Złoto i doświadczenie dopiero przy końcu następnej walki albo po
czasie walki + 6 s (samego opóźnienia w grze nie mierzyłem).

Teraz: gdy przy zgłoszeniu zostaje łup młodszy niż `min_s`, serwer sam pokazuje go, gdy tylko dojrzeje (najwyżej 1,5 s
po przyjęciu walki) — tylko łupy przyjęte przed tym zgłoszeniem; łup następnej walki dalej czeka na jej koniec.
Kod: `zrodla/SerwerStanu.server.luau` (obsługa „pokaz”, `publikuj(…, doCzasu)`), test `test_8c2` w `testy/test_stanu.py`.
Sprawdzone testem bez Studio na prawdziwym skrypcie serwera; próba „stan gracza” w Play 19.11 przeszła, ale tego
przypadku osobno nie mierzy.
Do oceny: skrócić `min_s` (np. do 0,5 s), jeśli 1,5 s opóźnienia po bardzo szybkim pominięciu ma zniknąć całkiem.
