---
status: do-decyzji
tags: [produkcja, pytania]
---
# Pytania otwarte

Odpowiedź dopisz pod pytaniem. Jeśli odpowiedź jest decyzją, przenieś ją do [[Rejestr decyzji]].

## 1. Oficjalna pisownia nazwy gry
- Do wyboru: „Blocky n Crycket” (stara dokumentacja) albo „BLOCKY & CRYCKET” (logo i nowsze materiały).
- Potrzebne do napisów w grze, nazwy grupy Roblox i strony gry.
Szczegóły: Dokumentacja używa „**Blocky n Crycket**”, a logo i późniejsze materiały „**BLOCKY & CRYCKET**”. Sejf nazywa się `B&C`.
**Odpowiedź:**

## 2. Gdzie jest zaprojektowane drzewo obiektów Karczmy?
- Dokumentacja mówi, że układ okna Karczmy istnieje, ale nie ma go w plikach projektu.
- Do wskazania: jest w pliku gry, w Figmie, czy projektujemy od nowa.
Szczegóły: Dokumentacja mówi, że struktura UI Karczmy istnieje, ale nie ma jej w `src/gui`. Jest w pliku `.rbxl`, w Figmie, czy gdzie indziej? Zob. [[Okno Karczmy]].
**Odpowiedź:**

## 3. Czy w `.rbxl` są już skrypty lub GUI?
- Jeśli w pliku gry są skrypty albo okna, których nie ma w `src/`, Claude ich nie widzi.
- Do zrobienia przez właściciela pliku: wyeksportować je do `src/`.
Szczegóły: Jeśli tak, wyeksportuj je do `src/`, żeby Claude mógł nad nimi pracować. Zob. [[Rojo i struktura projektu]].
**Odpowiedź:**

## 4. Czy zatwierdzasz propozycje D-006, D-007, D-009, D-010?
Zob. [[Rejestr decyzji]].
Rozstrzyga: D-006, D-007, D-009, D-010
**Odpowiedź:**
- Claude Code (2026-11-13): D-006 i D-007 zatwierdzone przez Karola (D-006 w rozmowie z Claude Code, D-007 w panelu). D-009 Karol odłożył na sesję główną ([[Sesje główne]]). D-010 (fazy roadmapy) czeka dalej w rejestrze.

## 5. Przyciski HUD: kanon czy Figma?
- Kanon: 5 zakładek (Karczma, Pety, Tycoon, Arena, Ekwipunek).
- Wdrożone z Figmy: 6 przycisków (Teleport, Equipment, Pets, Quests, Shop, Guilds).
- Do decyzji: który zestaw zostaje i gdzie trafią Tycoon i Arena. Język napisów rozstrzyga już D-045.
Szczegóły: [[HUD]] (kanon) przewiduje 5 zakładek na krawędziach: Karczma, Pety, Tycoon, Arena, Ekwipunek. Figma (node 9:1570) ma 6 przycisków: Teleport, Equipment, Pets, Quests, Shop, Guilds, z napisami po angielsku. Wdrożono wersję z Figmy. Czy zastępuje ona kanon (wtedy nowa decyzja w [[Rejestr decyzji]])? Gdzie trafią Tycoon i Arena? Czy napisy na przyciskach zostają po angielsku?
Dopisek z 2026-11-14 (sesja główna): język — angielski z tłumaczeniami (propozycja D-045); zestaw przycisków oraz miejsce Tycoona i Areny nie padły. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
**Odpowiedź:**

## 6. Diamenty (Gems) a Magiczne Kryształy
Kanon ([[Twierdza (Tycoon)]], [[HUD]]) zna dwie waluty: **Złoto** i **Magiczne Kryształy**, które pasywnie generują droppery. HUD z Figmy pokazuje **Złoto** i **Diamenty (Gems)**, opisane w specyfikacji HUD jako waluta premium. Czy Diamenty to Magiczne Kryształy pod inną nazwą? Czy waluta jest płatna (Robux), czy zdobywana w grze?
Dopisek z 2026-11-14 (sesja główna): Złoto na przedmioty; Diamenty jako waluta premium kupowana za Robuxy i zdobywana w grze; konwersja tylko Diamenty → Złoto (propozycja D-038); drzewka umiejętności za Diamenty (D-039); trzecia waluta i waluta petów (D-040). Nazwa „Diamenty” jest robocza — Paweł chce tematycznej. O Magicznych Kryształach na sesji nikt nie wspomniał; równoległa propozycja D-031 (z pytania Pawła w panelu) nazywa tę walutę Magiczne Kryształy i wyklucza wydawanie jej na losowania — rozstrzygnąć razem z D-038. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
Rozstrzyga: D-031, D-038
**Odpowiedź:**
- Claude Code (2026-11-14): Paweł zapytał w panelu, czym zastąpić grzybki z S&F jako walutę premium. Propozycja D-031: jedna waluta premium — Magiczne Kryształy z ikoną diamentu z HUD, zdobywana w grze i kupowana za Robuxy w stałych paczkach, wydawana tylko na rzeczy pewne (D-015). Temat był na liście [[Sesje główne]] (odhaczony przez Karola 14.11 bez spisanych ustaleń), więc decyzja w panelu zamknie to pytanie.

