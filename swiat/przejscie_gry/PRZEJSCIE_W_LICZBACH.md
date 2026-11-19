# Przejście gry w liczbach — od 1. poziomu do bramy Pustyni

*Status: **propozycja** (rachunek, nie decyzja). Zlecenie: D-106. Liczone 19.11.2026 symulatorem, bez Roblox Studio.
Wynik każdej walki liczy prawdziwy silnik walki, a liczby gry są czytane z plików gry. Wnioski poniżej są pisane ręcznie
do liczb z 19.11 (ok. 8:50); tabele na dole symulator podmienia sam przy każdym uruchomieniu.*

## Najważniejsze

1. **Grę da się przejść każdą klasą i każdym sposobem gry** — na 100 graczy w każdej z 42 kombinacji do Strażnika
   Dżungli doszło 100.
2. **Trwa to ok. 1 godz. 20 min** przy zwykłej grze (walki, mini-gry, pety, kowal); 45 min, gdy gracz pomija walki
   i pcha do przodu; ok. 2 godz., gdy ogląda każdą walkę w całości.
3. **Gracz utyka na Strażniku Topieli i na Wężu Stu Lian.** Sam bohater na ich poziomie wygrywa 12–28% walk (ze
   Strażnikiem Gaju 35–43%). Kto tylko walczy, w 10–18% przypadków przegrywa z nimi pięć razy lub więcej;
   niecierpliwy — w 21–42%.
4. **Nudzi się pod koniec Dżungli i Bagna**: 28 walk z Kokosowym Siłaczem (9 minut, 20–24 walki z rzędu z jednym
   potworem) i 26 walk z Kłodokłapem (8 minut); potem jeszcze kilka–kilkanaście minut odbijania się od Strażnika.
5. **Najtrudniej ma Mag na Strażniku Topieli** (sam wygrywa 12% walk), choć całą grę kończy najszybciej;
   najwolniej idzie Wojownik (o 4–25 minut dłużej niż Mag). Żadna klasa nie jest wymagana.

## Ile to trwa

Minuty gry, mediana, świat po zmianie D-107. Dwie pierwsze kolumny to średnia z trzech klas, w ostatniej trzy liczby = Wojownik / Zwiadowca / Mag.

| Sposób gry | Strażnik Gaju | Strażnik Topieli | Wąż Stu Lian (koniec) |
|---|---:|---:|---:|
| Tylko walki, każda oglądana w całości | 26 | 73 | 133 / 128 / 108 |
| Tylko walki (nowe ogląda, znane przyspiesza albo pomija) | 17 | 45 | 79 / 76 / 69 |
| Walki + mini-gry (10 min na godzinę) | 17 | 47 | 80 / 82 / 74 |
| Walki + mini-gry + pety + kowal | 19 | 48 | 84 / 83 / 76 |
| To samo + sklep z przedmiotami | 19 | 48 | 82 / 82 / 78 |
| Ostrożny (czeka na zapas poziomu, więcej mini-gier) | 33 | 69 | 114 / 114 / 106 |
| Niecierpliwy (pomija walki, idzie na Strażnika o poziom za wcześnie) | 10 | 27 | 47 / 46 / 42 |

- Pierwsza wygrana: po ok. 45 sekundach (szczęście początkującego działa — pierwszą walkę wygrywa ponad 9 na 10 graczy).
- Co dziesiąty gracz kończy o 5–20 minut później niż mediana (rozrzut w tabelach na dole).
- Poziom przy bramach: 11–12 (Bagno), 17–19 (Dżungla), 23–25 (Pustynia). Walk razem: 150–190, przegranych 12–46
  (niecierpliwy 64).
- Las zajmuje ok. 19 minut, Bagno ok. 30, Dżungla ok. 33. Plan z `tools/walka/tempo.py` zakładał 30 / 45 / 60.

## Gdzie gracz utyka

Szansa wygranej samego bohatera (bez mini-gier, petów i przedmiotów) na poziomie Strażnika:

| Strażnik | Wojownik | Zwiadowca | Mag | Z dodatkami (średnio) |
|---|---:|---:|---:|---:|
| Strażnik Gaju (poz. 10) | 43% | 38% | 35% | 78% |
| Strażnik Topieli (poz. 16) | 14% | 20% | 12% | 39% |
| Wąż Stu Lian (poz. 23) | 19% | 28% | 22% | 42% |

- „Z dodatkami” = po 6 punktów z mini-gier w trzech głównych statystykach i pełny zestaw kowala ulepszony o 2.
- Nawet trzy poziomy ponad Strażnika sam bohater ma tylko 36–48% (Topiel) i 36–45% (Wąż).
- Nikt nie utyka na stałe: przegrana daje doświadczenie, więc po kilku próbach i paru walkach obok gracz przechodzi.
  Ale kosztuje to ok. 8 minut przy każdym z dwóch Strażników i 2–3 przegrane z rzędu.
- Z mini-grami, petami i kowalem problem prawie znika (utyka 0–4% graczy). Czyli dodatki nie są wymagane, ale
  bez nich dwa ostatnie Strażniki są wyraźnie za mocni w porównaniu ze Strażnikiem Gaju.

## Gdzie się nudzi

| Miejsce | Co się dzieje (tylko walki) |
|---|---|
| Dżungla, Kokosowy Siłacz (21–23) | 28 walk, 9 minut, najdłuższa seria jednego potwora w całej grze (20–24) |
| Bagno, Kłodokłap (14–16) | 26 walk, 8 minut |
| Strażnik Topieli i Wąż Stu Lian | po 8 minut i 3 próby na każdego; najdłuższy czas bez nowej zagrody: 12–23 minut |
| Bagno, Rechotek i Dżungla, Zwijogon | odwrotnie — gracz wchodzi o 2 poziomy za mocny i mija zagrodę w minutę |

- Najdłużej bez awansu: 6 minut (tylko walki), 10 minut (każda walka oglądana) — zawsze przy Kokosowym Siłaczu.
- Powód: potrzebne doświadczenie rośnie szybciej niż doświadczenie z potworów. Na 5. poziomie awans to ok. 4 walki,
  na 21. — ok. 11.
- W lesie żadna zagroda nie trwa dłużej niż 4–6 minut.

