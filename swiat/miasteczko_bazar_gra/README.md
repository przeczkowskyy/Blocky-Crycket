# Miasteczko-bazar w grze — podpowiedzi E, uchwyt okien 2D, portal krain, przejścia

*Status: **propozycja** (17.11.2026). Kod przygotowany i sprawdzony bez Studio, **w Studio jeszcze nie uruchomiony**.
Wymagania: D-084 (do sklepu się wchodzi, E na sprzedawcy otwiera okno 2D Pawła), D-085 (portal krain, przejście na
działkę, zagroda petów, tablica z rankingiem, mini-gry z jednego miejsca), D-075 (miasteczko to pierwszy blok pasa,
teleport przez chmury), D-042 (lochy zamknięte, osobno dla gracza), D-093 (okna 2D i ich skrypty robi Paweł).
Mapa: `swiat/miasteczko_bazar/` (kontener `Workspace/MiasteczkoBazar`, buduje go inny etap) — ten pakiet jej nie zmienia.*

> **W skrócie.** Jeden kontener `Workspace/MiasteczkoBazarGra` (atrybut `Wygenerowane = true`) obok mapy bazaru.
> W nim **13 niewidzialnych punktów E** we własnych częściach (11 w bazarze w miejscach ze `znaczniki.json`, „Stare
> miasteczko (E)” przy starcie bazaru i „Nowe miasteczko (E)” w starym miasteczku przy dzisiejszym miejscu startu),
> **tablica z rankingiem** na powierzchni tablicy i dwa skrypty. E przy sprzedawcy wysyła **jedno zdarzenie dla okien
> Pawła** (`ReplicatedStorage.OknoMiejsca` z identyfikatorem miejsca) i — tam, gdzie pasuje przycisk HUD — sygnał HUD
> (`Shop`, `Pets`, `Quests`); dopóki okna nie ma, nad sprzedawcą pojawia się krótki dymek („Zbrojmistrz: sklep
> w budowie”). Portal krain otwiera **przejście przez chmury**, Brama Leśna przenosi do **Lasu** uchwytem pasa,
> działka i lochy mówią „wkrótce” / „Zamknięte”. Przenosi wyłącznie serwer, z blokadą czasu 3 s i wczytaniem okolicy.

## Pliki

| Plik | Co to jest |
|---|---|
| `miejsca.json` | **jedyne źródło ustawień**: akcje, teksty, przyciski HUD, czasy, zasięgi, przejścia — bez położeń |
| `dane.py` | generator `zrodla/DaneBazaru.luau`: położenia ze `swiat/miasteczko_bazar/znaczniki.json`, start starego miasteczka z `swiat/krzywe_miasteczko/uklad.json`, przypadki wzorcowe logiki; `--sprawdz`, `--wyjscie DIR` |
| `logika_bazaru.py` | lustro `zrodla/LogikaBazaru.luau` w Pythonie (decyzja po E, blokada czasu, odmowy, lochy, ranking, kandydaci w starym miasteczku, dymek) i 70 przypadków wzorcowych |
| `zrodla/LogikaBazaru.luau` | czysta logika (ModuleScript) — ta sama co lustro; sprawdza się przy starcie serwera |
| `zrodla/SerwerBazaru.server.luau` | serwer: podpowiedzi E, decyzje, przeniesienia, uchwyt Lasu, lochy, tablica, uchwyty `PrzeniesDoBazaru` i `SterowanieSerwera` |
| `zrodla/KlientBazaru.client.luau` | klient: `OknoMiejsca`, sygnał HUD, dymki, portal → chmury, kłódka lochów u siebie, haczyk `SterowanieKlienta` |
| `zrodla/DaneBazaru.luau` | **wygenerowany** — nie edytować ręcznie |
| `sprawdz_luau_bazaru.py` | kontrola statyczna Luau (reguły `swiat/las_potwory/sprawdz_luau.py`, parser `tools/walka/luau_mini.py`, bez liczb położeń w kodzie, bez zmian cudzych instancji) |
| `czasy_biegu.py` | plan czasów biegu ze startu do każdego E (siatka chodzenia mapy, tylko odczyt) i punkty przy ścianach — dla testów i próby |
| `zbuduj.py` | budowa w Studio: `--sucho`, `--skrypty`, `--usun`, `--studio` |
| `testy/test_bazaru.py` | 38 testów offline (opis w nagłówku pliku) |
| `testy/proba_play.py` | gotowa próba w Studio (Play) z listą kontrolną B01–B15 i 8 zrzutami — **dla następnego etapu, nieuruchomiona** |

