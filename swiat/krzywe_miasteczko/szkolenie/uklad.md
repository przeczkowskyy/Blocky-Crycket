# Układ huba — „Krzywe Miasteczko” (szkolenie + trzy projekty)

> **W skrócie.** Polecam **układ A — promienisty rynek**. Ze spawnu widać naraz karczmę z tablicą, zbrojownię, wylęgarnię, bramę lochów i bramę twierdzy; najdalsze miejsce jest 8,6 s chodu od spawnu; główna pętla jest płaska (jedyny wyjątek to 4-studowa rampa przed karczmą). Układy B (krzywa ulica na wzgórze) i C (dwa brzegi z mostem) są efektowniejsze, ale wolniejsze i droższe. Wszystkie współrzędne sprawdził skrypt: kolizje obrysów, ulice, najkrótsze dojścia, pierwszy kadr. **Przed budową trzeba rozstrzygnąć obrót miasta względem słońca (rozdz. 4)** — bez niego fasady z pierwszego kadru stoją w cieniu. To propozycja, nie kanon.

## 1. Liczby bazowe

| Co | Wartość | Skąd |
|---|---|---|
| Prędkość chodu | 16 studs/s → 12 s = 192 studs | Roblox, Humanoid |
| Skok / postać | 7,2 studa / ok. 5 studs wzrostu (6–6,5 przy proporcjach ludzkich) | Roblox, Humanoid; Avatar Settings |
| Przejście dla dwóch postaci, ściana nie do przeskoczenia | ≥ 10 studs szer. / ≥ 10 studs wys. | Roblox, Greybox |
| Kamera | 12,5 studa za postacią (25 w pionie telefonu); pole widzenia 70° w pionie → ok. 102° w poziomie na 16:9, ok. 113° na telefonie 19,5:9 | Core-Scripts; Roblox, Camera; przeliczenie własne |
| Doczytywanie świata | pierwsze 64 studs wokół gracza z najwyższym priorytetem, zasięg 1024 | Roblox, Streaming |
| Plac huba | 80 × 80 do 120 × 120 studs na ok. 16 graczy | Mad Studio (DevForum) |
| Gracze mobilni | ok. 80% | PocketGamer.biz (wg wyniku wyszukiwania) |

## 2. Zasady

1. **Pierwszy kadr to plakat gry.** Cel pętli stoi na wprost, bez obracania kamery — kto w pierwszych minutach nie wie, co robić, wychodzi (Roblox, onboarding). Pierwszy cel ≤ 64 studs od spawnu, żeby doczytał się od razu.
2. **Spawn patrzy tam, dokąd gracz ma iść, a plecy ma zasłonięte** (Mad Studio).
3. **Dominanta („weenie”) na końcu każdej osi.** Hub ma dawać „podgląd każdej krainy z jednego miejsca”; ulica bez dominanty na końcu nie ciągnie.
4. **Gracz nie patrzy w górę** i skupia się na kontraście (Level Design Book). Szyld, drzwi i świecące okna ≤ 25° nad horyzontem: ich górna krawędź ≤ 8 + 0,45 × odległość od kamery (reguła własna; 8 = wysokość kamery).
5. **Korytarz widoku musi być pusty.** W Disneylandzie dawne dominanty zasłoniły drzewa. Tu każdy obiekt ma przedział kątów widziany z kamery i przedziały celów nie mogą się nakładać.
6. **Odległość licz w sekundach.** 0–3 s: rzeczy codzienne (koło, studnia, stragany); 3–6 s: pętla (tablica, karczma, sklepy, wylęgarnia); 6–9 s: kamienie milowe (lochy, twierdza) i zapowiedzi „wkrótce”; nic głównego dalej niż 12 s.
7. **Wszystko, co klikane co kilka minut, w jednym węźle.** Sklepy „blisko spawnu i łatwo dostępne” (DevForum); Grow a Garden 2 zebrał pięć sklepów w centrum, bo w jedynce biegało się przez całą mapę.
8. **Szerokość mówi o randze drogi:** główna 16, boczna 12, zaułek 10 studs; mur 16.
9. **Pętle zamiast ślepych końców.** Szprychy spina ulica obwodowa — taka poprawka uczyniła parki Disneya „dużo bardziej funkcjonalnymi”, a hub przestaje być jedynym przejściem.
10. **Pionowość jako znak, nie przeszkoda.** 4–12 studs różnicy wystarcza, by cel wystawał nad dachy; główna pętla bez schodów.
11. **Dzielnice i krawędzie.** Lewa strona „moje” (koło, pety, twierdza, gildia, wierzchowce) w błękitach; prawa „przygoda” (zbrojownia, lochy, arena, magia) w czerwieniach i fioletach. Mur z basztami zasłania krawędź świata.
12. **Coś woła gracza co ≤ 5 s marszu** (Ghost of Tsushima: co ≤ 30 s; hub jest 6× mniejszy). Sekret: 10–20 s zboczenia, nagroda widoczna z daleka, wejście ukryte.
13. **Zamknięte miejsca stoją na końcach szprych** — poza pętlą, w szarościach i z rusztowaniem („anty-dominanta”).