## Klasy

- Mag kończy najszybciej w każdym sposobie gry (jego walki są najkrótsze), Wojownik najwolniej. Różnica: 4–10 minut
  przy zwykłej grze, 25 minut, gdy każda walka jest oglądana w całości.
- Mag najczęściej utyka na Strażniku Topieli (tylko walki: 16–20% graczy; niecierpliwy: 42%).
- U kowala Mag ma 4 przedmioty, Wojownik i Zwiadowca po 7 — Mag ma mniej do ulepszania.

## Złoto

- Gracz zarabia 23–26 tys. Złota na całą grę.
- Pety i kowal zabierają ok. 14,5 tys. (9 jajek to 7,2 tys., reszta ulepszenia) — zostaje ok. 8 tys. bez celu.
- Ze sklepem (katalog `swiat/postacie/sklep_liczby.json`, propozycja innego agenta, wczytany sam) gracz wydaje
  ok. 19 tys. i zostaje mu ok. 4 tys. Czas przejścia się nie zmienia (81 minut), przegranych jest mniej (24 → 20).
- **Kara za przegraną zjada dużo Złota graczowi, który nie wydaje**: przy samych walkach ok. 6,9 tys. z 26 tys.
  (27%), u niecierpliwego 9,1 tys. z 21,6 tys. (42%). Przy takim zapasie Złota zawsze działa górny limit kary
  (łup zwykłego potwora), więc zmiana samych 5% nic nie da — trzeba by obniżyć limit.

## Przed zmianą i po zmianie D-107

W trakcie liczenia inny agent wpisał liczby D-107 do plików gry (w zagrodzie 4 potwory dla jednego gracza zamiast 2,
odrodzenie 4 s, rzadki potwór 20 s, brak czekania po walce). „Po zmianie” = pliki gry; „przed zmianą” = stan z 18.11
odtworzony w symulatorze.

| Sposób gry | Koniec przed | Koniec po | Czekanie przed | Czekanie po |
|---|---:|---:|---:|---:|
| Tylko walki | 76 min | 75 min | 2,8 min | 0 |
| Walki + mini-gry + pety + kowal | 84 min | 81 min | 1,8 min | 0 |
| Ostrożny | 120 min | 111 min | 1,7 min | 0 |
| Niecierpliwy | 48 min | 45 min | 2,5 min | 0 |

- Dla jednego gracza na serwerze zmiana usuwa 2–3 minuty czystego czekania i nic nie psuje.
- Jak zmiana działa przy wielu graczach naraz, symulator nie liczy (jeden gracz na serwerze).

## Rekomendacje (propozycje liczb)

Rachunek „przed / po” policzony symulatorem na kopii danych — plików gry nie zmieniałem.

1. **Strażnik Topieli i Wąż Stu Lian: życie −30%** (ostrożniej: −15%).
   - Tylko walki: utyka 13% / 14% graczy → 3% / 2% (przy −15%: 6% / 6%); prób 3 → 2; koniec 75 → 71 min.
   - Niecierpliwy: utyka 32% / 30% → 9% / 8%.
   - Przy grze ze wszystkimi dodatkami prawie bez zmian (81 → 80 min) — Strażnicy nie robią się za łatwi.
2. **Doświadczenie z potworów Dżungli +25%.**
   - Tylko walki: koniec 75 → 70 min, najdłużej bez awansu 6,0 → 5,3 min; ze wszystkim 81 → 77 min.
3. **Oba razem.**
   - Tylko walki 75 → 66 min, ze wszystkim 81 → 75 min, niecierpliwy 45 → 40 min; różnica między klasami 10 → 8 min.
4. **Kara za przegraną: obniżyć górny limit** (np. do połowy łupu zwykłego potwora), nie procent.
   - Nie zmienia czasu gry, więc bez rachunku „przed / po”; dziś to 27–42% zarobku gracza, który nie wydaje.
5. **Nie wydłużać gry krzywą doświadczenia.**
   - Krzywa +25%: koniec 75 → 91 min, ale utyka 17% / 20% i dłużej bez awansu (7,1 min).
   - Wykładnik 1,5 zamiast 1,6 skraca grę do 59 min — tylko gdy krótsza gra jest w porządku.
   - Dłuższa gra powinna przyjść z nowych zagród i krain, nie z większej liczby walk z tym samym potworem.

## Czego symulacja nie obejmuje i co przyjęła

- **Jeden gracz na serwerze.** Bez tłoku, kolejek do potworów i gry z innymi.
- **Gracz rozdaje punkty statystyk jak wzorzec klasy.** Kto rozda źle, będzie słabszy.
- **Zachowanie gracza to reguły**, nie człowiek: idzie dalej, gdy ma poziom zagrody; po dwóch przegranych cofa się;
  po przegranej ze Strażnikiem robi 3 walki obok i wraca. Wszystkie reguły są w jednym miejscu (`STYLE`).
- **Czasy przyjęte**: podejście do potwora 9 s, karta wyniku 3 s, pominięta walka 1,5 s, wyjście do miasteczka 40 s,
  jajko 25 s, runda mini-gry 45 + 3 + 6 s, celność w mini-grach 77% (zmierzona 17.11; ostrożny 85%, niecierpliwy 65%).
- **Pety**: gracz nosi najrzadszego, nie najlepszego dla klasy; bez ewolucji i shardów.
- **Sklep**: gracz kupuje najtańszą rzecz lepszą od noszonej; ulepszania kupionych rzeczy nie liczę.
- **Poza symulacją**: drzewko umiejętności, Gemy, Twierdza, zadania, stroje (tylko wygląd), zapis postępu, zabawa.
- **Pliki gry zmieniały się w trakcie** (D-107, katalog sklepu, mini-gry) — po każdej zmianie warto puścić ponownie.
- „Nuda” to tylko liczby zastępcze: czas bez awansu, czas bez nowej zagrody, seria jednego potwora.

## Jak puścić ponownie

```
python -B swiat/przejscie_gry/symulacja_przejscia.py                 # całość, ok. 2,5 min; podmienia tabele niżej
python -B swiat/przejscie_gry/symulacja_przejscia.py --jeden mag wszystko po_zmianie 7   # jeden gracz
python -B -m unittest discover -s swiat/przejscie_gry -p "test_symulacji.py"            # testy, kilka sekund
```