## Co jest w kontenerze `Workspace/MiasteczkoBazarGra`

| Ścieżka | Klasa | Co robi |
|---|---|---|
| `Moduly/DaneBazaru`, `Moduly/LogikaBazaru` | ModuleScript | dane (wygenerowane) i logika |
| `SerwerBazaru` (RunContext Server), `KlientBazaru` (RunContext Client) | Script | poza Studio serwer usuwa cały kontener (jak LasTeleport, LasPasGra, TeleportChmury) |
| `Zdalne/ZdarzeniaBazaru` | RemoteEvent | serwer → klient: `"okno", id` · `"dymek", id, tekst` · `"chmury", id` · `"przeniesiono", id, cel`; klient nic nie wysyła |
| `Sygnaly/PrzeniesDoBazaru` | BindableFunction | uchwyt serwera: start bazaru (dla przejścia przez chmury i innych skryptów) |
| `Sygnaly/SterowanieSerwera`, `Sygnaly/SterowanieKlienta` | BindableFunction | haczyki testowe (i odblokowanie lochów) |
| `Punkty/E <id>` | Part 0,6³, niewidzialna, bez kolizji, z `ProximityPrompt „Podpowiedz”` | `Enabled = false` w Edit — włącza serwer w Play; atrybut `Miejsce = id` |
| `Tablica/Ekran` | Part z `SurfaceGui „Ranking”` | 6,4 × 4,8 st, 0,06 st przed powierzchnią `tablica_ranking`, przodem po normalnej |

Atrybuty kontenera z budowy: `Wygenerowane`, `Zrodlo`, `Zbudowano`, `Skrot`, **`PunktStartuBazaru` / `PatrzStartuBazaru`**
(Vector3, środek HumanoidRootPart na starcie — dla przejścia przez chmury), `PunktStaregoMiasteczka`,
`StartStaregoMiasteczka`, `ZrodloStartuStarego`, `PunktPowrotuStare` / `PatrzPowrotuStare`. Atrybuty ustawiane ręcznie
w Edit i przenoszone przy odbudowie: `DymkiWylaczone`, `BezDymku` (np. `"zbrojownia,karczma"`),
`RecznyPunktStaregoMiasteczka` (Vector3 — własne miejsce „Nowe miasteczko (E)”). W Play serwer ustawia
`SerwerBazaruGotowy`, `ZgodnoscLogikiBazaru` („OK 70/70”), `Podpowiedzi` (13), `Las` / `Chmury` (jest / brak),
`LicznikE`, `OstatnieE`, `LicznikPrzejsc`, `OstatniePrzejscie`, `TablicaWierszy`; klient — `KlientBazaruGotowy`.

## Miejsca (13)

