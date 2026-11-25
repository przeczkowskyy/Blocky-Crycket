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
- Karol Balucki (2026-11-14): BLOCKY & CRYCKET

## 2. Gdzie jest zaprojektowane drzewo obiektów Karczmy?
- Dokumentacja mówi, że układ okna Karczmy istnieje, ale nie ma go w plikach projektu.
- Do wskazania: jest w pliku gry, w Figmie, czy projektujemy od nowa.
Szczegóły: Dokumentacja mówi, że struktura UI Karczmy istnieje, ale nie ma jej w `src/gui`. Jest w pliku `.rbxl`, w Figmie, czy gdzie indziej? Zob. [[Okno Karczmy]].
**Odpowiedź:**
- Karol Balucki (2026-11-14): Nie ma chyba

## 3. Czy w `.rbxl` są już skrypty lub GUI?
- Jeśli w pliku gry są skrypty albo okna, których nie ma w `src/`, Claude ich nie widzi.
- Do zrobienia przez właściciela pliku: wyeksportować je do `src/`.
Szczegóły: Jeśli tak, wyeksportuj je do `src/`, żeby Claude mógł nad nimi pracować. Zob. [[Rojo i struktura projektu]].
**Odpowiedź:**
- Karol Balucki (2026-11-14): Sprawdź

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
Dopisek z 2026-11-14 (trzecia sesja): Teleport ma otwierać widok miasta z lotu ptaka z pinami dostępnych lokacji (propozycja D-064); gildie dopiero po premierze (D-067), więc przycisk „Guilds” nie ma treści na start. Zestaw przycisków nadal nie padł. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
**Odpowiedź:**
- Karol Balucki (2026-11-16): nieaktualne

## 6. Diamenty (Gems) a Magiczne Kryształy
Kanon ([[Twierdza (Tycoon)]], [[HUD]]) zna dwie waluty: **Złoto** i **Magiczne Kryształy**, które pasywnie generują droppery. HUD z Figmy pokazuje **Złoto** i **Diamenty (Gems)**, opisane w specyfikacji HUD jako waluta premium. Czy Diamenty to Magiczne Kryształy pod inną nazwą? Czy waluta jest płatna (Robux), czy zdobywana w grze?
Dopisek z 2026-11-14 (sesja główna): Złoto na przedmioty; Diamenty jako waluta premium kupowana za Robuxy i zdobywana w grze; konwersja tylko Diamenty → Złoto (propozycja D-038); drzewka umiejętności za Diamenty (D-039); trzecia waluta i waluta petów (D-040). Nazwa „Diamenty” jest robocza — Paweł chce tematycznej. O Magicznych Kryształach na sesji nikt nie wspomniał; równoległa propozycja D-031 (z pytania Pawła w panelu) nazywa tę walutę Magiczne Kryształy i wyklucza wydawanie jej na losowania — rozstrzygnąć razem z D-038. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
Dopisek z 2026-11-14 (druga sesja): Twierdza ma mieć kopalnię diamentów (propozycja D-049), czyli produkować walutę premium, a D-031 przewiduje, że droppery dają tylko Złoto albo bardzo mało Kryształów — jedno z nich trzeba zmienić. Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-14 (trzecia sesja): przy drzewkach obaj mówili „Gemy” (słowo z kodu HUD) — węzły drzewek kupuje się za Gemy, bez punktów talentu, a Gemy rzadko wypadają też z potworów (propozycja D-057). Nazwy nikt nie wybierał: Gemy, Diamenty czy Magiczne Kryształy — nadal do decyzji. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
Dopisek z 2026-11-17 (przy przepisywaniu notatek o grze): nazwy dalej nie są uporządkowane — „Diamenty” (HUD, D-038), „Gemy” (D-057), „Magiczne Kryształy” (D-031), a D-086 nazywa „walutą premium” Rybki. Nie wiadomo też, czy kryształ z kopalni kryształów (D-049, D-061) to ta sama waluta. Notatki piszą na razie „waluta premium (w HUD Diamenty)”.
Dopisek z 2026-11-17 (sesja główna 20:53): nazwa znowu nie padła (Karol mówił „Gemy”, Paweł „diamenty”). Ustalono tylko, skąd gracz bierze tę walutę bez płacenia: z walk, za poziom, z kopalni i za Rebirth (propozycje D-099, D-100). Zob. [[Sesja główna 2026-11-17 — zapis ustaleń]].
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
Dopisek z 2026-11-14 (druga sesja): Energia — rezygnacja (propozycja D-048): Karol zaproponował, Paweł zgodził się; farmienie stref i tak nie miało jej zużywać. Pasek „Many/Energii” w HUD zostałby paskiem Many. Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-17 (przy przepisywaniu notatki [[Karczma (Questy)]]): żadna decyzja nie mówi, czy zadanie na czas (D-034) kończy się walką albo mini-dungeonem z dokumentacji i czy zostaje klikanie w beczkę, które przyspiesza zadanie. W notatce stoi to jako sprawa otwarta.
Rozstrzyga: D-032, D-034, D-048
**Odpowiedź:**
- Claude Code (2026-11-13): Na sesję główną, razem z D-009 (Karczma: poziomy zadań i Energia). Karol: „będzie to dużo bardziej rozwinięte”; temat jest w [[Sesje główne]].

## 9. Twierdza: kiedy i co produkuje?
- Od którego poziomu działka: 12.11 padło ok. 25.; na drugiej sesji 14.11 Paweł chce Training Center od początku za grosze.
- Co produkuje — lista z drugiej sesji w propozycji D-049 (Złoto, Diamenty, drewno, kamień, doświadczenie, kryształy wyżej); Magiczne Kryształy z kanonu i klejnoty do broni nie padły.
- Training Center na działce czy obok (D-050); podziemia — nie padło.
Szczegóły: Rozmowa [21:46]: działka od ok. 25. poziomu, surowce i klejnoty do osadzania w broni. Kanon [[Twierdza (Tycoon)]]: droppery dające Złoto i Magiczne Kryształy. Rekomendacja Claude Code: pierwszy budynek już w pierwszej sesji. Łączy się z pytaniem 6 o waluty.
Dopisek z 2026-11-14 (sesja główna): temat Walut odhaczono, ale o działce Twierdzy nie rozmawiano. Padło tylko, że podstawa Twierdzy wchodzi do pierwszego wydania, a podziemia później (D-035), oraz drzewko Twierdzy za Diamenty, np. szybsze kopanie (D-039). Wraca na sesję ([[Sesje główne]]).
Dopisek z 2026-11-14 (druga sesja): Twierdzę omówiono i odhaczono — zamek z mini-budynkami i lista budynków (D-049), Training Center z mini-grami na statystyki (D-050), kowal i zaklinacz w biomie (D-051), stajnia petów poza działką, w mieście (D-052). Nie padło: poziom odblokowania działki (Karol zapytał „to Twierdza główna jest od początku?” — bez odpowiedzi), miejsce Training Center, podziemia. Odrzucone w rozmowie: napady na twierdze innych graczy. Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-14 (trzecia sesja): działka Twierdzy i Training Center **od pierwszego poziomu** (Karol; Paweł potwierdził Training Center od razu) — propozycja D-063, która zamienia też sześć stref Training Center na jeden budynek z wyborem mini-gry. Drzewko Twierdzy mnoży procentowo wydajność konkretnego budynku (D-056). Podziemia nie padły. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
Dopisek z 2026-11-17 (przy przepisywaniu notatki [[Twierdza (Tycoon)]]): dwie sprawy bez rozstrzygnięcia. Pierwsza: Training Center stoi na działce Twierdzy (D-049) czy w mieście — D-085 wymienia w mieście „mini-gry do wyboru z jednego panelu”, a próbne miasteczko-bazar ma tam trenera. Druga: surowce na budynki pochodzą z misji w karczmie (dokumentacja), z budynków Twierdzy (D-049) czy z obu.
**Odpowiedź:**
- Karol Balucki (2026-11-14): 25 poziom na kopalnie itd, a ceneter od początku. Twoje propozycje są dobre i dobrze wyłapałeś z rozmowy

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
Dopisek z 2026-11-14 (druga sesja): Training Center z mini-grami na statystyki (propozycja D-050) zakłada, że punkty statystyk zostają; Paweł mówił o sześciu statystykach — tyle ma lista w [[System RPG]].
Dopisek z 2026-11-14 (trzecia sesja): obaj policzyli sześć statystyk z ikon w assetach (Siła, Życie, Inteligencja, Zręczność, Szczęście, Pancerz) i przypisali im role — propozycja D-062: Pancerz jako punkty odejmowane od ciosu, Inteligencja jako moc umiejętności i odporność na magię, Zręczność jako unik z limitem klasy, Szczęście jako krytyk. Punkty statystyk za poziom zostają (D-057). Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
**Odpowiedź:**
- Karol Balucki (2026-11-14): Tak. Budujemy i rozpoczynami badania balansujące klasy pomiędzy sobą i progresynowścią gry

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
- Karol Balucki (2026-11-14): codziennie każdy może spędzić 2 godziny. Wydatki na reklame to około 2000 zł

## 22. Czy instrukcja „Glossy Ink” zastępuje Style Lock?
13.11 Game Director przekazał (przez Karola) [[Instrukcja promptów — Glossy Ink]]: nowy stały początek i koniec promptu, negative prompt i żelazne zasady. Różni się od zatwierdzonego [[Style Lock]] (D-001: inny prefiks, z nazwą gry-inspiracji) i od [[Kierunek artystyczny]] (D-002: pixel-art ikon, płaski interfejs). Rekomendacja Claude Code: tak, zastąpić — nowa wersja opisuje to, co faktycznie wdrożono, i nie zawiera cudzej nazwy. Po potwierdzeniu: wpis ✅ w rejestrze (D-027) i przepięcie szablonów skilla `/asset`.
2026-11-14: szablony skilla `/asset` przepiął Karol 13.11 (D-027 zatwierdzona przez niego, potwierdzenie Pawła → pytanie 27); Claude Code u Pawła dopisał model Nano Banana 2.1.
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
Dopisek z 2026-11-14 (trzecia sesja): Paweł — „Blender, zdecydowanie”; Karol — postacie i pety projektuje on w Blenderze (propozycja D-065). To przeciwne do odpowiedzi niżej z 11:52 (klocki Roblox główną drogą) — jedno z dwojga trzeba potwierdzić w panelu. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
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
- Karol Balucki (2026-11-14): Tu zostawiam to Claudowi, aby utrzymać gre kolorwą i zauleżniająca, czyli mnustwo tego efektu BAM POW

## 26. Glossy Ink: szczegóły, których instrukcja nie rozstrzyga
- Arkusz pinezek mapy: czy pominąć w nim frazę „floating map pins” z negative promptu.
- Angielskie zakończenia promptu dla mapy i teł są naszego autorstwa — do potwierdzenia.
- Napisy w grafikach: instrukcja pozwala, zasada skilla zabrania.
- Opis HUD nadal mówi o pixel-artowych ikonach walut.
Szczegóły: Przy przepinaniu skilla `/asset` wyszły cztery sprawy. (1) Stały negative prompt zawiera „floating map pins”, co działa przeciw arkuszowi pinezek mapy — czy przy tym jednym szablonie wolno tę frazę pominąć? (2) Zakończenia promptu dla mapy miasteczka oraz dla pełnych teł i key-artu instrukcja podaje tylko po polsku albo wcale; w szablonach są angielskie wersje naszego autorstwa — do potwierdzenia. (3) Instrukcja pozwala wpisywać dokładne napisy w obrazie, a zasada skilla mówi „zero tekstu w grafikach AI” (napisy natywnie); dziś skill dopuszcza napisy tylko na wyraźną prośbę. (4) Kanoniczna specyfikacja [[HUD]] nadal mówi o pixel-artowych ikonach walut — poprawiamy ją po D-027? Zob. [[Instrukcja promptów — Glossy Ink]], [[Pipeline assetów]].
**Odpowiedź:**
- Karol Balucki (2026-11-14): NIEAKTUALNE

## 27. Paweł: czy potwierdzasz zasadę równych praw (D-030)?
- Karol sam zatwierdził albo odrzucił kilkanaście decyzji 13–14.11.
- Według D-043 każda czeka na odpowiedź Pawła: zgoda, brak zgody albo „przedyskutuj”.
- Paweł przejdzie je po uruchomieniu alertów na Telegramie.
Szczegóły: 13.11.2026 Karol zdecydował, że obaj macie takie same prawa do zatwierdzania decyzji: wystarczy decyzja jednego, a każda zostaje w logach z imieniem i datą (D-030, odpowiedź na pytanie #15). Tego samego wieczoru Karol zatwierdził na tej podstawie D-027 (Glossy Ink) i D-028 (panel jako miejsce pracy). Wcześniejsza zasada mówiła, że kanon zatwierdza tylko Game Director, więc potrzebne jest Twoje potwierdzenie. Do tego czasu decyzje zatwierdzone tylko przez Karola mają jego podpis i możesz je cofnąć.
Dopisek z 2026-11-14 (sesja główna): Paweł na głos — jedna osoba nie powinna zatwierdzać bez wiedzy drugiej. Ustnie przyjęty model „decyzja plus potwierdzenie drugiej osoby po alercie na telefon” to propozycja D-043; D-030 obowiązuje do jej zatwierdzenia. Decyzji Karola z 13.11 Paweł nie przejrzał. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]], pytanie 29.
Dopisek z 2026-11-14 (trzecia sesja): Karol odhaczył temat w agendzie bez przeglądu („nie doszło do przeglądu, Telegram jest gotowy”) — przegląd ma iść przez alerty na Telegramie. Tego popołudnia Paweł potwierdził przez Telegram D-050, D-052, D-054, D-055 i odrzucenie D-047; wcześniejsze decyzje Karola z 13–14.11 nadal czekają. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
**Odpowiedź:**
- Karol Balucki (2026-11-16): nieaktualne

## 28. Mapa teleportacji: lokacje i prefiks stylu
- Propozycja 7 lokacji: Karczma, Arena, Twierdza, Zagroda petów, Targ, Gildia, Portal do lochów.
- Na sesji 14.11 padły inne budynki: sklep z bronią, sklep magiczny, mistrz gier, hala portali.
- Do decyzji: ostateczna lista lokacji. Język nazw rozstrzyga już D-045.
Szczegóły: [[Mapa teleportacji]] proponuje 7 lokacji: Karczma, Arena, Twierdza, Zagroda petów, Targ, Gildia, Portal do lochów. Czy lista jest dobra? Polskie czy angielskie nazwy na mapie?
Prompty w tej notatce opisują styl słowami („hand-inked comic book style…”) zamiast nazwy gry-inspiracji z prefiksu [[Style Lock]] (kanon), bo nazwa cudzej gry ciągnie model do kopiowania jej budynków. Czy zmieniamy też prefiks w Style Lock?
Dopisek z 13.11.2026: prefiks Style Lock zastąpiła instrukcja Glossy Ink (D-027), więc druga część pytania jest rozstrzygnięta. Otwarte zostają lista lokacji i język nazw. Pytanie miało u Pawła numer 7; przy scaleniu dostało numer 28, bo numery 7–27 były już zajęte.
Dopisek z 2026-11-14 (sesja główna): język — angielski z tłumaczeniami (propozycja D-045); lista lokacji nie padła. Budynki wymienione w rozmowie: karczma, sklep z bronią, sklep magiczny, Pety, Twierdza, hala portali do dungeonów (D-042), mistrz gier planszowych. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]].
Dopisek z 2026-11-14 (druga sesja): stajnia petów stoi w mieście, nie na działce (D-052); mistrz gier siedzi w karczmie (D-053); Training Center raczej w Twierdzy (D-050). Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-14 (trzecia sesja): zamiast wygenerowanej grafiki mapy — widok z lotu ptaka z kamery na miasteczko, piny tylko przy dostępnych lokacjach, klik teleportuje (propozycja D-064; pomysł Pawła, Karol: „jak w GTA V”). Lista lokacji nie padła; osiem biomów (D-061) też musi być z mapy osiągalne. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
Dopisek Pawła z 2026-11-14 (przy scaleniu): [[Mapa teleportacji]] ma 7 lokacji według promptu-wytycznej Game Directora: Karczma, Arena, Portal do lochów, Twierdza, Siedziba Gildii, Kuźnia, Zagroda petów (Targ wypadł, Shop zostaje w HUD). Czy lista jest dobra? Polskie czy angielskie nazwy na mapie? Prefiks stylu rozstrzygnęła D-027 (Glossy Ink); prompty mapy są od 2026-11-14 w tym formacie. Ramka mapy: instrukcja każe dać cienką drewnianą ramkę bez ciężkich kamiennych ram, a prompt-wytyczna miał „chunky stone-and-wood border”. W promptach jest cienka ramka — zostawić?
**Odpowiedź:**
- Karol Balucki (2026-11-14): Targ to to samo co skelp z bronią i armorem - łączymy te sklepy. / Twoja propozycja jest dobra. co do lokalizacji

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
Dopisek z 2026-11-20: przy publikacji BONK (D-113) lista twórców na koncie Karola miała tylko „Ja” — grupy nie ma albo Karol nie ma w niej prawa tworzenia. Prywatną wersję testową BONK opublikowano więc na konto Karola. Przed publicznym startem: przeniesienie własności do grupy (Creator Hub → Configure → Settings → Initiate ownership transfer); dźwięki BONK są na koncie Karola, więc po przeniesieniu trzeba dać grze dostęp do nich albo wgrać je w imieniu grupy.
**Odpowiedź:**
- Karol Balucki (2026-11-14): Paweł stworzy grupe