## 7. Questy na czas a decyzja D-004
Rozmowa 12.11 [8:54–10:17] wprowadza questy trwające od 3 minut do 5 sekund (skracane rozgłosem strefy) i najemnika, a zatwierdzona D-004 mówi „bez biernego czekania”. Propozycja D-013 godzi oba podejścia: walka od razu, liczniki tylko równolegle. Którą wersję przyjmujecie? Zob. [[Propozycje z rozmowy 2026-11-12]].
Dopisek z 2026-11-14 (sesja główna): czekanie w karczmie zostaje, ale równolegle gracz farmi w strefach, chodzi do dungeonów, sklepu i Twierdzy (propozycja D-034); cutscenka tylko przy bossach, rzadkich przeciwnikach i na koniec zadania (D-033). Zatwierdzenie D-034 zmienia D-004 w części „bez biernego czekania”. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
Rozstrzyga: D-013, D-034
**Odpowiedź:**
- Claude Code (2026-11-13): Na sesję główną. Karol odrzucił D-013 z dopiskiem „dłuższa rozmowa” i „do dyskusji z Pawłem”; temat jest w [[Sesje główne]].

## 8. Karczma: trzy misje czy strefy z rozgłosem i osobne lochy?
Kanon [[Karczma (Questy)]] opisuje trzy misje w mini-dungeonach. Rozmowa: strefy odblokowywane poziomem, a lochy jako osobna oś z portali (łatwy / średni / trudny). Co zostaje z D-009 i Energii?
Dopisek z 2026-11-14 (sesja główna): poziomy łatwy / średni / trudny lokalne dla biomu (propozycja D-032), zadania na czas plus strefy do farmienia (D-034). Energia nie padła — wraca na sesję ([[Sesje główne]]).
**Odpowiedź:**
- Claude Code (2026-11-13): Na sesję główną, razem z D-009 (Karczma: poziomy zadań i Energia). Karol: „będzie to dużo bardziej rozwinięte”; temat jest w [[Sesje główne]].

## 9. Twierdza: kiedy i co produkuje?
- Od którego poziomu gracz dostaje działkę (12.11 padło: ok. 25.).
- Co działka produkuje: Złoto, surowce, klejnoty do broni, Magiczne Kryształy?
- Czy Twierdza wchodzi do pierwszego wydania (D-035 tego nie rozstrzyga).
Szczegóły: Rozmowa [21:46]: działka od ok. 25. poziomu, surowce i klejnoty do osadzania w broni. Kanon [[Twierdza (Tycoon)]]: droppery dające Złoto i Magiczne Kryształy. Rekomendacja Claude Code: pierwszy budynek już w pierwszej sesji. Łączy się z pytaniem 6 o waluty.
Dopisek z 2026-11-14 (sesja główna): temat Walut odhaczono, ale o działce Twierdzy nie rozmawiano. Padło tylko, że podstawa Twierdzy wchodzi do pierwszego wydania, a podziemia później (D-035), oraz drzewko Twierdzy za Diamenty, np. szybsze kopanie (D-039). Wraca na sesję ([[Sesje główne]]).
**Odpowiedź:**

## 10. Styl UI: pixel-art z kanonu czy wdrożony cartoon?
Zob. propozycja D-018 i [[Styl UI gier Roblox]]. Czy napisy na przyciskach przenosimy z grafik do tekstu (tłumaczenia, polskie znaki)?
Dopisek z 2026-11-14 (sesja główna): Paweł obejrzał porównanie i obaj wybrali Krzywe Miasteczko — kreskówka z ciemną kreską, nie pixel-art (propozycja D-041). Napisy natywnie wynikają z D-011 i D-045. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
Rozstrzyga: D-018, D-041
**Odpowiedź:**
- Claude Code (2026-11-13): Decyzja wstrzymana. Karol przy D-018: chce najpierw zobaczyć oba style obok siebie na zdjęciach. Zlecenie na raport z porównaniem jest w [[Zadania]].

## 11. Czy panel zespołu jest zgodny z D-008?
D-008 porzuciła dashboard z agentami na rzecz sejfu. Karol poprosił 12.11 o wspólny panel; zbudowany `panel/` niczego nie trzyma poza sejfem (propozycja D-012, [[Panel zespołu]]). Game Director: zatwierdzasz, zmieniasz zakres czy usuwamy?
Rozstrzyga: D-012
**Odpowiedź:**
- Claude Code (2026-11-13): Rozstrzygnięte decyzją D-012: Karol zatwierdził panel w panelu 13.11.

