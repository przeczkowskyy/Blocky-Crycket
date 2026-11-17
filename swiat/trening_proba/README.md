# Training Center — próba mini-gier (Siła i Pancerz)

*Status: **propozycja** (17.11.2026). **Wdrożone w Studio i sprawdzone w trybie Play 17.11.2026 przed południem**
(etap B): lista T01–T14 zaliczona, zrzuty z gry w `klatki/`, wyniki w „Co sprawdzone w grze”. Opis sześciu mini-gier,
wybory dla ludzi i ustawienia „przyjęte, do zmiany”: [`PROJEKT.md`](PROJEKT.md).
Wymagania: D-050, D-063, D-074, D-085, D-093 (✅) i model statystyk D-062 (✅). Przyrost według propozycji
`tools/walka/BALANS_1711.md`, część 6 — to nie jest decyzja (wybór 1 w PROJEKT.md).*

> **W skrócie.** Jeden kontener `Workspace/TreningProba` (atrybut `Wygenerowane = true`). Arena z 83 klocków stoi
> w powietrzu, z dala od map, w (3000; 300; 3000). Są w niej dwa grywalne stanowiska — **Siła „Rozbijanie”**
> (miotacz rzuca skrzynki, gracz rozbija je strzałką w ich stronę) i **Pancerz „Blok”** (golem uderza, gracz blokuje
> w chwili ciosu i nie daje się nabrać na zmyłki) — oraz cztery zapowiedzi „w projekcie”. Wejście: E przy trenerze
> w bazarze (zdarzenie `OknoMiejsca`, bez zmian w pakiecie bazaru) albo E przy własnej tablicy obok miejsca startu.
> Otwiera się **tymczasowy** wybór mini-gry (docelowe okno 2D robi Paweł). Serwer decyduje o przyrostach i zapisuje je
> w atrybutach sesyjnych gracza (`TreningSila`, `TreningPancerz`; bez DataStore), a do tego ogłasza je sygnałem
> `Sygnaly/PrzyrostStatystyki`. WYJDŹ wraca gracza tam, skąd przyszedł.

## Pliki

| Plik | Co to jest |
|---|---|
| `PROJEKT.md` | sześć mini-gier (PROPOZYCJA), wybory dla ludzi, ustawienia „przyjęte, do zmiany” |
| `ustawienia.json` | **jedyne źródło liczb**: statystyki, runda, poziomy trudności, pasek przyrostu, ochrona przed spamem, układ areny i stanowisk, telefon (rozmiary), klawisze, dźwięki, teksty |
| `dane.py` | generator `zrodla/DaneTreningu.luau` (położenia w świecie, przypadki wzorcowe z lustra); `--sprawdz`, `--wyjscie DIR` |
| `logika_treningu.py` | lustro `zrodla/LogikaTreningu.luau` w Pythonie (plan rundy, werdykty, pasek, spam, wejście, skala UI) |
| `scena.py` | arena z prostych części (83): podłoga, murki, niewidzialne ściany, lobby z tablicą wyboru i bramą wyjścia, stanowiska, zapowiedzi |
| `zrodla/LogikaTreningu.luau` | czysta logika (ModuleScript) — ta sama co lustro; serwer sprawdza ją przy starcie (70 przypadków) |
| `zrodla/SerwerTreningu.server.luau` | serwer: werdykty i przyrosty, ochrona przed spamem, wejście i wyjście, podpowiedzi E, sygnał dla modułu statystyk, haczyk testowy |
| `zrodla/KlientTreningu.client.luau` | klient: własny ScreenGui (tymczasowy wybór, status, sterowanie, podsumowanie), kamera stanowiska, pochłanianie ruchu, efekty i dźwięki, `OknoMiejsca`, uchwyt `WybierzGre` |
| `zrodla/DaneTreningu.luau` | **wygenerowany** — nie edytować ręcznie |
| `sprawdz_luau_treningu.py` | kontrola statyczna Luau (reguły jak w bazarze + zakaz zasobów spoza Robloxa i rozmiarów tekstu z literałów) |
| `zbuduj.py` | budowa w Studio: `--sucho`, `--skrypty`, `--usun`, `--studio` |
| `testy/test_treningu.py` | 36 testów offline (opis w nagłówku pliku) |
| `testy/proba_play.py` | próba w Studio (Play) z listą kontrolną T01–T14 i 6 zrzutami roboczymi (wyniki poza repo) |
| `testy/zrzuty_gry.py` | 8 zrzutów z gry do `klatki/` (1280 px) i pomiar ekranu telefonu 667 × 375 (emulacja atrybutem `EmulacjaEkranu`) |
| `klatki/` | zrzuty z gry (tryb Play) — tabela w „Zrzuty z gry” |

