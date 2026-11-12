---
status: kanon
tags: [produkcja, decyzje]
---
# Rejestr decyzji

Tylko decyzje **✅ zatwierdzone** są obowiązujące. Zatwierdzonej decyzji się nie przepisuje: dodaje się nową, która ją **zastępuje**, i zostawia ślad.

Statusy: ✅ zatwierdzona · 🕓 do decyzji · 💡 propozycja · ❌ odrzucona · ♻️ zastąpiona

---

### D-001 Obowiązkowy prefiks Style Lock
✅ zatwierdzona · styl · źródło: dokumentacja
Każdy prompt 2D/UI zaczyna się od prefiksu z [[Style Lock]].

### D-002 Hybryda trzech estetyk
✅ zatwierdzona · styl · źródło: dokumentacja
Komiks/pop-art Shakes & Fidget + Roblox voxel/low-poly + pixel-art ikon. Zob. [[Kierunek artystyczny]].

### D-003 Projekty głównych postaci
✅ zatwierdzona · styl · źródło: dokumentacja
[[Rycerz]], [[Kot-Mag]], [[Pety]] (pies, slime, smok).

### D-004 Aktywna rozgrywka zamiast pasków czasu
✅ zatwierdzona · game design · źródło: dokumentacja
Misje w instancjonowanych mini-dungeonach (walka 3D lub clicker), bez biernego czekania.

### D-005 Priorytet: Faza 1 — Frontend
✅ zatwierdzona · roadmapa · źródło: dokumentacja
Najpierw logika UI, ViewportFrame postaci, ożywienie HUD. Bez restartu projektu i bez przeprojektowywania zatwierdzonych elementów.

### D-006 Mapowanie Rojo z `$ignoreUnknownInstances`
🕓 do decyzji · technika · zaproponował: Claude Code
Zob. [[Rojo i struktura projektu]]. Dotychczasowa zawartość `.rbxl` jest bezpieczna.

### D-007 GUI z Figmy jako pliki `.model.json`
🕓 do decyzji · technika · zaproponował: Claude Code
Jedna ramka Figmy to jeden ScreenGui w `src/gui`, a logika w `src/client`. Zob. [[Pipeline Figma → Roblox]].

### D-008 Sejf Obsidian `B&C` jest mózgiem projektu
✅ zatwierdzona · narzędzia · 2026-11-11 · zdecydował: Game Director
Cała wiedza o projekcie żyje w tym sejfie. Pomysł dashboardu z agentami AI został porzucony. Zob. [[Jak prowadzimy sejf]].

### D-009 Karczma — poziomy misji i Energia
💡 propozycja · game design · źródło: wcześniejsza specyfikacja
Trzy misje: Łatwa / Średnia / Epicki Boss. Misje zużywają Energię odnawianą napitkiem. Kanon mówi tylko o trzech misjach. Zob. [[Karczma (Questy)]].

### D-010 Fazy roadmapy 2–6
💡 propozycja · roadmapa · źródło: master prompt
Zob. [[Roadmapa]].

### D-011 Pipeline assetów `/asset` i moduł `AssetIds`
💡 propozycja · technika / grafika · 2026-11-12 · źródło: paczka `blocky-asset-pipeline`
Nowe grafiki powstają przez skill `/asset`: Higgsfield → obróbka → Figma → akceptacja Game Directora → upload przez Roblox Open Cloud → wpis w manifeście. Zasady paczki: asset ID w kodzie gry tylko przez moduł `AssetIds` (nie wpisane na sztywno), zero tekstu w grafikach AI (napisy natywnie). Obecny [[HUD]] i [[Ekran ładowania]] mają ID wpisane na sztywno, a przyciski HUD mają wypalone napisy, więc przyjęcie decyzji oznacza ich przepięcie. Zob. [[Pipeline assetów]].
Powiązane: [[Narzędzia]], [[Style Lock]]

### D-012 Panel zespołu jako okno na sejf
💡 propozycja · narzędzia · 2026-11-12 · zaproponował: Karol (przez Claude Code)
Lokalny panel `panel/` pokazuje sejf (decyzje, zadania, roadmapę), raporty z wdrożeń z akceptacją, podgląd 3D mapy i agenta na subskrypcji Claude Code. Nie trzyma własnej kopii wiedzy, więc nie narusza D-008 — uściśla jej zdanie o porzuconym dashboardzie. Zob. [[Panel zespołu]], [[Pytania otwarte]] #11.

### D-013 Pętla bez czekania: walka od razu, liczniki tylko równolegle
💡 propozycja · game design · 2026-11-12 · źródło: rozmowa 12.11 i rekomendacja Claude Code
Quest zaczyna się walką (8–15 s), a rozgłos strefy podnosi nagrody. Długie liczniki (jajko, wyprawa najemnika, budowa) działają tylko w slotach równoległych. Rozwija D-004, nie zastępuje jej. Zob. [[Propozycje z rozmowy 2026-11-12]], [[Pytania otwarte]] #7.

### D-014 MVP jednej pętli i test popytu przed rozbudową
💡 propozycja · roadmapa · 2026-11-12 · źródło: [[Ocena potencjału gry]]
Cztery tygodnie: plac → karczma → walka → łup → statystyki, jeden loch, pierwszy pet, pierwszy budynek twierdzy; publikacja i decyzja na podstawie danych (powroty następnego dnia 15–20%). Pełna twierdza, arena i gildie dopiero po tej bramce.

### D-015 Monetyzacja bez płatnej losowości
💡 propozycja · monetyzacja · 2026-11-12 · źródło: [[Retencja i monetyzacja — co wolno i co działa]]
Za Robuxy sprzedajemy wygodę, sloty, kosmetykę i VIP. Losowania (sklep, koło, jajka) tylko za walutę i tokeny zdobywane w grze. Bez symulowanego hazardu i bez cudzych marek w nazwach. Zob. [[Pytania otwarte]] #12.

### D-016 Hub na 16–20 graczy, walki liczone na serwerze
💡 propozycja · technika · 2026-11-12 · źródło: [[Technika gry — serwery, światy, walki]]
Serwer huba na 16–20 osób; wydarzenia „dla wszystkich” przez wspólny stan serwerów. Każdą walkę liczy serwer, a klient ją odtwarza (ekran 2D albo cutscenka 3D — po teście).

### D-017 Mapy z klocków: jeden plik `czesci.json` dla Blendera, Studio i panelu
💡 propozycja · technika / 3D · 2026-11-12 · zaproponował: Claude Code
Zob. [[Klocki — Blender i Roblox]]. Demo: `Workspace/DemoLesnaBaza`.

### D-018 Styl UI: „bubbly cartoon” zamiast pixel-artu
💡 propozycja · styl · 2026-11-12 · źródło: [[Styl UI gier Roblox]]
Wdrożone grafiki HUD pasują do standardu Roblox, a przeczą zapisom o pixel-arcie i płaskim designie w [[Kierunek artystyczny]] i [[Style Lock]]. Propozycja: zaktualizować kanon do wdrożonego stylu, a napisy przenieść z grafik do tekstu. Dotyka D-001 i D-002, więc wymaga nowej decyzji, która je zastąpi. Zob. [[Pytania otwarte]] #10.

---
*Nowa decyzja: skopiuj szablon [[Decyzja]] (folder Szablony) albo dopisz sekcję `### D-0XX` na końcu.*
