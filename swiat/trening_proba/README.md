# Training Center — próba sześciu mini-gier

*Status: **propozycja** (17.11.2026). **Siła i Pancerz wdrożone w Studio i sprawdzone w trybie Play 17.11.2026 przed
południem** (etap B): lista T01–T14 zaliczona, zrzuty z gry w `klatki/`, wyniki w „Co sprawdzone w grze”. **Cztery
nowe mini-gry (Kondycja „Bieżnia”, Zręczność „Kłody”, Inteligencja „Runy”, Szczęście „Koniczyny”) — noc 17/18.11:
zaprogramowane i sprawdzone offline (część A), a 18.11.2026 o 00:51–01:40 zbudowane w Studio i sprawdzone w trybie
Play (część B: lista T01–T22 — 22 × OK)**; podglądy brył w `podglady/`, zrzuty z gry w `klatki/` (09–25), wyniki
w „Noc 17/18.11” i „Część B”. **18.11.2026 (dzień): wygląd jak w walce — kamery pod kątami ekranu walki, komiksowe
napisy, efekty 3D trafień, konfetti i radość po rundzie — zaprogramowane, sprawdzone offline (54 testy), a o 09:50–11:00
wdrożone w Studio i sprawdzone w trybie Play z bohaterem klasy (część B: lista T01–T27 — 27 × OK)** (sekcja „Wygląd jak
w walce”; nowy wygląd pokazują zrzuty 26–79 w `klatki/`, zrzuty 01–25 są sprzed tej zmiany).
Opis sześciu mini-gier, wybory dla ludzi i ustawienia „przyjęte, do zmiany”: [`PROJEKT.md`](PROJEKT.md).
Wymagania: D-050, D-063, D-074, D-085, D-093 (✅) i model statystyk D-062 (✅). Przyrost według propozycji
`tools/walka/BALANS_1711.md`, część 6 — to nie jest decyzja (wybór 1 w PROJEKT.md).*

> **W skrócie.** Jeden kontener `Workspace/TreningProba` (atrybut `Wygenerowane = true`). Arena z 202 klocków
> (256 × 56 st) stoi w powietrzu, z dala od map, w (3000; 300; 3000). Sześć stanowisk w jednym rzędzie: **Siła
> „Rozbijanie”** (strzałka w stronę lecącej skrzynki), **Pancerz „Blok”** (blok w chwili ciosu, bez dawania się nabrać
> na zmyłki), **Kondycja „Bieżnia”** (lewa / prawa stopa w rytmie, gdy ślad dojedzie do linii), **Zręczność „Kłody”**
> (skok nad niską kłodą, padnij pod wysoką), **Inteligencja „Runy”** (powtórz świecące runy) i **Szczęście
> „Koniczyny”** (koszyk nad głową, przejście na tor koniczyny, z dala od kamieni). Wejście: E przy trenerze
> w bazarze (zdarzenie `OknoMiejsca`, bez zmian w pakiecie bazaru) albo E przy własnej tablicy obok miejsca startu.
> Otwiera się **tymczasowy** wybór mini-gry (docelowe okno 2D robi Paweł). Serwer decyduje o przyrostach i zapisuje je
> w atrybutach sesyjnych gracza (`TreningSila`, `TreningPancerz`; bez DataStore), a do tego ogłasza je sygnałem
> `Sygnaly/PrzyrostStatystyki`. WYJDŹ wraca gracza tam, skąd przyszedł.

## Pliki

| Plik | Co to jest |
|---|---|
| `PROJEKT.md` | sześć mini-gier (PROPOZYCJA), wybory dla ludzi, ustawienia „przyjęte, do zmiany” |
| `ustawienia.json` | **jedyne źródło liczb**: statystyki, runda, poziomy trudności i wagi sześciu gier, pasek przyrostu, ochrona przed spamem, układ areny i stanowisk (kamera gry, ujęcie początku odliczania, zbliżenie po rundzie, miejsce dużych napisów), telefon (rozmiary), ruch kamery (`ui.kamera`), komiksowe napisy (`ui.komiks`), efekty i konfetti (`ui.efekty`), haczyk bohatera (`ui.bohater`), klawisze, dźwięki (wbudowane i zdarzenia arkusza `swiat/dzwiek_gra`), teksty |
| `dane.py` | generator `zrodla/DaneTreningu.luau` (położenia w świecie, przypadki wzorcowe z lustra); reguły ustawień każdego rodzaju gry i wyglądu (kąty kamer, style napisów, nazwy wybuchów z modułu walki, litery napisów w czcionce komiksowej); `--sprawdz`, `--wyjscie DIR` |
| `logika_treningu.py` | lustro `zrodla/LogikaTreningu.luau` w Pythonie (plan rundy sześciu gier, werdykty: okno czasu, kolejność run, tor koszyka; pasek, waga, spam, wejście, skala UI) |
| `kamera_treningu.py` | lustro `zrodla/KameraTreningu.luau` (ujęcia kamery stanowisk) + rzut punktu na ekran, miejsca postaci, prostokąt karty podsumowania — dla podglądów i testów |
| `scena.py` | arena z prostych części (202): podłoga, murki, niewidzialne ściany, lobby z tablicą wyboru i bramą wyjścia, sześć stanowisk z trenerami; `pole_gry` — punkty, które gracz musi widzieć |
| `podglad.py` | **podglądy stanowisk bez Studio**: render brył z `scena.py` z kamery każdej mini-gry + przykładowa chwila gry, zarys przycisków i dużego napisu (numpy + Pillow, najniższy priorytet) → `podglady/`; `--ujecie start` / `final`, `--ekran 667x375` |
| `podglady/` | `podglad_<gra>.jpg` (kamera gry), `podglad_<gra>_start.jpg` (początek odliczania), `podglad_<gra>_final.jpg` (zbliżenie po rundzie z kartą) i `podglad_arena.jpg` — render brył, nie zrzut z gry |
| `zrodla/LogikaTreningu.luau` | czysta logika (ModuleScript) — ta sama co lustro; serwer sprawdza ją przy starcie (118 przypadków) |
| `zrodla/KameraTreningu.luau` | czysty rachunek kamery (ModuleScript): ujęcia stanowiska, odliczania, gry i zbliżenia po rundzie, zawężenie kąta po trafieniu, drżenie |
| `zrodla/EfektyTreningu.luau` | efekty 3D trafień w języku walki (z modułu efektów walki, gdy stoi w miejscu; inaczej własne kopie) i papierowe konfetti (ModuleScript) |
| `zrodla/KomiksTreningu.luau` | komiksowe napisy w stylu walki: Bangers, cień i obrys tuszem, obrót, gwiazda, wejście i zanik (ModuleScript) |
| `zrodla/SerwerTreningu.server.luau` | serwer: werdykty i przyrosty, ochrona przed spamem, wejście i wyjście, podpowiedzi E, sygnał dla modułu statystyk, haczyk testowy |
| `zrodla/KlientTreningu.client.luau` | klient: własny ScreenGui (tymczasowy wybór, status, sterowanie sześciu gier, podpowiedź obrazkowa, karta podsumowania) i warstwa komiksowa, kamera stanowiska (ujęcia jak w walce), pochłanianie ruchu, rysowanie stanowisk (`GRY[gra]`), ruch postaci (bieg, skok / padnij, przejścia z koszykiem, radość — awatar albo bohater klasy przez haczyk), efekty i dźwięki, `OknoMiejsca`, uchwyt `WybierzGre` |
| `zrodla/DaneTreningu.luau` | **wygenerowany** — nie edytować ręcznie |
| `sprawdz_luau_treningu.py` | kontrola statyczna Luau (reguły jak w bazarze + zakaz zasobów spoza Robloxa i rozmiarów tekstu z literałów; jedyny wyjątek: adres arkusza dźwięku z katalogu `swiat/dzwiek_gra`) |
| `zbuduj.py` | budowa w Studio: `--sucho`, `--skrypty`, `--usun`, `--studio` |
| `testy/test_treningu.py` | 54 testy offline (opis w nagłówku pliku; 5e — pole gry na czterech ekranach, 5f–5h i 3f–3g, 4f, 6i–6l — wygląd jak w walce) |
| `testy/proba_play.py` | próba w Studio (Play): T01–T14 (Siła, Pancerz, wejście, wyjście, telefon), T15–T22 (cztery nowe gry, spam, reset postaci, klatka) i T23–T27 (kamery, napisy, efekty, konfetti, bohater); `--nowe`, `--walka`; `--sprawdz` — kawałki Luau bez Studio |
| `testy/zrzuty_gry.py` | zrzuty z gry do `klatki/` (1280 px): 01–08 (Siła, Pancerz), 09–24 (każda nowa gra: start z podpowiedzią, środek rundy, podsumowanie, telefon 667 × 375), `--telefon` (26–37), `--walka` (38–67: odliczanie, trafienie, seria, zbliżenie z konfetti, zbliżenie na telefonie); `--nowe`, `--sprawdz` |
| `klatki/` | zrzuty z gry (tryb Play) — tabela w „Zrzuty z gry” |

## Co powstanie w kontenerze `Workspace/TreningProba`

| Ścieżka | Klasa | Co robi |
|---|---|---|
| `Moduly/DaneTreningu`, `Moduly/LogikaTreningu` | ModuleScript | dane (wygenerowane) i logika |
| `Moduly/KameraTreningu`, `Moduly/EfektyTreningu`, `Moduly/KomiksTreningu` | ModuleScript | wygląd jak w walce (tylko klient): rachunek kamery, efekty 3D i konfetti, komiksowe napisy |
| `SerwerTreningu` (RunContext Server), `KlientTreningu` (RunContext Client) | Script | poza Studio serwer usuwa cały kontener (jak inne prototypy) |
| `Zdalne/ZdarzeniaTreningu` | RemoteEvent | klient → serwer: `wejdz`, `start`, `akcja`, `przerwij`, `wyjdz`; serwer → klient: `wybor`, `odmowa`, `przybycie`, `runda`, `wynik`, `koniec`, `wyjscie` |
| `Sygnaly/PrzyrostStatystyki` | BindableEvent | **dla przyszłego modułu statystyk** (dziś nikt go nie słucha) |
| `Sygnaly/WybierzGre` | BindableFunction (klient) | **uchwyt dla docelowego okna 2D Pawła** |
| `Sygnaly/SterowanieSerwera`, `Sygnaly/SterowanieKlienta` | BindableFunction | haczyki testowe |
| `Arena` (Model, `ModelStreamingMode = Persistent`) | części | podłoga 256 × 56 st, murki i niewidzialne ściany 14 st, sześć stanowisk (Kłody, Bieżnia, Siła, Pancerz, Runy, Koniczyny), lobby: tablica „WYBÓR MINI-GRY (E)” i brama „WYJŚCIE (E)” (zapasowe — gracz trafia od razu na stanowisko) |
| `TablicaWejscia` (Model, Persistent) | części | tablica „TRAINING CENTER / MINI-GRY” z podpowiedzią E 14–26 st od pierwszego SpawnLocation, na wolnym gruncie, z dala od „Nowe miasteczko (E)” bazaru i portalu startowego; miejsce wybiera budowa w Studio |