## Co powstanie w kontenerze `Workspace/TreningProba`

| Ścieżka | Klasa | Co robi |
|---|---|---|
| `Moduly/DaneTreningu`, `Moduly/LogikaTreningu` | ModuleScript | dane (wygenerowane) i logika |
| `SerwerTreningu` (RunContext Server), `KlientTreningu` (RunContext Client) | Script | poza Studio serwer usuwa cały kontener (jak inne prototypy) |
| `Zdalne/ZdarzeniaTreningu` | RemoteEvent | klient → serwer: `wejdz`, `start`, `akcja`, `przerwij`, `wyjdz`; serwer → klient: `wybor`, `odmowa`, `przybycie`, `runda`, `wynik`, `koniec`, `wyjscie` |
| `Sygnaly/PrzyrostStatystyki` | BindableEvent | **dla przyszłego modułu statystyk** (dziś nikt go nie słucha) |
| `Sygnaly/WybierzGre` | BindableFunction (klient) | **uchwyt dla docelowego okna 2D Pawła** |
| `Sygnaly/SterowanieSerwera`, `Sygnaly/SterowanieKlienta` | BindableFunction | haczyki testowe |
| `Arena` (Model, `ModelStreamingMode = Persistent`) | części | podłoga 96 × 56 st, murki i niewidzialne ściany 14 st, stanowiska Siły i Pancerza, zapowiedzi, lobby: tablica „WYBÓR MINI-GRY (E)” i brama „WYJŚCIE (E)” (zapasowe — gracz trafia od razu na stanowisko) |
| `TablicaWejscia` (Model, Persistent) | części | tablica „TRAINING CENTER / MINI-GRY” z podpowiedzią E 14–26 st od pierwszego SpawnLocation, na wolnym gruncie, z dala od „Nowe miasteczko (E)” bazaru i portalu startowego; miejsce wybiera budowa w Studio |

Atrybuty kontenera: `Wygenerowane`, `Zrodlo`, `Zbudowano`, `Skrot`, `PunktTablicy`, **`WyborTymczasowy`** (true; false
= tymczasowy wybór się nie otwiera, bo jest okno Pawła). Ręczne w Edit i przenoszone przy odbudowie:
`WyborTymczasowy`, `RecznyPunktTablicy` (Vector3 na gruncie — własne miejsce tablicy). W Play serwer ustawia
`SerwerTreninguGotowy`, `ZgodnoscLogikiTreningu` („OK 70/70”), `Podpowiedzi` (3), liczniki `LicznikWejsc`,
`LicznikRund`, `LicznikTrafien`, `LicznikPudel`, `LicznikSpamu`, `LicznikSygnalow`, `LicznikOdmow`, `OstatniWynik`,
`OstatniaOdmowa`, a klient (u siebie) — `KlientTreninguGotowy`. Atrybuty gracza: `TreningSila`, `TreningPancerz`
(punkty w tej sesji), `TreningGra`, `TreningSeria`. Atrybutów `Strength`, `Armor`… (`PlayerStatsDefaults`) pakiet nie
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
python -B swiat/trening_proba/testy/test_treningu.py     # 36 testów, ok. 3 s
python -B swiat/trening_proba/zbuduj.py --sucho          # bez Studio: dane, Luau, strażniki, plan budowy
python -B swiat/trening_proba/zbuduj.py                  # Studio w trybie Edit: buduje / odbudowuje kontener
python -B swiat/trening_proba/zbuduj.py --skrypty        # tylko moduły i skrypty (arena i tablica zostają)
python -B swiat/trening_proba/zbuduj.py --usun           # usuwa Workspace/TreningProba
python -B swiat/trening_proba/testy/proba_play.py <folder poza repo>   # próba T01–T14 w trybie Play (ok. 4 min)
python -B swiat/trening_proba/testy/zrzuty_gry.py                      # 8 zrzutów do klatki/ (ok. 2 min)
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

## Co sprawdzone bez Studio (17.11.2026)

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
