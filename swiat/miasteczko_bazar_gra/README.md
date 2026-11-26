# Miasteczko-bazar w grze — podpowiedzi E, uchwyt okien 2D, portal krain, przejścia

> **Sprzątanie mapy 26.11.2026 (zlecenie Karola):** gracz zaczyna od razu na starcie bazaru (wspólny `Workspace/SpawnLocation` przeniesiony na znacznik `start`), więc tymczasowe przejścia **„Stare miasteczko (E)” i „Nowe miasteczko (E)” zniknęły** — pakiet ma **11 miejsc z E** zamiast 13, nie czyta już `swiat/krzywe_miasteczko/uklad.json`, nie stawia punktu w starym miasteczku (`zbuduj.py` bez kroku „stare miasteczko”), a logika nie ma akcji `przenies` ani kandydatów (uchwyt `Sygnaly/PrzeniesDoBazaru` zostaje). Opisy przejść niżej są historią. Próby: `B09` sprawdza teraz start gry w bazarze, `proba_dodatkowa.py D03` — brak starych przejść. Usuwanie z miejsca: `python -B tools/studio/sprzatanie_mapy.py` (najpierw `--sucho`); start gry na starcie bazaru: `python -B tools/studio/start_w_miasteczku.py`.

*Status: **propozycja** (17.11.2026). **Wdrożone w Studio i sprawdzone w trybie Play w nocy 16/17.11.2026** — wyniki
w „Co sprawdzone w grze” niżej, zrzuty w `klatki/`.
Wymagania: D-084 (do sklepu się wchodzi, E na sprzedawcy otwiera okno 2D Pawła), D-085 (portal krain, przejście na
działkę, zagroda petów, tablica z rankingiem, mini-gry z jednego miejsca), D-075 (miasteczko to pierwszy blok pasa,
teleport przez chmury), D-042 (lochy zamknięte, osobno dla gracza), D-093 (okna 2D i ich skrypty robi Paweł).
Mapa: `swiat/miasteczko_bazar/` (kontener `Workspace/MiasteczkoBazar`) — ten pakiet jej nie zmienia; poprawki mapy po
próbie w grze (kolizje dla kamery, nowe postacie) opisuje jej README.*

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
| `testy/proba_play.py` | próba w Studio (Play) z listą kontrolną B01–B15 i 8 zrzutami (uruchomiona 17.11.2026, wyniki niżej) |
| `testy/proba_dodatkowa.py` | uzupełnienie próby: kamera za plecami i odwrócona na 6 stoiskach (D01), dymki 11 miejsc (D02), brak starych przejść (D03; do 26.11.2026: stare ↔ nowe prawdziwym E), Kamień Powrotu z bazarem i bez — w obu przypadkach start bazaru (D04), koszt u klienta (D05), zrzuty z gry do README (Z) |
| `wyniki/` | zapisy prób w Studio (bez nazwy konta — `<gracz>`) |
| `klatki/` | zrzuty z gry (tryb Play) — tabela niżej |

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
| `training_center` | `training_center` | Trener / Train (od 26.11.2026; wcześniej „Mini-gry”) | `OknoMiejsca` → okno sześciu stanowisk AFK w `src/client/TreningAFKClient.client.luau` (zgłasza się atrybutem, więc dymku nie ma; zapasowy dymek „Trainer: training is closed right now.”) | — |
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

## Kolejność wdrożenia w Studio

Zrobione 17.11.2026 w nocy (punkty 1–6; panel i sejf — punkt 7 — nie, ten etap miał zakaz zapisu w `B&C/` i `panel/`).
Przy powtórce: tak samo, a po budowie także `testy/proba_dodatkowa.py <folder poza repo>`.

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

## Przejście przez chmury → lądowanie w nowym miasteczku (zrobione 17.11.2026)

**Wpisane i sprawdzone w grze 17.11.2026** (próba przejścia przez chmury 6/6, B07 tutaj: lądowanie 0,0 st od startu
bazaru). Jedna linijka w `swiat/teleport_chmury/krainy.json`, kraina `"miasteczko"`, jako **pierwszy** wpis listy
`"przybycie"` (plus obszar bazaru w `"obszary_xz"`):

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

