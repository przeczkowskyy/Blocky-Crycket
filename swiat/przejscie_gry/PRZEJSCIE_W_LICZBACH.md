# Przejście gry w liczbach — od 1. poziomu do bramy Pustyni

*Status: **propozycja** (rachunek, nie decyzja). Zlecenie: D-106. Liczone 19.11.2026 symulatorem, bez Roblox Studio.
Wynik każdej walki liczy prawdziwy silnik walki, a liczby gry są czytane z plików gry. Wnioski poniżej są pisane ręcznie
do liczb z 19.11 (ok. 8:50); liczby o Strażnikach, czasy i rekomendacje uaktualnione 19.11 ok. 13:50, po D-111
(Strażnik Topieli i Wąż Stu Lian: życie −15%). Tabele na dole symulator podmienia sam przy każdym uruchomieniu.*

## Najważniejsze

1. **Grę da się przejść każdą klasą i każdym sposobem gry** — na 100 graczy w każdej z 42 kombinacji do Strażnika
   Dżungli doszło 100.
2. **Trwa to ok. 1 godz. 20 min** przy zwykłej grze (walki, mini-gry, pety, kowal); 45 min, gdy gracz pomija walki
   i pcha do przodu; ok. 2 godz., gdy ogląda każdą walkę w całości.
3. **Po D-111 (życie −15%) gracz rzadziej utyka na Strażniku Topieli i na Wężu Stu Lian.** Sam bohater na ich
   poziomie wygrywa 24–35% walk (przed zmianą 12–28%; ze Strażnikiem Gaju 35–43%). Kto tylko walczy, w 0–8%
   przypadków przegrywa z nimi pięć razy lub więcej (przed 8–15%); niecierpliwy — w 10–20% (przed 30–55%).
4. **Nudzi się pod koniec Dżungli i Bagna**: 28 walk z Kokosowym Siłaczem (9 minut, 20–24 walki z rzędu z jednym
   potworem) i 26 walk z Kłodokłapem (8 minut); potem jeszcze ok. 5 minut przy Strażniku (przed D-111 ok. 8).
5. **Najtrudniej ma nadal Mag na Strażniku Topieli** (sam wygrywa 24% walk, przed D-111 12%), choć całą grę kończy
   najszybciej; najwolniej idzie Wojownik (o 4–25 minut dłużej niż Mag). Żadna klasa nie jest wymagana.

## Ile to trwa

Minuty gry, mediana, świat po zmianach D-107 i D-111. Dwie pierwsze kolumny to średnia z trzech klas, w ostatniej trzy liczby = Wojownik / Zwiadowca / Mag.

| Sposób gry | Strażnik Gaju | Strażnik Topieli | Wąż Stu Lian (koniec) |
|---|---:|---:|---:|
| Tylko walki, każda oglądana w całości | 25 | 71 | 129 / 123 / 104 |
| Tylko walki (nowe ogląda, znane przyspiesza albo pomija) | 17 | 42 | 76 / 76 / 64 |
| Walki + mini-gry (10 min na godzinę) | 17 | 45 | 78 / 79 / 73 |
| Walki + mini-gry + pety + kowal | 19 | 46 | 83 / 83 / 75 |
| To samo + sklep z przedmiotami | 19 | 47 | 81 / 81 / 78 |
| Ostrożny (czeka na zapas poziomu, więcej mini-gier) | 33 | 68 | 114 / 114 / 103 |
| Niecierpliwy (pomija walki, idzie na Strażnika o poziom za wcześnie) | 11 | 26 | 47 / 46 / 43 |

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
| Strażnik Topieli (poz. 16) | 27% | 30% | 24% | 52% |
| Wąż Stu Lian (poz. 23) | 30% | 35% | 31% | 52% |

- Przed D-111 (życie −15%, 19.11): Topiel 14 / 20 / 12% (z dodatkami 39%), Wąż 19 / 28 / 22% (42%). Życie na poziomie
  Strażnika: Topiel 2528 → 2149, Wąż 2852 → 2424.
- „Z dodatkami” = po 6 punktów z mini-gier w trzech głównych statystykach i pełny zestaw kowala ulepszony o 2.
- Trzy poziomy ponad Strażnika sam bohater ma 51–60% (Topiel) i 50–60% (Wąż); przed D-111 36–48% i 36–45%.
- Nikt nie utyka na stałe: przegrana daje doświadczenie, więc po kilku próbach i paru walkach obok gracz przechodzi.
  Kosztuje to ok. 5 minut przy każdym z dwóch Strażników i 1–2 przegrane (przed D-111 ok. 8 minut i 2–3 przegrane).
- Z mini-grami, petami i kowalem problem znika (utyka 0–3% graczy). Bez dodatków dwa ostatnie Strażniki są dalej
  trudniejsze niż Strażnik Gaju (sam bohater 24–35% wobec 35–43%, z dodatkami 52% wobec 78%), ale różnica zmalała —
  zgodnie z D-111: gracz ma się pomęczyć, tylko mniej.

## Gdzie się nudzi

| Miejsce | Co się dzieje (tylko walki) |
|---|---|
| Dżungla, Kokosowy Siłacz (21–23) | 28 walk, 9 minut, najdłuższa seria jednego potwora w całej grze (20–24) |
| Bagno, Kłodokłap (14–16) | 26 walk, 8 minut |
| Strażnik Topieli i Wąż Stu Lian | po ok. 5 minut i 2 próby na każdego (przed D-111: 8 minut, 3 próby); najdłuższy czas bez nowej zagrody: 10–21 minut |
| Bagno, Rechotek i Dżungla, Zwijogon | odwrotnie — gracz wchodzi o 2 poziomy za mocny i mija zagrodę w minutę |

