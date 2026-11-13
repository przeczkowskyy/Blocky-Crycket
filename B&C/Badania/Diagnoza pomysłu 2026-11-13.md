---
status: propozycja
tags: [badania, diagnoza, strategia, ocena]
---
# Diagnoza pomysłu 2026-11-13

> [!info] W skrócie
> W nocy 12/13.11 osiem soczewek (rynek, pierwsze 10 minut, psychologia, retencja, monetyzacja, społeczność, tożsamość, wykonalność) zbadało pomysł, a niezależni weryfikatorzy poprawili ich wnioski. Stan dzisiejszy (kanon, rozmowa 12.11 i propozycje D-013…D-018) to **3,8/10**, a najsłabsze są haczyk, pętla rdzenia i społeczność (po 3). Przyczyna nadrzędna: gra jest opisana przez cudzą grę, a nie przez własną fantazję z czasownikiem. Dwie zasady platformy wymuszają zmiany w kanonie: nową grę widzą najpierw tylko gracze 16+, a alkohol jest dozwolony tylko w grach 18+. To materiał do decyzji, nie kanon; poprawkę opisują [[Myśl przewodnia v2]], [[Systemy gry v2]] i [[Karta ocen v2 i plan sprawdzenia]].

Oznaczenia: **F** = fakt ze źródłem, **W** = wniosek, **H** = hipoteza. Gdzie soczewka i weryfikator się różniły, przyjęto wersję weryfikatora.

## Ocena dziś

| Kryterium | Ocena | Dlaczego |
|---|---|---|
| K1 Haczyk w 5 s | 3 | tytuł z dwóch imion, opis z czterech gatunków, brak ikony pokazującej czynność |
| K2 Pierwsze 10 min | 4 | wybór klasy, martwy HUD, okno z 3 kartami i 5,8 s wymuszonego ładowania przed zabawą |
| K3 Pętla rdzenia | 3 | powtarzaną czynnością jest patrzenie na wynik walki, w trzech sprzecznych wersjach |
| K4 Postęp | 4 | dobre klocki, ale bez krzywych i bez celów na dni 8–28 |
| K5 Powroty | 5 | dużo powodów, ale zegarowych i zebranych w pierwszym tygodniu |
| K6 Społeczność | 3 | pętla prywatna, martwe gildie, zero zaproszeń i momentów do nagrania |
| K7 Monetyzacja | 4 | dobra zasada D-015 bez zatwierdzenia, z przeciekami (spin z VIP-a, Diamenty) |
| K8 Tożsamość | 4 | własny [[Kot-Mag]], ale cudza nazwa w prefiksie stylu i humor w 12 zdaniach |
| K9 Wykonalność | 4 | brak uzgodnionej pętli, 0 z 15 pytań z odpowiedzią, rozjechane gałęzie |
| K10 Live-ops | 4 | narzędzia są, jednostki treści nie ma; „mapa na rok” to 20 nowych systemów |

**Średnia 3,8, minimum 3.** To mniej niż „5–6 jako kierunek” z [[Ocena potencjału gry]], bo tamta ocena zakładała dziecięcą publiczność i bramkę D1, które tej nocy upadły.

## Przyczyny źródłowe