Pliki: `symulacja_przejscia.py` (symulator; założenia w `WARIANTY`, `CZAS`, `STYLE`, `TRYBY`, propozycje w
`PROPOZYCJE`), `test_symulacji.py`, `przejscie_w_liczbach.json` (wszystkie liczby: mediana i rozrzut 10%–90%).

## Tabele szczegółowe

<!-- TABELE:START -->

### Czasy do kamieni milowych — świat „przed zmianą (stan z 18.11)” (minuty gry, mediana)

| Sposób gry | Klasa | 1. wygrana | Strażnik: Las | Strażnik: Bagno | Strażnik: Dżungla | Koniec: 10%–90% graczy | Skończyło |
|---|---|---:|---:|---:|---:|---|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 0,7 | 27 | 77 | 129 | 112–148 | 100% |
| Tylko walki, każda oglądana w całości | Zwiadowca | 0,7 | 27 | 73 | 124 | 111–142 | 100% |
| Tylko walki, każda oglądana w całości | Mag | 0,7 | 25 | 68 | 108 | 96–119 | 100% |
| Tylko walki | Wojownik | 0,7 | 18 | 50 | 80 | 71–93 | 100% |
| Tylko walki | Zwiadowca | 0,8 | 19 | 49 | 78 | 72–91 | 100% |
| Tylko walki | Mag | 0,7 | 18 | 45 | 70 | 64–79 | 100% |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 0,7 | 17 | 49 | 85 | 78–99 | 100% |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 0,7 | 19 | 51 | 83 | 78–99 | 100% |
| Walki + mini-gry (10 min na godzinę) | Mag | 0,7 | 18 | 47 | 76 | 71–85 | 100% |
| Walki + mini-gry + pety + kowal | Wojownik | 0,7 | 20 | 51 | 87 | 82–96 | 100% |
| Walki + mini-gry + pety + kowal | Zwiadowca | 0,7 | 20 | 51 | 86 | 82–97 | 100% |
| Walki + mini-gry + pety + kowal | Mag | 0,7 | 18 | 48 | 80 | 76–84 | 100% |
| Wszystko + sklep z przedmiotami | Wojownik | 0,7 | 20 | 51 | 86 | 82–95 | 100% |
| Wszystko + sklep z przedmiotami | Zwiadowca | 0,8 | 20 | 52 | 86 | 82–95 | 100% |
| Wszystko + sklep z przedmiotami | Mag | 0,7 | 20 | 49 | 81 | 77–92 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 0,7 | 35 | 74 | 125 | 113–132 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 0,7 | 35 | 74 | 126 | 113–133 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 0,7 | 33 | 68 | 109 | 105–123 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 0,5 | 11 | 28 | 49 | 44–54 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 0,5 | 11 | 27 | 47 | 43–52 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 0,5 | 10 | 27 | 46 | 42–51 | 100% |

Brama otwiera się od razu po wygranej ze Strażnikiem; dojście do niej to kilka sekund (dokładne czasy bram są w pliku JSON, pola `brama_…`).

### Poziom, walki i Złoto — świat „przed zmianą (stan z 18.11)” (mediana)

| Sposób gry | Klasa | Poziom przy bramach | Walk | Przegranych | Złoto zarobione | Złoto wydane | Złoto stracone po przegranych | Punkty z mini-gier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 11 / 18 / 25 | 190 | 38 | 25548 | 0 | 5900 | 0 |
| Tylko walki, każda oglądana w całości | Zwiadowca | 11 / 18 / 25 | 190 | 40 | 24970 | 0 | 6186 | 0 |
| Tylko walki, każda oglądana w całości | Mag | 11 / 19 / 25 | 187 | 37 | 25050 | 0 | 5680 | 0 |
| Tylko walki | Wojownik | 11 / 18 / 25 | 189 | 38 | 25108 | 0 | 5905 | 0 |
| Tylko walki | Zwiadowca | 11 / 18 / 24 | 192 | 41 | 24501 | 0 | 6321 | 0 |
| Tylko walki | Mag | 11 / 19 / 24 | 183 | 35 | 24478 | 0 | 5314 | 0 |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 11 / 18 / 24 | 179 | 31 | 24362 | 0 | 4642 | 25 |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 12 / 18 / 24 | 181 | 33 | 23662 | 0 | 4984 | 22 |
| Walki + mini-gry (10 min na godzinę) | Mag | 12 / 18 / 24 | 178 | 31 | 24054 | 0 | 4488 | 21 |
| Walki + mini-gry + pety + kowal | Wojownik | 11 / 17 / 23 | 159 | 17 | 23406 | 15450 | 834 | 25 |
| Walki + mini-gry + pety + kowal | Zwiadowca | 11 / 17 / 23 | 162 | 20 | 23375 | 14800 | 1292 | 22 |
| Walki + mini-gry + pety + kowal | Mag | 11 / 17 / 24 | 161 | 18 | 23712 | 14660 | 1004 | 21 |
| Wszystko + sklep z przedmiotami | Wojownik | 11 / 17 / 23 | 157 | 15 | 23410 | 19450 | 397 | 25 |
| Wszystko + sklep z przedmiotami | Zwiadowca | 11 / 17 / 23 | 159 | 17 | 23391 | 19025 | 541 | 22 |
| Wszystko + sklep z przedmiotami | Mag | 11 / 17 / 23 | 157 | 16 | 23476 | 20080 | 597 | 21 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 11 / 18 / 24 | 181 | 7 | 26396 | 22200 | 198 | 60 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 11 / 18 / 24 | 186 | 10 | 26401 | 22200 | 337 | 56 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 12 / 18 / 24 | 184 | 9 | 26584 | 22880 | 308 | 44 |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 11 / 17 / 24 | 176 | 57 | 20548 | 0 | 8250 | 0 |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 11 / 17 / 23 | 169 | 55 | 20147 | 0 | 7881 | 0 |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 11 / 17 / 24 | 168 | 52 | 20414 | 0 | 7562 | 0 |

### Strażnicy — świat „przed zmianą (stan z 18.11)”