- Najdłużej bez awansu: 6 minut (tylko walki), 10 minut (każda walka oglądana) — zawsze przy Kokosowym Siłaczu.
- Powód: potrzebne doświadczenie rośnie szybciej niż doświadczenie z potworów. Na 5. poziomie awans to ok. 4 walki,
  na 21. — ok. 11.
- W lesie żadna zagroda nie trwa dłużej niż 4–6 minut.

## Klasy

- Mag kończy najszybciej w każdym sposobie gry (jego walki są najkrótsze), Wojownik najwolniej. Różnica: 3–12 minut
  przy zwykłej grze, 25 minut, gdy każda walka jest oglądana w całości.
- Po D-111 klasy utykają na Strażnikach podobnie (tylko walki: 0–8% graczy; niecierpliwy: 10–20%); Mag ma dalej
  najmniejszą szansę samego bohatera na Strażniku Topieli (24%).
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

Rachunek „przed / po” policzony symulatorem na kopii danych (pliki gry bez zmian) — poza punktem 1, który jest już
w plikach gry.

1. **Strażnik Topieli i Wąż Stu Lian: życie −15% — wykonane (D-111, Karol 19.11).** Wariant −30% odpadł („gracz
   słusznie ma się pomęczyć”).
   - W plikach gry: życie na poziomie Strażnika 2528 → 2149 (Topiel, poz. 16) i 2852 → 2424 (Wąż, poz. 23), czyli
     równo −15%. Rano propozycja liczyła −0,15 modyfikatora życia (ok. −9% i −12% życia), więc zmiana w grze jest
     trochę mocniejsza niż ówczesny wiersz „−15%” (tam utykało 5% / 6%).
   - Tylko walki: utyka 12% / 11% graczy → 3% / 4%; prób 3,0 / 2,8 → 2,3 / 2,2; koniec 75 → 72 min.
   - Niecierpliwy: utyka 41% / 37% → 18% / 16%; koniec bez zmian (45 min).
   - Ze wszystkimi dodatkami prawie bez zmian (81 → 80 min, utyka 1% / 2% → 0% / 1%).
2. **Doświadczenie z potworów Dżungli +25%** (otwarte — druga część pytania 70), liczone już na Strażnikach po D-111.
   - Tylko walki: koniec 72 → 67 min, najdłużej bez awansu 6,0 → 5,2 min, różnica między klasami 12 → 7,6 min.
   - Ze wszystkim 80 → 76 min, niecierpliwy 45 → 41 min.
3. **Kara za przegraną: obniżyć górny limit** (np. do połowy łupu zwykłego potwora), nie procent.
   - Nie zmienia czasu gry, więc bez rachunku „przed / po”; dziś to 27–42% zarobku gracza, który nie wydaje.
4. **Nie wydłużać gry krzywą doświadczenia.**
   - Krzywa +25%: koniec 72 → 88 min, ale utyka 6% / 10% i dłużej bez awansu (7,0 min).
   - Wykładnik 1,5 zamiast 1,6 skraca grę do 58 min — tylko gdy krótsza gra jest w porządku.
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
| Tylko walki, każda oglądana w całości | Wojownik | 0,7 | 26 | 73 | 125 | 116–136 | 100% |
| Tylko walki, każda oglądana w całości | Zwiadowca | 0,7 | 28 | 69 | 124 | 110–137 | 100% |
| Tylko walki, każda oglądana w całości | Mag | 0,7 | 25 | 66 | 103 | 95–113 | 100% |
| Tylko walki | Wojownik | 0,7 | 17 | 49 | 77 | 72–89 | 100% |
| Tylko walki | Zwiadowca | 0,7 | 19 | 47 | 76 | 69–86 | 100% |
| Tylko walki | Mag | 0,7 | 18 | 41 | 66 | 62–76 | 100% |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 0,7 | 17 | 48 | 83 | 78–92 | 100% |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 0,8 | 18 | 49 | 82 | 77–95 | 100% |
| Walki + mini-gry (10 min na godzinę) | Mag | 0,7 | 17 | 45 | 75 | 71–81 | 100% |
| Walki + mini-gry + pety + kowal | Wojownik | 0,7 | 21 | 50 | 85 | 82–95 | 100% |
| Walki + mini-gry + pety + kowal | Zwiadowca | 0,7 | 20 | 50 | 85 | 82–96 | 100% |
| Walki + mini-gry + pety + kowal | Mag | 0,7 | 18 | 46 | 79 | 76–83 | 100% |
| Wszystko + sklep z przedmiotami | Wojownik | 0,7 | 21 | 50 | 85 | 82–93 | 100% |
| Wszystko + sklep z przedmiotami | Zwiadowca | 0,8 | 20 | 51 | 87 | 80–96 | 100% |
| Wszystko + sklep z przedmiotami | Mag | 0,7 | 20 | 48 | 80 | 75–84 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 0,7 | 35 | 73 | 125 | 113–130 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 0,7 | 35 | 74 | 126 | 113–134 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 0,7 | 33 | 68 | 108 | 106–113 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 0,5 | 11 | 27 | 47 | 44–52 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 0,5 | 12 | 26 | 48 | 43–52 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 0,5 | 10 | 25 | 45 | 42–48 | 100% |