**Kamień Powrotu** w lesie-pasie (`swiat/las_pas_gra`, zmienione 17.11.2026) woła ten uchwyt: gdy stoi
`Workspace/MiasteczkoBazarGra`, prowadzi na start bazaru; bez niego — do starego miasteczka (`LasTeleport.PunktMiasteczka`)
jak dotąd. Odmowa uchwytu (np. `trwa`) nie przenosi nigdzie indziej. Sprawdzone w grze prawdziwym E (D04 niżej).

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
- **Stare ↔ nowe miasteczko:** „Stare miasteczko (E)” stoi 16 st za plecami gracza na starcie bazaru (w pustym pasie
  środkowym uliczki, sprawdzone na siatce chodzenia), poza zasięgiem 8 st ze startu. Było 12 st — w grze tabliczka
  wisiała wtedy dokładnie w kamerze gracza na starcie (kamera stoi ok. 12,5 st za głową), przy lewej krawędzi ekranu,
  na HUD-zie; teraz jest za kamerą i widać ją po obróceniu się. „Nowe miasteczko (E)” wybiera
  budowa: SpawnLocation spoza bazaru najbliższy startowi z `swiat/krzywe_miasteczko/uklad.json` (bez niego ten punkt),
  pierścienie 12–26 st, najpierw ±45° od kierunku patrzenia na starcie, co najmniej 12 st od `LasTeleport/PortalStart`
  i 6 st od drogi start → portal, na wolnym miejscu (skrzynka 4 × 6 × 4 bez części z kolizją) i gruncie na wysokości
  startu. Powrót ląduje 9 st od punktu w stronę startu, twarzą do startu.
  **W Studio (17.11.2026):** jedyny `SpawnLocation` stoi w (0; 0,5; 0), czyli w `Workspace/DemoLesnaBaza` (plac ze
  spawnem, karczmą i kołem fortuny), a nie w `Workspace/KrzyweMiasteczko` (ono nie ma prawdziwego spawnu — jego
  README). Budowa wypisuje więc uwagę „start poza obszarem starego miasteczka” i stawia „Nowe miasteczko (E)” w
  (11,7; 1,0; −2,7): 12,0 st od spawnu, 22,1 st od `LasTeleport/PortalStart`, niczego nie zasłania (zrzut
  `klatki/12_przejscie_nowe_w_starym.jpg`). **26.11.2026:** od 20.11 stoi tam też brama BONK (`swiat/bonk`, atrybut
  `BonkGra.PortalPoz` (16; 1; 0), wejście w promieniu 5 st) — 5,1 st od tabliczki, więc postać przy tabliczce lądowała
  w BONK (B09). Budowa pomija teraz kandydatów bliżej niż 12 st od stref wejścia innych pakietów (`STREFY_WEJSCIA`
  w `zbuduj.py`); punkt stoi w (6,4; 1,0; −10,2): 12 st od spawnu, 14 st od bramy BONK. To miejsce, w którym gracz dziś wchodzi do gry, więc rano: spawn → E →
  bazar. „Stare miasteczko (E)” w bazarze prowadzi więc z powrotem na ten plac startowy, a nie do Krzywego
  Miasteczka — do decyzji (wybór 9).

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
  najbliższa cudza ≥ 11,8 st; „Stare miasteczko (E)” wolne na siatce chodzenia, 16 st od startu (zasięg 8; do 17.11.2026 12 st); tablica na
  powierzchni ze znacznika; zero liczb ≥ 100 w kodzie (położenia tylko w danych).
- **Czasy biegu planu** (siatka mapy, 16 st/s): portal 1,56 s, Brama Twierdzy 0,78, tablica 1,34, mistrz gier 2,66,
  zagroda 2,69, sklep magiczny 2,96, karczma 2,98, lochy 3,20, Brama Leśna 3,98, Training Center 4,32, zbrojownia
  4,42, „Stare miasteczko” 1,0 (przy 12 st: 0,75) — sklepy ≤ 5 s, portal ≤ 6 s (jak w PROJEKT.md mapy).
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

## Co sprawdzone w grze (17.11.2026, w nocy — Studio, tryb Play)