| id | Znacznik (`znaczniki.json`) | E (obiekt / akcja) | Co robi dziś | Sygnał HUD |
|---|---|---|---|---|
| `karczma` | `sklepy/karczma` | Karczmarz / Zadania | `OknoMiejsca("karczma")` + HUD, dymek „Karczmarz: zadania wkrótce!” | `Quests` |
| `mistrz_gier` | `sklepy/mistrz_gier` | Mistrz gier / Zagraj | `OknoMiejsca`, dymek „Mistrz gier: plansza w budowie” | — |
| `sklep_magiczny` | `sklepy/sklep_magiczny` | Mag / Sklep | `OknoMiejsca` + HUD, dymek „Mag: sklep w budowie” | `Shop` |
| `zbrojownia` | `sklepy/zbrojownia` | Zbrojmistrz / Sklep | `OknoMiejsca` + HUD, dymek „Zbrojmistrz: sklep w budowie” | `Shop` |
| `training_center` | `training_center` | Trener / Mini-gry | `OknoMiejsca`, dymek „Trener: mini-gry w budowie” | — |
| `zagroda_petow` | `zagroda/punkt_e` | Opiekunka / Zagroda petów | `OknoMiejsca` + HUD, dymek „Opiekunka: zagroda w budowie” | `Pets` |
| `tablica` | `tablica/tablica` | Tablica ogłoszeń / Ranking | `OknoMiejsca`, dymek „Pełny ranking — wkrótce” | — |
| `dzialka` | `dzialka` (Brama Twierdzy) | Brama Twierdzy / Na działkę | `OknoMiejsca`, dymek „Działka — wkrótce” | — |
| `lochy` | `lochy/punkt_e` | Wrota lochów / Otwórz | zamknięte: dymek „Zamknięte”; po odblokowaniu: `OknoMiejsca("lochy")`, dymek „Hala portali — wkrótce” | — |
| `portal_krain` | `portal_krain/portal_krain` | Portal krain / Podróżuj | `Workspace/TeleportChmury/Otworz:Fire()`; bez niego dymek | (Teleport) |
| `brama_lesna` | `las/brama_lesna` | Brama Leśna / Do Lasu | serwer → `LasPasGra/Sygnaly/PrzeniesDoLasu`; bez niego dymek „Las jeszcze niegotowy…” | — |
| `stare_miasteczko` | `start` + (−12; 0; 0) | Stare miasteczko / Przejdź | serwer → stare miasteczko (przy „Nowe miasteczko (E)”), tabliczka „STARE MIASTECZKO (E)” | — |
| `nowe_miasteczko` | wybór w Studio | Nowe miasteczko / Przejdź | serwer → start bazaru, tabliczka „NOWE MIASTECZKO (E)” | — |

Pominięte z powodem (`miejsca.json` → `pominiete`): studnia-pomnik (punkt orientacyjny), miejsca na pety (dla okna
zagrody), środek wiru portalu (portal działa przez E), kłódka lochów (chowa ją klient), brzeg Lasu (Brama Leśna ma E).

**Portal krain: wybrano E**, nie wejście w wir — spójnie ze sklepami i bez przypadkowych przejść (wybór 5 w
`swiat/miasteczko_bazar/PROJEKT.md`); znacznik `portal_krain_wir` czeka, gdyby ludzie wybrali dotyk (wybór 1 niżej).

## Jak zbudować i usunąć

```
python -B swiat/miasteczko_bazar_gra/dane.py                 # po każdej zmianie miejsca.json albo znaczników mapy
python -B swiat/miasteczko_bazar_gra/testy/test_bazaru.py    # 38 testów, ok. 3 s
python -B swiat/miasteczko_bazar_gra/zbuduj.py --sucho       # bez Studio: dane, Luau, strażniki, plan budowy
python -B swiat/miasteczko_bazar_gra/zbuduj.py               # Studio w trybie Edit: buduje / odbudowuje kontener
python -B swiat/miasteczko_bazar_gra/zbuduj.py --skrypty     # tylko moduły i skrypty (części zostają)
python -B swiat/miasteczko_bazar_gra/zbuduj.py --usun        # usuwa Workspace/MiasteczkoBazarGra (mapa zostaje)
```

Przy kilku oknach Studio dopisz `--studio <studio_id>`. Każdy wysyłany kod sprawdza `game.PlaceId == 129485428021967`
i tryb Edit (w Play: STOP), budowa rusza tylko kontener z `Wygenerowane` (obiekt o tej nazwie bez atrybutu → STOP),
stawia punkty historii przed i po (Ctrl+Z cofa całość), niczego nie publikuje ani nie zapisuje, Lighting nietknięty.

## Kolejność wdrożenia w Studio (następny etap)

1. `git pull`, potem offline: `python -B swiat/miasteczko_bazar_gra/testy/test_bazaru.py` i
   `python -B swiat/miasteczko_bazar_gra/zbuduj.py --sucho` — oba kod 0. Zgłoś pracę:
   `python panel/narzedzia/praca.py start --id bazar-gra --tytul "Bazar w grze: E, okna, przejścia" --koniec +45m --obszar studio:MiasteczkoBazarGra --obszar swiat/miasteczko_bazar_gra --stop-przy-kolizji`.