Brama otwiera się od razu po wygranej ze Strażnikiem; dojście do niej to kilka sekund (dokładne czasy bram są w pliku JSON, pola `brama_…`).

### Poziom, walki i Złoto — świat „przed zmianą (stan z 18.11)” (mediana)

| Sposób gry | Klasa | Poziom przy bramach | Walk | Przegranych | Złoto zarobione | Złoto wydane | Złoto stracone po przegranych | Punkty z mini-gier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 11 / 18 / 24 | 188 | 38 | 24630 | 0 | 5950 | 0 |
| Tylko walki, każda oglądana w całości | Zwiadowca | 12 / 18 / 25 | 190 | 41 | 25168 | 0 | 6352 | 0 |
| Tylko walki, każda oglądana w całości | Mag | 11 / 18 / 24 | 181 | 33 | 24290 | 0 | 4951 | 0 |
| Tylko walki | Wojownik | 11 / 18 / 24 | 189 | 36 | 24681 | 0 | 5496 | 0 |
| Tylko walki | Zwiadowca | 12 / 18 / 24 | 189 | 40 | 24290 | 0 | 6086 | 0 |
| Tylko walki | Mag | 12 / 18 / 24 | 180 | 34 | 23285 | 0 | 4904 | 0 |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 11 / 17 / 24 | 178 | 30 | 23838 | 0 | 4297 | 25 |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 11 / 18 / 24 | 180 | 34 | 23442 | 0 | 4920 | 22 |
| Walki + mini-gry (10 min na godzinę) | Mag | 11 / 18 / 24 | 176 | 29 | 24023 | 0 | 4150 | 21 |
| Walki + mini-gry + pety + kowal | Wojownik | 11 / 17 / 23 | 159 | 16 | 23368 | 15450 | 777 | 25 |
| Walki + mini-gry + pety + kowal | Zwiadowca | 11 / 17 / 23 | 162 | 20 | 23215 | 15000 | 1184 | 22 |
| Walki + mini-gry + pety + kowal | Mag | 11 / 17 / 23 | 161 | 17 | 23312 | 15800 | 1004 | 21 |
| Wszystko + sklep z przedmiotami | Wojownik | 11 / 17 / 23 | 155 | 13 | 23444 | 19350 | 346 | 24 |
| Wszystko + sklep z przedmiotami | Zwiadowca | 11 / 17 / 23 | 161 | 17 | 23498 | 19125 | 558 | 23 |
| Wszystko + sklep z przedmiotami | Mag | 11 / 17 / 23 | 155 | 15 | 23275 | 20080 | 557 | 20 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 11 / 18 / 24 | 181 | 7 | 26360 | 22200 | 192 | 60 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 11 / 18 / 24 | 188 | 11 | 26600 | 22200 | 368 | 56 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 11 / 18 / 24 | 182 | 10 | 26470 | 21740 | 317 | 45 |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 11 / 17 / 23 | 168 | 54 | 19996 | 0 | 7482 | 0 |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 11 / 17 / 23 | 174 | 55 | 20174 | 0 | 7875 | 0 |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 11 / 17 / 23 | 166 | 48 | 20206 | 0 | 6988 | 0 |

### Strażnicy — świat „przed zmianą (stan z 18.11)”

Dla każdej krainy: poziom przy pierwszej próbie · prób do wygranej (mediana / co dziesiąty gracz) · ilu graczy utknęło (co najmniej 5 przegranych prób).

| Sposób gry | Klasa | Las | Bagno | Dżungla |
|---|---|---|---|---|
| Tylko walki, każda oglądana w całości | Wojownik | poz. 10 · 2 / 4 · 2% | poz. 16 · 3 / 4 · 5% | poz. 23 · 2 / 5 · 10% |
| Tylko walki, każda oglądana w całości | Zwiadowca | poz. 10 · 2 / 5 · 2% | poz. 16 · 2 / 4 · 0% | poz. 23 · 2 / 5 · 2% |
| Tylko walki, każda oglądana w całości | Mag | poz. 10 · 2 / 4 · 2% | poz. 16 · 3 / 6 · 12% | poz. 23 · 3 / 5 · 10% |
| Tylko walki | Wojownik | poz. 10 · 2 / 4 · 0% | poz. 16 · 2 / 5 · 10% | poz. 23 · 2 / 6 · 12% |
| Tylko walki | Zwiadowca | poz. 10 · 2 / 4 · 5% | poz. 16 · 2 / 5 · 2% | poz. 23 · 2 / 5 · 0% |
| Tylko walki | Mag | poz. 10 · 2 / 4 · 2% | poz. 16 · 2 / 6 · 15% | poz. 23 · 2 / 5 · 8% |
| Walki + mini-gry (10 min na godzinę) | Wojownik | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 4 · 2% | poz. 23 · 2 / 4 · 5% |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | poz. 10 · 2 / 4 · 5% | poz. 16 · 2 / 5 · 5% | poz. 23 · 2 / 4 · 5% |
| Walki + mini-gry (10 min na godzinę) | Mag | poz. 10 · 2 / 4 · 0% | poz. 16 · 3 / 5 · 8% | poz. 23 · 2 / 5 · 10% |
| Walki + mini-gry + pety + kowal | Wojownik | poz. 10 · 1 / 3 · 0% | poz. 16 · 1 / 3 · 0% | poz. 23 · 1 / 2 · 0% |
| Walki + mini-gry + pety + kowal | Zwiadowca | poz. 10 · 1 / 3 · 0% | poz. 16 · 1 / 3 · 0% | poz. 23 · 1 / 3 · 0% |
| Walki + mini-gry + pety + kowal | Mag | poz. 10 · 1 / 3 · 0% | poz. 16 · 1 / 3 · 2% | poz. 23 · 1 / 3 · 0% |
| Wszystko + sklep z przedmiotami | Wojownik | poz. 10 · 1 / 3 · 0% | poz. 16 · 1 / 2 · 0% | poz. 23 · 1 / 2 · 0% |
| Wszystko + sklep z przedmiotami | Zwiadowca | poz. 10 · 2 / 3 · 0% | poz. 16 · 1 / 2 · 0% | poz. 23 · 1 / 3 · 2% |
| Wszystko + sklep z przedmiotami | Mag | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 4 · 2% | poz. 23 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | poz. 11 · 1 / 1 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | poz. 11 · 1 / 2 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | poz. 11 · 1 / 2 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | poz. 9 · 4 / 7 · 22% | poz. 15 · 4 / 6 · 22% | poz. 22 · 3 / 7 · 25% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | poz. 9 · 4 / 6 · 20% | poz. 15 · 4 / 7 · 25% | poz. 22 · 2 / 8 · 15% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | poz. 9 · 2 / 6 · 20% | poz. 15 · 3 / 8 · 30% | poz. 22 · 3 / 7 · 22% |