**Warunki.** Miejsce gry w Studio (Team Create, PlaceId 129485428021967), jeden gracz, okno gry 2041 × 1153. Ekran był
przykryty czarnym oknem — Studio rysuje wtedy ok. 15 kl./s, więc czas klatki 66,7 ms to ograniczenie Studia, nie gry.
W miejscu: `MiasteczkoBazar` (4410 części, po poprawkach z tej nocy), `MiasteczkoBazarGra` (60 instancji, 14 części,
13 podpowiedzi), `TeleportChmury`, `LasPas` + `LasPasGra` (silnik walki v2), `LasTeleport`, `KrzyweMiasteczko`.
Zapisy: `wyniki/` (nazwa konta zamieniona na `<gracz>`), zrzuty: `klatki/`.

**Lista B01–B15** (`testy/proba_play.py`) — przebieg o 02:23: **14 × OK, „?”: B14** (`wyniki/proba_play_20261117_0223_*`). Wcześniejsze przebiegi (01:17–02:19, dziewięć) wykryły błędy opisane
niżej w „Poprawkach”; zapisane m.in. `wyniki/proba_play_20261117_0126_*` (fałszywe OK w B09 — postać zginęła pod mapą
i odrodziła się przy spawnie, obok celu) i `…_0145_*` (B04 zagroda i B06 przed poprawkami próby).

| Punkt | Wynik |
|---|---|
| B01 gotowość | OK — `SerwerBazaruGotowy`, zgodność logiki „OK 70/70”, 13 podpowiedzi, `KlientBazaruGotowy`, Las i Chmury „jest” |
| B02 start bazaru | OK — postać 0,01 st od `PunktStartuBazaru`, 13/13 podpowiedzi włączonych |
| B03 bieg ze startu (`character_navigation`, od ruszenia do 2,5 st od stoiska) | OK — karczma 2,77 s (plan 2,99), mistrz gier 2,50 s (plan 2,68), sklep magiczny 2,70 s (plan 2,96), zbrojownia 4,15 s (plan 4,44), Training Center 4,07 s (plan 4,34), zagroda 2,42 s (plan 2,69), tablica 1,07 s (plan 1,34), Brama Twierdzy 0,62 s (plan 0,78), lochy 2,87 s (plan 3,20), **portal** 1,30 s (plan 1,56), Brama Leśna 3,83 s (plan 3,98), „Stare miasteczko” 0,78 s (plan 1,00). Każdy sklep ≤ 5 s, portal ≤ 6 s, każdy bieg krótszy od planu siatki |
| B04 E przy 8 punktach z oknem (prawdziwe E) | OK — karczma, mistrz gier, sklep magiczny, zbrojownia, Training Center, zagroda, tablica, Brama Twierdzy: `OstatnieE = <gracz>:<id>:okno`, `OknoMiejsca` z właściwym id, sygnał HUD (karczma → `Quests`, sklepy → `Shop`, zagroda → `Pets`, reszta bez), dymek zastępczy z tekstem z `miejsca.json` |
| B05 okna otwarte od razu | OK — żadne okno Pawła (Shop/Pets/Quests jeszcze nie istnieją); E przy portalu → `TeleportChmury` otwarte |
| B06 kamera za plecami w 5 wnętrzach | OK — 12,5 st i nic nie zasłania; mistrz gier 7,8 st (kamera opiera się o ramę drzwi karczmy, wszystko widać) |
| B07 portal → chmury → Las → chmury → „Miasteczko” | OK — Las (1114; 3; −700), powrót **na start bazaru, 0,0 st** (wpis w `krainy.json`) |
| B08 Brama Leśna → Las | OK — postać w Lesie (1114; 3,4; −700) w < 1 s (uchwyt pasa `PrzeniesDoLasu`); drugie E zaraz potem: „Chwila… jeszcze 2 s” / „… 3 s” (blokada `za_szybko`) |
| B09 stare ↔ nowe | OK — E w bazarze → 0,0 st od punktu powrotu przy spawnie; E przy „Nowe miasteczko (E)” → 0,0 st od startu bazaru; od razu drugie E → `za_szybko`; tabliczka 22,1 st od `PortalStart`; zero śmierci postaci |
| B10 tablica | OK — wiersz „1. `<gracz>` — poz. 1 · moc 130”, wierszy = liczba graczy (1) |
| B11 działka i lochy | OK — „Działka — wkrótce”, „Zamknięte”; po odblokowaniu kłódka niewidoczna u klienta 8/8 części, na serwerze 0/8; E → `OknoMiejsca("lochy")`, dymek „Hala portali — wkrótce”; po zamknięciu kłódka wraca |
| B12 niewidzialne ściany (marsz 30 st na zewnątrz ze skokami przy 4 brzegach) | OK — zatrzymanie na x ≈ 899 (zachód), x ≈ 1057 (wschód, zamknięta Brama Leśna), z ≈ −735,6 (północ), z ≈ −664,1 (południe); najniżej y ≈ 3,1 — nikt nie spadł |
| B13 dymek wyłączany atrybutem | OK — `DymkiWylaczone` i `BezDymku` gaszą dymek zbrojowni, po usunięciu wraca |
| B14 czas klatki | w porządku — 17.11 rano przy oknie Studio na wierzchu: 16,7 ms śr., p95 17,8–17,9 ms w 4 miejscach (60 kl./s). Nocne 66,7 ms to limit Studia z oknem w tle (15 kl./s) — nie zaciemnienie ekranu i nie pomiar gry |
| B15 konsola | OK — 0 błędów pakietu |

