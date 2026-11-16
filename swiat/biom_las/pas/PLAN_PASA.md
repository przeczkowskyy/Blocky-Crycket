# Las jako wąski pas — plan układu

*Status: **propozycja** (16.11.2026), nic nie jest zbudowane w Studio i nic tu nie jest kanonem. Wymagania: sesja
główna 16.11.2026 (D-075 pas biomów, D-076 układ biomu, D-077 przelot kamery, D-078 pomijanie walk — wszystkie jako
propozycje) i poprawka Karola z 16.11: Las ok. **30 min** gry (pasmo 25–40), ok. 10 h do ósmego biomu.*

Pliki w tym folderze:

| Plik | Co to jest |
|---|---|
| `plan_pasa.json` | układ: wymiary, przegrody, przejścia, miejsca, strefy potworów (pola jak w `swiat/biom_las/potwory.json`), Strażnik, przelot kamery, punkty przybycia, położenie w świecie, kolejne biomy, budżet czasu i części |
| `plan_pasa.png` | plansza z lotu ptaka (1600 px szer., pas pionowo: na dole przybycie, u góry brama do Bagna) |
| `rysuj_plan.py` | robi PNG z JSON: `python -B swiat/biom_las/pas/rysuj_plan.py` |
| `sprawdz_plan.py` | kontrola liczb i tabele: `python -B swiat/biom_las/pas/sprawdz_plan.py` (kod 1 = błąd; `--krotko`; można podać kopię JSON) |

> **W skrócie.** Las to prostokąt **72 × 964 st** (pole gry 72 = **4,5 s biegu**, po bokach po 24 st kulis), ustawiony
> na wschód od miasteczka na jego osi. Sześć przegród jedna za drugą: Polana Przybycia (teleport, jajko, Kamień
> Powrotu) → Zagroda Slime'ów (kojce 1, 2, 3) → Lasek Muchomorowy → Wilcze Zarośla → Leże Trolla → Arena Strażnika i
> brama do Bagna. Od przybycia do bramy **57,5 s** biegu; sąsiednie miejsca walki dzieli 4–7,5 s. Potworów **20 / 36 /
> 46** przy 1 / 8 / 20 graczach (ze Strażnikiem). Przy walkach oglądanych ×1 las zajmuje **ok. 29 min**, z czego
> chodzenie to **ok. 9%**. Przelot kamery przy pierwszym wejściu trwa **13,4 s** i kończy się rykiem Strażnika.
> Kontrola: **0 błędów, 0 ostrzeżeń**.

---

## 1. Wymiary i uzasadnienie

- **Prędkość biegu: 16 st/s.** Gra jej nie zmienia: w `src/` i `default.project.json` nie ma `WalkSpeed` ani
  `CharacterWalkSpeed` (sprawdzone 16.11). Wierzchowce ze Stajni mogą to kiedyś zmienić — wtedy wszystkie czasy w tym
  planie maleją.
- **Szerokość 72 st = 4,5 s** (środek pasma 4–5 s). W kojcu mieści się pętla 5 potworów (obwód 138 st ≥ 5 × 25) z
  placem walki r 12 i 2 st zapasu do ściany. Przy 64 st plac walki dotyka ściany; przy 80 st jest luźniej, ale to już
  górna granica (wybór 2).
- **Kulisy po 24 st z każdej strony**: gęste pnie, skały, jeżyny; kolizja tylko na pierwszym rzędzie, niewidzialna
  ściana na |v| = 38. Za plecami przybywającego ściana zamykająca (u −24…0) z Bramą Pniaków.
- **Teren płaski** (y = 0) w całym lesie; wysokość mają tylko rekwizyty (mostek, posadzka areny). Bez ramp i urwisk —
  prościej dla generatora, kamery i walki.
- **Układ pasa:** u wzdłuż (0 = początek lasu), v w poprzek (v > 0 po prawej ręce idącego do bramy).
  Świat = (1100 + u; y; −700 + v), bez obrotu.

