---
status: kanon
tags: [produkcja, decyzje]
---
# Rejestr decyzji

Tylko decyzje **✅ zatwierdzone** są obowiązujące. Zatwierdzonej decyzji się nie przepisuje: dodaje się nową, która ją **zastępuje**, i zostawia ślad.

Statusy: ✅ zatwierdzona · 🕓 do decyzji · 💡 propozycja · ❌ odrzucona · ♻️ zastąpiona

Zatwierdza Karol albo Paweł — wystarczy decyzja jednego (D-030). Wiersz statusu niesie podpis `zdecydował: <imię> <data>`, a ślad trafia też do [[Dziennik zmian]].

---

### D-001 Obowiązkowy prefiks Style Lock
♻️ zastąpiona · styl · źródło: dokumentacja · zastąpiona przez D-027 (2026-11-13)
Każdy prompt 2D/UI zaczyna się od prefiksu z [[Style Lock]].

### D-002 Hybryda trzech estetyk
✅ zatwierdzona · styl · źródło: dokumentacja
Komiks/pop-art Shakes & Fidget + Roblox voxel/low-poly + pixel-art ikon. Zob. [[Kierunek artystyczny]].
Od 2026-11-13 część o pixel-arcie ikon i płaskim interfejsie zastępuje D-027; komiks/pop-art i voxel/low-poly obowiązują dalej.

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
✅ zatwierdzona · technika · zaproponował: Claude Code · zdecydował: Karol 2026-11-13
Zob. [[Rojo i struktura projektu]]. Dotychczasowa zawartość `.rbxl` jest bezpieczna.
Uzasadnienie — Karol, 2026-11-13: zgoda w rozmowie z Claude Code po wyjaśnieniu, że to zasada techniczna (Rojo wgrywa kod z plików i nie kasuje w Studio tego, czego w plikach nie ma) i w kanonie gry nic nie zmienia.

### D-007 GUI z Figmy jako pliki `.model.json`
✅ zatwierdzona · technika · zaproponował: Claude Code · zdecydował: Karol Balucki 2026-11-13
Jedna ramka Figmy to jeden ScreenGui w `src/gui`, a logika w `src/client`. Zob. [[Pipeline Figma → Roblox]].

### D-008 Sejf Obsidian `B&C` jest mózgiem projektu
✅ zatwierdzona · narzędzia · 2026-11-11 · zdecydował: Game Director
Cała wiedza o projekcie żyje w tym sejfie. Pomysł dashboardu z agentami AI został porzucony. Zob. [[Jak prowadzimy sejf]].

### D-009 Karczma — poziomy misji i Energia
❌ odrzucona · game design · źródło: wcześniejsza specyfikacja · zdecydował: Karol Balucki 2026-11-13
Trzy misje: Łatwa / Średnia / Epicki Boss. Misje zużywają Energię odnawianą napitkiem. Kanon mówi tylko o trzech misjach. Zob. [[Karczma (Questy)]].
Uzasadnienie — Karol Balucki, 2026-11-13: Nie - będzie to duzo bardziej rozwinięte. Zostawiamy ten temat i dajemy go do omówienia na sesji długiej

### D-010 Fazy roadmapy 2–6
💡 propozycja · roadmapa · źródło: master prompt
Zob. [[Roadmapa]].

### D-011 Pipeline assetów `/asset` i moduł `AssetIds`
✅ zatwierdzona · technika / grafika · 2026-11-12 · źródło: paczka `blocky-asset-pipeline` · zdecydował: Karol Balucki 2026-11-13
Nowe grafiki powstają przez skill `/asset`: Higgsfield → obróbka → Figma → akceptacja Game Directora → upload przez Roblox Open Cloud → wpis w manifeście. Zasady paczki: asset ID w kodzie gry tylko przez moduł `AssetIds` (nie wpisane na sztywno), zero tekstu w grafikach AI (napisy natywnie). Obecny [[HUD]] i [[Ekran ładowania]] mają ID wpisane na sztywno, a przyciski HUD mają wypalone napisy, więc przyjęcie decyzji oznacza ich przepięcie. Zob. [[Pipeline assetów]].
Powiązane: [[Narzędzia]], [[Style Lock]]