### Nuda i przestoje — świat „przed zmianą (stan z 18.11)” (mediana)

| Sposób gry | Klasa | Najdłużej bez awansu | Najdłużej bez nowej zagrody | Najdłuższa seria jednego potwora | Czekanie (odradzanie + blokada) |
|---|---|---|---|---|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 11 min (dzungla/o1) | 19 min (dzungla/o1) | 23 × Kokosowy Siłacz | 0,0 min |
| Tylko walki, każda oglądana w całości | Zwiadowca | 10 min (dzungla/o1) | 19 min (dzungla/o1) | 24 × Gębokwiat | 0,0 min |
| Tylko walki, każda oglądana w całości | Mag | 8,6 min (dzungla/z1) | 16 min (dzungla/o1) | 24 × Kokosowy Siłacz | 0,0 min |
| Tylko walki | Wojownik | 6,3 min (dzungla/o1) | 12 min (bagno/k1) | 24 × Kokosowy Siłacz | 3,5 min |
| Tylko walki | Zwiadowca | 6,5 min (dzungla/o1) | 12 min (bagno/k1) | 23 × Kokosowy Siłacz | 2,7 min |
| Tylko walki | Mag | 5,3 min (dzungla/z1) | 9,9 min (dzungla/g1) | 24 × Kokosowy Siłacz | 1,6 min |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 9,8 min (dzungla/z1) | 14 min (dzungla/g1) | 25 × Kokosowy Siłacz | 3,1 min |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 9,6 min (dzungla/g1) | 14 min (dzungla/g1) | 24 × Gębokwiat | 2,6 min |
| Walki + mini-gry (10 min na godzinę) | Mag | 9,5 min (dzungla/g1) | 14 min (dzungla/g1) | 25 × Kokosowy Siłacz | 1,4 min |
| Walki + mini-gry + pety + kowal | Wojownik | 10 min (dzungla/z1) | 13 min (bagno/b1) | 24 × Kokosowy Siłacz | 2,1 min |
| Walki + mini-gry + pety + kowal | Zwiadowca | 10 min (dzungla/z1) | 13 min (bagno/b1) | 24 × Kokosowy Siłacz | 2,0 min |
| Walki + mini-gry + pety + kowal | Mag | 9,7 min (dzungla/g1) | 13 min (dzungla/g1) | 24 × Kokosowy Siłacz | 1,2 min |
| Wszystko + sklep z przedmiotami | Wojownik | 10 min (dzungla/z1) | 12 min (dzungla/z1) | 23 × Kokosowy Siłacz | 1,9 min |
| Wszystko + sklep z przedmiotami | Zwiadowca | 10 min (dzungla/z1) | 13 min (dzungla/z1) | 24 × Kokosowy Siłacz | 1,8 min |
| Wszystko + sklep z przedmiotami | Mag | 9,7 min (dzungla/g1) | 12 min (bagno/b1) | 24 × Kokosowy Siłacz | 1,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 14 min (bagno/k1) | 19 min (bagno/k1) | 24 × Kokosowy Siłacz | 2,3 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 14 min (bagno/k1) | 19 min (bagno/k1) | 23 × Zwijogon | 2,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 13 min (dzungla/g1) | 18 min (dzungla/g1) | 24 × Zwijogon | 1,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 4,1 min (dzungla/o1) | 7,3 min (dzungla/o1) | 26 × Kokosowy Siłacz | 3,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 4,1 min (dzungla/o1) | 7,3 min (dzungla/o1) | 26 × Kokosowy Siłacz | 2,8 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 3,8 min (dzungla/o1) | 7,1 min (dzungla/g1) | 26 × Kokosowy Siłacz | 1,9 min |

### Czasy do kamieni milowych — świat „po zmianie D-107 (pliki gry)” (minuty gry, mediana)