2. **Mapa bazaru** `Workspace/MiasteczkoBazar` musi stać (`swiat/miasteczko_bazar/README.md`, `tools/studio_buduj.py
   swiat/miasteczko_bazar/czesci.json`). Bez niej punkty E wiszą w powietrzu, a dymki nie mają nad kim stanąć.
3. Opcjonalnie (inaczej czytelne odmowy): `Workspace/TeleportChmury` (portal), `Workspace/LasPas` + `Workspace/LasPasGra`
   (Brama Leśna), `Workspace/LasTeleport` (portal przy dzisiejszym starcie — nasz punkt w starym miasteczku go omija).
4. `python -B swiat/miasteczko_bazar_gra/zbuduj.py` (Edit). Wypisze „w miejscu (tylko odczyt): …” (mapa, brakujące
   części mapy, PortalStart, TeleportChmury, LasPasGra, wszystkie SpawnLocation), „części: OK (punktów E w bazarze: 12,
   tablica 6.4 × 4.8)”, „stare miasteczko: OK Nowe miasteczko (E): (x; y; z) — kandydat n z m | start … z <SpawnLocation>”
   i na końcu „podpowiedzi E: 13” bez „UWAGA”.
5. Obejrzyj w Edit punkt „NOWE MIASTECZKO (E)” przy starym starcie (zrzut). Gdy stoi źle — atrybut kontenera
   `RecznyPunktStaregoMiasteczka` (Vector3 na gruncie) i ponowna budowa.
6. Próba w Play: `python -B swiat/miasteczko_bazar_gra/testy/proba_play.py <folder poza repo>` — lista B01–B15
   w `<folder>/lista.txt` i `wyniki.json`, 8 zrzutów. Ręcznie: telefon (emulator) i dwóch graczy.
7. Raport z zrzutami na panel (skill `panel`), wpisy w sejfie (`B&C/Technika/Klocki — Blender i Roblox.md`,
   `Zadania.md`, `Dziennik zmian.md` — w tym etapie zakres zapisu był ograniczony do tego folderu) i `praca.py koniec`.

## Jak Paweł podpina okno — jedna linijka

W swoim skrypcie klienta (ten sam wzór `bindable()`, który już jest w `EquipmentPanelClient`):

```lua
bindable("OknoMiejsca").Event:Connect(function(id) if id == "zbrojownia" then open() end end)
```

- `id`: `karczma`, `mistrz_gier`, `sklep_magiczny`, `zbrojownia`, `training_center`, `zagroda_petow`, `tablica`,
  `dzialka`, `lochy`; drugi argument: `{ nazwa, postac, akcja }` (np. `"Zbrojmistrz"`).
- Zdarzenie żyje w `ReplicatedStorage` (BindableEvent tylko u klienta, tworzy je pierwszy, kto go potrzebuje), więc
  linijka działa także w opublikowanej grze, gdzie tego pakietu nie ma (zdarzenie po prostu nie przyjdzie).
- **Dymek „w budowie” znika sam**, gdy po E jakiś ekran się otworzy (klient sprawdza po 0,35 s, czy włączył się
  ScreenGui albo pokazał jego główny element). Można też wprost: `bindable("OknoMiejsca"):SetAttribute("zbrojownia", true)`,
  albo w Edit na kontenerze `DymkiWylaczone = true` (wszystkie) / `BezDymku = "zbrojownia"`.
- **Istniejący sygnał HUD:** karczma wysyła też `HUDButtonPressed("Quests")`, sklepy `"Shop"`, zagroda `"Pets"` — okno,
  które Paweł podepnie pod przycisk HUD, otworzy się przy E bez żadnej zmiany. **Nie podpinaj tego samego okna drugi
  raz pod `OknoMiejsca` dla tego samego id** (okno przełączane jak ekwipunek otworzyłoby się i zamknęło) — wtedy usuń
  `"hud"` z miejsca w `miejsca.json` i przebuduj.
