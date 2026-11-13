---
status: kanon
tags: [produkcja, zadania]
---
# Zadania

> Format: `- [ ] Zadanie — kontekst · #priorytet`. Ukończone przenoś do sekcji „Zrobione” z datą.

## 🔥 Teraz (Sprint 1 — fundament Fazy 1)
- [ ] Przenieść istniejące skrypty z `.rbxl` do `src/` (Studio → Save to File), bo inaczej Claude ich nie widzi · #wysoki
- [ ] Uporządkować hierarchię StarterGui: MainHUD, LoadingScreenGui, TavernQuestGui, HeroSelectorGui, PetGui, InventoryGui · #wysoki
- [ ] Moduł statystyk gracza (HP / Mana / EXP / Level) z replikacją do klienta, jako źródło danych dla [[HUD]] · #wysoki
- [ ] Pasek HP w HUD (ukośny, czerwony, animacja TweenService). Zależy od dwóch zadań wyżej · #wysoki
- [ ] [[Okno Karczmy]]: tablica questów. Najpierw ustalić, gdzie jest istniejące drzewo · #wysoki
- [ ] [[HUD]]: test na telefonie (Device Emulator) i ręczny test hovera · #wysoki
- [ ] Decyzja: przyciski HUD z Figmy vs kanon ([[Pytania otwarte]] #5) · #wysoki
- [ ] [[Pipeline assetów]]: wpisać klucz Open Cloud do `.env`, zalogować Higgsfield przez `/mcp`, sprawdzić połączenia · #wysoki
- [ ] Decyzja D-011: pipeline assetów i moduł `AssetIds` ([[Rejestr decyzji]]) · #średni
- [ ] Decyzje po rozmowie 12.11: pytania 7–14 w [[Pytania otwarte]] i propozycje D-012–D-018 w [[Rejestr decyzji]] · #wysoki
- [ ] Obejrzeć demo `Workspace/DemoLesnaBaza` w Studio i w [[Panel zespołu|panelu]]: styl, skala, co poprawić ([[Klocki — Blender i Roblox]]) · #wysoki
- [ ] Szara pętla MVP: plac → karczma → walka 10 s → łup → statystyki ([[Ocena potencjału gry]], tydzień 1) — wersja sprzed diagnozy; propozycja v2 zamienia ją na szary prototyp BONK-a (pytanie 16) · #wysoki
- [ ] Wspólne wdrożenie panelu jako miejsca pracy: decyzja z pytania 23, potem włączenie zapisu (`"zapis_sejfu": true` w konfiguracji lokalnej) i link z kluczem Game Directora ([[Panel zespołu]]) · #wysoki
- [ ] Import siatek postaci do Studio: zatwierdzić folder `swiat/postacie/wynik` w Assistant → Settings → MCP Permissions, potem próba na Rycerzu (skala, kierunek, kolory, kości) · #średni
- [ ] Decyzja z pytania 24: droga postaci do gry i właściciel animacji ([[Postacie 3D — Blender i Roblox]]) · #średni
- [ ] Decyzje dnia 0 po nocnej diagnozie: pytania 16–21 w [[Pytania otwarte]] i 15 decyzji w [[Karta ocen v2 i plan sprawdzenia]] · #wysoki
- [ ] Makieta siatki: 12 kafelków z prawdziwą konkurencją, co najmniej 40 graczy 16+ — test haczyka przed prototypem ([[Karta ocen v2 i plan sprawdzenia]]) · #wysoki
- [ ] Szary prototyp BONK-a z botem-klikaczem (bramka B1, [[Systemy gry v2]]) — po decyzji z pytania 16 · #wysoki

## 📥 Backlog
- [ ] [[Okno ekwipunku]]: test na telefonie; potem prawdziwe przedmioty i statystyki z serwera · #wysoki
- [ ] [[Mapa teleportacji]]: wygenerować mapę z ramką i 7 pinów (prompty w notatce), potem `TeleportMapGui` i teleport przez RemoteEvent. Najpierw potwierdzić listę lokacji ([[Pytania otwarte]] #25) · #średni
- [ ] Postęp EXP i Level w HUD (animacja level-up „POW!”) · #średni
- [ ] [[Ekran ładowania]]: test na prawdziwym serwerze / telefonie (w Studio ekran znika po ~1 s) · #średni
- [ ] ViewportFrame z modelem [[Rycerz|Rycerza]] / [[Kot-Mag|Kota-Maga]] · #średni
- [ ] Podgląd peta podążającego za graczem ([[Pety]]) · #niski
- [ ] Usunąć pliki testowe Rojo: `Hello.server.luau`, `Hello.client.luau`, `FigmaTest.model.json` · #niski
- [ ] Decyzja po previzie i teście cutscenki: walki jako ekran 2D, cutscenka 3D czy — jak proponuje D-024 — cutscenka tylko przy bossie? Test do obejrzenia w Studio: Play, na wschód od placu do świecącego słupa, klawisz E · #średni
- [ ] Pomiar cutscenki i walki na tanim telefonie (≥ 30 klatek/s) — wymaga testowej publikacji albo urządzenia; na komputerze zmierzone · #średni
- [ ] Usunąć prototyp `Workspace/TestWalki` przed publikacją miejsca: `python swiat/test_walki_roblox/zbuduj.py --usun` · #średni
- [ ] Łańcuch narzędzi: `rokit.toml` jest w repo (Rojo 7.6.1); każda osoba instaluje Rokit u siebie (agent nie mógł — instalator zablokowany); potem wspólne podniesienie Rojo do 7.7.1 ([[Narzędzia i skille do Roblox]]) · #średni
- [ ] Włączyć telemetrię gry (decyzja D-023): skrypt startowy z `Telemetria.start()`, publikacja, klucz Open Cloud tylko do odczytu wpisany lokalnie ([[Telemetria gry]]) · #średni
- [ ] Po potwierdzeniu D-027: przepiąć szablony promptów skilla `/asset` na [[Instrukcja promptów — Glossy Ink]] (dziś mają starszy opis stylu i ciemnogranatowe tło ramek) · #średni
- [ ] [[Panel zespołu|Panel]]: lustro tylko-do-odczytu na GitHub Pages (właściciel repo włącza Pages → Source: GitHub Actions, potem uruchamia workflow „Panel — lustro”) · #niski

## 🎨 Assety do stworzenia
- [ ] Rycerz (3D) · [ ] Kot-Mag (3D) · [ ] Karczmarz (3D)
- [ ] Pies · [ ] Niebieski slime · [ ] Czerwony smok (3D)
- [x] Ikona Złota · [x] Ikona Kryształu (diament) · [x] Ikony przycisków HUD (6, z Figmy) · [x] Ramka portretu
- [x] Ilustracja ekranu ładowania (`rbxassetid://129202798952612`) · [x] Logo z koroną (w key-arcie)
- [ ] Budynek Karczmy · [ ] Beczka do rozbijania · [ ] Dropper Twierdzy (3D)

## ✅ Zrobione
- [x] 2026-11-12: Rozmowa o grze spisana i skomentowana: [[Rozmowa 2026-11-12 — zapis ustaleń]], [[Propozycje z rozmowy 2026-11-12]], [[Ocena potencjału gry]]
- [x] 2026-11-12: Badania: [[Rynek Roblox i konkurencja]], [[Shakes & Fidget — rozbiór mechanik]], [[Retencja i monetyzacja — co wolno i co działa]], [[Styl UI gier Roblox]], [[Narzędzia i skille do Roblox]], [[Technika gry — serwery, światy, walki]]
- [x] 2026-11-12: [[Panel zespołu]] (`panel/`) i demo mapy „Leśna baza startowa” w Blenderze i w Studio ([[Klocki — Blender i Roblox]])
- [x] 2026-11-12: Previz cutscenki auto-walki 3D w Blenderze (9 s: cios, kontra z blokiem, krytyk, łup) — prośba z rozmowy [17:08]; `swiat/test_cutscenki/`
- [x] 2026-11-13: Diagnoza pomysłu i poprawiona koncepcja: [[Diagnoza pomysłu 2026-11-13]], [[Myśl przewodnia v2]], [[Systemy gry v2]], [[Psychologia gracza v2]], [[Karta ocen v2 i plan sprawdzenia]], [[Specyfikacja v2.1 — Krzywa Banda]]
- [x] 2026-11-13: Test cutscenki auto-walki w samym Roblox (`swiat/test_walki_roblox/`, `Workspace/TestWalki`): 2 postacie R15, kamera skryptowa, POMIŃ, panel wyniku; zweryfikowany niezależnie (42 sprawdzenia w trybie Play)
- [x] 2026-11-13: [[Panel zespołu|Panel]]: zakładka Assety (rejestr grafik z `assets/manifest.json`) i sekcja „Telemetria gry” w Analityce; kod telemetrii w `src/server/Telemetria` ([[Telemetria gry]]); 141 testów
- [x] 2026-11-13: Postacie, pety i ekwipunek z kodu (`swiat/postacie/`): 6 postaci, 3 zestawy, 8 broni, 20 klipów; w Studio jako postacie z klocków w `Workspace/TestPostaci`, animacje sprawdzone w Edit i Play; manekiny z zestawami, przymierzalnia na awatarze gracza i pety idące za graczem ([[Postacie 3D — Blender i Roblox]])
- [x] 2026-11-13: [[Panel zespołu|Panel]]: zapis do sejfu z panelu (odpowiedzi, zadania, decyzje z kluczem Game Directora) — gotowy, po niezależnym przeglądzie, wyłączony do decyzji; 216 testów
- [x] 2026-11-13: Mapa v2 „Krzywe Miasteczko” w Studio po rundzie poprawek; kontrola kolizji ([[Klocki — Blender i Roblox]])
- [x] 2026-11-13: Migawka dema ze zrzutami z prawdziwego Roblox Studio (panel → Podgląd 3D)
- [x] 2026-11-13: Biblioteka map v2 (`swiat/biblioteka/`: krzywe bryły, obrys tuszem, podgląd w Blenderze) i `rokit.toml`
- [x] 2026-11-12: Przegląd bezpieczeństwa [[Panel zespołu|panelu]]: 14 potwierdzonych uwag poprawionych (klucz lokalny, konfiguracja wspólna bez ustawień bezpieczeństwa, limity czasu), przełącznik „Agent z telefonu”, 76 testów
- [x] 2026-11-12: Pipeline assetów przeniesiony do projektu gry (działa w jednym oknie Claude Code)
- [x] 2026-11-12: Instalacja [[Pipeline assetów|pipeline'u assetów]]: zależności, `.env` (bez klucza), oficjalny Studio MCP, manifest z ID istniejących assetów
- [x] 2026-11-12: Projekt na GitHubie (publiczne repo `przeczkowskyy/Blocky-Crycket`) + `DOKUMENTACJA.md`, zob. [[Workflow i Git]]
- [x] 2026-11-11: [[HUD]] z Figmy: panel gracza (XP, poziom, złoto, diamenty) + 6 przycisków, pokazywany po ekranie ładowania
- [x] 2026-11-11: [[Ekran ładowania]] w Roblox: key-art + natywny pasek z Figmy w `ReplicatedFirst` (skrypt `tools/studio/build_loading_screen.luau`)
- [x] 2026-11-11: Synchronizacja Rojo (`default.project.json`), zob. [[Rojo i struktura projektu]]
- [x] 2026-11-11: Pipeline Figma → Roblox, zob. [[Pipeline Figma → Roblox]]
- [x] 2026-11-11: Sejf Obsidian jako mózg projektu, zob. [[Jak prowadzimy sejf]]