Atrybuty kontenera: `Wygenerowane`, `Zrodlo`, `Zbudowano`, `Skrot`, `PunktTablicy`, **`WyborTymczasowy`** (true; false
= tymczasowy wybór się nie otwiera, bo jest okno Pawła). Ręczne w Edit i przenoszone przy odbudowie:
`WyborTymczasowy`, `RecznyPunktTablicy` (Vector3 na gruncie — własne miejsce tablicy). Tylko do prób, u klienta
w Play: `EmulacjaEkranu` (Vector2 — ekran telefonu), `EfektyWlasne` (true — efekty z własnego modułu mimo modułu
walki w miejscu), `HaczykBohatera` (ścieżka zastępczego haczyka bohatera). W Play serwer ustawia
`SerwerTreninguGotowy`, `ZgodnoscLogikiTreningu` („OK 70/70”), `Podpowiedzi` (3), liczniki `LicznikWejsc`,
`LicznikRund`, `LicznikTrafien`, `LicznikPudel`, `LicznikSpamu`, `LicznikSygnalow`, `LicznikOdmow`, `OstatniWynik`,
`OstatniaOdmowa`, a klient (u siebie) — `KlientTreninguGotowy`. Atrybuty gracza: `TreningSila`, `TreningKondycja`,
`TreningInteligencja`, `TreningZrecznosc`, `TreningSzczescie`, `TreningPancerz` (punkty w tej sesji), `TreningGra`,
`TreningSeria`. Atrybutów `Strength`, `Armor`… (`PlayerStatsDefaults`) pakiet nie
zmienia.

## Jak podpiąć resztę gry (bez zmian w cudzych plikach)

- **Bazar** (`swiat/miasteczko_bazar_gra`): E przy trenerze wysyła `ReplicatedStorage.OknoMiejsca("training_center")`.
  Klient próby słucha każdego zdarzenia o tej nazwie i otwiera tymczasowy wybór. Ustawia też na zdarzeniu atrybut
  `training_center = true` — to opisany w README bazaru sposób wyłączenia dymku „Trener: mini-gry w budowie”.
- **Okno Pawła** (gdy powstanie): w Edit `WyborTymczasowy = false`, a w jego skrypcie klienta:
  ```lua
  bindable("OknoMiejsca").Event:Connect(function(id) if id == "training_center" then open() end end)
  -- przycisk mini-gry w oknie:
  local w = workspace.TreningProba.Sygnaly.WybierzGre:Invoke("sila")   -- "wyslano" | "trwa_runda"
  ```
  Lista statystyk, nazw mini-gier i stanów („grywalna” / „w_projekcie”) jest w `Moduly/DaneTreningu.statystyki`.
- **Moduł statystyk** (gdy powstanie), po stronie serwera:
  ```lua
  workspace.TreningProba.Sygnaly.PrzyrostStatystyki.Event:Connect(function(gracz, p)
      -- p = { statystyka = "sila", atrybut = "Strength", atrybutSesji = "TreningSila", przyrost = 1,
      --       sumaSesji = 3, seria = 12, gra = "sila", runda = 4, zrodlo = "TreningProba" }
  end)
  ```

## Jak zbudować i obejrzeć

```
python -B swiat/trening_proba/dane.py                    # po każdej zmianie ustawienia.json
python -B swiat/trening_proba/testy/test_treningu.py     # 54 testy, ok. 18 s
python -B swiat/trening_proba/zbuduj.py --sucho          # bez Studio: dane, Luau, strażniki, plan budowy
python -B swiat/trening_proba/podglad.py                 # podglądy stanowisk do podglady/ (ok. 1 min, bez Studio)
python -B swiat/trening_proba/podglad.py --ujecie final  # zbliżenie po rundzie z kartą (--ujecie start: początek odliczania)
python -B swiat/trening_proba/podglad.py --ekran 667x375 --wyj <folder>   # kadr telefonu
python -B swiat/trening_proba/testy/proba_play.py --sprawdz   # kawałki Luau próby parsują się (bez Studio)
python -B swiat/trening_proba/zbuduj.py                  # Studio w trybie Edit: buduje / odbudowuje kontener
python -B swiat/trening_proba/zbuduj.py --skrypty        # tylko moduły i skrypty (arena i tablica zostają)
python -B swiat/trening_proba/zbuduj.py --usun           # usuwa Workspace/TreningProba
python -B swiat/trening_proba/testy/proba_play.py <folder poza repo>   # próba T01–T22 w trybie Play (ok. 12 min)
python -B swiat/trening_proba/testy/proba_play.py <folder> --nowe      # tylko T01 i T15–T22 (ok. 8 min)
python -B swiat/trening_proba/testy/proba_play.py <folder> --walka     # tylko T01, T22 i T23–T27 — wygląd jak w walce (ok. 7 min)
python -B swiat/trening_proba/testy/zrzuty_gry.py                      # 24 zrzuty do klatki/ (ok. 7 min)
python -B swiat/trening_proba/testy/zrzuty_gry.py --nowe               # tylko 09–24 (cztery nowe gry, ok. 5 min)
python -B swiat/trening_proba/testy/zrzuty_gry.py --telefon            # 26–37: sześć gier na telefonie (ok. 5 min)
python -B swiat/trening_proba/testy/zrzuty_gry.py --walka              # 38–67: odliczanie, trafienie, seria, zbliżenie (ok. 9 min)
```

Przy kilku oknach Studio dopisz `--studio <studio_id>`. Każdy wysyłany kod sprawdza `game.PlaceId == 129485428021967`
i tryb Edit. Budowa rusza tylko kontener z `Wygenerowane` (obiekt o tej nazwie bez atrybutu → STOP), a zanim cokolwiek
postawi, sprawdza, czy w pudle areny nie ma cudzych części (są → STOP). Stawia punkty historii przed i po (Ctrl+Z
cofa całość), niczego nie publikuje ani nie zapisuje, a `Lighting` zostaje nietknięte.

**Obejrzenie ręcznie w Studio:** Play → (Enter na ekranie wyboru klasy) → podejdź do tablicy „TRAINING CENTER /
MINI-GRY” obok miejsca startu
(albo do trenera w budynku Training Center w bazarze) → E → w oknie „TYMCZASOWY WYBÓR” kliknij GRAJ przy Sile →
START (albo spacja) → strzałki / WASD w stronę skrzynki, gdy dolatuje do świecącego kółka → po rundzie podsumowanie →
INNA GRA → Pancerz → spacja, gdy pierścień dojdzie do kółka (fioletowy = zmyłka, nie blokuj) → WYJDŹ (albo Q).
Telefon: Test → Device → telefon w poziomie (667 × 375) albo zrzut z emulacją: `python -B swiat/trening_proba/testy/zrzuty_gry.py`.

## Wygląd jak w walce: kamery, komiksowe napisy, efekty, konfetti (18.11.2026, część A — bez Studio, część B — w Studio)

Polecenie Karola z 18.11.2026: „Popraw gry, tak żeby były pod takimi kątami, i w takich samych efektach POW/PAF
komiksowych, konfetti jak walki.” Wzór: prototyp walki `swiat/test_walki2` (`OdtwarzaczWalki2`, `InterfejsWalki2`,
`Efekty3D`). **Stan: zaprogramowane, sprawdzone offline (część A, punkty 1–7), wdrożone w Studio i sprawdzone w trybie
Play (część B, punkt 8).** Reguły gier (werdykty serwera, przyrosty, ochrona przed spamem, lustro logiki — 118 przypadków) i dźwięki
bez zmian; arena bez zmian (te same 202 części), żadnych nowych zasobów.

### 1. Kamery (`stanowiska.<gra>.kamera`, `ui.kamera`; rachunek: `KameraTreningu.luau` = `kamera_treningu.py`)

Położenia względem podestu stanowiska (x w prawo, y w górę, z do gracza); kąt widzenia pionowy. Było: jeden kąt 70°
i kamera wysoko; jest: 44–51° (walka: 40–52°) i oko 2,7–4,1 st nad podestem.

| Gra | Było: oko → cel (70°) | Jest: oko → cel, kąt | Kadr | Pole gry na telefonie (szer. × wys. ekranu) |
|---|---|---|---|---|
| Siła | (3,2; 6,6; 11,5) → (6,0; 3,2; −8) | (5,3; 2,7; 8,8) → (1,4; 3,9; −3,4), 48° | zza prawego ramienia, nisko, 18° od osi, lekko w górę | 0,28 × 0,37 → 0,43 × 0,69 |
| Pancerz | (3,2; 6,6; 11,5) → (5,5; 3,6; −8) | (13,8; 2,8; 3,2) → (0,6; 5,2; −8,0), 48° | z boku (50°): gracz z tarczą po lewej, golem twarzą trzy czwarte | 0,13 × 0,31 → 0,48 × 0,66 |
| Kondycja | (0; 8,4; 14,5) → (0; 1,4; −0,5) | (2,6; 3,3; 14,7) → (−1,1; 1,9; 0,8), 49° | nisko z przodu, 15° z ukosa: taśma biegnie na widza | 0,16 × 0,33 → 0,35 × 0,70 |
| Zręczność | (7,6; 4,4; 8,2) → (−1,6; 2,2; −2,6) | (5,3; 2,9; 11,2) → (−0,4; 4,3; −0,7), 48° | nisko z ukosa (26°), w kadrze także szczyt skoku | 0,20 × 0,33 → 0,30 × 0,71 |
| Inteligencja | (3,4; 6,6; 9,0) → (2,8; 4,5; −8) | (9,7; 4,0; 6,3) → (4,8; 4,9; −8,1), 44° | ściana z runami z ukosa (19°), mag po lewej | 0,23 × 0,36 → 0,40 × 0,71 |
| Szczęście | (0; 9,4; 17,5) → (0; 8,1; −6) | (8,2; 4,1; 18,3) → (1,8; 7,4; −3,4), 51° | nisko z ukosa (16°), w górę na koronę drzewa | 0,22 × 0,54 → 0,26 × 0,74 |

Ujęcia (klient: `ujecie(…)`, `kameraKlatka`):

- **stanowisko** (przed rundą) — kamera gry z lekkim kołysaniem (±1,2° co 9 s);
- **odliczanie** — dojazd z ujęcia `kamera.start` (dalej, wyżej, szerzej o 3–4°) do kamery gry; kończy się 0,4 s przed
  startem, potem kamera stoi. Podpowiedź obrazkowa schodzi w odliczaniu na dół ekranu, liczby 3-2-1 i „START!” są
  na środku;