### D-012 Panel zespołu jako okno na sejf
✅ zatwierdzona · narzędzia · 2026-11-12 · zaproponował: Karol (przez Claude Code) · zdecydował: Karol Balucki 2026-11-13
Lokalny panel `panel/` pokazuje sejf (decyzje, zadania, roadmapę), raporty z wdrożeń z akceptacją, podgląd 3D mapy i agenta na subskrypcji Claude Code. Nie trzyma własnej kopii wiedzy, więc nie narusza D-008 — uściśla jej zdanie o porzuconym dashboardzie. Zob. [[Panel zespołu]], [[Pytania otwarte]] #11.

### D-013 Pętla bez czekania: walka od razu, liczniki tylko równolegle
❌ odrzucona · game design · 2026-11-12 · źródło: rozmowa 12.11 i rekomendacja Claude Code · zdecydował: Karol Balucki 2026-11-13
Quest zaczyna się walką (8–15 s), a rozgłos strefy podnosi nagrody. Długie liczniki (jajko, wyprawa najemnika, budowa) działają tylko w slotach równoległych. Rozwija D-004, nie zastępuje jej. Zob. [[Propozycje z rozmowy 2026-11-12]], [[Pytania otwarte]] #7.
Uzasadnienie — Karol Balucki, 2026-11-13: Dłuższa rozmowa

### D-014 MVP jednej pętli i test popytu przed rozbudową
❌ odrzucona · roadmapa · 2026-11-12 · źródło: [[Ocena potencjału gry]] · zdecydował: Karol Balucki 2026-11-13
Cztery tygodnie: plac → karczma → walka → łup → statystyki, jeden loch, pierwszy pet, pierwszy budynek twierdzy; publikacja i decyzja na podstawie danych (powroty następnego dnia 15–20%). Pełna twierdza, arena i gildie dopiero po tej bramce.
Uzasadnienie — Karol Balucki, 2026-11-13: Chcemy mieć zaimplemenotwane od razu przed pierwszym wypuszczeniem dużo więcej logik i połączeń

### D-015 Monetyzacja bez płatnej losowości
✅ zatwierdzona · monetyzacja · 2026-11-12 · źródło: [[Retencja i monetyzacja — co wolno i co działa]] · zdecydował: Karol Balucki 2026-11-13
Za Robuxy sprzedajemy wygodę, sloty, kosmetykę i VIP. Losowania (sklep, koło, jajka) tylko za walutę i tokeny zdobywane w grze. Bez symulowanego hazardu i bez cudzych marek w nazwach. Zob. [[Pytania otwarte]] #12.
Uzasadnienie — Karol Balucki, 2026-11-13: Okej, bez hazadu symulowanego. Docelowo chcemy żeby ta gra była dostępna dla najszerszego grona ludzi więc musimy się pozbyć wszelkich takich problemów regulacyjnych

### D-016 Hub na 16–20 graczy, walki liczone na serwerze
✅ zatwierdzona · technika · 2026-11-12 · źródło: [[Technika gry — serwery, światy, walki]] · zdecydował: Karol Balucki 2026-11-13
Serwer huba na 16–20 osób; wydarzenia „dla wszystkich” przez wspólny stan serwerów. Każdą walkę liczy serwer, a klient ją odtwarza (ekran 2D albo cutscenka 3D — po teście).
Uzasadnienie — Karol Balucki, 2026-11-13: Tak, ale decyzja definitywna padnie, że wszystlie walki będą 3D tak jak widzę w Roblox Studio po wciśnięciu "E" na arenie

### D-017 Mapy z klocków: jeden plik `czesci.json` dla Blendera, Studio i panelu
✅ zatwierdzona · technika / 3D · 2026-11-12 · zaproponował: Claude Code · zdecydował: Karol Balucki 2026-11-13
Zob. [[Klocki — Blender i Roblox]]. Demo: `Workspace/DemoLesnaBaza`.
Uzasadnienie — Karol Balucki, 2026-11-13: Odpowaiadałem już na to pytanie, gdy porównywaliśmy Blendera i Robloxa

