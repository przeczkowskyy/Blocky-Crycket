---
status: kanon
tags: [produkcja, dziennik]
---
# Dziennik zmian

Najnowsze na górze. Każdy wpis: data, kto, co się zmieniło, które pliki i notatki.

## 2026-11-14 · Claude Code (scalenie z main Karola)
- Scalone 7 commitów Karola (decyzje D-027/D-028/D-030, szablony Glossy Ink w skillu `/asset`, import siatek, odpowiedzi w panelu). W skillu `/asset` przyjęta wersja Karola, dopisany tylko model **Nano Banana 2.1** (`prompt-templates.md`, `SKILL.md`, `project-rules.md`, [[Pipeline assetów]]).
- Numeracja pytań wg Karola: mapa teleportacji #28 (opis zaktualizowany: Kuźnia zamiast Targu, ramka), Rybki #29. Odwołania poprawione w [[Mapa teleportacji]], [[HUD]], [[Zadania]], `DOKUMENTACJA.md`.

## 2026-11-14 · Claude Code (HUD: trzecia waluta — Rybki)
- Na polecenie Game Directora: w panelu gracza trzeci wiersz pod Złotem i Diamentami, ikona złotej rybki (grafika od Game Directora, `assets/raw/Fish/source.png` → `assets/processed/Fish.png`, wycięte flood fill), ta sama pigułka z granatowym gradientem i złotym obrysem, licznik w kolorze `#FFA53D` (odróżnia się od żółtego złota).
- Figma: komponent `Player Panel` (14:145) powiększony do 300 px wysokości, nowe warstwy Fish Pill / Fish Pill Ink / Fish / Fish Icon (PNG) 30:111–30:114.
- Roblox: `src/gui/HUD.model.json` (FishPillInk, FishPill, Fish, FishIcon), `src/client/HUDClient.client.luau` (atrybut `Fish`, animowany licznik), `src/server/PlayerStatsDefaults.server.luau` (`Fish = 0`); to samo w miejscu z chmury przez MCP (skrypty w Studio były identyczne z gitem). Test Play: licznik „1 250” po zmianie atrybutu.
- Ikona wgrana po „tak” Game Directora: `rbxassetid://92474194471064` (manifest `Fish`: zatwierdzony, sha256, `in_roblox`), podpięta w `FishIcon` (plik i miejsce z chmury); test Play: wczytana. Rola Rybek: [[Pytania otwarte]] #29. Notatki: [[HUD]], [[Zadania]].