- **gra** — kamera stoi (pole gry czytelne). Trafienie: krótkie zawężenie kąta o 0,8° (0,2 s), mocne trafienie 1,8°,
  próg serii / punkt statystyki 3° (0,6 s); drżenie gaśnie wykładniczo jak w walce (`exp(−9·t)`). Test 5e sprawdza
  pole gry także przy największym zawężeniu;
- **final** (po rundzie) — zbliżenie na postać: kamera 14 st przed nią, 2,4 st nad ziemią, kąt 42°, dojazd 8% i powolny
  objazd; postać obraca się do kamery (0,35 s), karta podsumowania stoi po prawej, a postać w środku wolnego pasa po
  lewej (kadr liczony z szerokości ekranu). Przed kolejną rundą postać wraca twarzą do gry.

Postać półprzezroczysta u siebie została tylko w Sile (kamera za plecami); w Pancerzu i Runach kamera z boku jej nie
potrzebuje. Pierścienie Pancerza stoją teraz na ekranie w miejscu, w które uderzy pięść (rzut punktu ciosu).
W emulacji telefonu (`EmulacjaEkranu`) kamera okna dostaje szerszy kąt, żeby w prostokącie telefonu było widać to
samo, co na telefonie.

### 2. Komiksowe napisy (`ui.komiks`; `KomiksTreningu.luau`, warstwa `TreningProbaKomiks`)

- Styl napisów walki: czcionka **Bangers**, cień i obrys tuszem, obrót do 8° (długie mniej), wejście od 0,2 przez 1,08
  do 1 w 0,2 s, zanik od 74% życia, za dużymi słowami **gwiazda** z dwóch kręcących się kwadratów (pomarańcz i czerwień).
- **Słowo przy miejscu trafienia** (rzut punktu 3D na ekran): rozbita skrzynka, tarcza, cel stopy obok taśmy, obok głowy
  przy kłodzie, naciśnięty kamień, miejsce złapania koniczyny. Siła dostała słowa „PAF!”, „ŁUP!”, „TRACH!”, „BAM!”, „POW!” (było:
  „TRAFIONE!”, „DOBRZE!”…). Kolor z walki: biały (cios), błękit (blok), zieleń (unik), fiolet (magia). Pudła —
  mniejsze, różowoczerwone, w tym samym miejscu.
- **Mocne trafienie** (co piąte w serii, próg serii, punkt statystyki, złota koniczyna, całe zaklęcie): większe żółte
  słowo z gwiazdą, większy wybuch, mocniejsze zawężenie kadru.
- **Duże słowa** („SERIA 10!”, „+1 Siła!”, „ZAKLĘCIE!”, „PATRZ!”, „TWOJA KOLEJ!”) w miejscu stanowiska z danych
  (`stanowiska.<gra>.napis`): Siła, Bieżnia, Kłody, Koniczyny — lewy górny róg; Pancerz — dół między graczem
  a golemem; Runy — przy magu (żeby „PATRZ!” nie zasłaniało kamieni). Jedno duże słowo naraz: punkt, potem seria,
  potem zaklęcie; nowe duże słowo zdejmuje poprzednie z tego miejsca (`Komiks:usun`), a przy zbliżeniu po rundzie
  słowa z rundy znikają, żeby nie zostały pod kartą.
- Litery mają rozmiar stylu wprost (`TextSize`, bez `TextScaled`), obrys i cień rosną razem z literami (małe słowo —
  cienki obrys, najmniej 1,5 px), gwiazda ma bok 1,4 wysokości napisu (w walce 1,15 wysokości tabliczki, która jest
  wyższa od liter). Odliczanie stoi w stałym miejscu ekranu (`licznik_miejsce` = środek, 45% wysokości).
- Napisy są w osobnej warstwie pod oknami mini-gry, więc nie przykrywają przycisków; z paneli schodzą, poza ekran nie
  wychodzą (`Komiks.miejsce`).
- **Czcionka a polskie znaki:** plik czcionki Bangers z instalacji klienta Roblox ma wszystkie polskie litery (a także
  × · — … „ ”) — sprawdzone 18.11.2026 (FredokaOne ich nie ma, stąd wcześniejsza zmiana na Nunito). Lista liter spoza
  ASCII jest w `ui.komiks.znaki`; napis z literą spoza listy dostaje czcionkę okien (Nunito ExtraBold), a generator
  danych takiego napisu nie przepuści. Tytuł karty podsumowania: LuckiestGuy (czcionka nagłówków walki, też ma
  polskie litery).

### 3. Efekty 3D trafień (`ui.efekty`; `EfektyTreningu.luau`)

| Gra | W chwili trafienia | Mocne trafienie / inne |
|---|---|---|
| Siła | iskry „cios” przy skrzynce + odłamki w jej kolorze, smuga za ostrzem miecza | wybuch „krytyk” |
| Pancerz | iskry „blok” i łuk odbicia (parada) na tarczy | cios bez bloku: iskry przy postaci, czerwony błysk |
| Kondycja | iskry i złota fala na celu stopy | — |
| Zręczność | rozbłysk i fala kurzu spod stóp | kłoda trąca postać: iskry na piersi |
| Inteligencja | fioletowe iskry „iskra” przy kamieniu | całe zaklęcie: rozbłysk „bariera” na ścianie + odłamki z czterech kamieni |
| Szczęście | zielony rozbłysk przy koszyku | złota: „krytyk”; kamień w koszyku: wybuch „kamien” |

Próg serii i punkt statystyki: złota fala wokół postaci (promień 5,5 st), drżenie i największe zawężenie kadru.

### 4. Konfetti i radość po rundzie

Walka **nie ma konfetti** — świętuje radością zwycięzcy, objazdem kamery, wstęgą „ZWYCIĘSTWO!” i wysypanym łupem.
Dlatego konfetti jest własne, w tym samym języku: papierowe prostokąty z klocków w barwach palety walki, wystrzelone
salwami z lewej i z prawej strony postaci, opadają wirując i gasną (3,2 s).

- Runda dała punkt statystyki → postać się cieszy (animacja „cheer” z własnego skryptu Animate awatara; gdy jej nie ma —
  ręce w górę i podskoki), 46 kawałków w 2 salwach, złoty rozbłysk nad głową.
- Runda bez pudła (i nieprzerwana) → 90 kawałków w 4 salwach i napis „BEZ PUDŁA!” z gwiazdą nad postacią.
- Bez punktu → samo zbliżenie i karta, bez konfetti i radości.
- Miecz Siły i tarcza Pancerza (rekwizyty stanowiska, wiszą w stałym miejscu) są w zbliżeniu schowane i wracają
  z kolejną rundą; postać obraca się do kamery.
- Karta podsumowania w stylu karty wyniku walki: przy prawej krawędzi, lekko przekrzywiona, pomarańczowa wstęga
  z tytułem, wyskakuje z powiększeniem, liczby rosną od zera (0,7 s). Rozmiar 400 × 244 i przyciski bez zmian. Panel
  rundy jest na podsumowaniu schowany.

### 5. Bohater klasy (`ui.bohater`)

Gdy w miejscu działa pakiet bohatera (`Workspace/BohaterSwiat/Sygnaly/RuchBohatera`, BindableFunction u klienta)
i gracz ma aktywnego bohatera, ruchy postaci idą przez haczyk: Bieżnia — klip `bieg`; Kłody — `skok` z przesunięciem
w górę po łuku (2,7 st), `padnij` **bez przesunięcia w dół** (poza sama opuszcza biodra), trącenie kłodą —
przesunięcie do tyłu; Koniczyny — `rece_gora`; po rundzie z punktem — `radosc` (zamawiana od nowa co 3 s). Bez haczyka
albo bez aktywnego bohatera — stawy i animacje awatara jak dotąd. Każde wywołanie jest osłonięte (`FindFirstChild`,
`pcall`, osobny wątek: haczyk bez obsługi nie zatrzyma gry — do następnego wejścia na stanowisko zostaje awatar).
Półprzezroczystość postaci w Sile działa także na bohaterze (przejmuje `LocalTransparencyModifier` awatara).

### 6. Co jest brane z walki, a co przeniesione

- **Brane w czasie gry (`require`), gdy w miejscu stoi `Workspace/TestWalki2/Moduly/Efekty3D`:** iskry, rozbłyski,
  fala uderzeniowa, łuk odbicia i tabela wybuchów. Klient sprawdza przy wejściu na stanowisko, czy moduł ma potrzebne
  funkcje i nazwy wybuchów; każde wywołanie idzie przez `pcall`, a pierwszy błąd przełącza na własne efekty do
  zejścia ze stanowiska. Bez kontenera walki mini-gry działają na własnych efektach (atrybut `EfektyWlasne = true`
  wymusza je do próby).
- **Przeniesione do pakietu:**
  - te same efekty jako zapas (`EfektyTreningu.luau`: iskry, kula, fala, parada, 14 wybuchów) — test 6j pilnuje, że
    nazwy, parametry i liczby są takie same jak w module walki;
  - styl napisów (`KomiksTreningu.luau`) — `InterfejsWalki2` rysuje napisy tylko wewnątrz swojego ekranu walki (kadr,
    tabliczki, stosy przy aktorach), a jego tabela stylów jest lokalna; liczby i kolory stylu są w `ui.komiks`,
    a test 6i porównuje je ze źródłami walki;
  - zasady kamery (`KameraTreningu.luau`) — ujęcia walki liczą się z geometrii dwóch aktorów na arenie, więc tu jest
    własny mały rachunek z tymi samymi regułami (wąski kąt, niski kadr, dojazd, drżenie, finał ze zbliżeniem);
  - konfetti — własne (w walce go nie ma).

### 7. Sprawdzone offline (18.11.2026; wszystko kod 0)

```
python -B swiat/trening_proba/dane.py --sprawdz               # aktualny (36 planów, 36 sekwencji wzorcowych)
python -B swiat/trening_proba/sprawdz_luau_treningu.py        # 7 plików, OK (z parserem luau_mini)
python -B swiat/las_potwory/sprawdz_luau.py swiat/trening_proba/zrodla/*.luau   # 7 plików, OK
python -B swiat/trening_proba/testy/test_treningu.py          # Ran 54 tests … OK (ok. 18 s)
python -B swiat/trening_proba/testy/proba_play.py --sprawdz   # 25 kawałków Luau, OK
python -B swiat/trening_proba/testy/zrzuty_gry.py --sprawdz   # 13 kawałków Luau, OK
python -B swiat/trening_proba/zbuduj.py --sucho               # sucho: OK (202 części, 7 modułów i skryptów)
```

Nowe testy (10) i zmienione:

- **3f** rachunek kamery w Luau (luau_mini) = lustro w Pythonie: ujęcia sześciu gier, zbliżenie dla losowych miejsc
  postaci i ekranów, zawężenie, drżenie; odliczanie zaczyna się w ujęciu „start” i kończy w kamerze gry przed startem;
- **3g** rozmiar i miejsce napisu (`Komiks.rozmiar`, `Komiks.miejsce`): 300 losowych układów — napis w obszarze, schodzi
  z przeszkody, bez kolizji zostaje na miejscu;
- **4f** oko kamery gry, początku odliczania, drogi dojazdu i zbliżenia stoi w arenie, nad podłogą i poza bryłami;
  ze zbliżenia widać pierś i głowę postaci (każde miejsce postaci, początek i koniec objazdu); kąt ≤ 52°, oko ≤ 5,5 st
  nad podestem;
- **5e** (zmieniony, reguła ta sama): pole gry — teraz także postać w Pancerzu i na Bieżni oraz szczyt skoku
  w Kłodach — na czterech ekranach w obszarze GUI i poza panelami, z kątem kamery stanowiska **i przy największym
  zawężeniu**; do tego pole gry zajmuje co najmniej ćwierć szerokości i połowę wysokości telefonu;
- **5f** postać (także nieprzezroczysty bohater) nie zasłania więcej niż połowy żadnej grupy punktów pola gry;
- **5g** zbliżenie po rundzie: stopy, głowa, barki i dłonie w górze mieszczą się w wolnym pasie na lewo od karty na
  czterech ekranach, na początku i po objeździe;
- **5h** duże napisy po ułożeniu przez kod z gry nie leżą na panelach ani poza ekranem; „PATRZ!” nie zasłania kamieni;
  odliczanie na środku nie koliduje z podpowiedzią na dole;
- **6i** liczby i kolory stylu napisów = źródła walki; **6j** efekty: nazwy, parametry i liczby wybuchów = moduł walki,
  klient woła tylko wspólne funkcje, moduł walki brany przez `FindFirstChild` + `pcall(require)`;
- **6k** każda litera każdego napisu jest w czcionce komiksowej (lista w danych + plik czcionki klienta Roblox, gdy jest
  na komputerze); **6l** haczyk bohatera: jedno osłonięte miejsce wywołania, „padnij” bez przesunięcia w dół;
- **1c** 15 nowych rodzajów złych ustawień wyglądu → błąd; **5c** karta ze wstęgą mieści się na czterech ekranach.

Podglądy (`podglady/`, render brył — obejrzane): kamera gry, początek odliczania i zbliżenie po rundzie dla sześciu
gier. Wybór kamer: przeszukanie losowe z regułami testu 5e (kilkadziesiąt tysięcy kadrów na grę), potem ocena na oko.

### 8. Część B — w Studio (18.11.2026, 09:50–11:00, tryb Play, z bohaterem klasy)

Miejsce: `Workspace/BohaterSwiat` z `BohaterWSwiecie = true`, więc po wyborze klasy gracz jest bohaterem klasy —
wszystkie próby szły z **prawdziwym** haczykiem `RuchBohatera` i z modułem efektów walki w miejscu. Wdrożenie:
`zbuduj.py --skrypty` (arena bez zmian, 7 modułów i skryptów), w sumie pięć razy — po każdej turze poprawek. Pełna
lista T01–T27 szła na trzeciej budowie; po dwóch ostatnich (przesunięcie trzech wierszy karty, miejsce słowa
w Kłodach) powtórzone T01, T09, T10, T16, T22, T26, T27 — OK.

```
python -B tools/studio_okno.py --na-wierzch                                  # przed próbą: czas klatki z okna w tle jest niemiarodajny
python -B swiat/trening_proba/zbuduj.py --skrypty                            # 1 min
python -B swiat/trening_proba/testy/proba_play.py <folder poza repo>         # 12 min — cała lista T01–T27
python -B swiat/trening_proba/testy/proba_play.py <folder poza repo> --walka # 4 min — T01, T22–T27
python -B swiat/trening_proba/testy/zrzuty_gry.py --walka --klasa Warrior    # 9 min — zrzuty 38–67 (+ 54b)
python -B swiat/trening_proba/testy/zrzuty_gry.py --walka --klasa Mage --krotko   # 3 min — zrzuty 68–79
python -B swiat/trening_proba/testy/zrzuty_gry.py --telefon --klasa Warrior  # 3 min — zrzuty 26–37
python -B swiat/przejscie_gry/proba_dymna.py <folder poza repo>              # 3 min — regresja całej gry
```

**Lista kontrolna T01–T27: 27 × OK.**

| Punkt | Wynik w grze |
|---|---|
| T01–T22 | OK jak w nocy 18.11 (reguły bez zmian): zgodność logiki 118/118; Siła 45/45, Pancerz 42/43 (zablokowana zmyłka), Bieżnia 67/67, Kłody 31/31, Runy 37 trafień i 7 zaklęć, Koniczyny 30/30; punkty i przyrosty = oczekiwane; spam odrzucony (54–56 z 60); reset postaci w rundzie sprząta; konsola: 0 błędów pakietu |
| T13, T21 | czas klatki z napisami, efektami i konfetti: Siła śr. 16,7 ms, p95 18,1 ms; Bieżnia 16,7 / 18,0 ms; Koniczyny 16,7 / 17,9 ms |
| T23 kamera | stanowisko 48,0° (= dane); odliczanie zaczyna w ujęciu „start” i dojeżdża do kamery gry; w grze 45,3–48,0° (zawężenie przy trafieniach), drżenie oka ≤ 0,14 st; zbliżenie 42,0°, postać zwrócona do kamery (1,00), karta od x = 1387 z 2041 px; po JESZCZE RAZ postać znów przodem do gry; po wyjściu kąt kamery gracza 70° jak przed wejściem |
| T24 napisy | 55 napisów w rundzie Siły na 45 trafień, naraz najwyżej 5, czcionką zastępczą 0 (Bangers), każdy napis z danych dostaje czcionkę komiksową |
| T25 efekty | moduł walki w miejscu → źródło „walka” (49 nowych części, 0 błędów); wymuszone własne → „wlasne” (55 części, 0 błędów) |
| T26 konfetti | runda bez pudła z punktami → 90 kawałków, radość postaci (klip bohatera), napis „BEZ PUDŁA!”; przerwana runda bez punktu → 0 kawałków, bez radości |
| T27 bohater | prawdziwy haczyk: bohater aktywny, w Kłodach klipy `skok`, `padnij`, po rundzie `radosc`, przesunięcie w skoku, stawy awatara nietknięte, haczyk nie zawieszony |

W pełnym przebiegu T27 wyszło „BŁĄD”, a T24 podało 529 napisów — oba przez kod próby, nie gry: próbki ruchu zapisywały
atrybuty dopiero po pętli (pętla trwa dłużej niż N × 0,1 s, więc próba czytała wynik poprzedniej gry), a licznik
napisów rośnie od startu klienta. Próbki zapisują teraz wynik po każdej próbce, T24 liczy przyrost od wejścia na
stanowisko; powtórka `--tylko T01,T24,T27,T22` na tej samej budowie: 4 × OK (wyniki w tabeli). Trzecia poprawka
próby: wybrane przez `--tylko` punkty bez T02 / T04 zaczynały z miejsca startu postaci, które bywa poza zasięgiem
tablicy (serwer słusznie odmawiał: „za_daleko”) — `wejdz_do` stawia teraz postać przy tablicy, gdy gracz nie jest na
stanowisku.

**Próba dymna całej gry** (`swiat/przejscie_gry/proba_dymna.py`): D00–D13 — 14 × OK (walka, łup 0 → 25 złota, trener
w bazarze, runda Siły, wyjście; klatka 16,7 ms, p95 17,8 ms; konsola bez śladów błędów). Żadna próba nie zmieniła
śledzonych plików poza tym pakietem.

**Co poprawione po zobaczeniu gry:**

1. Napisy: litery mają rozmiar stylu wprost, obrys i cień rosną z rozmiarem liter — małe słowa („TUP!”, „HOP!”) były
   plamą tuszu, bo pełny obrys zalewał litery.
2. Gwiazda za słowem większa (bok 1,4 wysokości napisu) — wcześniej prawie cała chowała się za literami.
3. Miecz Siły i tarcza Pancerza (rekwizyty stanowiska) schowane w zbliżeniu po rundzie — wisiały w powietrzu obok
   postaci obróconej do kamery.
4. Jedno duże słowo naraz w miejscu stanowiska („+1 Pancerz!” i „SERIA 10!” nakładały się); słowa z rundy znikają przy
   zbliżeniu (na telefonie zostawały pod kartą).
5. Smuga za mieczem węższa i krótsza (zasłaniała strefę „góra”).
6. Kłody: „HOP!” / „UNIK!” obok głowy po prawej, nie na głowie skaczącej postaci (po lewej zderzało się z dużym
   słowem stanowiska „+1 Zręczność!”).
7. Odliczanie na 45% wysokości ekranu — „START!” z większą gwiazdą nie mieściło się nad podpowiedzią na telefonie.
8. Karta podsumowania: wiersze nad przyrostem wyżej, przyrost niżej — kreski liter „Ś”, „Ć” („ZRĘCZNOŚĆ +3”)
   wchodziły na wiersz serii.

**Zrzuty z gry (`klatki/`, 1280 px; „✓” = obejrzany w tej wersji, „(✓)” = obejrzana wersja tego samego kadru sprzed ostatnich poprawek).** Bohater: Wojownik (38–67, 26–37) i Mag-kot (68–79). Nazwy konta
na zrzutach nie ma; wyniki prób z nazwą konta zostały poza repozytorium.

