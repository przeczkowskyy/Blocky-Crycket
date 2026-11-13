---
status: do-decyzji
tags: [produkcja, pytania]
---
# Pytania otwarte

Odpowiedź dopisz pod pytaniem. Jeśli odpowiedź jest decyzją, przenieś ją do [[Rejestr decyzji]].

## 1. Oficjalna pisownia nazwy gry
Dokumentacja używa „**Blocky n Crycket**”, a logo i późniejsze materiały „**BLOCKY & CRYCKET**”. Sejf nazywa się `B&C`.
**Odpowiedź:**

## 2. Gdzie jest zaprojektowane drzewo obiektów Karczmy?
Dokumentacja mówi, że struktura UI Karczmy istnieje, ale nie ma jej w `src/gui`. Jest w pliku `.rbxl`, w Figmie, czy gdzie indziej? Zob. [[Okno Karczmy]].
**Odpowiedź:**

## 3. Czy w `.rbxl` są już skrypty lub GUI?
Jeśli tak, wyeksportuj je do `src/`, żeby Claude mógł nad nimi pracować. Zob. [[Rojo i struktura projektu]].
**Odpowiedź:**

## 4. Czy zatwierdzasz propozycje D-006, D-007, D-009, D-010?
Zob. [[Rejestr decyzji]].
**Odpowiedź:**
- Claude Code (2026-11-13): D-006 i D-007 zatwierdzone przez Karola (D-006 w rozmowie z Claude Code, D-007 w panelu). D-009 Karol odłożył na sesję główną ([[Sesje główne]]). D-010 (fazy roadmapy) czeka dalej w rejestrze.

## 5. Przyciski HUD: kanon czy Figma?
[[HUD]] (kanon) przewiduje 5 zakładek na krawędziach: Karczma, Pety, Tycoon, Arena, Ekwipunek. Figma (node 9:1570) ma 6 przycisków: Teleport, Equipment, Pets, Quests, Shop, Guilds, z napisami po angielsku. Wdrożono wersję z Figmy. Czy zastępuje ona kanon (wtedy nowa decyzja w [[Rejestr decyzji]])? Gdzie trafią Tycoon i Arena? Czy napisy na przyciskach zostają po angielsku?
**Odpowiedź:**

## 6. Diamenty (Gems) a Magiczne Kryształy
Kanon ([[Twierdza (Tycoon)]], [[HUD]]) zna dwie waluty: **Złoto** i **Magiczne Kryształy**, które pasywnie generują droppery. HUD z Figmy pokazuje **Złoto** i **Diamenty (Gems)**, opisane w specyfikacji HUD jako waluta premium. Czy Diamenty to Magiczne Kryształy pod inną nazwą? Czy waluta jest płatna (Robux), czy zdobywana w grze?
**Odpowiedź:**

## 7. Questy na czas a decyzja D-004
Rozmowa 12.11 [8:54–10:17] wprowadza questy trwające od 3 minut do 5 sekund (skracane rozgłosem strefy) i najemnika, a zatwierdzona D-004 mówi „bez biernego czekania”. Propozycja D-013 godzi oba podejścia: walka od razu, liczniki tylko równolegle. Którą wersję przyjmujecie? Zob. [[Propozycje z rozmowy 2026-11-12]].
**Odpowiedź:**
- Claude Code (2026-11-13): Na sesję główną. Karol odrzucił D-013 z dopiskiem „dłuższa rozmowa” i „do dyskusji z Pawłem”; temat jest w [[Sesje główne]].

## 8. Karczma: trzy misje czy strefy z rozgłosem i osobne lochy?
Kanon [[Karczma (Questy)]] opisuje trzy misje w mini-dungeonach. Rozmowa: strefy odblokowywane poziomem, a lochy jako osobna oś z portali (łatwy / średni / trudny). Co zostaje z D-009 i Energii?
**Odpowiedź:**
- Claude Code (2026-11-13): Na sesję główną, razem z D-009 (Karczma: poziomy zadań i Energia). Karol: „będzie to dużo bardziej rozwinięte”; temat jest w [[Sesje główne]].

## 9. Twierdza: kiedy i co produkuje?
Rozmowa [21:46]: działka od ok. 25. poziomu, surowce i klejnoty do osadzania w broni. Kanon [[Twierdza (Tycoon)]]: droppery dające Złoto i Magiczne Kryształy. Rekomendacja Claude Code: pierwszy budynek już w pierwszej sesji. Łączy się z pytaniem 6 o waluty.
**Odpowiedź:**

## 10. Styl UI: pixel-art z kanonu czy wdrożony cartoon?
Zob. propozycja D-018 i [[Styl UI gier Roblox]]. Czy napisy na przyciskach przenosimy z grafik do tekstu (tłumaczenia, polskie znaki)?
**Odpowiedź:**
- Claude Code (2026-11-13): Decyzja wstrzymana. Karol przy D-018: chce najpierw zobaczyć oba style obok siebie na zdjęciach. Zlecenie na raport z porównaniem jest w [[Zadania]].