| Sposób gry | Klasa | 1. wygrana | Strażnik: Las | Strażnik: Bagno | Strażnik: Dżungla | Koniec: 10%–90% graczy | Skończyło |
|---|---|---:|---:|---:|---:|---|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 0,8 | 25 | 76 | 129 | 117–146 | 100% |
| Tylko walki, każda oglądana w całości | Zwiadowca | 0,7 | 27 | 73 | 123 | 108–142 | 100% |
| Tylko walki, każda oglądana w całości | Mag | 0,7 | 25 | 63 | 104 | 93–119 | 100% |
| Tylko walki | Wojownik | 0,8 | 18 | 43 | 76 | 65–88 | 100% |
| Tylko walki | Zwiadowca | 0,8 | 17 | 44 | 76 | 67–87 | 100% |
| Tylko walki | Mag | 0,7 | 17 | 40 | 64 | 57–71 | 100% |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 0,7 | 17 | 47 | 78 | 73–85 | 100% |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 0,7 | 17 | 45 | 79 | 73–92 | 100% |
| Walki + mini-gry (10 min na godzinę) | Mag | 0,8 | 16 | 43 | 73 | 69–79 | 100% |
| Walki + mini-gry + pety + kowal | Wojownik | 0,7 | 19 | 48 | 83 | 80–92 | 100% |
| Walki + mini-gry + pety + kowal | Zwiadowca | 0,8 | 20 | 49 | 83 | 77–86 | 100% |
| Walki + mini-gry + pety + kowal | Mag | 0,7 | 17 | 42 | 75 | 71–80 | 100% |
| Wszystko + sklep z przedmiotami | Wojownik | 0,7 | 19 | 47 | 81 | 77–85 | 100% |
| Wszystko + sklep z przedmiotami | Zwiadowca | 0,7 | 20 | 48 | 81 | 77–84 | 100% |
| Wszystko + sklep z przedmiotami | Mag | 0,7 | 19 | 45 | 78 | 74–81 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 0,7 | 33 | 70 | 114 | 108–124 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 0,7 | 34 | 70 | 114 | 108–126 | 100% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 0,7 | 31 | 65 | 103 | 100–108 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 0,6 | 11 | 28 | 47 | 41–50 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 0,5 | 11 | 26 | 46 | 40–52 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 0,6 | 9,8 | 26 | 43 | 39–47 | 100% |

Brama otwiera się od razu po wygranej ze Strażnikiem; dojście do niej to kilka sekund (dokładne czasy bram są w pliku JSON, pola `brama_…`).

### Poziom, walki i Złoto — świat „po zmianie D-107 (pliki gry)” (mediana)

| Sposób gry | Klasa | Poziom przy bramach | Walk | Przegranych | Złoto zarobione | Złoto wydane | Złoto stracone po przegranych | Punkty z mini-gier |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 11 / 18 / 25 | 188 | 48 | 25729 | 0 | 7332 | 0 |
| Tylko walki, każda oglądana w całości | Zwiadowca | 12 / 18 / 24 | 179 | 46 | 24556 | 0 | 6776 | 0 |
| Tylko walki, każda oglądana w całości | Mag | 12 / 18 / 25 | 175 | 42 | 25795 | 0 | 5780 | 0 |
| Tylko walki | Wojownik | 12 / 18 / 25 | 190 | 48 | 26609 | 0 | 7224 | 0 |
| Tylko walki | Zwiadowca | 12 / 18 / 25 | 189 | 48 | 26363 | 0 | 7274 | 0 |
| Tylko walki | Mag | 11 / 18 / 24 | 176 | 40 | 24320 | 0 | 6016 | 0 |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 11 / 18 / 24 | 169 | 38 | 23214 | 0 | 5148 | 25 |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 11 / 18 / 24 | 172 | 40 | 24368 | 0 | 5774 | 22 |
| Walki + mini-gry (10 min na godzinę) | Mag | 11 / 18 / 24 | 170 | 36 | 24338 | 0 | 5301 | 21 |
| Walki + mini-gry + pety + kowal | Wojownik | 11 / 17 / 23 | 155 | 24 | 23380 | 14150 | 1222 | 24 |
| Walki + mini-gry + pety + kowal | Zwiadowca | 11 / 17 / 23 | 156 | 26 | 23192 | 13775 | 1846 | 22 |
| Walki + mini-gry + pety + kowal | Mag | 11 / 17 / 24 | 152 | 22 | 23494 | 14660 | 1225 | 21 |
| Wszystko + sklep z przedmiotami | Wojownik | 11 / 17 / 23 | 148 | 18 | 23276 | 18950 | 514 | 24 |
| Wszystko + sklep z przedmiotami | Zwiadowca | 11 / 17 / 23 | 150 | 20 | 23252 | 18650 | 680 | 22 |
| Wszystko + sklep z przedmiotami | Mag | 11 / 17 / 23 | 151 | 20 | 23372 | 19420 | 692 | 21 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 12 / 18 / 24 | 172 | 11 | 26304 | 20900 | 272 | 49 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 12 / 18 / 24 | 176 | 14 | 26279 | 20900 | 475 | 47 |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 12 / 18 / 24 | 171 | 10 | 26112 | 21740 | 330 | 45 |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 11 / 18 / 24 | 171 | 67 | 21042 | 0 | 9518 | 0 |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 11 / 17 / 24 | 170 | 61 | 21624 | 0 | 8710 | 0 |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 11 / 18 / 24 | 160 | 59 | 20592 | 0 | 8116 | 0 |

### Strażnicy — świat „po zmianie D-107 (pliki gry)”