## 12. Do kogo celujemy i czym zarabiamy?
Gracze poniżej 13 lat (łagodna ocena treści, bez reklam nagradzanych) czy 13+? Czy rezygnujemy z płatnych tokenów losowania (propozycja D-015)? Jak nazwiemy koło fortuny — „Labubu” to cudza marka.
Dopisek z 2026-11-14 (sesja główna): lista produktów za Robuxy — propozycja D-036; bilety na rolki za Robuxy i mistrz gier planszowych — D-037 (konflikt z D-015, pytanie 30); nowa nazwa koła fortuny — zadanie dla agenta w [[Zadania]]. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
**Odpowiedź:**
- Claude Code (2026-11-13): Częściowo rozstrzygnięte decyzjami Karola z 13.11: gra dla wszystkich, także najmłodszych (D-022 odrzucona); bez płatnej losowości i symulowanego hazardu (D-015 zatwierdzona); waluta kupowana za Robuxy ma być (uzasadnienie przy D-021). Kompromis monetyzacji i nazwa koła fortuny idą na sesję główną ([[Sesje główne]]).

## 13. Własność gry i assetów
Konto jednej osoby czy wspólna grupa Roblox? Od tego zależy, kto wgrywa assety i animacje, kto tworzy klucz Open Cloud do analityki i kto dostaje wypłaty.
Dopisek z 2026-11-14 (sesja główna): jedna gra w grupie Roblox, obaj jako współpracownicy, koszt ok. 100 Robuxów (propozycja D-044). Właściciel grupy, wypłaty, klucz i sposób przeniesienia gry — pytanie 31. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
Rozstrzyga: D-044
**Odpowiedź:**
- Karol Balucki (2026-11-14): rozstrzygnięte decyzjami: D-044 zatwierdzona

## 14. Repozytorium publiczne czy prywatne?
W repo są sejf, prompty, plik `.rbxl`, a teraz też dane panelu (raporty, komentarze). Pełna transkrypcja rozmowy i prywatny Warsztat narzędziowy Karola **nie zostały wgrane** właśnie z tego powodu. Zob. [[Workflow i Git]].
Dopisek z 2026-11-14 (sesja główna): Karol — repozytorium ma być prywatne (propozycja D-044). Przełącza właściciel (Paweł) w ustawieniach repozytorium na GitHubie; zadanie w [[Zadania]]. Uwaga: w prywatnym repozytorium darmowe GitHub Pages (planowane lustro panelu) nie działa.
Rozstrzyga: D-044
**Odpowiedź:**
- Karol Balucki (2026-11-14): rozstrzygnięte decyzjami: D-044 zatwierdzona

## 15. Kto zatwierdza kanon, gdy pracują dwie osoby?
Dziś zasady sejfu mówią o jednym Game Directorze. Od 12.11 pracują dwie osoby, każda ze swoim Claude Code. Do czasu odpowiedzi Claude traktuje jako wiążącą tylko zgodę Game Directora (Pawła), a prośby Karola zapisuje jako propozycje. Czy tak ma zostać, czy obaj zatwierdzacie (a spory rozstrzyga Game Director)?
**Odpowiedź:**
- Karol (2026-11-13): Obaj mamy takie same prawa. Wystarczy decyzja jednego, bo i tak stale się porozumiewamy, ale każda decyzja zostaje w logach. Zapisane jako D-030 w [[Rejestr decyzji]]. To decyzja Karola podana w sesji Claude Code; potwierdzenie Pawła — pytanie #27.

## 16. Czy bierzemy myśl przewodnią v2 do szarego prototypu?
Nocna diagnoza (13.11) oceniła obecny pomysł na 3,8/10 i proponuje nową oś: BONK i krzywy montaż ([[Myśl przewodnia v2]], propozycje D-019 i D-020). Na papierze daje to 6,0/10; wyżej może pójść tylko po pomiarze. Najtańszy sprawdzian to tygodniowy szary prototyp z botem-klikaczem (bramka B1). Zgoda na prototyp nie zmienia jeszcze kanonu. Pełna lista 15 decyzji z rekomendacjami: [[Karta ocen v2 i plan sprawdzenia]].
Dopisek z 2026-11-14 (sesja główna): obaj odrzucają v2 (Paweł: „pet simulator w innym wydaniu”); zostajemy przy S&F w 3D z walkami 3D — do kliknięcia „odrzuć” przy D-019 i D-020. Własne zdanie o grze bez cudzej nazwy nadal nie padło. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
Rozstrzyga: D-019, D-020
**Odpowiedź:**
- Claude Code (2026-11-13): Na sesję główną. Karol 13.11: raczej nie — „nie robimy gry dla dzieci ze śmiesznym haczykiem”; chce to przegadać z Pawłem. Temat opisany prostymi słowami w [[Sesje główne]].

