# Przejście całej gry okiem nowego gracza — raport (17.11.2026)

*Status: **propozycja** (raport z próby, nie decyzja). Zlecenie Karola: „Upewnijmy się nad grywalnością już gry”.
Część 1 — tylko czytanie i granie, w grze niczego nie poprawiałem.*

> **Werdykt.** Da się chodzić, walczyć i grać w mini-gry bez zawieszenia ani jednego błędu skryptu — w moim
> przejściu ok. 15–20 minut treści (start → las od slime'a do Strażnika → bazar → Training Center). **Ale to jeszcze
> nie jest gra:** łup z walki (złoto, doświadczenie, gem, tokeny) pokazuje się na karcie i **nie trafia do gracza**,
> wybrana klasa i poziom **nie wpływają na walkę**, a trening i przycisk „+” zmieniają liczby, które nic nie robią.
> Po pierwszej walce nic nie rośnie i nic nie każe wrócić.

**Warunki.** Studio, miejsce gry (Team Create), tryb Play, jeden gracz na komputerze, okno gry 2041 × 1153, okno
Studio na wierzchu (czas klatki wiarygodny). Trzy sesje Play (Mag, Wojownik, Zwiadowca). Prawdziwe wejście:
`user_mouse_input` (kliknięcia w przyciski), `user_keyboard_input` (WASD, strzałki, E, spacja, Enter, Esc → R → Enter),
chodzenie postaci narzędziem `character_navigation`. Gdzie użyłem obejść — rozdz. „Haczyki i obejścia”. Rozróżniam:
**[gra]** = sprawdziłem w grze, **[kod]** = wnioskuję z kodu.

## Znaleziska (posortowane wagą)

Szacunek poprawki = sama zmiana kodu i próba w Studio, bez decyzji projektowych. „Karol” = pakiet z `swiat/` albo
silnik walki, „Paweł” = jego pliki (`src/client/HUDClient`, `src/gui`, `src/server/{ClassSelect,PlayerStatsDefaults,
StatPoints,SkillTree}`, `src/shared/{ClassData,SkillTreeData}`, ekran ładowania) — **plików Pawła nie ruszamy, tylko
zgłaszamy**.

### BLOKUJE

Zawieszeń, błędów skryptów ani miejsc, z których nie da się wyjść, **nie znalazłem** (rozdz. „Co przeszło”). Jedyny
punkt w tej wadze blokuje **postęp**, nie ruch:

| # | Co | Gdzie / jak powtórzyć | Co widać, konsola | Podejrzany plik | Czyje | Szacunek |
|---|---|---|---|---|---|---|
| B1 | **Łup z walki nie trafia do gracza** — złoto, doświadczenie, gem i tokeny są tylko na karcie wyniku; poziom gracza zawsze 1 | [gra] Las → walka ze slime'em → wygrana → karta „+22 złoto, +11 doświadcz., +1 token lasu” → ZAMKNIJ. Po 3 wygranych (2× slime, Strażnik: +702 złota, +416 XP, +1 gem) atrybuty gracza: `Gold = 0`, `XP = 0`, `Gems = 990` (bez zmian), `Level = 1`; HUD pokazuje 0 złota | zrzuty `07_karta_nagrody_22_zlota`, `08_po_walce_zloto_0`; konsola czysta (`[LasPasGra] walka … → wygrana`) | [kod] nikt nie ustawia `Gold`/`XP`/`Level` (szukane `SetAttribute("Gold"/"XP"/"Level"/"Gems")` w całym repo — jedyne trafienie: `src/server/SkillTree.server.luau:66`, odejmowanie gemów). Łup liczy silnik (`src/server/Walka/Przeciwnicy.luau`, `lup`), pokazuje `swiat/test_walki2/zrodla/InterfejsWalki2.luau`. Naturalne miejsce przyznania: serwer potworów po przyjętej walce (`swiat/las_potwory/zrodla/SerwerPotworow.server.luau`, tam, gdzie leci `Sygnaly/WynikWalki`) | brak kodu; łup i serwer potworów — Karol, atrybuty gracza i HUD — Paweł (do ustalenia, kto przyznaje) | 1–2 h (złoto/XP/gem do atrybutów, próg `XPMax` → `Level + 1`); zapis do DataStore osobno |

### MYLI (gracz nie wie, co robić, albo dostaje złą informację)

| # | Co | Gdzie / jak powtórzyć | Co widać | Podejrzany plik | Czyje | Szacunek |
|---|---|---|---|---|---|---|
| M1 | **Klasa z ekranu wyboru nic nie zmienia** — wszystkie trzy mają te same statystyki, a postać to domyślny awatar Roblox | [gra] trzy sesje: Mag (mysz, strzałka w prawo), Wojownik (Enter), Zwiadowca (strzałka w lewo + PLAY) — za każdym razem `STR 20, CON 16, INT 18, DEX 12, LUCK 7, ARMOR 57`; różni się tylko atrybut `Class`. Paski na ekranie wyboru sugerują różnice (Zwiadowca „Bow & dagger” z najniższą zręcznością) | zrzuty `18_scout_statystyki`, `02_start_brak_celu` | [kod] `src/server/PlayerStatsDefaults.server.luau:9` (jedne wartości dla wszystkich), `src/server/ClassSelect.server.luau:29` (ustawia tylko `Class`) | Paweł | decyzja + 0,5 h |
| M2 | **W lesie walczy „Wojownik · poz. AUTO”, a nie wybrana klasa i poziom** — przy AUTO bohater ma zawsze poziom potwora, a okno „TWÓJ BOHATER (TEST)” pozwala każdemu wybrać klasę i poziom 1/5/10 | [gra] wybrałem Maga → panel w lesie „Las-pas · Bohater: Wojownik · poz. auto”, walka „WOJOWNIK · POZ. 1”, przy slime poz. 2 bohater też poz. 2; po zmianie w panelu na Zwiadowcę 10 Strażnik pokonany od razu. Statystyki z okna ekwipunku (STR 26) nie zmieniają HP ani obrażeń | zrzuty `06_las_bohater_wojownik_u_maga`, `21_walka_wojownik_zamiast_maga`, `09_panel_bohatera_test` | [kod] `swiat/las_potwory/zrodla/KlientPotworow.client.luau:309–334` (reguła testowa T1, domyślnie `wojownik`/`auto`), wybór w `:951` | Karol | 1 h (klasa z `Class`: Warrior → wojownik, Scout → zwiadowca, Mage → mag; poziom z `Level`; panel testowy tylko w Studio pod atrybutem) |
| M3 | **Brak celu w pierwszej minucie** — nic nie mówi, dokąd iść ani co kliknąć | [gra] po PLAY postać stoi w starym miasteczku przed karczmą; na ekranie 6 przycisków HUD, napis „NOWE MIASTECZKO (E)”; tablica „TRAINING CENTER / MINI-GRY” jest częściowo zasłonięta lewą kolumną HUD; żadnej strzałki, zadania, dymka. Quests nic nie otwiera | zrzuty `02_start_brak_celu`, `20_odrodzenie_tablica_pod_hud` | brak (projekt: pierwsze zadanie / strzałka do TELEPORT) | Paweł (HUD, Quests) + Karol (świat) | decyzja; prosta strzałka/dymek 1 h |
| M4 | **Pets, Quests, Shop, Guilds nic nie otwierają** | [gra] klik każdego → nic na ekranie, w konsoli tylko `[HUD] pressed: Pets` itd.; to samo dają E w bazarze (karczma → Quests, sklepy → Shop, zagroda → Pets) | konsola `[HUD] pressed: …` | [kod] `src/client/HUDClient.client.luau:254–255` (tylko `Fire` + `print`), okien jeszcze nie ma | Paweł | okna = osobne zadania; tymczasowo dymek „wkrótce” 0,5 h |
| M5 | **Chmury bez podpowiedzi** — makieta krain nie mówi, jak wybrać (klik / strzałki + Enter) ani jak wrócić (Backspace, Esc) | [gra] TELEPORT → biel → makieta 9 krain, HUD znika, żadnego napisu. Wybór strzałką i Enterem działa; Backspace wraca do miasteczka | zrzut `05_chmury_bez_podpowiedzi` | `swiat/teleport_chmury/zrodla/KlientTeleportu.client.luau` | Karol | 0,5 h (pasek „Kliknij krainę · ← → Enter · Backspace = wróć”) |
| M6 | **E przy potworze często nic nie robi i nie mówi dlaczego** — potwory chodzą, podpowiedź „Walcz” jest tylko do 8 st, a po przewiniętej walce następna jest zablokowana przez prawdziwy czas poprzedniej. **Częściowo niepewne:** podpowiedź Roblox pokazuje się tylko, gdy punkt jest na ekranie, a moja postać chodziła narzędziem (kamera nie zawsze patrzyła na potwora) | [gra] na 15 naciśnięć E przy chodzących potworach 6 zaczęło walkę (slime: 2 z 5, wilk: 2 z 6; Strażnik stoi — 2 z 2). Po przegranej z wilkiem tempem ×4 trzy kolejne E przy tym samym wilku bez walki, choć podpowiedź pakietu była włączona; atrybut odmowy pusty, na ekranie nic. **Ale** w próbie dymnej z kamerą ustawioną za plecami E przy slime'ie zadziałało od pierwszego razu (1 z 1) — większość moich nieudanych E to prawdopodobnie kamera, nie gra | konsola czysta | [kod] `swiat/las_potwory/zrodla/Stale.luau:29` (`ZASIEG_E = 8`), blokada czasu walki — README `swiat/las_pas_gra` („Kolejna walka dopiero po prawdziwym czasie poprzedniej”) | Karol | 1–2 h (potwór staje, gdy gracz blisko; większy zasięg; dymek „Chwila…” przy odmowie); najpierw sprawdzić ręcznie myszą i klawiaturą |
| M7 | **Okno ekwipunku i drzewko obiecują rzeczy, których nie ma** — „+” dodaje statystykę za darmo i bez limitu, a statystyki nic nie robią; zakładki DESCRIPTION/INFO/INTERACTIONS podświetlają się bez zmiany treści; plecak pusty; drzewko pokazuje „WARRIOR” u Maga, UNLOCK zabiera 10 gemów i nic widocznego nie daje | [gra] 6 kliknięć „+” przy STR: 20 → 26 (DMG ~12 → ~15) na poz. 1 bez punktów; UNLOCK: gemy 1000 → 990, `SkillTree = {"Player_Root":1}` | zrzuty `04_equipment_plus_bez_kosztu`, `03_drzewko_warrior_u_maga` | [kod] `src/server/StatPoints.server.luau` („TYMCZASOWO bez kosztu”), `src/shared/SkillTreeData.luau:47` (`name = "WARRIOR"` dla każdej klasy) | Paweł | decyzje (System RPG) |
| M8 | **Trening nie zmienia statystyk, a podsumowanie przerwanej rundy liczy dziwnie** | [gra] Pancerz: START, kilka bloków, X → „KONIEC RUNDY (przerwana) · Trafienia 2 z 43 (15%) · Pancerz +0 · Pasek 8/40 · w tej sesji +0 (atrybut TreningPancerz, bez zapisu)”. „43” to wszystkie zdarzenia rundy, a 15% liczone od prób — po przerwaniu 2/43 ≠ 15%. [kod] przyrost Siły/Pancerza nie trafia do `Strength`/`Armor` | zrzut `14_runda_przerwana_15_procent` | [kod] `swiat/trening_proba/zrodla/SerwerTreningu.server.luau:12–17` („dziś nikt go nie słucha”), `KlientTreningu.client.luau:1216`, `LogikaTreningu.luau:312` | Karol | 0,5 h tekst; podpięcie statystyk — decyzja |
| M9 | **Ekran ładowania obiecuje rzeczy, których nie ma** — „W dungeonie okładaj beczkę, a quest skończy się szybciej!”, „Twierdza produkuje złoto…” | [gra] wskazówka na pasku ładowania | zrzut `01_ladowanie_wskazowka_dungeon` | `tools/studio/build_loading_screen.luau:157, 177–181` | Paweł | 10 min (wskazówki o tym, co już jest) |
| M10 | **Bazar: 13 punktów E, z czego działają 4** (stare miasteczko, trener, portal krain, Brama Leśna); reszta to dymek „… w budowie” albo sygnał do nieistniejącego okna | [gra] E przy tablicy, mistrzu gier, karczmarzu → historia klienta bazaru: dymek / sygnał HUD `Quests`; trener → okno mini-gier; Brama Leśna → las (bez drugiego przelotu). Dymków nie ma na zrzutach (narzędzie nie rysuje `BillboardGui` z `AlwaysOnTop`) — czytelności nie oceniam. Sklep maga, zbrojownia, lochy, zagroda, działka, portal — [kod] i próba pakietu (B04) | zrzut `15_bazar_kamera_w_scianie` | `swiat/miasteczko_bazar_gra/` | Karol (+ okna Pawła) | zależne od okien |

### PSUJE WRAŻENIE

| # | Co | Gdzie / jak powtórzyć | Plik | Czyje | Szacunek |
|---|---|---|---|---|---|
| P1 | **Teksty dla twórców na ekranie gracza**: „TYMCZASOWY WYBÓR (próba). Docelowe okno 2D robi Paweł (D-093).”, „TWÓJ BOHATER (TEST)”, „Las-pas · Bohater: …”, „(atrybut TreningPancerz, bez zapisu)”, stopka walki „dziennik policzył serwer • ziarno 1880885133 • 14 tur …” | [gra] okno wyboru mini-gry, panel bohatera, podsumowanie treningu, karta wyniku walki (zrzuty `12`, `09`, `14`, `07`) | `swiat/trening_proba/ustawienia.json:171` + `zrodla/DaneTreningu.luau:236`, `KlientTreningu.client.luau:1219`, `swiat/test_walki2/zrodla/InterfejsWalki2.luau:1539`, `swiat/las_potwory` (stała `PANEL_PREFIKS`) | Karol | 0,5 h (pokazywać tylko w Studio) |
| P2 | **Mieszanka języków** — ekrany Pawła po angielsku (CHOOSE YOUR CLASS, EQUIPMENT, BACKPACK, SKILL TREE, QUESTS…), świat i walka po polsku | [gra] wszędzie | `src/gui`, `src/client` | Paweł | decyzja (jaki język gry) |
| P3 | **Kamera wchodzi w ściany i dachy w bazarze**; w walce bywa kadr zasłonięty potworem | [gra] stoisko mistrza gier — pół ekranu czarne (ściana), przy lochach dach na pierwszym planie; 2. walka ze slime'em — kamera tuż za slime'em, bohatera nie widać | zrzuty `15_bazar_kamera_w_scianie`, `16_bazar_kamera_zaslonieta`, `22_walka_kamera_zaslonieta_slime`; `swiat/miasteczko_bazar` (stoiska), `swiat/test_walki2` (kamera walki) | Karol | 1–2 h |
| P4 | **Poza mapą szara płyta 2048 × 2048** — ze starego miasteczka można zejść na szarą pustkę; lokacje to wyspy na płycie | [gra] przestawienie w (500; 20; −350) → postać stoi na `Workspace.Baseplate`; za płytą spadek i odrodzenie | zrzut `17_poza_mapa_szara_plyta`; `Workspace.Baseplate` (tylko w `.rbxl`) | do ustalenia | decyzja (usunąć płytę / niewidzialne ściany starego miasteczka) |
| P5 | **Dwa miasteczka i zawsze start w starym** — start w Krzywym Miasteczku z napisem „NOWE MIASTECZKO (E)”; każda śmierć i reset odradza w starym (SpawnLocation 0; 0; 0), także po walce w lesie | [gra] reset w walce i w mini-grze → stare miasteczko | `Workspace.SpawnLocation` | do ustalenia | decyzja |
| P6 | **Przegrana daje więcej doświadczenia niż wygrana** (Strażnik przegrana +92 XP, slime wygrana +11) — gdy łup zacznie trafiać do gracza, przegrywanie z bossem stanie się najszybszym XP | [gra] karty wyniku | zrzut `10_przegrana_straznik_92xp`; `src/server/Walka/Przeciwnicy.luau` (`lup`) | Karol | 0,5 h + decyzja (łup za przegraną) |
| P7 | **HUD zostaje na ekranie w mini-grze** i jest klikalny; TELEPORT w trakcie rundy nic nie robi (dobrze), ale bez komunikatu | [gra] runda Siły — kolumny HUD obok skrzynek (zrzut `13_runda_sily_hud_na_wierzchu`); w walce HUD jest schowany | `swiat/trening_proba/zrodla/KlientTreningu.client.luau` | Karol | 0,5 h (schować HUD na czas rundy jak w walce) |
| P8 | **Pusta ramka awatara** w lewym górnym rogu HUD | [gra] zrzut `02_start_brak_celu` | `src/gui` HUD | Paweł | 0,5 h |

### DROBNE

| # | Co | Gdzie / jak powtórzyć | Plik | Czyje | Szacunek |
|---|---|---|---|---|---|
| D1 | Ostrzeżenie ze śladem stosu przy resecie w chmurach: `[TeleportChmury] przejście przerwane: PRZERWANE: śmierć postaci` + `Workspace.TeleportChmury.KlientTeleportu:1075 / :190 animuj / :1016 przebieg / :1074` — zachowanie poprawne (sprząta, kamera Custom), ale w konsoli wygląda jak błąd | [gra] TELEPORT → w chmurach Esc → R → Enter | `swiat/teleport_chmury/zrodla/KlientTeleportu.client.luau:190` (`error("PRZERWANE: …")`), `:1083` (`warn`) | Karol | 10 min (zwykły `print` bez śladu dla przerwania śmiercią) |
| D2 | Spacja nie zamyka karty wyniku walki (tylko klik ZAMKNIJ), choć spacja pomija walkę | [gra] | `swiat/test_walki2/zrodla/InterfejsWalki2.luau` | Karol | 15 min |
| D3 | Po resecie w trakcie przelotu (pierwsze wejście „zapomniane” haczykiem `zapomnijPrzelot`) następne wejście do lasu nie odtworzyło przelotu: `WidzialPrzelotLasu = false`, faza „brak”, licznik przelotów bez zmian. **Niepewne** — przy haczyku; nie wiem, czy reset trafił w przelot, czy jeszcze w chmury | [gra, z haczykiem] | `swiat/las_pas_gra/zrodla/SerwerPasa.server.luau` (automat przelotu) | Karol | 15 min na sprawdzenie |
| D4 | Na zrzutach nie widać podpowiedzi E ani dymków bazaru (narzędzie Studio nie rysuje `BillboardGui` z `AlwaysOnTop`) — nie da się ocenić ich czytelności zrzutami | — | — | — | — |
## Dziury w pętli gry

1. **Walka → łup → nic.** Karta pokazuje złoto, doświadczenie, gem, tokeny lasu i shard ewolucji; do gracza nie trafia
   nic (B1). Poziom stoi na 1, HUD zawsze „0 złota”.
2. **Postęp nie zmienia walki.** Bohater w lesie ma klasę i poziom z testowego panelu (domyślnie „Wojownik, AUTO =
   poziom potwora”), nie z wyboru klasy ani z `Level` (M1, M2). Każdego potwora — także Strażnika — wygrywa się po
   przełączeniu panelu, więc nie ma powodu się rozwijać.
3. **Statystyki bez znaczenia.** „+” w ekwipunku dodaje za darmo (M7), trening daje punkty sesji, które nic nie
   zmieniają i giną po wyjściu (M8); żadna z nich nie wchodzi do walki.
4. **Złoto i gemy nie mają na co iść.** Sklep, zbrojownia, mag, Shop — „w budowie”; jedyny wydatek to UNLOCK w drzewku
   za 10 gemów (startowe 1000), który niczego widocznego nie daje.
5. **Tokeny lasu i shard ewolucji** — nigdzie ich nie widać ani nie można wydać.
6. **Koniec treści za Strażnikiem.** Brama do Bagna otwarta → tabliczka „Bagno — wkrótce”. Kolejny cel nie istnieje.
7. **Nic nie każe wrócić.** Quests, Pets, Guilds puste; karczmarz („Zadania”) nie daje zadań; 4 z 6 mini-gier
   „w projekcie”.
8. **Pamięć tylko w serwerze.** Przelot, pokonany Strażnik, statystyki z „+”, punkty treningu — giną po wyjściu z gry
   (świadomie odłożone, ale dla pętli „wróć jutro” to brak).
9. **Przyciski bez okna:** Pets, Quests, Shop, Guilds (M4); zakładki DESCRIPTION/INFO/INTERACTIONS (M7); 9 punktów E
   w bazarze z samym dymkiem (M10).

## Co przeszło bez uwag (sprawdziłem w grze)

- **Start**: ekran ładowania → wybór klasy → postać przy starcie, **3/3 klasy** (Mag myszą, Wojownik Enterem — 13 s od
  Play w próbie dymnej, Zwiadowca strzałką w lewo + PLAY); kamera Custom, HUD, podpowiedzi E włączone.
- **Okna HUD**: EQUIPMENT otwiera się i zamyka X; drzewko (z okna ekwipunku) otwiera się i zamyka X; nic nie zostaje
  na ekranie. **Dwa okna naraz** (panel bohatera + ekwipunek) — ekwipunek na wierzchu, oba zamykają się osobno.
- **Teleport do lasu obiema drogami**: TELEPORT → chmury → strzałka + Enter → Las (przelot ok. 13 s, potem kamera
  Custom); **Brama Leśna w bazarze** (E) → Polana Przybycia **bez drugiego przelotu** (licznik 1 → 1).
- **Walki: 7 w grze** — 2 × slime (wygrane), 2 × wilk poz. 6 (przegrana; druga przerwana resetem — serwer policzył
  przegraną 7,3 s), Strażnik (przegrana Magiem 1, wygrana Zwiadowcą 10). Tempo ×4 działa i jest zapamiętane;
  **POMIŃ** pojawia się dopiero przy znanym gatunku i od razu daje kartę; **4 × E naraz = 1 walka**; w walce HUD
  schowany (nie da się teleportować w trakcie walki).
- **Strażnik**: po wygranej jeden baner „STRAŻNIK GAJU POKONANY! Brama do Bagna otwarta — idź za arenę”, przejście za
  bramę bez cofnięcia (zrzut `11`).
- **Kamień Powrotu** (E) → start bazaru (990; 3; −697), 2 × (ręcznie i w próbie dymnej).
- **Training Center**: E przy tablicy w starym miasteczku i E przy trenerze w bazarze otwierają wybór; Siła i Pancerz
  startują spacją; X w trakcie rundy → podsumowanie „przerwana”; WYJDŹ → postać tam, gdzie stała, kamera Custom;
  TELEPORT w trakcie rundy nie przerywa rundy.
- **Reset (Esc → R → Enter)**: w walce (ekran walki znika, odrodzenie, kamera Custom, HUD), w mini-grze (stan serwera
  i klienta wyczyszczony), w chmurach (sprzątanie poprawne, D1). **Spadek z mapy** (za płytą, y < −500) → odrodzenie
  po ok. 5 s, kamera Custom, HUD.
- **Czas klatki** (okno na wierzchu, 3 s RenderStepped): stare miasteczko 16,7 ms (p95 18,0), chmury 16,7 (17,7), las
  przy przybyciu 16,7 (18,1), bazar 16,7 (18,0); walka z wilkiem 16,7 (p95 18,5 — atrybuty odtwarzacza). Wszędzie
  60 kl./s.
- **Konsola**: 0 błędów ze skryptów gry w trzech sesjach; 1 ostrzeżenie (D1). Wpisy `AssistantCommand …` i
  `[LasPasGra] SterowanieSerwera: nieznane polecenie stan` to moje wywołania narzędzi, nie gra.

## Mały ekran (to NIE jest prawdziwy telefon)

Studio nie zmienia przez MCP rozmiaru okna gry ani nie włącza emulatora urządzeń, a okien Studio Karola nie
przestawiałem. Poniżej **szacunek z geometrii** [kod/pomiar]: najmniejszy przycisk i najmniejszy napis w oknie
2041 × 1153, przeliczone na 667 × 375 przy założeniu, że interfejs skaluje się z wysokością ekranu (Paweł ma w oknach
`UIScale` — jeśli jakiś skrypt dopasowuje je do ekranu, liczby będą inne). Próg Roblox na telefon: przycisk ≥ 44 pt.

| Okno | Rozmiary | Najmniejszy przycisk → przy 667 × 375 | Najmniejszy napis → przy 667 × 375 |
|---|---|---|---|
| HUD (Paweł) | skala | 152 px → ok. 49 | 34 px → ok. 11 |
| ClassSelect (Paweł) | skala | 146 px → ok. 47 | 18 px → ok. 6 |
| EquipmentPanel (Paweł) | skala | 43 px („+”, zakładki) → ok. 14 | 15 px → ok. 5 |
| SkillTree (Paweł) | skala | 63 px → ok. 21 | 14 px → ok. 5 |
| TreningProba (Karol) | piksele + własny `UIScale` | próba pakietu T12: ≥ 44 przy 667 × 375 | ≥ 12 pt (T12) |
| LasPasGraBohater (Karol) | stałe piksele, bez `UIScale` | 34 pt na każdym ekranie (< 44) | 16 pt |
| Interfejs walki (Karol) | własna emulacja | `swiat/test_walki2/testy/telefon.py` (osobna próba) | — |

Wniosek do sprawdzenia na prawdziwym telefonie albo w emulatorze Studio (Test → Device): okno ekwipunku i drzewko
mogą być nieczytelne, a panel bohatera lasu ma za małe przyciski.

## Haczyki i obejścia (gdzie nie było prawdziwego wejścia)

- **Chodzenie**: `character_navigation` (narzędzie Studio; postać idzie sama, nie z klawiatury) — podejście do potworów,
  tablic i stoisk. Klawiatura (W) tylko na początku lasu.
- **Przestawienie postaci przez serwer** (`PivotTo`, bez logiki gry): stoisko Bramy Leśnej (nawigacja w bazarze
  utykała), przed Strażnika (z Polany ok. 850 st), przed Kamień Powrotu, dwa razy poza mapę (szara płyta, pustka).
  W próbie dymnej: przy slime, Kamieniu i trenerze.
- **Haczyk sterujący — jeden raz**: `LasPasGra/Sygnaly/SterowaniePasa:Invoke("zapomnijPrzelot")` do próby resetu w
  przelocie (D3).
- **Panel „TWÓJ BOHATER (TEST)”** — klikany prawdziwą myszą (to dziś część gry), żeby przegrać z wilkiem (Mag 1) i
  wygrać ze Strażnikiem (Zwiadowca 10).
- **Odczyty stanu** haczykami „stan” i atrybutami (tylko odczyt) — do sprawdzania wyników.
- **Uwaga do własnych przestawień:** po `PivotTo` kamera zostaje zwrócona tam, gdzie patrzyła wcześniej; gdy punkt E
  jest za kamerą, Roblox nie pokazuje podpowiedzi i E nic nie robi (tak wyszły dwa fałszywe NIE w pierwszych
  przebiegach próby dymnej). Po teleportach gry (chmury, Kamień Powrotu, Brama Leśna) kamera była za plecami postaci —
  to nie jest błąd gry. Próba dymna ustawia kamerę za plecami przed każdym E.

## Czego nie sprawdziłem

- **Prawdziwy telefon / emulator Studio** — tylko szacunek wyżej; dotyk, przycisk E na ekranie, pad.
- **Dwóch graczy** (Test → Clients and Servers).
- **Długie stanie** — stałem najwyżej 1–2 minuty; wyrzucenia Roblox po 20 min bezczynności nie sprawdzałem.
- **Walka zaczęta w chwili teleportu** — nie udało się zgrać (w walce HUD jest schowany, więc TELEPORT niedostępny;
  E przy Kamieniu w trakcie walki — nie sprawdzone).
- **Powrót do miasteczka w trakcie walki** (Kamień, Brama) — nie sprawdzone.
- **Bazar, prawdziwym E**: sklep maga, zbrojownia, lochy, zagroda, działka, portal krain (nawigacja nie doszła) —
  opieram się na próbie pakietu `swiat/miasteczko_bazar_gra/testy/proba_play.py` (B04, B07, B11).
- **Stary las** (`BiomLas`, `LasPotwory`) — nie wchodziłem.
- **Dźwięk** na słuch.
- **Szybkie wielokrotne E w bazarze** (blokada „Chwila…”) — tylko w lesie (4 × E = 1 walka).
- **Mała rozdzielczość okna Studio** — nie zmieniałem okien Studio.
- **Opublikowana gra** — tylko Studio.

## Próba dymna

`swiat/przejscie_gry/proba_dymna.py` — Play → klasa (Enter) → TELEPORT → Las → walka ze slime'em → Kamień Powrotu →
trener → runda Siły → WYJDŹ, kontrola konsoli i klatki; wynik OK / NIE na punkt (D00–D10), ok. 3–4 minuty, sama wraca
do trybu Edit. Wszystkie przyciski i klawisze prawdziwe; haczyki tylko do odczytu; przestawia własną postać przy
slime'ie, Kamieniu i trenerze. Wyniki poza repo (nazwa konta zamieniana na `<gracz>`).

```
python -B swiat/przejscie_gry/proba_dymna.py <folder poza repo> [--studio <id>] [--bez-zrzutow]
```

Wynik na dziś (17.11.2026, trzeci przebieg, 126 s): **10 × OK, D04 NIE** (łup nie trafia do gracza — B1).
D01 klasa po 14 s od Play; D02 przelot przy pierwszym wejściu i potem kamera Custom; D03 walka ze slime'em od
pierwszego E (kamera za plecami); D05 Kamień → start bazaru (0,0 st); D06 okno mini-gier od pierwszego E; D07 pełna
runda Siły z podsumowaniem; D08 WYJDŹ → to samo miejsce; D09 las 16,7 ms (p95 17,9), bazar 16,7 ms (p95 17,8);
D10 0 śladów błędów. Dwa pierwsze przebiegi dały fałszywe NIE (strzałka w chmurach przed fazą wyboru; podpowiedź E za
kamerą po przestawieniu postaci) — poprawione w próbie, nie w grze.

## Zrzuty (`klatki/`)

`01_ladowanie_wskazowka_dungeon`, `02_start_brak_celu`, `03_drzewko_warrior_u_maga`, `04_equipment_plus_bez_kosztu`,
`05_chmury_bez_podpowiedzi`, `06_las_bohater_wojownik_u_maga`, `07_karta_nagrody_22_zlota`, `08_po_walce_zloto_0`,
`09_panel_bohatera_test`, `10_przegrana_straznik_92xp`, `11_straznik_pokonany_baner`,
`12_wybor_minigry_tekst_dla_tworcow`, `13_runda_sily_hud_na_wierzchu`, `14_runda_przerwana_15_procent`,
`15_bazar_kamera_w_scianie`, `16_bazar_kamera_zaslonieta`, `17_poza_mapa_szara_plyta`, `18_scout_statystyki`,
`19_reset_w_walce`, `20_odrodzenie_tablica_pod_hud`, `21_walka_wojownik_zamiast_maga`,
`22_walka_kamera_zaslonieta_slime`. Na żadnym nie ma nazwy konta (własna postać nie ma etykiety; zrzutów tablicy
rankingu w bazarze, gdzie nazwa jest widoczna, nie dołączyłem).

## Część 2 — poprawki w pakietach Karola (17.11.2026, bez Studio — czekają na wdrożenie)

Zakres przydzielony przez sesję główną; B1, M1, M2, M6 i statystyki z M8 robi pakiet `swiat/stan_gracza/` (inny
agent), M4, M7, M9 i ramka awatara to pliki Pawła (zgłoszenie przez sejf), P2 (język), P4 (płyta) i P5 (odrodzenie)
to decyzje ludzi.

| Znalezisko | Co zrobione | Pliki |
|---|---|---|
| M3 brak celu | nowy pakiet `swiat/wskazowki_gry/` → `Workspace/WskazowkiGry`: linijka celu z krzyżykiem, strzałka przy TELEPORT, znacznik nad celem; kroki (a)–(e) ze stanu gracza; bez StanGracza bez kroków o poziomach i treningu | cały pakiet (README) |
| M5 chmury | linijka podpowiedzi w fazie wyboru (mysz / klawiatura / dotyk / pad); przerwanie śmiercią albo resetem bez śladu stosu (`print`), prawdziwe błędy dalej `warn` ze śladem | `swiat/teleport_chmury/zrodla/KlientTeleportu.client.luau` |
| M8 tekst, P1, P7 | podsumowanie „Trafienia · pudła · celność”; bez „D-093”, „(próba)”, „bez zapisu”; HUD i inne ekrany schowane na stanowisku, oddawane przy zejściu i po resecie | `swiat/trening_proba/` (README, „Poprawki po przejściu gry”) |
| M10, P3 | dymki dla gracza (jedno zdanie); przyczyna kamery w ścianach: części mapy bez kolizji (Poppercam ich nie omija) — półprzezroczyste u gracza, gdy zasłaniają | `swiat/miasteczko_bazar_gra/` (README, „Poprawki po przejściu gry”) |
| P1 walka, D2 | stopka z ziarnem tylko w trybie próby (z JESZCZE RAZ), spacja / B zamyka kartę wyniku (po 0,6 s) | `swiat/test_walki2/zrodla/InterfejsWalki2.luau` |
| próba dźwięku | D2, D4, D5 rozpoznają stan (bez identyfikatora / wczytany / niewczytany) i wypisują go | `swiat/dzwiek_gra/testy/proba_play.py` |
| próba dymna | D11 (wskazówka po starcie), D12 (wskazówka w lesie), D13 (dźwięk w walce), D04 czeka do 10 s na łup | `proba_dymna.py` |

## Część 3 — po poprawkach (17.11.2026, wspólna próba całości, 14:52–15:50)

Wszystko z dysku wdrożone w Studio (StanGracza, oba lasy, Bagno, nowe skrypty walki, chmury, dźwięk, wskazówki,
Training Center, bazar, przymierzalnia). Okno Studio na wierzchu.

### Próby w Play

| Próba | Wcześniej | Teraz |
|---|---|---|
| `swiat/przejscie_gry/proba_dymna.py` (D01–D13) | 10 × OK, D04 NIE (łup) | **13/13 OK** (dwa przebiegi; D04: złoto 0 → 22 i 0 → 18) |
| `test_walki2/testy/test_walki_play.py --szybko` | 111/111 | **111/111** |
| `test_walki2/testy/test_v3_play.py` | 44/46 | **44/46** — te same dwa punkty: panel prób na telefonie 844 × 390 i 667 × 375 (napisy 10–11 pkt; czekają na decyzję) |
| `test_walki2/testy/test_poprawek_play.py` | 27/27 | **27/27** |
| `test_walki2/testy/test_klipow_play.py` | — | **29/29** |
| `test_walki2/testy/test_dopieszczenia_play.py --tylko final` | — | **9/9** (ujęcie pokonanego 1,8 s, upadek skończony w ujęciu, objazd 17 klatek, twarz zwycięzcy 35°) |
| `test_walki2/testy/klatki_aktorow.py --tylko mag --wszystkie` (+ `--przod`) | — | **zrzuty bezużyteczne** — na każdej klatce sala wyboru klasy, nie aktor (niżej) |
| `trening_proba/testy/proba_play.py` (T01–T14) | 14/14 (kliknięcia GRAJ / WYJDŹ przez haczyk) | **14/14**, po poprawce próby kliknięcia GRAJ i WYJDŹ są prawdziwe |
| `miasteczko_bazar_gra/testy/proba_play.py` (B01–B15) | B11 BŁĄD (próba znała stare dymki), B14 „?” | **13 × OK**, B03 „?” (bieg pominięty `--bez-biegu`), B14 „?” (klatka 16,7 ms) |
| `miasteczko_bazar_gra/testy/proba_dodatkowa.py` | — | D01–D04 OK, D05 „?” (klatka) |
| `teleport_chmury/testy/proba_play.py` | 6/6 | **6/6** |
| `dzwiek_gra/testy/proba_play.py` (D1–D6) | — | **6/6** — stan: arkusz niewczytany (gra nie ma prawa do zasobu) → grają dźwięki wbudowane (zagrane 21); muzyka bazaru i lasu niewczytana → nie gra |
| stroje S09 (walka w lesie w stroju) | „?” | **sprawdzone w grze**: Mag zdjął kapelusz w przymierzalni → w walce w lesie kot-mag bez kapelusza (`klatki/c3_07`, `c3_08`); liczby brył nie odczytałem |

### Przejście „po ludzku” (Mag, prawdziwe kliknięcia i klawisze; haczyki: przestawienie postaci przy potworach,
Kamieniach i trenerze, kamera za plecami przed E, autogra rundy Siły, poziom 14 i Strażnik lasu pokonany)