Dla każdej krainy: poziom przy pierwszej próbie · prób do wygranej (mediana / co dziesiąty gracz) · ilu graczy utknęło (co najmniej 5 przegranych prób).

| Sposób gry | Klasa | Las | Bagno | Dżungla |
|---|---|---|---|---|
| Tylko walki, każda oglądana w całości | Wojownik | poz. 10 · 2 / 4 · 5% | poz. 16 · 4 / 7 · 22% | poz. 23 · 3 / 7 · 20% |
| Tylko walki, każda oglądana w całości | Zwiadowca | poz. 10 · 2 / 4 · 2% | poz. 16 · 3 / 7 · 19% | poz. 23 · 2 / 5 · 7% |
| Tylko walki, każda oglądana w całości | Mag | poz. 10 · 2 / 4 · 2% | poz. 16 · 4 / 7 · 24% | poz. 23 · 4 / 7 · 28% |
| Tylko walki | Wojownik | poz. 10 · 2 / 4 · 0% | poz. 16 · 4 / 7 · 24% | poz. 23 · 3 / 7 · 19% |
| Tylko walki | Zwiadowca | poz. 10 · 2 / 4 · 3% | poz. 16 · 3 / 6 · 19% | poz. 23 · 2 / 7 · 18% |
| Tylko walki | Mag | poz. 10 · 2 / 4 · 6% | poz. 16 · 4 / 7 · 29% | poz. 23 · 3 / 7 · 18% |
| Walki + mini-gry (10 min na godzinę) | Wojownik | poz. 10 · 2 / 4 · 1% | poz. 16 · 3 / 5 · 6% | poz. 23 · 3 / 6 · 13% |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | poz. 10 · 2 / 4 · 5% | poz. 16 · 3 / 5 · 8% | poz. 23 · 2 / 6 · 15% |
| Walki + mini-gry (10 min na godzinę) | Mag | poz. 10 · 2 / 4 · 1% | poz. 16 · 3 / 7 · 21% | poz. 23 · 3 / 6 · 15% |
| Walki + mini-gry + pety + kowal | Wojownik | poz. 10 · 1 / 3 · 0% | poz. 16 · 2 / 4 · 0% | poz. 23 · 1 / 3 · 1% |
| Walki + mini-gry + pety + kowal | Zwiadowca | poz. 10 · 1 / 3 · 0% | poz. 16 · 2 / 4 · 3% | poz. 23 · 1 / 3 · 0% |
| Walki + mini-gry + pety + kowal | Mag | poz. 10 · 1 / 3 · 0% | poz. 16 · 2 / 5 · 8% | poz. 23 · 2 / 3 · 2% |
| Wszystko + sklep z przedmiotami | Wojownik | poz. 10 · 1 / 3 · 0% | poz. 16 · 1 / 2 · 0% | poz. 23 · 1 / 3 · 0% |
| Wszystko + sklep z przedmiotami | Zwiadowca | poz. 10 · 1 / 3 · 0% | poz. 16 · 2 / 4 · 0% | poz. 23 · 1 / 3 · 1% |
| Wszystko + sklep z przedmiotami | Mag | poz. 10 · 2 / 4 · 0% | poz. 16 · 2 / 5 · 5% | poz. 23 · 1 / 3 · 2% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | poz. 11 · 1 / 2 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | poz. 11 · 1 / 2 · 0% | poz. 17 · 1 / 3 · 0% | poz. 24 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | poz. 11 · 1 / 2 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 3 · 0% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | poz. 9 · 3 / 7 · 19% | poz. 15 · 5 / 11 · 43% | poz. 22 · 4 / 11 · 31% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | poz. 9 · 4 / 6 · 16% | poz. 15 · 4 / 8 · 37% | poz. 22 · 3 / 8 · 28% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | poz. 9 · 3 / 6 · 19% | poz. 15 · 6 / 11 · 50% | poz. 22 · 4 / 12 · 43% |

### Nuda i przestoje — świat „przed zmianą (stan z 18.11)” (mediana)

| Sposób gry | Klasa | Najdłużej bez awansu | Najdłużej bez nowej zagrody | Najdłuższa seria jednego potwora | Czekanie (odradzanie + blokada) |
|---|---|---|---|---|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 11 min (dzungla/o1) | 21 min (bagno/straznik) | 22 × Kokosowy Siłacz | 0,0 min |
| Tylko walki, każda oglądana w całości | Zwiadowca | 10 min (dzungla/o1) | 20 min (dzungla/o1) | 22 × Kokosowy Siłacz | 0,0 min |
| Tylko walki, każda oglądana w całości | Mag | 8,4 min (dzungla/o1) | 17 min (bagno/straznik) | 24 × Kokosowy Siłacz | 0,0 min |
| Tylko walki | Wojownik | 6,6 min (dzungla/o1) | 13 min (bagno/straznik) | 23 × Kokosowy Siłacz | 3,8 min |
| Tylko walki | Zwiadowca | 6,5 min (dzungla/o1) | 13 min (dzungla/o1) | 22 × Kokosowy Siłacz | 3,0 min |
| Tylko walki | Mag | 5,4 min (dzungla/o1) | 11 min (bagno/straznik) | 24 × Kokosowy Siłacz | 1,6 min |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 10 min (dzungla/z1) | 14 min (dzungla/g1) | 25 × Kokosowy Siłacz | 3,2 min |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 9,8 min (dzungla/g1) | 14 min (dzungla/g1) | 24 × Kokosowy Siłacz | 2,6 min |
| Walki + mini-gry (10 min na godzinę) | Mag | 9,4 min (dzungla/g1) | 14 min (dzungla/g1) | 24 × Kokosowy Siłacz | 1,4 min |
| Walki + mini-gry + pety + kowal | Wojownik | 10 min (dzungla/z1) | 13 min (bagno/b1) | 24 × Kokosowy Siłacz | 2,1 min |
| Walki + mini-gry + pety + kowal | Zwiadowca | 10 min (dzungla/z1) | 13 min (bagno/b1) | 24 × Kokosowy Siłacz | 2,0 min |
| Walki + mini-gry + pety + kowal | Mag | 9,9 min (dzungla/g1) | 13 min (dzungla/g1) | 24 × Kokosowy Siłacz | 1,2 min |
| Wszystko + sklep z przedmiotami | Wojownik | 10,0 min (dzungla/z1) | 12 min (dzungla/z1) | 23 × Kokosowy Siłacz | 2,0 min |
| Wszystko + sklep z przedmiotami | Zwiadowca | 10,0 min (dzungla/z1) | 12 min (bagno/b1) | 24 × Kokosowy Siłacz | 1,8 min |
| Wszystko + sklep z przedmiotami | Mag | 9,8 min (dzungla/g1) | 13 min (bagno/b1) | 24 × Kokosowy Siłacz | 1,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 14 min (bagno/k1) | 19 min (bagno/k1) | 24 × Kokosowy Siłacz | 2,2 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 14 min (bagno/k1) | 19 min (bagno/k1) | 23 × Zwijogon | 2,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 13 min (dzungla/g1) | 17 min (bagno/k1) | 24 × Zwijogon | 1,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 4,4 min (dzungla/o1) | 7,2 min (dzungla/o1) | 25 × Kokosowy Siłacz | 3,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 4,0 min (dzungla/o1) | 7,2 min (dzungla/o1) | 26 × Kokosowy Siłacz | 2,6 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 3,8 min (dzungla/o1) | 7,2 min (dzungla/o1) | 25 × Kokosowy Siłacz | 1,9 min |

