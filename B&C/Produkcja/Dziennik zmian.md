---
status: kanon
tags: [produkcja, dziennik]
---
# Dziennik zmian

Najnowsze na górze. Każdy wpis: data, kto, co się zmieniło, które pliki i notatki.

## 2026-11-13 · Claude Code (okno ekwipunku: upload EqBg3 v5)
- `EqBg3` v5 wgrany po „tak” (136695799877394), GUI przepięte. Po ~10 min Roblox jeszcze nie serwuje obrazka (w Play `IsLoaded = false`, lewa dolna ćwiartka okna pusta), ponowny upload zwraca to samo ID – prawdopodobnie moderacja. v4 (134448521798525) dalej się wczytuje.
- Do sprawdzenia: status moderacji w Studio (Asset Manager) / Creator Dashboard. Jeśli odrzucony – wrócić do v4 albo wgrać ponownie.

## 2026-11-13 · Claude Code (okno ekwipunku: obrys kart, zasłonki na całe wnętrze)
- Prawdziwa przyczyna złych kart w kolumnach 1 i 3: czyszczenie tekstu („DAMAGE…”, „DEFENSE…”) wymazało pionowy wewnętrzny obrys przy beżu, a odbicie lustrzane powieliło to na prawą stronę. `tools/eq_paint.py` bierze teraz krawędź (30 px) i beż z oryginału. `EqBg3` v5 czeka na akceptację.
- Lekcja: wcześniejsze „poprawione” oceniałem na pomniejszonych podglądach; karty sprawdzać w powiększeniu ×2–×3.
- Druga przyczyna: prawa krawędź kolumny 3 była źle zmierzona (1332 = ramka panelu, karta kończy się na 1315). Teraz wszystkie kolumny odbijane symetrycznie, krawędź granatowego paska z karty CONST.
- Test zasłonek myszą w Play (Scrap tymczasowo `slot = "Any"`): Trinket → Helmet → Chest → Gloves → Boots → Weapon → Amulet → Belt → Ring → Trinket; po każdym ruchu zasłonka tylko w zajętym slocie, zrzuty Boots/Weapon/Belt/Ring + wszystkie 9 naraz – wnętrza wypełnione w całości. Scrap wrócił do `slot = "Trinket"`; obsługa `"Any"` zostaje w kodzie do testów.
- Zasłonki slotów: dokładne wnętrze slotu wykrywane za ciemnym obrysem (`tools/eq_slice.py`), dwie warstwy: faz `724837` + środek `84563E` (mediana ze wszystkich slotów). Test Play: Trinket bez sakiewki, wnętrze wypełnione do obrysu.

## 2026-11-13 · Claude Code (okno ekwipunku: zasłonki slotów)
- `EqBg3` v4 wgrany do Roblox (134448521798525) po „tak”.
- Sloty ekwipunku: gdy leży w nich przedmiot, wypalona sylwetka (hełm, sakiewka…) znika pod natywną zasłonką `Cover` w kolorze wnętrza slotu (kolor liczony w `tools/eq_slice.py` → `layout.json` `slot_covers`). Uwaga: Rojo dopisuje nowe dzieci na końcu, więc warstwy ustawiamy jawnie przez `ZIndex`.
- Test Play: Scrap w slocie Trinket bez sakiewki pod spodem; po przeniesieniu do plecaka sylwetka wraca.

## 2026-11-13 · Claude Code (okno ekwipunku: karty, v4)
- Karty w grafice mają różne szerokości (351 / 361 / 369 px), a skrypty przesuwały je o stałe odstępy, więc pasowała tylko środkowa kolumna (CONST, LUCK). `tools/eq_paint.py` i `tools/eq_slice.py` mają teraz osobne granice dla każdej kolumny; „+” zawsze 27 px od prawego obrysu.
- Figma zaktualizowana (tło + pozycje kart). `EqBg3` v4 czeka na akceptację uploadu.