| Odcinek | u | Dł. | Bieg przez | Od przybycia |
|---|---|---|---|---|
| ściana zamykająca | −24…0 | 24 | — | — |
| **Polana Przybycia** | 0…64 | 64 | 4,0 s | 0 s |
| płot z furtką | 64…76 | 12 | 0,8 s | |
| **Zagroda Slime'ów** (kojce 64 + 64 + 64) | 76…268 | 192 | 12,0 s | 3,9 s |
| strumyk z mostkiem | 268…288 | 20 | 1,3 s | |
| **Lasek Muchomorowy** (3 polanki) | 288…480 | 192 | 12,0 s | 17,1 s |
| jeżynowe zwężenie (przejście 32) | 480…496 | 16 | 1,0 s | |
| **Wilcze Zarośla** (3 części) | 496…688 | 192 | 12,0 s | 30,1 s |
| kamienny próg (przejście 28) | 688…704 | 16 | 1,0 s | |
| **Leże Trolla** | 704…804 | 100 | 6,2 s | 43,1 s |
| brama menhirów | 804…820 | 16 | 1,0 s | |
| **Arena Strażnika Gaju** + brama do Bagna (u 934) | 820…940 | 120 | 7,5 s | 50,4 s |

**Chodzenie w ok. 30 minutach** (założenia w `plan_pasa.json` → `czas`; średnie czasy walk z notatki
`B&C/Gra/Walka v2 — silnik, klasy i umiejętności.md`, tabela balansu, 5. poziom ×1: slime 20 s, muchomornik 15, wilk 16, troll 23, Strażnik 29; narzut walki 7 s — E, cięcie, wynik, powrót —
i 2 s dojścia do następnego potwora; 5 min na trening, statystyki i pety; jajko 45 s):

| Sposób gry | Walk | Czas lasu | Chodzenie | Udział chodzenia |
|---|---|---|---|---|
| ogląda walki ×1 | 49 (15 + 14 + 15 + 2 trolle + 3 próby Strażnika) | **29,0 min** | 155 s (bieg prosto 57,5 s + 49 × 2 s) | **8,9%** |
| pomija znane walki (D-078) | te same 49 | 17,5 min | 155 s | 14,8% |

Przy pomijaniu te same 49 walk to tylko 17,5 min — do 30 min krzywa doświadczenia musiałaby wymagać ok. 60 walk więcej.
To rozstrzyga krzywa doświadczenia (liczy ją równolegle drugi agent), nie układ pasa: układ ma tylko nie zmuszać do
chodzenia i do czekania. Liczba walk na przegrodę i poziomy są propozycją do uzgodnienia z tą krzywą.

---

## 2. Przegrody, potwory i farmienie bez czekania

Każda główna przegroda ma **trzy kojce/polanki po 64 st** z rosnącym poziomem (przegródki z żywopłotu 0,8 z przerwą
24 na środku), w każdym pętla 8 węzłów (zaokrąglony prostokąt 36 × 44 st, obwód 138 st) i dwa domy pod ścianami
(|v| = 34, 13,4 st od najbliższego węzła). Konwencje jak w `swiat/las_potwory` (odstęp 25, smycz 10, skalowanie
`cel`, skracanie odrodzenia 0,15 na gracza, najmniej 10 s); zmienione: domy 12–20 st od węzłów zamiast 35–50 i blokada
domu 12 zamiast 18 (pas ma 72 st), krótsze odrodzenie.

| Strefa | Potwór | Poziom* | Naraz 1 / 8 / 20 graczy | Odrodzenie | Uwagi |
|---|---|---|---|---|---|
| s1 · s2 · s3 | Leśny Slime | 1 · 2 · 3 | po 2 / 4 / 5 | 12 s | kojce 1–3 |
| m1 · m2 · m3 | Muchomornik | 3–4 · 4–5 · 5 | po 2 / 4 / 5 | 15 s | trochę silniejsze |
| w1 | Cierniowy Wilk | 6 | 2 / 4 / 6 | 18 s | 2 watahy |
| w2 | Cierniowy Wilk | 6–7 | 2 / 3 / 4 | 18 s | 1 wataha |
| w3 | Cierniowy Wilk | 7–8 | 2 / 3 / 4 | 18 s | samotniki |
| t1 | Leśny Troll | 8–9 | 1 / 1 / 1 | 150 s stałe | rzadki, ciężki; krąży po leżu |
| — | Strażnik Gaju | 10 | 1 | 120 s stałe | boss; otwiera bramę |
| **razem** | | | **20 / 36 / 46** | | stary las: 36 / 65 / 87 |

\* poziomy to propozycja do uzgodnienia z krzywą doświadczenia (w JSON pole `poziomy_status`).

**Ile walk na minutę daje przegroda** (`sprawdz_plan.py`, tabela „FARMIENIE”; potwór zajęty przez czas walki + 1 s,
potem odrodzenie ze skracaniem i ok. 3 s wyjścia z domu):

