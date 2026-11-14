---
status: kanon
tags: [produkcja, decyzje]
---
# Rejestr decyzji

Tylko decyzje **✅ zatwierdzone** są obowiązujące. Zatwierdzonej decyzji się nie przepisuje: dodaje się nową, która ją **zastępuje**, i zostawia ślad.

Statusy: ✅ zatwierdzona · 🕓 do decyzji · 💡 propozycja · ❌ odrzucona · ♻️ zastąpiona · 🗃️ nieaktualna (zdjęta z kolejki: nie obowiązuje i nie czeka na drugi podpis)

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
✅ zatwierdzona · roadmapa · źródło: master prompt · zdecydował: Karol Balucki 2026-11-14
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
❌ odrzucona · game design · 2026-11-13 · źródło: [[Diagnoza pomysłu 2026-11-13]] i panel koncepcji (Claude Code u Karola) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Gra opisana jednym zdaniem o czynności — „Rozbij potwora na klocki, a kot złoży go krzywo, z błędem, który daje moc” — zamiast porównania do gry-inspiracji i listy czterech gatunków. Duet z logo staje się maskotkami (Crycket — kot składający potwory, Blocky — strażnik placu), a gracz gra własnym awatarem. Zmieniałaby [[Koncepcja i Core Loop]] i role z D-003 (wygląd postaci bez zmian). Zob. [[Myśl przewodnia v2]], [[Pytania otwarte]] #16.
Uzasadnienie — Karol Balucki, 2026-11-14: NIEAKTUALNE

### D-020 Pętla v2: BONK, banda i Album; dwa etapy z bramkami pomiaru
❌ odrzucona · game design / roadmapa · 2026-11-13 · źródło: [[Systemy gry v2]] · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Rdzeń: jeden przycisk BONK w otwartej strefie (wybity potwór przewraca stado), banda dobija, Finał, Album z jawnymi progami zamiast losowania; mini-dungeon z D-004 jako „Spiżarnia”. Budowa w dwóch etapach (A: rdzeń i pierwsze 10 minut, B: wersja do uczciwego pomiaru) z bramkami B0–B4. Rozwija D-013, zastępowałaby D-014. Zob. [[Karta ocen v2 i plan sprawdzenia]], [[Specyfikacja v2.1 — Krzywa Banda]].
Uzasadnienie — Karol Balucki, 2026-11-14: NIEAKTUALNE

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
✅ zatwierdzona · technika / 3D · 2026-11-13 · zaproponował: Karol (przez Claude Code) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
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

### D-031 Waluta premium: Magiczne Kryształy (w HUD „Diamenty”) w roli grzybków z S&F
✅ zatwierdzona · game design / monetyzacja · 2026-11-14 · źródło: pytanie Pawła w panelu („jaką walutę premium moglibyśmy zastąpić grzybki”) · zaproponował: Claude Code (u Karola) · zdecydował: Karol Balucki 2026-11-14
Grzybki w *Shakes & Fidget* to waluta premium, której symbolu nie kopiujemy ([[Shakes & Fidget — rozbiór mechanik]]). Ich rolę przejmują **Magiczne Kryształy**, które kanon już zna ([[Twierdza (Tycoon)]]); ikona diamentu z HUD zostaje jako ich obraz (w kodzie dalej `Gems`). Odpowiada to na [[Pytania otwarte]] #6: Diamenty i Magiczne Kryształy to jedna waluta. Zdobywa się ją w grze (bossowie, pierwsze zadanie dnia, kamienie milowe, wyczyny; droppery Twierdzy dawałyby tylko Złoto albo bardzo mało Kryształów — do spięcia z #9) **i** kupuje za Robuxy w stałych paczkach, z ceną w R$ widoczną na przycisku. Za Kryształy kupujemy wyłącznie rzeczy pewne, zgodnie z D-015: wygodę (wierzchowce, sloty ekwipunku, przyspieszenie budowy twierdzy), kosmetykę i VIP. Nigdy koła, jajek ani odświeżenia sklepu, bo waluta kupiona za R$ wydana na los jest płatnym przedmiotem losowym — losowania zostają za Złoto i tokeny z gry. Paczki dopasowane do cen przedmiotów, bez „resztek” i bez presji na kupno nadmiaru (zasady CPC w [[Retencja i monetyzacja — co wolno i co działa]]). Rozważone i odłożone nazwy: „Żetony” (z rozbioru S&F) odpada przez skojarzenie z kasynem; „Klocki” są zajęte przez propozycję v2 (klocki nigdy na sprzedaż, D-020); „Złote Rybki” (smakołyk Crycketa) to zabawny odpowiednik grzybka, gdyby zespół wolał humor zamiast klejnotu — wtedy nowa ikona. Zmienia opis dropperów w [[Twierdza (Tycoon)]] i etykietę licznika w [[HUD]]; stoi w sprzeczności ze zdaniem „Diamenty znikają” z propozycji v2 ([[Systemy gry v2]]), która nie jest kanonem. Zob. [[Pytania otwarte]] #6, #9, #12.

### D-032 Poziomy trudności zadań lokalne dla biomu
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 1) · zdecydował: Karol Balucki 2026-11-14
Każde zadanie z karczmy ma trzy poziomy: łatwy / średni / trudny, ale skala jest lokalna dla biomu — łatwe zadanie w biomie kryształowym jest trudniejsze niż trudne zadanie w lesie, bo przeciwnicy mają tam wyższy poziom. Biomy odblokowują się poziomem gracza (las od początku, kolejne wyżej). Z sesji: Karol zaproponował, Paweł się zgodził. Zastępuje część odrzuconej D-009 o poziomach misji; Energia z D-009 nadal nierozstrzygnięta. Zob. [[Karczma (Questy)]], [[Pytania otwarte]] #8.

### D-033 Cutscenka walki tylko przy bossach, rzadkich przeciwnikach i na koniec zadania
❌ odrzucona · game design / technika · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 2) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Zwykłe potwory w strefie bije się bez cutscenki, z prostą animacją zamachu (miecz, różdżka). Cutscenka 3D jest przy bossach i ważnych przeciwnikach (np. troll jaskiniowy), przy rzadkim przeciwniku, który pojawia się w strefie, i na koniec zadania z karczmy. Walka trwa, aż zdrowie jednej strony spadnie do zera; jej długość wynika z losowości i statystyk, nie ze stałej liczby sekund. Z sesji: Paweł zwrócił uwagę, że cutscenka przy 20 potworach w strefie zmęczy; Karol zmienił swoje stanowisko z 13.11 („cutscenka przy każdej walce”). Zastępuje odrzuconą D-024 i zamyka „po teście” z D-016. Zob. [[Pytania otwarte]] #7.
Uzasadnienie — Karol Balucki, 2026-11-14: Nie, animacja walki przy każdej walce

