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
- Karol i Paweł mają takie same prawa. Wystarczy decyzja jednego.
- Każda decyzja zostaje w logach: w [[Rejestr decyzji]] z podpisem `zdecydował: <imię> <data>` i w [[Dziennik zmian]].
- W [[Panel zespołu|panelu]] status decyzji zmienia osoba przy komputerze z panelem albo osoba z kluczem zatwierdzania. Wpis oznaczony „gość panelu” decyzją nie jest.
- Gdy się różnimy, spór trafia do [[Pytania otwarte]] i nic nie jest nadpisywane.

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

## My (Karol i Paweł)
- Możemy pisać notatki dowolnie, Claude je przeczyta.
- Żeby coś stało się obowiązujące, ustaw `status: kanon`, zatwierdź decyzję w panelu albo powiedz Claude „zatwierdzam”.
