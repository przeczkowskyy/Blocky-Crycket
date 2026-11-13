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

## 📥 Backlog
- [ ] [[Okno ekwipunku]]: test na telefonie; potem prawdziwe przedmioty i statystyki z serwera · #wysoki
- [ ] [[Mapa teleportacji]]: wygenerować mapę z ramką i 7 pinów (prompty w notatce), potem `TeleportMapGui` i teleport przez RemoteEvent. Najpierw potwierdzić listę lokacji ([[Pytania otwarte]] #7) · #średni
- [ ] Postęp EXP i Level w HUD (animacja level-up „POW!”) · #średni
- [ ] [[Ekran ładowania]]: test na prawdziwym serwerze / telefonie (w Studio ekran znika po ~1 s) · #średni
- [ ] ViewportFrame z modelem [[Rycerz|Rycerza]] / [[Kot-Mag|Kota-Maga]] · #średni
- [ ] Podgląd peta podążającego za graczem ([[Pety]]) · #niski
- [ ] Usunąć pliki testowe Rojo: `Hello.server.luau`, `Hello.client.luau`, `FigmaTest.model.json` · #niski

## 🎨 Assety do stworzenia
- [ ] Rycerz (3D) · [ ] Kot-Mag (3D) · [ ] Karczmarz (3D)
- [ ] Pies · [ ] Niebieski slime · [ ] Czerwony smok (3D)
- [x] Ikona Złota · [x] Ikona Kryształu (diament) · [x] Ikony przycisków HUD (6, z Figmy) · [x] Ramka portretu
- [x] Ilustracja ekranu ładowania (`rbxassetid://129202798952612`) · [x] Logo z koroną (w key-arcie)
- [ ] Budynek Karczmy · [ ] Beczka do rozbijania · [ ] Dropper Twierdzy (3D)

## ✅ Zrobione
- [x] 2026-11-12: Pipeline assetów przeniesiony do projektu gry (działa w jednym oknie Claude Code)
- [x] 2026-11-12: Instalacja [[Pipeline assetów|pipeline'u assetów]]: zależności, `.env` (bez klucza), oficjalny Studio MCP, manifest z ID istniejących assetów
- [x] 2026-11-12: Projekt na GitHubie (publiczne repo `przeczkowskyy/Blocky-Crycket`) + `DOKUMENTACJA.md`, zob. [[Workflow i Git]]
- [x] 2026-11-11: [[HUD]] z Figmy: panel gracza (XP, poziom, złoto, diamenty) + 6 przycisków, pokazywany po ekranie ładowania
- [x] 2026-11-11: [[Ekran ładowania]] w Roblox: key-art + natywny pasek z Figmy w `ReplicatedFirst` (skrypt `tools/studio/build_loading_screen.luau`)
- [x] 2026-11-11: Synchronizacja Rojo (`default.project.json`), zob. [[Rojo i struktura projektu]]
- [x] 2026-11-11: Pipeline Figma → Roblox, zob. [[Pipeline Figma → Roblox]]
- [x] 2026-11-11: Sejf Obsidian jako mózg projektu, zob. [[Jak prowadzimy sejf]]