## 3. Huby znanych gier

Wymiarów hubów w studach nie podaje żadne źródło, do którego dotarłem. Twarde liczby mam tylko dla Fisch (współrzędne NPC z gry; odległości policzyłem sam).

| Gra | Co stoi gdzie | Liczby | Wniosek |
|---|---|---|---|
| Fisch — Moosewood | przystań → NPC samouczka → wyżej targ (Rzeczoznawca, Kupiec, Phineas) → staw; Latarnik po drugiej stronie wyspy | samouczek 46 studs od przystani (3 s); targ 93–105 studs (6–7 s) i 15–20 studs wyżej; Rzeczoznawca–Kupiec 25; Latarnik ok. 190 studs od targu | usługi w kole Ø ok. 50 studs; taras robi z targu widoczny cel; daleki NPC nagradza eksplorację |
| Grow a Garden → 2 | jedynka: sklep z narzędziami po przeciwnej stronie mapy niż nasiona i skup; dwójka: ogrody wokół wspólnego środka z pięcioma sklepami | brak danych | krótkie dojścia liczą się najbardziej na pełnym serwerze; pierścień prowadzi obok cudzych ogrodów |
| Pet Simulator 99 | Spawn: jajka i plac (Indeks, poczta, nagrody, sala VIP); ulepszenia rozrzucone po kolejnych strefach; skróty 2↔9 i 7→14; teleport po 2. odrodzeniu | 99 stref w 1. świecie | losowanie od pierwszej sekundy; funkcje dawkowane w głąb ciągną naprzód |
| Bee Swarm Simulator | przy ulach 5 pól bez bramki; bramki 5/10/15/25/35 pszczół wyznaczają trasę pod górę; Pro Shop przy polu ze strefy 10 pszczół | 23 pola | wysokość = postęp; lepszy sklep jest nagrodą |
| Steal a Brainrot | taśma przez środek, bazy po obu stronach, sklepy przy taśmie | 8 baz na serwer | wszyscy patrzą na wspólną oś; sklep stoi tam, gdzie i tak się stoi |

## 4. Założenia wspólne

- **Obrys to działka maksymalna:** szer. (lokalne X) × głęb. (lokalne Z), wejście pośrodku frontu (+Z). Mieści ściany, schody i przyziemne dobudówki; okapy i szyldy mogą wystawać, jeśli wiszą ≥ 10 studs nad ziemią. Wysokość to górna granica sylwetki. Wymiary z `styl.md` mieszczą się w działkach poza dwoma: bramę twierdzy (tam 44 × 14) trzeba zmieścić w 32, bo szersza zamyka prześwit ulicy między karczmą a wylęgarnią; arena to wycinek pierścienia 48 × 36, bo pełny Ø 60 wychodzi poza kwadrat.
- „Dojście” = najkrótsza trasa piesza ze spawnu do punktu 4 studs przed wejściem, z omijaniem obrysów. Kąty pierwszego kadru liczę od kamery (12,5 studa za spawnem), „+” w prawo; kadr 16:9 sięga ±51°.
- Mur: wys. 16, grub. 4; baszty 12 × 12, wys. 28 na załamaniach. Bramy, arena i gildia są w mur wbudowane.
- **Spawn** w układzie lokalnym patrzy na północ (−Z). Cudzego SpawnLocation nie ruszamy: miasto przesuwamy tak, by punkt spawnu wypadł na nim.