### D-018 Styl UI: „bubbly cartoon” zamiast pixel-artu
❌ odrzucona · styl · 2026-11-12 · źródło: [[Styl UI gier Roblox]] · zdecydował: Karol Balucki 2026-11-13
Wdrożone grafiki HUD pasują do standardu Roblox, a przeczą zapisom o pixel-arcie i płaskim designie w [[Kierunek artystyczny]] i [[Style Lock]]. Propozycja: zaktualizować kanon do wdrożonego stylu, a napisy przenieść z grafik do tekstu. Dotyka D-001 i D-002, więc wymaga nowej decyzji, która je zastąpi. Zob. [[Pytania otwarte]] #10.
Uzasadnienie — Karol Balucki, 2026-11-13: Potrzebuje zobaczyć oba te style miasta jako zdjęcie na zywo. Nie jestem w stanie tak od razu odpowiedzieć któy styl będzie tym finalnym

### D-019 Myśl przewodnia v2: „krzywy montaż”
💡 propozycja · game design · 2026-11-13 · źródło: [[Diagnoza pomysłu 2026-11-13]] i panel koncepcji (Claude Code u Karola)
Gra opisana jednym zdaniem o czynności — „Rozbij potwora na klocki, a kot złoży go krzywo, z błędem, który daje moc” — zamiast porównania do gry-inspiracji i listy czterech gatunków. Duet z logo staje się maskotkami (Crycket — kot składający potwory, Blocky — strażnik placu), a gracz gra własnym awatarem. Zmieniałaby [[Koncepcja i Core Loop]] i role z D-003 (wygląd postaci bez zmian). Zob. [[Myśl przewodnia v2]], [[Pytania otwarte]] #16.

### D-020 Pętla v2: BONK, banda i Album; dwa etapy z bramkami pomiaru
💡 propozycja · game design / roadmapa · 2026-11-13 · źródło: [[Systemy gry v2]]
Rdzeń: jeden przycisk BONK w otwartej strefie (wybity potwór przewraca stado), banda dobija, Finał, Album z jawnymi progami zamiast losowania; mini-dungeon z D-004 jako „Spiżarnia”. Budowa w dwóch etapach (A: rdzeń i pierwsze 10 minut, B: wersja do uczciwego pomiaru) z bramkami B0–B4. Rozwija D-013, zastępowałaby D-014. Zob. [[Karta ocen v2 i plan sprawdzenia]], [[Specyfikacja v2.1 — Krzywa Banda]].

### D-021 Gra bez alkoholu, bez losowych nagród i bez waluty za Robuxy
❌ odrzucona · zgodność / monetyzacja · 2026-11-13 · źródło: [[Diagnoza pomysłu 2026-11-13]] · zdecydował: Karol Balucki 2026-11-13
Roblox dopuszcza odniesienia do alkoholu tylko w grach 18+, więc karczma zostaje jadłodajnią („Zupa u Chochli”), a kufel — także w ikonie HUD i żartach ekranu ładowania — zastępuje kociołek. Żadnej losowej nagrody (także darmowej) i żadnej waluty kupowanej za Robuxy; waluty to Złoto i Magiczne Kryształy, Diamenty znikają. Zaostrza D-015; dotyczy pytań #6, #8, #12 i #19. Zob. [[Psychologia gracza v2]].
Uzasadnienie — Karol Balucki, 2026-11-13: Absolutnie, aż tak to nie. Musimy pozwalac kupować walutę w grze za Robuxy. Musimy my też jako twórcy na tym zarabiać. Musi być tutaj pewien kompromis

### D-022 Publiczność startowa 16+ i miękka premiera
❌ odrzucona · rynek / roadmapa · 2026-11-13 · źródło: [[Diagnoza pomysłu 2026-11-13]] · zdecydował: Karol Balucki 2026-11-13
Nową grę widzą najpierw tylko gracze 16+ ze sprawdzonym wiekiem, a młodsi dopiero po progu odtworzeń. Haczyk, miniatury i pierwszy test popytu projektujemy więc pod starszych graczy; grudzień to miękka premiera bez decyzji „zakończyć”, a decyzje zapadają na dwóch ważnych kohortach po Etapie B. Zob. [[Karta ocen v2 i plan sprawdzenia]], [[Pytania otwarte]] #18.
Uzasadnienie — Karol Balucki, 2026-11-13: NIE. Grę będą musieli zobaczyć wszyscy, nawet najmłodsi, dlatego staramy się tak, aby na przykład w karczmach nie było piwa, tylko sok itd