## 17. Statystyki i ekwipunek: budujemy teraz czy odsuwamy?
- Pytanie powstało przy propozycji v2, którą na sesji 14.11 odrzuciliście ustnie.
- Jeśli zostajemy przy modelu S&F, punkty statystyk i okno ekwipunku zostają — wystarczy to potwierdzić.
Szczegóły: W nocy 12/13.11 w Studio pojawiły się `ServerScriptService.Server.StatPoints`, `ReplicatedStorage.Shared.Items` i zmiany w `EquipmentPanel` (praca Game Directora). Propozycja v2 odsuwa punkty statystyk (zamiast nich poziomy kumpli i jedna liczba „Moc bandy”), a okno ekwipunku zamienia w okno bandy z plecakiem. Trzy drogi: v2 w całości, hybryda (ekwipunek wraca jako warstwa po bramce B1) albo zostajemy przy statystykach i poprawiamy tylko pierwszą minutę. Kod Game Directora zostaje nietknięty do decyzji.
**Odpowiedź:**

## 18. Publiczność 16+ na start i miękka premiera
Nową grę widzą najpierw tylko gracze 16+ ze sprawdzonym wiekiem (propozycja D-022). Czy projektujemy haczyk i pierwszy test pod nich, a grudzień traktujemy jako miękką premierę bez decyzji „zakończyć”?
Rozstrzyga: D-022
**Odpowiedź:**
- Claude Code (2026-11-13): Rozstrzygnięte decyzją D-022 (odrzucona przez Karola 13.11): grę mają zobaczyć wszyscy, także najmłodsi, więc nie projektujemy jej pod graczy 16+.

## 19. Kufel i alkohol w kanonie
Kanoniczna ikona Karczmy w [[HUD]] to kufel, a [[Ekran ładowania]] ma żarty o kuflu. Roblox dopuszcza odniesienia do alkoholu tylko w grach 18+ (propozycja D-021). Zmieniamy na kociołek i chochlę („Zupa u Chochli”)? Dotyczy też demo v1 mapy (szyld z kuflem na karczmie).
Dopisek z 2026-11-14 (sesja główna): potwierdzone „bez piwa” i mistrz gier planszowych zamiast hazardzisty; ikona i nazwa karczmy w HUD oraz żarty ekranu ładowania nie padły. Uwaga: Paweł nazwał ikonę licznika zadania w HUD „kuflem piwa” — do rozstrzygnięcia tutaj. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
Rozstrzyga: D-021
**Odpowiedź:**
- Claude Code (2026-11-13): Bez alkoholu: Karol 13.11 przy D-022 — w karczmie sok zamiast piwa. D-021 odrzucił z innego powodu (waluta za Robuxy ma być). Ikona i nazwa karczmy w HUD oraz żarty ekranu ładowania idą na sesję główną ([[Sesje główne]]).

## 20. Telemetria: włączamy i kto ma klucz?
Kod jest gotowy i bezwładny (propozycja D-023, [[Telemetria gry]]). Do decyzji: czy w ogóle (wbudowana analityka Roblox działa od 10 graczy dziennie), kto tworzy klucz Open Cloud tylko do odczytu, jak długo trzymamy godziny w Data Store i czy goście panelu z kodem dostępu mają widzieć liczby sprzedaży.
**Odpowiedź:**
- Claude Code (2026-11-13): Włączamy: Karol zatwierdził D-023 w panelu 13.11. Klucz i pozostałe szczegóły ustalimy przy publikacji gry — do tego czasu zakładka Analityka zostaje bez zmian.

## 21. Godziny, telefon testowy i budżet reklamy
- Ile godzin tygodniowo realnie ma każdy z Was.
- Czy kupujemy tani telefon z Androidem do pomiarów.
- Jaki jest limit wydatków na reklamę.
Szczegóły: Plan v2 zakłada dziennik godzin (ok. 20 h na osobę tygodniowo daje Etap A w ok. 4 tygodnie; przy 15 h — ok. 8 tygodni), tani telefon z Androidem do pomiarów oraz reklamę rzędu 400 nowych graczy tygodniowo na kohortę z limitem kwoty od Game Directora. Ile godzin realnie mamy i jaki limit wydatków przyjmujemy?
**Odpowiedź:**

## 22. Czy instrukcja „Glossy Ink” zastępuje Style Lock?
13.11 Game Director przekazał (przez Karola) [[Instrukcja promptów — Glossy Ink]]: nowy stały początek i koniec promptu, negative prompt i żelazne zasady. Różni się od zatwierdzonego [[Style Lock]] (D-001: inny prefiks, z nazwą gry-inspiracji) i od [[Kierunek artystyczny]] (D-002: pixel-art ikon, płaski interfejs). Rekomendacja Claude Code: tak, zastąpić — nowa wersja opisuje to, co faktycznie wdrożono, i nie zawiera cudzej nazwy. Po potwierdzeniu: wpis ✅ w rejestrze (D-027) i przepięcie szablonów skilla `/asset`.
Rozstrzyga: D-027
**Odpowiedź:**
- Karol (2026-11-13): Tak, zastępuje. D-027 jest zatwierdzona, a szablony skilla `/asset` przeszły na nową instrukcję. Decyzja Karola podana w sesji Claude Code.