## 32. Pierwsze wydanie: ulepszanie przedmiotów, gildie i lista biomów (D-035)
- Ulepszanie przedmiotów: na premierę (Karol) czy później (Paweł).
- Gildie: na premierę czy później.
- Które biomy i ile na start.
Szczegóły: Lista „na premierę” i „później” jest w D-035. Sporne albo nie padło: (1) ulepszanie przedmiotów (kowal, zaklinanie) — Karol: może od razu, Paweł: później; (2) gildie — Paweł wcześniej chciał je odłożyć, na sesji wprost nie potwierdził; (3) które biomy i ile na start — padło tylko „las od początku, kryształowy wyżej” i „o biomach powiemy później”. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]], [[Roadmapa]].
Dopisek z 2026-11-14 (druga sesja): kowal znalazł się na liście budynków Twierdzy „do wersji początkowej” (propozycje D-049, D-051), choć D-035 odkłada go na po premierze; tiery przedmiotów — Paweł: „nie teraz”. Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-14 (trzecia sesja): (2) gildie — po premierze (obaj zgodni, propozycja D-067; budynek gildyjny z D-049 też); (3) biomy — osiem na start w kolejności las, bagno, dżungla, pustynia, góry z tundrą, lodowiec, wulkaniczny, kryształowy (D-061), obsydian pod znakiem zapytania. (1) ulepszanie na premierę nadal nie padło; zaklinacz miałby stać na pustyni. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
Dopisek z 2026-11-17 (przy przepisywaniu notatek o grze): kowal i ulepszanie przedmiotów — D-035 (podpis Karola) odkłada je po premierze, a D-049 i D-051 (oba podpisy) wpisują kowala na listę budynków Twierdzy. Karol odpowiedział tutaj „na premierę”; odpowiedzi Pawła nie ma.
Dopisek z 2026-11-17 (sesja główna 20:57): Karol: „dajemy Kowala” na premierę, logikę robi agent; Paweł: „no można dać” (propozycja D-102, zmienia D-035). Kto robi okno Kowala w Figmie — pytanie 57. Zob. [[Sesja główna 2026-11-17 — zapis ustaleń]].
**Odpowiedź:**
- Karol Balucki (2026-11-14): Ulepszanie przedmiotów normalnie na premiere. Gildie później, biomy już zostały odpoiwedziane

## 33. Krzywe Miasteczko: kolorystyka i czytelność budynków (D-041)
- Co dokładnie poprawić w kolorystyce.
- Jak oznaczać budynki, żeby było widać, co jest czym (Paweł nie rozpoznał sklepu z Petami ani wejścia do dungeonu).
- Czy wejście do dungeonu zastępują wrota z kłódką (D-042).
Szczegóły: Karol na sesji 14.11: Krzywe Miasteczko to styl oficjalny, ale „coś poprawiamy w kolorystyce” — co dokładnie (paleta, nasycenie, kontrast obrysu, kolory dachów)? Paweł nie rozpoznał w podglądzie 3D sklepu z Petami ani wejścia do dungeonu — jak oznaczać budynki (szyldy bez napisów, ikony nad wejściem, charakterystyczny kształt)? Czy wejście do dungeonu zastępują wrota z kłódką i hala portali (D-042)? Zob. [[Klocki — Blender i Roblox]], [[Sesja główna 2026-11-14 — zapis ustaleń]].
**Odpowiedź:**
- Karol Balucki (2026-11-14): Wydaje mi się że te lokacje są w maire logiczne. Dzięki opcji teleporu gracz może tepać się też między sklepami itd, a nie tylko pomiędzy lokalizajcami

## 34. Drzewko umiejętności postaci: kształt i zasady (D-039, D-047)
- Paweł zapytał w panelu 14.11, jak rozplanować skill tree postaci.
- Propozycja D-047: trzy gałęzie (Walka, Wyprawa, Fortuna) i pień, pięć pięter za poziom, pierwsza ranga węzła za punkt talentu, kolejne za Diamenty; jedno drzewko dla klas na premierę.
- Do wyboru: (a) tak, jak w D-047; (b) tylko Diamenty, bez punktów talentu (D-039 dosłownie); (c) osobne drzewko dla każdej klasy już na premierę.
Szczegóły: Pełny opis z przykładowymi węzłami, liczbami roboczymi, oknem i szkicem technicznym: [[Drzewko umiejętności postaci]]. Drzewko ma mnożyć statystyki i ekwipunek, nie je zastępować; piętra otwiera poziom postaci, więc Diamenty przyspieszają, ale nie przeskakują pięter (D-035). Liczby (poziomy pięter, koszty w Diamentach, 1 punkt talentu co poziom) są hipotezą do kalkulatora balansu i zależą od tempa zdobywania Diamentów w grze (pytanie 9, D-031). Osobno zostają drzewka petów (D-039, D-040 — temat Pawła w [[Sesje główne]]) i drzewko Twierdzy. Jeśli wybieracie (b) albo (c), odrzućcie D-047 i napiszcie wariant w komentarzu.
Dopisek z 2026-11-14 (druga sesja): Karol — osobne drzewko na klasę; Paweł — klasy Wojownik, Zwiadowca, Mag ze specjalizacjami w drzewku (D-054); węzły procentowe plus umiejętności aktywne z 0–3 slotami, jedno okno z sekcjami koło ekwipunku (D-055, odpowiada wariantowi (c)). Za co kupuje się węzły — nie padło. Temat niedokończony (koniec sesji). Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-14 (trzecia sesja): dokończone — węzły za Gemy (walutę premium), bez punktów talentu; poziom daje sklep, punkty statystyk i strefy (propozycja D-057); okno z trzema sekcjami gracz / pety / Twierdza, bez karczmy, i jedno ogólne drzewko petów zamiast drzewka każdego peta (D-056). Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
Rozstrzyga: D-047, D-055
**Odpowiedź:**
- Karol Balucki (2026-11-14): rozstrzygnięte decyzjami: D-047 odrzucona („Tak, ale płącimy jedynie dimaetnami za drzewko.”), D-055 zatwierdzona

## 35. Klasy postaci: które i czym się różnią (D-054)
- Paweł na drugiej sesji 14.11: Wojownik, Zwiadowca, Mag; specjalizacje (Berserker, Paladyn…) jako rozgałęzienia drzewka.
- Wcześniej w tej rozmowie Paweł wolał brak klas i podział po rodzaju broni; Karol zakłada klasy z osobnymi drzewkami.
- Do wyboru: (a) trzy klasy jak w D-054; (b) bez klas, liczy się rodzaj broni; (c) Rycerz i Kot-Mag z D-003 jako dwie klasy startowe.
Szczegóły: Pytanie dodane na prośbę Karola z rozmowy [13:25] („żebyśmy przedyskutowali też klasy”). Łączy się z [[Selektor bohatera]] (rasa + klasa, propozycja), D-003 ([[Rycerz]], [[Kot-Mag]]), D-033 (prosta animacja zamachu: miecz, różdżka — czym walczy Zwiadowca?), D-047 i D-055 (jedno drzewko czy na klasę). Do ustalenia też: czy klasa wyznacza broń, czy specjalizację da się zmienić i czy klasę wybiera się na starcie (Selektor bohatera) czy w drzewku. Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-14 (trzecia sesja): klas nie omawiano (Karol odhaczył temat agendy z notatką o biomach), ale przy statystykach padło: slot tarczy ma tylko Wojownik, limit uniku zależy od klasy (Zwiadowca najwyższy), umiejętności skalują się z Inteligencji (D-062, pytanie 40). Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
Rozstrzyga: D-054
**Odpowiedź:**
- Karol Balucki (2026-11-14): rozstrzygnięte decyzjami: D-054 zatwierdzona

## 36. Training Center: czy statystyki z mini-gier nie wypierają reszty gry (D-050)
- Paweł: statystyki grinduje się w mini-grach Training Center bez limitu, z trybem AFK bez mnożników; potwory dają Złoto i przedmioty.
- Karol: „mógłbym cały czas siedzieć na mini-grach” — „to musimy przegadać”.
- Do wyboru: (a) jak D-050 — bez limitu, AFK bez mnożnika; (b) limit dzienny albo tokeny (wcześniejszy pomysł Karola); (c) mini-gry dają tylko część statystyk, reszta z przedmiotów i Złota.
Szczegóły: Opis mini-gry (ciachanie rzucanych przedmiotów, +1 za trafienie, combo), ulepszanie centrum i tryb AFK są w D-050. Sześć statystyk Pawła odpowiada liczbowo liście w [[System RPG]] (Siła, Kondycja, Inteligencja, Zręczność, Szczęście, Pancerz) — czy każda ma własną mini-grę? Czy centrum jest od początku i stoi na działce Twierdzy (pytanie 9)? Przyrosty i ich stosunek do statystyk z przedmiotów to robota dla kalkulatora balansu (okno Balans agenta). Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-14 (trzecia sesja): o wypieraniu walki nie rozmawiano; padło za to: jeden budynek Training Center z wyborem mini-gry, dostępny od pierwszego poziomu, pięć czy sześć mini-gier (propozycja D-063, pytanie 39). Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
Rozstrzyga: D-050
**Odpowiedź:**
- Karol Balucki (2026-11-14): rozstrzygnięte decyzjami: D-050 zatwierdzona („Nie ma trybu AFK - na razie.”)

## 37. Mistrz gier planszowych: liczby i plansze (D-053)
- Nagrody na polach, koszt kolejnych rzutów za Złoto, jak często darmowy rzut.
- Osobne plansze po 100 pól (Karol) czy pętla z ulepszanymi polami (Paweł).
- Czy bilety za Robuxy z D-037 zostają, skoro rzuty są za Złoto.
Szczegóły: Na drugiej sesji 14.11 obaj opisali planszę bez stawek: kostka sześcienna, stała nagroda na każdym polu, im dalej tym lepsza, darmowy rzut na czas plus płatne rzuty za Złoto o rosnącej cenie, kolejne plansze lepsze od poprzednich, możliwość ominięcia planszy płacąc (D-053). Uwaga: D-037 (zatwierdzona przez Karola rano) opisuje też stawianie monet i utratę połowy — D-053 tego nie ma; jeśli zostanie zatwierdzona, ten punkt D-037 przestaje obowiązywać i trzeba to zapisać w rejestrze. Liczby do kalkulatora balansu. Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]], [[Retencja i monetyzacja — co wolno i co działa]].
**Odpowiedź:**
- Karol Balucki (2026-11-14): W game passie będzie opcja, która dla danego VIPa pozwoli mu rzucać 2 kościami naraz u tego mistrza gier. Rzucamy TYLKO ZA ZŁOT, rezygnujemy z biletów

## 38. Pety: od początku czy z drzewka; jawne szanse jajek (D-052)
- Paweł: podstawowe jajka w mieście od początku; Karol pamiętał, że pety odblokowuje drzewko umiejętności.
- Jajka za Złoto, a Złoto da się kupić przez Diamenty (D-038) — lista petów i szanse muszą być widoczne przed zakupem.
- Do wyboru: (a) jak D-052, pety od początku; (b) pety od poziomu albo z drzewka, stajnia w mieście zamknięta do tego czasu.
Szczegóły: Stajnia w mieście, zestawy jajek na strefę (pierwsze miasto np. trzy, najdroższe ok. 10 tys. Złota, ok. 1% na legendarnego), rzadkie jajka z potworów i karmienie petów przez rzadkość — D-052. Rozmowa 12.11 mówiła „pety odblokowywane poziomem” i o wylęganiu na czas — na sesji wylęganie nie padło. Drzewka petów i ich waluta: D-039, D-040 (temat Pawła w [[Sesje główne]]). Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]], [[Pety]].
Dopisek z 2026-11-14 (trzecia sesja): jajka w inkubatorach w każdym biomie, wyklucie od razu, bez jajek z potworów — zmiana wobec D-052, zapisana jako propozycja D-060 i pytanie 42. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
Dopisek z 2026-11-17 (przy przepisywaniu notatki [[Pety]]): wiersz „Rozstrzyga: D-052” jest na wyrost — D-052 zapisuje tylko stanowiska (Paweł: podstawowe jajka od początku; Karol nie potwierdził wprost). Inkubator przy wejściu do pierwszego biomu (D-076) sugeruje pety od początku, ale nikt tego nie zapisał.
Dopisek z 2026-11-17 (sesja główna 20:56): pety omówiono tylko od strony premii: różne premie i żywioły, zwykłe pety z małą pasywką (propozycja D-101). Pety od początku gry, cena jajek i szansa na legendarnego nie padły. Zob. [[Sesja główna 2026-11-17 — zapis ustaleń]].
Rozstrzyga: D-052
**Odpowiedź:**
- Karol Balucki (2026-11-14): rozstrzygnięte decyzjami: D-052 zatwierdzona

## 39. Pancerz: trenować w Training Center czy tylko z przedmiotów?
- Karol: szósta mini-gra na Pancerz — trenujemy go jak Siłę, choć broń też daje atak.
- Paweł: pięć mini-gier; Pancerz daje tylko ekwipunek, pełny zestaw i tak dobija limit.
- Do wyboru: (a) sześć mini-gier; (b) pięć, Pancerz z przedmiotów; (c) sześć, ale trening Pancerza z niskim limitem.
Szczegóły: Na trzeciej sesji 14.11 obaj zgodzili się, że Pancerz jest wartością punktową odejmowaną od zwykłego ciosu, nie procentem (propozycja D-062), i że Training Center to jeden budynek z wyborem mini-gry (D-063). Nie zgodzili się, czy Pancerz ma własną mini-grę. Paweł rzucił też rozdzielenie Pancerza i Obrony, a Karol pełniejszy zestaw (Pancerz, Obrona, Unik, Przebicie magiczne, Odporność magiczna) i sam zwątpił, bo prowadzi to do kontrowania klas — jeśli chcecie więcej statystyk obronnych, napiszcie które. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]], [[System RPG]].
**Odpowiedź:**
- Karol Balucki (2026-11-16): nieaktualne

## 40. Wojownik z tarczą i unikiem: jak ograniczyć Zręczność?
- Paweł: blok z tarczy plus unik ze Zręczności u Wojownika to za dużo.
- Karol: naturalne osłabienie — mało węzłów Zręczności w drzewku Wojownika albo o połowę mniejszy przyrost.
- Paweł: ograniczać drzewka nie ma sensu, skoro Zręczność trenuje się za monety w Training Center.
- Do wyboru: (a) limit uniku na klasę, Wojownik najniższy (jak w D-062); (b) mniejszy przyrost Zręczności z treningu u Wojownika; (c) blok i unik nie sumują się — jedna szansa na uniknięcie ciosu.
Szczegóły: Z trzeciej sesji 14.11 (D-062): Zręczność daje szansę na unik z limitem zależnym od klasy (Zwiadowca od 25% do maks. 50%, inne klasy od 0 i niżej); blok to cecha tarczy jako przedmiotu ze stałą szansą, slot tarczy ma tylko Wojownik; Inteligencja to moc umiejętności i odporność na magię. Paweł zauważył też ryzyko buildu „Wojownik z samą Inteligencją bijący tylko umiejętnościami”. Karol prosił o opinię agenta — dojdzie jako komentarz pod tym pytaniem z liczbami z kalkulatora balansu ([[Zadania]]). Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
**Odpowiedź:**
- Karol Balucki (2026-11-14): To zostawiam to Cloudowi do rozwiązania tego problemu z balansem i optymalizującego
- Claude Code (2026-11-17): Opinia z liczbami (silnik walki v3, 800 walk na parę): Wojownik z tarczą i unikiem nie jest za mocny. Limit uniku klasy, czyli (a), już działa — Wojownik ma najwyżej 24,2% uniku. Wojownik, który cały trening wkłada w Zręczność, wygrywa z potworami 84% zamiast 96% i tylko 28–32% pojedynków. Mniejszy przyrost Zręczności (b) niczego nie naprawia, a niesumowanie bloku z unikiem (c) wyłącza blok Maga i Zwiadowcy, czyli w praktyce cofa D-073, i zwiększa różnicę klas z ok. 4 do ok. 6 pp. Rekomendacja: zostać przy (a); decyzja należy do Was. Tabele: `tools/walka/BALANS_1711.md`, część 5.

## 41. Ewolucja petów: wszystkie czy tylko lepsze; liczby (D-058)
- Karol: ewolucje dla wszystkich petów (piesek → Cerber), legendarne z legendarnymi ewolucjami.
- Paweł: raczej tylko lepsze pety, nie każdy pospolity.
- Liczby do ustalenia: maks. poziom peta (robocze 30), ile shardów peta i tokenów krainy na ewolucję, szansa na Shard Ewolucji ze strażnika biomu.
Szczegóły: Model z trzeciej sesji 14.11: jeden stały skill na typ peta; poziom z karmienia (D-052) otwiera ewolucje; ewolucja kosztuje shardy peta (skrapowanie kopii, 1:1), jeden Shard Ewolucji (rzadki drop ze strażnika biomu) i tokeny krainy (zabijanie potworów w krainie, mniej z walk petów) — propozycja D-058. Pety nie walczą obok gracza: dają pasywne premie i mają własne strefy walk, ok. 10 petów na biom (D-059). Liczby do kalkulatora balansu razem z tempem zdobywania tokenów. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]], [[Pety]].
Dopisek z 2026-11-17 (kalkulator balansu, propozycja liczb): przy dzisiejszych 10% na Shard Ewolucji wychodzi średnio 14 prób strażnika (ok. 21 minut), a pechowe 10% graczy potrzebuje ponad 31; ochrona przed pechem po 20 wygranych obniża średnią do 12. Tokeny krainy: ok. 130 na godzinę, propozycja 60 / 180 / 450 na trzy ewolucje. Wąskim gardłem są kopie z jajek: komplet ewolucji legendarnego peta (2% w jajku) to ok. 550 jajek — propozycja: liczba kopii zależna od rzadkości. Tabele: `tools/walka/BALANS_1711.md`, część 3.
**Odpowiedź:**
- Karol Balucki (2026-11-14): Wszystkie pety jednak mogą ewolłować, tylko niektóre maja legendarne ewolucje