- Dziś **żadne okno Pawła nie otwiera się od razu**: w `src/` są tylko ekwipunek (przycisk `Equipment`), drzewko
  (z ekwipunku) i wybór klasy; okien Shop, Pets, Quests, Guilds jeszcze nie ma (`B&C/UI/HUD.md`: „Okien … jeszcze nie
  ma”). Od razu działa tylko portal → przejście przez chmury (pakiet `swiat/teleport_chmury`, nie Paweła).

## Przejście przez chmury → lądowanie w nowym miasteczku (zmiana na następny etap)

`swiat/teleport_chmury/**` nie był zmieniany. Jedna linijka w `swiat/teleport_chmury/krainy.json`, kraina
`"miasteczko"`, jako **pierwszy** wpis listy `"przybycie"`:

```json
{"atrybut": ["MiasteczkoBazarGra", "PunktStartuBazaru", "PatrzStartuBazaru"]},
```

Działa z dzisiejszym kodem `SerwerTeleportu` bez zmian (wpis „atrybut” czyta dwa atrybuty Vector3 cudzego kontenera;
gdy kontenera nie ma, bierze kolejny wpis — stare miasteczko). Potem `python -B swiat/teleport_chmury/zbuduj.py
--skrypty`. Dodatkowo (nie jest potrzebne do lądowania): do `"obszary_xz"` miasteczka dopisać `[882, 1066, -790, -610]`
(granice bazaru z `znaczniki.json`), żeby makieta wiedziała, że gracz stoi w miasteczku. Gdy do przejścia przez chmury
wejdą uchwyty pakietów (w kopii roboczej innego agenta jest wpis `{"gdy_jest": "LasPasGra", "uchwyt": "PrzeniesDoLasu", …}`),
równoważny wpis dla bazaru to `{"gdy_jest": "MiasteczkoBazarGra", "uchwyt": "PrzeniesDoBazaru", "punkt": "start"}` —
`Sygnaly/PrzeniesDoBazaru` ma ten sam kształt co `PrzeniesDoLasu`:

```lua
local f = workspace.MiasteczkoBazarGra.Sygnaly.PrzeniesDoBazaru   -- tylko po stronie serwera
local w = f:Invoke(gracz, { punkt = "start" })
-- w = { ok = true, punkt = Vector3, patrz = Vector3 } | { ok = false, powod = "zly_gracz" | "trwa" | "brak_postaci" | "nieznany_punkt" | "blad" }
```

Kamień Powrotu w Lesie (`swiat/las_pas_gra`) prowadzi dalej do starego miasteczka (`LasTeleport.PunktMiasteczka`); stamtąd
„Nowe miasteczko (E)”. Przestawienie go na bazar to osobna zmiana w tamtym pakiecie (`D.miasteczko` w jego danych).

## Brama Leśna, działka, lochy, tablica, przejścia

- **Brama Leśna:** E → serwer woła `LasPasGra/Sygnaly/PrzeniesDoLasu` z `{ punkt = "las", przelotPo = 0 }` — postać
  przenosi serwer pasa (wczytanie okolicy, własny odstęp 2 s, przelot przy pierwszym wejściu). Nasza blokada: w trakcie
  przejścia „Już cię przenoszę…”, po udanym 3 s „Chwila… jeszcze n s”. Bez uchwytu: „Las jeszcze niegotowy (nie ma pasa
  Lasu w miejscu)”; każdy powód odmowy uchwytu (`brak_mapy`, `za_szybko`, `przelot_trwa`, `brak_postaci`,
  `nieznany_punkt`, `zly_gracz`) ma czytelny tekst.
- **Działka:** dymek „Działka — wkrótce” i `OknoMiejsca("dzialka")` na przyszłość (Twierdza, D-049).
- **Lochy (D-042):** stan osobno dla gracza w pamięci serwera (bez zapisu). Odblokowanie:
  `workspace.MiasteczkoBazarGra.Sygnaly.SterowanieSerwera:Invoke("lochy", true, gracz)` albo liczba w
  `miejsca.json` → `lochy.wymagany_poziom` (serwer otwiera po atrybucie `Level`). Serwer ustawia graczowi
  `BazarLochyOtwarte`, a klient chowa **u siebie** kłódkę `MiasteczkoBazar/BramaLochow/Blokada`
  (`LocalTransparencyModifier`, nic nie idzie na serwer). Cutscenka odblokowania — osobne zadanie.