## 23. Czy włączamy pracę na sejfie z panelu (D-028)?
Panel potrafi już zapisywać do sejfu odpowiedzi na pytania, zadania i — z kluczem Game Directora — statusy decyzji; na razie jest to wyłączone. Do ustalenia przed włączeniem: (1) czy goście z kodem dostępu (np. przez tunel) mogą pisać do sejfu, skoro ich wpisy trafią potem do publicznego repozytorium; (2) dopisanie do `CLAUDE.md` i do [[Jak prowadzimy sejf]] reguły dla agentów: zgodę Game Directora z panelu poznaje się wyłącznie po znaczniku stawianym przez serwer („Game Director, data” w odpowiedzi albo „zdecydował: Game Director …” w rejestrze), a wpis podpisany samym imieniem zgodą nie jest; (3) kto i jak dostaje link z kluczem Game Directora (polecenie `python panel/serwer.py --klucz-gd` na komputerze z panelem). Łączy się z pytaniami #11 i #15.
Rozstrzyga: D-028
**Odpowiedź:**
- Karol (2026-11-13): Włączamy. Dostęp do panelu mamy tylko my dwaj, więc bez dodatkowych ograniczeń dla wejść z kodem dostępu. Zapis działa od tego dnia na komputerze Karola (D-028). Kto zatwierdza i jak to widać w logach, opisuje D-030; link z kluczem zatwierdzania wypisuje `python panel/serwer.py --klucz-gd` na komputerze z panelem.

## 24. Którą drogą postacie trafiają do gry i kto publikuje animacje (D-029)?
Sześć postaci stoi w Studio jako postacie z klocków z 20 klipami animacji ([[Postacie 3D — Blender i Roblox]]). Do ustalenia: (1) czy NPC i pety zostają w grze jako klocki, czy czekamy na import siatek; (2) kto publikuje animacje — według dokumentacji Roblox zasób animacji ma należeć do właściciela gry, więc albo konto Game Directora, albo przeniesienie gry do grupy; (3) czy katalog ekwipunku (41 przedmiotów, sloty łącznie z „drugą ręką” i podziałem torsu) ma się dopasować do slotów w kodzie Game Directora, czy odwrotnie; (4) czy wygląd Rycerza, Kota-Maga i Karczmarza z modeli jest do przyjęcia jako kierunek. Łączy się z pytaniami #15 i #17.
Dopisek z 2026-11-14 (sesja główna): Karol skłania się do klocków Roblox, Paweł pyta „czemu nie Blender?”; oboje chcą najpierw zobaczyć porównanie. Raport „Rycerz w trzech wersjach” czeka w zakładce Decyzje od 13.11 (Karol go nie znalazł); Paweł chce też miasteczko w obu wersjach — zadanie w [[Zadania]]. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
**Odpowiedź:**
- Claude Code (2026-11-13): Kierunek zatwierdzony: D-029 (Karol, panel, 13.11). Karol prosi o raport porównujący styl postaci z części Roblox ze stylem z Blendera („może nie potrzebujemy Blendera?”). Kto publikuje animacje i sloty ekwipunku — po tym raporcie.
- Claude Code (2026-11-14): Karol zaakceptował w panelu raport „Rycerz w trzech wersjach” (14.11, 11:52): klocki Roblox zostają główną drogą dla postaci, a siatki z Blendera bierzemy tylko tam, gdzie pomiar na telefonie pokaże potrzebę. Publikowanie animacji rozwiąże grupa Roblox (D-044); sloty ekwipunku zostają otwarte. Paweł prosił jeszcze o porównanie całego miasteczka w Blenderze i w Robloxie — zadanie w [[Zadania]].

## 25. Czy asymetryczne ramki, nachylone przyciski i komiksowe dymki pasują do Glossy Ink?
- Z kanonu D-002 zostały: asymetryczne ramki, lekko nachylone przyciski i dymki „BAM!/POW!”.
- Glossy Ink i styl Krzywego Miasteczka (D-041) nic o nich nie mówią.
- Do decyzji: zostają, zmieniamy czy rezygnujemy.
Szczegóły: D-027 zastąpiła w [[Kierunek artystyczny]] tylko pixel-art ikon i „płaski (flat design)”. Asymetryczne ramki, lekko nachylone przyciski (obrót od −2 do 2 stopni) i dymki „BAM!/POW!” obowiązują więc dalej jako część D-002, choć [[Instrukcja promptów — Glossy Ink]] o nich nie wspomina, a jej okna to proste, scalone bryły. Zostawiamy, zmieniamy czy rezygnujemy? Łączy się z pytaniem #10 i propozycją D-018.
Dopisek z 2026-11-14 (sesja główna): styl świata wybrany (D-041: Krzywe Miasteczko, kreskówka z ciemną kreską); o ramkach i dymkach nie rozmawiano.
**Odpowiedź:**