Dla każdej krainy: poziom przy pierwszej próbie · prób do wygranej (mediana / co dziesiąty gracz) · ilu graczy utknęło (co najmniej 5 przegranych prób).

| Sposób gry | Klasa | Las | Bagno | Dżungla |
|---|---|---|---|---|
| Tylko walki, każda oglądana w całości | Wojownik | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 4 · 0% | poz. 24 · 2 / 4 · 8% |
| Tylko walki, każda oglądana w całości | Zwiadowca | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 3 · 2% | poz. 23 · 2 / 4 · 2% |
| Tylko walki, każda oglądana w całości | Mag | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 5 · 10% | poz. 23 · 2 / 5 · 8% |
| Tylko walki | Wojownik | poz. 10 · 2 / 4 · 0% | poz. 16 · 2 / 4 · 2% | poz. 23 · 2 / 4 · 2% |
| Tylko walki | Zwiadowca | poz. 10 · 2 / 4 · 0% | poz. 16 · 2 / 5 · 8% | poz. 23 · 2 / 5 · 8% |
| Tylko walki | Mag | poz. 10 · 2 / 4 · 0% | poz. 16 · 2 / 4 · 0% | poz. 23 · 2 / 4 · 2% |
| Walki + mini-gry (10 min na godzinę) | Wojownik | poz. 10 · 2 / 4 · 5% | poz. 16 · 2 / 4 · 0% | poz. 23 · 2 / 3 · 0% |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | poz. 10 · 2 / 4 · 2% | poz. 16 · 2 / 5 · 2% | poz. 23 · 2 / 5 · 2% |
| Walki + mini-gry (10 min na godzinę) | Mag | poz. 10 · 2 / 2 · 0% | poz. 16 · 2 / 5 · 2% | poz. 23 · 2 / 4 · 2% |
| Walki + mini-gry + pety + kowal | Wojownik | poz. 10 · 2 / 3 · 0% | poz. 16 · 1 / 2 · 0% | poz. 23 · 1 / 3 · 0% |
| Walki + mini-gry + pety + kowal | Zwiadowca | poz. 10 · 2 / 3 · 0% | poz. 16 · 2 / 3 · 0% | poz. 23 · 1 / 3 · 2% |
| Walki + mini-gry + pety + kowal | Mag | poz. 10 · 1 / 2 · 0% | poz. 16 · 1 / 3 · 0% | poz. 23 · 1 / 3 · 0% |
| Wszystko + sklep z przedmiotami | Wojownik | poz. 10 · 1 / 3 · 0% | poz. 16 · 1 / 2 · 0% | poz. 23 · 1 / 2 · 0% |
| Wszystko + sklep z przedmiotami | Zwiadowca | poz. 10 · 2 / 3 · 0% | poz. 16 · 1 / 3 · 0% | poz. 23 · 1 / 2 · 0% |
| Wszystko + sklep z przedmiotami | Mag | poz. 10 · 2 / 3 · 0% | poz. 16 · 1 / 3 · 0% | poz. 23 · 1 / 3 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | poz. 11 · 1 / 1 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | poz. 11 · 1 / 2 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | poz. 11 · 1 / 2 · 0% | poz. 17 · 1 / 2 · 0% | poz. 24 · 1 / 2 · 0% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | poz. 9 · 2 / 5 · 8% | poz. 15 · 4 / 6 · 20% | poz. 22 · 3 / 5 · 10% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | poz. 9 · 3 / 4 · 5% | poz. 15 · 2 / 6 · 12% | poz. 22 · 2 / 6 · 20% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | poz. 9 · 3 / 5 · 5% | poz. 15 · 4 / 6 · 20% | poz. 22 · 3 / 7 · 18% |

### Nuda i przestoje — świat „po zmianie D-107 (pliki gry)” (mediana)