| Przegroda | Walk/min przy 8 graczach (walka 15 / 30 s) | Graczy bez czekania (8 / 20 na serwerze) | 1 gracz pomija walki |
|---|---|---|---|
| Zagroda Slime'ów | 23,1 / 15,6 | 9 / 12 | 1,8× potrzeb (3,6×, gdy pominięcie zwalnia potwora) |
| Lasek Muchomorowy | 20,8 / 14,5 | 9 / 9–12 | 1,9× (3,0×) |
| Wilcze Zarośla | 16,5 / 11,7 | 6 / 9 | 1,8× (2,8×) |
| Leże Trolla | 0,3 | — | rzadki z założenia: jedna walka co ok. 3 min na serwer |

Jeden gracz oglądający walki ×1 nigdy nie czeka w kojcu swojego poziomu (kontrola zgłasza to jako błąd). Gracz, który
pomija walki, w jednym kojcu czeka (potwór jest zajęty do końca walki jak w prototypie), ale przechodząc do kojca obok
ma zapas 1,8×. Przy tłoku (20 graczy w jednej przegrodzie) zaczyna się czekanie — wtedy rośnie `max` (więcej potworów,
pętla mieści 5).

---

## 3. Miejsca, przejścia i punkty orientacyjne

- **Przybycie** (u 14, v 0) — postać staje twarzą wzdłuż pasa; tu startuje przelot. **Stanowisko jajka** (30; 22, po
  prawej, 1,7 s od przybycia) — tylko podest 12 × 12 z punktem E (inkubator, farbowanie). **Kamień Powrotu** (6; −24,
  po lewej, 1,6 s) — E → miasteczko. **Brama Pniaków** za plecami. **Brama do Bagna** (u 934) — palisada przez cały pas
  z wrotami 16 st, zamknięta osobno dla gracza, póki nie pokona Strażnika. Strefy spokoju: cała Polana i przedbramie.
- **Przejścia** pokazują „następny etap”, ale nic nie blokują: płot 1,2 z otwartą furtką 16; płytki strumyk bez
  kolizji z mostkiem 12 i kamieniami brodu; jeżyny 6 wys. zwężające do 32; głazy zwężające do 28 (kości, szyld —
  ostrzeżenie przed trollem); dwa menhiry i niskie kamienie przed areną.
- **Punkty orientacyjne** (widać je z poprzedniej przegrody; pas jest prosty, więc kryształ areny widać z wejścia,
  o ile pozwoli mgła): paśnik-wieża z galaretą 16, Wielki Kapelusz 30, Wilcza Skała 30, głazy legowiska z kotłem 20,
  filar z zielonym kryształem 40. Stoją pod ścianami, poza placami walki.

---

## 4. Przelot kamery (pierwsze wejście, D-077)

| t (s) | Kamera (u; v; wys.) | Pokazuje |
|---|---|---|
| 0,0 | −10; 0; 28 | start nad plecami gracza, ponad Bramą Pniaków |
| 1,2 | 50; 12; 30 | Polana: jajko, płot z furtką |
| 2,7 | 160; −16; 26 | trzy kojce slime'ów |
| 4,3 | 300; 10; 26 | mostek i Lasek Muchomorowy |
| 6,1 | 470; −12; 24 | jeżynowe zwężenie i watahy |
| 8,1 | 660; 10; 22 | kamienny próg i Leże Trolla |
| 9,6 | 800; 0; 14 | brama menhirów, kamera zniża się |
| 10,5–13,4 | 848; 0; 10 | **STOP** na Strażniku (26 st przed nim, na wysokości głowy); **ryk** 10,7–12,7 s (klip `ryk` 2,0 s) |

Krzywa Catmull-Rom przez punkty, postój bez łuku; najszybciej 110 st/s. Potem zaciemnienie 0,5 s i kamera za plecami
gracza. Kontrola próbkuje tę samą krzywą co 0,05 s: cała w pasie, 10–30 st nad ziemią, nie wchodzi w punkty
orientacyjne. Flaga „widział przelot” na gracza (w Studio atrybut, w grze zapis). Streaming: przed startem serwer prosi
o wczytanie okolic u = 200, 450, 700, 874, a klient buduje Strażnika zawczasu (klon ok. 70 ms).

---

## 5. Położenie w świecie i kolejne biomy

