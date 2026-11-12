---
status: kanon
tags: [hub, zasady]
---
# Jak prowadzimy sejf

## Statusy notatek (pole `status` w nagłówku)
| Status | Znaczenie |
|---|---|
| `kanon` | Zatwierdzone przez Ciebie, obowiązuje |
| `propozycja` | Pomysł Claude albo starszej specyfikacji, **nie jest faktem** |
| `do-decyzji` | Czeka na Twoją odpowiedź |

## Struktura
- **Gra/** mechaniki i koncepcja
- **Postacie/** bohaterowie, NPC, pety
- **Styl/** kierunek artystyczny i [[Style Lock]]
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
5. Nie zmienia statusu na `kanon` bez Twojej zgody.

## Ty
- Możesz pisać notatki dowolnie, Claude je przeczyta.
- Żeby coś stało się obowiązujące, ustaw `status: kanon` albo powiedz Claude „zatwierdzam”.