| Sposób gry | Klasa | Najdłużej bez awansu | Najdłużej bez nowej zagrody | Najdłuższa seria jednego potwora | Czekanie (odradzanie + blokada) |
|---|---|---|---|---|---:|
| Tylko walki, każda oglądana w całości | Wojownik | 12 min (dzungla/o1) | 21 min (bagno/k1) | 20 × Kokosowy Siłacz | 0,0 min |
| Tylko walki, każda oglądana w całości | Zwiadowca | 11 min (dzungla/o1) | 20 min (bagno/k1) | 22 × Gębokwiat | 0,0 min |
| Tylko walki, każda oglądana w całości | Mag | 8,4 min (dzungla/o1) | 17 min (dzungla/straznik) | 22 × Kokosowy Siłacz | 0,0 min |
| Tylko walki | Wojownik | 6,5 min (dzungla/o1) | 12 min (dzungla/o1) | 24 × Kokosowy Siłacz | 0,0 min |
| Tylko walki | Zwiadowca | 6,3 min (dzungla/o1) | 13 min (dzungla/straznik) | 18 × Gębokwiat | 0,0 min |
| Tylko walki | Mag | 5,2 min (dzungla/z1) | 10 min (dzungla/o1) | 22 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry (10 min na godzinę) | Wojownik | 9,8 min (dzungla/z1) | 15 min (bagno/b1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry (10 min na godzinę) | Zwiadowca | 9,9 min (dzungla/z1) | 14 min (dzungla/g1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry (10 min na godzinę) | Mag | 9,4 min (dzungla/g1) | 14 min (dzungla/o1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry + pety + kowal | Wojownik | 10 min (dzungla/z1) | 13 min (bagno/b1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry + pety + kowal | Zwiadowca | 10 min (dzungla/z1) | 13 min (dzungla/g1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + mini-gry + pety + kowal | Mag | 9,2 min (dzungla/g1) | 13 min (dzungla/g1) | 23 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Wojownik | 9,8 min (bagno/b1) | 13 min (dzungla/g1) | 23 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Zwiadowca | 9,8 min (bagno/b1) | 12 min (bagno/b1) | 24 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Mag | 9,8 min (dzungla/g1) | 13 min (dzungla/g1) | 23 × Kokosowy Siłacz | 0,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Wojownik | 14 min (dzungla/z1) | 18 min (bagno/k1) | 23 × Zwijogon | 0,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Zwiadowca | 14 min (dzungla/z1) | 19 min (bagno/k1) | 23 × Zwijogon | 0,0 min |
| Ostrożny (bez sklepu, z zapasem poziomu) | Mag | 13 min (dzungla/z1) | 17 min (dzungla/o1) | 23 × Kokosowy Siłacz | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 4,0 min (dzungla/o1) | 7,4 min (dzungla/o1) | 24 × Kokosowy Siłacz | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 4,0 min (dzungla/o1) | 7,4 min (dzungla/o1) | 25 × Kokosowy Siłacz | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 3,7 min (dzungla/z1) | 6,8 min (dzungla/g1) | 24 × Kokosowy Siłacz | 0,0 min |

### Gdzie schodzi czas — „Tylko walki”, świat „po zmianie D-107 (pliki gry)” (mediana, średnio z klas)

Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.

| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |
|---|---|---:|---:|---:|---:|
| las/s1 | Leśny Slime (1–3) | 1 | 1,5 | 4 | 0,8 |
| las/m1 | Muchomornik (3–5) | 3 | 3,8 | 11 | 1,7 |
| las/w1 | Cierniowy Wilk (6–8) | 6 | 3,7 | 18 | 2,3 |
| las/t1 | Leśny Troll (8–9) | 8 | 4,0 | 6 | 2,0 |
| las/straznik | Strażnik Gaju (10–10) | 10 | 3,5 | 2 | 1,0 |
| bagno/r1 | Rechotek (10–12) | 12 | 1,0 | 11 | 2,0 |
| bagno/b1 | Bulgotnik (12–14) | 12 | 6,9 | 17 | 4,7 |
| bagno/k1 | Kłodokłap (14–16) | 14 | 8,1 | 22 | 4,7 |
| bagno/t1 | Ropucha z Chatką (16–16) | 16 | 1,2 | 5 | 2,3 |
| bagno/straznik | Strażnik Topieli (16–16) | 16 | 4,7 | 2 | 1,3 |
| dzungla/z1 | Zwijogon (17–19) | 18 | 2,1 | 19 | 3,5 |
| dzungla/g1 | Gębokwiat (19–21) | 19 | 8,3 | 23 | 6,0 |
| dzungla/o1 | Kokosowy Siłacz (21–23) | 21 | 9,3 | 27 | 5,8 |
| dzungla/t1 | Pancernik Ruin (23–23) | 23 | 1,8 | 6 | 2,3 |
| dzungla/straznik | Wąż Stu Lian (23–23) | 23 | 5,2 | 2 | 1,2 |

### Gdzie schodzi czas — „Walki + mini-gry + pety + kowal”, świat „po zmianie D-107 (pliki gry)” (mediana, średnio z klas)

Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.

| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |
|---|---|---:|---:|---:|---:|
| las/s1 | Leśny Slime (1–3) | 1 | 1,5 | 4 | 1,0 |
| las/m1 | Muchomornik (3–5) | 3 | 4,4 | 11 | 1,7 |
| las/w1 | Cierniowy Wilk (6–8) | 6 | 5,3 | 16 | 2,0 |
| las/t1 | Leśny Troll (8–9) | 8 | 4,4 | 5 | 2,0 |
| las/straznik | Strażnik Gaju (10–10) | 10 | 2,8 | 2 | 0,7 |
| bagno/r1 | Rechotek (10–12) | 11 | 2,6 | 7 | 1,2 |
| bagno/b1 | Bulgotnik (12–14) | 12 | 13 | 16 | 2,5 |
| bagno/k1 | Kłodokłap (14–16) | 14 | 7,8 | 19 | 1,7 |
| bagno/t1 | Ropucha z Chatką (16–16) | 16 | 1,0 | 2 | 0,7 |
| bagno/straznik | Strażnik Topieli (16–16) | 16 | 1,9 | 1 | 0,3 |
| dzungla/z1 | Zwijogon (17–19) | 17 | 9,7 | 20 | 3,3 |
| dzungla/g1 | Gębokwiat (19–21) | 19 | 10 | 22 | 3,0 |
| dzungla/o1 | Kokosowy Siłacz (21–23) | 21 | 8,6 | 24 | 2,0 |
| dzungla/t1 | Pancernik Ruin (23–23) | 23 | 1,5 | 2 | 0,0 |
| dzungla/straznik | Wąż Stu Lian (23–23) | 23 | 1,5 | 1 | 0,0 |

### Szansa wygranej ze Strażnikiem (%), bohater na poziomie Strażnika −1 … +3

„Sam” = bohater bez niczego. „Z dodatkami” = po 6 punktów z mini-gier w trzech głównych statystykach i pełny zestaw kowala ulepszony o 2.

| Strażnik | Klasa | Sam: −1 / 0 / +1 / +2 / +3 | Z dodatkami: −1 / 0 / +1 / +2 / +3 |
|---|---|---|---|
| Strażnik Gaju (poz. 10) | Wojownik | 21 / 43 / 52 / 72 / 85 | 60 / 77 / 87 / 94 / 98 |
| Strażnik Gaju (poz. 10) | Zwiadowca | 16 / 38 / 54 / 67 / 86 | 64 / 78 / 86 / 94 / 96 |
| Strażnik Gaju (poz. 10) | Mag | 14 / 35 / 55 / 68 / 85 | 68 / 78 / 91 / 96 / 98 |
| Strażnik Topieli (poz. 16) | Wojownik | 14 / 27 / 38 / 46 / 59 | 41 / 55 / 66 / 74 / 80 |
| Strażnik Topieli (poz. 16) | Zwiadowca | 20 / 30 / 38 / 51 / 60 | 39 / 56 / 58 / 69 / 74 |
| Strażnik Topieli (poz. 16) | Mag | 12 / 24 / 32 / 42 / 51 | 34 / 45 / 56 / 66 / 74 |
| Wąż Stu Lian (poz. 23) | Wojownik | 23 / 30 / 43 / 46 / 60 | 45 / 55 / 60 / 67 / 73 |
| Wąż Stu Lian (poz. 23) | Zwiadowca | 26 / 35 / 36 / 46 / 51 | 40 / 51 / 54 / 60 / 66 |
| Wąż Stu Lian (poz. 23) | Mag | 24 / 31 / 35 / 39 / 50 | 40 / 51 / 55 / 60 / 69 |

### Propozycje zmian liczb — „przed / po” (świat „po zmianie D-107 (pliki gry)”, mediana z trzech klas)

Liczone na kopii danych; pliki gry bez zmian. Kolumny: minuty do końca · różnica między klasami (najwolniejsza − najszybsza) · przegranych · prób ze Strażnikami i ilu graczy na nich utknęło (Las / Bagno / Dżungla) · najdłużej bez awansu.

**Tylko walki**

| Zmiana | Koniec (min) | Różnica klas (min) | Przegranych | Prób ze Strażnikami | Utknęło (%) | Bez awansu (min) |
|---|---:|---:|---:|---|---|---:|
| Bez zmian (liczby z plików gry) | 72 | 12 | 45 | 2,0 / 2,3 / 2,2 | 0 / 3 / 4 | 6,0 |
| Doświadczenie z potworów Dżungli +25% | 67 | 7,6 | 42 | 2,0 / 2,3 / 2,3 | 0 / 3 / 6 | 5,2 |
| Krzywa doświadczenia: wykładnik 1,5 zamiast 1,6 | 58 | 7,1 | 36 | 1,7 / 2,2 / 2,3 | 2 / 0 / 6 | 4,7 |
| Dla porównania: krzywa doświadczenia +25% (dłuższa gra) | 88 | 10 | 58 | 2,0 / 2,2 / 2,2 | 2 / 6 / 10 | 7,0 |

**Walki + mini-gry + pety + kowal**

| Zmiana | Koniec (min) | Różnica klas (min) | Przegranych | Prób ze Strażnikami | Utknęło (%) | Bez awansu (min) |
|---|---:|---:|---:|---|---|---:|
| Bez zmian (liczby z plików gry) | 80 | 7,8 | 24 | 1,7 / 1,3 / 1,0 | 0 / 0 / 1 | 9,8 |
| Doświadczenie z potworów Dżungli +25% | 76 | 8,7 | 22 | 1,7 / 1,3 / 1,0 | 0 / 0 / 0 | 9,7 |
| Krzywa doświadczenia: wykładnik 1,5 zamiast 1,6 | 69 | 7,8 | 20 | 1,3 / 1,3 / 1,3 | 0 / 0 / 0 | 9,0 |
| Dla porównania: krzywa doświadczenia +25% (dłuższa gra) | 97 | 12 | 27 | 1,0 / 1,0 / 1,0 | 0 / 0 / 0 | 11 |

**Niecierpliwy (pomija walki, pcha do przodu)**

| Zmiana | Koniec (min) | Różnica klas (min) | Przegranych | Prób ze Strażnikami | Utknęło (%) | Bez awansu (min) |
|---|---:|---:|---:|---|---|---:|
| Bez zmian (liczby z plików gry) | 45 | 3,8 | 62 | 2,7 / 3,3 / 2,7 | 6 / 18 / 16 | 3,9 |
| Doświadczenie z potworów Dżungli +25% | 41 | 1,6 | 57 | 2,7 / 3,3 / 2,5 | 6 / 18 / 15 | 3,4 |
| Krzywa doświadczenia: wykładnik 1,5 zamiast 1,6 | 35 | 2,1 | 48 | 3,0 / 2,8 / 3,3 | 2 / 13 / 21 | 3,0 |
| Dla porównania: krzywa doświadczenia +25% (dłuższa gra) | 55 | 4,4 | 74 | 3,3 / 3,3 / 2,3 | 8 / 22 / 13 | 4,7 |

_Uruchomienie: `python -B swiat/przejscie_gry/symulacja_przejscia.py --przebiegow 40 --ziarno 1` · 40 przebiegów na komórkę · krzywa doświadczenia 11,71 × L^1,6 · katalog sklepu: swiat/postacie/sklep_liczby.json · liczone 2026-11-19._

<!-- TABELE:KONIEC -->