- **Tablica:** gra **ma już dane** — atrybuty gracza `Level`, `XP` i statystyki (`Strength`, `Constitution`,
  `Intelligence`, `Dexterity`, `Luck`, `Armor`) ustawia `src/server/PlayerStatsDefaults.server.luau`. Ranking serwera:
  poziom ↓, XP ↓, „moc” (suma statystyk) ↓, nazwa ↑, do 8 wierszy, odświeżany co 2 s po zmianie. **Uwaga: to prawdziwy
  odczyt, ale wartości są tymczasowe** — `PlayerStatsDefaults` to PLACEHOLDER do czasu DataStore, więc dziś wszyscy
  mają poziom 1 i moc 130; stopka tablicy mówi to wprost.
- **Stare ↔ nowe miasteczko:** „Stare miasteczko (E)” stoi 12 st za plecami gracza na starcie bazaru (w pustym pasie
  środkowym uliczki, sprawdzone na siatce chodzenia), poza zasięgiem 8 st ze startu. „Nowe miasteczko (E)” wybiera
  budowa: SpawnLocation spoza bazaru najbliższy startowi z `swiat/krzywe_miasteczko/uklad.json` (bez niego ten punkt),
  pierścienie 12–26 st, najpierw ±45° od kierunku patrzenia na starcie, co najmniej 12 st od `LasTeleport/PortalStart`
  i 6 st od drogi start → portal, na wolnym miejscu (skrzynka 4 × 6 × 4 bez części z kolizją) i gruncie na wysokości
  startu. Powrót ląduje 9 st od punktu w stronę startu, twarzą do startu.

## Haczyki testowe (Play)

- serwer: `workspace.MiasteczkoBazarGra.Sygnaly.SterowanieSerwera:Invoke("stan" | "e", id, gracz? | "przenies",
  "bazar" | "stare", gracz? | "zeruj", gracz? | "lochy", true | false, gracz? | "tablica" | "zgodnosc")`;
- klient: `workspace.MiasteczkoBazarGra.Sygnaly.SterowanieKlienta:Invoke("stan" | "okno", id | "dymek", id, tekst |
  "chmury", id)` — „stan” zwraca historię ostatnich E (id, sygnał HUD, co się otworzyło, czy był dymek).

## Co sprawdzone bez Studio (17.11.2026)

Wszystko kod 0: `dane.py --sprawdz` (aktualny, 13 miejsc, 70 przypadków), `sprawdz_luau_bazaru.py` (4 pliki, z parserem
luau_mini), `swiat/las_potwory/sprawdz_luau.py` na tych samych plikach (4 pliki OK), `testy/test_bazaru.py` (**38/38 OK,
0 pominiętych**, ok. 2,3 s), `zbuduj.py --sucho`.

- **Dane (1a–1d):** generator deterministyczny (dwa zapisy bajt w bajt), plik w `zrodla/` aktualny, bez BOM, dat
  i ścieżek; zły znacznik, powtórzone id, nieznany przycisk HUD, zła ścieżka kłódki → błąd; przesunięcie starego
  miasteczka (0; 0; −700) = `--przesun` z jego README; przyciski HUD = `src/gui/HUD.model.json`.
- **Znaczniki (2a–2h):** każdy z 12 punktów z podpowiedzią ma E (11) albo powód (studnia); każdy znacznik rozliczony;
  położenia 1:1; 13 unikalnych id, wszystkie 9 okien z zadania; ze stoiska własna podpowiedź 0,3–7,7 st (zasięg 10),
  najbliższa cudza ≥ 11,8 st; „Stare miasteczko (E)” wolne na siatce chodzenia, 12 st od startu (zasięg 8); tablica na
  powierzchni ze znacznika; zero liczb ≥ 100 w kodzie (położenia tylko w danych).