### D-034 Pętla gry: zadania z karczmy na czas plus zajęcia równoległe, jedna karczma
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 3) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Karczma daje zadania na czas jak w S&F (miejsce, krótki opis, nagroda, czas); licznik zadania widać w HUD. W tym czasie gracz ma co robić: strefy z odradzającymi się potworami (podejście, E, walka), dungeony, sklep, Twierdza, odbieranie nagród — „zawsze coś do zrobienia”. Jedna karczma dla całej gry, nie po jednej na biom. Z sesji: Paweł zaproponował połączenie licznika z farmieniem w strefie (sam licznik zachęcałby do botów), Karol chce gry, od której nie da się oderwać. Zastępuje odrzuconą D-013 i zmienia D-004 w części „bez biernego czekania” (czekanie zostaje, ale równolegle z aktywną grą). Zob. [[Koncepcja i Core Loop]], [[Pytania otwarte]] #7.

### D-035 Zakres pierwszego wydania
✅ zatwierdzona · roadmapa · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 6) · zdecydował: Karol Balucki 2026-11-14
Na premierę: karczma z zadaniami na czas, kilka biomów (lista do ustalenia), strefy z potworami, pierwsze dungeony, sklep z bronią i sklep magiczny, Pety (zamiast wierzchowców), Twierdza w podstawie, kilka potworów (m.in. slime w kolorze biomu, troll) i kilku bossów. Po premierze w aktualizacjach: kolejne biomy i potwory, kowal, podziemia Twierdzy. Sporne: ulepszanie przedmiotów (Karol: może od razu, Paweł: później); gildie nie padły. Progresja ma mieć próg — gry nie da się „zmaksować” w dwa dni, dalsza treść przychodzi aktualizacjami; balans przez playtesty. Zastępuje odrzuconą D-014. Zob. [[Roadmapa]], [[Pytania otwarte]] #32.

### D-036 Monetyzacja: co sprzedajemy za Robuxy
✅ zatwierdzona · monetyzacja · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 7) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Za Robuxy: waluta (Diamenty, Złoto), paczki przedmiotów skalowane z poziomem gracza, paczki czasowe (pominięcie czekania, np. odebranie nagród z 24 godzin zadań karczmy albo budowy), paczki surowców po wejściu Twierdzy, emotki, game passy stałe (np. podwójne doświadczenie, VIP z pokojem VIP; także tanie passy rzędu 10 Robuxów). Nie sprzedajemy skinów postaci, chrom do przedmiotów, tańców ani finisherów (bronie mają je w zestawie); skiny budynków Twierdzy — może później. Z sesji: Karol zaznaczył, że stałe podwójne doświadczenie to „trochę pay-to-win, ale nie za bardzo”. Doprecyzowuje D-015 (wygoda, kosmetyka, VIP) i rozwija odpowiedź Karola przy D-021. Zob. [[Retencja i monetyzacja — co wolno i co działa]], [[Pytania otwarte]] #12.

### D-037 Bilety na rolki za Robuxy i „mistrz gier planszowych”
✅ zatwierdzona · monetyzacja / zgodność · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 5) · zdecydował: Karol Balucki 2026-11-14
Pomysł Pawła: losowania jako „RNG, nie hazard” — rolki z jawnymi szansami i mnożnikiem szczęścia, dzienne rolki u kupca, bilety dokupowane za Robuxy; zamiast hazardzisty mistrz gier planszowych (plansza, kostki, pionek, pole daje nagrodę albo mnożnik; można postawić monety, pole może je pomnożyć albo zabrać połowę). Diamentami też można u niego grać. Karol: dobrze, „jeżeli da się to sprytnie ukryć”; szczegóły to osobne pytania. **Konflikt z zatwierdzoną D-015** (losowania tylko za walutę i tokeny z gry, bez symulowanego hazardu) i z propozycją D-031 (waluta premium nigdy na losowania). Według [[Retencja i monetyzacja — co wolno i co działa]] stawianie waluty, by wygrać więcej, jest w Roblox zakazane, a losowanie za Robuxy (także bilety i waluta kupiona za Robuxy) wymaga jawnych szans. Zatwierdzenie tej propozycji oznacza nową decyzję zastępującą D-015. Zob. [[Pytania otwarte]] #30.

### D-038 Waluty: Złoto i Diamenty (nazwa robocza), konwersja w jedną stronę
✅ zatwierdzona · game design / ekonomia · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 13) · zdecydował: Karol Balucki 2026-11-14
Złoto kupuje przedmioty i tarcze (jak w S&F). Diamenty to waluta premium — kupowana za Robuxy i zdobywana w grze — na ulepszenia (D-039), dopłatę do lepszych przedmiotów (Złoto plus Diamenty) i paczki. Konwersja Diamenty → Złoto tak, Złoto → Diamenty nie (Karol, wzór z grzybków S&F; Paweł niepewny). Nazwa „Diamenty” jest tymczasowa — Paweł chce nazwy tematycznej, agent ma zaproponować. O Magicznych Kryształach z kanonu ([[Twierdza (Tycoon)]], [[HUD]]) na sesji nikt nie wspomniał. Równoległa propozycja D-031 (z pytania Pawła w panelu, tego samego dnia) nazywa tę walutę Magiczne Kryształy, przewiduje stałe paczki za Robuxy i wyklucza wydawanie jej na losowania — obie propozycje trzeba rozstrzygnąć razem; w sprzecznych punktach (nazwa, losowania u mistrza gier) obowiązuje ta zatwierdzona. Zob. [[Pytania otwarte]] #6.
Uzasadnienie — Karol Balucki, 2026-11-14: Tak, ale powiedzieliśmy również o walucie tokenów dla petów specjalnych, oraz waluta game passowa

### D-039 Drzewka umiejętności za Diamenty: postaci, Twierdzy i każdego peta
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 13) · zdecydował: Karol Balucki 2026-11-14
Paweł: Diamenty wydaje się głównie na ulepszenia w drzewkach — drzewko postaci (bonus do doświadczenia, większe szczęście do rolek) i drzewko Twierdzy (np. szybsze kopanie); prędkość ruchu — Karol: nieistotna. Karol: każdy pet ma własne, unikalne drzewko. Zob. [[System RPG]], [[Pety]], [[Twierdza (Tycoon)]].

