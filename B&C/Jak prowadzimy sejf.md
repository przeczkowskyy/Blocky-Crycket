---
status: kanon
tags: [hub, zasady]
---
# Jak prowadzimy sejf

## Statusy notatek (pole `status` w nagłówku)
| Status | Znaczenie |
|---|---|
| `kanon` | Zatwierdzone przez Karola albo Pawła, obowiązuje |
| `propozycja` | Pomysł Claude albo starszej specyfikacji, **nie jest faktem** |
| `do-decyzji` | Czeka na odpowiedź jednego z nas |

## Kto zatwierdza (D-030, 2026-11-13)
- Karol i Paweł mają takie same prawa. Wystarczy decyzja jednego. Zasadę przyjął Karol 13.11.2026; potwierdzenie Pawła czeka w [[Pytania otwarte]] #27, a do tego czasu Paweł może cofnąć decyzje zatwierdzone tylko przez Karola.
- Każda decyzja zostaje w logach: w [[Rejestr decyzji]] z podpisem `zdecydował: <imię> <data>` i w [[Dziennik zmian]].
- W [[Panel zespołu|panelu]] status decyzji zmienia osoba przy komputerze z panelem albo osoba z kluczem zatwierdzania. Wpis oznaczony „gość panelu” decyzją nie jest.
- Gdy się różnimy, spór trafia do [[Pytania otwarte]] i nic nie jest nadpisywane.
- Od 14.11.2026 (D-043, ustalone na pierwszej sesji głównej): jedna osoba podejmuje decyzję, a druga ją potwierdza — zgoda, brak zgody albo „przedyskutuj”. Decyzja z jednym podpisem to robocze ustalenie, które druga osoba może jeszcze cofnąć; w pełni obowiązuje po dwóch podpisach. Alert na Telegramie, którym panel będzie prosił o potwierdzenie, jest w budowie.

## Struktura
- **Gra/** mechaniki i koncepcja
- **Postacie/** bohaterowie, NPC, pety
- **Styl/** kierunek artystyczny i [[Instrukcja promptów — Glossy Ink]] (zastąpiła [[Style Lock]], D-027)
- **UI/** ekrany interfejsu
- **Technika/** Rojo, Figma, narzędzia
- **Produkcja/** [[Roadmapa]], [[Zadania]], [[Rejestr decyzji]], [[Pytania otwarte]], [[Dziennik zmian]]
- **Badania/** rozeznanie rynku, mechanik i narzędzi ze źródłami (zawsze `propozycja`, dopóki nie zapadnie decyzja)
- **Źródła/** oryginalne dokumenty (nie edytujemy ich, tylko cytujemy)
- **Szablony/** szablony nowych notatek (Obsidian: *Wstaw szablon*)

## Jak Claude korzysta z sejfu
1. **Przed pracą** czyta [[00 Start]] i notatki związane z zadaniem.
2. Traktuje `kanon` i zatwierdzone decyzje jako obowiązujące. Gdy coś się nie zgadza, pyta w [[Pytania otwarte]] i niczego nie nadpisuje po cichu.
3. **Po pracy:**
   - aktualizuje odpowiednie notatki (np. stan implementacji w [[HUD]]),
   - odhacza [[Zadania]],
   - dopisuje wpis do [[Dziennik zmian]].
4. Nowe pomysły zapisuje jako `propozycja` albo jako 💡 w [[Rejestr decyzji]]. Nigdy jako kanon.
5. Nie zmienia statusu na `kanon` bez wyraźnej zgody Karola albo Pawła, a przy zmianie zapisuje, kto i kiedy zdecydował.
6. Pytania i propozycje dla ludzi pisze krótko: tytuł do dziesięciu słów, potem dwa–cztery punkty (czego dotyczy, co jest do wyboru), a dłuższy kontekst niżej pod wierszem `Szczegóły:`. Jedno pytanie to jedna sprawa — zanim doda nowe, sprawdza, czy takie już jest. Gdy pytanie rozstrzyga decyzja, dopisuje wiersz `Rozstrzyga: D-0XX`.

## My (Karol i Paweł)
- Możemy pisać notatki dowolnie, Claude je przeczyta.
- Żeby coś stało się obowiązujące, ustaw `status: kanon`, zatwierdź decyzję w panelu albo powiedz Claude „zatwierdzam”.