| Pliki | Co widać |
|---|---|
| `38`, `43`, `48`, `53`, `58`, `63` `_walka_<gra>_odliczanie` | odliczanie: kamera w drodze z ujęcia „start”, cyfra na środku, podpowiedź obrazkowa na dole ((✓) 38, 58) |
| `39_walka_sila_trafienie`, `40_walka_sila_seria` | Siła: „TRACH!”, „ŁUP!” z gwiazdą przy rozbitej skrzynce, „SERIA 10!” w lewym górnym rogu, złota fala; bohater półprzezroczysty, strefy widać przez niego (✓ 40; (✓) 39) |
| `44_walka_pancerz_trafienie`, `45_walka_pancerz_seria` | Pancerz: pierścień na tarczy w miejscu ciosu, „SPOKÓJ!” przy tarczy, „SERIA 10!” na dole między graczem a golemem (✓ 44, 45) |
| `49_walka_kondycja_trafienie`, `50_walka_kondycja_seria` | Bieżnia: bohater biegnie po taśmie (klip `bieg`), „TUP!” / „W RYTM!” obok taśmy, „SERIA 10!” ((✓) 49, 50) |
| `54_walka_zrecznosc_trafienie`, `54b_walka_zrecznosc_padnij`, `55_walka_zrecznosc_seria` | Kłody: bohater w skoku nad kłodą („HOP!” obok głowy, po prawej) i w przysiadzie pod wysoką kłodą („ZWINNIE!” z gwiazdą, obok „+1 Zręczność!”) (✓ 54, 54b) |
| `59_walka_inteligencja_trafienie`, `60_walka_inteligencja_seria` | Runy: kadr zza ramienia bohatera, „PATRZ!” przy magu, „MĄDRZE!” / „PAMIĘTASZ!” na naciśniętych kamieniach, „SERIA 10!” (✓ 60; (✓) 59) |
| `64_walka_szczescie_trafienie`, `65_walka_szczescie_seria` | Koniczyny: bohater z rękami w górze (klip `rece_gora`), „MAM!” / „SZCZĘŚCIE!” w miejscu złapania, „SERIA 10!” (✓ 64; (✓) 65) |
| `41`, `46`, `51`, `56`, `61`, `66` `_walka_<gra>_final` | zbliżenie po rundzie bez pudła: bohater cieszy się twarzą do kamery, konfetti, „BEZ PUDŁA!”, karta po prawej (✓ 41, 46, 51; (✓) 56, 61, 66) |
| `42`, `47`, `52`, `57`, `62`, `67` `_walka_<gra>_final_telefon_667x375` | to samo na telefonie 667 × 375 po przerwanej rundzie z punktem: bohater w kadrze na lewo od karty, konfetti (✓ 42, 67; (✓) 47, 52, 57) |
| `68`–`79` `_mag_<gra>_runda` / `_final` | Mag (kot, niższy): runda z trafieniem i zbliżenie po pierwszym punkcie w każdej grze — kot mieści się w kadrze obok karty, skacze nad kłodą, biegnie po taśmie (✓ 68, 69, 70, 72, 74, 78, 79) |
| `26`–`37` `_telefon_<gra>_667x375` / `_844x390` | runda na dwóch ekranach telefonu: pierścień Pancerza na tarczy i słowo przy tarczy na obu ekranach, „TUP!” obok taśmy, przyciski nie zasłaniają pola gry (✓ 32; (✓) 26, 28, 29, 30, 33, 34) |

Zrzuty `01`–`25` nie były odświeżane — pokazują wygląd sprzed tej zmiany.

### 9. Czego nie sprawdzono i ryzyka

- **Prawdziwy telefon i dotyk** — tylko emulacja układu w oknie Studia (667 × 375 i 844 × 390); wycięcie ekranu,
  gęstość pikseli i wydajność telefonu nie.
- **Awatar bez bohatera klasy w Play nie był uruchomiony** — miejsce ma aktywnego bohatera, więc ruch stawami awatara,
  jego animacja radości i haczyk bez obsługi (zastępczy haczyk z T27) są pokryte tylko testami offline i nocnymi
  próbami sprzed bohatera. Wróci do sprawdzenia, gdy bohater będzie wyłączony.
- **Duże napisy na telefonie są duże:** „SERIA 5!” zajmuje ok. ćwierci szerokości ekranu 667 × 375 i na ok. 1 s
  przykrywa część pola gry (zrzuty 26, 28); w Runach „+1 Inteligencja!” zachodzi na kamienie w czasie wpisywania.
  Rozmiar idzie ze skalą okien (przyciski ≥ 44 px) — do decyzji, czy słowa na telefonie zmniejszyć.
- **Kule stref Siły zostają w kadrze zbliżenia** po rundzie (półprzezroczyste kule wokół postaci, zrzuty 41, 69) — to
  części areny, nie rekwizyt klienta; można je chować tak jak miecz, jeśli przeszkadzają.
- **Radość Maga (kot)** na zbliżeniu jest mało widoczna (zrzuty 69, 79) — to klip `radosc` z pakietu bohatera;
  Wojownik podnosi miecz wyraźnie.
- **Obrót postaci do kamery po rundzie** robi klient (`PivotTo`, jak przejścia w Koniczynach) — inni gracze też go
  widzą; z dwoma graczami naraz niesprawdzone.
- **Runy:** kadr zza ramienia — bohater stoi przy lewej krawędzi i jest przycięty przez kadr (zrzuty 58–60); kamienie
  i przyciski są wolne.
- Sekcje niżej opisują kamery i wygląd z 17–18.11 rano (sprzed tej zmiany), tak jak zrzuty 01–25.

## Noc 17/18.11.2026: cztery nowe mini-gry (część A — bez Studio)

Projekt każdej gry i zmiany względem pierwszego opisu: `PROJEKT.md`, sekcje 3–6. W skrócie:

| Gra | Co robi gracz | Rodzaj oceny | Zdarzeń w rundzie | Waga |
|---|---|---|---|---|
| Kondycja „Bieżnia” | biegnie na taśmie twarzą do kamery; LEWA / PRAWA, gdy ślad stopy dojedzie do linii (stopy na zmianę, bęben trenera) | okno czasu (rytm, bez rozrzutu, podbiegi) | 66–69 | 0,7 |
| Zręczność „Kłody” | ramię z kłodą obraca się wokół słupa; SKOK nad niską, PADNIJ pod wysoką (postać skacze i pada) | okno czasu, akcja zależna od wysokości | 30–32 | 1,2 |
| Inteligencja „Runy” | patrzy, które z czterech kamieni świecą (każdy ze swoją nutą), i powtarza | kolejność, bez okna czasu na runę | ok. 26 run trafionych | 1,35 |
| Szczęście „Koniczyny” | przechodzi z koszykiem nad głową na tor koniczyny, schodzi spod kamienia | tor koszyka w chwili upadku (i 0,2 s przed) | 37–39 | 1,3 |

Wspólne dla nowych gier: podpowiedź obrazkowa na stanowisku i w odliczaniu (przyciski gry dopiero po odliczaniu,
naciśnięcia w odliczaniu nic nie robią); serwer decyduje (klient zgłasza tylko naciśnięcie albo ruch koszyka);
dźwięki z arkusza `swiat/dzwiek_gra`, gdy jest wgrany, inaczej wbudowane; reset postaci sprząta stanowisko, stawy
i HUD (jak w Sile i Pancerzu).

**Sprawdzone offline (wszystko kod 0):**

```
python -B swiat/trening_proba/dane.py --sprawdz               # aktualny (36 planów, 36 sekwencji wzorcowych)
python -B swiat/trening_proba/sprawdz_luau_treningu.py        # 4 pliki, OK (z parserem luau_mini)
python -B swiat/las_potwory/sprawdz_luau.py swiat/trening_proba/zrodla/*.luau   # 4 pliki, OK
python -B swiat/trening_proba/testy/test_treningu.py          # Ran 43 tests … OK (ok. 13 s)
python -B swiat/trening_proba/testy/proba_play.py --sprawdz   # 17 kawałków Luau, OK
python -B swiat/trening_proba/testy/zrzuty_gry.py --sprawdz   # 10 kawałków Luau, OK
python -B swiat/trening_proba/zbuduj.py --sucho               # sucho: OK (202 części, kod areny 39 tys. znaków)
```

- **Lustro logiki = Luau:** 118 przypadków wzorcowych (36 planów i 36 sekwencji — po 6 na grę — 26 przyrostów,
  12 wejść, 8 skal) daje to samo w Pythonie i w `LogikaTreningu.luau` (luau_mini); do tego 90 losowych planów i 72
  losowe sekwencje kroków ze wszystkich gier (stan rundy, tory Koniczyn, stan Run, podsumowanie).
- **Ocena wejścia przez serwer (2k–2n):** Bieżnia — zła stopa, za wcześnie, przepuszczony krok, „zawsze ta sama stopa”
  nie rośnie; Kłody — skok pod wysoką = pudło, zmiana wysokości nie zmienia oceny, pierwszy poziom tylko niskie; Runy —
  naciśnięcie w pokazie pominięte bez kary, dubel, zła runa skraca o 2, zaklęcie wydłuża o 1, po 8 nowe zaklęcie,
  ponowny pokaz po bezczynności niezależny od chwili sprawdzenia; Koniczyny — ruch nie jest werdyktem, stanie
  w miejscu = 0 jednostek (40 rund), koniczyna nie spada na tor lecącego kamienia (ponad 500 sprawdzeń), werdykt
  klienta przy upadku = werdykt serwera z zapasem.
- **Nadużycia (2e):** bot wciskający losowo 20 razy na sekundę przez całą rundę: Siła, Pancerz, Bieżnia, Kłody — 0
  jednostek; Koniczyny — 11% zysku gracza 80% (wymóg 0,2 s pod koniczyną); Runy — 16–18% gracza mylącego co dziesiątą
  runę (zgadywanie 1 z 4). Spam 100 zgłoszeń w 1 s — kubełek.
- **Opóźnienie sieci (2g):** gry czasowe — naciśnięcia idealne, wiadomość po 0–0,3 s → wszystko trafia; Koniczyny —
  ruchy dochodzą do serwera po 0–0,3 s i w innej kolejności, serwer co tik → ten sam wynik co klient, 0 pudeł.
- **Balans (2h, D-074):** jednostki na minutę gracza-modelu względem Siły: Pancerz 0,97, Bieżnia 0,98, Kłody 1,02,
  Runy 0,96, Koniczyny 1,03 (test: 0,85–1,18). Celność modelu: 83–94%.
- **Przerwanie i koniec rundy (2o)** w każdej z sześciu gier; podsumowanie z rozstrzygniętych prób.
- **Scena (4a–4e):** 202 części w obrysie areny, bez powtórzonych nazw; części animowane istnieją (pasy taśmy, cele
  stóp, bęben, pałka, ramię z kłodą, znaki run, kula maga, tory); z kamery każdej nowej gry widać to, na co gracz
  reaguje (ślady na całej drodze, kłodę nisko i wysoko, cztery kamienie, trzy tory od korony do koszyka); ramię
  z kłodą obraca się (co 5°, obie wysokości) bez zahaczenia o lite części; miejsce gracza wolne (na taśmie — nad nią).
- **Telefon (5a–5d):** każdy przycisk ≥ 44 px przy skali 0,85, teksty ≥ 12 pt; przy 667 × 375, 568 × 320 i 812 × 375
  przyciski każdej gry, status i „X” mieszczą się i nie nachodzą na siebie, przyciski w dolnej części ekranu;
  podpowiedź obrazkowa między statusem a panelem startu; brak napisów dla twórców (także w zagnieżdżonych tekstach).
- **Styki (6a–6h):** adres arkusza dźwięku tylko raz i tylko z identyfikatora w katalogu; zdarzenia dźwięku istnieją
  w `swiat/dzwiek_gra/ustawienia.json`; `proba_play.py` ma T01–T22 i `--sprawdz`; `podglad.py` nie ładuje numpy przy
  imporcie.