**Orientacja względem słońca — rzecz do rozstrzygnięcia przed budową.** Według `rzemioslo.md` (odczyt z cieni na zrzutach, niepotwierdzony w Studio) słońce świeci z północnego zachodu, a ściana w cieniu ma ok. 70% jasności. Nieobrócony SpawnLocation każe graczowi patrzeć na północ, czyli pod słońce: w układzie A fronty karczmy, wylęgarni i bramy twierdzy stoją wtedy w cieniu (kosinus kąta padania w poziomie −0,71, −0,94, −0,95), a światło łapie tylko zbrojownia (+0,29).

Lekarstwo: obrócić całe miasto o **Θ = atan2(sx, sz)**, gdzie sx, sz to poziome składowe `Lighting:GetSunDirection()` (odczyt niczego nie zmienia). Dla słońca z północnego zachodu Θ = −135°: słońce świeci graczowi w plecy, wszystkie fronty z pierwszego kadru są oświetlone (karczma 1,00; lochy 0,90; twierdza 0,89; zbrojownia 0,47; wylęgarnia 0,42), a główne budynki lądują po wschodniej i południowej stronie rynku — tak, jak zaleca `rzemioslo.md`. Przeliczenie: x′ = x·cos Θ + z·sin Θ, z′ = −x·sin Θ + z·cos Θ, obrot_y′ = obrot_y + Θ, potem przesunięcie na SpawnLocation.

Warunek: SpawnLocation musi dostać Orientation.Y = Θ, inaczej gracz startuje odwrócony od karczmy o 135°. To zmiana cudzej instancji, więc decyduje Game Director. Θ ma być jednym parametrem generatora; wariant bez decyzji to Θ = 0 (kompozycja zachowana, fasady w cieniu ratują Neon i jasne ściany).

## 5. Układ A — promienisty rynek (polecany)

Rynek: elipsa o półosiach 52 (X) × 44 (Z); środek (r = 20) pusty, na bruku róża wiatrów w kolorach pięciu ulic. **Spawn (0, 30).** Karczma na podium +4 (rampa szer. 30, od z = −46 do −57), brama lochów w niecce −4, brama twierdzy na nasypie +6 — obie z rampą na końcu ulicy.

| Miejsce | x, z | obrot_y | obrys | wys. | dojście (studs / czas) |
|---|---|---|---|---|---|
| Karczma | 0, −74 | 0° | 48 × 34 | 52 | 83 / 5,2 s |
| Tablica zleceń | −13, −30 | 12° | 18 × 4 | 16 | 55 / 3,5 s |
| Zbrojownia z kuźnią | 65, −34 | −62° | 30 × 24 | 34 | 76 / 4,8 s |
| Sklep magiczny | 72, 24 | −107° | 22 × 22 | 46 | 64 / 4,0 s |
| Wylęgarnia petów | −65, −31 | 65° | 28 × 26 | 36 | 73 / 4,6 s |
| Stajnia | −50, 67 | 90° | 36 × 22 | 24 | 52 / 3,3 s |
| Brama lochów | 62, −98 | −26° | 30 × 18 | 38 | 129 / 8,1 s |
| Arena („wkrótce”) | 124, −10 | −85° | 48 × 36 | 40 | 109 / 6,8 s |
| Siedziba gildii („wkrótce”) | −122, −6 | 87° | 32 × 28 | 50 | 111 / 6,9 s |
| Koło fortuny | −34, 25 | 82° | 16 × 10 | 24 | 25 / 1,6 s |
| Brama do twierdzy | −68, −104 | 27° | 32 × 16 | 46 | 138 / 8,6 s |
| Studnia-pomnik | 34, 25 | 15° | 14 × 14 | 16 | 38 / 2,4 s |
| Brama miejska | 0, 106 | 180° | 30 × 12 | 32 | 67 / 4,2 s |
| Stragany ×5 | (−22, 46; 154°), (22, 46; −154°), (15, 66; −90°), (−15, 78; 90°), (15, 80; −90°) | — | 10 × 7 | 10 | ≤ 3,2 s |

