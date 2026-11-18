# Dźwięk gry — własne efekty, muzyka stref i muzyka kontekstów

> **Status: propozycja (17.11.2026, rozszerzona 18.11.2026), prototyp — działa tylko w Roblox Studio.**
> Stan na 18.11.2026: nowy kod muzyki (arkusz muzyki, utwory zastępcze, konteksty) jest w repozytorium i przeszedł
> testy bez Studio, ale **nie był jeszcze wysłany do Studio ani uruchomiony w Play** — w miejscu stoi wersja
> sprzed tej zmiany, dopóki ktoś nie uruchomi budowniczego.

## Stan na 18.11.2026 — co gra gdzie

| Gdzie | Co gra | Plik w Roblox |
|---|---|---|
| walka: efekty | 22 efekty jako odcinki arkusza `sfx_arkusz_a.ogg` | wgrany 17.11, identyfikator wpisany |
| bazar, plac startowy, stare miasteczko | trzy utwory miasteczka na zmianę | wgrane 17.11, wpisane |
| las-pas, stary las | dwa utwory lasu na zmianę | wgrane 17.11, wpisane |
| Bagno | własne: `muzyka_06_bagno_petla` (osobny plik) i `muzyka_06_bagno_b_petla` (arkusz muzyki); dopóki żaden nie ma identyfikatora — zastępczo dwa utwory lasu, ciszej | osobny plik wgrany 18.11 (jest w `assets/audio/wgrane.json`), **identyfikator jeszcze niewpisany** → dziś grają zastępcze |
| Dżungla | własne: `muzyka_07_dzungla_petla` i `muzyka_07_dzungla_b_petla` (arkusz); zastępczo utwory lasu | jak Bagno |
| walka (kontekst) | `muzyka_13_walka_petla` z arkusza muzyki | **arkusz niewgrany** → muzyka strefy przyciszona, jak dotąd |
| walka ze Strażnikiem krainy | `muzyka_14_walka_straznik_petla` z arkusza (bez niego: utwór zwykłej walki) | arkusz niewgrany → jak wyżej |
| mini-gry Training Center | `muzyka_15_trening_petla` z arkusza | arkusz niewgrany → muzyka strefy |
| menu główne (ekran Pawła) | nic — tylko pozycja w katalogu | niewgrane |

**Czeka na wgranie:** `assets/audio/arkusz/muzyka_arkusz_b.ogg` (jeden plik, 395,4 s, 8,37 MB: walka, Strażnik, trening,
Bagno B, Dżungla B) — po odsłuchu i zgodzie człowieka. **Czeka na wpisanie:** identyfikatory Bagna i Dżungli (niżej).

## W skrócie

- **Kontener** `Workspace/DzwiekGra` (atrybut `Wygenerowane = true`): moduł `Moduly/KatalogDzwiekow`, skrypt klienta
  `MuzykaStref` i haczyk testowy `Sygnaly/SterowanieMuzyki`. Żadnych części, niczego nie zmienia w cudzych kontenerach.
- **Efekty walki**: 22 efekty w jednym pliku-arkuszu; odtwarzacz walki prototypu
  (`swiat/test_walki2/zrodla/OdtwarzaczWalki2.luau`) gra z niego odcinki (`Sound.PlaybackRegion`). Bez zmian od 17.11.
- **Muzyka stref**: utwory strefy na zmianę, każdy raz do końca, płynne przejścia. Utwór to osobny plik albo
  **odcinek arkusza muzyki** (kilka utworów w jednym pliku — jedno wgranie do Roblox zamiast kilku).
- **Muzyka kontekstów** (nowe): walka, walka ze Strażnikiem krainy i mini-gry mają własne utwory; muzyka strefy
  przenika w muzykę kontekstu i wraca po nim (od miejsca, w którym ucichła). Kontekst bez wgranego utworu = zachowanie
  dotychczasowe (w walce muzyka strefy przyciszona, w mini-grze muzyka strefy).
- **Wpisanie identyfikatorów po wgraniu**: `python -B swiat/dzwiek_gra/zbuduj.py --identyfikatory <plik.json>`.