**Podglądy stanowisk** (`podglady/`, render brył z kamery gry + przykładowa chwila i zarys przycisków — *ocenione na
oko*, nie zrzut z gry): `podglad_kondycja.jpg`, `podglad_zrecznosc.jpg`, `podglad_inteligencja.jpg`,
`podglad_szczescie.jpg`, a także `podglad_sila.jpg`, `podglad_pancerz.jpg` i `podglad_arena.jpg` (cała arena).
Podglądy zmieniły projekt trzy razy: biegacz twarzą do kamery (za plecami zasłaniał ślady), koszyk nad głową (przed
postacią zasłaniało go ciało), postać i mag w Runach z boku (zasłaniali kamienie).

**Część B (Studio, w tej kolejności):** `python -B tools/studio_okno.py --na-wierzch` → `python -B
swiat/trening_proba/zbuduj.py` (pełna budowa — zmienia się arena) → `python -B swiat/trening_proba/testy/proba_play.py
<folder poza repo>` (T01–T22) → `python -B swiat/trening_proba/testy/zrzuty_gry.py` (24 zrzuty do `klatki/`) →
obejrzenie zrzutów i poprawki → regresja `python -B swiat/przejscie_gry/proba_dymna.py`.

**Obejrzenie ręcznie w Studio (nowe gry):** Play → E przy tablicy → GRAJ przy Kondycji → START → A / D (albo ← / →),
gdy ślad dojedzie do białej linii → INNA GRA → Zręczność → spacja nad niską kłodą, S pod wysoką → INNA GRA →
Inteligencja → patrz na kamienie, potem strzałki w tej samej kolejności → INNA GRA → Szczęście → A / D pod koniczynę,
z dala od cienia kamienia → WYJDŹ.

**Czego nie sprawdzono (nowe gry):** nic z czterech nowych gier nie było jeszcze uruchomione w Studio — rysowanie
stanowisk, ruch postaci (bieg z Animate, przesunięcie biodra, przejścia z koszykiem, podniesione ręce), dźwięki
z arkusza, czas klatki i czytelność na prawdziwym ekranie to część B. Gracz-model w testach to założenie (reakcja,
celność) — prawdziwe dziecko do oceny przez Karola i Pawła.

**Znane ryzyka (nowe gry):** przesunięcie stawów (`C0`) widać tylko u siebie (inni gracze widzą stojącą postać);
podniesione ręce tylko dla R15; animacja biegu tylko, gdy awatar ma domyślny skrypt Animate; „ZA PÓŹNO” w Koniczynach
może dziwić dzieci; w Runach zgadywanie daje trochę; arena jest dłuższa (256 st) — `zbuduj.py` sprawdza, że w jej pudle
nie ma cudzych części.

## Poprawki układu na telefonie (18.11.2026, bez Studio — do wdrożenia)

Po zrzutach telefonu z części B (koordynator): przyciski Run zasłaniały romb i krzyż, panel rundy — koronę drzewa
Koniczyn, prawy przycisk — prawy tor, a przyciski Bieżni — dolny odcinek taśmy.

- **Jeden układ dla klienta i testu:** `L.ukladUI(D, gra, szer, wys, skala)` (lustro `logika_treningu.uklad_ui`) liczy
  prostokąty panelu rundy, przycisku przerwania, kropek Run i przycisków każdej gry w obszarze GUI; klient ustawia
  z niego położenia (`odswiezSkale`, także przy wejściu na stanowisko), a obszar GUI omija pasek Robloxa i wycięcia
  ekranu (`ScreenInsets = CoreUISafeInsets`).
- **Zwarty panel rundy:** 210 × 52 (było 268 × 92): czas · seria · mnożnik w jednym wierszu i pasek statystyki pod
  nim; razem z „X” najwyżej 40% szerokości i 18% wysokości ekranu (test). Punkty w rundzie pokazuje napis „+1 …!”
  i podsumowanie.
- **Przyciski przy krawędziach ekranu:** prawe skupisko przy prawej krawędzi (było na 78,5% szerokości — miejsce
  zostawione dla kolumny HUD-u, a HUD jest na stanowisku schowany), lewe przy lewej. Rozmiary bez zmian (≥ 44 pt).
- **Kamery:** Bieżnia — oko (0; 8,4; 14,5), cel (0; 1,4; −0,5) (o 1 st niżej: ślady widać od pojawienia się aż do
  linii); Koniczyny — oko (0; 9,4; 17,5), cel (0; 8,1; −6) (o 4 st dalej i wyżej: korona, początek spadania i trzy
  tory pod panelem i między przyciskami). Pozostałe cztery gry bez zmian — mieściły się.
- **Test 5e:** dla sześciu gier i czterech ekranów (667 × 375; 844 × 390 z wycięciami 47 px po bokach i paskiem 21 px
  na dole; 1280 × 720; tablet 1024 × 768) rzutuje pole gry (`scena.pole_gry`: kamienie, tory od korony do koszyka,
  ślady na całej taśmie, nadlatująca kłoda nisko i wysoko z ćwierci obrotu, strefy Siły, pięść i golem) kamerą
  stanowiska (pionowy kąt 70°) i sprawdza, że każdy punkt jest w obszarze GUI i żaden nie leży pod panelem ani
  przyciskiem (zapas 6 px). Przed poprawką: Bieżnia — ślady poza dołem ekranu na wszystkich czterech, Koniczyny —
  prawy tor pod „X” na trzech; teraz 24 × OK. Test 5c: prostokąty układu nie nachodzą na siebie na tych ekranach.
  Testy offline: **44 × OK**.
- **Ekran pionowy:** gra trzyma poziom (domyślne ustawienie Robloxa; orientacja to sprawa okien Pawła) — układ liczony
  dla poziomu.
- **Ręce w Koniczynach:** pomiar w Studio (18.11, 01:19) — oba barki odwrócone w górę (AnimationConstraint); dłonie
  chowają się za koszykiem trzymanym nad głową, dlatego na zrzucie ich nie widać. Bez zmian.
- Podglądy (`podglady/`) rysują przyciski z tego samego układu.

**W oknie Studio:** `python -B swiat/trening_proba/zbuduj.py` (pełna — zmieniają się dane i skrypty), potem
`python -B swiat/trening_proba/testy/zrzuty_gry.py --telefon` (zrzuty 26–37: sześć gier w rundzie przy 667 × 375
i 844 × 390 + pomiar napisów i przycisków). Zrzut z emulacją wycina prostokąt telefonu z widoku okna Studio, więc kadr
3D przy 844 × 390 jest przybliżony — dokładny rachunek robi test 5e.

## Część B — cztery nowe gry w Studio (18.11.2026, 00:51–01:40, tryb Play)

**Warunki.** Miejsce gry (PlaceId 129485428021967), jeden gracz, okno gry 2041 × 1153, Studio na wierzchu (nakładka
nocna). W miejscu m.in. przebudowany `StanGracza` (zapis postępu wyłączony), `KowalProba`, `PetyProba`, bazar.
Próba porównuje atrybuty sesyjne `Trening…` (przed i po rundzie), nie stałe liczby statystyk.

1. `python -B swiat/trening_proba/zbuduj.py`: „pudło areny wolne | SpawnLocation: 1 | MiasteczkoBazarGra: true |
   trener w bazarze (E training_center): true”, „części areny: 202, podpowiedzi: 2”, tablica wejścia (−12,9; 0,8; 5,4),
   na końcu „instancji: 284, skryptów: 4, części: 208, podpowiedzi E: 3”, bez „UWAGA”.
2. Pierwsza próba (`proba_play.py --nowe`): T01, T15, T17–T22 OK; **T16 BŁĄD** — runda Kłód bez pudła, ale postać nie
   skakała i nie padała. Przyczyna: awatar w tym miejscu ma **15 AnimationConstraint i 0 Motor6D** (nowe stawy
   Robloxa), a klient szukał tylko Motor6D. Poprawka w kliencie: staw może być Motor6D (`C0`) albo AnimationConstraint
   (`CFrame` jego `Attachment0`) — to samo dla barków w Koniczynach. Przy okazji szersza tablica Bieżni (napis
   „KONDYCJA — BIEŻNIA” łamał się, druga linia za głową biegacza). Przebudowa, testy offline dalej 43 × OK.
3. Pełna próba `proba_play.py <folder poza repo>` (T01–T22, 00:59–01:09): **21 × OK, T11 BŁĄD** — wyjście wracało
   4,56 st od P0, bo nowy punkt T20 (reset postaci) odradza postać, a kolejne wejście zapamiętuje nowy punkt powrotu.
   T11 porównuje teraz z punktem powrotu zapamiętanym przez serwer przy ostatnim wejściu; powtórka `--tylko T11,T12`:
   **T11 OK (0,0 st)**. Razem **22 × OK**, wyniki (`wyniki.json`, `lista.txt`) poza repozytorium.

| Punkt | Wynik w Studio |
|---|---|
| T01 | „OK 118/118”, 3 podpowiedzi, **6/6 grywalnych kafelków**, arkusz dźwięku znaleziony |
| T02–T10, T12–T14 | jak 17.11 (Siła 45/45, 309 jednostek, 3 punkty; spam 56/60; werdykty; Pancerz 42/43 z jedną zablokowaną zmyłką; telefon 52 px / 15 pt, 568 × 320: 44,3 px / 12,8 pt; konsola bez błędów) |
| T15 Bieżnia | 67/67, pudła 0, 3 punkty (oczek. 3), 339,5 jednostki (oczek. 339,5), animacja biegu gra, A / D / ← / → → 4 zgłoszenia, postać nie przesunięta, podpowiedź obrazkowa na stanowisku i w odliczaniu |
| T16 Kłody | 31/31, pudła 0, 3 punkty; staw biodra przesunięty w rundzie, po rundzie wszystkie stawy jak przed; spacja i S → 3 zgłoszenia |
| T17 Runy | naciśnięcie w pokazie → „pokaz” (bez kary); 37 run, pudła 0, 7 zaklęć, najdłuższe 8, 3 punkty; zła runa: długość 3 → 2, pudło 1 |
| T18 Koniczyny | 28/28 złapanych, pudła 0, postać przechodziła między torami; 15 s bez ruchu: **0 jednostek**, 0 trafień, 10 pudeł (kamienie w koszyk) |
| T19 spam | po 60 naraz: odrzucone 54–56, jednostki ze spamu 0–4,8 (limit 8 × waga) |
| T20 reset w rundzie Kłód | (staw przesunięty) → serwer zdejmuje ze stanowiska, runda przerwana, klient: ekran „brak”, kamera Custom, dotyk przywrócony, HUD oddany, nowa postać bez zmian stawów |
| T21 klatka | Bieżnia śr. 16,7 ms, p95 18,0 ms; Koniczyny 16,7 / 17,8 ms (60 kl./s) |
| T11 wyjście | (powtórka) 0,0 st od punktu powrotu, kamera Custom, W przesuwa o 9,9 st, brama → poza areną |
| T22 konsola | 0 błędów pakietu, zgodność logiki „OK 118/118” |