## 26. Glossy Ink: szczegóły, których instrukcja nie rozstrzyga
- Arkusz pinezek mapy: czy pominąć w nim frazę „floating map pins” z negative promptu.
- Angielskie zakończenia promptu dla mapy i teł są naszego autorstwa — do potwierdzenia.
- Napisy w grafikach: instrukcja pozwala, zasada skilla zabrania.
- Opis HUD nadal mówi o pixel-artowych ikonach walut.
Szczegóły: Przy przepinaniu skilla `/asset` wyszły cztery sprawy. (1) Stały negative prompt zawiera „floating map pins”, co działa przeciw arkuszowi pinezek mapy — czy przy tym jednym szablonie wolno tę frazę pominąć? (2) Zakończenia promptu dla mapy miasteczka oraz dla pełnych teł i key-artu instrukcja podaje tylko po polsku albo wcale; w szablonach są angielskie wersje naszego autorstwa — do potwierdzenia. (3) Instrukcja pozwala wpisywać dokładne napisy w obrazie, a zasada skilla mówi „zero tekstu w grafikach AI” (napisy natywnie); dziś skill dopuszcza napisy tylko na wyraźną prośbę. (4) Kanoniczna specyfikacja [[HUD]] nadal mówi o pixel-artowych ikonach walut — poprawiamy ją po D-027? Zob. [[Instrukcja promptów — Glossy Ink]], [[Pipeline assetów]].
**Odpowiedź:**

## 27. Paweł: czy potwierdzasz zasadę równych praw (D-030)?
- Karol sam zatwierdził albo odrzucił kilkanaście decyzji 13–14.11.
- Według D-043 każda czeka na odpowiedź Pawła: zgoda, brak zgody albo „przedyskutuj”.
- Paweł przejdzie je po uruchomieniu alertów na Telegramie.
Szczegóły: 13.11.2026 Karol zdecydował, że obaj macie takie same prawa do zatwierdzania decyzji: wystarczy decyzja jednego, a każda zostaje w logach z imieniem i datą (D-030, odpowiedź na pytanie #15). Tego samego wieczoru Karol zatwierdził na tej podstawie D-027 (Glossy Ink) i D-028 (panel jako miejsce pracy). Wcześniejsza zasada mówiła, że kanon zatwierdza tylko Game Director, więc potrzebne jest Twoje potwierdzenie. Do tego czasu decyzje zatwierdzone tylko przez Karola mają jego podpis i możesz je cofnąć.
Dopisek z 2026-11-14 (sesja główna): Paweł na głos — jedna osoba nie powinna zatwierdzać bez wiedzy drugiej. Ustnie przyjęty model „decyzja plus potwierdzenie drugiej osoby po alercie na telefon” to propozycja D-043; D-030 obowiązuje do jej zatwierdzenia. Decyzji Karola z 13.11 Paweł nie przejrzał. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]], pytanie 29.
**Odpowiedź:**

## 28. Mapa teleportacji: lokacje i prefiks stylu
- Propozycja 7 lokacji: Karczma, Arena, Twierdza, Zagroda petów, Targ, Gildia, Portal do lochów.
- Na sesji 14.11 padły inne budynki: sklep z bronią, sklep magiczny, mistrz gier, hala portali.
- Do decyzji: ostateczna lista lokacji. Język nazw rozstrzyga już D-045.
Szczegóły: [[Mapa teleportacji]] proponuje 7 lokacji: Karczma, Arena, Twierdza, Zagroda petów, Targ, Gildia, Portal do lochów. Czy lista jest dobra? Polskie czy angielskie nazwy na mapie?
Prompty w tej notatce opisują styl słowami („hand-inked comic book style…”) zamiast nazwy gry-inspiracji z prefiksu [[Style Lock]] (kanon), bo nazwa cudzej gry ciągnie model do kopiowania jej budynków. Czy zmieniamy też prefiks w Style Lock?
Dopisek z 13.11.2026: prefiks Style Lock zastąpiła instrukcja Glossy Ink (D-027), więc druga część pytania jest rozstrzygnięta. Otwarte zostają lista lokacji i język nazw. Pytanie miało u Pawła numer 7; przy scaleniu dostało numer 28, bo numery 7–27 były już zajęte.
Dopisek z 2026-11-14 (sesja główna): język — angielski z tłumaczeniami (propozycja D-045); lista lokacji nie padła. Budynki wymienione w rozmowie: karczma, sklep z bronią, sklep magiczny, Pety, Twierdza, hala portali do dungeonów (D-042), mistrz gier planszowych. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
**Odpowiedź:**