Start → wybór klasy (strzałka, PLAY) → linijka „Otwórz TELEPORT i wybierz Las” ze strzałką przy TELEPORT (`c3_01`,
`c3_02`) → przymierzalnia: zakładka Mag, hełm „— nic —” → „Założone — tak wyjdziesz do następnej walki” (`c3_04`) →
TELEPORT → chmury z linijką podpowiedzi (`c3_05`) → przelot → las: panel „TWÓJ BOHATER: MAG · POZIOM 1”, linijka
„Podejdź do potwora i wciśnij E” (`c3_06`) → walka ze slime'em Magiem w stroju (`c3_07`; dźwięk: zestaw arkusz,
niewczytany → 24 dźwięki wbudowane) → karta bez stopki (`c3_08`) → **spacja zamyka kartę**, HUD wraca, złoto 0 → 21,
poziom 1 → 2, linijka „Zdobywaj poziomy (masz 2)” (`c3_09`) → Kamień Powrotu → bazar → trener → runda Siły: HUD
schowany (`c3_10`), „Trafienia 36 · pudła 11 · celność 77% · Siła +3” (`c3_11`), Siła gracza 10 → 13 → WYJDŹ →
(haczyk: poziom 14, Strażnik lasu) → baner „POZIOM 14 · AWANS ×4!” i linijka „Bagno otwarte: TELEPORT → Bagno”
(`c3_12`) → TELEPORT → Las → „Brama otwarta — idź do Bagna” → przez bramę (W) (`c3_13`) → przelot Bagna ze
Strażnikiem Topieli (`c3_14`) → Bagno: „Podejdź do potwora i wciśnij E” (`c3_15`) → walka z Rechotkiem poz. 10, Mag
poz. 14 ma 1144 HP (`c3_16`) → karta „TOKENY BAGNA” (`c3_17`) → spacja → złoto 138, panel „BAGNO · TWÓJ BOHATER”,
„Zdobywaj poziomy (masz 14) — Strażnik Topieli na końcu Bagna” (`c3_18`) → Kamień Powrotu Bagna → start bazaru
(`c3_19`). Konsola: 0 błędów ze skryptów gry; tylko „Requester does not have permission for Asset” (znane).

