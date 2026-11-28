---
status: propozycja
tags: [gra, loch, dungeon, przeciwnicy, progresja]
źródło: "rozmowa Pawła z Claude Code 2026-11-24 wieczorem (nazwa „katakumby” i ocena przeciwników — Paweł)"
---
# Katakumby — pierwszy loch (propozycja)

> [!info] W skrócie
> - Pierwszy loch gry: **Kocie Katakumby** (ang. *The Catacombs* — słowo „Cat” jest już w środku, gra słów za darmo). Nazwa „katakumby” — Paweł 24.11.
> - **10 przeciwników po kolei, bez przeskakiwania**, każdy jeden, ręcznie zrobiony, stoi jako model 3D w swojej komnacie; podejście + E = walka (jak w lesie). Paweł: „jest w miarę po porządku… nawet bardzo okej”.
> - Droga **liniowa z kratami**, nie otwarta mapa: krata do następnej komnaty otwiera się tylko temu graczowi, który wygrał (technika jak Wrota Bagna, D-042). Szczurzy Król widoczny przez kratę od samego wejścia.
> - Mini-boss (#5) i boss (#10) mają **lepszy łup** — większe szanse na przedmioty epickie, legendarne i sekretne: [[Rzadkość przedmiotów — zwykłe, epickie, legendarne, sekretne (propozycja)]].

## Dlaczego nie otwarta mapa
Otwarta mapa z potworami i E to już [[Biom Las]] (strefy, odradzanie, Strażnik na końcu). Loch musi być czymś innym, inaczej gracz nie poczuje, że wszedł w nowe miejsce:
1. **Każdy przeciwnik jeden i unikatowy**, nie odradzające się stado.
2. **Postęp zapisany**: pokonany zostaje „zaliczony”, licznik **4/10** widać w hali portali i w lochu.
3. **Liniowa droga z kratami** — jasny kierunek, mniej budowania, lżej na telefonie; nikt nie biegnie do bossa, żeby dostać „jeszcze zamknięte”.

## Jak wygląda (schodzimy w dół)
Wejście z rybimi ośćmi i świecami → krypty ze starymi kocimi sarkofagami → ossuarium z pajęczynami → zalany kanał → sala tronowa z puszek i kapsli. W każdej komnacie podest z jednym przeciwnikiem. Walka na arenie katakumb (D-095: arena zmienia się z miejscem).

## 10 przeciwników
Każdy sprawdza **inną rzecz w buildzie**, więc loch uczy systemu walki i statusów ([[Walka v2 — silnik, klasy i umiejętności]]).

| # | Przeciwnik | Poz. (robocze) | Co sprawdza |
|---|---|---|---|
| 1 | Mysz Podjadaczka | 5 | rozgrzewka, pierwsza wygrana |
| 2 | Karaluch Pancerny | 6 | dużo Pancerza — magia i krytyki mają przewagę |
| 3 | Pająk spod Sarkofagu | 7 | trucizna (nieblokowalna) — liczy się pula HP |
| 4 | Kret Kopacz | 8 | ogłuszenie (wyskakuje spod posadzki) |
| 5 | **Sir Ogonek, Szczurzy Giermek** (mini-boss) | 9 | tarcza z pokrywki od garnka, wysoki blok |
| 6 | Ćma Gromniczna | 10 | obrażenia magiczne — odporność z Inteligencji |
| 7 | Mysz Grabarka | 11 | łopatą zdziera pancerz |
| 8 | Gacek | 12 | bardzo wysoki unik — trzeba spowolnić |
| 9 | Szczur Kanalarz | 13 | podpalenie i dużo HP — test wytrzymałości |
| 10 | **Szczurzy Król** (boss) | 15 | korona z kapsla, tron z puszek; przy 50% HP wzywa szczury (tarcza na kilka tur) |

Nazwy #3, #6 i #7 lekko zmienione pod katakumby (wcześniej: Pająk spod Schodów, Ćma Lampowa, Mysz Kiszonkowa) — do odrzucenia, jeśli Paweł woli stare.

## Progresja i łup
- **Kłódka na 5. poziomie**, potem ok. +1 poziom na przeciwnika; #5 i #10 to **ściany** — gracz wraca na trening AFK (D-141), do sklepu i lasu, potem znów do lochu. To spina pętlę gry.
- **Bez kary czasowej** (D-107); przegrana kosztuje trochę Rybek (D-098, D-146).
- **Pierwsze pokonanie** każdego przeciwnika: gwarantowany przedmiot z puli Lv 1–10 ([[Przedmioty — pula Lv 1–10, 5 na slot (propozycja)]]) i Diamenty. Mini-boss przy pierwszym pokonaniu: gwarantowany epik. Szczurzy Król: gwarantowany epik + kosmetyczna **Korona z Kapsla** (do pokazania się innym).
- **Powtórki:** po zaliczeniu z każdym można walczyć dalej na mniejszy łup, z pomijaniem animacji (D-078); bossowie mają tu wyższe szanse na rzadkie przedmioty — tabela w notatce o rzadkości.

## Koszt
- 10 unikatowych modeli to duża praca 3D (obszar Karola, D-093). Oszczędność: 5 z 10 to gryzonie (mysz, giermek, grabarka, kanalarz, król) — **jeden szkielet, różne stroje**, jak rasy kotów. Osobne modele: karaluch, pająk, kret, ćma, gacek.
- Mapa wspólna dla serwera, kraty osobno dla gracza — taniej niż osobne serwery, inni widzą, jak walczysz.
- Układ „10 przeciwników po kolei” jest wzorem z [[Shakes & Fidget — rozbiór mechanik]]; mechanika jest ogólna, nazwy i wygląd nasze.

## Do ustalenia
- Pytanie 95 w [[Pytania otwarte]]: kto robi modele, wejście (Korzenna Gardziel w lesie czy hala portali z D-042), poziomy.

## Powiązane
- Następne lochy: [[Lochy 2 i 3 — Zatopiony Galeon i Psia Twierdza (propozycja)]]
- [[Biom Las]] · [[Koncepcja i Core Loop]] · [[Walka v2 — silnik, klasy i umiejętności]] · [[Rejestr decyzji]] (D-042, D-078, D-095, D-098, D-107)