- **Na wschód od miasteczka, na jego osi z = −700**, od X 1076 (za krawędzią Baseplate X 1024, zapas 52). Dlaczego:
  słońce świeci z pn.-zach. świata (`swiat/biom_las/PROJEKT.md` rozdz. 2), więc idąc na wschód gracz ma je za plecami
  i fronty lokacji są oświetlone — tak jak stary las osiągał to obrotem o 180°; nic tam nie stoi (miasteczko, stary
  las, oba prototypy walki i Baseplate są poza pasem — sprawdza `sprawdz_plan.py`); pas można zbudować obok starego
  lasu i porównać, zanim cokolwiek się usunie.
- **Kolejne biomy w tej samej linii**, każdy zarezerwowany na 940 st (jak las): Bagno u 940…1880, Dżungla, Pustynia,
  Góry z tundrą, Lodowiec, Wulkaniczny, Kryształowy do u 7520 (X 8620). Brama jednego biomu jest wejściem następnego.
- **Punkty przybycia** (przycisk Teleport: przejście przez chmury i widok pasa z góry — bez okna mapy i bez HUD, doprecyzowanie Karola z 16.11; kamera opada z wys. 60): miasteczko (jak dziś, ok. (−63,6; −771,5) przy
  Bramie Miejskiej), Las — Polana Przybycia (od początku), Las — przed Areną (u 812, opcja — wybór 8), Bagno (u 954,
  po pokonaniu Strażnika).

**Skalowanie na dłuższe biomy.** Ten sam układ przegród (wejście z jajkiem, trzy przegrody po trzy kojce rosnących
poziomów, leże rzadkiego potwora, arena) wystarcza na dłuższe biomy: dłuższy czas ma wynikać z większej liczby walk
(krzywa doświadczenia), treningu i trudniejszych buildów (D-076), nie z większej mapy. Przy tym samym pasie i średniej
walce z narzutem 27 s:

| Biom | Minut (propozycja) | Walk | Chodzenie |
|---|---|---|---|
| Las | 30 | ok. 51 | 8,9% |
| Bagno · Dżungla · Pustynia | 45 · 60 · 75 | 79 · 107 · 134 | 8,0 · 7,5 · 7,3% |
| Góry z tundrą · Lodowiec · Wulkaniczny | 95 · 125 · 170 | 172 · 227 · 310 | 7,0 · 6,8 · 6,6% |

Gdy w późnym biomie zabraknie stopni poziomów, czwarty kojec w przegrodzie to +64 st, czyli +4 s biegu.

---

## 6. Co z wersji 2 użyć ponownie, a co napisać od nowa

| Z wersji 2 | Co z tym |
|---|---|
| `swiat/biblioteka/scena.py`, `podglad.py`, `tools/studio_buduj.py`, `tools/studio_zrzuty.py` | bez zmian |
| `paleta.py`, `faktury.py` (rola części → materiał), `rosliny.py`, `skaly.py` | bez zmian (import) |
| `detale.py` | rodziny i gęstości tak; maskę rozsiewu przepiąć na pas (pole gry minus place walki i ścieżka) |
| `teren.py`, `geo.py` | wstęgi ścieżki i strumyka tak; model wysokości niepotrzebny (płasko) |
| `lokacje/*.py` | rekwizyty po przeskalowaniu w nowym układzie: Brama Pniaków i Kamień Powrotu (`laka.py`), Wielki Kapelusz (`kapeluszowo.py`), Wilcza Skała i Wrota Bagna (`ostepy.py`), legowisko i głazy (`wawoz.py`), Kamienny Krąg z kryształem (`korona.py`), jaja z Gniazda (`serce.py`) jako wzór stanowiska jajka |
| `studio_atrybuty.py` | wzór streamingu: punkty orientacyjne Persistent, kulisy StreamingMesh |
| `swiat/las_potwory` (Logika, Serwer, Klient, Stale) | prawie bez zmian (rozdz. 7) |
| teleport (`teleport.py`, `TeleportLasu.server.luau`) | mechanizm tak (prośba o streaming, `PivotTo`, odstęp 2 s); cele z listy punktów przybycia |
| mgła (`mgla.py`, `MglaLasu.client.luau`) | mechanizm tak (lokalnie u gracza, płynnie); prostokąt pasa zamiast kwadratu |
| **do wyrzucenia** | `uklad.json`, 24 lokacje, 16 stref, `wezly.py`, `sprawdz.py` lasu, `czesci.json` (22 419 części), ujęcia lasu |