### Czasy do kamieni milowych — świat „po zmianie D-107 (pliki gry)” (minuty gry, mediana)

| Sposób gry | Klasa | 1. wygrana | Strażnik: Las | Strażnik: Bagno | Strażnik: Dżungla | Koniec: 10%–90% graczy | Skończyło |
|---|---|---:|---:|---:|---:|---|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 0,7 | 26 | 80 | 133 | 119–155 | 100% |
| Tylko walki, każda oglądana w całości | Zwiadowca | 0,7 | 28 | 74 | 128 | 109–150 | 100% |
| Tylko walki, każda oglądana w całości | Mag | 0,7 | 23 | 66 | 108 | 94–124 | 100% |
| Tylko walki | Wojownik | 0,8 | 18 | 47 | 79 | 69–89 | 100% |
| Tylko walki | Zwiadowca | 0,8 | 18 | 45 | 76 | 67–86 | 100% |
| Tylko walki | Mag | 0,7 | 16 | 43 | 69 | 59–77 | 100% |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 0,7 | 18 | 48 | 80 | 75–94 | 100% |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 0,7 | 17 | 47 | 82 | 74–96 | 100% |
| Walki + mini-gry (10 min na godzinę) | Mag | 0,7 | 16 | 45 | 74 | 68–84 | 100% |
| Walki + mini-gry + pety + kowal | Wojownik | 0,7 | 19 | 50 | 84 | 79–94 | 100% |
| Walki + mini-gry + pety + kowal | Zwiadowca | 0,7 | 20 | 50 | 83 | 78–95 | 100% |
| Walki + mini-gry + pety + kowal | Mag | 0,7 | 17 | 45 | 76 | 72–81 | 100% |
| Wszystko + sklep z przedmiotami | Wojownik | 0,8 | 20 | 49 | 82 | 77–92 | 100% |
| Wszystko + sklep z przedmiotami | Zwiadowca | 0,8 | 20 | 49 | 82 | 77–87 | 100% |
| Wszystko + sklep z przedmiotami | Mag | 0,7 | 19 | 46 | 78 | 74–82 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 0,7 | 33 | 71 | 114 | 108–127 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 0,7 | 33 | 71 | 114 | 109–127 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 0,7 | 31 | 65 | 106 | 100–110 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 0,6 | 10 | 28 | 47 | 42–52 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 0,5 | 11 | 26 | 46 | 41–52 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 0,5 | 9,8 | 26 | 42 | 38–49 | 100% |

Brama otwiera się od razu po wygranej ze Strażnikiem; dojście do niej to kilka sekund (dokładne czasy bram są w pliku JSON, pola `brama_…`).

### Poziom, walki i Złoto — świat „po zmianie D-107 (pliki gry)” (mediana)

| Sposób gry | Klasa | Poziom przy bramach | Walk | Przegranych | Złoto zarobione | Złoto wydane | Złoto stracone po przegranych | Punkty z mini-gier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 12 / 19 / 25 | 186 | 49 | 26038 | 0 | 7440 | 0 |
| Tylko walki, każda oglądana w całości | Zwiadowca | 12 / 18 / 25 | 186 | 47 | 26364 | 0 | 7276 | 0 |
| Tylko walki, każda oglądana w całości | Mag | 12 / 19 / 25 | 175 | 42 | 26318 | 0 | 6080 | 0 |
| Tylko walki | Wojownik | 12 / 19 / 25 | 188 | 49 | 26470 | 0 | 7458 | 0 |
| Tylko walki | Zwiadowca | 12 / 18 / 25 | 186 | 47 | 26160 | 0 | 7118 | 0 |
| Tylko walki | Mag | 12 / 19 / 25 | 179 | 42 | 25790 | 0 | 6260 | 0 |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 12 / 18 / 24 | 170 | 38 | 24304 | 0 | 5294 | 25 |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 11 / 18 / 25 | 178 | 43 | 25254 | 0 | 6224 | 22 |
| Walki + mini-gry (10 min na godzinę) | Mag | 11 / 19 / 24 | 171 | 38 | 24472 | 0 | 5398 | 21 |
| Walki + mini-gry + pety + kowal | Wojownik | 11 / 17 / 23 | 153 | 24 | 23338 | 14675 | 1326 | 24 |
| Walki + mini-gry + pety + kowal | Zwiadowca | 11 / 17 / 24 | 157 | 26 | 24055 | 14150 | 1676 | 22 |
| Walki + mini-gry + pety + kowal | Mag | 11 / 17 / 24 | 150 | 21 | 23824 | 14660 | 1316 | 21 |
| Wszystko + sklep z przedmiotami | Wojownik | 11 / 17 / 23 | 148 | 19 | 23430 | 18950 | 552 | 24 |
| Wszystko + sklep z przedmiotami | Zwiadowca | 11 / 17 / 23 | 151 | 21 | 23499 | 18700 | 702 | 22 |
| Wszystko + sklep z przedmiotami | Mag | 11 / 17 / 24 | 150 | 20 | 23730 | 20058 | 714 | 21 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 12 / 18 / 24 | 174 | 10 | 26457 | 21550 | 325 | 50 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 12 / 18 / 24 | 177 | 14 | 26456 | 20900 | 465 | 48 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 12 / 18 / 24 | 173 | 12 | 26358 | 21740 | 430 | 45 |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 11 / 18 / 24 | 171 | 67 | 21788 | 0 | 9691 | 0 |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 11 / 18 / 24 | 170 | 66 | 21819 | 0 | 9410 | 0 |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 11 / 18 / 24 | 156 | 58 | 21288 | 0 | 8112 | 0 |

