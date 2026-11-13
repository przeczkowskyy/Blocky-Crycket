---
status: propozycja
tags: [badania, narzędzia, rojo, mcp, analityka]
---
# Narzędzia i skille do Roblox

> [!info] W skrócie
> Rdzeń łańcucha to Rokit 1.2.0 z przypiętymi wersjami: Rojo 7.7.1 (nowsze niż nasze 7.6.1, z poprawkami ścieżek Windows i komendą `syncback`), Selene 0.32.0, StyLua 2.6.0 i Wally 0.3.2. Aftman, Knit, Mantle i stary serwer `studio-rust-mcp-server` są zarchiwizowane albo porzucone. Oficjalny MCP jest teraz wbudowany w Studio. Do panelu wystarczą trzy warstwy: publiczne `games.roblox.com` bez klucza, Analytics Query API z kluczem `universe.analytics:read` oraz własne zdarzenia `AnalyticsService` widoczne w tym samym API. Live server nie wyśle danych na `localhost`, więc błędy lepiej zapisywać w MemoryStore lub DataStore i czytać przez Open Cloud.

Wersje sprawdzone na stronach wydań GitHub 2026-11-12. Wszystkie polecenia dotyczą PowerShell na Windows.

## a) Łańcuch narzędzi

| Narzędzie | Licencja | Wersja | Co daje | Werdykt | Instalacja |
|---|---|---|---|---|---|
| [Rokit](https://github.com/rojo-rbx/rokit) | MIT | 1.2.0 (30.09.2025) | Menedżer narzędzi z wersjami w `rokit.toml`, czyta też `aftman.toml` i `foreman.toml` | **TERAZ** | `Invoke-RestMethod https://raw.githubusercontent.com/rojo-rbx/rokit/main/scripts/install.ps1 \| Invoke-Expression` |
| [Aftman](https://github.com/LPGhatguy/aftman) | MIT | 0.3.0, **archiwum** | Poprzednik Rokita | **NIE** | — |
| [Rojo](https://github.com/rojo-rbx/rojo) | MPL-2.0 | **7.7.1** (02.10.2026), stabilne | 7.7.0: `rojo syncback` (pliki z `.rbxl`), websockety, `.jsonc`. 7.7.1: poprawki ścieżek `\\?\` na Windows | **TERAZ** (aktualizacja z 7.6.1) | `rokit add rojo-rbx/rojo@7.7.1`, potem wtyczka: `rojo plugin install` |
| [Wally](https://github.com/UpliftGames/wally) | MPL-2.0 | 0.3.2 (05.06, stabilna; istnieje tylko pre-release 0.4.0-alpha.1 z 12.10) | Paczki Luau (`wally.toml`), działa mimo braku nowych stabilnych wydań | **TERAZ** (przy pierwszej bibliotece) | `rokit add UpliftGames/wally@0.3.2` |
| [Selene](https://github.com/Kampfkarren/selene) | MPL-2.0 | 0.32.0 (01.10.2026) | Linter Luau, `std = "roblox"`. Dashboard już go wywołuje, jeśli jest | **TERAZ** | `rokit add Kampfkarren/selene@0.32.0` |
| [StyLua](https://github.com/JohnnyMorganz/StyLua) | MPL-2.0 | 2.6.0 (10.10.2026) | Formatowanie, jeden styl u obu osób i u Claude'a | **TERAZ** | `rokit add JohnnyMorganz/StyLua@2.6.0` |
| [luau-lsp](https://github.com/JohnnyMorganz/luau-lsp) | MIT | 1.70.1 (27.09.2026) | Typy i autouzupełnianie (rozszerzenie VS Code), `luau-lsp analyze` w CI | **PÓŹNIEJ** | `rokit add JohnnyMorganz/luau-lsp@1.70.1` + rozszerzenie „Luau Language Server” |
| [wally-package-types](https://github.com/JohnnyMorganz/wally-package-types) | MIT | 1.7.0 | Typy paczek Wally dla luau-lsp | **PÓŹNIEJ** (razem z luau-lsp) | `rokit add JohnnyMorganz/wally-package-types@1.7.0` |
| [Lune](https://github.com/lune-org/lune) | MPL-2.0 | 0.11.1 (21.10.2026) | Samodzielny runtime Luau do skryptów, czyta i zapisuje pliki miejsc | **PÓŹNIEJ** (np. symulacje ekonomii w Luau) | `rokit add lune-org/lune@0.11.1` |
| [darklua](https://github.com/seaofvoices/darklua) | MIT | 0.19.0 | Transformacje i bundlowanie kodu | **NIE** (nie potrzebujemy) | — |
| [rbxcloud](https://github.com/Sleitnick/rbxcloud) | MIT | 0.17.0 (03.2025) | CLI do Open Cloud | **NIE** (narzędzia Pythona w `tools/` robią to samo) | — |
| [Mantle](https://github.com/blake-mealey/mantle) | MIT | 0.11.18 (niezweryfikowane), **nieutrzymywany** (README: „no longer maintained”) | Infrastruktura jako kod (wdrażanie miejsc) | **NIE** | — |
| [Asphalt](https://github.com/jackTabsCode/asphalt) | MIT | 2.0.2 (07.07.2026) | Wysyła obrazy, dźwięki i modele i generuje moduł Luau z ID. Wymaga klucza `asset:read`+`asset:write` | **PÓŹNIEJ** (alternatywa dla `assets/manifest.json` w [[Pipeline assetów]]) | `rokit add jacktabscode/asphalt@2.0.2` |
| [Tarmac](https://github.com/Roblox/tarmac) | MIT | 0.8.2 | Poprzednik Asphalta | **NIE** | — |
| [run-in-roblox](https://github.com/rojo-rbx/run-in-roblox) | MIT | 0.3.0, ostatni commit 03.2024 | Uruchamia skrypt w Studio z CLI | **NIE** (zastępują go MCP `start_stop_play` i Open Cloud Luau Execution) | — |

Aktualizację Rojo robią obie osoby jednocześnie (CLI i wtyczka). Wersje wtyczki i serwera powinny się zgadzać (niezweryfikowane jako twarda blokada). `rojo syncback` rozwiązuje problem z [[Rojo i struktura projektu]]: zawartość istniejącą tylko w `.rbxl` da się zrzucić do plików.

## b) Biblioteki gry

Wally ma wiele nieoficjalnych kopii (np. `ddashdev/trove`, `vyon/profilestore`). Używamy tylko scope'ów z tabeli.

| Biblioteka | Licencja | Wersja | Do czego | Werdykt | `wally.toml` |
|---|---|---|---|---|---|
| [ProfileStore](https://github.com/MadStudioRoblox/ProfileStore) | Apache-2.0 (niezweryfikowane) | 1.0.3 (Wally `lm-loleris/profilestore`; repo nie ma wydań na GitHubie) | Zapis profilu z session lockingiem i auto-zapisem. Nie nadaje się do globalnych rankingów | **TERAZ** (przed pierwszym zapisem danych) | `[server-dependencies] ProfileStore = "lm-loleris/profilestore@1.0.3"` |
| [Replica](https://github.com/MadStudioRoblox/Replica) | Apache-2.0 | bez wydań | Replikacja stanu serwer→wybrani klienci | **PÓŹNIEJ** (Creator Store, brak `wally.toml`) | — |
| [Promise](https://github.com/evaera/roblox-lua-promise) | MIT | 4.0.0 | Asynchroniczność | **PÓŹNIEJ** | `evaera/promise@4.0.0` |
| Signal / Trove ([RbxUtil](https://github.com/Sleitnick/RbxUtil)) | MIT | 2.0.3 / 1.8.0 | Zdarzenia i sprzątanie połączeń | **TERAZ** (lekkie) | `sleitnick/signal@2.0.3`, `sleitnick/trove@1.8.0` |
| [Janitor](https://github.com/howmanysmall/Janitor) | MIT | 1.18.3 (Wally) | Alternatywa Trove | **NIE** (jedno wystarczy) | — |
| [Vide](https://github.com/centau/vide) | MIT | 0.4.1 | Reaktywne UI, aktywny (push 10.2026) | **PÓŹNIEJ**, jeśli dynamiczne UI | `centau/vide@0.4.1` |
| [Fusion](https://github.com/dphfox/Fusion) | MIT | 0.3 (Wally `elttob/fusion@0.3.0`) | Reaktywne UI | alternatywa dla Vide | — |
| [React-lua](https://github.com/jsdotlua/react-lua) | MIT | 17.2.1 | Port Reacta, ciężki | **NIE** (GUI idzie z Figmy) | — |
| [Knit](https://github.com/Sleitnick/Knit) | MIT | 1.7.0, **archiwum** | Framework usług | **NIE** | — |
| [Zap](https://github.com/red-blox/zap) | MIT | 0.6.29 | Generator sieci z IDL, binarny | **PÓŹNIEJ** (przy dużym ruchu) | `rokit add red-blox/zap@0.6.29` |
| [ByteNet](https://github.com/ffrostfall/ByteNet) | MIT | 0.4.6 (Wally) | Buforowa sieć, ostatni push 08.2025 | **NIE** (wybieramy Zap) | — |
| [TopbarPlus](https://github.com/1ForeverHD/TopbarPlus) | MIT + **wymóg przypisu** | 3.5.0 | Ikony w górnym pasku | **PÓŹNIEJ** | `1foreverhd/topbarplus@3.5.0` |
| [Cmdr](https://github.com/evaera/Cmdr) | MIT | 1.13.1 | Konsola admina (dawanie golda, testy ekonomii) | **PÓŹNIEJ** (w fazie balansu) | `evaera/cmdr@1.13.1` |

**Duże liczby.** Luau używa double: liczby całkowite są dokładne do 2^53 (~9·10^15), a zakres sięga ~1,8·10^308 ([devforum](https://devforum.roblox.com/t/how-do-you-handle-numbers-larger-than-the-max/159933)). Na start wystarczy zwykły `number` z własnym formatowaniem sufiksami (K, M, B, T…), testowanym jednostkowo. Biblioteki [EternityNum2](https://devforum.roblox.com/t/doing-math-with-arbitrarily-large-numbers-eternitynum2/3081503), [InfiniteMath](https://devforum.roblox.com/t/infinitemath-go-above-103081e308/2182434) i [GammaNum](https://devforum.roblox.com/t/gammanum-up-to-100x-faster-than-eternitynum/3906397) potrzebujemy dopiero wtedy, gdy krzywa przekroczy ~10^15 i liczy się dokładność. Ich deklaracje szybkości pochodzą od autorów (niezweryfikowane), licencji nie sprawdzałem.

## c) AI i agenci

**Oficjalny MCP Studio** jest wbudowany w Studio. Włącza się go w Assistant → … → Manage MCP Servers → „Enable Studio as MCP server”, a Quick connect obsługuje Claude Code. Ręcznie na Windows: `claude mcp add roblox-studio -- cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat` (składnia wyprowadzona z dokumentacji). Wiele instancji Studio rozróżnia `studio_id` z `list_roblox_studios`. Dokumentacja wymienia też narzędzia, których nie mamy na liście: `character_navigation`, `user_keyboard_input`, `user_mouse_input`, `http_get`, `get_studio_state`. Z kolei naszych `list_skills`, `open_cloud_invoke` i `generate_scene` nie ma w dokumentacji (niezweryfikowane: inna wersja Studio). Repozytorium `Roblox/studio-rust-mcp-server` zarchiwizowano 03.04.2026. **Werdykt: zostaje, nic nie instalować.**

**Wbudowane skille Asystenta** (`rbx-*`, dostępne przez narzędzie `skill`):
- `rbx-instrument-analytics` przegląda grę i po akceptacji dodaje `AnalyticsService` (**używać**),
- `rbx-unit-test`, `rbx-debug`, `rbx-perf-profiling`, `rbx-scene-analysis`, `rbx-device-simulator-lua`, `rbx-configs-experimentation` (A/B przez ConfigService), `rbx-docs-search`.

Własne skille Asystenta to Markdown z polami `name`, `description` i `enabled`, przypisane do konta Roblox.

| Pozycja | Licencja | Ocena | Werdykt |
|---|---|---|---|
| [boshyxd/robloxstudio-mcp](https://github.com/boshyxd/robloxstudio-mcp) | MIT | Zarchiwizowany 06.2026. Forki (drgost1, code-and-relax) mają niepewne pochodzenie, a `npx` uruchamia stary pakiet | **NIE** |
| [TabooHarmony/roblox-brain](https://github.com/TabooHarmony/roblox-brain) | MIT | 29 skilli, m.in. `roblox-data`, `roblox-networking`, `roblox-security`, `roblox-monetization`, `roblox-analytics`. Zgodny z oficjalnym MCP, bez wydań | **PÓŹNIEJ**: wybrane skille po przeglądzie skopiować do `.claude/skills/` |
| [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) (`roblox-luau`) | Apache-2.0 | Ogólny, 79 skilli na wiele silników | **PÓŹNIEJ** (do porównania) |
| [brockmartin/roblox-game-skill](https://github.com/brockmartin/roblox-game-skill) | **brak licencji** | 3 commity, nie wolno legalnie kopiować | **NIE** |

Instalator `npx skills add …` należy do serwisu zewnętrznego. Bezpieczniej pobrać repozytorium, przejrzeć `SKILL.md` i skopiować ręcznie.

## d) Open Cloud i dane do panelu

| Dane | Źródło | Klucz / uprawnienie |
|---|---|---|
| Gracze teraz (`playing`), wizyty, ulubione | `GET https://games.roblox.com/v1/games?universeIds={id}` (sprawdzone 2026-11-12) | **bez klucza** |
| Łapki | `GET https://games.roblox.com/v1/games/votes?universeIds={id}` | bez klucza |
| placeId → universeId | `GET https://apis.roblox.com/universes/v1/places/{placeId}/universe` | bez klucza |
| DAU (`DailyActiveUsers`), `PeakConcurrentPlayers` (dane wydajności i stabilności dostępne 28 dni, biznesowe metryki do 1468 dni; [źródło](https://create.roblox.com/docs/cloud/guides/analytics/metrics)), retencja pod nazwami `ForwardD1Retention`/`ForwardD7Retention` (D30 i `Visits`, sesje: niezweryfikowane) | `POST https://apis.roblox.com/analytics-query-api/v1/universes/{id}/metrics` | `universe-analytics` → `universe.analytics:read` |
| Robuxy: `DailyRevenue`, `ItemMonetizationRevenue` (po `ProductKey`/`ProductType`), ARPPU, `PayingUsers` | jw. | jw. |
| Crashe: `ClientCrashCount`, `ServerCrashCount`, `OomUnexpectedExits` (28 dni) | jw. | jw. |
| Ekonomia, lejki, zdarzenia własne (`Economy*`, `Funnel*`, `CustomEvent*`) | jw., zasilane z `AnalyticsService` | jw. |
| Własne logi z gry | DataStore / MemoryStore | `universe-datastores.objects:read`, `memory-store.sorted-map:read` |
| Wiadomość z panelu do serwerów | MessagingService (Open Cloud tylko publikuje) | `universe-messaging-service:publish` |
| Testy Luau w chmurze | Luau Execution (zadanie do 5 min, tworzenie 5/min na właściciela klucza, max 10 niezakończonych zadań na place, logi do 450 KB, dane zadania przez 24 h po zakończeniu; [źródło](https://create.roblox.com/docs/cloud/reference/features/luau-execution.md)) | `universe.place.luau-execution-session:write` |
| Game passy / produkty | Open Cloud | `game-pass:read`; `developer-product:read` (niezweryfikowane) |

Osobnego API z listą pojedynczych transakcji nie znalazłem. Najbliżej jest `ItemMonetizationRevenue` w rozbiciu na `ProductKey`.

**Telemetria w grze:**
- `AnalyticsService:LogEconomyEvent` (limity: dashboard ekonomii pozwala na 5 walut, [źródło](https://create.roblox.com/docs/production/analytics/economy-events); 20 typów transakcji i 100 SKU niezweryfikowane), `LogFunnelStepEvent` (limit 10 lejków niezweryfikowany), `LogOnboardingFunnelStepEvent`, `LogProgressionEvent` i `LogCustomEvent` (do 3 pól własnych). Pasuje do golda i questów z [[Karczma (Questy)]], do ulepszeń z [[Twierdza (Tycoon)]] i do jaj z [[Pety]].
- Błędy: `ScriptContext.Error` i `LogService.MessageOut` na serwerze. Agregujemy je per minuta, zapisujemy do sorted mapy MemoryStore z TTL, a panel odpytuje Open Cloud.
- `HttpService` z live servera nie dosięgnie `localhost` (działa tylko w Studio). Wysyłka push wymagałaby publicznego hosta.
- Klucz trzymamy w `dashboard/.env`, z ograniczeniem do IP panelu (dokumentacja zaleca brak ograniczenia IP tylko dla kluczy używanych z serwerów Roblox). Klucz nieużywany ani nieaktualizowany przez 60 dni wygasa ([źródło](https://create.roblox.com/docs/cloud/auth/api-keys)).

## e) CI: GitHub Actions

Repozytorium jest publiczne. Plik `.github/workflows/ci.yml`:

```yaml
name: CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: CompeyDev/setup-rokit@v0.2.1   # MIT, czyta rokit.toml
      - run: rokit install --no-trust-check  # flaga przeznaczona dla CI
      - run: rojo build default.project.json -o build.rbxl
      - run: selene src
      - run: stylua --check src
```

Alternatywa dla StyLua: `JohnnyMorganz/stylua-action@v5` z `version: 2.6.0` (wersja przypięta, bez `latest`).

## Zestaw startowy (obie osoby)

1. Zainstalować Rokit (polecenie z tabeli), zrestartować terminal i sprawdzić `rokit --version` (ma być 1.2.0).
2. W katalogu gry utworzyć `rokit.toml`:
   ```toml
   [tools]
   rojo = "rojo-rbx/rojo@7.7.1"
   wally = "UpliftGames/wally@0.3.2"
   selene = "Kampfkarren/selene@0.32.0"
   stylua = "JohnnyMorganz/StyLua@2.6.0"
   ```
3. Uruchomić `rokit install` i zaakceptować zaufanie do narzędzi.
4. Zaktualizować wtyczkę poleceniem `rojo plugin install`, zrestartować Studio i połączyć się na porcie 34872.
5. Utworzyć `selene.toml` z linią `std = "roblox"` oraz pusty `stylua.toml`, potem jednorazowo wykonać `stylua src` w osobnym commicie.
6. Dodać `wally.toml` z ProfileStore, Signal i Trove, uruchomić `wally install`, zmapować `Packages`/`ServerPackages` w `default.project.json` i dopisać je do `.gitignore`.
7. Dodać workflow CI z sekcji e.
8. W Studio sprawdzić Quick connect MCP. Przy dodawaniu analityki prosić o skill `rbx-instrument-analytics`.
9. Utworzyć klucz Open Cloud tylko z `universe.analytics:read` dla tej gry i wpisać go do `dashboard/.env`.

## Czego nie instalować

- **Aftman i Foreman**: Aftman zarchiwizowany, Foreman zbędny przy Rokicie.
- **Knit**: zarchiwizowany.
- **Mantle**: autor ogłosił koniec utrzymania.
- **run-in-roblox**: porzucony, zastąpiony przez MCP i Luau Execution.
- **Tarmac**: zastąpiony przez Asphalta.
- **`studio-rust-mcp-server` i `robloxstudio-mcp`**: zarchiwizowane, a forki są niepewne. Społecznościowy MCP wymaga też HTTP w grze.
- **React-lua**: za ciężki przy GUI z Figmy.
- **ByteNet i Janitor**: dublują Zap i Trove.
- **rbxcloud i darklua**: brak potrzeby.
- **brockmartin/roblox-game-skill**: brak licencji.
- **Kopie paczek w Wally spoza oficjalnych scope'ów**: ryzyko podmiany kodu.

## Weryfikacja

Sprawdzone 2026-11-12.
- Rokit 1.2.0 (30.09) i polecenie instalacji PowerShell -> potwierdzone -> https://github.com/rojo-rbx/rokit/releases, https://raw.githubusercontent.com/rojo-rbx/rokit/main/README.md
- Rojo 7.7.1 (02.10) z `syncback` (7.7.0), websocketami, `.jsonc` i poprawką `\\?\` -> potwierdzone -> https://github.com/rojo-rbx/rojo/releases
- Selene 0.32.0 (01.10.2026) -> potwierdzone -> https://github.com/Kampfkarren/selene/releases
- StyLua 2.6.0 (10.10.2026) -> potwierdzone -> https://github.com/JohnnyMorganz/StyLua/releases
- luau-lsp 1.70.1 (27.09.2026), Lune 0.11.1 (21.10), Asphalt 2.0.2 (07.07) -> potwierdzone -> strony releases tych repozytoriów
- `studio-rust-mcp-server` zarchiwizowany 03.04.2026 -> potwierdzone -> https://github.com/Roblox/studio-rust-mcp-server
- Wbudowany MCP: ścieżka Quick connect, komenda `cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat`, dodatkowe narzędzia -> potwierdzone (komenda w docs bez `claude mcp add`; `list_skills`, `open_cloud_invoke`, `generate_scene` faktycznie nie ma na liście) -> https://create.roblox.com/docs/studio/mcp
- Knit zarchiwizowany (31.07.2024) -> potwierdzone -> https://github.com/Sleitnick/Knit
- Klucz API wygasa po 60 dniach bezczynności -> potwierdzone -> https://create.roblox.com/docs/cloud/auth/api-keys
- Wally 0.3.2 -> poprawione (dopisano pre-release 0.4.0-alpha.1; rok 2023 nieweryfikowalny) -> https://github.com/UpliftGames/wally/releases
- Luau Execution: „logi 24 h” -> poprawione (logi trwają tyle co zadanie, max 450 KB; zadanie 24 h po zakończeniu; 10 równoległych zadań) -> https://create.roblox.com/docs/cloud/reference/features/luau-execution.md
- Metryki Analytics Query: „28 dni” dla `PeakConcurrentPlayers` -> poprawione (28 dni to dane wydajności; biznesowe 1468 dni); retencja to `ForwardD1Retention` itd.; `Visits`, D30, sesje -> niezweryfikowane -> https://create.roblox.com/docs/cloud/guides/analytics/metrics
- Limity AnalyticsService (20 typów transakcji, 100 SKU, 10 lejków) -> niezweryfikowane; potwierdzono tylko 5 walut w dashboardzie ekonomii -> https://create.roblox.com/docs/production/analytics/economy-events
- ProfileStore 1.0.3 pod `lm-loleris/profilestore` -> potwierdzone w rejestrze Wally; licencja Apache-2.0 niezweryfikowana -> https://api.wally.run/v1/package-search?query=profilestore
- Mantle „nieutrzymywany” -> potwierdzone; wersja 0.11.18 niezweryfikowana -> https://github.com/blake-mealey/mantle
- Zakres `universe.analytics:read` -> niezweryfikowane (strona metryk nie podaje nazwy zakresu)

## Powiązane

[[Narzędzia]] · [[Rojo i struktura projektu]] · [[Workflow i Git]] · [[Pipeline assetów]] · [[Technika gry — serwery, światy, walki]] · [[Retencja i monetyzacja — co wolno i co działa]] · [[Rejestr decyzji]] · [[Pytania otwarte]]

## Źródła

Dostęp 2026-11-12.
- https://github.com/rojo-rbx/rojo/releases
- https://github.com/rojo-rbx/rokit
- https://github.com/rojo-rbx/rokit/blob/main/src/cli/install.rs
- https://github.com/LPGhatguy/aftman
- https://github.com/UpliftGames/wally
- https://github.com/Kampfkarren/selene
- https://github.com/JohnnyMorganz/StyLua
- https://github.com/JohnnyMorganz/luau-lsp
- https://github.com/JohnnyMorganz/wally-package-types
- https://github.com/lune-org/lune
- https://github.com/seaofvoices/darklua
- https://github.com/Sleitnick/rbxcloud
- https://github.com/blake-mealey/mantle
- https://github.com/jackTabsCode/asphalt
- https://github.com/Roblox/tarmac
- https://github.com/rojo-rbx/run-in-roblox
- https://github.com/MadStudioRoblox/ProfileStore
- https://github.com/MadStudioRoblox/Replica
- https://github.com/evaera/roblox-lua-promise
- https://github.com/Sleitnick/RbxUtil
- https://github.com/howmanysmall/Janitor
- https://github.com/centau/vide
- https://github.com/dphfox/Fusion
- https://github.com/jsdotlua/react-lua
- https://github.com/Sleitnick/Knit
- https://github.com/red-blox/zap
- https://github.com/ffrostfall/ByteNet
- https://github.com/1ForeverHD/TopbarPlus
- https://github.com/evaera/Cmdr
- https://api.wally.run/v1/package-search?query=profilestore
- https://create.roblox.com/docs/studio/mcp
- https://github.com/Roblox/studio-rust-mcp-server
- https://devforum.roblox.com/t/studio-mcp-server-updates-and-external-llm-support-for-assistant/4415631
- https://create.roblox.com/docs/assistant/skills
- https://github.com/boshyxd/robloxstudio-mcp
- https://github.com/TabooHarmony/roblox-brain
- https://github.com/gamedev-skills/awesome-gamedev-agent-skills
- https://github.com/brockmartin/roblox-game-skill
- https://create.roblox.com/docs/cloud/guides/analytics
- https://create.roblox.com/docs/cloud/guides/analytics/metrics
- https://create.roblox.com/docs/cloud/auth/api-keys
- https://cdn.jsdelivr.net/gh/Roblox/creator-docs@main/content/en-us/reference/cloud/cloud.docs.json
- https://create.roblox.com/docs/cloud/reference/features/luau-execution
- https://create.roblox.com/docs/cloud/reference/features/game-passes
- https://create.roblox.com/docs/reference/engine/classes/AnalyticsService
- https://create.roblox.com/docs/reference/engine/classes/ScriptContext
- https://create.roblox.com/docs/reference/engine/classes/LogService
- https://devforum.roblox.com/t/cant-make-http-request-on-localhost-in-studio/1288931
- https://games.roblox.com/v1/games?universeIds=383310974
- https://github.com/CompeyDev/setup-rokit
- https://github.com/JohnnyMorganz/stylua-action