## 2026-11-13 · Claude Code (okno ekwipunku: karty w Figmie i Studio)
- Figma (`EquipmentPanel` 23:74): nowy kafelek `EqBg3` v3, skróty statystyk, nowe podpisy, mniejsze `PlusButton`, poprawione pozycje mikstur.
- `EqBg3` v3 wgrany do Roblox (101459179682764) na polecenie Game Directora; zrzut z Play: karty z pełnym obrzeżem, bez ciemnych rogów i plam.

## 2026-11-13 · Claude Code (okno ekwipunku: karty, „+”, zakładki plecaka)
- `tools/eq_paint.py` przepisany: dół kart odtworzony jak w oryginale (beż na całą szerokość, prawa krawędź = odbicie lewej), granatowy pasek nazwy wypełniony medianą czystego granatu (bez plam po cieniu liter). `EqBg3` v3 czeka na akceptację uploadu.
- „+” działa przez serwer: `src/server/StatPoints.server.luau` (RemoteEvent `AddStatPoint`, +1 bez kosztu, cooldown), startowe statystyki w `PlayerStatsDefaults`. Podpisy kart przeliczane (wzory = propozycja).
- Plecak: osobna strona na każdą zakładkę; `Items.category` (Scrap = Amulets). Upuszczenie na innej zakładce odkłada przedmiot na stronę jego kategorii.
- Błąd: atrybuty z `.model.json` (`Attributes`) nie przechodzą przez Rojo, więc karty rozpoznajemy po nazwie (`Card_Strength`).
- Test Play: STR 20→23 (DMG ~13), Scrap widoczny tylko w AMULETS.

## 2026-11-13 · Claude Code (okno ekwipunku: przeciąganie)
- Usunięte złote obramowania slotów i mikstur (hover, zaznaczenie, błyski). Informacja zwrotna: podskok ikony po upuszczeniu, potrząśnięcie przy złym slocie.
- Naprawione przeciąganie: `AbsolutePosition` w Roblox jest liczone pod paskiem Robloxa także przy `IgnoreGuiInset = true`, więc pozycję wejścia porównujemy bez insetu (inset tylko przy rysowaniu przeciąganej ikony). Test myszą w Play: 3/3 scenariusze OK.

## 2026-11-13 · Claude Code (okno ekwipunku, poprawki)
- Upload grafik przez Roblox Studio MCP (`upload_image`, bez klucza Open Cloud): 14 elementów panelu, potem `EqBg3` v2 i `ItemScrap` (po „tak”).
- Poprawki Game Directora: obramowania mikstur w złotym pierścieniu, flaszka skopiowana do 1. slotu, skróty statystyk (STR, CONST, INT, DEX, LUCK, ARMOR; DMG/HP/DEF/CRIT), zaokrąglone kremowe tabliczki kart bez wypalonych „+” (`tools/eq_paint.py`), mniejsze natywne „+” z animacją jak przyciski HUD.
- Przeciąganie przedmiotów w oknie (test: `Scrap`, pikselowa ikona z `tools/make_item_scrap.py`, moduł `src/shared/Items.luau`).
- Test Play w Studio: okno otwiera się z HUD, brak błędów skryptu.

## 2026-11-13 · Claude Code (okno ekwipunku)
- Grafika okna ekwipunku od Game Directora przerobiona na komponenty: usunięty wypalony tekst (`tools/eq_clean_text.py`), pocięcie na tło 2×2 + 10 elementów i `layout.json` (`tools/eq_slice.py`).
- Figma: nowa strona „Equipment Panel”, ramka `EquipmentPanel` (23:74) z natywnym tekstem Luckiest Guy, hotspotami slotów i komponentem `EqPlus`.
- Roblox: `src/gui/EquipmentPanel.model.json` (generator `tools/eq_build_gui.py`), `src/client/EquipmentPanelClient.client.luau` (otwieranie przyciskiem Equipment z HUD). Grafiki w manifeście ze statusem `awaiting_approval`; w `.env` brak `ROBLOX_API_KEY`.
- Mapa teleportacji: 3 warianty z GPT Image (`assets/raw/TeleportMap/v1_*`) i 2 z Nano Banana 2.1 wg promptu Game Directora (`v2_2`, `v2_3`); od teraz generujemy Nano Bananą. Wstrzymane na prośbę Game Directora.
- Notatki: [[Okno ekwipunku]] (nowa), [[Zadania]], [[00 Start]], `DOKUMENTACJA.md`.