Ulice (łamane, szerokość):
- **Bramna** (16): (0, 44) → (3, 64) → (−2, 84) → (0, 100)
- **Lochowa** (12): (30, −36) → (44, −60) → (57, −88) — w osi spawn → brama lochów
- **Twierdzowa** (12): (−33, −35) → (−45, −59) → (−63, −94) — w osi spawn → brama twierdzy
- **Arenowa** (12): (52, −6) → (78, −10) → (96, −8)
- **Gildyjna** (12): (−51, −6) → (−78, −2) → (−99, −6)
- **Podmurna** (10, pierścień 771 studs = 48 s): (0, 96) → (52, 95) → (98, 72) → (124, 34) → (98, 22) → (96, −8) → (98, −38) → (114, −62) → (86, −80) → (64, −76) → (50, −84) → (34, −100) → (0, −108) → (−34, −102) → (−58, −88) → (−86, −80) → (−116, −60) → (−102, −32) → (−99, −6) → (−100, 22) → (−112, 44) → (−96, 76) → (−52, 96) → (0, 96)
- **Mur**: (0, 110) → (58, 106) → (108, 82) → (136, 36) → (146, −10) → (132, −62) → (100, −108) → (40, −126) → (−40, −128) → (−102, −110) → (−134, −60) → (−142, −6) → (−134, 40) → (−106, 84) → (−56, 106); obwiednia 288 × 238.
- **Kamieniczki-statyści** (x, z; obrót; obrys; wys.): (54, 52; −134°; 16 × 14; 30), (36, 66; −151°; 14 × 14; 36), (74, 62; −110°; 14 × 14; 26), (−70, 42; 121°; 16 × 14; 34), (−78, 20; 104°; 14 × 16; 28), (−84, 62; 90°; 14 × 14; 28), (92, −56; −110°; 14 × 16; 36), (96, 46; −120°; 14 × 14; 32), (−90, −56; 115°; 14 × 16; 34). Pastelowe, bez neonu — nie konkurują z miejscami.

**Pierwszy widok.** Na wprost karczma (−14°…+14°, 102 studs, wierzch 25° nad horyzontem), przed nią tablica (−17°…−3°, 72 studs). W prawo: brama lochów w głębi ulicy (+18°…+30°, 145 studs) i zbrojownia (+29°…+50°). W lewo: brama twierdzy (−31°…−19°, 154 studs) i wylęgarnia (−51°…−30°). Na samych skrajach, niemal w całości poza kadrem 16:9: koło (lewy) i studnia (prawy), 1,6 i 2,4 s od gracza. Żaden cel nie zasłania innego; tablica zakrywa tylko lewy dół karczmy (do y = 19), drzwi zostają widoczne. Szyldy zbrojowni i wylęgarni wieszać na połowie fasady bliższej karczmy — druga leży przy krawędzi kadru. Arena i gildia odsłaniają się ze środka rynku, w osiach swoich ulic.

**Sekrety.** (1) Beczki za karczmą przy (26, −94) → dach → skrzynia przy kominie. (2) Ogródek ze stawem przy (58, 80), wejście szczeliną 6 studs między kamieniczkami przy (45, 60). (3) Schody przy bramie miejskiej (22, 104) → chodnik na murze → baszta (132, −62) z widokiem na całe miasto. (4) Gniazdo za wylęgarnią przy (−84, −38).

## 6. Układ B — krzywa ulica ze wzgórzem

Profil: z ≥ 24 → y = 0; ulica Stroma (z od 24 do −24) to rampa 0 → 10 (12°); Taras Karczemny (x −36…40, z −59…−24) y = 10; zbocze do z = −104 rośnie do 22 (16°); Szczyt (x −30…8, z −130…−104) y = 22. Rynek Dolny: x −42…22, z 26…70. **Spawn (−10, 50).**