## 2026-11-14 · Claude Code (prompty Higgsfield: jeden format Glossy Ink)
- Na polecenie Game Directora szablony skilla `/asset` przepięte na [[Instrukcja promptów — Glossy Ink]]: stały początek, koniec i negative kopiowane 1:1, środki dla każdej kategorii (ikona, przycisk, przedmiot, pet, waluta, okno, arkusz przycisków, mapa, tło). Dodana reguła projektu: napisy natywnie, więc w obrazie puste tabliczki (`NO text`).
- Domyślny model Higgsfield zapisany w skillu i sejfie: **Nano Banana 2.1** (`nano_banana_2_1`, nie GPT Image). Model nie ma pola negative, więc negative idzie na końcu promptu. Referencja stylu zawsze `assets/refs/KeyArt_ref.jpg`.
- [[Mapa teleportacji]]: prompty przepisane na Glossy Ink według promptu-wytycznej Game Directora (układ lokacji, Kuźnia zamiast Targu, cienka ramka), piny jako jeden arkusz 7 przycisków; tabela lokacji zaktualizowana.
- `style-guide.md` skilla: Glossy Ink ma pierwszeństwo, w nowych promptach bez pixel-artu.
- Pliki: `.claude/skills/asset/SKILL.md`, `references/prompt-templates.md`, `references/style-guide.md`, `references/project-rules.md`; notatki: [[Instrukcja promptów — Glossy Ink]], [[Pipeline assetów]], [[Mapa teleportacji]], [[Pytania otwarte]] (#22, #28), [[Zadania]]; `DOKUMENTACJA.md`. Po scaleniu z pracą Karola (D-027 zatwierdzona przez niego 13.11) w skillu zostały jego szablony, a z tej zmiany doszły model Nano Banana 2.1 i nowe prompty mapy.

## 2026-11-14 · Claude Code (okno ekwipunku: wyśrodkowanie zakładek, pola podpisów)
- Napisy zakładek wyśrodkowane na kolorowej części zakładki, nie na całym obrazku (`tools/eq_slice.py` mierzy korpus w `EqTab*.png`); OTHERS był przesunięty w prawo (korpus ma środek na 46% obrazka), AMULETS/WEAPONS o 1–2 px.
- Pola podpisów kart poszerzone (od wewnętrznego obrysu do „+”), żeby „DMG RED 25%” miał zapas przy 15 px. Wszystkie podpisy: 15 px (pomiar w Play).
- Zmienione w plikach (`layout.json`, `EquipmentPanel.model.json`) i w miejscu z chmury przez MCP (punkt historii). Grafiki bez zmian.

## 2026-11-14 · Claude Code (okno ekwipunku: rozmiary napisów 15/16/20)
- Na prośbę Game Directora: napisy statystyk (nazwa, wartość, podpis) max 15 px, zakładki postaci (ATTRIBUTES…) max 16 px, zakładki plecaka (WEAPONS…) max 20 px (`UITextSizeConstraint.MaxTextSize`, nadal skalowane w dół na małych ekranach). Zmienione w `tools/eq_build_gui.py` → `src/gui/EquipmentPanel.model.json` i w miejscu z chmury przez MCP (punkt historii). Pomiar w Play: 15 / 16 / 20 px.

## 2026-11-14 · Claude Code (okno ekwipunku na serwerze: rozmiar napisów)
- W miejscu z chmury (Team Create, place 129485428021967) wszystkie 29 napisów `StarterGui.EquipmentPanel` miało `TextScaled = false` (stały rozmiar 8 px) – napisy malutkie, inaczej niż w plikach i w Figmie. HUD bez zmian. Przyczyna nieznana (pliki w repo mają `TextScaled = true`).
- Naprawione w Studio przez MCP (punkt historii „EquipmentPanel: TextScaled jak w plikach”, tylko nasze okno). Zrzut z Play: napisy jak na grafice. `EqBg3` v5 przeszedł moderację i wyświetla się.
- Na przyszłość: połączyć Rojo z miejscem z chmury, żeby GUI szło z plików.

## 2026-11-13 · Claude Code (połączenie z gałęzią Karola)
- Gałąź `karol/panel-wiedza-demo` (31 commitów: Krzywe Miasteczko, postacie, panel zespołu, telemetria, sejf) połączona lokalnie z `main` (commit `11c4b4c`, niewypchnięty). Konflikty w sejfie rozwiązane przez zachowanie obu stron; pytanie o mapę teleportacji przeniesione z #7 na #25 (po scaleniu u Karola: #28).
- Miasto zbudowane w otwartym Studio skryptem Karola: `python tools/studio_buduj.py swiat/krzywe_miasteczko/czesci.json` → `Workspace/KrzyweMiasteczko` (5259 części). Uwaga: Studio miało otwarty lokalny `Blocky&Crycket.rbxl`, nie miejsce z chmury.

## 2026-11-13 · Panel (ludzie)
- Karol Balucki: decyzja D-007 zatwierdzona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-011 zatwierdzona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-012 zatwierdzona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-014 odrzucona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-015 zatwierdzona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-016 zatwierdzona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-017 zatwierdzona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-022 odrzucona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-023 zatwierdzona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-024 odrzucona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-009 odrzucona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-013 odrzucona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-018 odrzucona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-021 odrzucona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-026 zatwierdzona ([[Rejestr decyzji]])
- Karol Balucki: decyzja D-029 zatwierdzona ([[Rejestr decyzji]])

## 2026-11-13 · Claude Code u Karola (wieczór: decyzje Karola, panel jako miejsce pracy, import siatek)
- **Sprostowanie podpisów:** D-030 i D-027 były przez kilkadziesiąt minut podpisane „Karol i Paweł”. To decyzje samego Karola, więc podpisy poprawiono, a potwierdzenie zasady równych praw przez Pawła czeka w pytaniu 27.
- **Kto zatwierdza:** Karol i Paweł mają takie same prawa, wystarczy decyzja jednego, a każda decyzja zostaje w logach. Nowa decyzja D-030 w [[Rejestr decyzji]] (zdecydował Karol, odpowiedź na pytanie 15 w [[Pytania otwarte]]); zasada wpisana do [[Jak prowadzimy sejf]] i `CLAUDE.md`.
- **Glossy Ink:** D-027 zatwierdzona (Karol, pytanie 22). Zastępuje prefiks z D-001 (teraz ♻️) oraz zapisy o pixel-arcie ikon i płaskim interfejsie z D-002; reszta D-002 obowiązuje. Linki w [[00 Start]] zaktualizowane; szablony skilla `/asset` i notatki stylu są przepinane osobno.
- **Panel jako miejsce pracy:** D-028 zatwierdzona (Karol, pytanie 23). Zapis do sejfu z panelu włączony na komputerze Karola bez dodatkowych ograniczeń dla wejść z kodem dostępu; utworzony klucz zatwierdzania. Tunel zostaje otwarty, prywatny Warsztat Karola zostaje odpięty.
- **Walka:** Karol obejrzał test w `Workspace/TestWalki` i ocenił walkę jako bardzo wciągającą mimo drobnych błędów. Propozycja D-024 zmieniona z „cutscenka tylko przy bossie” na „walka w każdej potyczce, w trzech długościach”; nadal 💡, czeka na decyzję i na listę błędów.
- **Import siatek sprawdzony:** po zatwierdzeniu folderu w Studio plik `rycerz.fbx` został wgrany na konto Karola (zasób Model, moderacja zatwierdziła od razu) i wstawiony do `Workspace/TestPostaci` jako „Rycerz Blocky (import FBX)”. Roblox zrobił z niego postać R15: 15 części-siatek, `Humanoid`, komplet punktów zaczepienia, skala 1:1, kolory z tekstury-palety poprawne. Miecz i animacje nie wchodzą razem z modelem. Wynik: `swiat/postacie/wynik/_roblox/import_rycerz_fbx.json` i dwa zrzuty.
- **Panel po D-030:** status decyzji zmienia osoba przy komputerze z panelem albo osoba z kluczem zatwierdzania (dawny klucz Game Directora — plik, ciasteczko i link działają dalej). Podpis w rejestrze to `zdecydował: <imię> <data>`, bez słów „Game Director”; decyzja wymaga imienia zapisanego w Ustawieniach panelu. Niezależny przegląd zgłosił dwie uwagi, obie poprawione; 221 testów. Pliki: `panel/bc/`, `panel/serwer.py`, `panel/static/`, `panel/testy/`, `panel/README.md`, `panel/INSTALACJA.md`, skill `panel`, notatka [[Panel zespołu]]. Panel zrestartowany na nowym kodzie.
- **Glossy Ink wdrożone w skillu `/asset`:** każdy szablon ma stały początek, zmienny środek, stały koniec i osobny negative prompt, zgodne znak w znak z oryginałem w `Źródła/`. Notatki: [[Instrukcja promptów — Glossy Ink]] (kanon), [[Style Lock]] (zastąpiony, zostaje jako historia), [[Kierunek artystyczny]], [[Pipeline assetów]], [[Narzędzia]]. Sprostowanie po niezależnym przeglądzie: D-027 zastępuje w Kierunku artystycznym tylko pixel-art ikon i „płaski (flat design)” — reszta opisu interfejsu obowiązuje. Szablonów nie sprawdzano w generatorze. Nowe pytania 25 i 26 w [[Pytania otwarte]].
- **Odpowiedzi Karola w panelu (18:49–18:53):** raport o postaciach z klocków zaakceptowany; przymierzalnia „do poprawy” z wymaganiem, żeby broń trzymana w ręku nie nachodziła na twarz w animacjach i po wygranej walce; styl Krzywego Miasteczka „bardzo dobry”, decyzja czeka na Pawła; walka „wygląda świetnie”, cutscenka powinna być przy każdej walce, decyzja czeka na Pawła.
- **Zadania:** [[Zadania]] zaktualizowane.
- **GitHub:** Paweł dodał Karola jako współpracownika; gałąź `karol/panel-wiedza-demo` wypchnięta ok. 19:15 i scalona z `main` razem z commitem Pawła (okno ekwipunku, mapa teleportacji; jego pytanie o mapę ma numer 28).
- **Runda decyzji Karola w panelu (ok. 19:45–20:15):** zatwierdzone D-007, D-011, D-012, D-015, D-016, D-017, D-023, D-026, D-029; odrzucone albo odłożone D-009, D-013, D-014, D-018, D-021, D-022, D-024 — uzasadnienia są w [[Rejestr decyzji]]. D-006 Karol zatwierdził w rozmowie z Claude Code po wyjaśnieniu, że to zasada techniczna.
- **Sesje główne:** nowa notatka [[Sesje główne]] z tematami na długie rozmowy głosowe Karola i Pawła (karczma, walka 3D, pętla bez czekania, czym jest gra w jednym zdaniu, zakres pierwszego wydania, monetyzacja, treści dla wszystkich). Temat o myśli przewodniej v2 opisany prostymi słowami; stanowisko Karola: raczej nie. Link w [[00 Start]].
- **Pytania rozstrzygnięte decyzjami:** w [[Pytania otwarte]] dopisane odpowiedzi (podpis „Claude Code”) do pytań 4, 7, 8, 10, 11, 12, 16, 18, 19, 20 i 24 — każda mówi, która decyzja Karola je rozstrzyga albo że temat idzie na sesję główną.
- **Dwa raporty-porównania w panelu** na prośbę Karola: postać w trzech wersjach (Blender, klocki Roblox, siatka w Roblox) oraz dwa style mapy obok siebie.
- **Zlecenia Karola na panel:** zakładka „Sesja” (rozmowa głosowa, agent słucha, transkrypcja, notatki) — w budowie; połączenie Planu i Raportów w jedną zakładkę bez dubli, czytelniejszy Pulpit, lista aktywnych osób — w kolejce ([[Zadania]]).
- **Zakładka „Sesja” w panelu (zlecenie Karola):** rozmowa głosowa w panelu do 6 osób (głos bezpośrednio między przeglądarkami), przycisk „Agent słucha” z czerwonym znacznikiem u wszystkich, nagrywanie własnego mikrofonu w odcinkach 12 s, lokalna transkrypcja tym samym silnikiem co głosówki, notatki agenta co 5 minut i na żądanie, „Zakończ sesję i spisz ustalenia” (ustalenia trafiają do sejfu jako propozycje, agent niczego nie zatwierdza) oraz lista tematów z [[Sesje główne]] z dodawaniem i odhaczaniem. Nagrania są kasowane po spisaniu, a pełna transkrypcja zostaje w danych lokalnych, poza repozytorium. Niezależny przegląd zgłosił siedem uwag (m.in. dostęp gościa do dawnych sesji, kolejność sygnałów połączenia, gubiony ostatni kawałek nagrania) — wszystkie poprawione; 266 testów, w tym test z dwiema przeglądarkami. Próba prawdziwej transkrypcji na zdaniu z syntezatora mowy: 11 sekund dźwięku spisane w 0,6 s na karcie graficznej, tekst poprawny. Nie sprawdzono: rozmowy dwóch osób z dwóch domów, telefonów, prawdziwego agenta przy notatkach. Pliki: `panel/bc/sesje.py`, `panel/static/widoki/sesja.js`, `panel/static/wspolne/rozmowa.js`, zmiany w `panel/bc/{glos,agent,zapis,sejf,obecnosc,rdzen,statyczny}.py`, testy, `panel/README.md`, `panel/INSTALACJA.md`, skill `panel`, notatka [[Panel zespołu]]. Panel zrestartowany.
- **Dysk i przerwy:** sesję dwa razy przerwał brak pamięci przy pełnym dysku; po czyszczeniu za zgodą Karola wolne jest ponad 100 GB. Sprawdzenie animacji na zaimportowanym Rycerzu wstrzymane do ponownego otwarcia Roblox Studio.

## 2026-11-13 · Claude Code u Karola (noc i poranek: diagnoza, propozycja v2, kolejka zadań, instrukcja stylu)
- **Diagnoza całego pomysłu** (8 perspektyw, niezależna weryfikacja liczb w źródłach): ocena dziś 3,8/10, dziesięć przyczyn źródłowych i twarde ograniczenia platformy, których nie było w notatkach z 12.11 (nową grę widzą najpierw gracze 16+, odniesienia do alkoholu tylko w grach 18+, zakres płatnej losowości). Notatka [[Diagnoza pomysłu 2026-11-13]].
- **Propozycja v2 „krzywy montaż”** po panelu czterech koncepcji, dwóch sędziów i czerwonym zespole: [[Myśl przewodnia v2]], [[Systemy gry v2]], [[Psychologia gracza v2]], [[Karta ocen v2 i plan sprawdzenia]], [[Specyfikacja v2.1 — Krzywa Banda]], tablica `Gra/Pętla gry v2.canvas`. Uczciwa ocena po poprawkach: 6,0/10; wyżej tylko po pomiarze z graczami. Nic nie jest kanonem.
- **Rejestry:** propozycje D-019–D-026 i D-027 (🕓) w [[Rejestr decyzji]], pytania 16–22 w [[Pytania otwarte]], nowe pozycje w [[Zadania]], linki w [[00 Start]].
- **Instrukcja stylu Game Directora** (przekazana przez Karola 13.11): oryginał w `Źródła/Instrukcja stylu i promptowania (oryginał 2026-11-13).md`, notatka robocza [[Instrukcja promptów — Glossy Ink]], odsyłacz w [[Style Lock]]. Zastępuje prefiks z D-001 po formalnym potwierdzeniu (D-027).
- **Test cutscenki walki w samym Roblox:** `swiat/test_walki_roblox/` i kontener `Workspace/TestWalki` (serwer liczy walkę, klient odtwarza; POMIŃ, panel wyniku). Zweryfikowany niezależnie; pomiary z komputera, telefon niezmierzony. Wniosek jako propozycja D-024. Prototyp usunąć przed publikacją miejsca.
- **Panel:** zakładka Assety (rejestr grafik z `assets/manifest.json`) i sekcja „Telemetria gry” w Analityce; moduł `src/server/Telemetria` (bezwładny do włączenia) i notatka [[Telemetria gry]]. Po niezależnym przeglądzie 14 błędów poprawionych; 141 testów. Pierwsze prawdziwe uruchomienie tunelu (Cloudflare): zabezpieczenia sprawdzone od zewnątrz.
- **Mapy:** biblioteka v2 `swiat/biblioteka/` (krzywe bryły w układach lokalnych, obrys tuszem, podgląd w Blenderze), opcje w `tools/blender/klocki.py` i `tools/studio_buduj.py`, nowe `tools/studio_zrzuty.py`; migawka dema ze zrzutami z prawdziwego Studio. `rokit.toml` z Rojo 7.6.1 (instalacja Rokit po stronie ludzi).
- **Mapa v2 „Krzywe Miasteczko”** (`swiat/krzywe_miasteczko/`, `Workspace/KrzyweMiasteczko`, 5259 części): 12 budynków w stylu komiksowym, rynek, mur, tło; dwóch niezależnych krytyków i 25 wprowadzonych poprawek; kontrola kolizji w Studio bez zastrzeżeń. Propozycja D-025, opis w [[Klocki — Blender i Roblox]].
- **Panel jako miejsce pracy** (propozycja D-028, pytanie 23): zapis do sejfu z panelu — odpowiedzi na pytania, zadania, statusy decyzji z kluczem Game Directora, ślad w tym dzienniku. Po niezależnym przeglądzie 16 uwag poprawionych; zapis wyłączony do wspólnej decyzji.
- **Postacie 3D** (`swiat/postacie/`, propozycja D-029, pytanie 24): biblioteka postaci z kodu (Blender w tle), Rycerz, Kot-Mag, Karczmarz, pies, slime, smok, trzy zestawy ekwipunku i 8 broni; dwóch krytyków (wygląd 6,5/10, technika 6/10) i runda poprawek. Te same dane zbudowane w Studio jako postacie z części Roblox ze stawami (`Workspace/TestPostaci`: sześć postaci to 658 części i 20 klipów, z trzema manekinami 1781 części i 32 klipy) — bez wgrywania zasobów; wszystkie klipy sprawdzone w Animatorze w trybie Edit (pozy stawów zgodne z danymi) i odtwarzane w trybie Play w Studio. Import siatek nie sprawdzony: Studio wymaga zatwierdzenia folderu przez człowieka. Do tego trzy manekiny z zestawami ekwipunku i przymierzalnia: w trybie Play w Studio zestaw z klocków zakłada się na awatar gracza (sprawdzone na zestawach Rekrut, Rycerz, Mag), oraz pety idące za graczem po naciśnięciu E (pies, slime, smok; odesłanie klawiszem R). Po niezależnym przeglądzie kodu poprawiono dziewięć usterek w ścieżkach błędów, a kontrola twierdzeń — osiem nieścisłości w opisach. Notatka [[Postacie 3D — Blender i Roblox]].
- **Zauważone w Studio, nie nasze:** nowe `ServerScriptService.Server.StatPoints`, `ReplicatedStorage.Shared.Items` i zmiana w `EquipmentPanel` (praca Game Directora) — nietknięte; łączą się z pytaniem 17.

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

## 2026-11-12 · Claude Code u Karola (rozmowa, badania, panel zespołu, demo mapy)
- **Rozmowa o grze (33 min) spisana i skomentowana.** Nowe notatki: [[Rozmowa 2026-11-12 — zapis ustaleń]], [[Propozycje z rozmowy 2026-11-12]], [[Ocena potencjału gry]]. Pełna transkrypcja została lokalnie u Karola (repo jest publiczne).
- **Badania ze źródłami** (nowy folder `B&C/Badania/`): [[Rynek Roblox i konkurencja]], [[Shakes & Fidget — rozbiór mechanik]], [[Retencja i monetyzacja — co wolno i co działa]], [[Styl UI gier Roblox]], [[Narzędzia i skille do Roblox]], [[Technika gry — serwery, światy, walki]].
- **Sprzeczności z kanonem zgłoszone, niczego nie nadpisano:** pytania 7–15 w [[Pytania otwarte]] (m.in. questy na czas a D-004, panel a D-008, styl UI a kanon) i propozycje D-012–D-018 w [[Rejestr decyzji]] (wszystkie 💡).
- **Panel zespołu** (`panel/`, Python bez zależności, port 8787): okno na sejf, raporty z akceptacją, podgląd 3D, agent na subskrypcji Claude Code, głosówki, sieć notatek, analityka, lustro tylko-do-odczytu. Notatka [[Panel zespołu]]; instrukcja `panel/INSTALACJA.md`; skill `.claude/skills/panel/`. Stary `dashboard/` nietknięty.
- **Przegląd bezpieczeństwa panelu** przed oddaniem: 14 potwierdzonych uwag, wszystkie poprawione. Najważniejsze: uprawnienia „osoby przy komputerze” (agent, git, nowa migawka) daje klucz lokalny zapamiętany w przeglądarce po `panel\start.bat`, a nie samo połączenie z tego komputera; wspólna `panel/konfiguracja.json` nie może zmienić ustawień bezpieczeństwa; limity czasu i sprzątanie procesów agenta; lustro bez powiązań do prywatnych sejfów. Doszedł przełącznik „Agent z telefonu” (Ustawienia → Telefon). Testy: 76 w `panel/testy/`. W panelu czeka pięć raportów, w tym pytanie do Game Directora o D-012 (czy panel zostaje).
- **Mapy z klocków** (`swiat/`, `tools/blender/klocki.py`, `tools/studio_buduj.py`, `tools/studio_mcp.py`): demo „Leśna baza startowa” — 2599 części w `Workspace/DemoLesnaBaza` (jeden kontener, do cofnięcia), ten sam plik `czesci.json` w Blenderze i w podglądzie 3D. Notatka [[Klocki — Blender i Roblox]]. Oświetlenie i reszta miejsca bez zmian; nic nie opublikowano.
- **Previz cutscenki auto-walki 3D** (prośba z rozmowy [17:08]): 9 sekund z Blendera — Rycerz kontra Leśny Slime, cios, kontra z blokiem, krytyk, liczby obrażeń, paski życia, łup z jajkiem. Pliki: `swiat/test_cutscenki/` (`cutscenka.py`, `cutscenka_v1.mp4`, `.blend`). To szkic do decyzji „2D czy 3D”, nie assety gry.
- **Skille Claude** do Roblox (6, po przeglądzie, MIT i Apache-2.0): [[Skille Claude do Roblox]], `.claude/skills/LICENCJE-OBCE.md`.
- **Repo:** `.mcp.json` (dodany serwer Roblox Studio), `CLAUDE.md` (sekcje o panelu, klockach i dwóch osobach), `.gitignore`, `.gitattributes`, `tools/sejf_lint.py` (kontrola linków, statusów i sekretów), workflow `.github/workflows/panel-lustro.yml` (ręczny), `DOKUMENTACJA.md`.
- Zaktualizowano: [[00 Start]], [[Jak prowadzimy sejf]] (folder Badania), [[Zadania]].

## 2026-11-12 · Claude Code (mapa teleportacji)
- Nowa notatka [[Mapa teleportacji]] (propozycja): ekran po kliknięciu Teleport z mapą miasteczka 2D w ramce, piny lokacji, X; zachowanie natywne w Roblox; dwa prompty Higgsfield (ramka z mapą 16:9 oraz pin lokacji).
- Proponowana lista 7 lokacji: Karczma, Arena, Twierdza, Zagroda petów, Targ, Gildia, Portal do lochów.
- Pytanie #7 (po scaleniu z gałęzią Karola 13.11: #28) w [[Pytania otwarte]] (lista lokacji + nazwa cudzej gry w prefiksie [[Style Lock]]). Zaktualizowano: [[Zadania]], [[00 Start]], `DOKUMENTACJA.md`.
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