**Próba dodatkowa** (`testy/proba_dodatkowa.py`; D01, D03–D05 o 01:56, D02 i zrzuty o 02:04):

| Punkt | Wynik |
|---|---|
| D01 kamera na 6 stoiskach z postacią, za plecami i odwrócona | OK — za plecami 12,5 st wszędzie poza mistrzem gier (7,8 st: opiera się o ramę drzwi, sprzedawca widoczny); odwrócona (gracz obraca kamerę przy ladzie) 4,3–6,9 st: kamera opiera się o głowę sprzedawcy, który jest wtedy ZA kamerą — ekran czysty. Zero kamer w ozdobach bez kolizji, zero zasłon, nigdy nad stropem |
| D02 dymki 13 miejsc (kamera za plecami) | OK — 13/13 dymków na ekranie gracza, żaden po drugiej stronie ściany ani stropu; miejsca do stropu: karczma 5,8 st, mistrz gier 7,4, sklep magiczny 3,2, zbrojownia 4,0, Training Center 4,3, Brama Leśna 6,7 (pod łukiem); reszta pod gołym niebem. Teksty z `miejsca.json` (np. „Karczmarz: zadania wkrótce!”). Pierwsza wersja D02 (01:56) liczyła zasłonę promieniem i trafiała w głowy sprzedawców — dymek ma `AlwaysOnTop`, więc zasłona nie gra roli; kryterium poprawione |
| D03 stare ↔ nowe prawdziwym E | OK — 0,0 st od punktu powrotu przy spawnie i 0,0 st od startu bazaru, `…:stare_miasteczko:ok`, `…:nowe_miasteczko:ok`, zero śmierci |
| D04 Kamień Powrotu w lesie-pasie (prawdziwe E) | OK — z bazarem: start bazaru, 0,0 st; z uchwytem bazaru odpiętym na czas próby: `LasTeleport.PunktMiasteczka` (stare Krzywe Miasteczko), 0,0 st |
| D05 koszt u klienta (start bazaru) | „?” — w Workspace u klienta 36 256 części i 59 028 instancji (całe miejsce testowe; streaming włączony, bazar 4410 z 4410 wczytany); klatka 66,7 ms = limit Studia z oknem w tle (zob. B14: przy oknie na wierzchu 16,7 ms); D05 nie był powtarzany |

**Przejście przez chmury** (`swiat/teleport_chmury/testy/proba_play.py`, 01:25): **6/6 OK**, test 2 (Las → miasteczko,
prawdziwe kliknięcie myszą) — start bazaru, odchyłka 0,0. **Las-pas** (`swiat/las_pas_gra/testy/proba_play.py`, 01:49):
**15 × OK, P14 „?”** — m.in. P12 Kamień Powrotu (prawdziwe E) → start bazaru, walka z każdym gatunkiem, brama, przelot
tylko przy pierwszym wejściu (P05: licznik 1 → 1).

**Styk z płytą Baseplate:** skrypt na `swiat/miasteczko_bazar/czesci.json` — żadna płaska część nie ma górnej ściany
w płaszczyźnie gruntu (0,1) ani płyty (0,0), więc nie ma czego migotać; na zrzutach migotania nie widać.

