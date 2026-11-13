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

### D-019 Myśl przewodnia v2: „krzywy montaż”
💡 propozycja · game design · 2026-11-13 · źródło: [[Diagnoza pomysłu 2026-11-13]] i panel koncepcji (Claude Code u Karola)
Gra opisana jednym zdaniem o czynności — „Rozbij potwora na klocki, a kot złoży go krzywo, z błędem, który daje moc” — zamiast porównania do gry-inspiracji i listy czterech gatunków. Duet z logo staje się maskotkami (Crycket — kot składający potwory, Blocky — strażnik placu), a gracz gra własnym awatarem. Zmieniałaby [[Koncepcja i Core Loop]] i role z D-003 (wygląd postaci bez zmian). Zob. [[Myśl przewodnia v2]], [[Pytania otwarte]] #16.

### D-020 Pętla v2: BONK, banda i Album; dwa etapy z bramkami pomiaru
💡 propozycja · game design / roadmapa · 2026-11-13 · źródło: [[Systemy gry v2]]
Rdzeń: jeden przycisk BONK w otwartej strefie (wybity potwór przewraca stado), banda dobija, Finał, Album z jawnymi progami zamiast losowania; mini-dungeon z D-004 jako „Spiżarnia”. Budowa w dwóch etapach (A: rdzeń i pierwsze 10 minut, B: wersja do uczciwego pomiaru) z bramkami B0–B4. Rozwija D-013, zastępowałaby D-014. Zob. [[Karta ocen v2 i plan sprawdzenia]], [[Specyfikacja v2.1 — Krzywa Banda]].

### D-021 Gra bez alkoholu, bez losowych nagród i bez waluty za Robuxy
💡 propozycja · zgodność / monetyzacja · 2026-11-13 · źródło: [[Diagnoza pomysłu 2026-11-13]]
Roblox dopuszcza odniesienia do alkoholu tylko w grach 18+, więc karczma zostaje jadłodajnią („Zupa u Chochli”), a kufel — także w ikonie HUD i żartach ekranu ładowania — zastępuje kociołek. Żadnej losowej nagrody (także darmowej) i żadnej waluty kupowanej za Robuxy; waluty to Złoto i Magiczne Kryształy, Diamenty znikają. Zaostrza D-015; dotyczy pytań #6, #8, #12 i #19. Zob. [[Psychologia gracza v2]].

### D-022 Publiczność startowa 16+ i miękka premiera
💡 propozycja · rynek / roadmapa · 2026-11-13 · źródło: [[Diagnoza pomysłu 2026-11-13]]
Nową grę widzą najpierw tylko gracze 16+ ze sprawdzonym wiekiem, a młodsi dopiero po progu odtworzeń. Haczyk, miniatury i pierwszy test popytu projektujemy więc pod starszych graczy; grudzień to miękka premiera bez decyzji „zakończyć”, a decyzje zapadają na dwóch ważnych kohortach po Etapie B. Zob. [[Karta ocen v2 i plan sprawdzenia]], [[Pytania otwarte]] #18.

### D-023 Telemetria gry i jej odczyt w panelu
💡 propozycja · technika · 2026-11-13 · zaproponował: Karol (przez Claude Code)
Moduł `src/server/Telemetria` (bezwładny do czasu włączenia, bez danych osobowych: sesje, gracze naraz, wydane Robuxy, błędy, serwery) i sekcja „Telemetria gry” w Analityce panelu. Włączenie wymaga skryptu startowego w grze, publikacji i klucza Open Cloud tylko do odczytu, trzymanego lokalnie. Zob. [[Telemetria gry]], [[Pytania otwarte]] #13 i #20.

### D-024 Cutscenka walki 3D jako nagroda, nie jako rdzeń
💡 propozycja · game design / technika · 2026-11-13 · źródło: test w Roblox (`swiat/test_walki_roblox/`)
Test w samym Roblox (kontener `Workspace/TestWalki`, 9 sekund, serwer liczy — klient odtwarza) pokazał, że cutscenka jest wykonalna i tania dla procesora na komputerze (telefon niezmierzony). Diagnoza wskazuje jednak, że oglądanie walki nie wytrzyma powtórek, więc cutscenka zostaje najwyżej przy bossie. Prototyp trzeba usunąć ze wspólnego miejsca przed publikacją (`python swiat/test_walki_roblox/zbuduj.py --usun`). Dotyczy D-016.

### D-025 Mapy v2: biblioteka krzywych brył i „Krzywe Miasteczko”
💡 propozycja · technika / 3D · 2026-11-13 · zaproponował: Karol (przez Claude Code)
`swiat/biblioteka/` (układy lokalne do pochylonych brył, obrys „tuszem”, podgląd w Blenderze) i mapa `swiat/krzywe_miasteczko/` w stylu komiksowym. Według propozycji v2 miasteczko-hub wchodzi do gry dopiero po bramce D7 — do tego czasu to demo stylu i poligon narzędzi. Rozwija D-017. Zob. [[Klocki — Blender i Roblox]].

### D-026 Łańcuch narzędzi: Rokit z przypiętym Rojo 7.6.1
💡 propozycja · narzędzia · 2026-11-13 · źródło: [[Narzędzia i skille do Roblox]]
Plik `rokit.toml` w repozytorium przypina Rojo 7.6.1 (wersja z kanonu). Rokit instaluje każda osoba u siebie; podniesienie Rojo do 7.7.1 robimy u obu osób naraz, razem z pluginem w Studio.

### D-027 Instrukcja promptów „Glossy Ink” zastępuje prefiks Style Lock
🕓 do decyzji · styl / grafika · 2026-11-13 · źródło: dokument Game Directora przekazany przez Karola
Każdy prompt graficzny składa się ze stałego początku „Glossy Ink” (odwołanie do własnego obrazu referencyjnego, bez cudzej nazwy), zmiennego środka, stałego końca i osobnego negative promptu; do tego zasady zamkniętych krawędzi, pustych kontenerów, okien ze statystykami i map izometrycznych. Zastąpiłaby prefiks z D-001 i zapisy o pixel-arcie oraz płaskim interfejsie z D-002; zgodna z propozycją D-018. Czeka tylko na formalne potwierdzenie Game Directora; do tego czasu nowe prompty piszemy już według niej. Zob. [[Instrukcja promptów — Glossy Ink]], [[Pytania otwarte]] #22.

---
*Nowa decyzja: skopiuj szablon [[Decyzja]] (folder Szablony) albo dopisz sekcję `### D-0XX` na końcu.*