### Strażnicy — świat „po zmianie D-107 (pliki gry)”

Dla każdej krainy: poziom przy pierwszej próbie · prób do wygranej (mediana / co dziesiąty gracz) · ilu graczy utknęło (co najmniej 5 przegranych prób).

| Sposób gry | Klasa | Las | Bagno | Dżungla |
|---|---|---|---|---|
| Tylko walki, każda oglądana w całości | Wojownik | poz. 10 · 2 / 3 · 0% | poz. 16 · 3 / 5 · 8% | poz. 23 · 2 / 6 · 15% |
| Tylko walki, każda oglądana w całości | Zwiadowca | poz. 10 · 2 / 4 · 0% | poz. 16 · 2 / 4 · 6% | poz. 23 · 3 / 6 · 12% |
| Tylko walki, każda oglądana w całości | Mag | poz. 10 · 2 / 3 · 0% | poz. 16 · 3 / 6 · 20% | poz. 23 · 3 / 7 · 16% |
| Tylko walki | Wojownik | poz. 10 · 2 / 4 · 0% | poz. 16 · 3 / 5 · 10% | poz. 23 · 3 / 6 · 13% |
| Tylko walki | Zwiadowca | poz. 10 · 2 / 4 · 1% | poz. 16 · 3 / 6 · 12% | poz. 23 · 3 / 5 · 10% |
| Tylko walki | Mag | poz. 10 · 2 / 4 · 0% | poz. 16 · 3 / 6 · 16% | poz. 23 · 3 / 6 · 18% |
| Walki + mini-gry (10 min na godzinę) | Wojownik | poz. 10 · 2 / 4 · 2% | poz. 16 · 3 / 5 · 6% | poz. 23 · 2 / 4 · 8% |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | poz. 10 · 2 / 4 · 1% | poz. 16 · 3 / 5 · 6% | poz. 23 · 2 / 5 · 8% |
| Walki + mini-gry (10 min na godzinę) | Mag | poz. 10 · 2 / 3 · 1% | poz. 16 · 3 / 7 · 13% | poz. 23 · 2 / 6 · 13% |
| Walki + mini-gry + pety + kowal | Wojownik | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 4 · 0% | poz. 23 · 1 / 4 · 0% |
| Walki + mini-gry + pety + kowal | Zwiadowca | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 4 · 0% | poz. 23 · 2 / 4 · 4% |
| Walki + mini-gry + pety + kowal | Mag | poz. 10 · 1 / 3 · 0% | poz. 16 · 2 / 4 · 2% | poz. 23 · 2 / 4 · 0% |
| Wszystko + sklep z przedmiotami | Wojownik | poz. 10 · 1 / 3 · 0% | poz. 16 · 2 / 3 · 0% | poz. 23 · 1 / 3 · 0% |
| Wszystko + sklep z przedmiotami | Zwiadowca | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 3 · 0% | poz. 23 · 1 / 3 · 0% |
| Wszystko + sklep z przedmiotami | Mag | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 4 · 3% | poz. 23 · 1 / 4 · 2% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | poz. 11 · 1 / 1 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | poz. 11 · 1 / 2 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | poz. 11 · 1 / 2 · 0% | poz. 17 · 2 / 3 · 1% | poz. 24 · 1 / 2 · 0% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | poz. 9 · 3 / 5 · 7% | poz. 15 · 4 / 9 · 34% | poz. 22 · 4 / 8 · 30% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | poz. 9 · 3 / 5 · 6% | poz. 15 · 4 / 7 · 21% | poz. 22 · 3 / 8 · 27% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | poz. 9 · 3 / 5 · 6% | poz. 15 · 5 / 9 · 42% | poz. 22 · 4 / 9 · 33% |

### Nuda i przestoje — świat „po zmianie D-107 (pliki gry)” (mediana)