### Znaleziska z części 1 → stan teraz

| # | Znalezisko | Teraz |
|---|---|---|
| B1 | łup nie trafia do gracza | **naprawione** (StanGracza): złoto, XP, awans, tokeny krainy w HUD i atrybutach |
| M1 | klasa nic nie zmienia | **częściowo**: statystyki z rozkładu klasy (StanGracza), ale Mag ma Siłę 10 > Inteligencję 9 (rozkład do sprawdzenia); postać poza walką to dalej awatar Roblox |
| M2 | w lesie walczy „Wojownik AUTO” | **naprawione**: bohater z klasy i poziomu gracza („TWÓJ BOHATER: MAG · POZIOM N”) |
| M3 | brak celu | **naprawione** (wskazówki: las i Bagno) |
| M4 | Pets, Quests, Shop, Guilds bez okien | bez zmian (pliki Pawła, zgłoszone) |
| M5 | chmury bez podpowiedzi | **naprawione** |
| M6 | E przy chodzących potworach | **częściowo**: z kamerą za plecami E działa od razu (4 z 4); idąc narzędziem za slime'em raz chybione — dalej trzeba gonić |
| M7 | ekwipunek / drzewko obiecują | bez zmian (Paweł) |
| M8 | trening nie wzmacnia, tekst podsumowania | **naprawione** (Siła 10 → 13 po rundzie; nowy tekst) |
| M9 | wskazówki ekranu ładowania | bez zmian (Paweł) |
| M10 | dymki bazaru, kamera w ścianach | dymki **naprawione**; kamera — przenikanie części bez kolizji w pakiecie (B06/D01 bez zasłony); szczyty dachów w mapie dalej bez kolizji |
| P1 | napisy dla twórców | **częściowo**: trening, walka, bazar czyste; zostało „PRZYMIERZALNIA (próba stroju)” i nagłówek „PRÓBA” w oknie przymierzalni (`swiat/stroje_proba`) |
| P2 | język | do decyzji ludzi |
| P3 | kamera | jak M10; w stoiskach kamera dalej blisko (7,8 st u mistrza gier) |
| P4 | szara płyta | do decyzji ludzi |
| P5 | odrodzenie w starym miasteczku | do decyzji ludzi |
| P6 | przegrana daje więcej XP | niesprawdzone teraz |
| P7 | HUD w mini-grze | **naprawione** |
| P8 | pusta ramka awatara | bez zmian (Paweł) |
| D1 | ślad stosu przy resecie w chmurach | naprawione w kodzie; w grze niepowtórzone |
| D2 | spacja nie zamyka karty | **naprawione** (las i Bagno) |
| D3 | przelot po resecie | niesprawdzone |

