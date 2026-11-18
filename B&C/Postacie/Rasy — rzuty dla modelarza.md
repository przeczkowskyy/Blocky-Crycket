---
status: propozycja
tags: [postacie, rasy, rzuty, modele]
źródło: "polecenie Pawła 2026-11-17 (rzuty ras dla Karola do modeli); rasy z D-079, Półbóg z D-080"
---
# Rasy — rzuty dla modelarza

> [!info] W skrócie
> Rzuty (rysunki referencyjne) ras postaci w stylu Glossy Ink, **dla Karola do zrobienia modeli** (D-079, D-080, zadanie z propozycji D-104). Każda rasa w czterech widokach: przód, trzy czwarte, bok (profil w prawo), tył. Postacie są w bazowym stroju z D-071: jasna lniana koszula z krótkim rękawem, kolorowe spodenki, brązowe buty, bez zbroi i broni. Proporcje kanciaste jak Rycerz (R15). **Człowieka nie ma** — Paweł 17.11: model człowieka już jest (ciało bazowe Rycerza/Zwiadowcy).

## Pliki
| Rasa | Rzut | Cechy wyglądu |
|---|---|---|
| Demon | `assets/processed/RaceTurnarounds/demon.jpg` | czerwona skóra, małe czarne rogi, ogon z grotem, złote oczy, kieł; czarne spodenki |
| Elf | `assets/processed/RaceTurnarounds/elf.jpg` | jasna skóra, długie spiczaste uszy, długie złote włosy, zielone oczy; jasnozielone spodenki |
| Mroczny elf | `assets/processed/RaceTurnarounds/mroczny_elf.jpg` | lawendowo-szara skóra, spiczaste uszy, długie srebrne włosy, fioletowe oczy; fioletowe spodenki |
| Ork | `assets/processed/RaceTurnarounds/ork.jpg` | oliwkowa skóra, dwa kły, czarny kok, grube brwi, masywny; spodenki wyszły kolorowe (w prompcie brązowe) |
| Goblin | `assets/processed/RaceTurnarounds/goblin.jpg` | żółtozielona skóra, wielkie uszy, długi nos, szeroki uśmiech; pomarańczowe spodenki |
| Goblin (wariant 2) | `assets/processed/RaceTurnarounds/goblin_wariant2.jpg` | ten sam goblin z drugiej generacji (z linią podłoża) — przesłał Paweł; Karol wybiera, który bliższy |
| Półbóg | `assets/processed/RaceTurnarounds/polbog.jpg` | złota skóra z poświatą, aureola nad głową, jasne falowane włosy, świecące niebieskie oczy; białe spodenki ze złotą lamówką (arkusz ma ozdobną ramkę — generator) |

- Pliki JPG 2400 px; oryginały 5504 × 3072 lokalnie u Pawła w `assets/raw/RaceTurnarounds/` (folder `raw` nie trafia do gita) — na prośbę można je przesłać.
- Higgsfield, Nano Banana 2.1, 16:9, 4k, po jednej kopii; części stałe promptu z [[Instrukcja promptów — Glossy Ink]], środek: arkusz rzutów dla modelarza (A-poza, te same wymiary, wspólna linia stóp). Przycięcie i pomniejszenie: `tools/raceselect_assets.py`.
- Ikony ras do ekranu wyboru (te same twarze): `assets/processed/RaceSelect/Race<Id>.png` — zob. [[Selektor bohatera]].

## Stan modeli (18.11.2026)
- Modele robi agent Karola (D-104). **Pilotaż: elf i ork** zbudowane w Blenderze na ciele człowieka (te same klocki, kości i klipy co Rycerz i Zwiadowca), w stroju bazowym z rzutów; każdy przedmiot człowieka pasuje. To propozycja do oceny — raport w panelu „Modele ras z rzutów Pawła: elf i ork do oceny (pilotaż)”.
- **Komplet (18.11, 13:25):** demon, mroczny elf, goblin (pierwszy rzut) i Półbóg zbudowane na tym samym założeniu; włosy elfa oraz kok i uszy orka poprawione po pilotażu. Plansza zbiorcza: `swiat/postacie/wynik/_rasy/rasy_razem.jpg`; raport w panelu „Sześć ras z rzutów Pawła: komplet modeli do oceny”. Następne: wystawa ras w Studio; podpięcie do gry po odpowiedziach na pytania 67 i 68.
- Kod i opis: `swiat/postacie/rasy.py`, `swiat/postacie/RASY.md`; wyniki: `swiat/postacie/wynik/rasa_<id>/`.
- Pytania do ludzi w [[Pytania otwarte]]: 67 (proporcje ras), 68 (rasa a klasa Mag), 69 (drobne wybory wyglądu).

## Do ustalenia
- (Pytanie 67 w [[Pytania otwarte]].) Czy rasy mają tylko inną głowę, skórę i dodatki (rogi, uszy, ogon, kły) na tym samym ciele R15, czy własne proporcje (ork szerszy, goblin niższy) — wpływa na ekwipunek z D-071 (przedmiot pasuje do typu ciała).
- Wygląd Półboga zależy od rozstrzygnięcia D-080 (pytanie 47: mocniejsza rasa za Robuxy czy tylko inny wygląd).

## Powiązane
- [[Selektor bohatera]] · [[Rejestr decyzji]] (D-071, D-079, D-080) · [[Zadania]] · [[00 Start]]
