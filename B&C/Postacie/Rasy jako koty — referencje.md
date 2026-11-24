---
status: propozycja
tags: [postacie, rasy, kot-mag, modele]
źródło: "polecenia Pawła 2026-11-23/24 w Claude Code (kot-demon v2 zatwierdzony przez Pawła; reszta ras do akceptacji)"
---
# Rasy jako koty — referencje

> [!info] W skrócie
> - Paweł 23.11: każda rasa to **nasz Kot-Mag** z tym samym modelem — te same wymiary, sylwetka, kapelusz, szata w kształcie dzwonu, kostur i poza. Zmienia się tylko wygląd zewnętrzny: kolory futra i stroju, twarz i drobne cechy rasy. Rasy z planszy `swiat/postacie/wynik/_rasy/rasy_razem.jpg` (D-104) służą tylko jako wzór kolorów i twarzy, **nie** jako budowa ciała (bez ludzika Roblox z kocią głową).
> - Wiąże się z D-143 (gracz chodzi modelem rasy). Modele 3D to obszar Karola (D-093) — przed budową reszty ras dogadać z Karolem, kto je robi.

## Uwagi dla tego, kto robi modele (obowiązkowe)
- **Elf i mroczny elf: tylko JEDNA para uszu** (Paweł 24.11). Na obrazkach referencyjnych mają kocie uszy i dodatkowo długie uszy elfa — to błąd generatora. W modelu zostają zwykłe dwa kocie uszy z Kota-Maga; o rasie świadczy kolor (futro, oczy, włosy, strój), nie dodatkowe uszy. To samo dotyczy **goblina** (na referencji ma jedno wielkie ucho goblina obok kociego — uwaga agenta 24.11, w duchu prośby Pawła): dwa kocie uszy, ewentualnie trochę większe.
- Wymiary, kości i klipy zawsze z `swiat/postacie/kot_mag.py` (wariant = nowy plik, który wczytuje Kota-Maga i zmienia paletę oraz dodaje cechy; pliku Karola nie zmieniamy).
- Dwie wersje każdej rasy (Paweł 23.11): w pełnym stroju jak na referencji i w stroju podstawowym (koszulka i spodenki, bez przedmiotów).

## Koty klas w selektorze (24.11)
Koci Rycerz i Koci Zwiadowca — stroje Rycerza i Zwiadowcy Karola przerobione na kości Kota-Maga (`swiat/postacie/kot_klasy.py`, propozycja; plików Karola nie zmieniamy). W selektorze klas zamiast ludzików; broń startowa w łapce z `Weapon_<klasa>_Kot`.

## Referencje (Higgsfield, Nano Banana 2.1, po jednej wersji; pliki w `assets/raw/RasyKoty/`, poza repozytorium)
| Rasa | Plik | Stan |
|---|---|---|
| Człowiek | sam Kot-Mag (`swiat/postacie/wynik/kot_mag/kot_mag_bohater.jpg`) | baza; w wyborze rasy rudy kot w koszulce i niebieskich spodenkach (`kot_demon.czlowiek_podstawowy()`, `Race_Human`) |
| Demon | `kot_demon.png` (wersja 2; czerwone futro, czarne rogi przez rondo, żółte oczy, kieł, ogon ze szpicem, czarna szata z czerwonym obszyciem, kostur z płomieniem) | **zatwierdzony przez Pawła 23.11** — zbudowany 24.11 (`swiat/postacie/kot_demon.py`: pełny strój i podstawowy, klipy Kota-Maga), w Studio `Workspace/KotDemonPodglad`, w wyborze rasy jako `Race_Demon` |
| Elf | `kot_elf.png` | do akceptacji (uszy — patrz uwaga wyżej) |
| Mroczny elf | `kot_mroczny_elf.png` (wygenerowany 24.11 osobno — pierwsze zlecenie odrzucił limit 4 zadań naraz) | do akceptacji (uszy — patrz uwaga wyżej) |
| Ork | `kot_ork.png` | do akceptacji |
| Goblin | `kot_goblin.png` | do akceptacji (uszy — patrz uwaga wyżej) |
| Półbóg | `kot_polbog.png` | do akceptacji |

Plansza zbiorcza: `assets/raw/RasyKoty/koty_rasy_plansza.jpg`. Koszt: 7 obrazków × 2 kredyty (demon w dwóch podejściach).