**Zrzuty z gry** (`klatki/`, `testy/zrzuty_gry.py --nowe`; lista graczy i czat schowane, własna postać bez nazwy):

| Plik | Co widać |
|---|---|
| `25_wybor_szesc_gier.jpg` | tymczasowe okno wyboru — sześć grywalnych mini-gier (GRAJ przy każdej) |
| `09_kondycja_start.jpg` | Bieżnia: stanowisko z podpowiedzią obrazkową (taśma i ślady → A / D → stopy) nad panelem START |
| `10_kondycja_runda.jpg` | Bieżnia w trakcie rundy: biegacz, ślady na torach, świecący cel przy linii, bęben trenera |
| `11_kondycja_podsumowanie.jpg` | podsumowanie: 68 / 0 / 100%, najdłuższa seria 68, **Kondycja +3** |
| `12_kondycja_telefon_667x375.jpg` | Bieżnia na ekranie telefonu (wycięty prostokąt emulacji): stopy po bokach, status u góry |
| `13_zrecznosc_start.jpg` … `16_zrecznosc_telefon_667x375.jpg` | Kłody: start z podpowiedzią (niska → SKOK, wysoka → PADNIJ), skok nad niską kłodą („ZWINNIE!”), podsumowanie z przyrostem, telefon |
| `17_inteligencja_start.jpg` … `20_inteligencja_telefon_667x375.jpg` | Runy: start z podpowiedzią (oko → runa → przycisk), pokaz („PATRZ!”, świecący zielony romb, kropki postępu, świecąca kula maga), podsumowanie z najdłuższym zaklęciem, telefon |
| `21_szczescie_start.jpg` … `24_szczescie_telefon_667x375.jpg` | Koniczyny: start z podpowiedzią, złapana koniczyna w koszyku nad głową („ZŁAPANE!”), podsumowanie ze złapanymi, telefon |

**Regresja całej gry:** `python -B swiat/przejscie_gry/proba_dymna.py <folder poza repo>` (01:16–01:18) — **14 × OK**
(D00–D13: start, teleport, walka, łup, powrót, trener w bazarze → okno wyboru, runda Siły, wyjście, klatka 16,7 ms,
konsola bez błędów).

**Otwarte (kosmetyka):** w Koniczynach ręce pod koszykiem — pomiar pokazuje obrócone stawy barków (AnimationConstraint,
oba ramiona odwrócone), ale na zrzucie dłonie są na wysokości barków, a nie nad głową; do sprawdzenia przy kolejnej
próbie.

**Czego dalej nie sprawdzono:** prawdziwy telefon i dotyk palcem (tylko emulacja 667 × 375), pad, dźwięki na słuch,
dwóch graczy naraz, opóźnienie sieci w prawdziwej grze; przesunięcie stawów widać tylko u siebie (inni gracze
widzą stojącą postać); rundy grał automat — trudność dla dziecka do oceny przez Karola i Pawła.

## Co sprawdzone bez Studio (17.11.2026 — Siła i Pancerz, przed nowymi grami)

Wszystkie polecenia zakończone kodem 0:

```
python -B swiat/trening_proba/dane.py --sprawdz               # aktualny (12 planów, 12 sekwencji wzorcowych)
python -B swiat/trening_proba/sprawdz_luau_treningu.py        # 4 pliki, OK (z parserem luau_mini)
python -B swiat/las_potwory/sprawdz_luau.py swiat/trening_proba/zrodla/*.luau   # 4 pliki, OK
python -B swiat/trening_proba/testy/test_treningu.py          # Ran 36 tests … OK (ok. 3 s)
python -B swiat/trening_proba/zbuduj.py --sucho               # sucho: OK (Studio nieużywane)
```

- **Dane (1a–1f):** generator powtarzalny i aktualny; bez BOM, dat, ścieżek i adresów w plikach pakietu; 11 rodzajów
  złych ustawień → błąd; sześć statystyk = lista z `B&C/Gra/System RPG.md`, atrybuty = `PlayerStatsDefaults`; styk
  z bazarem (id `training_center`, `OknoMiejsca`, nazwa `Punkty/E training_center`, atrybut wyłączający dymek);
  arena ≥ 500 st od każdego obszaru krain z `swiat/teleport_chmury/krainy.json`, starego miasteczka, lasu, dema,
  wyboru klasy i makiety chmur, 200 st nad mapami.
- **Logika (2a–2j):** 300 planów na grę (rosnące czasy, odstęp > 2 okna + 0,05 s, poziomy, kierunki, zmyłki
  10–25%); pasek (4 / 5 / 6 / 8 jednostek, próg 40, pula 30 → 670, malejący zysk) i wariant dosłowny D-050 (+1 / +2 /
  +3 za trafienie); brzeg okna, zły kierunek, za wcześnie, za późno, pusty, dubel, przepuszczone, zmyłka przeczekana
  i zablokowana; czas klienta z przyszłości, sprzed 0,45 s, tekst, NaN, ∞; 100 naciśnięć w 1 s → przyjęte ≤ 9;
  **bot spamujący 20/s przez 40 rund na grę: 0 jednostek** (gracz trafiający 80%: ok. 160 na rundę); opóźnienie sieci 0–0,3 s →
  wszystko trafia; balans: jednostki na minutę Siła / Pancerz w 0,85–1,18; 20 rund jednej gry → ostatnie 5 dają
  < 50% pierwszych 5, a świeża statystyka więcej.
- **Luau w luau_mini (3a–3e):** 4 pliki parsują się; `sprawdzPrzypadki` 70/70, a dwa zepsute przypadki są wykryte;
  60 planów, 40 losowych sekwencji z losowym stanem paska (kod werdyktów i wszystkie liczniki), podsumowanie,
  150 × wejście, 150 × arena, skala UI, ziarno z czasu, 41 × przyrost, 100 × pula i próg — identyczne z lustrem;
  dane w Luau = dane z Pythona; cały kod wysyłany do Studio parsuje się, bez niewstawionych `__…__`.
- **Scena (4a–4d):** 83 części, wymiary ≥ 0,05, wszystkie w obrysie areny, nazwy bez powtórzeń; części animowane
  i podpowiedzi istnieją; z kamery Siły widać każdą strefę i miotacza; tory lotu skrzynek (21 punktów łuku) nie
  przecinają żadnej litej części i są nad podłogą; z kamery Pancerza widać cel pięści i tarczę; ściany ≥ 12 st;
  miejsce gracza nad podestem wolne.
- **Telefon (5a–5d):** każdy przycisk w kliencie (11 wywołań `przycisk(…)`) ≥ 44 px przy skali minimalnej 0,85; teksty ≥ 12 pt;
  panele mieszczą się na 667 × 375, 568 × 320 i 812 × 375 (bez paska Robloxa 36 px); status, przycisk przerwania,
  krzyż i BLOK nie nachodzą na siebie; wybór opisany „TYMCZASOWY … (D-093)”.
- **Styki (6a–6g):** wiadomości zdalne w obie strony obsłużone; nazwy `WaitForChild` = tworzone przez budowę; gracz
  dostaje tylko atrybuty sesyjne; bez DataStore, `Lighting`, `rbxassetid://`, Toolboxa; dźwięki tylko z 11 plików
  wbudowanych; PlaceId = `cel_studio.py`; 3 + 1 punkty historii; `--sucho` nie importuje `studio_mcp`;
  `proba_play.py` się kompiluje, ma T01–T14 i bez argumentów wypisuje sposób użycia; strażnik Studio w każdym pliku.
- **Dodatkowo (poza testami):** zgrubne szukanie nazw globalnych w Luau — w serwerze, kliencie i logice brak
  niezadeklarowanych nazw (poza adnotacjami typów).

Liczby z modelu gracza (celność zależna od okna, 200 rund): Siła ok. 45 zdarzeń na rundę, Pancerz ok. 43;
ok. 170–195 jednostek paska na rundę. Świeża statystyka przy 10. poziomie daje ok. 3–4 punkty w pierwszej rundzie
i ok. 1 po dziesięciu rundach tej samej gry. Wariant dosłowny D-050 dałby ok. 70 punktów na rundę.

## Wdrożenie w Studio (17.11.2026, etap B)

Zrobione w tej kolejności (pracę w panelu zgłosił koordynator; sejf i panel uzupełnia on):

1. Offline: `test_treningu.py` (36/36) i `zbuduj.py --sucho` — kod 0.
2. `python -B swiat/trening_proba/zbuduj.py` (Edit): „pudło areny wolne | SpawnLocation: 1 | MiasteczkoBazarGra: true |
   trener w bazarze (E training_center): true”, „części areny: 83, podpowiedzi: 2”, „OK tablica wejścia (−12,9; 0,8; 5,4)
   — pierścień 14 st, kierunek 7 (próba 1) | start (0,0; 1,0; 0,0) z Workspace.SpawnLocation”, na końcu „instancji: 144,
   skryptów: 4, części: 89, podpowiedzi E: 3” bez „UWAGA”. Ostatnia budowa: skrót danych `b5bab2e3004e`.
3. Zrzuty w Edit (`tools/studio_zrzuty.py`, poza repo) i w Play → poprawki (niżej) → przebudowa → próba
   `testy/proba_play.py` → zrzuty `testy/zrzuty_gry.py` do `klatki/`.
4. Na końcu Studio w trybie **Edit**, kontener `Workspace/TreningProba` stoi (atrybut `Wygenerowane`). Miejsca nie
   zapisano ani nie opublikowano; `Lighting` i cudze kontenery (w tym `DzwiekGra`, lasy, walka) nietknięte.

Przed każdą próbą w Play: `python -B tools/studio_okno.py --na-wierzch` (kod 0) — z oknem w tle Studio rysuje 15 kl./s
i wyniki zależne od czasu są niemiarodajne.

## Co sprawdzone w grze (17.11.2026, Studio, tryb Play)

**Warunki.** Miejsce gry (PlaceId 129485428021967), jeden gracz, okno gry 2041 × 1153, Studio na wierzchu:
**czas klatki śr. 16,7 ms, p95 17,9 ms** (60 kl./s). W miejscu m.in. `MiasteczkoBazar` + `MiasteczkoBazarGra` (T03
z prawdziwym E przy trenerze). Ekran wyboru klasy zamykany Enterem przed listą (jak w próbach lasu-pasa).

