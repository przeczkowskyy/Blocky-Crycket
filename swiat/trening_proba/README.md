# Training Center — próba mini-gier (Siła i Pancerz)

*Status: **propozycja** (17.11.2026). **Etap A gotowy: projekt, kod, budowniczy i testy bez Studio. W Studio jeszcze
NIC nie stoi** — budowa i próba w trybie Play to etap B (lista niżej). Opis sześciu mini-gier, wybory dla ludzi
i ustawienia „przyjęte, do zmiany”: [`PROJEKT.md`](PROJEKT.md).
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
| `testy/proba_play.py` | próba w Studio (Play) z listą kontrolną T01–T14 i 6 zrzutami — **jeszcze nieuruchomiona** (etap B) |

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
| `TablicaWejscia` (Model, Persistent) | części | tablica „TRAINING CENTER / PRÓBA MINI-GIER (E)” 14–26 st od pierwszego SpawnLocation, na wolnym gruncie, z dala od „Nowe miasteczko (E)” bazaru i portalu startowego; miejsce wybiera budowa w Studio |

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

## Jak zbudować i obejrzeć (etap B)

```
python -B swiat/trening_proba/dane.py                    # po każdej zmianie ustawienia.json
python -B swiat/trening_proba/testy/test_treningu.py     # 36 testów, ok. 3 s
python -B swiat/trening_proba/zbuduj.py --sucho          # bez Studio: dane, Luau, strażniki, plan budowy
python -B swiat/trening_proba/zbuduj.py                  # Studio w trybie Edit: buduje / odbudowuje kontener
python -B swiat/trening_proba/zbuduj.py --skrypty        # tylko moduły i skrypty (arena i tablica zostają)
python -B swiat/trening_proba/zbuduj.py --usun           # usuwa Workspace/TreningProba
python -B swiat/trening_proba/testy/proba_play.py <folder poza repo>   # próba T01–T14 w trybie Play
```

Przy kilku oknach Studio dopisz `--studio <studio_id>`. Każdy wysyłany kod sprawdza `game.PlaceId == 129485428021967`
i tryb Edit. Budowa rusza tylko kontener z `Wygenerowane` (obiekt o tej nazwie bez atrybutu → STOP), a zanim cokolwiek
postawi, sprawdza, czy w pudle areny nie ma cudzych części (są → STOP). Stawia punkty historii przed i po (Ctrl+Z
cofa całość), niczego nie publikuje ani nie zapisuje, a `Lighting` zostaje nietknięte.

**Obejrzenie ręcznie w Studio:** Play → podejdź do tablicy „TRAINING CENTER / PRÓBA MINI-GIER” obok miejsca startu
(albo do trenera w budynku Training Center w bazarze) → E → w oknie „TYMCZASOWY WYBÓR” kliknij GRAJ przy Sile →
START (albo spacja) → strzałki / WASD w stronę skrzynki, gdy dolatuje do świecącego kółka → po rundzie podsumowanie →
INNA GRA → Pancerz → spacja, gdy pierścień dojdzie do kółka (fioletowy = zmyłka, nie blokuj) → WYJDŹ (albo Q).
Telefon: Test → Device → telefon w poziomie (667 × 375).

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

## Etap B — co dokładnie zrobić w Studio (ok. 1,5–2,5 h z jedną rundą poprawek)

1. `git pull`; offline: `test_treningu.py` i `zbuduj.py --sucho` (kod 0). Zgłoś pracę:
   `python panel/narzedzia/praca.py start --id trening-proba --tytul "Training Center: próba mini-gier" --koniec +120m --obszar studio:TreningProba --obszar swiat/trening_proba --stop-przy-kolizji`.
2. Studio w trybie Edit, miejsce gry. Najlepiej z `MiasteczkoBazar` i `MiasteczkoBazarGra` (T03 z prawdziwym E przy
   trenerze); bez nich T03 sprawdza tylko zdarzenie.
3. `python -B swiat/trening_proba/zbuduj.py` (ok. 1 min). Oczekiwane: „pudło areny wolne”, „części areny: 83,
   podpowiedzi: 2”, „OK tablica wejścia (x; y; z) — pierścień …” bez „BRAK WOLNEGO MIEJSCA” i „podpowiedzi E: 3”
   bez „UWAGA”.
4. Obejrzyj w Edit tablicę wejścia przy spawnie i arenę (zrzuty `tools/studio_zrzuty.py` albo kamerą). Gdy tablica
   stoi źle — atrybut `RecznyPunktTablicy` i ponowna budowa.
5. `python -B swiat/trening_proba/testy/proba_play.py <folder poza repo>` (ok. 8–10 min: cztery pełne rundy po 48 s).
   Wynik: `lista.txt`, `wyniki.json`, 6 zrzutów.
6. Ręcznie: emulator telefonu w poziomie (czy krzyż nie zasłania skrzynek, czytelność), dźwięki na słuch, pad, dwóch
   graczy (Test → Clients and Servers, 2).
7. Poprawki po próbie (najpewniej kamera, położenie krzyża i pierścieni, wysokości stref) w `ustawienia.json`, potem
   `dane.py` i `zbuduj.py --skrypty` (albo pełna budowa przy zmianie sceny), powtórka próby.
8. Raport ze zrzutami na panel (skill `panel`), wpisy w sejfie (`Zadania.md`, `Dziennik zmian.md`, notatka Training
   Center), `praca.py koniec`, commit i push (D-070).

## Czego nie sprawdzono (wszystko, co wymaga Studio)

- **Nic nie działało jeszcze w Studio.** Logika jest wykonana w interpreterze luau_mini, a serwer i klient tylko
  sparsowane i przejrzane. Błędy wykonania w API Robloxa (ContextActionService, GuiService, TweenService, PivotTo,
  RequestStreamAroundAsync, ModelStreamingMode) wyjdą dopiero w T01–T14.
- **Wygląd:** kąty kamery, czytelność skrzynek i stref, golem i pięść, strzałki z kresek w przyciskach, pierścienie
  Pancerza, kolory i obrys `Highlight` — ustawione na oko, bez żadnego zrzutu.
- **Pochłanianie ruchu** (wysoki priorytet ContextActionService) i wyłączanie sterowania dotykowego — zachowanie
  domyślnych skryptów sterowania Robloxa nie było sprawdzone.
- **Telefon i pad** — tylko rachunek rozmiarów; HUD Pawła zostaje pod spodem (wybór 5).
- **Dźwięki** — nazwy plików jak w `swiat/test_walki2` (tam sprawdzone wczytanie), brzmienia nikt nie słyszał.
- **Dwóch graczy na jednym stanowisku** — stoją w tym samym miejscu (każdy widzi tylko swoje skrzynki); nie ma
  osobnych miejsc na stanowisku.
- **Opóźnienie sieci w prawdziwej grze** — tylko symulacja offline (0–0,3 s).
- **Miejsce tablicy wejścia** — wybiera je budowa w Studio (siatka kandydatów przy pierwszym SpawnLocation).

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