## Poprawki po próbach w grze (17.11.2026)

1. **Tablica z rankingiem nieczytelna** (`miejsca.json` → `tablica.odsuniecie` 0,06 → **0,45**): plakietki podium
   i medale mapy wystają do 0,23 st przed deskę, a deska jest pochylona o 4°, więc przebijały SurfaceGui (czarne
   kreski i niebieskie kółko na rankingu). Teraz ranking wisi przed nimi i je zasłania.
2. **Tabliczka „STARE MIASTECZKO (E)” w kamerze** (`miejsca.json` → `od_startu_bazar` −12 → **−16**): przy 12 st
   wisiała dokładnie tam, gdzie stoi kamera gracza na starcie (ok. 12,5 st za głową) — przy lewej krawędzi ekranu, na
   HUD-zie. Teraz jest za kamerą, widać ją po obróceniu się.
3. **Mapa — kamera we wnętrzach** (`swiat/miasteczko_bazar`, szczegóły w jego README): Poppercam zatrzymuje kamerę
   tylko na częściach z kolizją. Przy obróconej kamerze stawała za tablicą zleceń w karczmie (cały ekran = tył deski),
   między ścianą a księgami maga i W głowie maga; słupek ramy drzwi zasłaniał postać przy mistrzu gier. Teraz z kolizją:
   tablica zleceń, księgi i kryształy dolnej półki maga, rama drzwi każdego sklepu, głowy i nakrycia głów sprzedawców.
4. **Postacie — własne projekty** (punkt 6 zadania): nowy karczmarz (łysy, krótka ruda broda bez wąsów, czerwona
   opaska karczmy, skórzany fartuch, zielona koszula, kufel), mistrz gier bez cylindra, monokla i wąsika (beret ze złotą
   kostką, okulary), trener z niebieską opaską zamiast czerwonej.
5. **Błędy próby, nie gry** (`testy/proba_play.py`): pusta tabela atrybutów przychodziła jako `[]` (wyjątek w B03);
   stoisko „Stare miasteczko” = jego punkt E, więc `CFrame.lookAt` na ten sam punkt dawał NaN i postać ginęła pod mapą
   — B09 „przechodziło” dzięki odrodzeniu przy spawnie (teraz B09 wymaga `…:stare_miasteczko:ok` i zera śmierci);
   B07 nie czekało na koniec przelotu pasa (chmury się nie otwierały, a sprawdzenie było za luźne — „OK” bez powrotu);
   B04 i B06 brały kierunek kamery z poprzedniego stoiska — podpowiedź E pokazuje się tylko na ekranie, więc E przy
   zagrodzie „nie działało”, gdy była za kamerą (teraz kamera za plecami przed każdym E); próg B06 8 → 6 st (rama drzwi
   to część z kolizją — 7,8 st przy pełnej widoczności to zwykła praca Poppercam); drugie E w B08 od razu haczykiem serwera „e” (z ustawieniem kamery i zrzutem mijała blokada 3 s, a powrót
   postaci skryptem pod bramę i znów do Lasu zostawiał w B09 nieczynne podpowiedzi E — przebiegi 02:05 i 02:19); przelot kamery pasa przy pierwszym wejściu do Lasu (z B07)
   rusza 2,4 s po przybyciu i potrafił wystartować już po powrocie do bazaru, zostawiając kamerę skryptową — B07
   czeka teraz na start i koniec przelotu (haczyk `zapomnijPrzelot` nie nadaje się: klient pasa czekał wtedy na
   przelot bez końca, kamera skryptowa do końca próby — przebieg 02:13); polskie znaki w haczykach (`json.dumps` dawał `\u00f3`, którego
   Luau nie czyta).

## Zrzuty z gry (`klatki/`, tryb Play)