| Miejsce | x, z | obrot_y | obrys | wys. | y | dojście |
|---|---|---|---|---|---|---|
| Karczma | 2, −76 | 0° | 48 × 34 | 52 | 10 | 107 / 6,7 s |
| Tablica zleceń | −16, −36 | 8° | 18 × 4 | 16 | 10 | 81 / 5,1 s |
| Zbrojownia z kuźnią | −34, 2 | 90° | 30 × 24 | 34 | 4,6 | 49 / 3,1 s |
| Sklep magiczny | 22, −4 | −90° | 22 × 22 | 46 | 5,8 | 57 / 3,6 s |
| Wylęgarnia petów | −50, −38 | 90° | 28 × 26 | 36 | 10 | 94 / 5,9 s |
| Stajnia | −12, 104 | 90° | 36 × 22 | 24 | 0 | 56 / 3,5 s |
| Brama lochów | 50, −42 | −90° | 30 × 18 | 38 | 10 | 110 / 6,8 s |
| Arena („wkrótce”) | 88, 62 | −90° | 48 × 36 | 40 | 0 | 77 / 4,8 s |
| Siedziba gildii („wkrótce”) | −74, −86 | 90° | 32 × 28 | 50 | 17 | 150 / 9,4 s |
| Koło fortuny | 20, 40 | −72° | 16 × 10 | 24 | 0 | 23 / 1,4 s |
| Brama do twierdzy | −44, −122 | 76° | 32 × 16 | 46 | 22 | 176 / 11,0 s |
| Studnia-pomnik | −38, 44 | 15° | 14 × 14 | 16 | 0 | 26 / 1,6 s |
| Brama miejska | 44, 124 | 180° | 30 × 12 | 32 | 0 | 84 / 5,2 s |
| Stragany ×4 | (−30, 66; 160°), (20, 70; −140°), (34, 78; −50°), (54, 100; −100°) | — | 10 × 7 | 10 | 0 | ≤ 4,7 s |

- **Krzywa** (16): (44, 116) → (36, 98) → (6, 80) → (−10, 62) → (−10, 30) → (−8, 10) → (−2, −24)
- **Górna** (12): (−29, −60) → (−44, −84) → (−32, −108) → (−14, −114)
- **Schody Skrótu** (8): (−28, −62) → (−28, −100)
- **Arenowa** (12): (22, 57) → (48, 63) → (66, 62)
- **Mur**: (44, 128) → (96, 116) → (124, 80) → (118, 30) → (84, −6) → (78, −70) → (56, −118) → (10, −140) → (−56, −142) → (−100, −118) → (−104, −60) → (−80, −12) → (−72, 40) → (−66, 96) → (−30, 126); obwiednia 228 × 270.

**Pierwszy widok.** Kanion ulicy: po lewej zbrojownia (−38°…−9°, 47 studs), po prawej sklep magiczny (+15°…+38°, 59 studs), na końcu i wyżej karczma (−6°…+17°, 122 studs) z tablicą. Wylęgarnia, lochy, gildia i twierdza są zasłonięte — odsłaniają się dopiero na tarasie („ukryj i odsłoń”). Do bramy twierdzy ulicą Górną jest 11,6 s; Schody Skrótu ścinają zakole do 11,0 s — zapasu do 12 s prawie nie ma.

## 7. Układ C — dwa brzegi z Garbatym Mostem

Wąwóz biegnie ze wschodu na zachód: z od −38 do 2, dno y = −12; brzeg południowy y = 0 (Targowisko: x −44…44, z 6…54), północny y = 12 (Plac Karczemny: x −40…40, z −73…−48). Mur przekracza wąwóz kratami. **Spawn (0, 28).**

| Miejsce | x, z | obrot_y | obrys | wys. | y | dojście |
|---|---|---|---|---|---|---|
| Karczma | 0, −90 | 0° | 48 × 34 | 52 | 12 | 99 / 6,2 s |
| Tablica zleceń | −16, −58 | 12° | 18 × 4 | 16 | 12 | 85 / 5,3 s |
| Zbrojownia z kuźnią | 68, −72 | −80° | 30 × 24 | 34 | 12 | 124 / 7,8 s |
| Sklep magiczny | −64, 30 | 85° | 22 × 22 | 46 | 0 | 53 / 3,3 s |
| Wylęgarnia petów | −62, −72 | 79° | 28 × 26 | 36 | 12 | 119 / 7,4 s |
| Stajnia | −48, 80 | 90° | 36 × 22 | 24 | 0 | 62 / 3,9 s |
| Brama lochów | 30, −33 | 0° | 30 × 12 | 38 | −12 | 65 / 4,1 s |
| Arena („wkrótce”) | 104, 40 | −93° | 48 × 36 | 40 | 0 | 84 / 5,3 s |
| Siedziba gildii („wkrótce”) | 52, −114 | −32° | 32 × 28 | 50 | 12 | 139 / 8,7 s |
| Koło fortuny | 32, 26 | −86° | 16 × 10 | 24 | 0 | 23 / 1,4 s |
| Brama do twierdzy | −48, −116 | 31° | 32 × 16 | 46 | 12 | 151 / 9,4 s |
| Studnia-pomnik | −32, 26 | 15° | 14 × 14 | 16 | 0 | 30 / 1,9 s |
| Brama miejska | 0, 104 | 180° | 30 × 12 | 32 | 0 | 67 / 4,2 s |
| Stragany ×4 | (−22, 50; 160°), (22, 50; −160°), (15, 70; −90°), (−15, 84; 90°) | — | 10 × 7 | 10 | 0 | ≤ 3,5 s |