1. **Myśl przewodnia to port cudzej gry** (K1, K8, K3, K10). Sejf opisuje grę przez inspirację i cztery gatunki. Nazwa inspiracji pada w 25 plikach i 86 wierszach repozytorium (**F**, `git grep`, 13.11.2026), także w prefiksie D-001, a jest zarejestrowanym znakiem słownym.
2. **Rdzeń bez decyzji gracza** (K3, K2, K6, K10). „Wybierz, obejrzyj, odbierz” w trzech wersjach: kanon, auto-walka z rozmowy 12.11 i cutscenka z D-013. Hitu z biernym oglądaniem walki nie znaleziono. Działają gry, w których jednostki walczą same, ale gracz decyduje: Tower Defense ma 166–218 tys. graczy naraz (**F**, bloxodes, 13.11.2026).
3. **Pierwsza sesja zaczyna się od menu** (K2, K1). Wybór rasy i klasy, sześć przycisków bez funkcji, pet „od poziomu”, twierdza od ok. 25. poziomu. Wyjście w pierwszych 60 s i w 61–180 s to sygnał „most important” (**F**, docs discovery).
4. **Postęp to lista systemów, a dni 8–28 są puste** (K4, K5, K10). Rekomendacje liczą dni gry w oknie 28 dni. Mediana D7 to 1,6%, a D30 0,5% (**F**, GameAnalytics).
5. **Projekt pod niewłaściwą publiczność** (K1, K2, K9, K5). Projekt celuje w 9–15 lat, a nową grę widzą najpierw tylko sprawdzeni gracze 16+ (**F**). Bramka D-014 zmierzy więc inną grupę.
6. **Pętla prywatna** (K6, K5, K1). Inni gracze nic nie wnoszą. Dni wspólnej gry to sygnał rekomendacji (**F**).
7. **Powroty na zegarze** (K5, K7). Sklep co 5 min, „epik co 30 min, żeby kampili”, spin co godzinę, energia. Czas gry liczy się do sygnałów najwyżej przez 60 min dziennie (**F**).
8. **Granice platformy i etyki nie są wpisane w projekt** (K7, K8, K1). Kufel w czterech miejscach kanonu i propozycji, losowania pośrednio płatne, waluta premium.
9. **Brak jednej uzgodnionej pętli do zbudowania** (K9, K10). Zatwierdzonych 6 z 18 decyzji, narzędzia mają ok. 27 razy więcej linii niż gra (**F**, repozytorium).
10. **Humor istnieje na papierze, nie w rozgrywce** (K8, K1, K6). Postacie bez imion, wad i gagów (poza Kotem-Magiem).

**Mocne strony:** kierunek D-004 (aktywna gra) ma po swojej stronie dowody; RPG ma najwięcej graczy na grę i Roblox pisze, że starsi gracze chcą RPG; [[Kot-Mag]] to najmocniejsza własna postać; lochy z bossem i rozgłos strefy to dobry materiał na drabiny postępu.

## Twarde ograniczenia odkryte tej nocy

| Ograniczenie (odczyt 13.11.2026) | Skutek dla projektu |
|---|---|
| Nowa gra trafia najpierw tylko do sprawdzonych graczy 16+. Do kont 5–15 lat po 250 unikalnych odtworzeniach od „mocno zaangażowanych” w 60 dni; przegląd przyspieszony 50 000 R$, zwrotny (create.roblox.com/docs/production/publishing/kids-and-select) | haczyk i humor muszą najpierw działać na 16+; test z D-014 nic nie mówi o dzieciach |
| Alkohol i odniesienia do niego tylko w grach 18+; miejsca, gdzie alkohol jest powszechny, trzeba zgłosić w ankiecie (docs content-maturity) | Karczma bez kufla, bez napitku z D-009, nowe żarty na [[Ekran ładowania]] |
| Płatne losowania tylko z jawnymi szansami i PolicyService; obejmują też klucze, rerolle, szczęście i walutę za Robuxy (docs paid-random-items) | D-015 to wybór etyczny, nie wymóg; spin z VIP-a to płatny los |
| Gry łudząco podobne do innych gier Roblox tracą widoczność (devforum, 09.12.2024) | tytuł i ikona nie mogą przypominać hitów |
| Czat wymaga sprawdzenia wieku; gotowe hasła działają u wszystkich | żadna mechanika nie może wymagać czatu |
| Panel analityki od ponad 10 DAU przez 7 dni, porównania od 100 DAU; A/B sensowne od ok. 1000 graczy dziennie | wczesne decyzje na porównaniu kohort, nie na A/B |
| Reklamy nagradzane nie dla graczy poniżej 13 lat, od 2000 gości miesięcznie | nie w MVP |

Kierunki, które dziś nie wiążą, ale warto się na nie ubezpieczyć: projekt DFA z 11.11.2026 (zakaz płatnych losowań i pay-to-progress wobec nieletnich), projekt EU KIDS Act (zakaz zachęcania dzieci do gry o stałych porach) i kryteria PEGI od 06.2026.

## Sprawdzone liczby