| Plik | Co widać |
|---|---|
| `01_start_bazaru.jpg` | start bazaru (kamera gracza zaraz po przeniesieniu; za postacią tabliczka „STARE MIASTECZKO (E)”) |
| `02_uliczka_sklepow.jpg` | uliczka sklepów ze startu ku Bramie Leśnej (ujęcie u2 mapy) |
| `03_karczma_dymek.jpg` | wnętrze karczmy: nowy karczmarz za ladą z dymkiem „Karczmarz: zadania wkrótce!”, mistrz gier w berecie przy planszy (zrzut sprzed ostatniej poprawki twarzy karczmarza — usta jeszcze tuż pod nosem) |
| `03b_karczma_po_poprawce.jpg` | to samo wnętrze po poprawce z 17.11 ok. 02:30: karczmarz ma szeroki uśmiech z zębami nisko w brodzie (wcześniejsze usta pod nosem wyglądały jak czarne wąsy); zrzut z próby B06, kamera gracza |
| `04_karczmarz_z_bliska.jpg`, `04b_mistrz_gier_z_bliska.jpg` | nowe projekty postaci z bliska (tryb Edit, kamera edytora — `tools/studio_zrzuty.py`); karczmarz już po poprawce twarzy |
| `05_zbrojownia.jpg` | zbrojownia z dymkiem „Zbrojmistrz: sklep w budowie” |
| `06_sklep_magiczny.jpg` | sklep magiczny z dymkiem maga (na zrzucie częściowo za lampą — w grze dymek jest nad wszystkim) |
| `07_zagroda_petow.jpg` | zagroda petów: opiekunka z dymkiem, pies, smok, slime |
| `08_tablica_ranking.jpg` | tablica z rankingiem po poprawce: „RANKING SERWERA”, „1. Gracz — poz. 1 · moc 130”, ozdoby mapy już nie przebijają |
| `09_portal_krain.jpg` | portal krain (E → przejście przez chmury) |
| `10_brama_lesna.jpg` | Brama Leśna (E → Las) |
| `11_przejscie_stare_w_bazarze.jpg` | „STARE MIASTECZKO (E)” 16 st za startem, w środku uliczki, i tablica z rankingiem |
| `12_przejscie_nowe_w_starym.jpg` | plac startowy gry (spawn): „NOWE MIASTECZKO (E)” 12 st od spawnu, nic nie zasłania |

Narzędzie zrzutu nie rysuje `BillboardGui` z `AlwaysOnTop` (podpowiedzi E, dymki) — na czas zrzutów dymki dostają
u klienta `AlwaysOnTop = false`; podpowiedzi E na zrzutach nie ma. Nazwa konta na tablicy zamieniona u klienta na
„Gracz” (repozytorium jest publiczne). Kadry z kamery skryptowej (`proba_dodatkowa.py`, część Z).

## Czego nie sprawdzono (po próbach w Studio)

- **Telefon i pad** (emulator Studio): przycisk E, czytelność dymków i tabliczek na małym ekranie.
- **Dwóch graczy** (Test → Clients and Servers): dymki i kłódka lochów tylko u tego, kto nacisnął E; tablica z dwoma
  wierszami; blokady czasu osobno dla graczy (logika sprawdzona offline: 400 przebiegów).
- **Pamięć i czas klatki na telefonie** — czas klatki na komputerze zmierzony 17.11 przy oknie Studio na wierzchu (B14: 16,7 ms śr.); pamięci i telefonu nie mierzono. Sam bazar ma 4410 części; rozważyć `Persistent` dla huba.
- **Migotanie w ruchu** — sprawdzone tylko analizą płaszczyzn i nieruchomymi zrzutami.
- **Wykrywanie „okno się otworzyło”** — żadnego okna Pawła jeszcze nie ma (B05), więc heurystyka nie była sprawdzona na
  prawdziwym oknie.
- **Bieg na własnych nogach** — czasy z `character_navigation` (Studio prowadzi postać), nie z klawiatury.
- **Opublikowana gra** — pakiet działa tylko w Studio (serwer usuwa kontener poza Studio).
- **Podpowiedzi E po teleportach skryptem** — dwa przebiegi (02:05, 02:19): po przeniesieniu postaci skryptem
  (`PivotTo`) z bazaru do Lasu i z powrotem podpowiedź „Stare miasteczko (E)” przez kilka sekund nie działała
  (kamera skryptowa albo podpowiedzi wyłączone po stronie klienta). Gracz tak się nie przenosi (tylko E i uchwyty),
  więc próba już tego nie robi; przyczyny w kliencie pasa nie szukano — do sprawdzenia, gdyby wróciło w grze.

## Znane ryzyka