## 29. Alerty o decyzjach na telefon i panel bez włączonego komputera (D-043)
Na sesji 14.11 Karol zapytał agenta: czy obaj możecie mieć panel na telefonie, czy komputer musi być włączony i czy agent musi działać, żeby druga osoba dostała alert „zgódź się / nie zgódź się / przedyskutuj” i potwierdziła decyzję (propozycja D-043). Paweł woli bota Telegram niż osobną aplikację.
Odpowiedź techniczna agenta (stan na 14.11): panel działa na komputerze gospodarza (dziś Karola); z telefonu wchodzi się przez link tunelu, więc komputer z panelem musi być włączony. Agent (Claude) nie musi działać — zatwierdzanie i odpowiadanie to panel, nie agent. Lustro tylko-do-odczytu na GitHub Pages jest przygotowane, ale nie włączone, i tak nie pozwala zatwierdzać; po przełączeniu repozytorium na prywatne (D-044) darmowe GitHub Pages przestaje działać. Panel nie wysyła dziś żadnych powiadomień. Bot Telegram jest wykonalny: panel po zmianie statusu decyzji wysyła wiadomość z linkiem `#/decyzje?sprawa=D-0XX` przez token bota trzymany lokalnie poza repozytorium; też wymaga włączonego komputera z panelem. Alternatywa: e-mail. Zob. [[Panel zespołu]].
Do decyzji: (1) kanał — Telegram, e-mail czy tylko lista „Czeka na Ciebie” w panelu; (2) czy potwierdzenie drugiej osoby ma być wymagane (D-043), czy wystarczy powiadomienie przy obecnej D-030.
**Odpowiedź:**
- Karol (2026-11-14, w rozmowie z Claude Code): Telegram. Najpierw wersja działająca przy włączonym komputerze z panelem — alert z przyciskami zgoda / brak zgody / przedyskutuj — później wersja bez włączonego komputera. Bota i wspólną grupę zakładają Karol i Paweł; token zostaje lokalnie, poza repozytorium. Potwierdzenie drugiej osoby jest wymagane (D-043).

## 30. Rolki za Robuxy i „mistrz gier planszowych” a D-015
- Pomysł: bilety na rolki za Robuxy i mistrz gier planszowych zamiast hazardzisty.
- Roblox zakazuje stawiania waluty na wynik losowy; losowe nagrody za Robuxy wymagają jawnych szans.
- Do wyboru: (a) bilety za Robuxy z jawnymi szansami i mistrz gier bez stawek; (b) rolki tylko za walutę z gry; (c) bilety za walutę z gry, a za Robuxy sama waluta.
Szczegóły: Na sesji 14.11 Paweł zaproponował losowania jako „RNG, nie hazard”: rolki z jawnymi szansami i mnożnikiem szczęścia, dzienne rolki u kupca, bilety dokupowane za Robuxy, a zamiast hazardzisty mistrz gier planszowych (kostki, pionek, pole daje nagrodę albo mnożnik; można postawić monety, pole może je pomnożyć albo zabrać połowę). Karol: dobrze, „jeżeli da się to sprytnie ukryć”. Zapisane jako propozycja D-037.
Zatwierdzona 13.11 D-015 mówi: losowania tylko za walutę i tokeny zdobywane w grze, bez symulowanego hazardu — uzasadnieniem było unikanie problemów regulacyjnych. Według [[Retencja i monetyzacja — co wolno i co działa]] stawianie waluty, by wygrać więcej, jest w Roblox zakazane niezależnie od nazwy postaci, a bilety i waluta kupione za Robuxy użyte do losowania wymagają jawnych szans przed zakupem. Trzy drogi: (a) zatwierdzić D-037 — nowa decyzja zastępuje D-015, bilety za Robuxy z jawnymi szansami, a mistrz gier bez stawek (rzut za bilet, nagroda zawsze dodatnia); (b) odrzucić — D-015 zostaje, rolki tylko za walutę z gry; (c) środek: bilety tylko za walutę z gry, za Robuxy sama waluta (jak dziś D-015 i propozycja D-031).
Dopisek Claude Code z 2026-11-14 (sprawdzone w oficjalnych zasadach Roblox): symulowany hazard, czyli stawianie waluty na wynik losowy z szansą na więcej albo stratę, jest zakazany także wtedy, gdy waluty nie da się kupić za Robuxy, a nazwa postaci tego nie zmienia. Plansza, na której stawia się monety, a pole je mnoży albo zabiera połowę, pod to podpada. Losowe nagrody kupowane za Robuxy albo za walutę kupioną za Robuxy są dozwolone pod trzema warunkami: lista nagród i dokładne szanse widoczne przed zakupem, sprawdzenie uprawnień gracza (`PolicyService`) i pokazywanie zmienionych szans przy ulepszeniach szczęścia. Darmowa dzienna rolka bez stawki jest bezpieczna. Źródła: create.roblox.com/docs/production/monetization/paid-random-items oraz Roblox Rules of Conduct (en.help.roblox.com/hc/en-us/articles/203313410). Karol przyjął to wyjaśnienie w rozmowie 14.11; D-037 czeka na kliknięcie w panelu.
Rozstrzyga: D-037
**Odpowiedź:**
- Karol Balucki (2026-11-14): rozstrzygnięte decyzjami: D-037 zatwierdzona

