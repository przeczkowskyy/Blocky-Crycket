---
status: propozycja
tags: [gra, przedmioty, rzadkość, łup, balans]
źródło: "rozmowa Pawła z Claude Code 2026-11-24 wieczorem (liczba statystyk na rzadkość, sekretne przedmioty, lepszy łup z bossów — Paweł); liczby robocze agenta"
---
# Rzadkość przedmiotów — zwykłe, epickie, legendarne, sekretne (propozycja)

> [!info] W skrócie
> - Paweł 24.11: dzisiejsze przedmioty z puli to **zwykłe**; do tego szansa na **epickie**, **legendarne** i **sekretne**.
> - Zwykły daje premię do **1, najwyżej 2 statystyk**; epicki **do 3** i z większą premią; legendarny **do wszystkich**.
> - Mini-boss i boss lochu ([[Katakumby — pierwszy loch (propozycja)]]) mają wyraźnie lepsze szanse niż zwykłe potwory.
> - Rozwija [[Rejestr decyzji#D-142 Przedmioty: zwykłe w pulach według poziomu, rzadkie z szansą na każdym poziomie|D-142]] i zastępuje tabelę rzadkości w [[Przedmioty — zestawy v1]]. Liczby niżej są robocze — dobierze je kalkulator balansu (`tools/walka/balans.py`).

## Budżet statystyk
Każdy przedmiot ma **budżet statystyk** zależny od poziomu (puli). Rzadkość mnoży budżet i mówi, na ile statystyk się on dzieli. Statystyki: Siła, Kondycja, Inteligencja, Zręczność, Szczęście, Pancerz.

| Rzadkość | Kolor | Statystyki | Mnożnik budżetu | Ekstra |
|---|---|---|---|---|
| Zwykły | szary | 1–2 | ×1,0 | — |
| Epicki | fioletowy, iskry | 3 | ×1,4 | — |
| Legendarny | złoty, poświata | wszystkie 6 | ×1,8 | jedna pasywka (D-088), własna zabawna nazwa |
| Sekretny | tęczowy / czarno-złoty | stały zestaw | ok. ×1,8 | unikatowy, śmieszny efekt; znaleziony, nie wylosowany |

Co z tego wychodzi (przykład budżetu 100): zwykły z 1 statystyką daje 100 do niej, z 2 — po 50; epicki po ok. 47 do trzech; legendarny razem 180, ale **połowa trafia w główną statystykę klasy** (Siła / Zręczność / Inteligencja), reszta rozłożona na pięć pozostałych (po ok. 18).

**Uwaga agenta (D-114) — zgoda z poprawką:** samo „legendarny do wszystkich statystyk po równo” daje przedmiot, który jest najlepszy dla każdej klasy, a Mag marnuje budżet w Sile. Dlatego połowa idzie w główną statystykę klasy i legendarny ma pasywkę — wtedy legenda jest naprawdę „wow”, ale nie zabija buildów. Zmienię zdanie, jeśli kalkulator pokaże, że równy podział nie robi żadnej klasy za mocną.

- Statystyki rzadkiego przedmiotu liczą się od **poziomu gracza w chwili zdobycia** (jak w [[Przedmioty — zestawy v1]]), więc legenda z Lv 5 jest najlepsza w swojej puli, ale nie psuje gry na Lv 30. Limity z D-144 (krytyk, redukcja obrażeń) obowiązują też legendy.
- Tier **Rzadki** (niebieski) z [[Przedmioty — zestawy v1]] w tej wersji wypada — cztery stopnie są prostsze dla nowego gracza. Do decyzji (pytanie 96).

## Sekretne przedmioty
- Kilka na całą grę (np. 1 na loch i 1 na biom), każdy **stały** (zawsze te same statystyki i efekt), zdobywany przez **odkrycie**: ukryta krypta za pękniętą ścianą w Katakumbach, dziwna czynność w lesie, bardzo rzadki drop z bossa.
- Efekt śmieszny i widoczny, nie silniejszy od legendy (żeby nie był obowiązkowy), np. **Złota Ość** — broń, której krytyk wystrzeliwuje przeciwnika w powietrze; **Kłębek Wieczności** — raz na walkę przeciwnik traci turę, bawiąc się włóczką.
- Po co: sekrety to darmowy marketing („jak zdobyć sekretny przedmiot” na YouTube i TikToku) i powód do zwiedzania.

## Szanse (robocze)
| Źródło | Epicki | Legendarny | Sekretny |
|---|---|---|---|
| Potwór w strefie biomu | 1% | 0,05% | — |
| Zwykły przeciwnik Katakumb (#1–4, #6–9), powtórka | 3% | 0,2% | — |
| Mini-boss Sir Ogonek, powtórka | 12% | 1% | — |
| Szczurzy Król, powtórka | 20% | 3% | 0,1% (Korona z Kapsla to osobna nagroda za pierwsze przejście) |
| Pierwsze pokonanie mini-bossa / bossa | **gwarantowany epik** | — | — |

- **Licznik pecha** (opcja): po 50 powtórkach Szczurzego Króla bez legendy następna jest gwarantowana. Daje cel i chroni przed frustracją; kosztuje jedno pole w zapisie gracza.
- Łup z walk za darmo nie wymaga pokazywania szans; pokazanie ich w oknie bossa i tak buduje zaufanie. Gdyby rzadkie przedmioty miały być do kupienia za Robux w losowaniu, Roblox **wymaga** pokazania szans przed zakupem ([[Retencja i monetyzacja — co wolno i co działa]]).

## Ikony
Zwykłe mają ikony z puli. Epickie i legendarne: tańszy start to ta sama ikona z ramką i poświatą w kolorze rzadkości (ramki kolorów są już w oknie jajka); własne ikony najpierw dla legend i sekretów, których jest mało.

## Do ustalenia
- Pytanie 96 w [[Pytania otwarte]]: liczba statystyk na stopień, podział legendy, tier Rzadki, licznik pecha.

## Powiązane
- [[Przedmioty — pula Lv 1–10, 5 na slot (propozycja)]] · [[Przedmioty — zestawy v1]] · [[System RPG]] · [[Walka v2 — silnik, klasy i umiejętności]]