### D-040 Trzecia waluta na game passy i osobna waluta petów
✅ zatwierdzona · game design / monetyzacja · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (tematy 7 i 13) · zdecydował: Karol Balucki 2026-11-14
Paweł: trzecia, trudna do zdobycia waluta (robocza nazwa „chrupki Crycketa”), za którą można kupić game passy bez Robuxów (np. VIP za 100) — gracz może je wygrać graniem. Karol: zgoda (wzór: The Finals). Do tego osobna waluta petów (robocze „petcoiny”) zdobywana na wyprawach i w walkach petów, wydawana na drzewka petów (D-039). Zob. [[Pety]].
Uzasadnienie — Karol Balucki, 2026-11-14: Tak ale ta waluta na game passy będzie też mogła być zakupiona przez Roblox walute, a ta waluta game passowa może być wykożystana do innych zakupów ulepszających i pomagających przyspieszyć gre

### D-041 Styl świata: Krzywe Miasteczko jako styl oficjalny — kreskówka z ciemną kreską, nie pixel-art
✅ zatwierdzona · styl / 3D · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 10) · zdecydował: Karol Balucki 2026-11-14
Paweł obejrzał raport-porównanie dwóch stylów mapy i podgląd 3D; obaj wybrali Krzywe Miasteczko. Kierunek świata 3D: kreskówkowy z wyraźną ciemną kreską (obrys „tuszem”), nie pixel-art. Karol: „coś poprawiamy w kolorystyce” — co, do ustalenia; Paweł nie rozpoznał sklepu z Petami i wejścia do dungeonu, więc czytelność modeli do poprawy. Zastępuje odrzuconą D-018 w części „pixel-art czy cartoon” (zatwierdzenie oznacza aktualizację [[Kierunek artystyczny]]); przyjmuje mapę z D-025 jako wzorzec stylu (D-025 zostaje osobną propozycją o narzędziach). Ramki, nachylone przyciski i dymki z D-002 — bez zmian do pytania #25. Zob. [[Klocki — Blender i Roblox]], [[Pytania otwarte]] #10, #33.

### D-042 Wejście do dungeonów: wrota z kłódką i hala portali
✅ zatwierdzona · game design / świat · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 10) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Pomysł Pawła: w miasteczku stoją wrota z kłódką; po osiągnięciu wymaganego poziomu gracz widzi animację (kłódka spada, wrota się otwierają), a za nimi jest hala z portalami do dungeonów. Stan blokady jest widoczny osobno dla każdego gracza (gracz 8. poziomu widzi zamknięte, gracz 50. — otwarte). Karol: podoba mu się. Zob. [[Koncepcja i Core Loop]].
Uzasadnienie — Karol Balucki, 2026-11-14: Tak, ale w momencie odblokowania daneonu przez gracza to odpala mu się dokładniej mówią Cut scenka, a nie koniecznie animacja

### D-043 Decyzja jednej osoby plus potwierdzenie drugiej po alercie
✅ zatwierdzona · zasady pracy · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 9) · zdecydował: Karol Balucki 2026-11-14
Jedna osoba nie zatwierdza decyzji bez wiedzy drugiej (Paweł: „moim zdaniem nie”). Model: osoba podejmuje decyzję w panelu, druga dostaje automatyczny alert na telefon z wyborem „zgódź się / nie zgódź się / przedyskutuj”; Paweł woli bota Telegram niż osobną aplikację. Zastępowałaby D-030 (wystarczy decyzja jednego). Do czasu zatwierdzenia obowiązuje D-030, a decyzje zatwierdzone tylko przez Karola Paweł może cofnąć. Jak to zrobić technicznie i czy komputer musi być włączony: [[Pytania otwarte]] #29. Zob. [[Jak prowadzimy sejf]], [[Panel zespołu]].

### D-044 Własność: jedna gra w grupie Roblox i prywatne repozytorium
✅ zatwierdzona · organizacja · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 12) · zdecydował: Karol Balucki 2026-11-14
Zamiast dwóch kopii gry (projekt Pawła i jego kopia u Karola) jedna gra w grupie Roblox, w której obaj są współpracownikami; grupa kosztuje ok. 100 Robuxów (Karol: „możemy zainwestować”). Repozytorium GitHub ma być prywatne — przełącza właściciel (Paweł) w ustawieniach repozytorium. Nie padło: kto zakłada grupę i jest właścicielem, podział wypłat, kto trzyma klucz Open Cloud, czy przenieść istniejącą grę czy założyć nową ([[Pytania otwarte]] #31). Odpowiada na pytania #13 i #14. Zob. [[Workflow i Git]], [[Pipeline assetów]].

### D-045 Język gry: angielski jako podstawa, z tłumaczeniami
✅ zatwierdzona · UI / lokalizacja · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 — zapis ustaleń]] (temat 14) · zdecydował: Karol Balucki 2026-11-14
Teksty w grze po angielsku, z tłumaczeniami (gracz z polskim ustawieniem widzi polski) — Paweł, Karol zgadza się. Rozstrzyga język nazw z pytań #5 i #28; lista lokacji mapy teleportacji i zestaw przycisków HUD zostają otwarte. Wymaga napisów natywnych, nie wypalonych w grafikach (zgodnie z D-011). Zob. [[HUD]], [[Mapa teleportacji]].

### D-046 Nazwy: trzecia waluta „Chrupki”, waluta petów „Łapki”, koło „Krzywe Koło”
❌ odrzucona · game design / nazwy · 2026-11-14 · zaproponował: Claude Code (na prośbę Karola i Pawła z sesji 14.11) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Na sesji padła prośba o nazwy. Waluta premium ma już nazwę z D-031 (Magiczne Kryształy). Propozycje dla reszty: trzecia waluta z D-040, zdobywana graniem i wydawana na game passy — **Chrupki** (pomysł Pawła: przysmak Crycketa; po angielsku „Crunchies”); waluta petów z D-040 — **Łapki** („Paws”); koło fortuny zamiast nazwy z cudzą marką — **Krzywe Koło** („Wonky Wheel”), pasuje do Krzywego Miasteczka (D-041). Każdą nazwę można przyjąć osobno. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]], [[Pytania otwarte]] #12.
Uzasadnienie — Karol Balucki, 2026-11-14: Nowa waluta to Rybki. Pety nie mają swojej waluty, tylko shardy o których mówiliśmy. Shardy podczas scrapowania lub manualnego zabijania potworów. Krzywe Koło jest okej