- **Testy Luau offline** wykonują logikę interpreterem `tools/walka/luau_mini.py` — to plik innego agenta, jeszcze nie
  w git (gdy zniknie, testy Luau są pomijane z uwagą, reszta działa). W Studio logika przeszła sprawdzian 70/70 (B01).
- **Położenie „Nowe miasteczko (E)” zależy od Studio**: prawdziwego SpawnLocation nie ma w żadnym pliku repozytorium.
  W tym miejscu jedyny spawn stoi w `DemoLesnaBaza` (nie w Krzywym Miasteczku) — punkt stanął przy nim, 12 st od
  spawnu i 22 st od `PortalStart` (wybór 9). Zła pozycja → atrybut ręczny `RecznyPunktStaregoMiasteczka`.
- **Podpowiedź E działa tylko na ekranie** (zachowanie Roblox): gracz, który stoi tyłem do sprzedawcy z kamerą
  odwróconą, nie zobaczy podpowiedzi i E nic nie zrobi — tak jest w każdej grze Roblox, ale testy muszą ustawiać
  kamerę (próby to robią).
- **Kolizje dodane w mapie dla kamery** (głowy sprzedawców, tablica zleceń, księgi, rama drzwi): wszystko nad głową
  gracza albo w płaszczyźnie ściany — przejścia i czasy biegu bez zmian (B03), ale skok przy ladzie może teraz trafić
  w głowę sprzedawcy.
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

**7. Przejście przez chmury i Kamień Powrotu mają lądować w bazarze?**
- Tak (wpisane 17.11.2026 na polecenie z zadania, D-075): „Miasteczko” na makiecie i Kamień Powrotu w lesie-pasie
  prowadzą na start bazaru, gdy stoi `MiasteczkoBazarGra`.
- Jeszcze nie: usunąć pierwszy wpis „przybycia” miasteczka w `krainy.json` i `D.miasteczko.bazar` w
  `swiat/las_pas_gra/generuj_dane.py` — wróci stare miasteczko.

**9. „Stare miasteczko (E)” — dokąd ma prowadzić?**
- Dziś: na plac startowy gry (jedyny `SpawnLocation` w (0; 0,5; 0), czyli `Workspace/DemoLesnaBaza`) — tam też stoi
  „Nowe miasteczko (E)”, więc rano: spawn → E → bazar i z powrotem.
- Do Krzywego Miasteczka (`KrzyweMiasteczko`, jak mówił opis w `miejsca.json`): atrybut `RecznyPunktStaregoMiasteczka`
  przy `LasTeleport.PunktMiasteczka` (−63,6; 3,4; −771,9) i przebudowa — ale wtedy przy spawnie nie ma przejścia do
  bazaru (zostaje przycisk Teleport → „Miasteczko”). Krzywe Miasteczko jest dziś osiągalne tylko przez stary las
  (`PortalStart` → Kamień Powrotu `LasTeleport`).

**8. Tymczasowe przejścia stare ↔ nowe: kiedy usunąć?**
- Gdy bazar zostanie przyjęty i spawn przeniesiony.
- Zostawić jako drogę do „zwiedzania” starego miasta (wybór 8 w `swiat/miasteczko_bazar/PROJEKT.md`).

## Poprawki po przejściu gry (17.11.2026, bez Studio — do wdrożenia)

Raport `swiat/przejscie_gry/RAPORT_PRZEJSCIA.md` (M10, P3). Zmienione: `miejsca.json` (+ wygenerowany
`zrodla/DaneBazaru.luau`), `zrodla/KlientBazaru.client.luau`, `zbuduj.py` (atrybut testowy), `testy/test_bazaru.py`.
- **Dymki dla gracza:** jedno zdanie, co tu będzie i że jeszcze nie działa (np. „Zbrojmistrz: broń i zbroje już
  wkrótce.”, „Wrota lochów są jeszcze zamknięte.”), bez „w budowie” i nawiasów dla twórców; odmowy Lasu bez
  „(nie ma pasa Lasu w miejscu)”; stopka tablicy „ranking graczy na tym serwerze”. Dymek 300 × 76 px (było 270 × 62).
  Nowy tekst odmowy `zamkniete` („Ta kraina jest jeszcze zamknięta.”) — taki powód zwraca już uchwyt Lasu
  (zmiany agenta Bagna w `swiat/las_pas_gra`).