**Lista T01–T14** — `python -B swiat/trening_proba/testy/proba_play.py <folder poza repo>`, przebieg końcowy o 10:28
(na ostatniej wersji kodu): **14 × OK**. Pierwszy przebieg (10:15, przed poprawkami wyglądu) też 14 × OK. Progów nie
luzowałem; jedyna zmiana próby: zamykanie ekranu wyboru klasy Enterem po starcie Play.

| Punkt | Wynik (przebieg końcowy) |
|---|---|
| T01 gotowość | OK — „OK 70/70”, 3 podpowiedzi, 6 kafelków (2 grywalne), zdarzenie `OknoMiejsca` podpięte |
| T02 tablica, prawdziwe E | OK — wybór otwarty, źródło `tablica` |
| T03 trener w bazarze, prawdziwe E | OK — wybór otwarty, źródło `bazar`; historia bazaru: `otwarto = TreningProba`, **`dymek = false`** (dymek „w budowie” nie wyskakuje) |
| T04 GRAJ prawdziwym kliknięciem | OK — postać 0,00 st od podestu, kamera Scriptable, dotyk wyłączony, punkt powrotu 0,00 st od miejsca przy tablicy |
| T05 runda Siły bez pudła | OK — trafienia 45/45, pudła 0, jednostki 309 (oczek. 309), punkty 3 (oczek. 3), `TreningSila` +3, sygnałów `PrzyrostStatystyki` 3 (oczek. 3), rozbieżności klient ↔ serwer 0 |
| T06 prawdziwe klawisze w rundzie | OK — 5 zgłoszeń z 6 klawiszy (spacja w Sile nic nie robi), postać przesunięta o 0,00 st |
| T07 spam 60 naraz | OK — 56 odrzuconych jako spam, 0 jednostek paska ze spamu |
| T08 werdykty | OK — 1 trafienie, 2 zły kierunek, 3 za wcześnie, 4 przepuszczone, 5–7 trafienia; po 7 seria 3 (podwójne kliknięcie przy 6 pominięte) |
| T09 Pancerz przez INNA GRA | OK — trafienia 41/42, pudło 1 (celowo zablokowana zmyłka), `TreningPancerz` +3 = suma rundy |
| T10 podsumowanie, JESZCZE RAZ | OK — panel podsumowania, prawdziwa spacja startuje nową rundę |
| T11 wyjście | OK — kliknięcie WYJDŹ: 0,0 st od miejsca sprzed wejścia, kamera Custom, dotyk przywrócony, W przesuwa postać o 9,9 st; brama WYJŚCIE (E) w arenie bez punktu powrotu → poza areną (spawn) |
| T12 telefon (rachunek) | OK — 667 × 375: przycisk 52 px, tekst 15 pt; 568 × 320: 44,3 px, 12,8 pt |
| T13 czas klatki | OK — śr. 16,7 ms, p95 17,9 ms (okno na wierzchu) |
| T14 konsola | OK — 0 błędów pakietu |

**Telefon 667 × 375 na zrzucie** (`testy/zrzuty_gry.py`, emulacja: atrybut kontenera `EmulacjaEkranu = Vector2(667, 375)`
u klienta — prostokąt telefonu bez paska Robloxa, powiększony ×3,06): najmniejszy widoczny napis **14,7 pt**,
najmniejszy przycisk **52 pt** („X”), strzałki 56 pt. HUD Pawła układa się względem całego okna, więc na zrzucie stoi
jak na telefonie o tych proporcjach.

## Poprawki po próbach w grze (17.11.2026)

1. **Czcionka** FredokaOne rysowała ę, ż, ś, ć, ź zastępczą, mniejszą czcionką („Bieżnia”, „Zręczność”, „mini-grę”).
   Teraz napisy okien i szyldów mają Nunito ExtraBold (`ui.czcionka`, `ui.waga_czcionki`) — wszystkie polskie znaki.
2. **Strefa „dół” zasłonięta przez postać** (kamera za plecami): strefa dalej przed stopami (z −2,6 na −3,2 st),
   a w czasie rundy własna postać jest półprzezroczysta u siebie (`LocalTransparencyModifier` 0,55, tylko u klienta).
3. **Telefon: krzyż zasłaniał prawą strefę**, a „X” (przerwij) wchodził na przycisk Quests HUD-u. Kamera patrzy teraz
   bardziej w prawo (cel x 1,6 → 6,0 w Sile, 1,2 → 5,5 w Pancerzu), więc gracz i strefy stoją w lewej połowie ekranu
   (prawa strefa ok. 0,45 szerokości, krzyż od 0,52). „X” stoi na lewo od statusu; pierścienie Pancerza i napis
   środkowy przesunięte za graczem (0,34 / 0,38).
4. **Tarcza** pokazywała od tyłu złotą ramę — rama jest teraz z przodu, gracz widzi niebieską płytę ze złotą obwódką.
5. **BLOK** był kwadratem (dwa UICorner) — teraz okrągły.
6. **Tablica wejścia**: słupki zasłaniały brzegi napisu → słupki poza deską (±3,95 st), napis krótszy
   („TRAINING CENTER / MINI-GRY”). Próba bez zawijania napisów w SurfaceGui (`TextWrapped = false`) dawała bardzo małe
   napisy na szyldach — cofnięte.
7. **Podłoga areny** ciemniejsza (BFA37A), żeby białe strefy i skrzynki odcinały się od tła.

## Zrzuty z gry (`klatki/`, tryb Play, 1280 px)

| Plik | Co widać |
|---|---|
| `01_tablica_wejscia.jpg` | tablica „TRAINING CENTER / MINI-GRY” przy miejscu startu, kamera gracza |
| `02_wybor_przy_trenerze.jpg` | tymczasowy wybór po prawdziwym E przy trenerze w budynku Training Center w bazarze (opis „TYMCZASOWY WYBÓR … D-093”) |
| `03_sila_trafienie.jpg` | Siła: „TRAFIONE!”, odłamki skrzynki, licznik serii i pasek w statusie |
| `04_sila_seria.jpg` | Siła: „SERIA 10!”, mnożnik ×1,50, pierwszy punkt Siły w statusie |
| `05_sila_pudlo.jpg` | Siła: „ZŁA STRONA” (zły kierunek), seria spada do 0; skrzynka „dół” widoczna przez półprzezroczystą postać |
| `06_pancerz_zamach.jpg` | Pancerz: fioletowy pierścień i fioletowe oczy golema (zmyłka), „STOI!” po bloku, tarcza, okrągły BLOK |
| `07_podsumowanie.jpg` | podsumowanie rundy Pancerza (42 z 42, seria 42, Pancerz +3, pasek 62/160) |
| `08_telefon_667x375.jpg` | Siła na ekranie telefonu 667 × 375 (wycięty prostokąt emulacji) |

Nazwy konta na zrzutach nie ma (własna postać nie ma nad sobą nazwy). Pełne wyniki prób (`wyniki.json`, `lista.txt`)
zostały poza repozytorium — zawierają nazwę konta.

## Czego nie sprawdzono

- **Prawdziwy telefon i dotyk** — tylko emulacja układu (rozmiary, nachodzenie); dotyk palcem, gęstość pikseli
  i wydajność telefonu nie.
- **Pad** — mapowanie klawiszy w danych (ABXY, krzyżak), bez próby z padem.
- **Dźwięki** — wczytują się z plików wbudowanych, ale nikt ich nie słuchał.
- **Dwóch graczy** (Test → Clients and Servers) — nie było próby; na jednym stanowisku staliby w tym samym miejscu.
- **Opóźnienie sieci** w prawdziwej grze — Studio lokalnie; tylko symulacja offline (0–0,3 s).
- **Prawdziwa ręka gracza**: rundy w próbie grał „autograj” (naciśnięcia w zaplanowanych chwilach tą samą drogą co
  klawisz), a prawdziwe klawisze sprawdzono w T06 (dochodzą i nie ruszają postaci). Trudność dla człowieka do oceny
  przez Karola i Pawła.
- **Zrzut 02** pokazuje wybór na tle wnętrza budynku (kamera przy trenerze opiera się o ścianę) — sam trener na nim
  nie jest widoczny.

## Znane ryzyka

- **Przyrost to propozycja z BALANS_1711, a nie D-050.** Hamulec W żyje tylko w sesji (atrybut sesyjny), więc
  ponowne wejście go zeruje. Przy niskim poziomie kolejne rundy tej samej gry dają 0–1 punktu, co może zniechęcać.
  Pasek w statusie pokazuje postęp mimo to.
- **Poziom gracza** bierzemy z atrybutu `Level` (`PlayerStatsDefaults`, placeholder) — dziś wszyscy mają 1.
- **Testy Luau offline** zależą od `tools/walka/luau_mini.py` (podzbiór Luau). Zgodność w Studio pokaże atrybut
  `ZgodnoscLogikiTreningu` przy starcie serwera.
- **Lobby areny** (tablica wyboru i brama wyjścia) to droga zapasowa — w normalnym przebiegu gracz od razu stoi na
  stanowisku z zablokowanym ruchem i wychodzi przyciskiem WYJDŹ albo klawiszem Q.
- **Arena w powietrzu**: gdyby gracz z niej spadł (np. błąd przeniesienia), zginie i odrodzi się na spawnie;
  serwer wtedy kończy rundę i czyści stan.

## Poprawki po przejściu gry (17.11.2026, bez Studio — do wdrożenia)

Raport `swiat/przejscie_gry/RAPORT_PRZEJSCIA.md` (M8, P1, P7). Zmienione: `ustawienia.json` (+ wygenerowany
`zrodla/DaneTreningu.luau`), `zrodla/KlientTreningu.client.luau`, `zbuduj.py`, `testy/test_treningu.py` (5d).
- **Bez napisów dla twórców:** okno wyboru pokazuje „Gotowe są dwie mini-gry — cztery kolejne już wkrótce.” zamiast
  „TYMCZASOWY WYBÓR… robi Paweł (D-093)”; podpowiedź E tablicy „Training Center” (bez „(próba)”); podsumowanie bez
  „(atrybut …, bez zapisu)”. Test 5d pilnuje tego w danych, w napisach klienta i w podpowiedziach.
- **Podsumowanie przerwanej rundy:** „Trafienia N · pudła M · celność P%” (z rozstrzygniętych prób), zamiast
  „Trafienia 2 z 43 (15%)”, gdzie 43 to wszystkie zdarzenia planu.
- **HUD schowany na stanowisku:** jak ekran walki — wszystkie włączone ScreenGui gracza (poza TouchGui, Freecam,
  LoadingScreen, ProximityPrompts i własnym) chowane od wejścia na stanowisko do zejścia i oddawane przy zejściu,
  także po resecie (CharacterAdded → zejście). Haczyk „stan” podaje `schowaneEkrany`.
- Wdrożenie: `python -B swiat/trening_proba/zbuduj.py` (pełna budowa — zmienia się tekst podpowiedzi tablicy).