## 31. Grupa Roblox: kto zakłada, wypłaty, klucz Open Cloud i przeniesienie gry (D-044)
- Kto zakłada grupę i jest jej właścicielem.
- Jak dzielicie wypłaty.
- Kto tworzy klucz Open Cloud.
- Grę da się przenieść do grupy w Creator Hub (sprostowanie niżej).
Szczegóły: Na sesji 14.11 ustalono kierunek: jedna gra w grupie Roblox, repozytorium prywatne (D-044). Nie padło: (1) kto zakłada grupę i jest jej właścicielem — właściciel ma ostatnie słowo nad grą i ustawieniami wypłat; (2) podział wypłat między Karola i Pawła (Roblox pozwala ustawić procentowy podział przychodów grupy między członków); (3) kto tworzy klucz Open Cloud — przy grupie klucz wydaje się na grupę, więc może to zrobić każdy z odpowiednim uprawnieniem; (4) istniejącej gry Pawła nie da się „przenieść” — publikuje się ją z Roblox Studio jako nową grę grupy, więc gra dostaje nowe ID, a animacje i grafiki wgrane na konta prywatne trzeba wgrać ponownie w imieniu grupy (do potwierdzenia przy spisywaniu kroków). Agent spisze kroki po odpowiedzi ([[Zadania]]). Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]], [[Pipeline assetów]].
Sprostowanie Claude Code z 2026-11-14 do punktu (4): Roblox ma przeniesienie własności gry z konta na grupę. W Creator Hub: Creations → gra → Configure → Settings → Initiate ownership transfer → wybór grupy, w której ma się prawo publikowania; właściciel grupy akceptuje prośbę. Po akceptacji gra na czas przenoszenia staje się prywatna i zamykane są jej serwery, a zmiany zrobione w trakcie nie przechodzą, więc najpierw zapis w Studio. Co dzieje się z animacjami i grafikami wgranymi na konta prywatne, pokazuje okno „Transfer Details” — tego nie sprawdzano. Źródło: create.roblox.com/docs/projects/experience-ownership-transfer.
**Odpowiedź:**

## 32. Pierwsze wydanie: ulepszanie przedmiotów, gildie i lista biomów (D-035)
- Ulepszanie przedmiotów: na premierę (Karol) czy później (Paweł).
- Gildie: na premierę czy później.
- Które biomy i ile na start.
Szczegóły: Lista „na premierę” i „później” jest w D-035. Sporne albo nie padło: (1) ulepszanie przedmiotów (kowal, zaklinanie) — Karol: może od razu, Paweł: później; (2) gildie — Paweł wcześniej chciał je odłożyć, na sesji wprost nie potwierdził; (3) które biomy i ile na start — padło tylko „las od początku, kryształowy wyżej” i „o biomach powiemy później”. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]], [[Roadmapa]].
**Odpowiedź:**

## 33. Krzywe Miasteczko: kolorystyka i czytelność budynków (D-041)
- Co dokładnie poprawić w kolorystyce.
- Jak oznaczać budynki, żeby było widać, co jest czym (Paweł nie rozpoznał sklepu z Petami ani wejścia do dungeonu).
- Czy wejście do dungeonu zastępują wrota z kłódką (D-042).
Szczegóły: Karol na sesji 14.11: Krzywe Miasteczko to styl oficjalny, ale „coś poprawiamy w kolorystyce” — co dokładnie (paleta, nasycenie, kontrast obrysu, kolory dachów)? Paweł nie rozpoznał w podglądzie 3D sklepu z Petami ani wejścia do dungeonu — jak oznaczać budynki (szyldy bez napisów, ikony nad wejściem, charakterystyczny kształt)? Czy wejście do dungeonu zastępują wrota z kłódką i hala portali (D-042)? Zob. [[Klocki — Blender i Roblox]], [[Sesja główna 2026-11-14 — zapis ustaleń]].
**Odpowiedź:**

## 34. Drzewko umiejętności postaci: kształt i zasady (D-039, D-047)
- Paweł zapytał w panelu 14.11, jak rozplanować skill tree postaci.
- Propozycja D-047: trzy gałęzie (Walka, Wyprawa, Fortuna) i pień, pięć pięter za poziom, pierwsza ranga węzła za punkt talentu, kolejne za Diamenty; jedno drzewko dla klas na premierę.
- Do wyboru: (a) tak, jak w D-047; (b) tylko Diamenty, bez punktów talentu (D-039 dosłownie); (c) osobne drzewko dla każdej klasy już na premierę.
Szczegóły: Pełny opis z przykładowymi węzłami, liczbami roboczymi, oknem i szkicem technicznym: [[Drzewko umiejętności postaci]]. Drzewko ma mnożyć statystyki i ekwipunek, nie je zastępować; piętra otwiera poziom postaci, więc Diamenty przyspieszają, ale nie przeskakują pięter (D-035). Liczby (poziomy pięter, koszty w Diamentach, 1 punkt talentu co poziom) są hipotezą do kalkulatora balansu i zależą od tempa zdobywania Diamentów w grze (pytanie 9, D-031). Osobno zostają drzewka petów (D-039, D-040 — temat Pawła w [[Sesje główne]]) i drzewko Twierdzy. Jeśli wybieracie (b) albo (c), odrzućcie D-047 i napiszcie wariant w komentarzu.
Rozstrzyga: D-047
**Odpowiedź:**