### D-047 Drzewko umiejętności postaci: trzy gałęzie i pień, piętra za poziom, pierwsza ranga za punkt talentu, kolejne za Diamenty
❌ odrzucona · game design / monetyzacja · 2026-11-14 · źródło: pytanie Pawła w panelu („jak rozplanować skill tree postaci”) · zaproponował: Claude Code (u Karola) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Rozwija zatwierdzoną D-039 (drzewko postaci za Diamenty). Drzewko jest trzecią warstwą siły postaci obok statystyk i ekwipunku: daje premie procentowe (EXP, Złoto, obrażenia, szczęście) i wygodę, nie surowe statystyki, więc mnoży to, co gracz już wygrał, a nie zastępuje przedmiotów. Kształt: trzy gałęzie — **Walka, Wyprawa, Fortuna** — i wspólny pień; pięć pięter otwieranych poziomem postaci (robocze 1/10/25/40/60) i dwoma węzłami piętra niżej, żeby Diamenty nie przeskakiwały pięter (próg progresji z D-035). Każdy węzeł ma trzy rangi: **pierwszą kupuje punkt talentu (jeden co poziom), drugą i trzecią Diamenty** — „punkt otwiera, Diamenty pogłębiają”; szerokość drzewka jest darmowa, głębia jest ujściem Diamentów. Jedno drzewko wspólne dla klas na premierę, klasa daje jedną stałą cechę startową; osobne drzewka na klasę jako aktualizacja. Przestawienie: pierwsze darmowe, kolejne za Złoto, nic nie przepada. Węzły Fortuny zmieniające szanse rolek kupowanych za Diamenty lub Robuxy muszą być widoczne w panelu szans (zasada paid random items, [[Retencja i monetyzacja — co wolno i co działa]]). Okno: zakładka TALENTS w [[Okno ekwipunku]]. Liczby są hipotezą do kalkulatora balansu. Zmiana wobec D-039: dokłada punkty talentu jako darmową ścieżkę — wymaga zgody; odrzucenie oznacza drzewko tylko za Diamenty. Zob. [[Drzewko umiejętności postaci]], [[Pytania otwarte]] #34, [[System RPG]].
Uzasadnienie — Karol Balucki, 2026-11-14: Tak, ale płącimy jedynie dimaetnami za drzewko.

### D-048 Rezygnacja z Energii w karczmie
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] (temat 1) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Zadania z karczmy nie zużywają Energii. Tempo gry wyznaczają czas zadania (D-034), poziomy trudności lokalne dla biomu (D-032) i poziom gracza. Z sesji: Karol rozważał Energię rosnącą z trudnością zadania i poziomem biomu, z limitem rosnącym z poziomem postaci; Paweł pytał, czy farmienie stref też ją zużywa (nie) i jak ją odnawiać (przedmiot za Robuxy albo z misji, bez klikacza). Obaj uznali, że gracz bez Energii musiałby przestać grać — Karol zaproponował rezygnację, Paweł się zgodził. Zamyka część „Energia” z odrzuconej D-009. Skutek dla interfejsu: kanoniczny niebieski pasek „Many/Energii” w [[HUD]] zostaje paskiem Many (do potwierdzenia). Zob. [[Karczma (Questy)]], [[Pytania otwarte]] #8.

### D-049 Twierdza: zamek z mini-budynkami i lista budynków
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] (temat 2) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Twierdza to działka z zamkiem jako sercem i osobnymi mini-budynkami; poziom zamku odblokowuje ulepszenia budynków. Budynki (lista robocza, obaj zgodni): kopalnia złota, kopalnia diamentów, pozyskiwanie drewna i kamienia (surowce na kolejne budynki), budynek pasywnego doświadczenia (odbiór po powrocie do gry), Training Center (D-050), budynek gildyjny (tu gracz dołącza do gildii), kowal (D-051); kopalnia kryształów na wyższych poziomach — Karol: kryształ odblokowuje „technologie”. Twierdza „chodzi sama”, bez stałej uwagi gracza (Karol); Training Center i kowal są aktywne. Nie kopiujemy budynków S&F (Karol). Odłożone: łowisko dające Złote Rybki (Paweł; Karol nie chce opierać wszystkiego na rybce). Odrzucone w rozmowie: napady na twierdze innych graczy z kradzieżą surowców (Paweł; Karol: niesprawiedliwe, niezbalansowane). Nie padło: od którego poziomu działka (Paweł chce Training Center od początku za grosze; 12.11 mówiono o ok. 25. poziomie), podziemia. Konflikty do rozstrzygnięcia: kopalnia diamentów produkuje walutę premium, a zatwierdzona D-031 przewiduje, że droppery dają tylko Złoto albo bardzo mało Kryształów (pytanie 6); kowal jest na liście, a D-035 odkłada go na po premierze (pytanie 32); kanon [[Twierdza (Tycoon)]] buduje droppery za surowce z misji, tu surowce powstają w Twierdzy. Zob. [[Pytania otwarte]] #9.

### D-050 Training Center: statystyki z mini-gier 3D, grind bez limitu, tryb AFK
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] (temat 2) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Pomysł Pawła: w Twierdzy stoi Training Center ze strefą mini-gry na każdą statystykę (sześć statystyk → sześć stref). Przykład: postać rzuca w gracza przedmiotami, gracz ciacha je mieczem (góra / prawo / dół); każde trafienie daje +1 do statystyki, seria trafień daje combo i większy przyrost; ulepszone centrum daje więcej za trafienie. Grindu nie ograniczamy (Paweł: „w Robloxie chodzi o to, że można spamić”; Karol odstąpił od pomysłu tokenów i limitów czasowych) — zamiast tego tryb AFK: auto-trening daje przyrost na sekundę, ale bez mnożników z combo. Dostępne od początku i tanie (Paweł). Podział źródeł (Paweł): potwory i zadania dają Złoto, przedmioty i czasem walutę premium, nie statystyki; statystyki rosną z Training Center, z przedmiotów (ograniczone) i za Złoto (coraz drożej). Karol: „fajne”, ale pytał, czy nie opłaci się siedzieć tylko na mini-grach — „to musimy przegadać” (pytanie 36). Zmienia [[System RPG]] (nowe źródło statystyk; 12.11 głównym źródłem miały być przedmioty) i zakłada, że punkty statystyk zostają (pytanie 17). Spójne z D-047 w podziale ról: drzewko daje procenty, trening surowe punkty. Miejsce (na działce czy obok) nie padło wprost. Zob. [[Twierdza (Tycoon)]], [[Pytania otwarte]] #36.
Uzasadnienie — Karol Balucki, 2026-11-14: Nie ma trybu AFK - na razie.