### D-023 Telemetria gry i jej odczyt w panelu
✅ zatwierdzona · technika · 2026-11-13 · zaproponował: Karol (przez Claude Code) · zdecydował: Karol Balucki 2026-11-13
Moduł `src/server/Telemetria` (bezwładny do czasu włączenia, bez danych osobowych: sesje, gracze naraz, wydane Robuxy, błędy, serwery) i sekcja „Telemetria gry” w Analityce panelu. Włączenie wymaga skryptu startowego w grze, publikacji i klucza Open Cloud tylko do odczytu, trzymanego lokalnie. Zob. [[Telemetria gry]], [[Pytania otwarte]] #13 i #20.

### D-024 Walka 3D w każdej potyczce, w trzech długościach
❌ odrzucona · game design / technika · 2026-11-13 · źródło: test w Roblox (`swiat/test_walki_roblox/`) · zmieniona wieczorem 2026-11-13 · zdecydował: Karol Balucki 2026-11-13
Test w samym Roblox (kontener `Workspace/TestWalki`, 9 sekund, serwer liczy — klient odtwarza) pokazał, że cutscenka jest wykonalna i tania dla procesora na komputerze (telefon niezmierzony). Poranna wersja tej propozycji („cutscenka jako nagroda, nie jako rdzeń”) zostawiała ją tylko przy bossie, bo diagnoza przewidywała, że oglądanie walki nie wytrzyma powtórek. To było przewidywanie, nie pomiar. Wieczorem Karol obejrzał test w Studio i ocenił walkę jako bardzo wciągającą mimo drobnych błędów, więc propozycja brzmi teraz tak: zwykła potyczka trwa 3–4 s (dwie–trzy wymiany losowane z wyniku serwera: cios, blok, unik, krytyk; „POMIŃ” od pierwszej sekundy), a pełna wersja 9–12 s z pracą kamery zostaje na pierwsze spotkanie z nowym potworem, bossa i arenę. Różnorodność ma wynikać z postępu gracza: nowa broń daje nowy cios, a pet dokłada swój atak. Powtarzalność sprawdzamy pomiarem — licznik pominięć na numer walki. Stanowisko Karola z panelu (13.11): „cutscenka powinna być przy każdej walce z każdym potworem czy bossem”; z decyzją czeka na Pawła. Prototyp trzeba usunąć ze wspólnego miejsca przed publikacją (`python swiat/test_walki_roblox/zbuduj.py --usun`). Dotyczy D-016 i pętli z D-020.
Uzasadnienie — Karol Balucki, 2026-11-13: To pytanie będzie głębsze i będzie wymagało dyskusji na głos z Pawłem do transkrypcji

### D-025 Mapy v2: biblioteka krzywych brył i „Krzywe Miasteczko”
💡 propozycja · technika / 3D · 2026-11-13 · zaproponował: Karol (przez Claude Code)
`swiat/biblioteka/` (układy lokalne do pochylonych brył, obrys „tuszem”, podgląd w Blenderze) i mapa `swiat/krzywe_miasteczko/` w stylu komiksowym. Według propozycji v2 miasteczko-hub wchodzi do gry dopiero po bramce D7 — do tego czasu to demo stylu i poligon narzędzi. Rozwija D-017. Zob. [[Klocki — Blender i Roblox]].

### D-026 Łańcuch narzędzi: Rokit z przypiętym Rojo 7.6.1
✅ zatwierdzona · narzędzia · 2026-11-13 · źródło: [[Narzędzia i skille do Roblox]] · zdecydował: Karol Balucki 2026-11-13
Plik `rokit.toml` w repozytorium przypina Rojo 7.6.1 (wersja z kanonu). Rokit instaluje każda osoba u siebie; podniesienie Rojo do 7.7.1 robimy u obu osób naraz, razem z pluginem w Studio.

### D-027 Instrukcja promptów „Glossy Ink” zastępuje prefiks Style Lock
✅ zatwierdzona · styl / grafika · 2026-11-13 · źródło: dokument Game Directora przekazany przez Karola · zdecydował: Karol 2026-11-13
Każdy prompt graficzny składa się ze stałego początku „Glossy Ink” (odwołanie do własnego obrazu referencyjnego, bez cudzej nazwy), zmiennego środka, stałego końca i osobnego negative promptu; do tego zasady zamkniętych krawędzi, pustych kontenerów, okien ze statystykami i map izometrycznych. Zastępuje prefiks z D-001 oraz zapisy o pixel-arcie ikon i płaskim interfejsie z D-002; reszta D-002 obowiązuje dalej. Jest zgodna z propozycją D-018, ale jej nie zatwierdza. Zob. [[Instrukcja promptów — Glossy Ink]], [[Pytania otwarte]] #22.

