---
status: propozycja
tags: [wytwórnia, lekcje]
---
# Lekcje z prototypów

Co wiemy z własnych prób. Każdy wpis: data, gra, co się stało, wniosek, kto miał rację.

## 2026-11-20 · BONK — Karol zagrał kilka minut (prywatna wersja testowa)
**Co się stało (słowa Karola, skrót):** „Gra wygląda dobrze, ale to nie jest to. Znudziła mi się po paru minutach. Jajka są bez sensu — nie czuję value. Linie potworów bez sensu: mogę bić slime albo muchomorka, a muchomorek daje więcej, to po co slime. Brakuje bossów, głębi, haka, ciekawości, co się stanie dalej. Gra ma być prosta i logiczna od pierwszego kliknięcia — to jest — ale brakuje kontynuacji.”

**Wniosek agenta (krytycznie, także wobec siebie):**
- Karta oceny przewidziała to samo: BONK ma mocne „pierwsze 10 sekund” i „jedno zdanie”, ale **hak ciekawości 1/3 i głębię 1/3**. Zbudowaliśmy pętlę „liczba rośnie”, w której nic nie jest nieznane — kolejny krok zawsze wiadomo z góry.
- **Pet działa tylko jako niewidoczny mnożnik** — nagroda nie jest odczuwalna, bo nic się nie zmienia w tym, co gracz robi i widzi.
- **Zagrody tworzą strategię zdominowaną:** opłaca się bić tylko najlepszą dostępną zagrodę, więc słabsze potwory są dekoracją. Różnorodność potworów nie daje decyzji.
- **Strażnik to worek z życiem** bez zapowiedzi i mechaniki — brak oczekiwania („za 2 minuty boss!”) i brak umiejętności w walce.
- Uczciwie: Karol grał sam w Studio (bez innych graczy) i nie jest graczem docelowym — samotna próba zaniża warstwę społeczną. Ale nawet z innymi graczami brak haka by został.
- **Lekcja ogólna:** prostota i hak to nie przeciwieństwa. Prosta czynność musi prowadzić do **wyniku, którego nie znasz z góry** (losowanie, rzadki wariant, cel do trafienia, coś, co zrobi inny gracz). Każda nowa rzecz musi zmieniać to, co gracz robi lub widzi, a nie tylko liczbę.

## 2026-11-20 · BONK porzucony (D-117) — co z niego zabieramy
Karol: „To nie tak, że spędzony czas i tokeny na BONK-a i Blocky & Crycket były stracone.”
- **Warsztat, który działa i zostaje:** samowystarczalny pakiet gry budowany skryptem w pustym miejscu (ok. 15 minut od zera do grywalnej wersji), liczby w jednym pliku, serwer liczy a klient rysuje (60 klatek na sekundę z tysiącami brył), testy logiki bez Studio i próba w Play ze zrzutami, zapis z ochroną prób, ikona i miniatury z Higgsfield z napisami dodanymi u nas, prywatna publikacja i zaproszenie testera, demo wideo ze skryptu.
- **Zasoby, które przechodzą dalej:** 12 potworów, 15 petów, trzy jajka i scena wyklucia, Strażnicy, lot i komiksowe nokauty, Księga, okna na telefon i pad.
- **Czego nie powtarzamy:** pętli „liczba rośnie” bez niewiadomej, nagród-mnożników, których nie widać, opcji zdominowanych, bossa bez zapowiedzi i mechaniki, budowy trzech etapów przed pierwszym graniem człowieka.
- **Zmiana w sposobie pracy:** najpierw rdzeń do zagrania w kilka godzin, człowiek gra, dopiero potem warstwy.

## 2026-11-21 · Pet Arena / Throw & Catch Monsters — Karol zagrał na telefonie
**Co się stało (słowa Karola):** „Gra jest bardzo mało wciągająca. Cały czas dzieje się to samo praktycznie. Zero dynamiki. Ta gra to chyba nie ten pomysł.” To spełnia warunek wyjścia zapisany w projekcie (ludzie przestają rzucać po kilku minutach).

**Wniosek agenta (także wobec siebie):**
- **Trzy gry, ten sam błąd:** w B&C walka toczy się sama, w BONK stukasz i rośnie liczba, w Pet Arenie rzucasz i czekasz. **Sama czynność gracza przez 10 sekund nie bawi** — a jajka, łapanie, wydarzenia i koloseum to warstwy dokładane wokół nudnego środka. Żadna warstwa tego nie naprawi.
- **Karta oceny zawiodła dwa razy** (28/30, potem 21/30, a w ręku nuda): mierzy cechy na papierze, nie frajdę z czynności. Oceny agenta były zgadywaniem.
- **Sposób pracy był za drogi na szukanie:** jedna noc i ok. 1,2 mln tokenów na całą grę, zanim człowiek dotknął środka gry.
- **Zmiana (propozycja):** najpierw **zabawka** — sama czynność, bez jajek, złota, zapisu i ekranów, do zagrania na telefonie w dwie minuty. Kilka zabawek naraz, człowiek wybiera tę, przy której chce „jeszcze raz”. Dopiero wokół wybranej budujemy grę. Karta dostaje bramkę „próba zabawki”.
- **Co zostaje z Pet Areny:** rzut, sterowanie potworem z przewidywaniem ruchu, zderzenia i wybicia, wielkości według wagi, koloseum, wyklucie i scena złapania, zegar wydarzeń, wylęgarnia, pełna droga budowa → próba → prywatna publikacja (z nauczką o trybie publikacji).

## Powiązane
- [[00 Wytwórnia pomysłów]] · [[BONK]] · [[Karta oceny pomysłu]]