## 42. Jajka bez dropu z potworów i wyklucie od razu — zmiana D-052
- D-052 (oba podpisy) mówi: bardzo rzadko jajka wypadają też z potworów.
- Trzecia sesja: jajka tylko w inkubatorach w każdym biomie, za Złoto, wyklucie od razu z animacją 3–10 s (Paweł); Karol wolał rzadki drop i wyklucie na czas, ale „zdał się” na Pawła.
- Do decyzji: przyjąć D-060 teraz i sprawdzić w playteście przed premierą, czy dodać drop z potworów.
Szczegóły: Propozycja D-060 zastępuje w D-052 tylko punkt o jajkach z potworów; zestawy jajek na strefę, ceny, karmienie i jawne szanse zostają. „Stajnia w mieście” z D-052 staje się inkubatorami pierwszego biomu. Drzewko petów skraca animację wyklucia i pozwala otwierać kilka jajek naraz (D-056). Wylęgarnia na czas z rozmowy 12.11 jest nieaktualna. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]], [[Pety]].
Rozstrzyga: D-060
**Odpowiedź:**
- Karol Balucki (2026-11-14): rozstrzygnięte decyzjami: D-060 zatwierdzona („Tak. Dodatkowe w bundlach też dajemy oferty na jajka”)

## 43. Jajka i skrzynki za Robuxy a D-031
- D-031 (zatwierdzona przez Karola): za walutę premium nigdy jajek ani kół; losowania tylko za Złoto i tokeny z gry.
- Trzecia sesja: paczki jajek za Robuxy z jawnymi szansami (np. 10 jajek, 10% na najlepszego peta), możliwa skrzynka; obaj uznali to za dopuszczalne.
- Do wyboru: (a) zatwierdzić D-066 — nowa decyzja zastępuje ten punkt D-031; (b) odrzucić — jajka tylko za Złoto, za Robuxy sama waluta.
Szczegóły: Zasady Roblox z pytania 30: losowe nagrody kupowane za Robuxy albo za walutę kupioną za Robuxy są dozwolone, jeśli lista nagród i dokładne szanse są widoczne przed zakupem, gra sprawdza uprawnienia gracza (`PolicyService`) i pokazuje zmienione szanse przy ulepszeniach szczęścia; stawianie waluty na wynik losowy jest zakazane. Ponieważ Złoto da się kupić przez Diamenty (D-038), już dzisiejsze jajka za Złoto podpadają pod te zasady (D-052). D-066 zbiera też resztę sklepu z sesji: waluta, lepsze przedmioty, game passy (podwójna waluta, podwójna moc treningu), darmowy pet. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]], [[Retencja i monetyzacja — co wolno i co działa]].
Rozstrzyga: D-066
**Odpowiedź:**
- Karol Balucki (2026-11-15): rozstrzygnięte decyzjami: D-066 odrzucona („Za Robuxy waluta oraz bundle oraz Pass startowe”)

## 44. Rybki — trzecia waluta w HUD
14.11 Game Director kazał dodać do panelu gracza trzeci licznik z ikoną złotej rybki (pod Złotem i Diamentami; atrybut gracza `Fish`). Kanon zna dwie waluty (pytanie 6). Do czego służą Rybki: waluta z łowienia, karma dla petów czy coś innego? Jak się je zdobywa i na co wydaje?
Dopisek Claude Code z 2026-11-14 (przy scaleniu): na sesjach 14.11 trzecia waluta dostała rolę z D-040 — zdobywana graniem, wydawana na game passy. Nazwę proponuje D-046 („Chrupki”), a D-031 wymieniała „Złote Rybki” jako wariant. Rybki z HUD mogą być tą walutą — do potwierdzenia. Pytanie miało u Pawła numer 29; przy scaleniu dostało numer 44, bo numery 29–43 były już zajęte.
**Odpowiedź:**
- Karol Balucki (2026-11-15): Waluta premium skipy/bundle/passy bez wydawania robux

## 45. Drzewko: gałąź Timer w Twierdzy i premia do Diamentów
- Paweł (15.11) chce w Twierdzy gałęzi **Timer** (krótsza budowa) — D-056 jej nie wymienia.
- W gałęzi Player → **Income** jest też % do zdobywanych **Diamentów**, a Diamentami (Gemami) kupuje się węzły (D-057).
- Opcje: przyjąć obie · Timer tak, Diamenty bez premii · obie odłożyć.

Szczegóły: premia do Diamentów przyspiesza kupowanie kolejnych węzłów (pętla) i może zmienić balans z D-035. Układ okna: [[Okno drzewka umiejętności]].
**Odpowiedź:**
- Karol Balucki (2026-11-16): nieaktualne

## 46. Blok bez tarczy: ile zatrzymuje i kto go ma?
- Propozycja D-073: blok i unik ma każda klasa, a tarcza daje Wojownikowi większą szansę na blok.
- Paweł wolał blok tylko z tarczą i Maga bez uniku. Rzucił też: tarcza zatrzymuje cały cios, Zwiadowca np. połowę.
- Do wyboru: (a) blok zawsze zatrzymuje cały cios, klasy różnią się tylko szansą; (b) blok z tarczą cały, bez tarczy część (np. 50%); (c) liczby dobiera agent w balansie.

Szczegóły: Sesja główna 16.11, 20:05–20:07 ([[Sesja główna 2026-11-16 — zapis ustaleń]], temat 1). Zatwierdzona D-062 mówi, że blok to cecha tarczy, a slot tarczy ma tylko Wojownik. Karol w odpowiedzi na pytanie 40 zostawił balans Wojownika agentowi.
**Odpowiedź:**
- Karol Balucki (2026-11-16): a tarcza daje Wojownikowi większą szansę na blok,a blok po porstu zmniejsza otrzymany DMG

## 47. Półbóg za Robuxy: z lepszymi statystykami czy bez przewagi?
- Karol: rasa premium Półbóg za Robuxy, z lepszymi statystykami.
- Paweł: „pay to win”.
- Do wyboru: (a) za Robuxy, z lepszymi statystykami (D-080); (b) za Robuxy, ale tylko wygląd albo inna, nie mocniejsza cecha; (c) do zdobycia w grze, np. za Rybki.

Szczegóły: Sesja główna 16.11, 20:18–20:19 ([[Sesja główna 2026-11-16 — zapis ustaleń]], temat 6). Na tej samej sesji Karol odrzucił czwarty slot umiejętności za Robuxy jako „za bardzo pay-to-win” (D-088). Przy odrzuceniu D-080 wpiszcie w uzasadnieniu wariant (b) albo (c). Rasy: D-079.
Rozstrzyga: D-080
**Odpowiedź:**
- Karol Balucki (2026-11-16): rozstrzygnięte decyzjami: D-080 zatwierdzona („Tak. Moduluje Pawłek, a jak skończą mu się tokeny to ja.”)

## 48. Wskrzeszenie w walce: legendarna umiejętność czy wcale?
- Paweł: raz na walkę powrót ze 100% HP albo szansa na powrót z malejącym HP (50%, potem 25%…).
- Karol: za mocne, najwyżej jako umiejętność legendarna.
- Do wyboru: (a) nie ma wskrzeszenia; (b) legendarne, raz na walkę, z niskim HP (np. 25%); (c) wersja Pawła z malejącą szansą.

Szczegóły: Sesja główna 16.11, 20:31–20:32 ([[Sesja główna 2026-11-16 — zapis ustaleń]], temat 10). Zatwierdzona D-068 mówi, że walka trwa, aż życie jednej strony spadnie do zera. W [[Zadania]] czeka już węzeł drzewka „Jeszcze stoję” (ostatni dech) jako sprzeczny z D-068, więc oba rozstrzygnąć razem. Sloty umiejętności: D-088.
Rozstrzyga: D-094
**Odpowiedź:**
- Claude Code (2026-11-16, okno Balans w panelu, na polecenie Karola): Karol przyjął wariant (b) („Ok przyjmuję to”) — legendarna umiejętność w slocie, raz na walkę, powrót z 25% HP, zastępuje węzeł „Jeszcze stoję”. Zapisane jako propozycja D-094: czeka na podpis Karola w panelu i potwierdzenie Pawła.

## 49. Czyj agent robi zadania bez przydziału z sesji 16.11?
- Karol: gdy z rozmowy nie wynika, czyj Claude robi zadanie, agent ma zapytać (D-093).
- Bez przydziału: balans (mana, statusy, Pancerz, blok); modele ras z Półbogiem; przebudowa Krzywego Miasteczka z wnętrzami sklepów; okno zagrody petów i tablica ogłoszeń; pomijanie walk.
- Podział z D-093 podpowiada: modele i miasto (3D) — Karol, okna 2D — Paweł, kod walki — agent Karola, który zrobił silnik v2.
- Odpowiedz tutaj albo ustaw agenta przy zadaniu (Pytania → Plan → Zadania).

Szczegóły: Modele ras: Karol najpierw powiedział, że robi je Paweł w Blenderze (20:24), a minutę później duże modele i sceny przeszły na Karola. Zadania stoją w [[Zadania]] bez pola `agent:`. Źródło: [[Sesja główna 2026-11-16 — zapis ustaleń]], temat 5.
Dopisek z 2026-11-16 (Claude Code u Karola, 21:00): Karol polecił w rozmowie zacząć pracę po sesji. Agent Karola robi od 21:00 balans i zmiany silnika walki (praca „silnik-mana-balans”) oraz plan lasu jako pasa (praca „las-pas-plan”). Modele ras, miasto, okno zagrody petów z tablicą i pomijanie walk czekają na odpowiedź.
Dopisek z 2026-11-16 (Claude Code u Karola, 21:18, z rozmowy z Karolem): modele ras robi Paweł, a agent Karola po jego wypchnięciu poprawia modele, halę wyboru i faktury. Przejście teleportu przez chmury (D-075) robi agent Karola. Bez przydziału zostają: miasto, okno zagrody petów z tablicą i pomijanie walk.
**Odpowiedź:**
- Karol Balucki (2026-11-16): Te wszystkie rzeczy na mnie "Karol"

## 50. Trening: malejący zysk zamiast stałego +1 za trafienie?
- Bez zmian (D-050: +1 za trafienie, bez limitu) trening po 10 godzinach gry daje ok. 130% puli statystyk z poziomów, a siedzenie w jednej mini-grze (Kondycja) wystarcza.
- Propozycja: pasek treningu. Każde trafienie go napełnia, seria przyspiesza (×1 / ×1,25 / ×1,5 / ×2), a kolejny punkt tej samej statystyki wymaga coraz więcej trafień.
- Skutek: trening sześciu statystyk po kolei daje ok. dwa razy więcej niż jedna mini-gra; grindu dalej nic nie blokuje.
- Do wyboru: (a) przyjąć wzór; (b) zostać przy +1 za trafienie; (c) inny pomysł.

Szczegóły: Prośba Karola z D-074 („zbalansować przyrosty tak, żeby nie opłacało się nadużywać jednej mini-gry”). Wzór zmienia zapis „+1 za trafienie” z zatwierdzonej D-050, więc potrzebuje decyzji. Liczby i założenia: `tools/walka/BALANS_1711.md`, część 6; ten sam wzór jest roboczo w prototypie mini-gier (`swiat/trening_proba/`). Przy okazji: Kondycja i Inteligencja nie mają węzła w gałęzi Training Center drzewka Twierdzy.
Dopisek z 2026-11-17 (sesja główna 20:52): trening zostaje jednym z dwóch źródeł statystyk obok poziomu (propozycja D-097; Paweł: trening „na jak największy grind”). Tempo treningu Karol zostawił agentowi. Wzoru z paskiem treningu nie omawiano. Zob. [[Sesja główna 2026-11-17 — zapis ustaleń]].
**Odpowiedź:**
- Karol Balucki (2026-11-17): Odpowiedź (a), ale teraz myślimy również z Pawełem coś na temat AFK grindu w tego typu grach - co myślisz?

## 51. Gemy: skąd ma je brać gracz bez płacenia?
- Dziś łup z potworów daje ok. 7 Gemów w 10 godzin gry, a drzewka kosztują razem 20 650.
- Sloty umiejętności są w drzewku za 25 / 70 / 125 Gemów, więc gracz bez płacenia nie ma w 10 godzin żadnego slotu.
- Do wyboru: (a) Gemy za kamienie milowe, np. +10 za poziom i +100 za pierwszego strażnika biomu (ok. 135 na godzinę); (b) sloty umiejętności za poziom, nie za Gemy; (c) jedno i drugie; (d) zostawić.

Szczegóły: Liczby z kalkulatora (`tools/walka/BALANS_1711.md`, część 4), ceny węzłów z `src/shared/SkillTreeData.luau`. Dotyczy D-057 (węzły za Gemy) oraz D-055 i D-088 (sloty umiejętności). Cel roboczy: żeby gracz bez płacenia kupił w 10 godzin ćwierć drzewka gracza, potrzeba ok. 200 Gemów na godzinę; kamienie milowe z kopalnią diamentów od 25. poziomu dają ok. 200.
**Odpowiedź:**
- Claude Code (2026-11-17, z sesji głównej 20:53): Karol i Paweł: Gemy gracz dostaje za walki i za poziom (Karol), z kopalni w Twierdzy (Paweł) i za Rebirth od 100. poziomu (pomysł Pawła, Karol: „podoba mi się”) — propozycje D-099 i D-100; ile, liczy agent, a sloty umiejętności za poziom (wariant b) nie padły. Zapis agenta z rozmowy.

## 52. Co otwiera następny biom: strażnik, poziom czy oba?
- D-057 i D-061 (oba podpisy) oraz D-032 (podpis Karola): strefy i biomy otwiera poziom postaci.
- D-076 (oba podpisy, 16.11): następny biom otwiera pokonanie strażnika biomu.
- Do wyboru: (a) tylko strażnik; (b) strażnik i próg poziomu razem; (c) tylko poziom.

Szczegóły: Las-pas w Studio i plan Bagna przyjmują roboczo wariant (a) — brama otwiera się po Strażniku. Sprawa dotyczy też notatek [[System RPG]] (poziom i dostęp do stref) i [[Karczma (Questy)]] (poziomy trudności zadań liczone w biomie).
**Odpowiedź:**
- Karol Balucki (2026-11-17): Zabicie strażnioka - bossa danego regionu

## 53. Stan gracza: czy serwer Karola pisze poziom, złoto i statystyki?
- Przejście gry 17.11: łup z walk nie trafiał do gracza, klasa ze startu nie była klasą w walce, poziom i trening nic nie zmieniały.
- Zbudowane na próbę i wdrożone w Studio (`Workspace/StanGracza`): wygrana daje Złoto, doświadczenie i Gemy, poziom rośnie, walczysz swoją klasą na swoim poziomie, trening wzmacnia bohatera. Kod Pawła jest bez zmian; usunięcie kontenera przywraca stan sprzed zmiany.
- Skutek dla okien Pawła: atrybuty Level, XP, XPMax, Gold, Gems i sześć statystyk pisze teraz ten pakiet — startowe statystyki to 30 punktów według klasy zamiast testowych 130, a pasek doświadczenia ma zmienną długość.
- Do wyboru: (a) zostaje jako wspólny moduł stanu gracza; (b) Paweł przejmuje go i przenosi do `src/`; (c) wyłączamy do czasu decyzji.

Szczegóły: Pakiet `swiat/stan_gracza/` (status: propozycja), raport w panelu „Gra się spina: łup, awans, klasa i poziom w walce”. Przyjęte roboczo, do zmiany: krzywa doświadczenia 11,71 × poziom^1,6 (z kalkulatora tempa); +10 punktów statystyk na poziom rozdzielanych samoczynnie według rozkładu klasy z `ClassData` (pytanie 55); sloty umiejętności 1/2/3 od poziomów 1/5/10, inaczej niż w D-055 i D-088 (pytanie 51); Gemy z łupu dopisują się do testowych 1000; tablica próby walki nie daje nagród; bez zapisu między sesjami. Symulacja lasu na tych liczbach: przejście w ok. 27 minut, ok. 43 walki, ok. 8 przegranych, Strażnik pada zwykle na 11. poziomie. Zadanie „Moduł statystyk gracza” nie miało przydziału (pytanie 49). Do zgłoszenia Pawłowi: darmowy „+” w oknie ekwipunku wzmacnia teraz bohatera bez limitu, wybór klasy da się zmienić w każdej chwili (D-081 mówi o wyborze przy pierwszym wejściu), premie z drzewka dalej nie działają w walce, tokenów krain i shardów HUD nie pokazuje.
Dopisek z 2026-11-17 (sesja główna 20:54): o module stanu gracza nie rozmawiano, a z tego tematu agendy omówiono tylko przegraną (pytanie 54). Ustalenia z sesji zmieniają za to roboczy pakiet: za poziom 5 punktów do rozdania przez gracza zamiast +10 rozdzielanych samoczynnie, bez statystyk za Złoto (propozycja D-097), a po przegranej trochę mniej Złota (D-098). Zob. [[Sesja główna 2026-11-17 — zapis ustaleń]].
Dopisek z 2026-11-17 (czat Karola, ok. 21:20, w trakcie sesji głównej): na pytanie, czy spięcie stanu gracza zostaje jako wspólny moduł, Karol odpisał „Paweł potwierdza te zmiany”. Na sesji samo pytanie 53 nie padło ([[Sesja główna 2026-11-17 — zapis ustaleń]], temat 3), więc odpowiedź Pawła w panelu dalej się przyda.
**Odpowiedź:**
- Karol Balucki (2026-11-17): a

