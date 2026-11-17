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
| Obiekt | Kierunek | Argumenty → wynik |
|---|---|---|
| `Sygnaly/Bohater` (BindableFunction) | las → stan | `Invoke(gracz)` → opis postaci dla `Silnik.symuluj` albo `nil` |
| `Sygnaly/PrzyznajLup` (BindableFunction) | las → stan | `Invoke(gracz, { lup = walka.lup, wynik, czas = walka.czas, zrodlo = "LasPotwory" \| "LasPasGra", gatunek, poziom })` → `{ ok = true }` \| `{ ok = false, powod }` |
| `Sygnaly/SterowanieSerwera` (BindableFunction) | testy | `"stan", gracz?` · `"zgodnosc"` · `"publikuj", gracz?` · `"bohater", gracz?` · `"przyznaj", gracz, lup` |
| `Zdalne/ZdarzeniaStanu` (RemoteEvent) | serwer → klient | `"awans", poziom, ile` |
| | klient → serwer | `"pokaz"` (bez liczb, najwyżej raz na 0,5 s) |
| `Workspace/TreningProba/Sygnaly/PrzyrostStatystyki` | trening → stan | tylko słuchamy (z ponownym podłączeniem po przebudowie) |

Atrybuty gracza, które pisze pakiet: `Level`, `XP`, `XPMax`, `Gold`, `Gems`, `Strength`, `Constitution`,
`Intelligence`, `Dexterity`, `Luck`, `Armor` (Pawła) oraz własne `ShardyEwolucji` i `TokenyKrainy_<kraina>`.
Atrybuty kontenera do podglądu: `SerwerStanuGotowy`, `ZgodnoscLogikiStanu` („OK 80/80”), `RozkladyZ`,
`TreningPodlaczony`, `LicznikLupow`, `LicznikPokazan`, `LicznikAwansow`, `LicznikBohaterow`, `LicznikTreningu`,
`OstatniLup`, `OstatniePokazanie`, `OstatniBohater`.

## Wyłączniki
- **Cały pakiet:** `python -B swiat/stan_gracza/zbuduj.py --usun` — gra wraca do stanu sprzed pakietu (las walczy
  postacią wzorcową z panelu, łupu nie ma).
- **Statystyki klasy:** atrybut kontenera `StatystykiKlasy = false` — zostają wartości testowe z `PlayerStatsDefaults`
  (Paweł); trening dalej dopisuje, bohater walki dalej czyta atrybuty (wtedy jest ok. 4× za mocny).
- **Tryb testowy lasu:** atrybut kontenera lasu `TestBohater = true` (`Workspace/LasPotwory` albo `Workspace/LasPasGra`)
  — reguła testowa T1 jak dawniej (klasa i poziom z panelu), walki bez łupu. Ustawiają go próby w Play
  (`swiat/las_potwory/testy/proba_play.py`, `kontrola_play.py`, `swiat/las_pas_gra/testy/proba_play.py`,
  `proba_dodatkowa.py`).

## Przyjęte, do zmiany (robocze — do decyzji ludzi)
1. **Krzywa doświadczenia** 11,71 × L^1,6 (z `tools/walka/tempo.py`; las ok. 30 min) zamiast stałego `XPMax = 100`.
2. **Przyrost co poziom:** +10 punktów rozdzielanych automatycznie rozkładem klasy (jak postać wzorcowa w balansie).
   D-057 mówi też o punktach do rozdania przez gracza — ich nie ma.
3. **Sloty umiejętności** 1 / 2 / 3 od poziomów 1 / 5 / 10 (jak dziś w walce). D-055 i D-088 mówią: sloty z drzewka,
   na start 0; pytanie 51 (Gemy) otwarte.
4. **Przegrana:** nic nie tracisz, dostajesz 20% doświadczenia (tak liczy silnik). W rejestrze nie ma decyzji.
5. **Tablica próby walki (`TestWalki2`) bez nagród** — to piaskownica (dowolna klasa i poziom 1/5/10).
6. **Broń i pancerz z przedmiotów** ze wzoru dla poziomu; ekwipunek z okna Pawła (dziś tylko po stronie klienta)
   i drzewko (`ST_*`) do walki nie wchodzą.
7. **Przed wyborem klasy** statystyki to rozkład Wojownika; zmiana klasy w trakcie gry (ChooseClass na to pozwala)
   przelicza rozkład, trening i „+” zostają.
8. **Gemy z łupu** dopisują się do testowych 1000 z `PlayerStatsDefaults`.
9. **Rozkłady klas** czytane z `ReplicatedStorage.Shared.ClassData` (paski ekranu wyboru Pawła). Zmiana pasków zmieni
   balans walki — test pilnuje, że dziś są równe wzorcowym.
10. **Baner „POZIOM N”** to tymczasowe GUI pakietu; docelowe pop-upy projektuje Paweł (D-093).
11. **Bez zapisu:** profil w pamięci serwera; po wyjściu z gry wszystko znika (jak dziś). Miejsce na zapis: profil
    (`L.nowyProfil`, pole `wersja`), `swiat/las_pas_gra/zrodla/PamiecGracza.luau`.

