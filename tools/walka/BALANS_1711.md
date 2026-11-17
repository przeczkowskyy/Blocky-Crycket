# Kalkulator balansu 17.11 — Pancerz w biomach, Twierdza, pety, Gemy, pytanie 40, trening

> **Status: propozycja (liczby robocze), nie kanon.** Sześć zaległych rachunków z `B&C/Produkcja/Zadania.md`
> (wiersze „Kalkulator balansu po trzeciej sesji 14.11”, „Opinia agenta do pytania 40” i „Balans po sesji 16.11”).
> Liczy je `tools/walka/progresja.py` na prawdziwym silniku walki v3 (`tools/walka/silnik.py`) i na tej samej krzywej
> tempa co `tools/walka/tempo.py`. Niczego w sejfie, w kodzie gry ani w danych walki nie zmieniałem. Każda liczba,
> której nie ma w sejfie, jest opisana niżej jako „przyjęte, do zmiany”. Decyzje ✅ traktuję jako ustalone, a 💡
> (np. D-094) tylko jako propozycje.

## W skrócie

1. **Pancerz w ośmiu biomach.** Pancerz i ciosy rosną z poziomem liniowo, więc procent ciosu, który przechodzi przez
   Pancerz, sam z siebie się nie psuje. Wojownik wzorcowy już w lesie dochodzi do limitu z D-091 (przechodzi 25%
   zwykłego ciosu Slime'a i Wilka) — dodatkowy Pancerz pomaga mu tylko na krytyki, trolla i umiejętności. Żeby walki
   zostały „do przegrania”, potwory kolejnych biomów muszą mieć ciosy i życie większe o ok. **6% na biom** (mnożnik
   biomu od 1,04 w lesie do ok. 1,47 w kryształowym). Wtedy gracz, który trenuje 20% czasu, wygrywa ze zwykłymi
   potworami na wejściu 83% → 75%, ze strażnikiem na wyjściu 65% → 28%. Gracz, który nie trenuje wcale, w ostatnim
   biomie wygrywa ze zwykłymi tylko 39%, a ze strażnikiem prawie nigdy.
2. **Drzewko Twierdzy.** Sam mnożnik z drzewka się nie rozjeżdża (pełne drzewko daje ×1,3 do ×2,8 zależnie od tego,
   jak składać premie). Rozjeżdża się **krzywa budynku i praca offline**: kopalnia z krzywą ×1,6 na poziom albo
   n^1,5 zarabia więcej niż walka już przy 3.–7. poziomie budynku, a kopalnia pracująca całą dobę nawet przy łagodnej
   krzywej daje 180–420% Złota z walk na dobę. Węzeł drzewka ma stałą cenę, a jego wartość rośnie z budynkiem 6–43 razy.
3. **Ewolucja petów.** Przy dzisiejszej szansie 10% na Shard Ewolucji gracz farmiący strażnika potrzebuje średnio
   14 prób (ok. 21 minut) na jeden Shard, a pechowe 10% graczy ponad 31 prób. Tokeny nie są problemem (ok. 130 na
   godzinę). Wąskim gardłem są **kopie peta z jajek**: komplet ewolucji legendarnego peta (2% w jajku) to ok. 550 jajek.
4. **Gemy.** Dziś łup daje **ok. 7 Gemów w 10 godzin gry**, a drzewka kosztują razem 20 650 Gemów. Sloty umiejętności są
   w drzewku: pierwszy kosztuje 25 Gemów, wszystkie trzy 125 — **gracz bez płacenia nie ma dziś w 10 godzin ani jednego
   slotu**, choć balans walki zakłada sloty od 1., 5. i 10. poziomu.
5. **Pytanie 40.** Wojownik z tarczą i unikiem nie jest za mocny: limit uniku klasy (podejście a) już działa, a Wojownik,
   który cały trening wkłada w Zręczność, przegrywa z Wojownikiem trenującym rozkładem klasy (z potworami 84% zamiast
   96%, w pojedynkach 28–32%). Mniejszy przyrost Zręczności (b) i niesumowanie bloku z unikiem (c) niczego nie
   naprawiają, a (c) wyłącza blok Maga i Zwiadowcy. Rekomendacja: zostać przy (a).
6. **Trening.** Propozycja wzoru: pasek treningu (10 trafień = +1 punkt świeżej statystyki), seria ×1 / ×1,25 / ×1,5 /
   ×2, ulepszone centrum ×1–×2 i **malejący zysk tej jednej statystyki** liczony od puli poziomu. Wtedy jedna mini-gra
   daje ok. połowę tego, co sześć (z potworami +6…+16 pp zamiast +22…+26 pp pod koniec gry), a gracz trenujący 20% czasu
   ma pod koniec 7. biomu ok. 45% puli z treningu. Bez malejącego zysku ten sam trening daje 130% puli i jedna
   mini-gra (Kondycja) jest tak samo dobra jak sześć. Wzór dotyka zatwierdzonej D-050 („+1 za trafienie”, „bez limitu”).

## Skąd liczby

- **Silnik:** walki liczy prawdziwy silnik v3 (ten sam kod co testy i tabela balansu), na postaciach wzorcowych z
  `tools/walka/wzorcowe.py`. Każda para to 800 walk na stałych ziarnach (strażnik w części 3: 1000), więc wynik da się
  powtórzyć co do cyfry.
- **Potwory biomów 2–8 nie istnieją.** Zastępczo liczę potwory lasu przeskalowane do poziomu gracza i pomnożone
  „mnożnikiem biomu” k (ciosy i życie razy k, Pancerz potwora bez zmian).
- **Tempo:** krzywa doświadczenia 11,71 × L^1,6 z `tempo.py`; z niej wynika, ile minut walki trzeba do każdego poziomu.
  Plan 600 minut do ostatniego biomu z D-076 (korekta Karola): rosnący 30/45/60/75/95/125/170 albo równy ok. 86 min.
  Gracz, który trenuje część czasu, walczy mniej, więc na granicach biomów jest niżej (tabela „Tempo” w pełnym wyniku).
- **Drzewka:** ceny i premie czytam z `src/shared/SkillTreeData.luau` (cena poziomu węzła = (10 + 5 × głębokość) ×
  numer poziomu, korzeń 10). To robocze liczby Pawła z 15.11 — jeśli się zmienią, kalkulator przeliczy wszystko sam.

## Założenia „przyjęte, do zmiany”

| Co | Przyjęte | Gdzie w kodzie |
|---|---|---|
| Ile trwa 8. biom (tylko do „wyjścia” z niego) | 230 min (plan rosnący), 86 min (równy) | `ZALOZENIA["osmy_biom_min"]` |
| Gracz oczekiwany / dużo trenujący | 20% / 40% czasu w Training Center, trening rozkładem swojej klasy | `udzial_treningu`, `udzial_treningu_duzo` |
| Cel trudności zwykłych potworów na wejściu do biomu | 85% w lesie, liniowo do 75% w kryształowym („coraz trudniej”, D-076) | `cel_zwykle_wejscie` |
| Gdzie stoi troll i strażnik biomu | o jeden poziom niżej niż gracz na wyjściu z biomu | `czesc_1` |
| Mini-gra: trafień na minutę, średnia seria | 30 trafień/min, średni mnożnik serii ×1,3 | `trafienia_na_min`, `combo_srednie` |
| Pasek treningu, malejący zysk | 10 trafień na punkt; h = 10% puli; M = 1 / (1 + W / (h × pula))² | `trafien_na_punkt`, `polowa_udzialu`, `wykladnik` |
| Ulepszone centrum | ×1,0 / 1,15 / 1,3 / 1,45 / 1,6 / 1,75 / 1,9 / 2,0; poziom centrum najwyżej numer biomu | `centrum` |
| Kopalnie Twierdzy | od 25. poziomu gracza (odpowiedź Karola na pytanie 9), kolejny poziom budynku co 5 poziomów gracza, 1. poziom kopalni = 15% Złota z walk na godzinę | `kopalnie_od_poziomu`, `poziom_budynku_co`, `baza_kopalni` |
| Ile godzin dziennie gracz gra | 2 h (do rachunku offline) | `godzin_gry_dziennie` |
| Ewolucje peta | 3 (poziomy peta 10 / 20 / 30), kopie peta 2 / 3 / 5, tokeny 60 / 180 / 450 | `ewolucje`, `kopie_na_ewolucje`, `tokeny_na_ewolucje` |
| Jajko | pięć petów z szansami 50 / 25 / 15 / 8 / 2%, ceny 1 000 i 10 000 Złota (D-052 mówi o ok. 1% na legendarnego w najdroższym jajku za ok. 10 tys.) | `szanse_jajka`, `ceny_jajek` |
| Źródła Gemów do porównania | „łup ×5”, „kamienie milowe” (+10 Gemów za poziom, +100 za pierwszego strażnika biomu), kopalnia diamentów 30 Gemów/h ×1,25 na poziom budynku | `zrodla_gemow` |

## 1. Pancerz punktowy a obrażenia potworów w ośmiu biomach

**Co się dzieje z Pancerzem.** Pancerz gracza (punkty z puli i z przedmiotów) i cios potwora rosną z poziomem liniowo,
dlatego przy potworach rosnących jak w lesie procent ciosu, który przechodzi, jest na każdym poziomie prawie taki sam.
Pancerz punktowy z D-062 nie traci więc znaczenia w dalszych biomach i nie robi z nikogo czołgu — o ile potwory biomu
nie są słabsze od leśnych. Limit z D-091 (przechodzi zawsze co najmniej 25%) działa tak:

- **Wojownik wzorcowy jest przy limicie od lasu.** Zwykły cios Slime'a i Wilka przechodzi u niego w 25% na każdym
  poziomie (bez treningu, przy k = 1). Krytyk przechodzi w ok. 68%, cios trolla w ok. 33%. Dodatkowy Pancerz pomaga mu
  więc tylko na mocne ciosy. To spełnia D-091 („Wojownik szybciej dochodzi do limitu”), ale znaczy też, że mini-gra
  Pancerza jest dla Wojownika mało warta przeciw zwykłym potworom (w części 6 „tylko Pancerz” daje mu najmniej).
- **Zwiadowca i Mag** przepuszczają 38–63% zwykłego ciosu (więcej bez treningu). Żeby dojść do limitu, gracz oczekiwany potrzebowałby
  z treningu od kilku punktów Pancerza w lesie do ok. 109 (Zwiadowca) i 87 (Mag) w ostatnim biomie.

**Jak muszą rosnąć potwory.** Gracz, który trenuje, ma więcej statystyk niż postać wzorcowa tego samego poziomu, więc
potwory dalszych biomów muszą być mocniejsze od leśnych. Kalkulator dobrał mnożnik k (ciosy i życie potwora razy k)
tak, żeby gracz trenujący 20% czasu wygrywał ze zwykłymi potworami na wejściu do biomu 85% w lesie, a potem coraz
mniej, do 75% w ostatnim biomie.

| Biom (plan rosnący) | Poziom wejście → wyjście (20% treningu) | k | Zwykłe na wejściu: bez treningu / 20% / 40% | Strażnik na wyjściu: bez treningu / 20% / 40% | Cios zwykłego potwora fizycznego: wejście → wyjście |
|---|---|---:|---|---|---|
| Las | 1 → 10 | 1,04 | 83% / 83% / 83% | 47% / 65% / 76% | 19 → 76 |
| Bagno | 10 → 17 | 1,14 | 73% / 83% / 87% | 24% / 49% / 60% | 83 → 131 |
| Dżungla | 17 → 23 | 1,19 | 68% / 82% / 86% | 16% / 46% / 57% | 137 → 180 |
| Pustynia | 23 → 30 | 1,25 | 62% / 80% / 85% | 9% / 40% / 53% | 189 → 242 |
| Góry z tundrą | 30 → 37 | 1,30 | 56% / 79% / 84% | 6% / 38% / 51% | 251 → 307 |
| Lodowiec | 37 → 46 | 1,35 | 51% / 78% / 84% | 4% / 34% / 47% | 318 → 392 |
| Wulkaniczny | 46 → 56 | 1,40 | 46% / 77% / 83% | 2% / 32% / 46% | 406 → 491 |
| Kryształowy | 56 → 69 | 1,47 | 39% / 75% / 81% | 1% / 28% / 41% | 515 → 630 |

Plan równy daje prawie te same mnożniki (1,04 / 1,17 / 1,23 / 1,28 / 1,32 / 1,36 / 1,40 / 1,45).

**Co z tego wynika.**
- Mnożnik rośnie spokojnie, ok. +6% na biom, i jest prawie taki sam w obu planach. Można go wpisać w dane potworów
  jako stały mnożnik biomu (np. k ≈ 1,04 + 0,06 × (numer biomu − 1)).
- Pancerz gracza oczekiwanego rośnie szybciej niż Pancerz postaci bez treningu, więc u Wojownika zwykły cios
  przechodzi dalej w 25%. U postaci bez treningu przy k > 1,2 zaczyna przechodzić więcej (27–38%) — tu Pancerz
  zaczyna mieć znaczenie, czyli dalsze biomy nagradzają trening Pancerza, tak jak chciał Karol w D-076.
- Gracz, który w ogóle nie trenuje, od Pustyni przegrywa ze strażnikiem prawie zawsze. To zgodne z D-076 („gracz ma
  myśleć o statystykach i trenować”, „gra nie może być dziecinnie prosta”), ale to ostra kara — do decyzji (wybór 2).
- Strażnik na wyjściu spada z 65% w lesie do 28% w ostatnim biomie u gracza oczekiwanego, czyli ostatnie bramy są
  naprawdę trudne, ale do przejścia (trening, buildy, pety i drzewko dają jeszcze więcej, czego tu nie liczę).

## 2. Drzewko Twierdzy: mnożnik procentowy razy ulepszenie budynku

D-056 mówi: budynek daje bazę, drzewko ją mnoży. Dzisiejsze drzewko (`SkillTreeData.luau`) daje kopalni przy pełnych
poziomach +20% (MINING), +10% (BIG CARTS) i +25% w premii czasowej (RUSH HOUR); gracz ma też +35% Złota (GOLD I i II)
i +25% Złota offline.

**Mnożnik z drzewka nie jest problemem.** Pełne drzewko daje ×1,30, jeśli premie Twierdzy się dodaje, ×1,65 z gałęzią
gracza, ×1,78, jeśli gałęzie się mnoży, i ×2,78, jeśli mnoży się wszystko razem z premią czasową i offline. To stałe
liczby — nie rosną z poziomem budynku.

**Problemem jest krzywa budynku.** Kalkulator porównuje dochód kopalni Złota z Złotem z walk na godzinę gry na tym
samym poziomie gracza (kopalnie od 25. poziomu, kolejny poziom budynku co 5 poziomów gracza):

| Krzywa budynku | Kiedy kopalnia daje więcej niż walka (bez drzewka / drzewko Twierdzy / drzewko Twierdzy i gracza mnożone) | Kopalnia 9. poziomu względem walki (te same trzy) |
|---|---|---|
| liniowa (n) | nigdy / nigdy / nigdy | 53% / 69% / 95% |
| potęgowa (n^1,5) | 6. poziom budynku / 4. (ok. 100%) / 3. | 160% / 208% / 285% |
| wykładnicza ×1,25 | nigdy / nigdy / nigdy | 35% / 46% / 63% |
| wykładnicza ×1,6 | 7. / 6. / 5. (ok. 100%) | 254% / 330% / 453% |

**Praca offline zmienia wszystko.** Jeśli kopalnia pracuje także wtedy, gdy gracza nie ma (Twierdza „chodzi sama”,
D-049), liczy się doba, a nie godzina gry. Przy 2 godzinach gry dziennie i łagodnej krzywej ×1,25 kopalnia daje
15–35% Złota z walk, gdy pracuje tylko w czasie gry; 45–106%, gdy pracuje offline do 8 godzin w połowie tempa;
180–423%, gdy pracuje całą dobę (z pełnym drzewkiem 321–754%). Wtedy Twierdza zarabia kilka razy więcej niż walka.

**Wartość węzła rośnie z budynkiem, a cena nie.** Jeden poziom MINING (+4%) kosztuje 15–75 Gemów niezależnie od
budynku, a daje przy kopalni 9. poziomu od 6 razy (×1,25) do 43 razy (×1,6) więcej Złota niż przy 1. poziomie.

**Training Center w drzewku Twierdzy:** wszystkie mini-gry +40%, a Siła, Zręczność, Szczęście i Pancerz po +20%
więcej. Kondycja i Inteligencja nie mają własnego węzła — przy malejącym zysku z części 6 to ok. 5% mniej punktów
w tych dwóch mini-grach, czyli niewiele, ale wygląda na przeoczenie.

**Propozycja:** premie Twierdzy dodawać, a gałąź gracza GOLD niech nie działa na kopalnię (tak jak D-087 robi to
z Diamentami); krzywa budynku najwyżej ×1,25 na poziom albo liniowa; dochód offline z limitem (np. 8 godzin w połowie
tempa); cel: kopalnie najwyżej 30–50% Złota z walk na godzinę gry. Cenę węzła Twierdzy można wiązać z poziomem budynku.

## 3. Ewolucja petów: shardy, tokeny krainy, Shard Ewolucji

Model z D-058: ewolucja kosztuje kopie tego peta (jedna kopia = jeden shard), jeden Shard Ewolucji (tylko ze strażnika
biomu) i tokeny krainy. Gracz wzorcowy farmi Strażnika Gaju (10. poziom): na 10. poziomie wygrywa 36%, na 12. — 72%,
na 15. — 97%; jedna próba trwa z dojściem ok. 80–94 s.

| Szansa na Shard (za wygraną) | Prób na jeden Shard: średnio / połowa graczy / 90% graczy | Minut (gracz 2 poziomy wyżej) | Trzy ewolucje jednego peta | 10 petów biomu po 3 ewolucje |
|---:|---|---|---:|---:|
| 5% | 28 / 19 / 63 | 41 / 28 / 93 | ok. 2 h | ok. 21 h |
| **10% (dziś)** | 14 / 10 / 31 | 21 / 15 / 46 | ok. 1 h | ok. 10 h |
| 15% | 9 / 7 / 21 | 14 / 10 / 31 | 41 min | ok. 7 h |
| 20% | 7 / 5 / 15 | 10 / 7 / 22 | 31 min | ok. 5 h |
| 25% | 6 / 4 / 12 | 8 / 6 / 18 | 25 min | ok. 4 h |

**Pech.** Przy 10% co dziesiąty gracz czeka na Shard ponad 31 prób (ponad 45 minut). Ochrona przed pechem — Shard
gwarantowany po 20 wygranych bez Sharda — obniża średnią do 12 prób, a najgorszy przypadek to 20 wygranych
(ok. 28 prób).
Shard nie jest płatnym losowaniem, więc taka ochrona nie zmienia zasad Roblox dla płatnych przedmiotów losowych.

**Tokeny krainy** (dziś 1 + 30% szansy na drugi za zwykłego potwora, 5 + 50% za strażnika) to ok. 2,2 na minutę walki
(ok. 130 na godzinę). Propozycja 60 / 180 / 450 tokenów na trzy ewolucje to 27 / 82 / 205 minut zwykłych walk —
tokeny rosną naturalnie razem z graniem w krainie.

**Kopie z jajek to wąskie gardło.** Przy jajku z pięcioma petami (50 / 25 / 15 / 8 / 2%) i 10 kopiach na komplet ewolucji
pospolity pet potrzebuje średnio 22 jajek (2,3 godziny walki na Złoto przy jajku za 1 000), a legendarny 550 jajek
(58 godzin przy jajku za 1 000, 575 godzin przy jajku za 10 000). Przy szansie z D-052 (ok. 1%) byłoby dwa razy więcej.
Wariant „kopii według rzadkości” (pospolity 10, zwykły 8, rzadki 6, epicki 4, legendarny 3) skraca to do 200 jajek dla
legendarnego, czyli dalej 21–209 godzin.

**Propozycja:** szansa na Shard 10–15% z ochroną przed pechem (gwarancja po 2 / szansa wygranych); tokeny 60 / 180 /
450; liczba kopii zależna od rzadkości, a dla legendarnych 1–2 kopie albo inne źródło kopii (np. nagroda za
strażnika). Odpowiedź Karola na pytanie 41 („wszystkie pety mogą ewoluować, tylko niektóre mają legendarne ewolucje”)
pasuje do tego — legendarna ewolucja może mieć wyższą cenę w tokenach, a nie w kopiach.

## 4. Gemy na drzewka a czas gry

Drzewka w dzisiejszych danych kosztują: **Player 8 105, Fortress 5 860, Pets 6 685, razem 20 650 Gemów.** Dziś Gemy
wypadają tylko z łupu: zwykły potwór 1–1,2%, troll 5%, strażnik 15% szansy na 1 Gem za wygraną.

| Do końca biomu (plan rosnący) | Poziom | Dziś | Łup ×5 | Łup ×5 + kamienie milowe | To samo + kopalnia diamentów |
|---|---:|---:|---:|---:|---:|
| Las (30 min) | 11 | 0 | 2 | 202 (2,5% drzewka Player) | 202 (2,5%) |
| Pustynia (210 min) | 34 | 3 | 13 | 743 (8,8%) | 794 (9,3%) |
| Wulkaniczny (600 min) | 65 | 7 | 35 | 1 365 (16,7%) | 2 009 (24,7%) |
| Kryształowy (830 min) | 79 | 10 | 48 | 1 628 (19,6%) | 3 135 (38,1%) |

W planie równym liczby na końcu 10 godzin są te same (tyle samo walk), a w pierwszych biomach gracz ma więcej Gemów,
bo las trwa dłużej.

**Najważniejsze: sloty umiejętności.** Sloty są węzłami gałęzi Skills (D-055, D-088). Pierwszy kosztuje z korzeniem
25 Gemów, drugi razem 70, trzeci razem 125. Dziś gracz bez płacenia **nie kupi w 10 godzin nawet pierwszego slotu**;
z „łupem ×5” pierwszy slot przychodzi dopiero w Lodowcu (53. poziom). Z kamieniami milowymi wszystkie trzy sloty są
w lesie. Silnik i tabela balansu zakładają sloty od 1., 5. i 10. poziomu — bez slotu postać nie używa umiejętności;
dla porównania postać z jedną pasywką i bez aktywnej wygrywa z potworami 10. poziomu tylko 31–34% zamiast ok. 70%
(tabela g w `ZMIANY_SESJA_1611.md`).

**Ile trzeba.** Żeby gracz bez płacenia kupił w 10 godzin 25% / 50% / 100% drzewka Player, potrzebuje średnio
**ok. 200 / 400 / 810 Gemów na godzinę** (dziś 0,6). Kamienie milowe (+10 za poziom, +100 za strażnika) dają ok. 135
na godzinę, z kopalnią diamentów ok. 200.

**Propozycja do decyzji:** najpierw ustalić cel („ile drzewka ma gracz bez płacenia po 10 godzinach”, np. 25% drzewka
Player i korzenie dwóch pozostałych zakładek). Potem: Gemy za kamienie milowe (poziomy, pierwszy strażnik biomu), łup
×5 i kopalnia diamentów od 25. poziomu. Sloty umiejętności albo tanie i blisko korzenia (dziś są — ale za Gemy, których
nie ma), albo za poziom postaci tak jak w modelu balansu.

## 5. Pytanie 40: Wojownik z tarczą i unikiem

Pytanie jest dalej otwarte: Karol odpowiedział 14.11 „zostawiam to Cloudowi do rozwiązania”, a D-073 (✅, oba podpisy)
zmieniła jego tło — blok i unik ma każda klasa, tarcza daje Wojownikowi większy blok, wysokość szans ustala balans.
Podejście (a) z pytania jest już w silniku v3: limit uniku klasy (Wojownik 24,2%, Mag 41,9%, Zwiadowca 50%), a
Zręczność daje Wojownikowi też mnożnik krytyka (pomysł z D-091).

Kalkulator sprawdził „najgorszy przypadek”: Wojownik z tarczą wkłada cały trening (¼, ½ albo całą pulę poziomu)
w Zręczność. Przeciwnicy w pojedynkach mają ten sam wkład rozdany rozkładem swojej klasy. Poziom 10 (poziom 30 daje to
samo co do 1 pp).

| Podejście | Wojownik: cały trening (½ puli) w Zręczność — z potworami / z Wojownikiem / Zwiadowcą / Magiem | Ten sam trening rozkładem klasy — z potworami | Unik + blok Wojownika (trening w Zr.) | Różnica klas bez treningu (potwory) | Długość walki z potworami (bez treningu) |
|---|---|---:|---|---:|---|
| dziś = (a) limit uniku klasy | 84% / 28% / 31% / 32% | 96% | 18% + 27% | 3,9 pp | 20 tur, 32 s |
| (a') niższy limit: 15% | 81% / 25% / 25% / 28% | 96% | 11% + 30% | 5,2 pp | 20 tur, 32 s |
| (b) połowa przyrostu Zręczności z treningu | 81% / 23% / 26% / 28% | 96% | 15% + 28% | 3,9 pp | 20 tur, 32 s |
| (c) blok i unik się nie sumują | 80% / 24% / 24% / 27% | 96% | 18% + 15% | 5,6 pp | 19 tur, 31 s |

**Co z tego wynika.**
- Nabijanie Zręczności przez Wojownika się nie opłaca: krzywa uniku nasyca się przy limicie klasy, więc z każdą porcją
  treningu Wojownik „zręczny” coraz bardziej przegrywa z Wojownikiem trenującym rozkładem klasy. Przy całej puli
  w Zręczności unik + blok to najwyżej ok. 47% ciosów, a zablokowany cios i tak przechodzi w 25%.
- (a') i (b) tylko dalej osłabiają wybór, który i tak jest słaby; (b) wymaga osobnej reguły treningu dla jednej klasy.
- (c) zabiera Wojownikowi połowę bloku przy dużej Zręczności, ale przy okazji całkiem wyłącza blok Zwiadowcy i Maga
  (ich unik jest wyższy niż 5% bloku), co w praktyce cofa D-073. Różnica klas rośnie z ok. 4 do ok. 6 pp.
- Ryzyko „Wojownik z samą Inteligencją” (Paweł) też się nie potwierdza: tabela (h) w `ZMIANY_SESJA_1611.md` i część 6
  tutaj („tylko Inteligencja” u Wojownika: +15 pp zamiast +25 pp, w pojedynku 22%).

**Rekomendacja:** zostać przy (a) w dzisiejszej postaci; (b) i (c) nie wprowadzać. Komentarz pod pytanie jest
w raporcie dla panelu.

## 6. Trening: przyrost za trafienie i za serię, bez nadużywania jednej mini-gry

**Problem.** D-050 (✅) mówi: każde trafienie daje +1 do statystyki, seria daje więcej, grindu nie ograniczamy.
Pula statystyk z poziomów to 30 punktów na 1. poziomie i ok. 670 na 65. Mini-gra z ok. 30 trafieniami na minutę dałaby
przy +1 za trafienie 30 punktów na minutę — ok. 8 razy więcej niż walka w lesie i ok. 40 razy więcej niż walka pod
koniec gry. Nawet przy 3,9 punktu na minutę (wzór niżej bez malejącego zysku) gracz trenujący 20% czasu ma po 10
godzinach 130% puli z treningu, a jedna mini-gra (Kondycja) jest tak samo dobra jak sześć.

**Propozycja wzoru (do prototypu mini-gier):**

```
pasek[s]  += C × K                               przy każdym trafieniu w mini-grze statystyki s
próg[s]    = N0 × (1 + W[s] / (h × pula(L)))²    tyle trzeba nabić, żeby statystyka s dostała +1
gdy pasek[s] ≥ próg[s]:  W[s] += 1, statystyka s +1, pasek[s] −= próg[s], ekran: „+1 Siła”
pudło: seria = 0 (pasek zostaje)

N0 = 10                      trafień bez serii na +1 punkt świeżej statystyki
K  = 1 / 1,25 / 1,5 / 2      seria 0–4 / 5–9 / 10–19 / od 20 trafień bez pudła
C  = 1 / 1,15 / 1,3 / 1,45 / 1,6 / 1,75 / 1,9 / 2   poziom centrum 1–8 (najwyżej numer odblokowanego biomu)
h  = 0,10                    malejący zysk liczony od 10% puli poziomu
W[s]                         wszystkie punkty wytrenowane dotąd w statystyce s (zapis w profilu)
pula(L) = 30 + 10 × (L − 1)  punkty statystyk z poziomu gracza
```

To jest ten sam wzór co „punkty za trafienie = C × K × M / N0” z `progresja.py` (M = 1 / (1 + W / (h × pula))²).
W danych prototypu (`progi_serii` [5, 10, 20], `za_trafienie` jako liczby całkowite) da się to zapisać jako jednostki
paska: `za_trafienie` = [4, 5, 6, 8], próg paska 40 × (1 + W / (0,1 × pula))², a centrum jako mnożnik paska.
Dzisiejsza seria prototypu 1 / 2 / 3 / 4 jest bardziej stroma; przy malejącym zysku i średniej serii ×2,5 daje to
ok. 40% więcej punktów w całej grze (zamiast 45% puli ok. 62%), a nie dwa razy więcej.

**Co daje (plan rosnący, gracz trenuje 20% czasu):**

| | Las (10. poz.) | Pustynia (30. poz.) | Wulkaniczny (56. poz.) |
|---|---:|---:|---:|
| Punkty z treningu: sześć mini-gier po równo | 18 (15% puli) | 108 (34%) | 292 (50%) |
| … rozkładem klasy | 17 (14%) | 98 (31%) | 259 (45%) |
| … tylko jedna mini-gra (Kondycja) | 10 (8%) | 47 (15%) | 117 (20%) |
| Bez malejącego zysku (każda polityka tyle samo) | 23 (20%) | 209 (65%) | 751 (129%) |
| Wygrane z potworami: trening rozkładem klasy (Wojownik / Zwiadowca / Mag) | +11 / +10 / +10 pp | +21 / +19 / +17 pp | +25 / +24 / +22 pp |
| … tylko jedna mini-gra: najlepsza (Kondycja) | +7 / +7 / +8 pp | +12 / +11 / +13 pp | +16 / +14 / +16 pp |
| … tylko jedna mini-gra: najsłabsza | +4 / +4 / +3 pp | +7 / +6 / +5 pp | +9 / +7 / +6 pp |
| Pojedynek „tylko jedna” z „rozkładem klasy” (ten sam czas) | 37–45% | 23–39% | 15–34% |

**Co z tego wynika.**
- Siedzenie w jednej mini-grze nie wygrywa: daje ok. 40% punktów i ok. połowę zysku w walce, a w pojedynku z kimś, kto
  trenował tyle samo, ale po kolei, przegrywa. Najlepiej opłaca się zmieniać mini-gry — wtedy wszystkie sześć są
  używane.
- Tempo jednej mini-gry spada o połowę po ok. 1 minucie w lesie i ok. 4–5 minutach pod koniec gry; awans poziomu je
  przywraca (pula rośnie). Ekran powinien to pokazywać (pasek „zmęczenia” albo strzałka do innej mini-gry).
- Mini-gry nie są równe co do pożytku z punktu: Kondycja daje każdej klasie najwięcej, Zręczność, Szczęście
  i Inteligencja (u Maga) najmniej. Wagi na mini-gry prawie nic nie zmieniają, bo przy malejącym zysku punkty rosną
  wolniej niż tempo (Kondycja o 30% wolniej daje tylko 11% mniej punktów) — różnice biorą się z wartości statystyk
  w silniku (tabela c w `ZMIANY_SESJA_1611.md`), nie z mini-gier.
- Trening pasuje do 10 godzin: gracz trenujący 20% czasu jest na granicach biomów 1–9 poziomów niżej niż w planie bez
  treningu (tabela „Tempo”), ale silniejszy, a mnożnik biomu z części 1 jest dobrany właśnie do niego.
- Bez trybu AFK (Karol przy D-050) — wzór go nie potrzebuje.

## Wybory dla ludzi

1. **Mnożnik biomu potworów** — propozycja k ≈ 1,04 + 0,06 × (numer biomu − 1) dla ciosów i życia; cel trudności 85% → 75%
   ze zwykłymi na wejściu. Wyższy cel = łatwiej, niższy = trudniej.
2. **Gracz, który nie trenuje** — dziś od Pustyni prawie nie pokona strażnika. Zostawić (trening obowiązkowy, jak
   w D-076), czy złagodzić (mniejszy k, mocniejsze przedmioty z poziomu)?
3. **Twierdza** — krzywa budynku (liniowa albo ×1,25), czy premie gracza (GOLD) działają na kopalnię, limit offline,
   cel „kopalnie najwyżej 30–50% Złota z walk”.
4. **Shard Ewolucji** — szansa 10% czy 15%, ochrona przed pechem (tak / nie, po ilu wygranych).
5. **Kopie peta na ewolucję** — płasko (10 na komplet) czy według rzadkości; co z legendarnymi (1–2 kopie, inne źródło).
6. **Gemy** — cel „ile drzewka po 10 godzinach bez płacenia”; które źródła (kamienie milowe, łup ×5, kopalnia od 25.
   poziomu); czy sloty umiejętności zostają za Gemy.
7. **Pytanie 40** — zostać przy (a); (b) i (c) odrzucić.
8. **Trening** — pasek treningu zamiast „+1 za trafienie”, malejący zysk tej samej statystyki (h = 10% puli), seria
   1 / 1,25 / 1,5 / 2 (albo prototypowe 1 / 2 / 3 / 4), centrum ×1 → ×2. Węzły Kondycji i Inteligencji w gałęzi Training
   Center drzewka Twierdzy (dziś ich nie ma).

## Konflikty z kanonem (do dopisania w `Pytania otwarte.md` przez agenta, który prowadzi sejf)

- **D-050 ✅ („+1 do statystyki za trafienie”, „grindu nie ograniczamy”)** a propozycja z części 6: pasek treningu
  (0,1 punktu za trafienie świeżej statystyki) i malejący zysk tej samej statystyki. Malejący zysk nie jest limitem
  (zawsze coś daje, a inna mini-gra i awans przywracają tempo), ale to zmiana zatwierdzonej decyzji — potrzebna zgoda.
- **D-055 / D-088 ✅ (sloty z drzewka) i D-057 ✅ (węzły za Gemy)** razem z dzisiejszym łupem: gracz bez płacenia nie ma
  slotu w 10 godzin. To nie sprzeczność decyzji, tylko skutek liczb — ale bez zmiany tempa Gemów albo ceny slotów
  model walki (sloty od 1., 5. i 10. poziomu) nie odpowiada grze.
- **D-073 ✅** a wariant (c) z pytania 40: (c) wyłączyłby blok klasom z unikiem powyżej 5% — dlatego go odradzam.

## Jak policzyć jeszcze raz

```
python -B tools/walka/progresja.py --md wynik.md                 # wszystko, ok. 4 minuty w 3 procesach
python -B tools/walka/progresja.py --czesci 2,3,4                # Twierdza, pety, Gemy — kilka sekund
python -B tools/walka/progresja.py --procesy 1 --ziaren 400      # na zajętym komputerze
python -B -m unittest tools/walka/test_progresja.py -v           # testy kalkulatora (ok. 10 s)
python -B -m unittest discover -s tools/walka -p "test_*.py"     # wszystkie testy walki (ok. 5 minut)
```

Założenia zmienia się w słowniku `ZALOZENIA` na początku `progresja.py`; ceny drzewek kalkulator czyta sam
z `src/shared/SkillTreeData.luau`.

**Testy (17.11):** `python -B -m unittest discover -s tools/walka -p "test_*.py"` — **88/88 OK** (73 dotychczasowe testy
silnika i 15 nowych testów kalkulatora, ok. 5 minut). Nowe testy pilnują m.in. wzoru ceny drzewek, zgodności krzywej
tempa z `tempo.py`, tego, że jedna mini-gra daje mniej niż 60% punktów sześciu, że wariant „jedna szansa” daje
dokładnie max(unik, blok) i po wyjściu zostawia silnik bez zmian, oraz mnożnika potworów biomu.

## Czego nie sprawdziłem

- **Potworów dalszych biomów** — nie istnieją; liczę leśne przeskalowane mnożnikiem. Prawdziwe potwory z ostrzejszymi
  cechami (np. biom magów) zmienią część 1.
- **Przedmiotów, drzewka gracza i petów w sile postaci** — gracz w modelu to postać wzorcowa z punktami z poziomu
  i treningu. Premie procentowe z drzewka (Stats +10–25%) i petów podniosą siłę ponad to, co tu policzone.
- **Prawdziwego tempa mini-gier** — 30 trafień na minutę i średnia seria ×1,3 to założenia; prototyp (`swiat/trening_proba`,
  inny agent) je zmierzy. Z jego plików przeczytałem tylko ustawienia serii i funkcję przyrostu.
- **Cen jajek, budynków i ulepszeń centrum w Złocie** — liczę tylko dochód, nie koszty i zwrot.
- **Studio** — nic nie było uruchamiane w Roblox Studio; to rachunki w Pythonie.

## Pełny wynik kalkulatora

Poniżej dokładny wynik `python -B tools/walka/progresja.py --ziaren 800` (ziarna od 1).

### Tempo: poziom gracza na granicach biomów

Ta sama krzywa co w `tempo.py` (11,71 × L^1,6, cykl walki gracza wzorcowego). Plan rosnący i równy z D-076; 8. biom: 230 min (rosnący) i 86 min (równy) — przyjęte, tylko do „wyjścia” z ostatniego biomu. Gracz, który trenuje 20% czasu, walczy 80% czasu, więc jest niżej.

| Biom | Rosnący: minuty | poziom bez treningu | z 20% treningu | Równy: minuty | poziom bez treningu | z 20% treningu |
|---|---|---|---|---|---|---|
| Las | 0–30 | 1 → 11 | 1 → 10 | 0–86 | 1 → 20 | 1 → 18 |
| Bagno | 30–75 | 11 → 19 | 10 → 17 | 86–171 | 20 → 30 | 18 → 27 |
| Dżungla | 75–135 | 19 → 26 | 17 → 23 | 171–257 | 30 → 39 | 27 → 34 |
| Pustynia | 135–210 | 26 → 34 | 23 → 30 | 257–343 | 39 → 46 | 34 → 40 |
| Góry z tundrą | 210–305 | 34 → 43 | 30 → 37 | 343–429 | 46 → 53 | 40 → 46 |
| Lodowiec | 305–430 | 43 → 53 | 37 → 46 | 429–514 | 53 → 59 | 46 → 51 |
| Wulkaniczny | 430–600 | 53 → 65 | 46 → 56 | 514–600 | 59 → 65 | 51 → 56 |
| Kryształowy | 600–830 | 65 → 79 | 56 → 69 | 600–686 | 65 → 70 | 56 → 61 |

### 1. Pancerz punktowy a obrażenia potworów w ośmiu biomach

#### Plan rosnący (600 min do ostatniego biomu; gracz oczekiwany trenuje 20,0% czasu)

Mnożnik biomu k = o ile ciosy i życie potworów biomu są większe od potwora lasu tego samego poziomu (dobrany symulacją tak, żeby gracz oczekiwany na wejściu wygrywał ze zwykłymi potworami tyle, ile w kolumnie „Cel”). Wygrane: średnio trzy klasy; „gołe poziomy” = ta sama postać bez treningu, „dużo treningu” = 40,0% czasu w Training Center. Wyjście: zwykłe potwory poziomu gracza, troll i strażnik o poziom niżej.

| Biom | Poziom wejście → wyjście | k | Cel | Zwykłe na wejściu: gołe / oczekiwany / dużo | Zwykłe na wyjściu (oczekiwany) | Troll / strażnik na wyjściu: gołe | oczekiwany | dużo |
|---|---|---:|---:|---|---:|---|---|---|
| Las | 1 → 10 | 1,04 | 85,0% | 83,0% / 83,0% / 83,0% | 89,7% | 64,2% / 46,5% | 76,7% / 65,2% | 83,5% / 75,7% |
| Bagno | 10 → 17 | 1,14 | 83,6% | 73,1% / 82,8% / 86,5% | 85,3% | 42,2% / 24,4% | 66,8% / 49,0% | 74,5% / 60,4% |
| Dżungla | 17 → 23 | 1,19 | 82,1% | 67,8% / 81,7% / 86,2% | 84,8% | 29,6% / 15,7% | 61,3% / 46,3% | 70,2% / 56,8% |
| Pustynia | 23 → 30 | 1,25 | 80,7% | 62,2% / 80,4% / 85,4% | 82,5% | 22,5% / 9,3% | 56,7% / 40,2% | 66,8% / 52,5% |
| Góry z tundrą | 30 → 37 | 1,30 | 79,3% | 56,4% / 78,7% / 84,4% | 81,5% | 16,6% / 5,8% | 52,9% / 37,8% | 65,1% / 50,6% |
| Lodowiec | 37 → 46 | 1,35 | 77,9% | 51,4% / 77,8% / 83,7% | 80,0% | 12,2% / 3,6% | 49,4% / 34,1% | 62,6% / 47,2% |
| Wulkaniczny | 46 → 56 | 1,40 | 76,4% | 46,4% / 76,5% / 82,6% | 78,9% | 8,5% / 2,2% | 46,9% / 32,4% | 60,9% / 45,7% |
| Kryształowy | 56 → 69 | 1,47 | 75,0% | 39,3% / 74,5% / 80,7% | 76,4% | 5,4% / 0,9% | 41,7% / 27,9% | 55,5% / 40,6% |

Pancerz gracza (punkty po przeliczniku klasy) i cios zwykłego potwora fizycznego biomu (średnio Slime i Wilk × k, bez krytyka, rozrzut 100%). „Przechodzi” = część ciosu po Pancerzu (najmniej 25,0% — limit D-091). „Do limitu” = ile punktów Pancerza z treningu brakuje graczowi oczekiwanemu, żeby zwykły cios tego biomu dochodził tylko w 25,0%.

| Biom | Gdzie | Poziom | Cios potwora | Wojownik: Pancerz gołe / oczek. → przechodzi gołe / oczek. | do limitu | Zwiadowca: Pancerz gołe / oczek. → przechodzi gołe / oczek. | do limitu | Mag: Pancerz gołe / oczek. → przechodzi gołe / oczek. | do limitu |
|---|---|---:|---:|---|---:|---|---:|---|---:|
| Las | wejście | 1 | 19 | 16 / 16 → 25,0% / 25,0% | 0 | 10 / 10 → 46,2% / 46,2% | 2 | 11 / 11 → 44,0% / 44,0% | 2 |
| Las | wyjście | 10 | 76 | 67 / 71 → 25,0% / 25,0% | 0 | 40 / 42 → 47,1% / 44,8% | 9 | 44 / 47 → 42,5% / 37,9% | 6 |
| Bagno | wejście | 10 | 83 | 67 / 71 → 25,0% / 25,0% | 0 | 40 / 42 → 51,5% / 49,4% | 12 | 44 / 47 → 47,3% / 43,1% | 9 |
| Bagno | wyjście | 17 | 131 | 106 / 117 → 25,0% / 25,0% | 0 | 63 / 68 → 52,2% / 48,4% | 18 | 69 / 76 → 47,5% / 42,2% | 13 |
| Dżungla | wejście | 17 | 137 | 106 / 117 → 25,0% / 25,0% | 0 | 63 / 68 → 54,1% / 50,4% | 21 | 69 / 76 → 49,7% / 44,5% | 15 |
| Dżungla | wyjście | 23 | 180 | 138 / 159 → 25,0% / 25,0% | 0 | 82 / 92 → 54,5% / 48,9% | 26 | 91 / 103 → 49,7% / 42,9% | 18 |
| Pustynia | wejście | 23 | 189 | 138 / 159 → 26,8% / 25,0% | 0 | 82 / 92 → 56,6% / 51,3% | 30 | 91 / 103 → 52,1% / 45,6% | 22 |
| Pustynia | wyjście | 30 | 242 | 178 / 209 → 26,6% / 25,0% | 0 | 106 / 121 → 56,1% / 49,8% | 36 | 116 / 134 → 52,1% / 44,8% | 27 |
| Góry z tundrą | wejście | 30 | 251 | 178 / 209 → 29,3% / 25,0% | 0 | 106 / 121 → 57,7% / 51,7% | 40 | 116 / 134 → 53,8% / 46,9% | 31 |
| Góry z tundrą | wyjście | 37 | 307 | 217 / 259 → 29,3% / 25,0% | 0 | 129 / 151 → 57,9% / 50,8% | 47 | 141 / 166 → 53,9% / 45,9% | 37 |
| Lodowiec | wejście | 37 | 318 | 217 / 259 → 31,9% / 25,0% | 0 | 129 / 151 → 59,5% / 52,6% | 52 | 141 / 166 → 55,6% / 47,9% | 42 |
| Lodowiec | wyjście | 46 | 392 | 265 / 326 → 32,2% / 25,0% | 0 | 159 / 189 → 59,5% / 51,8% | 62 | 174 / 209 → 55,6% / 46,6% | 48 |
| Wulkaniczny | wejście | 46 | 406 | 265 / 326 → 34,7% / 25,0% | 0 | 159 / 189 → 60,9% / 53,5% | 69 | 174 / 209 → 57,2% / 48,5% | 55 |
| Wulkaniczny | wyjście | 56 | 491 | 321 / 401 → 34,7% / 25,0% | 0 | 192 / 232 → 60,9% / 52,7% | 81 | 210 / 258 → 57,2% / 47,5% | 63 |
| Kryształowy | wejście | 56 | 515 | 321 / 401 → 37,7% / 25,0% | 0 | 192 / 232 → 62,8% / 54,9% | 92 | 210 / 258 → 59,2% / 50,0% | 74 |
| Kryształowy | wyjście | 69 | 630 | 392 / 502 → 37,8% / 25,0% | 0 | 235 / 289 → 62,7% / 54,1% | 109 | 257 / 320 → 59,2% / 49,2% | 87 |

#### Plan równy (600 min do ostatniego biomu; gracz oczekiwany trenuje 20,0% czasu)

Mnożnik biomu k = o ile ciosy i życie potworów biomu są większe od potwora lasu tego samego poziomu (dobrany symulacją tak, żeby gracz oczekiwany na wejściu wygrywał ze zwykłymi potworami tyle, ile w kolumnie „Cel”). Wygrane: średnio trzy klasy; „gołe poziomy” = ta sama postać bez treningu, „dużo treningu” = 40,0% czasu w Training Center. Wyjście: zwykłe potwory poziomu gracza, troll i strażnik o poziom niżej.

| Biom | Poziom wejście → wyjście | k | Cel | Zwykłe na wejściu: gołe / oczekiwany / dużo | Zwykłe na wyjściu (oczekiwany) | Troll / strażnik na wyjściu: gołe | oczekiwany | dużo |
|---|---|---:|---:|---|---:|---|---|---|
| Las | 1 → 18 | 1,04 | 85,0% | 83,0% / 83,0% / 83,0% | 92,0% | 58,6% / 39,7% | 78,0% / 66,7% | 84,0% / 77,4% |
| Bagno | 18 → 27 | 1,17 | 83,6% | 70,1% / 83,0% / 87,4% | 85,9% | 31,5% / 17,3% | 62,9% / 47,7% | 72,0% / 59,7% |
| Dżungla | 27 → 34 | 1,23 | 82,1% | 64,1% / 81,5% / 86,2% | 83,9% | 23,8% / 10,9% | 58,1% / 42,0% | 67,5% / 54,1% |
| Pustynia | 34 → 40 | 1,28 | 80,7% | 59,0% / 80,3% / 85,4% | 82,2% | 18,3% / 6,2% | 53,7% / 38,2% | 65,7% / 50,8% |
| Góry z tundrą | 40 → 46 | 1,32 | 79,3% | 54,3% / 79,0% / 84,7% | 80,6% | 14,4% / 4,4% | 51,0% / 34,5% | 63,2% / 48,2% |
| Lodowiec | 46 → 51 | 1,36 | 77,9% | 50,3% / 77,8% / 83,8% | 79,1% | 10,8% / 3,3% | 47,5% / 32,5% | 61,0% / 46,4% |
| Wulkaniczny | 51 → 56 | 1,40 | 76,4% | 46,2% / 76,6% / 82,6% | 78,3% | 8,5% / 2,2% | 44,3% / 30,5% | 58,6% / 43,3% |
| Kryształowy | 56 → 61 | 1,45 | 75,0% | 41,4% / 74,7% / 80,8% | 75,8% | 6,2% / 1,2% | 40,5% / 26,3% | 54,4% / 39,5% |

Pancerz gracza (punkty po przeliczniku klasy) i cios zwykłego potwora fizycznego biomu (średnio Slime i Wilk × k, bez krytyka, rozrzut 100%). „Przechodzi” = część ciosu po Pancerzu (najmniej 25,0% — limit D-091). „Do limitu” = ile punktów Pancerza z treningu brakuje graczowi oczekiwanemu, żeby zwykły cios tego biomu dochodził tylko w 25,0%.

| Biom | Gdzie | Poziom | Cios potwora | Wojownik: Pancerz gołe / oczek. → przechodzi gołe / oczek. | do limitu | Zwiadowca: Pancerz gołe / oczek. → przechodzi gołe / oczek. | do limitu | Mag: Pancerz gołe / oczek. → przechodzi gołe / oczek. | do limitu |
|---|---|---:|---:|---|---:|---|---:|---|---:|
| Las | wejście | 1 | 19 | 16 / 16 → 25,0% / 25,0% | 0 | 10 / 10 → 46,2% / 46,2% | 2 | 11 / 11 → 44,0% / 44,0% | 2 |
| Las | wyjście | 18 | 126 | 111 / 124 → 25,0% / 25,0% | 0 | 66 / 73 → 47,3% / 42,0% | 13 | 72 / 80 → 42,3% / 36,8% | 8 |
| Bagno | wejście | 18 | 141 | 111 / 124 → 25,0% / 25,0% | 0 | 66 / 73 → 53,1% / 48,3% | 20 | 72 / 80 → 48,7% / 43,7% | 15 |
| Bagno | wyjście | 27 | 205 | 161 / 184 → 25,0% / 25,0% | 0 | 96 / 108 → 53,3% / 47,5% | 27 | 105 / 119 → 48,7% / 41,9% | 20 |
| Dżungla | wejście | 27 | 216 | 161 / 184 → 25,2% / 25,0% | 0 | 96 / 108 → 55,6% / 50,1% | 32 | 105 / 119 → 51,3% / 44,8% | 24 |
| Dżungla | wyjście | 34 | 268 | 198 / 232 → 26,0% / 25,0% | 0 | 119 / 135 → 55,8% / 49,5% | 39 | 130 / 150 → 51,3% / 44,1% | 29 |
| Pustynia | wejście | 34 | 278 | 198 / 232 → 28,7% / 25,0% | 0 | 119 / 135 → 57,4% / 51,4% | 44 | 130 / 150 → 53,1% / 46,2% | 34 |
| Pustynia | wyjście | 40 | 325 | 233 / 278 → 28,3% / 25,0% | 0 | 139 / 161 → 57,1% / 50,3% | 49 | 152 / 178 → 53,1% / 45,0% | 37 |
| Góry z tundrą | wejście | 40 | 335 | 233 / 278 → 30,5% / 25,0% | 0 | 139 / 161 → 58,4% / 51,9% | 54 | 152 / 178 → 54,6% / 46,8% | 42 |
| Góry z tundrą | wyjście | 46 | 383 | 265 / 321 → 30,7% / 25,0% | 0 | 159 / 186 → 58,6% / 51,5% | 60 | 174 / 205 → 54,5% / 46,3% | 47 |
| Lodowiec | wejście | 46 | 394 | 265 / 321 → 32,7% / 25,0% | 0 | 159 / 186 → 59,8% / 52,9% | 66 | 174 / 205 → 55,9% / 47,9% | 52 |
| Lodowiec | wyjście | 51 | 435 | 293 / 360 → 32,7% / 25,0% | 0 | 176 / 208 → 59,6% / 52,2% | 71 | 192 / 231 → 55,9% / 47,0% | 55 |
| Wulkaniczny | wejście | 51 | 448 | 293 / 360 → 34,6% / 25,0% | 0 | 176 / 208 → 60,7% / 53,6% | 76 | 192 / 231 → 57,1% / 48,5% | 60 |
| Wulkaniczny | wyjście | 56 | 491 | 321 / 399 → 34,7% / 25,0% | 0 | 192 / 230 → 60,9% / 53,0% | 82 | 210 / 256 → 57,2% / 47,9% | 64 |
| Kryształowy | wejście | 56 | 508 | 321 / 399 → 36,9% / 25,0% | 0 | 192 / 230 → 62,3% / 54,7% | 90 | 210 / 256 → 58,6% / 49,7% | 72 |
| Kryształowy | wyjście | 61 | 552 | 348 / 438 → 36,9% / 25,0% | 0 | 209 / 253 → 62,1% / 54,2% | 96 | 228 / 279 → 58,6% / 49,4% | 77 |

### 2. Drzewko Twierdzy: mnożnik procentowy razy ulepszenie budynku

Premie z drzewka w dzisiejszych danych (`src/shared/SkillTreeData.luau`, pełne poziomy): Twierdza → Income: kopalnia (MINING) +20,0%, wszystkie surowce (BIG CARTS) +10,0%, premia czasowa (RUSH HOUR) +25,0%; gracz → Income: Złoto (GOLD I i II) +35,0%, Złoto offline +25,0%.

| Jak składać premie z drzewka | Mnożnik dochodu kopalni przy pełnym drzewku |
|---|---:|
| tylko Twierdza, dodawane | ×1,30 |
| Twierdza + gracz, dodawane | ×1,65 |
| Twierdza + gracz, mnożone | ×1,78 |
| wszystko mnożone (z RUSH HOUR i offline) | ×2,78 |

Kopalnia Złota od 25. poziomu gracza, kolejny poziom budynku co 5 poziomów gracza. 1. poziom kopalni = 15,0% Złota z walk na godzinę na 25. poziomie (3286 zł/h z 21908 zł/h). Złoto z walk: gracz wzorcowy, zwykłe potwory jego poziomu, cykl jak w modelu tempa.

Komórka: dochód kopalni na godzinę jako procent Złota z walk na godzinę na tym poziomie gracza — bez drzewka / z pełnym drzewkiem Twierdzy (dodawane) / z drzewkiem Twierdzy i gracza mnożonym. Powyżej 100% kopalnia daje więcej niż walka.

| Krzywa budynku | poz. 25 (bud. 1) | poz. 30 (bud. 2) | poz. 35 (bud. 3) | poz. 40 (bud. 4) | poz. 45 (bud. 5) | poz. 50 (bud. 6) | poz. 55 (bud. 7) | poz. 60 (bud. 8) | poz. 65 (bud. 9) |
|---|---|---|---|---|---|---|---|---|---|
| liniowa (n) | 15 / 20 / 27 | 25 / 33 / 45 | 33 / 42 / 58 | 38 / 50 / 68 | 43 / 56 / 76 | 46 / 59 / 82 | 49 / 64 / 88 | 52 / 68 / 93 | 53 / 69 / 95 |
| potęgowa (n^1,5) | 15 / 20 / 27 | 36 / 46 / 64 | 56 / 73 / 101 | 77 / 100 / 137 | 95 / 124 / 170 | 112 / 146 / 200 | 130 / 169 / 232 | 148 / 192 / 264 | 160 / 208 / 285 |
| wykładnicza ×1,25 | 15 / 20 / 27 | 16 / 21 / 28 | 17 / 22 / 30 | 19 / 24 / 33 | 21 / 27 / 37 | 23 / 30 / 41 | 27 / 35 / 48 | 31 / 41 / 56 | 35 / 46 / 63 |
| wykładnicza ×1,6 | 15 / 20 / 27 | 20 / 26 / 36 | 28 / 36 / 50 | 39 / 51 / 70 | 56 / 73 / 100 | 80 / 104 / 143 | 118 / 154 / 210 | 176 / 228 / 313 | 254 / 330 / 453 |

Jeżeli kopalnia pracuje także wtedy, gdy gracza nie ma w grze (Twierdza „chodzi sama”, D-049; węzeł OFFLINE GOLD), liczy się doba, nie godzina gry. Gracz gra 2 h dziennie (przyjęte). Komórka: Złoto kopalni na dobę jako procent Złota z walk z tej doby — krzywa wykładnicza ×1,25, bez drzewka / z pełnym drzewkiem Twierdzy i gracza (mnożone):

| Kopalnia pracuje | poz. 25 (bud. 1) | poz. 35 (bud. 3) | poz. 45 (bud. 5) | poz. 55 (bud. 7) | poz. 65 (bud. 9) |
|---|---|---|---|---|---|
| tylko w czasie gry | 15,0% / 26,7% | 17,0% / 30,3% | 20,8% / 37,2% | 26,9% / 47,9% | 35,2% / 62,8% |
| offline do 8 h, 50% tempa | 45,0% / 80,2% | 50,9% / 90,8% | 62,5% / 111,5% | 80,6% / 143,6% | 105,7% / 188,4% |
| cała doba, pełne tempo | 180,0% / 320,8% | 203,8% / 363,1% | 250,2% / 445,9% | 322,2% / 574,2% | 423,0% / 753,7% |

Ile Złota na godzinę daje jeden poziom węzła MINING (+4% kopalni, cena 15–75 Gemów niezależnie od budynku) przy kopalni 1. i 9. poziomu:

| Krzywa budynku | Kopalnia 1. poz. | Kopalnia 9. poz. | Ile razy więcej |
|---|---:|---:|---:|
| liniowa (n) | 131 zł/h | 1183 zł/h | ×9,0 |
| potęgowa (n^1,5) | 131 zł/h | 3549 zł/h | ×27,0 |
| wykładnicza ×1,25 | 131 zł/h | 783 zł/h | ×6,0 |
| wykładnicza ×1,6 | 131 zł/h | 5646 zł/h | ×42,9 |

Gałąź Training Center w drzewku Twierdzy: wszystkie mini-gry +40,0% (TRAINING I i II), do tego osobne węzły Siła, Zręczność, Szczęście, Pancerz (po +20,0%). **Kondycja i Inteligencja nie mają własnego węzła**, więc przy pełnym drzewku cztery mini-gry dają ×1,60, a dwie ×1,40 — patrz część 6.

### 3. Ewolucja petów: shardy, tokeny krainy, Shard Ewolucji

Strażnik Gaju (10. poziom) farmiony przez gracza wzorcowego (średnio klasy): wygrane i czas jednej próby (walka + 40 s dojścia i odrodzenia + 15 s po przegranej):

| Gracz | Wygrane | Czas próby |
|---|---:|---:|
| poziom 10 (+0) | 36,0% | 94 s |
| poziom 12 (+2) | 71,9% | 89 s |
| poziom 15 (+5) | 96,7% | 80 s |

**Shard Ewolucji** (wypada tylko z wygranej ze strażnikiem, D-058; dziś szansa 10,0%): ile prób na JEDEN Shard — średnio / połowa graczy / 90% graczy — i ile to minut. Gracz farmi strażnika 2 poziomy wyżej. Ostatnia kolumna: ochrona przed pechem — Shard gwarantowany po 2/szansa wygranych bez Sharda (średnio prób).

| Szansa | Prób: średnio / 50% / 90% | Minut: średnio / 50% / 90% | Komplet 3 ewolucji jednego peta (śr. minut) | 10 petów biomu × 3 (śr. godzin) | Z ochroną po N wygranych: N, śr. prób |
|---:|---|---|---:|---:|---|
| 5,0% | 28 / 19 / 63 | 41 / 28 / 93 | 123 | 20,6 | 40, 24 |
| 10,0% | 14 / 10 / 31 | 21 / 15 / 46 | 62 | 10,3 | 20, 12 |
| 15,0% | 9 / 7 / 21 | 14 / 10 / 31 | 41 | 6,9 | 13, 8 |
| 20,0% | 7 / 5 / 15 | 10 / 7 / 22 | 31 | 5,1 | 10, 6 |
| 25,0% | 6 / 4 / 12 | 8 / 6 / 18 | 25 | 4,1 | 8, 5 |
| 33,0% | 4 / 3 / 9 | 6 / 4 / 13 | 19 | 3,1 | 6, 4 |

**Tokeny krainy** (dziś: zwykły potwór 1 + 30% szansy na drugi, troll 3 + 50%, strażnik 5 + 50%, tylko za wygraną): gracz 10. poziomu na zwykłych potworach lasu zbiera **2,19 tokenu na minutę** (132 na godzinę); z farmienia strażnika 2,67 na minutę.

| Ewolucja | Tokeny (propozycja) | Minut zwykłych walk | Shardy peta = kopie (propozycja) |
|---|---:|---:|---:|
| 1. | 60 | 27 | 2 |
| 2. | 180 | 82 | 3 |
| 3. | 450 | 205 | 5 |

**Kopie peta z jajek** (jedna kopia = jeden shard, D-058). Jajko z pięciu petów, szanse 50,0% / 25,0% / 15,0% / 8,0% / 2,0% (przyjęte); komplet ewolucji = 10 kopii + sam pet. Złoto gracza 10. poziomu z walk: 159 na minutę.

| Pet w jajku | Szansa | Jajek na komplet (śr.) | Godzin walki na Złoto: jajko 1000 / jajko 10000 | Wariant: kopii wg rzadkości | jajek | godzin: jajko 1000 / 10000 |
|---|---:|---:|---|---:|---:|---|
| 1. (pospolity) | 50,0% | 22 | 2,3 / 23,0 | 10 | 22 | 2,3 / 23,0 |
| 2. (zwykły) | 25,0% | 44 | 4,6 / 46,0 | 8 | 36 | 3,8 / 37,7 |
| 3. (rzadki) | 15,0% | 73 | 7,7 / 76,7 | 6 | 47 | 4,9 / 48,8 |
| 4. (epicki) | 8,0% | 138 | 14,4 / 143,9 | 4 | 62 | 6,5 / 65,4 |
| 5. (legendarny) | 2,0% | 550 | 57,6 / 575,5 | 3 | 200 | 20,9 / 209,3 |

### 4. Gemy na drzewka a czas gry (10 godzin do ostatniego biomu)

Koszt drzewek w dzisiejszych danych (`src/shared/SkillTreeData.luau`: korzeń 10, poziom węzła = (10 + 5 × głębokość) × numer poziomu): **Player 8105, Fortress 5860, Pets 6685, razem 20650 Gemów**.

Dziś Gemy wypadają tylko z łupu (`dane_walki.json`): zwykły potwór 1,0%–1,2%, troll 5,0%, strażnik 15,0% szansy na 1 Gem za wygraną. Zestawy do porównania (propozycje): „łup ×5” — pięć razy większe szanse; „kamienie milowe” — +10 Gemów za każdy poziom i +100 za pierwsze pokonanie strażnika biomu; „kopalnia” — kopalnia diamentów od 25. poziomu, 30 Gemów/h na 1. poziomie budynku i ×1,25 co poziom budynku (co 5 poziomów gracza). Kopalnia liczy tylko czas gry (bez dochodu offline).

#### Plan rosnący — Gemy zebrane do końca biomu (w nawiasie: procent kosztu drzewka Player, które da się kupić)

| Biom | Koniec (min) | Poziom | dzis | łup ×5 | łup ×5 + kamienie milowe | łup ×5 + milowe + kopalnia |
|---|---:|---:|---:|---:|---:|---:|
| Las | 30 | 11 | 0 (0,0%) | 2 (0,0%) | 202 (2,5%) | 202 (2,5%) |
| Bagno | 75 | 19 | 1 (0,0%) | 5 (0,0%) | 385 (4,6%) | 385 (4,6%) |
| Dżungla | 135 | 26 | 2 (0,0%) | 8 (0,0%) | 558 (6,8%) | 566 (6,8%) |
| Pustynia | 210 | 34 | 3 (0,0%) | 13 (0,1%) | 743 (8,8%) | 794 (9,3%) |
| Góry z tundrą | 305 | 43 | 4 (0,0%) | 19 (0,1%) | 939 (11,3%) | 1071 (13,0%) |
| Lodowiec | 430 | 53 | 5 (0,0%) | 26 (0,3%) | 1146 (13,6%) | 1439 (17,3%) |
| Wulkaniczny | 600 | 65 | 7 (0,0%) | 35 (0,3%) | 1365 (16,7%) | 2009 (24,7%) |
| Kryształowy | 830 | 79 | 10 (0,0%) | 48 (0,5%) | 1628 (19,6%) | 3135 (38,1%) |

#### Plan równy — Gemy zebrane do końca biomu (w nawiasie: procent kosztu drzewka Player, które da się kupić)

| Biom | Koniec (min) | Poziom | dzis | łup ×5 | łup ×5 + kamienie milowe | łup ×5 + milowe + kopalnia |
|---|---:|---:|---:|---:|---:|---:|
| Las | 86 | 20 | 1 (0,0%) | 4 (0,0%) | 294 (3,4%) | 294 (3,4%) |
| Bagno | 171 | 30 | 2 (0,0%) | 10 (0,0%) | 500 (6,0%) | 527 (6,4%) |
| Dżungla | 257 | 39 | 3 (0,0%) | 15 (0,1%) | 695 (8,3%) | 783 (9,3%) |
| Pustynia | 343 | 46 | 4 (0,0%) | 20 (0,1%) | 870 (10,3%) | 1044 (12,4%) |
| Góry z tundrą | 429 | 53 | 5 (0,0%) | 25 (0,1%) | 1045 (12,4%) | 1336 (16,1%) |
| Lodowiec | 514 | 59 | 6 (0,0%) | 30 (0,3%) | 1210 (14,9%) | 1656 (20,3%) |
| Wulkaniczny | 600 | 65 | 7 (0,0%) | 35 (0,3%) | 1365 (16,7%) | 2009 (24,7%) |
| Kryształowy | 686 | 70 | 8 (0,0%) | 40 (0,5%) | 1530 (18,8%) | 2436 (29,7%) |

**Sloty umiejętności są w drzewku** (D-055, D-088; gałąź Skills): 1. slot kosztuje z korzeniem 25 Gemów, 2. — razem 70, 3. — razem 125 (z węzłami po drodze na 1. poziomie). Model balansu walki zakłada sloty od 1., 5. i 10. poziomu. Komórka: biom, na którego końcu gracz ma już Gemy na kolejne sloty (1. / 2. / 3.; „—” = nie w 8 biomach):

| Plan | dzis | łup ×5 | łup ×5 + kamienie milowe | łup ×5 + milowe + kopalnia |
|---|---|---|---|---|
| rosnący | — / — / — | Lodowiec (poz. 53) / — / — | Las (poz. 11) / Las (poz. 11) / Las (poz. 11) | Las (poz. 11) / Las (poz. 11) / Las (poz. 11) |
| równy | — / — / — | Lodowiec (poz. 59) / — / — | Las (poz. 20) / Las (poz. 20) / Las (poz. 20) | Las (poz. 20) / Las (poz. 20) / Las (poz. 20) |

Ile Gemów na godzinę gry trzeba, żeby gracz bez płacenia kupił w 10 godzin 25% / 50% / 100% drzewka Player: **203 / 405 / 810 Gemów/h** (dziś łup daje ok. 0,6 Gemu/h).

### 5. Pytanie 40: Wojownik z tarczą i unikiem

Wojownik z tarczą (blok 5% + 28,3%) trenuje Zręczność: T dodatkowych punktów (ułamek puli poziomu) idzie w Zręczność; przeciwnicy w pojedynkach mają te same T punktów rozdane rozkładem swojej klasy (równy wkład). Dla porównania ten sam Wojownik z T rozdanym rozkładem klasy i Zwiadowca z T w Zręczności. 800 walk na parę, pojedynki średnio z obu miejsc.

| Podejście | Poziom | T (ułamek puli) | Wojownik T w Zręczność: z potworami / z Wojownikiem / Zwiadowcą / Magiem | Wojownik T rozkładem: z potworami / z Wojownikiem / Zwiadowcą / Magiem | Zwiadowca T w Zręczność: z potworami | Unik + blok Wojownika (T w Zr.) | Długość: tury (mediana) / czas z potworami |
|---|---:|---:|---|---|---:|---|---|
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 10 | 0,00 | 70,3% / 50,0% / 49,6% / 51,6% | 70,3% / 50,0% / 49,6% / 51,6% | 69,5% | 7,1% + 30,9% | 20 / 32,0 s |
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 10 | 0,25 | 81,4% / 42,0% / 43,4% / 43,6% | 88,3% / 50,0% / 51,2% / 55,1% | 77,8% | 15,1% + 28,2% | 19 / 30,0 s |
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 10 | 0,50 | 84,4% / 28,0% / 30,6% / 32,3% | 96,2% / 50,0% / 53,2% / 57,6% | 80,6% | 18,0% + 27,3% | 19 / 29,3 s |
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 10 | 1,00 | 85,9% / 10,8% / 13,0% / 16,9% | 99,8% / 50,0% / 53,6% / 62,1% | 83,1% | 20,4% + 26,5% | 18 / 28,8 s |
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 30 | 0,00 | 70,5% / 50,0% / 49,4% / 51,4% | 70,5% / 50,0% / 49,4% / 51,4% | 69,7% | 7,0% + 31,0% | 21 / 32,6 s |
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 30 | 0,25 | 81,9% / 42,2% / 43,4% / 44,1% | 89,1% / 50,0% / 50,9% / 55,2% | 77,8% | 15,1% + 28,3% | 19 / 30,4 s |
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 30 | 0,50 | 84,4% / 28,5% / 30,9% / 32,2% | 96,5% / 50,0% / 53,1% / 57,7% | 80,8% | 18,0% + 27,3% | 19 / 29,7 s |
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 30 | 1,00 | 86,2% / 10,9% / 13,1% / 17,0% | 99,8% / 50,0% / 53,1% / 62,6% | 83,4% | 20,4% + 26,5% | 19 / 29,1 s |
| (a') niższy limit uniku Wojownika: 15% | 10 | 0,00 | 69,0% / 50,0% / 48,4% / 49,0% | 69,0% / 50,0% / 48,4% / 49,0% | 69,8% | 4,4% + 31,8% | 20 / 31,7 s |
| (a') niższy limit uniku Wojownika: 15% | 10 | 0,25 | 78,2% / 39,4% / 39,0% / 38,8% | 87,0% / 50,0% / 49,4% / 52,2% | 78,1% | 9,4% + 30,2% | 19 / 29,6 s |
| (a') niższy limit uniku Wojownika: 15% | 10 | 0,50 | 80,9% / 24,6% / 25,3% / 28,2% | 95,7% / 50,0% / 50,4% / 55,2% | 80,8% | 11,2% + 29,6% | 18 / 28,8 s |
| (a') niższy limit uniku Wojownika: 15% | 10 | 1,00 | 82,8% / 10,4% / 10,6% / 13,4% | 99,7% / 50,0% / 50,9% / 59,6% | 83,2% | 12,7% + 29,1% | 18 / 28,3 s |
| (a') niższy limit uniku Wojownika: 15% | 30 | 0,00 | 69,5% / 50,0% / 48,4% / 49,2% | 69,5% / 50,0% / 48,4% / 49,2% | 69,9% | 4,3% + 31,8% | 20 / 32,3 s |
| (a') niższy limit uniku Wojownika: 15% | 30 | 0,25 | 78,5% / 39,8% / 38,9% / 39,2% | 87,9% / 50,0% / 48,8% / 52,1% | 78,2% | 9,4% + 30,2% | 19 / 30,0 s |
| (a') niższy limit uniku Wojownika: 15% | 30 | 0,50 | 80,8% / 24,8% / 26,0% / 28,2% | 96,1% / 50,0% / 50,6% / 55,0% | 81,1% | 11,2% + 29,6% | 19 / 29,2 s |
| (a') niższy limit uniku Wojownika: 15% | 30 | 1,00 | 82,8% / 10,6% / 10,5% / 13,7% | 99,8% / 50,0% / 50,5% / 59,8% | 83,7% | 12,7% + 29,1% | 18 / 28,7 s |
| (b) połowa przyrostu Zręczności z treningu u Wojownika | 10 | 0,00 | 70,3% / 50,0% / 49,6% / 51,6% | 70,3% / 50,0% / 49,6% / 51,6% | 69,5% | 7,1% + 30,9% | 20 / 32,0 s |
| (b) połowa przyrostu Zręczności z treningu u Wojownika | 10 | 0,25 | 77,3% / 34,9% / 38,6% / 39,1% | 88,3% / 50,0% / 51,2% / 55,1% | 77,8% | 12,4% + 29,2% | 19 / 30,6 s |
| (b) połowa przyrostu Zręczności z treningu u Wojownika | 10 | 0,50 | 81,4% / 23,1% / 25,6% / 28,3% | 96,2% / 50,0% / 53,2% / 57,6% | 80,6% | 15,1% + 28,2% | 19 / 30,0 s |
| (b) połowa przyrostu Zręczności z treningu u Wojownika | 10 | 1,00 | 84,4% / 9,1% / 10,2% / 13,5% | 99,8% / 50,0% / 53,6% / 62,1% | 83,1% | 18,0% + 27,3% | 19 / 29,3 s |
| (b) połowa przyrostu Zręczności z treningu u Wojownika | 30 | 0,00 | 70,5% / 50,0% / 49,4% / 51,4% | 70,5% / 50,0% / 49,4% / 51,4% | 69,7% | 7,0% + 31,0% | 21 / 32,6 s |
| (b) połowa przyrostu Zręczności z treningu u Wojownika | 30 | 0,25 | 77,7% / 35,5% / 38,4% / 38,9% | 89,1% / 50,0% / 50,9% / 55,2% | 77,8% | 12,3% + 29,2% | 19 / 31,1 s |
| (b) połowa przyrostu Zręczności z treningu u Wojownika | 30 | 0,50 | 81,9% / 23,2% / 25,9% / 27,9% | 96,5% / 50,0% / 53,1% / 57,7% | 80,8% | 15,1% + 28,3% | 19 / 30,4 s |
| (b) połowa przyrostu Zręczności z treningu u Wojownika | 30 | 1,00 | 84,4% / 9,1% / 10,5% / 13,2% | 99,8% / 50,0% / 53,1% / 62,6% | 83,4% | 18,0% + 27,3% | 19 / 29,7 s |
| (c) blok i unik się nie sumują (jedna szansa) | 10 | 0,00 | 68,9% / 50,0% / 48,3% / 49,6% | 68,9% / 50,0% / 48,3% / 49,6% | 68,5% | 7,1% + 26,2% | 19 / 30,7 s |
| (c) blok i unik się nie sumują (jedna szansa) | 10 | 0,25 | 77,1% / 38,6% / 37,1% / 38,2% | 87,4% / 50,0% / 49,0% / 53,2% | 77,0% | 15,1% + 18,1% | 18 / 28,5 s |
| (c) blok i unik się nie sumują (jedna szansa) | 10 | 0,50 | 79,8% / 24,1% / 24,1% / 26,8% | 95,8% / 50,0% / 50,4% / 55,0% | 79,8% | 18,0% + 15,2% | 17 / 27,8 s |
| (c) blok i unik się nie sumują (jedna szansa) | 10 | 1,00 | 80,8% / 8,4% / 8,5% / 12,1% | 99,7% / 50,0% / 49,9% / 59,1% | 82,5% | 20,4% + 12,8% | 16 / 27,3 s |
| (c) blok i unik się nie sumują (jedna szansa) | 30 | 0,00 | 69,6% / 50,0% / 48,8% / 49,4% | 69,6% / 50,0% / 48,8% / 49,4% | 69,5% | 7,0% + 26,3% | 20 / 31,2 s |
| (c) blok i unik się nie sumują (jedna szansa) | 30 | 0,25 | 77,7% / 38,7% / 37,1% / 38,9% | 88,1% / 50,0% / 48,9% / 52,6% | 77,4% | 15,1% + 18,2% | 18 / 28,9 s |
| (c) blok i unik się nie sumują (jedna szansa) | 30 | 0,50 | 79,8% / 24,6% / 23,8% / 26,4% | 96,3% / 50,0% / 50,2% / 55,1% | 80,2% | 18,0% + 15,3% | 18 / 28,2 s |
| (c) blok i unik się nie sumują (jedna szansa) | 30 | 1,00 | 81,3% / 8,8% / 8,4% / 12,0% | 99,8% / 50,0% / 49,6% / 59,5% | 83,0% | 20,4% + 12,8% | 17 / 27,6 s |

Skutek uboczny podejścia dla wszystkich klas (postacie wzorcowe bez treningu): największa różnica klas przy tym samym potworze i zakres pojedynków klas.

| Podejście | Poziom | Różnica klas (potwory) | Pojedynki klas | Wygrane z potworami: Wojownik / Zwiadowca / Mag |
|---|---:|---:|---|---|
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 10 | 3,9 pp | 48,2%–51,8% | 70,3% / 69,5% / 69,4% |
| dziś (limit uniku klasy już jest: Wojownik 24,2%) | 30 | 4,2 pp | 47,8%–52,2% | 70,5% / 69,7% / 70,7% |
| (a') niższy limit uniku Wojownika: 15% | 10 | 5,2 pp | 48,2%–51,8% | 69,0% / 69,8% / 69,8% |
| (a') niższy limit uniku Wojownika: 15% | 30 | 5,5 pp | 47,8%–52,2% | 69,5% / 69,9% / 71,2% |
| (c) blok i unik się nie sumują (jedna szansa) | 10 | 5,6 pp | 48,3%–51,7% | 68,9% / 68,5% / 68,6% |
| (c) blok i unik się nie sumują (jedna szansa) | 30 | 6,0 pp | 48,0%–52,0% | 69,6% / 69,5% / 69,9% |

### 6. Trening: przyrost za trafienie i za serię, bez nadużywania jednej mini-gry

**Wzór (propozycja):** punkty statystyki za trafienie = C × K × M / N0, gdzie N0 = 10 trafień na punkt (pasek treningu), K = seria (0–4: ×1, 5–9: ×1,25, 10–19: ×1,5, od 20: ×2; średnio przyjęte ×1,3), C = poziom centrum (1,0 / 1,1 / 1,3 / 1,4 / 1,6 / 1,8 / 1,9 / 2,0; poziom centrum najwyżej numer biomu), M = 1 / (1 + W / (0,10 × pula))², W = punkty już wytrenowane w TEJ statystyce, pula = punkty statystyk z poziomu gracza (30 + 10 za poziom). Przy 30 trafieniach na minutę świeża statystyka rośnie 3,9 punktu na minutę (centrum 1).

| Biom (plan rosnący) | Poziomy | Punkty z poziomów na minutę walki | Trening: świeża statystyka / po 10,0% puli w niej / po 20,0% puli | Minut jednej mini-gry do połowy tempa |
|---|---|---:|---|---:|
| Las | 1 → 10 | 3,75 | 3,9 / 1,0 / 0,4 | 1,1 |
| Bagno | 10 → 17 | 1,94 | 4,5 / 1,1 / 0,5 | 2,0 |
| Dżungla | 17 → 23 | 1,25 | 5,1 / 1,3 / 0,6 | 2,6 |
| Pustynia | 23 → 30 | 1,17 | 5,7 / 1,4 / 0,6 | 3,0 |
| Góry z tundrą | 30 → 37 | 0,92 | 6,2 / 1,6 / 0,7 | 3,4 |
| Lodowiec | 37 → 46 | 0,90 | 6,8 / 1,7 / 0,8 | 3,8 |
| Wulkaniczny | 46 → 56 | 0,74 | 7,4 / 1,9 / 0,8 | 4,4 |
| Kryształowy | 56 → 69 | 0,71 | 7,8 / 1,9 / 0,9 | 5,0 |

Punkty z treningu (gracz trenuje 20,0% czasu gry, plan rosnący) na końcu Lasu, Pustyni i Wulkanicznego — razem i jako procent puli z poziomów (Wojownik; inne klasy tak samo przy „po równo” i „tylko jednej”):

| Wzór | Polityka | Las (poz. 10) | Pustynia (poz. 30) | Wulkaniczny (poz. 56) |
|---|---|---:|---:|---:|
| propozycja | sześć po równo | 18 (14,7%) | 108 (33,7%) | 292 (50,3%) |
| propozycja | rozkładem klasy | 17 (13,8%) | 98 (30,6%) | 259 (44,7%) |
| propozycja | tylko Kondycja | 10 (8,0%) | 47 (14,8%) | 117 (20,2%) |
| bez malejącego | sześć po równo | 23 (19,5%) | 209 (65,4%) | 751 (129,4%) |
| bez malejącego | rozkładem klasy | 23 (19,5%) | 209 (65,4%) | 751 (129,4%) |
| bez malejącego | tylko Kondycja | 23 (19,5%) | 209 (65,4%) | 751 (129,4%) |

#### Wzór: propozycja

Komórka: średnie wygrane z pięcioma potworami lasu poziomu gracza (zmiana względem tej samej postaci bez treningu, pp) / pojedynek z tą samą klasą, która trenowała tyle samo czasu rozkładem klasy (oba miejsca). 800 walk na parę.

| Klasa | Koniec biomu | sześć po równo | rozkładem klasy | tylko Siła | tylko Kondycja | tylko Inteligencja | tylko Zręczność | tylko Szczęście | tylko Pancerz |
|---|---|---|---|---|---|---|---|---|---|
| Wojownik | Las (poz. 10) | +11,4 / 52,1% | +10,6 / 50,0% | +6,2 / 43,6% | +7,0 / 42,1% | +8,1 / 43,1% | +5,3 / 44,3% | +6,5 / 43,5% | +4,0 / 41,1% |
| Wojownik | Pustynia (poz. 30) | +21,3 / 53,6% | +20,9 / 50,0% | +11,1 / 32,7% | +11,6 / 30,2% | +12,4 / 30,1% | +8,2 / 32,2% | +9,4 / 30,4% | +7,3 / 29,4% |
| Wojownik | Wulkaniczny (poz. 56) | +25,8 / 54,4% | +24,9 / 50,0% | +13,5 / 27,5% | +15,5 / 23,1% | +14,9 / 22,4% | +9,9 / 24,3% | +10,9 / 24,4% | +9,3 / 22,6% |
| Zwiadowca | Las (poz. 10) | +10,7 / 50,5% | +10,4 / 50,0% | +5,8 / 45,4% | +6,5 / 45,3% | +6,5 / 44,4% | +3,6 / 42,2% | +4,2 / 43,8% | +5,3 / 43,2% |
| Zwiadowca | Pustynia (poz. 30) | +19,5 / 50,6% | +18,9 / 50,0% | +9,8 / 39,1% | +10,9 / 36,5% | +9,9 / 36,5% | +5,8 / 32,7% | +7,0 / 34,0% | +8,9 / 34,4% |
| Zwiadowca | Wulkaniczny (poz. 56) | +24,2 / 51,8% | +23,5 / 50,0% | +11,6 / 34,3% | +14,4 / 30,0% | +11,0 / 30,8% | +6,9 / 25,9% | +8,6 / 27,9% | +10,5 / 27,4% |
| Mag | Las (poz. 10) | +10,2 / 49,6% | +10,1 / 50,0% | +5,0 / 43,9% | +8,0 / 44,8% | +3,0 / 43,2% | +5,4 / 44,5% | +4,3 / 43,8% | +6,8 / 37,0% |
| Mag | Pustynia (poz. 30) | +18,7 / 49,6% | +17,1 / 50,0% | +8,1 / 37,1% | +12,5 / 35,0% | +4,9 / 34,3% | +7,9 / 36,4% | +6,2 / 33,4% | +8,6 / 23,2% |
| Mag | Wulkaniczny (poz. 56) | +23,2 / 49,9% | +22,4 / 50,0% | +11,0 / 31,8% | +15,9 / 26,1% | +5,9 / 24,9% | +9,2 / 29,0% | +7,5 / 26,6% | +10,7 / 14,5% |

#### Wzór: bez malejącego

Komórka: średnie wygrane z pięcioma potworami lasu poziomu gracza (zmiana względem tej samej postaci bez treningu, pp) / pojedynek z tą samą klasą, która trenowała tyle samo czasu rozkładem klasy (oba miejsca). 800 walk na parę.

| Klasa | Koniec biomu | sześć po równo | rozkładem klasy | tylko Siła | tylko Kondycja | tylko Inteligencja | tylko Zręczność | tylko Szczęście | tylko Pancerz |
|---|---|---|---|---|---|---|---|---|---|
| Wojownik | Las (poz. 10) | +15,2 / 52,0% | +14,8 / 50,0% | +13,7 / 48,6% | +14,3 / 46,6% | +14,5 / 42,8% | +9,5 / 44,7% | +10,6 / 43,6% | +8,6 / 44,3% |
| Wojownik | Pustynia (poz. 30) | +27,5 / 49,8% | +27,9 / 50,0% | +24,7 / 42,8% | +27,7 / 30,2% | +22,5 / 18,9% | +14,7 / 21,4% | +16,0 / 19,0% | +14,1 / 28,4% |
| Wojownik | Wulkaniczny (poz. 56) | +29,1 / 46,7% | +29,2 / 50,0% | +28,1 / 38,3% | +29,2 / 10,5% | +23,8 / 4,2% | +16,5 / 6,1% | +17,8 / 2,2% | +15,2 / 6,0% |
| Zwiadowca | Las (poz. 10) | +13,4 / 50,8% | +12,3 / 50,0% | +11,5 / 48,4% | +13,6 / 51,4% | +11,0 / 44,4% | +7,2 / 43,0% | +7,8 / 44,6% | +10,3 / 47,1% |
| Zwiadowca | Pustynia (poz. 30) | +27,3 / 47,9% | +27,8 / 50,0% | +23,8 / 43,2% | +27,5 / 41,1% | +19,2 / 26,7% | +11,8 / 23,1% | +13,5 / 22,6% | +18,0 / 31,7% |
| Zwiadowca | Wulkaniczny (poz. 56) | +29,4 / 43,4% | +29,6 / 50,0% | +27,8 / 39,0% | +29,6 / 28,0% | +22,8 / 13,2% | +13,9 / 9,2% | +15,5 / 8,8% | +18,5 / 13,8% |
| Mag | Las (poz. 10) | +13,0 / 49,9% | +12,1 / 50,0% | +10,9 / 49,5% | +16,1 / 52,4% | +5,9 / 46,4% | +9,3 / 47,1% | +7,2 / 45,9% | +10,4 / 32,8% |
| Mag | Pustynia (poz. 30) | +25,9 / 47,7% | +26,4 / 50,0% | +22,4 / 46,4% | +28,6 / 43,2% | +12,2 / 28,5% | +15,9 / 26,8% | +11,8 / 22,8% | +18,4 / 9,1% |
| Mag | Wulkaniczny (poz. 56) | +28,5 / 44,1% | +28,6 / 50,0% | +26,4 / 42,5% | +28,7 / 27,4% | +17,4 / 12,6% | +17,8 / 9,2% | +13,2 / 5,0% | +19,3 / 0,8% |

_Policzone w 214 s (python -B tools/walka/progresja.py --ziaren 800 --start 1 --czesci 1,2,3,4,5,6)._