## 54. Co gracz traci po przegranej walce?
- Decyzji nie ma; D-076 mówi tylko, że ma się dać przegrać.
- Przyjęte roboczo: gracz nic nie traci i dostaje 20% doświadczenia. Przegrana ze Strażnikiem daje przez to więcej doświadczenia (ok. 90) niż wygrana ze slime'em (ok. 11).
- Do wyboru: (a) nic i 20% doświadczenia; (b) nic i bez doświadczenia; (c) kara w Złocie; (d) mniejszy procent doświadczenia.

Szczegóły: 20% liczy silnik walki (`src/server/Walka/Przeciwnicy.luau`); od 17.11 przyznaje je pakiet `swiat/stan_gracza/`. Rewanż jest dozwolony od razu. Zob. pytanie 53.
Dopisek z 2026-11-17 (po sesji głównej, propozycja D-098): agent policzył sześć wariantów kary i przygotował w pakiecie stanu gracza jeden — przegrany traci 5% posiadanego Złota, ale najwyżej tyle, ile daje wygrana ze zwykłym potworem tego poziomu; Gemów nie traci, dostaje 20% doświadczenia, bez kary czasowej. W lesie to ok. 6 Złota za przegraną (najwyżej 14) i ok. 46 Złota w całym lesie przy ośmiu przegranych; pierwsze jajko się nie przesuwa, a każdą przegraną odrabia jedna walka. To jedna liczba do zmiany (z wyłącznikiem); w Studio jeszcze niewdrożone.
**Odpowiedź:**
- Claude Code (2026-11-17, z sesji głównej 20:55): Karol i Paweł: przegrany traci trochę Złota (Gemów nie), nie dostaje nagrody, ale dostaje doświadczenie, a kary czasowej nie ma (Paweł: gracz musi móc grać; Karol: „masz rację”) — wariant (c), propozycja D-098; ile Złota (pewnie procent, Karol rzucił 5%) i ile doświadczenia, policzy agent. Zapis agenta z rozmowy.

## 55. Punkty statystyk: same z poziomu, do rozdania czy za Złoto?
- D-050 mówi o statystykach za Złoto, coraz drożej; D-057 o stałym przyroście co poziom i punktach do rozdania. Brakuje reguły, jak to się łączy.
- Przyjęte roboczo: +10 punktów na poziom, rozdzielanych samoczynnie według klasy. Przycisk „+” w oknie ekwipunku dodaje punkt za darmo i bez limitu, a od 17.11 te punkty wzmacniają bohatera w walce.
- Do wyboru: (a) część punktów sama, część do rozdania przez gracza; (b) wszystko samo, a „+” kosztuje Złoto; (c) wszystko do rozdania. Do tego: ile kosztuje „+”.

Szczegóły: Zob. pytania 17, 36 i 50 (trening jako trzecie źródło statystyk) oraz 53. Dopóki „+” jest darmowy, liczby balansu z walk w Studio nie są miarodajne, gdy ktoś go używa.
**Odpowiedź:**
- Claude Code (2026-11-17, z sesji głównej 20:52): Karol i Paweł: statystyki tylko z poziomu i z treningu, a Złoto wyłącznie na przedmioty; o 21:02 ustalili 5 punktów za poziom do rozdania przez gracza (wariant c; Karol: „ja dałbym 5”, Paweł: „dobra, możemy dać 5 i zobaczymy”) — propozycja D-097. Zapis agenta z rozmowy.

## 56. Rozkład statystyk klas: profil Pawła czy wzorcowy Karola?
- Paweł 17.11 opisał profile klas na ekranie wyboru: Wojownik STR, CON i ARMOR; Zwiadowca DEX i dużo LUCK (mniej CON i STR niż Wojownik); Mag dużo INT i LUCK, najmniej CON, STR i ARMOR.
- Te same liczby w `src/shared/ClassData.luau` rozdzielają startowe punkty w pakiecie Karola `swiat/stan_gracza`, więc zmieniają balans, nie tylko wygląd karty.
- Dziś w grze profil Pawła (sumy 100): Wojownik 25/27/6/9/9/24, Zwiadowca 15/19/9/26/21/10, Mag 9/14/32/13/25/7 (STR/CON/INT/DEX/LUCK/ARMOR). StanGracza ostrzega „inne niż wzorcowe”.
- Do wyboru: (a) profil Pawła wszędzie; (b) wzorcowy Karola w walce, profil Pawła tylko na karcie; (c) wspólnie ustalić nowe liczby.

Szczegóły: Wcześniejsze liczby (wzorcowe, z [[Walka v2 — silnik, klasy i umiejętności]]): Wojownik 26/30/12/8/10/14, Zwiadowca 27/27/10/14/13/9, Mag 24/22/24/10/10/10. Powiązane: pytanie 53. Zmienił Claude Code u Pawła 17.11 na jego polecenie (karta wyboru klasy).
Dopisek z 2026-11-17 (symulacja lasu, 200 graczy na klasę i profil; las po skróceniu D-096): z profilem Pawła wszystkie klasy są słabsze niż z wzorcowym — Wojownik wygrywa ze Strażnikiem Gaju w 20% walk zamiast w 37% i przechodzi las w 32,5 minuty zamiast 27,4; Zwiadowca na trollu 30% zamiast 43%; Mag w pierwszej zagrodzie 54% zamiast 68%. Przegranych w lesie jest 11–13 zamiast 8, a rozrzut między klasami rośnie (na trollu 13 punktów procentowych zamiast 4), co dotyka D-069. Do decyzji gra czyta profil Pawła, czyli to, co gracz widzi na karcie klasy. Jeśli zostaje wariant (a), balans potworów trzeba przeliczyć pod ten profil.
Dopisek z 2026-11-18 (po odpowiedzi Karola „b”): wariant (b) jest w grze od 18.11 ok. 00:46 jako ustawienie z wyłącznikiem w pakiecie stanu gracza — w walce rozkład wzorcowy, karta wyboru klasy i `src/shared/ClassData.luau` bez zmian. Symulacja lasu po D-096 (wzorcowy / profil z karty): Wojownik ze Strażnikiem Gaju za pierwszym razem 33–39% / 24–26%, las 27,5 / 32–33 min; Zwiadowca 34–39% / 33–35%, 28 / 30–31 min; Mag 36–37% / 24–29%, 25 / 29 min; przegranych 7–9 zamiast 10–13. To robocze ustalenie z jednym podpisem — czeka na potwierdzenie Pawła (D-043); powrót do profilu z karty to jedna wartość (`ROZKLADY_KLAS` albo atrybut kontenera `RozkladyKlas`).
**Odpowiedź:**
- Karol Balucki (2026-11-17): b

## 57. Kto robi okno Kowala w Figmie?
- Karol na sesji 17.11 poprosił Pawła o okno Kowala w Figmie (2D to obszar Pawła, D-093).
- Paweł: „można dać”, ale bez modelu, z którego korzysta Karol, nie zrobi nic fajnego.
- Karol: „te rzeczy mogą być też na mnie”.
- Do wyboru: (a) Paweł; (b) agent Karola; (c) agent Karola robi grafiki, Paweł okno i skrypty.

Szczegóły: Sesja główna 17.11, 20:57 ([[Sesja główna 2026-11-17 — zapis ustaleń]], temat 5). Kowal na premierę: propozycja D-102. Logikę Kowala robi agent Karola. Odpowiedz tutaj albo ustaw agenta przy zadaniu (Pytania → Plan → Zadania).
**Odpowiedź:**
- Karol Balucki (2026-11-17): Paweł

## 58. Czy obok 5 punktów do rozdania zostaje stały przyrost?
- D-097 daje 5 punktów za poziom do rozdania przez gracza; czy zostaje też stały przyrost co poziom (D-057), na sesji nie padło.
- Dziś w grze roboczo: 5 punktów rozdaje się samo według klasy i 5 rozdaje gracz.
- Przy samych 5 do rozdania las trwa w symulacji ok. 61 minut zamiast ok. 31, a Strażnik Gaju pada za pierwszym razem w 2% prób zamiast w 29%.
- Do wyboru: (a) zostaje 5 samo + 5 do rozdania; (b) tylko 5 do rozdania i agent osłabia potwory; (c) inne liczby.

Szczegóły: Jedna liczba w `swiat/stan_gracza/dane.py` (`PUNKTY_SAMO_NA_POZIOM`, 0 = sam wariant z D-097); tabela wariantów w `swiat/stan_gracza/README.md`. Potwory były strojone pod 10 punktów na poziom. Zob. D-097, D-057, pytanie 55.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 59. Szczęście początkującego: premia do pierwszej wygranej?
- Po skróceniu pasa (D-096) nowy gracz przegrywał pierwszą walkę w ok. co czwartej próbie (73–79% wygranych zależnie od klasy).
- Roboczo w grze od 18.11: do pierwszej wygranej statystyki gracza w walce są mnożone ×1,75, bez żadnego napisu; potem premia znika. W symulacji daje to 96–99,6% wygranych z Leśnym Slime'em 1. poziomu.
- Do wyboru: (a) zostaje bez napisu; (b) zostaje, ale gracz widzi krótki napis; (c) wyłączyć i zamiast tego osłabić slime'y 1. poziomu.

Szczegóły: Jedna liczba (`SZCZESCIE_POCZATKUJACEGO` w `swiat/stan_gracza/dane.py`, 0 = wyłączone) albo atrybut kontenera `SzczesciePoczatkujacego`. Jeśli gracz trafi pierwszy na slime'a 2. poziomu, wygrywa w 73–88% prób. Premia nie dotyczy kolejnych walk, więc nie zmienia tempa lasu. Zob. pytanie 56 (profil klas).
Dopisek z 2026-11-18 (po regresji końcowej): przy ×1,75 pierwsza walka została w próbach dymnych przegrana 2 razy na 7 — gracz podchodzi do najbliższego slime'a, a ten bywa na 2. albo 3. poziomie (ze slime'em 3. poziomu było 58–72% wygranych). Mnożnik podniesiony do ×2,75: slime 1. i 2. poziomu 99–100%, 3. poziomu 95–96%. Nadużyć się tego praktycznie nie da: gracz bez wygranej pokona trolla w 2–4% prób, Strażnika Gaju w 0%. Dalej jedna liczba z wyłącznikiem; opcje (a)–(c) bez zmian.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 60. Zapis postępu gracza: kiedy włączamy?
- Kod zapisu jest gotowy w pakiecie stanu gracza i domyślnie wyłączony; sprawdzony tylko bez Studio, na atrapie usługi danych.
- Zapisuje: poziom, doświadczenie, Złoto, Gemy, klasę, trening, punkty, pety, wydatki, pokonanych strażników, obejrzane przeloty i strój.
- Nie zapisuje drzewka umiejętności Pawła ani przedmiotów z okna ekwipunku — bez tego gracz po powrocie straciłby drzewko, za które zapłacił Gemami.
- Do wyboru: (a) włączyć po zmianach po stronie Pawła (lista niżej); (b) włączyć już teraz na próbę tylko w Studio; (c) zostawić wyłączony do czasu przeniesienia pakietu do `src/`.

Szczegóły: Włączenie wymaga dostępu Studio do usług danych (ustawienie gry, zmienia właściciel) i zmian w plikach Pawła: ekran wyboru klasy czeka na wczytanie profilu; klasa wybierana tylko raz (D-081); zakupy drzewka zapisywane razem z profilem; wartości testowe (1000 Gemów) usunięte. Nowy gracz przy włączonym zapisie zaczyna z 0 Złota i 0 Gemów. Dziś pakiet działa tylko w Studio, więc na serwerze gry zapisu sprawdzić się nie da. Pełny opis: `swiat/stan_gracza/README.md`, rozdział „Zapis postępu”. Zob. pytanie 53.
Dopisek z 2026-11-19: po decyzji D-106 (gra do przejścia od startu do bramy Pustyni) to pytanie blokuje grę na więcej niż jedno posiedzenie — bez zapisu poziom, Złoto i przedmioty znikają po wyjściu. Włączenie wymaga zgody jednej z osób i dostępu Studio do usług danych w ustawieniach gry (robi właściciel gry).
**Odpowiedź:**
- Karol (2026-11-19): Tak. Daj zapis postępu.
Rozstrzyga: D-110


## 61. Kowal: czy robocze zasady z próby zostają?
- Kowal na próbę stoi w Studio (D-102): łup przedmiotów z walk, rozbieranie zapasów na materiały, ulepszenia +1…+5.
- Przyjęte roboczo: kuźnia w bazarze (D-049 i D-051 mówią o Twierdzy); przedmioty tylko własnej klasy, szansa 10% / 30% / 50% (zwykły / rzadki / strażnik); nowy przedmiot zakłada się sam.
- Przyjęte roboczo: podstawowy zestaw liczy się jak dziś, a przedmioty i ulepszenia dodają ponad to (pełny zestaw +5: średnia szansa wygranej z ok. 52% na ok. 84%); Wojownik bez tarczy traci blok.
- Do wyboru: (a) zostaje jak w próbie; (b) zostaje, ale z innymi liczbami — jakimi; (c) przedmioty zastępują wzór poziomu (trzeba ulepszać, żeby nadążyć za potworami).

Szczegóły: Projekt i tabele: `swiat/kowal_proba/PROJEKT.md`; raport w panelu „Kowal w bazarze: rozbieranie i ulepszanie przedmiotów (D-102)”. Koszty: 150 / 300 / 450 / 650 / 900 Złota i 1 / 2 / 3 / 4 / 6 materiałów; w symulacji pierwsze ulepszenie po ok. 8 minutach lasu, las się nie skraca, Bagno skraca się o ok. 13%. Okno jest tymczasowe; docelowe robi Paweł (pytanie 57). Bez tierów przedmiotów (D-051: „nie teraz”).
Dopisek z 2026-11-18: przy działającym kowalu przymierzalnia strojów (D-071) pokazuje i zakłada tylko posiadane przedmioty, a „Dawnego wyglądu” nie ma — nieposiadane po prostu znikają z listy, bez wyjaśnienia. Do wyboru przy okazji: przymierzalnia pozwala przymierzyć wszystko na podglądzie, a do walki liczą się tylko posiadane; albo zostają tylko posiadane z napisem „Resztę przedmiotów zdobędziesz w walkach”.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 62. Dżungla: czy potwory, nazwy i trudność z próby zostają?
- Dżungla stoi w Studio jako trzeci biom; jej potwory to propozycje agenta na podstawie zarysu biomów.
- Zmienione względem zarysu: „Zwijogon” zamiast „Liściołaza” (nazwa myliła się z petem Liściolis) i nowy rzadki potwór Pancernik Ruin.
- Strażnik Wąż Stu Lian jest tak trudny jak Strażnik Topieli: gracz na tym samym poziomie wygrywa w 17–26% walk.
- Do wyboru: (a) zostaje; (b) zostaje z innymi nazwami — jakimi; (c) strażnik łatwiejszy albo trudniejszy.

Szczegóły: Potwory i liczby: raport „Dżungla stoi w Studio: trzeci biom do przejścia”; modele: raport „Dżungla: pięć potworów z Blendera do oceny”. Poziomy potworów 17–23 z kalkulatora tempa. Zarys: `swiat/biomy/PLAN_BIOMOW.md` (propozycja). Karol 17.11 o Bagnie: „Strażnik Topieli musi być trudny” — tę samą miarę agent przyjął dla Dżungli.
Dopisek z 2026-11-18 (własne efekty umiejętności): do oceny doszły (1) napisy na banerach inne niż nazwy w silniku — „Usypiający pyłek”, „Plunięcie jadem”, „Ukąszenie”, „Kokosy z góry”, „Kamuflaż”; (2) kły Węża mało kontrastowe na jasnej posadzce areny; (3) płyty Pancernika szare jak on sam; (4) czy Wąż ma mieć własną ozdobę trucizny; (5) fala na ziemi przy kokosach; (6) dźwięki: pyłek gra „zarodniki”, jad „plusk galarety” — do odsłuchu. Raport: „Dżungla: własne efekty umiejętności potworów”.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 63. Postać gracza w świecie: bohater klasy zamiast awatara?
- Dziś po świecie chodzi zwykły awatar Roblox, a bohater klasy (Wojownik, Zwiadowca, Mag) pojawia się tylko w walce.
- Karol 18.11 zlecił próbę: po wyborze klasy gracz chodzi po bazarze i biomach modelem swojego bohatera w założonym stroju.
- Do wyboru: (a) bohater klasy wszędzie; (b) awatar w świecie, bohater tylko w walce — jak dotąd; (c) gracz sam wybiera w ustawieniach.