- **Bramna** (16): (0, 98) → (3, 78) → (−2, 58)
- **Garbaty Most** (20): (0, 2) → (0, −38), wznosi się 0 → 12 (17°); **kładki** (10): (±71, 2) → (±71, −38)
- **Schody do lochów**: południowe x 20…40, z od 2 do −14 (37°); północne x 48…58, z od −38 do −14 (45°)
- **Nabrzeże Górne** (10): (−71, −44) → (−40, −45) → (40, −45) → (71, −44); **Dolne** (10): (−71, 8) → (−44, 10) oraz (44, 10) → (71, 8)
- **Arenowa** (12): (44, 34) → (62, 38) → (78, 40); **Twierdzowa** (12): (−36, −70) → (−37, −96); **Gildyjna** (12): (36, −70) → (37, −94)
- **Mur**: (0, 108) → (56, 104) → (104, 84) → (134, 44) → (130, −40) → (112, −100) → (76, −132) → (30, −138) → (−36, −138) → (−84, −128) → (−112, −92) → (−118, −40) → (−110, 40) → (−96, 84) → (−54, 104); obwiednia 252 × 246.

**Pierwszy widok.** Trzy plany: targ, most w osi, nad nim karczma (−12°…+12°, 116 studs, wierzch na y = 64). Z wąwozu po prawej wystaje łuk bramy lochów (+11°…+34°, 69 studs) i zakrywa dół zbrojowni; wylęgarnia (−37°…−21°) czysta; brama twierdzy stoi między nią a karczmą, częściowo przesłonięta. Dno między mostem a bramą lochów zostaje otwarte, więc z mostu da się zeskoczyć (karczma → lochy szacunkowo 4,9 s; powrót schodami 6,7 s).

## 8. Porównanie i rekomendacja

| | A | B | C |
|---|---|---|---|
| Najdalsze miejsce od spawnu | 8,6 s | 11,0 s | 9,4 s |
| Średnio do punktów MVP (tablica, zbrojownia, wylęgarnia, lochy, arena) | 5,5 s | 5,1 s | 6,0 s |
| Karczma ↔ zbrojownia / wylęgarnia / lochy | 3,6 / 3,6 / 4,5 s | 3,8 / 2,4 / 2,3 s | 3,3 / 2,8 / 4,9–6,7 s |
| Cele w pierwszym kadrze bez zasłonięcia | 6 | 4 | 4 |
| Wolny plac | 104 × 88 (ok. 7200 studs²) | 64 × 44 i 76 × 35 | 88 × 48 i 80 × 25 |
| Różnica poziomów w pętli | rampa 4 studs przed karczmą | rampa 10 studs | most 12 studs |
| Wąskie gardło | brak | ulica szer. 16 | most szer. 20 |

**Polecam A**, bo: (1) pierwszy kadr pokazuje bez zasłonięć cztery z pięciu punktów MVP i bramę twierdzy — nowy gracz od razu widzi całą obietnicę gry; (2) pętla jest praktycznie płaska, co ma znaczenie przy ok. 80% graczy mobilnych; (3) najgorsze dojście jest o 2,4 s krótsze niż w B i o 0,8 s niż w C; (4) rozbudowa to dokładanie szprych i adresów przy Podmurnej; (5) płaski teren to najmniej części i ryzyka. Ceną jest dłuższa droga karczma ↔ wylęgarnia i lochy niż w B (o 1,2 i 2,2 s).

Z B wzięte: karczma wyżej niż rynek i odsłanianie zamkniętych miejsc dopiero z rynku. Z C: brama lochów poniżej ulicy, z poświatą z dołu. Ryzyko A to symetria — łamią ją różne odległości i poziomy obu bram, tablica poza osią i krzywe ulice.

## 9. Czego nie sprawdziłem