## Pliki

| Plik | Co to |
|---|---|
| `zbuduj.py` | budowniczy: `--sucho` (odświeża katalog, kontrola, plan), pełna budowa, `--skrypty`, `--usun`, `--identyfikatory plik.json`, `--studio <id>` |
| `ustawienia.json` | głośności efektów, zdarzenie walki → efekt, odgłosy potworów; muzyka: strefy (utwory, utwory zastępcze, głośność), konteksty (utwory, gatunki Strażników, atrybut mini-gry), arkusze muzyki (mapy), czas przejścia, przyciszenie w walce |
| `identyfikatory.json` | identyfikatory zasobów Roblox: `arkusz` (efekty), `arkusze_muzyki` (pliki z kilkoma utworami), `muzyka` (utwory wgrane osobno); 0 = jeszcze nie wgrane albo niewpisane |
| `zrodla/KatalogDzwiekow.luau` | **wygenerowany** z mapy arkusza efektów (`assets/audio/arkusz/sfx_arkusz_a.json`), map arkuszy muzyki (`assets/audio/arkusz/muzyka_arkusz_*.json`), `ustawienia.json` i `identyfikatory.json` — nie edytować ręcznie |
| `zrodla/MuzykaStref.client.luau` | klient: strefa z położenia postaci, kontekst (walka / Strażnik / mini-gra), utwory na zmianę, odcinki arkusza, przenikanie, przyciszenie |
| `testy/test_dzwieku.py` | testy bez Studio (24): katalog = mapy i ustawienia, arkusz muzyki, utwory zastępcze, konteksty i ich wykrywanie względem cudzych źródeł, wpisywanie identyfikatorów, strażniki, tylko odczyt cudzych kontenerów |
| `testy/proba_play.py` | próba w Play (lista D1–D10 w nagłówku; D7–D10 nowe, jeszcze nieuruchomione) |

Narzędzia audio: `tools/audio_petla.py` (wyrównanie głośności i pętla), `tools/audio_arkusz_muzyki.py` (arkusz muzyki
i jego mapa), `tools/audio_arkusz.py` (arkusz efektów). Opis plików audio: `assets/audio/README.md`.

## Jak wpisać identyfikatory po wgraniu

Plik JSON w jednej z dwóch postaci. Prosta:

```json
{"arkusz": 1234567890,
 "arkusze_muzyki": {"muzyka_arkusz_b": 1234567891},
 "muzyka": {"muzyka_06_bagno_petla": 1234567892, "muzyka_07_dzungla_petla": 1234567893}}
```

albo rejestr narzędzia wgrywania (`assets/audio/wgrane.json` z `tools/roblox_upload_audio.py`: lista `wgrane` z polami
`plik` i `assetId`). Plik `…/sfx_arkusz_*.ogg` to arkusz efektów, `…/muzyka_arkusz_b.ogg` to arkusz muzyki,
`…/muzyka_XX_…_petla.ogg` to utwór wgrany osobno (pozycje spoza `identyfikatory.json` są pomijane). Potem, w Studio
w trybie Edit:

```
python -B swiat/dzwiek_gra/zbuduj.py --identyfikatory assets/audio/wgrane.json
```

Polecenie sprawdza nazwy i liczby (nieznana nazwa albo liczba ≤ 0 = błąd, nic nie zapisuje), zapisuje
`identyfikatory.json`, odświeża `zrodla/KatalogDzwiekow.luau` i wysyła moduł do `Workspace/DzwiekGra` (jak
`--skrypty`). Z `--sucho` tylko zapis w repozytorium. Wpisanych już identyfikatorów nie rusza.

**Arkusz muzyki:** jeden identyfikator pliku obsługuje wszystkie utwory z arkusza — po wpisaniu
`arkusze_muzyki.muzyka_arkusz_b` zaczynają grać naraz: muzyka walki, Strażnika i treningu oraz drugie utwory Bagna
i Dżungli. Odcinki (początek i koniec każdego utworu) katalog bierze z mapy `assets/audio/arkusz/muzyka_arkusz_b.json`;
budowniczy odmawia, gdy plik arkusza ma inny skrót niż mapa. Jeśli arkusz zostanie zbudowany od nowa (np. bez
odrzuconego utworu), trzeba wgrać nowy plik i wpisać jego identyfikator — stary identyfikator wskazuje stary plik
z innymi odcinkami.