## 11. Czy panel zespołu jest zgodny z D-008?
D-008 porzuciła dashboard z agentami na rzecz sejfu. Karol poprosił 12.11 o wspólny panel; zbudowany `panel/` niczego nie trzyma poza sejfem (propozycja D-012, [[Panel zespołu]]). Game Director: zatwierdzasz, zmieniasz zakres czy usuwamy?
**Odpowiedź:**
- Claude Code (2026-11-13): Rozstrzygnięte decyzją D-012: Karol zatwierdził panel w panelu 13.11.

## 12. Do kogo celujemy i czym zarabiamy?
Gracze poniżej 13 lat (łagodna ocena treści, bez reklam nagradzanych) czy 13+? Czy rezygnujemy z płatnych tokenów losowania (propozycja D-015)? Jak nazwiemy koło fortuny — „Labubu” to cudza marka.
**Odpowiedź:**
- Claude Code (2026-11-13): Częściowo rozstrzygnięte decyzjami Karola z 13.11: gra dla wszystkich, także najmłodszych (D-022 odrzucona); bez płatnej losowości i symulowanego hazardu (D-015 zatwierdzona); waluta kupowana za Robuxy ma być (uzasadnienie przy D-021). Kompromis monetyzacji i nazwa koła fortuny idą na sesję główną ([[Sesje główne]]).

## 13. Własność gry i assetów
Konto jednej osoby czy wspólna grupa Roblox? Od tego zależy, kto wgrywa assety i animacje, kto tworzy klucz Open Cloud do analityki i kto dostaje wypłaty.
**Odpowiedź:**

## 14. Repozytorium publiczne czy prywatne?
W repo są sejf, prompty, plik `.rbxl`, a teraz też dane panelu (raporty, komentarze). Pełna transkrypcja rozmowy i prywatny Warsztat narzędziowy Karola **nie zostały wgrane** właśnie z tego powodu. Zob. [[Workflow i Git]].
**Odpowiedź:**

## 15. Kto zatwierdza kanon, gdy pracują dwie osoby?
Dziś zasady sejfu mówią o jednym Game Directorze. Od 12.11 pracują dwie osoby, każda ze swoim Claude Code. Do czasu odpowiedzi Claude traktuje jako wiążącą tylko zgodę Game Directora (Pawła), a prośby Karola zapisuje jako propozycje. Czy tak ma zostać, czy obaj zatwierdzacie (a spory rozstrzyga Game Director)?
**Odpowiedź:**
- Karol (2026-11-13): Obaj mamy takie same prawa. Wystarczy decyzja jednego, bo i tak stale się porozumiewamy, ale każda decyzja zostaje w logach. Zapisane jako D-030 w [[Rejestr decyzji]]. To decyzja Karola podana w sesji Claude Code; potwierdzenie Pawła — pytanie #27.

## 16. Czy bierzemy myśl przewodnią v2 do szarego prototypu?
Nocna diagnoza (13.11) oceniła obecny pomysł na 3,8/10 i proponuje nową oś: BONK i krzywy montaż ([[Myśl przewodnia v2]], propozycje D-019 i D-020). Na papierze daje to 6,0/10; wyżej może pójść tylko po pomiarze. Najtańszy sprawdzian to tygodniowy szary prototyp z botem-klikaczem (bramka B1). Zgoda na prototyp nie zmienia jeszcze kanonu. Pełna lista 15 decyzji z rekomendacjami: [[Karta ocen v2 i plan sprawdzenia]].
**Odpowiedź:**
- Claude Code (2026-11-13): Na sesję główną. Karol 13.11: raczej nie — „nie robimy gry dla dzieci ze śmiesznym haczykiem”; chce to przegadać z Pawłem. Temat opisany prostymi słowami w [[Sesje główne]].

## 17. Statystyki i ekwipunek: budujemy teraz czy odsuwamy?
W nocy 12/13.11 w Studio pojawiły się `ServerScriptService.Server.StatPoints`, `ReplicatedStorage.Shared.Items` i zmiany w `EquipmentPanel` (praca Game Directora). Propozycja v2 odsuwa punkty statystyk (zamiast nich poziomy kumpli i jedna liczba „Moc bandy”), a okno ekwipunku zamienia w okno bandy z plecakiem. Trzy drogi: v2 w całości, hybryda (ekwipunek wraca jako warstwa po bramce B1) albo zostajemy przy statystykach i poprawiamy tylko pierwszą minutę. Kod Game Directora zostaje nietknięty do decyzji.
**Odpowiedź:**