### D-051 Kowal ulepsza przedmioty, zaklinacz w biomie dodaje pasywki
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] (temat 2) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Paweł: kowal w Twierdzy (D-049) rozbiera zbędne przedmioty na materiały, a za materiały ulepsza inne — podnosi statystyki przedmiotu. Zaklinanie osobno, u postaci spotykanej w biomie: pasywki na broń (trucizna, podpalenie — dodatkowe obrażenia widoczne w animacji trafienia). Karol: „makes sense”. Tiery przedmiotów (np. drewniany miecz) — Paweł: „nie teraz”. Łączy się ze sporem o ulepszanie na premierę (D-035, pytanie 32). Zob. [[Okno ekwipunku]].

### D-052 Pety: stajnia w mieście, jajka za Złoto w każdej strefie, karmienie petów
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] (temat 2) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Stajnia (sklep z Petami) stoi w mieście, nie na działce Twierdzy (obaj). Pety wykluwają się z jajek kupowanych za Złoto; każda strefa ma własny zestaw jajek — w pierwszym mieście np. trzy podstawowe, najdroższe ok. 10 tys. Złota z ok. 1% szansy na legendarnego peta; lepsze pety w dalszych biomach (Paweł). Bardzo rzadko jajka wypadają też z potworów (Karol). Karmienie: słabszym petem karmi się lepszego, przekazując część jego doświadczenia — nie 1:1, przeliczone przez rzadkość zjadanego (Karol; Paweł: standard w grach Roblox). Od kiedy: Paweł — podstawowe jajka od początku; Karol pamiętał odblokowanie petów w drzewku i nie potwierdził wprost. Zgodne z kanonem [[Pety]] (jajka) i z D-015 (losowanie za walutę z gry), ale: skoro Diamenty kupione za Robuxy zamienia się na Złoto (D-038), jajka za Złoto podpadają pod zasady płatnych przedmiotów losowych — lista petów i szanse widoczne przed zakupem ([[Retencja i monetyzacja — co wolno i co działa]]). Drzewka i waluta petów: D-039, D-040. Zob. [[Pytania otwarte]] #38.

### D-053 Mistrz gier planszowych: plansza i kostka bez stawek, płatne rzuty i darmowy rzut na czas
✅ zatwierdzona · game design / zgodność · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] (temat 3) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Doprecyzowuje zatwierdzoną D-037 i zmienia ją w jednym punkcie: **bez stawiania monet i bez utraty połowy**. Mistrz gier siedzi w karczmie; podejście odpala cutscenkę. Gracz rzuca kostką sześcienną, pionek idzie po polach, każde pole ma stałą, zawsze dodatnią nagrodę — im dalej, tym lepszą; szanse są jawne, bo to kostka (Paweł: „żeby uniknąć gamble”). Rzut co jakiś czas darmowy (Paweł), każdy kolejny kosztuje Złoto i gracz decyduje, czy iść dalej (Karol); cena rzutów rośnie. Plansza ma np. 100 pól; po przejściu pojawia się nowa, lepsza (pierwsze pole nowej lepsze od ostatniego starej — „jak biomy”); planszę da się też ominąć płacąc. Karol woli osobne plansze (zmiana widoczna w 3D) od pętli z ulepszającymi się polami (pomysł Pawła). Na premierę tylko plansza, inne gry u mistrza później (Karol). Nagroda zawsze dodatnia, więc zgodne z D-015 i zasadami Roblox z pytania 30; Złoto jest wymienialne z Diamentów (D-038), więc nagrody pól muszą być widoczne przed rzutem. Bilety za Robuxy z D-037 nie padły. Zob. [[Karczma (Questy)]], [[Pytania otwarte]] #37.

### D-054 Klasy postaci: Wojownik, Zwiadowca, Mag; specjalizacje jako rozgałęzienia drzewka
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] (temat 4) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Paweł: trzy klasy podstawowe — Wojownik, Zwiadowca, Mag; w pewnym miejscu drzewka umiejętności gracz wybiera specjalizację (np. Wojownik → Berserker albo Paladyn; Mag → mroczny czarownik). Karol: ok. Wcześniej w tej samej rozmowie Paweł wolał brak sztywnych klas i podział tylko po rodzaju broni — nie rozstrzygnięto, czy klasa wiąże się z bronią. Powstało na prośbę Karola o osobne pytanie o klasach (pytanie 35). Dotyka D-003 ([[Rycerz]] i [[Kot-Mag]] jako główne postacie — wzór dla Wojownika i Maga?) oraz propozycji [[Selektor bohatera]] (rasa + klasa); D-047 zakłada jedno drzewko dla klas z jedną cechą klasy. Zob. [[System RPG]], [[Pytania otwarte]] #35.

### D-055 Drzewko umiejętności: osobne na klasę, pasywki procentowe, 0–3 sloty umiejętności, jedno okno przy ekwipunku
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (2) — zapis ustaleń]] (temat 4) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Wariant z sesji, inny niż D-047: każda klasa ma własne drzewko (Karol), a w nim specjalizacje z D-054. Węzły dają stałe bonusy procentowe (siła, kondycja i życie, szczęście — także do zdarzeń losowych — oraz zniżki w sklepach, np. −2%) i umiejętności aktywne do walki (np. cięcie Wojownika za 200% obrażeń, uderzenie z góry z szansą na krytyk, cios spowalniający i zdzierający pancerz); gracz dobiera je pod swój build. Sloty umiejętności odblokowuje drzewko: na start 0, potem 1 i 2, maksymalnie 3 (Karol; Paweł: jedna na walkę). Okno: jeden przycisk przy bohaterze, koło zakładki ekwipunku, z sekcjami gracz / pety / karczma / Twierdza (Paweł; Karol zgadza się). Nie padło: za co kupuje się węzły (D-039: Diamenty; D-047: punkt talentu + Diamenty), piętra i poziomy, jak umiejętności działają w walce liczonej automatycznie (D-016). Odpowiada wariantowi (c) z pytania 34; rozstrzygnąć razem z D-047. Zob. [[Drzewko umiejętności postaci]], [[Pytania otwarte]] #34.

