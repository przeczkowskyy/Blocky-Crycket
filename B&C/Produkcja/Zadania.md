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
- [ ] Szara pętla MVP: plac → karczma → walka 10 s → łup → statystyki ([[Ocena potencjału gry]], tydzień 1) · #wysoki

## 📥 Backlog
- [ ] Postęp EXP i Level w HUD (animacja level-up „POW!”) · #średni
- [ ] [[Ekran ładowania]]: test na prawdziwym serwerze / telefonie (w Studio ekran znika po ~1 s) · #średni
- [ ] ViewportFrame z modelem [[Rycerz|Rycerza]] / [[Kot-Mag|Kota-Maga]] · #średni
- [ ] Podgląd peta podążającego za graczem ([[Pety]]) · #niski
- [ ] Usunąć pliki testowe Rojo: `Hello.server.luau`, `Hello.client.luau`, `FigmaTest.model.json` · #niski
- [ ] Decyzja po previzie cutscenki (`swiat/test_cutscenki/cutscenka_v1.mp4`): walki jako ekran 2D czy cutscenka 3D? · #średni
- [ ] Test cutscenki w samym Roblox: 2 postacie R15, 3 animacje, 8–10 s, kamera skryptowa, przycisk „pomiń”; pomiar na tanim telefonie (po decyzji wyżej) · #średni
- [ ] Zrzuty ze Studio do migawki dema: okno Studio musi być widoczne; przycisk „Nowa migawka” w [[Panel zespołu|panelu]] · #średni
- [ ] Łańcuch narzędzi: Rokit z przypiętymi wersjami, aktualizacja Rojo do 7.7.1 u obu osób naraz ([[Narzędzia i skille do Roblox]]) · #średni
- [ ] Telemetria gry i analityka (AnalyticsService + klucz Open Cloud tylko do odczytu) → karty w [[Panel zespołu|panelu]] · #średni
- [ ] [[Panel zespołu|Panel]]: zakładka Assety z `assets/manifest.json` (miniatury, statusy, zgody) — wsparcie dla [[Pipeline assetów]] · #niski
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
- [x] 2026-11-12: Przegląd bezpieczeństwa [[Panel zespołu|panelu]]: 14 potwierdzonych uwag poprawionych (klucz lokalny, konfiguracja wspólna bez ustawień bezpieczeństwa, limity czasu), przełącznik „Agent z telefonu”, 76 testów
- [x] 2026-11-12: Pipeline assetów przeniesiony do projektu gry (działa w jednym oknie Claude Code)
- [x] 2026-11-12: Instalacja [[Pipeline assetów|pipeline'u assetów]]: zależności, `.env` (bez klucza), oficjalny Studio MCP, manifest z ID istniejących assetów
- [x] 2026-11-12: Projekt na GitHubie (publiczne repo `przeczkowskyy/Blocky-Crycket`) + `DOKUMENTACJA.md`, zob. [[Workflow i Git]]
- [x] 2026-11-11: [[HUD]] z Figmy: panel gracza (XP, poziom, złoto, diamenty) + 6 przycisków, pokazywany po ekranie ładowania
- [x] 2026-11-11: [[Ekran ładowania]] w Roblox: key-art + natywny pasek z Figmy w `ReplicatedFirst` (skrypt `tools/studio/build_loading_screen.luau`)
- [x] 2026-11-11: Synchronizacja Rojo (`default.project.json`), zob. [[Rojo i struktura projektu]]
- [x] 2026-11-11: Pipeline Figma → Roblox, zob. [[Pipeline Figma → Roblox]]
- [x] 2026-11-11: Sejf Obsidian jako mózg projektu, zob. [[Jak prowadzimy sejf]]