- **Czasy biegu planu** (siatka mapy, 16 st/s): portal 1,56 s, Brama Twierdzy 0,78, tablica 1,34, mistrz gier 2,66,
  zagroda 2,69, sklep magiczny 2,96, karczma 2,98, lochy 3,20, Brama Leśna 3,98, Training Center 4,32, zbrojownia
  4,42, „Stare miasteczko” 0,75 — sklepy ≤ 5 s, portal ≤ 6 s (jak w PROJEKT.md mapy).
- **Logika (3a–3i):** akcje 13 miejsc; granica zasięgu (zasięg + 4) i spam (0,4 s, odrzucone E nie zabiera odstępu);
  lochy (flaga, próg poziomu 7/8/50/brak/napis/bool); portal bez chmur, Brama Leśna bez Lasu, przejście bez celu;
  każdy powód odmowy `PrzeniesDoLasu` odczytany ze źródła pasa ma tekst; „Chwila… jeszcze 3 s” (zaokrąglenie w górę,
  min. 1); **symulacja 400 przebiegów blokady czasu** — nigdy dwa przejścia naraz, między udanym końcem a kolejnym
  startem ≥ 3 s; ranking (200 losowych list: kolejność, limit, remisy); kandydaci w starym miasteczku (300 losowych
  układów: ≥ 9 od startu, ≥ 12 od portalu, ≥ 6 od drogi do portalu); dymek okna i lista `BezDymku`.
- **Luau w luau_mini (4a–4f):** 4 pliki parsują się; `LogikaBazaru.sprawdzPrzypadki` → 70/70, a zepsuty przypadek jest
  wykrywany; losowo: 400 × `decyzja` (wynik i stan), 200 × `ranking` + każdy `wiersz`, 150 × `kandydaci` i
  `odlegloscOdOdcinka`, 150 × `tekstOdmowy` i `dymekOkna` — identyczne z lustrem; `DaneBazaru` wczytane w Luau = dane
  z Pythona; próg lochów w Luau = w Pythonie; cały kod wysyłany do Studio (sprawdzenie, start, usunięcie, części,
  stare miasteczko, skrypt, koniec) parsuje się i nie ma niewstawionych `__…__`.
- **Styki (5a–5k):** nazwy instancji, wiadomości zdalne (serwer → klient 4 rodzaje, klient nic nie wysyła), atrybuty
  (każdy czytany ktoś ustawia; statystyki tablicy istnieją w `PlayerStatsDefaults`), uchwyt `LasPasGra/Sygnaly/
  PrzeniesDoLasu` i punkt „las”, `TeleportChmury/Otworz` i atrybut `Trwa`, `HUDButtonPressed`, nazwa `OknoMiejsca`
  wolna w `src/` i pakietach Studio, wpis „atrybut” z tego README czyta `SerwerTeleportu`, strażnik Studio,
  samousunięcie serwera, PlaceId 129485428021967 = `cel_studio.py`, tryb Edit, 3 + 1 punkty historii, bez Lighting,
  budowa tworzy tylko w kontenerze, bez ścieżek lokalnych; `--sucho` nie importuje `studio_mcp` ani `cel_studio`;
  `proba_play.py` się kompiluje, ma B01–B15 i 8 zrzutów, bez argumentów tylko wypisuje sposób użycia.

## Czego nie da się sprawdzić bez Studio

Całe zachowanie w grze: czy `ProximityPrompt` pokazuje się na stoisku i nie przeszkadza ladą (RequiresLineOfSight =
false), czy dymek (BillboardGui w PlayerGui) wisi nad głową sprzedawcy i jest czytelny (także na telefonie), czy
wykrywanie „okno się otworzyło” nie łapie przypadkowych ekranów, kamera we wnętrzach sklepów, prawdziwe czasy biegu,
niewidzialne ściany, przejście przez chmury i Brama Leśna z pakietami innych agentów, wybór miejsca „Nowe miasteczko (E)”
przy prawdziwym SpawnLocation, czy `LocalTransparencyModifier` chowa kłódkę tylko u jednego gracza, czytelność tablicy
(SurfaceGui 50 px/st), koszt klatki. To wszystko jest w `testy/proba_play.py` (B01–B15) albo na liście ręcznej w jego
nagłówku.