### D-056 Drzewka umiejętności: trzy sekcje — gracz, pety (jedno ogólne), Twierdza; bez karczmy
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 1) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Okno drzewek ma trzy sekcje: **gracz** (procentowe premie do statystyk, pasywny dochód Złota i doświadczenia, szczęście — także do dropu przedmiotów i zadań — oraz umiejętności z D-055), **pety** (jedno wspólne drzewko: szybkość wyklucia, szczęście do jajek, otwieranie kilku jajek naraz, więcej petów przy graczu, +% do statystyk wszystkich petów) i **Twierdza** (procent wydajności konkretnego budynku — kopalnie, drwal, kamień — oraz większe przyrosty z Training Center i +% generowanego doświadczenia; budynek daje bazę, drzewko ją mnoży). Sekcja karczmy z D-055 odpada (Paweł; Karol zgodził się). Z sesji: Karol — „wcześniej mówiliśmy, że każdy pet ma swoje drzewko, ale z tego zrezygnowaliśmy”; Paweł — osobne drzewko na peta to za dużo. Karol o drzewku Twierdzy: „tu będzie musiała wejść matematyka”, żeby mnożnik z drzewka razy ulepszenie budynku nie wymknął się z balansu — liczby do kalkulatora. Zmienia zatwierdzoną D-039 w punkcie „każdy pet ma własne drzewko” (zatwierdzenie oznacza nową decyzję zastępującą ten punkt) i zatwierdzoną z dwoma podpisami D-055 w liczbie sekcji okna (cztery → trzy). Zob. [[Drzewko umiejętności postaci]], [[Pety]], [[Twierdza (Tycoon)]], [[Pytania otwarte]] #34.

### D-057 Węzły drzewek za Gemy (walutę premium), bez punktów talentu; poziom daje sklep, punkty statystyk i strefy
✅ zatwierdzona · game design / monetyzacja · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 1) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Węzły drzewek kupuje się za walutę premium (w rozmowie „Gemy” — to samo, co Diamenty z D-038 i Magiczne Kryształy z D-031; nazwa: pytanie 6), **bez punktów talentu** (Paweł: „bez skill pointów”; Karol: „za Gemy”). Gemy rzadko wypadają też z potworów (Karol, jak w grach Roblox). Poziom postaci (EXP) daje coś innego: dostęp do lepszych przedmiotów w sklepie, stały przyrost statystyk co poziom, podstawowe punkty statystyk do rozdania i dostęp do stref od poziomu (Paweł; Karol: „procenty to drzewko, punkty to statystyki”). Zgodne z tym, co stało się po sesji w panelu: D-047 odrzucona z dopiskiem Karola „płacimy jedynie Diamentami za drzewko” (Paweł potwierdził), D-055 (drzewko na klasę) zatwierdzona z dwoma podpisami — D-057 dopisuje do tego źródło Gemów i rolę poziomu. Gałęzie i piętra z D-047 przepadają razem z nią, chyba że wrócą osobną propozycją. Skutek: drzewko jest ujściem waluty premium w całości, więc tempo zdobywania Gemów w grze decyduje, czy gracz bez płacenia ma do niego dostęp (D-035: próg progresji; D-036: „trochę pay-to-win”). Zob. [[Drzewko umiejętności postaci]], [[Pytania otwarte]] #34, #6.

### D-058 Pety: jeden stały skill, poziom i ewolucja za shardy peta, Shard Ewolucji i tokeny krainy
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 2) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Każdy typ peta ma **jedną stałą umiejętność** (piesek — ugryzienie; legendarny pet — np. wzmocnienie obrażeń na kilka tur); bez losowania skilli, bez puli skilli na rzadkość i bez przenoszenia skilli między petami (Karol; Paweł zrezygnował ze swoich wariantów). Pet ma poziom (Karol: robocze maks. 30) zdobywany karmieniem (D-052); poziom otwiera **ewolucje** — pet zmienia wygląd i wzmacnia skill (Karol: piesek na maksymalnej ewolucji staje się Cerberem). Ewolucja kosztuje: **shardy tego peta** (skrapowanie kopii — jedna kopia daje jeden shard), **Shard Ewolucji** (jeden na ewolucję; rzadki drop ze strażnika biomu, z szansą) i **tokeny krainy**, z której pet pochodzi (ręczne zabijanie potworów w krainie; mniej z walk petów). Dzięki temu duplikaty z jajek się nie marnują (obaj). Nierozstrzygnięte: ewolucje dla wszystkich petów (Karol) czy tylko dla lepszych (Paweł); liczby. Zmienia zatwierdzoną D-040 w części „osobna waluta petów na drzewka petów” (teraz tokeny krain i shardy na ewolucje) i D-039 (drzewko każdego peta — razem z D-056); nazwa „Łapki” z D-046 traci przedmiot albo może nazwać tokeny. Uzupełnia zatwierdzoną D-052 (karmienie). Zob. [[Pety]], [[Pytania otwarte]] #41.

### D-059 Pety nie walczą z graczem: pasywne premie dla gracza i własne strefy walk petów; ok. 10 petów na biom
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (tematy 2 i 3) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Pety chodzą za graczem i dają mu **bazowe, pasywne premie do statystyk**, ale nie biorą udziału w jego walce (Paweł; Karol myślał, że biją się razem z graczem, przyjął model Pawła). Pety mają **własne środowiska walk** — strefy z przeciwnikami-petami (wejście koło portali do dungeonów albo wydzielone miejsce w biomie); pokonany pet daje jedzenie (karmienie → poziom), tokeny krainy i doświadczenie peta. Każdy biom ma własne pety: ok. **10 na biom** (Karol chciał 20, Paweł: 10–11 to już dużo modeli), np. dwa jajka po 5–6 petów; z jednego jajka wykluwa się jeden pet, losowany z puli jajka z jawnymi szansami. Zgodne z kanonem [[Pety]] (towarzyszą, modyfikują statystyki, pasywne ekspedycje). Dla walki liczonej na serwerze (D-016) oznacza, że pet jest tylko mnożnikiem statystyk gracza. Zob. [[Pety]], [[Pytania otwarte]] #41.

### D-060 Jajka: inkubatory w każdym biomie, wyklucie od razu z animacją, bez jajek z potworów — do playtestu
✅ zatwierdzona · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 4) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Jajka stoją w inkubatorach w wyznaczonym miejscu każdego biomu; gracz podchodzi, płaci Złotem, klika kilka razy i po animacji rozbijania (bazowo 3–10 s, skracanej drzewkiem petów z D-056) od razu dostaje peta. **Jajka nie wypadają z potworów** i nie wykluwają się na czas (model Pawła z gier Roblox; Karol wolał rzadki drop i wyklucie 10–15 minut, ale: „zdam się na ciebie, na razie zostajemy przy twoim”). Playtest przed premierą rozstrzygnie, czy dodać drop z potworów. **Zmienia zatwierdzoną z dwoma podpisami D-052** w punkcie „bardzo rzadko jajka wypadają też z potworów” — zatwierdzenie oznacza nową decyzję zastępującą ten punkt; reszta D-052 (zestawy jajek na strefę, ceny, karmienie) bez zmian, a „stajnia w mieście” z D-052 staje się inkubatorami pierwszego biomu. Wylęgarnia na czas z rozmowy 12.11 jest nieaktualna. Szanse z jajek jawne przed zakupem (D-052). Zob. [[Pety]], [[Pytania otwarte]] #42.
Uzasadnienie — Karol Balucki, 2026-11-14: Tak. Dodatkowe w bundlach też dajemy oferty na jajka

