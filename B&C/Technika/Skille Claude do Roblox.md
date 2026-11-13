---
status: propozycja
tags: [technika, skille, claude]
---
# Skille Claude do Roblox

> [!info] W skrócie
> W `.claude/skills/` doszło sześć gotowych skilli: UI pod telefon, bezpieczne RemoteEventy, zapis danych z ProfileStore, architektura kodu, zakupy za Robuxy oraz ekonomia symulatora (ceny ulepszeń, rebirth, jajka z jawnymi szansami). Pięć pochodzi z roblox-brain (MIT), jeden z awesome-gamedev-agent-skills (Apache-2.0). Każdy przeczytałem w całości przed skopiowaniem. Claude włącza je sam, gdy zadanie pasuje do opisu skilla. Kanonu gry nie zmieniają, a gdy wiedza ze skilla przeczy sejfowi, pierwszeństwo ma sejf.

## Zainstalowane

| Skill | Do czego | Kiedy się włącza | Źródło i licencja |
|---|---|---|---|
| `roblox-gui` | HUD, menu, sklep, okna. Projekt zaczyna się od najmniejszego telefonu w poziomie: `CoreUISafeInsets`, wolne strefy joysticka i skoku, układ liczony z `AbsolutePosition`/`AbsoluteSize`. Do tego gamepad, sprzątanie tweenów i test „otwórz i zamknij okno 10 razy” na wycieki | budowa lub poprawka UI; UI ucięte, za małe albo nachodzi na coś na telefonie | [roblox-brain](https://github.com/TabooHarmony/roblox-brain) `ceee4aa`, MIT |
| `roblox-networking` | kontrakt każdego RemoteEventa: walidacja typów, NaN i nieskończoności, UTF-8, limity wywołań. Wynik liczy serwer. Wybór Reliable albo Unreliable (limit 1000 B) | nowy lub zmieniany remote, cooldowny, desync, przegląd bezpieczeństwa | roblox-brain `ceee4aa`, MIT |
| `roblox-data` | zapis gracza: szablon z wersją i migracje, `UpdateAsync`. ProfileStore: `StartSessionAsync` z limitem czasu, `EndSession`, `ProfileStore.Mock` w Studio. Osobny magazyn dla Studio, klucze `player_<UserId>` zgodne z RTBF | zapis i odczyt danych, nowe pole w save, utracone lub zdublowane dane | roblox-brain `ceee4aa`, MIT |
| `roblox-architecture` | gdzie leży kod i kto jest właścicielem stanu. Bez frameworków typu Knit i bez obowiązkowego `Init`/`Start`. Jeden właściciel zapisu i paragonów | nowa funkcja, podział dużego skryptu, cykliczne `require`, przegląd struktury | roblox-brain `ceee4aa`, MIT |
| `roblox-monetization` | game passy, developer products, idempotentny `ProcessReceipt`, subskrypcje, `PolicyService`, jawne szanse w płatnych losowaniach | nowy lub sprawdzany zakup, zakup nie dochodzi, ceny, oferty w sklepie | roblox-brain `ceee4aa`, MIT |
| `roblox-simulator-economy` | krzywe cen ulepszeń, dochód na sekundę, rebirth, dochód offline, skróty dużych liczb (K, M, B…). Panel szans jajka i losowanie biorą tę samą listę. Moduł `scripts/economy_math.luau` kopiuje się bez zmian do `src/shared` | liczby ekonomii, ceny ulepszeń, rebirth, jajka i pety za walutę | [awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) `c6ca6c4`, Apache-2.0 |

Pełne skróty commitów i teksty licencji są w `.claude/skills/LICENCJE-OBCE.md`.

**Uwagi do używania:**
- Kalkulator tempa ekonomii (`balance.luau`) i jego testy wymagają Lune. Nie mamy go zainstalowanego, a w [[Narzędzia i skille do Roblox]] ma status „PÓŹNIEJ”. Skill zawiera zdanie „zainstaluj Lune”, więc Claude ma najpierw zapytać. Bez Lune działają wzory, wzorce kodu serwera i sam `economy_math.luau` (czysty Luau, działa w Studio).
- Skille wspominają siostrzane skille, których nie instalowaliśmy (`roblox-security`, `roblox-input`, `roblox-analytics`, `roblox-luau-patterns`, `roblox-datastores`, `roblox-ui`). To tylko odsyłacze. Zamienniki: `roblox-networking` zamiast `roblox-security`, `roblox-data` zamiast `roblox-datastores`, `roblox-gui` zamiast `roblox-ui`.
- **Konflikt z propozycją w [[Styl UI gier Roblox]]:** notatka zaleca globalny `UIScale` liczony z rozmiaru ekranu. `roblox-gui` ostrzega, że jeden wspólny mnożnik zmniejsza naraz przyciski i tekst: okno 900×580 na telefonie 844×390 wychodzi w skali ok. 0,6, więc przycisk 58 px ma ok. 34 px. Zamiast zmniejszać, skill każe przebudować układ (mniej kolumn, przewijanie, panel szczegółów jako osobny widok). Decyzja należy do Game Directora; obie rzeczy są propozycjami.
- Skille nie znają kanonu gry (paleta, fonty, [[HUD]]). `roblox-gui` sam każe trzymać się istniejącego stylu projektu, a nie wymyślać nowego.
- Wbudowane skille Asystenta Studio (`rbx-instrument-analytics`, `rbx-device-simulator-lua`, `rbx-configs-experimentation`) dalej obowiązują. Nasze skille ich nie zastępują, a `roblox-simulator-economy` sam do nich odsyła.

## Odrzucone i dlaczego

| Kandydat | Licencja | Powód |
|---|---|---|
| roblox-brain `roblox-performance` | MIT | poprawny, ale ogólny. Część o telefonach jest cienka, telefon wykrywa przez `TouchEnabled` (a `roblox-gui` zaleca `PreferredInput`) i odsyła do niezainstalowanego `roblox-luau-patterns`. **PÓŹNIEJ**, przy pierwszych problemach z FPS |
| roblox-brain `roblox-analytics` | MIT | dubluje wbudowany `rbx-instrument-analytics`. PÓŹNIEJ, gdy panel zacznie czytać zdarzenia |
| roblox-brain `roblox-security`, `roblox-luau-core`, `roblox-luau-patterns`, `roblox-luau-types`, `roblox-server-data` | MIT | w dużej części pokryte przez `roblox-networking` i `roblox-data`. Każdy dodatkowy skill to więcej kontekstu przy zadaniu |
| roblox-brain `roblox-tooling`, `roblox-studio-mcp`, `roblox-cloud` | MIT | narzędzia opisuje [[Narzędzia i skille do Roblox]], a MCP i Open Cloud obsługują skrypty w `tools/` |
| roblox-brain `roblox-game-design`, `roblox-player-psychology`, `roblox-growth-design` | MIT | projekt gry prowadzi Game Director w sejfie, a te skille mogłyby podsuwać gotowe decyzje |
| awesome-gamedev-agent-skills `roblox-ui` | Apache-2.0 | dobry, ale dubluje `roblox-gui`. Jego bramka jakości odradza gradienty, poświaty i „pigułki”, czyli właśnie styl bubbly cartoon. Wymaga też osobnego skilla `game-ui-ux` |
| awesome-gamedev-agent-skills `roblox-luau`, `roblox-networking`, `roblox-datastores` | Apache-2.0 | dublują wybrane skille z roblox-brain |
| nonlooped/roblox-suite (`roblox-user-interfaces`, `roblox-animation` i inne) | MIT | płytsze od roblox-brain. `roblox-animation` dotyczy głównie animacji postaci 3D, a dołączone skrypty `.lua` wymagałyby osobnego przeglądu |
| luumenlabs/luau-skills | MIT | dubluje roblox-brain, ostatni commit 05.2026 |
| xtrair/figma-to-roblox-ui | MIT | dubluje nasz `figma-to-roblox` i ma sprzeczne reguły (wszystko w Scale, `UIStroke` zawsze `ScaledSize`, którego działania nie zweryfikowaliśmy) |
| greedychipmunk/agent-skills `roblox-game-development` | MIT | opis „Use this skill for any Roblox related tasks” włączałby go przy każdym zadaniu. 257 KB ogólników, szablony marketingowe, skrypty typu „Manager” |
| sentinelcore/roblox-skills, flatbedj/roblox-skills, dig1t/skills, brockmartin/roblox-game-skill | brak licencji | nie wolno kopiować |
| christopher-buss/skills | niejasna (GitHub: NOASSERTION) | pisany pod roblox-ts, a my piszemy w Luau |

## Jak dodać kolejny skill

1. **Pobierz** repozytorium do nowego, pustego katalogu tymczasowego poza repo gry (`git clone --depth 1 <adres>`). Niczego z niego nie uruchamiaj i nie instaluj: bez `npx skills add`, npm i pip.
2. **Przeczytaj** cały `SKILL.md` oraz pliki z `references/` i `scripts/`. Odrzuć skill, który każe wysyłać dane, pobierać i uruchamiać kod albo zmieniać ustawienia, opiera się na porzuconych bibliotekach (np. Knit) albo przeczy `CLAUDE.md` i kanonowi.
3. **Sprawdź licencję** w pliku `LICENSE`: tylko MIT, Apache-2.0, CC0 lub podobnie liberalna. Bez licencji nie kopiujemy. Zapisz adres repo i commit (`git rev-parse HEAD`).
4. **Skopiuj** cały katalog skilla do `.claude/skills/<nazwa>/`. Nazwa nie może kolidować z istniejącym skillem. Na końcu `SKILL.md` dopisz sekcję „Źródło” (repo, commit, licencja, data, kto przejrzał).
5. **Dopisz** wiersz do `.claude/skills/LICENCJE-OBCE.md`, a przy nowym autorze także pełny tekst licencji. Potem zaktualizuj tę notatkę.

## Powiązane
[[Narzędzia]] · [[Narzędzia i skille do Roblox]] · [[Styl UI gier Roblox]]