## Jak działa

**Efekty w walce** (`OdtwarzaczWalki2`, „Własne dźwięki” w nagłówku pliku) — bez zmian od 17.11:
- `przygotujScene` szuka `Workspace/DzwiekGra/Moduly/KatalogDzwiekow`; gdy arkusz ma identyfikator, robi pulę 6
  dźwięków z tym plikiem. Każdy odcinek: `PlaybackRegionsEnabled = true`, `PlaybackRegion = (początek + pominięty
  wstęp, koniec)`, `TimePosition = początek`, zapasowe zatrzymanie po długości odcinka.
- **Uderzenia** (cios, krytyk, blok, unik, kula ognia, lodowy pocisk, kwaśny plusk galarety): szczyt efektu wypada na
  klatkę trafienia; gdy zdarzenie zaczyna się za późno, odcinek gra od razu z pominiętym wstępem.
- **Reszta zdarzeń**: rzut umiejętności, tarcza magiczna, tiki trucizny i podpalenia, ogłuszenie, zwycięstwo
  i porażka, „awans” przy wskrzeszeniu, monety, klik przycisków, zarodniki, odgłosy potworów. Zdarzenie bez wpisu
  w katalogu (strzała, krwawienie, upadek, łomot) gra dźwięk wbudowany.
- Wynik odtworzenia (atrybuty kontenera walki u klienta): `OstatniZestawDzwiekow`, `OstatnieOdcinkiArkusza`,
  `OstatnieRegionyArkusza`.

**Muzyka** (`MuzykaStref`) — co 0,5 s skrypt wybiera źródło muzyki: kontekst, a gdy żaden nie gra — strefę.

1. **Strefa** z położenia postaci: prostokąty gruntu map policzone przy budowie; strefa liczy się tylko, gdy jej mapa
   stoi w miejscu. Utwory strefy grają na zmianę, każdy raz do końca, potem przenikanie `przejscie_s` (2,5 s)
   w następny; jedyny utwór przenika w siebie.
2. **Utwór jako odcinek arkusza**: wpis katalogu z polami `arkusz`, `poczatek`, `koniec` gra przez
   `PlaybackRegionsEnabled` + `PlaybackRegion` (sekundy w pliku arkusza, zwężone o 0,05 s z każdej strony); koniec
   utworu to koniec odcinka, nie pliku. Gdyby odtwarzanie wyszło poza odcinek, skrypt wraca na jego początek (licznik
   `korekty` w stanie haczyka).
3. **Utwory zastępcze** (Bagno, Dżungla): gdy żaden własny utwór strefy nie ma identyfikatora, grają zastępcze —
   dwa utwory lasu z głośnością 0,7, czyli dokładnie to, co grało do 18.11. Gdy choć jeden własny ma identyfikator,
   grają tylko własne (te z identyfikatorem).
4. **Konteksty** — po czym skrypt je poznaje (wszystko tylko odczytem, u klienta):

   | Kontekst | Warunek | Skąd wiadomo |
   |---|---|---|
   | `walka` | trwa walka i odtwarzanie już ruszyło | `OdtwarzaczWalki2.czyTrwa()` oraz atrybut `OstatniStan` = `odtwarzanie` albo `wynik` na kontenerze, z którego ruszyła walka (`Workspace/TestWalki2` albo kontener potworów krainy) |
   | `walka_straznik` | jak wyżej, a przeciwnik to Strażnik krainy | atrybut `OstatniWybor` = `klasa/przeciwnik/poziom` na tym samym kontenerze. Tablica prototypu podaje gatunek — porównanie z listą `gatunki` (`straznik_lasu`, `straznik_topieli`, `waz_stu_lian`). Walka w krainie podaje identyfikator potwora — jego opis leży w `<kontener>/Stan/<id>` (atrybut `Straznik = true` albo `Gatunek` z listy) |
   | `trening` | gracz jest na stanowisku mini-gry | atrybut gracza `TreningGra` (serwer mini-gier ustawia go przy wejściu na stanowisko i zdejmuje przy wyjściu) |

   Kontekst gra tylko wtedy, gdy jego utwór ma identyfikator **i plik się wczytał** (skrypt wczytuje pliki kontekstów
   na zapas od startu). Inaczej zostaje muzyka strefy, w walce przyciszona (`przyciszenie_walki`, dziś 0,6) — tak jak
   przed 18.11. Strażnik bez własnego utworu dostaje utwór zwykłej walki. Kontekst walki ustala się raz, gdy
   odtwarzanie ruszy, i trzyma do końca walki (serwer usuwa pokonanego potwora, zanim gracz zamknie okno wyniku).
   Muzyka walki nie jest przyciszana w czasie walki; cichnie przy oknie wyniku (żeby było słychać fanfarę).