Szczegóły: Próba powstaje w `swiat/bohater_swiat/` (kontener `Workspace/BohaterSwiat`) z wyłącznikiem, który przywraca awatar bez przebudowy. Za (a): gracz widzi w świecie strój i przedmioty z D-071, a rasy z D-079 mają sens także poza walką. Za (b): gracze Roblox są przywiązani do własnego awatara, a bohater z klocków to więcej części na ekranie telefonu. Wynik próby i zrzuty dojdą w raporcie w panelu.
Dopisek z 2026-11-18 (po próbie w Studio): bohater chodzi po świecie w stroju gracza u wszystkich trzech klas; raport w panelu „Bohater klasy chodzi po świecie zamiast awatara” ze zrzutami i modelami 3D. Wyłącznik bez przebudowy: atrybut `BohaterWSwiecie = false` na `Workspace/BohaterSwiat`. Na komputerze 60 klatek na sekundę także z dwunastoma bohaterami naraz; telefon niesprawdzony. Drugi wybór przy okazji: bieg liczony przez kod (jest dziś) czy ręcznie zrobiony klip biegu w modelach postaci.
Dopisek z 2026-11-18 (wieczór): bieg liczony przez kod został poprawiony — prostsze kolana, praca rąk, poły stroju i szata kota w ruchu, brak ślizgu stopy przy przeszkodzie. Paski klatek trzech klas są w raporcie „Bohater w świecie: nowy bieg trzech klas”. Wybór „bieg z kodu czy ręczny klip w modelach” zostaje otwarty.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 64. Mini-gry w stylu walki: co zostaje, co zmienić?
- Karol 18.11 zlecił mini-gry „pod takimi kątami i w takich efektach jak walki”; próba stoi w Studio (`Workspace/TreningProba`).
- Całość do wyboru: (a) nowy wygląd zostaje; (b) wraca kamera z góry; (c) zostaje z poprawkami z listy niżej.
- Osobno do oceny: wielkość napisów na telefonie, kadr Siły i Run, kiedy sypie się konfetti.

Szczegóły: Kamera stoi nisko i z ukosa (kąt 44–51° zamiast 70°), dojeżdża w odliczaniu i robi zbliżenie na postać po rundzie; przy trafieniach wyskakują komiksowe napisy, po rundzie z punktem statystyki sypie się konfetti; ćwiczy bohater klasy (zależy od pytania 63). Zasady gier, przyrosty i dźwięki są bez zmian. Drobne wybory: (1) duże słowa — „SERIA 5!” zajmuje ok. ćwierci szerokości ekranu 667 × 375 — zmniejszyć na telefonie czy zostawić; (2) Siła: bohater stoi półprzezroczysty przed kamerą, a kule stref zostają w kadrze zbliżenia po rundzie — chować je jak miecz; (3) Runy: kadr zza ramienia przycina bohatera przy lewej krawędzi; (4) konfetti za punkt statystyki (dziś), po każdej ukończonej rundzie albo tylko po rundzie bez pudła; (5) słowa Siły „PAF!”, „ŁUP!”, „TRACH!”, „BAM!”, „POW!” zamiast pochwał; (6) postać obraca się do kamery po rundzie; (7) radość kota-Maga jest mało widoczna (klip z pakietu bohatera). Zrzuty i wynik próby: raport w panelu „Mini-gry Training Center w stylu walki: kamera, napisy, konfetti”; opis wyborów 14–17 w `swiat/trening_proba/PROJEKT.md`.
Dopisek z 2026-11-19: Karol zdecydował o otoczeniu (D-108) — mini-gry w sceneriach krain zamiast areny w murach; kamera, napisy i konfetti zostają do oceny jak wyżej.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 65. Stare zadania z 12–17.11: zamknąć te dziewięć?
- Przy przeglądzie listy zadań dziewięć pozycji wygląda na nieaktualne, ale to nie agent o tym decyduje.
- Do wyboru: (a) zamknąć wszystkie; (b) zamknąć poza wskazanymi — wpisz numery z listy niżej.

Szczegóły: (1) obejrzeć walkę v2 i raport „Walka v2 na ekranie” z decyzją o obrysie postaci — walkę zastąpił silnik v3; (2) spisać błędy z 13.11 w `Workspace/TestWalki` — to stary prototyp; (3) mapa teleportacji jako grafika z ramką i pinami (Backlog) — działa teleport przez chmury (D-075, D-076); (4) porównanie Krzywego Miasteczka w Blenderze i w Roblox, prośba Pawła z 14.11 — decyzja o Blenderze zapadła (D-029); (5) obejrzeć demo `Workspace/DemoLesnaBaza` z 12.11; (6) Krzywe Miasteczko: kolorystyka i czytelność budynków (pytanie 33) — miasteczko jest dziś bazarem (D-084); (7) „odpowiedzieć na pytania 50 i 51” oraz „na pytanie 52” — pytania mają odpowiedzi, zostały tylko wybory z raportu „Kalkulator balansu” i dopiski pod pytaniami 6, 8, 9, 32 i 38; (8) Paweł: `git pull`, panel, imię w Ustawieniach, pytanie 27 — pytanie zdjęte 16.11, Paweł korzysta z panelu i Telegrama; (9) zadania dla agenta osoby (D-072) — decyzja zatwierdzona, nie wiadomo, czy część Pawła jest zrobiona.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — Karol 20.11: większość starych spraw jest nieaktualna — dziewięć zadań z listy zamknięte jak w wariancie (a) (przeniesione do „Zrobione” jako zdjęte).


## 66. Nowa muzyka: które z pięciu utworów zostają?
- Karol 18.11 zlecił „zaprojektuj pozostałe muzyki”; powstało pięć utworów po 90 s: walka, walka ze Strażnikiem, mini-gry, drugi utwór Bagna, drugi utwór Dżungli.
- Do wyboru przy każdym: zostaje, do poprawki (napisz, co zmienić) albo odpada.
- Osobno: czy walka i mini-gry mają mieć własną muzykę zamiast przyciszonej muzyki krainy.

Szczegóły: Utwory są z tego samego generatora i w tej samej palecie instrumentów co pierwsza partia (ElevenLabs Music v2.5 przez Higgsfield, 65,4 kredytu, zostało 139,6). Nikt ich jeszcze nie słyszał — pliki poszły do Karola na telefon, gotowe wersje trafią do `assets/audio/muzyka/`. Do Roblox wejdą jako jeden plik z pięcioma utworami (gra odtwarza odcinki), żeby zużyć jedno wgranie zamiast pięciu: konto ma 10 wgrań audio na miesiąc, 6 zużytych, 2 pójdą na muzykę Bagna i Dżungli z pierwszej partii. Wgranie dopiero po odsłuchu i wyraźnej zgodzie. Kto wybiera: Karol (dźwięk i muzyka, D-093); Paweł może zgłosić uwagi.
Dopisek z 2026-11-18 (po obróbce i próbie w Studio): gotowe wersje są w `assets/audio/muzyka/` (pełne `.mp3` do odsłuchu, `_petla.ogg` do gry), a wspólny plik na jedno wgranie to `assets/audio/arkusz/muzyka_arkusz_b.ogg` (6 min 35 s). Gra już przełącza muzykę na walkę, Strażnika i mini-grę — w próbie z dźwiękiem zastępczym, bo nic z tej partii nie jest wgrane. Uwaga do odsłuchu: utwór mini-gier ma w pełnej wersji cichszy wstęp (ok. 7,5 s), którego w grze nie będzie. Raport w panelu: „Muzyka: Bagno i Dżungla wgrane, pięć nowych utworów, muzyka walki i mini-gier w grze”.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — muzyka do B&C czeka razem z całą grą (D-115); limit wgrań audio w tym miesiącu prawie wykorzystany. Pliki zostają w `assets/audio/muzyka/`; wybór utworów wraca przy publikacji B&C.


## 67. Rasy: te same klocki co człowiek czy własne proporcje?
- Pilotaż (elf, ork) stoi na klockach Rycerza: każdy przedmiot człowieka pasuje od razu, klipy klas działają bez zmian.
- Rzuty Pawła są smuklejsze, ork masywniejszy, goblin mniejszy — same klocki tego nie oddają.
- Do wyboru: (a) te same klocki i skala całej postaci (ork 1,08, goblin 0,88) — tak jest teraz; (b) własne klocki ras — bliżej rzutów, ale każdy przedmiot trzeba dopasować do każdej rasy.

Szczegóły: To pytanie z sekcji „Do ustalenia” notatki [[Rasy — rzuty dla modelarza]], teraz z modelami do porównania: raport w panelu „Modele ras z rzutów Pawła: elf i ork do oceny (pilotaż)” (plansze „rzut i model”, modele 3D). Na rzutach tułów z rękami to ok. 0,45 wzrostu, w modelu 0,78 (pomiar przybliżony). Przy (a) rasę odróżniają skóra, twarz, uszy, włosy, rogi, kły, ogon, aureola i kolor spodenek, a wielkość to mnożnik całego modelu, więc ekwipunek rośnie razem z postacią. Przy (b) kontrakt z D-071 („przedmiot pasuje do typu ciała”) oznacza osobne dopasowanie 20 przedmiotów bohaterów do każdej rasy. Pozostałe cztery rasy powstają na razie według (a). Opis: `swiat/postacie/RASY.md`.
Dopisek z 2026-11-18: komplet sześciu ras stoi na tym założeniu — plansza zbiorcza obok człowieka w raporcie „Sześć ras z rzutów Pawła: komplet modeli do oceny”. Najdalej od rzutu jest goblin (na rysunku duża głowa i cienkie ręce) i ork (masywne ciało).
Dopisek z 2026-11-18 (Paweł w rozmowie z Claude Code, do potwierdzenia w panelu): „w momencie wybierania rasy (…) wyświetli się zamiast ludzika bazowego model, który zrobił Karol, zależnie od rasy, z bazowym ubraniem” — ekran wyboru pokazuje już figury z `Workspace/RasyProba` (dzisiejsze klocki i skale, wariant a).
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 68. Rasa a klasa Mag: Mag jest kotem
- Mag to kot z własnym ciałem; rasy są ciałem człowieka, więc szata i kapelusz Maga na nie nie pasują.
- D-079 mówi „po wyborze klasy ekran ras”, ale nie rozstrzyga, jak wygląda Mag-elf albo Mag-ork.
- Do wyboru: (a) Mag dowolnej rasy na ciele człowieka — potrzebne nowe przedmioty Maga dla człowieka, kot zostaje maskotką; (b) klasa Mag bez wyboru rasy (zawsze kot).

Szczegóły: Wyszło przy budowie modeli ras (D-104): przedmioty mają typ ciała (`czlowiek` albo `kot`, D-071) i założenie szaty kota na ciało człowieka kończy się błędem. Dotyczy też logiki ras, którą robi sesja Pawła (D-079), i ekranu wyboru (D-081). Opis: `swiat/postacie/RASY.md` pkt 9.
Dopisek z 2026-11-18 (Paweł w rozmowie z Claude Code, do potwierdzenia w panelu): „po wyborze ten model ma być na graczu (…) gracz wybierze demona i chodzi demonem; dziś są modele rycerza, łucznika i kotka, a chciałbym, żeby ten model był zamiast tego” — czyli rasa zamiast modelu klasy także u Maga (bliżej wariantu a: Mag na ciele rasy; brakuje przedmiotów i klipów Maga dla ciała człowieka).
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 69. Rasy: drobne wybory wyglądu
- Przy modelach ras wyszło kilka małych wyborów; pilotaż przyjął robocze odpowiedzi.
- Najważniejsze: co robi hełm z uszami, rogami i włosami; kolor spodenek orka; który rzut goblina.
- Można odpowiedzieć na wybrane punkty, reszta zostaje jak w pilotażu.

Szczegóły: (1) Hełm i kaptur dziś chowają włosy w całości, a uszy przechodzą przez ściankę — zostawić, chować też uszy czy robić hełmy z wycięciami na uszy i rogi; (2) spodenki orka: w zamówieniu rzutu brązowe, na rysunku wielokolorowe, model ma brązowe (zlewają się z butami); (3) goblin: pierwszy rzut czy „wariant 2” (większa głowa, cieńsze ręce) — w budowie jest pierwszy; (4) buty: rasy mają brązowe buty jako część ciała, goły Rycerz i Zwiadowca są boso — ujednolicić?; (5) rękawice bez palców mają dłoń w kolorze skóry człowieka, więc ork dostaje ludzkie dłonie — przedmioty mają brać kolor skóry rasy?; (6) spoczynek rasy na ekranie wyboru: klipy są skopiowane z Rycerza (ręka jak do miecza) — zrobić neutralny?; (7) demon: ikona wyboru ma spiczaste uszy, rzut ich nie ma — model będzie bez uszu; (8) Półbóg: czy aureola i świecące oczy zostają pod hełmem (wygląd zależy też od pytania 47). Opis i liczby: `swiat/postacie/RASY.md` pkt 8 i 9.
Dopisek z 2026-11-18 (po komplecie sześciu ras): doszły trzy punkty. (9) Rogi demona: połowa siedzi w hełmie i kapturze, wystają ok. 0,4 studa nad nie — te same trzy możliwości co przy uszach. (10) Ogon demona jest sztywny na biodrach; ruchomy ogon wymagałby własnych kości, a wtedy demon nie dzieli klipów z człowiekiem. (11) Uszy goblina wystają przez hełm najbardziej (ok. 0,7 studa), uszy orka są prawie całe schowane. Raport: „Sześć ras z rzutów Pawła: komplet modeli do oceny”.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — szczegół B&C wstrzymany do decyzji o kierunku (Wytwórnia pomysłów, D-115; B&C na karcie 13/30). Robocze ustawienia z próby zostają w grze bez zmian; pytanie wraca, jeśli B&C zostanie wybrane do dalszej budowy.


## 70. Strażnicy Bagna i Dżungli: zdjąć im 30% życia?
- Symulacja przejścia gry: z samym bohaterem gracz wygrywa ze Strażnikiem Topieli i Wężem Stu Lian 12–28% walk i co siódmy–ósmy gracz odbija się od nich pięć razy lub więcej.
- Propozycja: obu Strażnikom −30% życia (ostrożniej −15%) i potworom Dżungli +25% doświadczenia; utyka wtedy 2–3% graczy, a gra skraca się tylko z 75 do 66 minut.
- Do wyboru: (a) −30% i +25%; (b) −15% i +25%; (c) bez zmian — Strażnicy mają być trudni, gracz ma sięgać po mini-gry, pety i przedmioty.

Szczegóły: Karol 17.11 ustalił na czacie, że Strażnik Topieli ma być trudny — dlatego to pytanie, a nie zmiana. Z mini-grami, petami i kowalem utyka dziś 0–4% graczy, więc trudność Strażników wymusza korzystanie z dodatków; bez dodatków boli (niecierpliwy gracz utyka w 21–42% przypadków). Osobna sprawa z tego samego rachunku: kara za przegraną zabiera graczowi, który nie wydaje, 27% zarobionego Złota (niecierpliwemu 42%) — do rozstrzygnięcia razem z propozycjami D-097–D-100. Liczby i założenia: `swiat/przejscie_gry/PRZEJSCIE_W_LICZBACH.md`; raport w panelu „Przejście gry w liczbach…”.
**Odpowiedź:**
- Karol (2026-11-19): Nie wiem czy 30% to nie za dużo. Gracz słusznie ma się pomęczyć. Może jakieś 15%?
Rozstrzyga: D-111 (życie −15%); doświadczenie z potworów Dżungli +25% zostaje otwarte


## 71. Paweł: makieta okna „Shop” a sklep zbrojmistrza
- W Studio stoi skrypt Pawła `ShopClient` z makietą okna „Shop”; przy zbrojowni otwierał się razem z tymczasowym oknem sklepu Karola.
- Sklep chowa dziś makietę u gracza przy zbrojowni (tylko w grze, niczego nie zmienia w miejscu); wyłącznik: atrybut `ChowajOknoShop = false` na `Workspace/SklepProba`.
- Do wyboru: (a) tak zostaje do czasu docelowego okna Pawła; (b) wyłączyć chowanie; (c) Paweł podpina swoje okno pod kupno i tymczasowe okno znika.

Szczegóły: Skryptu `ShopClient` nie ma w repozytorium ani w `src/` — jest tylko w miejscu gry, więc narzędzia go nie widzą; prośba do Pawła o dodanie go do repo razem z nowymi oknami (Kowal, Mag, sklepy). Umowa dla okna sklepu (pola przedmiotu, prośba `kup <id>`, odmowy) jest opisana w `swiat/sklep_proba/README.md` i `swiat/postacie/SKLEP_PRZEDMIOTY.md`. Kliknięcie w samą figurę zbrojmistrza otwiera dziś makietę Pawła, a E — okno sklepu. To pytanie do Pawła (jego okna, D-093).
**Odpowiedź:**
- Karol Balucki (2026-11-21): a

## 72. Przyciąć grę do jednego rdzenia: który wariant?
- Film twórcy hitu i nasza diagnoza z 13.11 mówią to samo: jedna prosta czynność, jedna liczba, moment do nagrania, telefon najpierw, szybko do prawdziwych graczy.
- (a) Szybki grinder: walka rozstrzyga się w 1–2 s w świecie, potwór odlatuje, pełna walka tylko przy Strażnikach; gracz widzi jedną liczbę „Moc”; karczma, Twierdza, drzewka, rasy, plansza, dungeony, arena i gildie zamrożone do czasu danych.
- (b) BONK: gracz sam uderza potwory w czasie rzeczywistym — więcej pracy, mocniejszy moment do nagrania. (c) Zostaje obecny kształt, tylko dopieszczamy.
- Osobno: kiedy pierwsza publiczna wersja testowa i czy wydajemy Robuxy na reklamę.