**Nowe:** generator pasa (z `plan_pasa.json` → `czesci.json` i znaczniki stref w świecie), skrypt przelotu kamery z
flagą pierwszego wejścia, brama osobna dla gracza (lokalna przegroda u klienta + kontrola serwera), lista punktów
przybycia dla teleportu (przejście teleportu przez chmury to osobne zadanie 3D, bez okna mapy).

## 7. Wpływ na `swiat/las_potwory`, mgłę i teleport

- **`generuj_dane.py`:** wejście z `plan_pasa.json` (`strefy`, `straznik`, `zasady`, `rozmiary` mają te same nazwy
  pól; `podbiom` = id przegrody); przeliczenie `swiat_z_lasu` (−x; y; −2000 − z) → `swiat_z_pasa` (1100 + u; y;
  −700 + v) — bez obrotu, więc kierunki się nie odwracają; `DOM_OD/DOM_DO` 35/50 → 12/20 i blokada 18 → 12 z `zasady`;
  bez wyjątku korytarza z09; kontrola położenia sprawdza Płytę kontenera `PasLas` (bez obrotu) zamiast Płyty
  `BiomLas` (1400 × 1400, obrót 180°);
  `GATUNKI` + Leśny Troll (`lesny_troll`, jest w silniku i w `TestWalki2/Aktorzy`); `pominiete` puste.
- **`Stale.luau`:** `SZABLONY` + `lesny_troll`. **Serwer:** stałe odrodzenie nie tylko dla Strażnika (pole
  `odrodzenie_stale` trolla); po wygranej ze Strażnikiem atrybut gracza otwierający bramę; ewentualnie Strażnik osobny
  dla gracza (wybór 4). **Klient:** 12 widoków w promieniu 120 wystarcza (w promieniu 120 są 2–3 kojce); w czasie
  przelotu budować widoki przed kamerą.
- **Strefy spokoju** w pasie są prostokątami (Polana, przedbramie) — generator zapisuje dziś koła; trzeba dopisać
  prostokąt albo opisać je kołami.
- **Mgła:** prostokąt pasa lasu (X 1076…2040, |Z + 700| ≤ 60) zamiast kwadratu 1000 × 1000; przy bramie płynne
  przejście w mgłę Bagna; na czas przelotu można ją rozrzedzić. Do sprawdzenia, ile przegród widać przez mgłę.
- **Teleport:** stary `Workspace/LasTeleport` (cel (−200; −2400)) zastępują punkty przybycia z planu; Brama Miejska i
  Kamień Powrotu zostają jako punkty E; portal przy starcie tylko do testów.

## 8. Kolejność budowy w Studio (szacunek pracy agenta)

Przed każdym cięższym etapem: zadanie w `panel/narzedzia/praca.py` (obszar `studio:PasLas`), budowa tylko we własnym
kontenerze, punkty historii przed i po.

| Etap | Co | Czas |
|---|---|---|
| 0 | ludzie akceptują plan i wybory (rozdz. 10) | — |
| 1 | generator pasa „na szaro”: płyta, pole gry, proste kulisy, ścieżka, przegródki, przejścia, miejsca z E, domy; budowa `Workspace/PasLas` obok starego lasu, zrzuty z góry | 2–3 h |
| 2 | potwory w pasie: przepięty `generuj_dane.py`, troll, test w Play z jednym graczem (E, walka, odradzanie, liczby z tabeli) | 2–3 h |
| 3 | teleport na nowe punkty przybycia, Kamień Powrotu, wyłączenie starego `LasTeleport` | 1 h |
| 4 | przelot kamery, ryk, flaga pierwszego wejścia, streaming przed przelotem | 2–3 h |
| 5 | brama do Bagna osobna dla gracza | 1 h |
| 6 | wygląd: kulisy z rodzin roślin i skał, punkty orientacyjne z modułów v2, faktury, detale, mgła pasa; zrzuty i poprawki | 4–6 h |
| 7 | pomiar: telefon, streaming, przelot na telefonie, kolizje; raport na panel | 1–2 h |
| 8 | po akceptacji: usunięcie starego `BiomLas`, `LasMgla`, `LasTeleport` i starych danych `LasPotwory` | 0,5 h |
| | **razem** | **ok. 14–20 h** + przeglądy ludzi |

## 9. Liczba części (szacunek)

| Grupa | Części |
|---|---|
| teren (płyta, plamy przegród, podkładki stref) · ścieżka | 150 · 170 |
| kulisy (2 × 964 st, dwa rzędy pni i skał) · tło za kulisami | 2 600 · 300 |
| przegrody: wejście 350, zagroda 650 (płoty), lasek 750 (grzyby), zarośla 650, leże 450, arena 500 | 3 350 |
| przejścia · detale · domy i punkty E | 600 · 1 600 · 250 |
| **razem** | **ok. 9 000** (stary las: 22 419, limit 25 000) |