## 18. Publiczność 16+ na start i miękka premiera
Nową grę widzą najpierw tylko gracze 16+ ze sprawdzonym wiekiem (propozycja D-022). Czy projektujemy haczyk i pierwszy test pod nich, a grudzień traktujemy jako miękką premierę bez decyzji „zakończyć”?
**Odpowiedź:**
- Claude Code (2026-11-13): Rozstrzygnięte decyzją D-022 (odrzucona przez Karola 13.11): grę mają zobaczyć wszyscy, także najmłodsi, więc nie projektujemy jej pod graczy 16+.

## 19. Kufel i alkohol w kanonie
Kanoniczna ikona Karczmy w [[HUD]] to kufel, a [[Ekran ładowania]] ma żarty o kuflu. Roblox dopuszcza odniesienia do alkoholu tylko w grach 18+ (propozycja D-021). Zmieniamy na kociołek i chochlę („Zupa u Chochli”)? Dotyczy też demo v1 mapy (szyld z kuflem na karczmie).
**Odpowiedź:**
- Claude Code (2026-11-13): Bez alkoholu: Karol 13.11 przy D-022 — w karczmie sok zamiast piwa. D-021 odrzucił z innego powodu (waluta za Robuxy ma być). Ikona i nazwa karczmy w HUD oraz żarty ekranu ładowania idą na sesję główną ([[Sesje główne]]).

## 20. Telemetria: włączamy i kto ma klucz?
Kod jest gotowy i bezwładny (propozycja D-023, [[Telemetria gry]]). Do decyzji: czy w ogóle (wbudowana analityka Roblox działa od 10 graczy dziennie), kto tworzy klucz Open Cloud tylko do odczytu, jak długo trzymamy godziny w Data Store i czy goście panelu z kodem dostępu mają widzieć liczby sprzedaży.
**Odpowiedź:**
- Claude Code (2026-11-13): Włączamy: Karol zatwierdził D-023 w panelu 13.11. Klucz i pozostałe szczegóły ustalimy przy publikacji gry — do tego czasu zakładka Analityka zostaje bez zmian.

## 21. Godziny, telefon testowy i budżet reklamy
Plan v2 zakłada dziennik godzin (ok. 20 h na osobę tygodniowo daje Etap A w ok. 4 tygodnie; przy 15 h — ok. 8 tygodni), tani telefon z Androidem do pomiarów oraz reklamę rzędu 400 nowych graczy tygodniowo na kohortę z limitem kwoty od Game Directora. Ile godzin realnie mamy i jaki limit wydatków przyjmujemy?
**Odpowiedź:**

## 22. Czy instrukcja „Glossy Ink” zastępuje Style Lock?
13.11 Game Director przekazał (przez Karola) [[Instrukcja promptów — Glossy Ink]]: nowy stały początek i koniec promptu, negative prompt i żelazne zasady. Różni się od zatwierdzonego [[Style Lock]] (D-001: inny prefiks, z nazwą gry-inspiracji) i od [[Kierunek artystyczny]] (D-002: pixel-art ikon, płaski interfejs). Rekomendacja Claude Code: tak, zastąpić — nowa wersja opisuje to, co faktycznie wdrożono, i nie zawiera cudzej nazwy. Po potwierdzeniu: wpis ✅ w rejestrze (D-027) i przepięcie szablonów skilla `/asset`.
**Odpowiedź:**
- Karol (2026-11-13): Tak, zastępuje. D-027 jest zatwierdzona, a szablony skilla `/asset` przeszły na nową instrukcję. Decyzja Karola podana w sesji Claude Code.

## 23. Czy włączamy pracę na sejfie z panelu (D-028)?
Panel potrafi już zapisywać do sejfu odpowiedzi na pytania, zadania i — z kluczem Game Directora — statusy decyzji; na razie jest to wyłączone. Do ustalenia przed włączeniem: (1) czy goście z kodem dostępu (np. przez tunel) mogą pisać do sejfu, skoro ich wpisy trafią potem do publicznego repozytorium; (2) dopisanie do `CLAUDE.md` i do [[Jak prowadzimy sejf]] reguły dla agentów: zgodę Game Directora z panelu poznaje się wyłącznie po znaczniku stawianym przez serwer („Game Director, data” w odpowiedzi albo „zdecydował: Game Director …” w rejestrze), a wpis podpisany samym imieniem zgodą nie jest; (3) kto i jak dostaje link z kluczem Game Directora (polecenie `python panel/serwer.py --klucz-gd` na komputerze z panelem). Łączy się z pytaniami #11 i #15.
**Odpowiedź:**
- Karol (2026-11-13): Włączamy. Dostęp do panelu mamy tylko my dwaj, więc bez dodatkowych ograniczeń dla wejść z kodem dostępu. Zapis działa od tego dnia na komputerze Karola (D-028). Kto zatwierdza i jak to widać w logach, opisuje D-030; link z kluczem zatwierdzania wypisuje `python panel/serwer.py --klucz-gd` na komputerze z panelem.