Szczegóły: Pełna analiza, tabela zasad i lista konfliktów z zatwierdzonymi decyzjami: [[Diagnoza 2026-11-19 — prostota i szansa na hit]]. Rekomendacja agenta: (a) jako najszybsza droga do graczy, (b) jeśli pomiar pokaże, że rdzeń jest za bierny. Zamrożenie nie kasuje kodu — systemy wracają, gdy gracze zostają (bramka z [[Ocena potencjału gry]]: powroty następnego dnia 15–20%). Przycięcie dotyka plików i decyzji Pawła (wybór klasy, drzewko, okna) — potrzebne zdanie obu osób. Przed jakimkolwiek wypuszczeniem i tak trzeba: sprawdzić grę na prawdziwym telefonie, przenieść ją z prób w Studio do prawdziwej gry i włączyć telemetrię (D-023).
Dopisek z 2026-11-19 (wieczór, po przeglądzie rynku): rekomendacja agenta zmienia się na (b) BONK z fizyką — trendy listopada to ragdoll i rzucanie (Hyper Realistic Ragdoll, Throw Food For Animals), jajka i pety oraz urocze zwierzęta (Cat Battles), a algorytm od czerwca nagradza powroty w oknie 28 dni i grę ze znajomymi. Proponowana decyzja biznesowa: jedna gra naraz, publiczna wersja testowa w ok. 3 tygodnie, progi z góry (co najmniej 30% powrotów następnego dnia → reklama ok. 35 tys. Robux i aktualizacje co tydzień; 15–30% → poprawki rdzenia; poniżej 15% → inny rdzeń z tych samych zasobów), bez klonu „Steal an Egg”. Szczegóły: rozdział „Rynek 19.11.2026 i decyzja biznesowa” w [[Diagnoza 2026-11-19 — prostota i szansa na hit]].
**Odpowiedź:**
- Karol (2026-11-19): Okej. Może to zrobimy. Podczas nocy na Opusie zrób tę grę w całości. To jest prosta gra, wedle twojego opisu. Zezwalam na wszystko w tej gestii oraz na korzystanie z Higgsfield.
Rozstrzyga: D-112

## 73. Ring Potworów jako druga gra: kiedy budujemy?
- Karol i Paweł 19.11: druga gra — jajka, potwory z Księgi, trening AFK, wspólny ring serwera, na którym kilka potworów bije się do ostatniego.
- Ocena agenta: mocny pomysł, w pokazaniu się i momencie do nagrania mocniejszy od BONK; używa najwięcej z tego, co mamy (silnik walki, modele potworów, jajka, areny).
- Do wyboru: (a) po pomiarze BONK jako druga próba; (b) zaraz po nocnej budowie BONK, równolegle; (c) Ring zamiast BONK.

Szczegóły: Opis, ocena wobec zasad z filmu i sześć poprawek agenta (przycisk dopingu w walce, rundy po ligach Mocy, nagroda dla każdego uczestnika, rytm rund, bez skojarzeń z walkami zwierząt i hazardem, Siła trenera bez utraty postępu): [[Ring Potworów — pomysł]]. Nocna budowa BONK tworzy wspólne klocki (jajka, pety, zapis, efekty, mapy), które Ring też wykorzysta.
**Odpowiedź:**
- Claude Code na polecenie Karola (2026-11-20): nieaktualne — zastąpione oceną w Wytwórni pomysłów (D-115): Ring Potworów jest pomysłem w lejku (`Wytwórnia/Pomysły/Ring Potworów`), a kolejność budowy ustala sesja według karty oceny i najtańszego testu (pytanie 75).


## 74. BONK: publikujemy jako osobną grę do pomiaru?
- BONK zbudowany w nocy 19/20.11: trzy krainy, pałki, pety, Strażnicy; próba w Studio 33/33, ikona i trzy miniatury gotowe.
- Publikacja to decyzja ludzi (D-112): nowe miejsce w grupie (D-044), kroki w `swiat/bonk/README.md`.
- Do wyboru: (a) publikujemy po próbie we dwóch; (b) najpierw poprawki po waszym graniu, potem publikacja; (c) nie publikujemy, wracamy do B&C.

Szczegóły: Cel pomiaru i progi z propozycji decyzji biznesowej (co najmniej 30% powrotów następnego dnia → reklama i aktualizacje co tydzień; 15–30% → poprawki rdzenia; poniżej 15% → inny rdzeń) w [[Diagnoza 2026-11-19 — prostota i szansa na hit]]. Opis gry i stan budowy: [[BONK — projekt prototypu]]. Raport w panelu ze zrzutami i planszą klatek demo.
**Odpowiedź:**
- Karol (2026-11-20): A — publikujemy po próbie we dwóch.
Rozstrzyga: D-113

## 75. Wytwórnia: który pomysł idzie do najtańszego testu?
- Na karcie oceny (agent, 20.11): Monster Evolution 26/30, Sleeping Giant Heist 25, Ring Potworów 23, Smash Tower 23, BONK naprawiony (Chain Reaction) 22, BONK dziś 19, B&C 13.
- Każdy pomysł ma w notatce najtańszy test na 2–3 dni; buduje się jeden naraz.
- Do wyboru: jeden z pomysłów do testu albo inny — oceńcie kartą w panelu (Wytwórnia).

Szczegóły: Notatki i oceny: [[00 Wytwórnia pomysłów]] (lejek, krytyka agenta, pre-mortem). Oceny agenta to szacunek, nie dane od graczy — spór rozstrzygnie test z ludźmi. Badanie rynku i zasady twórcy, którego ogląda Karol: [[Radar trendów]], [[Mózg — zasady hitu Roblox]].
Dopisek z 2026-11-20 (sesja główna 18:59): Karol i Paweł przedstawili po jednym nowym pomyśle — pet-arenę Karola i „Super Kitty Brawlers” Pawła (propozycja D-116: karty do lejka). Karol: oba trzeba jeszcze ocenić kartą i krytyką agenta; wyboru do najtańszego testu nie było. Zapis: [[Sesja główna 2026-11-20 — zapis ustaleń]].
**Odpowiedź:**
- Karol (2026-11-20): do budowy idzie Pet Arena (pomysł z sesji 20.11; agent 27/30, Karol 28/30).
Rozstrzyga: D-118



## 76. BONK: porzucić czy dokończyć próbę i pomiar?
- Karol na sesji 20.11 zaproponował porzucić BONK i budować nowe gry na jego zasobach, ale zastrzegł, że to nie jest ostateczna decyzja i czeka na opinię agenta.
- D-113 (podpis Karola) mówi co innego: próba we dwóch, publikacja jako osobna gra i pomiar powrotów.
- Do wyboru: (a) porzucamy, zasoby idą do nowych gier; (b) kończymy próbę i pomiar, potem decyzja według progów; (c) poprawiamy BONK (wariant Chain Reaction, 22/30) i traktujemy go jako jeden z testów obok nowych pomysłów.
Rozstrzyga: D-117

Szczegóły: Źródło: [[Sesja główna 2026-11-20 — zapis ustaleń]] (18:52 propozycja, 18:58 zastrzeżenie). Stan faktyczny: BONK ma prywatną wersję testową (D-113), w Wytwórni 19/30 z werdyktem „popraw” ([[BONK]]), a Karol po zagraniu napisał, że znudził mu się po paru minutach ([[Lekcje z prototypów]]). Uwaga agenta (D-114, nie z rozmowy): porzucenie bez pomiaru kłóci się z zasadą wytwórni „prawdziwi gracze rozstrzygają spory” ([[00 Wytwórnia pomysłów]]), a pomiar jest tani, bo gra już stoi; z drugiej strony czas jednej gry naraz jest ograniczony. Pełna opinia po krytycznym myśleniu jest zadaniem w [[Zadania]].
**Odpowiedź:**
- Karol (2026-11-20): (a) porzucamy BONK, zasoby i wiedza idą do Pet Areny — „to nie tak, że czas i tokeny były stracone”. Opinia agenta (zgodna): BONK nudzi nawet nas, naprawa i tak wymienia rdzeń, a pomiar słabej gry nie powie nic o rynku; prywatna wersja testowa zostaje.

## 77. Pet Arena: wystawić prywatną wersję testową dla Was dwóch?
- Prototyp stoi w Studio w pliku lokalnym (próba 28/28); żeby zagrać we dwóch i z telefonu, trzeba go opublikować jako prywatną grę, jak BONK 20.11.
- Do wyboru: (a) tak — agent publikuje prywatnie na koncie Karola i zaprasza Pawła; (b) najpierw Karol gra sam w Studio i mówi, co poprawić; (c) nie teraz.
- Publicznie nic nie idzie bez osobnej decyzji.

Szczegóły: Publikacja prywatna sprawdza też prawdziwy zapis postępu i telefon. Kroki są w `swiat/pet_arena/README.md`. Projekt i lista rzeczy do strojenia: [[Pet Arena — projekt prototypu]]; karta: [[Pet Arena]]. Przeniesienie do grupy przed startem publicznym — pytanie 31.
Dopisek z 2026-11-21: po notatce [[Nowa era Roblox 2026 — pięć zmian]] agent poleca (a) zaraz po przebudowie z 21.11 — okno trendu trwa tygodnie, a dopracowywanie gry, zanim zagra w nią ktoś spoza zespołu, to błąd, przed którym film ostrzega.
Dopisek z 2026-11-21 (po analizie trendu): okno jest krótkie — prywatny test z ludźmi spoza zespołu do ok. 28.11 (Roblox pozwala zaprosić do 10 testerów; najlepiej osoby 16+, bo tacy będą pierwszymi publicznymi graczami), publiczny test najpóźniej ok. 5.12. Szczegóły: [[Pet Arena — ocena wobec trendu 2026-11-21]].
**Odpowiedź:**
- Karol (2026-11-21): (a) tak — zgoda na prywatną wersję testową („zgadzam się na wszystko”); publicznie nic bez osobnej decyzji.

- Karol Balucki (2026-11-21): tak

## 78. Pet Arena: loch czy jaskrawa, zamknięta arena?
- Karol na sesji 21.11 myślał o lochu albo więzieniu, ale w grę będą grać też dzieci, a one wolą jaskrawe kolory; nie wybrał.
- Pewne jest tylko, że arena ma być zamkniętą przestrzenią.
- Do wyboru: (a) loch albo więzienie; (b) zamknięta arena w jaskrawych kolorach, np. stadion albo koloseum z zabawek; (c) agent pokazuje po jednym zrzucie obu wersji i wtedy wybór.

Szczegóły: [[Sesja główna 2026-11-21 — zapis ustaleń]] (18:28–18:29). Karol dodał, że liczy się tu z cudzym zdaniem — z zapisu nie wynika, czy mówił do agenta, czy do Pawła. Zdanie agenta (D-114): (b) — gra ma być dla każdej grupy wiekowej (D-022), a ciemna klatka z bijącymi się zwierzakami budzi skojarzenie z walkami zwierząt, którego mieliśmy unikać ([[Ring Potworów]]); zmienię zdanie, jeśli dzieci znajomych wybiorą ciemną wersję ze zrzutów. Od odpowiedzi zależy przebudowa sceny (propozycja D-119).
**Odpowiedź:**
- Claude Code u Karola (2026-11-25): nieaktualne — Pet Arena jest wstrzymana, wracamy do Blocky & Crycket (D-139, oba podpisy). Zdjęte z kolejki na polecenie Karola z 25.11 („wyczyść dashboard z pytań nieaktualnych”).

## 79. Pet Arena: czy Karol decyduje o niej sam?
- Karol 21.11, sam na sesji: agent może wykonywać jego polecenia o Pet Arenie bez wiedzy Pawła, bo to jego pomysł i projekt.
- D-043, ustalona przez obu 14.11, mówi: jedna osoba decyduje, druga potwierdza.
- Do wyboru: (a) wyjątek — przy Pet Arenie wystarcza podpis Karola; (b) bez zmian — Karol prowadzi grę, a Paweł potwierdza albo cofa jak dotąd.

Szczegóły: [[Sesja główna 2026-11-21 — zapis ustaleń]] (18:31). Pawła nie było na sesji; D-118 (budowa Pet Areny) dalej czeka na jego potwierdzenie, a 20.11 miał wątpliwość co do pomysłu. Dla pracy agenta oba warianty znaczą to samo: zlecenia Karola wykonuje od razu, na roboczych ustaleniach z jednym podpisem. Różnica jest tylko taka, czy Paweł może decyzję o Pet Arenie cofnąć. Zasadę podpisów zmieniają obaj, więc najlepiej, żeby odpowiedział tu Paweł.
Rozstrzyga: D-124
**Odpowiedź:**
- Claude Code u Karola (2026-11-25): nieaktualne — Pet Arena jest wstrzymana, wracamy do Blocky & Crycket (D-139, oba podpisy). Zdjęte z kolejki na polecenie Karola z 25.11 („wyczyść dashboard z pytań nieaktualnych”).

## 80. Konto klipów z wirtualnymi streamerami: w jakiej wersji?
- Pomysł Karola (21.11): konto na Instagramie i TikToku, streamerzy z Higgsfield reagują na gry Roblox, w tym naszą.
- Agent pomoże w wersji jawnej: postacie oznaczone jako AI, nasza gra oznaczona jako nasza; w wersji udającej prawdziwych streamerów i ukrywającej promocję — nie (zasady platform, prawo o ukrytej reklamie, widzowie-dzieci).
- Do wyboru: (a) wersja jawna, próba 15 klipów; (b) odłożyć, aż gra będzie miała dobre powroty; (c) inaczej — jak.
Rozstrzyga: D-126

Szczegóły: Ocena, zasady i progi próby: [[Konto klipów z wirtualnymi streamerami — pomysł]]; zasady marketingu: [[00 Marketing]]. Koszt klipu w kredytach Higgsfield do wyceny w sesji marketingowej.
**Odpowiedź:**
- Karol Balucki (2026-11-25): rozstrzygnięte decyzjami: D-126 zatwierdzona

## 81. Po Pet Arenie: wieczór trzech zabawek?
- Karol po graniu (21.11): Pet Arena jest mało wciągająca, „to chyba nie ten pomysł”. Agent zaleca zakończyć ją w tym kształcie.
- Propozycja agenta: zamiast kolejnej całej gry — trzy małe zabawki (sama czynność, 2 minuty grania na telefonie każda), wybór tej, przy której chce się „jeszcze raz”.
- Zabawki: (1) jesteś potworem i spychasz innych (drążek i szarża), (2) armata potworów — celujesz i burzysz zamki z klocków, (3) legowisko olbrzyma — skradasz się po jajka, hałas go budzi.
- Do wyboru: (a) wszystkie trzy (ok. 0,45 mln tokenów, jedna noc); (b) tylko wskazane; (c) inny pomysł Karola albo Pawła; (d) przerwa i rozmowa we dwóch.

Szczegóły: Dlaczego zabawki, a nie gra: [[Lekcje z prototypów]] (wpis o Pet Arenie) i bramka „próba zabawki” w [[Karta oceny pomysłu]]. Zabawki stanęłyby w obecnym prywatnym miejscu testowym jako trzy wejścia; używają tego, co mamy (sterowanie potworem i wybicia z Pet Areny, generator klocków, Strażnicy i jajka).
Dopisek z 2026-11-21 (po prośbie Karola o lepsze pomysły wyprowadzone z rynku): zamiast trzech zabawek z pierwszej wersji — cztery kierunki z danych tygodnia w [[Kierunki z rynku 2026-11-21]]; agent poleca dwie zabawki na jedną noc: „Eat & Evolve” (jesteś potworem, jesz i rośniesz) i „Lure a Monster” (rzut przynęty, zwabianie potworów).
**Odpowiedź:**
- Karol (2026-11-21): „Ok, puść je” — dwie zabawki polecone przez agenta („Eat & Evolve” i „Lure a Monster”). Wybór po graniu na telefonie.

## 82. Następna gra: zagrać w trzy gry i wybrać kierunek
- Analiza z 22.11 poleca pomysł „Zdąż przed nocą” (w dzień wyprowadzasz potwory z nor do obozu, o zmierzchu Olbrzym zabiera to, co nie zdążyło za bramę); pewność niska do średniej.
- Zanim cokolwiek zbudujemy: Karol gra po 10 minut w Stay the Night, Steal An Egg i Clean The Ballpit! (pół godziny, bez kosztu).
- Do wyboru: (a) wciąga Stay the Night — próbka „Zdąż przed nocą” (3–4 wieczory); (b) wciąga Ballpit — próbka „Odkop potwora” (2–3 wieczory); (c) nic nie wciąga — nie budujemy; (d) inny kierunek.