### D-028 Panel jako miejsce pracy: zapis do sejfu z panelu i klucz Game Directora
✅ zatwierdzona · narzędzia · 2026-11-13 · zaproponował: Karol (przez Claude Code) · zdecydował: Karol 2026-11-13
Z panelu da się odpowiadać na pytania otwarte, odhaczać i dodawać zadania oraz zatwierdzać i odrzucać decyzje. Panel zapisuje zmiany do tych samych plików sejfu (małe, czytelne wiersze, ślad w dzienniku), więc D-008 zostaje w mocy: sejf jest jedynym źródłem prawdy, a panel staje się wygodnym miejscem pracy na nim. Zapis jest włączony od 13.11.2026 na komputerze Karola, bez dodatkowych ograniczeń dla wejść z kodem dostępu, bo dostęp do panelu mają tylko Karol i Paweł. Odpowiedzi gości są oznaczane „gość panelu”. Zmiana statusu decyzji wymaga klucza lokalnego albo klucza zatwierdzania i jest podpisywana imieniem i datą (D-030). Rozwija D-012. Zob. [[Panel zespołu]], [[Pytania otwarte]] #23.

### D-029 Postacie, pety i ekwipunek z kodu; w Roblox najpierw postacie z klocków
✅ zatwierdzona · technika / grafika 3D · 2026-11-13 · zaproponował: Karol (przez Claude Code) · zdecydował: Karol Balucki 2026-11-13
Postacie, pety i ekwipunek opisujemy kodem (jeden plik na postać), a z tego opisu powstają siatki z animacjami w Blenderze oraz postacie z części Roblox ze stawami, które da się postawić w Studio bez wgrywania zasobów. Propozycja: na start NPC i pety stawiać w grze jako postacie z klocków, a import siatek zostawić jako drugą drogę do sprawdzenia. Dziś postacie stoją tylko w Studio jako próba (animacje i skrypty działają wyłącznie w Studio). Import siatki sprawdzono 13.11.2026 wieczorem na Rycerzu: wyszła poprawna postać R15 z 15 części, więc obie drogi są do wyboru. Rozwija D-017. Wygląd postaci i sloty ekwipunku pozostają do decyzji Karola albo Pawła. Zob. [[Postacie 3D — Blender i Roblox]], [[Pytania otwarte]] #24.
Uzasadnienie — Karol Balucki, 2026-11-13: Okej. Pokaż mi dokładnie w raporcie porównanie Stylu Robloxowego do stylu blenderowego. Może tak na prawdę nie potrzebujemy Blendera?

### D-030 Decyzje zatwierdza Karol albo Paweł; każda zostaje w logach
✅ zatwierdzona · zasady pracy · 2026-11-13 · zdecydował: Karol 2026-11-13
**Zdecydował Karol; potwierdzenie Pawła czeka w [[Pytania otwarte]] #27.** Do tego czasu decyzje zatwierdzone tylko przez Karola mają jego podpis, a Paweł może je cofnąć. Obaj mają takie same prawa do zatwierdzania decyzji i nadawania notatkom statusu `kanon`. Wystarczy decyzja jednej osoby, bo ustalenia i tak omawiają na bieżąco. Każda decyzja zostaje w logach: w tym rejestrze (podpis `zdecydował: <imię> <data>`) i w [[Dziennik zmian]]. Zastępuje zasadę jednego zatwierdzającego Game Directora z [[Jak prowadzimy sejf]] i z `CLAUDE.md`. W panelu zmiana statusu decyzji wymaga klucza lokalnego (osoba przy komputerze z panelem) albo klucza zatwierdzania; wpis oznaczony „gość panelu” decyzją nie jest. Gdy obaj się różnią, spór trafia do [[Pytania otwarte]] i nic nie jest nadpisywane. Odpowiedź na [[Pytania otwarte]] #15. Zob. [[Panel zespołu]].

---
*Nowa decyzja: skopiuj szablon [[Decyzja]] (folder Szablony) albo dopisz sekcję `### D-0XX` na końcu.*