### D-061 Biomy: osiem na start — las, bagno, dżungla, pustynia, góry z tundrą, lodowiec, wulkaniczny, kryształowy
💡 propozycja · game design / świat · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 3)
Kolejność odblokowania poziomem: **las → bagno → dżungla → pustynia → góry z tundrą (jeden biom) → lodowiec → wulkaniczny → kryształowy** (ostatni; odblokowuje kopalnie kryształów w Twierdzy z D-049). Paweł: „na początek osiem by pykło”; od prostych biomów do coraz bardziej fantastycznych. Dziewiąty, ciemny kryształ / obsydian — pod znakiem zapytania; dalsze biomy po premierze (inspiracje z rozmowy: kryształowe jaskinie, kaniony, czerwona pustynia, cmentarzysko, bioluminescencyjna dżungla). Każdy biom ma własnych przeciwników, **strażnika biomu** (specjalny przeciwnik; drop Shardu Ewolucji z D-058) i inkubatory z petami tego biomu (ok. 10, D-059). Zaklinacz z D-051 stoi na pustyni, żeby ulepszanie odblokowało się przed ostatnim biomem (Karol). Wypełnia „kilka biomów (lista do ustalenia)” z zatwierdzonej D-035; osiem biomów na premierę to dużo treści — do zestawienia z planem produkcji ([[Roadmapa]]). Zob. [[Pytania otwarte]] #32, [[Mapa teleportacji]].

### D-062 Model statystyk: Pancerz punktowy, Inteligencja jako moc umiejętności i odporność na magię, Zręczność jako unik z limitem klasy, blok z tarczy
💡 propozycja · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 6)
Sześć statystyk jak w [[System RPG]] i w kodzie: **Siła** — obrażenia zwykłych ciosów; **Kondycja (Życie)** — pula zdrowia; **Inteligencja** — moc umiejętności (umiejętności skalują się z Inteligencji, nie z Siły — Paweł) **i** odporność na magię (Karol, wzór z LoL: przeciw magom nie liczy się Pancerz; Paweł: „ile masz Inteligencji, tyle mniej mag bije”), dzięki czemu Wojownik też ma powód ją rozwijać; **Zręczność** — szansa na unik z limitem zależnym od klasy (Zwiadowca od 25% do maks. 50%, inne klasy od 0 i niżej — Paweł, Karol: „ok”); **Szczęście** — szansa na krytyk; **Pancerz** — **wartość punktowa odejmowana od zwykłego ciosu**, nie procent (Karol: procent z limitem „będzie zbroken” i zabija poczucie postępu, procenty są w drzewku; Paweł chciał limit 25–50%, przyjął przykład: 1000 Pancerza odejmuje 1000 z 10 000 obrażeń). **Blok** to cecha tarczy jako przedmiotu ze stałą szansą; slot tarczy ma tylko Wojownik (Paweł, wzór z S&F; Karol: „fajne”). Nierozstrzygnięte: czy Wojownik z tarczą i unikiem nie jest za mocny (Paweł) — Karol proponuje osłabienie w drzewku Wojownika albo o połowę mniejszy przyrost z Zręczności, Paweł: ograniczać drzewka nie ma sensu, skoro Zręczność trenuje się za monety (pytanie 40); czy rozdzielać Pancerz i Obronę oraz dodawać Przebicie i Odporność magiczną — Karol sam zwątpił, bo prowadzi to do kontrowania klas (pytanie 39). Paweł zauważył ryzyko buildu „Wojownik z samą Inteligencją bijący tylko umiejętnościami”. Dotyczy walki liczonej na serwerze (D-016) i klas z kanonu D-054. Zob. [[System RPG]], [[Pytania otwarte]] #17, #39, #40.

### D-063 Training Center: jeden budynek z wyborem mini-gry, od pierwszego poziomu razem z działką
💡 propozycja · game design · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 6)
Doprecyzowuje zatwierdzoną z dwoma podpisami D-050: zamiast sześciu stref — **jeden budynek** Training Center, w którym okno wyboru statystyki przenosi gracza do odpowiedniej mini-gry (Paweł; Karol: ok). Działka Twierdzy i Training Center są dostępne **od pierwszego poziomu** (Karol stwierdził, Paweł potwierdził Training Center od razu) — odpowiada na pierwszą część pytania 9 (12.11 mówiono o ok. 25. poziomie). Mini-gry 3D, interaktywne, nie za trudne, logicznie związane ze statystyką (wzór: Swords & Souls; przykład Pawła: rozbijanie mieczem rzucanych przedmiotów klikaniem strzałek w kierunku przedmiotu — Siła). **Nierozstrzygnięte: pięć czy sześć mini-gier** — Paweł: bez Pancerza (daje go ekwipunek, pełny zestaw i tak dobija limit); Karol: Pancerz też trenujemy, tak jak Siłę mimo broni (pytanie 39). Zatwierdzenie w części „jeden budynek” zastępuje „sześć stref” z D-050; „bez trybu AFK — na razie” z uzasadnienia Karola przy D-050 zostaje. Zob. [[Twierdza (Tycoon)]], [[System RPG]], [[Pytania otwarte]] #9, #39.

### D-064 Mapa teleportacji: widok z lotu ptaka z pinami dostępnych lokacji
💡 propozycja · UI / świat · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 8)
Po kliknięciu Teleport w [[HUD]] kamera odjeżdża zza pleców gracza i pokazuje miasto z lotu ptaka (krótki przelot); na widoku są piny przypięte do konkretnych lokacji (karczma, sklepy, Twierdza…), tylko dostępne dla tego gracza; klik pina teleportuje (Paweł; Karol: „jak w GTA V”). Zastępuje w [[Mapa teleportacji]] wygenerowaną grafikę mapy z ramką i siedmioma pinami widokiem z prawdziwej kamery na zbudowane miasteczko (D-041) — bez promptów Higgsfield na mapę, piny mogą zostać jako ikony. Lista lokacji nadal otwarta (pytania 5 i 28); przy ośmiu biomach (D-061) mapa musi też obsłużyć wejścia do biomów. Do sprawdzenia: wydajność i czytelność przelotu na telefonie. Zob. [[Mapa teleportacji]], [[Pytania otwarte]] #5, #28.

