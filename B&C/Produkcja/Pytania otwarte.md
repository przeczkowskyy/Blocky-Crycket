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

## 5. Przyciski HUD: kanon czy Figma?
[[HUD]] (kanon) przewiduje 5 zakładek na krawędziach: Karczma, Pety, Tycoon, Arena, Ekwipunek. Figma (node 9:1570) ma 6 przycisków: Teleport, Equipment, Pets, Quests, Shop, Guilds, z napisami po angielsku. Wdrożono wersję z Figmy. Czy zastępuje ona kanon (wtedy nowa decyzja w [[Rejestr decyzji]])? Gdzie trafią Tycoon i Arena? Czy napisy na przyciskach zostają po angielsku?
**Odpowiedź:**

## 6. Diamenty (Gems) a Magiczne Kryształy
Kanon ([[Twierdza (Tycoon)]], [[HUD]]) zna dwie waluty: **Złoto** i **Magiczne Kryształy**, które pasywnie generują droppery. HUD z Figmy pokazuje **Złoto** i **Diamenty (Gems)**, opisane w specyfikacji HUD jako waluta premium. Czy Diamenty to Magiczne Kryształy pod inną nazwą? Czy waluta jest płatna (Robux), czy zdobywana w grze?
**Odpowiedź:**

## 7. Questy na czas a decyzja D-004
Rozmowa 12.11 [8:54–10:17] wprowadza questy trwające od 3 minut do 5 sekund (skracane rozgłosem strefy) i najemnika, a zatwierdzona D-004 mówi „bez biernego czekania”. Propozycja D-013 godzi oba podejścia: walka od razu, liczniki tylko równolegle. Którą wersję przyjmujecie? Zob. [[Propozycje z rozmowy 2026-11-12]].
**Odpowiedź:**

## 8. Karczma: trzy misje czy strefy z rozgłosem i osobne lochy?
Kanon [[Karczma (Questy)]] opisuje trzy misje w mini-dungeonach. Rozmowa: strefy odblokowywane poziomem, a lochy jako osobna oś z portali (łatwy / średni / trudny). Co zostaje z D-009 i Energii?
**Odpowiedź:**

## 9. Twierdza: kiedy i co produkuje?
Rozmowa [21:46]: działka od ok. 25. poziomu, surowce i klejnoty do osadzania w broni. Kanon [[Twierdza (Tycoon)]]: droppery dające Złoto i Magiczne Kryształy. Rekomendacja Claude Code: pierwszy budynek już w pierwszej sesji. Łączy się z pytaniem 6 o waluty.
**Odpowiedź:**

## 10. Styl UI: pixel-art z kanonu czy wdrożony cartoon?
Zob. propozycja D-018 i [[Styl UI gier Roblox]]. Czy napisy na przyciskach przenosimy z grafik do tekstu (tłumaczenia, polskie znaki)?
**Odpowiedź:**

## 11. Czy panel zespołu jest zgodny z D-008?
D-008 porzuciła dashboard z agentami na rzecz sejfu. Karol poprosił 12.11 o wspólny panel; zbudowany `panel/` niczego nie trzyma poza sejfem (propozycja D-012, [[Panel zespołu]]). Game Director: zatwierdzasz, zmieniasz zakres czy usuwamy?
**Odpowiedź:**

## 12. Do kogo celujemy i czym zarabiamy?
Gracze poniżej 13 lat (łagodna ocena treści, bez reklam nagradzanych) czy 13+? Czy rezygnujemy z płatnych tokenów losowania (propozycja D-015)? Jak nazwiemy koło fortuny — „Labubu” to cudza marka.
**Odpowiedź:**

## 13. Własność gry i assetów
Konto jednej osoby czy wspólna grupa Roblox? Od tego zależy, kto wgrywa assety i animacje, kto tworzy klucz Open Cloud do analityki i kto dostaje wypłaty.
**Odpowiedź:**