| Sposób gry | Klasa | Najdłużej bez awansu | Najdłużej bez nowej zagrody | Najdłuższa seria jednego potwora | Czekanie (odradzanie + blokada) |
|---|---|---|---|---|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 11 min (dzungla/o1) | 23 min (dzungla/straznik) | 21 × Kokosowy Siłacz | 0,0 min |
| Tylko walki, każda oglądana w całości | Zwiadowca | 11 min (dzungla/o1) | 23 min (dzungla/straznik) | 19 × Gębokwiat | 0,0 min |
| Tylko walki, każda oglądana w całości | Mag | 8,6 min (dzungla/o1) | 21 min (bagno/straznik) | 22 × Kokosowy Siłacz | 0,0 min |
| Tylko walki | Wojownik | 6,5 min (dzungla/o1) | 14 min (dzungla/straznik) | 20 × Kokosowy Siłacz | 0,0 min |
| Tylko walki | Zwiadowca | 6,1 min (dzungla/o1) | 13 min (dzungla/straznik) | 18 × Kokosowy Siłacz | 0,0 min |
| Tylko walki | Mag | 5,3 min (dzungla/o1) | 12 min (bagno/straznik) | 22 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 9,8 min (dzungla/z1) | 15 min (dzungla/g1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 9,8 min (dzungla/z1) | 15 min (dzungla/g1) | 22 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry (10 min na godzinę) | Mag | 9,4 min (dzungla/o1) | 14 min (dzungla/o1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry + pety + kowal | Wojownik | 10 min (bagno/b1) | 13 min (bagno/b1) | 23 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry + pety + kowal | Zwiadowca | 10 min (bagno/b1) | 13 min (bagno/b1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry + pety + kowal | Mag | 9,3 min (dzungla/g1) | 13 min (dzungla/g1) | 23 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Wojownik | 9,8 min (bagno/b1) | 12 min (bagno/b1) | 23 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Zwiadowca | 9,8 min (bagno/b1) | 12 min (bagno/b1) | 23 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Mag | 9,6 min (dzungla/g1) | 13 min (dzungla/g1) | 23 × Kokosowy Siłacz | 0,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 14 min (dzungla/z1) | 18 min (bagno/k1) | 23 × Zwijogon | 0,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 14 min (dzungla/z1) | 19 min (bagno/k1) | 23 × Zwijogon | 0,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 13 min (dzungla/z1) | 17 min (dzungla/o1) | 23 × Kokosowy Siłacz | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 4,0 min (dzungla/o1) | 7,6 min (dzungla/straznik) | 24 × Kokosowy Siłacz | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 4,0 min (dzungla/o1) | 8,0 min (dzungla/o1) | 24 × Kokosowy Siłacz | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 3,7 min (dzungla/o1) | 7,3 min (bagno/straznik) | 24 × Kokosowy Siłacz | 0,0 min |

### Gdzie schodzi czas — „Tylko walki”, świat „po zmianie D-107 (pliki gry)” (mediana, średnio z klas)

Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.

| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |
|---|---|---:|---:|---:|---:|
| las/s1 | Leśny Slime (1–3) | 1 | 1,5 | 5 | 1,0 |
| las/m1 | Muchomornik (3–5) | 3 | 3,8 | 11 | 2,0 |
| las/w1 | Cierniowy Wilk (6–8) | 6 | 3,8 | 18 | 2,3 |
| las/t1 | Leśny Troll (8–9) | 8 | 4,0 | 6 | 2,0 |
| las/straznik | Strażnik Gaju (10–10) | 10 | 3,5 | 2 | 1,0 |
| bagno/r1 | Rechotek (10–12) | 12 | 0,9 | 10 | 2,0 |
| bagno/b1 | Bulgotnik (12–14) | 12 | 6,7 | 17 | 5,0 |
| bagno/k1 | Kłodokłap (14–16) | 14 | 8,2 | 26 | 5,0 |
| bagno/t1 | Ropucha z Chatką (16–16) | 16 | 1,2 | 7 | 3,3 |
| bagno/straznik | Strażnik Topieli (16–16) | 16 | 8,2 | 3 | 2,0 |
| dzungla/z1 | Zwijogon (17–19) | 19 | 0,9 | 10 | 2,0 |
| dzungla/g1 | Gębokwiat (19–21) | 19 | 6,8 | 22 | 4,8 |
| dzungla/o1 | Kokosowy Siłacz (21–23) | 21 | 9,2 | 28 | 5,8 |
| dzungla/t1 | Pancernik Ruin (23–23) | 23 | 1,8 | 7 | 2,3 |
| dzungla/straznik | Wąż Stu Lian (23–23) | 23 | 7,7 | 3 | 2,0 |

### Gdzie schodzi czas — „Walki + mini-gry + pety + kowal”, świat „po zmianie D-107 (pliki gry)” (mediana, średnio z klas)

Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.

| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |
|---|---|---:|---:|---:|---:|
| las/s1 | Leśny Slime (1–3) | 1 | 1,5 | 5 | 1,0 |
| las/m1 | Muchomornik (3–5) | 3 | 4,5 | 11 | 1,7 |
| las/w1 | Cierniowy Wilk (6–8) | 6 | 5,3 | 16 | 2,0 |
| las/t1 | Leśny Troll (8–9) | 8 | 4,3 | 5 | 2,0 |
| las/straznik | Strażnik Gaju (10–10) | 10 | 2,6 | 2 | 0,7 |
| bagno/r1 | Rechotek (10–12) | 11 | 2,8 | 7 | 1,0 |
| bagno/b1 | Bulgotnik (12–14) | 12 | 13 | 15 | 2,7 |
| bagno/k1 | Kłodokłap (14–16) | 14 | 8,0 | 20 | 1,3 |
| bagno/t1 | Ropucha z Chatką (16–16) | 16 | 1,0 | 3 | 1,0 |
| bagno/straznik | Strażnik Topieli (16–16) | 16 | 3,7 | 2 | 1,0 |
| dzungla/z1 | Zwijogon (17–19) | 17 | 8,0 | 16 | 2,0 |
| dzungla/g1 | Gębokwiat (19–21) | 19 | 11 | 22 | 2,7 |
| dzungla/o1 | Kokosowy Siłacz (21–23) | 21 | 8,7 | 24 | 2,0 |
| dzungla/t1 | Pancernik Ruin (23–23) | 23 | 1,5 | 2 | 0,0 |
| dzungla/straznik | Wąż Stu Lian (23–23) | 23 | 2,2 | 2 | 0,7 |

### Szansa wygranej ze Strażnikiem (%), bohater na poziomie Strażnika −1 … +3

„Sam” = bohater bez niczego. „Z dodatkami” = po 6 punktów z mini-gier w trzech głównych statystykach i pełny zestaw kowala ulepszony o 2.

| Strażnik | Klasa | Sam: −1 / 0 / +1 / +2 / +3 | Z dodatkami: −1 / 0 / +1 / +2 / +3 |
|---|---|---|---|
| Strażnik Gaju (poz. 10) | Wojownik | 21 / 43 / 52 / 72 / 85 | 60 / 77 / 87 / 94 / 98 |
| Strażnik Gaju (poz. 10) | Zwiadowca | 16 / 38 / 54 / 67 / 86 | 64 / 78 / 86 / 94 / 96 |
| Strażnik Gaju (poz. 10) | Mag | 14 / 35 / 55 / 68 / 85 | 68 / 78 / 91 / 96 / 98 |
| Strażnik Topieli (poz. 16) | Wojownik | 7 / 14 / 26 / 32 / 38 | 26 / 41 / 53 / 58 / 72 |
| Strażnik Topieli (poz. 16) | Zwiadowca | 13 / 20 / 24 / 42 / 48 | 31 / 44 / 46 / 60 / 65 |
| Strażnik Topieli (poz. 16) | Mag | 5 / 12 / 22 / 34 / 36 | 22 / 32 / 41 / 59 / 65 |
| Wąż Stu Lian (poz. 23) | Wojownik | 15 / 19 / 28 / 34 / 45 | 33 / 44 / 51 / 58 / 63 |
| Wąż Stu Lian (poz. 23) | Zwiadowca | 18 / 28 / 27 / 35 / 39 | 32 / 44 / 41 / 49 / 57 |
| Wąż Stu Lian (poz. 23) | Mag | 13 / 22 / 20 / 25 / 36 | 26 / 39 / 40 / 47 / 56 |

### Propozycje zmian liczb — „przed / po” (świat „po zmianie D-107 (pliki gry)”, mediana z trzech klas)

Liczone na kopii danych; pliki gry bez zmian. Kolumny: minuty do końca · różnica między klasami (najwolniejsza − najszybsza) · przegranych · prób ze Strażnikami i ilu graczy na nich utknęło (Las / Bagno / Dżungla) · najdłużej bez awansu.

**Tylko walki**

| Zmiana | Koniec (min) | Różnica klas (min) | Przegranych | Prób ze Strażnikami | Utknęło (%) | Bez awansu (min) |
|---|---:|---:|---:|---|---|---:|
| Bez zmian (liczby z plików gry) | 75 | 10 | 46 | 2,0 / 3,0 / 3,0 | 0 / 13 / 14 | 6,0 |
| Dla porównania: krzywa doświadczenia +25% (dłuższa gra) | 91 | 10 | 57 | 2,0 / 3,0 / 3,0 | 3 / 17 / 20 | 7,1 |
| Krzywa doświadczenia: wykładnik 1,5 zamiast 1,6 | 59 | 9,5 | 36 | 2,0 / 3,0 / 2,8 | 1 / 6 / 12 | 4,7 |
| Razem: Strażnicy −30% życia i doświadczenie Dżungli +25% | 66 | 8,0 | 41 | 2,0 / 2,0 / 2,0 | 0 / 3 / 3 | 5,3 |
| Strażnik Topieli i Wąż Stu Lian: życie −15% | 73 | 10 | 46 | 2,0 / 2,3 / 2,2 | 0 / 6 / 6 | 6,0 |
| Strażnik Topieli i Wąż Stu Lian: życie −30% | 71 | 9,9 | 45 | 2,0 / 2,0 / 2,0 | 0 / 3 / 2 | 5,9 |
| Doświadczenie z potworów Dżungli +25% | 70 | 11 | 43 | 2,0 / 3,0 / 3,0 | 0 / 13 / 15 | 5,3 |

**Walki + mini-gry + pety + kowal**

| Zmiana | Koniec (min) | Różnica klas (min) | Przegranych | Prób ze Strażnikami | Utknęło (%) | Bez awansu (min) |
|---|---:|---:|---:|---|---|---:|
| Bez zmian (liczby z plików gry) | 81 | 7,8 | 24 | 1,7 / 2,0 / 1,7 | 0 / 1 / 1 | 9,8 |
| Dla porównania: krzywa doświadczenia +25% (dłuższa gra) | 99 | 8,4 | 27 | 1,0 / 2,0 / 1,3 | 0 / 3 / 2 | 11 |
| Krzywa doświadczenia: wykładnik 1,5 zamiast 1,6 | 69 | 6,2 | 21 | 1,7 / 2,0 / 1,8 | 0 / 1 / 4 | 8,9 |
| Razem: Strażnicy −30% życia i doświadczenie Dżungli +25% | 75 | 7,3 | 22 | 1,7 / 1,0 / 1,0 | 0 / 0 / 0 | 9,5 |
| Strażnik Topieli i Wąż Stu Lian: życie −15% | 80 | 7,3 | 23 | 1,7 / 1,8 / 1,0 | 0 / 1 / 1 | 9,8 |
| Strażnik Topieli i Wąż Stu Lian: życie −30% | 80 | 7,2 | 23 | 1,7 / 1,0 / 1,0 | 0 / 0 / 0 | 9,8 |
| Doświadczenie z potworów Dżungli +25% | 77 | 6,4 | 22 | 1,7 / 2,0 / 1,8 | 0 / 1 / 2 | 9,5 |

**Niecierpliwy (pomija walki, pcha do przodu)**

| Zmiana | Koniec (min) | Różnica klas (min) | Przegranych | Prób ze Strażnikami | Utknęło (%) | Bez awansu (min) |
|---|---:|---:|---:|---|---|---:|
| Bez zmian (liczby z plików gry) | 45 | 4,6 | 64 | 3,0 / 4,3 / 3,5 | 6 / 32 / 30 | 3,9 |
| Dla porównania: krzywa doświadczenia +25% (dłuższa gra) | 55 | 2,7 | 76 | 3,0 / 4,7 / 3,7 | 10 / 39 / 32 | 4,7 |
| Krzywa doświadczenia: wykładnik 1,5 zamiast 1,6 | 35 | 3,2 | 49 | 3,0 / 4,0 / 3,7 | 2 / 27 / 27 | 3,0 |
| Razem: Strażnicy −30% życia i doświadczenie Dżungli +25% | 40 | 3,2 | 55 | 3,0 / 3,0 / 2,2 | 6 / 9 / 6 | 3,4 |
| Strażnik Topieli i Wąż Stu Lian: życie −15% | 45 | 4,3 | 61 | 3,0 / 3,7 / 3,0 | 6 / 20 / 19 | 3,9 |
| Strażnik Topieli i Wąż Stu Lian: życie −30% | 44 | 3,8 | 59 | 3,0 / 3,0 / 2,0 | 6 / 9 / 8 | 3,9 |
| Doświadczenie z potworów Dżungli +25% | 43 | 3,9 | 58 | 3,0 / 4,3 / 4,0 | 6 / 32 / 31 | 3,4 |

_Uruchomienie: `python -B swiat/przejscie_gry/symulacja_przejscia.py --przebiegow 100 --ziarno 1` · 100 przebiegów na komórkę · krzywa doświadczenia 11,71 × L^1,6 · katalog sklepu: swiat/postacie/sklep_liczby.json · liczone 2026-11-19._

<!-- TABELE:KONIEC -->