5. **Powrót do strefy**: utwór strefy, który ustąpił kontekstowi, zostaje wstrzymany i po kontekście gra dalej od
   tego samego miejsca. Gdy w czasie kontekstu jego tor został zajęty (utwór kontekstu zdążył przejść w następny —
   skrypt ma dwa tory), strefa zaczyna następny utwór od początku.

Utwór z identyfikatorem 0 jest pomijany; źródło bez utworów = cisza bez komunikatów w konsoli.

**Haczyk testowy** `Sygnaly/SterowanieMuzyki` (tylko Play): `Invoke("stan")`, `("wymus", strefa | nil)`,
`("wymus_kontekst", kontekst | "brak" | nil)`, `("probny", strefa | kontekst, id | nil, { poczatek, koniec }?)` —
próbny identyfikator (np. `rbxasset://sounds/action_falling.mp3`, wbudowany w klienta) dostaje pierwszy utwór źródła
i dopóki próba trwa, źródło gra tylko jego. Efekty: lokalne atrybuty `TestArkuszId` i `TestArkuszSkala` jak dotąd.

## Wyniki

**18.11.2026 — bez Studio** (nowy kod):
- `python -B swiat/dzwiek_gra/testy/test_dzwieku.py` — 24/24;
- `python -B swiat/dzwiek_gra/zbuduj.py --sucho` — kod 0 (katalog: 22 efekty, 22 zdarzenia, arkusz muzyki id 0
  z pięcioma utworami, trzy konteksty po 0/1 utworów z identyfikatorem, Bagno i Dżungla na utworach zastępczych);
- kontrola Luau pakietu (`swiat/las_potwory/sprawdz_luau.py`, wywoływana przez budowniczego) — 2 pliki, bez błędów;
- polecenie `--identyfikatory assets/audio/wgrane.json --sucho` sprawdzone na kopii plików (repozytorium bez zmian):
  wpisuje identyfikatory Bagna i Dżungli, a obie strefy przechodzą na utwory własne.

**18.11.2026 — w Studio: NIC z nowego kodu nie było uruchomione.** Punkty D7–D10 próby (utwory zastępcze, odcinek
pliku, muzyka walki i Strażnika, muzyka mini-gry ze wznowieniem strefy) są napisane, ale czekają na pierwszy
przebieg; mogą wymagać poprawek czasów oczekiwania.

**17.11.2026 — w Studio** (wersja bez kontekstów i arkusza muzyki): kontener zbudowany, `testy/proba_play.py` 6/6:
- D1 `PlaybackRegionsEnabled` i `PlaybackRegion` istnieją i działają (zapis i odczyt 1,5–2,5);
- D2 katalog z identyfikatorem 0 → walka na dźwiękach wbudowanych (21 zagranych, 0 odcinków);
- D3 „arkusz” próbny (`rbxasset://sounds/action_falling.mp3`, czasy × 0,19): 14 odcinków, region każdego = odcinek
  z katalogu × skala, pozycja odtwarzania zawsze w regionie (30 próbek), szczyt 11 uderzeń względem klatki trafienia:
  od −0,028 do +0,004 s;