## 24. Którą drogą postacie trafiają do gry i kto publikuje animacje (D-029)?
Sześć postaci stoi w Studio jako postacie z klocków z 20 klipami animacji ([[Postacie 3D — Blender i Roblox]]). Do ustalenia: (1) czy NPC i pety zostają w grze jako klocki, czy czekamy na import siatek; (2) kto publikuje animacje — według dokumentacji Roblox zasób animacji ma należeć do właściciela gry, więc albo konto Game Directora, albo przeniesienie gry do grupy; (3) czy katalog ekwipunku (41 przedmiotów, sloty łącznie z „drugą ręką” i podziałem torsu) ma się dopasować do slotów w kodzie Game Directora, czy odwrotnie; (4) czy wygląd Rycerza, Kota-Maga i Karczmarza z modeli jest do przyjęcia jako kierunek. Łączy się z pytaniami #15 i #17.
**Odpowiedź:**
- Claude Code (2026-11-13): Kierunek zatwierdzony: D-029 (Karol, panel, 13.11). Karol prosi o raport porównujący styl postaci z części Roblox ze stylem z Blendera („może nie potrzebujemy Blendera?”). Kto publikuje animacje i sloty ekwipunku — po tym raporcie.

## 25. Czy asymetryczne ramki, nachylone przyciski i komiksowe dymki pasują do Glossy Ink?
D-027 zastąpiła w [[Kierunek artystyczny]] tylko pixel-art ikon i „płaski (flat design)”. Asymetryczne ramki, lekko nachylone przyciski (obrót od −2 do 2 stopni) i dymki „BAM!/POW!” obowiązują więc dalej jako część D-002, choć [[Instrukcja promptów — Glossy Ink]] o nich nie wspomina, a jej okna to proste, scalone bryły. Zostawiamy, zmieniamy czy rezygnujemy? Łączy się z pytaniem #10 i propozycją D-018.
**Odpowiedź:**

## 26. Glossy Ink: szczegóły, których instrukcja nie rozstrzyga
Przy przepinaniu skilla `/asset` wyszły cztery sprawy. (1) Stały negative prompt zawiera „floating map pins”, co działa przeciw arkuszowi pinezek mapy — czy przy tym jednym szablonie wolno tę frazę pominąć? (2) Zakończenia promptu dla mapy miasteczka oraz dla pełnych teł i key-artu instrukcja podaje tylko po polsku albo wcale; w szablonach są angielskie wersje naszego autorstwa — do potwierdzenia. (3) Instrukcja pozwala wpisywać dokładne napisy w obrazie, a zasada skilla mówi „zero tekstu w grafikach AI” (napisy natywnie); dziś skill dopuszcza napisy tylko na wyraźną prośbę. (4) Kanoniczna specyfikacja [[HUD]] nadal mówi o pixel-artowych ikonach walut — poprawiamy ją po D-027? Zob. [[Instrukcja promptów — Glossy Ink]], [[Pipeline assetów]].
**Odpowiedź:**

## 27. Paweł: czy potwierdzasz zasadę równych praw (D-030)?
13.11.2026 Karol zdecydował, że obaj macie takie same prawa do zatwierdzania decyzji: wystarczy decyzja jednego, a każda zostaje w logach z imieniem i datą (D-030, odpowiedź na pytanie #15). Tego samego wieczoru Karol zatwierdził na tej podstawie D-027 (Glossy Ink) i D-028 (panel jako miejsce pracy). Wcześniejsza zasada mówiła, że kanon zatwierdza tylko Game Director, więc potrzebne jest Twoje potwierdzenie. Do tego czasu decyzje zatwierdzone tylko przez Karola mają jego podpis i możesz je cofnąć.
**Odpowiedź:**

## 28. Mapa teleportacji: lokacje i prefiks stylu
[[Mapa teleportacji]] proponuje 7 lokacji: Karczma, Arena, Twierdza, Zagroda petów, Targ, Gildia, Portal do lochów. Czy lista jest dobra? Polskie czy angielskie nazwy na mapie?
Prompty w tej notatce opisują styl słowami („hand-inked comic book style…”) zamiast nazwy gry-inspiracji z prefiksu [[Style Lock]] (kanon), bo nazwa cudzej gry ciągnie model do kopiowania jej budynków. Czy zmieniamy też prefiks w Style Lock?
Dopisek z 13.11.2026: prefiks Style Lock zastąpiła instrukcja Glossy Ink (D-027), więc druga część pytania jest rozstrzygnięta. Otwarte zostają lista lokacji i język nazw. Pytanie miało u Pawła numer 7; przy scaleniu dostało numer 28, bo numery 7–27 były już zajęte.
**Odpowiedź:**