## 2026-11-12 · Claude Code (mapa teleportacji)
- Nowa notatka [[Mapa teleportacji]] (propozycja): ekran po kliknięciu Teleport z mapą miasteczka 2D w ramce, piny lokacji, X; zachowanie natywne w Roblox; dwa prompty Higgsfield (ramka z mapą 16:9 oraz pin lokacji).
- Proponowana lista 7 lokacji: Karczma, Arena, Twierdza, Zagroda petów, Targ, Gildia, Portal do lochów.
- Pytanie #7 w [[Pytania otwarte]] (lista lokacji + nazwa cudzej gry w prefiksie [[Style Lock]]). Zaktualizowano: [[Zadania]], [[00 Start]], `DOKUMENTACJA.md`.
- Wcześniej tego dnia: commit `4d65da9` (pipeline `/asset`) wypchnięty na GitHub.

## 2026-11-12 · Claude Code (pipeline assetów w projekcie gry)
- Pipeline przeniesiony z osobnego folderu do projektu gry, żeby `/asset` działał w tym samym oknie: `.claude/skills/asset/`, `tools/*.py` + `tools/resolve_image_id.luau`, `assets/`, `docs/`, `requirements.txt`, `.env` (poza Git).
- Nowy `.mcp.json` z serwerem Higgsfield. `.gitignore`: `assets/raw/`, `__pycache__/`. `CLAUDE.md`: sekcja o pipeline.
- Zasady paczki przeniesione do `references/project-rules.md` z zastrzeżeniem: kanon jest w sejfie, reguła `AssetIds` to propozycja D-011.
- Notatki: [[Pipeline assetów]], [[Zadania]]; `DOKUMENTACJA.md`.

## 2026-11-12 · Claude Code (pipeline assetów)
- Zainstalowano paczkę `blocky-asset-pipeline` (osobny folder, poza repo): zależności Python, `.env` z typem i ID twórcy (bez klucza API), `.mcp.json` przestawiony na oficjalny serwer MCP Roblox Studio zamiast społecznościowego `robloxstudio-mcp`.
- Manifest paczki uzupełniony o ID 10 istniejących assetów (status `in_roblox`), żeby pipeline nie wgrywał ich drugi raz.
- Test: obróbka obrazka i generator `AssetIds` działają. `rembg` blokuje Windows (Inteligentna kontrola aplikacji), więc obróbka używa flood fill.
- Gra jest już opublikowana na Roblox; Studio otwiera wersję z chmury.
- Nowe: [[Pipeline assetów]] (propozycja), D-011 w [[Rejestr decyzji]] (💡). Zaktualizowano: [[Narzędzia]], [[Zadania]], [[Workflow i Git]], [[00 Start]], `DOKUMENTACJA.md`.