| Liczba | Źródło (data) | Pewność |
|---|---|---|
| Wiek sprawdzonych graczy: < 13 lat 34%, 13–17 37%, 18+ 29% | list do akcjonariuszy Q3 2026 (29.10.2026) | wysoka |
| DAU 138 mln (−9% r/r), płacący 30 mln (−16% r/r) | jw. | wysoka |
| Roblox zakłada sezonowy spadek DAU między Q3 a Q4 i dużą część wydatków w ostatnim tygodniu grudnia | jw. | wysoka |
| Wolumen gier robionych z AI rośnie o ponad 50% kwartał do kwartału | jw. | wysoka (deklaracja spółki) |
| ok. 40% tygodniowego top 100 to gry młodsze niż 3 miesiące | jw. | wysoka (deklaracja spółki) |
| Retencja: mediana D1 / D7 / D30 = 10,3 / 1,6 / 0,5%; górny 1%: 22,2 / 9,1 / 4,7% | gameanalytics.com, raport 2026 (01.09.2026) | średnia |
| Mediana sesji 9,8 min (p90 14,7) | jw. | średnia |
| Do odróżnienia D1 7% od 12% potrzeba ok. 240 nowych graczy | obliczenie weryfikatora (13.11.2026) | wysoka (arytmetyka) |
| Android to ok. 65% graczy typowej gry, ok. 60% z nich ma 2–4 GB RAM | create.roblox.com/docs/performance-optimization/test-on-hardware | wysoka |
| Koszt wejścia z reklamy: 0,007–0,011 $ (dane z końca 2025, sprzed bramki wieku) | naavik.co (01.03.2026) | średnia, nieaktualna |
| Fantazja „pokonany wróg walczy po twojej stronie”: ARISE CROSSOVER 3 719 graczy naraz wobec rekordu 334 189 (−98,9%); Catch a Monster 2 298; Evomon 2 178 z polowaniem na „Shiny” | games.roblox.com/v1/games (13.11.2026, migawka nocna) | wysoka |
| Hity też gasną: Bee Swarm −88%, Pet Simulator 99 −94% od szczytu | rolimons.com i API (13.11.2026) | średnia |
| Przerwane zadania ludzie wznawiają w 67% przypadków, ale ich nie pamiętają | Nature HSSC (01.07.2025) | wysoka (laboratorium) |
| Wymuszone czekanie na starcie gry: ≥ 5,8 s | repozytorium, skrypt ekranu ładowania | wysoka |

## Niewiadome

- Normy wejść po zobaczeniu gry i odbicia: Roblox pokazuje tylko percentyle w panelu.
- Koszt zdobycia 250 „mocno zaangażowanych” i koszt wejścia z reklamy dla gry w okresie próbnym.
- Udział sprawdzonych 16+ w DAU (szacunek 25–30% to hipoteza).
- Ile godzin tygodniowo zespół naprawdę ma. To kluczowa liczba dla wykonalności.
- Wydajność na telefonie z 2–4 GB RAM.
- Jak moderacja oceni karczmę fantasy bez alkoholu.
- Kolizje tytułów i zasięg znaku gry-inspiracji (to nie jest opinia prawna).
- Wpływ świąt na D1 i D7 nowych gier.
- Zasady Moments (kanał wideo Roblox) dla gier spoza własnego narzędzia platformy.

## Co z tego wynika

Dziesiątki nie da się zaprojektować na papierze. Da się usunąć dziesięć przyczyn i z góry zapisać progi, które ją potwierdzą albo obalą. Po nocy powstał projekt v2, który przeszedł przez trzech sceptyków (gracz, rynek, produkcja). Ich poprawki są w [[Systemy gry v2]], a uczciwa ocena po korekcie to ok. **6/10 z minimum 5**, opisana w [[Karta ocen v2 i plan sprawdzenia]].

## Powiązane
[[Myśl przewodnia v2]] · [[Systemy gry v2]] · [[Psychologia gracza v2]] · [[Karta ocen v2 i plan sprawdzenia]] · [[Ocena potencjału gry]] · [[Rynek Roblox i konkurencja]] · [[Retencja i monetyzacja — co wolno i co działa]] · [[Rejestr decyzji]] · [[Pytania otwarte]]