### Nowe w części 3

- **Przymierzalnia otwiera się na zakładce Wojownik**, choć gracz wybrał Maga (`c3_03`) — `swiat/stroje_proba` (MYLI).
- **Arena walki w Bagnie to las z sosnami** — zgodnie z decyzją Karola areny będą zależne od biomu (praca w toku).
- **Strzałka „◀” i znacznik „▼” były malutkie** (czcionka gry nie ma tych znaków) — poprawione: „<” 84 px i romb.
- **`klatki_aktorow.py` robi zrzuty sali wyboru klasy zamiast aktora** — kamera ekranu wyboru klasy Pawła przejmuje
  kadr w sesji Play próby; zamknięcie ekranu Enterem (próbowałem) nie pomogło, zmianę cofnąłem. Do sprawdzenia przez
  autora próby (ocena klipów Maga ze zrzutów niemożliwa).
- Dziennik serwera Bagna pisze „+ Strażnik Gaju” zamiast Topieli (`[BagnoPasGra] gotowy: …`) — kosmetyka wspólnego
  kodu potworów.
- Przy bramie do Bagna ekran na chwilę rozmyty (`c3_13`) — wygląda na przejście biomu; nie badałem.

### Werdykt po poprawkach

Da się dziś grać ok. **20–30 minut z sensem**: start z celem na ekranie, las z łupem w HUD i awansem, Training
Center, które naprawdę wzmacnia, strój z przymierzalni w walce, Bagno z nowymi potworami i Strażnikiem Topieli,
powrót Kamieniem. Bez zawieszeń i bez błędów skryptów. Najbardziej przeszkadza: **złota i gemów nie ma na co wydać**
(sklepy, karczma, zagroda „wkrótce”, okna Pawła puste), **długa droga do Strażnika** (slime daje ok. 12 XP, Strażnik
ma poziom 10 — nie mierzyłem, ile walk), gonienie chodzących potworów przy E i brak zapisu (wszystko ginie po wyjściu).