## 14. Repozytorium publiczne czy prywatne?
W repo są sejf, prompty, plik `.rbxl`, a teraz też dane panelu (raporty, komentarze). Pełna transkrypcja rozmowy i prywatny Warsztat narzędziowy Karola **nie zostały wgrane** właśnie z tego powodu. Zob. [[Workflow i Git]].
**Odpowiedź:**

## 15. Kto zatwierdza kanon, gdy pracują dwie osoby?
Dziś zasady sejfu mówią o jednym Game Directorze. Od 12.11 pracują dwie osoby, każda ze swoim Claude Code. Do czasu odpowiedzi Claude traktuje jako wiążącą tylko zgodę Game Directora (Pawła), a prośby Karola zapisuje jako propozycje. Czy tak ma zostać, czy obaj zatwierdzacie (a spory rozstrzyga Game Director)?
**Odpowiedź:**

## 16. Czy bierzemy myśl przewodnią v2 do szarego prototypu?
Nocna diagnoza (13.11) oceniła obecny pomysł na 3,8/10 i proponuje nową oś: BONK i krzywy montaż ([[Myśl przewodnia v2]], propozycje D-019 i D-020). Na papierze daje to 6,0/10; wyżej może pójść tylko po pomiarze. Najtańszy sprawdzian to tygodniowy szary prototyp z botem-klikaczem (bramka B1). Zgoda na prototyp nie zmienia jeszcze kanonu. Pełna lista 15 decyzji z rekomendacjami: [[Karta ocen v2 i plan sprawdzenia]].
**Odpowiedź:**

## 17. Statystyki i ekwipunek: budujemy teraz czy odsuwamy?
W nocy 12/13.11 w Studio pojawiły się `ServerScriptService.Server.StatPoints`, `ReplicatedStorage.Shared.Items` i zmiany w `EquipmentPanel` (praca Game Directora). Propozycja v2 odsuwa punkty statystyk (zamiast nich poziomy kumpli i jedna liczba „Moc bandy”), a okno ekwipunku zamienia w okno bandy z plecakiem. Trzy drogi: v2 w całości, hybryda (ekwipunek wraca jako warstwa po bramce B1) albo zostajemy przy statystykach i poprawiamy tylko pierwszą minutę. Kod Game Directora zostaje nietknięty do decyzji.
**Odpowiedź:**

## 18. Publiczność 16+ na start i miękka premiera
Nową grę widzą najpierw tylko gracze 16+ ze sprawdzonym wiekiem (propozycja D-022). Czy projektujemy haczyk i pierwszy test pod nich, a grudzień traktujemy jako miękką premierę bez decyzji „zakończyć”?
**Odpowiedź:**

## 19. Kufel i alkohol w kanonie
Kanoniczna ikona Karczmy w [[HUD]] to kufel, a [[Ekran ładowania]] ma żarty o kuflu. Roblox dopuszcza odniesienia do alkoholu tylko w grach 18+ (propozycja D-021). Zmieniamy na kociołek i chochlę („Zupa u Chochli”)? Dotyczy też demo v1 mapy (szyld z kuflem na karczmie).
**Odpowiedź:**

## 20. Telemetria: włączamy i kto ma klucz?
Kod jest gotowy i bezwładny (propozycja D-023, [[Telemetria gry]]). Do decyzji: czy w ogóle (wbudowana analityka Roblox działa od 10 graczy dziennie), kto tworzy klucz Open Cloud tylko do odczytu, jak długo trzymamy godziny w Data Store i czy goście panelu z kodem dostępu mają widzieć liczby sprzedaży.
**Odpowiedź:**

## 21. Godziny, telefon testowy i budżet reklamy
Plan v2 zakłada dziennik godzin (ok. 20 h na osobę tygodniowo daje Etap A w ok. 4 tygodnie; przy 15 h — ok. 8 tygodni), tani telefon z Androidem do pomiarów oraz reklamę rzędu 400 nowych graczy tygodniowo na kohortę z limitem kwoty od Game Directora. Ile godzin realnie mamy i jaki limit wydatków przyjmujemy?
**Odpowiedź:**