Cały świat (8 biomów) to ok. 70 tys. części, ale przy streamingu gracz ma wczytane najwyżej 1–2 biomy.

---

## 10. Wybory do decyzji

**1. Czas biomów: rozkład rosnący czy równy?**
- Rosnący: 30 / 45 / 60 / 75 / 95 / 125 / 170 min (Las ok. 30).
- Równy: ok. 85 min na każdy z siedmiu biomów.
- Oba dają ok. 10 h do ósmego biomu; układ pasa się nie zmienia.

**2. Szerokość pasa: 64, 72 czy 80 studów?**
- 72 st = 4,5 s (propozycja): pętla 5 potworów i 2 st zapasu.
- 64 st = 4 s: ciaśniej, plac walki dotyka ściany.
- 80 st = 5 s: luźniej, więcej miejsca na rekwizyty w polu gry.

**3. Gdzie postawić pas w świecie?**
- Na wschód od miasteczka, za Baseplate (propozycja): słońce za plecami, nic nie koliduje.
- W miejscu starego lasu na północy: najpierw usunąć `BiomLas`, gracz idzie pod słońce.

**4. Strażnik Gaju wspólny czy osobny dla gracza?**
- Wspólny (jak dziś w `LasPotwory`): wraca po 120 s, przy kilku graczach kolejka.
- Osobny: każdy walczy ze swoim, bez czekania; brama i tak otwiera się osobno.

**5. Leśny Troll: wspólny rzadki czy osobny dla gracza?**
- Wspólny: jeden na serwer, wraca po 150 s (przy 8 graczach trafia się rzadko).
- Osobny: każdy ma swojego co kilka minut.
- Troll nie zamyka drogi — do bramy wystarczy Strażnik.

**6. Pominięta walka: kiedy potwór i gracz są wolni?**
- Jak w prototypie: po pełnym czasie walki — farmienie wolniejsze.
- Od razu po oknie wyniku (wynik i tak liczy serwer): farmienie ok. 2× szybsze.

**7. Walka: cięcie na arenę czy na miejscu w pasie?**
- Arena prototypu (dziś): działa od razu.
- Na miejscu: każdy węzeł ma plac r 12; trzeba zmienić odtwarzacz walki.

**8. Teleport z HUD: tylko wejście czy też przed Areną?**
- Tylko wejście biomu (do bramy 57,5 s).
- Plus punkt „przed Areną” po pierwszym dojściu.

**9. Przelot kamery: czy można go pominąć?**
- Bez pomijania: 13,4 s, raz na biom.
- Pominięcie dowolnym klawiszem po 3 s.

**10. Stary las: usunąć po akceptacji pasa?**
- Usunąć `BiomLas`, `LasMgla`, `LasTeleport`; walki petów i loch zostają w mieście (D-042).
- Zostawić jako osobną strefę do zwiedzania.

Szczegóły: wybory 4–6 zmieniają liczby farmienia (rozdz. 2); wybór 7 to lista zmian A1–A4 z
`swiat/las_potwory/PROJEKT.md` rozdz. 6.

## 11. Czego nie sprawdzono

- Nic nie było budowane ani oglądane w Studio: wygląd pasa, kulisy, czytelność przegród, kolizje, niewidzialne ściany.
- Kierunek słońca wzięty z dokumentacji starego lasu; rozmiar Baseplate (±1024) założony — do sprawdzenia w Studio.
- Narzut walki 7 s i dojście 2 s to szacunki; czasy walk to średnie z balansu na 5. poziomie, nie pomiar.
- Budżet 30 min zależy od krzywej doświadczenia, której jeszcze nie ma; poziomy w przegrodach są propozycją.
- Przelot: krzywa sprawdzona tylko na liczbach; płynność, streaming i budowa widoków potworów w czasie lotu — niesprawdzone,
  szczególnie na telefonie. Ile widać przez mgłę — niesprawdzone.
- Liczba części to szacunek z gęstości starego lasu.
- `plan_pasa.json` powstał skryptem pomocniczym spoza repozytorium (pętle liczone jako zaokrąglone prostokąty); przy
  ręcznych zmianach węzłów uruchom `sprawdz_plan.py` — pilnuje obwodu, pojemności, domów i placów walki.