### D-065 Postacie i pety projektuje Karol w Blenderze
✅ zatwierdzona · 3D / pipeline · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 10) · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14
Paweł: „Blender, zdecydowanie — ładniejszy był ten ludek”; Karol: projekty postaci i petów robi on w Blenderze (ma Blendera), Paweł podrzuca pomysły; „postawiliśmy raczej na Blendera, bo ładnie wyglądało”. **Sprzeczne z odpowiedzią Karola na pytanie 24 z tego samego dnia** (11:52, akceptacja raportu „Rycerz w trzech wersjach”: klocki Roblox główną drogą, siatki z Blendera tylko tam, gdzie pomiar na telefonie pokaże potrzebę) i z zatwierdzoną D-029 („w Roblox najpierw postacie z klocków”). Zatwierdzenie oznacza: siatki z Blendera (import FBX sprawdzony 13.11 na Rycerzu) jako główna droga dla postaci i petów; miasteczko i mapy z klocków (D-017, D-025) bez zmian — na sesji o nich nie mówiono. Kto publikuje siatki i animacje: grupa Roblox (D-044). Zob. [[Postacie 3D — Blender i Roblox]], [[Pytania otwarte]] #24.
Uzasadnienie — Karol Balucki, 2026-11-14: Tak to ja (Karol) Pomyliłem twoją próbkę z Blendera vs Rolbox - Blender wyglądał bardziej dopracowany

### D-066 Sklep za Robuxy: paczki jajek i skrzynki z jawnymi szansami, game passy, darmowy pet
💡 propozycja · monetyzacja / zgodność · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 5)
Karol: sklep za Robuxy „takim samym modelem”, jak w dochodowych grach Roblox, które pokazał Paweł. Paweł wylicza: paczki jajek (np. 10 jajek za ok. 800 Robuxów z jawną szansą, np. 10%, na najlepszego peta), waluta, lepsze przedmioty, game passy (podwójna waluta, podwójna moc treningu), darmowy pet do odebrania; możliwa skrzynka (lootbox) z jawnymi szansami. Obaj uznali losowania z jawnymi szansami za dopuszczalne, powołując się na wyjaśnienie agenta (pytanie 30). **Konflikt z zatwierdzoną D-031** („nigdy koła, jajek ani odświeżenia sklepu” za walutę premium; losowania tylko za Złoto i tokeny) — zatwierdzenie oznacza nową decyzję zastępującą ten punkt D-031; spójne z D-036 (game passy, paczki) i D-037 (bilety za Robuxy). Warunki Roblox dla płatnych przedmiotów losowych (lista nagród i dokładne szanse przed zakupem, `PolicyService`, zmienione szanse przy ulepszeniach szczęścia) z pytania 30 obowiązują. Karol: „zostajemy przy koncepcji” złożonej gry mimo sukcesu prostych; Paweł: po premierze ocena, ewentualnie drugi, prostszy projekt. Zob. [[Retencja i monetyzacja — co wolno i co działa]], [[Pytania otwarte]] #43, #12.

### D-067 Gildie i wojny gildii po premierze
💡 propozycja · roadmapa · 2026-11-14 · źródło: [[Sesja główna 2026-11-14 (3) — zapis ustaleń]] (temat 7)
Gildii nie ma w pierwszej wersji (Karol: „na razie gildii nie będziemy robić”; Paweł: zostawić na później, nie w podstawowej implementacji). Wojny gildii między światami z rozmowy 12.11 i napady na twierdze (odrzucone na drugiej sesji) — nie na premierę. Doprecyzowuje zatwierdzoną D-035 („gildie nie padły”) i zamyka drugą część pytania 32. Skutek: budynek gildyjny z listy D-049 „do wersji początkowej” też po premierze, a przycisk „Guilds” w wdrożonym [[HUD]] (pytanie 5) nie ma na start treści. Zob. [[Roadmapa]], [[Pytania otwarte]] #32.

### D-068 Walka: długość wyłącznie ze statystyk i losowości
✅ zatwierdzona · game design · 2026-11-14 · źródło: rozmowa Karola z Claude Code 14.11 (korekta zlecenia na silnik walki v2) · zdecydował: Karol Balucki 2026-11-14
Walka trwa, aż życie jednej strony spadnie do zera, a jej długość wynika tylko ze statystyk i losowości. Rodzaj przeciwnika jej nie wyznacza: zwykły potwór, który zrobi dziesięć uników z rzędu, daje długą walkę, a boss, który dostanie potężnego krytyka, może paść od jednego ciosu (Karol: „wszystko zależy od RNG”). Żadnych reguł sztucznie skracających ani wydłużających walkę — prototyp z 13.11 miał sztywne 4–6 wymian i cios rozstrzygający; tego nie przenosimy. Animacja jest przy każdej walce (uzasadnienie odrzucenia D-033). Zgodne z ustaleniem z pierwszej sesji 14.11 (temat 2). Realizuje to silnik walki v2 (`src/server/Walka/`, `tools/walka/`). Zob. [[System RPG]], [[Sesja główna 2026-11-14 — zapis ustaleń]].

### D-069 Klasy zbalansowane, bez kontrowania
✅ zatwierdzona · game design · 2026-11-14 · źródło: rozmowa Karola z Claude Code 14.11 · zdecydował: Karol Balucki 2026-11-14
Nie ma klasy, która z założenia wygrywa z inną (np. Zwiadowca kontrujący Maga). Wojownik, Zwiadowca i Mag (D-054) różnią się stylem gry, nie skutecznością: przy tym samym poziomie i tej samej puli punktów statystyk każda klasa ma podobne wyniki z każdym przeciwnikiem, a pojedynek klasa na klasę wychodzi blisko 50%. Tabela balansu z symulacji silnika ma to wykazać — nie pokazuje, „kto kogo kontruje”. Dotyczy modelu statystyk z D-062 (magia omijająca Pancerz nie może zrobić z Maga kontry na Wojownika) i [[Arena (PvP)]]. Zob. [[System RPG]].

---
*Nowa decyzja: skopiuj szablon [[Decyzja]] (folder Szablony) albo dopisz sekcję `### D-0XX` na końcu.*