## Znane ryzyka

- **Nic nie było uruchomione w Studio.** Luau sprawdzone statycznie, sparsowane, a czysta logika wykonana
  interpreterem `tools/walka/luau_mini.py` — to plik innego agenta, jeszcze nie w git (gdy zniknie, testy Luau są
  pomijane z uwagą, reszta działa).
- **Położenie „Nowe miasteczko (E)” zależy od Studio**: prawdziwego SpawnLocation nie ma w żadnym pliku repozytorium
  (stare miasteczko ma tylko znacznik wejścia). Budowa wypisuje, skąd wzięła start; zła pozycja → atrybut ręczny.
- **Wykrywanie otwartego okna** to heurystyka (włączony ScreenGui albo pokazany jego główny element w ciągu 0,35 s).
  Okno, które otwiera się inaczej, dostanie dymek, dopóki Paweł nie ustawi atrybutu na `OknoMiejsca`.
- **Dwa sklepy na jednym przycisku `Shop`** — do decyzji (wybór 3); `OknoMiejsca` i tak niesie id sklepu.
- **Stan lochów i blokady w pamięci serwera** — restart serwera = lochy znów zamknięte (jak w pakietach Lasu).
- **Kłódka chowana lokalnie** w cudzym kontenerze mapy (tylko `LocalTransparencyModifier` u klienta, tylko po
  odblokowaniu) — tak zakłada lista prac mapy (`swiat/miasteczko_bazar/README.md`, punkt 7).
- **Mapa bazaru stoi na płycie Baseplate** (wybór 1 mapy); rzut promienia przy przenoszeniu bierze tylko części
  z kolizją w pasie 6 st nad gruntem z danych, więc nie wyląduje na dachu ani markizie.

## Wybory do decyzji

**1. Portal krain: E czy wejście w wir?**
- E przed portalem (dziś) — jak sklepy, bez przypadkowych przejść.
- Wejście w wir (znacznik `portal_krain_wir`, promień 5,6) — szybciej, ale łatwo wejść niechcący.

**2. Zbrojownia do czasu sklepu: dymek czy okno ekwipunku?**
- Dymek „sklep w budowie” i sygnał `Shop` (dziś).
- Okno ekwipunku Pawła (jedyne istniejące z bronią i pancerzem): `"hud": "Equipment"` w `miejsca.json`.

**3. Oba sklepy na jednym przycisku HUD Shop?**
- Tak (dziś): mag i zbrojmistrz wysyłają `Shop`, a `OknoMiejsca` niesie id sklepu.
- Nie: tylko `OknoMiejsca` — Paweł robi dwa okna i rozróżnia je po id.

**4. Ranking na tablicy: według czego?**
- Poziom, potem XP, potem suma statystyk (dziś, atrybuty z `PlayerStatsDefaults`).
- Inna miara „największych zdolności” z D-085 (np. punkty drzewka) — do ustalenia.

**5. Lochy: od jakiego poziomu otwarte?**
- Dziś tylko haczyk (`wymagany_poziom: null`).
- Liczba w `miejsca.json` — serwer otwiera sam po atrybucie `Level` (D-042).

**6. Gdzie gracz startuje po wejściu do gry?**
- Dziś: stary spawn i obok „Nowe miasteczko (E)”.
- SpawnLocation na starcie bazaru — zmiana cudzej instancji, decyzja człowieka (lista prac mapy, punkt 2).

**7. Przejście przez chmury ma lądować w bazarze?**
- Tak: jedna linijka w `krainy.json` (wyżej) — „Miasteczko” na makiecie prowadzi na bazar.
- Jeszcze nie: zostaje stare miasteczko, dopóki bazar nie jest kanonem.

**8. Tymczasowe przejścia stare ↔ nowe: kiedy usunąć?**
- Gdy bazar zostanie przyjęty i spawn przeniesiony.
- Zostawić jako drogę do „zwiedzania” starego miasta (wybór 8 w `swiat/miasteczko_bazar/PROJEKT.md`).