## Co zgłosić Pawłowi
- Jego atrybuty `Level`, `XP`, `XPMax`, `Gold`, `Gems` i sześć statystyk pisze teraz serwer pakietu (XPMax z krzywej,
  statystyki 30 pkt według klasy zamiast 20/16/18/12/7/57). Jego pliki są nietknięte; `PlayerStatsDefaults` dalej
  ustawia tylko brakujące wartości.
- Darmowy „+” (`StatPoints`) wzmacnia teraz bohatera w walce bez limitu — potrzebny koszt (Złoto, D-050) albo punkty
  z poziomu (D-057).
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
python -B swiat/stan_gracza/testy/test_stanu.py        # 39 testów, w tym SerwerStanu i KlientStanu w luau_mini
python -B swiat/stan_gracza/sprawdz_luau_stanu.py      # kontrola statyczna Luau
python -B swiat/stan_gracza/zbuduj.py --sucho          # plan budowy
python -B swiat/stan_gracza/symulacja_lasu.py          # szanse w przegrodach lasu-pasa i czas do Strażnika
```
W Studio (część B): `zbuduj.py` buduje kontener; potem wymiana skryptów obu lasów
(`python -B swiat/las_potwory/zbuduj.py --skrypty`, `python -B swiat/las_pas_gra/zbuduj.py --skrypty`) i próba w Play:
```
python -B swiat/stan_gracza/testy/proba_play.py <folder wyników poza repo>   # S00–S12, zrzuty → klatki/
python -B swiat/stan_gracza/testy/proba_play.py --sprawdz                    # bez Studio: parsuje kawałki Luau próby
```
Próba sprawdza: trzy klasy w walce na poziomie gracza, łup dopiero po walce i HUD = atrybuty, baner awansu,
przegraną (+20% XP), trening Siły → Strength → opis bohatera, tryb testowy `TestBohater`, brak sygnału i usunięcie
kontenera (las działa jak dawniej), konsolę, `script_grep` po innych piszących Gold / XP / DataStore / leaderstats,
oraz pomiar poprawki M6 lasu (15 podejść prawdziwym E z dawną kotwicą i 15 z nową; dymek przy blokadzie po walce).
Wyniki mogą zawierać nazwę konta, dlatego folder wyników musi być poza repozytorium; zrzuty są bez listy graczy i czatu.
`--tylko-m6` powtarza sam pomiar M6 (gracz staje 4,5 studa od potwora i wciska E po 1,5 s, jak człowiek).

Wynik w Studio 17.11.2026 (13:50–14:15): S00–S12 OK; M6 — walka ruszyła w 5 z 15 prób z dawną podpowiedzią i w 13 z 15
po poprawce (histereza zasięgu 7 przy zapasie serwera 10; obie nieudane dały dymek „Podejdź bliżej potwora…”).

## Liczby z symulacji (17.11.2026, propozycja)
Bohater na prawdziwym poziomie, bez treningu: pierwsza przegroda (Leśny Slime poz. 1) na poziomie 1 to 84–88% wygranych.
Przejście lasu-pasa do wygranej ze Strażnikiem: mediana ok. 27 min przy walkach ×1 (Mag 25, Wojownik i Zwiadowca 28),
ok. 19 min przy ×2. Gracz dochodzi do Strażnika na 10. poziomie i wygrywa z nim na 11., zwykle za drugim razem,
z ok. 8 przegranymi po drodze. Cel planu rosnącego z `tools/walka/tempo.py`: ok. 30 min na Las. Pełne tabele:
`python -B swiat/stan_gracza/symulacja_lasu.py --md <plik>`.

## Pliki
- `dane.py` → `zrodla/DaneStanu.luau` (wygenerowany; liczby z `tools/walka/wzorcowe.py`, `tempo.py`,
  `src/server/Walka/Statystyki.luau`), `logika_stanu.py` (lustro `zrodla/LogikaStanu.luau`).
- `zrodla/SerwerStanu.server.luau`, `zrodla/KlientStanu.client.luau`, `zrodla/LogikaStanu.luau`.
- `zbuduj.py`, `sprawdz_luau_stanu.py`, `symulacja_lasu.py`, `testy/test_stanu.py`, `testy/atrapa_roblox.py`.
- Zmiany w innych pakietach (małe, w osobnych funkcjach): `swiat/las_potwory/zrodla/Stale.luau` (stałe stanu gracza),
  `SerwerPotworow.server.luau` (`sygnalStanu`, `bohaterZeStanu`, `nagrodaZaWalke` + dwa wywołania w kontroli 7
  i po przyjęciu walki), `KlientPotworow.client.luau` (`trybTestowyBohatera`, `poziomGracza`,
  `zsynchronizujBohatera`, napis panelu). Las-pas używa tych samych źródeł.