Szczegóły: [[Następna gra — rekomendacja 2026-11-22]] (jedna strona), pełne opisy: [[Trzy pomysły na następną grę (2026-11-22)]], karta pomysłu: [[Bring Monsters Home Before Dark]]. Ważny wniosek analizy: sam pomysł to mniejsza część wyniku — gra-wzór była mała przez pięć tygodni i wybiła się cotygodniowymi aktualizacjami.
Dopisek z 2026-11-22 (po walidacji wybranego kierunku): pierwotny kształt „Zdąż przed nocą” jest słabszy, niż wyglądał — zob. [[Walidacja kierunku noc i Olbrzym (2026-11-22)]]. Agent proponuje zmieniony kształt „Guard Your Monsters From the Giant” ([[Projekt próbki — Guard Your Monsters From the Giant]]): budowa próbki 3–4 wieczory, bramka po pierwszym wieczorze (sama scena nocy pokazana dwóm–trzem osobom), potem próba z 8–12 osobami spoza zespołu. Do decyzji Karola (i Pawła): budujemy próbkę / rozmowa we dwóch / inny kierunek.
Dopisek z 2026-11-22 (południe, po odrzuceniu porwania przez Karola): do ustalenia, jak wygląda noc. (a) oblężenie — Olbrzym uderza w płot, „czy wytrzymał” (zaleca agent, pewność niska); (b) kradzież między graczami (największe liczby na rynku, fala ma cztery miesiące i dziesiątki kopii); (c) fale i potwory-wieżyczki (pomysł Karola; walidacja: ta odmiana gaśnie); (d) inny kierunek. Szczegóły: [[Walidacja wariantu nocne fale i potwory-obrońcy (2026-11-22)]].
Dopisek z 2026-11-22 (po porzuceniu pomysłu z Olbrzymem): nowa krótka lista z fal rosnących — (A) jesteś potworem, każda ewolucja to losowanie; (B) armia potworów, która idzie za tobą i walczy; (C) odsłoń potwora własnymi rękami, zmywając bryłę; rezerwowo jazda na potworze i wspólne skradanie. Najpierw weto ludzi (które odpadają od razu), potem agent szuka przegranych dla reszty. Szczegóły: [[Kierunki z rynku 2026-11-22]].
Dopisek z 2026-11-22 (wybór z liczb): Karol nie chce rozstrzygać gustem; agent wskazał kierunek A („jesteś potworem”) i go sprawdził — przechodzi minimum, z niskim sufitem ([[Walidacja kierunku jesteś potworem (2026-11-22)]]). Budowa próbki: [[Projekt próbki — Monster Evolution]].
**Odpowiedź:**
- Karol (2026-11-22): wybiera pomysł drugi, „Zdąż przed nocą” („najlepiej brzmi”); nie chce testu własnego gustu — „nie ma znaczenia, co mnie pociąga, tylko co obecnie pociąga internet”. Budowy jeszcze nie zlecił; agent pogłębia analizę tego kierunku (przegrane próby, rozbiór najbliższych gier, dowody z filmów w sieci, projekt próbki).
- Karol (2026-11-22, południe): „Bez sensu jest ta kradzież. Może zrobilibyśmy jakieś fale do przejścia, a zwierzaki będą wieżyczkami i atakować fale potworów. Nie wiem” — porwanie przez Olbrzyma odrzucone; fale to luźna propozycja, nie decyzja. Agent: po walidacji fal nie poleca, zaleca oblężenie; czeka na wybór.
- Karol (2026-11-22, po walidacji fal): „W takim razie nie przywiązujmy się do tego pomysłu i lećmy gdzie indziej. Podchodźmy do problemu optymalnie. Jeżeli jakiś pomysł ma być porażką, to po co w niego inwestować. Znajdźmy ten wschodzący trend i dodajmy nasz wyjątkowy faktor” — pomysł z Olbrzymem porzucony; kierunek następnej gry nadal otwarty.
- Karol (2026-11-22): „Co sam uważasz, że ma największy potencjał? Jakie znaczenie ma moje zdanie, skoro będzie ono subiektywne, a nie obiektywne? Liczą się liczby i statystyki”, a po wskazaniu kierunku A: „Okej. Zgoda. Zdajemy się na realne liczby i statystykę. Daj mi tu link do Ant Evolution i rozpocznij budowę”.

Rozstrzyga: D-129 (budowa próbki Monster Evolution); zasada wyboru: D-128.

## 83. Monster Evolution: animacje chodu potworów
- Żaden z ośmiu modeli nie ma szkieletu; w próbce ruszają się proceduralnie (podskok, ściskanie, pochylenie).
- Lider fali wygrywa wykonaniem: Karol wskazał u niego grafikę, responsywność i animacje chodzenia.
- Do wyboru: (a) zostajemy przy ruchu proceduralnym do próby z graczami; (b) Karol robi szkielety i chód dla ośmiu form w Blenderze przed próbą; (c) tylko dla dwóch–trzech pierwszych form, które widzi każdy gracz.

Szczegóły: [[Projekt próbki — Monster Evolution]], sekcja „Po etapie 1”. Agent zaleca (c): pierwsze minuty decydują o pierwszym wrażeniu, a osiem pełnych animacji to dni pracy w oknie 2–4 tygodni.
Dopisek z 2026-11-22: jedno dwunożne zwierzę na standardowym szkielecie postaci Roblox rozwiązałoby animacje bez pracy w Blenderze — zob. pytanie 84.
Dopisek z 2026-11-22 (po próbie technicznej): gotowe animacje postaci Roblox działają na dwunożnym modelu w skali 0,5–6 razy; od Karola potrzebne byłyby najwyżej części ciała w stylu klocków, bez szkieletu i bez animacji. Chód jest ludzki, wyprostowany.
**Odpowiedź:**
- Karol (2026-11-22): zgoda na wgrywanie modeli smoka („masz pełne zgody”). Animacje robi agent w Blenderze jako klipy z biblioteki postaci; smok czworonożny, bez standardowego szkieletu postaci.

## 84. Monster Evolution: jedno zwierzę — które?
- Karol zapytał, czy nie robić jednego zwierzęcia; dane to popierają (jeden rozpoznawalny stwór w tytule, jeden szkielet na osiem form).
- Sama zamiana zwierzęcia nie robi hitu: klony lidera z innym zwierzęciem mają 27–427 graczy.
- Do wyboru: (a) małpka → goryl → olbrzymi goryl — zaleca agent; (b) jaszczurka → smok chodzący, wymaga szkieletu z Blendera, tytuł zajęty; (c) wilk; (d) zostaje osiem różnych potworów.
- Agent przerobi drabinę na (a) po etapie 2, jeśli nikt nie wybierze inaczej; zmiana jest odwracalna (formy są w tabeli danych).

Szczegóły: [[Wybór zwierzęcia do gry o ewolucji (2026-11-22)]]; uzasadnienie i ryzyka także w [[Projekt próbki — Monster Evolution]].
Dopisek z 2026-11-22 (po próbie technicznej): wariant (a) jest wykonalny bez Blendera — zob. [[Projekt próbki — Monster Evolution]], „Próba techniczna”. Próbny model małpy jest surowy; przeróbka całej gry to 150–200 tys. tokenów i czeka na wybór zwierzęcia.
**Odpowiedź:**
- Karol (2026-11-22): „Nie wiem, może smok? Ale jeśli sugerujesz małpę, to może być, ale więcej zdolności uda nam się zrobić na smokach”. Agent zmienia zalecenie na smoka: w tej mechanice klon ze smokiem ma ok. cztery razy więcej graczy niż klon z małpą, pięć nowych gier ze smokami ma razem 27,5 tys. graczy, smok daje najwięcej zdolności i najlepszą ostatnią formę, a legowisko ze skarbem to naturalny motyw smoka; próba techniczna pokazała też, że przewaga małpy (gotowy chód) jest mniejsza, niż zakładał. Ustalenie robocze: smok chodzący, bez swobodnego latania (krótki ślizg jako zdolność późnych form); tytuł „Dragon Evolution” jest zajęty — wolne w wyszukiwarce 22.11: „Dragon Lair Evolution”, „Evolve a Dragon”, „Baby Dragon Evolution”. Przeróbka po etapie 3; modelu smoka nie mamy — na start złoży go agent z klocków, docelowy model w naszym stylu to praca Karola.
- Karol (2026-11-22): „Tak. Masz pełne zgody, tytuł jest dobry.” — tytuł „Dragon Lair Evolution”; styl smoka: kierunek „Żarołuska” z arkusza stylu (zalecenie agenta, bez sprzeciwu Karola).

Rozstrzyga: D-138 (tytuł); zwierzę — smok, w D-137.

## 85. Baseball for treasure: skąd gracz bierze siłę?
- Na sesji 22.11 padły trzy wersje i żadna nie wygrała.
- (a) hantla, którą postać podnosi sama (Paweł); (b) podciąganie albo pompki, jak drążek we wzorze (Karol); (c) bez osobnego treningu — siłę dają kij i ulepszenia (Karol pod koniec, zdanie urwane).
- Karol zostawił to zdaniu agenta; Paweł do (c) się nie odniósł.

Szczegóły: [[Sesja główna 2026-11-22 — zapis ustaleń]] (18:56–18:57, 19:00). Łączy się z propozycją D-132: kij roboczo daje mnożnik siły. Zdanie agenta (D-114): zostawić trening, czyli (a) albo (b) — różnica między nimi to tylko wygląd, a hantla odróżnia nas od drążka ze wzoru. Wariant (c) zabiera grze powód, żeby zostawić ją włączoną i wrócić następnego dnia, oraz jeden z trzech wydatków złota: we wzorze drążek robi powtórzenie co pół sekundy także pod nieobecność gracza, a drążków do kupienia jest 46 ([[Rozbiór wzoru — Throw Food For Animals]]). Zmienię zdanie, jeśli próbka bez treningu trzyma graczy tak samo długo. Karta: [[Baseball for treasure]].
**Odpowiedź:**
- Claude Code u Karola (2026-11-25): nieaktualne — Baseball for treasure jest wstrzymany, wracamy do Blocky & Crycket (D-139, oba podpisy). Zdjęte z kolejki na polecenie Karola z 25.11 („wyczyść dashboard z pytań nieaktualnych”).

## 86. Baseball, ameba czy smok: co budujemy dalej?
- Na sesji 22.11 Paweł przedstawił Baseball for treasure, a Karol rozbudowę gry o smoku: od ameby, z osobnymi serwerami na poziomy.
- Karol: gra o smoku może zostać przerobiona, jeśli agent uzna nowe pomysły za lepsze; obaj czekają na ocenę.
- Do wyboru po ocenie: (a) smok bez zmian idzie do próby z graczami, baseball jako następna próbka; (b) baseball od razu, smok wstrzymany; (c) smok rozbudowany od ameby; (d) żadne — szukamy dalej.

Szczegóły: [[Sesja główna 2026-11-22 — zapis ustaleń]] (18:57–18:59, 19:01); propozycje D-133 (ameba) i D-134 (najpierw ocena). Pełnej oceny jeszcze nie ma — to zadanie w [[Zadania]] (sprawdzenie rynku po mechanice baseballu ok. 0,2 mln tokenów; start po poleceniu na czacie). Wstępne zdanie agenta (D-114, hipoteza): (a) z dopiskiem. Gra o smoku stoi, jest opublikowana prywatnie i czeka na graczy, nie na budowę, więc przerabianie jej przed pomiarem znów rozstrzygałoby gustem (D-128). Próbka jednej pętli baseballu może powstać równolegle, jeśli pomysł przejdzie sprawdzenie rynku — okno fali liczymy do ok. 6.12 ([[Baseball for treasure]], „Krytyka agenta”). Ameby w kształcie z sesji nie polecam: najbliższa gra o ewolucji komórki spadła z 11,5 tys. graczy do 62 ([[Walidacja kierunku jesteś potworem (2026-11-22)]]).
Dopisek z 2026-11-22 (sesja główna 19:39): na drugiej, minutowej sesji Karol wrócił do tego pytania, ale nie wybrał żadnej z dróg. Poprosił agenta o odmiany baseballu łatające słabe punkty z oceny (jego przykład: potworek zamiast skarbu — propozycja D-136) i o pokrewne gry tego typu; uznał też, że kryterium „Inni gracze” nie powinno obniżać oceny (D-135). Paweł nie zabrał głosu. Zapis: [[Sesja główna 2026-11-22 (2) — zapis ustaleń]].
Dopisek z 2026-11-22 (wieczór; Karol: „Co powinniśmy teraz zrobić… Musimy na czymś definitywnie przystanąć”; agent, D-114): zalecenie — stajemy na metodzie z datą, nie na guście: (1) gra o smoku zamrożona bez zmian i idzie do graczy w tym tygodniu; (2) baseball dostaje sprawdzenie rynku po mechanice (ok. 0,2 mln tokenów), a jeśli przejdzie — próbkę jednej pętli w dwa wieczory na kodzie smoka (zapis, gablota jak legowisko, ulepszenia, pomiar), z warstwą ragdolla (piłka przewraca postacie na trasie lotu); (3) ci sami gracze grają w obie, ok. 30.11 wybór jednej gry z liczb, zwycięzca dostaje cztery tygodnie cotygodniowych aktualizacji, przegrany idzie do szuflady; do tego czasu żadnych nowych budów. Ameba z serwerami poziomów — nie (gra o ewolucji komórki: 11,5 tys. → 62 graczy; trzy różne budowy ciała to trzy razy więcej modeli; osobne serwery rozbijają małą grę na puste serwery). Ragdoll jako czysta piaskownica — nie (ponad sto gier od października, pierwsza fala traci 25–45% tygodniowo); jako warstwa w grze — tak.
Dopisek z 2026-11-22 (21:00, po sprawdzeniu baseballu): agent ok. 20:30 polecił baseball pod warunkiem, że sprawdzenie nie znajdzie cmentarza — znalazło ([[Walidacja Baseball for treasure (2026-11-22)]]). Zgodnie z tym warunkiem zalecenie zmienia się na: **gra o smoku, wydana publicznie w tym tygodniu** — dane z fali rzutu mówią, że wygrywały tylko kopie wydane w dwa tygodnie po wybiciu lidera; lider fali ewolucji jest na listach od 14–15.11, więc okno smoka liczymy do ok. 29.11. Przed wydaniem jeden wieczór poprawek pierwszego wrażenia (pisklę i skrzydła, miniatura z czarną sylwetką i znakiem zapytania — cecha 4 z 9 wygranych kopii i 0 z 9 przegranych). Publiczne wydanie wymaga osobnej zgody ludzi.
**Odpowiedź:**
- Karol (2026-11-22, wieczór): „Zgadzam się z tą wizją. Lecimy ze smokami” — gra o smoku do końca, wydanie we wtorek–środę 24–25.11; baseball wstrzymany, ameba z serwerami poziomów nie wchodzi.

Rozstrzyga: D-137.

## 87. Sklep w grze o smoku: ceny i łączenie mnożników
- Kod sklepu jest w grze, ale wyłączony. Produkty i przepustki w Roblox założymy dopiero po Waszym „tak”, bo ceny to decyzja ludzi.
- Propozycja agenta, bez płatnych losowań:
  - przepustki: 2x GROWTH za 199 R$ i VIP LAIR (złoto legowiska ×1,5, złoty sztandar) za 249 R$;
  - złoto: 1000 za 25 R$, 6000 za 99 R$, 25 000 za 299 R$;
  - podwójny wzrost na 15 min za 39 R$.
- Do wyboru: (a) te ceny; (b) inne ceny; (c) sklep dopiero po pierwszym tygodniu.
- Drugie pytanie: czy 15-minutowy podwójny wzrost łączy się z przepustką, dając ×4?

Szczegóły: kod, sprawdzenia i uzasadnienie każdej ceny opisuje sekcja „Odczucie walki, krótkie powitanie, tempo, sklep (odczucie1)” w `swiat/ewolucja/README.md`, stan gry jest w [[Projekt próbki — Monster Evolution]].
- ProcessReceipt sprawdzono na udawanym sklepie: nagroda zapisuje się przed potwierdzeniem i nie da się jej dostać dwa razy.
- Zdanie agenta (D-114): (a) oraz łączenie do ×4. Pierwsza fala graczy po wydaniu to największa szansa na przychód, więc sklep powinien być od pierwszego dnia. Łączenie mnożników to w grach o wzroście norma, a gracze się go spodziewają.
- Zmienię zdanie, jeśli próba z ludźmi pokaże, że ×4 przeskakuje stadia tak szybko, że gra traci cel. Wtedy zostaje (a) bez łączenia.
**Odpowiedź:**
- Claude Code u Karola (2026-11-25): nieaktualne — gra o smoku nie wychodzi (D-137 zastąpiona przez D-139), więc jej sklep nie jest potrzebny. Zdjęte z kolejki na polecenie Karola z 25.11 („wyczyść dashboard z pytań nieaktualnych”).

## 88. Powrót do Blocky & Crycket: co z wydaniem smoka?
- Paweł 23.11 zdecydował: wracamy do Blocky & Crycket jako głównej gry (D-139). Czeka na potwierdzenie Karola.
- Twoja D-137 zakładała wydanie gry o smoku 24–25.11 — dwie decyzje się rozjeżdżają, żadnej nie zmieniono.
- Do wyboru: (a) wydajemy smoka w obecnym stanie, potem całość na Blocky & Crycket; (b) smok wstrzymany od razu, bez wydania; (c) smok dalej równolegle.

Szczegóły: zdanie agenta (D-114) — (a). Wydanie kosztuje mało, bo gra jest gotowa do próby, a da pierwsze dane o prawdziwych graczach; porzucenie dzień przed wydaniem marnuje największą naukę z tej pracy. Zmienię zdanie, jeśli przed wydaniem zostało więcej niż około dzień pracy.
**Odpowiedź:**
- Karol (2026-11-25): „Okej, wracamy do pracy. Ostateczną decyzją jest powrót do B&C na 100%. Dokańczamy tę grę, zwracając uwagę na nasze błędy.” Oznacza to wariant (b): smok wstrzymany bez wydania, wersja prywatna zostaje.

Rozstrzyga: D-139.

## 89. Karol: za poziom Diamenty, trening AFK — kto wdraża?
- Paweł 23.11: awans daje Diamenty na drzewko zamiast punktów statystyk (D-140), a statystyki trenuje się na stanowiskach AFK z paskiem (D-141). Obie czekają na Twoje potwierdzenie.
- Obie zmiany są w Twoich pakietach (`stan_gracza`, `trening_proba`) i w 3D, więc agent Pawła ich nie ruszał.
- Do wyboru: (a) Twój agent wdraża obie, a agent Pawła robi okno paska treningu 2D; (b) zgadzasz się, żeby agent Pawła zmienił liczby w `stan_gracza` i zbudował stanowiska; (c) nie zgadzasz się — rozmowa na sesji.

Szczegóły: poprawki agenta (tapnięcie przyspiesza pasek, przyrost rośnie z poziomem, mini-gry jako bonus, przeliczenie tempa walk bez punktów za poziom) są w treści D-140 i D-141 w [[Rejestr decyzji]]. Dotyka D-097 (dwa podpisy), D-050, D-108 i pytania 50.
**Odpowiedź:**
- Karol Balucki (2026-11-25): Paweł już wdrożył

