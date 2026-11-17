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
**Odpowiedź:**
- Karol Balucki (2026-11-14): Paweł stworzy grupe

## 32. Pierwsze wydanie: ulepszanie przedmiotów, gildie i lista biomów (D-035)
- Ulepszanie przedmiotów: na premierę (Karol) czy później (Paweł).
- Gildie: na premierę czy później.
- Które biomy i ile na start.
Szczegóły: Lista „na premierę” i „później” jest w D-035. Sporne albo nie padło: (1) ulepszanie przedmiotów (kowal, zaklinanie) — Karol: może od razu, Paweł: później; (2) gildie — Paweł wcześniej chciał je odłożyć, na sesji wprost nie potwierdził; (3) które biomy i ile na start — padło tylko „las od początku, kryształowy wyżej” i „o biomach powiemy później”. Zob. [[Sesja główna 2026-11-14 — zapis ustaleń]], [[Roadmapa]].
Dopisek z 2026-11-14 (druga sesja): kowal znalazł się na liście budynków Twierdzy „do wersji początkowej” (propozycje D-049, D-051), choć D-035 odkłada go na po premierze; tiery przedmiotów — Paweł: „nie teraz”. Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
Dopisek z 2026-11-14 (trzecia sesja): (2) gildie — po premierze (obaj zgodni, propozycja D-067; budynek gildyjny z D-049 też); (3) biomy — osiem na start w kolejności las, bagno, dżungla, pustynia, góry z tundrą, lodowiec, wulkaniczny, kryształowy (D-061), obsydian pod znakiem zapytania. (1) ulepszanie na premierę nadal nie padło; zaklinacz miałby stać na pustyni. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
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
**Odpowiedź:**

## 51. Gemy: skąd ma je brać gracz bez płacenia?
- Dziś łup z potworów daje ok. 7 Gemów w 10 godzin gry, a drzewka kosztują razem 20 650.
- Sloty umiejętności są w drzewku za 25 / 70 / 125 Gemów, więc gracz bez płacenia nie ma w 10 godzin żadnego slotu.
- Do wyboru: (a) Gemy za kamienie milowe, np. +10 za poziom i +100 za pierwszego strażnika biomu (ok. 135 na godzinę); (b) sloty umiejętności za poziom, nie za Gemy; (c) jedno i drugie; (d) zostawić.

Szczegóły: Liczby z kalkulatora (`tools/walka/BALANS_1711.md`, część 4), ceny węzłów z `src/shared/SkillTreeData.luau`. Dotyczy D-057 (węzły za Gemy) oraz D-055 i D-088 (sloty umiejętności). Cel roboczy: żeby gracz bez płacenia kupił w 10 godzin ćwierć drzewka gracza, potrzeba ok. 200 Gemów na godzinę; kamienie milowe z kopalnią diamentów od 25. poziomu dają ok. 200.
**Odpowiedź:**