- D4 po zabraniu identyfikatora próbnego — znów dźwięki wbudowane;
- D5 muzyka stref: strefa z położenia, z identyfikatorem próbnym gra utwór bazaru, w walce przyciszenie, po zabraniu
  cisza, 0 błędów;
- D6 konsola bez błędów i ostrzeżeń `[DzwiekGra]` / `[TestWalki2]`.

**Niesprawdzone:**
- wszystko, co nowe, w Studio (lista wyżej), w tym: czy `Sound.PlaybackRegion` zaczyna odtwarzanie od początku
  odcinka także wtedy, gdy plik dopiero się wczytuje (skrypt ma na to korektę pozycji), `Pause` / `Resume` utworu
  strefy, wykrywanie walki ze Strażnikiem w krainie (w próbie jest tylko Strażnik z tablicy prototypu), prawdziwe
  wejście na stanowisko mini-gry (próba ustawia atrybut gracza sama);
- prawdziwe pliki: głośność muzyki walki względem efektów i muzyki stref, przesunięcie czasów arkusza muzyki po
  przekodowaniu w Roblox (margines 0,05 s i 1,5 s ciszy między utworami są przyjęte z zapasem, nie zmierzone), czas
  wczytywania arkusza (8,37 MB) przed pierwszą walką;
- telefon; przejście przez chmury (efekt `chmury` jest w katalogu, ale pakiet `swiat/teleport_chmury` go nie gra).

## Przyjęte, do zmiany (ustawienia agenta, nikt ich nie słyszał)

- mapowanie zdarzeń na efekty i głośności (`ustawienia.json`); arkusz efektów × 0,6;
- głośność muzyki: strefy 0,8, utwory zastępcze 0,7, konteksty 0,7; przenikanie 2,5 s; przyciszenie 0,6;
- muzyka walki zaczyna się, gdy ruszy odtwarzanie walki (nie przy prośbie do serwera), gra do zamknięcia okna
  wyniku i przy oknie wyniku jest przyciszona;
- muzyka mini-gry gra przez cały pobyt na stanowisku (także między rundami i przy podsumowaniu), nie tylko
  w czasie rundy — klient mini-gier nie wystawia stanu rundy (opis haczyka niżej);
- strefa, która ma choć jeden własny utwór z identyfikatorem, nie miesza go z zastępczymi (jeden utwór gra w kółko
  z przenikaniem, dopóki nie dojdzie drugi);
- po kontekście strefa wznawia przerwany utwór zamiast zaczynać następny;
- „awans” gra przy wskrzeszeniu; odgłos potwora tylko przy jego umiejętności i w radości po wygranej; strzała,
  krwawienie, upadek i łomot zostają na dźwiękach wbudowanych;
- poza strefami z katalogu — cisza.

**Haczyk, którego dziś nie ma (nie jest potrzebny do działania):** gdyby muzyka mini-gry miała grać tylko w czasie
rundy, klient mini-gier (`swiat/trening_proba/zrodla/KlientTreningu.client.luau`) musiałby wystawić stan ekranu, np.
lokalny atrybut kontenera `KlientTreninguEkran` = `brak` / `stanowisko` / `runda` / `podsumowanie`, ustawiany tam,
gdzie zmienia się `stan.ekran`. Dziś ten stan widać tylko przez haczyk testowy `SterowanieKlienta:Invoke("stan")`,
którego skrypt muzyki nie woła.

## Bezpieczeństwo i zasady

Każdy skrypt i moduł zaczyna się od strażnika `RunService:IsStudio()`. Budowniczy rusza tylko `Workspace/DzwiekGra`
z atrybutem `Wygenerowane` (cudzy obiekt o tej nazwie = przerwanie), ustawia punkty historii przed i po, działa tylko
w trybie Edit, niczego nie zapisuje w miejscu, nie publikuje i nie wgrywa. Skrypt muzyki ustawia atrybuty wyłącznie
na własnym kontenerze; cudze kontenery, potwory i gracza tylko czyta. Przed publikacją miejsca:
`python -B swiat/dzwiek_gra/zbuduj.py --usun`.