- Limit wyszukiwań skończył się w trakcie: nie mam wymiarów hubów poza Fisch; część faktów znam tylko ze streszczeń wyników (PocketGamer.biz, Sportskeeda, esports.gg).
- Kierunek patrzenia po spawnie i brak obrażeń od upadku to zgłoszenia społeczności i moja wiedza, nie dokumentacja — sprawdzić w Studio.
- Początkowego pochylenia kamery nie znam (stąd zapas w regule 25°); kąt poziomy liczyłem przy założeniu, że 70° to pole pionowe.
- Pierwszy kadr policzyłem geometrycznie z obrysów, nie z renderu; nic nie było budowane ani testowane z graczami.
- Kierunku słońca nie mierzyłem; biorę go z `rzemioslo.md`.

Pliki robocze: `<folder roboczy>/tmp_uklad/` — `uklady.json` (trzy układy z wejściami i dojściami), `uklad_a.png`, `uklad_b.png`, `uklad_c.png` (szkice z góry), `sprawdz.py`.

## 10. Źródła (dostęp 13.11.2026)

- Roblox Creator Hub: Humanoid — https://create.roblox.com/docs/reference/engine/classes/Humanoid ; Greybox your environment — https://create.roblox.com/docs/tutorials/curriculums/environmental-art/greybox-your-environment ; Customize the camera — https://create.roblox.com/docs/workspace/camera ; Avatar Settings — https://create.roblox.com/docs/studio/avatar-settings ; Instance streaming — https://create.roblox.com/docs/workspace/streaming ; SpawnLocation — https://create.roblox.com/docs/reference/engine/classes/SpawnLocation ; Onboarding techniques — https://create.roblox.com/docs/production/game-design/onboarding-techniques
- Roblox Core-Scripts, BaseCamera.lua — https://github.com/Roblox/Core-Scripts/blob/master/PlayerScripts/StarterPlayerScripts_NewStructure/RobloxPlayerScript/CameraScript/BaseCamera.lua
- DevForum: Mad Studio map layout design guidebook (23.05.2021) — https://devforum.roblox.com/t/mad-studio-map-layout-design-guidebook/1246963 ; Creating Lobbies (12.08.2019) — https://devforum.roblox.com/t/creating-lobbies-engagement-and-what-to-include/328575 ; kierunek po spawnie (2020) — https://devforum.roblox.com/t/spawn-makes-character-face-wrong-direction/645033
- The Level Design Book: Wayfinding — https://book.leveldesignbook.com/process/blockout/wayfinding ; Typology — https://book.leveldesignbook.com/process/layout/typology
- Game Developer, „A taxonomy of weenies” (22.07.2021) — https://www.gamedeveloper.com/design/a-taxonomy-of-weenies-the-landmarks-that-define-i-ghost-of-tsushima-i-
- „Level Layout, Disneyland Style” (2000) — https://www.above-the-garage.com/wienies/
- Imagineerland, „It all started with a Hub and Spoke” (30.07.2018) — https://imagineerland.blogspot.com/2018/07/it-all-started-with-hub-and-spoke.html
- Fisch: Destructoid (25.12.2024, akt. 14.04.2025) — https://www.destructoid.com/fisch-map-with-all-islands-and-npcs/ ; Gamezebo (27.01.2025) — https://www.gamezebo.com/walkthroughs/fisch-map/
- Grow a Garden 2: AllThings.How (akt. 13.06.2026) — https://allthings.how/grow-a-garden-2-every-major-change-in-the-roblox-sequel/ ; jedynka: esports.gg — https://esports.gg/news/roblox/where-to-find-the-gear-shop-in-grow-a-garden
- Pet Simulator 99: HoldToReset (28.01.2026, akt. 21.10.2026) — https://holdtoreset.com/pet-simulator-99-areas-list-and-whats-in-them
- Bee Swarm Simulator: Bloxodes — https://bloxodes.com/wiki/bee-swarm-simulator/fields
- Steal a Brainrot: AllThings.How (akt. 5.09.2025) — https://allthings.how/steal-a-brainrot-roblox-efficient-stealing-events-and-rebirths ; Sportskeeda — https://www.sportskeeda.com/roblox-news/steal-brainrot-map-guide
- Opracowania tej nocy: `rzemioslo.md` (słońce, wymiary przejść), `styl.md` (wymiary budynków) — ten sam folder
- Udział graczy mobilnych: PocketGamer.biz (04.2025) — https://www.pocketgamer.biz/80-of-roblox-users-are-on-mobile-contributing-46-of-robux-revenue