## 90. Pakiety Karola działają tylko w Studio — przed wydaniem?
- Stan gracza, kowal, sklep (i inne pakiety `swiat/…`) mają na początku `if not RunService:IsStudio() then return`.
- W opublikowanej grze nie ruszy więc zapis, łup, poziomy ani sklep — Blocky & Crycket nie jest dziś gotowe do wydania.
- Do wyboru: (a) zdjąć blokady pakiet po pakiecie i przejść całą grę w prywatnej wersji; (b) zostawić do czasu wyboru, które pakiety idą do wydania.

Szczegóły: wykryte 23.11 przy podpinaniu sklepu Pawła pod serwer sklepu Karola (`swiat/sklep_proba/zrodla/SerwerSklepu.server.luau`, wiersz 19; podobnie `swiat/kowal_proba`, `swiat/stan_gracza`). Prawdopodobnie zabezpieczenie prototypów przed przypadkową publikacją. Właściciel: Karol.
**Odpowiedź:**
- Karol Balucki (2026-11-25): a

## 91. Karol: gracz chodzi modelem rasy zamiast bohatera klasy?
- Paweł 23.11 (D-143): po wyborze rasy gracz porusza się modelem rasy (demon, elf, ork…), nie Rycerzem, Zwiadowcą ani Kotem-Magiem; animacje mają pasować do ras.
- Dotyka Twoich pakietów: `swiat/bohater_swiat` (wybór modelu po klasie) i modeli ras `swiat/rasy_proba` (D-104, propozycja). Agent Pawła ich nie ruszał.
- Do wyboru: (a) Twój agent przestawia bohatera w świecie na model rasy (klasa = broń i strój); (b) zgoda, żeby zrobił to agent Pawła na swojej gałęzi; (c) zostaje bohater klasy — rozmowa na sesji.

Szczegóły: modele ras mają ten sam szkielet R15 i klipy co bohaterowie (`swiat/postacie/RASY.md` pkt 1). Animacje treningu AFK (gałąź `pawel/diamenty-afk`) już działają na bohaterze, awatarze i każdym szkielecie R15 — nadpisują pozę tylko lokalnie, w czasie treningu, po pętli Twojego bohatera (priorytet Last + 1). Poza tym trening potrzebuje od Ciebie: rozszerzenia umowy `RuchBohatera` o wymuszony obrót korzenia (leżenie na ławce) albo zgody na obecne obejście.
**Odpowiedź:**
- Karol Balucki (2026-11-25): Tak. Teraz zdecydowaliśmy że każda postać to kotem, tylko różnica będzie jako model rasy. Teraz wojownik też jest kotkiem, ale może być razy ddemon, elf itd

## 92. Skalowanie statystyk: limit krytyka i redukcji obrażeń
- Paweł: przy 134 Szczęścia okno pokazuje 167,50% krytyka — trzeba to przeskalować, np. krytyk najwyżej 50% (D-144, do decyzji).
- Propozycja: krytyk = 50% · Szczęście / (Szczęście + 30); redukcja obrażeń = 75% · Pancerz / (Pancerz + 160).
- Do wyboru: (a) ten wzór w oknie i w walce; (b) Karol podaje limity, które już ma w walce, a okno je pokazuje; (c) inne limity.

Szczegóły: dziś okno ekwipunku (`EquipmentPanelClient`) liczy Szczęście × 1,25% i Pancerz × 0,44% bez limitu — to zastępcze napisy, nie te same liczby co walka w `StanGracza` (Karol). Przy obecnym starcie wzór z (a) daje te same wartości co teraz (10 Szczęścia ≈ 12,5%, 10 Pancerza ≈ 4,4%), a rośnie coraz wolniej. Zdanie agenta (D-114): (a) albo (b) — ważne, żeby okno i walka liczyły tak samo.
**Odpowiedź:**
- Karol Balucki (2026-11-25): c - zbalansowane limity, balans całkowity przeprowadzimy w ramach wporwadzenia broni, bo balans będzie się musiał na nich opierać

## 93. Karol: koty zamiast ludzików — kto robi modele i przedmioty?
- Paweł 24.11 (D-145): wszystkie postacie gracza to koty (rasy = warianty Kota-Maga), w wyborze klasy koty w przedmiotach Rycerza i Zwiadowcy; Blocky zostaje właścicielem kotów w lore.
- Zrobione u Pawła na próbę: Kot-Demon (pełny strój i podstawowy) i Kot-Człowiek w wyborze rasy (`swiat/postacie/kot_demon.py`, kopie w `ReplicatedStorage.WyborKlasyModele`); Twoje pliki nietknięte.
- Do wyboru: (a) Twoja strona robi resztę ras, przedmioty klas i sklepu pod ciało kota oraz bohatera w świecie (plan Max); (b) agent Pawła robi to krok po kroku; (c) nie zgadzasz się z D-144 — rozmowa na sesji.

Szczegóły: referencje 7 ras (jedna para uszu u elfów i goblina): [[Rasy jako koty — referencje]]. Przedmioty z katalogu sklepu mają ciało „czlowiek” i nie pasują do kota. Bohater w świecie (`swiat/bohater_swiat`) dalej pokazuje Rycerza/Zwiadowcę/Kota-Maga — zob. też pytanie 91. Kopie ludzików w wyborze rasy zostały jako `Race_Demon_ludek` i `Race_Human_ludek`.
**Odpowiedź:**
- Karol Balucki (2026-11-25): Paweł zrobił modele, pobierzmy je, poprawmy bugi i animacje. Przedmiotami zajmuje się ja. Zadbaj aby się nie bugował podczas animacji i żeby nie nachodziły na kotka twarz podczas wykonywnia ruchów lub czegoś

## 94. Pula Lv 1–10: 5 przedmiotów na slot, spodnie jako slot, strefy?
- Paweł 24.11: w pierwszej puli po 5 przedmiotów na slot (broń, hełm, klata, spodnie, buty, rękawice) dla każdej klasy; zestawy opcjonalne — lista nazw: [[Przedmioty — pula Lv 1–10, 5 na slot (propozycja)]].
- Spodnie to nowy slot (dziś są częścią zbroi, a slotem jest pas) — zmienia ekwipunek i sklep.
- Do wyboru: (a) lista jak w notatce, ikony najpierw dla Rycerza (30); (b) wszystkie 90 ikon od razu; (c) poprawki nazw. Osobno: spodnie zamiast pasa / obok pasa; strefa tylko podbija szansę na „przedmiot strefy” z puli (zgodnie z D-142) albo pule według stref.

Szczegóły: D-142 (Paweł 23.11) mówi „według poziomu, nie według krainy”; pomysł ze strefami ją zmienia, dlatego wariant zgodny z D-142 jest w notatce. Koszt ikon: 15 arkuszy po 6 ikon.
**Odpowiedź:**
- Karol Balucki (2026-11-25): b

## 95. Katakumby i kolejne lochy: 10 przeciwników po kolei
- Paweł 24.11: loch „Katakumby”, 10 przeciwników jako modele 3D, E = walka, kolejno bez przeskakiwania; lista przeciwników „bardzo okej” — [[Katakumby — pierwszy loch (propozycja)]]. Lochy 2 i 3 (Zatopiony Galeon 16–26, Psia Twierdza 26–36): [[Lochy 2 i 3 — Zatopiony Galeon i Psia Twierdza (propozycja)]].
- Agent: liniowa droga z kratami otwieranymi osobno dla gracza zamiast otwartej mapy (otwarta mapa to już las), postęp 4/10 zapisany.
- Do wyboru: (a) modele robi strona Karola (5 gryzoni na jednym szkielecie + 5 osobnych); (b) agent Pawła krok po kroku; osobno wejście: Korzenna Gardziel w lesie / hala portali w mieście (D-042) / oba.

Szczegóły: poziomy robocze 5–15 (#5 i #10 to ściany), łup za pierwsze pokonanie, powtórki z pomijaniem animacji (D-078). Dotyka pytania 3 w [[Biom Las]] („Loch lasu”).
**Odpowiedź:**
- Karol Balucki (2026-11-25): a. Ja mogę zrobić pomnijesze gryzonie, ale podobno Paweł zrobił już bosa.

## 96. Rzadkość przedmiotów: ile statystyk na stopień?
- Paweł 24.11: zwykły 1–2 statystyki, epicki do 3 i mocniej, legendarny do wszystkich, do tego sekretne; mini-boss i boss mają lepsze szanse — [[Rzadkość przedmiotów — zwykłe, epickie, legendarne, sekretne (propozycja)]].
- Agent: legenda daje połowę budżetu w główną statystykę klasy + pasywkę, żeby nie była najlepsza dla każdej klasy po równo.
- Do wyboru: (a) jak w notatce; (b) legenda po równo na wszystkie; osobno: tier Rzadki (niebieski) zostaje / wypada; licznik pecha tak / nie.

Szczegóły: mnożniki budżetu ×1,0 / ×1,4 / ×1,8 i szanse są robocze — do kalkulatora `tools/walka/balans.py`. Zastępuje tabelę rzadkości w [[Przedmioty — zestawy v1]]; rozwija D-142.
**Odpowiedź:**

## 97. Bez Blocky'ego: gra o kotach, nowa nazwa później?
- Paweł 24.11: nie nawiązujemy do Blocky'ego, gra „po prostu o kotkach”, w stylu Shakes & Fidget; ekran ładowania i nazwę przerobić później.
- Zmienia część D-145 (Blocky jako właściciel kotów) — czeka na zdanie Karola.
- Do wyboru: (a) zgoda, nazwa i ekran ładowania na osobnej sesji; (b) Blocky zostaje jako NPC; (c) rozmowa na sesji.

Szczegóły: tytuł „Blocky & Crycket” bez Blocky'ego traci sens — nowa nazwa dotknie ekranu ładowania ([[Ekran ładowania]]), strony gry i miniatur; repo i nazwy w kodzie mogą zostać. Uwaga agenta (D-114): zgoda — „Cat” w nazwie pomaga w wyszukiwaniu na Roblox, a kot jest jednym rozpoznawalnym bohaterem.
Dopisek z 2026-11-25 (Karol): ekran ładowania trzeba poprawić już teraz, bo postaciami są tylko koty (D-145). Przy odpowiedzi do ustalenia: czy na nowym ekranie zostaje napis „BLOCKY & CRYCKET” do czasu nowej nazwy, czy ekran jest bez tytułu. Zdanie agenta: zostawić obecny tytuł i zmienić tylko grafikę na koty, bo nazwa gry w Roblox i ekran powinny mówić to samo, a zmiana nazwy to osobna sesja.
**Odpowiedź:**

## 98. Karol: mistrz gier i leśne jajo — podpięcie u Ciebie
- Okno mistrza gier działa (D-053): nagrody wypłaca dziś testowe „przyznaj” Twojego stanu gracza, a płatny rzut odmawia, bo źródła „MistrzGier” nie ma w `DaneStanu.wydatki.zrodla`.
- Leśne jajo Pawła (model z jego projektu 3D, karta petów, scenka z klikaniem, pet wyłania się ze słupa światła) stoi w miasteczku obok Twojej zagrody i kupuje przez haczyk `SterowanieSerwera("kup")` Twoich petów.
- Do wyboru: (a) dopisujesz „MistrzGier” do wydatków i dajesz źródło nagród, a nowe jajo zastępuje model przy Twoim inkubatorze; (b) agent Pawła robi to na gałęzi, Ty oglądasz; (c) zostaje próbą.
- Trzy dylematy do jaja: gdzie ma stać na stałe; czy oddajesz budowę modeli petów poza Studio; czy opisy umiejętności mówią „Rybki” zamiast „Złoto” (D-146).

Szczegóły: pliki `src/server/MistrzGier.server.luau`, `src/server/JajkoKorowe.server.luau`, `src/client/JajkoKoroweClient.client.luau`, `tools/studio/jajo_lesne_ustaw.luau`; Twoich plików nikt nie zmieniał. Numer zmieniony z 95 na 98 (24.11 dwa pytania dostały numer 95).
Dopisek z 2026-11-24 (wieczór), dylematy szerzej: (1) miejsce — jajo stało za północną ścianą miasteczka (983, −652), gdzie gracz nie dojdzie; przeniesione na próbę na (955, −695), obok zagrody petów i stacji treningu Siły — czy tam zostaje, czy staje w lesie zamiast Twojego inkubatora. (2) Pet nad jajem i podobizny na karcie budują się Twoim `RigPetow.zbuduj`, a ten moduł poza Studio zwraca pustą tabelę — w wydanej grze byłyby same napisy (zob. pytanie 90). (3) Klient jaja podmienia w opisach „Złota” na „Rybek” tylko na wyświetlaniu; dane w `DanePetow` zostają Twoje. (4) Scenka u kupującego czeka na 5 kliknięć (bez kliknięcia idzie dalej sama po 7 s), inni gracze widzą wyklucie od razu — to odpowiedź Pawła na D-060 (wyklucie samo czy z klikaniem), do Twojego potwierdzenia.
**Odpowiedź:**


## 99. Karol: dolna siatka u kowala — zapasy do rozbiórki?
- Nowe okno kowala Pawła ma pod przedmiotami siatkę pustych slotów; Paweł pytał, do czego służą.
- Propozycja agenta: pokazywać tam zapasowe przedmioty (te, które Twoja kuźnia pozwala rozebrać na materiały), klik = rozbierz.
- Do wyboru: (a) tak, zapasy do rozbiórki; (b) siatka na materiały; (c) usunąć siatkę z okna.

Szczegóły: okno `src/client/OknoKowalaClient.client.luau` korzysta z Twojego zdalnego `KowalProba/Zdalne/Kuznia` („widok”, „ulepsz”, „rozbierz”) bez zmian u Ciebie; Paweł jeszcze nie wybrał.
**Odpowiedź:**

## 100. Miasto: kreska jak w sali dziś czy czarna i grubsza?
- Karol 25.11 (D-147): miasto ma dostać kreskę i tekstury jak sala wyboru rasy; mówił o „widoczniejszych czarnych kreskach”.
- Paweł 24.11 zmiękczył salę: cienka brązowa kreska i tekstury w wersji 2 zamiast grubego czarnego tuszu.
- Do wyboru: (a) miasto jak sala dziś, czyli brązowa i cienka; (b) czarna i grubsza w mieście i w sali; (c) czarna tylko w mieście.

Szczegóły: [[Tekstury sali wyboru klasy]], sekcja „Wersja 2”. Zdanie agenta (D-114): (a). Celem jest jednolitość, a Paweł dopiero co wybrał miękką kreskę; wariant (b) cofa jego zmianę, więc wymaga jego zgody. Zmienię zdanie, jeśli na telefonie brązowa kreska na budynkach widzianych z daleka zniknie — wtedy grubsza kreska tylko na dużych bryłach.
**Odpowiedź:**

## 101. Lag przy otwieraniu sklepu i ekwipunku: kto poprawia?
- Karol 25.11: okna sklepu i ekwipunku czasem przycinają przy otwieraniu.
- Kod tych okien jest Pawła (`src/client`, `src/gui`), więc agent Karola nie zmienia go bez zgody.
- Do wyboru: (a) agent Karola mierzy i poprawia na osobnej gałęzi, Paweł ogląda przed scaleniem; (b) agent Karola tylko mierzy i opisuje, poprawia agent Pawła; (c) Paweł zgadza się na poprawki prosto na `main`.

Szczegóły: Paweł 24.11 już przyspieszył okna (grafiki wczytywane z góry, bez animacji wjazdu). Zdanie agenta: (a) — pomiar i poprawka w jednych rękach, a Paweł zachowuje kontrolę nad swoim kodem.
**Odpowiedź:**
- Karol Balucki (2026-11-25): ja


## 102. Karol: nowy układ HUD — przyciski po lewej, questy w szufladzie
- Paweł 25.11: sześć mniejszych przycisków po lewej w dwóch rzędach, Index zamiast Quests, questy w wysuwanym panelu po prawej.
- Stoi na próbę w Studio; kanon HUD (5 zakładek) i układ z Figmy czekają na decyzję.
- Do wyboru: (a) zostaje; (b) zostaje z poprawkami — jakimi; (c) wracamy do dwóch kolumn.
- Osobno: co pokazuje szuflada questów — zadania na czas z karczmy (D-034), zadania dzienne, jedno i drugie?

Szczegóły: opis w [[HUD]], sekcja „Układ z 2026-11-25”. W szufladzie są dziś trzy przykładowe wpisy bez logiki. Twoja tablica w karczmie woła dawny przycisk „Quests” — teraz otwiera szufladę. Przycisk Index nie ma jeszcze okna. Zastrzeżenie agenta: na telefonie lewy dół zajmuje joystick, więc rzędy stoją tam wyżej.
**Odpowiedź:**


## 103. Karol: pety — drugi slot, zdejmowanie i usuwanie
- Okno petów Pawła ma 4 sloty (2 otwarte), a Twój stan gracza zna jednego aktywnego peta.
- Dziś slot 2 jest tylko w oknie (bez premii, bez zapisu), peta ze slotu 1 nie da się zdjąć poza zagrodą, DELETE nie działa.
- Do wyboru: (a) dodajesz w stanie gracza kilka aktywnych petów, „odstaw” bez zasięgu i usuwanie kopii; (b) agent Pawła robi to na gałęzi, Ty oglądasz; (c) zostaje jeden pet, okno pokazuje jeden slot.
- Do ustalenia też: jak odblokowuje się sloty 3 i 4 i czy plecak petów ma limit.

Szczegóły: [[Okno petów (propozycja)]]; serwer okna `src/server/OknoPetow.server.luau` woła tylko Twój haczyk `SterowanieSerwera` („stan”, „wybierz” z pominięciem zasięgu). Premie kilku petów naraz zmieniają balans walki (dziś +20% Inteligencji od jednego epickiego).
**Odpowiedź:**