- **Kamera w ścianach — przyczyna:** kamera Roblox (Poppercam) przybliża się tylko przed częściami Z KOLIZJĄ.
  W mapie bazaru (`swiat/miasteczko_bazar/czesci.json`) bez kolizji są m.in. wszystkie szczyty dachów (104), markizy
  nad stoiskami (30), daszki, belki stropu, ramy okien i skrzydła drzwi — kamera wchodzi w nie albo staje za nimi.
  **Poprawka w pakiecie:** klient co 0,1 s puszcza promień głowa → kamera i części mapy bazaru bez kolizji, które go
  przecinają, robi u siebie półprzezroczyste (`LocalTransparencyModifier` 0,7, nic nie idzie na serwer), a gdy
  przestają zasłaniać — oddaje 0. Kłódki lochów nie rusza. Wyłącznik: atrybut kontenera `PrzenikanieKamery = false`.
  Inne drogi (do decyzji, poza pakietem): kolizja dla szczytów dachów i markiz w mapie (przebudowa mapy) albo
  `DevCameraOcclusionMode = Invisicam` w `StarterPlayer` (wspólne ustawienie gry).
- Wdrożenie: pełna budowa `python -B swiat/miasteczko_bazar_gra/zbuduj.py` (stopka tablicy powstaje przy budowie;
  `--skrypty` podmieniłby tylko dymki i kamerę).

## Postacie niezależne zamiast figur (D-109, 19.11.2026 — część bez Studio)

Sześć miejsc w `miejsca.json` ma pole `"npc"` (karczma → `karczmarz`, mistrz_gier → `mistrz_gier`, sklep_magiczny →
`mag`, zbrojownia → `zbrojmistrz`, training_center → `trener`, zagroda_petow → `opiekunka`): id postaci z pakietu
`swiat/npc_gra`, która stoi w tym miejscu zamiast figury z klocków. To jedyna zmiana w tym pakiecie — pola nie czyta
`dane.py`, więc `DaneBazaru.luau`, jego skrót i skrypty są bez zmian i bazaru nie trzeba wdrażać od nowa. Figura
z mapy zostaje w Studio; klient pakietu `NpcGra` chowa ją u gracza, gdy stoi NPC (kolizje figury, dymek i podpowiedź E
bez zmian), a bez `NpcGra` albo przy `NpcWGrze = false` figura jest widoczna jak dawniej. Opis: `swiat/npc_gra/README.md`.
Sprawdzone w grze 19.11.2026 próbą pakietu NPC (N00–N14: 15 × OK — figury schowane, ich kolizje zostały, podpowiedź E
karczmy działa, tabliczka NPC ustępuje dymkowi bazaru).

## Zbrojownia: okno sklepu zamiast dymku — próba B04 i B13 (19.11.2026)
Rano 19.11 w próbie bazaru po E przy zbrojowni nie było dymku zastępczego (B04 i B13 BŁĄD). Przyczyna nie leży
w NPC ani w bazarze: w miejscu gry (tylko w Studio) stoi skrypt `StarterPlayerScripts/Client/ShopClient` — makieta
okna sklepu (ScreenGui `Shop`), która słucha `OknoMiejsca` dla `zbrojownia` i `sklep_magiczny` i zgłasza oba miejsca
atrybutem zdarzenia, więc bazar zgodnie z zasadą dymku nie pokazuje. Okno `Shop` było najpewniej otwarte jeszcze od
kroku sklepu magicznego (próba okien nie zamyka), więc klient bazaru nie zauważył „nowego” okna — próba nie dostała
ani okna, ani dymku.
Zmiana tylko w próbie (`testy/proba_play.py`; kod bazaru bez zmian): B04 przy zbrojowni oczekuje okna sklepu
zbrojmistrza (`SklepProbaOkno`, jedno okno, bez dymku), gdy stoi `Workspace/SklepProba`; bez niego, przy oknie
zgłoszonym atrybutem — okna `Shop` bez dymku; bez żadnego okna — dymku. B13 przy zbrojowni ze zgłoszonym oknem
sprawdza wyłączanie dymku przy mistrzu gier (miejsce bez okna). Dwa okna naraz przy zbrojowni rozwiązuje pakiet
sklepu (chowa makietę `Shop`, opis w `swiat/sklep_proba/README.md`).