## 2026-11-12 · Claude Code (GitHub i dokumentacja)
- Projekt wypchnięty do publicznego repozytorium https://github.com/przeczkowskyy/Blocky-Crycket (gałąź `main`): sejf, kod `src/`, `tools/`, skill, plik `.rbxl` i archiwalny `dashboard/` (bez `node_modules`, bazy danych i `.env`).
- Nowe pliki w repo: `DOKUMENTACJA.md` (pełne podsumowanie projektu: gra, styl, UI, architektura, narzędzia, workflow), `README.md`, `.gitignore`, `.gitattributes`. `CLAUDE.md`: sekcja Git.
- Nowa notatka [[Workflow i Git]] (propozycja). Nowe pytanie w [[Pytania otwarte]] (#6: Diamenty a Magiczne Kryształy).
- Zaktualizowano: [[Narzędzia]], [[Roadmapa]] (ekran ładowania ✓), [[Ekran ładowania]] (zapis `.rbxl` potwierdzony), [[Zadania]], [[00 Start]].

## 2026-11-11 · Claude Code (HUD: większe przyciski)
- Przyciski HUD powiększone ze 128 do 150 px @1080p (+17%; +25% dałoby 160 px, czyli rozmiar sprzed zmian). Odstęp 18 → 21 px, dół kolumny bez zmian.
- Plik: `src/gui/HUD.model.json`. Notatki: [[HUD]].

## 2026-11-11 · Claude Code (HUD z Figmy)
- [[HUD]] zbudowany według Figmy (9:1571 / 14:145 / 9:1570): panel gracza (ramka portretu, pasek XP, poziom, złoto, diamenty) + 6 przycisków (Teleport, Equipment, Pets / Quests, Shop, Guilds).
- Przyciski zmniejszone ze 160 do 128 px i przesunięte niżej (dół 160 px od dołu, jak w Figmie).
- HUD ukryty do końca [[Ekran ładowania|ekranu ładowania]]: `LoadingClient` ustawia atrybut `LoadingDone`.
- Nowe pliki: `src/gui/HUD.model.json`, `src/client/HUDClient.client.luau`, `src/server/PlayerStatsDefaults.server.luau` (atrybuty Level/XP/XPMax/Gold/Gems, placeholder do DataStore).
- Test Play Solo: OK (wejście, animacje statów, kliknięcia). Telefon niesprawdzony.
- Konflikt z kanonem (5 zakładek vs 6 przycisków) → [[Pytania otwarte]] #5.
- Notatki: [[HUD]], [[Ekran ładowania]], [[Zadania]], [[Pytania otwarte]].

## 2026-11-11 · Claude Code (ekran ładowania: opóźnienie i treści)
- Sprawdzono: tekst pod paskiem to `TextLabel` (`Tip` + `TipShadow`), jedynym obrazem jest tło.
- `LoadingClient`: minimalny czas napełniania 4,5 s z losowymi przystankami; rotacja treści co 2,6 s z płynnym przejściem; 19 tekstów w 3 kategoriach (WSKAZÓWKA / PLOTKA Z KARCZMY / CIEKAWOSTKA), losowanych bez powtórek.
- Zaktualizowano skrypt w Studio i `tools/studio/build_loading_screen.luau`. Play Solo bez błędów.
- Notatki: [[Ekran ładowania]].

## 2026-11-11 · Claude Code (ekran ładowania)
- [[Ekran ładowania]] zbudowany w Roblox Studio przez MCP: `ReplicatedFirst.LoadingScreen` (key-art `rbxassetid://129202798952612` + natywny pasek postępu z Figmy, node 2:2 / 2:75) i `ReplicatedFirst.LoadingClient` (preload, procenty, rotujące wskazówki, fade-out).
- `tools/studio/build_loading_screen.luau`: wpisane ID tła.
- Podgląd zgodny z Figmą, Play Solo bez błędów skryptu.
- Notatki: [[Ekran ładowania]], [[Zadania]].

## 2026-11-11 · Claude Code
- Utworzono strukturę sejfu `B&C` jako mózgu projektu ([[Rejestr decyzji#D-008 Sejf Obsidian `B&C` jest mózgiem projektu|D-008]]).
- Oryginalną dokumentację przeniesiono z `docs/` do [[Dokumentacja projektu (oryginał)]].
- Wiedzę z dokumentacji rozpisano na notatki: Gra, Postacie, Styl, UI, Technika, Produkcja.
- Elementy spoza kanonu oznaczono jako `propozycja`.

## 2026-11-11 · Claude Code (wcześniej tego dnia)
- Skonfigurowano Rojo (`default.project.json`, `src/server|client|shared|gui`).
- Dodano skill `figma-to-roblox` ([[Pipeline Figma → Roblox]]).
- Zbudowano dashboard `dashboard/`. **Projekt porzucony** na rzecz sejfu Obsidian.
